"""
Создаёт таблицы в DB/users.db.
Запускать один раз: python init_users_db.py
"""
import sqlite3
import os

import _G

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
]


def init():
    os.makedirs(os.path.dirname(_G.AUTH_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(_G.AUTH_DB_PATH)
    cur  = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON")
    for sql in TABLES:
        cur.execute(sql)
    conn.commit()
    conn.close()
    print(f"users.db готова: {_G.AUTH_DB_PATH}")


if __name__ == "__main__":
    init()
