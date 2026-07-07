"""Solution 04: Properties — Temperature"""


class Temperature:
    def __init__(self, celsius: float):
        self.celsius = celsius  # uses the setter (triggers validation)

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float):
        if value < -273.15:
            raise ValueError(
                f"Temperature {value}°C is below absolute zero (-273.15°C)"
            )
        self._celsius = value

    @property
    def fahrenheit(self) -> float:
        return self._celsius * 9 / 5 + 32

    @fahrenheit.setter
    def fahrenheit(self, value: float):
        self.celsius = (value - 32) * 5 / 9

    @property
    def kelvin(self) -> float:
        return self._celsius + 273.15

    def __repr__(self) -> str:
        return f"Temperature({self._celsius}\u00b0C)"


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
