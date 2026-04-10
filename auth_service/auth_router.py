from pathlib import Path

import bcrypt
from fastapi import APIRouter, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse

from . import users_db
from .auth_core import create_session, remove_session

router = APIRouter()


@router.get("/login")
async def login_page():
    html = (Path(__file__).parent / "login.html").read_text(encoding="utf-8")
    return HTMLResponse(html)


@router.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    user = users_db.get_user_by_username(username)
    ok   = user and bcrypt.checkpw(password.encode(), user["password_hash"].encode())
    if not ok:
        html = (Path(__file__).parent / "login.html").read_text(encoding="utf-8")
        html = html.replace("<!--ERROR-->", '<div class="error">Неверный логин или пароль</div>')
        return HTMLResponse(html, status_code=401)

    token    = create_session(user["id"], user["username"])
    response = RedirectResponse(url="/stats", status_code=302)
    response.set_cookie("session", token, httponly=True, samesite="lax")
    return response


@router.get("/logout")
async def logout(session: str | None = Cookie(default=None)):
    if session:
        remove_session(session)
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("session")
    return response