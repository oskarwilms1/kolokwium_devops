import os
import sqlite3
import threading

DB_PATH = os.environ.get("DB_PATH", "/data/app.db")
_lock = threading.Lock()


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_schema():
    parent = os.path.dirname(DB_PATH) or "."
    os.makedirs(parent, exist_ok=True)
    with get_conn() as c:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                priority TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def insert_task(title, priority):
    with _lock, get_conn() as c:
        cur = c.execute(
            "INSERT INTO tasks(title, priority) VALUES (?, ?)", (title, priority)
        )
        return cur.lastrowid


def list_tasks():
    with get_conn() as c:
        rows = c.execute(
            "SELECT id, title, priority, created_at FROM tasks ORDER BY id"
        ).fetchall()
        return [dict(r) for r in rows]
