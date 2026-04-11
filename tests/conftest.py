"""
conftest.py — общие фикстуры для всех тестов.

run:
    cd vk_callbacks
    python -m pytest tests/ -v
"""

import os
import sys
import sqlite3
import tempfile
import pytest
from unittest.mock import patch, MagicMock

sys.dont_write_bytecode = True 

# ── Добавляем корень проекта в sys.path ──────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
 


# ── Создаём временные .db файлы ──────────────────────────────────────────────

def make_main_db(path: str):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    tables = [
        """CREATE TABLE IF NOT EXISTS wall_post (
            id INTEGER PRIMARY KEY, from_id INTEGER, group_id INTEGER,
            text TEXT, date INTEGER, likes INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0, postponed_id INTEGER)""",
        """CREATE TABLE IF NOT EXISTS wall_reply (
            id INTEGER PRIMARY KEY, from_id INTEGER, post_id INTEGER,
            group_id INTEGER, text TEXT, date INTEGER)""",
        """CREATE TABLE IF NOT EXISTS wall_reply_delete (
            id INTEGER PRIMARY KEY, group_id INTEGER,
            deleter_id INTEGER, post_id INTEGER)""",
        """CREATE TABLE IF NOT EXISTS wall_schedule_post (
            id INTEGER PRIMARY KEY, schedule_time INTEGER, group_id INTEGER)""",
        """CREATE TABLE IF NOT EXISTS like_event (
            id INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT,
            liker_id INTEGER, object_type TEXT, object_owner_id INTEGER,
            object_id INTEGER, thread_reply_id INTEGER, post_id INTEGER,
            group_id INTEGER, created_at INTEGER DEFAULT (strftime('%s','now')))""",
        """CREATE TABLE IF NOT EXISTS group_join (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
            join_type TEXT, group_id INTEGER,
            joined_at INTEGER DEFAULT (strftime('%s','now')))""",
        """CREATE TABLE IF NOT EXISTS group_leave (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
            self INTEGER, group_id INTEGER,
            left_at INTEGER DEFAULT (strftime('%s','now')))""",
        """CREATE TABLE IF NOT EXISTS user_block (
            id INTEGER PRIMARY KEY AUTOINCREMENT, admin_id INTEGER,
            user_id INTEGER, unblock_date INTEGER, reason INTEGER,
            comment TEXT, group_id INTEGER,
            blocked_at INTEGER DEFAULT (strftime('%s','now')))""",
        """CREATE TABLE IF NOT EXISTS user_unblock (
            id INTEGER PRIMARY KEY AUTOINCREMENT, admin_id INTEGER,
            user_id INTEGER, by_end_date INTEGER, group_id INTEGER,
            unblocked_at INTEGER DEFAULT (strftime('%s','now')))""",
        """CREATE TABLE IF NOT EXISTS message (
            id INTEGER PRIMARY KEY, event_type TEXT, from_id INTEGER,
            peer_id INTEGER, text TEXT, date INTEGER,
            conversation_message_id INTEGER, has_attachments INTEGER DEFAULT 0,
            group_id INTEGER)""",
        """CREATE TABLE IF NOT EXISTS message_allow (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
            key TEXT, group_id INTEGER,
            created_at INTEGER DEFAULT (strftime('%s','now')))""",
        """CREATE TABLE IF NOT EXISTS message_deny (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
            group_id INTEGER,
            created_at INTEGER DEFAULT (strftime('%s','now')))""",
        """CREATE TABLE IF NOT EXISTS message_typing_state (
            id INTEGER PRIMARY KEY AUTOINCREMENT, from_id INTEGER,
            to_id INTEGER, state TEXT,
            created_at INTEGER DEFAULT (strftime('%s','now')))""",
        """CREATE TABLE IF NOT EXISTS message_event (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
            peer_id INTEGER, event_id TEXT, payload TEXT,
            conversation_message_id INTEGER, group_id INTEGER,
            created_at INTEGER DEFAULT (strftime('%s','now')))""",
        """CREATE TABLE IF NOT EXISTS photo (
            id INTEGER PRIMARY KEY, owner_id INTEGER, group_id INTEGER,
            text TEXT, date INTEGER)""",
        """CREATE TABLE IF NOT EXISTS photo_comment (
            id INTEGER PRIMARY KEY, event_type TEXT, from_id INTEGER,
            photo_id INTEGER, photo_owner_id INTEGER, text TEXT,
            date INTEGER, group_id INTEGER)""",
        """CREATE TABLE IF NOT EXISTS photo_comment_delete (
            id INTEGER PRIMARY KEY, photo_id INTEGER,
            photo_owner_id INTEGER, deleter_id INTEGER,
            user_id INTEGER, group_id INTEGER)""",
        """CREATE TABLE IF NOT EXISTS video (
            id INTEGER PRIMARY KEY, owner_id INTEGER, group_id INTEGER,
            title TEXT, duration INTEGER, date INTEGER)""",
        """CREATE TABLE IF NOT EXISTS video_comment (
            id INTEGER PRIMARY KEY, event_type TEXT, from_id INTEGER,
            video_id INTEGER, video_owner_id INTEGER, text TEXT,
            date INTEGER, group_id INTEGER)""",
        """CREATE TABLE IF NOT EXISTS video_comment_delete (
            id INTEGER PRIMARY KEY, owner_id INTEGER, user_id INTEGER,
            deleter_id INTEGER, video_id INTEGER, group_id INTEGER)""",
        """CREATE TABLE IF NOT EXISTS poll_vote (
            id INTEGER PRIMARY KEY AUTOINCREMENT, owner_id INTEGER,
            poll_id INTEGER, option_id INTEGER, user_id INTEGER,
            group_id INTEGER,
            created_at INTEGER DEFAULT (strftime('%s','now')))""",
        """CREATE TABLE IF NOT EXISTS group_officers_edit (
            id INTEGER PRIMARY KEY AUTOINCREMENT, admin_id INTEGER,
            user_id INTEGER, level_old INTEGER, level_new INTEGER,
            group_id INTEGER,
            created_at INTEGER DEFAULT (strftime('%s','now')))""",
        """CREATE TABLE IF NOT EXISTS vkpay_transaction (
            id INTEGER PRIMARY KEY AUTOINCREMENT, from_id INTEGER,
            amount INTEGER, description TEXT, date INTEGER, group_id INTEGER)""",
        """CREATE TABLE IF NOT EXISTS group_data (
            group_id INTEGER PRIMARY KEY, name TEXT, photo_url TEXT,
            members_count INTEGER, updated_at INTEGER)""",
        """CREATE TABLE IF NOT EXISTS vk_servers (
            group_id INTEGER PRIMARY KEY, confirm_code TEXT)""",
        """CREATE TABLE IF NOT EXISTS vk_server_secrets (
            group_id INTEGER PRIMARY KEY, secret TEXT NOT NULL)""",
        """CREATE TABLE IF NOT EXISTS audio (
            id INTEGER PRIMARY KEY, owner_id INTEGER, group_id INTEGER,
            artist TEXT, title TEXT, date INTEGER)""",
        """CREATE TABLE IF NOT EXISTS donut_subscription (
            id INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT,
            user_id INTEGER, amount INTEGER, amount_without_fee INTEGER,
            amount_old INTEGER, amount_new INTEGER, group_id INTEGER,
            created_at INTEGER DEFAULT (strftime('%s','now')))""",
        """CREATE TABLE IF NOT EXISTS donut_money_withdraw (
            id INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT,
            amount INTEGER, amount_without_fee INTEGER,
            reason TEXT, group_id INTEGER,
            created_at INTEGER DEFAULT (strftime('%s','now')))""",
    ]
    for sql in tables:
        c.execute(sql)

    # Тестовые данные
    c.execute("INSERT INTO vk_servers VALUES (123456, 'TEST_CONFIRM_CODE')")
    c.execute("INSERT INTO vk_server_secrets VALUES (123456, 'TEST_SECRET')")
    c.execute("INSERT INTO group_data VALUES (123456, 'Test Group', 'http://photo.url', 1000, 0)")

    conn.commit()
    conn.close()


