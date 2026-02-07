"""Solution 02: Tuples

Complete implementations of tuple exercises.
"""


def min_max(lst: list[int]) -> tuple[int, int]:
    """Return the (minimum, maximum) of a list of integers.

    Do NOT use the built-in min() or max() functions.

    >>> min_max([3, 1, 4, 1, 5, 9])
    (1, 9)
    """
    lo = lst[0]
    hi = lst[0]
    for x in lst[1:]:
        if x < lo:
            lo = x
        if x > hi:
            hi = x
    return (lo, hi)


def unpack_pairs(pairs: list[tuple]) -> tuple[list, list]:
    """Unzip a list of pairs into two separate lists.

    >>> unpack_pairs([(1, 'a'), (2, 'b'), (3, 'c')])
    ([1, 2, 3], ['a', 'b', 'c'])
    """
    if not pairs:
        return ([], [])
    firsts = []
    seconds = []
    for a, b in pairs:
        firsts.append(a)
        seconds.append(b)
    return (firsts, seconds)


def running_average(numbers: list[float]) -> list[tuple[int, float]]:
    """Compute the running average at each position.

    Return a list of (index, average_so_far) tuples using enumerate.
    The average at index i is the mean of numbers[0] through numbers[i].

    >>> running_average([10, 20, 30])
    [(0, 10.0), (1, 15.0), (2, 20.0)]
    """
    result = []
    total = 0.0
    for i, num in enumerate(numbers):
        total += num
        result.append((i, total / (i + 1)))
    return result


if __name__ == "__main__":
    # min_max
    assert min_max([3, 1, 4, 1, 5, 9]) == (1, 9)
    assert min_max([42]) == (42, 42)
    assert min_max([-5, -1, -10]) == (-10, -1)
    assert min_max([0, 0, 0]) == (0, 0)
    print("min_max: all tests passed")

    # unpack_pairs
    assert unpack_pairs([(1, "a"), (2, "b"), (3, "c")]) == ([1, 2, 3], ["a", "b", "c"])
    assert unpack_pairs([]) == ([], [])
    assert unpack_pairs([(10, 20)]) == ([10], [20])
    print("unpack_pairs: all tests passed")

    # running_average
    assert running_average([10, 20, 30]) == [(0, 10.0), (1, 15.0), (2, 20.0)]
    assert running_average([5]) == [(0, 5.0)]
    assert running_average([1, 3]) == [(0, 1.0), (1, 2.0)]
    print("running_average: all tests passed")

    print("\nAll exercise 02 tests passed!")
