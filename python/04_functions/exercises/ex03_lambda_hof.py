"""Exercise 03 — Lambda Expressions and Higher-Order Functions

Topics: lambda, function composition, reimplementing map() and filter().

Implement the four functions below. Run this file to check your solutions.
"""

from typing import Callable


def sort_by_last(words: list[str]) -> list[str]:
    """Return a new list of *words* sorted by their last character.

    Ties are broken by the default (stable) sort order.

    >>> sort_by_last(["hello", "world", "apple"])
    ['world', 'apple', 'hello']
    """
    raise NotImplementedError


def compose(f: Callable, g: Callable) -> Callable:
    """Return a new function that computes ``f(g(x))``.

    >>> double = lambda x: x * 2
    >>> inc = lambda x: x + 1
    >>> double_then_inc = compose(inc, double)  # inc(double(x))
    >>> double_then_inc(3)
    7
    """
    raise NotImplementedError


def my_map(func: Callable, iterable: list) -> list:
    """Reimplement ``map()`` — apply *func* to every element and return a list.

    >>> my_map(str.upper, ["hello", "world"])
    ['HELLO', 'WORLD']
    """
    raise NotImplementedError


def my_filter(func: Callable, iterable: list) -> list:
    """Reimplement ``filter()`` — return a list of elements for which *func*
    returns a truthy value.

    >>> my_filter(lambda x: x > 0, [-2, -1, 0, 1, 2])
    [1, 2]
    """
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # sort_by_last
    assert sort_by_last(["hello", "world", "apple"]) == ["world", "apple", "hello"]
    assert sort_by_last(["abc", "xyz", "mno"]) == ["abc", "mno", "xyz"]
    assert sort_by_last([]) == []
    assert sort_by_last(["a"]) == ["a"]

    # compose
    double = lambda x: x * 2
    inc = lambda x: x + 1
    double_then_inc = compose(inc, double)
    assert double_then_inc(3) == 7   # inc(double(3)) = inc(6) = 7
    assert double_then_inc(0) == 1   # inc(double(0)) = inc(0) = 1

    inc_then_double = compose(double, inc)
    assert inc_then_double(3) == 8   # double(inc(3)) = double(4) = 8

    to_upper_list = compose(list, str.upper)
    assert to_upper_list("hi") == ["H", "I"]

    # my_map
    assert my_map(str.upper, ["hello", "world"]) == ["HELLO", "WORLD"]
    assert my_map(lambda x: x ** 2, [1, 2, 3]) == [1, 4, 9]
    assert my_map(abs, [-1, -2, 3]) == [1, 2, 3]
    assert my_map(str, []) == []

    # my_filter
    assert my_filter(lambda x: x > 0, [-2, -1, 0, 1, 2]) == [1, 2]
    assert my_filter(lambda s: len(s) > 3, ["hi", "hello", "hey", "world"]) == [
        "hello",
        "world",
    ]
    assert my_filter(lambda x: x, [0, 1, "", "a", None, True]) == [1, "a", True]
    assert my_filter(lambda x: True, []) == []

    print("All tests passed!")
