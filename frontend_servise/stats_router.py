from fastapi import APIRouter
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path

from .stats_cache import StatsCache
import _G
router = APIRouter()


_cache  = StatsCache(_G.DB_PATH)


@router.get("/data")
async def stats_data():
    html = (Path(__file__).parent / "stats.html").read_text(encoding="utf-8")
    return HTMLResponse(html)


@router.get("/is_data_invalid")
async def is_data_invalid():
    return JSONResponse(_cache.is_data_invalid())


@router.get("/json")
async def stats_json():
    return JSONResponse(_cache.get())
