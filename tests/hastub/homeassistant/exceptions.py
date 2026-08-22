"""Minimal Home Assistant exception hierarchy for the test stub.

Kept faithful to the real classes the integration relies on: the service layer
raises ``ServiceValidationError`` for bad input, and callers catch it (or its
base) rather than a bare ``ValueError``, so the stub must expose the same
inheritance for tests to exercise that path honestly.
"""


class HomeAssistantError(Exception):
    """Base class for Home Assistant errors."""


class ServiceValidationError(HomeAssistantError):
    """A service was called with invalid data."""
