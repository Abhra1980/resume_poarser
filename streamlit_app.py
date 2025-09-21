import os
import json
import streamlit as st
from dotenv import load_dotenv
from crew_app.file_tools.file_loader import detect_and_extract
from crew_app.crew import run_pipeline
from crew_app.utils import txt_to_docx_bytes

# Load env
load_dotenv()
st.set_page_config(page_title="ATS Resume Agent (CrewAI)", page_icon="🧠", layout="wide")

st.title("🧠 ATS-Optimized Resume Agent (CrewAI + OpenAI)")
st.caption("Upload your resume (.pdf or .docx), target a role, and get an ATS-friendly version with scores & quick wins.")

with st.sidebar:
    st.subheader("OpenAI Settings")
    st.text_input("Model:", value="gpt-4o-mini", disabled=True)
    st.write("API Key loaded: ✅ Working OpenAI key")

# Inputs
colL, colR = st.columns([1,1])
with colL:
    up = st.file_uploader("Upload Resume (.pdf or .docx preferred)", type=["pdf", "docx", "txt"])
with colR:
    job_title = st.text_input("Target Job Title (e.g., 'Machine Learning Engineer')")
    job_desc = st.text_area("Paste Job Description", height=220, placeholder="Paste JD here...")

run_btn = st.button("Run ATS Agent")

tabs = st.tabs(["Cleaned Resume", "Rewritten (ATS-optimized)", "Final (Refined Bullets)", "ATS Evaluation"])

if run_btn:
    if up is None:
        st.error("Please upload a resume file.")
    elif not job_title or not job_desc.strip():
        st.error("Please provide a target job title and job description.")
    else:
        ext, raw_text = detect_and_extract(up.name, up.read())
        if not raw_text.strip():
            st.error("Could not extract any text from the file.")
        else:
            with st.spinner("Running Crew agents..."):
                cleaned, rewritten, final_resume, evaluation = run_pipeline(
                    raw_resume_text=raw_text,
                    job_title=job_title.strip(),
                    job_description=job_desc.strip()
                )

            with tabs[0]:
                st.subheader("Cleaned Resume (plain text)")
                st.code(cleaned, language="markdown")
                st.download_button(
                    "Download cleaned.txt",
                    data=cleaned.encode("utf-8"),
                    file_name="cleaned_resume.txt",
                    mime="text/plain"
                )

            with tabs[1]:
                st.subheader("Rewritten Resume (ATS-optimized)")
                st.code(rewritten, language="markdown")
                st.download_button(
                    "Download rewritten.txt",
                    data=rewritten.encode("utf-8"),
                    file_name="rewritten_resume.txt",
                    mime="text/plain"
                )

            with tabs[2]:
                st.subheader("Final Resume (Refined Bullets)")
                st.code(final_resume, language="markdown")

                # Offer DOCX & TXT downloads
                st.download_button(
                    "Download final.txt",
                    data=final_resume.encode("utf-8"),
                    file_name="final_resume.txt",
                    mime="text/plain"
                )
                try:
                    docx_bytes = txt_to_docx_bytes(final_resume)
                    st.download_button(
                        "Download final.docx",
                        data=docx_bytes,
                        file_name="final_resume.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                except Exception as e:
                    st.warning(f"Could not generate DOCX: {e}")

            with tabs[3]:
                st.subheader("ATS Evaluation & Suggestions")
                # Try to parse evaluation as JSON-like
                parsed = None
                try:
                    # Allow loose JSON (single quotes); try a quick fix
                    text = evaluation.strip()
                    fixed = text.replace("'", '"')
                    parsed = json.loads(fixed)
                except Exception:
                    pass

                if parsed and isinstance(parsed, dict):
                    st.json(parsed)
                    # Pretty headline
                    if "overall_score" in parsed:
                        st.metric("Overall ATS Score", f"{parsed['overall_score']}/100")
                else:
                    st.write("Raw evaluation output:")
                    st.code(evaluation, language="json")
