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
    return f
