"""Solution 01: Conditionals"""


def grade(score: int) -> str:
    """Return a letter grade based on a numeric score."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def fizzbuzz(n: int) -> str:
    """Return the FizzBuzz result for a single number."""
    if n % 15 == 0:
        return "FizzBuzz"
    elif n % 3 == 0:
        return "Fizz"
    elif n % 5 == 0:
        return "Buzz"
    else:
        return str(n)


def sign(n: float) -> int:
    """Return the sign of a number."""
    if n > 0:
        return 1
    elif n < 0:
        return -1
    else:
        return 0


def absolute_value(n: float) -> float:
    """Return the absolute value of n without using abs()."""
    return n if n >= 0 else -n


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
