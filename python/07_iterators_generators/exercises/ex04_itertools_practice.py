"""Exercise 04: itertools Practice

Implement these utility functions using the itertools module:

1. take(n, iterable) - take first n elements from any iterable.
2. pairwise(iterable) - return consecutive pairs.
3. powerset(iterable) - return all subsets.
4. groupby_key(iterable, key) - group elements by a key function into a dict.
"""

import itertools


def take(n: int, iterable) -> list:
    """Return the first n elements of iterable as a list.

    >>> take(3, range(10))
    [0, 1, 2]
    """
    raise NotImplementedError


def pairwise(iterable) -> list[tuple]:
    """Return consecutive overlapping pairs from iterable.

    >>> pairwise([1, 2, 3, 4])
    [(1, 2), (2, 3), (3, 4)]
    """
    raise NotImplementedError


def powerset(iterable) -> list[tuple]:
    """Return all subsets of the iterable, from empty set to full set.

    Elements are treated as unique based on position, not value.

    >>> powerset([1, 2])
    [(), (1,), (2,), (1, 2)]
    """
    raise NotImplementedError


def groupby_key(iterable, key) -> dict:
    """Group elements of iterable by the result of key(element).

    Return a dict mapping each key to a list of elements with that key.
    Unlike itertools.groupby, this works on unsorted data.

    >>> groupby_key(["apple", "banana", "avocado", "cherry", "blueberry"], lambda w: w[0])
    {'a': ['apple', 'avocado'], 'b': ['banana', 'blueberry'], 'c': ['cherry']}
    """
    raise NotImplementedError


if __name__ == "__main__":
    # --- take tests ---
    assert take(3, range(10)) == [0, 1, 2]
    assert take(5, [1, 2, 3]) == [1, 2, 3]
    assert take(0, [1, 2, 3]) == []

    # --- pairwise tests ---
    assert pairwise([1, 2, 3, 4]) == [(1, 2), (2, 3), (3, 4)]
    assert pairwise([1]) == []
    assert pairwise([]) == []
    assert pairwise("abcd") == [("a", "b"), ("b", "c"), ("c", "d")]

    # --- powerset tests ---
    assert powerset([1, 2]) == [(), (1,), (2,), (1, 2)]
    assert powerset([]) == [()]
    assert powerset([1, 2, 3]) == [
        (), (1,), (2,), (3,), (1, 2), (1, 3), (2, 3), (1, 2, 3)
    ]

    # --- groupby_key tests ---
    result = groupby_key(
        ["apple", "banana", "avocado", "cherry", "blueberry"], lambda w: w[0]
    )
    assert result == {
        "a": ["apple", "avocado"],
        "b": ["banana", "blueberry"],
        "c": ["cherry"],
    }

    nums = groupby_key([1, 2, 3, 4, 5, 6], lambda x: x % 2)
    assert nums == {1: [1, 3, 5], 0: [2, 4, 6]}

    print("All tests passed!")
