# Chapter 02: Control Flow

Control flow determines the order in which statements are executed. Python provides
a clean, indentation-based syntax for branching, looping, and pattern matching.

---

## 1. if / elif / else

Python uses `if`, `elif`, and `else` for conditional branching. There are no braces
or parentheses required around the condition -- just a colon and indentation.

```python
temperature = 35

if temperature > 30:
    print("Hot")
elif temperature > 20:
    print("Warm")
elif temperature > 10:
    print("Cool")
else:
    print("Cold")
```

Any expression that evaluates to a truthy or falsy value can be used as a condition.
Falsy values in Python: `False`, `None`, `0`, `0.0`, `""`, `[]`, `{}`, `set()`, `()`.

```python
name = ""

if name:
    print(f"Hello, {name}")
else:
    print("Name is empty")
```

---

## 2. Ternary Expression

Python's ternary (conditional) expression allows inline branching:

```python
x = 10
label = "even" if x % 2 == 0 else "odd"
# label == "even"

# Useful for default values
user_input = ""
name = user_input if user_input else "Anonymous"
```

Ternary expressions can be nested, but doing so hurts readability. Prefer `if/elif/else`
blocks when there are more than two branches.

---

## 3. for Loops

### range()

`range(stop)`, `range(start, stop)`, or `range(start, stop, step)` generates a
sequence of integers.

```python
for i in range(5):          # 0, 1, 2, 3, 4
    print(i)

for i in range(2, 8):       # 2, 3, 4, 5, 6, 7
    print(i)

for i in range(0, 10, 3):   # 0, 3, 6, 9
    print(i)

for i in range(10, 0, -1):  # 10, 9, 8, ... 1
    print(i)
```

### Iterating Over Sequences

Python `for` loops iterate directly over elements, not indices.

```python
fruits = ["apple", "banana", "cherry"]

for fruit in fruits:
    print(fruit)

for char in "hello":
    print(char)

for key, value in {"a": 1, "b": 2}.items():
    print(f"{key} = {value}")
```

### enumerate()

When you need both the index and the value, use `enumerate()`:

```python
colors = ["red", "green", "blue"]

for i, color in enumerate(colors):
    print(f"{i}: {color}")

# Start from a different index
for i, color in enumerate(colors, start=1):
    print(f"{i}: {color}")
```

### zip()

`zip()` iterates over multiple sequences in parallel, stopping at the shortest:

```python
names = ["Alice", "Bob", "Charlie"]
scores = [85, 92, 78]

for name, score in zip(names, scores):
    print(f"{name}: {score}")

# Unequal lengths -- stops at shortest
for a, b in zip([1, 2, 3], [10, 20]):
    print(a, b)  # (1, 10), (2, 20)
```

---

## 4. while Loops, break, continue, else

### while

A `while` loop runs as long as its condition is truthy:

```python
count = 0
while count < 5:
    print(count)
    count += 1
```

### break and continue

`break` exits the loop immediately. `continue` skips to the next iteration.

```python
# break: find the first even number
for n in [1, 3, 4, 7, 8]:
    if n % 2 == 0:
        print(f"First even: {n}")
        break

# continue: skip odd numbers
for n in range(10):
    if n % 2 != 0:
        continue
    print(n)  # 0, 2, 4, 6, 8
```

### else Clause on Loops

The `else` block after a `for` or `while` executes only if the loop completed
without hitting a `break`. This is useful for search patterns.

```python
target = 7
for n in [1, 3, 5, 9]:
    if n == target:
        print("Found!")
        break
else:
    print("Not found")  # This runs because no break occurred
```

---

## 5. match-case (Python 3.10+)

Structural pattern matching goes beyond simple value comparison. It can destructure
sequences, match types, bind variables, and use guards.

### Basic Value Matching

```python
def http_status(code: int) -> str:
    match code:
        case 200:
            return "OK"
        case 404:
            return "Not Found"
        case 500:
            return "Server Error"
        case _:
            return "Unknown"
```

### Sequence and Type Matching

