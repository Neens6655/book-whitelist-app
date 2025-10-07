# ============================================================
# 📚 Book Evaluation & Whitelist Report (Streamlit Version)
# Mirrors your Colab logic with minimal UI wrappers
# ============================================================

import streamlit as st
from openai import OpenAI
from PyPDF2 import PdfReader
import json

# ------------------------------------------------------------
# ✅ STEP 1 — Setup OpenAI Client (uses Streamlit Secrets)
# ------------------------------------------------------------
st.set_page_config(page_title="Book Whitelist Evaluator", layout="wide")
st.title("📚 Book Evaluation & Whitelist Report Generator")

if "OPENAI_API_KEY" not in st.secrets:
    st.error("Missing OPENAI_API_KEY in Streamlit Secrets. Add it in Streamlit Cloud → App → Settings → Secrets.")
    st.stop()

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ------------------------------------------------------------
# ✅ STEP 2 — Upload & Load Book File (same extraction logic)
# ------------------------------------------------------------
uploaded_file = st.file_uploader("Upload a PDF or TXT book", type=["pdf", "txt"])

def load_book(file):
    if file.name.lower().endswith(".pdf"):
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
    else:
        text = file.read().decode("utf-8", errors="ignore")
    return text[:18000]  # safety cutoff identical to your Colab

book_text = None
if uploaded_file:
    st.success(f"✅ File uploaded: {uploaded_file.name}")
    book_text = load_book(uploaded_file)
    st.info(f"Loaded {len(book_text)} characters from the book.")

# ------------------------------------------------------------
# ✅ STEP 3 — Build Evaluation Prompt (unchanged)
# ------------------------------------------------------------
evaluation_prompt = """
You are a content and literacy evaluator for the UAE Ministry of Education.
You will evaluate a children's or family book based on its content, complexity, and cultural ethics.

Return a detailed JSON with these fields:
{
  "title": "Book Title",
  "executive_summary": "Concise overview of the story, its themes, and tone.",
  "language_complexity": "Low / Moderate / High based on vocabulary, sentence structure, and readability.",
  "domains": {
    "gambling": "...",
    "language": "...",
    "violence_&_terror": "...",
    "alcohol_drugs_smoking": "...",
    "sex_&_nudity": "...",
    "islamic_arab_uae_cultural_ethics": "..."
  },
  "lessons_learned": "List the moral or educational takeaways for children or families.",
  "parent_discussion_guide": {
    "before_reading": ["Question 1", "Question 2", "Question 3"],
    "after_reading": ["Question 1", "Question 2", "Question 3", "Question 4"]
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
  "key_drivers": ["List of reasons behind the classification"]
}

Now, perform the evaluation carefully in both English and Arabic books.
Adjust the age recommendations based on:
- Plot and theme complexity
- Vocabulary difficulty
- Reading comprehension expected
- Sensitivity to violence or ethics
Return complete JSON output only.
"""

# ------------------------------------------------------------
# ✅ STEP 4–7 — Run OpenAI Evaluation, Score, Report (same logic)
# ------------------------------------------------------------
def compute_penalty(domain_value: str) -> int:
    t = str(domain_value or "").lower()
    if "high" in t or "severe" in t:
        return 30
    if "moderate" in t:
        return 15
    return 0

def build_report(results: dict) -> str:
    nl = "\n"
    pdg = results.get("parent_discussion_guide", {}) or {}
    before = pdg.get("before_reading", []) or []
    after = pdg.get("after_reading", []) or []
    ages = results.get("age_verdicts", {}) or {}

    lines = []
    lines.append(f"📚 Book Title: {results.get('title', 'Unknown')}{nl}")
    lines.append(f"📊 Whitelist Score: {results.get('whitelist_score', 'N/A')} / 100")
    lines.append(f"Verdict: {results.get('whitelist_verdict', 'N/A')}{nl}")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("📝 Executive Summary")
    lines.append(results.get('executive_summary', 'No summary available.') + nl)
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("🎓 Language Complexity")
    lines.append(results.get('language_complexity', 'N/A') + nl)
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("🌟 Lessons Learned")
    lines.append(results.get('lessons_learned', 'No lessons found.') + nl)
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("👨‍👩‍👧 Parent Discussion Guide")
    if before:
        lines.append("Before Reading:")
        lines += [f"- {q}" for q in before]
    if after:
        lines.append("After Reading:")
        lines += [f"- {q}" for q in after]
    lines.append(nl + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("🎯 Age Recommendations")
    lines.append(f"Recommended Minimum Age: {results.get('recommended_minimum_age', 'N/A')}")
    for k, v in ages.items():
        lines.append(f"{k}: {v}")
    lines.append(nl + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("🔑 Key Drivers")
    for d in results.get("key_drivers", []):
        lines.append(f"- {d}")
    lines.append(nl + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" + nl)
    return nl.join(lines)

if book_text:
    if st.button("Run Evaluation"):
        with st.spinner("Evaluating book..."):
            response = client.responses.create(
                model="gpt-4.1",
                input=evaluation_prompt + "\n\nBOOK TEXT:\n" + book_text,
                temperature=0.3
            )
            # robust JSON slice if model wraps output
            output = response.output[0].content[0].text
            try:
                results = json.loads(output)
            except Exception:
                start = output.find("{")
                end = output.rfind("}") + 1
                results = json.loads(output[start:end])

            # Whitelist score (same as Colab)
            whitelist_score = 100
            for v in (results.get("domains") or {}).values():
                whitelist_score -= compute_penalty(v)

            lc = (results.get("language_complexity") or "").lower()
            if "high" in lc:
                whitelist_score -= 15
            elif "moderate" in lc:
                whitelist_score -= 5

            verdict = "✅ Whitelisted – Safe for general use" if whitelist_score >= 70 else "🚫 Not Whitelisted – Requires Review"
            results["whitelist_score"] = whitelist_score
            results["whitelist_verdict"] = verdict

            # UI
            st.subheader("📊 Whitelist Summary")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Score", f"{whitelist_score}/100")
            with col2:
                st.write(f"**Verdict:** {verdict}")

            st.subheader("📝 Executive Summary")
            st.write(results.get("executive_summary", "N/A"))

            st.subheader("🎓 Language Complexity")
            st.write(results.get("language_complexity", "N/A"))

            st.subheader("🌟 Lessons Learned")
            st.write(results.get("lessons_learned", "N/A"))

            st.subheader("👨‍👩‍👧 Parent Discussion Guide")
            st.json(results.get("parent_discussion_guide", {}))

            st.subheader("🎯 Age Recommendations")
            st.json(results.get("age_verdicts", {}))

            st.subheader("🔑 Key Drivers")
            st.write(results.get("key_drivers", []))

            # Save & downloads
            report_text = build_report(results)
            st.download_button("⬇️ Download JSON", data=json.dumps(results, ensure_ascii=False, indent=2), file_name="evaluation_result.json")
            st.download_button("⬇️ Download Report (TXT)", data=report_text, file_name="executive_report.txt")

            st.success("Done. Files ready to download above.")
else:
    st.info("Upload a PDF or TXT file to begin.")
