"""D2 round-5 harness 5: the capacity term's soft top-k under-charges peaks.

METRIC DEFINITION (one line)
----------------------------
``rel_err`` = (``tariff.peak_cost(total, baseline, thr, 1/k, 60, 0.25, k)`` - the
exact ``full/k * sum(top-k excess)`` with ``full = 1``) / exact, dimensionless:
the signed relative error of the capacity term the optimizer is handed against
the arithmetic its own docstring states (``full x mean(top-k)``).  Negative =
the term under-charges the plan's peak.

THE SEAM THE NUMBER IS KEYED ON
-------------------------------
Counted on ``tariff.peak_cost``'s own return value -- the value production
delivers to the objective and publishes as ``projected_peak_cost`` -- not on
an input attribute and not on the private helper.  ``peak_cost`` uses
``tariff._smooth_topk_sum`` only when the hard top-k would be gradient-blind
(``n_at_peak = #{excess >= peak - _PEAK_TIE_BAND}`` exceeds ``k``); every
other input takes the exact hard sum.  That gate IS the null control: the
same measurement on non-plateau inputs must be identically 0.

ARMS
----
* ``plateau``    — inputs satisfying the invocation condition, k in 1..3.
* ``null``       — inputs failing it (separated peaks): ``peak_cost`` takes
  the exact hard branch, so ``plateau_null_rel_max`` must be 0.0.
* ``perturbed_up``   — ``tariff._PEAK_SMOOTH_TAU`` 0.05 -> 0.5 (the one-line
  production edit).  The under-charge must GROW.
* ``perturbed_zero`` — ``tariff._PEAK_SMOOTH_TAU`` 0.05 -> 1e-9, which
  collapses the logistic to a hard step.  The under-charge must go TO ZERO.
* ``realised``   — the same wrapper around ``peak_cost`` during real
  ``HeatPumpOptimizer.optimize`` solves on golden scenarios with a capacity
  tariff switched on: how often the soft branch is taken, and the worst
  relative error on the plans the solver actually prices.

COMMAND
-------
    PYTHONPATH=tests/hastub python3 tools/audit/round5/D2/smooth_topk.py

Expected (baseline eaa2a06af16a1b5b006f58a0f36cc92131f80225):
``plateau_rel_min`` about -0.040, ``plateau_frac_gt_1pct`` about 10 %,
``plateau_null_rel_max`` exactly 0.0, ``perturbed_up_rel_min`` about -0.44,
``perturbed_zero_rel_min`` about 0.0, and ``realised_calls`` in the
thousands with ``realised_rel_min`` about -0.012.  Machine: darwin arm64,
8-core M1, 8 GB.  ROOT RULE: root from ``__file__`` (four parents up).  No
Node harness runs, so HPO_PLANDATA is untouched.
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
from heatpump_optimizer import tariff as T  # noqa: E402

WINDOW = 60
DT = 0.25


def emit(name, value, unit):
    text = f"{value:.6g}" if isinstance(value, float) else str(value)
    print(f"RESULT {name}={text} {unit}", flush=True)


def excess_of(house, baseline, thr):
    return np.maximum(
        0.0, T.metering_windows(house + baseline, WINDOW, DT, 0) - thr
    )


def measure(house, baseline, thr, k):
    """(exact top-k excess sum, peak_cost*the bill) for one cell."""
    excess = excess_of(house, baseline, thr)
    if not np.any(excess > 0):
        return None
    kk = max(1, min(k, excess.size))
    exact = float(np.sum(np.sort(excess)[-kk:]))
    if exact <= 1e-12:
        return None
    # full price 1.0, so peak_price_per_kw is the marginal 1/k
    got = float(T.peak_cost(house, baseline, thr, 1.0 / kk, WINDOW, DT,
                            peaks_averaged=kk, offset_steps=0))
    return exact, got * kk


def cells(seed, trials, want_plateau):
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(trials):
        n = 96
        k = int(rng.integers(1, 4))
        house = rng.uniform(0.0, 6.0, n)
        baseline = rng.uniform(0.0, 2.0, n)
        thr = float(rng.uniform(0.0, 4.0))
        # force a plateau: a contiguous run of steps at the same power, so
        # several metering windows tie at the same mean (what a bang-bang
        # plan does), or leave the series random for the null arm.
        if want_plateau:
            level = float(rng.uniform(3.0, 8.0))
            start = int(rng.integers(0, n - 8))
            length = int(rng.integers(4, 9))
            house[start:start + length] = level
            baseline[start:start + length] = 0.0
        excess = excess_of(house, baseline, thr)
        if not np.any(excess > 0):
            continue
        peak = float(np.max(excess))
        n_at = int(np.sum(excess >= peak - T._PEAK_TIE_BAND))
        if (n_at > max(1, min(k, excess.size))) != want_plateau:
            continue
        out.append((house, baseline, thr, k))
    return out


def arm(cells_):
    rel = []
    for house, baseline, thr, k in cells_:
        got = measure(house, baseline, thr, k)
        if got is None:
            continue
        exact, soft = got
        rel.append((soft - exact) / exact)
    a = np.asarray(rel) if rel else np.zeros(1)
    return (float(a.min()), float(a.mean()),
            100.0 * float(np.mean(np.abs(a) > 0.01)), int(a.size))


def synthetic():
    for label, want in (("plateau", True), ("null", False)):
        cs = cells(31 + (0 if want else 1), 30000, want)
        lo, mean, frac, n = arm(cs)
        emit(f"{label}_cells", n, "count")
        emit(f"{label}_rel_min", lo, "ratio")
        emit(f"{label}_rel_mean", mean, "ratio")
        emit(f"{label}_frac_gt_1pct", frac, "percent")
    cs = cells(31, 30000, True)
    saved = T._PEAK_SMOOTH_TAU
    try:
        T._PEAK_SMOOTH_TAU = 0.5
        lo, mean, frac, n = arm(cs)
        emit("perturbed_up_rel_min", lo, "ratio")
        emit("perturbed_up_rel_mean", mean, "ratio")
        emit("perturbed_up_frac_gt_1pct", frac, "percent")
        T._PEAK_SMOOTH_TAU = 1e-9
        lo, mean, frac, n = arm(cs)
        emit("perturbed_zero_rel_min", lo, "ratio")
        emit("perturbed_zero_rel_mean", mean, "ratio")
        emit("perturbed_zero_frac_gt_1pct", frac, "percent")
    finally:
        T._PEAK_SMOOTH_TAU = saved
    emit("perturbation_cells", len(cs), "count")


def realised():
    """The same error on the plans a real solve actually prices.

    ``optimizer`` binds ``peak_cost``/``peak_cost_batch`` into its own module
    namespace at import, so the wrapper goes on ``optimizer``, not on
    ``tariff``.  ``peak_price_per_kw`` is set to the MARGINAL price the
    production coordinator assigns it (``tariff.marginal_price_per_kw``,
    20/3), which is the only convention under which the published figure is
    the bill.
    """
    from heatpump_optimizer import optimizer as OPT

    calls = [0]
    inner = OPT.peak_cost

    def spy(total, baseline, thr, price, window, dt, *a, **kw):
        calls[0] += 1
        return inner(total, baseline, thr, price, window, dt, *a, **kw)

    OPT.peak_cost = spy
    rel = []
    try:
        for name in ("winter_two_zone_dhw", "winter_single_dhw", "flat_prices",
                     "shoulder"):
            b = golden.make(**dict(golden.SCENARIOS[name]))
            opt = b["optimizer"]
            cfg = opt.config
            cfg.peak_price_per_kw = 20.0 / 3.0
            cfg.peak_threshold_kw = 2.0
            cfg.peak_window_minutes = WINDOW
            cfg.peak_count = 3
            cfg.peak_months = ()
            cfg.peak_hours = ()
            cfg.peak_weekdays_only = False
            cfg.peak_offpeak_factor = 1.0
            r = opt.optimize(
                b["state"], b["prices"], b["outdoor"], b["wind"], b["rain"],
                b["solar"], golden.START,
            )
            emit(f"realised_calls_{name}", int(calls[0]), "count")
            emit(f"realised_peak_cost_{name}", float(r.peak_cost), "currency")
            emit(f"realised_peak_kw_{name}", float(r.projected_peak_kw), "kW")
            calls[0] = 0

            # the exact bill for the plan the solve settled on, on the SAME
            # baseline array the objective prices with (the whole-house
            # non-heat-pump load -- NOT result.baseline_power_schedule, which
            # is the thermostat baseline's own kW).
            base = np.asarray(
                cfg.baseline_load_array(len(r.power_schedule)), dtype=float
            )
            if base.size == len(r.power_schedule):
                excess = excess_of(
                    np.asarray(r.power_schedule, dtype=float), base,
                    cfg.peak_threshold_kw,
                )
                if np.any(excess > 0):
                    kk = max(1, min(cfg.peak_count, excess.size))
                    exact = (20.0 / 3.0) * float(np.sum(np.sort(excess)[-kk:]))
                    if exact > 1e-12:
                        rel.append((float(r.peak_cost) - exact) / exact)
    finally:
        OPT.peak_cost = inner
    if rel:
        a = np.asarray(rel)
        emit("realised_plan_cells", int(a.size), "count")
        emit("realised_plan_rel_min", float(a.min()), "ratio")
        emit("realised_plan_rel_mean", float(a.mean()), "ratio")


def main():
    t0 = time.monotonic()
    for fn in (synthetic, realised):
        try:
            fn()
        except Exception as err:
            emit(f"ERROR_{fn.__name__}", f"{type(err).__name__}:{err}", "label")
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
