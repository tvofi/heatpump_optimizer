"""Minimal stand-in for ``homeassistant.data_entry_flow``."""
from __future__ import annotations

import voluptuous as vol

FlowResult = dict


class SectionConfig(dict):
    """Upstream is a ``TypedDict``; at runtime that is a plain dict."""


class section:
    """Groups fields into a collapsible block (#516).

    Mirrors ``homeassistant/data_entry_flow.py`` at the declared 2025.2.0
    floor (``class section`` at line 886; introduced in 2024.7.0 and absent
    at the 2024.6.0 floor this integration used to declare, which is why
    grouping was originally parked). Three behaviours are copied because
    tests depend on them, not for completeness:

    * ``schema`` is the ``vol.Schema`` it was handed, kept as an attribute
      rather than merged into the parent. That attribute IS the nesting, and
      it is what ``golden.py``'s ``schema_fingerprint`` recurses into.
    * presentation config lives on ``options``, **not** on ``config``. Every
      selector in ``helpers/selector.py`` exposes ``config``, so a capture
      that reads only ``config`` records ``None`` for a section and never
      looks inside it.
    * ``options`` is validated, so ``collapsed`` defaults to ``False`` and an
      unknown key raises here exactly as it would on a real install.
    """

    CONFIG_SCHEMA = vol.Schema(
        {
            vol.Optional("collapsed", default=False): bool,
        },
    )

    def __init__(
        self, schema: vol.Schema, options: SectionConfig | None = None
    ) -> None:
        self.schema = schema
        self.options: SectionConfig = self.CONFIG_SCHEMA(options or {})

    def __call__(self, value):
        return self.schema(value)


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
