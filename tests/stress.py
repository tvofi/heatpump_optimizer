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

import copy
import inspect
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
from heatpump_optimizer import optimizer as optimizer_module
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
#:
#: DERIVED, not chosen. Every budget in this file now sits at the GEOMETRIC
#: MIDPOINT between what the sweep costs today and the smallest regression
#: the gate is required to see (DETECTION_TARGET, below): a budget of
#: sqrt(DETECTION_TARGET) x the measured cost leaves the same ratio-margin
#: against a false failure as against missing that regression. At
#: DETECTION_TARGET = 2 the multiplier is 1.41421.
#:
#: The measurement, five consecutive runs of the sweep on one Apple M1
#: 8-core with the box verified exclusive by process count (no other
#: tests/*.py running), load1 1.56-2.60, thread factor 1.000 on every run:
#: the worst scenario is shoulder/tariff+pv+cycle at a mean 553.04x its
#: reference, sd 4.40, cv 0.80 %. 1.41421 x 553.04 = 782.11. The budget
#: therefore stands 52 standard deviations above a clean run and 37 below a
#: doubled one, and the smallest uniform regression it can see is 1.414x.
#:
#: It replaces 1400, which was sized when the two dearest scenarios cost
#: 655x and 662x. The batched jacobian then made every combination 10-20x
#: cheaper and nobody re-derived the ceiling, so by v6.3.x it stood at 2.8x
#: the worst observed cost and an injected exact 2x regression passed it
#: untouched (#287). The detection check at the end of the sweep exists so
#: that cannot happen quietly again.
SOLVE_BUDGET_RATIO = float(os.environ.get("STRESS_SOLVE_RATIO", "782.11"))

#: The whole sweep may cost this many times the reference work timed
#: alongside it. Totals average the per-scenario spread away -- and average
#: the ruler's own noise away with it, over fifty-odd samples -- so this is
#: the steadiest number the run produces: cv 0.61 % over the same five runs
#: (0.12 % against the trailing median rather than the raw samples). It is what catches a change
#: that made everything moderately slower, which is the shape a solver
#: regression usually has.
#:
#: Same derivation: 1.41421 x the measured mean of 94.9804 = 134.32, which
#: is 67 standard deviations above a clean run. The 450 it replaces came
#: with its own instruction -- "deliberately generous for a first release of
#: this check ... tighten it once a few runs' aggregate ratios are on
#: record". Five runs are now on record and this is that tightening.
#:
#: One thing this figure is NOT: a verdict on #291. This sweep ratio is
#: 94.98 against 52.67 at the round-2 baseline, and the difference is the
#: two-zone DHW solve getting 2.33x slower. Sizing the budget on today's
#: cost is correct -- today's cost is what the gate has to watch for change
#: -- but it does bake that regression into the baseline, which is why #291
#: is tracked separately and must be judged on its own evidence, not on
#: this file's silence.
SWEEP_BUDGET_RATIO = float(os.environ.get("STRESS_SWEEP_RATIO", "134.32"))

#: Backstop only: a solve this slow is pathological whatever the machine is
#: doing -- a non-converging objective, not a busy box.
SOLVE_CEILING_MS = float(os.environ.get("STRESS_SOLVE_CEILING_MS", "600000"))

#: The size of regression this gate is REQUIRED to be able to see, and the
#: reason every budget below is a measured figure rather than a comfortable
#: one. Each budget is checked against this run's own observed cost at the
#: end of the sweep (see the detection check): a budget more than this many
#: times what the run actually cost cannot detect a regression of this size,
#: and fails the run. That is the half of the question every check here used
#: to leave out -- "is it slower than the budget" was asked, "could the
#: budget ever notice" was not, and the answer was no: at 1400x/450x against
#: an observed 553x/95x the two global checks could see 2.53x at best, and
#: with #145's x3 per-scenario table the whole gate could see 2.09x. An
#: injected exact 2x tripped none of the three (#287). Together with the budget checks themselves this pins every
#: observed figure into (budget / DETECTION_TARGET, budget]; widening a
#: budget to make a red run pass now turns the run red here instead.
DETECTION_TARGET = float(os.environ.get("STRESS_DETECTION_TARGET", "2.0"))

