"""
Создаёт таблицы в DB/users.db.
Запускать один раз: python init_users_db.py
"""
import sqlite3
import os


TABLES = [
    """
    CREATE TABLE IF NOT EXISTS users (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        username      TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS user_groups (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id  INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        group_id INTEGER NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS sessions (
        token      TEXT PRIMARY KEY,
        user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        created_at INTEGER NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS user_roles (
        user_id    INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
        role_index INTEGER NOT NULL
    )
    """,
]

_AUTH_DB_PATH = 'auth_service/users.db'

def init():
    os.makedirs(os.path.dirname(_AUTH_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(_AUTH_DB_PATH)
    cur  = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON")
    for sql in TABLES:
        cur.execute(sql)
    conn.commit()
    conn.close()
    print(f"users.db готова: {_AUTH_DB_PATH}")


if __name__ == "__main__":
    init()
