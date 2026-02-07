"""Solution 02: Inheritance — Shapes"""

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
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)


class Square(Rectangle):
    def __init__(self, side: float):
        super().__init__(side, side)


class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    def area(self) -> float:
        return math.pi * self.radius ** 2

    def perimeter(self) -> float:
        return 2 * math.pi * self.radius


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
