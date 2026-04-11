"""
test_routes.py
Тест 2: Все HTTP-роуты.

Проверяем каждый роут: статус-коды, Content-Type,
структуру JSON-ответов, редиректы и защиту авторизацией.
"""

import pytest
from conftest import GROUP_ID, SESSION


# ── Хелпер ───────────────────────────────────────────────────────────────────

def assert_json_keys(data: dict, *keys):
    for k in keys:
        assert k in data, f"Ключ '{k}' отсутствует в ответе: {data}"


# ═════════════════════════════════════════════════════════════════════════════
# Auth роуты
# ═════════════════════════════════════════════════════════════════════════════

class TestAuthRoutes:

    def test_login_page_get(self, client):
        """GET /login возвращает HTML форму."""
        r = client.get("/login")
        assert r.status_code == 200
        assert "text/html" in r.headers["content-type"]
        assert "Вход" in r.text
        assert 'name="username"' in r.text
        assert 'name="password"' in r.text

    def test_login_correct_credentials(self, client):
        """POST /login с верными данными — редирект на /."""
        r = client.post("/login",
                        data={"username": "testuser", "password": "testpass"},
                        follow_redirects=False)
        assert r.status_code == 302
        assert r.headers["location"] == "/"

    def test_login_wrong_password(self, client):
        """POST /login с неверным паролем — 401 и сообщение об ошибке."""
        r = client.post("/login",
                        data={"username": "testuser", "password": "wrongpass"},
                        follow_redirects=False)
        assert r.status_code == 401
        assert "Неверный логин" in r.text

    def test_login_unknown_user(self, client):
        """POST /login с несуществующим юзером — 401."""
        r = client.post("/login",
                        data={"username": "nobody", "password": "x"},
                        follow_redirects=False)
        assert r.status_code == 401

    def test_logout(self, client):
        """GET /logout — редирект на /login."""
        r = client.get("/logout", follow_redirects=False)
        assert r.status_code == 302
        assert "/login" in r.headers["location"]


# ═════════════════════════════════════════════════════════════════════════════
# Защита авторизацией (без куки)
# ═════════════════════════════════════════════════════════════════════════════

class TestAuthProtection:

    PROTECTED = [
        "/",
        "/group-menu",
        "/front/api/groups",
        "/stats/",
        "/stats/json",
    ]

    @pytest.mark.parametrize("url", PROTECTED)
    def test_redirect_without_session(self, client, url):
        """Все защищённые роуты без куки → редирект на /login."""
        # Убеждаемся что куки нет
        client.cookies.clear()
        r = client.get(url, follow_redirects=False)
        assert r.status_code in (302, 307), \
            f"{url} вернул {r.status_code} вместо редиректа"
        assert "/login" in r.headers.get("location", "")


# ═════════════════════════════════════════════════════════════════════════════
# Frontend роуты (с авторизацией)
# ═════════════════════════════════════════════════════════════════════════════

class TestFrontendRoutes:

    @pytest.fixture(autouse=True)
    def set_cookie(self, client):
        client.cookies.set("session", SESSION)
        yield
        client.cookies.clear()

    def test_shell_page(self, client):
        """GET / возвращает HTML панели управления."""
        r = client.get("/")
        assert r.status_code == 200
        assert "text/html" in r.headers["content-type"]
        assert "Панель" in r.text

    def test_group_menu_page(self, client):
        """GET /group-menu возвращает HTML выбора группы."""
        r = client.get("/group-menu")
        assert r.status_code == 200
        assert "text/html" in r.headers["content-type"]
        assert "Группы" in r.text or "group" in r.text.lower()

    def test_front_api_groups(self, client):
        """GET /front/api/groups возвращает список group_ids пользователя."""
        r = client.get("/front/api/groups")
        assert r.status_code == 200
        assert "application/json" in r.headers["content-type"]
        data = r.json()
        assert "group_ids" in data
        assert isinstance(data["group_ids"], list)
        assert GROUP_ID in data["group_ids"]


# ═════════════════════════════════════════════════════════════════════════════
# Stats роуты
# ═════════════════════════════════════════════════════════════════════════════

