import sqlite3, _G


def get_conn():
    conn = sqlite3.connect(_G.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
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


def upsert(table: str, data: dict, conflict_col: str):
    conn = get_conn()
    cols     = ", ".join(data.keys())
    vals     = ", ".join(["?"] * len(data))
    updates  = ", ".join(f"{k} = excluded.{k}" for k in data if k != conflict_col)
    try:
        conn.execute(
            f"INSERT INTO {table} ({cols}) VALUES ({vals}) "
            f"ON CONFLICT({conflict_col}) DO UPDATE SET {updates}",
            list(data.values())
        )
        conn.commit()
    except Exception as e:
        print(f"  [DB ERROR] upsert {table}: {e}")
    finally:
        conn.close()


def fetchall(query: str, params: list = []):
    conn = get_conn()
    try:
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()