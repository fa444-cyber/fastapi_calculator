import uuid

import pytest
import requests
from playwright.sync_api import expect

SERVER = "http://127.0.0.1:8000"


def unique_email():
    """Return an email address no earlier test has used, so the database never has a duplicate."""
    return f"user-{uuid.uuid4().hex[:10]}@example.com"


def api_register(email, password="secret123"):
    """Create a user directly through the API so a login test has an account to use."""
    response = requests.post(
        f"{SERVER}/register",
        json={"username": f"u{uuid.uuid4().hex[:8]}", "email": email, "password": password},
        timeout=10,
    )
    assert response.status_code == 201


@pytest.mark.e2e
def test_register_with_valid_data_shows_success(page, fastapi_server):
    """Positive: registering with a valid email and password shows a success message and stores a token."""
    page.goto(f"{fastapi_server}register.html")
    page.fill("#username", f"u{uuid.uuid4().hex[:8]}")
    page.fill("#email", unique_email())
    page.fill("#password", "secret123")
    page.fill("#confirm-password", "secret123")
    page.click("#register-button")

    expect(page.locator("#message")).to_have_text("Registration successful. You are now signed in.")
    token = page.evaluate("() => localStorage.getItem('access_token')")
    assert token


@pytest.mark.e2e
def test_login_with_correct_credentials_shows_success(page, fastapi_server):
    """Positive: logging in with a registered email and correct password shows success and stores a token."""
    email = unique_email()
    api_register(email)

    page.goto(f"{fastapi_server}login.html")
    page.fill("#email", email)
    page.fill("#password", "secret123")
    page.click("#login-button")

    expect(page.locator("#message")).to_have_text("Login successful.")
    token = page.evaluate("() => localStorage.getItem('access_token')")
    assert token


@pytest.mark.e2e
def test_register_with_short_password_shows_error(page, fastapi_server):
    """Negative: a password under 8 characters is rejected in the browser with a clear message."""
    page.goto(f"{fastapi_server}register.html")
    page.fill("#username", f"u{uuid.uuid4().hex[:8]}")
    page.fill("#email", unique_email())
    page.fill("#password", "short")
    page.click("#register-button")

    expect(page.locator("#message")).to_have_text("Password must be at least 8 characters.")
    expect(page.locator("#message")).to_have_class("message error")


@pytest.mark.e2e
def test_login_with_wrong_password_shows_invalid_credentials(page, fastapi_server):
    """Negative: a wrong password gets a 401 from the server, and the page shows the invalid credentials message."""
    email = unique_email()
    api_register(email)

    page.goto(f"{fastapi_server}login.html")
    page.fill("#email", email)
    page.fill("#password", "wrong-pass")
    page.click("#login-button")

    expect(page.locator("#message")).to_have_text("Invalid email or password.")
    expect(page.locator("#message")).to_have_class("message error")
