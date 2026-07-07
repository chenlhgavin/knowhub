# Project 03: Task Scheduler

**Level:** Advanced -- covers concepts from all 10 chapters.

Build an asynchronous task scheduler that lets you define tasks as decorated async functions, resolve dependencies between them, and execute everything concurrently where possible.

---

## What You Will Build

A small framework with three main pieces:

1. A `@task` decorator that registers async functions with metadata (priority, retry count, dependencies).
2. A `TaskScheduler` class that collects registered tasks, resolves their execution order via topological sort, runs them concurrently (respecting dependencies), and retries failures.
3. A reporting layer that summarises what ran, how long each task took, and whether it succeeded or failed.

When you are finished, you should be able to write code like this:

```python
@task(name="fetch", priority=Priority.HIGH)
async def fetch():
    data = await download()
    return data

@task(name="transform", depends_on=["fetch"])
async def transform():
    return clean(data)

@task(name="load", depends_on=["transform"], priority=Priority.LOW, retries=3)
async def load():
    await save(data)

scheduler = TaskScheduler()
results = asyncio.run(scheduler.run())
print(scheduler.report(results))
```

---

## Requirements

### Task Definition

- Tasks are async functions decorated with `@task(...)`.
- The decorator accepts:
  - `name` -- a unique string identifier (defaults to the function name).
  - `priority` -- one of `Priority.HIGH`, `Priority.MEDIUM`, or `Priority.LOW`.
  - `retries` -- how many times to attempt the task before giving up (default 1, meaning no retries).
  - `depends_on` -- a list of task names that must complete before this task starts.
- Decorating a function registers it in a global task registry.

### Priority

Use an `Enum`:

| Member   | Value |
|----------|-------|
| `HIGH`   | 1     |
| `MEDIUM` | 2     |
| `LOW`    | 3     |

When two tasks are both ready to run (all dependencies satisfied), the one with the higher priority (lower numeric value) should be started first.

### Dependency Resolution

- The scheduler must perform a topological sort on the dependency graph.
- If a cycle is detected, raise `CyclicDependencyError`.
- If a task declares a dependency on a name that does not exist in the registry, raise `DependencyError`.

### Execution

- Use `asyncio` to run tasks concurrently.
- A task must not start until every task it depends on has completed successfully.
- If a task fails and has remaining retries, re-run it (up to `retries` total attempts).
- Track each task's status through its lifecycle: `PENDING` -> `RUNNING` -> `COMPLETED` or `FAILED`.

### Reporting

After execution, produce a formatted report containing:

- Task name
- Final status (COMPLETED / FAILED)
- Number of attempts
- Duration (seconds)
- Error message (if failed)

### Code Quality

- Type-hint every function signature and important variables.
- Use `dataclasses` for structured data (`TaskDef`, `TaskResult`).
- Define custom exceptions (`TaskError`, `DependencyError`, `CyclicDependencyError`).
- Support `async with` on the scheduler (context manager for setup/teardown).

---

## Concepts Demonstrated

This project ties together topics from every chapter in the curriculum:

| Chapter | Concept | Where It Appears |
|---------|---------|------------------|
| 01 Basics | Variables, f-strings | Throughout |
| 02 Control Flow | Loops, conditionals | Topological sort, retry logic |
| 03 Data Structures | Dicts, sets, lists | Task registry, dependency graph |
| 04 Functions | Closures, higher-order functions | Decorator factory |
| 05 OOP | Classes, dunder methods | `TaskScheduler`, `__aenter__`/`__aexit__` |
| 06 Modules & Errors | Custom exceptions, imports | `TaskError`, `DependencyError` |
| 07 Iterators & Generators | Generator functions | Status reporting |
| 08 Decorators | Decorator factories, `wraps` | `@task(...)` |
| 09 Concurrency | `asyncio`, `await`, `create_task` | Core execution engine |
| 10 Advanced | Type hints, dataclasses, enums | `TaskDef`, `TaskResult`, `Priority` |

---

## Hints

1. **Global registry.** Use a module-level `dict[str, TaskDef]` as the registry. The `@task` decorator factory returns a wrapper that stores the function and its metadata in this dict. Provide a `clear_registry()` helper so tests can reset state.

2. **Topological sort.** Kahn's algorithm works well:
   - Build an in-degree count for each node.
   - Start with nodes whose in-degree is zero.
   - Repeatedly remove a zero-in-degree node, decrement its dependents' counts, and add any new zero-in-degree nodes.
   - If you process fewer nodes than exist, there is a cycle.

3. **Concurrent execution with dependency gates.** One approach:
   - Create an `asyncio.Event` for each task.
   - Before running a task, `await` the events of all its dependencies.
   - After a task completes, set its event so dependents can proceed.
   - Use `asyncio.gather` to launch all tasks simultaneously -- each one internally waits for its own dependencies.

4. **Retry wrapper.** Inside `_run_task`, loop up to `retries` times. Catch exceptions, and only re-raise after all attempts are exhausted.

5. **Context manager.** Implement `__aenter__` and `__aexit__` on `TaskScheduler` so users can write `async with TaskScheduler() as s: ...`. Use `__aenter__` for any setup (e.g., recording start time) and `__aexit__` for teardown.

6. **Report formatting.** Build a simple table string with aligned columns. `f"{name:<20} {status:<12} {attempts:>8} {duration:>10.4f}s"` is a reasonable starting format.

---

## Files

```
p03_task_scheduler/
    README.md              # this file
    reference/
        task_scheduler.py  # complete working implementation
```

Write your own solution first. When you are ready, compare against the reference implementation.

---

## Running

```bash
# Demo run -- registers sample tasks and prints the execution report
python3 python/projects/p03_task_scheduler/reference/task_scheduler.py

# Run built-in tests
python3 python/projects/p03_task_scheduler/reference/task_scheduler.py --test
```
