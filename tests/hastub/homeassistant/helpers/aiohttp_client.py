"""Stub of homeassistant.helpers.aiohttp_client for offline tests."""


def async_get_clientsession(hass, verify_ssl=True):
    raise RuntimeError("no HTTP session available in the test stub")
