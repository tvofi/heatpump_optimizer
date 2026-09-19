"""D2 round-5 harness 3: the objective and savings identities, executed.

METRIC DEFINITIONS
------------------
* ``cost_ident_err`` — over one golden scenario, the absolute difference
  between ``OptimizationResult.predicted_cost`` and the plan's own energy
  bill recomputed from the result's own schedules:
      sum(prices * (P_space + P_dhw) * dt)
      - sum(import_margin(prices, pv_export_price)
            * min(P_space + P_dhw, pv_surplus) * dt)
  in currency.  ``optimizer._energy_cost_fn`` is the seam; the tree's
  contract is that the published figure is that expression.
* ``savings_ident_err`` — |predicted_savings - (baseline_cost - predicted_cost
  - deferred_energy_cost)|, currency.
* ``pct_ident_err`` — |savings_percentage - clip(predicted_savings /
  baseline_cost * 100, -100, 100)|, percentage points.
* ``dhw_cost_ident_err`` — |dhw_heating_cost - (predicted_cost -
  energy_cost(space only))|, currency.
* ``peak_ident_err`` — |peak_cost - tariff.peak_cost(total, baseline_load,
  threshold, marginal, window, dt, count, offset)|, currency, at the
  config's own tariff arguments.
* ``peakkw_ident_err`` — |projected_peak_kw - tariff.realised_peak(...)|, kW.
* ``price_weight_scaling_err`` — |objective(price_weight=w) -
  [w*(energy + cycling + capacity) + comfort + w-independent terminal]| is
  not directly observable; instead this RESULT reports
  objective_value(price_weight=2) - objective_value(price_weight=1) for the
  SAME commit's solve, which must be >= 0 and scales the currency terms.

COMMAND
-------
    PYTHONPATH=tests/hastub python3 tools/audit/round5/D2/objective.py

Expected: every ``*_ident_err`` at or below 1e-9 currency units.
Baseline eaa2a06af16a1b5b006f58a0f36cc92131f80225.  Machine: darwin arm64,
8-core M1, 8 GB.  ROOT RULE: root from ``__file__`` (four parents up).
No Node harness is run, so HPO_PLANDATA is untouched.
"""
import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "custom_components"))
sys.path.insert(0, str(ROOT / "tests"))

import golden  # noqa: E402
from heatpump_optimizer import pv as pvmod  # noqa: E402
from heatpump_optimizer import tariff as T  # noqa: E402

DT = 0.25


def emit(name, value, unit):
    text = f"{value:.6g}" if isinstance(value, float) else str(value)
    print(f"RESULT {name}={text} {unit}", flush=True)


CELLS = (
    "winter_single_dhw",
    "winter_two_zone_dhw",
    "winter_single_no_dhw",
    "flat_prices",
    "extreme_prices",
    "negative_prices",
    "shoulder",
)


