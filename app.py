import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import pdfplumber
from pdf2image import convert_from_path
import pytesseract

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# PVS LINE


def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        if text.strip():
            return text.strip()
    except Exception as e:
        print("Error extracting text with pdfplumber:", e)

    try:
        images = convert_from_path(
            pdf_path,
            poppler_path=(
                r"C:\Users\SUGANDHA SAWHNEY\Documents"
                r"\poppler-24.04.0\Library\bin"
            )
        )
        for image in images:
            text += pytesseract.image_to_string(image) + "\n"
    except Exception as e:
        print("Error extracting text with OCR:", e)

    return text.strip()


def analyze_resume(resume_text, job_description=None):
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = (
        "You are a hiring expert. Evaluate the resume below.\n"
        "- Identify skills, strengths, weaknesses.\n"
        "- Suggest improvements & course recommendations.\n"
        "- Compare with job description if provided.\n\n"
        f"Resume:\n{resume_text}"
    )
    if job_description:
        prompt += f"\n\nJob Description:\n{job_description}"
    response = model.generate_content(prompt)
    return response.text.strip()


# --- Page Settings ---
st.set_page_config(page_title="Aspirobot Resume Analyzer", layout="centered")

# --- Custom CSS ---
st.markdown(
    """
    <style>
    @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap'
    );

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #0f0e1f;
        color: white;
    }
    .title {
        text-align: center;
        font-size: 38px;
        font-weight: 700;
        margin-bottom: 5px;
        background: linear-gradient(to right, #d38bff, #533bea);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .subtitle {
        text-align: center;
        font-size: 16px;
        color: #cccccc;
        margin-bottom: 40px;
    }
    .card {
        background: rgba(28, 27, 58, 0.85);
        border-radius: 16px;
        padding: 30px;
        box-shadow: 0 0 30px rgba(0,0,0,0.3);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
    }
    .stTextArea textarea, .stTextInput input {
        background-color: #25244a !important;
        color: white !important;
        border-radius: 10px !important;
    }
    .stButton > button {
        background: linear-gradient(to right, #6a5af9, #8c3eff);
        color: white;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        filter: brightness(1.15);
        transform: scale(1.02);
    }
    .result-box {
        background-color: #1f1f3f;
        padding: 20px;
        margin-top: 20px;
        border-radius: 12px;
        color: #eee;
        white-space: pre-wrap;
        box-shadow: 0 0 15px rgba(0,0,0,0.4);
    }
    footer {
        text-align: center;
        color: #888;
        padding-top: 40px;
        font-size: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- UI ---
st.markdown("<div class='title'>Resume Analyzer</div>", unsafe_allow_html=True)

st.markdown(
    (
        "<div class='subtitle'>Upload your resume, and get "
        "AI-powered insights on your career path.</div>"
    ),
    unsafe_allow_html=True
)

# --- Upload Section ---
uploaded_file = st.file_uploader(
    "📄 Upload your Resume (PDF only)",
    type=["pdf"]
)

job_description = st.text_area(
    "💼 Paste Job Description (Optional)",
    height=150
)

# --- Process ---
if uploaded_file:
    with open("resume.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    resume_text = extract_text_from_pdf("resume.pdf")

    if st.button("🔍 Analyze Resume"):
        with st.spinner("Analyzing resume with Gemini..."):
            try:
                output = analyze_resume(resume_text, job_description)
                st.markdown("<div class='result-box'>", unsafe_allow_html=True)
                st.markdown(output)
                st.markdown("</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Analysis failed: {e}")
else:
    st.info("Please upload a PDF resume to begin.")

# --- Footer ---
st.markdown(
    "<footer>Made with 💜 by Aspirobot • Powered by Google Gemini</footer>",
    unsafe_allow_html=True
)
