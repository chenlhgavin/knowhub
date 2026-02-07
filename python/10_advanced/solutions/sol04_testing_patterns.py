"""
Solution 04: Testing Patterns

Implements:
- calculate_statistics: mean, median, and population standard deviation
- parse_email: email validation and splitting
- RateLimiter: time-window-based rate limiting
"""

import math
import time


def calculate_statistics(numbers: list[float]) -> dict[str, float]:
    """Calculate mean, median, and standard deviation of a list of numbers.

    Returns a dict with keys "mean", "median", "std_dev".

    The standard deviation is the population standard deviation:
        std_dev = sqrt(sum((x - mean)^2 for x in numbers) / len(numbers))

    Raises:
        ValueError: If numbers is empty.

    Args:
        numbers: A non-empty list of floats/ints.

    Returns:
        Dict with "mean", "median", "std_dev" (all floats).
    """
    if not numbers:
        raise ValueError("Cannot calculate statistics of an empty list")

    n = len(numbers)

    # Mean
    mean = sum(numbers) / n

    # Median
    sorted_nums = sorted(numbers)
    mid = n // 2
    if n % 2 == 0:
        median = (sorted_nums[mid - 1] + sorted_nums[mid]) / 2
    else:
        median = sorted_nums[mid]

    # Population standard deviation
    variance = sum((x - mean) ** 2 for x in numbers) / n
    std_dev = math.sqrt(variance)

    return {
        "mean": float(mean),
        "median": float(median),
        "std_dev": float(std_dev),
    }


def parse_email(email: str) -> tuple[str, str]:
    """Parse an email address into (local_part, domain).

    Validation rules:
    - Must contain exactly one '@' character.
    - Both the local part and domain must be non-empty.

    Raises:
        ValueError: If the email is invalid.

    Args:
        email: An email address string.

    Returns:
        Tuple of (local_part, domain).
    """
    if email.count("@") != 1:
        raise ValueError(
            f"Email must contain exactly one '@', got {email.count('@')}"
        )

    local, domain = email.split("@")

    if not local:
        raise ValueError("Local part of email must be non-empty")
    if not domain:
        raise ValueError("Domain part of email must be non-empty")

    return (local, domain)


class RateLimiter:
    """A rate limiter that allows max_calls calls within a given period (seconds).

    Each call to allow() checks whether the call should be permitted:
    - Track timestamps of allowed calls.
    - Remove timestamps older than `period` seconds.
    - If the number of remaining timestamps is less than max_calls, allow
      the call (return True) and record the timestamp.
    - Otherwise, deny the call (return False).

    Args:
        max_calls: Maximum number of calls allowed in the period.
        period: Time window in seconds.
    """

    def __init__(self, max_calls: int, period: float):
        self.max_calls = max_calls
        self.period = period
        self._timestamps: list[float] = []

    def allow(self) -> bool:
        """Check if a call is allowed under the rate limit.

        Returns:
            True if the call is allowed, False otherwise.
        """
        now = time.monotonic()

        # Remove timestamps older than the period
        self._timestamps = [
            ts for ts in self._timestamps if now - ts < self.period
        ]

        if len(self._timestamps) < self.max_calls:
            self._timestamps.append(now)
            return True
        return False


if __name__ == "__main__":
    # --- Test calculate_statistics: basic correctness ---
    stats = calculate_statistics([1, 2, 3, 4, 5])
    assert stats["mean"] == 3.0, f"Expected mean=3.0, got {stats['mean']}"
    assert stats["median"] == 3.0, f"Expected median=3.0, got {stats['median']}"
    expected_std = math.sqrt(sum((x - 3) ** 2 for x in [1, 2, 3, 4, 5]) / 5)
    assert abs(stats["std_dev"] - expected_std) < 1e-9, (
        f"Expected std_dev={expected_std}, got {stats['std_dev']}"
    )

    # Even number of elements (median is average of two middle)
    stats = calculate_statistics([1, 2, 3, 4])
    assert stats["median"] == 2.5, f"Expected median=2.5, got {stats['median']}"
    assert stats["mean"] == 2.5, f"Expected mean=2.5, got {stats['mean']}"

    # Single element
    stats = calculate_statistics([42])
    assert stats["mean"] == 42.0
    assert stats["median"] == 42.0
    assert stats["std_dev"] == 0.0

    # All same values
    stats = calculate_statistics([5, 5, 5, 5])
    assert stats["mean"] == 5.0
    assert stats["median"] == 5.0
    assert stats["std_dev"] == 0.0

    print("calculate_statistics correctness: all tests passed")

    # --- Test calculate_statistics: empty list raises ValueError ---
    try:
        calculate_statistics([])
        assert False, "Should have raised ValueError for empty list"
    except ValueError:
        pass

    print("calculate_statistics edge cases: all tests passed")

    # --- Test parse_email: parametrize-style valid cases ---
    valid_cases = [
        ("user@example.com", ("user", "example.com")),
        ("alice@domain.org", ("alice", "domain.org")),
        ("test.name@sub.domain.com", ("test.name", "sub.domain.com")),
        ("a@b", ("a", "b")),
    ]
    for email, expected in valid_cases:
        result = parse_email(email)
        assert result == expected, f"parse_email({email!r}) = {result}, expected {expected}"

    print("parse_email valid cases: all tests passed")

    # --- Test parse_email: parametrize-style invalid cases ---
    invalid_emails = [
        "",                # empty
        "noatsign",        # no @
        "@domain.com",     # empty local part
        "user@",           # empty domain
        "a@b@c",           # multiple @
        "@",               # just @
    ]
    for email in invalid_emails:
        try:
            parse_email(email)
            assert False, f"Should have raised ValueError for {email!r}"
        except ValueError:
            pass

    print("parse_email invalid cases: all tests passed")

    # --- Test RateLimiter: basic behavior ---
    limiter = RateLimiter(max_calls=3, period=1.0)
    assert limiter.allow() is True, "First call should be allowed"
    assert limiter.allow() is True, "Second call should be allowed"
    assert limiter.allow() is True, "Third call should be allowed"
    assert limiter.allow() is False, "Fourth call should be denied"
    assert limiter.allow() is False, "Fifth call should still be denied"

    print("RateLimiter basic: all tests passed")

    # --- Test RateLimiter: resets after period ---
    limiter2 = RateLimiter(max_calls=2, period=0.1)
    assert limiter2.allow() is True
    assert limiter2.allow() is True
    assert limiter2.allow() is False

    time.sleep(0.15)  # Wait for period to expire

    assert limiter2.allow() is True, "Should be allowed after period expires"
    assert limiter2.allow() is True, "Should be allowed after period expires"
    assert limiter2.allow() is False, "Should be denied again after max_calls"

    print("RateLimiter reset: all tests passed")

    # --- Test RateLimiter: single call limit ---
    limiter3 = RateLimiter(max_calls=1, period=0.1)
    assert limiter3.allow() is True
    assert limiter3.allow() is False
    time.sleep(0.15)
    assert limiter3.allow() is True

    print("RateLimiter single call: all tests passed")

    print("\nAll solution 04 tests passed!")
