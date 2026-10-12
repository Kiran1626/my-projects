import pytest
from django.contrib.auth.models import User

from tracker.models import Application

pytestmark = pytest.mark.django_db

VALID_APP = {
    "company": "Acme Corp",
    "role": "Backend Engineer",
    "status": "applied",
    "applied_at": "2026-10-01",
}


def _auth(api_client, username="alice"):
    user = User.objects.create_user(username=username, password="pass12345!")
    api_client.force_authenticate(user=user)
    return user


def test_requires_authentication(api_client):
    response = api_client.get("/api/applications/")
    assert response.status_code == 401


def test_create_and_list_isolated_per_user(api_client):
    user = _auth(api_client)
    other = User.objects.create_user("bob", password="pass12345!")
    Application.objects.create(
        user=other,
        company="Rival",
        role="Dev",
        status="applied",
        applied_at="2026-09-01",
    )

    response = api_client.post("/api/applications/", VALID_APP)
    assert response.status_code == 201, response.data
    assert Application.objects.filter(user=user, company="Acme Corp").exists()

    listed = api_client.get("/api/applications/")
    payload = listed.data
    if isinstance(payload, dict):
        items = payload["results"]
    else:
        items = payload
    companies = [app["company"] for app in items]
    assert companies == ["Acme Corp"]  # bob's entry is not visible
    assert user.applications.count() == 1


def test_status_requires_applied_at(api_client):
    _auth(api_client)
    bad = {**VALID_APP, "applied_at": None}
    response = api_client.post("/api/applications/", bad)
    assert response.status_code == 400
    assert "applied_at" in str(response.data)

    wishlist = {**VALID_APP, "status": "wishlist", "applied_at": None}
    assert api_client.post("/api/applications/", wishlist).status_code == 201


def test_stats_counts_statuses(api_client):
    user = _auth(api_client)
    Application.objects.create(
        user=user, company="A", role="r1", status="applied", applied_at="2026-09-01"
    )
    Application.objects.create(user=user, company="B", role="r2", status="interview")
    Application.objects.create(user=user, company="C", role="r3", status="interview")

    data = api_client.get("/api/applications/stats/").data
    assert data["total"] == 3
    assert data["by_status"] == {"applied": 1, "interview": 2}
    assert data["interview_rate"] == pytest.approx(66.67, abs=0.01)


def test_cannot_edit_others_application(api_client):
    _auth(api_client)
    other = User.objects.create_user("bob", password="pass12345!")
    app = Application.objects.create(
        user=other, company="X", role="Dev", status="wishlist"
    )

    response = api_client.patch(f"/api/applications/{app.id}/", {"status": "offer"})
    assert response.status_code == 404
