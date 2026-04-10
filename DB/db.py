import sqlite3, _G



def get_conn():
    conn = sqlite3.connect(_G.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def insert(table: str, data: dict):
    conn = get_conn()
    cols = ", ".join(data.keys())
    vals = ", ".join(["?"] * len(data))
    try:
        conn.execute(f"INSERT OR IGNORE INTO {table} ({cols}) VALUES ({vals})", list(data.values()))
        conn.commit()
    except Exception as e:
        print(f"  [DB ERROR] {table}: {e}")
    finally:
        conn.close()
