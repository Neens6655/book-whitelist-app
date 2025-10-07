import streamlit as st
import requests

# ------------------------------------------------------------
# ✅ Page Config
# ------------------------------------------------------------
st.set_page_config(page_title="Book Whitelist Marketplace", layout="wide")

AIRTABLE_BASE_ID = st.secrets["AIRTABLE_BASE_ID"]
AIRTABLE_TABLE_ID = st.secrets["AIRTABLE_TABLE_ID"]
AIRTABLE_API_KEY = st.secrets["AIRTABLE_API_KEY"]

# ------------------------------------------------------------
# ✅ Hero Section
# ------------------------------------------------------------
st.markdown("""
<style>
.hero {
  background: linear-gradient(135deg, #007BFF 0%, #00C9A7 100%);
  color: white;
  padding: 60px 30px;
  border-radius: 15px;
  text-align: center;
  margin-bottom: 40px;
}
.hero h1 {
  font-size: 48px;
  margin-bottom: 10px;
}
.hero p {
  font-size: 20px;
  margin-bottom: 20px;
}
.hero .btn {
  display: inline-block;
  margin: 0 10px;
  padding: 12px 24px;
  border-radius: 8px;
  background: white;
  color: #007BFF;
  font-weight: bold;
  text-decoration: none;
}
.hero .btn.green {
  background: #28a745;
  color: white;
}
.hero .btn.purple {
  background: #6f42c1;
  color: white;
}
</style>

<div class="hero">
  <h1>Protecting Young Minds</h1>
  <p>Over 1,000 children’s books reviewed for Islamic values, UAE culture, and educational quality</p>
  <a href="#books" class="btn">📚 Browse Books</a>
  <a href="#upload" class="btn green">➕ Add Book</a>
  <a href="#ai" class="btn purple">🤖 AI Assessment</a>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# ✅ Fetch from Airtable
# ------------------------------------------------------------
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

# ------------------------------------------------------------
# ✅ Book Detail Page (Secondary View)
# ------------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "catalog"
if "selected_book" not in st.session_state:
    st.session_state.selected_book = None

if st.session_state.page == "detail" and st.session_state.selected_book:
    book = st.session_state.selected_book
    fields = book.get("fields", {})

    st.markdown("### 📖 Book Detail")
    st.image(fields.get("cover_url", ""), width=300)
    st.title(fields.get("title", "Untitled"))
    st.write(f"**Score:** {fields.get('whitelist_score', 'N/A')}")
    st.write(f"**Verdict:** {fields.get('whitelist_verdict', 'N/A')}")
    st.write(f"**Language Complexity:** {fields.get('language_complexity', 'N/A')}")

    st.subheader("📝 Executive Summary")
    st.write(fields.get("executive_summary", "N/A"))

    if st.button("⬅ Back to Catalog"):
        st.session_state.page = "catalog"
        st.experimental_rerun()

else:
    # ------------------------------------------------------------
    # ✅ Catalog Section
    # ------------------------------------------------------------
    st.markdown("## 📚 Approved Books Catalog", unsafe_allow_html=True)

    # CSS for grid layout
    st.markdown("""
    <style>
    .card-grid {
      display: flex;
      flex-wrap: wrap;
      gap: 20px;
    }
    .card {
      flex: 1 1 calc(30% - 20px);
      background: #fff;
      border-radius: 15px;
      padding: 20px;
      box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
      min-width: 280px;
      max-width: 350px;
      cursor: pointer;
      transition: transform 0.2s;
    }
    .card:hover {
      transform: translateY(-5px);
      box-shadow: 0px 8px 16px rgba(0,0,0,0.12);
    }
    .card img {
      width: 100%;
      border-radius: 10px;
      margin-bottom: 10px;
    }
    .card h3 {
      margin: 0;
      color: #222;
    }
    .card p {
      margin: 5px 0;
      color: #555;
    }
    .score {
      font-weight: bold;
      color: #007BFF;
    }
    .verdict {
      font-weight: bold;
      color: #28a745;
    }
    .verdict-bad {
      font-weight: bold;
      color: #dc3545;
    }
    </style>
    """, unsafe_allow_html=True)

    # Render grid
    st.markdown('<div class="card-grid">', unsafe_allow_html=True)
    for record in books:
        fields = record.get("fields", {})
        title = fields.get("title", "Untitled")
        summary = fields.get("executive_summary", "")
        score = fields.get("whitelist_score", "N/A")
        verdict = fields.get("whitelist_verdict", "N/A")
        cover = fields.get("cover_url", None)

        card_html = f"""
        <div class="card" onclick="window.location.reload()">
            {'<img src="'+cover+'" />' if cover else ''}
            <h3>{title}</h3>
            <p>{summary[:120]}...</p>
            <p class="score">Score: {score}</p>
            <p class='{"verdict" if "✅" in verdict else "verdict-bad"}'>{verdict}</p>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

        # Make card clickable using Streamlit button
        if st.button(f"View {title}"):
            st.session_state.page = "detail"
            st.session_state.selected_book = record
            st.experimental_rerun()

    st.markdown('</div>', unsafe_allow_html=True)