def make_users_db(path: str):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS user_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            group_id INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS user_roles (
            user_id INTEGER PRIMARY KEY,
            role_index INTEGER NOT NULL
        );
    """)
    import bcrypt
    pw_hash = bcrypt.hashpw(b"testpass", bcrypt.gensalt()).decode()
    c.execute("INSERT INTO users (username, password_hash) VALUES ('testuser', ?)", (pw_hash,))
    c.execute("INSERT INTO user_groups (user_id, group_id) VALUES (1, 123456)")
    c.execute("INSERT INTO sessions (token, user_id, created_at) VALUES ('TEST_TOKEN', 1, strftime('%s','now'))")
    c.execute("INSERT INTO user_roles (user_id, role_index) VALUES (1, 1)")
    conn.commit()
    conn.close()


# ── Фикстура: временные БД + патчи ──────────────────────────────────────────

@pytest.fixture(scope="session")
def tmp_dbs():
    with tempfile.TemporaryDirectory() as tmpdir:
        main_db  = os.path.join(tmpdir, "db.db")
        users_db = os.path.join(tmpdir, "users.db")
        make_main_db(main_db)
        make_users_db(users_db)
        yield {"main": main_db, "users": users_db, "dir": tmpdir}


@pytest.fixture(scope="session")
def client(tmp_dbs):
    """Тестовый HTTP-клиент с замоканными путями к БД."""
    from unittest.mock import patch

    with patch.dict(os.environ, {
        "SECRET_KEY_VK_GROUP": "fake_vk_token",
        "DB_NAME": "db.db",
    }):
        import _G as g_module
        g_module.DB_PATH      = tmp_dbs["main"]
        g_module.AUTH_DB_PATH = tmp_dbs["users"]

        # Перегружаем DB модуль чтобы он видел новый путь
        import importlib, DB.DB as db_mod
        db_mod_patched = patch.object(db_mod, "get_conn",
            lambda: (lambda c: (setattr(c, "row_factory", sqlite3.Row), c)[1])(
                sqlite3.connect(tmp_dbs["main"])
            ))

        import auth_service.UsersDB as udb
        udb_patched = patch.object(udb, "get_conn",
            lambda: (lambda c: (setattr(c, "row_factory", sqlite3.Row), c)[1])(
                sqlite3.connect(tmp_dbs["users"])
            ))

        with db_mod_patched, udb_patched:
            from fastapi.testclient import TestClient
            from main import app
            with TestClient(app, raise_server_exceptions=False) as c:
                yield c


@pytest.fixture(scope="session")
def auth_client(client):
    """Клиент с уже установленной сессионной кукой."""
    client.cookies.set("session", "TEST_TOKEN")
    return client


# ── Константы для тестов ─────────────────────────────────────────────────────

GROUP_ID    = 123456
SECRET      = "TEST_SECRET"
CONFIRM     = "TEST_CONFIRM_CODE"
USER_ID     = 42289534
SESSION     = "TEST_TOKEN"
