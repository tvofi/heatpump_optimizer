"""D9 round 4 / H2 -- what one coordinator cycle costs, and where.

METRICS (D9.md, verbatim):
  * "Full solves per cycle" = entries into
    ``heatpump_optimizer.optimizer:_multi_start_minimize`` during one
    coordinator cycle, split by path (main solve / shadow / diagnose / other).
  * "Loop-thread work per cycle" = ``time.thread_time()`` measured ON THE
    EVENT-LOOP THREAD across one ``_async_update_data``, minus nothing --
    the solve is pushed through a REAL ``ThreadPoolExecutor`` (never
    FakeHass's inline executor), so executor CPU does not land in it.
  * Executor-thread CPU per cycle is reported beside it.

The hass object is ``tests/harness.py:FakeHass`` with ONE override:
``async_add_executor_job`` dispatches to a real ThreadPoolExecutor on the
running loop. Network fetches (`_fetch_tibber_prices`,
`_fetch_weather_forecast`, `_fetch_solar_forecast`) are replaced by no-ops
and the price/weather series are pre-seeded exactly as
``tests/golden.py:_capture_coordinator`` seeds them, so the cycle measures
computation and not a socket.

COMMAND (from the repository root):

    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
      python3 tools/audit/round4/D9/h2_cycle.py

EXPECTED (re-recorded at ad7bcdf 2026-09-14, #950; the 7dd68dd bands are
kept below as the finding's frozen record):
  msm_entries_per_cycle = 0 (+/- 0) -- the shipped route is entirely
  out-of-process (#199/#290), so the parent never enters
  ``_multi_start_minimize`` (round 4's own non-finding 3; the old band of
  1 was a draft expectation the runs never printed);
  loop_thread_cpu_ms_per_cycle 2 - 6 ms (provisional, +/- 30 %);
  executor_cpu_ms per cycle 0.1 - 1 ms (provisional) -- the old band of
  1200 - 2500 ms conflated the solve WALL with executor CPU: the parent's
  executor only ferries the pickled job to the child interpreter, and the
  finder's own report measured 0.28 ms/cycle at 7dd68dd;
  thread_factor (the residual defined below) <= 1.05;
  whole_run_process_over_thread_ratio 1.1 - 1.5, ABOVE the contract's
  1.05 bar by construction -- see the telemetry note.

FINAL RESULT (exact; #1005 review follow-up -- with the live-header
marker below, tests/harness_headers.py executes this harness and
compares this line to the run):
    RESULT msm_entries_per_cycle=0
That count is the only FINAL number under a checker-readable name: the
CPU milliseconds are PROVISIONAL and thread_factor is in the checker's
SKIP set, both by design.

live-header: this header is maintained against the tree; harness_headers.py executes it.

TELEMETRY NOTE (#950, round 4 D9-INST): this harness deliberately pushes
real work through a REAL ``ThreadPoolExecutor`` (the FakeHass trap in
tools/audit/README.md demands it), so ``process_time/thread_time`` over
the whole run can never come under 1.05: the executor thread's honest CPU
-- the job ferry plus the futures plumbing around it, measured 3.3 ms
against 0.19 ms inside the wrapped jobs themselves -- lands in
``process_time`` and not in ``thread_time`` by construction. The printed
``thread_factor`` is therefore the RESIDUAL ``(process_cpu -
executor_thread_cpu)/thread_cpu`` the contract's bar actually scopes to,
with ``main_thread_cpu_s`` and ``executor_thread_cpu_s`` printed beside it
so the decomposition is auditable; the bare whole-run ratio is kept under
its own name.

PERTURBATION: ``H2_CYCLES=3`` changes nothing per cycle (idempotence
control); ``H2_PERTURB=nosolve`` sets mode OFF so no solve runs -- the
executor CPU must collapse to ~0 and msm_entries to 0, while the loop
thread work must stay within a factor of 2. That separates loop work from
solve work.

Counts are contention-immune; CPU milliseconds are PROVISIONAL.
"""
from __future__ import annotations

import os

for _t in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_t, "1")

