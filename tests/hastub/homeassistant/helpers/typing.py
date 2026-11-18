"""Upstream's ``homeassistant.helpers.typing`` sentinel, as the integration uses it.

``async_update_entry`` treats a keyword left at ``UNDEFINED`` as "not given";
``config_flow.identity_update`` returns it when the unique id stays (#1799).
"""
from __future__ import annotations

from enum import Enum


class UndefinedType(Enum):
    """Singleton type for use with not set sentinel values."""

    _singleton = 0


UNDEFINED = UndefinedType._singleton
