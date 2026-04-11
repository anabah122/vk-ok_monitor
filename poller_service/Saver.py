import time
import DB as DB
import json

WINDOW = 15 * 86400  # 15 дней


def save_posts(posts: list[dict], user_id: int):
    """Парсит сырые посты из wall.get и сохраняет в БД."""
    cutoff     = int(time.time()) - WINDOW
    fetched_at = int(time.time())
    count      = 0

    for post in posts:
        if post.get("date", 0) < cutoff:
            continue
        print(json.dumps(post,indent=3))
        DB.upsert_post({
            "id":         post["id"],
            "owner_id":   user_id,
            "date":       post["date"],
            "likes":      post.get("likes",    {}).get("count", 0),
            "comments":   post.get("comments", {}).get("count", 0),
            "reposts":    post.get("reposts",  {}).get("count", 0),
            "views":      post.get("views",    {}).get("count", 0),
            "fetched_at": fetched_at,
        })
        count += 1

    return count
