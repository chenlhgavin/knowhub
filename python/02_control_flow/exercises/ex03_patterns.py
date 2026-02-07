"""Exercise 03: Loop Patterns

Practice nested loops, list comprehensions, and common algorithmic patterns.

Implement each function according to its docstring. Run this file to check
your solutions against the built-in assertions.
"""


def flatten(nested: list) -> list:
    """Flatten a 2D list (list of lists) into a 1D list.

    Args:
        nested: A list of lists, e.g. [[1, 2], [3, 4], [5]].

    Returns:
        A single flat list with all elements, e.g. [1, 2, 3, 4, 5].
    """
    raise NotImplementedError("Implement flatten()")


def matrix_transpose(matrix: list[list]) -> list[list]:
    """Transpose a matrix (list of lists).

    Rows become columns and columns become rows.

    Args:
        matrix: A rectangular 2D list (all rows have the same length).

    Returns:
        The transposed matrix.

    Example:
        matrix_transpose([[1, 2, 3], [4, 5, 6]])
        -> [[1, 4], [2, 5], [3, 6]]
    """
    raise NotImplementedError("Implement matrix_transpose()")


def prime_sieve(n: int) -> list[int]:
    """Return all prime numbers up to n (inclusive) using the Sieve of Eratosthenes.

    Algorithm:
        1. Create a boolean list of size n+1, initialized to True.
        2. Mark 0 and 1 as not prime.
        3. For each number i starting from 2, if it is still marked prime,
           mark all its multiples (starting from i*i) as not prime.
        4. Collect all indices still marked as prime.

    Args:
        n: The upper bound (inclusive). Must be >= 0.

    Returns:
        A sorted list of all primes up to n.

    Examples:
        prime_sieve(10) -> [2, 3, 5, 7]
        prime_sieve(1)  -> []
    """
    raise NotImplementedError("Implement prime_sieve()")


def group_by_parity(numbers: list[int]) -> dict[str, list[int]]:
    """Group numbers into even and odd categories.

    Args:
        numbers: A list of integers.

    Returns:
        A dictionary with keys "even" and "odd", each mapping to a list
        of integers from the input. The order within each group must match
        the original order. Both keys must always be present, even if empty.

    Example:
        group_by_parity([1, 2, 3, 4, 5])
        -> {"even": [2, 4], "odd": [1, 3, 5]}
    """
    raise NotImplementedError("Implement group_by_parity()")


if __name__ == "__main__":
    # --- flatten tests ---
    assert flatten([[1, 2], [3, 4], [5]]) == [1, 2, 3, 4, 5]
    assert flatten([]) == []
    assert flatten([[], [], []]) == []
    assert flatten([[1]]) == [1]
    assert flatten([[1, 2, 3]]) == [1, 2, 3]
    print("flatten: all tests passed")

    # --- matrix_transpose tests ---
    assert matrix_transpose([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]]
    assert matrix_transpose([[1]]) == [[1]]
    assert matrix_transpose([[1, 2], [3, 4], [5, 6]]) == [[1, 3, 5], [2, 4, 6]]
    assert matrix_transpose([[1, 2, 3]]) == [[1], [2], [3]]
    print("matrix_transpose: all tests passed")

    # --- prime_sieve tests ---
    assert prime_sieve(10) == [2, 3, 5, 7]
    assert prime_sieve(1) == []
    assert prime_sieve(0) == []
    assert prime_sieve(2) == [2]
    assert prime_sieve(20) == [2, 3, 5, 7, 11, 13, 17, 19]
    assert prime_sieve(30) == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    print("prime_sieve: all tests passed")

    # --- group_by_parity tests ---
    assert group_by_parity([1, 2, 3, 4, 5]) == {"even": [2, 4], "odd": [1, 3, 5]}
    assert group_by_parity([]) == {"even": [], "odd": []}
    assert group_by_parity([2, 4, 6]) == {"even": [2, 4, 6], "odd": []}
    assert group_by_parity([1, 3, 5]) == {"even": [], "odd": [1, 3, 5]}
    assert group_by_parity([0]) == {"even": [0], "odd": []}
    print("group_by_parity: all tests passed")

    print("\nAll exercise 03 tests passed!")
