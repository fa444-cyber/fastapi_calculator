# tests/e2e/test_e2e_calculator.py

import pytest
from playwright.sync_api import expect


def press(page, button_name):
    """Click one of the calculator buttons by its exact name."""
    page.get_by_role("button", name=button_name, exact=True).click()


@pytest.mark.e2e
def test_the_page_has_the_expected_layout(page, fastapi_server):
    page.goto(fastapi_server)
    expect(page).to_have_title("Hello World & Calculator Demo")
    expect(page.locator("h1")).to_have_text("Hello World")
    expect(page.locator("h2")).to_have_text("Calculator")
    expect(page.locator("#a")).to_be_visible()
    expect(page.locator("#b")).to_be_visible()
    for name in ["Add", "Subtract", "Multiply", "Divide"]:
        expect(page.get_by_role("button", name=name, exact=True)).to_be_visible()


@pytest.mark.e2e
def test_the_result_area_is_empty_at_first(page, fastapi_server):
    page.goto(fastapi_server)
    expect(page.locator("#result")).to_be_empty()


@pytest.mark.e2e
@pytest.mark.parametrize("a, b, button, expected", [
    ("10", "5", "Add", "Calculation Result: 15"),
    ("10", "5", "Subtract", "Calculation Result: 5"),
    ("10", "5", "Multiply", "Calculation Result: 50"),
    ("10", "5", "Divide", "Calculation Result: 2"),
    ("2.5", "0.5", "Add", "Calculation Result: 3"),
    ("-4", "6", "Multiply", "Calculation Result: -24"),
    ("1", "4", "Divide", "Calculation Result: 0.25"),
    ("0", "7", "Subtract", "Calculation Result: -7"),
])
def test_each_operation_shows_its_result(page, fastapi_server, a, b, button, expected):
    page.goto(fastapi_server)
    page.fill("#a", a)
    page.fill("#b", b)
    press(page, button)
    expect(page.locator("#result")).to_have_text(expected)


@pytest.mark.e2e
def test_dividing_by_zero_shows_an_error(page, fastapi_server):
    page.goto(fastapi_server)
    page.fill("#a", "10")
    page.fill("#b", "0")
    press(page, "Divide")
    expect(page.locator("#result")).to_have_text("Error: Cannot divide by zero!")


@pytest.mark.e2e
@pytest.mark.parametrize("button", ["Add", "Subtract", "Multiply", "Divide"])
def test_empty_fields_show_an_error(page, fastapi_server, button):
    page.goto(fastapi_server)
    press(page, button)
    expect(page.locator("#result")).to_contain_text("Input should be a valid number")


@pytest.mark.e2e
def test_the_result_changes_when_a_second_calculation_is_made(page, fastapi_server):
    page.goto(fastapi_server)
    page.fill("#a", "6")
    page.fill("#b", "3")
    press(page, "Add")
    expect(page.locator("#result")).to_have_text("Calculation Result: 9")
    press(page, "Multiply")
    expect(page.locator("#result")).to_have_text("Calculation Result: 18")