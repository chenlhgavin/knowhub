# Chapter 06: Modules and Errors

## 1. The Import System

Python's import system lets you organize code into reusable units.

### Basic Imports

```python
# Import the entire module
import math
print(math.sqrt(16))  # 4.0

# Import specific names
from math import sqrt, pi
print(sqrt(16))  # 4.0

# Import with alias
import numpy as np
from collections import defaultdict as dd

# Import everything (generally discouraged)
from math import *
```

### Relative Imports

Inside a package, you can use relative imports to refer to sibling modules:

```python
# Inside mypackage/submodule/utils.py
from . import helpers          # same directory
from .. import config          # parent package
from ..sibling import tools    # sibling package
```

Relative imports only work inside packages and only with the `from` form.

---

## 2. Module Search Path

When you write `import foo`, Python searches these locations in order:

1. `sys.modules` cache (already-imported modules)
2. Built-in modules
3. Directories listed in `sys.path`

```python
import sys
print(sys.path)
# ['',                          <-- current directory
#  '/usr/lib/python3.12',
#  '/usr/lib/python3.12/lib-dynload',
#  '/home/user/.local/lib/python3.12/site-packages',
#  ...]
```

You can extend the search path:

```python
# At runtime
import sys
sys.path.insert(0, "/path/to/my/modules")

# Or via environment variable (before running Python)
# export PYTHONPATH="/path/to/my/modules:$PYTHONPATH"
```

---

## 3. Package Structure

A **package** is a directory containing Python files and (optionally) an `__init__.py`.

```
mypackage/
    __init__.py          # Makes it a package; runs on import
    module_a.py
    module_b.py
    subpackage/
        __init__.py
        module_c.py
```

### `__init__.py`

Executed when the package is imported. Used to expose a public API:

```python
# mypackage/__init__.py
from .module_a import ClassA
from .module_b import function_b

__all__ = ["ClassA", "function_b"]  # Controls `from mypackage import *`
```

### `__all__`

Defines which names are exported by `from module import *`:

```python
# mymodule.py
__all__ = ["public_func", "PublicClass"]

def public_func():
    ...

def _private_helper():
    ...

class PublicClass:
    ...
```

### Namespace Packages (PEP 420)

Packages without `__init__.py`. They allow a single logical package to be
spread across multiple directories. Rarely needed in everyday code.

---

## 4. Creating Your Own Modules and Packages

Any `.py` file is a module. To create a package:

```
calculator/
    __init__.py
    operations.py
    formatting.py
```

```python
# calculator/operations.py
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b
```

```python
# calculator/__init__.py
from .operations import add, multiply
from .formatting import format_result
```

```python
# Usage
from calculator import add, multiply
print(add(2, 3))  # 5
```

Guard top-level side effects with:

```python
if __name__ == "__main__":
    # This only runs when the file is executed directly,
    # not when it is imported.
    main()
```

---

## 5. Exception Hierarchy

Python exceptions form a class hierarchy:

```
BaseException
 +-- SystemExit
 +-- KeyboardInterrupt
 +-- GeneratorExit
 +-- Exception
      +-- StopIteration
      +-- ArithmeticError
      |    +-- ZeroDivisionError
      |    +-- OverflowError
      +-- LookupError
      |    +-- IndexError
      |    +-- KeyError
      +-- OSError
      |    +-- FileNotFoundError
      |    +-- PermissionError
      +-- TypeError
      +-- ValueError
      +-- AttributeError
      +-- RuntimeError
      +-- ...
```

Key rules:
- Catch `Exception`, never `BaseException` (unless you truly need `SystemExit` etc.).
- Catch the most specific exception possible.

---

## 6. try / except / else / finally

```python
try:
    result = int(user_input)
except ValueError as e:
    print(f"Invalid input: {e}")
except (TypeError, KeyError):
    print("Wrong type or missing key")
else:
    # Runs ONLY if no exception was raised
    print(f"Parsed successfully: {result}")
finally:
    # Runs ALWAYS, whether exception occurred or not
    print("Cleanup complete")
```

### How the blocks work together

| Block     | Runs when                              |
|-----------|----------------------------------------|
| `try`     | Always                                 |
| `except`  | Only if a matching exception is raised |
| `else`    | Only if NO exception was raised        |
| `finally` | Always, even if an exception propagates|

---

## 7. Raising Exceptions

