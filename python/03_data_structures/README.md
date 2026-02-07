# Chapter 03: Data Structures

Python's built-in data structures are powerful, flexible, and optimized. Mastering
them is essential for writing idiomatic Python code.

---

## 1. Lists

A **list** is an ordered, mutable sequence of arbitrary objects.

### Creation

```python
empty = []
nums = [1, 2, 3]
mixed = [1, "two", 3.0, [4]]
from_range = list(range(5))        # [0, 1, 2, 3, 4]
from_string = list("hello")        # ['h', 'e', 'l', 'l', 'o']
```

### Indexing and Slicing

```python
a = [10, 20, 30, 40, 50]

a[0]        # 10       first element
a[-1]       # 50       last element
a[1:3]      # [20, 30] start inclusive, stop exclusive
a[:2]       # [10, 20] from beginning
a[2:]       # [30, 40, 50] to end
a[::2]      # [10, 30, 50] every second element
a[::-1]     # [50, 40, 30, 20, 10] reversed copy
```

### Common Methods

```python
a = [3, 1, 4]

a.append(5)            # [3, 1, 4, 5]        add one element at the end
a.extend([6, 7])       # [3, 1, 4, 5, 6, 7]  add all elements from iterable
a.insert(0, 0)         # [0, 3, 1, 4, 5, 6, 7] insert at index
a.remove(0)            # [3, 1, 4, 5, 6, 7]  remove first occurrence
val = a.pop()          # val=7, a=[3, 1, 4, 5, 6]  remove & return last
val = a.pop(1)         # val=1, a=[3, 4, 5, 6]     remove & return at index

a.sort()               # [3, 4, 5, 6]  in-place sort (returns None)
a.reverse()            # [6, 5, 4, 3]  in-place reverse (returns None)

# sort() vs sorted()
original = [3, 1, 2]
new_list = sorted(original)   # new_list=[1,2,3], original unchanged
original.sort()               # original=[1,2,3], returns None
```

### List as a Stack (LIFO)

```python
stack = []
stack.append("a")   # push
stack.append("b")
stack.pop()          # "b" -- last in, first out
```

> **Tip:** For a queue (FIFO), use `collections.deque` instead of a list.
> `list.pop(0)` is O(n); `deque.popleft()` is O(1).

---

## 2. Tuples

A **tuple** is an ordered, **immutable** sequence.

### Creation and Immutability

```python
t = (1, 2, 3)
t = 1, 2, 3           # parentheses are optional (tuple packing)
single = (42,)         # trailing comma required for single-element tuple
not_a_tuple = (42)     # this is just the integer 42

t[0] = 99             # TypeError -- tuples cannot be modified
```

### Packing and Unpacking

```python
# Packing
point = 3, 4

# Unpacking
x, y = point          # x=3, y=4

# Swap without temp variable
a, b = 1, 2
a, b = b, a            # a=2, b=1

# Ignore values
_, y, _ = (1, 2, 3)    # y=2

# Extended unpacking
first, *rest = [1, 2, 3, 4]   # first=1, rest=[2,3,4]
first, *mid, last = [1, 2, 3, 4]  # first=1, mid=[2,3], last=4
```

### Named Tuples

```python
from collections import namedtuple

Point = namedtuple("Point", ["x", "y"])
p = Point(3, 4)
print(p.x, p.y)       # 3 4
print(p[0], p[1])     # 3 4  -- still indexable

# typing.NamedTuple (modern style)
from typing import NamedTuple

class Point(NamedTuple):
    x: float
    y: float

p = Point(3.0, 4.0)
```

---

## 3. Dictionaries

A **dict** maps unique, hashable keys to arbitrary values.

### Creation

```python
d = {"a": 1, "b": 2}
d = dict(a=1, b=2)
d = dict([("a", 1), ("b", 2)])
d = {k: k**2 for k in range(5)}   # {0:0, 1:1, 2:4, 3:9, 4:16}
```

### Access

```python
d = {"x": 10, "y": 20}

d["x"]                 # 10
d["z"]                 # KeyError

d.get("z")             # None (no error)
d.get("z", 0)          # 0 (default value)
```

### Key Methods

```python
d = {"a": 1, "b": 2, "c": 3}

list(d.keys())         # ["a", "b", "c"]
list(d.values())       # [1, 2, 3]
list(d.items())        # [("a", 1), ("b", 2), ("c", 3)]

d.setdefault("d", 4)  # inserts "d":4, returns 4
d.setdefault("a", 99) # key exists, returns 1, dict unchanged

d.update({"a": 100, "e": 5})   # merge another dict in
d |= {"f": 6}                  # merge operator (Python 3.9+)
merged = d | {"g": 7}          # creates new merged dict (3.9+)
```

### Ordering Guarantee (Python 3.7+)

Since Python 3.7, dictionaries **preserve insertion order** as part of the
language specification (it was an implementation detail in CPython 3.6).

### defaultdict

