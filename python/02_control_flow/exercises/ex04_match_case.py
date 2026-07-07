"""Exercise 04: match-case (Structural Pattern Matching)

Practice using Python 3.10+ match-case statements for value matching,
sequence destructuring, and type-based dispatch.

Implement each function according to its docstring. Run this file to check
your solutions against the built-in assertions.

Note: This exercise requires Python 3.10 or later.
"""


def http_status(code: int) -> str:
    """Return a human-readable status text for an HTTP status code.

    Use a match-case statement with the following mappings:
        200 -> "OK"
        301 -> "Moved"
        404 -> "Not Found"
        500 -> "Server Error"
        anything else -> "Unknown"

    Args:
        code: An HTTP status code.

    Returns:
        The corresponding status text.
    """
    raise NotImplementedError("Implement http_status()")


def describe_sequence(seq) -> str:
    """Describe a sequence using pattern matching.

    Use match-case to return:
        - "empty list"    if seq is an empty list []
        - "singleton"     if seq is a list with exactly one element
        - "tuple of N"    if seq is a tuple (where N is its length)
        - "other"         for anything else (including lists with 2+ elements)

    Hint: Sequence patterns like [] and [_] match both lists and tuples.
    Consider checking for tuple() first, or use type-specific patterns
    like list() with guards.

    Args:
        seq: Any value.

    Returns:
        A description string.
    """
    raise NotImplementedError("Implement describe_sequence()")


def evaluate(expr: tuple) -> float:
    """Evaluate a simple arithmetic expression represented as a tuple.

    Use match-case to destructure tuples of the form (operator, a, b):
        ("+", a, b) -> a + b
        ("-", a, b) -> a - b
        ("*", a, b) -> a * b
        ("/", a, b) -> a / b

    For any unrecognized operator, raise a ValueError with the message
    "Unknown operator: {op}" where {op} is the operator string.

    Args:
        expr: A tuple of (operator_string, operand1, operand2).

    Returns:
        The result as a float.
    """
    raise NotImplementedError("Implement evaluate()")


if __name__ == "__main__":
    # --- http_status tests ---
    assert http_status(200) == "OK"
    assert http_status(301) == "Moved"
    assert http_status(404) == "Not Found"
    assert http_status(500) == "Server Error"
    assert http_status(418) == "Unknown"
    assert http_status(0) == "Unknown"
    print("http_status: all tests passed")

    # --- describe_sequence tests ---
    assert describe_sequence([]) == "empty list"
    assert describe_sequence([42]) == "singleton"
    assert describe_sequence([1, 2]) == "other"
    assert describe_sequence([1, 2, 3]) == "other"
    assert describe_sequence((1, 2, 3)) == "tuple of 3"
    assert describe_sequence((1,)) == "tuple of 1"
    assert describe_sequence(()) == "tuple of 0"
    assert describe_sequence("hello") == "other"
    assert describe_sequence(42) == "other"
    print("describe_sequence: all tests passed")

    # --- evaluate tests ---
    assert evaluate(("+", 2, 3)) == 5.0
    assert evaluate(("-", 10, 4)) == 6.0
    assert evaluate(("*", 3, 7)) == 21.0
    assert evaluate(("/", 10, 2)) == 5.0
    assert evaluate(("+", 0, 0)) == 0.0
    assert evaluate(("*", -2, 3)) == -6.0

    try:
        evaluate(("%", 10, 3))
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Unknown operator: %" in str(e)

    print("evaluate: all tests passed")

    print("\nAll exercise 04 tests passed!")
