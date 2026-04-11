import secrets
from dataclasses import dataclass, field
from fastapi import Cookie, Request, HTTPException

from . import UsersDB


@dataclass
class AuthUser:
    id:        int
    username:  str
    role:      int = 0
    group_ids: list[int] = field(default_factory=list)


# ── сессии в ОЗУ ──────────────────────────────────────────────────────────────
_sessions: dict[str, AuthUser] = {}


def create_session(user_id: int, username: str) -> str:
    group_ids = UsersDB.get_user_group_ids(user_id)
    role      = UsersDB.get_user_role(user_id)
    user      = AuthUser(id=user_id, username=username, role=role, group_ids=group_ids)
    token     = secrets.token_hex(32)

    _sessions[token] = user
    UsersDB.save_session(token, user_id)
    return token


def remove_session(token: str) -> None:
    _sessions.pop(token, None)
    UsersDB.delete_session(token)


def _load_from_db(token: str) -> AuthUser | None:
    row = UsersDB.get_session(token)
    if not row:
        return None
    user_row = UsersDB.get_user_by_id(row["user_id"])
    if not user_row:
        return None
    group_ids        = UsersDB.get_user_group_ids(user_row["id"])
    role             = UsersDB.get_user_role(user_row["id"])
    user             = AuthUser(id=user_row["id"], username=user_row["username"], role=role, group_ids=group_ids)
    _sessions[token] = user
    return user


def get_user(token: str | None) -> AuthUser | None:
    if not token:
        return None
    user = _sessions.get(token)
    if user:
        return user
    return _load_from_db(token)


# ── dependencies ───────────────────────────────────────────────────────────────
def require_auth(request: Request, session: str | None = Cookie(default=None)):
    user = get_user(session)
    if not user:
        raise HTTPException(status_code=302, headers={"Location": "/login"})
    return user


def require_role(min_role: int):
    def dependency(request: Request, session: str | None = Cookie(default=None)):
        user = get_user(session)
        if not user:
            raise HTTPException(status_code=302, headers={"Location": "/login"})
        if user.role < min_role:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return dependency