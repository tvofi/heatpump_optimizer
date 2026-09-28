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


class IntegrationError(HomeAssistantError):
    """Base class for errors raised during integration setup.

    It exists so a caller can catch every config-entry setup error at once,
    and the classes below hang off it. Not empty upstream: the real base's
    ``__str__`` falls back to the cause (``exceptions.py:198-203``), so an
    integration error raised ``from`` an underlying exception reports that
    exception when it carries no message of its own -- the shape
    ``async_config_entry_first_refresh`` produces (#924).
    """

    def __str__(self) -> str:
        """Return a human readable error, the cause's when there is none."""
        return super().__str__() or str(self.__cause__)


class ConfigEntryNotReady(IntegrationError):
    """A config entry could not finish setting up; retry later.

    The base class's first refresh raises this when the update fails
    (upstream: ``async_config_entry_first_refresh`` raises it unless
    ``last_update_success``). The integration's setup documents exactly that
    contract -- Home Assistant then runs the entry's ``async_on_load``
    callbacks and nothing else (#236) -- so the stub carries the real class,
    not a look-alike, for a test to exercise the retry path honestly.
    """
