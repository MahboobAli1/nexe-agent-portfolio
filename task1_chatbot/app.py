import streamlit as st
from groq import Groq

st.set_page_config(page_title="AI Chatbot | Nexe-Agent", page_icon="🤖")

st.title("🤖 AI Chatbot")
st.caption("Task 1 — Basic AI Chatbot | Nexe-Agent Internship by Khadija Maqsood")

# Sidebar for API key
with st.sidebar:
    st.header("⚙️ Settings")
    groq_api_key = st.text_input("Groq API Key", type="password", 
                                  help="Get free key at console.groq.com")
    st.markdown("---")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    if not groq_api_key:
        st.error("Please enter your Groq API key in the sidebar.")
        st.stop()

    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                client = Groq(api_key=groq_api_key)
                response = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[
                        {"role": "system", "content": "You are a helpful AI assistant."},
                        *st.session_state.messages
                    ],
                    max_tokens=1024
                )
                reply = response.choices[0].message.content
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"Error: {str(e)}")