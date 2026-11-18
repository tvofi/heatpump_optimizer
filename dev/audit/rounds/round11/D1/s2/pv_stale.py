"""D1-s2 round 11, D1.M3: the PV production input is read past its declared age limit.

Metric (one line): over a grid of report ages (minutes since the PV production
entity's last report), the number of cells where the real cycle
(``_async_update_data``) still publishes the reading as
``data["pv"]["measured_production_kw"]`` -- and seeds step 0 of the PV
forecast from it -- although the age exceeds
``const.INPUT_MAX_AGE_MINUTES[CONF_PV_PRODUCTION_ENTITY]`` (30 min); plus the
same for a report stamped in the future.
Count key: the published ``pv.measured_production_kw`` and the
``coordinator._pv_measured_production`` return, never the planted stamp.

Command:
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/s2/pv_stale.py [--fix] [--fresh]
Expected at baseline: RESULT stale_cells_published=6 (of 6 ages past the
limit) and future_published=1. --fresh (null control: the entity re-reports at
every cycle) -> 0. --fix (perturbation: ``_pv_measured_production`` reads
through ``InputReader.read`` with its declared limit) -> 0.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (export). Machine: macOS arm64, shared box.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d1s2_lib as L  # noqa: E402

import argparse  # noqa: E402
import asyncio  # noqa: E402
import time  # noqa: E402
from datetime import timedelta  # noqa: E402
from unittest import mock  # noqa: E402

from heatpump_optimizer import inputs as inputs_mod  # noqa: E402

C = L.const
EID = "sensor.pv_production"
AGES = [5, 20, 31, 45, 90, 180, 420, 1440]  # minutes since the last report
LIMIT = C.INPUT_MAX_AGE_MINUTES[C.CONF_PV_PRODUCTION_ENTITY]


def pv_state(stamp):
    return L.FakeState("5000", attributes={"unit_of_measurement": "W", "device_class": "power",
                                           "state_class": "measurement"},
                       last_updated=stamp, last_reported=stamp)


def fixed_reader(self, config):
    """The perturbation: the same read, held to the slot's declared age."""
    entity_id = config.production_entity
    if not entity_id:
        return None
    r = inputs_mod.InputReader(self.hass, {}).read(C.CONF_PV_PRODUCTION_ENTITY, entity_id=entity_id)
    if not r.ok:
        return None
    return inputs_mod.state_power_kw(self.hass.states.get(entity_id), sign="clamp")


async def one(age_min, fresh):
    t = L.T0 + timedelta(hours=12)  # midday sun
    L.dtu.freeze(t)
    stamp = t if fresh else t - timedelta(minutes=age_min)
    states = {**L.base_states(), EID: pv_state(stamp)}
    for k in ("sensor.indoor", "sensor.outdoor"):
        states[k] = L.FakeState(states[k].state, last_updated=t, last_reported=t)
    hass = L.SchedHass(states)
    cfg = L.base_config({"pv_enabled": True, "pv_peak_kw": 8.0, C.CONF_PV_PRODUCTION_ENTITY: EID})
    coord = L.HeatPumpOptimizerCoordinator(hass, L.FakeEntry(data=cfg))
    await L.drain(hass)
    d = await coord._async_update_data()
    await L.drain(hass)
    got = (d.get("pv") or {}).get("measured_production_kw")
    direct = coord._pv_measured_production(coord._pv_config())
    await coord.async_shutdown()
    await L.drain(hass, 5)
    return got, direct


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("--fresh", action="store_true")
    a = ap.parse_args()
    proc0, thr0 = time.process_time(), time.thread_time()
    extra = [mock.patch.object(L.coord_mod.HeatPumpOptimizerCoordinator, "_pv_measured_production", fixed_reader)] if a.fix else []
    stale = past = 0
    for age in AGES + [-90]:
        L.reset_globals()
        ps = L.patches() + L.price_patches() + extra
        for p in ps:
            p.start()
        try:
            got, direct = asyncio.run(one(age, a.fresh))
        finally:
            L.dtu.freeze(None)
            for p in ps:
                p.stop()
        over = (not a.fresh) and (age > LIMIT or age < 0)
        print(f"CELL age_min={age} over_limit={over} published={got} direct={direct}")
        if (age > LIMIT) and not (age < 0):
            past += 1
            stale += over and got is not None
        if age < 0 and not a.fresh:
            print(f"RESULT future_published={int(got is not None)} count")
    print(f"RESULT limit_minutes={LIMIT}")
    print(f"RESULT cells_past_limit={past} count")
    print(f"RESULT stale_cells_published={stale} count")
    print(f"RESULT thread_factor={L.thread_factor(proc0, thr0):.3f}")
    print(f"RESULT load1={L.load_avg():.2f}")
    print(f"RESULT swapins={L.swapins()}")


if __name__ == "__main__":
    main()
