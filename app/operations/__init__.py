# app/operations/__init__.py

"""
Module: operations

This module contains basic arithmetic functions that perform addition, subtraction,
multiplication, and division of two numbers. These functions are foundational for
building more complex applications, such as calculators or financial tools.

Every operation writes a line to the application log: an INFO line with the result
when it works, and a WARNING line when it is asked to do something invalid.

Functions:
- add(a, b): Returns the sum of a and b.
- subtract(a, b): Returns the difference when b is subtracted from a.
- multiply(a, b): Returns the product of a and b.
- divide(a, b): Returns the quotient of a divided by b. Raises ValueError if b is zero.
"""

import logging
from typing import Union

# A child of the "calculator" logger set up in app/logging_config.py
logger = logging.getLogger("calculator.operations")

# A type alias for numbers that can be either int or float
Number = Union[int, float]


def add(a: Number, b: Number) -> Number:
    """
    Add two numbers and return the result.

    Example:
    >>> add(2, 3)
    5
    >>> add(2.5, 3)
    5.5
    """
    result = a + b
    logger.info("add(%s, %s) = %s", a, b, result)
    return result


def subtract(a: Number, b: Number) -> Number:
    """
    Subtract the second number from the first and return the result.

    Example:
    >>> subtract(5, 3)
    2
    >>> subtract(5.5, 2)
    3.5
    """
    result = a - b
    logger.info("subtract(%s, %s) = %s", a, b, result)
    return result


def multiply(a: Number, b: Number) -> Number:
    """
    Multiply two numbers and return the product.

    Example:
    >>> multiply(2, 3)
    6
    >>> multiply(2.5, 4)
    10.0
    """
    result = a * b
    logger.info("multiply(%s, %s) = %s", a, b, result)
    return result


def divide(a: Number, b: Number) -> float:
    """
    Divide the first number by the second and return the quotient.

    Raises:
    - ValueError: If b is zero, as division by zero is undefined.

    Example:
    >>> divide(6, 3)
    2.0
    >>> divide(5.5, 2)
    2.75
    >>> divide(5, 0)
    Traceback (most recent call last):
        ...
    ValueError: Cannot divide by zero!
    """
    # Check if the divisor is zero to prevent division by zero
    if b == 0:
        logger.warning("divide(%s, %s) rejected: division by zero", a, b)
        raise ValueError("Cannot divide by zero!")

    result = a / b
    logger.info("divide(%s, %s) = %s", a, b, result)
    return result