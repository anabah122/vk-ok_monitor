from DB import db


class MediaMixin:

    # ── Фото ──────────────────────────────────────────────────────────

    def on_photo_new(self, o, group_id=None):
        pid   = o.get("id")
        owner = o.get("owner_id")
        text  = o.get("text", "")[:60]
        print(f"  🖼️  Новое фото #{pid} от {owner}" + (f": {text!r}" if text else ""))
        db.insert("photo", {
            "id": pid, "owner_id": owner, "group_id": group_id,
            "text": o.get("text", ""), "date": o.get("date", 0),
        })

    def on_photo_comment_new(self, o, group_id=None):
        cid      = o.get("id")
        from_id  = o.get("from_id")
        photo_id = o.get("photo_id")
        text     = o.get("text", "")[:60]
        print(f"  🖼️💬 Комментарий #{cid} к фото #{photo_id} от {from_id}: {text!r}")
        db.insert("photo_comment", {
            "id": cid, "event_type": "photo_comment_new",
            "from_id": from_id, "photo_id": photo_id,
            "photo_owner_id": o.get("photo_owner_id"),
            "text": o.get("text", ""), "date": o.get("date", 0),
            "group_id": group_id,
        })

    def on_photo_comment_edit(self, o, group_id=None):
        cid      = o.get("id")
        photo_id = o.get("photo_id")
        text     = o.get("text", "")[:60]
        print(f"  🖼️✏️  Комментарий #{cid} к фото #{photo_id} отредактирован: {text!r}")
        db.insert("photo_comment", {
            "id": cid, "event_type": "photo_comment_edit",
            "from_id": o.get("from_id"), "photo_id": photo_id,
            "photo_owner_id": o.get("photo_owner_id"),
            "text": o.get("text", ""), "date": o.get("date", 0),
            "group_id": group_id,
        })

    def on_photo_comment_restore(self, o, group_id=None):
        cid      = o.get("id")
        photo_id = o.get("photo_id")
        print(f"  🖼️♻️  Комментарий #{cid} к фото #{photo_id} восстановлен")
        db.insert("photo_comment", {
            "id": cid, "event_type": "photo_comment_restore",
            "from_id": o.get("from_id"), "photo_id": photo_id,
            "photo_owner_id": o.get("photo_owner_id"),
            "text": o.get("text", ""), "date": o.get("date", 0),
            "group_id": group_id,
        })

    def on_photo_comment_delete(self, o, group_id=None):
        cid      = o.get("id")
        photo_id = o.get("photo_id")
        deleter  = o.get("deleter_id")
        print(f"  🖼️🗑️  Комментарий #{cid} к фото #{photo_id} удалён пользователем {deleter}")
        db.insert("photo_comment_delete", {
            "id": cid, "photo_id": photo_id,
            "photo_owner_id": o.get("photo_owner_id"),
            "deleter_id": deleter, "user_id": o.get("user_id"),
            "group_id": group_id,
        })

    # ── Видео ─────────────────────────────────────────────────────────

    def on_video_new(self, o, group_id=None):
        vid   = o.get("id")
        owner = o.get("owner_id")
        title = o.get("title", "")
        dur   = o.get("duration", 0)
        print(f"  🎥 Новое видео #{vid} от {owner}: {title!r} ({dur}с)")
        db.insert("video", {
            "id": vid, "owner_id": owner, "group_id": group_id,
            "title": title, "duration": dur, "date": o.get("date", 0),
        })

    def on_video_comment_new(self, o, group_id=None):
        cid      = o.get("id")
        from_id  = o.get("from_id")
        video_id = o.get("video_id")
        text     = o.get("text", "")[:60]
        print(f"  🎥💬 Комментарий #{cid} к видео #{video_id} от {from_id}: {text!r}")
        db.insert("video_comment", {
            "id": cid, "event_type": "video_comment_new",
            "from_id": from_id, "video_id": video_id,
            "video_owner_id": o.get("video_owner_id"),
            "text": o.get("text", ""), "date": o.get("date", 0),
            "group_id": group_id,
        })

    def on_video_comment_edit(self, o, group_id=None):
        cid      = o.get("id")
        video_id = o.get("video_id")
        text     = o.get("text", "")[:60]
        print(f"  🎥✏️  Комментарий #{cid} к видео #{video_id} отредактирован: {text!r}")
        db.insert("video_comment", {
            "id": cid, "event_type": "video_comment_edit",
            "from_id": o.get("from_id"), "video_id": video_id,
            "video_owner_id": o.get("video_owner_id"),
            "text": o.get("text", ""), "date": o.get("date", 0),
            "group_id": group_id,
        })

    def on_video_comment_restore(self, o, group_id=None):
        cid      = o.get("id")
        video_id = o.get("video_id")
        print(f"  🎥♻️  Комментарий #{cid} к видео #{video_id} восстановлен")
        db.insert("video_comment", {
            "id": cid, "event_type": "video_comment_restore",
            "from_id": o.get("from_id"), "video_id": video_id,
            "video_owner_id": o.get("video_owner_id"),
            "text": o.get("text", ""), "date": o.get("date", 0),
            "group_id": group_id,
        })

    def on_video_comment_delete(self, o, group_id=None):
        cid      = o.get("id")
        video_id = o.get("video_id")
        deleter  = o.get("deleter_id")
        print(f"  🎥🗑️  Комментарий #{cid} к видео #{video_id} удалён пользователем {deleter}")
        db.insert("video_comment_delete", {
            "id": cid, "owner_id": o.get("owner_id"),
            "user_id": o.get("user_id"),
            "deleter_id": deleter, "video_id": video_id,
            "group_id": group_id,
        })

    # ── Аудио ─────────────────────────────────────────────────────────

    def on_audio_new(self, o, group_id=None):
        aid    = o.get("id")
        owner  = o.get("owner_id")
        artist = o.get("artist", "")
        title  = o.get("title", "")
        print(f"  🎵 Новое аудио #{aid} от {owner}: {artist} — {title}")
        db.insert("audio", {
            "id": aid, "owner_id": owner, "group_id": group_id,
            "artist": artist, "title": title, "date": o.get("date", 0),
        })
