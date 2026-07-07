# Chapter 10: Advanced Python

This chapter covers advanced topics that separate intermediate Python developers from
experts. You will learn about Python's object model internals, type system, testing
practices, profiling, and design patterns.

---

## Table of Contents

1. [Metaclasses](#metaclasses)
2. [Descriptors](#descriptors)
3. [\_\_slots\_\_](#__slots__)
4. [Type Hints and the typing Module](#type-hints-and-the-typing-module)
5. [mypy Basics](#mypy-basics)
6. [Testing with pytest](#testing-with-pytest)
7. [Profiling](#profiling)
8. [Python Internals](#python-internals)
9. [Design Patterns in Python](#design-patterns-in-python)

---

## Metaclasses

A metaclass is a class whose instances are themselves classes. In Python, `type` is
the default metaclass — it is the class that creates all other classes.

### type as a Metaclass

Every class is an instance of `type`:

```python
class Foo:
    pass

print(type(Foo))        # <class 'type'>
print(type(int))        # <class 'type'>
print(type(type))       # <class 'type'> — type is its own metaclass
```

You can create classes dynamically with `type(name, bases, namespace)`:

```python
# These two are equivalent:
class Dog:
    sound = "woof"

Dog = type("Dog", (), {"sound": "woof"})
```

### \_\_new\_\_ vs \_\_init\_\_ in Metaclasses

In a metaclass, `__new__` creates the class object and `__init__` initializes it
after creation. `__new__` is where you can modify the class namespace before the
class is created.

```python
class MyMeta(type):
    def __new__(mcs, name, bases, namespace):
        # Called to CREATE the class object
        # You can inspect or modify namespace here
        print(f"Creating class: {name}")
        cls = super().__new__(mcs, name, bases, namespace)
        return cls

    def __init__(cls, name, bases, namespace):
        # Called to INITIALIZE the class object after creation
        print(f"Initializing class: {name}")
        super().__init__(name, bases, namespace)

class Example(metaclass=MyMeta):
    pass
# Output:
# Creating class: Example
# Initializing class: Example
```

### \_\_init_subclass\_\_

Introduced in Python 3.6, `__init_subclass__` is a simpler alternative to metaclasses
for many use cases. It is called on the parent class whenever a subclass is created.

```python
class Plugin:
    _registry: dict[str, type] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Plugin._registry[cls.__name__] = cls

class AudioPlugin(Plugin):
    pass

class VideoPlugin(Plugin):
    pass

print(Plugin._registry)
# {'AudioPlugin': <class 'AudioPlugin'>, 'VideoPlugin': <class 'VideoPlugin'>}
```

### Custom Metaclasses

A custom metaclass inherits from `type` and overrides `__new__` or `__init__`.

```python
class ValidatedMeta(type):
    """Metaclass that enforces all classes have a 'validate' method."""

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        # Skip validation for the base class itself
        if bases and not hasattr(cls, "validate"):
            raise TypeError(f"Class {name} must define a validate() method")
        return cls

class BaseModel(metaclass=ValidatedMeta):
    def validate(self):
        pass

class User(BaseModel):
    def validate(self):
        return len(self.name) > 0  # type: ignore

# This would raise TypeError:
# class BadModel(BaseModel):
#     pass  # No validate() method
```

### Practical Uses: Registries and Validation

**Registry pattern** — automatically register all subclasses:

```python
class RegistryMeta(type):
    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if not hasattr(cls, "_registry"):
            cls._registry = {}
        elif bases:  # Only register subclasses, not the base
            cls._registry[name] = cls
        return cls

class Handler(metaclass=RegistryMeta):
    pass

class JSONHandler(Handler):
    pass

class XMLHandler(Handler):
    pass

print(Handler._registry)
# {'JSONHandler': <class 'JSONHandler'>, 'XMLHandler': <class 'XMLHandler'>}
```

**Validation pattern** — enforce class structure at definition time:

```python
class InterfaceMeta(type):
    required_methods: list[str] = []

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if bases:  # Skip the base class
            for method_name in mcs.required_methods:
                if method_name not in namespace:
                    raise TypeError(
                        f"Class {name} must implement {method_name}()"
                    )
        return cls
```

---

## Descriptors

Descriptors are objects that define `__get__`, `__set__`, or `__delete__`. They
control what happens when an attribute is accessed, set, or deleted on another object.

### \_\_get\_\_, \_\_set\_\_, \_\_delete\_\_

```python
class Verbose:
    """A descriptor that logs all attribute access."""

    def __set_name__(self, owner, name):
        self.name = name
        self.storage_name = f"_desc_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self  # Accessed on the class, not an instance
        value = getattr(obj, self.storage_name, None)
        print(f"Getting {self.name}: {value}")
        return value

    def __set__(self, obj, value):
        print(f"Setting {self.name} to {value}")
        setattr(obj, self.storage_name, value)

    def __delete__(self, obj):
        print(f"Deleting {self.name}")
        delattr(obj, self.storage_name)

class MyClass:
    attr = Verbose()

m = MyClass()
m.attr = 42       # Setting attr to 42
print(m.attr)     # Getting attr: 42 -> 42
del m.attr        # Deleting attr
```

### Data vs Non-Data Descriptors

- A **data descriptor** defines both `__get__` and `__set__` (or `__delete__`).
  It takes priority over the instance `__dict__`.
- A **non-data descriptor** defines only `__get__`. The instance `__dict__` takes
  priority over it.

```python
class DataDescriptor:
    """Data descriptor — defines __get__ and __set__."""
    def __get__(self, obj, objtype=None):
        return "from descriptor"
    def __set__(self, obj, value):
        pass  # Intercepts all sets

class NonDataDescriptor:
    """Non-data descriptor — defines only __get__."""
    def __get__(self, obj, objtype=None):
        return "from descriptor"

class Example:
    data = DataDescriptor()
    non_data = NonDataDescriptor()

e = Example()
e.__dict__["data"] = "from instance"
e.__dict__["non_data"] = "from instance"

print(e.data)      # "from descriptor" — data descriptor wins
print(e.non_data)  # "from instance"   — instance dict wins
```

Attribute lookup order:
1. Data descriptors (from the class and its MRO)
2. Instance `__dict__`
3. Non-data descriptors (from the class and its MRO)

### How @property Works Under the Hood

`property` is a data descriptor implemented in C. Here is a simplified Python
equivalent:

```python
class Property:
    """Simplified reimplementation of the built-in property."""

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.__doc__ = doc or (fget.__doc__ if fget else None)

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(obj)

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(obj, value)

    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(obj)

    def setter(self, fset):
        return type(self)(self.fget, fset, self.fdel, self.__doc__)

    def deleter(self, fdel):
        return type(self)(self.fget, self.fset, fdel, self.__doc__)
```

When you write `@property`, Python creates a `Property` data descriptor. Because it
defines both `__get__` and `__set__`, it always takes priority over instance attributes.

---

## \_\_slots\_\_

By default, Python stores instance attributes in a per-instance `__dict__` dictionary.
`__slots__` replaces that dict with a fixed set of attribute slots, saving memory.

### Memory Optimization

```python
class PointDict:
    """Uses __dict__ — flexible but memory-heavy."""
    def __init__(self, x, y):
        self.x = x
        self.y = y

class PointSlots:
    """Uses __slots__ — fixed attributes, less memory."""
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y

import sys
d = PointDict(1, 2)
s = PointSlots(1, 2)

print(sys.getsizeof(d) + sys.getsizeof(d.__dict__))  # ~200 bytes (varies)
print(sys.getsizeof(s))                                # ~56 bytes (varies)
```

Key rules:
- Classes with `__slots__` cannot have arbitrary attributes added at runtime.
- No `__dict__` is created per instance (unless `"__dict__"` is included in slots).
- `__slots__` is most useful when you create millions of instances of the same class.

### Inheritance with \_\_slots\_\_

When inheriting, each class in the hierarchy should declare its own `__slots__`
for the attributes it introduces:

```python
class Base:
    __slots__ = ("x",)

class Derived(Base):
    __slots__ = ("y",)  # Only new attributes; x is inherited from Base

d = Derived()
d.x = 1
d.y = 2

# If a parent does NOT use __slots__, the child still gets __dict__:
class RegularBase:
    pass

class SlottedChild(RegularBase):
    __slots__ = ("z",)

sc = SlottedChild()
sc.z = 1
sc.arbitrary = 2  # Works because RegularBase provides __dict__
```

Pitfall: if you forget `__slots__` in a child class, it gets a `__dict__` again and
you lose the memory savings.

---

## Type Hints and the typing Module

Type hints are annotations that document the expected types of variables, function
parameters, and return values. They have no runtime effect by default but are used
by static analysis tools like mypy.

### Basic Hints

```python
# Variable annotations
name: str = "Alice"
age: int = 30
scores: list[float] = [9.5, 8.0, 7.5]

# Function annotations
def greet(name: str, excited: bool = False) -> str:
    if excited:
        return f"Hello, {name}!"
    return f"Hello, {name}."

# Since Python 3.10, use | for unions:
def parse(value: str) -> int | float:
    try:
        return int(value)
    except ValueError:
        return float(value)
```

### Optional and Union

```python
from typing import Optional, Union

# Optional[X] is shorthand for X | None
def find_user(user_id: int) -> Optional[str]:
    if user_id == 1:
        return "Alice"
    return None

# Union[X, Y] means X or Y — Python 3.10+ allows X | Y
def process(value: Union[str, int]) -> str:
    return str(value)

# Modern syntax (Python 3.10+):
def process_modern(value: str | int) -> str:
    return str(value)
```

### Built-in Generic Types

Since Python 3.9, you can use built-in types directly in annotations:

```python
# Python 3.9+
names: list[str] = ["Alice", "Bob"]
config: dict[str, int] = {"timeout": 30, "retries": 3}
coords: tuple[float, float] = (1.0, 2.0)
unique: set[int] = {1, 2, 3}

# Variable-length tuple:
values: tuple[int, ...] = (1, 2, 3, 4)

# Nested types:
matrix: list[list[int]] = [[1, 2], [3, 4]]
registry: dict[str, list[tuple[int, str]]] = {}
```

### TypeVar and Generic

`TypeVar` creates generic type variables. `Generic` lets you build generic classes.

```python
from typing import TypeVar, Generic

T = TypeVar("T")

def first(items: list[T]) -> T:
    return items[0]

# first([1, 2, 3]) -> inferred as int
# first(["a", "b"]) -> inferred as str

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

    def peek(self) -> T:
        return self._items[-1]

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def __len__(self) -> int:
        return len(self._items)

stack: Stack[int] = Stack()
stack.push(1)
stack.push(2)
print(stack.pop())  # 2
```

### Protocol

`Protocol` defines structural subtyping (duck typing with type checking). A class
does not need to explicitly inherit from a Protocol — it just needs to have the
required methods.

```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> str: ...

class Circle:
    def draw(self) -> str:
        return "Drawing circle"

class Square:
    def draw(self) -> str:
        return "Drawing square"

def render(shape: Drawable) -> str:
    return shape.draw()

# Both work — no inheritance needed:
render(Circle())  # OK
render(Square())  # OK
```

### TypeAlias and Literal

```python
from typing import TypeAlias, Literal

# TypeAlias makes type aliases explicit
UserId: TypeAlias = int
Config: TypeAlias = dict[str, str | int | bool]

def get_user(uid: UserId) -> str:
    return f"User {uid}"

# Literal restricts values to specific literals
def set_mode(mode: Literal["read", "write", "append"]) -> None:
    print(f"Mode set to {mode}")

set_mode("read")   # OK
set_mode("write")  # OK
# set_mode("delete")  # mypy error: not a valid literal
```

---

## mypy Basics

mypy is the most popular static type checker for Python. It reads your type hints
and reports type errors without running your code.

### Running mypy

```bash
# Install
pip install mypy

# Check a single file
mypy my_module.py

# Check a package
mypy my_package/

# Check with strict mode (most thorough)
mypy --strict my_module.py
```

### Common Flags

| Flag | Description |
|------|-------------|
| `--strict` | Enable all strict checks (recommended for new projects) |
| `--ignore-missing-imports` | Suppress errors from untyped third-party libraries |
| `--disallow-untyped-defs` | Error on functions without type annotations |
| `--disallow-any-generics` | Error on bare `list`, `dict` (must use `list[int]`, etc.) |
| `--warn-return-any` | Warn when a function returns `Any` |
| `--no-implicit-optional` | Require explicit `Optional` instead of inferring from `None` default |
| `--check-untyped-defs` | Type-check the body of functions without annotations |

### Configuration with mypy.ini or pyproject.toml

```ini
# mypy.ini
[mypy]
python_version = 3.12
strict = True
ignore_missing_imports = True

[mypy-tests.*]
disallow_untyped_defs = False
```

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.12"
strict = true
ignore_missing_imports = true
```

### Common mypy Patterns

```python
from typing import cast, TYPE_CHECKING

# TYPE_CHECKING is False at runtime, True for mypy
if TYPE_CHECKING:
    from expensive_module import HeavyClass

# cast() tells mypy to trust your type assertion
value = cast(int, some_function())

# reveal_type() — mypy prints the inferred type (removed at runtime)
reveal_type(value)  # mypy output: Revealed type is "builtins.int"
```

---

## Testing with pytest

pytest is the standard testing framework for Python. It uses plain `assert`
statements, automatic test discovery, and a powerful fixture system.

### Test Functions

```python
# test_math.py
def test_addition():
    assert 1 + 1 == 2

def test_string_upper():
    assert "hello".upper() == "HELLO"

def test_list_append():
    items = [1, 2]
    items.append(3)
    assert items == [1, 2, 3]
    assert len(items) == 3
```

Run with: `pytest test_math.py -v`

### Assert

pytest rewrites assert statements to provide detailed failure messages:

```python
def test_detailed_failure():
    data = {"name": "Alice", "age": 30}
    assert data["age"] == 31
    # Output shows:
    # AssertionError: assert 30 == 31
    # where 30 = {'name': 'Alice', 'age': 30}['age']
```

Testing exceptions with `pytest.raises`:

```python
import pytest

def test_raises_value_error():
    with pytest.raises(ValueError, match="invalid"):
        int("not_a_number")

def test_raises_zero_division():
    with pytest.raises(ZeroDivisionError):
        1 / 0
```

### Fixtures (@pytest.fixture)

Fixtures provide reusable setup and teardown for tests.

```python
import pytest

@pytest.fixture
def sample_list():
    return [1, 2, 3, 4, 5]

@pytest.fixture
def db_connection():
    conn = create_connection()
    yield conn          # Provide the fixture value
    conn.close()        # Teardown after the test

def test_sum(sample_list):
    assert sum(sample_list) == 15

def test_length(sample_list):
    assert len(sample_list) == 5
```

Fixture scopes control how often setup runs:

```python
@pytest.fixture(scope="module")  # Once per module
def expensive_resource():
    return load_data()

@pytest.fixture(scope="session")  # Once per entire test session
def global_config():
    return read_config()
```

### Parametrize (@pytest.mark.parametrize)

Run the same test with multiple inputs:

```python
import pytest

@pytest.mark.parametrize("input_val,expected", [
    (1, 1),
    (2, 4),
    (3, 9),
    (4, 16),
    (-1, 1),
])
def test_square(input_val, expected):
    assert input_val ** 2 == expected

@pytest.mark.parametrize("email,valid", [
    ("user@example.com", True),
    ("invalid", False),
    ("@domain.com", False),
    ("user@", False),
])
def test_email_validation(email, valid):
    assert is_valid_email(email) == valid
```

### Markers

Markers let you categorize and selectively run tests:

```python
import pytest

@pytest.mark.slow
def test_large_dataset():
    # Takes a long time
    pass

@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    pass

@pytest.mark.skipif(sys.platform == "win32", reason="Unix only")
def test_unix_permissions():
    pass
```

Run selectively: `pytest -m "not slow"` or `pytest -m slow`.

### conftest.py

`conftest.py` is a special file that pytest automatically imports. Fixtures defined
in it are available to all tests in the same directory and subdirectories.

```
tests/
    conftest.py          # Shared fixtures
    test_users.py
    test_orders.py
    integration/
        conftest.py      # Additional fixtures for integration tests
        test_api.py
```

```python
# conftest.py
import pytest

@pytest.fixture
def app():
    """Create and configure a test application."""
    app = create_app(testing=True)
    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()
```

---

## Profiling

Profiling helps you find performance bottlenecks. Python provides several tools
at different granularity levels.

### timeit

`timeit` measures the execution time of small code snippets by running them many
times to get reliable measurements.

```python
import timeit

# Time a simple expression
t = timeit.timeit("sum(range(1000))", number=10000)
print(f"Total: {t:.4f}s")

# Time with setup
t = timeit.timeit(
    "sorted(data)",
    setup="import random; data = [random.random() for _ in range(1000)]",
    number=1000,
)
print(f"Sorting: {t:.4f}s")

# Compare approaches
list_comp = timeit.timeit("[x**2 for x in range(100)]", number=10000)
map_call = timeit.timeit("list(map(lambda x: x**2, range(100)))", number=10000)
print(f"List comp: {list_comp:.4f}s, map: {map_call:.4f}s")
```

From the command line:

```bash
python -m timeit "sum(range(1000))"
python -m timeit -s "data = list(range(1000))" "sorted(data)"
```

### cProfile

`cProfile` profiles an entire program, showing how much time is spent in each
function.

```python
import cProfile

def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# Profile a function call
cProfile.run("fibonacci(30)")

# Save results to a file for later analysis
cProfile.run("fibonacci(30)", "profile_output.prof")

# Programmatic usage
profiler = cProfile.Profile()
profiler.enable()
result = fibonacci(30)
profiler.disable()
profiler.print_stats(sort="cumulative")
```

Output columns:
- `ncalls` — number of calls
- `tottime` — total time spent in the function (excluding sub-calls)
- `cumtime` — cumulative time (including sub-calls)
- `percall` — time per call

From the command line:

```bash
python -m cProfile -s cumulative my_script.py
```

### line_profiler Concepts

`line_profiler` shows time spent on each individual line of a function. It requires
installing the `line_profiler` package.

```python
# Install: pip install line_profiler

# Decorate functions you want to profile:
@profile  # This decorator is added by line_profiler
def process_data(data):
    result = []                        # Line 1
    for item in data:                  # Line 2
        transformed = item ** 2        # Line 3
        if transformed > 100:          # Line 4
            result.append(transformed) # Line 5
    return result                      # Line 6
```

Run with:

```bash
kernprof -l -v my_script.py
```

Output shows time per line, hits (number of executions), and percentage of total
function time — extremely useful for identifying which specific line is the bottleneck.

---

## Python Internals

Understanding how CPython works under the hood helps write more efficient code and
debug subtle issues.

### Reference Counting

CPython uses reference counting as its primary memory management strategy. Every
object has a reference count tracking how many names point to it.

```python
import sys

a = [1, 2, 3]
print(sys.getrefcount(a))  # 2 (one for 'a', one for getrefcount argument)

b = a
print(sys.getrefcount(a))  # 3 (a, b, and getrefcount argument)

del b
print(sys.getrefcount(a))  # 2 again

# When the count reaches 0, the object is immediately deallocated.
```

### Garbage Collection

Reference counting cannot detect reference cycles. Python has a cyclic garbage
collector to handle them.

```python
import gc

# Create a reference cycle
class Node:
    def __init__(self):
        self.ref = None

a = Node()
b = Node()
a.ref = b
b.ref = a  # Cycle: a -> b -> a

del a, b   # Reference counts are 1 (from cycle), not 0
gc.collect()  # Cyclic GC detects and collects the cycle

# Inspect GC state
print(gc.get_count())       # (gen0_count, gen1_count, gen2_count)
print(gc.get_threshold())   # Thresholds that trigger collection
```

The garbage collector uses a generational scheme with three generations (0, 1, 2).
New objects start in generation 0. Objects that survive a collection are promoted to
the next generation. Higher generations are collected less frequently.

### Interning

CPython interns (caches and reuses) certain immutable objects for efficiency.

```python
# Small integers (-5 to 256) are interned
a = 256
b = 256
print(a is b)  # True — same object

a = 257
b = 257
print(a is b)  # False — different objects (outside interning range)

# Short strings that look like identifiers are interned
a = "hello"
b = "hello"
print(a is b)  # True — interned

a = "hello world"
b = "hello world"
print(a is b)  # May be False — contains space, not interned

# You can manually intern strings
import sys
a = sys.intern("hello world")
b = sys.intern("hello world")
print(a is b)  # True — manually interned
```

**Important:** Never rely on interning for equality checks. Always use `==` for
value comparison and `is` only for identity (e.g., `is None`).

### \_\_dict\_\_ vs \_\_slots\_\_

```python
import sys

class WithDict:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class WithSlots:
    __slots__ = ("x", "y")
    def __init__(self, x, y):
        self.x = x
        self.y = y

d = WithDict(1, 2)
s = WithSlots(1, 2)

# __dict__ stores attributes in a dictionary
print(d.__dict__)   # {'x': 1, 'y': 2}
d.z = 3             # Can add new attributes dynamically

# __slots__ uses fixed descriptors — no __dict__
# print(s.__dict__)  # AttributeError: no __dict__
# s.z = 3           # AttributeError: no attribute 'z'

# Memory comparison
print(sys.getsizeof(d) + sys.getsizeof(d.__dict__))  # ~200+ bytes
print(sys.getsizeof(s))                                # ~56 bytes
```

When to use `__slots__`:
- You create millions of instances (e.g., data points, records).
- You know the exact set of attributes upfront.
- You do not need dynamic attribute assignment.

When to stick with `__dict__`:
- You need flexibility (dynamic attributes, monkey-patching).
- The class has few instances.
- You use features that require `__dict__` (e.g., `__getattr__` tricks).

---

## Design Patterns in Python

Design patterns are reusable solutions to common problems. Python's dynamic nature
makes many patterns simpler than in static languages.

### Singleton

Ensure a class has only one instance.

```python
class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, value=None):
        # __init__ is called every time Singleton() is called,
        # so guard against re-initialization if needed.
        if not hasattr(self, "_initialized"):
            self.value = value
            self._initialized = True

a = Singleton("first")
b = Singleton("second")
print(a is b)       # True
print(a.value)      # "first" — not overwritten
```

A simpler Pythonic approach uses a module-level instance, since modules are singletons:

```python
# config.py
class _Config:
    def __init__(self):
        self.debug = False
        self.db_url = "sqlite:///default.db"

config = _Config()  # Module-level singleton

# Usage:
# from config import config
# config.debug = True
```

### Factory

Create objects without specifying the exact class.

```python
class Serializer:
    def serialize(self, data: dict) -> str:
        raise NotImplementedError

class JSONSerializer(Serializer):
    def serialize(self, data: dict) -> str:
        import json
        return json.dumps(data)

class XMLSerializer(Serializer):
    def serialize(self, data: dict) -> str:
        items = "".join(f"<{k}>{v}</{k}>" for k, v in data.items())
        return f"<root>{items}</root>"

def create_serializer(fmt: str) -> Serializer:
    """Factory function."""
    serializers = {
        "json": JSONSerializer,
        "xml": XMLSerializer,
    }
    cls = serializers.get(fmt)
    if cls is None:
        raise ValueError(f"Unknown format: {fmt}")
    return cls()

s = create_serializer("json")
print(s.serialize({"name": "Alice"}))  # {"name": "Alice"}
```

### Observer

Objects subscribe to events and get notified when they occur.

```python
class EventEmitter:
    def __init__(self):
        self._listeners: dict[str, list[callable]] = {}

    def on(self, event: str, callback: callable) -> None:
        self._listeners.setdefault(event, []).append(callback)

    def emit(self, event: str, *args, **kwargs) -> None:
        for callback in self._listeners.get(event, []):
            callback(*args, **kwargs)

    def off(self, event: str, callback: callable) -> None:
        if event in self._listeners:
            self._listeners[event].remove(callback)

# Usage
emitter = EventEmitter()

def on_data(data):
    print(f"Received: {data}")

def on_error(error):
    print(f"Error: {error}")

emitter.on("data", on_data)
emitter.on("error", on_error)
emitter.emit("data", "hello")   # Received: hello
emitter.emit("error", "oops")   # Error: oops
```

### Strategy

Select an algorithm at runtime by passing it as a function or callable.

```python
from typing import Callable

# In Python, functions are first-class — no need for a Strategy interface.

def sort_by_name(items: list[dict]) -> list[dict]:
    return sorted(items, key=lambda x: x["name"])

def sort_by_price(items: list[dict]) -> list[dict]:
    return sorted(items, key=lambda x: x["price"])

def sort_by_rating(items: list[dict]) -> list[dict]:
    return sorted(items, key=lambda x: x["rating"], reverse=True)

def display_products(
    products: list[dict],
    sort_strategy: Callable[[list[dict]], list[dict]],
) -> list[dict]:
    """Display products using the chosen sorting strategy."""
    return sort_strategy(products)

products = [
    {"name": "Widget", "price": 25.99, "rating": 4.5},
    {"name": "Gadget", "price": 49.99, "rating": 4.8},
    {"name": "Doohickey", "price": 9.99, "rating": 3.9},
]

by_price = display_products(products, sort_by_price)
print([p["name"] for p in by_price])  # ['Doohickey', 'Widget', 'Gadget']

by_rating = display_products(products, sort_by_rating)
print([p["name"] for p in by_rating])  # ['Gadget', 'Widget', 'Doohickey']
```

The Strategy pattern in Python often reduces to "pass a function." No abstract base
class or interface ceremony is needed — just accept a callable.

---

## Exercises

- [ex01_descriptors.py](exercises/ex01_descriptors.py) -- Validated and Bounded descriptors
- [ex02_metaclasses.py](exercises/ex02_metaclasses.py) -- Registry and validation metaclasses
- [ex03_type_hints.py](exercises/ex03_type_hints.py) -- Generic functions, typed stacks, parsing
- [ex04_testing_patterns.py](exercises/ex04_testing_patterns.py) -- Statistics, email parsing, rate limiting

Solutions are in the [solutions/](solutions/) directory.
