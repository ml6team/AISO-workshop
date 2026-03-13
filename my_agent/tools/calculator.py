import math


def calculator(operation: str, a: float, b: float = 0.0) -> str:
    """Perform a mathematical calculation.

    Use this tool for ANY arithmetic or math operation. Supported operations:
    - "add": returns a + b
    - "subtract": returns a - b
    - "multiply": returns a * b
    - "divide": returns a / b
    - "power": returns a raised to the power of b
    - "sqrt": returns the square root of a (b is ignored)
    - "modulo": returns a % b

    Args:
        operation: The math operation to perform. One of: add, subtract, multiply, divide, power, sqrt, modulo.
        a: The first number.
        b: The second number (not used for sqrt).

    Returns:
        The result of the calculation as a string.
    """
    operation = operation.lower().strip()

    if operation == "add":
        result = a + b
    elif operation == "subtract":
        result = a - b
    elif operation == "multiply":
        result = a * b
    elif operation == "divide":
        if b == 0:
            return "Error: Division by zero."
        result = a / b
    elif operation == "power":
        result = a ** b
    elif operation == "sqrt":
        if a < 0:
            return "Error: Cannot take square root of a negative number."
        result = math.sqrt(a)
    elif operation == "modulo":
        if b == 0:
            return "Error: Modulo by zero."
        result = a % b
    else:
        return f"Error: Unknown operation '{operation}'. Supported: add, subtract, multiply, divide, power, sqrt, modulo."

    return str(result)
