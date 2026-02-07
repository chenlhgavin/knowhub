"""Solution 01: Classes — Vector2D"""

import math


class Vector2D:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def magnitude(self) -> float:
        """Return the Euclidean length of the vector."""
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def dot(self, other: "Vector2D") -> float:
        """Return the dot product of this vector with another."""
        return self.x * other.x + self.y * other.y

    def __repr__(self) -> str:
        return f"Vector2D({self.x}, {self.y})"

    def __add__(self, other: "Vector2D") -> "Vector2D":
        return Vector2D(self.x + other.x, self.y + other.y)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector2D):
            return NotImplemented
        return self.x == other.x and self.y == other.y


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
