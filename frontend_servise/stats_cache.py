import sqlite3
import time
from datetime import datetime, date, timedelta

import _G


class StatsCache:

    def __init__(self, db_path: str):
        self.db_path    = db_path
        self._cache     = None
        self._cached_at = 0

    def is_data_invalid(self):
        return not (self._cached_at > _G.LAST_ACTION_TIMESTAMP)

    def get(self, with_log: bool = False) -> dict:
        if self._cache and self._cached_at > _G.LAST_ACTION_TIMESTAMP:
            if with_log:
                return self._cache
            return {k: v for k, v in self._cache.items() if k != "log_rows"}

        conn = sqlite3.connect(self.db_path)
        self._cache     = self._build(conn)
        self._cached_at = time.time()
        conn.close()

        if with_log:
            return self._cache
        return {k: v for k, v in self._cache.items() if k != "log_rows"}

    def _build(self, conn) -> dict:
        c = conn.cursor()
        today = date.today()
        KEYS = ("posts", "comments", "likes", "messages", "joined", "left", "photos", "videos")

        def day_ts(d):
            return int(datetime(d.year, d.month, d.day).timestamp())

        def q1(sql):
            try:    return c.execute(sql).fetchone()[0] or 0
            except: return 0

        # ── totals ──
        total_members  = q1("SELECT COUNT(*) FROM group_join") - q1("SELECT COUNT(*) FROM group_leave")
        total_posts    = q1("SELECT COUNT(*) FROM wall_post")
        total_comments = q1("SELECT COUNT(*) FROM wall_reply")
        total_likes    = q1("SELECT COUNT(*) FROM like_event WHERE event_type='like_add'")
        total_messages = q1("SELECT COUNT(*) FROM message WHERE event_type='message_new'")
        total_photos   = q1("SELECT COUNT(*) FROM photo")
        total_videos   = q1("SELECT COUNT(*) FROM video")

        # ── 30-day daily buckets ──
        num_days = 30
        daily = []
        boundaries = []
        for i in range(num_days):
            d = today - timedelta(days=num_days - 1 - i)
            ds = day_ts(d)
            boundaries.append(ds)
            daily.append({"date": d, "ds": ds,
              "posts": 0, "comments": 0, "likes": 0,
              "messages": 0, "joined": 0, "left": 0,
              "photos": 0, "videos": 0})

        boundaries.append(boundaries[-1] + 86400)

        range_start = boundaries[0]
        range_end   = boundaries[-1]

        def fill(table, ts_col, key, extra=""):
            sql = f"SELECT {ts_col} FROM {table} WHERE {ts_col} >= ? AND {ts_col} < ? {extra}"
            for row in c.execute(sql, (range_start, range_end)).fetchall():
                ts = row[0]
                for j in range(num_days):
                    if boundaries[j] <= ts < boundaries[j + 1]:
                        daily[j][key] += 1
                        break

        fill("wall_post",   "date",       "posts")
        fill("wall_reply",  "date",       "comments")
        fill("like_event",  "created_at", "likes",    "AND event_type='like_add'")
        fill("message",     "date",       "messages", "AND event_type='message_new'")
        fill("group_join",  "joined_at",  "joined")
        fill("group_leave", "left_at",    "left")
        fill("photo", "date", "photos")
        fill("video", "date", "videos")

        # ── period builder (max 14 points) ──
        def make_period(slc, max_pts=14):
            n = len(slc)
            totals = {k: 0 for k in KEYS}
            for d in slc:
                for k in KEYS:
                    totals[k] += d[k]

            if n <= max_pts:
                points = [{
                    "label": d["date"].strftime("%d.%m"),
                    **{k: d[k] for k in KEYS}
                } for d in slc]
            else:
                bsz = n / max_pts
                points = []
                for i in range(max_pts):
                    si, ei = int(i * bsz), int((i + 1) * bsz)
                    bucket = slc[si:ei]
                    agg = {k: sum(d[k] for d in bucket) for k in KEYS}
                    agg["label"] = bucket[0]["date"].strftime("%d.%m")
                    points.append(agg)

            return {"points": points, "totals": totals}

        # ── 24h hourly buckets (12 x 2-hour points) ──
        now_ts = int(time.time())
        h24_start = now_ts - 86400
        num_slots = 12
        slot_sec = 7200  # 2 hours

        hourly = [{k: 0 for k in KEYS} for _ in range(num_slots)]

        def fill_hourly(table, ts_col, key, extra=""):
            sql = f"SELECT {ts_col} FROM {table} WHERE {ts_col} >= ? AND {ts_col} < ? {extra}"
            for row in c.execute(sql, (h24_start, now_ts)).fetchall():
                ts = row[0]
                idx = min(int((ts - h24_start) / slot_sec), num_slots - 1)
                hourly[idx][key] += 1

        fill_hourly("wall_post",   "date",       "posts")
        fill_hourly("wall_reply",  "date",       "comments")
        fill_hourly("like_event",  "created_at", "likes",    "AND event_type='like_add'")
        fill_hourly("message",     "date",       "messages", "AND event_type='message_new'")
        fill_hourly("group_join",  "joined_at",  "joined")
        fill_hourly("group_leave", "left_at",    "left")
        fill_hourly("photo", "date", "photos")
        fill_hourly("video", "date", "videos")

        h24_totals = {k: 0 for k in KEYS}
        h24_points = []
        for i, slot in enumerate(hourly):
            slot_start = h24_start + i * slot_sec
            lbl = datetime.fromtimestamp(slot_start).strftime("%H:%M")
            h24_points.append({"label": lbl, **{k: slot[k] for k in KEYS}})
            for k in KEYS:
                h24_totals[k] += slot[k]

        day_data   = {"points": h24_points, "totals": h24_totals}
        week_data  = make_period(daily[-7:])
        month_data = make_period(daily)

        # ── log ──
        raw = []
        raw += [(r[0], "JOIN",    f"user_id={r[1]}",             "+участник")   for r in c.execute("SELECT joined_at, user_id FROM group_join  ORDER BY joined_at DESC LIMIT 20").fetchall()]
        raw += [(r[0], "LEAVE",   f"user_id={r[1]}",             "−участник")   for r in c.execute("SELECT left_at,   user_id FROM group_leave ORDER BY left_at   DESC LIMIT 20").fetchall()]
        raw += [(r[0], "POST",    f"user_id={r[1]} post={r[2]}", "новый пост")  for r in c.execute("SELECT date, from_id, id      FROM wall_post  ORDER BY date DESC LIMIT 20").fetchall()]
        raw += [(r[0], "COMMENT", f"user_id={r[1]} post={r[2]}", "комментарий") for r in c.execute("SELECT date, from_id, post_id FROM wall_reply ORDER BY date DESC LIMIT 20").fetchall()]
        raw += [(r[0], "LIKE",    f"user_id={r[1]} obj={r[2]}",  "лайк")        for r in c.execute("SELECT created_at, liker_id, object_id FROM like_event WHERE event_type='like_add' ORDER BY created_at DESC LIMIT 20").fetchall()]
        raw += [(r[0], "MSG",     f"user_id={r[1]}",             "сообщение")   for r in c.execute("SELECT date, from_id FROM message WHERE event_type='message_new' ORDER BY date DESC LIMIT 20").fetchall()]
        raw.sort(key=lambda x: x[0], reverse=True)
        log_rows = [
            {"time": datetime.fromtimestamp(ts).strftime("%d.%m.%Y %H:%M:%S"),
             "type": etype, "detail": detail, "label": label}
            for ts, etype, detail, label in raw[:60]
        ]

        return {
            "date":            today.strftime("%d.%m.%Y"),
            "total_members":   total_members,
            "total_posts":     total_posts,
            "total_comments":  total_comments,
            "total_likes":     total_likes,
            "total_messages":  total_messages,
            "total_photos":    total_photos,
            "total_videos":    total_videos,
            "month":           month_data,
            "week":            week_data,
            "day":             day_data,
            "log_rows":        log_rows,
        }