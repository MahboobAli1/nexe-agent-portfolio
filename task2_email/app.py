import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import time

st.set_page_config(page_title="Email Automation | Nexe-Agent", page_icon="📧")

st.title("📧 Email Automation Script")
st.caption("Task 2 — Email Automation | Nexe-Agent Internship by Mahboob Ali")

with st.sidebar:
    st.header("⚙️ Gmail Settings")
    st.info("Use Gmail App Password (not your real password). Enable 2FA first, then create App Password at myaccount.google.com/apppasswords")
    sender_email = st.text_input("Your Gmail Address")
    app_password = st.text_input("Gmail App Password", type="password")
    st.markdown("---")
    st.markdown("**📅 Schedule Options**")
    schedule_type = st.selectbox("Send", ["Send Now", "Send Once (Delayed)", "Repeat (Interval)"])
    if schedule_type == "Send Once (Delayed)":
        delay_mins = st.number_input("Delay (minutes)", min_value=1, value=5)
    elif schedule_type == "Repeat (Interval)":
        interval_mins = st.number_input("Interval (minutes)", min_value=1, value=60)
        repeat_count = st.number_input("Number of emails", min_value=1, value=3)

tab1, tab2 = st.tabs(["✉️ Compose Email", "📜 Send Log"])

if "send_log" not in st.session_state:
    st.session_state.send_log = []

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        to_email = st.text_input("To (recipient email)")
    with col2:
        subject = st.text_input("Subject")

    # Template selector
    template = st.selectbox("📄 Use Template", [
        "Custom", "Meeting Reminder", "Follow-up", "Welcome Email", "Newsletter"
    ])

    templates = {
        "Meeting Reminder": ("Meeting Reminder", "Hi,\n\nThis is a reminder about our upcoming meeting scheduled for tomorrow.\n\nPlease be prepared with your updates.\n\nBest regards,\nMahboo Ali"),
        "Follow-up": ("Follow-up", "Hi,\n\nI wanted to follow up on my previous email. Please let me know if you need any additional information.\n\nBest regards,\nMahboo Ali"),
        "Welcome Email": ("Welcome!", "Hi,\n\nWelcome aboard! We're excited to have you.\n\nFeel free to reach out if you have any questions.\n\nBest regards,\nMahboo Ali"),
        "Newsletter": ("Monthly Newsletter", "Hi,\n\nHere are the highlights from this month:\n\n1. [Update 1]\n2. [Update 2]\n3. [Update 3]\n\nStay tuned for more!\n\nBest regards,\nMahboo Ali"),
    }

    if template != "Custom":
        subject = templates[template][0]
        default_body = templates[template][1]
    else:
        default_body = ""

    body = st.text_area("Email Body", value=default_body, height=200)

    if st.button("🚀 Send Email", type="primary"):
        if not all([sender_email, app_password, to_email, subject, body]):
            st.error("Please fill in all fields and settings.")
        else:
            def send_email(to, subj, bod):
                msg = MIMEMultipart()
                msg["From"] = sender_email
                msg["To"] = to
                msg["Subject"] = subj
                msg.attach(MIMEText(bod, "plain"))
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                    server.login(sender_email, app_password)
                    server.send_message(msg)

            try:
                if schedule_type == "Send Now":
                    with st.spinner("Sending..."):
                        send_email(to_email, subject, body)
                    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.success(f"✅ Email sent to {to_email} at {ts}")
                    st.session_state.send_log.append({"time": ts, "to": to_email, "subject": subject, "status": "✅ Sent"})

                elif schedule_type == "Send Once (Delayed)":
                    st.info(f"⏳ Email will be sent in {delay_mins} minute(s)...")
                    time.sleep(delay_mins * 60)
                    send_email(to_email, subject, body)
                    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.success(f"✅ Delayed email sent at {ts}")
                    st.session_state.send_log.append({"time": ts, "to": to_email, "subject": subject, "status": "✅ Sent (delayed)"})

                elif schedule_type == "Repeat (Interval)":
                    for i in range(int(repeat_count)):
                        send_email(to_email, subject, body)
                        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.success(f"✅ Email {i+1}/{int(repeat_count)} sent at {ts}")
                        st.session_state.send_log.append({"time": ts, "to": to_email, "subject": subject, "status": f"✅ Sent ({i+1}/{int(repeat_count)})"})
                        if i < int(repeat_count) - 1:
                            time.sleep(interval_mins * 60)

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

with tab2:
    st.subheader("📜 Email Send Log")
    if st.session_state.send_log:
        import pandas as pd
        df = pd.DataFrame(st.session_state.send_log)
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False)
        st.download_button("⬇️ Download Log", csv, "email_log.csv", "text/csv")
    else:
        st.info("No emails sent yet. Send an email to see the log here.")
