from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pathlib import Path

from fastapi import Depends
from auth_service.auth_core import require_auth, AuthUser

import _G

# dependencies=[Depends(require_auth)]

from .stats_cache import StatsCache
cache_instance = StatsCache(_G.DB_PATH)

router = APIRouter()



# --- base

@router.get("/bad_request")
async def stats_bad_request():
    html = (Path(__file__).parent / "bad_request.html").read_text(encoding="utf-8")
    return HTMLResponse(html)

@router.get("/")
async def stats_shell(user: AuthUser = Depends(require_auth), group_id: int = Query(None)):
    if not user.group_ids:
        status = "no_groups"
    elif group_id is None:
        status = "no_group_selected"
    elif group_id not in user.group_ids:
        status = "access_denied"
    else:
        status = "ok"

    if status != "ok":
        return RedirectResponse(url=f"/stats/bad_request#{status}", status_code=302)

    html = (Path(__file__).parent / "stats.html").read_text(encoding="utf-8")
    return HTMLResponse(html)



# --- routes 

@router.get("/log")
async def stats_log():
    html = (Path(__file__).parent / "log.html").read_text(encoding="utf-8")
    return HTMLResponse(html)

# on data page 
@router.get("/data")
async def stats_data():
    html = (Path(__file__).parent / "stats.html").read_text(encoding="utf-8")
    return HTMLResponse(html)


@router.get("/is_data_invalid")
async def is_data_invalid():
    return JSONResponse(cache_instance.is_data_invalid())


@router.get("/json")
async def stats_json(user: AuthUser = Depends(require_auth)):
    return JSONResponse(cache_instance.get(user=user))