import asyncio  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
import traceback  # noqa: E402
from concurrent.futures import ThreadPoolExecutor  # noqa: E402
from datetime import timedelta  # noqa: E402

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round4", "D9"))

import d9common as C  # noqa: E402

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import optimizer as OPT  # noqa: E402
from heatpump_optimizer import thermal_model as TM  # noqa: E402
from heatpump_optimizer.coordinator import (  # noqa: E402
    HeatPumpOptimizerCoordinator,
)

CYCLES = int(os.environ.get("H2_CYCLES", "3"))
PERTURB = os.environ.get("H2_PERTURB", "")

STATE = {"msm": 0, "scalar": 0, "batch_rows": 0}
PATHS = {}
EXEC_CPU = {"total": 0.0}
# The executor thread's own thread_time at its first job entry and its
# last job exit: the span covers the futures plumbing around the wrapped
# jobs too, which the per-job wrapper above deliberately does not count.
# That span -- not the per-job total -- is what the residual thread_factor
# subtracts (see the telemetry note in the header, #950 D9-INST).
EXEC_SPAN = {"first": None, "last": None}


class RealExecHass(FakeHass):
    """FakeHass with a REAL executor boundary (README trap: the stock one
    runs inline on the calling thread and would measure nothing)."""

    def __init__(self, states=None):
        super().__init__(states)
        self.pool = ThreadPoolExecutor(max_workers=1)

    async def async_add_executor_job(self, func, *args):
        loop = asyncio.get_running_loop()

        def timed():
            t0 = time.thread_time()
            if EXEC_SPAN["first"] is None:
                EXEC_SPAN["first"] = t0
            try:
                return func(*args)
            finally:
                EXEC_SPAN["last"] = time.thread_time()
                EXEC_CPU["total"] += time.thread_time() - t0

        return await loop.run_in_executor(self.pool, timed)


def install():
    orig_step = TM.ThermalModel.simulate_step
    orig_batch = TM.ThermalModel.simulate_trajectory_batch

    def step(self, *a, **kw):
        STATE["scalar"] += 1
        return orig_step(self, *a, **kw)

    def batch(self, initial_state, power_matrix, *a, **kw):
        import numpy as np

        m = np.asarray(power_matrix)
        STATE["batch_rows"] += int(m.shape[0]) if m.ndim == 2 else 1
        return orig_batch(self, initial_state, power_matrix, *a, **kw)

    TM.ThermalModel.simulate_step = step
    TM.ThermalModel.simulate_trajectory_batch = batch

    orig_msm = OPT._multi_start_minimize

    def msm(*a, **kw):
        STATE["msm"] += 1
        names = [f.name for f in traceback.extract_stack()]
        for probe in (
            "async_run_optimization",
            "async_simulate",
            "diagnose_record",
            "_optimize_with_dhw",
            "_optimize_space_only",
        ):
            if probe in names:
                PATHS[probe] = PATHS.get(probe, 0) + 1
        return orig_msm(*a, **kw)

    OPT._multi_start_minimize = msm
    # coordinator.py imported optimize_in_process by name; the solve runs
    # through HeatPumpOptimizer.optimize either way, so patching the module
    # symbol above is enough.


def build_coordinator():
    hass = RealExecHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    cfg = {
        const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
        const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
        const.CONF_DHW_TANK_VOLUME: 180.0,
        "tibber_token": "x",
        "weather_entity": "weather.home",
        "target_temperature": 21.0,
        "min_temperature": 17.0,
        "max_temperature": 23.0,
        "upper_floor_thermal_mass": 3.0,
        "lower_floor_thermal_mass": 8.0,
        "upper_floor_heat_loss": 0.08,
        "lower_floor_heat_loss": 0.07,
    }
    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=cfg))
    start = C.START
    coord._prices = [
        {
            "total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
            "starts_at": (start + timedelta(hours=h)).isoformat(),
            "level": "NORMAL",
        }
        for h in range(48)
    ]
    coord._weather_forecast = [
        {
            "datetime": (start + timedelta(hours=h)).isoformat(),
            "temperature": -5.0 + 3.0 * (h % 24) / 24.0,
            "wind_speed": 3.0,
            "precipitation": 0.0,
            "humidity": 85.0,
        }
        for h in range(48)
    ]
    coord._solar_radiation_forecast = [
        max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)
    ]

    async def _noop(*a, **kw):
        return None

    coord._fetch_tibber_prices = _noop
    coord._fetch_weather_forecast = _noop
    coord._fetch_solar_forecast = _noop
    coord._skip_solve_once = False
    if PERTURB == "nosolve":
        coord._mode = const.MODE_OFF
    return coord


