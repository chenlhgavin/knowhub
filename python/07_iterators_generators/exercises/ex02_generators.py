"""Exercise 02: Generator Functions

Implement these generator functions:

1. fibonacci() - infinite generator yielding 0, 1, 1, 2, 3, 5, 8, ...
2. chunks(iterable, size) - yield successive chunks of the given size.
3. unique(iterable) - yield only first occurrences, preserving order.
4. window(iterable, size) - yield sliding windows as tuples.
"""

from typing import Generator


def fibonacci() -> Generator[int, None, None]:
    """Infinite generator of Fibonacci numbers starting from 0.

    >>> gen = fibonacci()
    >>> [next(gen) for _ in range(8)]
    [0, 1, 1, 2, 3, 5, 8, 13]
    """
    raise NotImplementedError


def chunks(iterable, size: int):
    """Yield successive chunks of `size` elements from `iterable`.

    The last chunk may be shorter if there are not enough elements.
    Must work with any iterable (not just sequences).

    >>> list(chunks([1, 2, 3, 4, 5], 2))
    [[1, 2], [3, 4], [5]]
    """
    raise NotImplementedError


def unique(iterable):
    """Yield elements from iterable, skipping duplicates. Preserve order.

    >>> list(unique([1, 2, 1, 3, 2, 4]))
    [1, 2, 3, 4]
    """
    raise NotImplementedError


def window(iterable, size: int):
    """Yield sliding windows of `size` as tuples.

    >>> list(window([1, 2, 3, 4, 5], 3))
    [(1, 2, 3), (2, 3, 4), (3, 4, 5)]
    """
    raise NotImplementedError


if __name__ == "__main__":
    # --- fibonacci tests ---
    fib = fibonacci()
    first_10 = [next(fib) for _ in range(10)]
    assert first_10 == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

    # --- chunks tests ---
    assert list(chunks([1, 2, 3, 4, 5], 2)) == [[1, 2], [3, 4], [5]]
    assert list(chunks([1, 2, 3, 4], 2)) == [[1, 2], [3, 4]]
    assert list(chunks([], 3)) == []
    assert list(chunks(range(7), 3)) == [[0, 1, 2], [3, 4, 5], [6]]

    # --- unique tests ---
    assert list(unique([1, 2, 1, 3, 2, 4])) == [1, 2, 3, 4]
    assert list(unique("abracadabra")) == ["a", "b", "r", "c", "d"]
    assert list(unique([])) == []

    # --- window tests ---
    assert list(window([1, 2, 3, 4, 5], 3)) == [(1, 2, 3), (2, 3, 4), (3, 4, 5)]
    assert list(window([1, 2, 3], 1)) == [(1,), (2,), (3,)]
    assert list(window([1, 2], 3)) == []
    assert list(window(range(5), 2)) == [(0, 1), (1, 2), (2, 3), (3, 4)]

    print("All tests passed!")
