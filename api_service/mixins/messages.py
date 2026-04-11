from datetime import datetime
from DB import DB


def _ts(unix):
    return datetime.fromtimestamp(unix).strftime("%H:%M:%S")


class MessagesMixin:

    def on_message_new(self, o, group_id=None):
        msg     = o.get("message", {})
        mid     = msg.get("id")
        from_id = msg.get("from_id")
        text    = msg.get("text", "")[:80]
        date    = msg.get("date", 0)
        atts    = msg.get("attachments", [])
        att_str = f" | вложений: {len(atts)}" if atts else ""
        print(f"  ✉️  Новое сообщение #{mid} от {from_id} [{_ts(date)}]")
        print(f"     {text!r}{att_str}")
        DB.insert("message", {
            "id": mid, "event_type": "message_new",
            "from_id": from_id, "peer_id": msg.get("peer_id"),
            "text": msg.get("text", ""), "date": date,
            "conversation_message_id": msg.get("conversation_message_id"),
            "has_attachments": 1 if atts else 0,
            "group_id": group_id,
        })

    def on_message_reply(self, o, group_id=None):
        mid     = o.get("id")
        text    = o.get("text", "")[:80]
        peer_id = o.get("peer_id")
        print(f"  ✉️↩️  Исходящее сообщение #{mid} в {peer_id}: {text!r}")
        DB.insert("message", {
            "id": mid, "event_type": "message_reply",
            "from_id": o.get("from_id"), "peer_id": peer_id,
            "text": o.get("text", ""), "date": o.get("date", 0),
            "conversation_message_id": o.get("conversation_message_id"),
            "has_attachments": 0, "group_id": group_id,
        })

    def on_message_edit(self, o, group_id=None):
        mid     = o.get("id")
        text    = o.get("text", "")[:80]
        peer_id = o.get("peer_id")
        print(f"  ✉️✏️  Сообщение #{mid} в {peer_id} отредактировано: {text!r}")
        DB.insert("message", {
            "id": mid, "event_type": "message_edit",
            "from_id": o.get("from_id"), "peer_id": peer_id,
            "text": o.get("text", ""), "date": o.get("date", 0),
            "conversation_message_id": o.get("conversation_message_id"),
            "has_attachments": 0, "group_id": group_id,
        })

    def on_message_allow(self, o, group_id=None):
        user = o.get("user_id")
        print(f"  ✅ Пользователь {user} разрешил сообщения от сообщества")
        DB.insert("message_allow", {"user_id": user, "key": o.get("key", ""), "group_id": group_id})

    def on_message_deny(self, o, group_id=None):
        user = o.get("user_id")
        print(f"  🚫 Пользователь {user} запретил сообщения от сообщества")
        DB.insert("message_deny", {"user_id": user, "group_id": group_id})

    def on_message_read(self, o, group_id=None):
        from_id = o.get("from_id")
        peer_id = o.get("peer_id")
        msg_id  = o.get("read_message_id")
        print(f"  👁️  Сообщение #{msg_id} прочитано: {from_id} → {peer_id}")

    def on_message_event(self, o, group_id=None):
        user    = o.get("user_id")
        peer_id = o.get("peer_id")
        payload = o.get("payload", "")
        print(f"  🔘 Callback-кнопка от {user} в {peer_id}: payload={payload!r}")
        DB.insert("message_event", {
            "user_id": user, "peer_id": peer_id,
            "event_id": o.get("event_id"), "payload": str(payload),
            "conversation_message_id": o.get("conversation_message_id"),
            "group_id": group_id,
        })
