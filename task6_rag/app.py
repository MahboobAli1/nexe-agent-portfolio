import streamlit as st
from groq import Groq
import PyPDF2
import io
import numpy as np
import json
import re
from typing import List

st.set_page_config(page_title="RAG Assistant | Nexe-Agent", page_icon="🧠", layout="wide")

st.title("🧠 RAG Knowledge Assistant")
st.caption("Task 6 — RAG-based Knowledge Assistant | Nexe-Agent Internship by Khadija Maqsood")

with st.sidebar:
    st.header("⚙️ Settings")
    groq_api_key = st.text_input("Groq API Key", type="password")
    st.markdown("---")
    st.subheader("📚 Uploaded Documents")
    if "doc_store" in st.session_state and st.session_state.doc_store:
        for name in st.session_state.doc_store.keys():
            st.success(f"📄 {name}")
    else:
        st.info("No documents uploaded yet.")
    st.markdown("---")
    chunk_size = st.slider("Chunk Size (words)", 100, 500, 200)
    top_k = st.slider("Top K chunks to retrieve", 1, 5, 3)
    if st.button("🗑️ Clear All Documents"):
        st.session_state.doc_store = {}
        st.session_state.rag_messages = []
        st.rerun()

# ──── Text Processing ────
def extract_text_from_pdf(file_bytes):
    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        text += (page.extract_text() or "") + "\n"
    return text

def chunk_text(text: str, chunk_size: int = 200) -> List[str]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size // 2):  # 50% overlap
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks

def get_embedding_groq(client, text: str) -> List[float]:
    """Simple TF-IDF-like embedding using word frequencies (no external embedding API needed)"""
    # We use a simple bag-of-words similarity since Groq doesn't have embeddings endpoint
    # This is a fallback — in production use OpenAI embeddings or sentence-transformers
    words = re.findall(r'\w+', text.lower())
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    return freq

def cosine_similarity_dicts(d1: dict, d2: dict) -> float:
    """Cosine similarity between two word-frequency dicts"""
    keys = set(d1.keys()) | set(d2.keys())
    if not keys:
        return 0.0
    v1 = np.array([d1.get(k, 0) for k in keys], dtype=float)
    v2 = np.array([d2.get(k, 0) for k in keys], dtype=float)
    n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
    if n1 == 0 or n2 == 0:
        return 0.0
    return float(np.dot(v1, v2) / (n1 * n2))

def retrieve_chunks(query: str, chunk_store: List[dict], top_k: int = 3) -> List[dict]:
    query_vec = get_embedding_groq(None, query)
    scored = []
    for item in chunk_store:
        score = cosine_similarity_dicts(query_vec, item["embedding"])
        scored.append({**item, "score": score})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]

# Initialize state
if "doc_store" not in st.session_state:
    st.session_state.doc_store = {}
if "chunk_store" not in st.session_state:
    st.session_state.chunk_store = []
if "rag_messages" not in st.session_state:
    st.session_state.rag_messages = []

tab1, tab2 = st.tabs(["📤 Upload Documents", "💬 Query Assistant"])

with tab1:
    st.subheader("📤 Upload Company Documents")
    uploaded_files = st.file_uploader(
        "Upload PDF or TXT files",
        type=["pdf", "txt"],
        accept_multiple_files=True
    )

    if uploaded_files and st.button("📥 Process Documents", type="primary"):
        progress = st.progress(0)
        for i, f in enumerate(uploaded_files):
            with st.spinner(f"Processing {f.name}..."):
                file_bytes = f.read()
                if f.name.endswith(".pdf"):
                    text = extract_text_from_pdf(file_bytes)
                else:
                    text = file_bytes.decode("utf-8", errors="ignore")

                if not text.strip():
                    st.warning(f"⚠️ No text found in {f.name}")
                    continue

                st.session_state.doc_store[f.name] = text
                chunks = chunk_text(text, chunk_size)
                for chunk in chunks:
                    embedding = get_embedding_groq(None, chunk)
                    st.session_state.chunk_store.append({
                        "text": chunk,
                        "source": f.name,
                        "embedding": embedding
                    })
            progress.progress((i + 1) / len(uploaded_files))

        st.success(f"✅ Processed {len(uploaded_files)} document(s) into {len(st.session_state.chunk_store)} chunks!")
        st.balloons()

    if st.session_state.doc_store:
        st.markdown("---")
        st.subheader("📊 Document Statistics")
        for name, text in st.session_state.doc_store.items():
            col1, col2, col3 = st.columns(3)
            with col1: st.metric("Document", name[:30])
            with col2: st.metric("Words", len(text.split()))
            with col3: st.metric("Chunks", len([c for c in st.session_state.chunk_store if c["source"] == name]))

with tab2:
    if not st.session_state.chunk_store:
        st.warning("⚠️ Please upload and process documents first (Tab 1).")
    else:
        st.subheader(f"💬 Query your {len(st.session_state.doc_store)} document(s)")

        for msg in st.session_state.rag_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg.get("sources"):
                    with st.expander("📚 Retrieved Sources"):
                        for src in msg["sources"]:
                            st.markdown(f"**{src['source']}** (score: {src['score']:.3f})")
                            st.text(src["text"][:300] + "...")

        if prompt := st.chat_input("Ask anything about your documents..."):
            if not groq_api_key:
                st.error("Enter Groq API key in sidebar.")
                st.stop()

            st.session_state.rag_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("🔍 Retrieving relevant context..."):
                    relevant = retrieve_chunks(prompt, st.session_state.chunk_store, top_k)
                    context = "\n\n---\n\n".join([
                        f"[From: {c['source']}]\n{c['text']}" for c in relevant
                    ])

                with st.spinner("🧠 Generating answer..."):
                    try:
                        client = Groq(api_key=groq_api_key)
                        sys_prompt = f"""You are a knowledgeable assistant. Answer questions ONLY based on the provided context documents.
If the answer is not in the context, say "I couldn't find this information in the provided documents."
Always cite which document your answer came from.

CONTEXT:
{context}"""
                        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.rag_messages[-6:]]
                        response = client.chat.completions.create(
                            model="llama3-8b-8192",
                            messages=[{"role": "system", "content": sys_prompt}] + history,
                            max_tokens=1024
                        )
                        answer = response.choices[0].message.content
                        st.markdown(answer)

                        source_info = [{"source": c["source"], "score": c["score"], "text": c["text"]} for c in relevant]
                        with st.expander("📚 Retrieved Sources"):
                            for src in source_info:
                                st.markdown(f"**{src['source']}** (relevance: {src['score']:.3f})")
                                st.text(src["text"][:300] + "...")

                        st.session_state.rag_messages.append({
                            "role": "assistant", "content": answer, "sources": source_info
                        })
                    except Exception as e:
                        st.error(f"Error: {str(e)}")