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
st.caption("Task 6 — RAG Knowledge Assistant | Nexe-Agent Internship by Mahboob Ali")

# Load API key from backend
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("API key not configured. Please contact the app owner.")
    st.stop()

with st.sidebar:
    st.success("🔑 API Key: Configured ✅")
    st.markdown("---")
    st.subheader("📚 Uploaded Documents")
    if "doc_store" in st.session_state and st.session_state.doc_store:
        for name in st.session_state.doc_store.keys():
            st.success(f"📄 {name}")
    else:
        st.info("No documents uploaded yet.")
    st.markdown("---")
    chunk_size = st.slider("Chunk Size (words)", 100, 500, 200)
    top_k = st.slider("Top K chunks", 1, 5, 3)
    if st.button("🗑️ Clear All Documents"):
        st.session_state.doc_store = {}
        st.session_state.chunk_store = []
        st.session_state.rag_messages = []
        st.rerun()

def extract_text_from_pdf(file_bytes):
    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    return "".join(page.extract_text() or "" for page in reader.pages)

def chunk_text(text, chunk_size=200):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size // 2):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks

def get_word_freq(text):
    words = re.findall(r'\w+', text.lower())
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    return freq

def cosine_similarity(d1, d2):
    keys = set(d1.keys()) | set(d2.keys())
    if not keys:
        return 0.0
    v1 = np.array([d1.get(k, 0) for k in keys], dtype=float)
    v2 = np.array([d2.get(k, 0) for k in keys], dtype=float)
    n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
    if n1 == 0 or n2 == 0:
        return 0.0
    return float(np.dot(v1, v2) / (n1 * n2))

def retrieve_chunks(query, chunk_store, top_k=3):
    query_vec = get_word_freq(query)
    scored = [{**item, "score": cosine_similarity(query_vec, item["embedding"])} for item in chunk_store]
    return sorted(scored, key=lambda x: x["score"], reverse=True)[:top_k]

if "doc_store" not in st.session_state:
    st.session_state.doc_store = {}
if "chunk_store" not in st.session_state:
    st.session_state.chunk_store = []
if "rag_messages" not in st.session_state:
    st.session_state.rag_messages = []

tab1, tab2 = st.tabs(["📤 Upload Documents", "💬 Query Assistant"])

with tab1:
    st.subheader("📤 Upload Company Documents")
    uploaded_files = st.file_uploader("Upload PDF or TXT files", type=["pdf", "txt"], accept_multiple_files=True)

    if uploaded_files and st.button("📥 Process Documents", type="primary"):
        progress = st.progress(0)
        for i, f in enumerate(uploaded_files):
            with st.spinner(f"Processing {f.name}..."):
                file_bytes = f.read()
                text = extract_text_from_pdf(file_bytes) if f.name.endswith(".pdf") else file_bytes.decode("utf-8", errors="ignore")
                if not text.strip():
                    st.warning(f"⚠️ No text in {f.name}")
                    continue
                st.session_state.doc_store[f.name] = text
                for chunk in chunk_text(text, chunk_size):
                    st.session_state.chunk_store.append({
                        "text": chunk,
                        "source": f.name,
                        "embedding": get_word_freq(chunk)
                    })
            progress.progress((i + 1) / len(uploaded_files))
        st.success(f"✅ {len(uploaded_files)} document(s) → {len(st.session_state.chunk_store)} chunks!")
        st.balloons()

    if st.session_state.doc_store:
        st.markdown("---")
        st.subheader("📊 Document Statistics")
        import pandas as pd
        stats = [{"Document": name, "Words": len(text.split()), "Chunks": len([c for c in st.session_state.chunk_store if c["source"] == name])}
                 for name, text in st.session_state.doc_store.items()]
        st.dataframe(pd.DataFrame(stats), use_container_width=True)

with tab2:
    if not st.session_state.chunk_store:
        st.warning("⚠️ Please upload and process documents first.")
    else:
        st.subheader(f"💬 Ask questions about your {len(st.session_state.doc_store)} document(s)")

        for msg in st.session_state.rag_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg.get("sources"):
                    with st.expander("📚 Sources"):
                        for src in msg["sources"]:
                            st.markdown(f"**{src['source']}** (score: {src['score']:.3f})")
                            st.text(src["text"][:300] + "...")

        if prompt := st.chat_input("Ask anything about your documents..."):
            st.session_state.rag_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("🔍 Searching documents..."):
                    relevant = retrieve_chunks(prompt, st.session_state.chunk_store, top_k)
                    context = "\n\n---\n\n".join([f"[From: {c['source']}]\n{c['text']}" for c in relevant])

                with st.spinner("🧠 Generating answer..."):
                    try:
                        sys_prompt = f"""You are a helpful assistant. Answer ONLY from the context below.
If the answer is not in the context, say 'I couldn't find this in the documents.'
Always mention which document your answer came from.

CONTEXT:
{context}"""
                        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.rag_messages[-6:]]
                        response = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
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

                        st.session_state.rag_messages.append({"role": "assistant", "content": answer, "sources": source_info})
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
