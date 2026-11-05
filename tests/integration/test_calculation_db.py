import pytest
from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal, engine
from app.models import Base, Calculation, User
from app.security import hash_password


@pytest.fixture
def db():
    """Fresh tables for each test, with a session that is rolled back afterward."""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def user(db):
    u = User(username="alice", email="alice@example.com", password_hash=hash_password("secret123"))
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def test_calculation_is_stored_with_correct_data(db, user):
    calc = Calculation(a=6.0, b=3.0, type="Divide", result=2.0, user_id=user.id)
    db.add(calc)
    db.commit()

    saved = db.query(Calculation).filter_by(id=calc.id).one()
    assert saved.a == 6.0
    assert saved.b == 3.0
    assert saved.type == "Divide"
    assert saved.result == 2.0
    assert saved.user_id == user.id
    assert saved.timestamp is not None


def test_calculation_links_to_its_user(db, user):
    db.add(Calculation(a=1.0, b=2.0, type="Add", result=3.0, user_id=user.id))
    db.commit()

    db.refresh(user)
    assert len(user.calculations) == 1
    assert user.calculations[0].type == "Add"


def test_calculation_requires_a_valid_user(db):
    db.add(Calculation(a=1.0, b=2.0, type="Add", result=3.0, user_id=99999))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_calculation_requires_result(db, user):
    db.add(Calculation(a=1.0, b=2.0, type="Add", result=None, user_id=user.id))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_deleting_user_removes_their_calculations(db, user):
    db.add(Calculation(a=1.0, b=2.0, type="Add", result=3.0, user_id=user.id))
    db.commit()

    db.delete(user)
    db.commit()

    assert db.query(Calculation).count() == 0