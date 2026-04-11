"""
Poller.py — VK user wall poller.

Usage:
    python poller_service/Poller.py

Public API:
    import Poller
    Poller.add_user(user_id)
    Poller.remove_user(user_id)
    asyncio.run(Poller.run())
"""

import asyncio
import sys
import os

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import httpx
import DB as DB
import VkUserApiLogin as VkUserApiLogin
import Saver

# ── Config ────────────────────────────────────────────────────────────────────

POLL_INTERVAL = 10          # seconds between cycles
WINDOW        = 15 * 86400  # look back 15 days
REQUEST_PAUSE = 3           # delay between VK requests (sec)

VK_API = "https://api.vk.com/method"
VK_V   = "5.199"


# ── Public API ─────────────────────────────────────────────────────────────────

def add_user(user_id: int):
    DB.execute(
        "INSERT OR IGNORE INTO tracked_users (user_id) VALUES (?)",
        [user_id],
    )
    print(f"[Poller] tracking user_id={user_id}")


def remove_user(user_id: int):
    DB.execute("DELETE FROM tracked_users WHERE user_id = ?", [user_id])
    print(f"[Poller] removed user_id={user_id}")


# ── Polling ────────────────────────────────────────────────────────────────────

async def _fetch_wall(client: httpx.AsyncClient, user_id: int, token: str) -> list[dict] | None:
    """Calls wall.get. On auth failure refreshes the token and retries once."""
    for attempt in range(2):
        r = await client.get(f"{VK_API}/wall.get", params={
            "owner_id":     user_id,
            "count":        100,
            "filter":       "owner",
            "access_token": token,
            "v":            VK_V,
        })
        r.raise_for_status()
        data = r.json()

        if "error" in data:
            code = data["error"]["error_code"]
            if code == 5 and attempt == 0:
                print("[Poller] access token expired, refreshing...")
                token = await VkUserApiLogin.refresh_token()
                continue
            # 15 = private wall, 18 = deleted user, 30 = private profile
            if code in (15, 18, 30):
                return None
            print(f"[Poller] VK error {code} for user_id={user_id}: {data['error']['error_msg']}")
            return None

        return data["response"]["items"]

    return None


async def _poll_user(client: httpx.AsyncClient, user_id: int, token: str):
    posts = await _fetch_wall(client, user_id, token)
    if posts is None:
        return

    count = Saver.save_posts(posts, user_id)
    print(f"[Poller] user_id={user_id}: {count} posts saved")


async def _poll_cycle():
    rows = DB.fetchall("SELECT user_id FROM tracked_users")
    if not rows:
        print("[Poller] no tracked users")
        return

    token = VkUserApiLogin.get_token()
    print(f"[Poller] cycle start: {len(rows)} users")

    async with httpx.AsyncClient(timeout=10) as client:
        for row in rows:
            try:
                await _poll_user(client, row["user_id"], token)
            except Exception as e:
                print(f"[Poller] error for user_id={row['user_id']}: {e}")
            await asyncio.sleep(REQUEST_PAUSE)


async def run():
    print(f"[Poller] started, interval: {round(POLL_INTERVAL / 60, 3)} min")
    while True:
        try:
            await _poll_cycle()
        except Exception as e:
            print(f"[Poller] cycle error: {e}")
        await asyncio.sleep(POLL_INTERVAL)


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    asyncio.run(run())
