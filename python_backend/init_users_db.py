import sqlite3
import os

# -------------------------------------------------
# Database path
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "users.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# -------------------------------------------------
# Create users table (FINAL + VERIFIED SCHEMA)
# -------------------------------------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,

    gmail_email TEXT,
    gmail_app_password TEXT,
    whatsapp TEXT,
    language TEXT DEFAULT 'English',

    role TEXT DEFAULT 'user',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()

print("✅ users table created / verified successfully")
