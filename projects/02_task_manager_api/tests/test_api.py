import pytest
from app import create_app


@pytest.fixture()
def client():
    app = create_app("sqlite:///:memory:")
    app.config["TESTING"] = True
    return app.test_client()


def make_user(c, email="a@b.com"):
    return c.post("/users", json={"name": "Asha", "email": email}).get_json()


def test_health(client):
    assert client.get("/health").get_json() == {"status": "ok"}


def test_user_validation_and_duplicate(client):
    assert client.post("/users", json={"name": "", "email": "x"}).status_code == 400
    make_user(client)
    assert client.post("/users", json={"name": "B", "email": "a@b.com"}).status_code == 409


def test_task_crud(client):
    uid = make_user(client)["id"]
    r = client.post("/tasks", json={"title": "Write report", "user_id": uid, "due_date": "2026-12-01"})
    assert r.status_code == 201
    tid = r.get_json()["id"]
    assert client.get(f"/tasks/{tid}").get_json()["title"] == "Write report"
    r = client.put(f"/tasks/{tid}", json={"status": "done"})
    assert r.get_json()["status"] == "done"
    assert client.delete(f"/tasks/{tid}").status_code == 204
    assert client.get(f"/tasks/{tid}").status_code == 404


def test_task_validation(client):
    uid = make_user(client)["id"]
    assert client.post("/tasks", json={"user_id": uid}).status_code == 400
    assert client.post("/tasks", json={"title": "x", "user_id": 999}).status_code == 400
    assert client.post("/tasks", json={"title": "x", "user_id": uid, "status": "bad"}).status_code == 400
    assert client.post("/tasks", json={"title": "x", "user_id": uid, "due_date": "01-12-2026"}).status_code == 400


def test_filter_and_pagination(client):
    uid = make_user(client)["id"]
    for i in range(12):
        client.post("/tasks", json={"title": f"t{i}", "user_id": uid, "status": "done" if i % 2 else "todo"})
    page = client.get("/tasks?size=5&page=2").get_json()
    assert page["total"] == 12 and len(page["items"]) == 5
    assert client.get("/tasks?status=done").get_json()["total"] == 6
