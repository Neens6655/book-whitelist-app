import streamlit as st
import requests
import json
from PyPDF2 import PdfReader
from openai import OpenAI

# ------------------------------------------------------------
# ✅ Setup
# ------------------------------------------------------------
st.set_page_config(page_title="Book Whitelist Marketplace", layout="wide")
st.title("📚 Book Whitelist Marketplace")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

AIRTABLE_BASE_ID = st.secrets["AIRTABLE_BASE_ID"]
AIRTABLE_TABLE_ID = st.secrets["AIRTABLE_TABLE_ID"]
AIRTABLE_API_KEY = st.secrets["AIRTABLE_API_KEY"]

# ------------------------------------------------------------
# ✅ Airtable save function (simple version: only 5 fields)
# ------------------------------------------------------------
def save_to_airtable(fields):
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }

    airtable_record = {
        "fields": {
            "title": fields.get("title", ""),
            "executive_summary": fields.get("executive_summary", ""),
            "language_complexity": fields.get("language_complexity", ""),
            "whitelist_score": fields.get("whitelist_score", 0),
            "whitelist_verdict": fields.get("whitelist_verdict", ""),
        }
    }

    r = requests.post(url, headers=headers, data=json.dumps(airtable_record))
    if r.status_code == 200:
        st.success("✅ Book saved to Airtable!")
    else:
        st.error(f"❌ Error saving to Airtable: {r.text}")


# ------------------------------------------------------------
# ✅ Upload Book
# ------------------------------------------------------------
uploaded_file = st.file_uploader("Upload a book (PDF or TXT)", type=["pdf", "txt"])

book_text = None
if uploaded_file:
    if uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        book_text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    else:
        book_text = uploaded_file.read().decode("utf-8")
    st.success("📖 Book uploaded successfully.")


# ------------------------------------------------------------
# ✅ Evaluation Prompt
# ------------------------------------------------------------
evaluation_prompt = """
You are a content and literacy evaluator for the UAE Ministry of Education.
You will evaluate a children's or family book based on its content, complexity, and cultural ethics.

Return a detailed JSON with these fields:
{
  "title": "Book Title",
  "executive_summary": "Concise overview of the story, its themes, and tone.",
  "language_complexity": "Low / Moderate / High",
  "whitelist_score": 0-100,
  "whitelist_verdict": "✅ Whitelisted – Safe for general use OR 🚫 Not Whitelisted – Requires Review"
}
"""


# ------------------------------------------------------------
# ✅ Run Evaluation
# ------------------------------------------------------------
if book_text:
    if st.button("Run Evaluation"):
        with st.spinner("Evaluating book..."):
            response = client.responses.create(
                model="gpt-4.1",
                input=evaluation_prompt + "\n\nBOOK TEXT:\n" + book_text,
                temperature=0.3
            )

            output = response.output[0].content[0].text

            try:
                results = json.loads(output)
            except:
                start, end = output.find("{"), output.rfind("}") + 1
                results = json.loads(output[start:end])

            # ✅ Show results
            st.subheader("Evaluation Results")
            st.json(results)

            # ✅ Save to Airtable
            if st.button("Approve & Save Book"):
                save_to_airtable(results)


# ------------------------------------------------------------
# ✅ Show Books from Airtable
# ------------------------------------------------------------
st.subheader("📚 Approved Books Catalog")

def fetch_books():
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}"
    headers = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.json().get("records", [])
    else:
        st.error(f"❌ Error fetching books: {r.text}")
        return []

books = fetch_books()

cols = st.columns(3)
for i, record in enumerate(books):
    fields = record["fields"]
    with cols[i % 3]:
        st.markdown(f"### {fields.get('title', 'Untitled')}")
        st.write(fields.get("executive_summary", ""))
        st.write(f"**Language Complexity:** {fields.get('language_complexity', 'N/A')}")
        st.write(f"**Score:** {fields.get('whitelist_score', 'N/A')}")
        st.write(f"**Verdict:** {fields.get('whitelist_verdict', 'N/A')}")
