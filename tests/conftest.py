# tests/conftest.py

import subprocess
import sys
import time
from pathlib import Path

import pytest
import requests
from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SERVER_URL = "http://127.0.0.1:8000/"


@pytest.fixture(scope="session")
def fastapi_server():
    """
    Start the FastAPI server before the end-to-end tests and stop it afterwards.

    The fixture returns the server's URL, so tests can use it with page.goto().
    """
    # Run main.py with the same Python that is running the tests
    process = subprocess.Popen([sys.executable, "main.py"], cwd=PROJECT_ROOT)

    # Wait for the server to start by polling the home page
    timeout = 30  # seconds
    start_time = time.time()
    server_up = False

    while time.time() - start_time < timeout:
        try:
            if requests.get(SERVER_URL, timeout=2).status_code == 200:
                server_up = True
                break
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)

    if not server_up:
        process.terminate()
        raise RuntimeError("FastAPI server failed to start within the timeout period.")

    yield SERVER_URL

    # Stop the server
    process.terminate()
    process.wait()


@pytest.fixture(scope="session")
def playwright_instance_fixture():
    """Manage Playwright's lifecycle."""
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance_fixture):
    """Launch one headless browser for the whole test session."""
    browser = playwright_instance_fixture.chromium.launch(headless=True)
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def page(browser):
    """Give every test a fresh browser page."""
    page = browser.new_page()
    yield page
    page.close()