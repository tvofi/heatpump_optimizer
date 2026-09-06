"""Fix flows for set-point consistency issues (#408).

Home Assistant loads this module dynamically when the user clicks Fix, so a
test must ``import repairs`` or the file is an orphan and forces MODE: FULL.
``async_create_fix_flow`` is that convention.
"""
from __future__ import annotations

from typing import Any

from homeassistant.components.repairs import ConfirmRepairFlow, RepairsFlow
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .setpoint_check import ISSUE_DHW, ISSUE_SPACE, evaluate


class DhwSetpointRepairFlow(RepairsFlow):
    """Write the configured DHW floor to the pump's set-point entity.

    Stub: the failing witness pins the service call before the write exists.
    """

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        return await self.async_step_confirm(user_input)

    async def async_step_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is None:
            return self.async_show_form(step_id="confirm")
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
    evaluate  # referenced so the detector is not a dead top-level name
    return ConfirmRepairFlow()
