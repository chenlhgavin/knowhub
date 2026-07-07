"""Exercise 02 — *args and **kwargs

Topics: variadic positional arguments, variadic keyword arguments, unpacking.

Implement the four functions below. Run this file to check your solutions.
"""


def concat(*args: str, sep: str = " ") -> str:
    """Join all positional string arguments using *sep*.

    >>> concat("Hello", "World")
    'Hello World'
    >>> concat("a", "b", "c", sep="-")
    'a-b-c'
    """
    raise NotImplementedError


def pick(d: dict, *keys: str) -> dict:
    """Return a new dict containing only the *keys* that exist in *d*.

    Keys that are not present in *d* are silently ignored.

    >>> pick({"a": 1, "b": 2, "c": 3}, "a", "c")
    {'a': 1, 'c': 3}
    """
    raise NotImplementedError


def defaults(d: dict, **kwargs) -> dict:
    """Return a new dict that merges *kwargs* as default values into *d*.

    Existing keys in *d* are **not** overwritten.

    >>> defaults({"a": 1}, a=99, b=2)
    {'a': 1, 'b': 2}
    """
    raise NotImplementedError


def call_with(func, *args, **kwargs):
    """Call *func* with the provided positional and keyword arguments and
    return the result.

    >>> call_with(pow, 2, 10)
    1024
    >>> call_with(sorted, [3, 1, 2], reverse=True)
    [3, 2, 1]
    """
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # concat
    assert concat("Hello", "World") == "Hello World"
    assert concat("a", "b", "c", sep="-") == "a-b-c"
    assert concat("only") == "only"
    assert concat() == ""
    assert concat("x", "y", sep="") == "xy"

    # pick
    assert pick({"a": 1, "b": 2, "c": 3}, "a", "c") == {"a": 1, "c": 3}
    assert pick({"a": 1}, "b") == {}
    assert pick({"a": 1, "b": 2}, "a", "b", "z") == {"a": 1, "b": 2}
    assert pick({}, "a") == {}

    # defaults
    assert defaults({"a": 1}, a=99, b=2) == {"a": 1, "b": 2}
    assert defaults({}, x=1, y=2) == {"x": 1, "y": 2}
    assert defaults({"k": "v"}) == {"k": "v"}
    original = {"a": 1}
    result = defaults(original, b=2)
    assert original == {"a": 1}, "must not mutate the input dict"

    # call_with
    assert call_with(pow, 2, 10) == 1024
    assert call_with(sorted, [3, 1, 2], reverse=True) == [3, 2, 1]
    assert call_with(max, 1, 2, 3) == 3
    assert call_with(lambda: 42) == 42

    print("All tests passed!")
