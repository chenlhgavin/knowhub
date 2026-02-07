"""
Exercise 03: Type Hints

Topics covered:
- TypeVar and generic functions
- Generic classes with Generic[T]
- Union types (str | int)
- Properly typed function signatures

Instructions:
    Implement each function and class below. This exercise focuses on writing
    correctly typed Python code. Each function/method raises NotImplementedError
    until you provide an implementation. Run the file to verify your solutions
    against the assert-based tests at the bottom.
"""

from typing import TypeVar, Generic

T = TypeVar("T")


def first_or_default(items: list[T], default: T) -> T:
    """Return the first element of items, or default if items is empty.

    Args:
        items: A list of elements.
        default: The value to return if items is empty.

    Returns:
        The first element, or default.
    """
    raise NotImplementedError("Implement first_or_default")


def parse_config(raw: dict[str, str]) -> dict[str, int | float | str | bool]:
    """Parse string values from a raw config dict into appropriate types.

    Conversion rules (applied in this order):
    1. "true" (case-insensitive) -> True, "false" (case-insensitive) -> False
    2. Strings that represent integers (e.g., "42", "-7") -> int
    3. Strings that represent floats (e.g., "3.14", "-0.5") -> float
    4. Everything else stays as str

    Args:
        raw: A dict mapping string keys to string values.

    Returns:
        A new dict with the same keys but parsed values.
    """
    raise NotImplementedError("Implement parse_config")


class Stack(Generic[T]):
    """A generic stack (LIFO) data structure.

    Supports push, pop, peek, is_empty, and len().
    Raises IndexError on pop/peek when empty.
    """

    def __init__(self) -> None:
        raise NotImplementedError("Implement Stack.__init__")

    def push(self, item: T) -> None:
        """Push an item onto the stack."""
        raise NotImplementedError("Implement Stack.push")

    def pop(self) -> T:
        """Remove and return the top item. Raises IndexError if empty."""
        raise NotImplementedError("Implement Stack.pop")

    def peek(self) -> T:
        """Return the top item without removing it. Raises IndexError if empty."""
        raise NotImplementedError("Implement Stack.peek")

    def is_empty(self) -> bool:
        """Return True if the stack has no items."""
        raise NotImplementedError("Implement Stack.is_empty")

    def __len__(self) -> int:
        """Return the number of items on the stack."""
        raise NotImplementedError("Implement Stack.__len__")


def process_items(items: list[str | int], *, upper: bool = False) -> list[str]:
    """Convert all items to strings, optionally uppercasing them.

    Args:
        items: A list of strings or integers.
        upper: If True, uppercase all resulting strings.

    Returns:
        A list of string representations.
    """
    raise NotImplementedError("Implement process_items")


if __name__ == "__main__":
    # --- Test first_or_default ---
    assert first_or_default([1, 2, 3], 0) == 1
    assert first_or_default([], 0) == 0
    assert first_or_default(["a", "b"], "z") == "a"
    assert first_or_default([], "z") == "z"
    assert first_or_default([None, 1, 2], "default") is None
    assert first_or_default([], None) is None

    print("first_or_default: all tests passed")

    # --- Test parse_config ---
    raw = {
        "debug": "true",
        "verbose": "False",
        "port": "8080",
        "rate": "3.14",
        "name": "myapp",
        "negative": "-7",
        "neg_float": "-0.5",
        "empty": "",
    }
    parsed = parse_config(raw)
    assert parsed["debug"] is True, f"Expected True, got {parsed['debug']}"
    assert parsed["verbose"] is False, f"Expected False, got {parsed['verbose']}"
    assert parsed["port"] == 8080, f"Expected 8080, got {parsed['port']}"
    assert isinstance(parsed["port"], int), f"port should be int, got {type(parsed['port'])}"
    assert parsed["rate"] == 3.14, f"Expected 3.14, got {parsed['rate']}"
    assert isinstance(parsed["rate"], float), f"rate should be float, got {type(parsed['rate'])}"
    assert parsed["name"] == "myapp", f"Expected 'myapp', got {parsed['name']}"
    assert parsed["negative"] == -7, f"Expected -7, got {parsed['negative']}"
    assert isinstance(parsed["negative"], int)
    assert parsed["neg_float"] == -0.5
    assert isinstance(parsed["neg_float"], float)
    assert parsed["empty"] == ""

    # Empty dict
    assert parse_config({}) == {}

    print("parse_config: all tests passed")

    # --- Test Stack ---
    stack: Stack[int] = Stack()
    assert stack.is_empty() is True
    assert len(stack) == 0

    stack.push(10)
    stack.push(20)
    stack.push(30)
    assert len(stack) == 3
    assert stack.is_empty() is False

    assert stack.peek() == 30
    assert len(stack) == 3  # peek should not remove

    assert stack.pop() == 30
    assert stack.pop() == 20
    assert len(stack) == 1

    assert stack.peek() == 10
    assert stack.pop() == 10
    assert stack.is_empty() is True

    # Test IndexError on empty pop/peek
    try:
        stack.pop()
        assert False, "Should have raised IndexError"
    except IndexError:
        pass

    try:
        stack.peek()
        assert False, "Should have raised IndexError"
    except IndexError:
        pass

    # Test with strings
    str_stack: Stack[str] = Stack()
    str_stack.push("hello")
    str_stack.push("world")
    assert str_stack.pop() == "world"
    assert str_stack.pop() == "hello"

    print("Stack: all tests passed")

    # --- Test process_items ---
    assert process_items(["hello", 42, "world"]) == ["hello", "42", "world"]
    assert process_items(["hello", 42], upper=True) == ["HELLO", "42"]
    assert process_items([]) == []
    assert process_items([1, 2, 3]) == ["1", "2", "3"]
    assert process_items([1, 2, 3], upper=True) == ["1", "2", "3"]
    assert process_items(["abc", "DEF"], upper=False) == ["abc", "DEF"]
    assert process_items(["abc", "DEF"], upper=True) == ["ABC", "DEF"]

    print("process_items: all tests passed")

    print("\nAll exercise 03 tests passed!")
