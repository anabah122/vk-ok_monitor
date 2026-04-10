import sqlite3
import _G

TABLES = [
    "wall_post", "wall_reply", "wall_reply_delete", "wall_schedule_post",
    "like_event",
    "group_join", "group_leave", "user_block", "user_unblock",
    "message", "message_allow", "message_deny", "message_typing_state", "message_event",
    "photo", "photo_comment", "photo_comment_delete",
    "video", "video_comment", "video_comment_delete",
    "poll_vote", "group_officers_edit", "vkpay_transaction",
]

def clear_all():
    conn = sqlite3.connect(_G.DB_PATH)
    cur  = conn.cursor()
    for table in TABLES:
        cur.execute(f"DELETE FROM {table}")
        print(f"  cleared  {table:<35} rows deleted: {cur.rowcount}")
    conn.commit()
    conn.close()
    print(f"\nготово — {len(TABLES)} таблиц очищено")

if __name__ == "__main__":
    ans = input("очистить ВСЕ таблицы? (yes): ")
    if ans.strip().lower() == "yes":
        clear_all()
    else:
        print("отмена")