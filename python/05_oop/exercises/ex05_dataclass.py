"""Exercise 05: Dataclasses — Student and Point

Implement data-holding classes using the dataclasses module.

Requirements:

Student (mutable dataclass):
- Fields: name (str), grades (list[int]), active (bool, default True)
- property average -> float
- method letter_grade() -> str  (A >= 90, B >= 80, C >= 70, D >= 60, F < 60)
- __post_init__: validate all grades are 0-100

Point (frozen dataclass):
- Fields: x (float), y (float)
- method distance_to(other: Point) -> float
- Must be hashable (frozen=True)
"""

import math
from dataclasses import dataclass, field


# TODO: implement Student as a @dataclass
class Student:
    def __init__(self, name: str, grades: list[int], active: bool = True):
        raise NotImplementedError("Implement Student as a @dataclass")

    @property
    def average(self) -> float:
        raise NotImplementedError("Implement average property")

    def letter_grade(self) -> str:
        raise NotImplementedError("Implement letter_grade")


# TODO: implement Point as a @dataclass(frozen=True)
class Point:
    def __init__(self, x: float, y: float):
        raise NotImplementedError("Implement Point as a frozen @dataclass")

    def distance_to(self, other: "Point") -> float:
        raise NotImplementedError("Implement distance_to")


if __name__ == "__main__":
    # --- Student tests ---
    s1 = Student("Alice", [95, 87, 92])
    assert s1.name == "Alice"
    assert s1.grades == [95, 87, 92]
    assert s1.active is True

    # Average
    expected_avg = (95 + 87 + 92) / 3
    assert abs(s1.average - expected_avg) < 1e-9, f"Got {s1.average}"

    # Letter grade
    assert s1.letter_grade() == "A", f"Got {s1.letter_grade()}"  # avg ~91.3

    s2 = Student("Bob", [75, 80, 70], active=False)
    assert s2.letter_grade() == "C", f"Got {s2.letter_grade()}"  # avg 75.0
    assert s2.active is False

    s3 = Student("Carol", [60, 55, 65])
    assert s3.letter_grade() == "D", f"Got {s3.letter_grade()}"  # avg 60.0

    # Validation: grades out of range
    try:
        Student("Bad", [105, 80])
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    try:
        Student("Bad", [-1, 80])
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    # --- Point tests ---
    p1 = Point(0.0, 0.0)
    p2 = Point(3.0, 4.0)

    # Distance
    assert p1.distance_to(p2) == 5.0, f"Got {p1.distance_to(p2)}"
    assert p2.distance_to(p1) == 5.0  # symmetric

    # Frozen: cannot modify
    try:
        p1.x = 10.0
        assert False, "Should have raised FrozenInstanceError"
    except AttributeError:
        pass

    # Hashable: can be used as dict key
    d = {p1: "origin", p2: "point"}
    assert d[Point(0.0, 0.0)] == "origin"
    assert d[Point(3.0, 4.0)] == "point"

    print("All tests passed!")
