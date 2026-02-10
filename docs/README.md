# Library Assistant Chatbot Documentation

## 1. Project Overview
- **Purpose**: Provide patrons with a concierge-style chat experience for searching the catalog, managing loans, and handling availability checks without relying on external AI APIs.
- **Stack**: Flask, Python 3.13, PostgreSQL, custom rule-based chatbot, vanilla JS/CSS front-end.
- **Key Traits**: Session-based usernames, fully local inference rules, responsive UI, and database-backed workflows for search, borrow, renew, and return.

## 2. Architecture
```
┌─────────────────────┐        ┌──────────────────────┐
│ Front-end (Flask    │        │ Static Assets        │
│ templates + JS/CSS) │<──────>│ templates/, static/  │
└─────────┬───────────┘        └─────────┬────────────┘
          │                                │
          ▼                                ▼
┌─────────────────────┐        ┌──────────────────────┐
│ Flask App (app.py)  │<──────>│ Chatbot Engine       │
│ Routes, sessions,   │        │ chatbot/chatbot.py   │
│ logging             │        │ rule-based actions   │
└─────────┬───────────┘        └─────────┬────────────┘
          │                                │
          ▼                                ▼
┌─────────────────────┐        ┌──────────────────────┐
│ Database Connector  │<──────>│ PostgreSQL           │
│ chatbot/database.py │        │ books, users, loans  │
└─────────────────────┘        └──────────────────────┘
```

## 3. Directory Layout
- `app.py` – Flask entry point, routes, logging, session handling.
- `chatbot/`
  - `chatbot.py` – rule-based conversation + DB workflows.
  - `database.py` – environment-aware connection factory.
- `templates/` – `index.html` (chat), `set_username.html` (login).
- `static/` – `style.css`, `script.js`, favicon and other assets.
- `docs/README.md` – this documentation.
- `requirements.txt` – Python dependencies.
- `populate_database.py` – seeding script for demo catalog data.

## 4. Setup & Installation
1. **Clone & enter project**
   ```bash
   git clone <repo-url>
   cd Library-Assistant-Chatbot
   ```
2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/Scripts/activate  # Windows PowerShell
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure environment** (`.env`)
   ```env
   DATABASE_URL=postgresql://<user>:<password>@localhost:5432/library_bot
   FLASK_SECRET_KEY=<random-secret>
   ```
5. **Prepare database**
   - Create database `library_bot` in PostgreSQL.
   - Run migrations/schema SQL (see §6) or create tables manually.
   - Seed sample data: `python populate_database.py`.
6. **Start application**
   ```bash
   python app.py
   ```
   Access at <http://localhost:5000>.

## 5. User Experience Flow
1. **Login / Name capture**
   - Landing page prompts for username (stored in Flask session).
2. **Chat Interface**
   - Sidebar highlights commands.
   - Messages handled in real time via `static/script.js` (fetch to `/chat`).
3. **Session Management**
   - `ensure_username` guard ensures chat routes require a session.
   - `/logout` clears session and redirects to login view.

## 6. Database Schema
```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username TEXT UNIQUE NOT NULL
);

CREATE TABLE books (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  author TEXT NOT NULL,
  available_copies INT NOT NULL DEFAULT 1
);

CREATE TABLE loans (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES users(id),
  book_id INT NOT NULL REFERENCES books(id),
  borrowed_at TIMESTAMP NOT NULL DEFAULT NOW(),
  due_at TIMESTAMP NOT NULL,
  returned_at TIMESTAMP NULL,
  renewals INT NOT NULL DEFAULT 0
);
```

## 7. Chatbot Command Reference
| Command | Example | Behavior |
|---------|---------|----------|
| `search title=<t> author=<a>` | `search title=python author=ramalho` | Lists up to 10 matches with availability badges. |
| `availability <book_id>` | `availability 3` | Checks current copies for given book id. |
| `borrow <book_id>` | `borrow 7` | Creates loan, decrements copies, sets due date (14 days). |
| `return <loan_id>` | `return 12` | Marks loan returned, increments copies. |
| `renew <loan_id>` | `renew 9` | Extends due date (+7 days) up to 2 renewals. |
| `my loans` | `my loans` | Lists active loans with due dates and renewal counts. |
| Small talk (`hello`, `help`, `bye`) | `hello` | Friendly canned responses. |

## 8. API / Route Summary
| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Chat UI if session has username; else login page. |
| `/chat` | POST | Processes chat form submission, returns response text. |
| `/set_username` | POST | Stores username in session. |
| `/logout` | GET | Clears session and redirects to `/`. |
| `/test` | GET | Health endpoint returning 200/"Server is running". |

## 9. Styling & Front-End Notes
- Typography: Space Grotesk + IBM Plex Sans.
- Background: layered gradient + orb texture for depth.
- Components: sidebar command cards, status chips, floating composer, matching login experience.
- Responsive behavior: collapses to single-column on tablets/phones.
- Animations: subtle slide-in for messages, hover/tap feedback on buttons.

## 10. Logging & Debugging
- `logging.basicConfig` writes both to console and `app_debug.log`.
- `log_request_info` before-request hook traces endpoints + payloads.
- When debugging chat logic, run `python -m chatbot.chatbot` for REPL-style tests.

## 11. Deployment Considerations
- Replace Flask dev server with production WSGI (Gunicorn/Waitress) behind reverse proxy.
- Configure environment variables securely (no secrets in repo).
- Use managed Postgres or ensure backups.
- Consider enabling HTTPS, session cookie security flags, and rate limiting for public deployments.

## 12. Troubleshooting Checklist
| Symptom | Possible Cause | Fix |
|---------|----------------|-----|
| Redirect loop on `/` | Session lacks username | Ensure `/set_username` reachable; clear cookies. |
| Chat returns HTML instead of text | `/chat` route rendering template | Confirm it returns plain response string. |
| Database connection failure | Wrong `DATABASE_URL` or server down | Verify Postgres service and credentials. |
| Commands always fallback to "didn't understand" | Username missing or parsing failed | Confirm session, check command format. |
| `psycopg2` import errors | Env mismatch | Reinstall `psycopg2` inside venv. |

## 13. Future Enhancements
- Add authentication provider (SSO/library card).
- Introduce analytics dashboard for command usage.
- Expand chatbot intents (recommendations, holds, fees).
- Localize UI copy for multilingual deployments.
- Add automated tests (pytest) for routes and chatbot logic.

---
Need more help? Reach out via repository issues or extend this documentation with deployment notes tailored to your environment.
