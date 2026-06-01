import streamlit as st
from groq import Groq
import PyPDF2
import io
import json
import re

st.set_page_config(page_title="Resume Screener | Nexe-Agent", page_icon="📄", layout="wide")

st.title("📄 Resume Screener AI")
st.caption("Task 3 — Resume Screener | Nexe-Agent Internship by Mahboob Ali")

# Load API key from backend
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("API key not configured. Please contact the app owner.")
    st.stop()

with st.sidebar:
    st.success("🔑 API Key: Configured ✅")
    st.markdown("---")
    st.markdown("### How to use")
    st.markdown("1. Paste a job description")
    st.markdown("2. Upload one or more PDF resumes")
    st.markdown("3. Click **Screen Resumes**")

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

def analyze_resume(resume_text, job_description):
    prompt = f"""You are an expert HR recruiter and resume screener.

Analyze the following resume against the job description and return a JSON response with this exact structure:
{{
  "candidate_name": "extracted name or Unknown",
  "match_percentage": 0-100,
  "extracted_skills": ["skill1", "skill2"],
  "matched_skills": ["skill1", "skill2"],
  "missing_skills": ["skill1", "skill2"],
  "experience_years": "X years or Not specified",
  "education": "highest degree or Not specified",
  "strengths": ["strength1", "strength2", "strength3"],
  "weaknesses": ["weakness1", "weakness2"],
  "recommendation": "Strong Match / Good Match / Average Match / Weak Match",
  "summary": "2-3 sentence summary of the candidate fit"
}}

RESUME:
{resume_text[:3000]}

JOB DESCRIPTION:
{job_description[:1500]}

Return ONLY the JSON, no other text."""

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500
    )
    return response.choices[0].message.content

col1, col2 = st.columns([1, 1])
with col1:
    st.subheader("📋 Job Description")
    job_description = st.text_area(
        "Paste the job description here",
        height=300,
        placeholder="e.g. We are looking for a Python Developer..."
    )
with col2:
    st.subheader("📎 Upload Resumes")
    uploaded_files = st.file_uploader(
        "Upload resume(s) (PDF)",
        type=["pdf"],
        accept_multiple_files=True
    )

if st.button("🔍 Screen Resumes", type="primary"):
    if not job_description:
        st.error("Please enter a job description.")
    elif not uploaded_files:
        st.error("Please upload at least one resume.")
    else:
        results = []
        progress = st.progress(0)
        status = st.empty()

        for i, file in enumerate(uploaded_files):
            status.text(f"Analyzing {file.name}...")
            try:
                resume_text = extract_text_from_pdf(file)
                if not resume_text.strip():
                    st.warning(f"⚠️ Could not extract text from {file.name}.")
                    continue
                raw = analyze_resume(resume_text, job_description)
                raw = re.sub(r"```json|```", "", raw).strip()
                result = json.loads(raw)
                result["filename"] = file.name
                results.append(result)
            except Exception as e:
                st.error(f"Error processing {file.name}: {e}")
            progress.progress((i + 1) / len(uploaded_files))

        status.empty()
        progress.empty()

        if results:
            results.sort(key=lambda x: x.get("match_percentage", 0), reverse=True)
            st.markdown("---")
            st.subheader("📊 Screening Results")

            import pandas as pd
            summary_data = [{
                "File": r["filename"],
                "Candidate": r.get("candidate_name", "Unknown"),
                "Match %": f"{r.get('match_percentage', 0)}%",
                "Experience": r.get("experience_years", "N/A"),
                "Recommendation": r.get("recommendation", "N/A")
            } for r in results]
            st.dataframe(pd.DataFrame(summary_data), use_container_width=True)

            for r in results:
                match = r.get("match_percentage", 0)
                with st.expander(f"📄 {r['filename']} — {r.get('candidate_name','Unknown')} — {match}% match"):
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Match %", f"{match}%")
                    c2.metric("Experience", r.get("experience_years", "N/A"))
                    c3.metric("Verdict", r.get("recommendation", "N/A"))
                    st.markdown(f"**Summary:** {r.get('summary','')}")
                    st.markdown(f"**Education:** {r.get('education','N/A')}")
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.markdown("**✅ Matched Skills**")
                        for s in r.get("matched_skills", []): st.markdown(f"- {s}")
                    with col_b:
                        st.markdown("**❌ Missing Skills**")
                        for s in r.get("missing_skills", []): st.markdown(f"- {s}")
                    with col_c:
                        st.markdown("**💪 Strengths**")
                        for s in r.get("strengths", []): st.markdown(f"- {s}")
