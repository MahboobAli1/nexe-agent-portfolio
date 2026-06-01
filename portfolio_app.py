import streamlit as st

st.set_page_config(
    page_title="Nexe-Agent Portfolio | Mahboob Ali",
    page_icon="🤖",
    layout="wide"
)

# ── Custom CSS ──
st.markdown("""
<style>
.task-card {
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 20px;
    margin: 10px 0;
    background: #fafafa;
}
.task-card:hover { border-color: #4CAF50; }
.badge-beginner { background:#d4edda; color:#155724; padding:4px 10px; border-radius:20px; font-size:12px; }
.badge-intermediate { background:#fff3cd; color:#856404; padding:4px 10px; border-radius:20px; font-size:12px; }
.badge-advanced { background:#f8d7da; color:#721c24; padding:4px 10px; border-radius:20px; font-size:12px; }
.hero-title { font-size: 2.5em; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

# ── Hero ──
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<div class="hero-title">🤖 Nexe-Agent Internship Portfolio</div>', unsafe_allow_html=True)
    st.markdown("**AI & Automation Projects** by Mahboob Ali")
    st.caption("Role: AI & Automation Intern | Company: Nexe-Agent | Language: Python 🐍")
with col2:
    c1, c2, c3 = st.columns(3)
    c1.metric("Tasks", "6/6")
    c2.metric("Apps", "6")
    c3.metric("Status", "✅")

st.markdown("---")

# ── Task Data ──
TASKS = [
    {
        "num": 1, "title": "Basic AI Chatbot", "level": "Beginner",
        "badge": "badge-beginner",
        "desc": "A multi-turn AI chatbot powered by Groq LLM API with full error handling and chat history.",
        "features": ["Accept user input", "Groq AI API integration", "Multi-turn conversation", "Error handling"],
        "tech": "Python · Groq AI · Streamlit",
        "demo_url": "https://YOUR-TASK1-URL.streamlit.app",  # REPLACE
        "github_url": "https://github.com/YOUR_USERNAME/nexe-agent-portfolio/tree/main/task1_chatbot",  # REPLACE
        "icon": "🤖"
    },
    {
        "num": 2, "title": "Email Automation Script", "level": "Beginner",
        "badge": "badge-beginner",
        "desc": "Automates sending scheduled and template-based emails using Gmail SMTP with a full send log.",
        "features": ["Gmail SMTP / App Password", "Email templates", "Scheduled sending", "Send log with CSV export"],
        "tech": "Python · Gmail SMTP · Streamlit",
        "demo_url": "https://YOUR-TASK2-URL.streamlit.app",  # REPLACE
        "github_url": "https://github.com/YOUR_USERNAME/nexe-agent-portfolio/tree/main/task2_email",
        "icon": "📧"
    },
    {
        "num": 3, "title": "Resume Screener AI", "level": "Intermediate",
        "badge": "badge-intermediate",
        "desc": "Upload multiple PDF resumes and get AI-powered skill extraction and match percentage against any job description.",
        "features": ["Upload PDF resumes", "Extract skills with AI", "Match with job description", "Output match percentage"],
        "tech": "Python · Groq AI · PyPDF2 · Streamlit",
        "demo_url": "https://YOUR-TASK3-URL.streamlit.app",
        "github_url": "https://github.com/YOUR_USERNAME/nexe-agent-portfolio/tree/main/task3_resume_screener",
        "icon": "📄"
    },
    {
        "num": 4, "title": "WhatsApp Automation", "level": "Intermediate",
        "badge": "badge-intermediate",
        "desc": "FAQ-based WhatsApp bot with auto-reply logic, chat simulator, conversation logging, and FAQ manager.",
        "features": ["Auto-reply system", "FAQ-based bot", "Conversation log", "CSV export"],
        "tech": "Python · Twilio · Streamlit",
        "demo_url": "https://YOUR-TASK4-URL.streamlit.app",
        "github_url": "https://github.com/YOUR_USERNAME/nexe-agent-portfolio/tree/main/task4_whatsapp",
        "icon": "💬"
    },
    {
        "num": 5, "title": "Multi-Tool AI Agent", "level": "Advanced",
        "badge": "badge-advanced",
        "desc": "AI agent with tool-use capabilities: calculator, unit converter, text analyzer, datetime, and JSON parser.",
        "features": ["Calculator tool", "Unit converter", "Text analyzer", "Datetime tool", "Agent loop with Groq"],
        "tech": "Python · Groq AI (Tool Use) · Streamlit",
        "demo_url": "https://YOUR-TASK5-URL.streamlit.app",
        "github_url": "https://github.com/YOUR_USERNAME/nexe-agent-portfolio/tree/main/task5_ai_agent",
        "icon": "🛠️"
    },
    {
        "num": 6, "title": "RAG Knowledge Assistant", "level": "Advanced",
        "badge": "badge-advanced",
        "desc": "Upload company documents, store embeddings, and query them with contextual AI answers citing sources.",
        "features": ["Upload PDF/TXT docs", "Chunk & embed text", "Vector similarity search", "Contextual QA with sources"],
        "tech": "Python · Groq AI · PyPDF2 · NumPy · Streamlit",
        "demo_url": "https://YOUR-TASK6-URL.streamlit.app",
        "github_url": "https://github.com/YOUR_USERNAME/nexe-agent-portfolio/tree/main/task6_rag",
        "icon": "🧠"
    }
]

st.subheader("✅ All 6 Tasks Complete")

for task in TASKS:
    with st.container():
        col_main, col_btns = st.columns([4, 1])
        with col_main:
            st.markdown(f"""
            <div class="task-card">
            <b>{task['icon']} Task {task['num']} — {task['title']}</b>
            &nbsp;&nbsp;<span class="{task['badge']}">{task['level']}</span>
            <p style="margin:8px 0; color:#555">{task['desc']}</p>
            <small><b>Features:</b> {' · '.join(['✅ ' + f for f in task['features']])}</small><br>
            <small style="color:#888"><b>Tech:</b> {task['tech']}</small>
            </div>
            """, unsafe_allow_html=True)
        with col_btns:
            st.write("")
            st.write("")
            st.link_button("🚀 Live Demo", task["demo_url"])
            st.link_button("💻 GitHub", task["github_url"])

st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#888; padding:20px'>
Built with ❤️ by <b>Mahboob Ali</b> | AI & Automation Intern at <b>Nexe-Agent</b><br>
<a href='https://github.com/YOUR_USERNAME/nexe-agent-portfolio'>📂 View All Code on GitHub</a>
</div>
""", unsafe_allow_html=True)