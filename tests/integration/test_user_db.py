import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app.models import Base, User
from app.schemas import UserCreate
from app.security import hash_password, verify_password


@pytest.fixture
def db():
    """Give each test a fresh users table and a session that is rolled back afterward."""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    session: Session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


def make_user(username="alice", email="alice@example.com", password="secret123"):
    data = UserCreate(username=username, email=email, password=password)
    return User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
    )


def test_user_is_saved_with_hashed_password(db):
    db.add(make_user())
    db.commit()

    saved = db.query(User).filter_by(username="alice").one()
    assert saved.password_hash != "secret123"
    assert verify_password("secret123", saved.password_hash)
    assert saved.created_at is not None


def test_duplicate_username_is_rejected(db):
    db.add(make_user(username="alice", email="alice@example.com"))
    db.commit()

    db.add(make_user(username="alice", email="other@example.com"))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_duplicate_email_is_rejected(db):
    db.add(make_user(username="alice", email="alice@example.com"))
    db.commit()

    db.add(make_user(username="bob", email="alice@example.com"))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_invalid_email_is_rejected_before_saving():
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        UserCreate(username="alice", email="not-an-email", password="secret123")