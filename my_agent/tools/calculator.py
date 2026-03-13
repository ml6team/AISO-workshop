def calculator(operation: str, a: float, b: float = 0.0) -> str:
    """Perform a basic arithmetic operation.

    Use this tool for all arithmetic instead of mental math.

    Args:
        operation: One of add, subtract, multiply, divide, power, or sqrt.
        a: Left operand, or the value for sqrt.
        b: Right operand for binary operations.

    Returns:
        The numeric result as a string, or an error string.
    """
    operation_name = operation.strip().lower()

    if operation_name == "add":
        result = a + b
    elif operation_name == "subtract":
        result = a - b
    elif operation_name == "multiply":
        result = a * b
    elif operation_name == "divide":
        if b == 0:
            return "Error: Division by zero."
        result = a / b
    elif operation_name == "power":
        result = a**b
    elif operation_name == "sqrt":
        if a < 0:
            return "Error: Cannot take square root of a negative number."
        result = a**0.5
    else:
        return (
            "Error: Unknown operation. Use add, subtract, multiply, divide, "
            "power, or sqrt."
        )

    return str(result)
