"""Exercise 02: Parameterized Decorators

Implement decorator factories -- decorators that accept arguments.
These use the triple-nested function pattern: factory -> decorator -> wrapper.
"""

import functools


def repeat(n: int):
    """Decorator factory: call the decorated function n times, return the last result.

    Usage:
        @repeat(3)
        def greet():
            print("Hello!")
            return "done"
        # greet() prints "Hello!" three times, returns "done"
    """
    raise NotImplementedError("Implement the repeat decorator factory")


def retry(max_attempts: int = 3, exceptions: tuple = (Exception,)):
    """Decorator factory: retry the function on specified exceptions.

    If the function raises one of the specified exceptions, retry up to
    max_attempts total calls. If all attempts fail, raise the last exception.

    Usage:
        @retry(max_attempts=3, exceptions=(ValueError,))
        def flaky():
            ...
    """
    raise NotImplementedError("Implement the retry decorator factory")


def validate_types(**type_kwargs):
    """Decorator factory: validate that arguments match specified types.

    Maps parameter names to expected types. Raises TypeError if a provided
    argument does not match its expected type.

    Usage:
        @validate_types(x=int, y=int)
        def add(x, y):
            return x + y

        add(1, 2)       # OK
        add("1", 2)     # raises TypeError
    """
    raise NotImplementedError("Implement the validate_types decorator factory")


if __name__ == "__main__":
    import io
    import sys

    # --- repeat tests ---
    call_log = []

    @repeat(3)
    def track_call(value):
        """Track calls."""
        call_log.append(value)
        return value

    result = track_call("x")
    assert result == "x", f"Expected 'x', got {result}"
    assert len(call_log) == 3, f"Expected 3 calls, got {len(call_log)}"
    assert all(v == "x" for v in call_log), f"Unexpected call log: {call_log}"
    assert track_call.__name__ == "track_call", "functools.wraps not applied"

    @repeat(1)
    def single_call():
        return 42

    assert single_call() == 42

    # --- retry tests ---
    attempt_counter = [0]

    @retry(max_attempts=3, exceptions=(ValueError,))
    def flaky_function():
        """A flaky function."""
        attempt_counter[0] += 1
        if attempt_counter[0] < 3:
            raise ValueError("Not ready yet")
        return "success"

    attempt_counter[0] = 0
    result = flaky_function()
    assert result == "success", f"Expected 'success', got {result}"
    assert attempt_counter[0] == 3, f"Expected 3 attempts, got {attempt_counter[0]}"
    assert flaky_function.__name__ == "flaky_function", "functools.wraps not applied"

    # Test that non-matching exceptions are not caught
    @retry(max_attempts=3, exceptions=(ValueError,))
    def wrong_exception():
        raise TypeError("wrong type")

    try:
        wrong_exception()
        assert False, "Should have raised TypeError"
    except TypeError:
        pass

    # Test all attempts exhausted
    @retry(max_attempts=2, exceptions=(ValueError,))
    def always_fails():
        raise ValueError("always")

    try:
        always_fails()
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert str(e) == "always"

    # --- validate_types tests ---
    @validate_types(x=int, y=int)
    def add(x, y):
        """Add two integers."""
        return x + y

    assert add(2, 3) == 5

    try:
        add("2", 3)
        assert False, "Should have raised TypeError"
    except TypeError:
        pass

    try:
        add(2, "3")
        assert False, "Should have raised TypeError"
    except TypeError:
        pass

    # Unvalidated arguments should pass through
    @validate_types(x=int)
    def flexible(x, y):
        return (x, y)

    assert flexible(1, "hello") == (1, "hello")
    assert flexible(1, 2) == (1, 2)
    assert add.__name__ == "add", "functools.wraps not applied"

    print("All ex02 tests passed.")