#: Per-scenario budgets (D9-03). The single SOLVE_BUDGET_RATIO above has to
#: clear the dearest scenario in the sweep (553.04x its reference on this
#: box today, against 3.05x for the cheapest -- a 181-fold spread), which
#: means the cheapest one -- a few multiples -- could regress by three
#: orders of magnitude and still pass: exactly the hole the old absolute
#: budget had, rebuilt one level up. Each scenario therefore carries its OWN
#: budget, recorded in tests/stress_budgets.json as a clean run's ratio
#: against the reference solve (a pure work ratio: the reference is timed on
#: the same machine, in the same run, so the number travels). A scenario may
#: cost this many times its own recorded ratio.
#:
#: STAYS AT 3.0, and the attempt to tighten it is the useful part of the
#: record. On one machine this number could be 1.4142 -- the same sqrt(2)
#: derivation as the two budgets above, and over five clean consecutive
#: sweeps it would have been comfortable: the median scenario's ratio has a
#: cv of 0.44 %, the 90th percentile 0.73 %, the noisiest single scenario
#: (winter/1z/dhw) 6.04 %, and the largest deviation of any scenario from
#: its own five-run mean was +10.8 %.
#:
#: It does not survive a second machine, and the reason is not noise. CI
#: ran shoulder/tariff+cycle at 352.7x its reference against a recorded
#: 154.4x -- 2.28x the work, on a runner whose own reference solve was
#: steady at 51.4 / 52.1 / 59.3 ms over 58 samples with a thread factor of
#: 1.000 on both sides. A steady ruler and 2.3x the work means the SOLVE
#: was different: the multi-start method landed in another basin and did
#: more iterations, which floating-point differences between platforms can
#: decide. The same family swings the other way too -- against a table
#: recorded elsewhere, winter/tariff measured 1.435x its record here and
#: shoulder/tariff+cycle 0.865x.
#:
#: So a per-scenario budget cannot be both portable and under 2x: some
#: scenarios' cost is bimodal across platforms. 3.0 covers the measured
#: 2.28x with 31 % to spare. What carries the 2x detection instead is the
#: SWEEP budget, which averages the basin flips away -- 94.98x here, 77.96x
#: and 84.02x on two CI runners, all far under its 134.32 -- and that is
#: what makes the gate's smallest detectable UNIFORM regression 1.42x
#: rather than the 2.09x it was. A single scenario doubling on its own is
#: caught at 3.0x, and honestly recorded as such.
SCENARIO_BUDGET_FACTOR = float(os.environ.get("STRESS_SCENARIO_FACTOR", "3.0"))
#: ...and a scenario that has become CHEAPER than its record by more than
#: this factor makes the table stale-high: a later regression back to the
#: old cost would pass unnoticed. Like the golden-claims file, the table is
#: re-recorded deliberately (`--record-budgets`), not inherited.
SCENARIO_STALE_FACTOR = float(os.environ.get("STRESS_STALE_FACTOR", "3.0"))
#: The SINGLE-SCENARIO detection statistic (#346), measured in SOLVER WORK
#: rather than in CPU time -- and the only per-scenario number in this file
#: that is allowed to sit under DETECTION_TARGET.
#:
#: SCENARIO_BUDGET_FACTOR above cannot be tightened, and its own comment is
#: the record of why: CI ran shoulder/tariff+cycle at 2.28x its recorded
#: cost on a ruler that was steady to a millisecond, because the multi-start
#: solver landed in another basin. #371 then measured that no value of that
#: factor moves this file's detection floor at all, and closed. So a 2x
#: regression confined to ONE scenario passed the whole gate: an injected
#: 1.99x tripped 0 of 38 checks, because 1.99 < 3.0 and the sweep budget is
#: a MEAN that divides one scenario's doubling by fifty-one.
#:
#: Three CPU-denominated candidates were measured on the audit box before
#: this one, and all three failed on this box's own numbers -- the measured
#: spreads are in the PR for #346:
#:
#:   * the per-scenario CPU ratio, repeated: identical work (bit-identical
#:     objective, so the same iterates) cost 1.10x to 1.44x of itself over
#:     six consecutive solves. A 1.5x factor has 4 % of margin over that;
#:   * the same ratio normalised by the sweep's own median, which does
#:     remove the up-to-1.7x compression of the reference solve between
#:     machines: over three clean sweeps it still ranged 0.60x to 1.81x,
#:     with a run-to-run spread of 2.03x on one scenario;
#:   * CPU per solver evaluation, which cancels a basin flip but also
#:     cancels the injection the finding is written against -- calling
#:     optimize() twice doubles the evaluations with it.
#:
#: What is stable is the COUNT. The solver's evaluations are integers
#: produced by the iterate path, not by the machine: over the six repeats
#: above every scenario's count was bit-identical, spread 1.000, while its
#: CPU moved by up to 44 %. A count carries no ruler, so it cannot compress
#: between an M1 and a runner, and it cannot drift with a core's clock. That
#: is what makes a factor under DETECTION_TARGET defensible here when three
#: attempts at one in CPU were not.
#:
#: 1.5, not 1.05: the count is exact on one machine but the iterate path is
#: not identical across platforms -- floating-point differences can add or
#: drop a line-search step, which is the same mechanism that makes strict
#: golden mode non-reproducible off the recording machine (tests/README.md).
#: 1.5 leaves 50 % for that and still sees the 1.99x the finding injected;
#: the detection check below holds it under DETECTION_TARGET so it cannot be
#: widened past the thing it exists to catch.
SCENARIO_WORK_FACTOR = float(os.environ.get("STRESS_WORK_FACTOR", "1.5"))
#: How far this run's objective value may sit from the recorded one and
#: still count as the same basin, relative.
#:
#: This is the hinge, so it is worth saying what it separates. A performance
#: regression does not move the plan -- if it did the golden gate would fail
#: first, and that is a different failure with a different owner. A
#: multi-start basin flip moves it by PERCENT: a different local minimum is
#: the whole reason _multi_start_minimize exists. Between those lies the
#: last-decimal drift of the same basin re-evaluated on another platform.
#: 1e-4 sits two orders above that drift and two below a basin, so it is a
#: knife-edge in neither direction, and deliberately not 1e-9: a tolerance
#: tight enough to call float noise a basin flip would quietly empty this
#: check on the first CI runner it met.
SCENARIO_BASIN_TOLERANCE = float(
    os.environ.get("STRESS_BASIN_TOLERANCE", "1e-4")
)
#: ...and how many scenarios may drop out of the work check as flipped
#: before it is reported BLIND instead of passing on whatever is left. A
#: check that silently narrows to the scenarios that happen to still agree
#: is a check that reports success for doing nothing, which this file has
#: shipped five times. A table with no recorded fingerprints at all -- an
#: old table, or one written by a tool that does not know about the field --
#: flips every scenario and so fails here, loudly, rather than passing empty.
SCENARIO_BASIN_MAX_FLIPPED = int(
    os.environ.get("STRESS_BASIN_MAX_FLIPPED", "12")
)

#: A floor under the per-scenario budget, for a machine whose cheap
#: scenarios are noisy enough that the factor above cannot hold them.
#:
#: RETIRED to 0.0, on measurement. It was 10.0, sized against "a scenario
#: recorded at 2x is not failed for normal solver jitter at 2.5x" -- a
#: plausible worry, and false here. At 10.0 with the factor at 1.4142 the
#: floor, not the factor, would be the budget for every scenario recorded
#: below 7.07x: TEN of the fifty-one, the cheapest of them recorded at
#: 3.05x and therefore free to cost 3.3x its record before failing. That is
#: the D9-03 hole -- a budget wide enough for the dearest scenario applied
#: to the cheapest -- rebuilt at the bottom of the table. And the jitter it
#: guards against is not there: the five-run cv of those ten scenarios is
#: 0.44-5.16 %, no worse than the sweep's median, so the factor clears them
#: by eight to ninety standard deviations on its own. Cheap does not mean
#: noisy on this box; summer/1z/space, the cheapest at 3.05x, has a cv of
#: 0.45 %.
#: The knob stays, at zero, for a machine that measures otherwise -- but it
#: has to be set from a measured spread, and the detection check refuses a
#: floor that would blind a scenario to a DETECTION_TARGET-fold regression.
SCENARIO_BUDGET_FLOOR_RATIO = float(
    os.environ.get("STRESS_SCENARIO_FLOOR", "0.0")
)

#: Memory instrumentation (D9-04). tracemalloc slows allocation-heavy code,
#: so it must never run inside the timed sweep; the memory pass re-runs a
#: fixed subset of scenarios afterwards, untimed, and reports the traced
#: allocation peak and the process's RSS watermark growth. Peaks are
#: budgeted against the same recorded table, at this factor.
MEMORY_BUDGET_FACTOR = float(os.environ.get("STRESS_MEMORY_FACTOR", "1.5"))
#: How many scenarios the memory pass covers, split evenly between the two
#: recorded axes: the biggest traced allocation peaks and the biggest RSS
#: watermarks. Selected by RECORDED MEMORY, not by recorded CPU -- they are
#: nearly uncorrelated in this suite's own table, and the CPU ordering
#: happened to pick six samples of one profile while missing both extremes
#: (see the memory section for the numbers).
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


