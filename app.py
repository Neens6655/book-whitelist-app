# 📚 Book Evaluation & Whitelist Report (Streamlit Version)
# ------------------------------------------------------------
# Mirrors your Colab logic but with an upload UI

import streamlit as st
from openai import OpenAI
from PyPDF2 import PdfReader
import json
import os

# ------------------------------------------------------------
# ✅ Setup OpenAI client (reads key from Streamlit secrets)
# ------------------------------------------------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Book Whitelist Evaluator", layout="wide")
st.title("📚 UAE Book Whitelist Evaluator")
st.write("Upload a book file (PDF or TXT), run evaluation, and see whitelist scoring.")

# ------------------------------------------------------------
# ✅ Upload book
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
  "executive_summary": "...",
  "language_complexity": "Low / Moderate / High",
  "domains": {
    "gambling": "...",
    "language": "...",
    "violence_&_terror": "...",
    "alcohol_drugs_smoking": "...",
    "sex_&_nudity": "...",
    "islamic_arab_uae_cultural_ethics": "..."
  },
  "lessons_learned": "...",
  "parent_discussion_guide": {
    "before_reading": ["..."],
    "after_reading": ["..."]
  },
  "age_verdicts": {
    "0-3": "",
    "3-5": "",
    "6-9": "",
    "10-12": "",
    "13-16": "",
    "17+": "",
    "21+": ""
  },
  "recommended_minimum_age": "One group only (e.g., '6-9')",
  "key_drivers": ["..."]
}
"""

# ------------------------------------------------------------
# ✅ Run Evaluation Button
# ------------------------------------------------------------
if book_text:
    if st.button("Run Evaluation"):
        with st.spinner("Evaluating book... this may take a moment..."):
            try:
                response = client.responses.create(
                    model="gpt-4.1",
                    input=evaluation_prompt + "\n\nBOOK TEXT:\n" + book_text[:18000],
                    temperature=0.3
                )

                output = response.output[0].content[0].text

                try:
                    results = json.loads(output)
                except Exception:
                    start, end = output.find("{"), output.rfind("}") + 1
                    results = json.loads(output[start:end])

                # Whitelist scoring
                whitelist_score = 100
                domains = results.get("domains", {})

                def penalty(domain_value):
                    text = str(domain_value).lower()
                    if "moderate" in text: return 15
                    if "high" in text or "severe" in text: return 30
                    return 0

                for v in domains.values():
                    whitelist_score -= penalty(v)

                language_complexity = results.get("language_complexity", "").lower()
                if "high" in language_complexity:
                    whitelist_score -= 15
                elif "moderate" in language_complexity:
                    whitelist_score -= 5

                whitelist_verdict = (
                    "✅ Whitelisted – Safe for general use" if whitelist_score >= 70
                    else "🚫 Not Whitelisted – Requires Review"
                )

                results["whitelist_score"] = whitelist_score
                results["whitelist_verdict"] = whitelist_verdict

                # ------------------------------------------------------------
                # ✅ Display Results
                # ------------------------------------------------------------
                st.subheader("📊 Evaluation Results")
                st.json(results)

                st.markdown(f"### Whitelist Score: **{whitelist_score} / 100**")
                st.markdown(f"### Verdict: **{whitelist_verdict}**")

                st.download_button("⬇️ Download JSON Results", data=json.dumps(results, indent=2), file_name="evaluation_result.json")

            except Exception as e:
                st.error(f"❌ Error during evaluation: {str(e)}")