class TestStatsRoutes:

    @pytest.fixture(autouse=True)
    def set_cookie(self, client):
        client.cookies.set("session", SESSION)
        yield
        client.cookies.clear()

    def test_stats_redirect_no_group(self, client):
        """GET /stats/ без group_id → редирект на bad_request."""
        r = client.get("/stats/", follow_redirects=False)
        assert r.status_code == 302
        assert "bad_request" in r.headers["location"]

    def test_stats_redirect_wrong_group(self, client):
        """GET /stats/?group_id=999 (нет доступа) → редирект на bad_request."""
        r = client.get("/stats/?group_id=999", follow_redirects=False)
        assert r.status_code == 302
        assert "bad_request" in r.headers["location"]

    def test_stats_valid_group(self, client):
        """GET /stats/?group_id=<доступный> → 200 HTML."""
        r = client.get(f"/stats/?group_id={GROUP_ID}")
        assert r.status_code == 200
        assert "text/html" in r.headers["content-type"]

    def test_stats_bad_request_page(self, client):
        """GET /stats/bad_request → 200 HTML."""
        r = client.get("/stats/bad_request")
        assert r.status_code == 200
        assert "text/html" in r.headers["content-type"]

    def test_stats_log_page(self, client):
        """GET /stats/log → 200 HTML."""
        r = client.get("/stats/log")
        assert r.status_code == 200
        assert "text/html" in r.headers["content-type"]

    def test_stats_is_data_invalid(self, client):
        """GET /stats/is_data_invalid → boolean."""
        r = client.get("/stats/is_data_invalid")
        assert r.status_code == 200
        assert r.json() in (True, False)

    def test_stats_json_structure(self, client):
        """GET /stats/json → корректная структура данных."""
        r = client.get("/stats/json")
        assert r.status_code == 200
        assert "application/json" in r.headers["content-type"]

        data = r.json()

        # Топ-уровень
        assert_json_keys(data,
            "date", "total_members", "total_posts", "total_comments",
            "total_likes", "total_messages", "total_photos", "total_videos",
            "month", "week", "day",
        )

        # Числовые поля
        for field in ("total_members", "total_posts", "total_comments",
                      "total_likes", "total_messages", "total_photos", "total_videos"):
            assert isinstance(data[field], int), f"{field} должен быть int"

        # Периоды
        for period_key in ("month", "week", "day"):
            period = data[period_key]
            assert_json_keys(period, "points", "totals")
            assert isinstance(period["points"], list)
            assert isinstance(period["totals"], dict)
            assert_json_keys(period["totals"],
                "posts", "comments", "likes", "messages",
                "joined", "left", "photos", "videos",
            )

        # Точки
        if data["week"]["points"]:
            pt = data["week"]["points"][0]
            assert_json_keys(pt, "label", "posts", "comments", "likes",
                             "messages", "joined", "left", "photos", "videos")
            assert isinstance(pt["label"], str)
            for k in ("posts", "comments", "likes"):
                assert isinstance(pt[k], int)

    def test_stats_json_no_log_rows(self, client):
        """GET /stats/json не должен содержать log_rows (они только внутри кэша)."""
        r = client.get("/stats/json")
        data = r.json()
        assert "log_rows" not in data


# ═════════════════════════════════════════════════════════════════════════════
# API роуты
# ═════════════════════════════════════════════════════════════════════════════

class TestApiRoutes:

    @pytest.fixture(autouse=True)
    def set_cookie(self, client):
        client.cookies.set("session", SESSION)
        yield
        client.cookies.clear()

    def test_vk_callback_only_post(self, client):
        """GET /api/vk_callback не существует → 405."""
        r = client.get("/api/vk_callback")
        assert r.status_code == 405

    def test_get_all_group_data(self, client):
        """GET /api/all_groups_data → список групп (нужен role>=1)."""
        r = client.get("/api/all_groups_data")
        assert r.status_code == 200
        data = r.json()
        assert "groups" in data
        assert isinstance(data["groups"], list)

    def test_get_all_group_data_forbidden_without_auth(self, client):
        """GET /api/all_groups_data без авторизации → 302."""
        client.cookies.clear()
        r = client.get("/api/all_groups_data", follow_redirects=False)
        assert r.status_code in (302, 403)

    def test_update_confirm_code(self, client):
        """GET /api/update_confirm_code → обновляет код подтверждения."""
        r = client.get(f"/api/update_confirm_code?id={GROUP_ID}&code=NEWCODE123")
        assert r.status_code == 200
        data = r.json()
        assert data.get("ok") is True
        assert data.get("group_id") == GROUP_ID

    def test_update_confirm_code_forbidden_without_auth(self, client):
        """GET /api/update_confirm_code без авторизации → 302/403."""
        client.cookies.clear()
        r = client.get(f"/api/update_confirm_code?id={GROUP_ID}&code=X",
                       follow_redirects=False)
        assert r.status_code in (302, 403)


# ═════════════════════════════════════════════════════════════════════════════
# Несуществующие роуты
# ═════════════════════════════════════════════════════════════════════════════

class TestNotFound:

    @pytest.mark.parametrize("url", [
        "/nonexistent",
        "/api/nonexistent",
        "/stats/nonexistent",
    ])
    def test_404(self, client, url):
        """Несуществующие роуты → 404."""
        r = client.get(url)
        assert r.status_code == 404