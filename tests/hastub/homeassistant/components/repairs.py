"""Stand-in for ``homeassistant.components.repairs``.

Home Assistant loads an integration's ``repairs.py`` by convention and
looks up ``async_create_fix_flow``. The production module subclasses
these types; tests instantiate a flow and drive ``async_step_confirm``
directly, the same way ``tests/config_flow_steps.py`` drives options
handlers without a flow manager.

Destination: tests/hastub/homeassistant/components/repairs.py
"""
from __future__ import annotations

from typing import Any


class RepairsFlow:
    """Handler for a repair issue. Real HA stamps ``issue_id`` and ``data``."""

    issue_id: str = ""
    data: dict[str, Any] | None = None
    hass: Any = None

    def async_show_form(self, **kwargs):
        return {"type": "form", **kwargs}

    def async_create_entry(self, **kwargs):
        return {"type": "create_entry", **kwargs}

    def async_abort(self, **kwargs):
        return {"type": "abort", **kwargs}


class ConfirmRepairFlow(RepairsFlow):
    """Issue whose Fix is a confirmation only."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        return await self.async_step_confirm(user_input)

    async def async_step_confirm(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            return self.async_create_entry(title="", data={})
        return self.async_show_form(step_id="confirm")