class SolverWork:
    """Counts the solver's own evaluations across one optimize() call.

    Wraps ``optimizer._scoped_minimize`` -- the single seam every L-BFGS-B
    run in the package goes through, from both the DHW and the space stage
    and from every multi-start guess -- and adds up the ``nfev``/``njev``
    scipy reports for each. Four calls per solve on the sweep's scenarios,
    so the instrument costs four Python-level function calls against
    hundreds of objective evaluations; it is measured as unchanged CPU in
    the PR for #346 rather than argued to be free.

    The candidate SCORING loop in ``_multi_start_minimize`` evaluates the
    objective directly and is therefore not counted. That is deliberate and
    harmless: it is a fixed handful of evaluations per solve, the same
    handful in the recording and in the run being judged.

    Hooking a private symbol is a coupling, so it is one that fails loudly:
    the class body below resolves it at import, so a rename stops the whole
    file rather than leaving a counter that silently reports zero -- and the
    sweep additionally refuses a scenario whose count came back zero.
    """

    _wrapped = optimizer_module._scoped_minimize

    def __init__(self) -> None:
        self.evaluations = 0
        self.calls = 0

    def __enter__(self) -> "SolverWork":
        outer = self

        def counting(*args, **kwargs):
            res = SolverWork._wrapped(*args, **kwargs)
            outer.calls += 1
            outer.evaluations += int(getattr(res, "nfev", 0) or 0)
            outer.evaluations += int(getattr(res, "njev", 0) or 0)
            return res

        optimizer_module._scoped_minimize = counting
        return self

    def __exit__(self, *exc) -> bool:
        optimizer_module._scoped_minimize = SolverWork._wrapped
        return False


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
    power_cap_kw: float | None = None,
    pin_off_steps: tuple[int, ...] | None = None,
):
    """One fully specified run of the optimizer.

    ``power_cap_kw`` supplies a flat per-step ``power_caps_extra`` -- the fuse
    guard's channel, a ceiling on space *plus* hot water -- and
    ``pin_off_steps`` supplies a manual-plan ``space_pins`` array with those
    steps forced off. Both exist so the sweep samples the ZERO-RANGE BOUND
    path (#286): the moment one variable's bound has ``lo == hi`` the batched
    jacobian is refused and scipy estimates every gradient with n scalar
    objective calls instead of three batched ones. Nothing in ``stress.py``
    or ``optimality.py`` passed either argument before, so a regression
    confined to that path was invisible to the whole gate (#287) -- not
    under-budgeted, UNSAMPLED.
    """
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

    # The zero-range-bound channels (#286/#287). Both are shipped inputs:
    # power_caps_extra is what the fuse guard and the monthly fuse advisor
    # pass, space_pins is what a manual plan passes. A flat cap below the
    # DHW run power (0.8 x p_max = 4.8 kW on the default 6 kW pump -- a 16 A
    # single-phase supply is 3.68 kW) leaves IDENTICALLY ZERO space headroom
    # at every planned DHW step, and one forced-off pin is one (0, 0) bound.
    # Either is enough to take the whole solve off the batched jacobian.
    caps_extra = None
    if power_cap_kw is not None:
        caps_extra = np.full(n, float(power_cap_kw))
    space_pins = None
    if pin_off_steps:
        space_pins = np.full(n, float("nan"))
        for _step in pin_off_steps:
            space_pins[int(_step)] = 0.0

    model = ThermalModel(params)
    optimizer = HeatPumpOptimizer(model, opt_cfg)
    # CPU time, measured here rather than taken from result.solve_time_ms,
    # which is wall clock. Wall clock counts time spent waiting for a busy
    # machine; CPU time counts work done. Measured on this box: putting
    # three extra CPU hogs on it moved a scenario's wall time 3.08x and its
    # CPU time 0.99x. Only one of those two numbers is about the code.
    work = SolverWork()
    _cpu_before = time.process_time()
    _thread_before = time.thread_time()
    with work:
        result = optimizer.optimize(
            initial, price_series, outdoor, wind, rain, solar, START, None, surplus,
            space_pins=space_pins, power_caps_extra=caps_extra,
        )
    solve_cpu_ms = (time.process_time() - _cpu_before) * 1000.0
    solve_thread_ms = (time.thread_time() - _thread_before) * 1000.0
    return {
        "result": result,
        "solve_cpu_ms": solve_cpu_ms,
        "solve_thread_ms": solve_thread_ms,
        # The machine-independent half of the cost (#346): what the solver
        # actually did, as opposed to how long this core took to do it.
        "solver_evals": work.evaluations,
        "solver_calls": work.calls,
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
        "power_caps_extra": caps_extra,
        "space_pins": space_pins,
    }


# ---------------------------------------------------------------------------
# Build each distinct scenario once
# ---------------------------------------------------------------------------
# ``build_case`` is a pure function of its arguments -- same season, same
# seeded profiles, same deterministic solve -- so asking for the same
# scenario twice buys nothing but CPU. This file asked a lot: the plain
# winter one-zone space case was built NINE times (the thermostat loop, the
# price-spread loop, four times inside the comfort-weight loop and twice
# inside the solver-noise loop, where each iteration then threw its solve
# away and re-optimized, plus `standard`), and three of the economics cases
# repeat a sweep combination exactly. None of those repeats asserted
# anything the first did not, so collapsing them gives up no coverage:
# measured, the Economics section falls from 28 solves and 13.9 s of CPU to
# 15 solves and 7.3 s.
#
# The key is the FULLY DEFAULTED argument tuple, so
# ``build_case(season="winter", two_zone=True, dhw=True, tariff=True)`` and
# the sweep's ``dict(..., tariff=True, pv=False, cycling=0.0)`` are
# recognised as the same scenario rather than missing each other over a
# default nobody wrote down.
_CASE_SIGNATURE = inspect.signature(build_case)
_case_cache: dict[tuple, dict] = {}


def case_key(spec: dict) -> tuple:
    bound = _CASE_SIGNATURE.bind(**spec)
    bound.apply_defaults()
    return tuple(sorted((k, repr(v)) for k, v in bound.arguments.items()))


