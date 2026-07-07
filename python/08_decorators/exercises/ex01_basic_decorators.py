"""Exercise 01: Basic Decorators

Implement simple function decorators that add behavior around function calls.
Focus on using functools.wraps to preserve the original function's metadata.
"""

import functools
import time


def timer(func):
    """Decorator that prints execution time to stdout and returns the result.

    Output format: "{func_name} took {elapsed:.4f}s"
    Must use functools.wraps to preserve metadata.
    """
    raise NotImplementedError("Implement the timer decorator")


def debug(func):
    """Decorator that prints function name, args, kwargs before the call
    and the return value after.

    Before call: "Calling {func_name}({args}, {kwargs})"
    After call:  "{func_name} returned {result}"
    Must use functools.wraps to preserve metadata.
    """
    raise NotImplementedError("Implement the debug decorator")


def count_calls(func):
    """Decorator that tracks how many times the function has been called.

    The wrapper must have a `call_count` attribute (int) starting at 0,
    incremented on each call. Must use functools.wraps to preserve metadata.
    """
    raise NotImplementedError("Implement the count_calls decorator")


if __name__ == "__main__":
    import io
    import sys

    # --- timer tests ---
    @timer
    def slow_add(a, b):
        """Add two numbers slowly."""
        time.sleep(0.05)
        return a + b

    captured = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured
    result = slow_add(2, 3)
    sys.stdout = old_stdout

    assert result == 5, f"Expected 5, got {result}"
    output = captured.getvalue()
    assert "slow_add took" in output, f"Expected timing output, got: {output}"
    assert slow_add.__name__ == "slow_add", "functools.wraps not applied"
    assert slow_add.__doc__ == "Add two numbers slowly.", "functools.wraps not applied"

    # --- debug tests ---
    @debug
    def multiply(x, y):
        """Multiply two numbers."""
        return x * y

    captured = io.StringIO()
    sys.stdout = captured
    result = multiply(3, 4)
    sys.stdout = old_stdout

    assert result == 12, f"Expected 12, got {result}"
    output = captured.getvalue()
    assert "Calling multiply" in output, f"Expected calling info, got: {output}"
    assert "multiply returned 12" in output, f"Expected return info, got: {output}"
    assert multiply.__name__ == "multiply", "functools.wraps not applied"
    assert multiply.__doc__ == "Multiply two numbers.", "functools.wraps not applied"

    # --- count_calls tests ---
    @count_calls
    def greet(name):
        """Greet someone."""
        return f"Hello, {name}!"

    assert greet.call_count == 0, f"Expected 0, got {greet.call_count}"
    assert greet("Alice") == "Hello, Alice!"
    assert greet.call_count == 1, f"Expected 1, got {greet.call_count}"
    greet("Bob")
    assert greet.call_count == 2, f"Expected 2, got {greet.call_count}"
    assert greet.__name__ == "greet", "functools.wraps not applied"
    assert greet.__doc__ == "Greet someone.", "functools.wraps not applied"

    print("All ex01 tests passed.")
