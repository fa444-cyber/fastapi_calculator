from typing import Callable

from app.operations import add, subtract, multiply, divide

# Maps each calculation type name to the operation that performs it.
OPERATIONS: dict[str, Callable[[float, float], float]] = {
    "Add": add,
    "Sub": subtract,
    "Multiply": multiply,
    "Divide": divide,
}


class CalculationFactory:
    """Chooses the correct operation for a calculation type string."""

    @staticmethod
    def get_operation(calc_type: str) -> Callable[[float, float], float]:
        try:
            return OPERATIONS[calc_type]
        except KeyError:
            raise ValueError(f"Unsupported calculation type: {calc_type!r}") from None

    @staticmethod
    def compute(calc_type: str, a: float, b: float) -> float:
        return CalculationFactory.get_operation(calc_type)(a, b)