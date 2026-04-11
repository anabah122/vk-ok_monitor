from datetime import datetime
from DB import DB


def _ts(unix):
    return datetime.fromtimestamp(unix).strftime("%H:%M:%S")


class WallMixin:

    def on_wall_post_new(self, o, group_id=None):
        pid     = o.get("id")
        from_id = o.get("from_id")
        text    = o.get("text", "")[:80]
        likes   = o.get("likes", {}).get("count", 0)
        cmts    = o.get("comments", {}).get("count", 0)
        date    = o.get("date", 0)
        print(f"  📝 Новый пост #{pid} от {from_id} [{_ts(date)}]")
        print(f"     Текст: {text!r}")
        print(f"     Лайков: {likes} | Комментов: {cmts}")
        DB.insert("wall_post", {
            "id": pid, "from_id": from_id, "group_id": group_id,
            "text": o.get("text", ""), "date": date,
            "likes": likes, "comments": cmts,
            "postponed_id": o.get("postponed_id"),
        })

    def on_wall_repost(self, o, group_id=None):
        pid     = o.get("id")
        from_id = o.get("from_id")
        text    = o.get("text", "")[:60]
        print(f"  🔁 Репост #{pid} от {from_id}: {text!r}")
        DB.insert("wall_post", {
            "id": pid, "from_id": from_id, "group_id": group_id,
            "text": o.get("text", ""), "date": o.get("date", 0),
            "likes": o.get("likes", {}).get("count", 0),
            "comments": o.get("comments", {}).get("count", 0),
            "postponed_id": o.get("postponed_id"),
        })

    def on_wall_reply_new(self, o, group_id=None):
        cid     = o.get("id")
        from_id = o.get("from_id")
        post_id = o.get("post_id")
        text    = o.get("text", "")[:80]
        print(f"  💬 Новый комментарий #{cid} к посту #{post_id} от {from_id}")
        print(f"     {text!r}")
        DB.insert("wall_reply", {
            "id": cid, "from_id": from_id, "post_id": post_id,
            "group_id": group_id,
            "text": o.get("text", ""), "date": o.get("date", 0),
        })

    def on_wall_reply_edit(self, o, group_id=None):
        cid     = o.get("id")
        post_id = o.get("post_id")
        text    = o.get("text", "")[:80]
        print(f"  ✏️  Комментарий #{cid} к посту #{post_id} отредактирован: {text!r}")
        DB.insert("wall_reply", {
            "id": cid, "from_id": o.get("from_id"), "post_id": post_id,
            "group_id": group_id,
            "text": o.get("text", ""), "date": o.get("date", 0),
        })

    def on_wall_reply_restore(self, o, group_id=None):
        cid     = o.get("id")
        post_id = o.get("post_id")
        print(f"  ♻️  Комментарий #{cid} к посту #{post_id} восстановлен")
        DB.insert("wall_reply", {
            "id": cid, "from_id": o.get("from_id"), "post_id": post_id,
            "group_id": group_id,
            "text": o.get("text", ""), "date": o.get("date", 0),
        })

    def on_wall_reply_delete(self, o, group_id=None):
        cid     = o.get("id")
        post_id = o.get("post_id")
        deleter = o.get("deleter_id")
        print(f"  🗑️  Комментарий #{cid} к посту #{post_id} удалён пользователем {deleter}")
        DB.insert("wall_reply_delete", {
            "id": cid, "group_id": group_id,
            "deleter_id": deleter, "post_id": post_id,
        })

    def on_wall_schedule_post_new(self, o, group_id=None):
        pid  = o.get("id")
        date = o.get("schedule_time", 0)
        print(f"  🕐 Отложенный пост #{pid} запланирован на {_ts(date)}")
        DB.insert("wall_schedule_post", {"id": pid, "schedule_time": date, "group_id": group_id})

    def on_wall_schedule_post_delete(self, o, group_id=None):
        pid  = o.get("id")
        date = o.get("schedule_time", 0)
        print(f"  🗑️  Отложенный пост #{pid} (был на {_ts(date)}) удалён")
        DB.insert("wall_schedule_post", {"id": pid, "schedule_time": date, "group_id": group_id})
