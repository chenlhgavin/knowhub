"""
Solution 01: Descriptors

Implements:
- Validated descriptor with custom predicate validation
- Bounded descriptor for numeric range enforcement
- Person class demonstrating both descriptors
"""


class Validated:
    """A descriptor that validates values using a custom predicate.

    The descriptor stores values in the instance's __dict__ under a private key
    derived from the attribute name.

    Args:
        name: The attribute name (used for storage key).
        validator: A callable that takes a value and returns True if valid.
        error_msg: Message for the ValueError raised on invalid values.
    """

    def __init__(self, name: str, validator: callable, error_msg: str = "Invalid value"):
        self.validator = validator
        self.error_msg = error_msg
        self.storage_name = f"_validated_{name}"

    def __set_name__(self, owner, name):
        self.storage_name = f"_validated_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.storage_name, None)

    def __set__(self, obj, value):
        if not self.validator(value):
            raise ValueError(self.error_msg)
        setattr(obj, self.storage_name, value)


class Bounded:
    """A descriptor for numeric attributes with min/max bounds.

    Raises ValueError if the assigned value is outside [min_val, max_val].

    Args:
        name: The attribute name (used for storage key).
        min_val: Minimum allowed value (inclusive).
        max_val: Maximum allowed value (inclusive).
    """

    def __init__(self, name: str, min_val: float, max_val: float):
        self.min_val = min_val
        self.max_val = max_val
        self.storage_name = f"_bounded_{name}"

    def __set_name__(self, owner, name):
        self.storage_name = f"_bounded_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.storage_name, None)

    def __set__(self, obj, value):
        if not (self.min_val <= value <= self.max_val):
            raise ValueError(
                f"Value {value} is out of range [{self.min_val}, {self.max_val}]"
            )
        setattr(obj, self.storage_name, value)


class Person:
    """A class using Validated and Bounded descriptors.

    Attributes:
        name: Must be a non-empty string.
        age: Must be a number between 0 and 150 (inclusive).
    """

    name = Validated(
        "name",
        lambda x: isinstance(x, str) and len(x) > 0,
        "Name must be non-empty string",
    )
    age = Bounded("age", 0, 150)

    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age


if __name__ == "__main__":
    # --- Test Person with valid values ---
    p = Person("Alice", 30)
    assert p.name == "Alice", f"Expected 'Alice', got {p.name}"
    assert p.age == 30, f"Expected 30, got {p.age}"

    p.name = "Bob"
    assert p.name == "Bob", f"Expected 'Bob', got {p.name}"

    p.age = 0
    assert p.age == 0, f"Expected 0, got {p.age}"

    p.age = 150
    assert p.age == 150, f"Expected 150, got {p.age}"

    print("Person with valid values: all tests passed")

    # --- Test Validated raises on invalid values ---
    try:
        p.name = ""
        assert False, "Should have raised ValueError for empty name"
    except ValueError as e:
        assert "non-empty" in str(e).lower() or "invalid" in str(e).lower(), (
            f"Unexpected error message: {e}"
        )

    try:
        p.name = 123
        assert False, "Should have raised ValueError for non-string name"
    except ValueError:
        pass

    print("Validated descriptor errors: all tests passed")

    # --- Test Bounded raises on out of range ---
    try:
        p.age = -1
        assert False, "Should have raised ValueError for age < 0"
    except ValueError:
        pass

    try:
        p.age = 151
        assert False, "Should have raised ValueError for age > 150"
    except ValueError:
        pass

    try:
        p.age = -100
        assert False, "Should have raised ValueError for age = -100"
    except ValueError:
        pass

    print("Bounded descriptor errors: all tests passed")

    # --- Test multiple instances are independent ---
    p1 = Person("Charlie", 25)
    p2 = Person("Diana", 40)
    assert p1.name == "Charlie"
    assert p2.name == "Diana"
    assert p1.age == 25
    assert p2.age == 40

    p1.name = "Eve"
    assert p1.name == "Eve"
    assert p2.name == "Diana"  # p2 should not be affected

    print("Multiple instances: all tests passed")

    print("\nAll solution 01 tests passed!")
