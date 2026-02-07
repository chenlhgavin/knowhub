"""Exercise 01: Classes — Vector2D

Implement a 2D vector class with arithmetic operations and common dunder methods.

Requirements:
- Vector2D(x: float, y: float)
- magnitude() -> float : return the length (Euclidean norm)
- dot(other: Vector2D) -> float : return the dot product
- __repr__ : return "Vector2D(x, y)"
- __add__ : vector addition, returning a new Vector2D
- __eq__ : compare x and y components
"""

import math


class Vector2D:
    def __init__(self, x: float, y: float):
        raise NotImplementedError("Implement __init__")

    def magnitude(self) -> float:
        """Return the Euclidean length of the vector."""
        raise NotImplementedError("Implement magnitude")

    def dot(self, other: "Vector2D") -> float:
        """Return the dot product of this vector with another."""
        raise NotImplementedError("Implement dot")

    def __repr__(self) -> str:
        raise NotImplementedError("Implement __repr__")

    def __add__(self, other: "Vector2D") -> "Vector2D":
        raise NotImplementedError("Implement __add__")

    def __eq__(self, other: object) -> bool:
        raise NotImplementedError("Implement __eq__")


if __name__ == "__main__":
    # Construction and repr
    v1 = Vector2D(3, 4)
    v2 = Vector2D(1, 2)
    assert repr(v1) == "Vector2D(3, 4)", f"Got {repr(v1)}"
    assert repr(v2) == "Vector2D(1, 2)", f"Got {repr(v2)}"

    # Magnitude
    assert v1.magnitude() == 5.0, f"Got {v1.magnitude()}"
    assert Vector2D(0, 0).magnitude() == 0.0

    # Dot product
    assert v1.dot(v2) == 11.0, f"Got {v1.dot(v2)}"  # 3*1 + 4*2 = 11
    assert v2.dot(v1) == 11.0  # commutative

    # Addition
    v3 = v1 + v2
    assert repr(v3) == "Vector2D(4, 6)", f"Got {repr(v3)}"

    # Equality
    assert v1 == Vector2D(3, 4)
    assert v1 != v2
    assert v1 != "not a vector"

    # Addition does not mutate originals
    assert repr(v1) == "Vector2D(3, 4)"
    assert repr(v2) == "Vector2D(1, 2)"

    print("All tests passed!")
