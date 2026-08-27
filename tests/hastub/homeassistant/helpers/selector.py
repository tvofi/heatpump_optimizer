"""Minimal stand-in for ``homeassistant.helpers.selector``.

The selectors are pure declarations in the config flow, so the stub only has
to record what it was given. Tests assert on the resulting schema structure,
not on how the frontend would render it.
"""


class _Config(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for key, value in kwargs.items():
            setattr(self, key, value)


class _Selector:
    def __init__(self, config=None):
        self.config = config or {}

    def __call__(self, value):
        return value


class SelectSelectorConfig(_Config):
    pass


class SelectSelectorMode(str):
    DROPDOWN = "dropdown"
    LIST = "list"


class SelectSelector(_Selector):
    """Mirrors the one validation rule of the real selector that bites.

    Home Assistant coerces the incoming value with ``vol.Schema(str)`` before
    matching it against the options, so a non-string default — an int number of
    minutes against string options, say — fails with "expected str" the moment
    the user leaves that field untouched. The stub used to accept anything,
    which let exactly that bug reach a release.
    """

    def __call__(self, value):
        if not isinstance(value, str):
            raise ValueError(f"expected str, got {type(value).__name__}: {value!r}")
        options = self.config.get("options") or []
        if options and value not in options:
            raise ValueError(f"{value!r} is not one of {options}")
        return value


class NumberSelectorConfig(_Config):
    pass


class NumberSelectorMode(str):
    BOX = "box"
    SLIDER = "slider"


class NumberSelector(_Selector):
    """Mirrors the real selector's validation: coerce to float, then range.

    Home Assistant runs ``vol.Coerce(float)`` on the incoming value and
    rejects anything outside the configured min/max, so a page default that
    cannot coerce — or sits outside its own declared range — fails the moment
    the user submits the form untouched. A stub that accepts anything hides
    exactly that class of bug.
    """

    def __call__(self, value):
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError(
                f"expected a number, got {type(value).__name__}: {value!r}"
            ) from None
        minimum = self.config.get("min")
        if minimum is not None and value < minimum:
            raise ValueError(f"{value} is below the minimum {minimum}")
        maximum = self.config.get("max")
        if maximum is not None and value > maximum:
            raise ValueError(f"{value} is above the maximum {maximum}")
        return value


class TextSelectorConfig(_Config):
    pass


class TextSelectorType(str):
    TEXT = "text"
    PASSWORD = "password"


class TextSelector(_Selector):
    pass


class EntitySelectorConfig(_Config):
    pass


class EntitySelector(_Selector):
    pass


class LocationSelectorConfig(_Config):
    pass


class LocationSelector(_Selector):
    pass


class BooleanSelector(_Selector):
    pass


class TimeSelector(_Selector):
    pass
