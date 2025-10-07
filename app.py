# ------------------------------------------------------------
# ✅ Helper Functions (define BEFORE evaluation block)
# ------------------------------------------------------------
def penalty(domain_value):
    text = str(domain_value).lower()
    if "moderate" in text: 
        return 15
    if "high" in text or "severe" in text: 
        return 30
    return 0

def build_report(results: dict) -> str:
    lines = []
    lines.append(f"📚 Title: {results.get('title','Unknown')}")
    lines.append(f"📊 Score: {results.get('whitelist_score','N/A')} / 100")
    lines.append(f"Verdict: {results.get('whitelist_verdict','N/A')}\n")
    return "\n".join(lines)

# ------------------------------------------------------------
# ✅ STEP 4–7 — Run OpenAI Evaluation
# ------------------------------------------------------------
if book_text is not None:   # prevent NameError if no upload
    if st.button("Run Evaluation"):
        with st.spinner("Evaluating book..."):
            response = client.responses.create(
                model="gpt-4o-mini",  # stable model
                input=evaluation_prompt + "\n\nBOOK TEXT:\n" + book_text,
                temperature=0.3
            )
            output = response.output[0].content[0].text

            try:
                results = json.loads(output)
            except Exception:
                start, end = output.find("{"), output.rfind("}")+1
                results = json.loads(output[start:end])

            # Whitelist scoring
            whitelist_score = 100
            for v in results.get("domains", {}).values():
                whitelist_score -= penalty(v)

            lc = results.get("language_complexity", "").lower()
            if "high" in lc: whitelist_score -= 15
            elif "moderate" in lc: whitelist_score -= 5

            verdict = "✅ Whitelisted – Safe" if whitelist_score >= 70 else "🚫 Requires Review"
            results["whitelist_score"], results["whitelist_verdict"] = whitelist_score, verdict

            # Display
            st.subheader("📊 Whitelist Report")
            st.metric("Score", f"{whitelist_score}/100")
            st.write(f"Verdict: {verdict}")

            st.subheader("📝 Executive Summary")
            st.write(results.get("executive_summary","N/A"))

            st.subheader("🎓 Language Complexity")
            st.write(results.get("language_complexity","N/A"))

            st.subheader("🌟 Lessons Learned")
            st.write(results.get("lessons_learned","N/A"))

            st.subheader("👨‍👩‍👧 Parent Discussion Guide")
            st.json(results.get("parent_discussion_guide", {}))

            st.subheader("🎯 Age Recommendations")
            st.json(results.get("age_verdicts", {}))

            st.subheader("🔑 Key Drivers")
            st.write(results.get("key_drivers", []))

            # Download
            st.download_button("⬇️ Download JSON",
                data=json.dumps(results, ensure_ascii=False, indent=2),
                file_name="evaluation_result.json"
            )
            st.download_button("⬇️ Download Report (TXT)",
                data=build_report(results),
                file_name="executive_report.txt"
            )
else:
    st.info("📥 Please upload a PDF or TXT file to start.")
