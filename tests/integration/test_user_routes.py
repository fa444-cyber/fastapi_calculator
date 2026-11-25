import jwt
import pytest
from fastapi.testclient import TestClient

from app.database import SessionLocal, engine
from app.models import Base, User
from app.security import SECRET_KEY, ALGORITHM
from main import app


@pytest.fixture
def client():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with TestClient(app) as c:
        yield c


def register(client, username="alice", email="alice@example.com", password="secret123"):
    return client.post(
        "/register",
        json={"username": username, "email": email, "password": password},
    )


def test_register_returns_token_and_safe_user_fields(client):
    response = register(client)
    assert response.status_code == 201
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["user"]["username"] == "alice"
    assert body["user"]["email"] == "alice@example.com"
    assert "password" not in body["user"]
    assert "password_hash" not in body["user"]


def test_register_token_identifies_the_new_user(client):
    body = register(client).json()
    payload = jwt.decode(body["access_token"], SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["username"] == "alice"
    assert payload["sub"] == str(body["user"]["id"])


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
    response = client.post("/login", json={"email": "alice@example.com", "password": "secret123"})
    assert response.status_code == 200
    body = response.json()
    assert body["user"]["username"] == "alice"
    assert "password_hash" not in body["user"]
    payload = jwt.decode(body["access_token"], SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["username"] == "alice"


def test_login_fails_with_wrong_password(client):
    register(client)
    response = client.post("/login", json={"email": "alice@example.com", "password": "wrong-pass"})
    assert response.status_code == 401
    assert response.json()["error"] == "Invalid email or password"


def test_login_fails_for_unknown_email(client):
    response = client.post("/login", json={"email": "nobody@example.com", "password": "secret123"})
    assert response.status_code == 401
