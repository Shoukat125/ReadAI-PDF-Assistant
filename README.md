# 📚 READ AI — Intelligent PDF Reading Assistant

<div align="center">

![ReadAI Banner](https://img.shields.io/badge/READ%20AI-PDF%20Assistant-orange?style=for-the-badge&logo=bookstack&logoColor=white)

[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.x-black?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Groq](https://img.shields.io/badge/Groq-LLM-red?style=flat-square&logo=groq&logoColor=white)](https://groq.com)
[![SQLite](https://img.shields.io/badge/SQLite-Database-blue?style=flat-square&logo=sqlite&logoColor=white)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)]()
[![Made By](https://img.shields.io/badge/Made%20by-Shoukat%20Ali-purple?style=flat-square)](https://github.com/Shoukat125)

**Upload. Read. Summarize. Chat — All Powered by AI 🤖**

[🌐 Live Demo](#) · [📸 Screenshots](#screenshots) · [🚀 Quick Start](#quick-start) · [📬 Contact](#contact)

</div>

---

## 🧠 What is READ AI?

**READ AI** is a full-stack AI-powered PDF reading assistant built for **students**, **teachers**, and **researchers**. Simply upload any PDF and instantly:

- 📖 Read it **page by page** in a clean reader
- 📝 Generate **AI-powered summaries** for any page range
- 🤖 **Chat with your document** using an intelligent chatbot
- 🔍 Get **smart answers** using BM25-based RAG search
- 🌐 Supports both **Urdu & English** languages

---

## ✨ Features

| Feature | Description |
|--------|-------------|
| 📄 **PDF Upload & Reader** | Upload any PDF and read page by page with smooth navigation |
| 📝 **AI Summary Generator** | Generate detailed summaries for any custom page range |
| 🤖 **ReadAI Chatbot** | Chat with your document — Current Page or Full Book mode |
| 🔍 **BM25 RAG Search** | Vectorless intelligent search to find relevant content |
| 🌐 **Bilingual Support** | Auto-detects Urdu & English and responds accordingly |
| 📊 **Reading Dashboard** | Track total books, pages read, summaries & weekly progress |
| 🔐 **Secure Admin Login** | bcrypt-hashed password authentication |
| 🌙 **Dark / Light Theme** | Toggle between beautiful dark and light modes |
| 📚 **Reading History** | Automatically saves your last read page |
| 🗑️ **Library Management** | Upload, view, and delete books easily |

---

## 🛠️ Tech Stack

```
Backend       → Python, Flask
AI / LLM      → Groq API (Llama 3.1 8B Instant)
PDF Processing → PyMuPDF (fitz)
RAG Search    → BM25 (rank-bm25)
Database      → SQLite
Security      → bcrypt
Frontend      → HTML, CSS, JavaScript (Jinja2 Templates)
Logging       → Python logging module
```

---

## 📸 Screenshots

### 🏠 Dashboard
> Overview of your reading stats and library

![Dashboard](screenshots/dashboard.png)

### 📚 Library
> Upload and manage your PDF books

![Library](screenshots/library.png)

### 📖 Reader
> Read PDF page by page with AI chat sidebar

![Reader](screenshots/reader.png)

### 📝 Summary
> Generate AI summaries for any page range

![Summary](screenshots/summary.png)

### 💬 ReadAI Chat
> Chat with your document intelligently

![Chat](screenshots/chat.png)

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Shoukat125/ReadAI-PDF-Assistant.git
cd ReadAI-PDF-Assistant
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Create `.env` File
```env
GROQ_API_KEY=your_groq_api_key_here
SECRET_KEY=readai_secret_2024
MODEL_NAME=llama-3.1-8b-instant
ADMIN_PASSWORD=admin123
```

> 🔑 Get your free Groq API key at [console.groq.com](https://console.groq.com)

### 4. Run the App
```bash
python app.py
```

### 5. Open in Browser
```
http://127.0.0.1:5000
```

---

## 📁 Project Structure

```
ReadAI-PDF-Assistant/
│
├── app.py                  # Main Flask application & routes
├── bot.py                  # AI chatbot & summary generator
├── database.py             # SQLite database operations
├── pdf_processor.py        # PDF extraction & BM25 RAG search
├── requirements.txt        # Python dependencies
├── .gitignore              # Git ignore rules
│
├── templates/              # HTML templates (Jinja2)
│   ├── index.html          # Dashboard
│   ├── library.html        # Library & upload
│   ├── reader.html         # PDF reader + chat
│   ├── summary.html        # Summary generator
│   └── login.html          # Admin login
│
├── uploads/                # Uploaded PDF files (local only)
└── instance/               # SQLite database (local only)
```

---

## ⚙️ How It Works

```
1. User uploads PDF
        ↓
2. PyMuPDF extracts all pages → saved to SQLite DB
        ↓
3. User reads page by page in the reader
        ↓
4. For Summary → Groq LLM generates structured summary
        ↓
5. For Chat → BM25 finds relevant pages → Groq LLM answers
        ↓
6. Language detected (Urdu/English) → AI replies in same language
```

---

## 🔐 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Your Groq API key | Required |
| `SECRET_KEY` | Flask session secret | `readai_secret_2024` |
| `MODEL_NAME` | Groq model to use | `llama-3.1-8b-instant` |
| `ADMIN_PASSWORD` | Admin login password | `admin123` |

---

## 📦 Dependencies

```txt
flask
groq
httpx
pymupdf
rank-bm25
bcrypt
python-dotenv
numpy
```

---

## 🗺️ Roadmap

- [x] PDF Upload & Page Reader
- [x] AI Summary Generator
- [x] BM25 RAG Chatbot
- [x] Urdu & English Language Support
- [x] Admin Authentication
- [x] Reading History Tracking
- [ ] Multi-user Support
- [ ] Cloud Storage for PDFs
- [ ] Mobile Responsive UI
- [ ] Export Summaries as PDF
- [ ] Voice Reading Mode

---

## 👨‍💻 Author

**Shoukat Ali**
AI Engineer & ML Developer

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Shoukat%20Ali-blue?style=flat-square&logo=linkedin)](https://linkedin.com/in/shoukat-ali-619074248)
[![GitHub](https://img.shields.io/badge/GitHub-Shoukat125-black?style=flat-square&logo=github)](https://github.com/Shoukat125)
[![Portfolio](https://img.shields.io/badge/Portfolio-s--ali--intelligence.lovable.app-orange?style=flat-square&logo=google-chrome)](https://s-ali-intelligence.lovable.app)
[![Kaggle](https://img.shields.io/badge/Kaggle-shoukatsukkur-blue?style=flat-square&logo=kaggle)](https://kaggle.com/shoukatsukkur)

---

## 📄 License

This project is licensed under the **MIT License** — feel free to use, modify, and distribute.

---

<div align="center">

**⭐ If you found this project helpful, please give it a star!**

Made with ❤️ by [Shoukat Ali](https://github.com/Shoukat125) from Sukkur, Pakistan 🇵🇰

</div>
