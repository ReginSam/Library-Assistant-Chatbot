import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set.")
    connection = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    connection.autocommit = True
    return connection