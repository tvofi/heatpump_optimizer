"""D1-s2 round 11, D1.M3 helper: who reads each d1-inputs slot the watchdog never sees.

Metric (one line): per slot, the production functions that call
``hass.states.get(<probe entity>)`` during setup and two cycles, and every
``inputs.InputReader`` reading of it (whatever InputHealth it lands in).
Feeds staleness_unread.py; prints CONSUMER lines, no RESULT defect count.

Command:
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/s2/consumers.py [--slots A,B]
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (export). Machine: macOS arm64, shared box.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d1s2_lib as L  # noqa: E402

import argparse  # noqa: E402
import asyncio  # noqa: E402
from datetime import timedelta  # noqa: E402

import staleness as S  # noqa: E402
from heatpump_optimizer import inputs as inputs_mod  # noqa: E402

CALLERS: dict[str, set] = {}
READS: list = []


class SpyStates(L.FakeHass().states.__class__):
    probe = None

    def get(self, entity_id):
        if entity_id == SpyStates.probe:
            f = sys._getframe(1)
            names = []
            while f is not None and len(names) < 3:
                mod = f.f_globals.get("__name__", "")
                if mod.startswith("heatpump_optimizer"):
                    names.append(f"{mod.split('.')[-1]}:{f.f_code.co_name}")
                f = f.f_back
            CALLERS.setdefault(entity_id, set()).add(" <- ".join(names) or "?")
        return super().get(entity_id)


EXTRA = {
    # feature gates the config flow and EntryConfig read before the slot is used
    "CONF_PV_PRODUCTION_ENTITY": {"pv_enabled": True, "pv_peak_kw": 6.0},
    "CONF_PV_EXPORT_PRICE_ENTITY": {"pv_enabled": True, "pv_peak_kw": 6.0},
    "CONF_AWAY_PRESENCE_ENTITY": {"away_enabled": True},
    "CONF_AWAY_RETURN_ENTITY": {"away_enabled": True},
    "CONF_HOLIDAY_CALENDAR_ENTITY": {"away_enabled": True},
    "CONF_GRID_FEE_ENTITY": {"grid_fee_mode": "entity"},
}


async def drive(slot):
    key = getattr(S.C, slot)
    dom, st, attrs = S.DOMAIN_OF.get(slot, S.TEMP)
    eid = f"{dom}.probe_{key}"
    SpyStates.probe = eid
    states = {k: S.mkstate("sensor", v.state, {"unit_of_measurement": "°C"}, L.T0) for k, v in L.base_states().items()}
    states[eid] = S.mkstate(dom, st, attrs, L.T0 - timedelta(minutes=1))
    hass = L.SchedHass()
    hass.states = SpyStates(states)
    cfg = L.base_config({key: eid, **S.GATES.get(slot, {}), **EXTRA.get(slot, {})})
    coord = L.HeatPumpOptimizerCoordinator(hass, L.FakeEntry(data=cfg))
    await L.drain(hass)
    for i in range(2):
        L.dtu.freeze(L.T0 + timedelta(minutes=15 * i))
        try:
            await coord._async_update_data()
        except Exception as e:  # noqa: BLE001
            print(f"   cycle raised {e!r}")
        await L.drain(hass)
    await coord.async_shutdown()
    await L.drain(hass, 5)
    return eid


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slots", default="")
    a = ap.parse_args()
    slots = [s for s in a.slots.split(",") if s] or S.enumerate_slots()
    real_begin = inputs_mod.InputReader._begin

    def spy_begin(self, key, max_age_minutes, entity_id=None):
        out = real_begin(self, key, max_age_minutes, entity_id)
        if out and out[0] is not None and out[0].entity_id == SpyStates.probe:
            READS.append((SpyStates.probe, key))
        return out
    inputs_mod.InputReader._begin = spy_begin
    for slot in slots:
        CALLERS.clear()
        READS.clear()
        L.reset_globals()
        ps = L.patches() + L.price_patches()
        for p in ps:
            p.start()
        L.dtu.freeze(L.T0)
        try:
            eid = asyncio.run(drive(slot))
        finally:
            L.dtu.freeze(None)
            for p in ps:
                p.stop()
        print(f"CONSUMER {slot}: reader_keys={sorted(set(k for _e, k in READS))} getters={sorted(CALLERS.get(eid, []))}")


if __name__ == "__main__":
    main()
