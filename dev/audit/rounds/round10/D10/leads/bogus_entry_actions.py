"""Leads seat (round 10), owner D10-s1, D10.M1 action-exceptions: actions that accept a bogus entry_id.

Metric: number of registered heat_pump_optimizer actions that, called with entry_id set to an id no
  config entry has and otherwise the smallest payload their own registered voluptuous schema accepts
  (schema applied, as Home Assistant applies it), return without raising.
Count key: whether the production handler (the function services.async_register_services registered)
  raises when awaited; a return is counted, a HomeAssistantError (ServiceValidationError) is not.
Command (from the export root):
  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D10/leads/bogus_entry_actions.py [--perturb]
Expected at baseline 17f1c55fad1b: RESULT actions_silent_on_bogus_entry=1 count (apply_schedule), tolerance 0.
Perturbation (--perturb, in memory): services.handle_apply_schedule is wrapped so it resolves
  services._loaded_entries(hass, entry_id) before its early "nothing to apply" return (the one-line
  reorder a fix would make); the count must fall to 0.
Seam rule: every action in hass.services.async_services()[DOMAIN], driven by this loop.
Machine: macOS arm64 (leads seat). Counts only, contention-immune.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import sys
import time

sys.path.insert(0, "tests")
sys.path.insert(0, ".")
t0p, t0t = time.process_time(), time.thread_time()

from harness import FakeHass, FakeServiceCall  # noqa: E402
from homeassistant.exceptions import HomeAssistantError  # noqa: E402
from custom_components.heatpump_optimizer import const  # noqa: E402
from custom_components.heatpump_optimizer import services as svc  # noqa: E402

PERTURB = "--perturb" in sys.argv
BOGUS = "0000000000000000000000bogus"
# Minimal extra fields for actions whose schema has required keys (same values
# as D10-s1 rules.py CALL_DATA minus apply_schedule; layout no_valve).
# An action whose schema refuses entry_id (extra keys not allowed) takes no entry
# id at all and is reported as schema_rejected, not counted.
REQUIRED = {"set_mode": {"mode": "auto"}, "set_away": {"active": True},
            "debug_collect": {"action": "status"},
            "assign_entity": {"key": "outdoor_temp_entity", "entity_id": ""},
            "apply_topology": {"layout": "no_valve"}}

if PERTURB:
    _orig = svc.handle_apply_schedule

    async def _fixed(hass, call):
        svc._loaded_entries(hass, call.data.get("entry_id"))
        return await _orig(hass, call)

    svc.handle_apply_schedule = _fixed

hass = FakeHass()
svc.async_register_services(hass)
silent, raised, rejected, other = [], 0, [], []
for name, handler in sorted(hass.services.async_services()[const.DOMAIN].items()):
    schema = hass.services._schemas.get((const.DOMAIN, name))
    raw = {"entry_id": BOGUS, **REQUIRED.get(name, {})}
    try:
        data = schema(raw) if schema is not None else raw
    except Exception as err:  # noqa: BLE001 -- schema refuses: HA would refuse too
        rejected.append(f"{name}:{type(err).__name__}")
        continue
    try:
        asyncio.run(handler(FakeServiceCall(const.DOMAIN, name, data)))
        silent.append(name)
    except HomeAssistantError:
        raised += 1
    except Exception as err:  # noqa: BLE001
        other.append(f"{name}:{type(err).__name__}:{err}")

print(f"silent={silent}")
print(f"schema_rejected={rejected}")
print(f"other={other}")
print(f"RESULT actions_total={len(hass.services.async_services()[const.DOMAIN])} count")
print(f"RESULT actions_raised_on_bogus_entry={raised} count")
print(f"RESULT actions_silent_on_bogus_entry={len(silent)} count")
pc, tc = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=na")
