from DB import db

JOIN_TYPES = {
    "join":     "вступил сам",
    "unsure":   "возможно пойдёт",
    "accepted": "принял приглашение",
    "approved": "заявка одобрена",
    "request":  "подал заявку",
}

BLOCK_REASONS = {
    0: "другое",
    1: "спам",
    2: "оскорбление участников",
    3: "нецензурные выражения",
    4: "сообщения не по теме",
}


class MembersMixin:

    def on_group_join(self, o):
        user_id   = o.get("user_id")
        join_type = o.get("join_type", "")
        print(f"  👤 Вступил {user_id} — {JOIN_TYPES.get(join_type, join_type)}")
        db.insert("group_join", {"user_id": user_id, "join_type": join_type})

    def on_group_leave(self, o):
        user_id = o.get("user_id")
        self_   = o.get("self", 0)
        print(f"  🚪 Покинул {user_id} — {'сам вышел' if self_ else 'исключён'}")
        db.insert("group_leave", {"user_id": user_id, "self": self_})

    def on_user_block(self, o):
        admin   = o.get("admin_id")
        user    = o.get("user_id")
        reason  = o.get("reason", 0)
        comment = o.get("comment", "")
        print(f"  🚫 Пользователь {user} заблокирован администратором {admin}")
        print(f"     Причина: {BLOCK_REASONS.get(reason, 'другое')}" + (f" | {comment}" if comment else ""))
        db.insert("user_block", {
            "admin_id": admin, "user_id": user,
            "unblock_date": o.get("unblock_date"),
            "reason": reason, "comment": comment,
        })

    def on_user_unblock(self, o):
        admin = o.get("admin_id")
        user  = o.get("user_id")
        print(f"  ✅ Пользователь {user} разблокирован администратором {admin}")
        db.insert("user_unblock", {
            "admin_id": admin, "user_id": user,
            "by_end_date": o.get("by_end_date"),
        })
