def calculator(operation: str, a: float, b: float) -> str:
    """Performs a basic arithmetic calculation on two numbers.

    Use this tool whenever you need to do math — addition, subtraction,
    multiplication, or division. Always prefer this over mental arithmetic.

    Args:
        operation (str): The math operation to perform.
            Must be one of: "add", "subtract", "multiply", "divide", "power", "sqrt".
        a (float): The first number (left operand).
        b (float): The second number (right operand).

    Returns:
        str: The numeric result as a string, or an error message.

    Examples:
        >>> calculator("add", 2, 3)
        '5.0'
        >>> calculator("divide", 10, 0)
        'Error: Division by zero.'
    """
    match operation:
        case "add":
            result = a + b
        case "subtract":
            result = a - b
        case "multiply":
            result = a * b
        case "divide":
            if b == 0:
                return "Error: Division by zero."
            result = a / b
        case "power":
            result = a ** b
        case "sqrt":
            if a < 0:
                return "Error: Cannot take square root of a negative number."
            result = a ** 0.5
        case _:
            return f"Error: Unknown operation '{operation}'. Use add, subtract, multiply, divide, power, or sqrt."

    return str(result)
