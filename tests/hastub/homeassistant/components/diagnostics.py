"""Stand-in for ``homeassistant.components.diagnostics``.

Only ``async_redact_data``, the helper an integration's ``diagnostics.py``
imports, reproduced from Home Assistant's own
``homeassistant/components/diagnostics/util.py``: substitute ``REDACTED`` for
every value whose key is in ``to_redact``, at any depth, recursing through
mappings and lists.

Destination: tests/hastub/homeassistant/components/diagnostics.py
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

REDACTED = "**REDACTED**"


def async_redact_data(
    data: Any, to_redact: Iterable[Any] | Mapping[Any, Any]
) -> Any:
    """Redact sensitive data in a dict."""
    if not isinstance(data, (Mapping, list)):
        return data

    if isinstance(data, list):
        return [async_redact_data(val, to_redact) for val in data]

    redacted = {**data}

    for key, value in redacted.items():
        if key in to_redact:
            if isinstance(to_redact, Mapping):
                redacted[key] = to_redact[key]
            else:
                redacted[key] = REDACTED
        elif isinstance(value, Mapping):
            redacted[key] = async_redact_data(value, to_redact)
        elif isinstance(value, list):
            redacted[key] = [async_redact_data(item, to_redact) for item in value]

    return redacted
