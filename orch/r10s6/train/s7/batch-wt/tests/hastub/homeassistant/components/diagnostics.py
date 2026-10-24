"""Stand-in for ``homeassistant.components.diagnostics``.

``async_redact_data`` and ``REDACTED``, the two names an integration's
``diagnostics.py`` imports, reproduced from Home Assistant's own
``diagnostics/util.py`` and ``diagnostics/const.py`` (both re-exported from
that package's ``__init__``, which names them in ``__all__``).

Faithful to upstream in the two places that are easy to get wrong, because
real Home Assistant is not installed here and this stub is what the tests
actually execute: a ``None`` value and an empty string are **skipped**, not
redacted, so ``async_redact_data({"k": None}, {"k"})["k"]`` is ``None`` and
not the marker. ``to_redact`` is a plain iterable of key names; upstream has
no mapping-of-replacements form.

Destination: tests/hastub/homeassistant/components/diagnostics.py
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

REDACTED = "**REDACTED**"


def async_redact_data(data: Any, to_redact: Iterable[Any]) -> Any:
    """Redact sensitive data in a dict."""
    if not isinstance(data, (Mapping, list)):
        return data

    if isinstance(data, list):
        return [async_redact_data(val, to_redact) for val in data]

    redacted = {**data}

    for key, value in redacted.items():
        if value is None:
            continue
        if isinstance(value, str) and not value:
            continue
        if key in to_redact:
            redacted[key] = REDACTED
        elif isinstance(value, Mapping):
            redacted[key] = async_redact_data(value, to_redact)
        elif isinstance(value, list):
            redacted[key] = [async_redact_data(item, to_redact) for item in value]

    return redacted
