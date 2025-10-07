# ============================================================
# ✅ STEP 4–7 — Run OpenAI Evaluation, Score, Report
# ============================================================

if book_text:
    if st.button("Run Evaluation"):
        with st.spinner("Evaluating book..."):
            response = client.responses.create(
                model="gpt-4o-mini",   # ✅ Updated model (instead of "gpt-4.1")
                input=evaluation_prompt + "\n\nBOOK TEXT:\n" + book_text,
                temperature=0.3
            )

            # Extract model output safely
            output = response.output[0].content[0].text

            try:
                results = json.loads(output)
            except Exception:
                start = output.find("{")
                end = output.rfind("}") + 1
                results = json.loads(output[start:end])

            # Whitelist scoring logic (unchanged from your Colab)
            whitelist_score = 100
            def penalty(domain_value):
                text = str(domain_value).lower()
                if "moderate" in text: return 15
                if "high" in text or "severe" in text: return 30
                return 0

            for v in results.get("domains", {}).values():
                whitelist_score -= penalty(v)

            lc = results.get("language_complexity", "").lower()
            if "high" in lc:
                whitelist_score -= 15
            elif "moderate" in lc:
                whitelist_score -= 5

            verdict = "✅ Whitelisted – Safe for general use" if whitelist_score >= 70 else "🚫 Not Whitelisted – Requires Review"
            results["whitelist_score"], results["whitelist_verdict"] = whitelist_score, verdict

            # UI output (cards, metrics, text)
            st.subheader("📊 Whitelist Report")
            st.metric("Whitelist Score", f"{whitelist_score}/100")
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

            # Save outputs + download buttons
            st.download_button(
                "⬇️ Download JSON",
                data=json.dumps(results, ensure_ascii=False, indent=2),
                file_name="evaluation_result.json"
            )
            st.download_button(
                "⬇️ Download Report (TXT)",
                data=json.dumps(results, ensure_ascii=False, indent=2),
                file_name="executive_report.txt"
            )

            st.success("✅ Evaluation complete! Files ready for download.")
else:
    st.info("Upload a PDF or TXT file to begin.")
