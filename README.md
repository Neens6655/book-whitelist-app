# Book Whitelist Evaluator (Streamlit)

A Streamlit web app to evaluate children's/family books for language complexity, cultural ethics, and whitelist scoring.

## Run on Streamlit Cloud
- Add secret: `OPENAI_API_KEY`
- App reads uploaded PDF/TXT (first 18k chars), calls OpenAI, computes whitelist score, and lets you download the JSON + report.

## Files
- `app.py` — Streamlit app
- `requirements.txt` — dependencies
