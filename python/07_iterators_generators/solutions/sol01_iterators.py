"""Solution 01: Custom Iterators

Implementations of Countdown, Cycle, and ChainedIterator using the
iteration protocol (__iter__ and __next__).
"""


class Countdown:
    """Iterator that counts from `start` down to 1.

    >>> list(Countdown(5))
    [5, 4, 3, 2, 1]
    """

    def __init__(self, start: int):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current < 1:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value


class Cycle:
    """Infinite iterator that cycles through the given items repeatedly.

    >>> c = Cycle([1, 2, 3])
    >>> [next(c) for _ in range(7)]
    [1, 2, 3, 1, 2, 3, 1]
    """

    def __init__(self, items: list):
        self.items = items
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if not self.items:
            raise StopIteration
        value = self.items[self.index]
        self.index = (self.index + 1) % len(self.items)
        return value


class ChainedIterator:
    """Iterator that chains multiple iterables together in sequence.

    >>> list(ChainedIterator([1, 2], [3, 4], [5]))
    [1, 2, 3, 4, 5]
    """

    def __init__(self, *iterables):
        self.iterators = iter([iter(it) for it in iterables])
        self.current = None
        self._advance()

    def _advance(self):
        """Move to the next non-exhausted iterator."""
        try:
            self.current = next(self.iterators)
        except StopIteration:
            self.current = None

    def __iter__(self):
        return self

    def __next__(self):
        while self.current is not None:
            try:
                return next(self.current)
            except StopIteration:
                self._advance()
        raise StopIteration


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
