"""Stress the optimizer across realistic combinations, and check the economics.

    PYTHONPATH=tests/hastub python tests/stress.py

The other suites each answer a narrow question. `validate.py` checks a fixed
list of scenarios, `golden.py` checks that behaviour has not *changed*, and
`features.py` checks each module in isolation. None of them asks the question
that actually matters:

    across the whole space of houses, seasons, tariffs and feature
    combinations a real user might have, does this thing behave sensibly?

So this sweeps a combinatorial matrix and asserts the invariants that must hold
everywhere. Failures here are the interesting ones: they are conditions nobody
thought to write a scenario for.

Three families of check:

* **Physical.** Power within bounds, temperatures finite, tank never boiled,
  energy conserved between the schedule and the slot summaries. A violation is
  unambiguously a bug.
* **Economic.** Cheaper than a thermostat when there is price spread to exploit;
  never worse than one; costs reconcile with the schedule. These are the claims
  the integration makes, checked rather than assumed.
* **Comfort.** The floor is respected to within the tolerance the soft penalty
  allows, and hot water is available when it was promised. A cheaper plan that
  is colder is not a better plan.
"""
from __future__ import annotations

import itertools
import json
import os
import resource
import sys
import time
import tracemalloc
from datetime import datetime, timedelta

from harness import Results

# Pinned BEFORE numpy is imported, because OpenBLAS reads these once when
# the library loads and ignores them afterwards. harness only imports
# stdlib, so this is still the first chance.
#
# Two reasons, and the second is the one that bites. time.process_time()
# sums CPU over every thread in the process, and OpenBLAS worker threads
# SPIN-WAIT rather than sleep: measured on this box, one reference solve
# burned 349.6 ms of process CPU for 105.0 ms of this thread's CPU -- a
# thread factor of 3.33, nearly all of it threads busy-waiting on 96-element
# vectors no BLAS should have bothered to thread. That inflates the number
# the solve-time guard budgets, and it inflates it by an amount that depends
# on how many cores are idle, which is exactly the load-dependence the guard
# exists to remove. Pinning makes process CPU mean work done again.
#
# And it makes the budgets portable: a runner with a different core count
# would otherwise record a different thread factor for identical work, so
# ratios calibrated on one machine would be wrong on another.
#
# setdefault, not assignment: an operator investigating threading can still
# override from the environment, and the guard's own parallelism check will
# then tell them what it did to the measurement. Numerics are unaffected --
# the drift gate's numeric probe hashes identically at one, two and default
# threads on this build.
for _threads in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                 "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_threads, "1")

import numpy as np
from scipy.optimize import minimize

from profiles import DT, house, prices, weather
from heatpump_optimizer import pv as pv_model

# ===========================================================================
# The solve-time guard: relative to this machine, not to a stopwatch
# ===========================================================================
#
# This check used to compare every scenario's solve against an absolute
# millisecond budget (STRESS_SOLVE_BUDGET_MS). An absolute budget cannot
# tell "this change made the solver slower" from "this machine is busy",
# and only the first of those is a bug. On a shared box it answers the
# second one: the check has failed five times in one day for load it could
# not see, twice needing a hand-built interleaved A/B against a pristine
# main to prove the branch innocent, and once failing on pristine main with
# WORSE timings than the branch under test. A guard that fires on the
# machine's mood is not a guard; it is a tax on every reader of its output.
#
# Two changes, and the first matters more than the second.
#
# THE CLOCK. The budgets are denominated in CPU time, not wall clock.
# Wall clock counts time spent waiting for a busy machine; CPU time counts
# work done. Measured on this box by putting three extra CPU hogs on it
# while re-solving the same scenario:
#
#     scenario wall time   1694 ms -> 5224 ms   (3.08x)
#     scenario CPU time    1044 ms -> 1038 ms   (0.99x)
#
# One of those two numbers is about the code and the other is about the
# neighbours. result.solve_time_ms is the wall-clock one, so stress.py
# times the solve itself with time.process_time() and budgets that. This
# is the whole trick; everything below is refinement.
#
# THE RULER. CPU time still depends on how fast the machine is, which is
# why an absolute CPU budget would go wrong on a slow CI runner in the
# same way an absolute wall budget goes wrong on a busy one. So it is
# normalised: immediately before each scenario's solve this file times a
# REFERENCE SOLVE -- a fixed, seeded L-BFGS-B minimisation over a 96-step
# vector, built out of the same numpy shapes and operations the optimizer's
# own objective uses -- and budgets the ratio between them. Two properties
# make it the right ruler:
#
#   * It is defined HERE, in the test suite, not in custom_components. No
#     change to the integration can make it slower or faster, so it never
#     moves for the reason the guard is watching for.
#   * It is the same kind of work the solver does -- bounded L-BFGS-B over
#     a small dense vector with a Python objective -- so CPU contention,
#     thermal throttling and a noisy neighbour move it and the real solve
#     together.
#
# A ruler has to be steadier than what it measures, and the first version
# of this one was not: see reference_solve for the measurements that sized
# it. On the same three-hog experiment the two ratios behaved like this:
#
#     wall-clock ratio     3.0 -> 6.4   (2.12x -- absorbs only part of it)
#     CPU-time ratio       2.9 -> 3.0   (1.03x)
#
# which is why the check is denominated in CPU. A wall-clock ratio was
# tried first and rejected on this evidence rather than on taste.
#
# There are two relative checks, because they catch different things.
#
#   * Per scenario: a solve fails when it exceeds STRESS_SOLVE_RATIO times
#     the reference measured alongside it (median of a short trailing
#     window, so a single hiccup in either direction cannot decide the
#     run). This catches one scenario going pathological. Its budget has
#     to be wide enough for the most expensive scenario in the sweep, so
#     the cheap ones sit far under it -- which is exactly the weakness the
#     old absolute budget had, for the same reason.
#   * Whole sweep: total solve time against total reference time, under
#     STRESS_SWEEP_RATIO. Totals average the per-scenario spread away, so
#     this margin is far tighter, and it is what notices a change that
#     made everything moderately slower -- the regression that would
#     otherwise hide under a budget sized for the worst case.
#
# Load lifts the reference and both budgets with it. A solver that
# genuinely got slower does not lift the reference at all, so the ratios --
# and only the ratios -- blow up. That is exactly the question worth asking.
#
# The absolute ceiling stays as a backstop, and stays on the WALL clock,
# because the thing it is there to catch -- a solve that has stopped
# converging and will never return -- is a wall-clock problem. It is
# deliberately far above anything load can produce: it exists for a hung
# solve, not for a busy afternoon, and it is no longer the primary signal.
#
# For scale, from a real run of this file on unmodified code, on a
# four-CPU box carrying five other test suites: the dearest scenario took
# 87 977 ms of wall clock against the 90 000 ms absolute budget the release
# gate passes in. Two seconds of headroom, on code that had changed
# nothing. That is the false failure this rewrite removes, caught in the
# act.
#
# STRESS_SOLVE_BUDGET_MS is retired. It is still read, and a run that sets
# it says so loudly, because the old value would otherwise look like it was
# still doing something.

#: A scenario may cost this many times the reference solve's CPU.
#: Measured, not guessed, and measured with threads pinned as this file
#: now pins them: the two dearest scenarios came out at 655x and 662x --
#: 49.6 s and 49.8 s of solver CPU against a ~75 ms reference. (Unpinned
#: the same scenarios read 150x and 168x, because an unpinned reference
#: burns 3.3x its own work in spinning BLAS threads while a real solve
#: burns only 1.27x. That mismatch is why the numbers had to be taken
#: again and why the parallelism check below exists.) The budget leaves
#: the worst of those a factor of ~2.1, because this check exists to catch ONE scenario going
#: pathological and its budget has to clear the dearest scenario in the
#: sweep -- the cheap ones therefore sit far under it. The sweep-wide check
#: below is the tight one. The observed spread is printed at the end of the
#: section, so the headroom is visible rather than assumed.
SOLVE_BUDGET_RATIO = float(os.environ.get("STRESS_SOLVE_RATIO", "1400"))

#: The whole sweep may cost this many times the reference work timed
#: alongside it. Totals average the per-scenario spread away -- and average
#: the ruler's own noise away with it, over fifty-odd samples -- so this
#: margin is far tighter than the per-scenario one, and it is what catches
#: a change that made everything moderately slower: a uniform 50 % would
#: sail under any per-scenario budget wide enough for the dearest scenario
#: and lands here instead. Expected around 250 with threads pinned, from
#: the per-scenario measurements above and the sweep's cost distribution;
#: the run prints the figure it actually saw, and the budget leaves that
#: estimate a factor of ~1.8. That margin is deliberately generous for
#: a first release of this check -- there is one run's worth of evidence
#: behind it. Tighten it once a few runs' aggregate ratios are on record;
#: the run prints its own so they accumulate in gate output.
SWEEP_BUDGET_RATIO = float(os.environ.get("STRESS_SWEEP_RATIO", "450"))

