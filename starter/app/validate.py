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