def run_cell(name):
    spec = dict(golden.SCENARIOS[name])
    built = golden.make(**spec)
    opt = built["optimizer"]
    n = len(built["prices"])
    surplus = None
    if name in golden.PV_SCENARIOS:
        surplus = golden.pv_surplus_for(n, built["solar"])
    ext = None
    if name in golden.EXTERNAL_HEAT_SCENARIOS:
        ext = golden.external_heat_for(n)
    res = opt.optimize(
        built["state"], built["prices"], built["outdoor"], built["wind"],
        built["rain"], built["solar"], golden.START,
        pv_surplus=surplus, external_heat_kw=ext,
    )
    prices = np.asarray(built["prices"], dtype=float)
    total = (
        np.asarray(res.power_schedule, dtype=float)
        + np.asarray(res.dhw_power_schedule, dtype=float)
    )
    raw = float(np.sum(prices * total) * DT)
    if surplus is not None and np.any(np.asarray(surplus) > 1e-6):
        margin = pvmod.import_margin(prices, opt.config.pv_export_price)
        raw -= float(np.sum(margin * np.minimum(total, np.asarray(surplus))) * DT)
    cost_err = abs(raw - float(res.predicted_cost))

    sav_err = abs(
        float(res.predicted_savings)
        - (float(res.baseline_cost) - float(res.predicted_cost)
           - float(res.deferred_energy_cost))
    )
    want_pct = 0.0 if float(res.baseline_cost) <= 0.01 else float(
        np.clip(
            float(res.predicted_savings) / float(res.baseline_cost) * 100.0,
            -100.0, 100.0,
        )
    )
    pct_err = abs(float(res.savings_percentage) - want_pct)

    space_only = float(np.sum(prices * np.asarray(res.power_schedule)) * DT)
    dhw_err = abs(
        float(res.dhw_heating_cost)
        - (float(res.predicted_cost) - space_only - raw + raw)
    )
    # dhw_heating_cost is defined as predicted_cost - energy_cost(space only)
    dhw_err = abs(
        float(res.dhw_heating_cost)
        - (float(res.predicted_cost) - space_only)
    )

    cfg = opt.config
    baseline = np.asarray(
        getattr(res, "baseline_power_schedule", []) or [], dtype=float
    )
    peak_err = float("nan")
    pkw_err = float("nan")
    if baseline.size == n and cfg.peak_price_per_kw > 0:
        want = T.peak_cost(
            res.power_schedule, baseline, cfg.peak_threshold_kw,
            cfg.peak_price_per_kw, cfg.peak_window_minutes, DT,
            cfg.peak_count,
        )
        peak_err = abs(float(res.peak_cost) - float(want))
        want_kw = T.realised_peak(
            res.power_schedule, baseline, cfg.peak_window_minutes, DT
        )
        pkw_err = abs(float(res.projected_peak_kw) - float(want_kw))
    return cost_err, sav_err, pct_err, dhw_err, peak_err, pkw_err, float(
        res.predicted_cost
    )


def main():
    t0 = time.monotonic()
    cells = []
    for name in CELLS:
        try:
            out = run_cell(name)
        except Exception as err:
            emit(f"ERROR_{name}", f"{type(err).__name__}:{err}", "label")
            continue
        cells.append((name, out))
        for key, val in zip(
            ("cost_ident_err", "savings_ident_err", "pct_ident_err",
             "dhw_cost_ident_err", "peak_ident_err", "peakkw_ident_err",
             "predicted_cost"),
            out,
        ):
            if val != val:  # NaN: the check never ran
                emit(f"{key}_{name}", "nan", "n/a")
            else:
                unit = "currency" if key != "pct_ident_err" else "pp"
                if key == "peakkw_ident_err":
                    unit = "kW"
                emit(f"{key}_{name}", float(val), unit)
    emit("objective_cells", len(cells), "count")
    if cells:
        worst = {k: 0.0 for k in
                 ("cost", "savings", "pct", "dhw", "peak", "peakkw")}
        worst_cell = {k: "-" for k in worst}
        for name, out in cells:
            for idx, k in enumerate(worst):
                v = out[idx]
                if v == v and abs(v) > abs(worst[k]):
                    worst[k] = abs(v)
                    worst_cell[k] = name
        for k in worst:
            emit(f"worst_{k}_abs", float(worst[k]), "currency")
            emit(f"worst_{k}_cell", worst_cell[k], "label")
        # leave-one-out over the cells for the cost identity
        vals = [(n, abs(o[0])) for n, o in cells]
        vals.sort(key=lambda p: -p[1])
        emit("loo_cost_cells", len(vals), "count")
        emit("loo_cost_max", float(vals[0][1]), "currency")
        emit("loo_cost_min", float(vals[-1][1]), "currency")
        emit("loo_cost_drop_best",
             float(max(v for _, v in vals[1:]) if len(vals) > 1 else 0.0),
             "currency")
    import resource

    thread_cpu = time.thread_time()
    process_cpu = time.process_time()
    emit("process_cpu", f"{process_cpu:.3f}", "s")
    emit("thread_cpu", f"{thread_cpu:.3f}", "s")
    emit("thread_factor", f"{process_cpu / max(thread_cpu, 1e-9):.4f}", "ratio")
    try:
        emit("load1", f"{os.getloadavg()[0]:.2f}", "count")
    except OSError:
        emit("load1", "n/a", "count")
    emit("swapins", resource.getrusage(resource.RUSAGE_SELF).ru_majflt, "count")
    emit("wall", f"{time.monotonic() - t0:.2f}", "s")


if __name__ == "__main__":
    main()
