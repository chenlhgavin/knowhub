"""Solution 04: itertools Practice

Implementations of take, pairwise, powerset, and groupby_key using itertools.
"""

import itertools


def take(n: int, iterable) -> list:
    """Return the first n elements of iterable as a list.

    >>> take(3, range(10))
    [0, 1, 2]
    """
    return list(itertools.islice(iterable, n))


def pairwise(iterable) -> list[tuple]:
    """Return consecutive overlapping pairs from iterable.

    >>> pairwise([1, 2, 3, 4])
    [(1, 2), (2, 3), (3, 4)]
    """
    a, b = itertools.tee(iterable)
    next(b, None)
    return list(zip(a, b))


def powerset(iterable) -> list[tuple]:
    """Return all subsets of the iterable, from empty set to full set.

    Elements are treated as unique based on position, not value.

    >>> powerset([1, 2])
    [(), (1,), (2,), (1, 2)]
    """
    items = list(iterable)
    return list(
        itertools.chain.from_iterable(
            itertools.combinations(items, r) for r in range(len(items) + 1)
        )
    )


def groupby_key(iterable, key) -> dict:
    """Group elements of iterable by the result of key(element).

    Return a dict mapping each key to a list of elements with that key.
    Unlike itertools.groupby, this works on unsorted data.

    >>> groupby_key(["apple", "banana", "avocado", "cherry", "blueberry"], lambda w: w[0])
    {'a': ['apple', 'avocado'], 'b': ['banana', 'blueberry'], 'c': ['cherry']}
    """
    result = {}
    for item in iterable:
        k = key(item)
        if k not in result:
            result[k] = []
        result[k].append(item)
    return result


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
