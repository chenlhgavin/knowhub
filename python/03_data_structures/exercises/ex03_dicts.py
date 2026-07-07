"""Exercise 03: Dictionaries

Practice dictionary creation, manipulation, and common patterns like
inversion, merging, frequency counting, and grouping.
"""


def invert_dict(d: dict) -> dict:
    """Swap keys and values in a dictionary.

    Assumes all values are unique and hashable.

    >>> invert_dict({'a': 1, 'b': 2})
    {1: 'a', 2: 'b'}
    """
    raise NotImplementedError


def merge_dicts(*dicts: dict) -> dict:
    """Merge multiple dictionaries into one.

    If the same key appears in more than one dict, the value from the
    later (rightmost) dict wins.

    >>> merge_dicts({'a': 1}, {'b': 2}, {'a': 3, 'c': 4})
    {'a': 3, 'b': 2, 'c': 4}
    """
    raise NotImplementedError


def word_frequency(text: str) -> dict[str, int]:
    """Count the frequency of each word in the text.

    Words are lowercased and split on whitespace.

    >>> word_frequency("the cat and the dog")
    {'the': 2, 'cat': 1, 'and': 1, 'dog': 1}
    """
    raise NotImplementedError


def group_by_length(words: list[str]) -> dict[int, list[str]]:
    """Group words by their length.

    >>> group_by_length(['hi', 'hey', 'go', 'wow'])
    {2: ['hi', 'go'], 3: ['hey', 'wow']}
    """
    raise NotImplementedError


if __name__ == "__main__":
    # invert_dict
    assert invert_dict({"a": 1, "b": 2}) == {1: "a", 2: "b"}
    assert invert_dict({}) == {}
    assert invert_dict({"x": "y"}) == {"y": "x"}
    print("invert_dict: all tests passed")

    # merge_dicts
    assert merge_dicts({"a": 1}, {"b": 2}, {"a": 3, "c": 4}) == {
        "a": 3,
        "b": 2,
        "c": 4,
    }
    assert merge_dicts() == {}
    assert merge_dicts({"x": 1}) == {"x": 1}
    print("merge_dicts: all tests passed")

    # word_frequency
    assert word_frequency("the cat and the dog") == {
        "the": 2,
        "cat": 1,
        "and": 1,
        "dog": 1,
    }
    assert word_frequency("") == {}
    assert word_frequency("hello") == {"hello": 1}
    assert word_frequency("A a A") == {"a": 3}
    print("word_frequency: all tests passed")

    # group_by_length
    assert group_by_length(["hi", "hey", "go", "wow"]) == {
        2: ["hi", "go"],
        3: ["hey", "wow"],
    }
    assert group_by_length([]) == {}
    assert group_by_length(["a", "bb", "c"]) == {1: ["a", "c"], 2: ["bb"]}
    print("group_by_length: all tests passed")

    print("\nAll exercise 03 tests passed!")
