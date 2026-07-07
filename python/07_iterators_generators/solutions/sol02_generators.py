"""Solution 02: Generator Functions

Implementations of fibonacci, chunks, unique, and window generators.
"""

from collections import deque
from typing import Generator


def fibonacci() -> Generator[int, None, None]:
    """Infinite generator of Fibonacci numbers starting from 0.

    >>> gen = fibonacci()
    >>> [next(gen) for _ in range(8)]
    [0, 1, 1, 2, 3, 5, 8, 13]
    """
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


def chunks(iterable, size: int):
    """Yield successive chunks of `size` elements from `iterable`.

    The last chunk may be shorter if there are not enough elements.
    Works with any iterable (not just sequences).

    >>> list(chunks([1, 2, 3, 4, 5], 2))
    [[1, 2], [3, 4], [5]]
    """
    it = iter(iterable)
    while True:
        chunk = []
        try:
            for _ in range(size):
                chunk.append(next(it))
        except StopIteration:
            if chunk:
                yield chunk
            return
        yield chunk


def unique(iterable):
    """Yield elements from iterable, skipping duplicates. Preserve order.

    >>> list(unique([1, 2, 1, 3, 2, 4]))
    [1, 2, 3, 4]
    """
    seen = set()
    for item in iterable:
        if item not in seen:
            seen.add(item)
            yield item


def window(iterable, size: int):
    """Yield sliding windows of `size` as tuples.

    >>> list(window([1, 2, 3, 4, 5], 3))
    [(1, 2, 3), (2, 3, 4), (3, 4, 5)]
    """
    it = iter(iterable)
    win = deque(maxlen=size)

    # Fill the initial window
    for _ in range(size):
        try:
            win.append(next(it))
        except StopIteration:
            return  # Not enough elements for even one window

    yield tuple(win)

    # Slide the window
    for item in it:
        win.append(item)
        yield tuple(win)


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
