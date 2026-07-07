"""Solution 04: Context Managers

Implement context managers using both the class-based protocol (__enter__/__exit__)
and the contextlib.contextmanager decorator.
"""

import os
import sys
import time
import tempfile
import shutil
from contextlib import contextmanager
from io import StringIO


class Timer:
    """Context manager that measures elapsed time.

    After exiting the context, the .elapsed attribute contains the elapsed
    time in seconds as a float.
    """

    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.perf_counter() - self._start
        return False  # do not suppress exceptions


@contextmanager
def temp_directory():
    """Context manager that creates a temporary directory, yields its path,
    and cleans it up on exit.
    """
    path = tempfile.mkdtemp()
    try:
        yield path
    finally:
        shutil.rmtree(path)


class suppress_errors:
    """Context manager that suppresses specified exception types.

    Has an .exception attribute set to the caught exception instance,
    or None if no exception occurred.
    """

    def __init__(self, *exception_types):
        self.exception_types = exception_types
        self.exception = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None and issubclass(exc_type, self.exception_types):
            self.exception = exc_val
            return True  # suppress the exception
        return False  # let it propagate


@contextmanager
def redirect_output():
    """Context manager that captures stdout. Yields a StringIO object.
    After exit, stdout is restored.
    """
    buffer = StringIO()
    old_stdout = sys.stdout
    sys.stdout = buffer
    try:
        yield buffer
    finally:
        sys.stdout = old_stdout


if __name__ == "__main__":

    # --- Timer tests ---
    with Timer() as t:
        time.sleep(0.05)
    assert hasattr(t, "elapsed"), "Timer must have .elapsed attribute"
    assert t.elapsed >= 0.04, f"Elapsed too short: {t.elapsed}"
    assert t.elapsed < 1.0, f"Elapsed too long: {t.elapsed}"

    # Timer should not suppress exceptions
    try:
        with Timer() as t2:
            raise ValueError("test")
    except ValueError:
        assert hasattr(t2, "elapsed"), "elapsed should be set even on exception"

    # --- temp_directory tests ---
    with temp_directory() as tmpdir:
        assert os.path.isdir(tmpdir), "temp_directory must yield an existing directory"
        test_file = os.path.join(tmpdir, "test.txt")
        with open(test_file, "w") as f:
            f.write("hello")
        assert os.path.exists(test_file)
        saved_path = tmpdir

    assert not os.path.exists(saved_path), "temp_directory must clean up after exit"

    # --- suppress_errors tests ---
    with suppress_errors(ValueError) as ctx:
        raise ValueError("test error")
    assert ctx.exception is not None, "exception should be captured"
    assert isinstance(ctx.exception, ValueError)
    assert str(ctx.exception) == "test error"

    with suppress_errors(ValueError) as ctx2:
        pass  # no exception
    assert ctx2.exception is None, "exception should be None when no error"

    # Non-matching exceptions should propagate
    try:
        with suppress_errors(ValueError) as ctx3:
            raise TypeError("wrong type")
        assert False, "Should have raised TypeError"
    except TypeError:
        pass

    # --- redirect_output tests ---
    with redirect_output() as output:
        print("hello world")
        print("second line")

    captured = output.getvalue()
    assert "hello world" in captured, f"Expected 'hello world' in output, got: {captured}"
    assert "second line" in captured, f"Expected 'second line' in output, got: {captured}"

    # Verify stdout is restored
    import io

    test_buf = io.StringIO()
    old = sys.stdout
    sys.stdout = test_buf
    print("after context")
    sys.stdout = old
    assert "after context" in test_buf.getvalue()

    print("All sol04 tests passed.")
