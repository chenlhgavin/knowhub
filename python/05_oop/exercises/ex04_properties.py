"""Exercise 04: Properties — Temperature

Implement a Temperature class with properties that convert between scales.

Requirements:
- __init__(celsius: float)
- property celsius: getter and setter
- property fahrenheit: getter and setter (F = C * 9/5 + 32)
- property kelvin: getter only (K = C + 273.15), read-only
- Setting celsius below -273.15 must raise ValueError
- __repr__ -> "Temperature(20.0°C)"
"""


class Temperature:
    def __init__(self, celsius: float):
        raise NotImplementedError("Implement __init__")

    @property
    def celsius(self) -> float:
        raise NotImplementedError("Implement celsius getter")

    @celsius.setter
    def celsius(self, value: float):
        raise NotImplementedError("Implement celsius setter")

    @property
    def fahrenheit(self) -> float:
        raise NotImplementedError("Implement fahrenheit getter")

    @fahrenheit.setter
    def fahrenheit(self, value: float):
        raise NotImplementedError("Implement fahrenheit setter")

    @property
    def kelvin(self) -> float:
        raise NotImplementedError("Implement kelvin getter")

    def __repr__(self) -> str:
        raise NotImplementedError("Implement __repr__")


if __name__ == "__main__":
    # Basic construction
    t = Temperature(20.0)
    assert t.celsius == 20.0
    assert repr(t) == "Temperature(20.0°C)", f"Got {repr(t)}"

    # Celsius to Fahrenheit
    t.celsius = 100.0
    assert t.fahrenheit == 212.0, f"Got {t.fahrenheit}"

    t.celsius = 0.0
    assert t.fahrenheit == 32.0, f"Got {t.fahrenheit}"

    # Fahrenheit to Celsius
    t.fahrenheit = 212.0
    assert t.celsius == 100.0, f"Got {t.celsius}"

    t.fahrenheit = 32.0
    assert t.celsius == 0.0, f"Got {t.celsius}"

    # Kelvin (read-only)
    t.celsius = 0.0
    assert t.kelvin == 273.15, f"Got {t.kelvin}"

    t.celsius = 100.0
    assert t.kelvin == 373.15, f"Got {t.kelvin}"

    # Kelvin is read-only
    try:
        t.kelvin = 300.0
        assert False, "Should have raised AttributeError"
    except AttributeError:
        pass

    # Validation: below absolute zero
    try:
        t.celsius = -300.0
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    try:
        Temperature(-274.0)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    # Valid edge case: absolute zero
    t2 = Temperature(-273.15)
    assert t2.kelvin == 0.0, f"Got {t2.kelvin}"

    print("All tests passed!")
