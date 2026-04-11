"""
test_vk_callback.py
Тест 1: Мок VK-сервера.

Симулируем VK — шлём все типы событий на /api/vk_callback
и проверяем что сервер их принимает и возвращает "ok".
"""

import time
import pytest
from conftest import GROUP_ID, SECRET, CONFIRM, USER_ID


# ── Хелпер ───────────────────────────────────────────────────────────────────

def vk(client, event_type: str, obj: dict, secret=SECRET, group_id=GROUP_ID):
    payload = {
        "type":     event_type,
        "object":   obj,
        "group_id": group_id,
        "secret":   secret,
        "v":        "5.199",
    }
    return client.post("/api/vk_callback", json=payload)


# ── Подключение / базовые проверки ────────────────────────────────────────────

class TestVkConnection:

    def test_confirmation(self, client):
        """VK сначала шлёт confirmation — должны вернуть непустой confirm_code."""
        r = client.post("/api/vk_callback", json={
            "type":     "confirmation",
            "group_id": GROUP_ID,
            "secret":   SECRET,
        })
        assert r.status_code == 200
        assert len(r.text) > 0  # код непустой (может быть изменён другим тестом)

    def test_wrong_secret_rejected(self, client):
        """Неверный secret — 403."""
        r = vk(client, "wall_post_new",
                {"id": 1, "from_id": USER_ID, "text": "hi", "date": int(time.time())},
                secret="WRONG_SECRET")
        assert r.status_code == 403

    def test_unknown_event_returns_ok(self, client):
        """Неизвестный тип события — сервер не падает, возвращает ok."""
        r = vk(client, "some_future_event_type", {"foo": "bar"})
        assert r.status_code == 200
        assert r.text == "ok"


# ── Wall (стена) ──────────────────────────────────────────────────────────────

class TestWallEvents:

    def test_wall_post_new(self, client):
        obj = {
            "id": 101, "from_id": -GROUP_ID, "text": "Новый пост",
            "date": int(time.time()),
            "likes":    {"count": 0},
            "comments": {"count": 0},
        }
        r = vk(client, "wall_post_new", obj)
        assert r.status_code == 200
        assert r.text == "ok"

    def test_wall_repost(self, client):
        obj = {
            "id": 102, "from_id": USER_ID, "text": "Репост",
            "date": int(time.time()),
            "likes":    {"count": 1},
            "comments": {"count": 0},
        }
        r = vk(client, "wall_repost", obj)
        assert r.status_code == 200
        assert r.text == "ok"

    def test_wall_reply_new(self, client):
        obj = {
            "id": 201, "from_id": USER_ID,
            "post_id": 101, "text": "Комментарий",
            "date": int(time.time()),
        }
        r = vk(client, "wall_reply_new", obj)
        assert r.status_code == 200
        assert r.text == "ok"

    def test_wall_reply_edit(self, client):
        obj = {
            "id": 201, "from_id": USER_ID,
            "post_id": 101, "text": "Отредактированный комментарий",
            "date": int(time.time()),
        }
        r = vk(client, "wall_reply_edit", obj)
        assert r.status_code == 200
        assert r.text == "ok"

    def test_wall_reply_restore(self, client):
        obj = {"id": 201, "from_id": USER_ID, "post_id": 101,
               "text": "Восстановленный", "date": int(time.time())}
        r = vk(client, "wall_reply_restore", obj)
        assert r.status_code == 200
        assert r.text == "ok"

    def test_wall_reply_delete(self, client):
        obj = {"id": 201, "post_id": 101, "deleter_id": USER_ID}
        r = vk(client, "wall_reply_delete", obj)
        assert r.status_code == 200
        assert r.text == "ok"

    def test_wall_schedule_post_new(self, client):
        obj = {"id": 301, "schedule_time": int(time.time()) + 3600}
        r = vk(client, "wall_schedule_post_new", obj)
        assert r.status_code == 200
        assert r.text == "ok"

    def test_wall_schedule_post_delete(self, client):
        obj = {"id": 301, "schedule_time": int(time.time()) + 3600}
        r = vk(client, "wall_schedule_post_delete", obj)
        assert r.status_code == 200
        assert r.text == "ok"


# ── Лайки ────────────────────────────────────────────────────────────────────

class TestLikeEvents:

    def test_like_add(self, client):
        obj = {
            "liker_id":        USER_ID,
            "object_type":     "post",
            "object_owner_id": -GROUP_ID,
            "object_id":       101,
            "post_id":         101,
            "thread_reply_id": 0,
        }
        r = vk(client, "like_add", obj)
        assert r.status_code == 200
        assert r.text == "ok"

    def test_like_remove(self, client):
        obj = {
            "liker_id":        USER_ID,
            "object_type":     "post",
            "object_owner_id": -GROUP_ID,
            "object_id":       101,
            "post_id":         101,
            "thread_reply_id": 0,
        }
        r = vk(client, "like_remove", obj)
        assert r.status_code == 200
        assert r.text == "ok"


