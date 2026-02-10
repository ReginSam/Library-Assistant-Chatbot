# This file contains the chatbot logic.

import logging
import re
from datetime import datetime, timedelta
from typing import Optional, Tuple

from chatbot.database import get_db_connection

logger = logging.getLogger(__name__)


class Chatbot:
    """Rule-based chatbot that executes common library workflows."""

    BORROW_DAYS = 14
    RENEW_DAYS = 7
    MAX_RENEWALS = 2

    def __init__(self) -> None:
        self.smalltalk = {
            "hello": "Hi there! How can I assist you today?",
            "help": "Try commands like search, availability <book_id>, borrow <book_id>, return <loan_id>, renew <loan_id>, or my loans.",
            "bye": "Goodbye! Have a great day!",
            "harry potter": "Harry Potter is a series of fantasy novels written by J.K. Rowling. Would you like to search for a specific book in the series?",
        }

    # ------------------------------------------------------------------
    # Parsing helpers
    def _parse_search_terms(self, message: str) -> Tuple[Optional[str], Optional[str]]:
        pattern = re.compile(r"(title|author)\s*=\s*([^=]+?)(?=\s+(?:title|author)\s*=|$)", re.IGNORECASE)
        matches = pattern.findall(message)
        params = {key.lower(): value.strip() for key, value in matches if value.strip()}
        return params.get("title"), params.get("author")

    def _extract_first_int(self, message: str) -> Optional[int]:
        match = re.search(r"(\d+)", message)
        return int(match.group(1)) if match else None

    def _get_or_create_user(self, cursor, username: str) -> int:
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        row = cursor.fetchone()
        if row:
            return row["id"]
        cursor.execute("INSERT INTO users (username) VALUES (%s) RETURNING id", (username,))
        return cursor.fetchone()["id"]

    # ------------------------------------------------------------------
    # Command handlers
    def search_books(self, title: Optional[str], author: Optional[str]) -> str:
        if not title and not author:
            return "Please provide a title and/or author to search for."

        logger.debug("Searching books with title=%s author=%s", title, author)
        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            query = "SELECT id, title, author, available_copies FROM books WHERE 1=1"
            params = []
            if title:
                query += " AND title ILIKE %s"
                params.append(f"%{title}%")
            if author:
                query += " AND author ILIKE %s"
                params.append(f"%{author}%")

            query += " ORDER BY title"
            cursor.execute(query, params)
            results = cursor.fetchall()
        finally:
            cursor.close()
            connection.close()

        if not results:
            return "No books found matching your search criteria."

        lines = ["Here are the books I found:"]
        for book in results[:10]:
            availability = "Available" if book["available_copies"] > 0 else "Checked out"
            lines.append(f"- ({book['id']}) {book['title']} by {book['author']} - {availability}")
        if len(results) > 10:
            lines.append("…and more. Please refine your search for narrower results.")
        return "\n".join(lines)

    def get_book_availability(self, book_id: Optional[int]) -> str:
        if not book_id:
            return "Please provide a valid book ID, e.g. availability 3."

        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT title, author, available_copies FROM books WHERE id = %s", (book_id,))
            book = cursor.fetchone()
        finally:
            cursor.close()
            connection.close()

        if not book:
            return f"I couldn't find a book with ID {book_id}."

        if book["available_copies"] > 0:
            return f"{book['title']} by {book['author']} has {book['available_copies']} copies available."
        return f"All copies of {book['title']} are currently checked out."

    def borrow_book(self, username: str, book_id: Optional[int]) -> str:
        if not book_id:
            return "Please provide a book ID to borrow, e.g. borrow 5."

        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT id, title, available_copies FROM books WHERE id = %s", (book_id,))
            book = cursor.fetchone()
            if not book:
                return f"Book {book_id} was not found."
            if book["available_copies"] <= 0:
                return f"All copies of {book['title']} are checked out right now."

            user_id = self._get_or_create_user(cursor, username)
            borrowed_at = datetime.utcnow()
            due_at = borrowed_at + timedelta(days=self.BORROW_DAYS)
            cursor.execute(
                "INSERT INTO loans (user_id, book_id, borrowed_at, due_at, renewals) VALUES (%s, %s, %s, %s, 0) RETURNING id",
                (user_id, book_id, borrowed_at, due_at),
            )
            loan_id = cursor.fetchone()["id"]
            cursor.execute("UPDATE books SET available_copies = available_copies - 1 WHERE id = %s", (book_id,))
        finally:
            cursor.close()
            connection.close()

        return f"Loan #{loan_id} confirmed! Please return {book['title']} by {due_at.date():%Y-%m-%d}."

    def return_book(self, username: str, loan_id: Optional[int]) -> str:
        if not loan_id:
            return "Please provide the loan ID you want to return, e.g. return 12."

        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(
                """
                SELECT loans.id, loans.book_id, books.title
                FROM loans
                JOIN users ON users.id = loans.user_id
                JOIN books ON books.id = loans.book_id
                WHERE loans.id = %s AND users.username = %s AND loans.returned_at IS NULL
                """,
                (loan_id, username),
            )
            loan = cursor.fetchone()
            if not loan:
                return "I couldn't find an active loan with that ID under your name."

            cursor.execute("UPDATE loans SET returned_at = %s WHERE id = %s", (datetime.utcnow(), loan_id))
            cursor.execute("UPDATE books SET available_copies = available_copies + 1 WHERE id = %s", (loan["book_id"],))
        finally:
            cursor.close()
            connection.close()

        return f"Thanks! {loan['title']} has been checked in."

    def renew_loan(self, username: str, loan_id: Optional[int]) -> str:
        if not loan_id:
            return "Please provide the loan ID you want to renew, e.g. renew 7."

        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(
                """
                SELECT loans.id, loans.due_at, loans.renewals, books.title
                FROM loans
                JOIN users ON users.id = loans.user_id
                JOIN books ON books.id = loans.book_id
                WHERE loans.id = %s AND users.username = %s AND loans.returned_at IS NULL
                """,
                (loan_id, username),
            )
            loan = cursor.fetchone()
            if not loan:
                return "I couldn't find an active loan with that ID under your name."
            if loan["renewals"] >= self.MAX_RENEWALS:
                return "That loan has reached the maximum number of renewals."

            new_due = loan["due_at"] + timedelta(days=self.RENEW_DAYS)
            cursor.execute(
                "UPDATE loans SET due_at = %s, renewals = renewals + 1 WHERE id = %s",
                (new_due, loan_id),
            )
        finally:
            cursor.close()
            connection.close()

        return f"Renewed! {loan['title']} is now due on {new_due.date():%Y-%m-%d}."

    def list_loans(self, username: str) -> str:
        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(
                """
                SELECT loans.id, books.title, loans.due_at, loans.renewals
                FROM loans
                JOIN users ON users.id = loans.user_id
                JOIN books ON books.id = loans.book_id
                WHERE users.username = %s AND loans.returned_at IS NULL
                ORDER BY loans.due_at
                """,
                (username,),
            )
            loans = cursor.fetchall()
        finally:
            cursor.close()
            connection.close()

        if not loans:
            return "You have no active loans right now."

        lines = ["Here are your current loans:"]
        for loan in loans:
            due_dt = loan["due_at"]
            due_str = due_dt.strftime("%Y-%m-%d") if due_dt else "n/a"
            lines.append(
                f"- Loan #{loan['id']}: {loan['title']} - due {due_str} (renewals {loan['renewals']})"
            )
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Public API
    def get_response(self, message: str, username: Optional[str] = None) -> str:
        if not message:
            return "Please type a message so I can help."

        logger.debug("Received message: %s", message)
        original = message.strip()
        normalized = original.lower()

        if normalized.startswith("search"):
            title, author = self._parse_search_terms(original)
            return self.search_books(title, author)

        if normalized.startswith("availability"):
            return self.get_book_availability(self._extract_first_int(original))

        if normalized.startswith("borrow"):
            if not username:
                return "Please tell me your name before borrowing a book."
            return self.borrow_book(username, self._extract_first_int(original))

        if normalized.startswith("return"):
            if not username:
                return "Please tell me your name before returning a book."
            return self.return_book(username, self._extract_first_int(original))

        if normalized.startswith("renew"):
            if not username:
                return "Please tell me your name before renewing a book."
            return self.renew_loan(username, self._extract_first_int(original))

        if normalized.startswith("my loans") or normalized.startswith("my loan"):
            if not username:
                return "Please tell me your name first so I can find your account."
            return self.list_loans(username)

        for key, response in self.smalltalk.items():
            if key in normalized:
                return response

        return "I'm sorry, I didn't understand that. Try 'help' to see the supported commands."


if __name__ == "__main__":
    bot = Chatbot()
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Bot: Goodbye!")
            break
        print(f"Bot: {bot.get_response(user_input, username='demo_user')}")