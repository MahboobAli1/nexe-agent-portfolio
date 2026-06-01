import streamlit as st
from datetime import datetime
import json
import re

st.set_page_config(page_title="WhatsApp Bot | Nexe-Agent", page_icon="💬")

st.title("💬 WhatsApp Automation Bot")
st.caption("Task 4 — WhatsApp Automation | Nexe-Agent Internship by Khadija Maqsood")

# FAQ knowledge base
DEFAULT_FAQS = {
    "hello": "Hello! 👋 Welcome to Nexe-Agent! How can I help you today?\n\nReply with a number:\n1. Services\n2. Pricing\n3. Contact\n4. About Us\n5. Help",
    "hi": "Hello! 👋 Welcome to Nexe-Agent! How can I help you today?\n\nReply with a number:\n1. Services\n2. Pricing\n3. Contact\n4. About Us\n5. Help",
    "1": "🚀 **Our Services:**\n- AI Chatbot Development\n- Automation Scripts\n- Data Analysis\n- Web Scraping\n- Custom AI Solutions\n\nType 'pricing' to see our rates.",
    "services": "🚀 **Our Services:**\n- AI Chatbot Development\n- Automation Scripts\n- Data Analysis\n- Custom AI Solutions",
    "2": "💰 **Pricing:**\n- Basic Package: $99\n- Standard Package: $299\n- Premium Package: $599\n- Custom: Contact us\n\nType 'contact' to reach us.",
    "pricing": "💰 **Pricing:**\n- Basic: $99\n- Standard: $299\n- Premium: $599",
    "3": "📞 **Contact Us:**\n- Email: nexeagent@gmail.com\n- Phone: 03222100121\n- LinkedIn: Nexe-Agent",
    "contact": "📞 **Contact Us:**\nEmail: nexeagent@gmail.com\nPhone: 03222100121",
    "4": "🏢 **About Nexe-Agent:**\nWe are an AI & Automation company helping businesses scale with intelligent solutions. Founded by Maryam Arif.",
    "about": "🏢 Nexe-Agent is an AI & Automation company helping businesses scale with intelligent solutions.",
    "5": "❓ **Help Menu:**\nType any of:\n- 'services' → Our offerings\n- 'pricing' → Price list\n- 'contact' → Get in touch\n- 'about' → About us\n- 'hello' → Main menu",
    "help": "❓ Type: services, pricing, contact, about, or hello for the main menu.",
}

with st.sidebar:
    st.header("⚙️ Bot Configuration")
    bot_name = st.text_input("Bot Name", value="Nexe-Agent Bot")
    st.markdown("---")
    st.subheader("📝 Manage FAQs")
    st.info("Add keyword → response pairs below:")
    new_keyword = st.text_input("Keyword (e.g. 'hours')")
    new_response = st.text_area("Response", height=80)
    if st.button("➕ Add FAQ"):
        if new_keyword and new_response:
            if "faqs" not in st.session_state:
                st.session_state.faqs = DEFAULT_FAQS.copy()
            st.session_state.faqs[new_keyword.lower()] = new_response
            st.success(f"Added FAQ: '{new_keyword}'")
    st.markdown("---")
    if st.button("🗑️ Clear Chat Log"):
        st.session_state.chat_log = []
        st.rerun()
    if st.button("📥 Download Log"):
        if "chat_log" in st.session_state and st.session_state.chat_log:
            log_str = "\n".join([f"[{m['time']}] {m['sender']}: {m['message']}" for m in st.session_state.chat_log])
            st.download_button("⬇️ Download", log_str, "whatsapp_log.txt", "text/plain")

# Initialize session state
if "faqs" not in st.session_state:
    st.session_state.faqs = DEFAULT_FAQS.copy()
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []
if "chat_display" not in st.session_state:
    st.session_state.chat_display = []

def get_bot_response(user_msg):
    msg = user_msg.lower().strip()
    # Exact match
    if msg in st.session_state.faqs:
        return st.session_state.faqs[msg]
    # Partial match
    for keyword, response in st.session_state.faqs.items():
        if keyword in msg:
            return response
    return f"Sorry, I didn't understand that. 🤔\n\nType 'help' to see what I can do, or 'hello' for the main menu."

tab1, tab2, tab3 = st.tabs(["💬 Chat Simulator", "📜 Conversation Log", "📊 FAQ Manager"])

with tab1:
    st.subheader("WhatsApp Chat Simulator")
    st.caption("Simulate how the bot responds to incoming messages")

    # Chat display
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_display:
            if msg["type"] == "user":
                st.markdown(f"""
                <div style='text-align:right; margin:8px 0'>
                <span style='background:#DCF8C6; padding:8px 14px; border-radius:12px 12px 2px 12px; display:inline-block; max-width:70%; text-align:left; color:#000'>
                {msg["text"]}<br><small style='color:#666; font-size:10px'>{msg["time"]}</small>
                </span></div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='text-align:left; margin:8px 0'>
                <span style='background:#fff; border:1px solid #ddd; padding:8px 14px; border-radius:12px 12px 12px 2px; display:inline-block; max-width:70%; color:#000'>
                <b>{bot_name}</b><br>{msg["text"]}<br><small style='color:#666; font-size:10px'>{msg["time"]}</small>
                </span></div>""", unsafe_allow_html=True)

    # Input
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Type a message...", placeholder="e.g. hello, pricing, services")
        send = st.form_submit_button("Send 📤")

    if send and user_input:
        ts = datetime.now().strftime("%H:%M")
        dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Add user message
        st.session_state.chat_display.append({"type": "user", "text": user_input, "time": ts})
        st.session_state.chat_log.append({"time": dt, "sender": "User", "message": user_input})
        # Bot response
        bot_reply = get_bot_response(user_input)
        st.session_state.chat_display.append({"type": "bot", "text": bot_reply, "time": ts})
        st.session_state.chat_log.append({"time": dt, "sender": bot_name, "message": bot_reply})
        st.rerun()

with tab2:
    st.subheader("📜 Full Conversation Log")
    if st.session_state.chat_log:
        import pandas as pd
        df = pd.DataFrame(st.session_state.chat_log)
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False)
        st.download_button("⬇️ Export as CSV", csv, "whatsapp_log.csv", "text/csv")
    else:
        st.info("No conversations yet. Go to the Chat Simulator tab.")

with tab3:
    st.subheader("📊 Current FAQ Entries")
    import pandas as pd
    faq_df = pd.DataFrame([{"Keyword": k, "Response": v[:60]+"..."} for k, v in st.session_state.faqs.items()])
    st.dataframe(faq_df, use_container_width=True)
    st.info("💡 To connect to real WhatsApp, use Twilio API — see GitHub README for steps.")