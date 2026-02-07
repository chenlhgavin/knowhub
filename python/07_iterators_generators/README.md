# Chapter 07: Iterators and Generators

Iterators and generators are at the heart of Python's approach to processing
sequences of data. They enable lazy evaluation, memory-efficient pipelines, and
elegant solutions to problems involving potentially infinite data streams.

---

## 1. The Iteration Protocol

Python's `for` loop works with any object that implements the **iteration
protocol** -- two dunder methods:

| Method | Purpose |
|---|---|
| `__iter__()` | Return the iterator object itself (or a new one). |
| `__next__()` | Return the next value, or raise `StopIteration` when exhausted. |

An **iterable** is any object whose `__iter__()` returns an iterator.
An **iterator** is an object that implements both `__iter__()` and `__next__()`.

```python
class CountUp:
    """Iterator that counts from 1 to limit."""

    def __init__(self, limit: int):
        self.limit = limit
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        self.current += 1
        if self.current > self.limit:
            raise StopIteration
        return self.current

for n in CountUp(3):
    print(n)  # 1, 2, 3
```

Under the hood a `for` loop does roughly this:

```python
it = iter(obj)          # calls obj.__iter__()
while True:
    try:
        value = next(it)  # calls it.__next__()
    except StopIteration:
        break
```

---

## 2. Building Custom Iterators

A common pattern is to separate the **iterable** (the collection) from the
**iterator** (the cursor). This allows multiple independent iterations over the
same data:

```python
class Sentence:
    def __init__(self, text: str):
        self.words = text.split()

    def __iter__(self):
        return SentenceIterator(self.words)

class SentenceIterator:
    def __init__(self, words):
        self.words = words
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.words):
            raise StopIteration
        word = self.words[self.index]
        self.index += 1
        return word

s = Sentence("hello world")
list(s)  # ['hello', 'world']
list(s)  # ['hello', 'world']  -- works again because __iter__ creates a new iterator
```

---

## 3. The `iter()` Built-in with a Sentinel Value

`iter()` has a two-argument form: `iter(callable, sentinel)`. It calls the
callable repeatedly until the return value equals the sentinel, then raises
`StopIteration`.

```python
import random

random.seed(42)

# Roll a die until we get a 6
rolls = iter(lambda: random.randint(1, 6), 6)
print(list(rolls))  # all rolls before the first 6

# Read fixed-size blocks from a file
with open("data.bin", "rb") as f:
    for block in iter(lambda: f.read(64), b""):
        process(block)
```

---

## 4. Generators: `yield` and Generator Functions

A **generator function** contains one or more `yield` expressions. Calling it
does not execute the body -- it returns a **generator object** (a lazy
iterator).

```python
def countdown(n):
    while n > 0:
        yield n
        n -= 1

gen = countdown(3)
print(type(gen))   # <class 'generator'>
print(next(gen))   # 3
print(next(gen))   # 2
print(next(gen))   # 1
# next(gen) -> StopIteration
```

**Key differences from regular functions:**

| Regular function | Generator function |
|---|---|
| Runs to completion on call | Suspends at each `yield` |
| Returns a single value via `return` | Yields multiple values lazily |
| `return` ends execution | `return` (or falling off the end) raises `StopIteration` |
| State is lost after return | State is preserved between `next()` calls |

---

## 5. Generator Expressions

Generator expressions look like list comprehensions but use parentheses
instead of brackets. They produce a generator object -- nothing is computed
until you iterate.

```python
# List comprehension -- builds the entire list in memory
squares_list = [x ** 2 for x in range(1_000_000)]

# Generator expression -- produces values on demand
squares_gen = (x ** 2 for x in range(1_000_000))

# When passed as the sole argument to a function the extra parens are optional
total = sum(x ** 2 for x in range(1_000_000))
```

---

## 6. `yield from` for Delegating to Sub-generators

`yield from` delegates iteration to another iterable, forwarding all values
transparently:

```python
def flatten(nested):
    for item in nested:
        if isinstance(item, list):
            yield from flatten(item)  # delegate recursively
        else:
            yield item

list(flatten([1, [2, [3, 4], 5], 6]))
# [1, 2, 3, 4, 5, 6]
```

Without `yield from` you would need an explicit loop:

```python
# Equivalent but more verbose
for value in flatten(item):
    yield value
```

`yield from` also properly forwards `.send()`, `.throw()`, and `.close()`
to the sub-generator, which matters for coroutine-style code.

---

## 7. Lazy Evaluation: Memory Efficiency and Infinite Sequences

Generators compute values **on demand**. This means:

- **Memory efficiency**: only one value is in memory at a time.
- **Infinite sequences**: you can model sequences that never end.

