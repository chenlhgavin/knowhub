"""
Solution 03: asyncio

Implements:
- fetch_data: simulated async fetch
- gather_results: concurrent fetching with asyncio.gather
- producer_consumer: asyncio.Queue-based pattern
- timeout_fetch: fetch with asyncio.wait_for timeout
"""

import asyncio


async def fetch_data(url: str, delay: float = 0.01) -> dict:
    """Simulate an async data fetch.

    Await asyncio.sleep(delay) to simulate network latency, then return
    a dict with the URL and a status code.

    Args:
        url: The URL string to 'fetch'.
        delay: Simulated network delay in seconds.

    Returns:
        {"url": url, "status": 200}
    """
    await asyncio.sleep(delay)
    return {"url": url, "status": 200}


async def gather_results(urls: list[str]) -> list[dict]:
    """Fetch all URLs concurrently using asyncio.gather.

    Each URL should be fetched using fetch_data with the default delay.

    Args:
        urls: List of URL strings.

    Returns:
        List of result dicts from fetch_data, in the same order as urls.
    """
    if not urls:
        return []
    coroutines = [fetch_data(url) for url in urls]
    results = await asyncio.gather(*coroutines)
    return list(results)


async def producer_consumer(items: list, process_func) -> list:
    """Implement a producer-consumer pattern using asyncio.Queue.

    - A producer coroutine puts each item from `items` into the queue.
    - A consumer coroutine gets items from the queue, applies process_func
      to each, and collects the results.
    - Use a sentinel value (None) to signal the consumer to stop.

    Args:
        items: List of items to process.
        process_func: A synchronous callable to apply to each item.

    Returns:
        List of processed results, in the order they were consumed.
    """
    queue: asyncio.Queue = asyncio.Queue()
    results = []

    async def producer():
        for item in items:
            await queue.put(item)
        await queue.put(None)  # Sentinel

    async def consumer():
        while True:
            item = await queue.get()
            if item is None:
                break
            results.append(process_func(item))

    prod_task = asyncio.create_task(producer())
    cons_task = asyncio.create_task(consumer())
    await prod_task
    await cons_task

    return results


async def timeout_fetch(url: str, timeout: float = 0.05) -> dict | None:
    """Fetch data with a timeout.

    Uses fetch_data (with its default delay) but wraps it with
    asyncio.wait_for. If the fetch exceeds the timeout, return None
    instead of raising an exception.

    Args:
        url: The URL string to fetch.
        timeout: Maximum seconds to wait.

    Returns:
        The fetch_data result dict, or None if the timeout is exceeded.
    """
    try:
        result = await asyncio.wait_for(fetch_data(url), timeout=timeout)
        return result
    except asyncio.TimeoutError:
        return None


if __name__ == "__main__":
    # --- Test fetch_data ---
    result = asyncio.run(fetch_data("http://example.com"))
    assert result == {"url": "http://example.com", "status": 200}, (
        f"Expected {{'url': 'http://example.com', 'status': 200}}, got {result}"
    )

    result2 = asyncio.run(fetch_data("http://test.org", delay=0.0))
    assert result2 == {"url": "http://test.org", "status": 200}, (
        f"Expected {{'url': 'http://test.org', 'status': 200}}, got {result2}"
    )

    print("fetch_data: all tests passed")

    # --- Test gather_results ---
    urls = ["http://a.com", "http://b.com", "http://c.com"]
    results = asyncio.run(gather_results(urls))
    assert len(results) == 3, f"Expected 3 results, got {len(results)}"
    for i, url in enumerate(urls):
        assert results[i]["url"] == url, f"Expected url {url}, got {results[i]['url']}"
        assert results[i]["status"] == 200, f"Expected status 200, got {results[i]['status']}"

    empty_results = asyncio.run(gather_results([]))
    assert empty_results == [], f"Expected [], got {empty_results}"

    print("gather_results: all tests passed")

    # --- Test producer_consumer ---
    processed = asyncio.run(producer_consumer([1, 2, 3, 4, 5], lambda x: x * 2))
    assert processed == [2, 4, 6, 8, 10], f"Expected [2, 4, 6, 8, 10], got {processed}"

    processed_empty = asyncio.run(producer_consumer([], lambda x: x))
    assert processed_empty == [], f"Expected [], got {processed_empty}"

    processed_str = asyncio.run(producer_consumer(["a", "b"], str.upper))
    assert processed_str == ["A", "B"], f"Expected ['A', 'B'], got {processed_str}"

    print("producer_consumer: all tests passed")

    # --- Test timeout_fetch ---
    result_ok = asyncio.run(timeout_fetch("http://fast.com", timeout=1.0))
    assert result_ok is not None, "Expected a result, got None"
    assert result_ok["url"] == "http://fast.com", f"Expected url 'http://fast.com', got {result_ok['url']}"

    result_timeout = asyncio.run(timeout_fetch("http://slow.com", timeout=0.001))
    assert result_timeout is None, f"Expected None for timeout, got {result_timeout}"

    print("timeout_fetch: all tests passed")

    print("\nAll solution 03 tests passed!")