def case(**spec) -> dict:
    """``build_case``, memoised on the fully defaulted arguments."""
    key = case_key(spec)
    run = _case_cache.get(key)
    if run is None:
        run = _case_cache[key] = build_case(**spec)
    return run


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

    # --- the zero-range-bound channels (#286/#287) ------------------------
    # Only meaningful when the scenario supplied them, and worth asserting
    # for their own sake: a fuse cap that the plan quietly exceeds would burn
    # the fuse, and a forced-off pin the plan quietly ignores would be the
    # optimizer overriding a manual plan without saying so. The optimizer
    # MAY release a pin to keep the house above its floor -- it says which
    # steps in manual_released_space -- so the invariant is over the steps it
    # did NOT release.
    caps_extra = run.get("power_caps_extra")
    if caps_extra is not None:
        over = float(np.max(combined - np.asarray(caps_extra)[: combined.size]))
        if over > 1e-3:
            problems.append(
                f"combined power exceeds the {float(caps_extra[0]):.2f} kW "
                f"external cap by {over:.3f} kW"
            )
    pins = run.get("space_pins")
    if pins is not None:
        released = set(result.manual_released_space)
        honoured = [
            i
            for i in range(min(len(pins), space.size))
            if float(pins[i]) == 0.0 and i not in released
        ]
        breached = [i for i in honoured if space[i] > 1e-6]
        if breached:
            problems.append(
                f"{len(breached)} forced-off space pins were neither honoured "
                f"nor reported as released (steps {breached[:4]})"
            )
        if not result.manual_pins_active:
            problems.append("manual pins were supplied but not reported active")

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
    # is only the right reference when there is no surplus. Written out on
    # the live ``pv.import_margin`` helper: the ``pv.piecewise_cost`` wrapper
    # this oracle used to call was production-dead and removed (#226), and
    # the point here is to re-derive the figure INDEPENDENTLY of the
    # optimizer's inline version anyway.
    surplus = run.get("surplus")
    if surplus is not None:
        _ref_prices = np.asarray(result.prices)
        _ref_power = np.asarray(combined, dtype=float)
        _ref_covered = np.minimum(
            _ref_power, np.asarray(surplus)[: combined.size]
        )
        _ref_margin = pv_model.import_margin(
            _ref_prices, run["config"].pv_export_price
        )
        recomputed = float(
            (np.sum(_ref_prices * _ref_power) - np.sum(_ref_margin * _ref_covered))
            * DT
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

    The floor is a per-machine escape hatch for a box whose cheap scenarios
    are noisier than the factor tolerates; it is 0.0 here because this one's
    are not (see SCENARIO_BUDGET_FLOOR_RATIO). Whenever it is non-zero it,
    not the factor, is the budget for every scenario recorded below
    floor / factor -- which is why the detection check refuses a floor that
    would let any recorded scenario reach DETECTION_TARGET times its cost.
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


def stale_cheap_verdict(observed: float, recorded: float) -> bool:
    """Has this figure fallen far enough that its record is stale-high?

    Extracted from the sweep loop so both ends of its range are exercised by
    a check rather than by the sweep happening to contain an example, and
    shared by the cost and the solver-work tables so they cannot drift
    apart. Two later groups (#288, #289) make scenarios cheaper on purpose;
    this is the rule that has to keep saying so instead of being quietly
    re-fitted around.
    """
    return observed < recorded / SCENARIO_STALE_FACTOR


def recorded_objective(table: dict, label: str) -> float | None:
    """The objective value this scenario reached when the table was recorded.

    ``None`` when the table carries no usable fingerprint for it: an older
    table, a renamed scenario, or a recording whose solve failed. Callers
    read that as "cannot tell which basin", never as "the same one".
    """
    entry = table.get(label)
    if not isinstance(entry, dict):
        return None
    value = entry.get("objective")
    if value is None:
        return None
    value = float(value)
    return value if np.isfinite(value) else None


def recorded_evals(table: dict, label: str) -> int | None:
    """How many solver evaluations this scenario took when recorded."""
    entry = table.get(label)
    if not isinstance(entry, dict):
        return None
    value = entry.get("evals")
    if value is None:
        return None
    value = int(value)
    return value if value > 0 else None


def same_basin(observed: float | None, recorded: float | None) -> bool:
    """Did this solve land in the same local minimum the recording did?

    The objective value answers it and nothing cheaper does. Cost cannot:
    that is exactly the observation that reverted the 1.4142 factor, a
    scenario costing 2.28x on a steady ruler because the plan changed. Nor
    can the evaluation count, which moves WITH the basin -- which is why it
    is the thing being judged here rather than the thing doing the judging.
    """
    if observed is None or recorded is None:
        return False
    if not (np.isfinite(observed) and np.isfinite(recorded)):
        return False
    scale = max(abs(float(recorded)), 1e-12)
    return abs(float(observed) - float(recorded)) <= SCENARIO_BASIN_TOLERANCE * scale


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


def sweep_combinations() -> list[dict]:
    """The build_case() specs the sweep runs, in order.

    A module-level function rather than a block inside ``__main__`` so
    that the checks below, and any harness re-deriving this file's
    numbers, see exactly the list the gate runs. A second, hand-copied
    list is how a budget table and the sweep it was recorded from drift
    apart without either one being wrong on its own.
    """
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

    # Zero-range bounds (#286/#287). Every scenario above leaves every
    # variable a strictly positive range, so until these three were added
    # EVERY solve in this file and in optimality.py did -- and a bound with
    # lo == hi takes a different path through the gradient.
    #
    # How much that mattered, measured here across #317 (D9-01's fix, which
    # treats a fixed variable as fixed instead of abandoning the batched
    # jacobian for scipy's scalar finite differences): the same three
    # scenarios cost 68.0x / 34.5x / 54.1x their reference at 890ecbd and
    # 7.4x / 5.5x / 4.3x at 0026f22 -- 9.0x, 6.2x and 12.4x. That is the
    # size of the thing this file could not see, and these three are still
    # the only samples of that path anywhere in the gate: if #317 is ever
    # reverted or broken they go back to costing six to twelve times their
    # recorded budget, and now something says so. Before them the class was
    # not merely under-budgeted by a global ratio, it was UNSAMPLED, and no
    # re-sizing of a global constant could have found it.
    #
    # Three scenarios, because there are three distinct producers:
    #
    #   * a flat external power cap below the DHW run power (0.8 x 6.0 kW =
    #     4.8 kW here) -- what the fuse guard and the monthly fuse advisor
    #     pass for a 16 A single-phase supply. The DHW run power is clamped
    #     to the cap and solve_space subtracts it from the same cap, so the
    #     space headroom is identically zero at every planned DHW step;
    #   * a forced-off manual pin on a two-zone DHW solve -- the production
    #     topology, one (0, 0) bound out of 96;
    #   * the same pin on a space-only solve, which reaches the (0, 0) bound
    #     through _apply_pins_to_bounds rather than through the DHW stage.
    #
    # They are deliberately the CHEAPEST members of their class (summer, one
    # zone where the shape allows): the per-scenario budget judges each
    # against its own recorded cost, so a cheap sample detects a regression
    # exactly as well as a dear one. They cost the sweep 17.2 reference
    # units -- 0.3 s of CPU -- against the ~150 the winter two-zone members
    # of the same class would, and against the 157 the same three cost
    # before #317.
    _FUSE_CAP_KW = 3.68          # 16 A x 230 V, a shipped single-phase supply
    _PIN_STEP = 90               # 22:30 on a 24 h/15 min horizon
    combinations.extend(
        [
            dict(season="summer", two_zone=False, dhw=True,
                 power_cap_kw=_FUSE_CAP_KW, label="summer/1z/dhw/fuse-cap"),
            dict(season="summer", two_zone=True, dhw=True,
                 pin_off_steps=(_PIN_STEP,), label="summer/2z/dhw/pin-off"),
            dict(season="winter", two_zone=False, dhw=False,
                 pin_off_steps=(_PIN_STEP,), label="winter/1z/space/pin-off"),
        ]
    )
    return combinations


if __name__ == "__main__":
    # ===========================================================================
    # The single-scenario detection statistic (#346)
    # ===========================================================================
    # The sweep below MEASURES; this section checks that the instrument
    # doing the measuring can see what it claims to, on synthetic tables, in
    # milliseconds. Every case is a run that actually happened somewhere and
    # is named with its number, because this file's two historical failure
    # modes are a check that cannot fail and a check that false-fails on the
    # second machine -- and the second one is what reverted the 1.4142
    # factor and closed #371.
    R.section("Single-scenario detection (#346)")

    _T = load_budget_table()
    _rec_ev = {
        label: recorded_evals(_T, label)
        for label in _T
        if isinstance(_T[label], dict)
    }
    _rec_ob = {label: recorded_objective(_T, label) for label in _rec_ev}
    R.check(
        "the committed table records a solver-work count and a basin for "
        "every scenario",
        len(_rec_ev) >= 40
        and all(v is not None for v in _rec_ev.values())
        and all(v is not None for v in _rec_ob.values()),
        f"{len(_rec_ev)} scenarios, "
        f"{sum(v is None for v in _rec_ev.values())} without a work count, "
        f"{sum(v is None for v in _rec_ob.values())} without a basin",
    )

    if any(v is None for v in _rec_ev.values()) or any(
        v is None for v in _rec_ob.values()
    ):
        # Bootstrap: a table that predates #346, or one being re-recorded
        # right now. The check above has already failed on the real table;
        # the instrument's own properties are still worth checking, so they
        # run against a synthetic stand-in rather than being skipped -- a
        # section that quietly disappears when the fixture is missing is the
        # same silence this file refuses everywhere else.
        _rec_ev = {f"synthetic/{i:02d}": 20 + 7 * i for i in range(51)}
        _rec_ob = {label: 100.0 + i for i, label in enumerate(sorted(_rec_ev))}

    def _fires(label, work_factor, objective_factor=1.0):
        """Would the sweep's work check fail this scenario, so perturbed?"""
        got = int(round(_rec_ev[label] * work_factor))
        if not same_basin(_rec_ob[label] * objective_factor, _rec_ob[label]):
            return False
        return got > _rec_ev[label] * SCENARIO_WORK_FACTOR

    _victim = "shoulder/cycle" if "shoulder/cycle" in _rec_ev else sorted(_rec_ev)[0]

    # (a) the null: an unchanged run fails nothing at all.
    R.check(
        "an unchanged sweep fires the work check on no scenario",
        not [label for label in _rec_ev if _fires(label, 1.0)],
        f"{[label for label in _rec_ev if _fires(label, 1.0)]}",
    )

    # (b) the finding itself, executed at 1.99x on one scenario. Before this
    # section existed that tripped 0 of 38 checks: 1.99 < SCENARIO_BUDGET_
    # FACTOR, and the sweep budget is a mean over fifty-one.
    R.check(
        "a 2x regression confined to one scenario is seen",
        _fires(_victim, 1.99),
        f"{_victim} at 1.99x its recorded {_rec_ev[_victim]} evaluations "
        f"did not reach the {SCENARIO_WORK_FACTOR:.2f}x factor",
    )
    R.check(
        "...and it is still under the per-scenario CPU factor, so this is "
        "the gap #346 records and not a different one",
        1.99 <= SCENARIO_BUDGET_FACTOR,
        f"1.99x against SCENARIO_BUDGET_FACTOR {SCENARIO_BUDGET_FACTOR:.2f}",
    )

    # (c) THE acceptance bar. CI ran shoulder/tariff+cycle at 352.7x its
    # recorded 154.4x -- 2.28x the work, on a runner whose own reference
    # solve was steady to a millisecond -- because the multi-start solver
    # landed in another basin. That is not a regression and must not fire.
    _flip = (
        "shoulder/tariff+cycle"
        if "shoulder/tariff+cycle" in _rec_ev
        else sorted(_rec_ev)[-1]
    )
    R.check(
        "the recorded 2.28x basin flip does not fire the work check",
        not _fires(_flip, 2.28, objective_factor=1.01),
        f"{_flip} at 2.28x the work with a 1 % different objective fired "
        "the check that exists to exempt exactly it",
    )
    R.check(
        "...and 2.28x is still inside the loose per-scenario CPU factor, so "
        "the gate stays green on it rather than exempting it twice",
        2.28 <= SCENARIO_BUDGET_FACTOR,
        f"2.28x against SCENARIO_BUDGET_FACTOR {SCENARIO_BUDGET_FACTOR:.2f}",
    )

    # The tolerance has to separate those two populations with room on both
    # sides, or it is a knife-edge wearing a constant's clothes.
    R.check(
        "the basin tolerance sits between float drift and a real flip",
        same_basin(1234.5, 1234.5 * (1.0 + 1e-9))
        and not same_basin(1234.5, 1234.5 * 1.01),
        f"tolerance {SCENARIO_BASIN_TOLERANCE:g} does not separate a 1e-9 "
        "last-decimal difference from a 1 % basin move",
    )
    R.check(
        "a missing or non-finite fingerprint is 'cannot tell', never 'agrees'",
        not same_basin(1.0, None)
        and not same_basin(None, 1.0)
        and not same_basin(float("nan"), 1.0)
        and not same_basin(1.0, float("inf")),
        "same_basin() agreed with a fingerprint it does not have",
    )

    # (d) the check may not narrow itself to whatever still agrees. A table
    # with no fingerprints exempts every scenario, and that has to be a
    # failure rather than fifty-one silent passes.
    _bare = {
        label: {"ratio": 1.0, "evals": _rec_ev[label]} for label in _rec_ev
    }
    _bare_flipped = [
        label
        for label in _bare
        if not same_basin(_rec_ob[label], recorded_objective(_bare, label))
    ]
    R.check(
        "a table with no recorded basins covers nothing, and says so",
        len(_bare_flipped) == len(_bare)
        and len(_bare_flipped) > SCENARIO_BASIN_MAX_FLIPPED,
        f"{len(_bare) - len(_bare_flipped)} scenarios still covered from a "
        f"table with no objectives, {len(_bare_flipped)} flipped against a "
        f"{SCENARIO_BASIN_MAX_FLIPPED} allowance",
    )

    # (e) the cheaper side, at both ends of its range. #288 and #289 make
    # scenarios cheaper on purpose; this rule is what stops the table being
    # silently re-fitted around them, and it now guards the work count too.
    R.check(
        "a figure more than the stale factor cheaper is still caught",
        stale_cheap_verdict(100.0 / (SCENARIO_STALE_FACTOR + 0.5), 100.0)
        and stale_cheap_verdict(4, 4 * SCENARIO_STALE_FACTOR + 4),
        f"{SCENARIO_STALE_FACTOR + 0.5:.1f}x cheaper passed the stale rule",
    )
    R.check(
        "...and one less than the stale factor cheaper is still allowed",
        not stale_cheap_verdict(100.0 / (SCENARIO_STALE_FACTOR - 0.5), 100.0)
        and not stale_cheap_verdict(100.0, 100.0),
        f"{SCENARIO_STALE_FACTOR - 0.5:.1f}x cheaper failed the stale rule",
    )

    # (f) the instrument itself, end to end: the hook has to reach the
    # solver and the count has to move with the work. A counter that reports
    # a plausible constant is the failure this file exists to refuse.
    _probe = dict(sweep_combinations()[0])
    _probe_label = _probe.pop("label")
    _plain = build_case(**_probe)
    _orig_optimize = optimizer_module.HeatPumpOptimizer.optimize

    def _twice(self, *a, **k):
        _orig_optimize(self, *a, **k)
        return _orig_optimize(self, *a, **k)

    optimizer_module.HeatPumpOptimizer.optimize = _twice
    try:
        _doubled = build_case(**_probe)
    finally:
        optimizer_module.HeatPumpOptimizer.optimize = _orig_optimize
    R.check(
        "the solver-work counter sees a real solve, and doubles with it",
        _plain["solver_evals"] > 0
        and 1.9 <= _doubled["solver_evals"] / _plain["solver_evals"] <= 2.1,
        f"{_plain['solver_evals']} evaluations plain, "
        f"{_doubled['solver_evals']} with optimize() run twice",
    )
    R.check(
        "...and the hook is restored, so nothing downstream is left wrapped",
        optimizer_module._scoped_minimize is SolverWork._wrapped,
        "SolverWork left optimizer._scoped_minimize replaced",
    )
    # ...and the loop closes: a real doubling, on a real scenario, against
    # the real recorded count, reaching the same rule the sweep applies.
    # Cases (a)-(e) are the statistic's properties; this one is the finding.
    _probe_rec = recorded_evals(_T, _probe_label)
    R.check(
        "a real 2x on one scenario reaches the rule the sweep applies",
        _probe_rec is not None
        and _plain["solver_evals"] <= _probe_rec * SCENARIO_WORK_FACTOR
        and _doubled["solver_evals"] > _probe_rec * SCENARIO_WORK_FACTOR,
        f"{_probe_label}: recorded {_probe_rec}, plain "
        f"{_plain['solver_evals']}, doubled {_doubled['solver_evals']}, "
        f"factor {SCENARIO_WORK_FACTOR:.2f}",
    )

    # ===========================================================================
    # The sweep
    # ===========================================================================
    R.section("Combination sweep")

    combinations = sweep_combinations()

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
    observed_evals: dict[str, int] = {}
    observed_objective: dict[str, float] = {}
    work_over: list[str] = []
    work_stale: list[str] = []
    work_flipped: list[str] = []
    work_unrecorded: list[str] = []
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

    # Three sweep combinations are re-solved verbatim by the economics
    # section below. The sweep's own run is kept for them -- three
    # dictionaries against the 245 reference units the three solves cost --
    # and `case()` hands it back when economics asks. Every other run is
    # dropped as before, so the sweep's memory profile is unchanged.
    # The sweep must NOT go through `case()` wholesale: it would retain all
    # fifty-one runs to save nothing, since no sweep combination repeats.
    REUSED_BY_ECONOMICS = ("winter/2z/dhw", "winter/tariff", "winter/1z/dhw")

    for combo in combinations:
        label = combo.pop("label")
        # Time the reference immediately before the solve it will judge, so the
        # ruler and the thing being measured see the same machine.
        sample_ms = calibration.sample()
        unit_ms = max(calibration.unit_ms, 1e-6)
        budget_ms = SOLVE_BUDGET_RATIO * unit_ms
        run = build_case(**combo)
        if label in REUSED_BY_ECONOMICS:
            _case_cache[case_key(combo)] = run
        solve_ms = float(run["solve_cpu_ms"])          # CPU: the load-free clock
        wall_ms = float(run["result"].solve_time_ms)   # wall: for the ceiling only
        ratio = solve_ms / unit_ms
        ratios.append((ratio, label, solve_ms, unit_ms))
        # The machine-independent channel (#346). The count is what the
        # iterate path did; the CPU above is what this core charged for it.
        evals = int(run["solver_evals"])
        observed_evals[label] = evals
        # NaN when the solve failed, which same_basin() reads as "cannot
        # tell" rather than as agreement.
        observed_objective[label] = float(run["result"].objective_value)
        sweep_reference_ms += sample_ms
        sweep_solve_ms += solve_ms
        sweep_solve_thread_ms += float(run["solve_thread_ms"])
        if record_mode:
            new_table[label] = {"ratio": round(ratio, 2), "evals": evals}
            _objective = observed_objective[label]
            if np.isfinite(_objective):
                # Ten significant figures puts the stored fingerprint six
                # orders below the 1e-4 the comparison uses, so the rounding
                # is never what decides a basin.
                new_table[label]["objective"] = float(f"{_objective:.10g}")
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
                if stale_cheap_verdict(ratio, recorded):
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

        # -- the single-scenario statistic (#346) ------------------------
        # Everything above judges a scenario's CPU against its own record
        # times a constant, and that constant has to be 3.0: it must clear
        # the most bimodal scenario on the least similar machine, so 1.99x
        # on one scenario passes it by design. This judges the SOLVER WORK
        # instead -- a count of evaluations, an integer the iterate path
        # produces and the machine does not touch -- and can therefore run
        # at a factor under DETECTION_TARGET. See SCENARIO_WORK_FACTOR for
        # the three CPU-denominated statistics measured and rejected first.
        #
        # A basin flip is the thing this must not fire on, and it is also
        # the one perturbation that moves the count without any regression:
        # a different local minimum is a different iterate path. So the
        # check applies only where the plan is unchanged, judged by the
        # objective value, and every exempted scenario is NAMED -- the blind
        # spot is a printed list rather than an average nobody can take
        # apart.
        for label in sorted(observed_evals):
            entry = budget_table.get(label)
            if not isinstance(entry, dict):
                continue
            rec_evals = recorded_evals(budget_table, label)
            if rec_evals is None:
                work_unrecorded.append(label)
                continue
            if not same_basin(
                observed_objective.get(label),
                recorded_objective(budget_table, label),
            ):
                work_flipped.append(label)
                continue
            got = observed_evals[label]
            if got > rec_evals * SCENARIO_WORK_FACTOR:
                work_over.append(
                    f"{label} took {got} solver evaluations against a "
                    f"recorded {rec_evals} = {got / rec_evals:.2f}x, over the "
                    f"{SCENARIO_WORK_FACTOR:.2f}x factor, on an unchanged "
                    f"plan (objective {observed_objective[label]:.10g})"
                )
            if stale_cheap_verdict(got, rec_evals):
                work_stale.append(
                    f"{label} took {got} solver evaluations against a "
                    f"recorded {rec_evals} (cheaper by more than "
                    f"{SCENARIO_STALE_FACTOR:.0f}x: re-record, or a "
                    f"regression back to the old work would pass unnoticed)"
                )
        _work_covered = (
            len(observed_evals) - len(work_flipped) - len(work_unrecorded)
        )
        print(
            f"  solver work: {_work_covered} of {len(observed_evals)} "
            f"scenarios judged against their recorded evaluation count at "
            f"{SCENARIO_WORK_FACTOR:.2f}x, {len(work_flipped)} exempt as "
            f"another basin"
            + (f" ({', '.join(sorted(work_flipped))})" if work_flipped else "")
        )
        R.check(
            "the solver-work counter counted something for every scenario",
            all(v > 0 for v in observed_evals.values()),
            f"{sum(1 for v in observed_evals.values() if v <= 0)} scenarios "
            "reported zero solver evaluations -- SolverWork's hook on "
            "optimizer._scoped_minimize has stopped reaching the solver, so "
            "the check below cannot fail and means nothing",
        )
        R.check(
            "every scenario has a recorded solver-work count",
            not work_unrecorded,
            f"{len(work_unrecorded)} without one: "
            f"{', '.join(work_unrecorded[:8])}"
            + (" ..." if len(work_unrecorded) > 8 else "")
            + "; run `stress.py --record-budgets` on a clean tree",
        )
        R.check(
            "no scenario's solver work grew on an unchanged plan",
            not work_over,
            "; ".join(work_over)
            + "; this is the localised-regression check -- the sweep budget "
            "is a mean over fifty-one and cannot see one scenario double, "
            "and the per-scenario CPU factor is 3.0 because bimodal "
            "scenarios need it there (#346)",
        )
        R.check(
            "no scenario's solver work fell far enough to stale its record",
            not work_stale,
            "; ".join(work_stale),
        )
        R.check(
            "the solver-work check still covers most of the sweep",
            len(work_flipped) <= SCENARIO_BASIN_MAX_FLIPPED,
            f"{len(work_flipped)} of {len(observed_evals)} scenarios solved "
            f"into a different basin than the recording and are exempt "
            f"({', '.join(sorted(work_flipped)[:8])}"
            + (" ..." if len(work_flipped) > 8 else "")
            + f"), over the {SCENARIO_BASIN_MAX_FLIPPED} allowed -- re-record "
            "the table on this machine (`stress.py --record-budgets`) rather "
            "than letting the check narrow to whatever still agrees",
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
    # Record mode probes ALL of them. Check mode probes the scenarios whose
    # RECORDED peaks are the largest -- half by traced allocation, half by
    # RSS watermark -- and this is a correction, not a refinement (#287).
    #
    # It used to probe the MEMORY_TOP_N dearest scenarios by CPU, on the
    # assumption that "the dear ones allocate the biggest trajectories".
    # The recorded table says otherwise, in this repository's own numbers:
    # the six dearest by CPU cost 2050 reference units between them and all
    # traced the same middling 1.83 MiB, while the actual leaders -- 3.47
    # MiB traced and 98.1 MiB of RSS -- cost 588. So the old selection
    # probed six samples of ONE memory profile, missed both extremes, and
    # paid tracemalloc's 3.5x more solver CPU for it: measured end to end on
    # a box with no competing test process and load1 1.74-2.10, the memory
    # pass falls from 667.7 s of child CPU to 207.0 s, which is 60 % of this
    # whole script's cost. It is also the tighter test: the traced budget is
    # recorded x1.5 + 2 MiB, which is 2.08x on a 3.47 MiB record and 2.59x
    # on an 1.83 MiB one.
    #
    # Selecting from the COMMITTED table rather than from this run's
    # measurements also makes the probe set machine-independent, which fixes
    # at the root the CI failure the old comment described: a peak recorded
    # only for this machine's own dearest six left a runner with a different
    # ordering with unrecorded scenarios (shoulder/tariff, shoulder/cycle).
    _by_cost = sorted(((r[1], r[0]) for r in ratios), key=lambda kv: -kv[1])

    def _memory_probe_labels() -> list[str]:
        """The recorded memory leaders, half on each axis, in a stable order."""
        half = max(1, MEMORY_TOP_N // 2)
        chosen: list[str] = []
        for key in ("traced_peak_mb", "rss_peak_mb"):
            ranked = sorted(
                (-float(entry[key]), label)
                for label, entry in budget_table.items()
                if isinstance(entry, dict) and float(entry.get(key, 0.0)) > 0.0
            )
            taken = 0
            for _peak, label in ranked:
                if taken >= half:
                    break
                if label in chosen:
                    continue
                chosen.append(label)
                taken += 1
        return chosen

    if record_mode:
        mem_labels = [label for label, _ in _by_cost]
    else:
        mem_labels = [
            label
            for label in _memory_probe_labels()
            if label in combos_by_label
        ]
        if not mem_labels:
            # No memory recorded yet (a first run, or a fresh table): fall
            # back to the cost ordering so the pass still says something.
            mem_labels = [label for label, _ in _by_cost[:MEMORY_TOP_N]]
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
        # The pass is only worth its CPU if it probes the scenarios that
        # actually allocate. It used to probe six samples of one middling
        # profile and miss both extremes, so this states the requirement
        # rather than trusting the selection rule to keep meeting it.
        _mem_missed: list[str] = []
        for _axis in ("traced_peak_mb", "rss_peak_mb"):
            _ranked = sorted(
                (-float(entry[_axis]), name)
                for name, entry in budget_table.items()
                if isinstance(entry, dict) and float(entry.get(_axis, 0.0)) > 0.0
            )
            if _ranked and _ranked[0][1] not in mem_labels:
                _mem_missed.append(
                    f"{_axis}: the recorded maximum is {_ranked[0][1]} at "
                    f"{-_ranked[0][0]:.2f} and it was not probed"
                )
        R.check(
            "the memory pass probes the recorded peak on each axis",
            not _mem_missed,
            "; ".join(_mem_missed)
            + "; the pass exists to watch the biggest allocators, so it has "
            "to include them",
        )
        R.check(
            "the probed scenarios' memory peaks stay within their "
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

    # -- can the budgets SEE a regression? (#287) -------------------------
    # The other half of every check above. They ask whether the run exceeded
    # its budget; this one asks whether the budget sits close enough to the
    # observed cost to be capable of noticing. A budget nobody re-derives
    # drifts away from the code it guards -- the two global ones were sized
    # when the dearest scenario cost 655x, the batched jacobian made every
    # combination 10-20x cheaper, and nothing brought them back down -- and a
    # gate that cannot fail is not a gate.
    # It is judged against the RECORDED table, not against this run's own
    # observation, and that distinction was executed rather than reasoned.
    # The first version of this check compared the budgets to the run's own
    # figures; it passed here and FAILED on CI, because the ratio itself
    # does not travel. On the M1 the reference solve is 18.1 ms and the
    # dearest scenario 10056 ms -- a ratio of 553x. On a GitHub runner the
    # same scenario costs 10846 ms (1.08x more) against a 33.5 ms reference
    # (1.85x more), a ratio of 324x. The runner is disproportionately slow
    # at the tiny 96-element reference, so every ratio COMPRESSES by up to
    # 1.7x there. A budget is a property of the recording; an observation is
    # a property of the machine, and judging the first by the second is
    # exactly the false failure this file's whole design exists to avoid.
    # Both figures are printed below so a reader sees the machine's own
    # headroom too -- and note what that compression costs: where the table
    # detects a 1.41x regression on the machine it was recorded on, it
    # detects 1.5-2.4x on a runner whose ratios compress. Re-record there if
    # that matters.
    _recorded = [
        float(entry["ratio"])
        for entry in budget_table.values()
        if isinstance(entry, dict) and float(entry.get("ratio", 0.0)) > 0.0
    ]
    _rec_worst = max(_recorded) if _recorded else _worst[0]
    _rec_sweep = sum(_recorded) / len(_recorded) if _recorded else _sweep_ratio
    _blind: list[str] = []
    if SOLVE_BUDGET_RATIO >= DETECTION_TARGET * _rec_worst:
        _blind.append(
            f"the per-scenario ceiling is {SOLVE_BUDGET_RATIO:.0f}x against a "
            f"dearest recorded {_rec_worst:.1f}x: it cannot see a "
            f"{SOLVE_BUDGET_RATIO / max(_rec_worst, 1e-9):.2f}x regression, "
            f"let alone a {DETECTION_TARGET:.0f}x one"
        )
    if SWEEP_BUDGET_RATIO >= DETECTION_TARGET * _rec_sweep:
        _blind.append(
            f"the sweep budget is {SWEEP_BUDGET_RATIO:.0f}x against a recorded "
            f"mean of {_rec_sweep:.2f}x: it cannot see a "
            f"{SWEEP_BUDGET_RATIO / max(_rec_sweep, 1e-9):.2f}x regression"
        )
    # The per-scenario factor is NOT held to DETECTION_TARGET, and that is a
    # measured concession rather than a comfortable one: some scenarios' cost
    # is bimodal across platforms (see SCENARIO_BUDGET_FACTOR), so a factor
    # under 2 false-fails on a runner where the solver picks another basin.
    # What must see a DETECTION_TARGET-fold UNIFORM regression is the gate as
    # a whole -- in practice the sweep budget, which averages basin flips
    # away. The floor, though, may never be looser than the factor: that
    # would rebuild D9-03's hole at the bottom of the table, where a budget
    # sized for the dearest scenario gets applied to the cheapest.
    _floor_blind = [
        (label, float(entry["ratio"]))
        for label, entry in budget_table.items()
        if isinstance(entry, dict)
        and float(entry.get("ratio", 0.0)) > 0.0
        and SCENARIO_BUDGET_FLOOR_RATIO
        > SCENARIO_BUDGET_FACTOR * float(entry["ratio"])
    ]
    if _floor_blind:
        _worst_floored = min(_floor_blind, key=lambda kv: kv[1])
        _blind.append(
            f"the per-scenario floor is {SCENARIO_BUDGET_FLOOR_RATIO:.2f}x and "
            f"is looser than the {SCENARIO_BUDGET_FACTOR:.2f}x factor for "
            f"{len(_floor_blind)} scenario(s) -- {_worst_floored[0]} is "
            f"recorded at {_worst_floored[1]:.2f}x and could reach "
            f"{SCENARIO_BUDGET_FLOOR_RATIO / _worst_floored[1]:.1f}x its cost "
            f"before failing, against the "
            f"{SCENARIO_BUDGET_FACTOR:.1f}x every other scenario gets"
        )
    print(
        f"  detection against the RECORDED costs: per-scenario ceiling "
        f"{SOLVE_BUDGET_RATIO / max(_rec_worst, 1e-9):.2f}x, sweep budget "
        f"{SWEEP_BUDGET_RATIO / max(_rec_sweep, 1e-9):.2f}x, per-scenario "
        f"table {SCENARIO_BUDGET_FACTOR:.2f}x -- the smallest of those is the "
        f"smallest UNIFORM regression this gate can see where it was "
        f"recorded; a regression confined to one scenario is seen at "
        f"{SCENARIO_WORK_FACTOR:.2f}x of that scenario's recorded solver "
        f"work instead, and in nothing denominated in CPU"
    )
    print(
        f"  detection on THIS machine: per-scenario ceiling "
        f"{SOLVE_BUDGET_RATIO / max(_worst[0], 1e-9):.2f}x, sweep budget "
        f"{SWEEP_BUDGET_RATIO / max(_sweep_ratio, 1e-9):.2f}x -- these move "
        f"with the machine because the reference solve does not scale with "
        f"the real ones (measured 1.7x of ratio compression between an M1 "
        f"and a CI runner); re-record here to get the figures above"
    )
    _smallest = min(
        SOLVE_BUDGET_RATIO / max(_rec_worst, 1e-9),
        SWEEP_BUDGET_RATIO / max(_rec_sweep, 1e-9),
        SCENARIO_BUDGET_FACTOR,
    )
    if _smallest >= DETECTION_TARGET:
        _blind.append(
            f"the smallest uniform regression any budget could see is "
            f"{_smallest:.2f}x, against a required {DETECTION_TARGET:.0f}x"
        )
    # The other half of the same question, and the one #346 was opened on:
    # what is the smallest regression this gate sees when it is confined to
    # ONE scenario? Not the min() above. Its sweep term is a mean over
    # fifty-one, so a single scenario's doubling reaches it divided by
    # fifty-one, and its per-scenario term is 3.0 for reasons no code change
    # can move -- #371 measured the min() at 1.420 for every value of that
    # factor from 3.0 to 100.0 and closed on it, which is what a decorative
    # check looks like. It is SCENARIO_WORK_FACTOR, and that constant IS
    # free to be tightened, so this check can bind on it.
    if SCENARIO_WORK_FACTOR >= DETECTION_TARGET:
        _blind.append(
            f"a regression confined to ONE scenario is invisible below "
            f"{SCENARIO_WORK_FACTOR:.2f}x of its recorded solver work, "
            f"against a required {DETECTION_TARGET:.0f}x"
        )
    R.check(
        f"the budgets are tight enough to see a {DETECTION_TARGET:.0f}x "
        "regression, uniform or confined to one scenario",
        not _blind,
        "; ".join(_blind)
        + "; re-derive the budgets from a measured quiet run "
        "(tests/stress.py prints its own figures) rather than widening them",
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
        run = case(season=season, two_zone=False, dhw=False)
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
    flat = case(season="flat", two_zone=False, dhw=False)
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
        run = case(season=season, two_zone=False, dhw=False)
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
    # One case, four re-optimizations. It used to build the case inside the
    # loop, which solved it a fifth, sixth, seventh and eighth time and read
    # none of those four results -- the loop wants the case's model, config
    # and inputs, never its plan. The config is COPIED rather than mutated
    # in place: it is now shared with every other user of this scenario, and
    # leaving comfort_weight at 40 behind would silently change them.
    comfort_curve = []
    _comfort_base = case(season="winter", two_zone=False, dhw=False)
    for weight in (5.0, 10.0, 20.0, 40.0):
        run = _comfort_base
        weighted = copy.copy(run["config"])
        weighted.comfort_weight = weight
        optimizer = HeatPumpOptimizer(run["model"], weighted)
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
        # Same case both times, by construction: the wobble is the only
        # thing that differs, which is the whole point of the measurement.
        # Rebuilding it inside the loop also re-solved it twice over,
        # unread.
        run = case(season="winter", two_zone=False, dhw=False)
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
    plain = case(season="winter", two_zone=True, dhw=True)
    tariffed = case(season="winter", two_zone=True, dhw=True, tariff=True)
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
    smooth = case(season="winter", two_zone=False, dhw=True, cycling=3.0)
    rough = case(season="winter", two_zone=False, dhw=True, cycling=0.0)
    R.check(
        "a cycling cost reduces compressor starts",
        smooth["result"].compressor_starts <= rough["result"].compressor_starts,
        f"{rough['result'].compressor_starts} -> {smooth['result'].compressor_starts}",
    )

    # PV surplus must pull consumption into the surplus hours.
    sunny = case(season="shoulder", two_zone=False, dhw=True, pv=True)
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
    efficient = case(season="winter", two_zone=False, dhw=False, cop_scale=1.4)
    standard = case(season="winter", two_zone=False, dhw=False, cop_scale=1.0)


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
    tight = case(season="winter", building="light_new", dhw=False)
    leaky = case(season="winter", building="heavy_old", dhw=False)
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
            run = case(**spec)
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
    tiny = case(season="winter", config={"heat_pump_max_power": 0.5}, dhw=False)
    R.check(
        "an undersized pump runs flat out rather than giving up",
        float(np.mean(tiny["result"].power_schedule)) > 0.3,
        f"mean {float(np.mean(tiny['result'].power_schedule)):.3f} kW of 0.5 kW",
    )

    # Negative prices mean being paid to consume; the plan should take some.
    negative = case(season="summer_negative", dhw=True)
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
    with_fire = case(
        **_fire_spec, state={"external_heat_active": True, "dhw_temperature": 52.0}
    )
    without_fire = case(**_fire_spec, state={"dhw_temperature": 52.0})
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
