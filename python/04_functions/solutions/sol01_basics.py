"""Solution 01 — Function Basics

Complete implementations for ex01_basics.py.
"""

from typing import Callable


def power(base: float, exp: int = 2) -> float:
    """Raise *base* to *exp*.  Defaults to squaring when *exp* is omitted."""
    return base ** exp


def multi_return(s: str) -> tuple[int, int, int]:
    """Return a 3-tuple: (length, vowel_count, consonant_count)."""
    vowels = set("aeiouAEIOU")
    length = len(s)
    vowel_count = sum(1 for ch in s if ch in vowels)
    consonant_count = sum(1 for ch in s if ch.isalpha() and ch not in vowels)
    return length, vowel_count, consonant_count


def apply_all(value, *funcs):
    """Apply each function in *funcs* to *value* in sequence."""
    for func in funcs:
        value = func(value)
    return value


def make_greeting(greeting: str = "Hello") -> Callable[[str], str]:
    """Return a function that takes a *name* and returns ``f"{greeting}, {name}!"``."""
    def greet(name: str) -> str:
        return f"{greeting}, {name}!"
    return greet


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # power
    assert power(3) == 9
    assert power(2, 10) == 1024
    assert power(5, 0) == 1
    assert power(7, 1) == 7

    # multi_return
    assert multi_return("Hello!") == (6, 2, 3)
    assert multi_return("") == (0, 0, 0)
    assert multi_return("aeiou") == (5, 5, 0)
    assert multi_return("bcdfg") == (5, 0, 5)
    assert multi_return("123") == (3, 0, 0)

    # apply_all
    assert apply_all(5, str, list) == ["5"]
    assert apply_all(-3, abs, str) == "3"
    assert apply_all("hello", str.upper, list) == ["H", "E", "L", "L", "O"]
    assert apply_all(42) == 42

    # make_greeting
    hi = make_greeting()
    assert hi("Alice") == "Hello, Alice!"
    bye = make_greeting("Goodbye")
    assert bye("Bob") == "Goodbye, Bob!"

    print("All tests passed!")
