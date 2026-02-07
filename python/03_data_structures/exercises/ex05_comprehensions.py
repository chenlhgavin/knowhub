"""Exercise 05: Comprehensions

Practice list, dict, and set comprehensions, including nested comprehensions.
"""


def squares_of_evens(numbers: list[int]) -> list[int]:
    """Return the squares of all even numbers, preserving order.

    Use a list comprehension.

    >>> squares_of_evens([1, 2, 3, 4, 5, 6])
    [4, 16, 36]
    """
    raise NotImplementedError


def flatten_2d(matrix: list[list]) -> list:
    """Flatten a 2D list into a 1D list using a list comprehension.

    >>> flatten_2d([[1, 2], [3, 4], [5]])
    [1, 2, 3, 4, 5]
    """
    raise NotImplementedError


def char_count(s: str) -> dict[str, int]:
    """Count the frequency of each character using a dict comprehension.

    >>> char_count("abba")
    {'a': 2, 'b': 2}
    """
    raise NotImplementedError


def pythagorean_triples(n: int) -> list[tuple[int, int, int]]:
    """Find all Pythagorean triples (a, b, c) where 1 <= a < b < c <= n.

    A Pythagorean triple satisfies a**2 + b**2 == c**2.
    Use a list comprehension.

    >>> pythagorean_triples(15)
    [(3, 4, 5), (5, 12, 13), (6, 8, 10), (9, 12, 15)]
    """
    raise NotImplementedError


if __name__ == "__main__":
    # squares_of_evens
    assert squares_of_evens([1, 2, 3, 4, 5, 6]) == [4, 16, 36]
    assert squares_of_evens([1, 3, 5]) == []
    assert squares_of_evens([]) == []
    assert squares_of_evens([0, 2]) == [0, 4]
    print("squares_of_evens: all tests passed")

    # flatten_2d
    assert flatten_2d([[1, 2], [3, 4], [5]]) == [1, 2, 3, 4, 5]
    assert flatten_2d([]) == []
    assert flatten_2d([[], [1]]) == [1]
    assert flatten_2d([[1]]) == [1]
    print("flatten_2d: all tests passed")

    # char_count
    assert char_count("abba") == {"a": 2, "b": 2}
    assert char_count("") == {}
    assert char_count("aaa") == {"a": 3}
    assert char_count("abc") == {"a": 1, "b": 1, "c": 1}
    print("char_count: all tests passed")

    # pythagorean_triples
    assert pythagorean_triples(15) == [(3, 4, 5), (5, 12, 13), (6, 8, 10), (9, 12, 15)]
    assert pythagorean_triples(5) == [(3, 4, 5)]
    assert pythagorean_triples(4) == []
    print("pythagorean_triples: all tests passed")

    print("\nAll exercise 05 tests passed!")
