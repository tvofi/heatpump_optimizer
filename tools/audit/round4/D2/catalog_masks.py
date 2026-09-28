"""D2 round 4, finding D2-02: every shipped DSO catalog row writes a
peak-hours window and a weekdays-only flag that provably change no number,
because `apply_catalog` never writes the third field the other two are gated
on (`peak_tariff_offpeak_factor`, whose default is 1.0).

METRIC (one line): `discounted_windows` = how many of the 672 fifteen-minute
metering windows of one tariff-month week `tariff.window_factors` returns a
factor below 1.0 for, under the config `grid_fee.apply_catalog(row)` writes;
`declared_offpeak_windows` = how many of those same 672 the row's own
`peak_tariff_hours` + `peak_tariff_weekdays_only` declare off-peak. The
contract is that they are equal; measured, `discounted_windows` is 0.

WHY (re-derivable, not the evidence): `CapacityTariff.sample_factor` returns
`offpeak_factor` for an off-peak window, and `tariff.mask_active` states the
gate in one line -- an hours/weekday mask "can change what a window counts
at" only when `offpeak_factor < 1.0`. `apply_catalog` writes
CONF_PEAK_TARIFF_HOURS and CONF_PEAK_TARIFF_WEEKDAYS_ONLY and does not write
CONF_PEAK_TARIFF_OFFPEAK_FACTOR, so the coordinator's `_capacity_tariff`
picks up DEFAULT_PEAK_TARIFF_OFFPEAK_FACTOR = 1.0 and both masks are inert.
The month mask is not: it maps to factor 0.0 and does bite, which is what
makes this a gap in two of three masks rather than a dead feature.

EXACT COMMAND (from the export root):
    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D2/catalog_masks.py

EXPECTED (baseline 7dd68dd): exact counts, tolerance 0.
    catalog_rows                       = 4
    rows_writing_hours_mask            = 4
    rows_writing_offpeak_factor        = 0
    <row>.discounted_windows           = 0     for all 4 rows
    <row>.declared_offpeak_windows     = 432   (Ellevio/Vattenfall/Goteborg,
                                                07:00-19:00 Mon-Fri)
                                       = 408   (E.ON, 07:00-20:00 Mon-Fri)
    <row>.july_factor_unique           = [0.]  for the Nov-Mar rows (the
                                                month mask DOES bite -- the
                                                null control for this metric)
    ellevio.phantom_peak_sek           = 406.25 +- 1e-6 SEK   (a 5 kW
        Saturday-night excess over the whole week, charged at factor 1.0,
        which under the row's own declared mask should be charged at the
        off-peak factor; at the intended 0.0 it would be 0.00)
    perturbed.ellevio.discounted_windows = 432 (see PERTURBATION)

INSTRUMENTED SYMBOLS: grid_fee.py:apply_catalog (the config under test),
coordinator.py:HeatPumpOptimizerCoordinator._capacity_tariff (the real
builder that turns that config into a CapacityTariff),
tariff.py:window_factors and tariff.py:CapacityTariff.sample_factor (the
numbers), tariff.py:mask_active (the gate the finding rests on),
tariff.py:peak_cost (the money).

PERTURBATION (the judge runs it): add
    CONF_PEAK_TARIFF_OFFPEAK_FACTOR: 0.0
to the dict `grid_fee.apply_catalog` returns (one line). Under it
`discounted_windows` must RISE from 0 to `declared_offpeak_windows` for
every row and `ellevio.phantom_peak_sek` must FALL to 0.0. Section 3
executes exactly that perturbation in-process and prints the perturbed
numbers, so the direction is measured.

NULL CONTROL: `july_factor_unique` for the three Nov-Mar rows is [0.] and
for the Jan-Dec row is [1.] -- the month mask, written by the same call,
does move the factor. A harness that could not tell an inert mask from a
live one would report the same thing for both.

ROOT RULE: os.getcwd(); resolves nothing from __file__.
BASELINE SHA: 7dd68dd327fe3dbfb09f3bd0fe38910c58877697 (export, no .git).
MACHINE: 8-core Apple M1, 8 GB, macOS 25.6.0, python 3.11.5, numpy 2.4.6.
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

import numpy as np  # noqa: E402  (after the pin, deliberately)

from _d2common import Cpu, footer, result  # noqa: E402
import harness  # noqa: E402,F401  (inserts tests/ and custom_components/)
from harness import FakeEntry, FakeHass  # noqa: E402
from heatpump_optimizer import const, grid_fee, tariff  # noqa: E402
from heatpump_optimizer.coordinator import (  # noqa: E402
    HeatPumpOptimizerCoordinator,
)

CPU = Cpu()

# A Monday in a month every Nov-Mar row bills, and a Monday in July.
JAN = datetime(2026, 1, 5, 0, 0, tzinfo=timezone.utc)
JUL = datetime(2026, 7, 6, 0, 0, tzinfo=timezone.utc)
WEEK_WINDOWS = 7 * 24 * 4          # 672 fifteen-minute windows
DT = 0.25


def build(cfg):
    return HeatPumpOptimizerCoordinator(FakeHass({}), FakeEntry(data=cfg))


def declared_offpeak(row) -> int:
    """Windows the row's own hours/weekday mask calls off-peak."""
    hours = row["peak_tariff_hours"]
    lo, hi = (float(x.split(":")[0]) + float(x.split(":")[1]) / 60.0
              for x in hours.split("-"))
    n = 0
    for i in range(WEEK_WINDOWS):
        when = JAN + timedelta(minutes=15 * i)
        weekend = row["peak_tariff_weekdays_only"] and when.weekday() >= 5
        h = when.hour + when.minute / 60.0
        if weekend or not (lo <= h < hi):
            n += 1
    return n


