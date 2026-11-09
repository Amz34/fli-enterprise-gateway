import sqlite3
import json
import time
import os

DB_PATH = os.path.expanduser("~/fli-enterprise-gateway/data/routes_cache.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS route_cache (
                route_key TEXT PRIMARY KEY,
                response_json TEXT,
                updated_at REAL
            )
        """)
        conn.commit()

def get_cached_route(route_key: str, ttl_seconds: int = 7200):
    try:
        init_db()
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT response_json, updated_at FROM route_cache WHERE route_key = ?", (route_key,))
            row = cursor.fetchone()
            if row:
                payload, updated_at = row
                if (time.time() - updated_at) < ttl_seconds:
                    return json.loads(payload)
    except Exception:
        pass
    return None

def set_cached_route(route_key: str, data: dict):
    try:
        init_db()
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO route_cache (route_key, response_json, updated_at) VALUES (?, ?, ?)",
                (route_key, json.dumps(data), time.time())
            )
            conn.commit()
    except Exception:
        pass
