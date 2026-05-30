
# ===== app/db.py =====

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

# ===== app/main.py =====

from flask import Flask, jsonify, request

from app import db as dbmod
from app import validate as v

app = Flask(__name__)
dbmod.init_schema()


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/tasks")
def get_tasks():
    return jsonify(dbmod.list_tasks())


@app.post("/tasks")
def create_task():
    data = request.get_json(silent=True)
    cleaned, err = v.validate_task(data)
    if err:
        return jsonify({"error": err}), 400
    task_id = dbmod.insert_task(cleaned["title"], cleaned["priority"])
    return jsonify({"id": task_id, **cleaned}), 201

# ===== app/__init__.py =====


# ===== app/tests/test_validate.py =====

from app.validate import validate_task


def test_accepts_minimal():
    cleaned, err = validate_task({"title": "wash dishes"})
    assert err is None
    assert cleaned == {"title": "wash dishes", "priority": "normal"}


def test_trims_title():
    cleaned, err = validate_task({"title": "  buy milk  "})
    assert err is None
    assert cleaned["title"] == "buy milk"


def test_rejects_empty_title():
    _, err = validate_task({"title": "   "})
    assert err is not None


def test_rejects_non_dict():
    _, err = validate_task("not a dict")
    assert err is not None


def test_rejects_long_title():
    _, err = validate_task({"title": "x" * 101})
    assert err is not None


def test_rejects_invalid_priority():
    _, err = validate_task({"title": "x", "priority": "urgent"})
    assert err is not None


def test_accepts_high_priority():
    cleaned, err = validate_task({"title": "x", "priority": "high"})
    assert err is None
    assert cleaned["priority"] == "high"

# ===== app/tests/__init__.py =====


# ===== app/validate.py =====

def validate_task(data):
    if not isinstance(data, dict):
        return None, "expected JSON object"
    title = data.get("title")
    priority = data.get("priority", "normal")
    if not isinstance(title, str) or not title.strip():
        return None, "title must be non-empty string"
    title = title.strip()
    if len(title) > 100:
        return None, "title too long (max 100)"
    if priority not in ("low", "normal", "high"):
        return None, "priority must be low|normal|high"
    return {"title": title, "priority": priority}, None
