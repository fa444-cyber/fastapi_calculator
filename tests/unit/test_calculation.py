import pytest
from pydantic import ValidationError

from app.calculation_factory import CalculationFactory
from app.schemas import CalculationCreate


# --- Factory: each type picks the right operation ---

@pytest.mark.parametrize(
    "calc_type, a, b, expected",
    [
        ("Add", 2, 3, 5),
        ("Sub", 5, 3, 2),
        ("Multiply", 4, 5, 20),
        ("Divide", 10, 2, 5),
    ],
)
def test_factory_computes_each_type(calc_type, a, b, expected):
    assert CalculationFactory.compute(calc_type, a, b) == expected


def test_factory_returns_callable_for_known_type():
    assert callable(CalculationFactory.get_operation("Add"))


def test_factory_rejects_unknown_type():
    with pytest.raises(ValueError, match="Unsupported calculation type"):
        CalculationFactory.get_operation("Power")


def test_factory_divide_by_zero_raises():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        CalculationFactory.compute("Divide", 5, 0)


# --- CalculationCreate: validation ---

@pytest.mark.parametrize("calc_type", ["Add", "Sub", "Multiply", "Divide"])
def test_create_accepts_each_valid_type(calc_type):
    calc = CalculationCreate(a=6, b=3, type=calc_type)
    assert calc.type == calc_type


def test_create_rejects_unknown_type():
    with pytest.raises(ValidationError):
        CalculationCreate(a=6, b=3, type="Power")


def test_create_rejects_zero_divisor():
    with pytest.raises(ValidationError, match="Cannot divide by zero"):
        CalculationCreate(a=6, b=0, type="Divide")


def test_create_allows_zero_for_non_divide_types():
    calc = CalculationCreate(a=6, b=0, type="Multiply")
    assert calc.b == 0


def test_create_rejects_non_numeric_operand():
    with pytest.raises(ValidationError):
        CalculationCreate(a="six", b=3, type="Add")