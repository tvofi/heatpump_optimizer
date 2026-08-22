"""Minimal stand-in for ``homeassistant.helpers.entity``."""


class DeviceInfo(dict):
    pass


class EntityCategory(str):
    DIAGNOSTIC = "diagnostic"
    CONFIG = "config"
