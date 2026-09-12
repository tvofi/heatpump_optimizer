"""D2 -- the capacity-tariff billing mask walks the WALL clock while the plan
grid walks UTC, so on the two DST days a year every window after the transition
bills under the wrong hour.

`tariff.py:window_factors` builds its window instants as
`_window_slot(start) + timedelta(minutes=window*i)`, which is wall-clock
arithmetic on an aware datetime: it skips the repeated hour in autumn and
invents the non-existent hour in spring.  The plan's own step clock
(`optimizer.py:_utc_step_starts`, added by #243 for exactly this reason) walks
UTC and does not.  `PeakTracker.observe` keys a live window off the real
instant, so the plan's cost term and the live meter DO disagree about which
hour a window bills under -- which is the property `window_factors`'s docstring
claims can never happen.

METRIC: `mismatches` = the number of horizon windows i where
`window_factors(mask, start, n, dt)[i]` differs from
`mask.sample_factor(_utc_step_starts(start, n, dt)[i])`, i.e. the factor the
same tariff object assigns to the instant the plan's own step clock puts that
window at.  Zero is the only correct value.

COMMAND (from the repository root, < 5 s):
    PYTHONPATH=tests/hastub python3 tools/audit/round3/D2/dst_window_factors.py

EXPECTED on this tree (the walk is shipped; #777).  The 48 h header was the
    #817 defect: `OptimizationConfig.from_mapping({}).horizon_hours` is 24.0,
    and a 48 h cell inflated a year-long population from 0 to 80 solves.
    At ae36eff the unfixed 48 h run printed total_mismatched_cells=12_of_12;
    that is history, not this header.
    RESULT default_horizon_hours=24.0
    RESULT cells=12
    RESULT total_mismatched_cells=0_of_12
    RESULT mismatches_autumn_60min_peak_hours=0_of_24_windows
    RESULT null_control_non_dst_day_mismatches=0
    RESULT no_mask_returns_none=True
Tolerance: exact integers; no float comparison, no BLAS, contention-immune.

MONEY ARM: an hourly tariff, peak_hours 07:00-20:00, offpeak_factor 0.0,
threshold 0 kW, marginal price 20 currency/kW (a 60/kW tariff over 3 averaged
peaks -- the low end of a Swedish effekttariff).  A flat plan cannot show the
error: every window ties and the top-3 is the same under either mask.  So the
arm scores the plan a masked tariff actually produces -- 9 kW parked in the
first hour the mask calls free, nothing elsewhere -- under both factor vectors.
`unpriced` is what the meter bills that the objective did not charge; at
baseline it is +180 currency on both transition days and 0 on the control.

PERTURBATION (direction stated): move the horizon start off the transition --
`--date 2026-10-18` (the NULL CONTROL arm, run automatically) -> mismatches must
fall to 0 in every cell.  Second perturbation: set `offpeak_factor=1.0` and
`peak_hours=()` (no mask) -> `window_factors` returns None and the whole term is
inert; reported as `no_mask_returns_none`.

BASELINE SHA: ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1
MACHINE: 8-core Apple M1, 8 GB, numpy 2.4.6 / scipy 1.17.1 on OpenBLAS
INSTRUMENTED SYMBOLS: tariff.py:window_factors, tariff.py:_window_slot,
    tariff.py:CapacityTariff.sample_factor, tariff.py:peak_cost,
    optimizer.py:_utc_step_starts,
    optimizer.py:HeatPumpOptimizer._peak_window_factors
"""
from datetime import datetime
from zoneinfo import ZoneInfo

import d2lib  # noqa: F401  -- thread pin + sys.path, must be first
import numpy as np

from heatpump_optimizer.optimizer import (
    HeatPumpOptimizer,
    OptimizationConfig,
    _utc_step_starts,
)
from heatpump_optimizer.tariff import CapacityTariff, peak_cost, window_factors
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters

d2lib.repo_root_ok()

STHLM = ZoneInfo("Europe/Stockholm")
AUTUMN = datetime(2026, 10, 25, 0, 0, tzinfo=STHLM)   # 25-hour day
SPRING = datetime(2026, 3, 29, 0, 0, tzinfo=STHLM)    # 23-hour day
CONTROL = datetime(2026, 10, 18, 0, 0, tzinfo=STHLM)  # ordinary 24-hour Sunday

PEAK_MASK = dict(peak_hours=((7.0, 20.0),), offpeak_factor=0.0)
WEEKDAY_MASK = dict(weekdays_only=True, offpeak_factor=0.4)


def mask(window_minutes, **kw):
    return CapacityTariff(
        enabled=True, window_minutes=window_minutes, price_per_kw=60.0, **kw
    )


