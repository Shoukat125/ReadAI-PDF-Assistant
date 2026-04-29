from flask import Flask, request, jsonify, render_template, session, redirect, url_for, send_from_directory
from dotenv import load_dotenv
from groq import Groq
import httpx
import webbrowser
import os
import json
import bcrypt
import logging
from database import (
    init_db, get_all_books, get_book_by_id, delete_book,
    save_reading_record, get_last_read_page, get_total_pages_read,
    save_summary, get_summaries, get_dashboard_stats,
    get_admin_password, set_admin_password
)
from pdf_processor import (
    process_and_register_pdf, get_page_content,
    get_pages_content, get_total_pages,
    delete_pdf_file, validate_pdf
)
from bot import generate_summary, answer_question

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "readai_secret_2024")

LOG_FILE = "readai.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.1-8b-instant")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

client = Groq(
    api_key=GROQ_API_KEY,
    http_client=httpx.Client()
)

# ==========================================
# INITIALIZE DATABASE
# ==========================================
init_db()

if not get_admin_password():
    hashed = bcrypt.hashpw(ADMIN_PASSWORD.encode(), bcrypt.gensalt()).decode()
    set_admin_password(hashed)

# ==========================================
# PASSWORD UTILS
# ==========================================
def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def login_required():
    return not session.get("logged_in")

# ==========================================
# ROUTES — MAIN
# ==========================================
@app.route("/")
def index():
    if login_required():
        return redirect(url_for("login"))
    stats = get_dashboard_stats()
    books = get_all_books()
    return render_template("index.html", stats=stats, books=books)

# ==========================================
# ROUTES — AUTH
# ==========================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password", "")
        hashed = get_admin_password()
        if hashed and check_password(password, hashed):
            session["logged_in"] = True
            return redirect(url_for("index"))
        return render_template("login.html", error="❌ Incorrect password!")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))

# ==========================================
# ROUTES — LIBRARY
# ==========================================
@app.route("/library")
def library():
    if login_required():
        return redirect(url_for("login"))
    books = get_all_books()
    return render_template("library.html", books=books)

@app.route("/upload-book", methods=["POST"])
def upload_book():
    if login_required():
        return redirect(url_for("login"))

    file = request.files.get("pdf")
    title = request.form.get("title", "").strip()
    subject = request.form.get("subject", "").strip()

    if not file or not title:
        books = get_all_books()
        return render_template("library.html", books=books,
                               error="❌ Title aur PDF dono zaroori hain!")

    is_valid, error_msg = validate_pdf(file)
    if not is_valid:
        books = get_all_books()
        return render_template("library.html", books=books, error=f"❌ {error_msg}")

    filename = file.filename.replace(" ", "_")
    book_id = process_and_register_pdf(file, filename, title, subject)

    if book_id:
        books = get_all_books()
        return render_template("library.html", books=books,
                               success=f"✅ '{title}' successfully upload ho gayi!")
    else:
        books = get_all_books()
        return render_template("library.html", books=books,
                               error="❌ PDF upload failed. Please try again.")

@app.route("/delete-book/<int:book_id>", methods=["POST"])
def delete_book_route(book_id):
    if login_required():
        return redirect(url_for("login"))
    book = get_book_by_id(book_id)
    if book:
        delete_pdf_file(book[2])
        delete_book(book_id)
    return redirect(url_for("library"))

# ==========================================
# ROUTES — READER
# ==========================================
@app.route("/reader/<int:book_id>")
def reader(book_id):
    if login_required():
        return redirect(url_for("login"))
    book = get_book_by_id(book_id)
    if not book:
        return redirect(url_for("library"))
    last_page = get_last_read_page(book_id)
    total_pages = get_total_pages(book_id)
    all_books = get_all_books()
    return render_template("reader.html",
                           book=book,
                           last_page=last_page,
                           total_pages=total_pages,
                           all_books=all_books)

@app.route("/api/get-page", methods=["POST"])
def api_get_page():
    if login_required():
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json()
    book_id = data.get("book_id")
    page_number = data.get("page_number", 1)
    content = get_page_content(book_id, page_number)
    if content is None:
        return jsonify({"error": "Page not found"}), 404
    save_reading_record(book_id, page_number)
    return jsonify({"page_number": page_number, "content": content})

# ==========================================
# ROUTES — SUMMARY
# ==========================================
@app.route("/summary/<int:book_id>")
def summary_page(book_id):
    if login_required():
        return redirect(url_for("login"))
    book = get_book_by_id(book_id)
    if not book:
        return redirect(url_for("library"))
    total_pages = get_total_pages(book_id)
    summaries = get_summaries(book_id)
    return render_template("summary.html",
                           book=book,
                           total_pages=total_pages,
                           summaries=summaries)

@app.route("/api/generate-summary", methods=["POST"])
def api_generate_summary():
    if login_required():
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json()
    book_id = data.get("book_id")
    page_from = int(data.get("page_from", 1))
    page_to = int(data.get("page_to", 1))
    if page_from > page_to:
        return jsonify({"error": "Page from must be less than page to"}), 400
    summary = generate_summary(book_id, page_from, page_to, client, MODEL_NAME)
    save_summary(book_id, page_from, page_to, summary)
    return jsonify({"summary": summary})

# ==========================================
# ROUTES — Q&A
# ==========================================
@app.route("/api/ask", methods=["POST"])
def api_ask():
    if login_required():
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json()
    book_id = data.get("book_id")
    page_from = int(data.get("page_from", 1))
    page_to = int(data.get("page_to", 1))
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "Question is empty"}), 400
    answer = answer_question(book_id, page_from, page_to, question, client, MODEL_NAME)
    return jsonify({"answer": answer})

# ==========================================
# ROUTES — CHANGE PASSWORD
# ==========================================
@app.route("/change-password", methods=["POST"])
def change_password():
    if login_required():
        return redirect(url_for("login"))
    old_password = request.form.get("old_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")
    hashed = get_admin_password()
    stats = get_dashboard_stats()
    books = get_all_books()
    if not check_password(old_password, hashed):
        return render_template("index.html", stats=stats, books=books,
                               pw_error="❌ Old password is incorrect!")
    if new_password != confirm_password:
        return render_template("index.html", stats=stats, books=books,
                               pw_error="❌ Passwords do not match!")
    if len(new_password) < 6:
        return render_template("index.html", stats=stats, books=books,
                               pw_error="❌ Minimum 6 characters required!")
    set_admin_password(hash_password(new_password))
    return render_template("index.html", stats=stats, books=books,
                           pw_success="✅ Password updated successfully!")

# ==========================================
# SERVE UPLOADED PDFs
# ==========================================
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory("uploads", filename)

# ==========================================
# RUN APP
# ==========================================
if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        webbrowser.open("http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