```python
from collections import defaultdict

counts = defaultdict(int)      # missing keys default to 0
counts["apple"] += 1           # no KeyError

groups = defaultdict(list)     # missing keys default to []
groups["fruit"].append("apple")
```

---

## 4. Sets

A **set** is an unordered collection of unique, hashable elements.

### Creation

```python
s = {1, 2, 3}
s = set([1, 2, 2, 3])     # {1, 2, 3} -- duplicates removed
empty_set = set()          # {} creates an empty dict, not a set!
```

### Operations

```python
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

a | b          # {1, 2, 3, 4, 5, 6}   union
a & b          # {3, 4}                intersection
a - b          # {1, 2}                difference (in a but not in b)
a ^ b          # {1, 2, 5, 6}          symmetric difference

a.issubset(b)       # False
a.issuperset(b)     # False
a.isdisjoint(b)     # False (they share 3, 4)
```

### Modifying Sets

```python
s = {1, 2}
s.add(3)           # {1, 2, 3}
s.discard(99)      # no error if absent
s.remove(99)       # KeyError if absent
s.pop()            # remove and return an arbitrary element
```

### frozenset

An **immutable** set. Can be used as a dict key or as an element of another set.

```python
fs = frozenset([1, 2, 3])
# fs.add(4)  -> AttributeError
d = {fs: "immutable key"}   # works
```

---

## 5. Comprehensions

Comprehensions provide a concise syntax for creating collections from iterables.

### List Comprehension

```python
squares = [x**2 for x in range(10)]
evens = [x for x in range(20) if x % 2 == 0]
```

### Dict Comprehension

```python
square_map = {x: x**2 for x in range(5)}
# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

inverted = {v: k for k, v in square_map.items()}
```

### Set Comprehension

```python
unique_lengths = {len(w) for w in ["apple", "banana", "pear", "fig"]}
# {5, 6, 4, 3}
```

### Nested Comprehension

```python
# Flatten a 2D list
matrix = [[1, 2], [3, 4], [5, 6]]
flat = [x for row in matrix for x in row]
# [1, 2, 3, 4, 5, 6]

# Read order: for row in matrix -> for x in row -> x

# Multiplication table
table = {(i, j): i * j for i in range(1, 4) for j in range(1, 4)}
```

> **Guideline:** If a comprehension becomes hard to read (more than ~2 nested
> loops or complex conditions), use a regular for-loop instead.

---

## 6. Unpacking

### Iterable Unpacking with `*`

```python
a, *rest = [1, 2, 3, 4]       # a=1, rest=[2,3,4]
*head, last = [1, 2, 3, 4]    # head=[1,2,3], last=4
first, *mid, last = "abcde"   # first='a', mid=['b','c','d'], last='e'

# Merge lists
merged = [*[1, 2], *[3, 4]]   # [1, 2, 3, 4]
```

### Dictionary Unpacking with `**`

```python
defaults = {"color": "red", "size": 10}
overrides = {"size": 20, "weight": 5}
merged = {**defaults, **overrides}
# {"color": "red", "size": 20, "weight": 5}
```

### Swapping

```python
a, b = b, a               # swap two values
a, b, c = c, a, b         # rotate three values
```

---

## 7. Shallow vs Deep Copy

### Assignment (no copy)

```python
a = [1, [2, 3]]
b = a              # b is the SAME object
b[0] = 99          # a is also changed: [99, [2, 3]]
```

### Shallow Copy

Copies the outer container but **not** nested objects.

```python
import copy

a = [1, [2, 3]]
b = a.copy()           # or list(a), a[:], copy.copy(a)
b[0] = 99              # a is unchanged: [1, [2, 3]]
b[1].append(4)         # a IS changed:   [1, [2, 3, 4]]  (shared inner list)
```

### Deep Copy

Recursively copies everything.

```python
import copy

a = [1, [2, 3]]
b = copy.deepcopy(a)
b[1].append(4)         # a is unchanged: [1, [2, 3]]
```

---

## 8. When to Use Which Data Structure

| Need | Use | Why |
|---|---|---|
| Ordered, mutable sequence | `list` | General-purpose sequence |
| Immutable sequence / record | `tuple` | Hashable, lighter than list |
| Key-value mapping | `dict` | O(1) average lookup by key |
| Unique elements, membership testing | `set` | O(1) average membership test |
| Ordered unique elements | `dict.fromkeys()` | Preserves insertion order (3.7+) |
| Default values on missing keys | `defaultdict` | Avoids repeated `setdefault` calls |
| Immutable set (for hashing) | `frozenset` | Usable as dict key or set element |
| Fixed fields with names | `namedtuple` / `NamedTuple` | Self-documenting, lightweight |
| Stack (LIFO) | `list` | `append()` / `pop()` are O(1) |
| Queue (FIFO) | `collections.deque` | O(1) append and popleft |

---

## Exercises

The `exercises/` directory contains five exercise files covering lists, tuples,
dictionaries, sets, and comprehensions. Each file has function stubs with type
hints and assert-based tests in the `__main__` block. Implement each function
so that all assertions pass.

Solutions are in the `solutions/` directory.
