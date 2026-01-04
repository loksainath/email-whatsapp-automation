import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)
DB_PATH = os.path.join(BASE_DIR, "users.db")


# =================================================
# DB CONNECTION
# =================================================
def get_db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


# =================================================
# INIT DB (SAFE + COMPLETE)
# =================================================
def init_db():
    db = get_db()

    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,

            -- Profile settings
            gmail_email TEXT,
            gmail_app_password TEXT,
            whatsapp TEXT,
            language TEXT DEFAULT 'English',

            role TEXT DEFAULT 'user',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    db.commit()
    db.close()


# 🔥 ENSURE DB IS INITIALIZED (SAFE)
init_db()


# =================================================
# REGISTER
# =================================================
def register_user(full_name, email, password):
    db = get_db()
    password_hash = generate_password_hash(password)

    try:
        db.execute("""
            INSERT INTO users (full_name, email, password_hash)
            VALUES (?, ?, ?)
        """, (
            full_name.strip(),
            email.lower().strip(),
            password_hash
        ))
        db.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        db.close()


# =================================================
# LOGIN
# =================================================
def authenticate_user(email, password):
    db = get_db()
    cur = db.execute("""
        SELECT id, password_hash
        FROM users
        WHERE email = ?
    """, (email.lower().strip(),))

    row = cur.fetchone()
    db.close()

    if row and check_password_hash(row[1], password):
        return row[0]

    return None


# =================================================
# GET USER (ORDER MATTERS)
# =================================================
def get_user(user_id):
    db = get_db()
    cur = db.execute("""
        SELECT
            full_name,          -- 0
            email,              -- 1
            gmail_email,        -- 2
            gmail_app_password, -- 3
            whatsapp,           -- 4
            language            -- 5
        FROM users
        WHERE id = ?
    """, (user_id,))

    user = cur.fetchone()
    db.close()
    return user


# =================================================
# 🔥 GET ALL USERS (BACKEND USE)
# =================================================
def get_all_users():
    db = get_db()
    cur = db.execute("""
        SELECT id
        FROM users
        WHERE gmail_email IS NOT NULL
          AND gmail_app_password IS NOT NULL
    """)
    users = [{"id": row[0]} for row in cur.fetchall()]
    db.close()
    return users


# =================================================
# UPDATE PROFILE
# =================================================
def update_profile(
    user_id,
    gmail_email,
    gmail_app_password,
    whatsapp,
    language
):
    db = get_db()

    db.execute("""
        UPDATE users
        SET
            gmail_email = ?,
            gmail_app_password = ?,
            whatsapp = ?,
            language = ?
        WHERE id = ?
    """, (
        gmail_email.strip(),
        gmail_app_password.strip(),
        whatsapp.strip(),
        language,
        user_id
    ))

    db.commit()
    db.close()
