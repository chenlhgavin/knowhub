# Chapter 05: Object-Oriented Programming (OOP)

## Classes and Objects

A class is a blueprint for creating objects. Objects are instances of a class.

```python
class Dog:
    # Class attribute (shared by all instances)
    species = "Canis familiaris"

    def __init__(self, name: str, age: int):
        # Instance attributes (unique to each instance)
        self.name = name
        self.age = age

d = Dog("Rex", 5)
print(d.name)       # "Rex"       — instance attribute
print(d.species)    # "Canis familiaris" — class attribute
print(Dog.species)  # "Canis familiaris" — accessed via class
```

- `__init__` is the initializer (called automatically when creating an object).
- `self` refers to the current instance. It is passed implicitly on method calls.
- **Instance attributes** are defined on `self` inside `__init__` (or other methods). Each object gets its own copy.
- **Class attributes** are defined directly in the class body. They are shared across all instances.

```python
class Counter:
    count = 0  # class attribute

    def __init__(self):
        Counter.count += 1  # modify via class name

a = Counter()
b = Counter()
print(Counter.count)  # 2
```

---

## Methods

### Instance Methods

Regular methods that receive the instance (`self`) as the first argument.

```python
class Circle:
    def __init__(self, radius: float):
        self.radius = radius

    def area(self) -> float:
        import math
        return math.pi * self.radius ** 2
```

### Class Methods (`@classmethod`)

Receive the class (`cls`) as the first argument. Useful for alternative constructors.

```python
class Date:
    def __init__(self, year: int, month: int, day: int):
        self.year = year
        self.month = month
        self.day = day

    @classmethod
    def from_string(cls, date_str: str) -> "Date":
        y, m, d = map(int, date_str.split("-"))
        return cls(y, m, d)

d = Date.from_string("2025-01-15")
```

### Static Methods (`@staticmethod`)

No implicit first argument. They behave like regular functions but live inside the class namespace.

```python
class MathUtils:
    @staticmethod
    def is_even(n: int) -> bool:
        return n % 2 == 0

MathUtils.is_even(4)  # True
```

---

## Properties

Properties let you define getters and setters that look like attribute access.

```python
class Celsius:
    def __init__(self, temperature: float = 0.0):
        self._temperature = temperature  # "private" by convention

    @property
    def temperature(self) -> float:
        """Getter."""
        return self._temperature

    @temperature.setter
    def temperature(self, value: float):
        """Setter with validation."""
        if value < -273.15:
            raise ValueError("Temperature below absolute zero")
        self._temperature = value

c = Celsius(25)
print(c.temperature)   # 25   — calls getter
c.temperature = 30     # calls setter
c.temperature = -300   # raises ValueError
```

You can also create read-only properties by omitting the setter.

---

## Inheritance

### Single Inheritance

```python
class Animal:
    def __init__(self, name: str):
        self.name = name

    def speak(self) -> str:
        raise NotImplementedError

class Dog(Animal):
    def speak(self) -> str:
        return f"{self.name} says Woof!"
```

### `super()`

Calls the parent class method. Essential for cooperative inheritance.

```python
class Animal:
    def __init__(self, name: str):
        self.name = name

class Dog(Animal):
    def __init__(self, name: str, breed: str):
        super().__init__(name)
        self.breed = breed
```

### Multiple Inheritance

Python supports inheriting from multiple classes.

```python
class Flyer:
    def fly(self):
        return "Flying"

class Swimmer:
    def swim(self):
        return "Swimming"

class Duck(Flyer, Swimmer):
    pass

d = Duck()
d.fly()   # "Flying"
d.swim()  # "Swimming"
```

### Method Resolution Order (MRO)

When multiple base classes define the same method, Python uses the **C3 linearization** algorithm to determine which method to call.

```python
class A:
    def greet(self):
        return "A"

class B(A):
    def greet(self):
        return "B"

class C(A):
    def greet(self):
        return "C"

class D(B, C):
    pass

print(D().greet())  # "B"
print(D.__mro__)
# (<class 'D'>, <class 'B'>, <class 'C'>, <class 'A'>, <class 'object'>)
```

---

## Magic / Dunder Methods

Dunder (double-underscore) methods let you customize how objects behave with built-in operations.

```python
class Book:
    def __init__(self, title: str, pages: list[str]):
        self.title = title
        self.pages = pages

    # String representations
    def __repr__(self) -> str:
        return f"Book({self.title!r}, {len(self.pages)} pages)"

    def __str__(self) -> str:
        return self.title

    # Comparison
    def __eq__(self, other) -> bool:
        if not isinstance(other, Book):
            return NotImplemented
        return self.title == other.title

    def __lt__(self, other) -> bool:
        if not isinstance(other, Book):
            return NotImplemented
        return self.title < other.title

    def __hash__(self) -> int:
        return hash(self.title)

    # Container protocol
    def __len__(self) -> int:
        return len(self.pages)

    def __getitem__(self, index: int) -> str:
        return self.pages[index]

    def __contains__(self, text: str) -> bool:
        return any(text in page for page in self.pages)

    # Arithmetic
    def __add__(self, other: "Book") -> "Book":
        return Book(f"{self.title} & {other.title}", self.pages + other.pages)

    # Boolean
    def __bool__(self) -> bool:
        return len(self.pages) > 0
```

