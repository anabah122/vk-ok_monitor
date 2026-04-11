import DB.DB as DB

from fastapi import APIRouter

db_admin_router = APIRouter()


@db_admin_router.get("/all_groups_data")
def get_groups():
    rows = DB.fetchall(
        "SELECT group_id, name, photo_url, members_count FROM group_data ORDER BY group_id"
    )
    return {"groups": rows}


@db_admin_router.get("/vkserver_update_confirm")
def update_confirm_code(id: int, code: str):
    DB.upsert("vk_servers", {"group_id": id, "confirm_code": code}, "group_id")
    return {"ok": True, "group_id": id}


"""
@db_admin_router.get("/vkserver_autoupdate_confirm")
def update_confirm_code(id: int, code: str):
    DB.upsert("vk_servers", {"group_id": id, "confirm_code": code}, "group_id")
    return {"ok": True, "group_id": id}
"""