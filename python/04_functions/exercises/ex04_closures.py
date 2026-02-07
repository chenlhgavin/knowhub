"""Exercise 04 — Closures

Topics: closures, nonlocal, mutable state captured by enclosing scope, memoization.

Implement the four functions below. Run this file to check your solutions.
"""

from typing import Callable


def counter(start: int = 0) -> Callable[[], int]:
    """Return a function that returns incrementing integers starting from *start*.

    >>> c = counter(10)
    >>> c()
    10
    >>> c()
    11
    >>> c()
    12
    """
    raise NotImplementedError


def make_accumulator() -> Callable[[int | float], int | float]:
    """Return a function that accumulates (sums) all values passed to it.

    >>> acc = make_accumulator()
    >>> acc(5)
    5
    >>> acc(3)
    8
    >>> acc(2)
    10
    """
    raise NotImplementedError


def memoize(func: Callable) -> Callable:
    """Return a memoized version of *func*.

    Cache results in a dict keyed by the positional arguments. Assume all
    arguments are hashable.

    >>> @memoize
    ... def slow_square(x):
    ...     return x ** 2
    >>> slow_square(4)
    16
    >>> slow_square(4)  # returns cached result
    16
    """
    raise NotImplementedError


def once(func: Callable) -> Callable:
    """Return a function that calls *func* only on the first invocation.

    Subsequent calls return the cached result of the first call, regardless of
    the arguments passed.

    >>> @once
    ... def greet(name):
    ...     return f"Hello, {name}!"
    >>> greet("Alice")
    'Hello, Alice!'
    >>> greet("Bob")
    'Hello, Alice!'
    """
    raise NotImplementedError


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
