import pytest
from fastapi.testclient import TestClient

from app.database import SessionLocal, engine
from app.models import Base, User
from main import app


@pytest.fixture
def client():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with TestClient(app) as c:
        yield c


def register(client, username="alice", email="alice@example.com", password="secret123"):
    return client.post(
        "/users/register",
        json={"username": username, "email": email, "password": password},
    )


def test_register_creates_user_and_returns_safe_fields(client):
    response = register(client)
    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "alice"
    assert body["email"] == "alice@example.com"
    assert "password" not in body
    assert "password_hash" not in body


def test_register_stores_hashed_password_in_database(client):
    register(client)
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(username="alice").one()
        assert user.password_hash != "secret123"
        assert user.password_hash.startswith("$2b$")
    finally:
        db.close()


def test_register_rejects_duplicate_username(client):
    register(client)
    response = register(client, email="other@example.com")
    assert response.status_code == 400
    assert "already registered" in response.json()["error"]


def test_register_rejects_duplicate_email(client):
    register(client)
    response = register(client, username="bob")
    assert response.status_code == 400


def test_register_rejects_invalid_email(client):
    response = register(client, email="not-an-email")
    assert response.status_code == 400


def test_register_rejects_short_password(client):
    response = register(client, password="short")
    assert response.status_code == 400


def test_login_succeeds_with_correct_password(client):
    register(client)
    response = client.post("/users/login", json={"username": "alice", "password": "secret123"})
    assert response.status_code == 200
    assert response.json()["username"] == "alice"
    assert "password_hash" not in response.json()


def test_login_fails_with_wrong_password(client):
    register(client)
    response = client.post("/users/login", json={"username": "alice", "password": "wrong-pass"})
    assert response.status_code == 401
    assert response.json()["error"] == "Invalid username or password"


def test_login_fails_for_unknown_user(client):
    response = client.post("/users/login", json={"username": "nobody", "password": "secret123"})
    assert response.status_code == 401