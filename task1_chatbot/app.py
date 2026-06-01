import streamlit as st
from groq import Groq

st.set_page_config(page_title="AI Chatbot | Nexe-Agent", page_icon="🤖")

st.title("🤖 AI Chatbot")
st.caption("Task 1 — Basic AI Chatbot | Nexe-Agent Internship by Mahboob Ali")

# Load API key from Streamlit secrets (backend)
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("API key not configured. Please contact the app owner.")
    st.stop()

with st.sidebar:
    st.header("⚙️ Settings")
    st.success("🔑 API Key: Configured ✅")
    st.markdown("---")
    model = st.selectbox("Model", [
        "llama3-8b-8192",
        "llama3-70b-8192",
        "mixtral-8x7b-32768"
    ])
    temperature = st.slider("Creativity", 0.0, 1.0, 0.7)
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a helpful AI assistant."},
                        *st.session_state.messages
                    ],
                    max_tokens=1024,
                    temperature=temperature
                )
                reply = response.choices[0].message.content
                st.markdown(reply)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": reply
                })
            except Exception as e:
                st.error(f"Error: {str(e)}")
