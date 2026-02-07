"""Exercise 02: Loops

Practice using for loops, while loops, range(), break, and continue.

Implement each function according to its docstring. Run this file to check
your solutions against the built-in assertions.
"""


def sum_range(start: int, end: int) -> int:
    """Return the sum of all integers from start to end, inclusive.

    Args:
        start: The starting integer.
        end: The ending integer (included in the sum).

    Returns:
        The sum of integers in [start, end].

    Examples:
        sum_range(1, 5) -> 15   (1 + 2 + 3 + 4 + 5)
        sum_range(3, 3) -> 3
    """
    raise NotImplementedError("Implement sum_range()")


def factorial(n: int) -> int:
    """Compute n! (n factorial) using a loop.

    Args:
        n: A non-negative integer.

    Returns:
        n! (0! is defined as 1).

    Examples:
        factorial(0) -> 1
        factorial(5) -> 120
    """
    raise NotImplementedError("Implement factorial()")


def reverse_list(lst: list) -> list:
    """Return a new list with elements in reverse order.

    Do NOT use reversed(), [::-1], or list.reverse().

    Args:
        lst: The input list.

    Returns:
        A new list containing the same elements in reverse order.
    """
    raise NotImplementedError("Implement reverse_list()")


def find_index(lst: list, target) -> int:
    """Return the index of the first occurrence of target in lst.

    Do NOT use list.index().

    Args:
        lst: The list to search.
        target: The value to find.

    Returns:
        The index of the first occurrence, or -1 if not found.
    """
    raise NotImplementedError("Implement find_index()")


if __name__ == "__main__":
    # --- sum_range tests ---
    assert sum_range(1, 5) == 15
    assert sum_range(1, 1) == 1
    assert sum_range(3, 3) == 3
    assert sum_range(1, 10) == 55
    assert sum_range(0, 0) == 0
    assert sum_range(-3, 3) == 0
    print("sum_range: all tests passed")

    # --- factorial tests ---
    assert factorial(0) == 1
    assert factorial(1) == 1
    assert factorial(5) == 120
    assert factorial(10) == 3628800
    assert factorial(3) == 6
    print("factorial: all tests passed")

    # --- reverse_list tests ---
    assert reverse_list([1, 2, 3]) == [3, 2, 1]
    assert reverse_list([]) == []
    assert reverse_list([42]) == [42]
    assert reverse_list(["a", "b", "c", "d"]) == ["d", "c", "b", "a"]
    original = [1, 2, 3]
    reversed_copy = reverse_list(original)
    assert original == [1, 2, 3], "original list must not be modified"
    print("reverse_list: all tests passed")

    # --- find_index tests ---
    assert find_index([10, 20, 30, 40], 30) == 2
    assert find_index([10, 20, 30, 40], 99) == -1
    assert find_index([], 1) == -1
    assert find_index(["a", "b", "c"], "a") == 0
    assert find_index([1, 2, 3, 2, 1], 2) == 1
    print("find_index: all tests passed")

    print("\nAll exercise 02 tests passed!")
