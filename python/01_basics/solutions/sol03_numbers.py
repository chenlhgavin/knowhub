"""Solution 03: Numbers"""


def celsius_to_fahrenheit(c: float) -> float:
    """Convert Celsius to Fahrenheit."""
    return c * 9 / 5 + 32


def is_even(n: int) -> bool:
    """Return True if n is even, False otherwise."""
    return n % 2 == 0


def digit_sum(n: int) -> int:
    """Return the sum of all digits of the absolute value of n."""
    return sum(int(d) for d in str(abs(n)))


def clamp(value: float, low: float, high: float) -> float:
    """Clamp value to the range [low, high]."""
    if value < low:
        return low
    if value > high:
        return high
    return value


if __name__ == "__main__":
    # celsius_to_fahrenheit
    assert celsius_to_fahrenheit(0) == 32.0
    assert celsius_to_fahrenheit(100) == 212.0
    assert celsius_to_fahrenheit(-40) == -40.0
    assert celsius_to_fahrenheit(37) == 98.6

    # is_even
    assert is_even(0) is True
    assert is_even(2) is True
    assert is_even(7) is False
    assert is_even(-4) is True
    assert is_even(-3) is False

    # digit_sum
    assert digit_sum(123) == 6
    assert digit_sum(-456) == 15
    assert digit_sum(0) == 0
    assert digit_sum(9) == 9
    assert digit_sum(1000) == 1

    # clamp
    assert clamp(5, 0, 10) == 5
    assert clamp(-3, 0, 10) == 0
    assert clamp(15, 0, 10) == 10
    assert clamp(0, 0, 10) == 0
    assert clamp(10, 0, 10) == 10

    print("All tests passed!")
