"""Solution 01: Exception Handling Basics

Practice fundamental exception handling patterns in Python:
- Catching and converting exceptions
- Raising exceptions with informative messages
- Type checking and validation
- Retry logic with exception propagation
"""


def safe_int(value: str) -> int | None:
    """Convert a string to an integer, returning None on failure.

    Args:
        value: The string to convert.

    Returns:
        The integer value, or None if conversion fails.

    Examples:
        >>> safe_int("42")
        42
        >>> safe_int("hello") is None
        True
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def safe_divide(a: float, b: float) -> float:
    """Divide a by b, raising ZeroDivisionError if b is zero.

    Args:
        a: The numerator.
        b: The denominator.

    Returns:
        The result of a / b.

    Raises:
        ZeroDivisionError: If b is zero, with message "Cannot divide by zero".
    """
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b


def validate_age(age: int) -> int:
    """Validate that age is a reasonable integer.

    Args:
        age: The age to validate.

    Returns:
        The validated age.

    Raises:
        TypeError: If age is not an int (bool is not accepted).
        ValueError: If age is negative or greater than 150.
    """
    if not isinstance(age, int) or isinstance(age, bool):
        raise TypeError(f"age must be an int, got {type(age).__name__}")
    if age < 0 or age > 150:
        raise ValueError(f"age must be between 0 and 150, got {age}")
    return age


def retry(func, max_attempts: int = 3):
    """Call func() with retry logic.

    Calls func() up to max_attempts times. If func() succeeds, return
    its result immediately. If func() raises an Exception, retry until
    max_attempts is exhausted, then re-raise the last exception.

    Args:
        func: A callable taking no arguments.
        max_attempts: Maximum number of attempts (default 3).

    Returns:
        The return value of func() on success.

    Raises:
        The last Exception raised by func() if all attempts fail.
    """
    last_exception = None
    for _ in range(max_attempts):
        try:
            return func()
        except Exception as e:
            last_exception = e
    raise last_exception


if __name__ == "__main__":
    # --- safe_int tests ---
    assert safe_int("42") == 42
    assert safe_int("-7") == -7
    assert safe_int("0") == 0
    assert safe_int("hello") is None
    assert safe_int("3.14") is None
    assert safe_int("") is None

    # --- safe_divide tests ---
    assert safe_divide(10, 2) == 5.0
    assert safe_divide(7, 3) == 7 / 3
    assert safe_divide(-6, 3) == -2.0
    assert safe_divide(0, 5) == 0.0

    try:
        safe_divide(1, 0)
        assert False, "Should have raised ZeroDivisionError"
    except ZeroDivisionError as e:
        assert str(e) == "Cannot divide by zero"

    # --- validate_age tests ---
    assert validate_age(0) == 0
    assert validate_age(25) == 25
    assert validate_age(150) == 150

    try:
        validate_age(-1)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    try:
        validate_age(151)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    try:
        validate_age("25")
        assert False, "Should have raised TypeError"
    except TypeError:
        pass

    try:
        validate_age(True)
        assert False, "Should have raised TypeError"
    except TypeError:
        pass

    # --- retry tests ---
    # Succeeds on first try
    assert retry(lambda: 42) == 42

    # Succeeds on second try
    call_count = 0

    def flaky():
        global call_count
        call_count += 1
        if call_count < 2:
            raise RuntimeError("temporary failure")
        return "ok"

    call_count = 0
    assert retry(flaky) == "ok"
    assert call_count == 2

    # Fails all attempts
    def always_fails():
        raise ValueError("permanent failure")

    try:
        retry(always_fails, max_attempts=3)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert str(e) == "permanent failure"

    # Single attempt
    call_count = 0

    def fail_once():
        global call_count
        call_count += 1
        if call_count == 1:
            raise RuntimeError("fail")
        return "success"

    call_count = 0
    try:
        retry(fail_once, max_attempts=1)
        assert False, "Should have raised RuntimeError"
    except RuntimeError:
        pass

    print("All sol01_exceptions tests passed!")
