"""Fix flows for set-point consistency issues (#408).

Home Assistant loads this module dynamically when the user clicks Fix, so a
test must ``import repairs`` or the file is an orphan and forces MODE: FULL.
``async_create_fix_flow`` is that convention.
"""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.repairs import ConfirmRepairFlow, RepairsFlow
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import issue_registry as ir

from .const import DOMAIN
from .setpoint_check import ISSUE_DHW, ISSUE_SPACE

_LOGGER = logging.getLogger(__name__)

_NUMERIC_DOMAINS = ("number", "input_number")


class DhwSetpointRepairFlow(RepairsFlow):
    """Write the configured DHW floor to the pump's set-point entity."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        return await self.async_step_confirm(user_input)

    async def async_step_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        data = self.data or {}
        target = data.get("target")
        if user_input is None:
            return self.async_show_form(
                step_id="confirm",
                description_placeholders={
                    "entity": str(data.get("entity_id") or ""),
                    "target": f"{float(target):.0f}"
                    if target is not None
                    else "",
                },
            )
        entity_id = data.get("entity_id")
        if entity_id and target is not None:
            await _write_setpoint(self.hass, str(entity_id), float(target))
        try:
            ir.async_delete_issue(self.hass, DOMAIN, ISSUE_DHW)
        except Exception as err:  # noqa: BLE001 - clearing is best-effort
            _LOGGER.debug("Could not clear %s after repair: %s", ISSUE_DHW, err)
        return self.async_create_entry(data={})


async def _write_setpoint(hass: Any, entity_id: str, target: float) -> None:
    domain = entity_id.split(".", 1)[0]
    value = round(float(target), 1)
    if domain == "climate":
        await hass.services.async_call(
            "climate",
            "set_temperature",
            {"entity_id": entity_id, "temperature": value},
            blocking=True,
        )
        return
    if domain in _NUMERIC_DOMAINS:
        await hass.services.async_call(
            domain,
            "set_value",
            {"entity_id": entity_id, "value": value},
            blocking=True,
        )


async def async_create_fix_flow(
    hass: HomeAssistant,
    issue_id: str,
    data: dict[str, str | int | float | None] | None,
) -> RepairsFlow:
    if issue_id == ISSUE_DHW:
        return DhwSetpointRepairFlow()
    if issue_id == ISSUE_SPACE:
        return ConfirmRepairFlow()
    return ConfirmRepairFlow()