```python
def naturals(start=0):
    """Infinite sequence of natural numbers."""
    n = start
    while True:
        yield n
        n += 1

# Take the first 5 even numbers
evens = (x for x in naturals() if x % 2 == 0)
first_five = [next(evens) for _ in range(5)]
print(first_five)  # [0, 2, 4, 6, 8]
```

Processing a 10 GB log file line by line with generators uses almost no
memory regardless of file size:

```python
def read_lines(path):
    with open(path) as f:
        for line in f:
            yield line.strip()

def grep(pattern, lines):
    for line in lines:
        if pattern in line:
            yield line

matches = grep("ERROR", read_lines("/var/log/app.log"))
for m in matches:
    print(m)
```

---

## 8. `itertools` Module Essentials

The `itertools` module provides fast, memory-efficient building blocks for
iterator-based programming.

### Infinite iterators

```python
from itertools import count, cycle, repeat

# count(start, step) -- infinite counter
list(zip(count(10, 2), "abc"))  # [(10, 'a'), (12, 'b'), (14, 'c')]

# cycle(iterable) -- repeat an iterable forever
from itertools import islice
list(islice(cycle([1, 2, 3]), 7))  # [1, 2, 3, 1, 2, 3, 1]

# repeat(value, times) -- repeat a value (infinite if times omitted)
list(repeat("x", 4))  # ['x', 'x', 'x', 'x']
```

### Finite iterators

```python
from itertools import chain, islice, takewhile, dropwhile, accumulate

# chain(*iterables) -- concatenate iterables
list(chain([1, 2], [3, 4], [5]))  # [1, 2, 3, 4, 5]

# islice(iterable, stop) or islice(iterable, start, stop, step)
list(islice(range(100), 5, 15, 3))  # [5, 8, 11, 14]

# takewhile(predicate, iterable) -- yield while predicate is True
list(takewhile(lambda x: x < 5, [1, 3, 5, 2, 4]))  # [1, 3]

# dropwhile(predicate, iterable) -- drop while predicate is True, then yield the rest
list(dropwhile(lambda x: x < 5, [1, 3, 5, 2, 4]))  # [5, 2, 4]

# accumulate(iterable, func) -- running accumulation (default: addition)
list(accumulate([1, 2, 3, 4]))           # [1, 3, 6, 10]
list(accumulate([1, 2, 3, 4], max))      # [1, 2, 3, 4]
```

### Grouping

```python
from itertools import groupby

# groupby(iterable, key) -- group consecutive elements with the same key
# IMPORTANT: data must be sorted by the key first!
data = sorted(["apple", "avocado", "banana", "blueberry", "cherry"], key=lambda w: w[0])
for letter, words in groupby(data, key=lambda w: w[0]):
    print(letter, list(words))
# a ['apple', 'avocado']
# b ['banana', 'blueberry']
# c ['cherry']
```

### Combinatoric iterators

```python
from itertools import product, combinations, permutations

# product(*iterables, repeat=1) -- Cartesian product
list(product("AB", [1, 2]))
# [('A', 1), ('A', 2), ('B', 1), ('B', 2)]

# combinations(iterable, r) -- r-length subsequences without repetition
list(combinations([1, 2, 3], 2))
# [(1, 2), (1, 3), (2, 3)]

# permutations(iterable, r) -- r-length orderings
list(permutations([1, 2, 3], 2))
# [(1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2)]
```

---

## 9. Generator-Based Pipelines

Generators compose naturally into data-processing pipelines where each stage
pulls data lazily from the previous one:

```python
import csv
from itertools import islice

def read_csv(path):
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row

def filter_active(rows):
    for row in rows:
        if row["status"] == "active":
            yield row

def extract_emails(rows):
    for row in rows:
        yield row["email"]

# Build pipeline -- nothing executes until we iterate
pipeline = extract_emails(filter_active(read_csv("users.csv")))

# Pull only what we need
first_10 = list(islice(pipeline, 10))
```

Each stage processes one record at a time. The entire file is never loaded
into memory. If we only need 10 results, only roughly 10 records flow through
the pipeline.

---

## 10. Comparison: List Comprehension vs Generator Expression

```python
# List comprehension -- eager, stores all values
[x ** 2 for x in range(10)]   # -> [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# Generator expression -- lazy, yields values on demand
(x ** 2 for x in range(10))   # -> <generator object ...>
```

| Aspect | List comprehension | Generator expression |
|---|---|---|
| Syntax | `[expr for ...]` | `(expr for ...)` |
| Evaluation | Eager -- builds full list | Lazy -- one value at a time |
| Memory | O(n) | O(1) |
| Reusable | Yes (iterate multiple times) | No (exhausted after one pass) |
| Subscriptable | Yes (`result[3]`) | No |
| Best for | Small/medium data, need random access | Large/infinite data, single pass |

**Rule of thumb**: use a generator expression when you only need to iterate
once and the data is large. Use a list comprehension when you need the result
as a concrete list or will iterate multiple times.