# ── Участники ─────────────────────────────────────────────────────────────────

class TestMemberEvents:

    def test_group_join(self, client):
        r = vk(client, "group_join", {"user_id": USER_ID, "join_type": "approved"})
        assert r.status_code == 200
        assert r.text == "ok"

    def test_group_leave(self, client):
        r = vk(client, "group_leave", {"user_id": USER_ID, "self": 1})
        assert r.status_code == 200
        assert r.text == "ok"

    def test_user_block(self, client):
        obj = {
            "admin_id":    1, "user_id": USER_ID,
            "reason":      1, "comment": "спам",
            "unblock_date": 0,
        }
        r = vk(client, "user_block", obj)
        assert r.status_code == 200
        assert r.text == "ok"

    def test_user_unblock(self, client):
        obj = {"admin_id": 1, "user_id": USER_ID, "by_end_date": 0}
        r = vk(client, "user_unblock", obj)
        assert r.status_code == 200
        assert r.text == "ok"


# ── Сообщения ─────────────────────────────────────────────────────────────────

class TestMessageEvents:

    def test_message_new(self, client):
        obj = {
            "message": {
                "id": 1001, "from_id": USER_ID, "peer_id": USER_ID,
                "text": "Привет", "date": int(time.time()),
                "conversation_message_id": 1, "attachments": [],
            }
        }
        r = vk(client, "message_new", obj)
        assert r.status_code == 200
        assert r.text == "ok"

    def test_message_reply(self, client):
        obj = {
            "id": 1002, "from_id": -GROUP_ID, "peer_id": USER_ID,
            "text": "Ответ", "date": int(time.time()),
            "conversation_message_id": 2,
        }
        r = vk(client, "message_reply", obj)
        assert r.status_code == 200
        assert r.text == "ok"

    def test_message_edit(self, client):
        obj = {
            "id": 1001, "from_id": USER_ID, "peer_id": USER_ID,
            "text": "Привет (ред.)", "date": int(time.time()),
            "conversation_message_id": 1,
        }
        r = vk(client, "message_edit", obj)
        assert r.status_code == 200
        assert r.text == "ok"

    def test_message_allow(self, client):
        r = vk(client, "message_allow", {"user_id": USER_ID, "key": "abc123"})
        assert r.status_code == 200
        assert r.text == "ok"

    def test_message_deny(self, client):
        r = vk(client, "message_deny", {"user_id": USER_ID})
        assert r.status_code == 200
        assert r.text == "ok"

    def test_message_read(self, client):
        obj = {
            "from_id": USER_ID, "peer_id": USER_ID,
            "read_message_id": 1001,
        }
        r = vk(client, "message_read", obj)
        assert r.status_code == 200
        assert r.text == "ok"

    def test_message_event(self, client):
        obj = {
            "user_id":  USER_ID, "peer_id": USER_ID,
            "event_id": "evt_1", "payload": {"action": "buy"},
            "conversation_message_id": 1,
        }
        r = vk(client, "message_event", obj)
        assert r.status_code == 200
        assert r.text == "ok"


# ── Медиа ─────────────────────────────────────────────────────────────────────