def compare(t: CapacityTariff, start: datetime, hours: float):
    """(mismatches, n_windows, produced, truth) for one (mask, start) cell."""
    dt = t.window_minutes / 60.0
    n = int(round(hours / dt))
    produced = window_factors(t, start, n, dt)
    if produced is None:
        return None, n, None, None
    instants = _utc_step_starts(start, n, dt)
    truth = np.array([t.sample_factor(d) for d in instants], dtype=float)
    return int(np.sum(produced != truth)), n, produced, truth


def main() -> int:
    d2lib.result(
        "default_horizon_hours",
        OptimizationConfig.from_mapping({}).horizon_hours,
    )
    cells = []
    for label, start in (("autumn", AUTUMN), ("spring", SPRING)):
        for wm in (60, 30, 15):
            for mname, kw in (("peak_hours", PEAK_MASK), ("weekdays_only", WEEKDAY_MASK)):
                cells.append((f"{label}_{wm}min_{mname}", mask(wm, **kw), start))

    bad = 0
    for name, t, start in cells:
        # 24 h: OptimizationConfig.from_mapping({}).horizon_hours. A 48 h
        # header inflated the year-long population from 0 to 80 solves.
        m, n, _, _ = compare(t, start, 24.0)
        d2lib.result(f"mismatches_{name}", f"{m}_of_{n}_windows")
        if m:
            bad += 1
    d2lib.result("cells", len(cells))
    d2lib.result("total_mismatched_cells", f"{bad}_of_{len(cells)}")

    # --- NULL CONTROL: an ordinary day, same masks ------------------------
    ctrl = 0
    for wm in (60, 30, 15):
        for mname, kw in (("peak_hours", PEAK_MASK), ("weekdays_only", WEEKDAY_MASK)):
            m, n, _, _ = compare(mask(wm, **kw), CONTROL, 24.0)
            ctrl += m
    d2lib.result("null_control_non_dst_day_mismatches", ctrl)

    # --- second control: no mask at all -> the term is inert --------------
    flat = CapacityTariff(enabled=True, window_minutes=60, price_per_kw=60.0)
    d2lib.result(
        "no_mask_returns_none", window_factors(flat, AUTUMN, 25, 1.0) is None
    )

    # --- the production path actually builds these ------------------------
    # HeatPumpOptimizer._peak_window_factors composes the same CapacityTariff
    # from OptimizationConfig, so the defect is reached from a real solve.
    cfg = OptimizationConfig(
        horizon_hours=48,
        time_step_minutes=60,
        peak_price_per_kw=20.0,
        peak_threshold_kw=0.0,
        peak_window_minutes=60,
        peak_hours=[(7.0, 20.0)],
        peak_offpeak_factor=0.0,
        peak_count=3,
    )
    opt = HeatPumpOptimizer(ThermalModel(ThermalParameters()), cfg)
    for label, start in (("autumn", AUTUMN), ("spring", SPRING), ("control", CONTROL)):
        n_h = 48
        prod = opt._peak_window_factors(n_h, 1.0, start, 0)
        instants = _utc_step_starts(start, n_h, 1.0)
        t = CapacityTariff(
            enabled=True, window_minutes=60,
            peak_hours=((7.0, 20.0),), offpeak_factor=0.0,
        )
        truth = np.array([t.sample_factor(d) for d in instants], dtype=float)
        m = int(np.sum(np.asarray(prod)[: len(truth)] != truth))
        d2lib.result(f"optimizer_peak_window_factors_{label}_mismatches", m)

        # The user-facing direction: hours the plan believes are unbilled but
        # the meter bills at full rate.
        pf = np.asarray(prod, dtype=float)[: len(truth)]
        free_but_billed = np.flatnonzero((pf == 0.0) & (truth == 1.0))
        d2lib.result(
            f"hours_plan_thinks_free_but_meter_bills_{label}",
            free_but_billed.size,
        )
        # Money arm.  A flat plan cannot show this: every window ties, so the
        # top-3 is the same under either mask.  The plan a masked tariff
        # actually produces parks its load where the mask says the kW is free,
        # so score exactly that plan -- 9 kW in the first such hour, nothing
        # elsewhere -- under both factor vectors.  `as_planned` is what the
        # objective charged it; `at_true_instants` is what the meter bills.
        base = np.zeros(n_h)
        if free_but_billed.size:
            power = np.zeros(n_h)
            power[free_but_billed[0]] = 9.0
        else:
            power = np.zeros(n_h)
            power[12] = 9.0
        wrong = peak_cost(power, base, 0.0, 20.0, 60, 1.0, 3, 0, pf)
        right = peak_cost(power, base, 0.0, 20.0, 60, 1.0, 3, 0, truth)
        d2lib.result(
            f"peak_cost_{label}",
            f"as_planned={wrong:.4f} at_true_instants={right:.4f} "
            f"unpriced={right - wrong:+.4f}",
            "currency",
        )

    d2lib.env_footer()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
