from chatbot.database import get_db_connection
import random

# Sample data for books
titles = [
    "Harry Potter and the Philosopher's Stone",
    "The Hobbit",
    "To Kill a Mockingbird",
    "1984",
    "The Great Gatsby",
    "Pride and Prejudice",
    "The Catcher in the Rye",
    "The Lord of the Rings",
    "The Chronicles of Narnia",
    "Moby Dick"
]

authors = [
    "J.K. Rowling",
    "J.R.R. Tolkien",
    "Harper Lee",
    "George Orwell",
    "F. Scott Fitzgerald",
    "Jane Austen",
    "J.D. Salinger",
    "J.R.R. Tolkien",
    "C.S. Lewis",
    "Herman Melville"
]

def populate_database():
    connection = get_db_connection()
    cursor = connection.cursor()

    # Insert 100 sample entries
    for i in range(1, 101):
        title = random.choice(titles)
        author = random.choice(authors)
        available = random.randint(1, 5)
        query = "INSERT INTO books (title, author, available_copies) VALUES (%s, %s, %s)"
        cursor.execute(query, (f"{title} - Copy {i}", author, available))

    connection.commit()
    cursor.close()
    connection.close()
    print("Database populated with 100 sample entries.")

if __name__ == "__main__":
    populate_database()