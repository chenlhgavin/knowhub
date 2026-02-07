"""Exercise 02: Inheritance — Shapes

Implement a shape hierarchy using abstract base classes.

Requirements:
- Shape (abstract): area() -> float, perimeter() -> float
- Rectangle(width, height) extends Shape
- Square(side) extends Rectangle
- Circle(radius) extends Shape

All area/perimeter methods must return floats.
"""

import math
from abc import ABC, abstractmethod


class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        ...

    @abstractmethod
    def perimeter(self) -> float:
        ...


class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        raise NotImplementedError("Implement Rectangle.__init__")

    def area(self) -> float:
        raise NotImplementedError("Implement Rectangle.area")

    def perimeter(self) -> float:
        raise NotImplementedError("Implement Rectangle.perimeter")


class Square(Rectangle):
    def __init__(self, side: float):
        raise NotImplementedError("Implement Square.__init__")


class Circle(Shape):
    def __init__(self, radius: float):
        raise NotImplementedError("Implement Circle.__init__")

    def area(self) -> float:
        raise NotImplementedError("Implement Circle.area")

    def perimeter(self) -> float:
        raise NotImplementedError("Implement Circle.perimeter")


if __name__ == "__main__":
    # Rectangle
    r = Rectangle(3, 4)
    assert r.area() == 12.0, f"Got {r.area()}"
    assert r.perimeter() == 14.0, f"Got {r.perimeter()}"

    # Square
    s = Square(5)
    assert s.area() == 25.0, f"Got {s.area()}"
    assert s.perimeter() == 20.0, f"Got {s.perimeter()}"

    # Circle
    c = Circle(7)
    assert abs(c.area() - math.pi * 49) < 1e-9, f"Got {c.area()}"
    assert abs(c.perimeter() - 2 * math.pi * 7) < 1e-9, f"Got {c.perimeter()}"

    # isinstance checks
    assert isinstance(r, Shape)
    assert isinstance(r, Rectangle)
    assert isinstance(s, Shape)
    assert isinstance(s, Rectangle)
    assert isinstance(s, Square)
    assert isinstance(c, Shape)
    assert isinstance(c, Circle)
    assert not isinstance(c, Rectangle)

    # Cannot instantiate Shape directly
    try:
        Shape()
        assert False, "Should have raised TypeError"
    except TypeError:
        pass

    print("All tests passed!")