#: Backstop only: a solve this slow is pathological whatever the machine is
#: doing -- a non-converging objective, not a busy box.
SOLVE_CEILING_MS = float(os.environ.get("STRESS_SOLVE_CEILING_MS", "600000"))

#: Per-scenario budgets (D9-03). The single SOLVE_BUDGET_RATIO above has to
#: clear the dearest scenario in the sweep (measured ~662x its reference),
#: which means the cheapest one -- a few multiples -- could regress by three
#: orders of magnitude and still pass: exactly the hole the old absolute
#: budget had, rebuilt one level up. Each scenario therefore carries its OWN
#: budget, recorded in tests/stress_budgets.json as a clean run's ratio
#: against the reference solve (a pure work ratio: the reference is timed on
#: the same machine, in the same run, so the number travels). A scenario may
#: cost this many times its own recorded ratio.
SCENARIO_BUDGET_FACTOR = float(os.environ.get("STRESS_SCENARIO_FACTOR", "3.0"))
#: ...and a scenario that has become CHEAPER than its record by more than
#: this factor makes the table stale-high: a later regression back to the
#: old cost would pass unnoticed. Like the golden-claims file, the table is
#: re-recorded deliberately (`--record-budgets`), not inherited.
SCENARIO_STALE_FACTOR = float(os.environ.get("STRESS_STALE_FACTOR", "3.0"))
#: A floor under the per-scenario budget, so a scenario recorded at 2x is
#: not failed for normal solver jitter at 2.5x.
SCENARIO_BUDGET_FLOOR_RATIO = float(
    os.environ.get("STRESS_SCENARIO_FLOOR", "10.0")
)

#: Memory instrumentation (D9-04). tracemalloc slows allocation-heavy code,
#: so it must never run inside the timed sweep; the memory pass re-runs a
#: fixed subset of scenarios afterwards, untimed, and reports the traced
#: allocation peak and the process's RSS watermark growth. Peaks are
#: budgeted against the same recorded table, at this factor.
MEMORY_BUDGET_FACTOR = float(os.environ.get("STRESS_MEMORY_FACTOR", "1.5"))
#: How many of the dearest scenarios (by recorded cost) the memory pass
#: covers. The dear ones allocate the biggest trajectories; a leak or an
#: unbounded retention shows up there first.
MEMORY_TOP_N = int(os.environ.get("STRESS_MEMORY_TOP_N", "6"))

#: The committed per-scenario budget table, read from the repo root (the
#: suite always runs from there, per tests/run.sh). Contents: {"scenario":
#: {"ratio": <clean-run work ratio>, "rss_peak_mb": ..., "traced_peak_mb":
#: ...}}. Recorded by `stress.py --record-budgets`, which prints the table
#: for shell capture (see print_budget_table); a missing or renamed
#: scenario fails the check run loudly rather than falling back to the
#: global budget, because a silent fallback is how the cheapest scenario
#: regressed 2626x unnoticed in the first place.
BUDGET_TABLE_PATH = "tests/stress_budgets.json"

#: How many reference samples the trailing median runs over. Wide enough
#: that the ruler varies less than the solves it judges (see
#: reference_solve), narrow enough to still follow the machine's load
#: through a sweep that takes tens of minutes.
CALIBRATION_WINDOW = int(os.environ.get("STRESS_CALIBRATION_WINDOW", "7"))

_RETIRED_BUDGET = os.environ.get("STRESS_SOLVE_BUDGET_MS")

_CAL_N = 96
_cal_rng = np.random.default_rng(4711)
_CAL_WEIGHTS = np.abs(_cal_rng.standard_normal(_CAL_N)) + 0.5
_CAL_TARGET = 21.0 + 0.5 * _cal_rng.standard_normal(_CAL_N)
_CAL_START = np.full(_CAL_N, 1.5)
_CAL_BOUNDS = [(0.0, 5.0)] * _CAL_N


def _reference_objective(x: np.ndarray) -> float:
    """A stand-in for the space-heating objective, fixed for all time.

    Same shapes and same kinds of operation as the real one -- a cumulative
    sum for stored energy, a squared penalty against a comfort target, a
    smoothness term over the differences, an exponential response curve --
    so it responds to machine load the way a real solve does. Its arithmetic
    is nobody's business but this file's: it must never be "improved", or
    the ruler moves and every historical ratio stops meaning anything.
    """
    stored = np.cumsum(x) * 0.25
    return float(
        np.sum(_CAL_WEIGHTS * x)
        + np.sum((stored - _CAL_TARGET) ** 2)
        + 0.05 * np.sum(np.diff(x) ** 2)
        + np.sum(np.exp(-x / 3.0))
    )


def reference_solve() -> tuple[float, float, float]:
    """One reference solve: (wall ms, process CPU ms, this-thread CPU ms).

    Both CPU clocks, because they answer different questions.
    ``process_time`` sums CPU over every thread of the process, so a numpy
    build that runs BLAS on N threads records roughly N times the
    single-threaded figure. ``thread_time`` counts only this thread. Their
    ratio is the effective parallelism of the timed section, and the guard
    checks that the reference's matches the scenarios' -- see the
    parallelism check at the end of the sweep for why that matters.
    """
    started = time.perf_counter()
    started_cpu = time.process_time()
    started_thread = time.thread_time()
    # The iteration cap is not a convergence setting: it makes the amount of
    # work FIXED. L-BFGS-B stops on the limit rather than on a tolerance, so
    # every call costs the same number of objective evaluations whatever the
    # machine, which is what a ruler has to do. Numerical gradients
    # (eps=1e-4, as the real solver uses) over 96 bounded variables are most
    # of that cost.
    #
    # The SIZE was measured, not guessed, and the first guess was wrong. At
    # maxiter=3 the call took ~78 ms and had a coefficient of variation of
    # 19-29 % on a loaded box, while the scenario solves it was meant to
    # judge varied by only 9.5 %: the ruler wobbled more than the thing it
    # measured, so dividing by it made the measurement worse rather than
    # better. A call that short is at the mercy of a single scheduling
    # quantum. Measured against the same box: ~78 ms -> CV 19 %, ~610 ms ->
    # CV 10 %, ~1.6 s -> CV 4.5 %. maxiter=12 lands in the middle at a few
    # hundred milliseconds, and the trailing median over CALIBRATION_WINDOW
    # samples takes it below the solves' own variation, at a cost of one
    # sample per scenario rather than a rerun of anything.
    minimize(
        _reference_objective,
        _CAL_START,
        method="L-BFGS-B",
        bounds=_CAL_BOUNDS,
        options={"maxiter": 12, "ftol": 1e-6, "eps": 1e-4},
    )
    return ((time.perf_counter() - started) * 1000.0,
            (time.process_time() - started_cpu) * 1000.0,
            (time.thread_time() - started_thread) * 1000.0)


class Calibration:
    """A rolling measurement of how much work this machine does per unit CPU.

    Keeps both clocks. CPU time is what the budgets are denominated in --
    it is what does not move when the box gets busy -- and wall time is
    kept only so the run can report its own overhead honestly.
    """

    def __init__(self, window: int) -> None:
        self.window = max(1, window)
        self.samples: list[float] = []      # CPU ms, trailing window
        self.all_cpu: list[float] = []
        self.all_wall: list[float] = []
        self.all_thread: list[float] = []
        self.overhead_ms = 0.0              # wall, for reporting
        self.count = 0

    def warm_up(self) -> None:
        """Pay scipy's first-call costs, then fill the window with samples.

        The very first call measures imports and page faults rather than the
        machine's speed, so it is timed as overhead and thrown away.
        """
        started = time.perf_counter()
        reference_solve()
        self.overhead_ms += (time.perf_counter() - started) * 1000.0
        for _ in range(self.window):
            self.sample()

    def sample(self) -> float:
        started = time.perf_counter()
        wall, cpu, thread = reference_solve()
        self.samples.append(cpu)
        self.all_cpu.append(cpu)
        self.all_wall.append(wall)
        self.all_thread.append(thread)
        if len(self.samples) > self.window:
            self.samples.pop(0)
        self.count += 1
        self.overhead_ms += (time.perf_counter() - started) * 1000.0
        return cpu

    @property
    def unit_ms(self) -> float:
        """Trailing median reference CPU time -- the current machine unit."""
        return float(np.median(self.samples))

    def budget_ms(self) -> float:
        return SOLVE_BUDGET_RATIO * self.unit_ms

    def spread(self) -> tuple[float, float, float]:
        arr = np.asarray(self.all_cpu, dtype=float)
        return float(arr.min()), float(np.median(arr)), float(arr.max())

    def wall_spread(self) -> tuple[float, float, float]:
        arr = np.asarray(self.all_wall, dtype=float)
        return float(arr.min()), float(np.median(arr)), float(arr.max())

    @property
    def parallelism(self) -> float:
        """Process CPU over this-thread CPU: the reference's thread factor."""
        thread = float(np.median(self.all_thread)) if self.all_thread else 0.0
        cpu = float(np.median(self.all_cpu)) if self.all_cpu else 0.0
        return cpu / thread if thread > 1e-9 else 1.0
