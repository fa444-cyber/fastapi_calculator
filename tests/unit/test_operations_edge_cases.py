# tests/unit/test_operations_edge_cases.py

import pytest

from app.operations import add, divide, multiply, subtract


@pytest.mark.parametrize("a, b", [(2, 3), (-5, 8), (0.5, 0.25), (0, 0)])
def test_addition_does_not_depend_on_the_order(a, b):
    assert add(a, b) == add(b, a)


@pytest.mark.parametrize("number", [0, 7, -3, 2.5])
def test_adding_zero_changes_nothing(number):
    assert add(number, 0) == number


def test_adding_floats_is_accurate_enough():
    assert add(0.1, 0.2) == pytest.approx(0.3)


def test_adding_very_large_integers_stays_exact():
    assert add(10**15, 1) == 10**15 + 1


def test_integers_stay_integers_when_adding():
    assert isinstance(add(2, 3), int)


@pytest.mark.parametrize("number", [0, 4, -9, 1.5])
def test_subtracting_a_number_from_itself_gives_zero(number):
    assert subtract(number, number) == 0


def test_subtraction_depends_on_the_order():
    assert subtract(5, 3) == 2
    assert subtract(3, 5) == -2


@pytest.mark.parametrize("number", [0, 4, -9, 1.5])
def test_multiplying_by_one_changes_nothing(number):
    assert multiply(number, 1) == number


@pytest.mark.parametrize("number", [0, 4, -9, 1.5])
def test_multiplying_by_zero_gives_zero(number):
    assert multiply(number, 0) == 0


def test_two_negative_numbers_multiply_to_a_positive_number():
    assert multiply(-3, -4) == 12


def test_multiplying_very_large_integers_stays_exact():
    assert multiply(10**10, 10**10) == 10**20


def test_dividing_integers_gives_a_float():
    assert isinstance(divide(4, 2), float)


@pytest.mark.parametrize("a, b, expected", [
    (1, 3, 0.3333333333),
    (1, 1e-10, 1e10),
    (0, -5, 0),
    (-8, -2, 4),
    (7.5, 2.5, 3),
])
def test_division_edge_cases(a, b, expected):
    assert divide(a, b) == pytest.approx(expected)


@pytest.mark.parametrize("zero", [0, 0.0, -0.0])
def test_every_kind_of_zero_is_rejected(zero):
    with pytest.raises(ValueError, match="Cannot divide by zero!"):
        divide(5, zero)


def test_zero_divided_by_zero_is_rejected():
    with pytest.raises(ValueError, match="Cannot divide by zero!"):
        divide(0, 0)