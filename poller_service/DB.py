import os
import sqlite3

_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "poller.db")


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def fetchall(query: str, params: list = []) -> list[dict]:
    conn = get_conn()
    try:
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def execute(query: str, params: list = []):
    conn = get_conn()
    try:
        conn.execute(query, params)
        conn.commit()
    except Exception as e:
        print(f"[DB ERROR] {e}")
    finally:
        conn.close()


def upsert_post(post: dict):
    conn = get_conn()
    try:
        conn.execute(
            """
            INSERT INTO user_posts (id, owner_id, date, likes, comments, reposts, views, fetched_at)
            VALUES (:id, :owner_id, :date, :likes, :comments, :reposts, :views, :fetched_at)
            ON CONFLICT(id, owner_id) DO UPDATE SET
                likes      = excluded.likes,
                comments   = excluded.comments,
                reposts    = excluded.reposts,
                views      = excluded.views,
                fetched_at = excluded.fetched_at
            """,
            post,
        )
        conn.commit()
    except Exception as e:
        print(f"[DB ERROR] upsert_post: {e}")
    finally:
        conn.close()
