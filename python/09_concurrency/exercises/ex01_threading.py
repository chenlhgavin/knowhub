"""
Exercise 01: Threading

Topics covered:
- ThreadPoolExecutor for parallel mapping
- Thread-safe counters with Lock
- Concurrent I/O simulation with threads

Instructions:
    Implement each function/class below. Each raises NotImplementedError until
    you provide an implementation. Run the file to verify your solutions against
    the assert-based tests at the bottom.
"""

from concurrent.futures import ThreadPoolExecutor
import threading
import time


def parallel_map(func, items: list, max_workers: int = 4) -> list:
    """Apply func to each item using ThreadPoolExecutor.

    Returns results in the same order as the input items.

    Args:
        func: A callable to apply to each item.
        items: List of inputs.
        max_workers: Maximum number of threads.

    Returns:
        List of results, preserving input order.
    """
    raise NotImplementedError("Implement parallel_map")


class SafeCounter:
    """A thread-safe counter using a Lock.

    Attributes:
        value (property): Current counter value.

    Methods:
        increment(): Atomically add 1.
        decrement(): Atomically subtract 1.
    """

    def __init__(self) -> None:
        raise NotImplementedError("Implement SafeCounter.__init__")

    def increment(self) -> None:
        raise NotImplementedError("Implement SafeCounter.increment")

    def decrement(self) -> None:
        raise NotImplementedError("Implement SafeCounter.decrement")

    @property
    def value(self) -> int:
        raise NotImplementedError("Implement SafeCounter.value")


def download_simulation(urls: list[str]) -> dict[str, int]:
    """Simulate downloading URLs concurrently.

    For each URL, simulate work by sleeping 0.01 seconds, then record
    the length of the URL string as the 'downloaded size'.

    This function must use threads and must be faster than doing it
    sequentially.

    Args:
        urls: List of URL strings.

    Returns:
        Dict mapping each URL to its string length.
    """
    raise NotImplementedError("Implement download_simulation")


if __name__ == "__main__":
    # --- Test parallel_map ---
    results = parallel_map(lambda x: x * x, [1, 2, 3, 4, 5])
    assert results == [1, 4, 9, 16, 25], f"Expected [1, 4, 9, 16, 25], got {results}"

    results = parallel_map(str.upper, ["hello", "world"])
    assert results == ["HELLO", "WORLD"], f"Expected ['HELLO', 'WORLD'], got {results}"

    results = parallel_map(lambda x: x + 1, [])
    assert results == [], f"Expected [], got {results}"

    print("parallel_map: all tests passed")

    # --- Test SafeCounter ---
    counter = SafeCounter()
    assert counter.value == 0, f"Expected 0, got {counter.value}"

    threads = []
    for _ in range(10):
        t = threading.Thread(target=lambda: [counter.increment() for _ in range(1000)])
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    assert counter.value == 10_000, f"Expected 10000, got {counter.value}"

    for _ in range(5000):
        counter.decrement()
    assert counter.value == 5_000, f"Expected 5000, got {counter.value}"

    print("SafeCounter: all tests passed")

    # --- Test download_simulation ---
    test_urls = [f"http://example.com/page/{i}" for i in range(20)]

    start_seq = time.perf_counter()
    expected = {}
    for url in test_urls:
        time.sleep(0.01)
        expected[url] = len(url)
    seq_time = time.perf_counter() - start_seq

    start_par = time.perf_counter()
    result = download_simulation(test_urls)
    par_time = time.perf_counter() - start_par

    assert result == expected, f"Results do not match expected dict"
    assert par_time < seq_time, (
        f"Parallel ({par_time:.3f}s) was not faster than sequential ({seq_time:.3f}s)"
    )

    print(f"download_simulation: all tests passed (seq={seq_time:.3f}s, par={par_time:.3f}s)")

    print("\nAll exercise 01 tests passed!")
