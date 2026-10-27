# tests/integration/test_api_endpoints.py

import logging

import pytest
from fastapi.testclient import TestClient

import main
from main import app

OPERATION_PATHS = ["/add", "/subtract", "/multiply", "/divide"]


@pytest.fixture
def client():
    """A test client that talks to the FastAPI app without starting a real server."""
    with TestClient(app) as client:
        yield client


# ---------------------------------------------
# The home page
# ---------------------------------------------

def test_the_home_page_is_served(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Hello World" in response.text
    assert 'id="a"' in response.text


# ---------------------------------------------
# Successful operations
# ---------------------------------------------

@pytest.mark.parametrize("path, a, b, expected", [
    ("/add", 10, 5, 15),
    ("/add", -2, -3, -5),
    ("/add", 2.5, 0.25, 2.75),
    ("/subtract", 10, 5, 5),
    ("/subtract", 5, 10, -5),
    ("/subtract", 1.5, 0.5, 1.0),
    ("/multiply", 10, 5, 50),
    ("/multiply", -4, 2.5, -10.0),
    ("/multiply", 7, 0, 0),
    ("/divide", 10, 2, 5),
    ("/divide", 1, 4, 0.25),
    ("/divide", -9, 3, -3),
])
def test_operations_return_the_right_result(client, path, a, b, expected):
    response = client.post(path, json={"a": a, "b": b})
    assert response.status_code == 200
    assert response.json() == {"result": expected}


def test_numbers_sent_as_text_are_accepted(client):
    response = client.post("/add", json={"a": "10", "b": "5"})
    assert response.status_code == 200
    assert response.json() == {"result": 15}


# ---------------------------------------------
# Division by zero
# ---------------------------------------------

def test_dividing_by_zero_returns_a_400_with_the_message(client):
    response = client.post("/divide", json={"a": 1, "b": 0})
    assert response.status_code == 400
    assert response.json() == {"error": "Cannot divide by zero!"}


# ---------------------------------------------
# Invalid input
# ---------------------------------------------

@pytest.mark.parametrize("path", OPERATION_PATHS)
def test_a_missing_number_returns_a_400(client, path):
    response = client.post(path, json={"a": 1})
    assert response.status_code == 400
    assert response.json() == {"error": "b: Field required"}


@pytest.mark.parametrize("path", OPERATION_PATHS)
def test_text_instead_of_a_number_returns_a_400(client, path):
    response = client.post(path, json={"a": "abc", "b": 1})
    assert response.status_code == 400
    assert response.json()["error"].startswith("a: Input should be a valid number")


def test_every_problem_is_reported_together(client):
    response = client.post("/add", json={"a": "x", "b": "y"})
    assert response.status_code == 400
    error = response.json()["error"]
    assert "a:" in error
    assert "b:" in error


def test_an_empty_body_returns_a_400(client):
    response = client.post("/add")
    assert response.status_code == 400
    assert "error" in response.json()


def test_empty_fields_from_the_web_page_return_a_400(client):
    # An empty input box becomes null when the page sends it as JSON
    response = client.post("/multiply", json={"a": None, "b": None})
    assert response.status_code == 400
    assert "Input should be a valid number" in response.json()["error"]


def test_invalid_json_returns_a_400(client):
    response = client.post(
        "/add",
        content="this is not json",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400
    assert "error" in response.json()


# ---------------------------------------------
# Unknown pages and wrong methods
# ---------------------------------------------

def test_an_unknown_page_returns_a_404(client):
    assert client.get("/nothing-here").status_code == 404


@pytest.mark.parametrize("path", OPERATION_PATHS)
def test_reading_an_operation_with_get_returns_a_405(client, path):
    assert client.get(path).status_code == 405


# ---------------------------------------------
# Unexpected errors inside an operation
# ---------------------------------------------

def broken_operation(a, b):
    raise RuntimeError("something broke")


@pytest.mark.parametrize("name", ["add", "subtract", "multiply"])
def test_an_unexpected_error_returns_a_400(client, monkeypatch, name):
    monkeypatch.setattr(main, name, broken_operation)
    response = client.post(f"/{name}", json={"a": 1, "b": 2})
    assert response.status_code == 400
    assert response.json() == {"error": "something broke"}


def test_an_unexpected_error_in_divide_returns_a_500(client, monkeypatch):
    monkeypatch.setattr(main, "divide", broken_operation)
    response = client.post("/divide", json={"a": 1, "b": 2})
    assert response.status_code == 500
    assert response.json() == {"error": "Internal Server Error"}


# ---------------------------------------------
# Logging
# ---------------------------------------------

def test_the_home_page_is_logged(client, caplog):
    with caplog.at_level(logging.INFO, logger="calculator"):
        client.get("/")
    assert "Serving the calculator page" in caplog.messages


def test_a_successful_request_is_logged(client, caplog):
    with caplog.at_level(logging.INFO, logger="calculator"):
        client.post("/add", json={"a": 2, "b": 3})
    assert "Received /add request: a=2.0, b=3.0" in caplog.messages
    assert "add(2.0, 3.0) = 5.0" in caplog.messages


def test_division_by_zero_is_logged_as_an_error(client, caplog):
    with caplog.at_level(logging.INFO, logger="calculator"):
        client.post("/divide", json={"a": 1, "b": 0})
    assert "Divide Operation Error: Cannot divide by zero!" in caplog.messages
    assert "HTTPException on /divide: Cannot divide by zero!" in caplog.messages


def test_validation_errors_are_logged(client, caplog):
    with caplog.at_level(logging.INFO, logger="calculator"):
        client.post("/add", json={"a": 1})
    assert "ValidationError on /add: b: Field required" in caplog.messages