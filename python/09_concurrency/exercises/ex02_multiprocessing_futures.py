"""
Exercise 02: Multiprocessing and Futures

Topics covered:
- CPU-bound tasks with ProcessPoolExecutor
- concurrent.futures.as_completed for racing tasks

Instructions:
    Implement each function below. Each raises NotImplementedError until
    you provide an implementation. Run the file to verify your solutions against
    the assert-based tests at the bottom.

Note:
    The multiprocessing tests must be guarded by `if __name__ == "__main__":`
    to work correctly on all platforms.
"""

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed


def cpu_bound_task(n: int) -> int:
    """Compute the sum of squares from 1 to n (inclusive).

    This is intentionally CPU-bound work.

    Args:
        n: Upper bound (inclusive).

    Returns:
        Sum of i*i for i in 1..n.
    """
    raise NotImplementedError("Implement cpu_bound_task")


def parallel_cpu(numbers: list[int], max_workers: int = 4) -> list[int]:
    """Apply cpu_bound_task to each number using ProcessPoolExecutor.

    Returns results in the same order as the input list.

    Args:
        numbers: List of integers to process.
        max_workers: Maximum number of worker processes.

    Returns:
        List of results, preserving input order.
    """
    raise NotImplementedError("Implement parallel_cpu")


def first_completed(funcs: list) -> object:
    """Submit all zero-argument callables to a ThreadPoolExecutor and return
    the result of whichever finishes first.

    Uses concurrent.futures.as_completed to detect the first completion.

    Args:
        funcs: List of zero-argument callables.

    Returns:
        The return value of the first callable to complete.
    """
    raise NotImplementedError("Implement first_completed")


if __name__ == "__main__":
    # --- Test cpu_bound_task ---
    assert cpu_bound_task(1) == 1, f"Expected 1, got {cpu_bound_task(1)}"
    assert cpu_bound_task(5) == 55, f"Expected 55, got {cpu_bound_task(5)}"
    assert cpu_bound_task(10) == 385, f"Expected 385, got {cpu_bound_task(10)}"
    assert cpu_bound_task(100) == 338350, f"Expected 338350, got {cpu_bound_task(100)}"

    print("cpu_bound_task: all tests passed")

    # --- Test parallel_cpu ---
    numbers = [10, 100, 1000]
    expected = [cpu_bound_task(n) for n in numbers]
    results = parallel_cpu(numbers, max_workers=2)
    assert results == expected, f"Expected {expected}, got {results}"

    results_empty = parallel_cpu([], max_workers=2)
    assert results_empty == [], f"Expected [], got {results_empty}"

    print("parallel_cpu: all tests passed")

    # --- Test first_completed ---
    import time

    def slow():
        time.sleep(0.5)
        return "slow"

    def fast():
        time.sleep(0.01)
        return "fast"

    result = first_completed([slow, fast])
    assert result == "fast", f"Expected 'fast', got {result}"

    def instant():
        return 42

    result2 = first_completed([slow, instant])
    assert result2 == 42, f"Expected 42, got {result2}"

    print("first_completed: all tests passed")

    print("\nAll exercise 02 tests passed!")