```python
def describe(value):
    match value:
        case []:
            return "empty list"
        case [x]:
            return f"single element: {x}"
        case [x, y]:
            return f"pair: {x}, {y}"
        case [x, *rest]:
            return f"starts with {x}, {len(rest)} more"
        case _:
            return "something else"
```

### Guards

```python
def classify(value):
    match value:
        case int(n) if n > 0:
            return "positive int"
        case int(n) if n < 0:
            return "negative int"
        case int():
            return "zero"
        case _:
            return "not an int"
```

### Matching Tuples (Expression Trees)

```python
def evaluate(expr):
    match expr:
        case ("+", a, b):
            return a + b
        case ("-", a, b):
            return a - b
        case ("*", a, b):
            return a * b
        case ("/", a, b):
            return a / b
```

---

## 6. Walrus Operator `:=`

The walrus operator (`:=`) assigns a value to a variable as part of an expression.
It was introduced in Python 3.8.

```python
# Without walrus operator
line = input()
while line != "quit":
    print(f"You said: {line}")
    line = input()

# With walrus operator -- avoids duplicating the input() call
while (line := input()) != "quit":
    print(f"You said: {line}")
```

Common use cases:

```python
# In list comprehensions -- filter and transform with one computation
data = [1, 5, 12, 3, 18, 7]
results = [y for x in data if (y := x * 2) > 10]
# results == [24, 36, 14]

# In if statements
import re
text = "My phone is 555-1234"
if m := re.search(r"\d{3}-\d{4}", text):
    print(f"Found phone number: {m.group()}")
```

---

## 7. Nested Loops and Common Patterns

### Nested Iteration

```python
# Multiplication table
for i in range(1, 4):
    for j in range(1, 4):
        print(f"{i} x {j} = {i * j}")
```

### Flattening a 2D List

```python
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flat = [elem for row in matrix for elem in row]
# [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

### Matrix Transpose

```python
matrix = [[1, 2, 3], [4, 5, 6]]
transposed = [[row[i] for row in matrix] for i in range(len(matrix[0]))]
# [[1, 4], [2, 5], [3, 6]]
```

### Finding Pairs

```python
from itertools import combinations

numbers = [1, 2, 3, 4, 5]
pairs = [(a, b) for a, b in combinations(numbers, 2) if a + b == 6]
# [(1, 5), (2, 4)]
```

---

## 8. Best Practices

### Avoid Deep Nesting

Deeply nested code is hard to read and maintain. Refactor using early returns,
guard clauses, or helper functions.

```python
# Bad: deep nesting
def process(data):
    if data is not None:
        if len(data) > 0:
            if data[0].isdigit():
                return int(data[0])
            else:
                return -1
        else:
            return -1
    else:
        return -1

# Good: early returns (guard clauses)
def process(data):
    if data is None:
        return -1
    if len(data) == 0:
        return -1
    if not data[0].isdigit():
        return -1
    return int(data[0])
```

### Prefer `for` Over `while` When Possible

`for` loops are less error-prone because they handle iteration automatically.

```python
# Avoid: manual index management
i = 0
while i < len(items):
    print(items[i])
    i += 1

# Prefer: direct iteration
for item in items:
    print(item)
```

### Use Comprehensions for Simple Transformations

```python
# Good for simple cases
squares = [x ** 2 for x in range(10)]

# Use a regular loop for complex logic
results = []
for x in range(10):
    if x % 2 == 0:
        results.append(x ** 2)
    else:
        results.append(x ** 3)
```

### Keep Loop Bodies Small

If a loop body exceeds ~10 lines, extract the body into a function.

---

## Exercises

Work through the exercises in the `exercises/` directory:

| File | Topics |
|------|--------|
| `ex01_conditionals.py` | if/elif/else, ternary expressions |
| `ex02_loops.py` | for loops, while loops, range, break |
| `ex03_patterns.py` | Nested loops, list comprehensions, algorithms |
| `ex04_match_case.py` | Structural pattern matching (Python 3.10+) |

Solutions are in the `solutions/` directory.
