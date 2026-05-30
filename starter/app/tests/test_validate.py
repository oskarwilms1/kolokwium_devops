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
