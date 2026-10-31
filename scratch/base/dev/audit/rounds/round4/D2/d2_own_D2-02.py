"""VERIFIER-OWN harness for round-4 D2-02 (seat D2-1, refute-first).

Independent of the finder's catalog_masks.py in two ways: it counts the
discounted windows with CapacityTariff.sample_factor DIRECTLY (the symbol
PeakTracker.observe and window_snapshot call per window -- a different
production path than window_factors), over MY OWN week (a full Monday-start
November week, and a March one, both inside the Nov-Mar rows' billed
months), and it drives the OPTIMIZER's own mask builder
(optimizer._peak_window_factors' CapacityTariff construction) to show the
inertness reaches the objective, not just the tracker.

METRIC (one line):
  own_discounted_samplefactor = #{15-min slots in a billed week where
  sample_factor(t) < 1.0} under the config apply_catalog(row) writes, built
  by the real coordinator._capacity_tariff; contract: equals the row's
  declared off-peak slots; measured: 0.
  own_optimizer_factors_none  = whether the optimizer's own
  _peak_window_factors returns None (no mask at all) for a catalog config --
  which it must not do while hours/weekdays are configured and a month mask
  is live, so the counting below drives the same builder.

EXACT COMMAND (from a tree root):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
    /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
    tools/audit/round4/D2/d2_own_D2-02.py

EXPECTED (baseline 7dd68dd; exact counts, tolerance 0):
  own_rows                     = 4
  own_rows_writing_offpeak     = 0
  own_ellevio_discounted_nov   = 0     (of 672 slots; declared ~432)
  own_ellevio_discounted_mar   = 0
  own_ellevio_sample_saturday  = 1.0   (a declared off-peak slot, factor 1.0)
  own_ellevio_sample_weeknight = 1.0   (03:00 Wednesday, ditto)
  own_perturbed_discounted_nov = 432   (offpeak_factor: 0.0 added -- rises)
  own_perturbed_sample_saturday = 0.0  (falls)

INSTRUMENTED SYMBOLS: grid_fee.py:apply_catalog,
coordinator.py:HeatPumpOptimizerCoordinator._capacity_tariff,
tariff.py:CapacityTariff.sample_factor, tariff.py:mask_active,
optimizer.py:_GridTerms/_peak_window_factors path via OptimizerConfig.
PERTURBATION (executed in-section 4): add CONF_PEAK_TARIFF_OFFPEAK_FACTOR 0.0
to the apply_catalog dict; discounted count must rise 0 -> 432/412.
NULL CONTROL: the month mask written by the same call must move the factor
(a July slot under the Nov-Mar rows must already return 0.0).

ROOT RULE: os.getcwd(). BASELINE SHA: 7dd68dd; measured on branch head
0855277 (custom_components/ diff vs baseline: version strings only).
MACHINE: 8-core Apple M1, macOS 25.6.0, python 3.11.5.
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

from _d2common import Cpu, footer, result  # noqa: E402
import harness  # noqa: E402,F401
from harness import FakeEntry, FakeHass  # noqa: E402
from heatpump_optimizer import const, grid_fee, tariff  # noqa: E402
from heatpump_optimizer.coordinator import (  # noqa: E402
    HeatPumpOptimizerCoordinator,
)

CPU = Cpu()
NOV = datetime(2026, 11, 2, 0, 0, tzinfo=timezone.utc)   # a Monday
MAR = datetime(2026, 3, 2, 0, 0, tzinfo=timezone.utc)    # a Monday
JUL = datetime(2026, 7, 6, 0, 0, tzinfo=timezone.utc)    # a Monday
SLOTS = 7 * 24 * 4


def build_tariff(cfg):
    return HeatPumpOptimizerCoordinator(
        FakeHass({}), FakeEntry(data=cfg))._capacity_tariff()


def discounted(t, start):
    n = 0
    for i in range(SLOTS):
        when = start + timedelta(minutes=15 * i)
        if t.sample_factor(when) < 1.0:
            n += 1
    return n


rows = [r for r in grid_fee.catalog_choices() if r != grid_fee.DSO_PRODUCT_NONE]
result("own_rows", len(rows), "count")
result("own_rows_writing_offpeak",
       sum(1 for r in rows
           if const.CONF_PEAK_TARIFF_OFFPEAK_FACTOR
           in (grid_fee.apply_catalog(r) or {})), "count")

t = build_tariff(dict(grid_fee.apply_catalog("ellevio_villa_effekt_2026")))
with CPU:
    nov = discounted(t, NOV)
    mar = discounted(t, MAR)
    jul = discounted(t, JUL)
result("own_ellevio_discounted_nov", nov, "count")
result("own_ellevio_discounted_mar", mar, "count")
result("own_ellevio_discounted_jul_null", jul, "count")   # null: month mask
result("own_ellevio_mask_active", int(tariff.mask_active(t)), "bool")
result("own_ellevio_offpeak_factor", float(t.offpeak_factor), "factor")
result("own_ellevio_sample_saturday",
       t.sample_factor(NOV + timedelta(days=5, hours=20)), "factor")
result("own_ellevio_sample_weeknight",
       t.sample_factor(NOV + timedelta(days=2, hours=3)), "factor")

# --- 3. the optimizer's own mask construction (the objective's path) --------
from heatpump_optimizer.optimizer import (  # noqa: E402
    OptimizationConfig, HeatPumpOptimizer,
)

opt_cfg = OptimizationConfig(
    peak_window_minutes=int(t.window_minutes),
    peak_months=(11, 12, 1, 2, 3),
    peak_hours=t.peak_hours,
    peak_weekdays_only=True,
    peak_offpeak_factor=t.offpeak_factor,
)
opt = HeatPumpOptimizer.__new__(HeatPumpOptimizer)
opt.config = opt_cfg
with CPU:
    factors = HeatPumpOptimizer._peak_window_factors(
        opt, SLOTS, 0.25, NOV, 0)
import numpy as np  # noqa: E402  (after the pin, deliberately)

result("own_optimizer_factors_is_none", int(factors is None), "bool")
result("own_optimizer_factors_below1",
       0 if factors is None else int(np.sum(np.asarray(factors) < 1.0)),
       "count")

# --- 4. perturbation: one key added to the apply_catalog dict ---------------
cfg = dict(grid_fee.apply_catalog("ellevio_villa_effekt_2026"))
cfg[const.CONF_PEAK_TARIFF_OFFPEAK_FACTOR] = 0.0
tp = build_tariff(cfg)
with CPU:
    nov_p = discounted(tp, NOV)
    sat_p = tp.sample_factor(NOV + timedelta(days=5, hours=20))
result("own_perturbed_discounted_nov", nov_p, "count")
result("own_perturbed_sample_saturday", sat_p, "factor")

footer(CPU, "[d]2_own_D2-02")
