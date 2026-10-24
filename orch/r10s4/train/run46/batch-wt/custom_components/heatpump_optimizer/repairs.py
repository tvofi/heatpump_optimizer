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
from .inputs import write_setpoint
from .setpoint_check import ISSUE_DHW, ISSUE_SPACE

_LOGGER = logging.getLogger(__name__)

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
        # ``value`` is the target in the entity's own unit (#1513); a notice
        # raised before it existed carries only the degC ``target``.
        value = data.get("value", target)
        if entity_id and value is not None:
            await write_setpoint(self.hass, str(entity_id), float(value))
        try:
            ir.async_delete_issue(self.hass, DOMAIN, ISSUE_DHW)
        except Exception as err:  # noqa: BLE001 - clearing is best-effort
            _LOGGER.debug("Could not clear %s after repair: %s", ISSUE_DHW, err)
        return self.async_create_entry(data={})


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
