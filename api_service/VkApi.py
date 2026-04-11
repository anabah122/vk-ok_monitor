import httpx, time
import _G
import DB.DB as DB

VK_API = "https://api.vk.com/method"
VK_V   = "5.199"



def load_vk_server_secrets() -> dict[int, str]:
    rows = DB.fetchall("SELECT group_id, secret FROM vk_server_secrets")
    return {r["group_id"]: r["secret"] for r in rows}


async def fetch_group_info(group_id: int) -> dict | None:
    """
    Возвращает { name, photo_url, members_count } для группы.
    Пока не используется — для будущей синхронизации данных группы.
    """
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{VK_API}/groups.getById", params={
            "group_id":     group_id,
            "fields":       "members_count,photo_200",
            "access_token": _G.SECRET_KEY_VK_GROUP,
            "v":            VK_V,
        })
    data = r.json()

    groups = data.get("response", {}).get("groups") or data.get("response")
    if not groups:
        return None

    g = groups[0] if isinstance(groups, list) else groups
    return {
        "name":          g.get("name"),
        "photo_url":     g.get("photo_200"),
        "members_count": g.get("members_count"),
    }

def get_confirm_code(group_id: int) -> str | None:
    rows = DB.fetchall(
        "SELECT confirm_code FROM vk_servers WHERE group_id = ?",
        [group_id]
    )
    return rows[0]["confirm_code"] if rows else None


async def sync_group_data(group_id: int):
    info = await fetch_group_info(group_id)
    DB.upsert("group_data", {
        "group_id":      group_id,
        "name":          info.get("name")          if info else None,
        "photo_url":     info.get("photo_url")     if info else None,
        "members_count": info.get("members_count") if info else None,
        "updated_at":    int(time.time()),
    }, "group_id")