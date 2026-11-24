import pytest
from fastapi.testclient import TestClient

from app.database import engine
from app.models import Base
from main import app


@pytest.fixture
def client():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with TestClient(app) as c:
        yield c


def create(client, a=6, b=3, calc_type="Divide"):
    return client.post("/calculations", json={"a": a, "b": b, "type": calc_type})


def test_create_returns_201_with_computed_result(client):
    response = create(client, a=6, b=3, calc_type="Divide")
    assert response.status_code == 201
    body = response.json()
    assert body["type"] == "Divide"
    assert body["result"] == 2.0


@pytest.mark.parametrize(
    "calc_type, a, b, expected",
    [("Add", 2, 3, 5), ("Sub", 5, 3, 2), ("Multiply", 4, 5, 20), ("Divide", 10, 2, 5)],
)
def test_create_computes_each_type(client, calc_type, a, b, expected):
    response = create(client, a=a, b=b, calc_type=calc_type)
    assert response.status_code == 201
    assert response.json()["result"] == expected


def test_browse_lists_all_calculations(client):
    create(client, a=1, b=2, calc_type="Add")
    create(client, a=6, b=3, calc_type="Divide")
    response = client.get("/calculations")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_read_returns_one_calculation(client):
    created = create(client, a=2, b=3, calc_type="Add").json()
    response = client.get(f"/calculations/{created['id']}")
    assert response.status_code == 200
    assert response.json()["result"] == 5.0


def test_read_missing_returns_404(client):
    response = client.get("/calculations/99999")
    assert response.status_code == 404
    assert response.json()["error"] == "Calculation not found"


def test_edit_updates_and_recomputes(client):
    created = create(client, a=6, b=3, calc_type="Divide").json()
    response = client.put(
        f"/calculations/{created['id']}",
        json={"a": 4, "b": 5, "type": "Multiply"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "Multiply"
    assert body["result"] == 20.0


def test_edit_missing_returns_404(client):
    response = client.put("/calculations/99999", json={"a": 1, "b": 1, "type": "Add"})
    assert response.status_code == 404


def test_delete_removes_calculation(client):
    created = create(client).json()
    response = client.delete(f"/calculations/{created['id']}")
    assert response.status_code == 204
    assert client.get(f"/calculations/{created['id']}").status_code == 404


def test_delete_missing_returns_404(client):
    response = client.delete("/calculations/99999")
    assert response.status_code == 404


def test_create_rejects_unknown_type(client):
    response = client.post("/calculations", json={"a": 1, "b": 2, "type": "Power"})
    assert response.status_code == 400


def test_create_rejects_zero_divisor(client):
    response = client.post("/calculations", json={"a": 6, "b": 0, "type": "Divide"})
    assert response.status_code == 400