from heatpump_optimizer.dhw_schedule import hour_in_windows, parse_windows
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.presets import (
    BuildingPreset,
    EMITTER_FLOOR,
    EMITTER_RADIATORS,
    ERA_1960_1980,
    ERA_POST_2005,
    ERA_PRE_1960,
    STRUCTURE_CONCRETE_SLAB,
    STRUCTURE_MASONRY,
    STRUCTURE_TIMBER_CRAWLSPACE,
    derive,
)
from heatpump_optimizer.thermal_model import (
    ThermalModel,
    ThermalParameters,
    ThermalState,
)

R = Results("Stress and economics")

START = datetime(2026, 1, 15, 0, 0)

# Season -> (price profile, weather profile). Paired because a summer price
# curve with a January weather profile is not a case any user has.
SEASONS = {
    "winter": ("winter_typical", "winter_cold"),
    "winter_extreme": ("winter_extreme", "winter_cold"),
    "winter_mild": ("winter_typical", "winter_mild"),
    "shoulder": ("shoulder", "shoulder"),
    "summer": ("summer_typical", "summer_warm"),
    "summer_negative": ("summer_negative", "summer_warm"),
    "flat": ("flat", "winter_cold"),
}

# Building archetypes covering the light/heavy and leaky/tight corners.
BUILDINGS = {
    "light_new": BuildingPreset(
        structure=STRUCTURE_TIMBER_CRAWLSPACE,
        era=ERA_POST_2005,
        heated_area_m2=120,
        lower_emitter=EMITTER_RADIATORS,
    ),
    "heavy_old": BuildingPreset(
        structure=STRUCTURE_MASONRY,
        era=ERA_PRE_1960,
        heated_area_m2=200,
        lower_emitter=EMITTER_FLOOR,
    ),
    "typical_slab": BuildingPreset(
        structure=STRUCTURE_CONCRETE_SLAB,
        era=ERA_1960_1980,
        heated_area_m2=150,
        lower_emitter=EMITTER_FLOOR,
    ),
}


def build_case(
    *,
    season: str,
    building: str | None = None,
    two_zone: bool = False,
    dhw: bool = True,
    tariff: bool = False,
    pv: bool = False,
    cycling: float = 0.0,
    cop_scale: float = 1.0,
    hours: int = 24,
    state: dict | None = None,
    config: dict | None = None,
):
    """One fully specified run of the optimizer."""
    price_key, weather_key = SEASONS[season]
    cfg = house(two_zone=two_zone, dhw=dhw)
    if building:
        preset = BuildingPreset(**{**vars(BUILDINGS[building]), "two_zone": two_zone})
        derived = derive(preset)
        derived.pop("heating_response_hours", None)
        cfg.update(derived)
    cfg.update(config or {})

    params = ThermalParameters.from_config(cfg)
    params.dhw_enabled = dhw
    params.cop_scale = cop_scale

    opt_cfg = OptimizationConfig(
        horizon_hours=hours,
        time_step_minutes=15,
        target_temp=cfg["target_temperature"],
        min_temp=cfg["min_temperature"],
        max_temp=cfg["max_temperature"],
        cycling_cost=cycling,
    )
    if tariff:
        opt_cfg.peak_price_per_kw = 20.0
        opt_cfg.peak_threshold_kw = 3.0
        opt_cfg.baseline_load_kw = 1.5

    n = int(hours / DT)

    def fit(arr):
        arr = np.asarray(arr, dtype=float)
        if len(arr) >= n:
            return arr[:n]
        return np.tile(arr, int(np.ceil(n / len(arr))))[:n]

    price_series = fit(prices(price_key, START))
    outdoor, wind, rain, solar = (fit(a) for a in weather(weather_key, START))

    surplus = None
    if pv:
        production = np.clip(solar / 1000.0 * 8.0 * 0.8, 0, 8.0)
        surplus = np.clip(production - 1.0, 0.0, None)
        # Prices stay the raw import series. Since v3.8.0 the optimizer
        # prices the surplus-covered energy at the export compensation
        # itself, piecewise per step, exactly as the coordinator wires it —
        # substituting a cliff price into the series here would double-count
        # the discount.
        opt_cfg.pv_export_price = 0.25

    initial = ThermalState(
        room_temperature=21.0,
        slab_temperature=22.0,
        outdoor_temperature=float(outdoor[0]),
        upper_floor_temperature=21.0,
        lower_floor_temperature=21.0,
        dhw_temperature=50.0,
        dhw_hours_since_legionella=20.0,
        buffer_tank_temperature=40.0,
    )
    for key, value in (state or {}).items():
        setattr(initial, key, value)

    model = ThermalModel(params)
    optimizer = HeatPumpOptimizer(model, opt_cfg)
    # CPU time, measured here rather than taken from result.solve_time_ms,
    # which is wall clock. Wall clock counts time spent waiting for a busy
    # machine; CPU time counts work done. Measured on this box: putting
    # three extra CPU hogs on it moved a scenario's wall time 3.08x and its
    # CPU time 0.99x. Only one of those two numbers is about the code.
    _cpu_before = time.process_time()
    _thread_before = time.thread_time()
    result = optimizer.optimize(
        initial, price_series, outdoor, wind, rain, solar, START, None, surplus
    )
    solve_cpu_ms = (time.process_time() - _cpu_before) * 1000.0
    solve_thread_ms = (time.thread_time() - _thread_before) * 1000.0
    return {
        "result": result,
        "solve_cpu_ms": solve_cpu_ms,
        "solve_thread_ms": solve_thread_ms,
        "model": model,
        "params": params,
        "config": opt_cfg,
        "cfg": cfg,
        "prices": price_series,
        "outdoor": outdoor,
        "wind": wind,
        "rain": rain,
        "solar": solar,
        "initial": initial,
        "optimizer": optimizer,
        "surplus": surplus,
        "n": n,
    }


# ===========================================================================
# Invariants that must hold in every scenario
# ===========================================================================


