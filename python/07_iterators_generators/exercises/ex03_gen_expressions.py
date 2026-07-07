"""Exercise 03: Generator Expressions and Pipelines

Implement these functions using generator expressions and generators:

1. sum_of_squares(n) - sum of squares from 1 to n using a generator expression.
2. first_match(predicate, iterable) - first element matching predicate, or None.
3. nested_flatten(data) - recursively flatten arbitrarily nested lists.
4. gen_pipeline(data) - multi-step processing pipeline.
"""


def sum_of_squares(n: int) -> int:
    """Return the sum of squares from 1 to n (inclusive) using a generator expression.

    >>> sum_of_squares(5)
    55
    """
    raise NotImplementedError


def first_match(predicate, iterable):
    """Return the first element in iterable for which predicate returns True.

    Return None if no element matches. Use next() with a generator expression.

    >>> first_match(lambda x: x > 3, [1, 2, 3, 4, 5])
    4
    """
    raise NotImplementedError


def nested_flatten(data) -> list:
    """Recursively flatten arbitrarily nested lists.

    Use a generator internally and return a list.

    >>> nested_flatten([1, [2, [3, 4], 5], 6])
    [1, 2, 3, 4, 5, 6]
    """
    raise NotImplementedError


def gen_pipeline(data: list[str]) -> list[int]:
    """Process a list of strings through a multi-step pipeline:

    1. Filter out empty strings.
    2. Strip whitespace from each string.
    3. Convert to int.
    4. Keep only positive values.
    5. Return a sorted list.

    Use generator expressions for each intermediate step.

    >>> gen_pipeline(["  3 ", "", "-1", " 5", "0", "  2"])
    [2, 3, 5]
    """
    raise NotImplementedError


if __name__ == "__main__":
    # --- sum_of_squares tests ---
    assert sum_of_squares(1) == 1
    assert sum_of_squares(5) == 55       # 1 + 4 + 9 + 16 + 25
    assert sum_of_squares(10) == 385

    # --- first_match tests ---
    assert first_match(lambda x: x > 3, [1, 2, 3, 4, 5]) == 4
    assert first_match(lambda x: x > 10, [1, 2, 3]) is None
    assert first_match(lambda s: s.startswith("b"), ["apple", "banana", "cherry"]) == "banana"

    # --- nested_flatten tests ---
    assert nested_flatten([1, [2, [3, 4], 5], 6]) == [1, 2, 3, 4, 5, 6]
    assert nested_flatten([]) == []
    assert nested_flatten([1, 2, 3]) == [1, 2, 3]
    assert nested_flatten([[[[1]]]]) == [1]
    assert nested_flatten([1, [2], [[3]], [[[4]]]]) == [1, 2, 3, 4]

    # --- gen_pipeline tests ---
    assert gen_pipeline(["  3 ", "", "-1", " 5", "0", "  2"]) == [2, 3, 5]
    assert gen_pipeline(["", "  ", "-5", "-3"]) == []
    assert gen_pipeline(["10", "1", "  7  "]) == [1, 7, 10]

    print("All tests passed!")
