"""VERIFIER 3 own harness, D2-02 (independent of the finder's week-window
metric).

METRIC (one line): over a full 365-day year at 15-minute resolution (35040
windows), v3_discounted_year = count of windows whose
CapacityTariff.sample_factor < 1.0 under the exact config the options flow
stores after a DSO catalog selection (config_flow.py:2917's
`cleaned.update(grid_fee.apply_catalog(...))` path), vs
v3_declared_masked_year = count of windows the row's own hours/weekday mask
marks off-peak. Plus the SEK the plan is charged for a pure night/weekend
excess under that config.

EXACT COMMAND (from a tree root):
    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D2/verify03_d2_02.py

ROOT RULE: os.getcwd(). BASELINE SHA of the finding: 7dd68dd.
"""
from __future__ import annotations

import os
import sys

for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")

ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "tools", "audit", "round4", "D2"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "tests", "hastub"))
sys.path.insert(0, os.path.join(ROOT, "custom_components"))

from datetime import datetime, timedelta, timezone  # noqa: E402

import numpy as np  # noqa: E402

from _d2common import Cpu, footer, result  # noqa: E402
import harness  # noqa: E402,F401
from harness import FakeEntry, FakeHass  # noqa: E402
from heatpump_optimizer import const, grid_fee, tariff  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

CPU = Cpu()
YEAR0 = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
N_WIN = 365 * 24 * 4  # 35040 fifteen-minute windows

rows = [r for r in grid_fee.catalog_choices() if r != grid_fee.DSO_PRODUCT_NONE]
result("v3_catalog_rows", len(rows), "count")

for rid in rows:
    # exactly what the options flow stores: defaults + applied catalog keys
    stored = {const.CONF_PEAK_TARIFF_OFFPEAK_FACTOR:
              const.DEFAULT_PEAK_TARIFF_OFFPEAK_FACTOR}
    stored.update(grid_fee.apply_catalog(rid))
    co = HeatPumpOptimizerCoordinator(FakeHass({}), FakeEntry(data=stored))
    with CPU:
        t = co._capacity_tariff()
        when = [YEAR0 + timedelta(minutes=15 * i) for i in range(0, N_WIN, 16)]
        factors = np.array([t.sample_factor(w) for w in when])
    # sampled every 4th window (hour resolution); scale to the full year
    discounted = int(np.sum(factors < 1.0)) * 4
    zeroed = int(np.sum(factors == 0.0)) * 4
    hours = grid_fee.SWEDEN_CATALOG[rid]["peak_tariff_hours"]
    lo, hi = (float(x.split(":")[0]) + float(x.split(":")[1]) / 60.0
              for x in hours.split("-"))
    declared = sum(
        1 for w in when
        if w.weekday() >= 5 or not (lo <= w.hour + w.minute / 60.0 < hi)
    ) * 4
    short = rid.split("_")[0]
    result(f"v3_{short}.stored_offpeak_factor", stored[
        const.CONF_PEAK_TARIFF_OFFPEAK_FACTOR], "factor")
    result(f"v3_{short}.discounted_year", discounted, "windows")
    result(f"v3_{short}.zeroed_by_monthmask_year", zeroed, "windows")
    result(f"v3_{short}.declared_masked_year", declared, "windows")

# money: a 5 kW excess that lives entirely in the row's declared off-peak
# (Saturday 22:00 -> Sunday 06:00, Nov-Mar week, Ellevio)
ELL = "ellevio_villa_effekt_2026"
stored = dict(grid_fee.apply_catalog(ELL))
co = HeatPumpOptimizerCoordinator(FakeHass({}), FakeEntry(data=stored))
t = co._capacity_tariff()
sat_night = datetime(2026, 11, 7, 22, 0, tzinfo=timezone.utc)
n = 8 * 4
house = np.full(n, 5.0)
wf = tariff.window_factors(t, sat_night, n, 0.25)
with CPU:
    charged = tariff.peak_cost(
        house, np.zeros(n), 0.0, t.marginal_price_per_kw,
        t.window_minutes, 0.25, peaks_averaged=t.peaks_averaged,
        window_factors=wf)
result("v3_ellevio_night_excess_charged_sek", charged, "SEK")
result("v3_ellevio_night_factor_unique",
       "[]" if wf is None else str(np.unique(wf)), "")

footer(CPU, "[v]erify03_d2_02")
