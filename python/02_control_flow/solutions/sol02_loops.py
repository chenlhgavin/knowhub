"""Solution 02: Loops"""


def sum_range(start: int, end: int) -> int:
    """Return the sum of all integers from start to end, inclusive."""
    total = 0
    for i in range(start, end + 1):
        total += i
    return total


def factorial(n: int) -> int:
    """Compute n! using a loop."""
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def reverse_list(lst: list) -> list:
    """Return a new list with elements in reverse order."""
    result = []
    for i in range(len(lst) - 1, -1, -1):
        result.append(lst[i])
    return result


def find_index(lst: list, target) -> int:
    """Return the index of the first occurrence of target, or -1."""
    for i, value in enumerate(lst):
        if value == target:
            return i
    return -1


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