def check_invariants(label: str, run: dict) -> list[str]:
    """Return a list of violations. Empty means the plan is sound."""
    problems = []
    result = run["result"]
    params = run["params"]
    cfg = run["config"]
    n = run["n"]

    space = np.asarray(result.power_schedule, dtype=float)
    dhw = np.asarray(result.dhw_power_schedule or np.zeros(n), dtype=float)
    p_max = params.max_electrical_power

    # --- physical ---------------------------------------------------------
    if not np.all(np.isfinite(space)):
        problems.append("space power is not finite")
    if not np.all(np.isfinite(dhw)):
        problems.append("DHW power is not finite")
    if space.min() < -1e-6:
        problems.append(f"negative space power {space.min():.3f}")
    if dhw.size and dhw.min() < -1e-6:
        problems.append(f"negative DHW power {dhw.min():.3f}")
    # The compressor serves one circuit at a time, so the *sum* is what the
    # hardware has to deliver.
    combined = space + (dhw if dhw.size == space.size else 0.0)
    if combined.max() > p_max + 1e-3:
        problems.append(
            f"combined power {combined.max():.3f} exceeds the {p_max:.1f} kW pump"
        )

    for name, trajectory in (
        ("room", result.room_temp_trajectory),
        ("slab", result.slab_temp_trajectory),
        ("upper", result.upper_temp_trajectory),
        ("lower", result.lower_temp_trajectory),
        ("dhw", result.dhw_temp_trajectory),
    ):
        if not trajectory:
            continue
        arr = np.asarray(trajectory, dtype=float)
        if not np.all(np.isfinite(arr)):
            problems.append(f"{name} trajectory is not finite")
        elif arr.min() < -50 or arr.max() > 120:
            problems.append(
                f"{name} trajectory left physical reality "
                f"({arr.min():.1f}..{arr.max():.1f} °C)"
            )

    if result.dhw_temp_trajectory:
        peak = float(np.max(result.dhw_temp_trajectory))
        # A tank that *starts* above its rating cannot be brought down by a
        # plan -- there is no way to un-heat water, only to stop adding heat
        # and let it coast. So the bound is the rating or the starting
        # temperature, whichever is higher. The RATING, not the everyday
        # charge limit: a disinfection cycle is meant to exceed the limit
        # (v5.1.10 split the two).
        ceiling = max(params.dhw_hard_max_temp, run["initial"].dhw_temperature)
        if peak > ceiling + 1.0:
            problems.append(
                f"tank reached {peak:.1f} °C, over its {ceiling:.0f} °C ceiling"
            )

    # --- accounting -------------------------------------------------------
    # With PV surplus the cost is piecewise — covered energy at the export
    # compensation, the rest at import — so the plain price-times-power sum
    # is only the right reference when there is no surplus.
    surplus = run.get("surplus")
    if surplus is not None:
        recomputed = pv_model.piecewise_cost(
            np.asarray(result.prices),
            np.asarray(surplus)[: combined.size],
            run["config"].pv_export_price,
            combined,
            DT,
        )
    else:
        recomputed = float(np.sum(np.asarray(result.prices) * combined * DT))
    if abs(recomputed - result.predicted_cost) > max(0.05, abs(recomputed) * 0.01):
        problems.append(
            f"predicted cost {result.predicted_cost:.2f} does not match the "
            f"schedule's {recomputed:.2f}"
        )
    if result.baseline_cost < -1e-6:
        problems.append(f"negative baseline cost {result.baseline_cost:.2f}")
    if not -100.0 <= result.savings_percentage <= 100.0:
        problems.append(f"savings {result.savings_percentage:.1f}% out of range")

    # --- provenance and reporting ----------------------------------------
    if len(result.price_known) != len(result.prices):
        problems.append("price provenance mask does not cover the horizon")
    if len(result.space_reasons) != n:
        problems.append("reason codes do not cover the horizon")
    else:
        unexplained = sum(
            1
            for i, p in enumerate(space)
            if p > 0.05 and result.space_reasons[i] == "idle"
        )
        if unexplained:
            problems.append(f"{unexplained} heating steps have no reason code")

    return problems


#: How far below the comfort floor a plan may sit before it counts as a
#: failure rather than as the soft constraint doing its job.
COMFORT_TOLERANCE_DEGREE_HOURS = 1.5


def best_possible_violation(run: dict) -> float:
    """Degree-hours below the floor with the pump running flat out.

    An undersized pump in a leaky house cannot hold the comfort floor at all,
    and calling that a planning bug would be blaming the optimizer for physics.
    """
    model = run["model"]
    room, _, upper, lower = model.simulate_trajectory(
        initial_state=run["initial"],
        power_schedule=np.full(run["n"], run["params"].max_electrical_power),
        outdoor_temps=run["outdoor"],
        wind_speeds=run["wind"],
        precipitation=run["rain"],
        solar_radiation=run["solar"],
        dt_hours=DT,
    )
    if run["params"].two_zone_enabled:
        indoor = np.minimum(upper[1:], lower[1:])
    else:
        indoor = room[1:]
    cfg = run["config"]
    floor = np.array(
        [cfg.get_temp_bounds((i * DT) % 24)[0] for i in range(len(indoor))]
    )
    return float(np.sum(np.maximum(0.0, floor - indoor)) * DT)


def comfort_violation(run: dict) -> float:
    """Degree-hours below the comfort floor, in the coldest zone."""
    result = run["result"]
    cfg = run["config"]
    if result.upper_temp_trajectory and result.lower_temp_trajectory:
        indoor = np.minimum(
            np.asarray(result.upper_temp_trajectory[1:]),
            np.asarray(result.lower_temp_trajectory[1:]),
        )
    else:
        indoor = np.asarray(result.room_temp_trajectory[1:])
    floor = np.array(
        [cfg.get_temp_bounds((i * DT) % 24)[0] for i in range(len(indoor))]
    )
    return float(np.sum(np.maximum(0.0, floor - indoor)) * DT)


def dhw_shortfall(run: dict) -> float:
    """Worst shortfall below the usable minimum inside a demand window, °C."""
    result = run["result"]
    if not result.dhw_temp_trajectory:
        return 0.0
    windows = parse_windows(run["cfg"].get("dhw_windows", "") or "")
    if not windows:
        return 0.0
    temps = np.asarray(result.dhw_temp_trajectory[1:])
    hours = [(START.hour + i * DT) % 24 for i in range(len(temps))]
    inside = np.array([hour_in_windows(h, windows) for h in hours])
    if not inside.any():
        return 0.0
    return float(max(0.0, run["params"].dhw_min_temp - temps[inside].min()))


# ===========================================================================
# The per-scenario budget table (D9-03) and the memory pass (D9-04)
# ===========================================================================
def load_budget_table() -> dict:
    """The committed per-scenario budgets, or {} when not yet recorded."""
    try:
        with open("tests/stress_budgets.json", encoding="utf-8") as fh:
            table = json.load(fh)
    except (OSError, ValueError):
        return {}
    return table if isinstance(table, dict) else {}


def print_budget_table(table: dict) -> None:
    """Emit the budget table between markers, for shell capture.

    Recording never writes into the repository itself: the JSON goes to
    stdout between BEGIN/END BUDGET TABLE markers and the operator (or
    the workflow) captures it --

        python3 tests/stress.py --record-budgets \\
          | sed -n '/^BEGIN BUDGET TABLE$/,/^END BUDGET TABLE$/p' \\
          | grep -v BUDGET TABLE > tests/stress_budgets.json

    A recording is read as a diff like any golden fixture, and the extra
    step keeps that reading deliberate.
    """
    ordered = {label: table[label] for label in sorted(table)}
    print("BEGIN BUDGET TABLE")
    print(json.dumps(ordered, indent=1, sort_keys=True))
    print("END BUDGET TABLE")


def scenario_budget(label: str, table: dict) -> float | None:
    """This scenario's allowed work ratio, or None when unrecorded.

    The floor keeps normal solver jitter on a cheap scenario (recorded at
    2x, say) from failing a budget that a 3x factor would turn into 6x --
    but never below what the dearest cheap scenario actually needs, so the
    floor is a fraction of the historical global budget, not of this
    scenario's own record.
    """
    entry = table.get(label)
    if not isinstance(entry, dict):
        return None
    recorded = float(entry.get("ratio", 0.0))
    if recorded <= 0.0:
        return None
    return max(
        recorded * SCENARIO_BUDGET_FACTOR, SCENARIO_BUDGET_FLOOR_RATIO
    )


def rss_mb() -> float:
    """The process's resident set high-water mark, in MiB (platform-tuned)."""
    ru = resource.getrusage(resource.RUSAGE_SELF)
    # macOS reports bytes, Linux reports KiB.
    div = 1024.0 * 1024.0 if sys.platform == "darwin" else 1024.0
    return float(ru.ru_maxrss) / div


def _memory_probe_main(argv: list[str]) -> int:
    """`--memory-probe <json>`: build one scenario, print its memory peaks.

    Runs in a SUBPROCESS on purpose: tracemalloc sees only Python-object
    allocations (numpy's allocator is largely invisible to it -- the whole
    sweep traced ~1.8 MiB while actually holding tens of MiB of arrays),
    and ru_maxrss in the parent is a watermark every earlier scenario
    already raised. A fresh process gives each scenario an honest
    high-water mark; the interpreter+numpy baseline it also contains is
    the same constant in every probe, recorded and measured alike, so it
    cancels in the comparison.
    """
    spec = json.loads(argv[argv.index("--memory-probe") + 1])
    tracemalloc.start()
    build_case(**spec)
    _cur, traced_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(
        json.dumps(
            {
                "rss_mb": round(rss_mb(), 1),
                "traced_mb": round(traced_peak / (1024.0 * 1024.0), 2),
            }
        )
    )
    return 0


if "--memory-probe" in sys.argv:
    sys.exit(_memory_probe_main(sys.argv))


