import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")
    DATABASE_URL = os.environ.get("DATABASE_URL")
    MAX_BORROWED_BOOKS = 3
    LOAN_DAYS = 14
    CATALOG_PREVIEW_LIMIT = 5