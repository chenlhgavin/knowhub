"""Exercise 01: Conditionals

Practice using if/elif/else statements and ternary expressions.

Implement each function according to its docstring. Run this file to check
your solutions against the built-in assertions.
"""


def grade(score: int) -> str:
    """Return a letter grade based on a numeric score.

    Grading scale:
        90-100 -> "A"
        80-89  -> "B"
        70-79  -> "C"
        60-69  -> "D"
        0-59   -> "F"

    Args:
        score: An integer between 0 and 100 inclusive.

    Returns:
        A single-character string: "A", "B", "C", "D", or "F".
    """
    raise NotImplementedError("Implement grade()")


def fizzbuzz(n: int) -> str:
    """Return the FizzBuzz result for a single number.

    Rules:
        - Divisible by both 3 and 5 -> "FizzBuzz"
        - Divisible by 3 only       -> "Fizz"
        - Divisible by 5 only       -> "Buzz"
        - Otherwise                 -> the number as a string

    Args:
        n: A positive integer.

    Returns:
        "Fizz", "Buzz", "FizzBuzz", or str(n).
    """
    raise NotImplementedError("Implement fizzbuzz()")


def sign(n: float) -> int:
    """Return the sign of a number.

    Args:
        n: Any numeric value.

    Returns:
        1 if n is positive, -1 if n is negative, 0 if n is zero.
    """
    raise NotImplementedError("Implement sign()")


def absolute_value(n: float) -> float:
    """Return the absolute value of n without using the built-in abs().

    Args:
        n: Any numeric value.

    Returns:
        The absolute value of n.
    """
    raise NotImplementedError("Implement absolute_value()")


if __name__ == "__main__":
    # --- grade tests ---
    assert grade(95) == "A"
    assert grade(90) == "A"
    assert grade(85) == "B"
    assert grade(80) == "B"
    assert grade(75) == "C"
    assert grade(70) == "C"
    assert grade(65) == "D"
    assert grade(60) == "D"
    assert grade(55) == "F"
    assert grade(0) == "F"
    assert grade(100) == "A"
    print("grade: all tests passed")

    # --- fizzbuzz tests ---
    assert fizzbuzz(1) == "1"
    assert fizzbuzz(3) == "Fizz"
    assert fizzbuzz(5) == "Buzz"
    assert fizzbuzz(15) == "FizzBuzz"
    assert fizzbuzz(30) == "FizzBuzz"
    assert fizzbuzz(7) == "7"
    assert fizzbuzz(9) == "Fizz"
    assert fizzbuzz(10) == "Buzz"
    print("fizzbuzz: all tests passed")

    # --- sign tests ---
    assert sign(42) == 1
    assert sign(-7) == -1
    assert sign(0) == 0
    assert sign(0.001) == 1
    assert sign(-0.001) == -1
    print("sign: all tests passed")

    # --- absolute_value tests ---
    assert absolute_value(5) == 5
    assert absolute_value(-5) == 5
    assert absolute_value(0) == 0
    assert absolute_value(-3.14) == 3.14
    assert absolute_value(3.14) == 3.14
    print("absolute_value: all tests passed")

    print("\nAll exercise 01 tests passed!")
