import secrets
from dataclasses import dataclass, field
from fastapi import Cookie, Request, HTTPException

from . import users_db


@dataclass
class AuthUser:
    id:        int
    username:  str
    group_ids: list[int] = field(default_factory=list)


# ── сессии в ОЗУ ──────────────────────────────────────────────────────────────
_sessions: dict[str, AuthUser] = {}


def create_session(user_id: int, username: str) -> str:
    group_ids = users_db.get_user_group_ids(user_id)
    user      = AuthUser(id=user_id, username=username, group_ids=group_ids)
    token     = secrets.token_hex(32)

    _sessions[token] = user
    users_db.save_session(token, user_id)
    return token


def remove_session(token: str) -> None:
    _sessions.pop(token, None)
    users_db.delete_session(token)


def _load_from_db(token: str) -> AuthUser | None:
    row = users_db.get_session(token)
    if not row:
        return None
    user_row = users_db.get_user_by_id(row["user_id"])
    if not user_row:
        return None
    group_ids        = users_db.get_user_group_ids(user_row["id"])
    user             = AuthUser(id=user_row["id"], username=user_row["username"], group_ids=group_ids)
    _sessions[token] = user   # кладём обратно в ОЗУ
    return user


def get_user(token: str | None) -> AuthUser | None:
    if not token:
        return None
    user = _sessions.get(token)
    if user:
        return user
    return _load_from_db(token)


# ── dependency ─────────────────────────────────────────────────────────────────
def require_auth(request: Request, session: str | None = Cookie(default=None)):
    user = get_user(session)
    if not user:
        raise HTTPException(status_code=302, headers={"Location": "/login"})
    return user