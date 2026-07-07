"""
Solution 02: Metaclasses

Implements:
- RegistryMeta metaclass for automatic subclass registration
- ValidatedMeta metaclass for enforcing class structure
"""


class RegistryMeta(type):
    """A metaclass that automatically registers all subclasses.

    When a class is created using this metaclass, if it has base classes
    (i.e., it is a subclass, not the base itself), it is added to the
    base class's _registry dict mapping class name -> class.

    The base class should initialize _registry as an empty dict.
    Subclasses should be added to the base class's _registry.
    """

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if not bases:
            # This is the base class itself -- initialize the registry
            cls._registry = {}
        else:
            # This is a subclass -- register it on the base class
            cls._registry[name] = cls
        return cls


class Plugin(metaclass=RegistryMeta):
    """Base class using RegistryMeta. Subclasses are auto-registered."""
    pass


class AudioPlugin(Plugin):
    """An audio plugin. Should be auto-registered."""
    pass


class VideoPlugin(Plugin):
    """A video plugin. Should be auto-registered."""
    pass


class ValidatedMeta(type):
    """A metaclass that ensures all classes define a validate() method.

    If a class created with this metaclass has base classes (is a subclass)
    and does not define a 'validate' method in its own namespace, raise
    TypeError with a descriptive message.
    """

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if bases and "validate" not in namespace:
            raise TypeError(
                f"Class {name} must define a validate() method"
            )
        return cls


class BaseModel(metaclass=ValidatedMeta):
    """Base class using ValidatedMeta."""

    def validate(self):
        return True


if __name__ == "__main__":
    # --- Test RegistryMeta ---
    assert hasattr(Plugin, "_registry"), "Plugin should have _registry attribute"
    assert isinstance(Plugin._registry, dict), "_registry should be a dict"
    assert "AudioPlugin" in Plugin._registry, "AudioPlugin should be registered"
    assert "VideoPlugin" in Plugin._registry, "VideoPlugin should be registered"
    assert Plugin._registry["AudioPlugin"] is AudioPlugin
    assert Plugin._registry["VideoPlugin"] is VideoPlugin
    assert "Plugin" not in Plugin._registry, "Base class should not register itself"
    assert len(Plugin._registry) == 2, f"Expected 2 entries, got {len(Plugin._registry)}"

    print("RegistryMeta: all tests passed")

    # --- Test ValidatedMeta raises TypeError for missing validate() ---
    try:
        class BadModel(BaseModel):
            pass  # No validate() method defined

        assert False, "Should have raised TypeError for missing validate()"
    except TypeError as e:
        assert "validate" in str(e).lower(), f"Error should mention validate: {e}"

    # Verify that a proper subclass works
    class GoodModel(BaseModel):
        def validate(self):
            return self is not None

    good = GoodModel()
    assert good.validate() is True

    print("ValidatedMeta: all tests passed")

    # --- Test that new subclasses of Plugin are registered dynamically ---
    class TextPlugin(Plugin):
        pass

    assert "TextPlugin" in Plugin._registry
    assert Plugin._registry["TextPlugin"] is TextPlugin
    assert len(Plugin._registry) == 3

    print("Dynamic registration: all tests passed")

    print("\nAll solution 02 tests passed!")
