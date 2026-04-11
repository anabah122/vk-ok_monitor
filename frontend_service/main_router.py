from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
from auth_service.auth_core import require_auth, AuthUser

router = APIRouter()


@router.get("/")
async def shell(user: AuthUser = Depends(require_auth)):
    html = (Path(__file__).parent / "shell.html").read_text(encoding="utf-8")
    return HTMLResponse(html)


@router.get("/front/api/groups")
async def user_groups(user: AuthUser = Depends(require_auth)):
    return JSONResponse({"group_ids": user.group_ids})


@router.get("/group-menu")
async def group_menu(user: AuthUser = Depends(require_auth)):
    html = (Path(__file__).parent / "group_menu.html").read_text(encoding="utf-8")
    return HTMLResponse(html)
