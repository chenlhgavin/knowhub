"""Solution 04: match-case (Structural Pattern Matching)"""


def http_status(code: int) -> str:
    """Return a human-readable status text for an HTTP status code."""
    match code:
        case 200:
            return "OK"
        case 301:
            return "Moved"
        case 404:
            return "Not Found"
        case 500:
            return "Server Error"
        case _:
            return "Unknown"


def describe_sequence(seq) -> str:
    """Describe a sequence using pattern matching."""
    match seq:
        case tuple():
            return f"tuple of {len(seq)}"
        case list() as lst if len(lst) == 0:
            return "empty list"
        case list() as lst if len(lst) == 1:
            return "singleton"
        case _:
            return "other"


def evaluate(expr: tuple) -> float:
    """Evaluate a simple arithmetic expression represented as a tuple."""
    match expr:
        case ("+", a, b):
            return float(a + b)
        case ("-", a, b):
            return float(a - b)
        case ("*", a, b):
            return float(a * b)
        case ("/", a, b):
            return float(a / b)
        case (op, _, _):
            raise ValueError(f"Unknown operator: {op}")


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
