from DB import db


class MiscMixin:

    def on_poll_vote_new(self, o, group_id=None):
        user    = o.get("user_id")
        poll_id = o.get("poll_id")
        option  = o.get("option_id")
        print(f"  📊 Голос в опросе #{poll_id} от {user}, вариант #{option}")
        db.insert("poll_vote", {
            "owner_id": o.get("owner_id"), "poll_id": poll_id,
            "option_id": option, "user_id": user,
            "group_id": group_id,
        })

    def on_group_officers_edit(self, o, group_id=None):
        admin     = o.get("admin_id")
        user      = o.get("user_id")
        level_old = o.get("level_old")
        level_new = o.get("level_new")
        levels = {0: "нет", 1: "модератор", 2: "редактор", 3: "администратор"}
        print(f"  👮 Права {user} изменены администратором {admin}: "
              f"{levels.get(level_old)} → {levels.get(level_new)}")
        db.insert("group_officers_edit", {
            "admin_id": admin, "user_id": user,
            "level_old": level_old, "level_new": level_new,
            "group_id": group_id,
        })

    def on_group_change_settings(self, o, group_id=None):
        user    = o.get("user_id")
        changes = o.get("changes", {})
        print(f"  ⚙️  Настройки сообщества изменены пользователем {user}")
        for field, vals in changes.items():
            old = vals.get("old_value", "?")
            new = vals.get("new_value", "?")
            print(f"     {field}: {old!r} → {new!r}")

    def on_group_change_photo(self, o, group_id=None):
        user = o.get("user_id")
        print(f"  🖼️  Фото сообщества изменено пользователем {user}")

    def on_vkpay_transaction(self, o, group_id=None):
        from_id = o.get("from_id")
        amount  = o.get("amount", 0) / 1000
        desc    = o.get("description", "")
        print(f"  💳 VK Pay перевод от {from_id}: {amount:.2f}₽ — {desc!r}")
        db.insert("vkpay_transaction", {
            "from_id": from_id, "amount": o.get("amount", 0),
            "description": desc, "date": o.get("date", 0),
            "group_id": group_id,
        })

    # ── Donut ─────────────────────────────────────────────────────────

    def on_donut_subscription_create(self, o, group_id=None):
        user   = o.get("user_id")
        amount = o.get("amount", 0)
        print(f"  🍩 Новая подписка Donut от {user}: {amount}₽/мес")
        db.insert("donut_subscription", {
            "event_type": "create", "user_id": user,
            "amount": amount, "amount_without_fee": o.get("amount_without_fee"),
            "group_id": group_id,
        })

    def on_donut_subscription_prolonged(self, o, group_id=None):
        user   = o.get("user_id")
        amount = o.get("amount", 0)
        print(f"  🍩 Продление Donut от {user}: {amount}₽")
        db.insert("donut_subscription", {
            "event_type": "prolonged", "user_id": user,
            "amount": amount, "amount_without_fee": o.get("amount_without_fee"),
            "group_id": group_id,
        })

    def on_donut_subscription_expired(self, o, group_id=None):
        user = o.get("user_id")
        print(f"  🍩 Подписка Donut истекла: {user}")
        db.insert("donut_subscription", {"event_type": "expired", "user_id": user, "group_id": group_id})

    def on_donut_subscription_cancelled(self, o, group_id=None):
        user = o.get("user_id")
        print(f"  🍩 Подписка Donut отменена: {user}")
        db.insert("donut_subscription", {"event_type": "cancelled", "user_id": user, "group_id": group_id})

    def on_donut_subscription_price_changed(self, o, group_id=None):
        user       = o.get("user_id")
        amount_old = o.get("amount_old", 0)
        amount_new = o.get("amount_new", 0)
        print(f"  🍩 Цена Donut для {user}: {amount_old}₽ → {amount_new}₽")
        db.insert("donut_subscription", {
            "event_type": "price_changed", "user_id": user,
            "amount_old": amount_old, "amount_new": amount_new,
            "amount_without_fee": o.get("amount_diff_without_fee"),
            "group_id": group_id,
        })

    def on_donut_money_withdraw(self, o, group_id=None):
        amount = o.get("amount", 0)
        print(f"  🍩💰 Вывод средств Donut: {amount}₽")
        db.insert("donut_money_withdraw", {
            "event_type": "withdraw",
            "amount": amount, "amount_without_fee": o.get("amount_without_fee"),
            "group_id": group_id,
        })

    def on_donut_money_withdraw_error(self, o, group_id=None):
        reason = o.get("reason", "")
        print(f"  🍩❌ Ошибка вывода Donut: {reason}")
        db.insert("donut_money_withdraw", {"event_type": "withdraw_error", "reason": reason, "group_id": group_id})
