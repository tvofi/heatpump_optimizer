"""D9 round 3 / H5 -- what the four multi-start L-BFGS-B runs cost and buy.

METRICS (step-equivalents per tools/audit/briefs/D9.md, verbatim):
  step_equivalents  = scalar ThermalModel.simulate_step calls + ROWS of
                      ThermalModel.simulate_trajectory_batch, both hooked by
                      monkeypatching the production symbols, attributed to the
                      L-BFGS-B run (_scoped_minimize call) they occurred in.
  lbfgs_runs        = calls into optimizer._scoped_minimize per optimize().
  redundant_share   = step-equivalents spent inside L-BFGS-B runs whose final
                      objective did NOT improve on the best already reached by
                      an earlier run of the same _multi_start_minimize call,
                      over all step-equivalents spent inside L-BFGS-B runs.
  best_gain         = (f(first refined start) - f(best)) / |f(first)|, the
                      objective improvement the extra runs actually buy.

  All four are COUNTS or ratios of counts: contention-immune, no wall clock.

COMMAND (from the repository root; ~3 minutes):
  PYTHONPATH=tests/hastub python3 tools/audit/round3/D9/h5_multistart_grid.py

GRID: 8 price profiles from tests/profiles.py x 2 topologies (single-zone DHW,
two-zone DHW) = 16 cells, so the aggregate carries a range and a
leave-one-out, per COMMON.md item 6.  ``flat`` is the null-control profile.

EXPECTED (baseline ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1, Apple M1,
python 3.11.5 / numpy 2.4.6 / scipy 1.17.1):
  grid.cells                        = 16     +-0
  grid.redundant_share_mean         = 0.66   +-0.10
  grid.redundant_share_min/max      report the range across cells
  grid.best_gain_mean               < 0.005            (half a percent)
  grid.cells_with_zero_gain         >= 8 of 16
  flat_vs_priced.step_equiv_ratio   > 1.5   (the null-control profile is the
                                             DEAREST to solve, not the cheapest)

PERTURBATION: HPO_D9_STARTS=<n> rewrites optimizer._MULTI_START_SOLVES.  At
n=1 step_equivalents must FALL by about redundant_share and best_gain must go
to 0 by construction; at n=4 (the shipped value) it must return to baseline.
The judge should run both.

INSTRUMENTED SYMBOLS: optimizer._scoped_minimize, optimizer.
_multi_start_minimize, optimizer._MULTI_START_SOLVES,
thermal_model.ThermalModel.simulate_step,
thermal_model.ThermalModel.simulate_trajectory_batch.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round3", "D9"))
import d9lib  # noqa: E402
from d9lib import START, result, telemetry  # noqa: E402

import numpy as np  # noqa: E402

from profiles import DT, house, prices, weather  # noqa: E402
from heatpump_optimizer import optimizer as OPT  # noqa: E402
from heatpump_optimizer.optimizer import (  # noqa: E402
    HeatPumpOptimizer,
    OptimizationConfig,
)
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel,
    ThermalParameters,
    ThermalState,
)

STARTS = os.environ.get("HPO_D9_STARTS")
PRICE_PROFILES = (
    "winter_typical", "winter_extreme", "summer_typical", "summer_negative",
    "shoulder", "winter_narrow", "winter_moderate", "flat",
)
WEATHER_FOR = {
    "winter_typical": "winter_cold", "winter_extreme": "winter_cold",
    "summer_typical": "summer_warm", "summer_negative": "summer_warm",
    "shoulder": "shoulder", "winter_narrow": "winter_cold",
    "winter_moderate": "winter_mild", "flat": "winter_cold",
}

STATE = dict(steps=0, rows=0)
RUNS: list[dict] = []      # one per _scoped_minimize call
GROUPS: list[list[int]] = []  # indices of RUNS, grouped by _multi_start call


def install():
    o_step = ThermalModel.simulate_step
    o_batch = ThermalModel.simulate_trajectory_batch
    o_sm = OPT._scoped_minimize
    o_ms = OPT._multi_start_minimize

    def step(self, *a, **k):
        STATE["steps"] += 1
        return o_step(self, *a, **k)

    def batch(self, initial_state, power_matrix, *a, **k):
        STATE["rows"] += int(len(power_matrix))
        return o_batch(self, initial_state, power_matrix, *a, **k)

    def scoped(*a, **k):
        before = STATE["steps"] + STATE["rows"]
        res = o_sm(*a, **k)
        RUNS.append({
            "equiv": STATE["steps"] + STATE["rows"] - before,
            "fun": float(res.fun),
            "nit": int(getattr(res, "nit", -1)),
            "nfev": int(getattr(res, "nfev", -1)),
        })
        if GROUPS:
            GROUPS[-1].append(len(RUNS) - 1)
        return res

    def multi(*a, **k):
        GROUPS.append([])
        return o_ms(*a, **k)

    ThermalModel.simulate_step = step
    ThermalModel.simulate_trajectory_batch = batch
    OPT._scoped_minimize = scoped
    OPT._multi_start_minimize = multi

    def restore():
        ThermalModel.simulate_step = o_step
        ThermalModel.simulate_trajectory_batch = o_batch
        OPT._scoped_minimize = o_sm
        OPT._multi_start_minimize = o_ms

    return restore


def build_solve(price_profile: str, two_zone: bool):
    cfg = house(two_zone=two_zone, dhw=True)
    params = ThermalParameters.from_config(cfg)
    params.dhw_enabled = True
    opt_cfg = OptimizationConfig(
        horizon_hours=24, time_step_minutes=15,
        target_temp=cfg["target_temperature"],
        min_temp=cfg["min_temperature"], max_temp=cfg["max_temperature"],
    )
    n = int(24 / DT)

    def fit(arr):
        arr = np.asarray(arr, dtype=float)
        return arr[:n] if len(arr) >= n else np.tile(
            arr, int(np.ceil(n / len(arr)))
        )[:n]

    price_series = fit(prices(price_profile, START))
    outdoor, wind, rain, solar = (
        fit(a) for a in weather(WEATHER_FOR[price_profile], START)
    )
    initial = ThermalState(
        room_temperature=21.0, slab_temperature=22.0,
        outdoor_temperature=float(outdoor[0]),
        upper_floor_temperature=21.0, lower_floor_temperature=21.0,
        dhw_temperature=50.0, dhw_hours_since_legionella=20.0,
        buffer_tank_temperature=40.0,
    )
    optimizer = HeatPumpOptimizer(ThermalModel(params), opt_cfg)
    return optimizer, initial, price_series, outdoor, wind, rain, solar


def cell(price_profile: str, two_zone: bool) -> dict:
    STATE["steps"] = STATE["rows"] = 0
    RUNS.clear()
    GROUPS.clear()
    optimizer, state, p, outdoor, wind, rain, solar = build_solve(
        price_profile, two_zone
    )
    optimizer.optimize(state, p, outdoor, wind, rain, solar, START)

    in_runs = sum(r["equiv"] for r in RUNS)
    redundant = 0
    gains = []
    for grp in GROUPS:
        best = None
        for k, idx in enumerate(grp):
            f = RUNS[idx]["fun"]
            if best is None or f < best - 1e-12:
                if best is not None:
                    pass
                best = f
            else:
                # this run did not improve on what an earlier run already had
                redundant += RUNS[idx]["equiv"]
        if grp:
            first = RUNS[grp[0]]["fun"]
            bestf = min(RUNS[i]["fun"] for i in grp)
            gains.append(
                (first - bestf) / abs(first) if first not in (0.0,) else 0.0
            )
    return {
        "equiv": STATE["steps"] + STATE["rows"],
        "in_runs": in_runs,
        "lbfgs_runs": len(RUNS),
        "multi_start_calls": len(GROUPS),
        "redundant": redundant,
        "redundant_share": (redundant / in_runs) if in_runs else 0.0,
        "best_gain": max(gains) if gains else 0.0,
    }


def main() -> None:
    result("baseline_sha", "ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1", "sha")
    if STARTS:
        OPT._MULTI_START_SOLVES = int(STARTS)
    result("multi_start_solves", OPT._MULTI_START_SOLVES, "count")

    restore = install()
    cells = {}
    try:
        for two_zone in (False, True):
            for prof in PRICE_PROFILES:
                name = f"{'2z' if two_zone else '1z'}/{prof}"
                c = cell(prof, two_zone)
                cells[name] = c
                result(f"cell[{name}].step_equivalents", c["equiv"], "count")
                result(f"cell[{name}].lbfgs_runs", c["lbfgs_runs"], "count")
                result(
                    f"cell[{name}].redundant_share", c["redundant_share"], "1"
                )
                result(f"cell[{name}].best_gain", c["best_gain"], "1")
    finally:
        restore()

    shares = [c["redundant_share"] for c in cells.values()]
    gains = [c["best_gain"] for c in cells.values()]
    equivs = {k: c["equiv"] for k, c in cells.items()}
    result("grid.cells", len(cells), "count")
    result("grid.redundant_share_mean", sum(shares) / len(shares), "1")
    result("grid.redundant_share_min", min(shares), "1")
    result("grid.redundant_share_max", max(shares), "1")
    # leave-one-out: drop the single most favourable cell (the largest share)
    lo = sorted(shares)[:-1]
    result("grid.redundant_share_mean_drop_best", sum(lo) / len(lo), "1")
    result("grid.best_gain_mean", sum(gains) / len(gains), "1")
    result("grid.best_gain_max", max(gains), "1")
    result(
        "grid.cells_with_zero_gain", sum(1 for g in gains if g <= 0.0), "count"
    )
    result(
        "grid.total_step_equivalents", sum(c["equiv"] for c in cells.values()),
        "count",
    )
    result(
        "grid.total_redundant",
        sum(c["redundant"] for c in cells.values()), "count",
    )

    # the null-control profile against the priced ones, per topology
    for tag in ("1z", "2z"):
        flat = equivs[f"{tag}/flat"]
        priced = [v for k, v in equivs.items()
                  if k.startswith(tag) and not k.endswith("flat")]
        result(
            f"flat_vs_priced.{tag}.step_equiv_ratio",
            flat / (sum(priced) / len(priced)),
            "1",
        )
        result(f"flat_vs_priced.{tag}.flat_equiv", flat, "count")
        result(
            f"flat_vs_priced.{tag}.priced_mean_equiv",
            sum(priced) / len(priced), "count",
        )
        result(
            f"flat_vs_priced.{tag}.priced_max_equiv", max(priced), "count"
        )
    telemetry()


if __name__ == "__main__":
    main()
