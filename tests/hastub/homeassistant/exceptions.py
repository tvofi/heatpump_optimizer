"""Minimal Home Assistant exception hierarchy for the test stub.

Kept faithful to the real classes the integration relies on: the service layer
raises ``ServiceValidationError`` for bad input, and callers catch it (or its
base) rather than a bare ``ValueError``, so the stub must expose the same
inheritance for tests to exercise that path honestly.
"""


class HomeAssistantError(Exception):
    """Base class for Home Assistant errors.

    Faithful to the real class on the one axis these tests read: a raise may
    carry ``translation_domain`` / ``translation_key`` /
    ``translation_placeholders`` and every one of them lands on the instance
    (defaulting to ``None``), which is what the frontend renders a
    translatable error from. A stub without those attributes would make every
    translation check pass vacuously by crashing on the kwargs instead.
    """

    def __init__(self, *args, **kwargs) -> None:
        """Initialize a Home Assistant error, keeping the translation kwargs."""
        super().__init__(*args)
        self.translation_domain = kwargs.get("translation_domain")
        self.translation_key = kwargs.get("translation_key")
        self.translation_placeholders = kwargs.get("translation_placeholders")


class ServiceValidationError(HomeAssistantError):
    """A service was called with invalid data."""
