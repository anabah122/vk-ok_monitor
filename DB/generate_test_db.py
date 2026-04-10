"""
Generate test.db with realistic fake data.
Range: 7 days ago → 365 days forward.
Density: 2..12 events per day per type.
"""

import sqlite3
import random
import os
from datetime import datetime, date, timedelta

DB_PATH = "DB/test.db"

TABLES_SQL = [
    """CREATE TABLE IF NOT EXISTS wall_post (
        id INTEGER PRIMARY KEY, from_id INTEGER, owner_id INTEGER,
        text TEXT, date INTEGER, likes INTEGER DEFAULT 0,
        comments INTEGER DEFAULT 0, postponed_id INTEGER)""",

    """CREATE TABLE IF NOT EXISTS wall_reply (
        id INTEGER PRIMARY KEY, from_id INTEGER, post_id INTEGER,
        post_owner_id INTEGER, text TEXT, date INTEGER)""",

    """CREATE TABLE IF NOT EXISTS like_event (
        id INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT,
        liker_id INTEGER, object_type TEXT, object_owner_id INTEGER,
        object_id INTEGER, thread_reply_id INTEGER, post_id INTEGER,
        created_at INTEGER DEFAULT (strftime('%s','now')))""",

    """CREATE TABLE IF NOT EXISTS group_join (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
        join_type TEXT, joined_at INTEGER DEFAULT (strftime('%s','now')))""",

    """CREATE TABLE IF NOT EXISTS group_leave (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
        self INTEGER, left_at INTEGER DEFAULT (strftime('%s','now')))""",

    """CREATE TABLE IF NOT EXISTS message (
        id INTEGER PRIMARY KEY, event_type TEXT, from_id INTEGER,
        peer_id INTEGER, text TEXT, date INTEGER,
        conversation_message_id INTEGER, has_attachments INTEGER DEFAULT 0)""",

    """CREATE TABLE IF NOT EXISTS photo (
        id INTEGER PRIMARY KEY, owner_id INTEGER, text TEXT, date INTEGER)""",

    """CREATE TABLE IF NOT EXISTS video (
        id INTEGER PRIMARY KEY, owner_id INTEGER, title TEXT,
        duration INTEGER, date INTEGER)""",
]

USER_IDS = list(range(100001, 100051))  # 50 fake users
GROUP_ID = -200001


def rand_ts(day_start_ts: int) -> int:
    """Random timestamp within a day."""
    return day_start_ts + random.randint(0, 86399)


def day_ts(d: date) -> int:
    return int(datetime(d.year, d.month, d.day).timestamp())


def generate():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for sql in TABLES_SQL:
        cur.execute(sql)

    today = date.today()
    start = today - timedelta(days=7)
    end = today + timedelta(days=365)

    post_id = 1
    reply_id = 1
    msg_id = 1
    photo_id = 1
    video_id = 1
    post_ids_pool = []

    d = start
    while d <= end:
        ds = day_ts(d)

        # -- wall_post: 2..8/day --
        n_posts = random.randint(2, 8)
        for _ in range(n_posts):
            uid = random.choice(USER_IDS)
            ts = rand_ts(ds)
            cur.execute(
                "INSERT INTO wall_post (id, from_id, owner_id, text, date, likes, comments) VALUES (?,?,?,?,?,?,?)",
                (post_id, uid, GROUP_ID, f"Post #{post_id}", ts,
                 random.randint(0, 30), random.randint(0, 15)),
            )
            post_ids_pool.append(post_id)
            post_id += 1

        # -- wall_reply: 4..12/day --
        n_replies = random.randint(4, 12)
        for _ in range(n_replies):
            uid = random.choice(USER_IDS)
            ts = rand_ts(ds)
            pid = random.choice(post_ids_pool) if post_ids_pool else 1
            cur.execute(
                "INSERT INTO wall_reply (id, from_id, post_id, post_owner_id, text, date) VALUES (?,?,?,?,?,?)",
                (reply_id, uid, pid, GROUP_ID, f"Reply #{reply_id}", ts),
            )
            reply_id += 1

        # -- like_event: 3..12/day (mostly like_add, ~15% like_remove) --
        n_likes = random.randint(3, 12)
        for _ in range(n_likes):
            uid = random.choice(USER_IDS)
            ts = rand_ts(ds)
            etype = "like_remove" if random.random() < 0.15 else "like_add"
            oid = random.choice(post_ids_pool) if post_ids_pool else 1
            cur.execute(
                "INSERT INTO like_event (event_type, liker_id, object_type, object_owner_id, object_id, created_at) VALUES (?,?,?,?,?,?)",
                (etype, uid, "post", GROUP_ID, oid, ts),
            )

        # -- group_join: 2..6/day --
        n_join = random.randint(2, 6)
        for _ in range(n_join):
            uid = random.randint(200000, 299999)
            ts = rand_ts(ds)
            cur.execute(
                "INSERT INTO group_join (user_id, join_type, joined_at) VALUES (?,?,?)",
                (uid, "approved", ts),
            )

        # -- group_leave: 0..4/day (fewer than joins → net growth) --
        n_leave = random.randint(0, 4)
        for _ in range(n_leave):
            uid = random.randint(200000, 299999)
            ts = rand_ts(ds)
            cur.execute(
                "INSERT INTO group_leave (user_id, self, left_at) VALUES (?,?,?)",
                (uid, 1, ts),
            )

        # -- message: 2..10/day --
        n_msg = random.randint(2, 10)
        for _ in range(n_msg):
            uid = random.choice(USER_IDS)
            ts = rand_ts(ds)
            cur.execute(
                "INSERT INTO message (id, event_type, from_id, peer_id, text, date) VALUES (?,?,?,?,?,?)",
                (msg_id, "message_new", uid, GROUP_ID, f"Msg #{msg_id}", ts),
            )
            msg_id += 1

        # -- photo: 0..3/day --
        n_photo = random.randint(0, 3)
        for _ in range(n_photo):
            uid = random.choice(USER_IDS)
            ts = rand_ts(ds)
            cur.execute(
                "INSERT INTO photo (id, owner_id, text, date) VALUES (?,?,?,?)",
                (photo_id, uid, "", ts),
            )
            photo_id += 1

        # -- video: 0..2/day --
        n_video = random.randint(0, 2)
        for _ in range(n_video):
            uid = random.choice(USER_IDS)
            ts = rand_ts(ds)
            cur.execute(
                "INSERT INTO video (id, owner_id, title, duration, date) VALUES (?,?,?,?,?)",
                (video_id, uid, f"Video #{video_id}", random.randint(30, 600), ts),
            )
            video_id += 1

        d += timedelta(days=1)

    conn.commit()

    # stats
    counts = {}
    for tbl in ["wall_post", "wall_reply", "like_event", "group_join",
                 "group_leave", "message", "photo", "video"]:
        counts[tbl] = cur.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
    conn.close()

    print(f"Created {DB_PATH}")
    for tbl, cnt in counts.items():
        print(f"  {tbl}: {cnt}")


if __name__ == "__main__":
    generate()
