"""Solution 03: Loop Patterns"""


def flatten(nested: list) -> list:
    """Flatten a 2D list into a 1D list."""
    result = []
    for sublist in nested:
        for item in sublist:
            result.append(item)
    return result


def matrix_transpose(matrix: list[list]) -> list[list]:
    """Transpose a matrix."""
    if not matrix:
        return []
    rows = len(matrix)
    cols = len(matrix[0])
    return [[matrix[r][c] for r in range(rows)] for c in range(cols)]


def prime_sieve(n: int) -> list[int]:
    """Return all primes up to n using the Sieve of Eratosthenes."""
    if n < 2:
        return []

    is_prime = [True] * (n + 1)
    is_prime[0] = False
    is_prime[1] = False

    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for multiple in range(i * i, n + 1, i):
                is_prime[multiple] = False

    return [i for i in range(n + 1) if is_prime[i]]


def group_by_parity(numbers: list[int]) -> dict[str, list[int]]:
    """Group numbers into even and odd categories."""
    result: dict[str, list[int]] = {"even": [], "odd": []}
    for num in numbers:
        if num % 2 == 0:
            result["even"].append(num)
        else:
            result["odd"].append(num)
    return result


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
