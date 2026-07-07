"""Exercise 01: Custom Iterators

Implement the iteration protocol (__iter__ and __next__) for three classes:

1. Countdown(start) - counts from start down to 1, then stops.
2. Cycle(items) - cycles through items infinitely.
3. ChainedIterator(*iterables) - iterates through multiple iterables in sequence.
"""


class Countdown:
    """Iterator that counts from `start` down to 1.

    >>> list(Countdown(5))
    [5, 4, 3, 2, 1]
    """

    def __init__(self, start: int):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __next__(self):
        raise NotImplementedError


class Cycle:
    """Infinite iterator that cycles through the given items repeatedly.

    >>> c = Cycle([1, 2, 3])
    >>> [next(c) for _ in range(7)]
    [1, 2, 3, 1, 2, 3, 1]
    """

    def __init__(self, items: list):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __next__(self):
        raise NotImplementedError


class ChainedIterator:
    """Iterator that chains multiple iterables together in sequence.

    >>> list(ChainedIterator([1, 2], [3, 4], [5]))
    [1, 2, 3, 4, 5]
    """

    def __init__(self, *iterables):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __next__(self):
        raise NotImplementedError


if __name__ == "__main__":
    # --- Countdown tests ---
    assert list(Countdown(5)) == [5, 4, 3, 2, 1]
    assert list(Countdown(1)) == [1]
    assert list(Countdown(0)) == []

    # --- Cycle tests ---
    c = Cycle([1, 2, 3])
    assert [next(c) for _ in range(7)] == [1, 2, 3, 1, 2, 3, 1]

    c2 = Cycle(["a", "b"])
    assert [next(c2) for _ in range(5)] == ["a", "b", "a", "b", "a"]

    # --- ChainedIterator tests ---
    assert list(ChainedIterator([1, 2], [3, 4])) == [1, 2, 3, 4]
    assert list(ChainedIterator([1], [2], [3])) == [1, 2, 3]
    assert list(ChainedIterator([], [1, 2], [])) == [1, 2]
    assert list(ChainedIterator()) == []

    print("All tests passed!")
