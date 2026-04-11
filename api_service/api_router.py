import api_service.VkApi as VkApi

from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse

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
 

