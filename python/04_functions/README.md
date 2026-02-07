# Chapter 04 — Functions

Functions are the primary building blocks for organizing and reusing code in Python.
This chapter covers everything from basic definitions to closures and higher-order
functions.

---

## 1. Defining Functions

Use `def` to define a function. Use `return` to send a value back to the caller.

```python
def add(a, b):
    return a + b

result = add(3, 4)  # 7
```

A function without an explicit `return` returns `None`.

### Multiple Return Values

Python functions can return multiple values as a tuple:

```python
def divide(a, b):
    quotient = a // b
    remainder = a % b
    return quotient, remainder

q, r = divide(17, 5)  # q=3, r=2
```

---

## 2. Parameters

### Positional and Keyword Arguments

```python
def greet(name, greeting):
    return f"{greeting}, {name}!"

greet("Alice", "Hello")           # positional
greet(greeting="Hi", name="Bob")  # keyword (order doesn't matter)
```

### Default Values

```python
def power(base, exp=2):
    return base ** exp

power(3)     # 9  (exp defaults to 2)
power(3, 3)  # 27
```

> **Warning:** Never use a mutable object (list, dict) as a default value. Use `None`
> instead and create the object inside the function body.

---

## 3. `*args` and `**kwargs`

`*args` collects extra positional arguments into a tuple.
`**kwargs` collects extra keyword arguments into a dict.

```python
def log(*args, **kwargs):
    print("args:", args)
    print("kwargs:", kwargs)

log(1, 2, 3, level="INFO")
# args: (1, 2, 3)
# kwargs: {'level': 'INFO'}
```

You can also use `*` and `**` to unpack when *calling* a function:

```python
def add(a, b, c):
    return a + b + c

values = [1, 2, 3]
add(*values)  # 6
```

---

## 4. Positional-Only and Keyword-Only Parameters

Python 3.8+ supports `/` (positional-only) and `*` (keyword-only) markers:

```python
def example(pos_only, /, normal, *, kw_only):
    print(pos_only, normal, kw_only)

example(1, 2, kw_only=3)        # OK
example(1, normal=2, kw_only=3) # OK
example(pos_only=1, normal=2, kw_only=3)  # TypeError
example(1, 2, 3)                           # TypeError
```

- Parameters before `/` must be passed positionally.
- Parameters after `*` must be passed as keyword arguments.

---

## 5. Scope — The LEGB Rule

Python resolves names in this order:

| Level       | Description                              |
|-------------|------------------------------------------|
| **L**ocal   | Names assigned inside the current function |
| **E**nclosing | Names in enclosing function scopes (closures) |
| **G**lobal  | Names at the module level                |
| **B**uilt-in | Names in the `builtins` module (`len`, `print`, ...) |

```python
x = "global"

def outer():
    x = "enclosing"

    def inner():
        x = "local"
        print(x)  # "local"

    inner()

outer()
```

### `global` and `nonlocal` Keywords

```python
count = 0

def increment():
    global count
    count += 1

def outer():
    total = 0

    def add(n):
        nonlocal total
        total += n
        return total

    return add
```

- `global` lets you modify a module-level variable from inside a function.
- `nonlocal` lets you modify a variable from an enclosing (but non-global) scope.

---

## 6. First-Class Functions

Functions in Python are objects. You can assign them to variables, store them in
data structures, and pass them as arguments.

```python
def shout(text):
    return text.upper()

def whisper(text):
    return text.lower()

def apply(func, text):
    return func(text)

apply(shout, "hello")    # "HELLO"
apply(whisper, "HELLO")  # "hello"
```

### Returning Functions

```python
def make_multiplier(n):
    def multiplier(x):
        return x * n
    return multiplier

double = make_multiplier(2)
double(5)  # 10
```

---

## 7. Lambda Expressions

A lambda is a small anonymous function limited to a single expression:

```python
square = lambda x: x ** 2
square(4)  # 16

# Common use: as a key function
names = ["Alice", "Bob", "Charlie"]
sorted(names, key=lambda n: len(n))  # ['Bob', 'Alice', 'Charlie']
```

Lambdas are best used for short, throwaway functions. For anything complex, prefer
a named `def`.

---

## 8. Closures

A closure is a function that remembers the variables from its enclosing scope even
after that scope has finished executing.

```python
def make_counter(start=0):
    count = start

    def counter():
        nonlocal count
        value = count
        count += 1
        return value

    return counter

c = make_counter(10)
c()  # 10
c()  # 11
c()  # 12
```

Closures are the mechanism behind decorators, factory functions, and callback
patterns.

---

## 9. Recursion Basics

A recursive function calls itself. Every recursive function needs a **base case**
to stop the recursion.

```python
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

factorial(5)  # 120
```

```python
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
```

> **Note:** Python has a default recursion limit of 1000. For deep recursion,
> consider iterative solutions or `sys.setrecursionlimit()`.

---

## 10. Docstrings and Type Hints

### Docstrings

Use triple-quoted strings as the first statement in a function:

```python
def gcd(a: int, b: int) -> int:
    """Return the greatest common divisor of a and b.

    Uses the Euclidean algorithm.

    Args:
        a: First positive integer.
        b: Second positive integer.

    Returns:
        The greatest common divisor.
    """
    while b:
        a, b = b, a % b
    return a
```

### Type Hints

Type hints document expected types and enable static analysis tools like `mypy`:

```python
from typing import Callable

def apply_twice(func: Callable[[int], int], value: int) -> int:
    return func(func(value))
```

Common hint types: `int`, `str`, `float`, `bool`, `list[int]`, `dict[str, int]`,
`tuple[int, ...]`, `Callable[[ArgTypes], ReturnType]`, `Optional[int]`.

---

## 11. Common Built-in Higher-Order Functions

### `map(func, iterable)`

Applies `func` to every item and returns an iterator:

```python
list(map(str.upper, ["hello", "world"]))  # ['HELLO', 'WORLD']
list(map(lambda x: x * 2, [1, 2, 3]))    # [2, 4, 6]
```

### `filter(func, iterable)`

Returns an iterator of items for which `func` returns `True`:

```python
list(filter(lambda x: x > 0, [-2, -1, 0, 1, 2]))  # [1, 2]
```

### `sorted(iterable, key=..., reverse=...)`

Returns a new sorted list. The `key` parameter accepts a function:

```python
students = [("Alice", 88), ("Bob", 95), ("Charlie", 72)]
sorted(students, key=lambda s: s[1])
# [('Charlie', 72), ('Alice', 88), ('Bob', 95)]

sorted(students, key=lambda s: s[1], reverse=True)
# [('Bob', 95), ('Alice', 88), ('Charlie', 72)]
```

---

## Exercises

| File | Topics |
|------|--------|
| `ex01_basics.py` | Function definitions, defaults, multiple returns, factory functions |
| `ex02_args_kwargs.py` | `*args`, `**kwargs`, flexible parameter handling |
| `ex03_lambda_hof.py` | Lambdas, composition, reimplementing `map` and `filter` |
| `ex04_closures.py` | Closures, mutable state, memoization |
