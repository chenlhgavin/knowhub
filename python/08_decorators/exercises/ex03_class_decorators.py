"""Exercise 03: Class Decorators

Implement decorators that modify or wrap classes, adding functionality
like singleton enforcement, automatic __repr__, and immutability.
"""

import inspect


def singleton(cls):
    """Class decorator: ensure only one instance of the class exists.

    Subsequent calls to the constructor return the same instance.

    Usage:
        @singleton
        class Database:
            def __init__(self, url):
                self.url = url

        db1 = Database("postgres://localhost")
        db2 = Database("postgres://localhost")
        assert db1 is db2
    """
    raise NotImplementedError("Implement the singleton class decorator")


def auto_repr(cls):
    """Class decorator: automatically add __repr__ based on __init__ parameters.

    Uses the inspect module to discover __init__ parameter names (excluding 'self').
    The generated __repr__ should look like: ClassName(param1=value1, param2=value2)

    Usage:
        @auto_repr
        class Point:
            def __init__(self, x, y):
                self.x = x
                self.y = y

        p = Point(1, 2)
        repr(p)  # "Point(x=1, y=2)"
    """
    raise NotImplementedError("Implement the auto_repr class decorator")


def frozen(cls):
    """Class decorator: make instances immutable after __init__.

    After __init__ completes, any attempt to set an attribute should raise
    AttributeError with message "Cannot modify frozen instance".

    Hint: override __setattr__. During __init__, allow normal attribute setting.

    Usage:
        @frozen
        class Config:
            def __init__(self, debug, verbose):
                self.debug = debug
                self.verbose = verbose

        c = Config(True, False)
        c.debug  # True
        c.debug = False  # raises AttributeError
    """
    raise NotImplementedError("Implement the frozen class decorator")


if __name__ == "__main__":

    # --- singleton tests ---
    @singleton
    class Database:
        def __init__(self, url):
            self.url = url

    db1 = Database("postgres://localhost")
    db2 = Database("mysql://localhost")
    assert db1 is db2, "singleton must return the same instance"
    assert db1.url == "postgres://localhost", "First call's args should stick"

    # --- auto_repr tests ---
    @auto_repr
    class Point:
        def __init__(self, x, y):
            self.x = x
            self.y = y

    p = Point(1, 2)
    assert repr(p) == "Point(x=1, y=2)", f"Unexpected repr: {repr(p)}"

    @auto_repr
    class Person:
        def __init__(self, name, age):
            self.name = name
            self.age = age

    person = Person("Alice", 30)
    assert repr(person) == "Person(name='Alice', age=30)", f"Unexpected repr: {repr(person)}"

    # --- frozen tests ---
    @frozen
    class Config:
        def __init__(self, debug, verbose):
            self.debug = debug
            self.verbose = verbose

    c = Config(True, False)
    assert c.debug is True
    assert c.verbose is False

    try:
        c.debug = False
        assert False, "Should have raised AttributeError"
    except AttributeError as e:
        assert "frozen" in str(e).lower(), f"Unexpected error message: {e}"

    try:
        c.new_attr = "value"
        assert False, "Should have raised AttributeError"
    except AttributeError:
        pass

    print("All ex03 tests passed.")
