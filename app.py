import streamlit as st
from openai import OpenAI
from PyPDF2 import PdfReader
import json

# ------------------------------------------------------------
# ✅ Setup
# ------------------------------------------------------------

# Prevent NameError
book_text = None

# Load OpenAI API key from Streamlit secrets
if "OPENAI_API_KEY" not in st.secrets:
    st.error("⚠️ Missing API key in Streamlit secrets. Please add it in Streamlit Cloud Settings ▸ Secrets.")
    st.stop()

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Book Whitelist Evaluator", page_icon="📚", layout="centered")
st.title("📚 UAE Book Whitelist Evaluator")

st.markdown("""
Upload a children's book (PDF or TXT) and get:
- ✅ Whitelist suitability scoring  
- ✅ Reasons why it is (or isn’t) suitable for kids  
- ✅ Structured evaluation report
""")

# ------------------------------------------------------------
# ✅ Upload book
# ------------------------------------------------------------

uploaded_file = st.file_uploader("Upload a book (PDF or TXT)", t
