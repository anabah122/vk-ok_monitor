
from poller_service.Poller import DB

TABLES = [
    """
    CREATE TABLE IF NOT EXISTS tracked_users (
        user_id  INTEGER PRIMARY KEY,
        added_at INTEGER DEFAULT (strftime('%s','now'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS user_posts (
        id         INTEGER,
        owner_id   INTEGER,
        date       INTEGER,
        likes      INTEGER DEFAULT 0,
        comments   INTEGER DEFAULT 0,
        reposts    INTEGER DEFAULT 0,
        views      INTEGER DEFAULT 0,
        fetched_at INTEGER,
        PRIMARY KEY (id, owner_id)
    )
    """,
]


def create_db():
    for sql in TABLES:
        DB.execute(sql)
    print(f"БД создана: {DB._DB_PATH}")
    print(f"Таблиц: {len(TABLES)}")


if __name__ == "__main__":
    create_db()
