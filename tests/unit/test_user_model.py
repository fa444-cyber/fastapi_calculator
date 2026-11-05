import pytest
from pydantic import ValidationError

from app.schemas import UserCreate, UserRead
from app.security import hash_password, verify_password


# --- Hashing ---

def test_hash_password_does_not_return_plain_text():
    hashed = hash_password("secret123")
    assert hashed != "secret123"


def test_hash_password_produces_different_hashes_for_same_input():
    # bcrypt uses a random salt, so two hashes of the same password differ.
    assert hash_password("secret123") != hash_password("secret123")


def test_verify_password_accepts_correct_password():
    hashed = hash_password("secret123")
    assert verify_password("secret123", hashed) is True


def test_verify_password_rejects_wrong_password():
    hashed = hash_password("secret123")
    assert verify_password("wrong-password", hashed) is False


# --- UserCreate schema ---

def test_user_create_accepts_valid_data():
    user = UserCreate(username="alice", email="alice@example.com", password="secret123")
    assert user.username == "alice"


def test_user_create_rejects_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(username="alice", email="not-an-email", password="secret123")


def test_user_create_rejects_short_password():
    with pytest.raises(ValidationError):
        UserCreate(username="alice", email="alice@example.com", password="short")


def test_user_create_rejects_short_username():
    with pytest.raises(ValidationError):
        UserCreate(username="al", email="alice@example.com", password="secret123")


# --- UserRead schema ---

def test_user_read_has_no_password_fields():
    fields = set(UserRead.model_fields)
    assert "password" not in fields
    assert "password_hash" not in fields