async def amain():
    install()
    coord = build_coordinator()
    dt_util.freeze(C.START)
    rows = []
    try:
        for i in range(CYCLES):
            for k in STATE:
                STATE[k] = 0
            PATHS.clear()
            EXEC_CPU["total"] = 0.0
            loop_t0 = time.thread_time()
            w0 = time.perf_counter()
            data = await coord._async_update_data()
            wall = time.perf_counter() - w0
            loop_cpu = time.thread_time() - loop_t0
            rows.append(
                dict(
                    i=i,
                    msm=STATE["msm"],
                    equiv=STATE["scalar"] + STATE["batch_rows"],
                    loop_ms=loop_cpu * 1e3,
                    exec_ms=EXEC_CPU["total"] * 1e3,
                    wall=wall,
                    keys=len(data or {}),
                    paths=dict(PATHS),
                )
            )
    finally:
        dt_util.freeze(None)
    return rows


def main():
    print(f"# baseline=7dd68dd  perturb={PERTURB or 'none'}  cycles={CYCLES}")
    print(f"# procs_at_start={C.concurrent_procs()} load1={C.load1():.2f}")
    p0, t0 = time.process_time(), time.thread_time()
    rows = asyncio.run(amain())
    proc, thr = time.process_time() - p0, time.thread_time() - t0
    for r in rows:
        C.result(f"cycle{r['i']}.msm_entries", r["msm"], "entries")
        C.result(f"cycle{r['i']}.paths", r["paths"])
        C.result(f"cycle{r['i']}.simulate_equivalents", r["equiv"], "steps")
        C.result(f"cycle{r['i']}.loop_thread_cpu_ms_PROVISIONAL",
                 float(r["loop_ms"]), "ms")
        C.result(f"cycle{r['i']}.executor_cpu_ms_PROVISIONAL",
                 float(r["exec_ms"]), "ms")
        total = r["loop_ms"] + r["exec_ms"]
        C.result(
            f"cycle{r['i']}.loop_share_pct",
            float(100.0 * r["loop_ms"] / total) if total else float("nan"),
            "pct",
        )
        C.result(f"cycle{r['i']}.wall_s_PROVISIONAL", float(r["wall"]), "s")
        C.result(f"cycle{r['i']}.data_keys", r["keys"], "keys")
    steady = rows[1:] or rows
    C.result("msm_entries_per_cycle",
             sum(r["msm"] for r in steady) / len(steady), "entries")
    C.result("loop_thread_cpu_ms_per_cycle_PROVISIONAL",
             float(sum(r["loop_ms"] for r in steady) / len(steady)), "ms")
    C.result("executor_cpu_ms_per_cycle_PROVISIONAL",
             float(sum(r["exec_ms"] for r in steady) / len(steady)), "ms")
    # The decomposition the contract's bar needs on an executor-crossing
    # harness (#950 D9-INST): whole-run ratio kept under its own name, the
    # deliberate thread's CPU printed beside the residual factor.
    exec_total = ((EXEC_SPAN["last"] - EXEC_SPAN["first"])
                  if EXEC_SPAN["first"] is not None else 0.0)
    C.result("main_thread_cpu_s_PROVISIONAL", float(thr), "s")
    C.result("executor_thread_cpu_s_PROVISIONAL", float(exec_total), "s")
    C.result("whole_run_process_over_thread_ratio",
             float(proc / thr) if thr > 0 else float("nan"))
    C.telemetry((proc - exec_total) / thr if thr > 0 else float("nan"))


if __name__ == "__main__":
    main()