class TestMediaEvents:

    def test_photo_new(self, client):
        obj = {"id": 501, "owner_id": -GROUP_ID, "text": "", "date": int(time.time())}
        r = vk(client, "photo_new", obj)
        assert r.status_code == 200
        assert r.text == "ok"

    def test_photo_comment_new(self, client):
        obj = {
            "id": 601, "from_id": USER_ID, "photo_id": 501,
            "photo_owner_id": -GROUP_ID, "text": "Класс!",
            "date": int(time.time()),
        }
        r = vk(client, "photo_comment_new", obj)
        assert r.status_code == 200
        assert r.text == "ok"

    def test_photo_comment_edit(self, client):
        obj = {
            "id": 601, "from_id": USER_ID, "photo_id": 501,
            "photo_owner_id": -GROUP_ID, "text": "Класс! (ред.)",
            "date": int(time.time()),
        }
        r = vk(client, "photo_comment_edit", obj)
        assert r.status_code == 200
        assert r.text == "ok"

    def test_photo_comment_restore(self, client):
        obj = {
            "id": 601, "from_id": USER_ID, "photo_id": 501,
            "photo_owner_id": -GROUP_ID, "text": "",
            "date": int(time.time()),
        }
        r = vk(client, "photo_comment_restore", obj)
        assert r.status_code == 200
        assert r.text == "ok"

    def test_photo_comment_delete(self, client):
        obj = {
            "id": 601, "photo_id": 501,
            "photo_owner_id": -GROUP_ID, "deleter_id": USER_ID, "user_id": USER_ID,
        }
        r = vk(client, "photo_comment_delete", obj)
        assert r.status_code == 200
        assert r.text == "ok"

    def test_video_new(self, client):
        obj = {
            "id": 701, "owner_id": -GROUP_ID,
            "title": "Тест", "duration": 120, "date": int(time.time()),
        }
        r = vk(client, "video_new", obj)
        assert r.status_code == 200
        assert r.text == "ok"

    def test_video_comment_new(self, client):
        obj = {
            "id": 801, "from_id": USER_ID, "video_id": 701,
            "video_owner_id": -GROUP_ID, "text": "Огонь",
            "date": int(time.time()),
        }
        r = vk(client, "video_comment_new", obj)
        assert r.status_code == 200
        assert r.text == "ok"

    def test_video_comment_edit(self, client):
        obj = {
            "id": 801, "from_id": USER_ID, "video_id": 701,
            "video_owner_id": -GROUP_ID, "text": "Огонь (ред.)",
            "date": int(time.time()),
        }
        r = vk(client, "video_comment_edit", obj)
        assert r.status_code == 200
        assert r.text == "ok"

    def test_video_comment_restore(self, client):
        obj = {
            "id": 801, "from_id": USER_ID, "video_id": 701,
            "video_owner_id": -GROUP_ID, "text": "",
            "date": int(time.time()),
        }
        r = vk(client, "video_comment_restore", obj)
        assert r.status_code == 200
        assert r.text == "ok"

    def test_video_comment_delete(self, client):
        obj = {
            "id": 801, "owner_id": -GROUP_ID, "user_id": USER_ID,
            "deleter_id": USER_ID, "video_id": 701,
        }
        r = vk(client, "video_comment_delete", obj)
        assert r.status_code == 200
        assert r.text == "ok"

    def test_audio_new(self, client):
        obj = {
            "id": 901, "owner_id": USER_ID,
            "artist": "Artist", "title": "Song", "date": int(time.time()),
        }
        r = vk(client, "audio_new", obj)
        assert r.status_code == 200
        assert r.text == "ok"


# ── Прочее ────────────────────────────────────────────────────────────────────

class TestMiscEvents:

    def test_poll_vote_new(self, client):
        obj = {
            "owner_id": -GROUP_ID, "poll_id": 111,
            "option_id": 1,        "user_id": USER_ID,
        }
        r = vk(client, "poll_vote_new", obj)
        assert r.status_code == 200
        assert r.text == "ok"

    def test_group_officers_edit(self, client):
        obj = {
            "admin_id": 1,       "user_id":   USER_ID,
            "level_old": 0,      "level_new": 1,
        }
        r = vk(client, "group_officers_edit", obj)
        assert r.status_code == 200
        assert r.text == "ok"

    def test_group_change_settings(self, client):
        obj = {
            "user_id": USER_ID,
            "changes": {"title": {"old_value": "Old", "new_value": "New"}},
        }
        r = vk(client, "group_change_settings", obj)
        assert r.status_code == 200
        assert r.text == "ok"

    def test_group_change_photo(self, client):
        r = vk(client, "group_change_photo", {"user_id": USER_ID})
        assert r.status_code == 200
        assert r.text == "ok"

    def test_vkpay_transaction(self, client):
        obj = {
            "from_id": USER_ID, "amount": 50000,
            "description": "Донат", "date": int(time.time()),
        }
        r = vk(client, "vkpay_transaction", obj)
        assert r.status_code == 200
        assert r.text == "ok"

    def test_donut_subscription_create(self, client):
        obj = {"user_id": USER_ID, "amount": 149, "amount_without_fee": 130}
        r = vk(client, "donut_subscription_create", obj)
        assert r.status_code == 200
        assert r.text == "ok"

    def test_donut_subscription_prolonged(self, client):
        obj = {"user_id": USER_ID, "amount": 149, "amount_without_fee": 130}
        r = vk(client, "donut_subscription_prolonged", obj)
        assert r.status_code == 200
        assert r.text == "ok"

    def test_donut_subscription_expired(self, client):
        r = vk(client, "donut_subscription_expired", {"user_id": USER_ID})
        assert r.status_code == 200
        assert r.text == "ok"

    def test_donut_subscription_cancelled(self, client):
        r = vk(client, "donut_subscription_cancelled", {"user_id": USER_ID})
        assert r.status_code == 200
        assert r.text == "ok"

    def test_donut_subscription_price_changed(self, client):
        obj = {"user_id": USER_ID, "amount_old": 99, "amount_new": 149}
        r = vk(client, "donut_subscription_price_changed", obj)
        assert r.status_code == 200
        assert r.text == "ok"

    def test_donut_money_withdraw(self, client):
        obj = {"amount": 5000, "amount_without_fee": 4500}
        r = vk(client, "donut_money_withdraw", obj)
        assert r.status_code == 200
        assert r.text == "ok"

    def test_donut_money_withdraw_error(self, client):
        r = vk(client, "donut_money_withdraw_error", {"reason": "insufficient funds"})
        assert r.status_code == 200
        assert r.text == "ok"
