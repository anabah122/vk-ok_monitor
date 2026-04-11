
TABLES = [

    # ── Стена ─────────────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS wall_post (
        id           INTEGER PRIMARY KEY,
        from_id      INTEGER,
        group_id     INTEGER,
        text         TEXT,
        date         INTEGER,
        likes        INTEGER DEFAULT 0,
        comments     INTEGER DEFAULT 0,
        postponed_id INTEGER
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS wall_reply (
        id       INTEGER PRIMARY KEY,
        from_id  INTEGER,
        post_id  INTEGER,
        group_id INTEGER,
        text     TEXT,
        date     INTEGER
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS wall_reply_delete (
        id         INTEGER PRIMARY KEY,
        group_id   INTEGER,
        deleter_id INTEGER,
        post_id    INTEGER
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS wall_schedule_post (
        id            INTEGER PRIMARY KEY,
        schedule_time INTEGER,
        group_id      INTEGER
    )
    """,

    # ── Лайки ─────────────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS like_event (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type      TEXT,
        liker_id        INTEGER,
        object_type     TEXT,
        object_owner_id INTEGER,
        object_id       INTEGER,
        thread_reply_id INTEGER,
        post_id         INTEGER,
        group_id        INTEGER,
        created_at      INTEGER DEFAULT (strftime('%s','now'))
    )
    """,

    # ── Участники ─────────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS group_join (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id   INTEGER,
        join_type TEXT,
        group_id  INTEGER,
        joined_at INTEGER DEFAULT (strftime('%s','now'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS group_leave (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id  INTEGER,
        self     INTEGER,
        group_id INTEGER,
        left_at  INTEGER DEFAULT (strftime('%s','now'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS user_block (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_id     INTEGER,
        user_id      INTEGER,
        unblock_date INTEGER,
        reason       INTEGER,
        comment      TEXT,
        group_id     INTEGER,
        blocked_at   INTEGER DEFAULT (strftime('%s','now'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS user_unblock (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_id     INTEGER,
        user_id      INTEGER,
        by_end_date  INTEGER,
        group_id     INTEGER,
        unblocked_at INTEGER DEFAULT (strftime('%s','now'))
    )
    """,

    # ── Сообщения ─────────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS message (
        id                      INTEGER PRIMARY KEY,
        event_type              TEXT,
        from_id                 INTEGER,
        peer_id                 INTEGER,
        text                    TEXT,
        date                    INTEGER,
        conversation_message_id INTEGER,
        has_attachments         INTEGER DEFAULT 0,
        group_id                INTEGER
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS message_allow (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id    INTEGER,
        key        TEXT,
        group_id   INTEGER,
        created_at INTEGER DEFAULT (strftime('%s','now'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS message_deny (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id    INTEGER,
        group_id   INTEGER,
        created_at INTEGER DEFAULT (strftime('%s','now'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS message_typing_state (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        from_id    INTEGER,
        to_id      INTEGER,
        state      TEXT,
        created_at INTEGER DEFAULT (strftime('%s','now'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS message_event (
        id                      INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id                 INTEGER,
        peer_id                 INTEGER,
        event_id                TEXT,
        payload                 TEXT,
        conversation_message_id INTEGER,
        group_id                INTEGER,
        created_at              INTEGER DEFAULT (strftime('%s','now'))
    )
    """,

    # ── Фото ──────────────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS photo (
        id       INTEGER PRIMARY KEY,
        owner_id INTEGER,
        group_id INTEGER,
        text     TEXT,
        date     INTEGER
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS photo_comment (
        id             INTEGER PRIMARY KEY,
        event_type     TEXT,
        from_id        INTEGER,
        photo_id       INTEGER,
        photo_owner_id INTEGER,
        text           TEXT,
        date           INTEGER,
        group_id       INTEGER
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS photo_comment_delete (
        id             INTEGER PRIMARY KEY,
        photo_id       INTEGER,
        photo_owner_id INTEGER,
        deleter_id     INTEGER,
        user_id        INTEGER,
        group_id       INTEGER
    )
    """,

    # ── Видео ─────────────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS video (
        id       INTEGER PRIMARY KEY,
        owner_id INTEGER,
        group_id INTEGER,
        title    TEXT,
        duration INTEGER,
        date     INTEGER
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS video_comment (
        id             INTEGER PRIMARY KEY,
        event_type     TEXT,
        from_id        INTEGER,
        video_id       INTEGER,
        video_owner_id INTEGER,
        text           TEXT,
        date           INTEGER,
        group_id       INTEGER
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS video_comment_delete (
        id         INTEGER PRIMARY KEY,
        owner_id   INTEGER,
        user_id    INTEGER,
        deleter_id INTEGER,
        video_id   INTEGER,
        group_id   INTEGER
    )
    """,

    # ── Прочее ────────────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS poll_vote (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id   INTEGER,
        poll_id    INTEGER,
        option_id  INTEGER,
        user_id    INTEGER,
        group_id   INTEGER,
        created_at INTEGER DEFAULT (strftime('%s','now'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS group_officers_edit (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_id   INTEGER,
        user_id    INTEGER,
        level_old  INTEGER,
        level_new  INTEGER,
        group_id   INTEGER,
        created_at INTEGER DEFAULT (strftime('%s','now'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS vkpay_transaction (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        from_id     INTEGER,
        amount      INTEGER,
        description TEXT,
        date        INTEGER,
        group_id    INTEGER
    )
    """,
    '''
    CREATE TABLE IF NOT EXISTS group_data (
        group_id     INTEGER PRIMARY KEY,
        name         TEXT,
        photo_url    TEXT,
        members_count INTEGER,
        updated_at   INTEGER
    );
    ''',
    '''
    CREATE TABLE IF NOT EXISTS vk_servers (
        group_id     INTEGER PRIMARY KEY,
        confirm_code TEXT
    );
    ''',
    '''
    CREATE TABLE IF NOT EXISTS vk_server_secrets (
        group_id INTEGER PRIMARY KEY,
        secret   TEXT NOT NULL
    );
    '''
]

import sqlite3

def create_db():
    conn = sqlite3.connect('DB/main.db')
    cur  = conn.cursor()
    for sql in TABLES:
        cur.execute(sql)
    conn.commit()
    conn.close()
    print(f"БД создана: {'DB/main.db'}")
    print(f"Таблиц: {len(TABLES)}")


if __name__ == "__main__":
    create_db()
