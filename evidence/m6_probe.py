"""Reviewer's own probe (not the finder's): live-entity fee goes negative, recovers, goes negative again in ONE instance."""
import sys
sys.path.insert(0, "custom_components")
from heatpump_optimizer import setpoint_check as sc
from homeassistant.helpers import issue_registry as ir
calls = []
ir.async_create_issue = lambda hass, d, i, **k: calls.append(("create", i))
ir.async_delete_issue = lambda hass, d, i: calls.append(("delete", i))
n = sc.ConfigNotices()
for v in (-1.0, None, -1.0):
    n.report(object(), "grid_fee_sign", v, {"rate": "x"})
up = calls[-1] == ("create", "grid_fee_sign")
print("calls", calls)
print(f"RESULT reraised_after_recovery={int(up)}")
