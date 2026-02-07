"""Solution 02: Strings"""


def reverse_string(s: str) -> str:
    """Return the reverse of s using slicing."""
    return s[::-1]


def count_vowels(s: str) -> int:
    """Count the number of vowels (a, e, i, o, u) in s. Case insensitive."""
    return sum(1 for c in s.lower() if c in "aeiou")


def is_palindrome(s: str) -> bool:
    """Check if s is a palindrome. Case insensitive, ignoring spaces."""
    cleaned = s.lower().replace(" ", "")
    return cleaned == cleaned[::-1]


def format_greeting(name: str, age: int) -> str:
    """Return a greeting using an f-string."""
    return f"Hello, {name}! You are {age} years old."


def extract_domain(email: str) -> str:
    """Extract and return the domain from an email address."""
    return email.split("@")[1]


if __name__ == "__main__":
    # reverse_string
    assert reverse_string("hello") == "olleh"
    assert reverse_string("Python") == "nohtyP"
    assert reverse_string("") == ""
    assert reverse_string("a") == "a"
    assert reverse_string("abba") == "abba"

    # count_vowels
    assert count_vowels("hello") == 2
    assert count_vowels("AEIOU") == 5
    assert count_vowels("aeiouAEIOU") == 10
    assert count_vowels("rhythm") == 0
    assert count_vowels("") == 0

    # is_palindrome
    assert is_palindrome("racecar") is True
    assert is_palindrome("A man a plan a canal Panama") is True
    assert is_palindrome("hello") is False
    assert is_palindrome("Was it a car or a cat I saw") is True
    assert is_palindrome("") is True

    # format_greeting
    assert format_greeting("Alice", 30) == "Hello, Alice! You are 30 years old."
    assert format_greeting("Bob", 25) == "Hello, Bob! You are 25 years old."

    # extract_domain
    assert extract_domain("user@example.com") == "example.com"
    assert extract_domain("alice@mail.org") == "mail.org"
    assert extract_domain("test@sub.domain.co.uk") == "sub.domain.co.uk"

    print("All tests passed!")
