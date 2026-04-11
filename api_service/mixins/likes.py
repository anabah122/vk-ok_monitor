from DB import DB


class LikesMixin:

    def on_like_add(self, o, group_id=None):
        liker    = o.get("liker_id")
        obj_type = o.get("object_type")
        obj_id   = o.get("object_id")
        owner_id = o.get("object_owner_id")
        post_id  = o.get("post_id")
        extra = f" (пост #{post_id})" if post_id else ""
        print(f"  ❤️  Лайк от {liker} на {obj_type} #{obj_id} владельца {owner_id}{extra}")
        DB.insert("like_event", {
            "event_type": "like_add", "liker_id": liker,
            "object_type": obj_type, "object_owner_id": owner_id,
            "object_id": obj_id, "thread_reply_id": o.get("thread_reply_id"),
            "post_id": post_id, "group_id": group_id,
        })

    def on_like_remove(self, o, group_id=None):
        liker    = o.get("liker_id")
        obj_type = o.get("object_type")
        obj_id   = o.get("object_id")
        owner_id = o.get("object_owner_id")
        print(f"  💔 Убран лайк от {liker} на {obj_type} #{obj_id} владельца {owner_id}")
        DB.insert("like_event", {
            "event_type": "like_remove", "liker_id": liker,
            "object_type": obj_type, "object_owner_id": owner_id,
            "object_id": obj_id, "thread_reply_id": o.get("thread_reply_id"),
            "post_id": o.get("post_id"), "group_id": group_id,
        })
