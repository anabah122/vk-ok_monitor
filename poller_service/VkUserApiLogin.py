"""
VkUserApiLogin.py — синглтон для управления токеном одного VK-пользователя.

Первый запуск (один раз руками):
    python VkUserApiLogin.py

Браузер откроется, после входа VK редиректнет на blank.html с кодом в адресной строке.
Скопируй полный URL и вставь в консоль.

Использование из других скриптов:
    import VkUserApiLogin

    token = VkUserApiLogin.get_token()
    await VkUserApiLogin.refresh_token()
"""

import asyncio
import hashlib
import base64
import json
import os
import secrets
import time
import webbrowser
from urllib.parse import urlparse, parse_qs

import httpx
from dotenv import load_dotenv

load_dotenv()

# ── Конфиг ────────────────────────────────────────────────────────────────────

_CLIENT_ID    = os.environ["VK_CLIENT_ID"]
_REDIRECT_URI = "https://oauth.vk.com/blank.html"
_TOKENS_FILE  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vk_tokens.json")
_SCOPE        = "email"

_AUTH_URL  = "https://id.vk.ru/authorize"
_TOKEN_URL = "https://id.vk.ru/oauth2/auth"


# ── Хранилище токенов ─────────────────────────────────────────────────────────

def _load() -> dict:
    if os.path.exists(_TOKENS_FILE):
        with open(_TOKENS_FILE, "r") as f:
            return json.load(f)
    return {}


def _save(data: dict):
    with open(_TOKENS_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ── PKCE ──────────────────────────────────────────────────────────────────────

def _make_pkce() -> tuple[str, str]:
    verifier  = secrets.token_urlsafe(48)
    digest    = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return verifier, challenge


# ── Первичная авторизация ─────────────────────────────────────────────────────

def _do_initial_login():
    state               = secrets.token_urlsafe(32)
    verifier, challenge = _make_pkce()

    params = "&".join([
        "response_type=code",
        f"client_id={_CLIENT_ID}",
        f"redirect_uri={_REDIRECT_URI}",
        f"state={state}",
        f"code_challenge={challenge}",
        "code_challenge_method=S256",
        f"scope={_SCOPE}",
    ])
    url = f"{_AUTH_URL}?{params}"

    print("\n[VkUserApiLogin] Открываю браузер...")
    print("[VkUserApiLogin] После входа скопируй полный URL из адресной строки и вставь сюда.\n")
    webbrowser.open(url)

    callback_url = input("URL: ").strip()

    qs = parse_qs(urlparse(callback_url).query)

    returned_state = qs.get("state", [None])[0]
    code           = qs.get("code",  [None])[0]
    device_id      = qs.get("device_id", [None])[0]

    assert returned_state == state, "state не совпадает"
    assert code,                    "code не найден в URL"
    assert device_id,               "device_id не найден в URL"

    tokens = asyncio.run(_exchange(code, verifier, device_id))
    _save(tokens)
    print(f"\n[VkUserApiLogin] Токены сохранены → {_TOKENS_FILE}")
    return tokens


# ── Обмен code на токены ──────────────────────────────────────────────────────

async def _exchange(code: str, verifier: str, device_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.post(_TOKEN_URL, data={
            "grant_type":    "authorization_code",
            "code":          code,
            "code_verifier": verifier,
            "client_id":     _CLIENT_ID,
            "device_id":     device_id,
            "redirect_uri":  _REDIRECT_URI,
            "state":         secrets.token_urlsafe(16),
        })
        r.raise_for_status()

    data = r.json()
    data["device_id"] = device_id
    data["saved_at"]  = int(time.time())
    return data


# ── Публичное API ─────────────────────────────────────────────────────────────

def get_token() -> str:
    """Возвращает текущий access_token."""
    tokens = _load()
    if not tokens:
        raise RuntimeError("Токены не найдены. Запустите: python VkUserApiLogin.py")
    return tokens["access_token"]


async def refresh_token() -> str:
    """Обновляет access_token и возвращает новый."""
    tokens = _load()
    if not tokens:
        raise RuntimeError("Токены не найдены. Запустите: python VkUserApiLogin.py")

    async with httpx.AsyncClient() as client:
        r = await client.post(_TOKEN_URL, data={
            "grant_type":    "refresh_token",
            "refresh_token": tokens["refresh_token"],
            "client_id":     _CLIENT_ID,
            "device_id":     tokens["device_id"],
            "state":         secrets.token_urlsafe(16),
        })
        r.raise_for_status()

    new_tokens = r.json()
    new_tokens["device_id"] = tokens["device_id"]
    new_tokens["saved_at"]  = int(time.time())
    _save(new_tokens)
    print("[VkUserApiLogin] Токен обновлён")
    return new_tokens["access_token"]


# ── init auth ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if os.path.exists(_TOKENS_FILE):
        ans = input(f"Файл {_TOKENS_FILE} уже существует. Перелогиниться? [y/N] ")
        if ans.strip().lower() != "y":
            print("Отмена.")
            exit(0)
    _do_initial_login()