### Basic raise

```python
def withdraw(amount):
    if amount <= 0:
        raise ValueError(f"Amount must be positive, got {amount}")
```

### Re-raising

```python
try:
    risky_operation()
except ConnectionError:
    log_error()
    raise  # Re-raises the original exception with its traceback
```

### Exception Chaining (from)

```python
try:
    value = int(raw)
except ValueError as e:
    raise RuntimeError("Failed to parse config") from e
```

This preserves the original exception as `__cause__`, producing a clear
traceback showing both the root cause and the higher-level error.

---

## 8. Custom Exception Classes

```python
class AppError(Exception):
    """Base exception for this application."""
    pass

class ValidationError(AppError):
    """Raised when input validation fails."""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")

class NotFoundError(AppError):
    """Raised when a resource is not found."""
    pass
```

Best practices:
- Inherit from `Exception` (or a custom base).
- Keep a small hierarchy; don't over-engineer.
- Store structured data as attributes for programmatic access.

---

## 9. Context-Appropriate Exception Handling Patterns

### LBYL vs. EAFP

```python
# LBYL (Look Before You Leap) -- sometimes appropriate
if key in mapping:
    value = mapping[key]

# EAFP (Easier to Ask Forgiveness than Permission) -- Pythonic
try:
    value = mapping[key]
except KeyError:
    value = default
```

### Don't silence exceptions blindly

```python
# BAD -- hides bugs
try:
    do_something()
except Exception:
    pass

# GOOD -- handle or log specifically
try:
    do_something()
except SpecificError as e:
    logger.warning("Expected issue: %s", e)
```

### Use context managers for resource cleanup

```python
# Preferred: guarantees the file is closed
with open("data.txt") as f:
    contents = f.read()
```

---

## 10. File I/O

### open() and modes

```python
# Common modes:
# "r"  - read text (default)
# "w"  - write text (truncates)
# "a"  - append text
# "x"  - exclusive create (fails if file exists)
# "rb" - read binary
# "wb" - write binary

with open("output.txt", "w", encoding="utf-8") as f:
    f.write("Hello, world!\n")

with open("output.txt", "r", encoding="utf-8") as f:
    content = f.read()
```

### Reading methods

```python
with open("data.txt", encoding="utf-8") as f:
    full_text = f.read()           # Entire file as one string
    # or
    lines = f.readlines()          # List of lines (with \n)
    # or
    for line in f:                 # Memory-efficient iteration
        process(line.strip())
```

### The `with` statement

The `with` statement invokes a context manager that guarantees cleanup:

```python
with open("file.txt") as f:
    data = f.read()
# f is automatically closed here, even if an exception occurred
```

### Encoding

Always specify `encoding="utf-8"` explicitly. The default encoding is
platform-dependent, which leads to subtle bugs on Windows.

---

## 11. Reading/Writing CSV and JSON

### JSON

```python
import json

data = {"name": "Alice", "scores": [95, 87, 92]}

# Write
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

# Read
with open("data.json", "r", encoding="utf-8") as f:
    loaded = json.load(f)

# Strings
json_str = json.dumps(data)
parsed = json.loads(json_str)
```

### CSV

```python
import csv

# Writing
with open("people.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "age"])
    writer.writeheader()
    writer.writerow({"name": "Alice", "age": 30})
    writer.writerow({"name": "Bob", "age": 25})

# Reading
with open("people.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row["name"], row["age"])
```

---

## 12. pathlib.Path Basics

`pathlib` provides an object-oriented interface for filesystem paths.

```python
from pathlib import Path

# Create paths
p = Path("/home/user/data")
config = Path.home() / ".config" / "myapp" / "settings.json"

# Inspect
print(p.name)        # "data"
print(p.suffix)      # ""
print(p.parent)      # /home/user
print(p.exists())    # True/False
print(p.is_file())   # True/False
print(p.is_dir())    # True/False

# Iterate directory contents
for child in p.iterdir():
    print(child)

# Glob
for py_file in p.glob("**/*.py"):
    print(py_file)

# Read/write shortcuts
text = config.read_text(encoding="utf-8")
config.write_text("new content", encoding="utf-8")

# Create directories
Path("new/nested/dir").mkdir(parents=True, exist_ok=True)
```

`pathlib.Path` works cross-platform and composes cleanly with the `/` operator.
Prefer it over `os.path` for new code.
