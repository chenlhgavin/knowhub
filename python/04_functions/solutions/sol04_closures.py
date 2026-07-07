"""Solution 04 — Closures

Complete implementations for ex04_closures.py.
"""

from typing import Callable


def counter(start: int = 0) -> Callable[[], int]:
    """Return a function that returns incrementing integers starting from *start*."""
    count = start

    def next_value() -> int:
        nonlocal count
        value = count
        count += 1
        return value

    return next_value


def make_accumulator() -> Callable[[int | float], int | float]:
    """Return a function that accumulates (sums) all values passed to it."""
    total = 0

    def accumulate(n):
        nonlocal total
        total += n
        return total

    return accumulate


def memoize(func: Callable) -> Callable:
    """Return a memoized version of *func*.

    Cache results in a dict keyed by the positional arguments.
    """
    cache: dict = {}

    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]

    return wrapper


def once(func: Callable) -> Callable:
    """Return a function that calls *func* only on the first invocation.

    Subsequent calls return the cached result of the first call.
    """
    called = False
    result = None

    def wrapper(*args, **kwargs):
        nonlocal called, result
        if not called:
            result = func(*args, **kwargs)
            called = True
        return result

    return wrapper


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # counter
    c = counter(10)
    assert c() == 10
    assert c() == 11
    assert c() == 12

    c2 = counter()
    assert c2() == 0
    assert c2() == 1

    # make_accumulator
    acc = make_accumulator()
    assert acc(5) == 5
    assert acc(3) == 8
    assert acc(2) == 10

    acc2 = make_accumulator()
    assert acc2(100) == 100
    assert acc2(-50) == 50

    # memoize
    call_log = []

    @memoize
    def tracked_square(x):
        call_log.append(x)
        return x ** 2

    assert tracked_square(4) == 16
    assert tracked_square(4) == 16
    assert tracked_square(5) == 25
    assert len(call_log) == 2, "func should only be called once per unique args"

    # memoize with multiple args
    @memoize
    def add(a, b):
        return a + b

    assert add(1, 2) == 3
    assert add(1, 2) == 3
    assert add(3, 4) == 7

    # once
    once_log = []

    @once
    def greet(name):
        once_log.append(name)
        return f"Hello, {name}!"

    assert greet("Alice") == "Hello, Alice!"
    assert greet("Bob") == "Hello, Alice!"
    assert greet("Charlie") == "Hello, Alice!"
    assert len(once_log) == 1

    print("All tests passed!")
