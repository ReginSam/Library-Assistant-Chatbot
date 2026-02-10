# 📚 Library Assistant Chatbot

## Overview
The **Library Assistant Chatbot** is a lightweight Flask chatbot that connects to a PostgreSQL database of books. It compresses catalog context and enforces borrowing policies so patrons can quickly search, check availability, borrow/return, and renew loans.

This project demonstrates how to build a practical chatbot with a simple backend and database integration, suitable for deployment in a real-world library or as a prototype for educational purposes.

---

## Features
* 🔍 **Book Search**: Find books by title, author, or keyword.
* 📖 **Borrow & Return**: Manage book loans with borrowing policies enforced.
* ⏳ **Renewals**: Extend loan periods within policy limits.
* 🧑‍🤝‍🧑 **User Accounts**: Track borrowing history per user.
* 📊 **Catalog Compression**: Efficient handling of large book catalogs using context compression.
* 💡 **Recommendations**: Suggest books based on borrowing history or catalog metadata.

---

## Tech Stack
* **Language**: Python
* **Framework**: Flask
* **Database**: PostgreSQL
* **Libraries**:
    * `psycopg` for database operations
    * `Flask` for chatbot API and UI

---

## Project Structure
```text
Library-Assistant-Chatbot/
│
├── app.py                # Main Flask application
├── requirements.txt      # Python dependencies
├── static/               # Static assets (CSS)
├── templates/            # HTML templates for web UI
└── README.md             # Documentation
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure PostgreSQL
Set the `DATABASE_URL` environment variable:
```
postgresql://username:password@localhost:5432/library_bot
```

### 3. Configure ScaleDown Compression
Set the `SCALEDOWN_API_KEY` environment variable (and optional `SCALEDOWN_MODEL`):
```
SCALEDOWN_API_KEY=YOUR_API_KEY
SCALEDOWN_MODEL=gpt-4o
```

### 4. Run the App
```bash
python app.py
```

Open http://localhost:5000 in your browser.
