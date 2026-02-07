"""Exercise 04: Sets

Practice set creation, membership testing, and set-theoretic operations.
"""


def unique_chars(s: str) -> set[str]:
    """Return the set of unique characters in the string.

    >>> unique_chars("banana")
    {'b', 'a', 'n'}
    """
    raise NotImplementedError


def common_elements(a: list, b: list) -> list:
    """Return the sorted list of elements present in both a and b.

    >>> common_elements([1, 2, 3, 4], [3, 4, 5, 6])
    [3, 4]
    """
    raise NotImplementedError


def is_subset(a: list, b: list) -> bool:
    """Check if every element of a is also in b.

    >>> is_subset([1, 2], [1, 2, 3, 4])
    True
    >>> is_subset([1, 5], [1, 2, 3])
    False
    """
    raise NotImplementedError


def symmetric_diff(a: list, b: list) -> list:
    """Return the sorted symmetric difference of a and b.

    The symmetric difference contains elements in either a or b but not both.

    >>> symmetric_diff([1, 2, 3], [2, 3, 4])
    [1, 4]
    """
    raise NotImplementedError


if __name__ == "__main__":
    # unique_chars
    assert unique_chars("banana") == {"b", "a", "n"}
    assert unique_chars("") == set()
    assert unique_chars("aaa") == {"a"}
    assert unique_chars("abc") == {"a", "b", "c"}
    print("unique_chars: all tests passed")

    # common_elements
    assert common_elements([1, 2, 3, 4], [3, 4, 5, 6]) == [3, 4]
    assert common_elements([1, 2], [3, 4]) == []
    assert common_elements([], [1, 2]) == []
    assert common_elements([1, 1, 2], [1, 1, 3]) == [1]
    print("common_elements: all tests passed")

    # is_subset
    assert is_subset([1, 2], [1, 2, 3, 4]) is True
    assert is_subset([1, 5], [1, 2, 3]) is False
    assert is_subset([], [1, 2, 3]) is True
    assert is_subset([1], [1]) is True
    print("is_subset: all tests passed")

    # symmetric_diff
    assert symmetric_diff([1, 2, 3], [2, 3, 4]) == [1, 4]
    assert symmetric_diff([1, 2], [1, 2]) == []
    assert symmetric_diff([], [1, 2]) == [1, 2]
    assert symmetric_diff([1, 2, 3], []) == [1, 2, 3]
    print("symmetric_diff: all tests passed")

    print("\nAll exercise 04 tests passed!")
