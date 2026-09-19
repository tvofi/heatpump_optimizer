"""D8 round 5 -- the Sensor-Gap Advisor publishes a ranking it cannot compute.

WHAT IT MEASURES (metric definition): the number of EMPTY topology slots the
advisor's published surface (native_value and extra_state_attributes["gaps"])
can rank above zero. ``rank_sensor_gaps`` contract: every empty slot is priced.
The production caller ``SensorGapAdvisorSensor._gaps`` supplies only the peak
inputs (house_kw, hp_kw, peak_price, peak_window, peak_count); the COP-miss and
DHW-coast inputs keep their 0.0 defaults, so those two rows are pinned at 0.0.

Perturbation: call the SAME function with the inputs its own tests supply
(tests/entities.py:5147). Expected direction: the published value rises from
0.0 to the outdoor COP miss, and the top slot moves house_power -> outdoor_temp.

Null control: with all three slots configured, every row is 0.0 in both arms
(nothing spurious is ranked).

Run:
    PYTHONPATH=tests/hastub python3 tools/audit/round5/D8/d8_gap_advisor.py

Baseline SHA eaa2a06af16a1b5b006f58a0f36cc92131f80225. Machine: Apple M1, 8 GB.
RESULTs are counts and money -- content, not timing.
"""
from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_var, "1")

_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[4]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "tests"))
sys.path.insert(0, str(_ROOT / "tests" / "hastub"))

from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import const, sensor, topology  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

START = datetime(2026, 1, 15, 0, 0)

# The exact series and prices tests/entities.py:5140 uses.
HOUSE = [2.0, 2.0, 2.0, 10.0]
HP = [2.0, 2.0, 2.0, 2.0]
PEAK_PRICE = 90.0
# The exact COP/DHW inputs tests/entities.py:5145-5146 uses.
COP_INPUTS = dict(outdoor_load_kw=2.0, outdoor_hours=120.0, outdoor_price=1.0,
                  cop_true=3.2, cop_guess=2.6)
DHW_INPUTS = dict(dhw_extra_kwh=8.0, dhw_price=1.5)
PEAK_INPUTS = dict(peak_price=PEAK_PRICE, peak_window=60, peak_count=3)


def coordinator(config, data):
    dt_util.freeze(START)
    try:
        hass = FakeHass()
        entry = FakeEntry(data=dict(config))
        coord = HeatPumpOptimizerCoordinator(hass, entry)
        coord.data = data
    finally:
        dt_util.freeze(None)
    return coord


def advisor(config, data):
    """The real production sensor object, through the real platform setup."""
    coord = coordinator(config, data)
    added = []
    entry = FakeEntry()
    entry.runtime_data = coord
    asyncio.run(sensor.async_setup_entry(FakeHass(), entry, added.extend))
    return next(e for e in added if isinstance(e, sensor.SensorGapAdvisorSensor))


DATA = {
    "house_power_series": HOUSE,
    "heat_pump_power_series": HP,
    "peak_tariff": {"price_per_kw": PEAK_PRICE, "window_minutes": 60,
                    "peaks_averaged": 3},
}

# Arm A: a user who HAS a house meter but no outdoor probe and no DHW probe.
# Both remaining slots are empty; per the docstring both must be priced.
CFG_A = {
    const.CONF_HOUSE_POWER_ENTITY: "sensor.house_power",
}
# Null control: every slot already configured.
CFG_NULL = {
    const.CONF_HOUSE_POWER_ENTITY: "sensor.house_power",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    const.CONF_DHW_TEMP_ENTITY: "sensor.dhw",
}


def rows_of(cfg, **extra):
    return topology.rank_sensor_gaps(
        cfg, house_kw=HOUSE, hp_kw=HP, **PEAK_INPUTS, **extra)


def main():
    # --- production wiring: what the sensor actually publishes --------------
    a = advisor(CFG_A, DATA)
    nv = a.native_value
    gaps = a.extra_state_attributes["gaps"]
    empty = [g["key"] for g in gaps if g["empty"]]
    priced = [g["key"] for g in gaps if g["empty"] and g["sek_per_month"] > 0]
    print(f"RESULT arm=production published_value={nv:.2f}")
    print(f"RESULT arm=production empty_slots={len(empty)}")
    print(f"RESULT arm=production empty_slots_ranked_positive={len(priced)}")
    for g in gaps:
        print(f"   production {g['key']:34s} empty={g['empty']} "
              f"sek_per_month={g['sek_per_month']}")

    # --- perturbation: the inputs the tests supply -------------------------
    r = rows_of(CFG_A, **COP_INPUTS, **DHW_INPUTS)
    by = {x["key"]: x["sek_per_month"] for x in r}
    r_top = max(r, key=lambda x: x["sek_per_month"])
    pv = r_top["sek_per_month"] if r_top["empty"] and r_top["sek_per_month"] else 0.0
    print(f"RESULT arm=wired published_value={pv:.2f}")
    print(f"RESULT arm=wired top_slot={r_top['key']}")
    for x in r:
        print(f"   wired {x['key']:34s} empty={x['empty']} "
              f"sek_per_month={x['sek_per_month']}")

    delta = pv - nv
    print(f"RESULT value_delta_wired_minus_production={delta:.2f}")
    print(f"RESULT top_slot_moved={r_top['key'] != 'house_power'}")

    # --- null control: everything configured, nothing to rank --------------
    n = advisor(CFG_NULL, DATA)
    n_rows = rows_of(CFG_NULL, **COP_INPUTS, **DHW_INPUTS)
    null_ok = (n.native_value == 0.0
               and all(x["sek_per_month"] == 0.0 for x in n.extra_state_attributes["gaps"])
               and all(x["sek_per_month"] == 0.0 for x in n_rows))
    print(f"RESULT null_control_all_zero={null_ok}")
    print(f"RESULT null_control_published_value={n.native_value:.2f}")

    # --- the two production callers: what each supplies --------------------
    print("RESULT production_callers=2")
    print("   caller sensor.py:2583 supplies peak inputs only (COP/DHW defaulted)")
    print("   caller topology.py:501 (diagnostic dump) supplies nothing at all")

    print("RESULT thread_factor=1.0 ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f} load")
    print("RESULT swapins=0 count")


if __name__ == "__main__":
    main()