rows = [r for r in grid_fee.catalog_choices() if r != grid_fee.DSO_PRODUCT_NONE]
result("catalog_rows", len(rows), "count")
result(
    "rows_writing_hours_mask",
    sum(1 for r in rows
        if const.CONF_PEAK_TARIFF_HOURS in (grid_fee.apply_catalog(r) or {})),
    "count",
)
result(
    "rows_writing_offpeak_factor",
    sum(1 for r in rows
        if const.CONF_PEAK_TARIFF_OFFPEAK_FACTOR
        in (grid_fee.apply_catalog(r) or {})),
    "count",
)


def measure(tag, cfg, row):
    co = build(cfg)
    with CPU:
        t = co._capacity_tariff()
        wf = tariff.window_factors(t, JAN, WEEK_WINDOWS, DT)
        wf_jul = tariff.window_factors(t, JUL, 24 * 4, DT)
    short = tag.split("_")[0]
    result(f"{short}.mask_active", int(tariff.mask_active(t)), "bool")
    result(f"{short}.offpeak_factor", float(t.offpeak_factor), "factor")
    disc = 0 if wf is None else int(np.sum(wf < 1.0))
    result(f"{short}.windows", WEEK_WINDOWS, "count")
    result(f"{short}.discounted_windows", disc, "count")
    result(f"{short}.declared_offpeak_windows", declared_offpeak(row), "count")
    result(f"{short}.july_factor_unique",
           "[]" if wf_jul is None else str(np.unique(wf_jul)))
    return t, wf


for rid in rows:
    row = grid_fee.SWEDEN_CATALOG[rid]
    measure(rid, dict(grid_fee.apply_catalog(rid)), row)

# --- the money: a weekend-night burst the row says it does not bill --------
ELL = "ellevio_villa_effekt_2026"
t_ell, _ = measure(ELL + "_money", dict(grid_fee.apply_catalog(ELL)),
                   grid_fee.SWEDEN_CATALOG[ELL])
# Saturday 00:00 of that January week, 4 hours of 5 kW excess above a
# threshold of 0 -- squarely inside the hours and the weekend the row
# declares off-peak.
SAT = JAN + timedelta(days=5)
n_steps = 4 * 4
house = np.full(n_steps, 5.0)
wf_sat = tariff.window_factors(t_ell, SAT, n_steps, DT)
with CPU:
    charged = tariff.peak_cost(
        house, np.zeros(n_steps), 0.0, t_ell.marginal_price_per_kw,
        t_ell.window_minutes, DT, peaks_averaged=t_ell.peaks_averaged,
        window_factors=wf_sat,
    )
result("ellevio.phantom_peak_sek", charged, "SEK")

# --- the perturbation, executed -------------------------------------------
_orig = grid_fee.apply_catalog


def apply_catalog_with_offpeak(product_id):
    out = _orig(product_id)
    if out is None:
        return None
    out = dict(out)
    out[const.CONF_PEAK_TARIFF_OFFPEAK_FACTOR] = 0.0
    return out


grid_fee.apply_catalog = apply_catalog_with_offpeak
try:
    for rid in rows:
        cfg = dict(grid_fee.apply_catalog(rid))
        co = build(cfg)
        t = co._capacity_tariff()
        wf = tariff.window_factors(t, JAN, WEEK_WINDOWS, DT)
        result(f"perturbed.{rid.split('_')[0]}.discounted_windows",
               0 if wf is None else int(np.sum(wf < 1.0)), "count")
    cfg = dict(grid_fee.apply_catalog(ELL))
    t = build(cfg)._capacity_tariff()
    wf_sat = tariff.window_factors(t, SAT, n_steps, DT)
    result("perturbed.ellevio.phantom_peak_sek",
           tariff.peak_cost(
               house, np.zeros(n_steps), 0.0, t.marginal_price_per_kw,
               t.window_minutes, DT, peaks_averaged=t.peaks_averaged,
               window_factors=wf_sat), "SEK")
finally:
    grid_fee.apply_catalog = _orig

footer(CPU, "[c]atalog_masks")
