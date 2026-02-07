"""Exercise 04: Operators

Practice Python operators:
- Safe division with zero-check
- Comparison operators and chaining for range checks
- Logical operators to implement XOR
- Variadic functions with *args and the all() pattern
"""


def safe_divide(a: float, b: float) -> float:
    """Divide a by b. Return 0.0 if b is zero.

    >>> safe_divide(10, 3)
    3.3333333333333335
    >>> safe_divide(10, 0)
    0.0
    """
    if b == 0:
        return 0.0
    return a / b


def is_between(x: float, low: float, high: float) -> bool:
    """Return True if x is in the inclusive range [low, high].

    >>> is_between(5, 1, 10)
    True
    >>> is_between(0, 1, 10)
    False
    >>> is_between(10, 1, 10)
    True
    """
    return low <= x <= high


def xor(a, b) -> bool:
    """Return the logical XOR of a and b.

    XOR is True when exactly one operand is truthy.

    >>> xor(True, False)
    True
    >>> xor(True, True)
    False
    >>> xor(False, False)
    False
    """
    return bool(a) != bool(b)


def all_positive(*args: float) -> bool:
    """Return True if all arguments are positive (> 0).

    Return True for no arguments (vacuous truth).

    >>> all_positive(1, 2, 3)
    True
    >>> all_positive(1, -2, 3)
    False
    >>> all_positive()
    True
    """
    return all(x > 0 for x in args)


if __name__ == "__main__":
    # safe_divide
    assert safe_divide(10, 2) == 5.0
    assert safe_divide(10, 0) == 0.0
    assert safe_divide(0, 5) == 0.0
    assert safe_divide(-10, 2) == -5.0
    assert isinstance(safe_divide(10, 3), float)

    # is_between
    assert is_between(5, 1, 10) is True
    assert is_between(0, 1, 10) is False
    assert is_between(1, 1, 10) is True
    assert is_between(10, 1, 10) is True
    assert is_between(11, 1, 10) is False

    # xor
    assert xor(True, False) is True
    assert xor(False, True) is True
    assert xor(True, True) is False
    assert xor(False, False) is False
    assert xor(1, 0) is True
    assert xor(0, 0) is False

    # all_positive
    assert all_positive(1, 2, 3) is True
    assert all_positive(1, -2, 3) is False
    assert all_positive() is True
    assert all_positive(0) is False
    assert all_positive(0.1) is True

    print("All tests passed!")
