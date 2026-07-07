"""Exercise 01: Lists

Practice list manipulation techniques including rotation, chunking,
interleaving, and deduplication.
"""


def rotate_left(lst: list, k: int) -> list:
    """Rotate a list to the left by k positions.

    Elements that fall off the left end reappear on the right.

    >>> rotate_left([1, 2, 3, 4, 5], 2)
    [3, 4, 5, 1, 2]
    """
    raise NotImplementedError


def chunk(lst: list, size: int) -> list[list]:
    """Split a list into consecutive chunks of the given size.

    The last chunk may be shorter if the list length is not evenly divisible.

    >>> chunk([1, 2, 3, 4, 5], 2)
    [[1, 2], [3, 4], [5]]
    """
    raise NotImplementedError


def interleave(a: list, b: list) -> list:
    """Interleave two lists of equal length element by element.

    >>> interleave([1, 2, 3], [4, 5, 6])
    [1, 4, 2, 5, 3, 6]
    """
    raise NotImplementedError


def remove_duplicates(lst: list) -> list:
    """Remove duplicate elements while preserving the original order.

    Only the first occurrence of each element is kept.

    >>> remove_duplicates([1, 3, 2, 3, 1, 4, 2])
    [1, 3, 2, 4]
    """
    raise NotImplementedError


if __name__ == "__main__":
    # rotate_left
    assert rotate_left([1, 2, 3, 4, 5], 2) == [3, 4, 5, 1, 2]
    assert rotate_left([1, 2, 3], 0) == [1, 2, 3]
    assert rotate_left([1, 2, 3], 3) == [1, 2, 3]
    assert rotate_left([1, 2, 3], 5) == [3, 1, 2]
    assert rotate_left([], 3) == []
    print("rotate_left: all tests passed")

    # chunk
    assert chunk([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]
    assert chunk([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]
    assert chunk([1], 5) == [[1]]
    assert chunk([], 3) == []
    print("chunk: all tests passed")

    # interleave
    assert interleave([1, 2, 3], [4, 5, 6]) == [1, 4, 2, 5, 3, 6]
    assert interleave([], []) == []
    assert interleave(["a"], ["b"]) == ["a", "b"]
    print("interleave: all tests passed")

    # remove_duplicates
    assert remove_duplicates([1, 3, 2, 3, 1, 4, 2]) == [1, 3, 2, 4]
    assert remove_duplicates([]) == []
    assert remove_duplicates([1, 1, 1]) == [1]
    assert remove_duplicates([1, 2, 3]) == [1, 2, 3]
    print("remove_duplicates: all tests passed")

    print("\nAll exercise 01 tests passed!")
