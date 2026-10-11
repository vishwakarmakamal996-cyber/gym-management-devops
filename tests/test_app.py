import pytest

from app import app, members


@pytest.fixture()
def client():
    members.clear()
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client
    members.clear()


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json == {
        "service": "gym-management-api",
        "status": "healthy",
    }


def test_create_and_list_member(client):
    created = client.post(
        "/api/members",
        json={"name": "Asha Patel", "email": "ASHA@example.com"},
    )

    assert created.status_code == 201
    assert created.json["member"]["email"] == "asha@example.com"
    assert created.json["member"]["status"] == "active"

    listed = client.get("/api/members")
    assert listed.status_code == 200
    assert listed.json["members"] == [created.json["member"]]


@pytest.mark.parametrize(
    "payload",
    [
        None,
        {"name": "", "email": "member@example.com"},
        {"name": "Asha Patel", "email": "not-an-email"},
    ],
)
def test_rejects_invalid_member(client, payload):
    response = client.post("/api/members", json=payload)

    assert response.status_code == 400
    assert "error" in response.json


def test_rejects_duplicate_email(client):
    payload = {"name": "Asha Patel", "email": "asha@example.com"}
    client.post("/api/members", json=payload)

    response = client.post(
        "/api/members",
        json={"name": "Asha P.", "email": "ASHA@example.com"},
    )

    assert response.status_code == 409
    assert response.json["error"] == "A member with this email already exists."


def test_returns_404_for_unknown_member(client):
    response = client.get("/api/members/not-a-real-id")

    assert response.status_code == 404
