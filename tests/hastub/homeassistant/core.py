"""Minimal stand-in for ``homeassistant.core``."""


class HomeAssistant:
    pass


class ServiceCall:
    pass


class SupportsResponse:
    ONLY = "only"
    OPTIONAL = "optional"
    NONE = "none"


def callback(f):
    """Tag ``f`` as a loop callback, as upstream does (``_hass_callback``)."""
    setattr(f, "_hass_callback", True)
    return f
