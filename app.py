import streamlit as st
from openai import OpenAI
from PyPDF2 import PdfReader
import json

# --- App config ---
st.set_page_config(page_title="Book Whitelist Evaluator", layout="wide")
st.title("📚 Book Evaluation & Whitelist Report")

# --- API key ---
if "OPENAI_API_KEY" not in st.secrets:
    st.error("Missing OPENAI_API_KEY in Streamlit Secrets.")
    st.stop()
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- Upload handling ---
book_text = None   # 👈 define it here so it's never undefined
uploaded_file = st.file_uploader("Upload a PDF or TXT book", type=["pdf","txt"])

def load_book(file):
    if file.name.lower().endswith(".pdf"):
        reader = PdfReader(file)
        text = "".join([page.extract_text() or "" for page in reader.pages])
    else:
        text = file.read().decode("utf-8", errors="ignore")
    return text[:18000]

if uploaded_file:
    book_text = load_book(uploaded_file)
    st.success(f"✅ Loaded {len(book_text)} characters from {uploaded_file.name}")

# --- Only run evaluation if we have text ---
if book_text and st.button("Run Evaluation"):
    with st.spinner("Evaluating book..."):
        response = client.responses.create(
            model="gpt-4o-mini",
            input="...prompt..." + "\n\nBOOK TEXT:\n" + book_text,
            temperature=0.3
        )
        output = response.output[0].content[0].text
        # continue with JSON parsing, scoring, display...
