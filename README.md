# 📚 Library Assistant Chatbot

## Overview
The **Library Assistant Chatbot** is an AI-powered conversational system designed to help patrons quickly access library services. It compresses book catalog data and borrowing policies to provide efficient, low-latency responses. Users can search for books, check availability, borrow or return items, renew loans, and receive personalized recommendations.

This project demonstrates how to build a practical chatbot with a simple backend and database integration, suitable for deployment in a real-world library or as a prototype for educational purposes.

---

## Features
- 🔍 **Book Search**: Find books by title, author, or keyword.
- 📖 **Borrow & Return**: Manage book loans with borrowing policies enforced.
- ⏳ **Renewals**: Extend loan periods within policy limits.
- 🧑‍🤝‍🧑 **User Accounts**: Track borrowing history per user.
- 📊 **Catalog Compression**: Efficient handling of large book catalogs using context compression.
- 💡 **Recommendations**: Suggest books based on borrowing history or catalog metadata.

---

## Tech Stack
- **Language**: Python
- **Framework**: Flask (for web/chat interface)
- **Database**: SQLite (lightweight, portable)
- **Libraries**:
  - `sqlite3` for database operations
  - `Flask` for chatbot API and UI
  - `NLTK` or `spaCy` (optional) for natural language parsing

---

## Project Structure
library-assistant-chatbot/
│
├── app.py                 # Main Flask application
├── database.db            # SQLite database (auto-generated)
├── schema.sql             # Database schema (books, users, loans)
├── static/               # Static assets (CSS, JS)
├── templates/            # HTML templates for web UI
└── README.md              # Documentation

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/library-assistant-chatbot.git
cd library-assistant-chatbot