if __name__ == "__main__":
    # ===========================================================================
    # The sweep
    # ===========================================================================
    R.section("Combination sweep")

    combinations = []
    for season, two_zone, dhw in itertools.product(
        SEASONS, (False, True), (False, True)
    ):
        combinations.append(
            dict(season=season, two_zone=two_zone, dhw=dhw, label=f"{season}/{'2z' if two_zone else '1z'}/{'dhw' if dhw else 'space'}")
        )

    # Feature combinations, on the seasons where each actually bites.
    for season in ("winter", "shoulder"):
        for tariff, pv, cycling in itertools.product(
            (False, True), (False, True), (0.0, 1.0)
        ):
            if not (tariff or pv or cycling):
                continue
            flags = "+".join(
                f for f, on in (("tariff", tariff), ("pv", pv), ("cycle", cycling)) if on
            )
            combinations.append(
                dict(
                    season=season, two_zone=True, dhw=True, tariff=tariff, pv=pv,
                    cycling=cycling, label=f"{season}/{flags}",
                )
            )

    # Building archetypes.
    for building, season in itertools.product(BUILDINGS, ("winter", "shoulder")):
        combinations.append(
            dict(season=season, building=building, dhw=True,
                 label=f"{building}/{season}")
        )

    failures = 0
    comfort_failures: list[str] = []
    worst_dhw = 0.0
    slow: list[str] = []
    pathological: list[str] = []
    ratios: list[tuple[float, str, float, float]] = []
    sweep_reference_ms = 0.0
    sweep_solve_ms = 0.0
    sweep_solve_thread_ms = 0.0

    if _RETIRED_BUDGET is not None:
        print(
            f"  NOTE: STRESS_SOLVE_BUDGET_MS={_RETIRED_BUDGET} is set but no longer\n"
            "        decides anything. An absolute budget cannot separate a slower\n"
            "        solver from a busier machine, which is the only question this\n"
            "        guard exists to answer, so the check is now relative to a\n"
            "        reference solve timed on this machine beside every scenario.\n"
            "        Tune it with STRESS_SOLVE_RATIO (multiple of the reference)\n"
            "        and STRESS_SOLVE_CEILING_MS (the pathological backstop)."
        )

    calibration = Calibration(CALIBRATION_WINDOW)
    calibration.warm_up()
    print(
        f"  solve-time guard: reference solve {calibration.unit_ms:.1f} ms of CPU "
        f"on this machine, budget {SOLVE_BUDGET_RATIO:.0f}x that per scenario "
        f"(= {calibration.budget_ms() / 1000.0:.1f} s of CPU), sweep budget "
        f"{SWEEP_BUDGET_RATIO:.0f}x, absolute wall ceiling {SOLVE_CEILING_MS:.0f} ms"
    )

    # D9-03: each scenario is ALSO judged against its own recorded work
    # ratio (tests/stress_budgets.json). The global budget above has to
    # clear the dearest scenario, so alone it let the cheapest one regress
    # by three orders of magnitude; the per-scenario table closes that. In
    # record mode the sweep's measurements become the new table instead of
    # being judged.
    record_mode = "--record-budgets" in sys.argv
    budget_table = load_budget_table()
    unrecorded: list[str] = []
    stale_cheap: list[str] = []
    over_budget: list[str] = []
    new_table: dict[str, dict] = {}
    if not record_mode and not budget_table:
        print(
            "  NOTE: no budget table found; run `stress.py --record-budgets`\n"
            "        on a clean tree to give every scenario its own budget."
        )
    # The loop below pops "label" out of each combo; the memory pass re-runs
    # a subset by label afterwards and needs the build arguments intact.
    combos_by_label = {
        c["label"]: {k: v for k, v in c.items() if k != "label"}
        for c in combinations
    }

    for combo in combinations:
        label = combo.pop("label")
        # Time the reference immediately before the solve it will judge, so the
        # ruler and the thing being measured see the same machine.
        sample_ms = calibration.sample()
        unit_ms = max(calibration.unit_ms, 1e-6)
        budget_ms = SOLVE_BUDGET_RATIO * unit_ms
        run = build_case(**combo)
        solve_ms = float(run["solve_cpu_ms"])          # CPU: the load-free clock
        wall_ms = float(run["result"].solve_time_ms)   # wall: for the ceiling only
        ratio = solve_ms / unit_ms
        ratios.append((ratio, label, solve_ms, unit_ms))
        sweep_reference_ms += sample_ms
        sweep_solve_ms += solve_ms
        sweep_solve_thread_ms += float(run["solve_thread_ms"])
        if record_mode:
            new_table[label] = {"ratio": round(ratio, 2)}
        else:
            allowed = scenario_budget(label, budget_table)
            if allowed is None:
                unrecorded.append(label)
            else:
                recorded = float(budget_table[label]["ratio"])
                if ratio > allowed:
                    over_budget.append(
                        f"{label} at {ratio:.1f}x its reference vs its own "
                        f"budget {allowed:.1f}x (recorded {recorded:.1f}x "
                        f"x {SCENARIO_BUDGET_FACTOR:.0f})"
                    )
                if ratio < recorded / SCENARIO_STALE_FACTOR:
                    stale_cheap.append(
                        f"{label} at {ratio:.1f}x vs recorded {recorded:.1f}x "
                        f"(cheaper by more than {SCENARIO_STALE_FACTOR:.0f}x: "
                        f"re-record, or a regression back to the old cost "
                        f"would pass unnoticed)"
                    )
        if solve_ms > budget_ms:
            slow.append(
                f"{label} used {solve_ms:.0f} ms of CPU = {ratio:.0f}x the "
                f"{unit_ms:.1f} ms reference measured beside it "
                f"(budget {SOLVE_BUDGET_RATIO:.0f}x)"
            )
        if wall_ms > SOLVE_CEILING_MS:
            pathological.append(f"{label} took {wall_ms:.0f} ms of wall clock")
        problems = check_invariants(label, run)
        violation = comfort_violation(run)
        shortfall = dhw_shortfall(run)
        worst_dhw = max(worst_dhw, shortfall)
        if violation > COMFORT_TOLERANCE_DEGREE_HOURS:
            achievable = best_possible_violation(run)
            if violation > achievable + COMFORT_TOLERANCE_DEGREE_HOURS:
                comfort_failures.append(
                    f"{label}: {violation:.2f} vs {achievable:.2f} achievable"
                )

        # The comfort floor is a soft constraint, so a small breach is by design.
        # A large one means the penalty is not doing its job -- unless the pump
        # physically cannot hold the house, in which case no plan can, and the
        # honest comparison is against what running flat out would achieve.
        if violation > COMFORT_TOLERANCE_DEGREE_HOURS:
            achievable = best_possible_violation(run)
            if violation > achievable + COMFORT_TOLERANCE_DEGREE_HOURS:
                problems.append(
                    f"{violation:.2f} degree-hours below the comfort floor, "
                    f"against {achievable:.2f} achievable at full power"
                )
        if shortfall > 2.0:
            problems.append(f"hot water {shortfall:.1f} °C short inside a demand window")

        if problems:
            failures += 1
            print(f"  FAIL {label}")
            for p in problems:
                print(f"         {p}")

    R.check(
        f"all {len(combinations)} combinations satisfy the invariants",
        failures == 0,
        f"{failures} failed",
    )
    R.check(
        "the comfort floor is never breached beyond what physics forces",
        not comfort_failures,
        "; ".join(comfort_failures),
    )
    R.check(
        "hot water is available when promised",
        worst_dhw <= 2.0,
        f"worst shortfall {worst_dhw:.1f} °C",
    )
    # The guard can only mean something if the ruler was actually measured. A
    # calibration that silently produced nothing would turn the check below into
    # one more test that cannot fail, which is a failure mode this suite has
    # shipped five times already.
    R.check(
        "the solve-time guard calibrated against a reference solve per scenario",
        calibration.count >= len(combinations) + CALIBRATION_WINDOW
        and calibration.unit_ms > 0.0,
        f"{calibration.count} reference samples for {len(combinations)} scenarios, "
        f"unit {calibration.unit_ms:.3f} ms",
    )
    _worst = max(ratios) if ratios else (0.0, "-", 0.0, 0.0)
    _lo, _mid, _hi = calibration.spread() if calibration.all_cpu else (0.0, 0.0, 0.0)
    _wlo, _wmid, _whi = (
        calibration.wall_spread() if calibration.all_wall else (0.0, 0.0, 0.0)
    )
    print(
        f"  reference solve over the sweep: {_lo:.1f} / {_mid:.1f} / {_hi:.1f} ms of "
        f"CPU (min/median/max of {calibration.count} samples); the same samples in "
        f"wall clock: {_wlo:.1f} / {_wmid:.1f} / {_whi:.1f} ms -- the wall spread is "
        f"the machine's load, the CPU spread is all the guard has to tolerate"
    )
    print(
        f"  calibration overhead: {calibration.overhead_ms / 1000.0:.1f} s of wall "
        f"clock for {calibration.count} samples"
    )
    print(
        f"  worst scenario: {_worst[1]} used {_worst[2]:.0f} ms of CPU = "
        f"{_worst[0]:.1f}x its {_worst[3]:.1f} ms reference; budget is "
        f"{SOLVE_BUDGET_RATIO:.0f}x"
    )
    R.check(
        "every scenario's solve costs what it should, in CPU, for this machine",
        not slow,
        "; ".join(slow),
    )
    # D9-03's per-scenario half. The global check above has to accommodate
    # the dearest scenario in the sweep, which is exactly why the cheapest
    # one could regress 2626x under it alone; these two hold every scenario
    # to its own recorded cost. Unrecorded scenarios fail rather than fall
    # back -- a silent fallback to the global budget is the hole itself.
    if record_mode:
        print(
            f"  budget table: recorded {len(new_table)} scenarios; writing "
            "tests/stress_budgets.json -- read the diff before "
            f"committing it, exactly as you would a golden fixture"
        )
    else:
        R.check(
            "every scenario has a per-scenario budget on record",
            not unrecorded,
            f"{len(unrecorded)} unrecorded: {', '.join(unrecorded[:8])}"
            + (" ..." if len(unrecorded) > 8 else "")
            + "; run `stress.py --record-budgets` on a clean tree",
        )
        R.check(
            "no scenario exceeds its own recorded cost by the budget factor",
            not over_budget,
            "; ".join(over_budget),
        )
        R.check(
            "no scenario got dramatically cheaper without a re-record",
            not stale_cheap,
            "; ".join(stale_cheap),
        )

    # -- D9-04: memory instrumentation -----------------------------------
    # tracemalloc slows allocation-heavy code by more than the solve-time
    # budgets tolerate, and it only sees Python objects anyway, so the
    # memory pass re-runs a subset of scenarios UNTIMED in SUBPROCESSES
    # after the sweep: each probe reports its own ru_maxrss (a real
    # high-water mark, numpy included) and its traced allocation peak.
    # Both are budgeted from the same recorded table. The RSS budget's
    # headroom is generous on purpose: the interpreter+numpy baseline
    # differs by tens of MiB across platforms, and this check exists to
    # catch retained-growth regressions, not interpreter noise.
    R.section("Memory (D9-04)")
    mem_labels = [
        label
        for label, _ in sorted(
            ((r[1], r[0]) for r in ratios), key=lambda kv: -kv[1]
        )[:MEMORY_TOP_N]
    ]
    rss_before_mb = rss_mb()
    mem_over: list[str] = []
    mem_unrecorded: list[str] = []
    probe_env = dict(os.environ)
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(tests_dir)
    for part in (os.path.join(tests_dir, "hastub"),
                 os.path.join(repo_root, "custom_components")):
        probe_env["PYTHONPATH"] = (
            part + os.pathsep + probe_env.get("PYTHONPATH", "")
        )
    import subprocess as _sp

    for label in mem_labels:
        proc = _sp.run(
            [sys.executable, os.path.abspath(__file__), "--memory-probe",
             json.dumps(combos_by_label[label])],
            capture_output=True, text=True, env=probe_env,
        )
        try:
            probe = json.loads(proc.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            R.check(
                f"the memory probe for {label} ran",
                False,
                (proc.stderr or proc.stdout or "no output")[-200:],
            )
            continue
        rss_peak = float(probe["rss_mb"])
        traced_peak = float(probe["traced_mb"])
        entry = new_table.get(label) if record_mode else budget_table.get(label)
        recorded_rss = float(entry.get("rss_peak_mb", 0.0)) if entry else 0.0
        recorded_traced = (
            float(entry.get("traced_peak_mb", 0.0)) if entry else 0.0
        )
        if record_mode:
            new_table[label]["rss_peak_mb"] = round(rss_peak, 1)
            new_table[label]["traced_peak_mb"] = round(traced_peak, 2)
        else:
            if recorded_rss <= 0.0 or recorded_traced <= 0.0:
                mem_unrecorded.append(label)
                continue
            if rss_peak > recorded_rss + max(
                150.0, recorded_rss * (MEMORY_BUDGET_FACTOR - 1.0)
            ):
                mem_over.append(
                    f"{label} RSS peak {rss_peak:.0f} MiB vs recorded "
                    f"{recorded_rss:.0f} MiB (+150 MiB or "
                    f"x{MEMORY_BUDGET_FACTOR:.1f} headroom)"
                )
            if traced_peak > recorded_traced * MEMORY_BUDGET_FACTOR + 2.0:
                mem_over.append(
                    f"{label} traced peak {traced_peak:.1f} MiB vs recorded "
                    f"{recorded_traced:.1f} MiB "
                    f"(x{MEMORY_BUDGET_FACTOR:.1f} + 2)"
                )
        print(
            f"  {label:<34} RSS peak {rss_peak:7.1f} MiB, traced "
            f"{traced_peak:5.1f} MiB"
            + (
                f" (recorded {recorded_rss:.0f} / {recorded_traced:.1f})"
                if recorded_rss > 0.0
                else " (unrecorded)"
            )
        )
    rss_growth_mb = rss_mb() - rss_before_mb
    print(
        f"  parent RSS watermark growth over the memory pass: "
        f"{rss_growth_mb:.1f} MiB (ru_maxrss is a high-water mark; growth "
        f"here means the pass itself retained memory)"
    )
    if not record_mode:
        R.check(
            "the dearest scenarios' memory peaks stay within their "
            "recorded budgets",
            not mem_over,
            "; ".join(mem_over),
        )
        R.check(
            "every memory-pass scenario has recorded peaks",
            not mem_unrecorded,
            f"unrecorded: {mem_unrecorded}",
        )
        R.check(
            "the memory pass retains less than 512 MiB of RSS in the parent",
            rss_growth_mb < 512.0,
            f"RSS watermark grew {rss_growth_mb:.1f} MiB across "
            f"{len(mem_labels)} probe launches",
        )

    if record_mode:
        print_budget_table(new_table)
        print(
            "ALL BUDGETS RECORDED -- capture the block above into "
            "tests/stress_budgets.json and read its diff before committing; "
            "a recording is a decision, not a reflex"
        )
        sys.exit(0)
    _sweep_ratio = sweep_solve_ms / max(sweep_reference_ms, 1e-6)
    print(
        f"  whole sweep: {sweep_solve_ms / 1000.0:.1f} s of solver CPU against "
        f"{sweep_reference_ms / 1000.0:.1f} s of reference CPU = "
        f"{_sweep_ratio:.2f}x; budget is {SWEEP_BUDGET_RATIO:.2f}x"
    )
    R.check(
        "the sweep as a whole costs what it has always cost, relative to this machine",
        _sweep_ratio <= SWEEP_BUDGET_RATIO,
        f"{sweep_solve_ms / 1000.0:.1f} s of solver CPU vs "
        f"{sweep_reference_ms / 1000.0:.1f} s of reference CPU = {_sweep_ratio:.2f}x, "
        f"over the {SWEEP_BUDGET_RATIO:.2f}x budget",
    )
    # The thread factor has to cancel, or the budgets do not travel.
    #
    # time.process_time() sums CPU over every thread in the process. A numpy
    # built against a threaded BLAS records roughly N times the single-threaded
    # figure for work big enough to parallelise. That is perfectly stable on one
    # machine and completely unstable across machines -- CI has a different core
    # count -- so a ratio calibrated here would be systematically wrong there.
    #
    # It cancels in the ratio only if the reference and the scenarios are
    # parallelised to the SAME degree, and they need not be: the reference works
    # on 96-element vectors that no BLAS bothers to thread, while a scenario
    # solve touches larger arrays that one might. So rather than assume it, the
    # run measures both factors and says so. If they diverge the ratio is not a
    # pure work ratio any more and the budget below is not portable -- which is
    # a thing to be told, loudly, not to discover as a mystery failure on a
    # runner with a different core count. Pinning OMP_NUM_THREADS and
    # OPENBLAS_NUM_THREADS to 1 makes both factors 1 and the question go away.
    _ref_parallel = calibration.parallelism
    _solve_parallel = (
        sweep_solve_ms / sweep_solve_thread_ms if sweep_solve_thread_ms > 1e-9 else 1.0
    )
    print(
        f"  thread factor (process CPU / this-thread CPU): reference "
        f"{_ref_parallel:.3f}, scenarios {_solve_parallel:.3f} -- these must "
        f"match for the ratio above to be a pure work ratio that travels to "
        f"another machine"
    )
    R.check(
        "the reference and the scenarios are parallelised alike, so the thread "
        "factor cancels in the ratio",
        abs(_ref_parallel - _solve_parallel) <= 0.25 * max(_ref_parallel, 1.0),
        f"reference runs at {_ref_parallel:.2f} threads' worth of CPU and the "
        f"scenarios at {_solve_parallel:.2f}; the ratio then carries a thread "
        f"factor that will differ on a machine with another core count. Pin "
        f"OMP_NUM_THREADS=1 and OPENBLAS_NUM_THREADS=1 for this suite, or "
        f"recalibrate STRESS_SOLVE_RATIO and STRESS_SWEEP_RATIO on this machine",
    )

    # Not redundant, whatever it looks like. A CPU-time budget measures work
    # done, so it is blind to a regression that makes the solver WAIT rather
    # than compute -- a lock held across a solve, an I/O stall, a retry loop
    # with a sleep in it, a solve that never converges and never returns. Those
    # consume no CPU and would sail through every check above while making the
    # gate take an hour longer. The wall clock is the only thing that sees them,
    # which is why this ceiling stays on the wall clock and stays in the file.
    R.check(
        "no scenario hits the absolute pathological-solve ceiling",
        not pathological,
        f"wall-clock ceiling {SOLVE_CEILING_MS:.0f} ms: " + "; ".join(pathological),
    )


    # ===========================================================================
    # Economics: the claims the integration makes
    # ===========================================================================
    R.section("Economics")


    def thermostat_cost(run: dict) -> float:
        """What a plain setpoint-holding thermostat would spend."""
        power, _ = run["optimizer"]._compute_baseline_power(
            run["initial"], run["outdoor"], run["wind"], run["rain"], run["solar"], DT
        )
        return float(np.sum(run["prices"] * np.asarray(power) * DT))


    for season in ("winter", "winter_extreme", "shoulder"):
        run = build_case(season=season, two_zone=False, dhw=False)
        result = run["result"]
        baseline = thermostat_cost(run)
        R.check(
            f"{season}: cheaper than holding the setpoint",
            result.predicted_cost < baseline,
            f"{result.predicted_cost:.2f} vs {baseline:.2f}",
        )

    # With a flat price curve there is nothing to arbitrage, so the optimizer
    # should not be *worse* than a thermostat -- but neither should it claim a
    # large saving, which would mean it is simply running colder.
    flat = build_case(season="flat", two_zone=False, dhw=False)
    R.check(
        "a flat price curve produces no fictitious saving",
        flat["result"].savings_percentage < 35.0,
        f"claimed {flat['result'].savings_percentage:.1f}%",
    )
    R.check(
        "a flat price curve still respects comfort",
        comfort_violation(flat) <= COMFORT_TOLERANCE_DEGREE_HOURS,
        f"{comfort_violation(flat):.2f} degree-hours",
    )

    # More price spread must buy more saving. If it does not, the optimizer is not
    # actually responding to price.
    spread_savings = {}
    for season in ("flat", "winter", "winter_extreme"):
        run = build_case(season=season, two_zone=False, dhw=False)
        prices_arr = np.asarray(run["result"].prices)
        spread = float(prices_arr.max() - prices_arr.min())
        spread_savings[season] = (spread, run["result"].savings_percentage)

    R.check(
        "a wider price spread yields a larger saving",
        spread_savings["winter_extreme"][1] > spread_savings["winter"][1]
        > spread_savings["flat"][1],
        ", ".join(
            f"{k}: spread {v[0]:.2f} -> {v[1]:.0f}%" for k, v in spread_savings.items()
        ),
    )

    # Comfort weight is the money/degrees exchange rate, and the README publishes
    # a table of what it buys. That table is the contract, so it is what gets
    # checked -- over the documented range, where the signal is far larger than the
    # solver noise discussed below.
    comfort_curve = []
    for weight in (5.0, 10.0, 20.0, 40.0):
        run = build_case(season="winter", two_zone=False, dhw=False)
        run["config"].comfort_weight = weight
        optimizer = HeatPumpOptimizer(run["model"], run["config"])
        result = optimizer.optimize(
            run["initial"], run["prices"], run["outdoor"], run["wind"],
            run["rain"], run["solar"], START,
        )
        comfort_curve.append(
            (weight, float(np.mean(result.room_temp_trajectory)),
             result.savings_percentage)
        )

    temps = [t for _, t, _ in comfort_curve]
    savings = [s for _, _, s in comfort_curve]
    R.check(
        "a higher comfort weight is warmer, across the documented range",
        all(a < b for a, b in zip(temps, temps[1:])),
        ", ".join(f"w={w:.0f}: {t:.2f}°C" for w, t, _ in comfort_curve),
    )
    R.check(
        "a higher comfort weight saves less, across the documented range",
        all(a > b for a, b in zip(savings, savings[1:])),
        ", ".join(f"w={w:.0f}: {s:.0f}%" for w, _, s in comfort_curve),
    )
    # The README's own table, reproduced. If this drifts, either the optimizer
    # changed or the documentation is now lying to users.
    documented = {5.0: (19.4, 53), 10.0: (19.8, 51), 20.0: (20.2, 49), 40.0: (20.4, 47)}
    drift = [
        f"w={w:.0f}: {t:.1f}°C/{s:.0f}% vs documented "
        f"{documented[w][0]}°C/{documented[w][1]}%"
        for w, t, s in comfort_curve
        if abs(t - documented[w][0]) > 0.15 or abs(s - documented[w][1]) > 2
    ]
    R.check("the README's comfort-weight table still holds", not drift, "; ".join(drift))

    # Solver noise, measured directly. The objective is non-convex -- the
    # comfort penalty is one-sided and the price signal creates several distinct
    # "charge here, coast there" patterns that are each locally optimal -- so a
    # meaningless perturbation can in principle drop the solver into a different
    # basin. This used to be measured between comfort weights 2 and 5, on the
    # observation that nearby weights differ only by basin noise (~1%). The
    # v3.8.0 wind-default correction gave the comfort trade room to be real:
    # weight 2 vs 5 now buys 0.3 K of average warmth for 17% of cost, and even
    # 5 vs 5.25 moves 0.7 kWh of genuine energy, so no weight pair isolates
    # noise from signal any more. An economically nil perturbation does: a
    # ±1e-6 wobble on the prices changes the optimal cost by nothing a user
    # could ever see, so whatever it moves is pure solver instability.
    adjacent = []
    for scale in (0.0, 1.0):
        run = build_case(season="winter", two_zone=False, dhw=False)
        optimizer = HeatPumpOptimizer(run["model"], run["config"])
        wobble = np.where(np.arange(run["n"]) % 2 == 0, 1e-6, -1e-6) * scale
        result = optimizer.optimize(
            run["initial"], run["prices"] + wobble, run["outdoor"], run["wind"],
            run["rain"], run["solar"], START,
        )
        adjacent.append(result.predicted_cost)
    R.check(
        "solver noise under an economically nil perturbation stays small",
        abs(adjacent[0] - adjacent[1]) / max(adjacent) < 0.02,
        f"{adjacent[0]:.2f} vs {adjacent[1]:.2f}",
    )

    # The capacity tariff must actually flatten the peak it is priced against.
    plain = build_case(season="winter", two_zone=True, dhw=True)
    tariffed = build_case(season="winter", two_zone=True, dhw=True, tariff=True)
    plain_peak = plain["result"].projected_peak_kw
    tariff_peak = tariffed["result"].projected_peak_kw
    R.check(
        "a capacity tariff lowers the projected peak",
        tariff_peak <= plain_peak + 1e-6,
        f"{plain_peak:.2f} kW -> {tariff_peak:.2f} kW",
    )
    R.check(
        "and does not wreck comfort doing it",
        comfort_violation(tariffed) <= COMFORT_TOLERANCE_DEGREE_HOURS,
        f"{comfort_violation(tariffed):.2f} degree-hours",
    )

    # A cycling cost must reduce cycling.
    smooth = build_case(season="winter", two_zone=False, dhw=True, cycling=3.0)
    rough = build_case(season="winter", two_zone=False, dhw=True, cycling=0.0)
    R.check(
        "a cycling cost reduces compressor starts",
        smooth["result"].compressor_starts <= rough["result"].compressor_starts,
        f"{rough['result'].compressor_starts} -> {smooth['result'].compressor_starts}",
    )

    # PV surplus must pull consumption into the surplus hours.
    sunny = build_case(season="shoulder", two_zone=False, dhw=True, pv=True)
    R.check(
        "PV surplus is self-consumed",
        sunny["result"].pv_self_consumed_kwh > 0.0,
        f"{sunny['result'].pv_self_consumed_kwh:.2f} kWh",
    )

    # A better heat pump must never leave the house worse off. It is tempting to
    # assert simply that it costs less, and that was the check here until v3.9.0 --
    # but it is not an invariant of an optimizer that values comfort, and it fails
    # for a legitimate reason.
    #
    # `winter_typical` has a six-hour cheap night block, which is exactly 24
    # quarter-hour steps; both plans saturate it, so both buy 36.00 kWh and both
    # spend 23.28 SEK. What the efficient pump does with that identical energy is
    # deliver more heat: the same money buys a house 0.95 K warmer on average and
    # 1.21 K warmer at its coldest. Efficiency is converted into whichever of
    # money or comfort the user's `comfort_weight` says is worth more, and here
    # the price structure means the cheap window binds before the money does.
    #
    # So the honest invariant is dominance: never worse on either axis, and
    # strictly better on at least one.
    efficient = build_case(season="winter", two_zone=False, dhw=False, cop_scale=1.4)
    standard = build_case(season="winter", two_zone=False, dhw=False, cop_scale=1.0)


    def _warmth(run):
        """Mean indoor temperature the plan actually delivers."""
        result = run["result"]
        series = [
            s
            for s in (result.upper_temp_trajectory, result.lower_temp_trajectory)
            if s
        ] or [result.room_temp_trajectory]
        return float(np.mean([np.mean(np.asarray(s)[1:]) for s in series]))


    _eff_cost = efficient["result"].predicted_cost
    _std_cost = standard["result"].predicted_cost
    _eff_warm, _std_warm = _warmth(efficient), _warmth(standard)
    R.check(
        "a more efficient heat pump is never worse, and is better somewhere",
        _eff_cost <= _std_cost + 1e-6
        and _eff_warm >= _std_warm - 1e-6
        and (_eff_cost < _std_cost - 1e-6 or _eff_warm > _std_warm + 1e-6),
        f"cost {_std_cost:.2f} -> {_eff_cost:.2f}, "
        f"mean indoor {_std_warm:.2f} -> {_eff_warm:.2f} °C",
    )

    # A leakier house must cost more than a tight one, all else equal.
    tight = build_case(season="winter", building="light_new", dhw=False)
    leaky = build_case(season="winter", building="heavy_old", dhw=False)
    R.check(
        "a leakier, larger house costs more to heat",
        leaky["result"].predicted_cost > tight["result"].predicted_cost,
        f"{tight['result'].predicted_cost:.2f} vs {leaky['result'].predicted_cost:.2f}",
    )


    # ===========================================================================
    # Edge conditions
    # ===========================================================================
    R.section("Edge conditions")

    edges = {
        "very cold start": dict(
            season="winter", state={"room_temperature": 10.0,
                                    "upper_floor_temperature": 10.0,
                                    "lower_floor_temperature": 10.0,
                                    "slab_temperature": 11.0}),
        "overheated start": dict(
            season="summer", state={"room_temperature": 30.0,
                                    "upper_floor_temperature": 30.0,
                                    "lower_floor_temperature": 30.0}),
        "empty tank": dict(season="winter", state={"dhw_temperature": 10.0}),
        "boiling tank": dict(season="winter", state={"dhw_temperature": 70.0}),
        "legionella overdue": dict(
            season="winter", state={"dhw_hours_since_legionella": 400.0}),
        "collapsed comfort band": dict(
            season="winter",
            config={"min_temperature": 21.0, "target_temperature": 21.0,
                    "max_temperature": 21.0}),
        "enormous band": dict(
            season="winter",
            config={"min_temperature": 5.0, "max_temperature": 35.0}),
        "tiny pump": dict(season="winter", config={"heat_pump_max_power": 0.5}),
        "huge pump": dict(season="winter", config={"heat_pump_max_power": 40.0}),
        "tiny tank": dict(season="winter", config={"dhw_tank_volume": 20.0}),
        "enormous tank": dict(season="winter", config={"dhw_tank_volume": 2000.0}),
        "no demand windows": dict(season="winter", config={"dhw_windows": ""}),
        "all-day window": dict(season="winter", config={"dhw_windows": "00:00-24:00"}),
        "six hour horizon": dict(season="winter", hours=6),
        "48 hour horizon": dict(season="winter", hours=48),
        "negative prices": dict(season="summer_negative"),
        "external heat": dict(
            season="winter", state={"external_heat_active": True,
                                    "dhw_temperature": 60.0}),
    }

    edge_failures = 0
    for label, spec in edges.items():
        try:
            run = build_case(**spec)
        except Exception as err:  # noqa: BLE001 - a crash is the finding
            edge_failures += 1
            print(f"  FAIL {label}: raised {type(err).__name__}: {err}")
            continue
        problems = check_invariants(label, run)
        if problems:
            edge_failures += 1
            print(f"  FAIL {label}")
            for p in problems:
                print(f"         {p}")

    R.check(
        f"all {len(edges)} edge conditions produce a sound plan",
        edge_failures == 0,
        f"{edge_failures} failed",
    )

    # A pump that physically cannot keep up must still produce its best effort
    # rather than an infeasible or nonsensical plan.
    tiny = build_case(season="winter", config={"heat_pump_max_power": 0.5}, dhw=False)
    R.check(
        "an undersized pump runs flat out rather than giving up",
        float(np.mean(tiny["result"].power_schedule)) > 0.3,
        f"mean {float(np.mean(tiny['result'].power_schedule)):.3f} kW of 0.5 kW",
    )

    # Negative prices mean being paid to consume; the plan should take some.
    negative = build_case(season="summer_negative", dhw=True)
    cheapest = float(np.min(negative["result"].prices))
    if cheapest < 0:
        total = np.asarray(negative["result"].power_schedule) + np.asarray(
            negative["result"].dhw_power_schedule or 0.0
        )
        negative_steps = np.asarray(negative["result"].prices) < 0
        R.check(
            "negative prices are exploited rather than ignored",
            float(np.sum(total[negative_steps])) > 0.0,
            "nothing was consumed while being paid to consume",
        )

    # External heat must suppress discretionary electric hot water. The
    # suppression only zeroes planned DHW steps inside its 2 h coasting horizon,
    # and only where coasting on nothing would still meet the requirement — so
    # the energy it can remove is by construction DISCRETIONARY: pre-heating
    # ahead of a window, never a run the floor is forcing. The scenario has to
    # put exactly that kind of power in the first two hours, which is why the
    # guard below exists: a pair of already-hot tanks would produce
    # byte-identical plans and a check that can never fail.
    #
    # The default windows do it. START is midnight and the first window opens at
    # 06:00, so the first two hours are the night trough (0.62 SEK against a
    # 2.85 peak) and a tank three degrees under its charge limit pre-buys there
    # for the morning — 3.1 kW of it — while coasting alone still clears the
    # floor, so the fire can take all of it away.
    #
    # A window opening AT t=0 was used here until v5.1.10 and no longer works.
    # With the disinfection temperature out of `dhw_max_temp` the everyday
    # ceiling is the user's 55 °C charge limit, so a tank starting at 52 °C
    # inside a demand window has three degrees of headroom rather than eight:
    # it is already above the floor, and the plan buys later in the window
    # instead of immediately. Baseline and fire then both plan 0.00 kW in the
    # first two hours and the suppression check measures nothing — which is
    # precisely what the guard caught.
    _fire_spec = dict(season="winter")
    with_fire = build_case(
        **_fire_spec, state={"external_heat_active": True, "dhw_temperature": 52.0}
    )
    without_fire = build_case(**_fire_spec, state={"dhw_temperature": 52.0})
    _horizon_steps = int(round(2.0 / DT))
    _fire_early = float(np.sum(with_fire["result"].dhw_power_schedule[:_horizon_steps]))
    _base_early = float(
        np.sum(without_fire["result"].dhw_power_schedule[:_horizon_steps])
    )
    R.check(
        "the baseline scenario plans electric hot water inside the 2 h horizon",
        _base_early > 1e-6,
        f"only {_base_early:.2f} kW planned; the suppression check would be vacuous",
    )
    R.check(
        "an external heat source suppresses electric hot water",
        _fire_early < _base_early - 1e-6,
        f"first 2 h: {_base_early:.2f} -> {_fire_early:.2f} kW (no suppression)",
    )
    R.check(
        "suppression lowers total electric DHW energy, not just moves it",
        float(np.sum(with_fire["result"].dhw_power_schedule))
        < float(np.sum(without_fire["result"].dhw_power_schedule)) - 1e-6,
        f"{float(np.sum(without_fire['result'].dhw_power_schedule)):.2f} -> "
        f"{float(np.sum(with_fire['result'].dhw_power_schedule)):.2f}",
    )


    sys.exit(R.close("STRESS CHECKS"))
