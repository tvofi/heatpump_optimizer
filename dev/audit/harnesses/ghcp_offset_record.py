#!/usr/bin/env python3
"""Kind offset's off-restore record, dumped (R10-GENERIC-HEAT-CURVE-PERSISTENT's null control).

The design note's round-2 ruling (a): C1's entity record and rule R bind only
a consumer with no neutral, so kind ``offset`` keeps #3299's record and its
disarm-on-unconfigured rule. Run it from a worktree root at e066a630 (#3299's
head) and at the fix head; the two outputs are byte-identical:

    PYTHONPATH=tests/hastub:custom_components:tests \\
        python3 dev/audit/harnesses/ghcp_offset_record.py

Kind ``offset`` on ``number.o`` (K, -20..20, step 0.5), displace 2 (arms):
  (i)   the off-restore Store's saved JSON;
  (ii)  MODE_OFF: the writes and the Store;
  (iii) re-arm, clear the entity in the options, restart, MODE_OFF: the
        writes and the Store (disarmed unwritten).

Perturbation: applying rule R to neutral entries flips (i) to a mapping and
(iii) to a write of 0.
"""
from __future__ import annotations

import asyncio

from harness import FakeEntry, FakeHass, FakeState
from homeassistant.helpers.storage import _DISK
from heatpump_optimizer.const import MODE_AUTO, MODE_OFF
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator

ENTITY = "number.o"
ENTRY_ID = "ghcp_offset_record"
KEY = f"heatpump_optimizer_{ENTRY_ID}_off_restore"


def coord(hass, entity=ENTITY):
    cfg = {"tibber_token": "x", "weather_entity": "weather.home", "heat_curve_target_kind": "offset"}
    if entity:
        cfg["heat_curve_displace_entity"] = entity
    return HeatPumpOptimizerCoordinator(hass, FakeEntry(data=cfg, entry_id=ENTRY_ID))


def writes(c):
    return [(d.get("entity_id"), d.get("value")) for _, s, d in c.hass.services.calls if s == "set_value"]


def main() -> None:
    hass = FakeHass()
    hass.states.set(ENTITY, FakeState("0", unit="K", attributes={"step": 0.5, "min": -20.0, "max": 20.0}))
    c = coord(hass)
    asyncio.run(c.async_publish_ecl110_command(2.0, True))
    print("(i)", _DISK.get(KEY))
    asyncio.run(c.async_set_mode(MODE_OFF, refresh=False))
    print("(ii)", writes(c), _DISK.get(KEY))
    asyncio.run(c.async_set_mode(MODE_AUTO, refresh=False))
    asyncio.run(c.async_publish_ecl110_command(2.0, True))
    before = len(writes(c))
    c2 = coord(hass, entity=None)
    asyncio.run(c2.async_set_mode(MODE_OFF, refresh=False))
    print("(iii)", writes(c2)[before:], _DISK.get(KEY))


if __name__ == "__main__":
    main()
