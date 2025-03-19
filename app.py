import streamlit as st
import sqlite3
import pandas as pd
import qrcode
from io import BytesIO
import base64

# Database Setup
def init_db():
    conn = sqlite3.connect("library.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS books (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 title TEXT,
                 author TEXT,
                 year INTEGER,
                 category TEXT,
                 cover BLOB,
                 qr_code BLOB)''')
    conn.commit()
    conn.close()

# Insert Book
def add_book(title, author, year, category, cover):
    conn = sqlite3.connect("library.db")
    c = conn.cursor()
    qr_code_img = generate_qr_code(title)
    c.execute("INSERT INTO books (title, author, year, category, cover, qr_code) VALUES (?, ?, ?, ?, ?, ?)",
              (title, author, year, category, cover, qr_code_img))
    conn.commit()
    conn.close()

# Get Books
def get_books():
    conn = sqlite3.connect("library.db")
    df = pd.read_sql_query("SELECT * FROM books", conn)
    conn.close()
    return df

# Delete Book
def delete_book(book_id):
    conn = sqlite3.connect("library.db")
    c = conn.cursor()
    c.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()

# Generate QR Code
def generate_qr_code(data):
    qr = qrcode.make(data)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    return buffer.getvalue()

# Streamlit UI
st.set_page_config(page_title="📚 Personal Library Manager", layout="wide")
st.title("📚 Personal Library Manager")

init_db()

tab1, tab2 = st.tabs(["Add Book", "View Library"])

with tab1:
    st.header("📖 Add a New Book")
    title = st.text_input("Book Title")
    author = st.text_input("Author")
    year = st.number_input("Publication Year", min_value=1000, max_value=2100, step=1)
    category = st.text_input("Category")
    cover_image = st.file_uploader("Upload Book Cover", type=["png", "jpg", "jpeg"])
    
    if st.button("Add Book"):
        if title and author and category and cover_image:
            cover_bytes = cover_image.read()
            add_book(title, author, year, category, cover_bytes)
            st.success("✅ Book added successfully!")
        else:
            st.error("⚠️ Please fill all fields and upload a cover image.")

with tab2:
    st.header("📚 Library Collection")
    books_df = get_books()
    
    if not books_df.empty:
        st.dataframe(books_df[['id', 'title', 'author', 'year', 'category']])
        book_id = st.number_input("Enter Book ID to Delete", min_value=1, step=1)
        if st.button("Delete Book"):
            delete_book(book_id)
            st.success("🗑️ Book deleted successfully!")
    else:
        st.info("📭 No books in the library.")
