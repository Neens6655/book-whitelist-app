import streamlit as st
import requests

# Load secrets
AIRTABLE_API_KEY = st.secrets["AIRTABLE_API_KEY"]
BASE_ID = st.secrets["BASE_ID"]
TABLE_NAME = st.secrets["TABLE_NAME"]

# Airtable endpoint
AIRTABLE_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
HEADERS = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}

st.set_page_config(page_title="📚 Book Whitelist Library", layout="wide")
st.title("📚 Book Whitelist Marketplace")

# -----------------------------
# Helper functions
# -----------------------------

def get_books():
    response = requests.get(AIRTABLE_URL, headers=HEADERS)
    if response.status_code == 200:
        return response.json()["records"]
    else:
        st.error(f"Error fetching books: {response.text}")
        return []

def add_book(title, author, summary, score, verdict, approved=False):
    data = {
        "fields": {
            "Title": title,
            "Author": author,
            "Summary": summary,
            "Whitelist Score": score,
            "Verdict": verdict,
            "Approved": approved
        }
    }
    response = requests.post(AIRTABLE_URL, headers=HEADERS, json=data)
    if response.status_code == 200:
        st.success("✅ Book added successfully!")
    else:
        st.error(f"❌ Error adding book: {response.text}")

def update_book(record_id, fields):
    url = f"{AIRTABLE_URL}/{record_id}"
    data = {"fields": fields}
    response = requests.patch(url, headers=HEADERS, json=data)
    if response.status_code == 200:
        st.success("✅ Book updated!")
    else:
        st.error(f"❌ Error updating book: {response.text}")

# -----------------------------
# Upload new book form
# -----------------------------
st.subheader("➕ Add a New Book")
with st.form("book_form"):
    title = st.text_input("Book Title")
    author = st.text_input("Author")
    summary = st.text_area("Summary")
    score = st.slider("Whitelist Score", 0, 100, 50)
    verdict = st.selectbox("Verdict", ["✅ Whitelisted – Safe", "❌ Not Approved"])
    approved = st.checkbox("Approve this book")
    submitted = st.form_submit_button("Add Book")
    if submitted:
        add_book(title, author, summary, score, verdict, approved)

# -----------------------------
# Display all approved books
# -----------------------------
st.subheader("📖 Approved Books Catalog")
books = get_books()

cols = st.columns(3)
i = 0
for book in books:
    fields = book["fields"]
    if fields.get("Approved"):
        with cols[i % 3]:
            st.markdown(f"### {fields.get('Title', 'Untitled')}")
            st.write(f"👤 {fields.get('Author', 'Unknown')}")
            st.write(f"📊 Score: {fields.get('Whitelist Score', 0)} / 100")
            st.write(f"📝 {fields.get('Verdict', '')}")
            st.caption(fields.get("Summary", ""))

            # Show cover if exists
            if "Cover" in fields:
                img_url = fields["Cover"][0]["url"]
                st.image(img_url, use_container_width=True)

            # Button to unapprove
            if st.button(f"Unapprove {fields.get('Title')}", key=book["id"]):
                update_book(book["id"], {"Approved": False})

        i += 1
