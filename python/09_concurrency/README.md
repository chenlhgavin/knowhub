# Chapter 09: Concurrency

Concurrency is one of the most powerful and nuanced topics in Python. This chapter
covers threads, processes, and asynchronous programming — when to use each, and how
to avoid the pitfalls that come with concurrent execution.

---

## Table of Contents

1. [Concurrency vs Parallelism](#concurrency-vs-parallelism)
2. [The GIL (Global Interpreter Lock)](#the-gil-global-interpreter-lock)
3. [threading Module](#threading-module)
4. [Thread Safety](#thread-safety)
5. [multiprocessing Module](#multiprocessing-module)
6. [concurrent.futures](#concurrentfutures)
7. [asyncio Fundamentals](#asyncio-fundamentals)
8. [asyncio Primitives](#asyncio-primitives)
9. [Async Context Managers and Async Iterators](#async-context-managers-and-async-iterators)
10. [When to Use What](#when-to-use-what)
11. [Common Patterns and Pitfalls](#common-patterns-and-pitfalls)

---

## Concurrency vs Parallelism

These terms are often confused, but they describe different things:

- **Concurrency** means dealing with multiple tasks at once. The tasks may not
  actually run simultaneously — they can be interleaved on a single core.
- **Parallelism** means executing multiple tasks at the exact same time, typically
  on multiple CPU cores.

An analogy: a single cook juggling three dishes is concurrent. Three cooks each
making one dish is parallel.

```
Concurrency (interleaved):     Parallelism (simultaneous):

Core 1: [A][B][A][B][A]        Core 1: [AAAAAAA]
                                Core 2: [BBBBBBB]
```

Python supports both, but the GIL makes true parallelism tricky for CPU-bound
work within a single process.

---

## The GIL (Global Interpreter Lock)

The GIL is a mutex in CPython that allows only one thread to execute Python
bytecode at a time, even on multi-core machines.

### Why it exists

CPython's memory management (reference counting) is not thread-safe. The GIL
prevents race conditions on internal interpreter state.

### Implications

| Task Type | GIL Impact | Recommendation |
|-----------|-----------|----------------|
| **I/O-bound** (network, file, sleep) | GIL is released during I/O waits | `threading` or `asyncio` work well |
| **CPU-bound** (math, parsing, loops) | GIL prevents true parallelism | Use `multiprocessing` to bypass GIL |

```python
import threading
import time

counter = 0

def increment():
    global counter
    for _ in range(1_000_000):
        counter += 1  # NOT atomic — the GIL does not make this safe

threads = [threading.Thread(target=increment) for _ in range(2)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print(counter)  # Almost certainly NOT 2_000_000 due to race condition
```

---

## threading Module

### Creating Threads

```python
import threading

def worker(name):
    print(f"Thread {name} running")

t = threading.Thread(target=worker, args=("A",))
t.start()
t.join()  # Wait for thread to finish
```

### Lock

A Lock ensures mutual exclusion — only one thread can hold it at a time.

```python
lock = threading.Lock()

def safe_increment(counter_list):
    with lock:
        counter_list[0] += 1
```

### RLock (Reentrant Lock)

An RLock can be acquired multiple times by the same thread without deadlocking.

```python
rlock = threading.RLock()

def outer():
    with rlock:
        inner()  # Same thread can re-acquire

def inner():
    with rlock:
        print("inner")
```

### Event

An Event is a simple signaling mechanism between threads.

```python
event = threading.Event()

def waiter():
    print("Waiting for event...")
    event.wait()
    print("Event received!")

def setter():
    import time
    time.sleep(1)
    event.set()

threading.Thread(target=waiter).start()
threading.Thread(target=setter).start()
```

### Semaphore

A Semaphore limits the number of threads that can access a resource concurrently.

```python
semaphore = threading.Semaphore(3)  # Allow 3 concurrent threads

def limited_access(n):
    with semaphore:
        print(f"Thread {n} entered")
        import time
        time.sleep(0.1)
        print(f"Thread {n} exiting")

threads = [threading.Thread(target=limited_access, args=(i,)) for i in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

### Daemon Threads

Daemon threads are killed automatically when the main program exits. They are
useful for background tasks that should not prevent program termination.

```python
def background_task():
    import time
    while True:
        print("Background...")
        time.sleep(1)

t = threading.Thread(target=background_task, daemon=True)
t.start()
# Main thread exits -> daemon thread is killed automatically
```

---

## Thread Safety

### Race Conditions

A race condition occurs when the outcome depends on the order of thread execution.

```python
# UNSAFE — race condition
balance = 0

def deposit():
    global balance
    for _ in range(100_000):
        balance += 1  # read-modify-write is NOT atomic

def withdraw():
    global balance
    for _ in range(100_000):
        balance -= 1

# After running both, balance should be 0 but often is not.
```

**Fix: use a Lock.**

```python
lock = threading.Lock()
balance = 0

def deposit():
    global balance
    for _ in range(100_000):
        with lock:
            balance += 1

def withdraw():
    global balance
    for _ in range(100_000):
        with lock:
            balance -= 1
```

### Deadlocks

A deadlock occurs when two or more threads wait for each other to release locks.

```python
# DEADLOCK — Thread A holds lock1, waits for lock2
#            Thread B holds lock2, waits for lock1
lock1 = threading.Lock()
lock2 = threading.Lock()

def task_a():
    with lock1:
        with lock2:  # Waits forever if task_b holds lock2
            pass

def task_b():
    with lock2:
        with lock1:  # Waits forever if task_a holds lock1
            pass
```

**How to avoid deadlocks:**

1. **Lock ordering** — always acquire locks in the same order.
2. **Timeouts** — use `lock.acquire(timeout=5)` instead of blocking forever.
3. **Minimize lock scope** — hold locks for the shortest time possible.
4. **Use higher-level abstractions** — `concurrent.futures` or `asyncio` avoid
   manual lock management.

---

## multiprocessing Module

The `multiprocessing` module spawns separate OS processes, each with its own
Python interpreter and GIL. This enables true parallelism for CPU-bound work.

### Process

```python
from multiprocessing import Process

def compute(n):
    print(f"Sum: {sum(range(n))}")

p = Process(target=compute, args=(10_000_000,))
p.start()
p.join()
```

### Pool

A Pool manages a group of worker processes.

```python
from multiprocessing import Pool

def square(x):
    return x * x

with Pool(4) as pool:
    results = pool.map(square, range(10))
    print(results)  # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
```

### Shared State

Processes have separate memory. To share state, use special constructs:

```python
from multiprocessing import Process, Value, Array, Manager

# Value and Array — shared memory (fast, limited types)
counter = Value('i', 0)   # 'i' = integer
arr = Array('d', [0.0, 1.0, 2.0])  # 'd' = double

def increment_shared(val):
    for _ in range(1000):
        with val.get_lock():
            val.value += 1

# Manager — shared via proxy objects (flexible, slower)
with Manager() as manager:
    shared_list = manager.list([1, 2, 3])
    shared_dict = manager.dict({"key": "value"})

    def append_item(lst, item):
        lst.append(item)

    p = Process(target=append_item, args=(shared_list, 4))
    p.start()
    p.join()
    print(list(shared_list))  # [1, 2, 3, 4]
```

---

## concurrent.futures

The `concurrent.futures` module provides a high-level interface for launching
parallel tasks. It abstracts away the details of threads and processes behind
a unified `Executor` API.

### ThreadPoolExecutor

```python
from concurrent.futures import ThreadPoolExecutor
import time

def fetch(url):
    time.sleep(0.1)  # Simulate I/O
    return f"Data from {url}"

with ThreadPoolExecutor(max_workers=4) as executor:
    urls = ["http://a.com", "http://b.com", "http://c.com"]
    results = list(executor.map(fetch, urls))
    print(results)
```

### ProcessPoolExecutor

```python
from concurrent.futures import ProcessPoolExecutor

def heavy_compute(n):
    return sum(i * i for i in range(n))

with ProcessPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(heavy_compute, [10**6, 10**6, 10**6]))
```

### Future and as_completed

A `Future` represents a computation that may not be done yet. `as_completed`
yields futures as they finish — useful when tasks have varying durations.

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def task(n):
    time.sleep(n)
    return n

with ThreadPoolExecutor() as executor:
    futures = {executor.submit(task, i): i for i in [3, 1, 2]}

    for future in as_completed(futures):
        result = future.result()
        print(f"Completed: {result}")
    # Prints in order: 1, 2, 3 (fastest first)
```

---

## asyncio Fundamentals

`asyncio` is Python's built-in framework for writing single-threaded concurrent
code using coroutines. It uses cooperative multitasking: tasks voluntarily yield
control at `await` points.

### Event Loop

The event loop is the core of asyncio. It schedules and runs coroutines.

```python
import asyncio

async def main():
    print("Hello")
    await asyncio.sleep(1)
    print("World")

asyncio.run(main())  # Creates event loop, runs coroutine, closes loop
```

### Coroutines

A coroutine is defined with `async def` and can contain `await` expressions.

```python
async def fetch_data(url: str) -> str:
    await asyncio.sleep(0.1)  # Non-blocking sleep
    return f"Data from {url}"

async def main():
    data = await fetch_data("http://example.com")
    print(data)

asyncio.run(main())
```

### async/await

- `async def` declares a coroutine function.
- `await` suspends the coroutine until the awaited object completes.
- You can only use `await` inside an `async def`.

```python
async def step_one():
    await asyncio.sleep(0.1)
    return 1

async def step_two(x):
    await asyncio.sleep(0.1)
    return x + 1

async def pipeline():
    result = await step_one()
    result = await step_two(result)
    print(result)  # 2

asyncio.run(pipeline())
```

---

## asyncio Primitives

### asyncio.gather

Run multiple coroutines concurrently and collect all results.

```python
async def fetch(url, delay):
    await asyncio.sleep(delay)
    return {"url": url, "status": 200}

async def main():
    results = await asyncio.gather(
        fetch("http://a.com", 0.1),
        fetch("http://b.com", 0.2),
        fetch("http://c.com", 0.1),
    )
    print(results)  # List of dicts, in the same order as arguments

asyncio.run(main())
```

### asyncio.create_task

Schedule a coroutine to run soon, without waiting for it immediately.

```python
async def background():
    await asyncio.sleep(1)
    print("Background done")

async def main():
    task = asyncio.create_task(background())
    print("Main continues immediately")
    await task  # Now wait for it

asyncio.run(main())
```

### asyncio.sleep

Non-blocking sleep. Unlike `time.sleep`, this yields control back to the event
loop so other tasks can run.

```python
async def timed():
    print("Start")
    await asyncio.sleep(0.5)
    print("End")
```

### asyncio.Queue

An async-friendly queue for producer-consumer patterns.

```python
import asyncio

async def producer(queue):
    for i in range(5):
        await queue.put(i)
        print(f"Produced {i}")
    await queue.put(None)  # Sentinel to signal completion

async def consumer(queue):
    results = []
    while True:
        item = await queue.get()
        if item is None:
            break
        results.append(item * 2)
        print(f"Consumed {item}")
    return results

async def main():
    queue = asyncio.Queue()
    prod = asyncio.create_task(producer(queue))
    cons = asyncio.create_task(consumer(queue))
    await prod
    results = await cons
    print(results)  # [0, 2, 4, 6, 8]

asyncio.run(main())
```

---

## Async Context Managers and Async Iterators

### Async Context Managers

Use `async with` for resources that need asynchronous setup and teardown.

```python
class AsyncConnection:
    async def __aenter__(self):
        print("Connecting...")
        await asyncio.sleep(0.1)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("Disconnecting...")
        await asyncio.sleep(0.1)

    async def query(self, sql):
        await asyncio.sleep(0.01)
        return f"Result for: {sql}"

async def main():
    async with AsyncConnection() as conn:
        result = await conn.query("SELECT * FROM users")
        print(result)

asyncio.run(main())
```

Or use `contextlib.asynccontextmanager`:

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def managed_resource():
    print("Acquiring")
    await asyncio.sleep(0.01)
    try:
        yield "resource"
    finally:
        print("Releasing")
        await asyncio.sleep(0.01)

async def main():
    async with managed_resource() as res:
        print(f"Using {res}")

asyncio.run(main())
```

### Async Iterators

Use `async for` to iterate over asynchronously produced items.

```python
class AsyncRange:
    def __init__(self, start, stop):
        self.current = start
        self.stop = stop

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.current >= self.stop:
            raise StopAsyncIteration
        await asyncio.sleep(0.01)
        value = self.current
        self.current += 1
        return value

async def main():
    async for num in AsyncRange(0, 5):
        print(num)

asyncio.run(main())
```

Async generators provide a simpler syntax:

```python
async def async_range(start, stop):
    for i in range(start, stop):
        await asyncio.sleep(0.01)
        yield i

async def main():
    async for num in async_range(0, 5):
        print(num)

asyncio.run(main())
```

---

## When to Use What

| Scenario | Tool | Why |
|----------|------|-----|
| Many network requests | `asyncio` or `threading` | I/O-bound; GIL is released during waits |
| File I/O with many files | `threading` or `asyncio` | I/O-bound |
| CPU-heavy computation | `multiprocessing` | Bypasses the GIL with separate processes |
| Simple parallel tasks | `concurrent.futures` | High-level API, easy to switch thread/process |
| High-concurrency I/O (1000s of connections) | `asyncio` | Lightweight coroutines scale better than threads |
| Quick script, few tasks | `threading` | Simplest to set up |

### Decision flowchart

```
Is the task CPU-bound?
  YES -> Use multiprocessing / ProcessPoolExecutor
  NO  -> Is high concurrency needed (100s+ of tasks)?
           YES -> Use asyncio
           NO  -> Use threading / ThreadPoolExecutor
```

---

## Common Patterns and Pitfalls

### Pattern: Worker Pool

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def process(item):
    return item * 2

with ThreadPoolExecutor(max_workers=8) as executor:
    futures = {executor.submit(process, i): i for i in range(100)}
    results = {}
    for future in as_completed(futures):
        original = futures[future]
        results[original] = future.result()
```

### Pattern: Async Semaphore for Rate Limiting

```python
import asyncio

async def limited_fetch(sem, url):
    async with sem:
        await asyncio.sleep(0.1)
        return f"Data from {url}"

async def main():
    sem = asyncio.Semaphore(5)  # Max 5 concurrent fetches
    urls = [f"http://example.com/{i}" for i in range(20)]
    tasks = [limited_fetch(sem, url) for url in urls]
    results = await asyncio.gather(*tasks)

asyncio.run(main())
```

### Pitfall: Forgetting to await

```python
async def fetch():
    return "data"

async def main():
    result = fetch()      # WRONG — returns coroutine object, not "data"
    result = await fetch() # CORRECT
```

### Pitfall: Using time.sleep in async code

```python
async def bad():
    time.sleep(1)          # WRONG — blocks the entire event loop

async def good():
    await asyncio.sleep(1)  # CORRECT — yields control to event loop
```

### Pitfall: Sharing mutable state without locks

```python
# WRONG — race condition
shared = []
def append_item(item):
    shared.append(item)  # list.append is thread-safe in CPython, but
                          # read-modify-write patterns are NOT

# CORRECT — use a lock for compound operations
lock = threading.Lock()
def safe_update(item):
    with lock:
        if item not in shared:
            shared.append(item)
```

### Pitfall: Creating too many processes

```python
# WRONG — spawning 10,000 processes
with ProcessPoolExecutor(max_workers=10000) as executor:
    ...

# CORRECT — use a reasonable pool size
import os
with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
    ...
```

### Pitfall: Not handling exceptions in futures

```python
from concurrent.futures import ThreadPoolExecutor

def risky():
    raise ValueError("oops")

with ThreadPoolExecutor() as executor:
    future = executor.submit(risky)
    # Exception is silently swallowed unless you call .result()
    try:
        result = future.result()
    except ValueError as e:
        print(f"Caught: {e}")
```

---

## Exercises

- [ex01_threading.py](exercises/ex01_threading.py) — Thread pools, safe counters, concurrent downloads
- [ex02_multiprocessing_futures.py](exercises/ex02_multiprocessing_futures.py) — CPU-bound parallelism, futures
- [ex03_asyncio.py](exercises/ex03_asyncio.py) — Async fetch, gather, producer-consumer, timeouts

Solutions are in the [solutions/](solutions/) directory.