Key dunder methods at a glance:

| Method | Triggered by |
|---|---|
| `__repr__` | `repr(obj)`, debugger display |
| `__str__` | `str(obj)`, `print(obj)` |
| `__eq__` | `obj == other` |
| `__lt__` | `obj < other` (enables sorting with `functools.total_ordering`) |
| `__hash__` | `hash(obj)`, dict keys, set members |
| `__len__` | `len(obj)` |
| `__getitem__` | `obj[index]` |
| `__contains__` | `item in obj` |
| `__add__` | `obj + other` |
| `__bool__` | `bool(obj)`, `if obj:` |

---

## Operator Overloading

By implementing dunder methods you can make your objects work with Python operators.

```python
from functools import total_ordering

@total_ordering
class Temperature:
    def __init__(self, celsius: float):
        self.celsius = celsius

    def __eq__(self, other):
        if not isinstance(other, Temperature):
            return NotImplemented
        return self.celsius == other.celsius

    def __lt__(self, other):
        if not isinstance(other, Temperature):
            return NotImplemented
        return self.celsius < other.celsius

    def __add__(self, other):
        if not isinstance(other, Temperature):
            return NotImplemented
        return Temperature(self.celsius + other.celsius)

t1 = Temperature(20)
t2 = Temperature(30)
print(t1 < t2)    # True
print(t1 + t2)    # Temperature with celsius=50
print(t1 >= t2)   # False — provided by @total_ordering
```

`@total_ordering` automatically generates `__le__`, `__gt__`, and `__ge__` from `__eq__` and `__lt__`.

---

## Abstract Base Classes (abc module)

Abstract classes cannot be instantiated and enforce subclasses to implement specific methods.

```python
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

# Shape()       # TypeError: Can't instantiate abstract class
r = Rectangle(3, 4)
print(r.area())  # 12
```

---

## Dataclasses

The `dataclasses` module reduces boilerplate for classes that mainly hold data.

```python
from dataclasses import dataclass, field

@dataclass
class Point:
    x: float
    y: float

p = Point(1.0, 2.0)
print(p)           # Point(x=1.0, y=2.0)  — auto __repr__
print(p == Point(1.0, 2.0))  # True       — auto __eq__
```

### `field()` for Mutable Defaults

```python
@dataclass
class Inventory:
    items: list[str] = field(default_factory=list)
```

### `frozen=True` for Immutable Instances

```python
@dataclass(frozen=True)
class Color:
    r: int
    g: int
    b: int

c = Color(255, 0, 0)
# c.r = 100  # raises FrozenInstanceError
print(hash(c))  # frozen dataclasses are hashable
```

### `order=True` for Comparison

```python
@dataclass(order=True)
class Version:
    major: int
    minor: int
    patch: int

v1 = Version(1, 2, 3)
v2 = Version(1, 3, 0)
print(v1 < v2)  # True — compares field by field
```

---

## `__slots__` for Memory Optimization

By default Python stores instance attributes in a per-instance `__dict__`. Using `__slots__` replaces this with a fixed set of attribute slots, saving memory.

```python
class PointDict:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class PointSlots:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y

p = PointSlots(1, 2)
# p.z = 3  # AttributeError — cannot add attributes not in __slots__
```

When you have millions of instances, `__slots__` can reduce memory usage significantly (often 30-50%).

**Caveat:** classes with `__slots__` do not have a `__dict__` unless you explicitly include `"__dict__"` in `__slots__`.

---

## Composition vs Inheritance

**Inheritance** models an "is-a" relationship. **Composition** models a "has-a" relationship. Prefer composition when you need flexibility.

```python
# Inheritance: a Dog IS an Animal
class Animal:
    def eat(self):
        return "Eating"

class Dog(Animal):
    def bark(self):
        return "Woof!"

# Composition: a Car HAS an Engine
class Engine:
    def __init__(self, horsepower: int):
        self.horsepower = horsepower

    def start(self):
        return "Vroom!"

class Car:
    def __init__(self, engine: Engine):
        self.engine = engine  # composition

    def start(self):
        return self.engine.start()

car = Car(Engine(150))
print(car.start())  # "Vroom!"
```

**Guidelines:**
- Use inheritance for genuine type hierarchies (Shape -> Rectangle).
- Use composition when you need to combine behaviors from unrelated objects.
- Favor shallow inheritance trees (one or two levels deep).
- If you find yourself inheriting just to reuse code, composition is likely a better fit.
