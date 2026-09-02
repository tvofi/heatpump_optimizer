"""Minimal stand-in for ``homeassistant.data_entry_flow``."""
from __future__ import annotations

FlowResult = dict


class FlowError(Exception):
    """Base class for data entry flow errors."""


class AbortFlow(FlowError):
    """Raised inside a step to abort the flow; the manager turns it into an
    abort result. Mirrors the real class: ``reason`` is the abort key looked
    up in ``strings.json`` (``config.abort.<reason>``)."""

    def __init__(self, reason: str, description_placeholders=None) -> None:
        super().__init__(f"Flow aborted: {reason}")
        self.reason = reason
        self.description_placeholders = description_placeholders
