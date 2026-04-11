import sqlite3
import time
from datetime import datetime, date, timedelta
from dataclasses import dataclass, field


@dataclass
class CacheEntry:
    is_valid: bool
    data:     dict


class StatsCache:

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._cache: dict[frozenset, CacheEntry] = {}

    def set_group_invalid(self, group_id: int) -> None:
        for key, entry in self._cache.items():
            if group_id in key:
                entry.is_valid = False

    def is_data_invalid(self):
        return any(not entry.is_valid for entry in self._cache.values())

    def get(self, user) -> dict:
        key   = frozenset(user.group_ids)
        entry = self._cache.get(key)

        if entry and entry.is_valid:
            return {k: v for k, v in entry.data.items() if k != "log_rows"}

        conn = sqlite3.connect(self.db_path)
        data = self._build(conn, user.group_ids)
        conn.close()

        self._cache[key] = CacheEntry(is_valid=True, data=data)
        return {k: v for k, v in data.items() if k != "log_rows"}
    

    def _build(self, conn, group_ids: list[int]) -> dict:
        c = conn.cursor()
        today = date.today()
        KEYS = ("posts", "comments", "likes", "messages", "joined", "left", "photos", "videos")

        # WHERE group_id IN (...)
        gids     = group_ids if group_ids else []
        in_ph    = ",".join("?" * len(gids)) if gids else "NULL"
        gid_filt = f" AND group_id IN ({in_ph})" if gids else " AND 1=0"

        def day_ts(d):
            return int(datetime(d.year, d.month, d.day).timestamp())

        def q1(sql, params=()):
            try:    return c.execute(sql, list(params)).fetchone()[0] or 0
            except: return 0

        # ── totals ──
        total_members  = (q1(f"SELECT COUNT(*) FROM group_join  WHERE 1=1{gid_filt}", gids) -
                          q1(f"SELECT COUNT(*) FROM group_leave WHERE 1=1{gid_filt}", gids))
        total_posts    = q1(f"SELECT COUNT(*) FROM wall_post WHERE 1=1{gid_filt}", gids)
        total_comments = q1(f"SELECT COUNT(*) FROM wall_reply WHERE 1=1{gid_filt}", gids)
        total_likes    = q1(f"SELECT COUNT(*) FROM like_event WHERE event_type='like_add'{gid_filt}", gids)
        total_messages = q1(f"SELECT COUNT(*) FROM message WHERE event_type='message_new'{gid_filt}", gids)
        total_photos   = q1(f"SELECT COUNT(*) FROM photo WHERE 1=1{gid_filt}", gids)
        total_videos   = q1(f"SELECT COUNT(*) FROM video WHERE 1=1{gid_filt}", gids)

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
            sql = f"SELECT {ts_col} FROM {table} WHERE {ts_col} >= ? AND {ts_col} < ?{extra}{gid_filt}"
            params = [range_start, range_end] + gids
            for row in c.execute(sql, params).fetchall():
                ts = row[0]
                for j in range(num_days):
                    if boundaries[j] <= ts < boundaries[j + 1]:
                        daily[j][key] += 1
                        break

        fill("wall_post",   "date",       "posts")
        fill("wall_reply",  "date",       "comments")
        fill("like_event",  "created_at", "likes",    " AND event_type='like_add'")
        fill("message",     "date",       "messages", " AND event_type='message_new'")
        fill("group_join",  "joined_at",  "joined")
        fill("group_leave", "left_at",    "left")
        fill("photo",       "date",       "photos")
        fill("video",       "date",       "videos")

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
        now_ts    = int(time.time())
        h24_start = now_ts - 86400
        num_slots = 12
        slot_sec  = 7200

        hourly = [{k: 0 for k in KEYS} for _ in range(num_slots)]

        def fill_hourly(table, ts_col, key, extra=""):
            sql = f"SELECT {ts_col} FROM {table} WHERE {ts_col} >= ? AND {ts_col} < ?{extra}{gid_filt}"
            params = [h24_start, now_ts] + gids
            for row in c.execute(sql, params).fetchall():
                ts = row[0]
                idx = min(int((ts - h24_start) / slot_sec), num_slots - 1)
                hourly[idx][key] += 1

        fill_hourly("wall_post",   "date",       "posts")
        fill_hourly("wall_reply",  "date",       "comments")
        fill_hourly("like_event",  "created_at", "likes",    " AND event_type='like_add'")
        fill_hourly("message",     "date",       "messages", " AND event_type='message_new'")
        fill_hourly("group_join",  "joined_at",  "joined")
        fill_hourly("group_leave", "left_at",    "left")
        fill_hourly("photo",       "date",       "photos")
        fill_hourly("video",       "date",       "videos")

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
        raw += [(r[0], "JOIN",    f"user_id={r[1]}",             "+участник")   for r in c.execute(f"SELECT joined_at, user_id FROM group_join  WHERE 1=1{gid_filt} ORDER BY joined_at DESC LIMIT 20", gids).fetchall()]
        raw += [(r[0], "LEAVE",   f"user_id={r[1]}",             "−участник")   for r in c.execute(f"SELECT left_at,   user_id FROM group_leave WHERE 1=1{gid_filt} ORDER BY left_at   DESC LIMIT 20", gids).fetchall()]
        raw += [(r[0], "POST",    f"user_id={r[1]} post={r[2]}", "новый пост")  for r in c.execute(f"SELECT date, from_id, id      FROM wall_post  WHERE 1=1{gid_filt} ORDER BY date DESC LIMIT 20", gids).fetchall()]
        raw += [(r[0], "COMMENT", f"user_id={r[1]} post={r[2]}", "комментарий") for r in c.execute(f"SELECT date, from_id, post_id FROM wall_reply WHERE 1=1{gid_filt} ORDER BY date DESC LIMIT 20", gids).fetchall()]
        raw += [(r[0], "LIKE",    f"user_id={r[1]} obj={r[2]}",  "лайк")        for r in c.execute(f"SELECT created_at, liker_id, object_id FROM like_event WHERE event_type='like_add'{gid_filt} ORDER BY created_at DESC LIMIT 20", gids).fetchall()]
        raw += [(r[0], "MSG",     f"user_id={r[1]}",             "сообщение")   for r in c.execute(f"SELECT date, from_id FROM message WHERE event_type='message_new'{gid_filt} ORDER BY date DESC LIMIT 20", gids).fetchall()]
        raw.sort(key=lambda x: x[0], reverse=True)
        log_rows = [
            {"time": datetime.fromtimestamp(ts).strftime("%d.%m.%Y %H:%M:%S"),
             "type": etype, "detail": detail, "label": label}
            for ts, etype, detail, label in raw[:60]
        ]

        return {
            "date":           today.strftime("%d.%m.%Y"),
            "total_members":  total_members,
            "total_posts":    total_posts,
            "total_comments": total_comments,
            "total_likes":    total_likes,
            "total_messages": total_messages,
            "total_photos":   total_photos,
            "total_videos":   total_videos,
            "month":          month_data,
            "week":           week_data,
            "day":            day_data,
            "log_rows":       log_rows,
        }