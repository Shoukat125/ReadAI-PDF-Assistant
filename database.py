import sqlite3
import os

DB_FILE = "instance/readai.db"

# ==========================================
# DATABASE INITIALIZE
# ==========================================
def init_db():
    os.makedirs("instance", exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # --- Books Table ---
    c.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            filename TEXT NOT NULL,
            subject TEXT,
            total_pages INTEGER DEFAULT 0,
            uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # --- Reading History Table ---
    c.execute('''
        CREATE TABLE IF NOT EXISTS reading_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            page_number INTEGER NOT NULL,
            read_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (book_id) REFERENCES books(id)
        )
    ''')

    # --- Summaries Table ---
    c.execute('''
        CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            page_from INTEGER,
            page_to INTEGER,
            summary_text TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (book_id) REFERENCES books(id)
        )
    ''')

    # --- Pages Table (PyMuPDF extracted, used for RAG + Reader) ---
    c.execute('''
        CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            page_number INTEGER NOT NULL,
            content TEXT,
            FOREIGN KEY (book_id) REFERENCES books(id)
        )
    ''')
    c.execute('''
        CREATE INDEX IF NOT EXISTS idx_pages_book_page
        ON pages (book_id, page_number)
    ''')

    # --- Admin Table ---
    c.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            password TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")


# ==========================================
# BOOKS — CRUD
# ==========================================
def add_book(title, filename, subject, total_pages):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO books (title, filename, subject, total_pages) VALUES (?, ?, ?, ?)",
        (title, filename, subject, total_pages)
    )
    book_id = c.lastrowid
    conn.commit()
    conn.close()
    return book_id


def get_all_books():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM books ORDER BY uploaded_at DESC")
    books = c.fetchall()
    conn.close()
    return books


def get_book_by_id(book_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM books WHERE id = ?", (book_id,))
    book = c.fetchone()
    conn.close()
    return book


def delete_book(book_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM books WHERE id = ?", (book_id,))
    c.execute("DELETE FROM reading_history WHERE book_id = ?", (book_id,))
    c.execute("DELETE FROM summaries WHERE book_id = ?", (book_id,))
    c.execute("DELETE FROM pages WHERE book_id = ?", (book_id,))
    conn.commit()
    conn.close()


# ==========================================
# PAGES — CRUD (PyMuPDF + RAG)
# ==========================================
def save_pages(book_id, pages):
    """pages = list of {page_number, content}"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.executemany(
        "INSERT INTO pages (book_id, page_number, content) VALUES (?, ?, ?)",
        [(book_id, p["page_number"], p["content"]) for p in pages]
    )
    conn.commit()
    conn.close()


def get_page_from_db(book_id, page_number):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "SELECT content FROM pages WHERE book_id = ? AND page_number = ?",
        (book_id, page_number)
    )
    result = c.fetchone()
    conn.close()
    return result[0] if result else None


def get_pages_range_from_db(book_id, page_from, page_to):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "SELECT page_number, content FROM pages WHERE book_id = ? AND page_number BETWEEN ? AND ? ORDER BY page_number",
        (book_id, page_from, page_to)
    )
    rows = c.fetchall()
    conn.close()
    return rows


def get_all_pages_from_db(book_id):
    """BM25 ke liye saari pages load karo"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "SELECT page_number, content FROM pages WHERE book_id = ? ORDER BY page_number",
        (book_id,)
    )
    rows = c.fetchall()
    conn.close()
    return rows


def pages_exist_in_db(book_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT 1 FROM pages WHERE book_id = ? LIMIT 1", (book_id,))
    result = c.fetchone()
    conn.close()
    return result is not None


# ==========================================
# READING HISTORY — CRUD
# ==========================================
def save_reading_record(book_id, page_number):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO reading_history (book_id, page_number) VALUES (?, ?)",
        (book_id, page_number)
    )
    conn.commit()
    conn.close()


def get_last_read_page(book_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "SELECT page_number FROM reading_history WHERE book_id = ? ORDER BY read_at DESC LIMIT 1",
        (book_id,)
    )
    result = c.fetchone()
    conn.close()
    return result[0] if result else 1


def get_total_pages_read(book_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "SELECT COUNT(DISTINCT page_number) FROM reading_history WHERE book_id = ?",
        (book_id,)
    )
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0


# ==========================================
# SUMMARIES — CRUD
# ==========================================
def save_summary(book_id, page_from, page_to, summary_text):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO summaries (book_id, page_from, page_to, summary_text) VALUES (?, ?, ?, ?)",
        (book_id, page_from, page_to, summary_text)
    )
    conn.commit()
    conn.close()


def get_summaries(book_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "SELECT * FROM summaries WHERE book_id = ? ORDER BY created_at DESC",
        (book_id,)
    )
    summaries = c.fetchall()
    conn.close()
    return summaries


# ==========================================
# DASHBOARD STATS
# ==========================================
def get_dashboard_stats():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM books")
    total_books = c.fetchone()[0]

    c.execute("SELECT COUNT(DISTINCT page_number || '-' || book_id) FROM reading_history")
    total_pages_read = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM summaries")
    total_summaries = c.fetchone()[0]

    c.execute("""
        SELECT COUNT(DISTINCT page_number || '-' || book_id)
        FROM reading_history
        WHERE read_at >= datetime('now', '-7 days')
    """)
    weekly_pages = c.fetchone()[0]

    conn.close()

    return {
        "total_books": total_books,
        "total_pages_read": total_pages_read,
        "total_summaries": total_summaries,
        "weekly_pages": weekly_pages
    }


# ==========================================
# ADMIN — CRUD
# ==========================================
def get_admin_password():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT password FROM admin LIMIT 1")
    result = c.fetchone()
    conn.close()
    return result[0] if result else None


def set_admin_password(hashed_password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM admin")
    c.execute("INSERT INTO admin (password) VALUES (?)", (hashed_password,))
    conn.commit()
    conn.close()


# ==========================================
# RUN DIRECTLY — TEST
# ==========================================
if __name__ == "__main__":
    init_db()
    print("✅ All tables created successfully!")
    print("📊 Dashboard Stats:", get_dashboard_stats())
