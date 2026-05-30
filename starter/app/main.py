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
