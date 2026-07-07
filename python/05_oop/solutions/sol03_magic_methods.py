"""Solution 03: Magic Methods — Money"""


class Money:
    def __init__(self, amount: float, currency: str = "USD"):
        self.amount = round(amount, 2)
        self.currency = currency

    def __repr__(self) -> str:
        return f"Money({self.amount:.2f}, '{self.currency}')"

    def __str__(self) -> str:
        if self.currency == "USD":
            return f"${self.amount:.2f}"
        return f"{self.amount:.2f} {self.currency}"

    def _check_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot operate on different currencies: "
                f"{self.currency} and {other.currency}"
            )

    def __add__(self, other: "Money") -> "Money":
        self._check_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        self._check_currency(other)
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: float) -> "Money":
        return Money(self.amount * factor, self.currency)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount and self.currency == other.currency

    def __lt__(self, other: "Money") -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        self._check_currency(other)
        return self.amount < other.amount

    def __bool__(self) -> bool:
        return self.amount != 0


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
