"""Exercise 03: Magic Methods — Money

Implement a Money class that supports arithmetic and comparison operations.

Requirements:
- Money(amount: float, currency: str = "USD")
- __repr__ -> "Money(10.00, 'USD')"
- __str__  -> "$10.00" for USD, "10.00 EUR" for other currencies
- __add__  -> add amounts if same currency, raise ValueError if different
- __sub__  -> subtract amounts if same currency, raise ValueError if different
- __mul__(factor: float) -> multiply amount by factor
- __eq__   -> compare amount and currency
- __lt__   -> compare amount (same currency only, raise ValueError otherwise)
- __bool__ -> True if amount != 0
"""


class Money:
    def __init__(self, amount: float, currency: str = "USD"):
        raise NotImplementedError("Implement __init__")

    def __repr__(self) -> str:
        raise NotImplementedError("Implement __repr__")

    def __str__(self) -> str:
        raise NotImplementedError("Implement __str__")

    def __add__(self, other: "Money") -> "Money":
        raise NotImplementedError("Implement __add__")

    def __sub__(self, other: "Money") -> "Money":
        raise NotImplementedError("Implement __sub__")

    def __mul__(self, factor: float) -> "Money":
        raise NotImplementedError("Implement __mul__")

    def __eq__(self, other: object) -> bool:
        raise NotImplementedError("Implement __eq__")

    def __lt__(self, other: "Money") -> bool:
        raise NotImplementedError("Implement __lt__")

    def __bool__(self) -> bool:
        raise NotImplementedError("Implement __bool__")


if __name__ == "__main__":
    # Construction
    m1 = Money(10.00, "USD")
    m2 = Money(5.50, "USD")
    m3 = Money(20.00, "EUR")

    # __repr__
    assert repr(m1) == "Money(10.00, 'USD')", f"Got {repr(m1)}"
    assert repr(m3) == "Money(20.00, 'EUR')", f"Got {repr(m3)}"

    # __str__
    assert str(m1) == "$10.00", f"Got {str(m1)}"
    assert str(m3) == "20.00 EUR", f"Got {str(m3)}"

    # __add__
    m4 = m1 + m2
    assert repr(m4) == "Money(15.50, 'USD')", f"Got {repr(m4)}"
    try:
        _ = m1 + m3  # different currencies
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    # __sub__
    m5 = m1 - m2
    assert repr(m5) == "Money(4.50, 'USD')", f"Got {repr(m5)}"

    # __mul__
    m6 = m2 * 3
    assert repr(m6) == "Money(16.50, 'USD')", f"Got {repr(m6)}"

    # __eq__
    assert m1 == Money(10.00, "USD")
    assert m1 != m2
    assert m1 != m3
    assert m1 != "not money"

    # __lt__
    assert m2 < m1
    assert not m1 < m2
    try:
        _ = m1 < m3  # different currencies
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    # __bool__
    assert bool(m1) is True
    assert bool(Money(0, "USD")) is False

    print("All tests passed!")
