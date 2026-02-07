"""Solution 03: Class Decorators

Implement decorators that modify or wrap classes, adding functionality
like singleton enforcement, automatic __repr__, and immutability.
"""

import inspect


def singleton(cls):
    """Class decorator: ensure only one instance of the class exists.

    Subsequent calls to the constructor return the same instance.
    """
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    get_instance.__name__ = cls.__name__
    get_instance.__qualname__ = cls.__qualname__
    get_instance.__doc__ = cls.__doc__
    return get_instance


def auto_repr(cls):
    """Class decorator: automatically add __repr__ based on __init__ parameters.

    Uses the inspect module to discover __init__ parameter names (excluding 'self').
    The generated __repr__ looks like: ClassName(param1=value1, param2=value2)
    """
    params = inspect.signature(cls.__init__).parameters
    param_names = [name for name in params if name != "self"]

    def __repr__(self):
        parts = []
        for name in param_names:
            value = getattr(self, name)
            parts.append(f"{name}={value!r}")
        return f"{cls.__name__}({', '.join(parts)})"

    cls.__repr__ = __repr__
    return cls


def frozen(cls):
    """Class decorator: make instances immutable after __init__.

    After __init__ completes, any attempt to set an attribute raises
    AttributeError with message "Cannot modify frozen instance".
    """
    original_init = cls.__init__

    def new_init(self, *args, **kwargs):
        # Allow attribute setting during __init__ by using object.__setattr__
        # to set a flag
        object.__setattr__(self, "_frozen", False)
        original_init(self, *args, **kwargs)
        object.__setattr__(self, "_frozen", True)

    def new_setattr(self, name, value):
        if getattr(self, "_frozen", False):
            raise AttributeError("Cannot modify frozen instance")
        object.__setattr__(self, name, value)

    cls.__init__ = new_init
    cls.__setattr__ = new_setattr
    return cls


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

    print("All sol03 tests passed.")
