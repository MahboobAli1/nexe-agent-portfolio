import streamlit as st
from groq import Groq

# Page Configuration
st.set_page_config(
    page_title="AI Chatbot | Nexe-Agent",
    page_icon="🤖"
)

# Header
st.title("🤖 AI Chatbot")
st.caption("Task 1 — Basic AI Chatbot | Nexe-Agent Internship by Mahboob Ali")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")

    groq_api_key = st.text_input(
        "Groq API Key",
        type="password",
        help="Get your free API key from https://console.groq.com"
    )

    st.markdown("---")

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Previous Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
prompt = st.chat_input("Type your message here...")

if prompt:

    if not groq_api_key:
        st.error("Please enter your Groq API Key in the sidebar.")
        st.stop()

    # Display User Message
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate AI Response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            try:
                client = Groq(api_key=groq_api_key)

                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful AI assistant."
                        },
                        *st.session_state.messages
                    ],
                    max_tokens=1024,
                    temperature=0.7
                )

                reply = response.choices[0].message.content

                st.markdown(reply)

                st.session_state.messages.append(
                    {"role": "assistant", "content": reply}
                )

            except Exception as e:
                st.error(f"Error: {e}")
