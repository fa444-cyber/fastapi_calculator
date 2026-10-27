# tests/unit/test_operations_logging.py

import logging

import pytest

from app.operations import add, divide, multiply, subtract


@pytest.mark.parametrize("function, a, b, expected_message", [
    (add, 2, 3, "add(2, 3) = 5"),
    (subtract, 5, 3, "subtract(5, 3) = 2"),
    (multiply, 4, 2.5, "multiply(4, 2.5) = 10.0"),
    (divide, 6, 3, "divide(6, 3) = 2.0"),
])
def test_successful_operations_are_logged_at_info(
    caplog, function, a, b, expected_message
):
    with caplog.at_level(logging.INFO, logger="calculator"):
        function(a, b)
    expected = ("calculator.operations", logging.INFO, expected_message)
    assert expected in caplog.record_tuples


def test_dividing_by_zero_is_logged_as_a_warning(caplog):
    with caplog.at_level(logging.INFO, logger="calculator"):
        with pytest.raises(ValueError):
            divide(6, 0)
    expected = (
        "calculator.operations",
        logging.WARNING,
        "divide(6, 0) rejected: division by zero",
    )
    assert expected in caplog.record_tuples


def test_a_failed_operation_logs_no_result(caplog):
    with caplog.at_level(logging.INFO, logger="calculator"):
        with pytest.raises(ValueError):
            divide(1, 0)
    assert not [r for r in caplog.records if r.levelno == logging.INFO]