"""D1-s2 round 11, D1.M2 perturbation: a persisted hold driven across a restart to the first actuator write.

Metric (one line): of hold records written by the previous run (every
hold-bearing store is v1 with no earlier version, so the previous release's
record is this shape) whose hold EXPIRED during the downtime -- an away
override past its return time, a DHW/space boost past its end, a duty block
past its end, the off-mode stand-in armed while the mode is no longer off --
how many are still in force after the restart: published as active, or
written to an actuator by the first cycle's ``services.async_call``.
Controls: the same records with the hold still running (must stay in force).
Count key: the published ``away_override_active`` / ``boost_*_active`` and the
service calls the cycle makes, never the planted record.

Command:
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/s2/hold_restore.py
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (export). Machine: macOS arm64, shared box.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d1s2_lib as L  # noqa: E402

import asyncio  # noqa: E402
import json  # noqa: E402
import time  # noqa: E402
from datetime import timedelta  # noqa: E402

C = L.const
KP = f"{C.DOMAIN}_{L.ENTRY_ID}_"
T0 = L.T0
PAST = (T0 - timedelta(hours=1)).isoformat()
FUTURE = (T0 + timedelta(hours=1)).isoformat()

SCENARIOS = [
    # (name, store, record, published key to read, expired?)
    ("away expired", "away", {"active": True, "return_time": PAST, "migrated_helpers": True}, "away_override_active", True),
    ("away running", "away", {"active": True, "return_time": FUTURE, "migrated_helpers": True}, "away_override_active", False),
    ("boost dhw expired", "boost", {"dhw": {"until": PAST}}, "boost_dhw_active", True),
    ("boost dhw running", "boost", {"dhw": {"until": FUTURE}}, "boost_dhw_active", False),
    ("boost space expired", "boost", {"space": {"until": PAST, "since": (T0 - timedelta(hours=3)).isoformat()}}, "boost_space_active", True),
    ("boost space running", "boost", {"space": {"until": FUTURE, "since": (T0 - timedelta(hours=1)).isoformat()}}, "boost_space_active", False),
    ("block dhw expired", "boost", {"block_dhw": {"until": PAST}}, "dhw_blocked", True),
    ("block dhw running", "boost", {"block_dhw": {"until": FUTURE}}, "dhw_blocked", False),
    ("off stand-in armed, mode auto", "off_restore", {"armed": {"heat_curve": None, "stand_in": 21.5}}, None, True),
]


def states():
    st = L.base_states()
    for eid, v in (("number.space_sp", "19.0"), ("number.dhw_sp", "50.0"), ("number.curve", "0")):
        st[eid] = L.FakeState(v, attributes={"unit_of_measurement": "°C", "min": 5, "max": 70, "step": 0.5},
                              last_updated=T0, last_reported=T0)
    return st


async def one(store, record):
    L.storage_stub._DISK.clear()
    L.storage_stub._VERSIONS.clear()
    L.storage_stub._DISK[KP + store] = json.dumps(record)
    L.storage_stub._VERSIONS[KP + store] = 1
    hass = L.SchedHass(states())
    cfg = L.base_config({"away_enabled": True, C.CONF_SPACE_SETPOINT_ENTITY: "number.space_sp",
                         C.CONF_DHW_SETPOINT_ENTITY: "number.dhw_sp", C.CONF_HEAT_CURVE_DISPLACE_ENTITY: "number.curve",
                         C.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.hp"})
    coord = L.HeatPumpOptimizerCoordinator(hass, L.FakeEntry(data=cfg))
    await L.drain(hass)
    from heatpump_optimizer import off_restore
    await off_restore._armed_record(hass, coord.entry)
    hass.services.calls.clear()
    d = await coord._async_update_data()
    await L.drain(hass)
    from heatpump_optimizer import boost
    held = boost.held_for(coord)
    calls = [c for c in hass.services.calls if c[0] not in ("weather",)]
    after = json.loads(L.storage_stub._DISK.get(KP + store, "null"))
    await coord.async_shutdown()
    await L.drain(hass, 5)
    return d, held, calls, after


def main():
    proc0, thr0 = time.process_time(), time.thread_time()
    stuck = ctrl_lost = 0
    for name, store, record, key, expired in SCENARIOS:
        L.reset_globals()
        ps = L.patches() + L.price_patches()
        for p in ps:
            p.start()
        L.dtu.freeze(T0)
        try:
            d, held, calls, after = asyncio.run(one(store, record))
        finally:
            L.dtu.freeze(None)
            for p in ps:
                p.stop()
        if key == "dhw_blocked":
            active = "dhw" in held.blocked
        elif key in ("boost_dhw_active", "boost_space_active"):
            # the boost module's own held state (boost.held_for); it publishes through its entities
            active = key.split("_")[1] in held.until
        elif key is None:
            active = any(c[2] and 21.5 in [v for v in (c[2] or {}).values() if isinstance(v, (int, float))] for c in calls)
        else:
            active = bool(d.get(key))
        print(f"HOLD {name}: in_force={active} calls={[(c[0], c[1], {k: v for k, v in (c[2] or {}).items() if k != 'entity_id'}) for c in calls][:4]} "
              f"store_after={json.dumps(after)[:120]}")
        if expired and active:
            stuck += 1
        if not expired and not active:
            ctrl_lost += 1
    print(f"RESULT scenarios={len(SCENARIOS)} count")
    print(f"RESULT expired_hold_in_force={stuck} count")
    print(f"RESULT running_hold_lost={ctrl_lost} count")
    print(f"RESULT thread_factor={L.thread_factor(proc0, thr0):.3f}")
    print(f"RESULT load1={L.load_avg():.2f}")
    print(f"RESULT swapins={L.swapins()}")


if __name__ == "__main__":
    main()
