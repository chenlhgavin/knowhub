"""
Solution 01: Threading

Implements:
- parallel_map using ThreadPoolExecutor
- SafeCounter with Lock for thread safety
- download_simulation using concurrent threads
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
    if not items:
        return []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(func, items))
    return results


class SafeCounter:
    """A thread-safe counter using a Lock.

    Attributes:
        value (property): Current counter value.

    Methods:
        increment(): Atomically add 1.
        decrement(): Atomically subtract 1.
    """

    def __init__(self) -> None:
        self._value = 0
        self._lock = threading.Lock()

    def increment(self) -> None:
        with self._lock:
            self._value += 1

    def decrement(self) -> None:
        with self._lock:
            self._value -= 1

    @property
    def value(self) -> int:
        with self._lock:
            return self._value


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
    def _download(url: str) -> tuple[str, int]:
        time.sleep(0.01)
        return (url, len(url))

    result = {}
    with ThreadPoolExecutor(max_workers=min(len(urls), 10) if urls else 1) as executor:
        futures_results = list(executor.map(_download, urls))
    for url, length in futures_results:
        result[url] = length
    return result


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

    print("\nAll solution 01 tests passed!")
