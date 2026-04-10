import sqlite3
import time
from datetime import datetime, date, timedelta

import _G 

class StatsCache:

    def __init__(self, db_path: str):
        self.db_path    = db_path
        self._cache     = None
        self._dv        = None
        self._cached_at = 0

    def is_data_invalid(self):
        return not ( self._cached_at > _G.LAST_ACTION_TIMESTAMP )

    def get(self) -> dict:

        if self._cache and self._cached_at > _G.LAST_ACTION_TIMESTAMP :
            return self._cache

        conn = sqlite3.connect(self.db_path)
        self._cache     = self._build(conn)
        self._cached_at = time.time()
        conn.close()
        return self._cache


    def _build(self, conn) -> dict:
        c = conn.cursor()

        today      = date.today()
        ts_start   = int(datetime(today.year, today.month, today.day).timestamp())
        ts_end     = ts_start + 86400
        yesterday  = today - timedelta(days=1)
        yday_start = int(datetime(yesterday.year, yesterday.month, yesterday.day).timestamp())
        yday_end   = ts_start
        week_start = ts_start - 6 * 86400

        def q(sql, params=()):
            try:
                return c.execute(sql, params).fetchone()[0] or 0
            except Exception:
                return 0

        def qq(sql, params=()):
            try:
                return c.execute(sql, params).fetchall()
            except Exception:
                return []

        joined   = q("SELECT COUNT(*) FROM group_join  WHERE joined_at >= ? AND joined_at < ?", (ts_start, ts_end))
        left_cnt = q("SELECT COUNT(*) FROM group_leave WHERE left_at   >= ? AND left_at   < ?", (ts_start, ts_end))
        posts    = q("SELECT COUNT(*) FROM wall_post   WHERE date      >= ? AND date      < ?", (ts_start, ts_end))
        comments = q("SELECT COUNT(*) FROM wall_reply  WHERE date      >= ? AND date      < ?", (ts_start, ts_end))
        likes    = q("SELECT COUNT(*) FROM like_event  WHERE event_type='like_add'    AND created_at >= ? AND created_at < ?", (ts_start, ts_end))
        unlikes  = q("SELECT COUNT(*) FROM like_event  WHERE event_type='like_remove' AND created_at >= ? AND created_at < ?", (ts_start, ts_end))
        videos   = q("SELECT COUNT(*) FROM video        WHERE date >= ? AND date < ?", (ts_start, ts_end))
        photos   = q("SELECT COUNT(*) FROM photo        WHERE date >= ? AND date < ?", (ts_start, ts_end))
        messages = q("SELECT COUNT(*) FROM message WHERE event_type='message_new' AND date >= ? AND date < ?", (ts_start, ts_end))

        posts_yday    = q("SELECT COUNT(*) FROM wall_post  WHERE date      >= ? AND date      < ?", (yday_start, yday_end))
        comments_yday = q("SELECT COUNT(*) FROM wall_reply WHERE date      >= ? AND date      < ?", (yday_start, yday_end))
        likes_yday    = q("SELECT COUNT(*) FROM like_event WHERE event_type='like_add' AND created_at >= ? AND created_at < ?", (yday_start, yday_end))
        messages_yday = q("SELECT COUNT(*) FROM message    WHERE event_type='message_new' AND date >= ? AND date < ?", (yday_start, yday_end))
        joined_yday   = q("SELECT COUNT(*) FROM group_join  WHERE joined_at >= ? AND joined_at < ?", (yday_start, yday_end))
        left_yday     = q("SELECT COUNT(*) FROM group_leave WHERE left_at   >= ? AND left_at   < ?", (yday_start, yday_end))

        joined_week   = q("SELECT COUNT(*) FROM group_join  WHERE joined_at >= ?", (week_start,))
        left_week     = q("SELECT COUNT(*) FROM group_leave WHERE left_at   >= ?", (week_start,))
        posts_week    = q("SELECT COUNT(*) FROM wall_post   WHERE date      >= ?", (week_start,))
        likes_week    = q("SELECT COUNT(*) FROM like_event  WHERE event_type='like_add' AND created_at >= ?", (week_start,))
        messages_week = q("SELECT COUNT(*) FROM message     WHERE event_type='message_new' AND date >= ?", (week_start,))

        total_members = q("SELECT COUNT(*) FROM group_join") - q("SELECT COUNT(*) FROM group_leave")
        total_posts   = q("SELECT COUNT(*) FROM wall_post")
        total_photos  = q("SELECT COUNT(*) FROM photo")
        total_videos  = q("SELECT COUNT(*) FROM video")

        raw = []
        raw += [(r[0], "JOIN",    f"user_id={r[1]}",             "+участник")    for r in qq("SELECT joined_at, user_id FROM group_join  ORDER BY joined_at DESC LIMIT 20")]
        raw += [(r[0], "LEAVE",   f"user_id={r[1]}",             "−участник")    for r in qq("SELECT left_at,   user_id FROM group_leave ORDER BY left_at   DESC LIMIT 20")]
        raw += [(r[0], "POST",    f"user_id={r[1]} post={r[2]}", "новый пост")   for r in qq("SELECT date, from_id, id      FROM wall_post  ORDER BY date DESC LIMIT 20")]
        raw += [(r[0], "COMMENT", f"user_id={r[1]} post={r[2]}", "комментарий")  for r in qq("SELECT date, from_id, post_id FROM wall_reply ORDER BY date DESC LIMIT 20")]
        raw += [(r[0], "LIKE",    f"user_id={r[1]} obj={r[2]}",  "лайк")         for r in qq("SELECT created_at, liker_id, object_id FROM like_event WHERE event_type='like_add' ORDER BY created_at DESC LIMIT 20")]
        raw += [(r[0], "MSG",     f"user_id={r[1]}",             "сообщение")    for r in qq("SELECT date, from_id FROM message WHERE event_type='message_new' ORDER BY date DESC LIMIT 20")]
        raw += [(r[0], "PHOTO",   f"user_id={r[1]}",             "фото")         for r in qq("SELECT date, owner_id FROM photo ORDER BY date DESC LIMIT 10")]
        raw += [(r[0], "VIDEO",   f"user_id={r[1]}",             "видео")        for r in qq("SELECT date, owner_id FROM video ORDER BY date DESC LIMIT 10")]

        raw.sort(key=lambda x: x[0], reverse=True)
        log_rows = [
            {"time": datetime.fromtimestamp(ts).strftime("%d.%m.%Y %H:%M:%S"),
             "type": etype, "detail": detail, "label": label}
            for ts, etype, detail, label in raw[:60]
        ]

        def delta(val, prev):
            d = val - prev
            if d > 0: return f"+{d}", "plus"
            if d < 0: return str(d), "minus"
            return "±0", "zero"

        members_delta                  = joined - left_cnt
        posts_df,    posts_dc          = delta(posts,    posts_yday)
        comments_df, comments_dc       = delta(comments, comments_yday)
        likes_df,    likes_dc          = delta(likes,    likes_yday)
        messages_df, messages_dc       = delta(messages, messages_yday)

        return {
            "date":                today.strftime("%d.%m.%Y"),
            "members_joined":      joined,
            "members_left":        left_cnt,
            "members_delta_fmt":   f"+{members_delta}" if members_delta > 0 else str(members_delta),
            "members_delta_class": "plus" if members_delta > 0 else ("minus" if members_delta < 0 else "zero"),
            "posts":    posts,    "comments": comments, "likes":   likes,
            "unlikes":  unlikes,  "videos":   videos,   "photos":  photos,
            "messages": messages,
            "posts_diff_fmt":    posts_df,    "posts_diff_class":    posts_dc,
            "comments_diff_fmt": comments_df, "comments_diff_class": comments_dc,
            "likes_diff_fmt":    likes_df,    "likes_diff_class":    likes_dc,
            "messages_diff_fmt": messages_df, "messages_diff_class": messages_dc,
            "joined_yday":    joined_yday,   "left_yday":      left_yday,
            "joined_week":    joined_week,   "left_week":      left_week,
            "posts_week":     posts_week,    "likes_week":     likes_week,
            "messages_week":  messages_week,
            "total_members":  total_members, "total_posts":    total_posts,
            "total_photos":   total_photos,  "total_videos":   total_videos,
            "log_rows":       log_rows,
        }