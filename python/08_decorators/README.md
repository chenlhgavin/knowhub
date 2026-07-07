# Chapter 08: Decorators and Context Managers

## What Decorators Are

A decorator is syntactic sugar for wrapping a function (or class) with another
callable. When you write:

```python
@decorator
def func():
    pass
```

Python translates this to:

```python
def func():
    pass
func = decorator(func)
```

The decorator receives the original function, typically wraps it with additional
behavior, and returns the wrapper. This pattern keeps cross-cutting concerns
(logging, timing, access control) separate from business logic.

---

## Simple Function Decorators

A basic decorator is a function that takes a function and returns a new function:

```python
def shout(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result.upper()
    return wrapper

@shout
def greet(name):
    return f"hello, {name}"

print(greet("world"))  # HELLO, WORLD
```

The `wrapper` uses `*args, **kwargs` so it works with any signature.

---

## functools.wraps: Preserving Function Metadata

Without `functools.wraps`, the wrapper replaces the original function's
`__name__`, `__doc__`, and other attributes:

```python
import functools

def shout(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result.upper()
    return wrapper

@shout
def greet(name):
    """Greet someone by name."""
    return f"hello, {name}"

print(greet.__name__)  # "greet" (not "wrapper")
print(greet.__doc__)   # "Greet someone by name."
```

Always use `@functools.wraps(func)` on your wrapper functions.

---

## Decorators with Arguments

When a decorator needs parameters, you add an outer function that returns the
actual decorator. This creates the triple-nested pattern:

```python
import functools

def repeat(n):
    """Decorator factory: call the function n times."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = None
            for _ in range(n):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(3)
def say_hello():
    print("Hello!")
    return "done"

say_hello()  # prints "Hello!" three times
```

The call chain is: `repeat(3)` returns `decorator`, then `decorator(say_hello)`
returns `wrapper`.

---

## Stacking Multiple Decorators

Decorators can be stacked. They apply bottom-up (closest to the function first):

```python
@decorator_a
@decorator_b
def func():
    pass

# Equivalent to: func = decorator_a(decorator_b(func))
```

Order matters. If `decorator_b` adds logging and `decorator_a` adds timing, the
timer will include the logging overhead. Reverse them to time only the function.

```python
@timer        # outer: measures total time including logging
@log_calls    # inner: logs before/after the actual call
def process(data):
    pass
```

---

## Class-Based Decorators Using `__call__`

Any callable can be a decorator. A class with `__call__` works:

```python
import functools

class CountCalls:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
        self.call_count = 0

    def __call__(self, *args, **kwargs):
        self.call_count += 1
        return self.func(*args, **kwargs)

@CountCalls
def say_hi():
    print("Hi!")

say_hi()
say_hi()
print(say_hi.call_count)  # 2
```

Class-based decorators are useful when you need to maintain state.

---

## Decorating Classes

Decorators can also wrap classes. A class decorator receives a class and returns
a (possibly modified) class:

```python
def singleton(cls):
    instances = {}
    @functools.wraps(cls, updated=[])
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton
class Database:
    def __init__(self, url):
        self.url = url

db1 = Database("postgres://localhost")
db2 = Database("postgres://localhost")
assert db1 is db2
```

---

## Common Standard Library Decorators

### @staticmethod and @classmethod

```python
class MathUtils:
    base = 10

    @staticmethod
    def add(a, b):
        return a + b

    @classmethod
    def add_to_base(cls, value):
        return cls.base + value

MathUtils.add(2, 3)         # 5 -- no instance needed
MathUtils.add_to_base(5)    # 15 -- receives the class
```

### @property

```python
class Circle:
    def __init__(self, radius):
        self._radius = radius

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("Radius cannot be negative")
        self._radius = value

    @property
    def area(self):
        import math
        return math.pi * self._radius ** 2

c = Circle(5)
print(c.area)     # 78.539...
c.radius = 10     # uses the setter
```

### @functools.lru_cache

Memoizes function results with a Least Recently Used eviction policy:

```python
import functools

@functools.lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

fibonacci(100)  # instant, without cache this would be impossibly slow
print(fibonacci.cache_info())
```

### @functools.total_ordering

Fill in missing comparison methods from `__eq__` and one of `__lt__`, `__gt__`,
`__le__`, or `__ge__`:

```python
import functools

@functools.total_ordering
class Student:
    def __init__(self, name, grade):
        self.name = name
        self.grade = grade

    def __eq__(self, other):
        return self.grade == other.grade

    def __lt__(self, other):
        return self.grade < other.grade

s1 = Student("Alice", 90)
s2 = Student("Bob", 85)
print(s1 > s2)   # True -- generated by total_ordering
print(s1 >= s2)  # True
```

---

## Context Managers: The `with` Statement

Context managers guarantee cleanup. The `with` statement calls `__enter__` on
entry and `__exit__` on exit (even if an exception occurs):

```python
with open("data.txt", "w") as f:
    f.write("hello")
# f is automatically closed here, even if write() raised an exception
```

This replaces fragile try/finally patterns.

---

## Writing Context Managers: `__enter__` / `__exit__`

Implement the context manager protocol with two methods:

```python
class Timer:
    def __enter__(self):
        import time
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        self.elapsed = time.perf_counter() - self._start
        return False  # do not suppress exceptions

with Timer() as t:
    total = sum(range(1_000_000))

print(f"Elapsed: {t.elapsed:.4f}s")
```

`__exit__` receives exception info. Return `True` to suppress the exception,
`False` (or `None`) to let it propagate.

---

## contextlib: Convenient Context Managers

### @contextmanager

Write context managers as generator functions instead of classes:

```python
from contextlib import contextmanager

@contextmanager
def managed_resource(name):
    print(f"Acquiring {name}")
    resource = {"name": name, "active": True}
    try:
        yield resource
    finally:
        resource["active"] = False
        print(f"Releasing {name}")

with managed_resource("db_conn") as r:
    print(r)  # {'name': 'db_conn', 'active': True}
# prints "Releasing db_conn"
```

Everything before `yield` is `__enter__`, everything after is `__exit__`.

### contextlib.suppress

Selectively ignore exceptions:

```python
from contextlib import suppress

with suppress(FileNotFoundError):
    os.remove("nonexistent.txt")
# no exception raised
```

### contextlib.redirect_stdout

Capture stdout output:

```python
from contextlib import redirect_stdout
from io import StringIO

buffer = StringIO()
with redirect_stdout(buffer):
    print("captured!")

print(buffer.getvalue())  # "captured!\n"
```

---

## Real-World Patterns

### Timing

```python
import functools
import time

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper
```

### Logging

```python
import functools
import logging

logger = logging.getLogger(__name__)

def log_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Calling {func.__name__}({args}, {kwargs})")
        result = func(*args, **kwargs)
        logger.info(f"{func.__name__} returned {result}")
        return result
    return wrapper
```

### Retry

```python
import functools
import time

def retry(max_attempts=3, delay=1.0, exceptions=(Exception,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator

@retry(max_attempts=3, delay=0.5, exceptions=(ConnectionError,))
def fetch_data(url):
    ...
```

### Access Control

```python
import functools

def require_role(role):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(user, *args, **kwargs):
            if role not in user.get("roles", []):
                raise PermissionError(f"Role '{role}' required")
            return func(user, *args, **kwargs)
        return wrapper
    return decorator

@require_role("admin")
def delete_user(user, target_id):
    print(f"Deleting user {target_id}")
```
