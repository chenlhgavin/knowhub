# Chapter 01: Basics

## Variables and Assignment

Python is dynamically typed -- you never declare a type, the interpreter figures it out at runtime. Every value in Python is an object, including integers and booleans.

```python
x = 42          # int
x = "hello"     # now a str -- same name, different type
y = x           # y points to the same object as x

# Multiple assignment in one line
a, b, c = 1, 2, 3

# Swap without a temp variable
a, b = b, a

# Everything is an object
print(type(42))        # <class 'int'>
print(type(3.14))      # <class 'float'>
print(type(True))      # <class 'bool'>
print(id(x))           # memory address of the object x points to
```

Identity vs. equality:

```python
a = [1, 2, 3]
b = [1, 2, 3]
print(a == b)   # True  -- same value
print(a is b)   # False -- different objects

c = a
print(a is c)   # True  -- same object
```

---

## Numeric Types

### int -- arbitrary precision

Python integers have no fixed size. They grow as needed.

```python
big = 10 ** 100                  # a googol, no overflow
hex_val = 0xFF                   # 255
bin_val = 0b1010                 # 10
oct_val = 0o17                   # 15
readable = 1_000_000             # underscores for readability
```

### float -- IEEE 754 double precision

64-bit floating point. Subject to the usual precision quirks.

```python
pi = 3.14159
sci = 2.5e-3                    # 0.0025
print(0.1 + 0.2)                # 0.30000000000000004
print(0.1 + 0.2 == 0.3)         # False
import math
print(math.isclose(0.1 + 0.2, 0.3))  # True

inf = float('inf')
nan = float('nan')
print(math.isinf(inf))          # True
print(math.isnan(nan))          # True
```

### complex

```python
z = 3 + 4j
print(z.real)       # 3.0
print(z.imag)       # 4.0
print(abs(z))       # 5.0 (magnitude)
```

---

## Strings

Strings are immutable sequences of Unicode characters.

### Creation

```python
s1 = 'single quotes'
s2 = "double quotes"
s3 = '''triple quotes
span multiple lines'''
s4 = r"raw string: \n is literal backslash-n"
```

### Indexing and Slicing

```python
s = "Python"
s[0]       # 'P'
s[-1]      # 'n'
s[1:4]     # 'yth'
s[:3]      # 'Pyt'
s[3:]      # 'hon'
s[::-1]    # 'nohtyP' (reverse)
s[::2]     # 'Pto'    (every 2nd char)
```

### Common Methods

```python
"hello".upper()              # 'HELLO'
"HELLO".lower()              # 'hello'
"  hello  ".strip()          # 'hello'
"hello world".split()        # ['hello', 'world']
"a,b,c".split(",")           # ['a', 'b', 'c']
", ".join(["a", "b", "c"])   # 'a, b, c'
"hello".replace("l", "r")   # 'herro'
"hello".startswith("hel")   # True
"hello".find("ll")          # 2
"hello".count("l")          # 2
"hello".isalpha()           # True
"123".isdigit()             # True
```

### f-strings (formatted string literals)

```python
name = "Alice"
age = 30
print(f"Name: {name}, Age: {age}")
print(f"Next year: {age + 1}")
print(f"Pi: {3.14159:.2f}")          # "Pi: 3.14"
print(f"{'left':<10}|{'right':>10}") # alignment
print(f"{1000000:,}")                 # "1,000,000"
```

---

## Boolean

`bool` is a subclass of `int`. `True` is `1`, `False` is `0`.

```python
print(True + True)    # 2
print(False * 10)     # 0
print(isinstance(True, int))  # True
```

### Truthy and Falsy

These are falsy -- everything else is truthy:

| Falsy value       | Type      |
|--------------------|-----------|
| `False`            | bool      |
| `0`, `0.0`, `0j`  | numeric   |
| `""` (empty str)   | str       |
| `[]`, `()`, `{}`  | containers|
| `set()`            | set       |
| `None`             | NoneType  |

```python
if []:
    print("won't print")

if [1]:
    print("will print")

# bool() to check truthiness
bool(0)       # False
bool(42)      # True
bool("")      # False
bool("hi")    # True
```

---

## Type Conversions

```python
int("42")          # 42
int(3.9)           # 3 (truncates, does NOT round)
int("0xFF", 16)    # 255

float("3.14")      # 3.14
float(42)          # 42.0

str(42)            # "42"
str(3.14)          # "3.14"

bool(0)            # False
bool(1)            # True
bool("")           # False
bool("False")      # True  -- non-empty string is truthy!
```

---

## Operators

### Arithmetic

```python
7 + 3      # 10   addition
7 - 3      # 4    subtraction
7 * 3      # 21   multiplication
7 / 3      # 2.3333...  true division (always float)
7 // 3     # 2    floor division
7 % 3      # 1    modulo
7 ** 3     # 343  exponentiation
-7 // 3    # -3   floors toward negative infinity
-7 % 3     # 2    result has sign of divisor
```

### Comparison

```python
3 == 3     # True
3 != 4     # True
3 < 4      # True
3 <= 3     # True
# Chained comparisons
1 < 2 < 3          # True (same as 1 < 2 and 2 < 3)
1 < 2 > 0          # True
```

### Logical

```python
True and False     # False
True or False      # True
not True           # False

# Short-circuit evaluation
# `and` returns first falsy value, or last value
0 and 42           # 0
1 and 42           # 42

# `or` returns first truthy value, or last value
0 or 42            # 42
"" or "default"    # "default"
```

### Membership

```python
"h" in "hello"           # True
3 in [1, 2, 3]           # True
"key" in {"key": "val"}  # True (checks keys)
5 not in [1, 2, 3]       # True
```

---

## Input/Output

### print()

```python
print("hello")                          # hello
print("a", "b", "c")                    # a b c
print("a", "b", "c", sep="-")          # a-b-c
print("no newline", end="")            # suppress trailing newline
print(f"{'Item':<10} {'Price':>8}")     # formatted columns
```

### input()

`input()` always returns a string.

```python
name = input("Enter your name: ")
age = int(input("Enter your age: "))    # must convert manually
```

---

## Comments and Style Basics

```python
# Single-line comment

"""
This is a docstring, not technically a comment.
Used at the top of modules, classes, and functions.
"""

# Naming conventions (PEP 8):
my_variable = 1          # snake_case for variables and functions
MY_CONSTANT = 3.14       # UPPER_SNAKE_CASE for constants
class MyClass:            # PascalCase for classes
    pass

# Line length: keep under 79 characters (or 88/120 by team convention)
# Indentation: 4 spaces, never tabs
# Blank lines: 2 between top-level definitions, 1 between methods
```
