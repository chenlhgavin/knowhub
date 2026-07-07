"""Async Task Scheduler -- Project 03 reference implementation.

Demonstrates: asyncio, decorators, generators, dataclasses, enums,
custom exceptions, context managers, and type hints.
"""

from __future__ import annotations

import asyncio
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from typing import Any, Callable, Generator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Priority(Enum):
    """Task execution priority. Lower numeric value = higher priority."""

    HIGH = 1
    MEDIUM = 2
    LOW = 3


class TaskStatus(Enum):
    """Lifecycle status of a task."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class TaskError(Exception):
    """Base exception for task-scheduler errors."""


class DependencyError(TaskError):
    """Raised when a task depends on an unknown task name."""


class CyclicDependencyError(TaskError):
    """Raised when the dependency graph contains a cycle."""


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class TaskResult:
    """Outcome of a single task execution."""

    task_name: str
    status: TaskStatus
    result: Any = None
    error: str | None = None
    duration: float = 0.0
    attempts: int = 0


@dataclass
class TaskDef:
    """Definition of a registered task."""

    name: str
    func: Callable[..., Any]
    priority: Priority = Priority.MEDIUM
    retries: int = 1
    depends_on: list[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING


# ---------------------------------------------------------------------------
# Global task registry
# ---------------------------------------------------------------------------

_task_registry: dict[str, TaskDef] = {}


def clear_registry() -> None:
    """Remove all registered tasks.  Useful between test runs."""
    _task_registry.clear()


# ---------------------------------------------------------------------------
# @task decorator factory
# ---------------------------------------------------------------------------

def task(
    name: str | None = None,
    priority: Priority = Priority.MEDIUM,
    retries: int = 1,
    depends_on: list[str] | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Register an async function as a schedulable task.

    Parameters
    ----------
    name:
        Unique identifier.  Defaults to the function's ``__name__``.
    priority:
        Execution priority when multiple tasks are ready.
    retries:
        Total number of attempts before the task is marked FAILED.
    depends_on:
        List of task names that must complete before this task starts.

    Returns
    -------
    The original function, unchanged, so it can still be called directly.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        task_name = name if name is not None else func.__name__

        task_def = TaskDef(
            name=task_name,
            func=func,
            priority=priority,
            retries=retries,
            depends_on=list(depends_on) if depends_on else [],
        )
        _task_registry[task_name] = task_def

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await func(*args, **kwargs)

        return wrapper

    return decorator


# ---------------------------------------------------------------------------
# TaskScheduler
# ---------------------------------------------------------------------------

class TaskScheduler:
    """Collect registered tasks, resolve order, and execute concurrently."""

    def __init__(self) -> None:
        # Snapshot the global registry so later registrations do not
        # interfere with an already-constructed scheduler.
        self._tasks: dict[str, TaskDef] = {
            name: TaskDef(
                name=td.name,
                func=td.func,
                priority=td.priority,
                retries=td.retries,
                depends_on=list(td.depends_on),
                status=TaskStatus.PENDING,
            )
            for name, td in _task_registry.items()
        }
        self._results: list[TaskResult] = []

    # -- Dependency resolution -----------------------------------------------

    def _validate_dependencies(self) -> None:
        """Raise ``DependencyError`` if any task depends on an unknown name."""
        known = set(self._tasks)
        for td in self._tasks.values():
            for dep in td.depends_on:
                if dep not in known:
                    raise DependencyError(
                        f"Task '{td.name}' depends on unknown task '{dep}'"
                    )

    def _topological_sort(self) -> list[str]:
        """Return task names in a valid execution order (Kahn's algorithm).

        Among tasks with the same topological depth the order is
        determined by priority (HIGH before LOW).

        Raises
        ------
        CyclicDependencyError
            If the dependency graph contains a cycle.
        """
        self._validate_dependencies()

        # Build adjacency list and in-degree counts.
        in_degree: dict[str, int] = {name: 0 for name in self._tasks}
        dependents: dict[str, list[str]] = {name: [] for name in self._tasks}

        for td in self._tasks.values():
            for dep in td.depends_on:
                dependents[dep].append(td.name)
                in_degree[td.name] += 1

        # Seed the queue with zero-in-degree tasks, sorted by priority.
        queue: list[str] = sorted(
            (n for n, d in in_degree.items() if d == 0),
            key=lambda n: self._tasks[n].priority.value,
        )
        order: list[str] = []

        while queue:
            current = queue.pop(0)
            order.append(current)

            # Collect newly-ready tasks, then sort by priority before
            # extending the queue so higher-priority tasks come first.
            newly_ready: list[str] = []
            for dep_name in dependents[current]:
                in_degree[dep_name] -= 1
                if in_degree[dep_name] == 0:
                    newly_ready.append(dep_name)

            newly_ready.sort(key=lambda n: self._tasks[n].priority.value)
            queue.extend(newly_ready)

        if len(order) != len(self._tasks):
            remaining = set(self._tasks) - set(order)
            raise CyclicDependencyError(
                f"Cyclic dependency detected among tasks: {remaining}"
            )

        return order

    # -- Single-task execution -----------------------------------------------

    async def _run_task(self, task_def: TaskDef) -> TaskResult:
        """Execute *task_def*, retrying on failure up to ``task_def.retries`` times."""
        attempts = 0
        last_error: str | None = None
        result_value: Any = None

        start = time.monotonic()

        while attempts < task_def.retries:
            attempts += 1
            task_def.status = TaskStatus.RUNNING
            try:
                result_value = await task_def.func()
                task_def.status = TaskStatus.COMPLETED
                return TaskResult(
                    task_name=task_def.name,
                    status=TaskStatus.COMPLETED,
                    result=result_value,
                    duration=time.monotonic() - start,
                    attempts=attempts,
                )
            except Exception as exc:
                last_error = f"{type(exc).__name__}: {exc}"

        task_def.status = TaskStatus.FAILED
        return TaskResult(
            task_name=task_def.name,
            status=TaskStatus.FAILED,
            error=last_error,
            duration=time.monotonic() - start,
            attempts=attempts,
        )

    # -- Full execution run --------------------------------------------------

    async def run(self) -> list[TaskResult]:
        """Execute all registered tasks respecting dependencies and priorities.

        Returns a list of :class:`TaskResult` in the order tasks completed.
        """
        order = self._topological_sort()

        # An asyncio.Event per task signals when it is finished.
        done_events: dict[str, asyncio.Event] = {
            name: asyncio.Event() for name in order
        }
        results_map: dict[str, TaskResult] = {}

        async def _execute(name: str) -> None:
            td = self._tasks[name]

            # Wait for every dependency to finish.
            for dep in td.depends_on:
                await done_events[dep].wait()

                # If a dependency failed, skip this task immediately.
                if results_map[dep].status == TaskStatus.FAILED:
                    td.status = TaskStatus.FAILED
                    results_map[name] = TaskResult(
                        task_name=name,
                        status=TaskStatus.FAILED,
                        error=f"Dependency '{dep}' failed",
                        attempts=0,
                    )
                    done_events[name].set()
                    return

            result = await self._run_task(td)
            results_map[name] = result
            done_events[name].set()

        # Launch all tasks concurrently; each one internally waits for its
        # own dependencies via the events above.
        await asyncio.gather(*(_execute(name) for name in order))

        # Return results in topological order.
        self._results = [results_map[name] for name in order]
        return self._results

    # -- Reporting -----------------------------------------------------------

    def report(self, results: list[TaskResult]) -> str:
        """Return a formatted execution report."""
        lines: list[str] = []
        header = (
            f"{'Task':<20} {'Status':<12} {'Attempts':>8} "
            f"{'Duration':>10} {'Error'}"
        )
        lines.append(header)
        lines.append("-" * len(header))

        for r in results:
            error_col = r.error if r.error else ""
            lines.append(
                f"{r.task_name:<20} {r.status.value:<12} {r.attempts:>8} "
                f"{r.duration:>9.4f}s {error_col}"
            )

        return "\n".join(lines)

    # -- Generator for status snapshots --------------------------------------

    def status_snapshot(self) -> Generator[tuple[str, TaskStatus], None, None]:
        """Yield ``(task_name, status)`` pairs for every registered task."""
        for name, td in self._tasks.items():
            yield name, td.status

    # -- Async context manager -----------------------------------------------

    async def __aenter__(self) -> "TaskScheduler":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> bool:
        return False


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def run_tests() -> None:
    """Test the task scheduler."""

    # ---- Test 1: basic execution and dependency ordering -------------------
    clear_registry()

    @task(name="fetch_data", priority=Priority.HIGH)
    async def fetch_data() -> dict[str, list[int]]:
        await asyncio.sleep(0.01)
        return {"data": [1, 2, 3]}

    @task(name="process_data", depends_on=["fetch_data"])
    async def process_data() -> dict[str, bool]:
        await asyncio.sleep(0.01)
        return {"processed": True}

    @task(name="generate_report", depends_on=["process_data"], priority=Priority.LOW)
    async def generate_report() -> str:
        await asyncio.sleep(0.01)
        return "report done"

    scheduler = TaskScheduler()
    results = asyncio.run(scheduler.run())

    assert len(results) == 3, f"Expected 3 results, got {len(results)}"
    assert all(r.status == TaskStatus.COMPLETED for r in results)

    names = [r.task_name for r in results]
    assert names.index("fetch_data") < names.index("process_data")
    assert names.index("process_data") < names.index("generate_report")

    # ---- Test 2: retry on failure ------------------------------------------
    clear_registry()
    call_count = 0

    @task(name="flaky_task", retries=3)
    async def flaky_task() -> str:
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("not yet")
        return "success"

    scheduler = TaskScheduler()
    results = asyncio.run(scheduler.run())

    assert results[0].status == TaskStatus.COMPLETED
    assert results[0].attempts == 3

    # ---- Test 3: exhausted retries mark the task as FAILED -----------------
    clear_registry()

    @task(name="always_fails", retries=2)
    async def always_fails() -> None:
        raise RuntimeError("boom")

    scheduler = TaskScheduler()
    results = asyncio.run(scheduler.run())

    assert results[0].status == TaskStatus.FAILED
    assert results[0].attempts == 2
    assert "boom" in (results[0].error or "")

    # ---- Test 4: cycle detection -------------------------------------------
    clear_registry()

    @task(name="a", depends_on=["b"])
    async def task_a() -> str:
        return "a"

    @task(name="b", depends_on=["a"])
    async def task_b() -> str:
        return "b"

    scheduler = TaskScheduler()
    try:
        asyncio.run(scheduler.run())
        assert False, "Should have raised CyclicDependencyError"
    except CyclicDependencyError:
        pass  # expected

    # ---- Test 5: unknown dependency ----------------------------------------
    clear_registry()

    @task(name="orphan", depends_on=["nonexistent"])
    async def orphan() -> str:
        return "orphan"

    scheduler = TaskScheduler()
    try:
        asyncio.run(scheduler.run())
        assert False, "Should have raised DependencyError"
    except DependencyError:
        pass  # expected

    # ---- Test 6: report generation -----------------------------------------
    clear_registry()

    @task(name="quick")
    async def quick() -> str:
        return "done"

    scheduler = TaskScheduler()
    results = asyncio.run(scheduler.run())
    report = scheduler.report(results)
    assert "quick" in report

    # ---- Test 7: async context manager -------------------------------------
    clear_registry()

    @task(name="cm_task")
    async def cm_task() -> str:
        return "ok"

    async def _ctx_test() -> None:
        async with TaskScheduler() as s:
            res = await s.run()
            assert res[0].status == TaskStatus.COMPLETED

    asyncio.run(_ctx_test())

    # ---- Test 8: status snapshot generator ---------------------------------
    clear_registry()

    @task(name="snap")
    async def snap() -> str:
        return "snap"

    scheduler = TaskScheduler()
    statuses = list(scheduler.status_snapshot())
    assert statuses == [("snap", TaskStatus.PENDING)]

    print("All tests passed!")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if "--test" in sys.argv:
        run_tests()
    else:
        # Demo run
        clear_registry()

        @task(name="step1", priority=Priority.HIGH)
        async def step1() -> str:
            await asyncio.sleep(0.1)
            return "Step 1 done"

        @task(name="step2", depends_on=["step1"])
        async def step2() -> str:
            await asyncio.sleep(0.1)
            return "Step 2 done"

        @task(name="step3", depends_on=["step1"])
        async def step3() -> str:
            await asyncio.sleep(0.1)
            return "Step 3 done"

        @task(name="step4", depends_on=["step2", "step3"], priority=Priority.LOW)
        async def step4() -> str:
            await asyncio.sleep(0.1)
            return "Step 4 done"

        scheduler = TaskScheduler()
        results = asyncio.run(scheduler.run())
        print(scheduler.report(results))
