"""Solution 01: Variables and Assignment"""


def swap(a, b) -> tuple:
    """Return a tuple with a and b swapped."""
    return (b, a)


def type_name(x) -> str:
    """Return the name of x's type as a string."""
    return type(x).__name__


def is_same_object(a, b) -> bool:
    """Return True if a and b refer to the exact same object (identity check)."""
    return a is b


def multi_assign() -> tuple:
    """Assign the values 10, 20, 30 to three variables in one statement
    and return them as a tuple."""
    a, b, c = 10, 20, 30
    return (a, b, c)


if __name__ == "__main__":
    # swap
    assert swap(1, 2) == (2, 1), "swap(1, 2) should return (2, 1)"
    assert swap("a", "b") == ("b", "a"), "swap('a', 'b') should return ('b', 'a')"
    assert swap(None, 42) == (42, None), "swap(None, 42) should return (42, None)"

    # type_name
    assert type_name(42) == "int"
    assert type_name(3.14) == "float"
    assert type_name("hi") == "str"
    assert type_name(True) == "bool"
    assert type_name([]) == "list"
    assert type_name({}) == "dict"
    assert type_name(None) == "NoneType"

    # is_same_object
    x = [1, 2, 3]
    y = x
    z = [1, 2, 3]
    assert is_same_object(x, y) is True, "x and y point to the same list"
    assert is_same_object(x, z) is False, "x and z are equal but not identical"
    assert is_same_object(1, 1) is True, "small ints are cached singletons"

    # multi_assign
    result = multi_assign()
    assert result == (10, 20, 30), "multi_assign() should return (10, 20, 30)"
    assert isinstance(result, tuple), "multi_assign() must return a tuple"

    print("All tests passed!")
