import DB.DB as DB
import api_service.VkApi as VkApi

from fastapi import APIRouter, Request, Depends
from fastapi.responses import PlainTextResponse
from auth_service.auth_core import require_role, AuthUser

api_router = APIRouter()


# ── VK Callback (/api/vk_callback) ───────────────────────────────────────────

_secrets: dict[int, str] = VkApi.load_vk_server_secrets()

@api_router.post("/vk_callback")
async def vk_callback(request: Request):
    data     = await request.json()
    group_id = data.get("group_id")
 
    secret = _secrets.get(group_id)
    if secret and data.get("secret") != secret:
        return PlainTextResponse("forbidden", status_code=403)
 
    event_type = data.get("type")
 
    if event_type == "confirmation":
        code = VkApi.get_confirm_code(group_id)
        return PlainTextResponse(code or "")
 
    from api_service.callback_action import CallbackAction
    from frontend_service.stats.stats_router import cache_instance
    return PlainTextResponse(CallbackAction(cache=cache_instance).dispatch(data))
 


# ── /api/groups ───────────────────────────────────────────────────────────────

@api_router.get("/all_groups_data")
def get_groups(user: AuthUser = Depends(require_role(1))):
    rows = DB.fetchall(
        "SELECT group_id, name, photo_url, members_count FROM group_data ORDER BY group_id"
    )
    return {"groups": rows}


# ── /api/update_confirm_code ──────────────────────────────────────────────────

@api_router.get("/update_confirm_code")
def update_confirm_code(id: int, code: str, user: AuthUser = Depends(require_role(1))):
    DB.upsert("vk_servers", {"group_id": id, "confirm_code": code}, "group_id")
    return {"ok": True, "group_id": id}
