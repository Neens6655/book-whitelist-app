import streamlit as st
import json
import requests
import os
from PyPDF2 import PdfReader

# ------------------------------------------------------------
# ✅ App Config
# ------------------------------------------------------------
st.set_page_config(page_title="Book Whitelist Marketplace", layout="wide")
st.title("📚 Book Whitelist Marketplace")

# Airtable credentials (from Streamlit secrets)
AIRTABLE_API_KEY = st.secrets["AIRTABLE_API_KEY"]
AIRTABLE_BASE_ID = st.secrets["AIRTABLE_BASE_ID"]
AIRTABLE_TABLE_ID = st.secrets["AIRTABLE_TABLE_ID"]

AIRTABLE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}"
HEADERS = {"Authorization": f"Bearer {AIRTABLE_API_KEY}", "Content-Type": "application/json"}

# ------------------------------------------------------------
# ✅ Upload Book Feature
# ------------------------------------------------------------
st.subheader("📤 Upload a New Book")

uploaded_file = st.file_uploader("Upload a book (PDF or TXT)", type=["pdf", "txt"])
book_text = None

if uploaded_file:
    if uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        book_text = ""
        for page in reader.pages:
            book_text += page.extract_text() or ""
    else:
        book_text = uploaded_file.read().decode("utf-8")

    st.success("✅ Book uploaded successfully!")

# ------------------------------------------------------------
# ✅ Run Evaluation (mock for now)
# ------------------------------------------------------------
if book_text:
    if st.button("Run AI Evaluation"):
        st.info("⚡ Running evaluation... please wait")

        # 🔹 Mock evaluation (replace later with OpenAI call)
        results = {
            "title": uploaded_file.name,
            "author": "Unknown Author",
            "executive_summary": book_text[:300] + "...",
            "whitelist_score": 85,
            "whitelist_verdict": "✅ Whitelisted – Safe for general use"
        }

        # Save to Airtable
        payload = {"fields": results}
        r = requests.post(AIRTABLE_URL, headers=HEADERS, data=json.dumps(payload))

        if r.status_code == 200:
            st.success("📊 Book evaluation saved to Airtable!")
        else:
            st.error(f"❌ Error saving to Airtable: {r.text}")

        st.subheader("📖 Evaluation Results")
        st.json(results)

# ------------------------------------------------------------
# ✅ Display Approved Books Catalog
# ------------------------------------------------------------
st.subheader("📚 Approved Books Catalog")

def fetch_books():
    r = requests.get(AIRTABLE_URL, headers=HEADERS)
    if r.status_code == 200:
        return r.json().get("records", [])
    else:
        st.error(f"❌ Error fetching books: {r.text}")
        return []

books = fetch_books()

cols = st.columns(3)  # Display in 3 columns
for i, record in enumerate(books):
    fields = record.get("fields", {})
    with cols[i % 3]:
        st.markdown(f"### {fields.get('title', 'Untitled')}")
        st.write(f"👤 {fields.get('author', 'Unknown')}")
        st.write(f"📊 Score: {fields.get('whitelist_score', 'N/A')} / 100")
        st.write(fields.get("whitelist_verdict", "No verdict"))
        if "executive_summary" in fields:
