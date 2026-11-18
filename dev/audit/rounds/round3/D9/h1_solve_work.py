"""D9 round 3 / H1 -- how much simulation one coordinator cycle buys.

METRIC (one line each, from tools/audit/briefs/D9.md):
  full_solves_per_cycle   = entries into optimizer._multi_start_minimize during
                            one coordinator cycle, split by the coordinator
                            method on the stack (main solve / shadow / other).
  step_equivalents        = scalar ThermalModel.simulate_step calls + ROWS of
                            ThermalModel.simulate_trajectory_batch, both hooked
                            by monkeypatching the production symbols.
  steps_per_gradient      = step_equivalents attributable to one evaluation of
                            the jac supplied to L-BFGS-B (_batch_fd_gradient),
                            i.e. total batch rows / _batch_fd_gradient calls.

COMMAND (from the repository root, nothing else needed):
  PYTHONPATH=tests/hastub python3 tools/audit/round3/D9/h1_solve_work.py

EXPECTED (baseline ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1, 8-core Apple M1,
python 3.11.5 / numpy 2.4.6 / scipy 1.17.1). All exact counts, +-0 on a re-run
of the same tree -- they are contention-immune:
  cycle.optimize_calls              = 1
  cycle.multi_start_entries         = 2      (space stage + _co_optimize re-solve)
  cycle.step_equivalents            = 22944
  cycle.steps_per_gradient          = 96     (one batch row per free variable)
  flat.step_equivalents             = 46560  NULL CONTROL (flat price profile)
  single_zone_nodhw.step_equivalents= 19872
  fuse_first_cycle.optimize_calls   = 2      <- the shadow solve, D9-02
  fuse_first_cycle.step_equivalents = 45888
  fuse_rate_limited.optimize_calls  = 1
  fuse_rate_limited.step_equivalents= 22944  (exactly half: 2.000x)
  fuse_first_cycle_flat / fuse_rate_limited_flat = 93120 / 46560 (also 2.000x)

PERTURBATION: HPO_D9_MAXITER=<n> lowers L-BFGS-B's maxiter through
optimizer._multi_start_minimize's default; step_equivalents must fall and
multi_start_entries must not.  HPO_D9_HORIZON=<hours> shortens the horizon;
step_equivalents must fall.

Counts and rows are contention-immune; no timing number is reported here.
"""
from __future__ import annotations

import asyncio
import os
import sys
import traceback

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round3", "D9"))
import d9lib  # noqa: E402  (thread pin lives here, before numpy)
from d9lib import result, telemetry  # noqa: E402

from heatpump_optimizer import optimizer as OPT  # noqa: E402
from heatpump_optimizer import coordinator as C  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel  # noqa: E402

MAXITER = os.environ.get("HPO_D9_MAXITER")
HORIZON = os.environ.get("HPO_D9_HORIZON")

COORD_TAGS = (
    "async_run_optimization",
    "_maybe_run_fuse_advisor",
    "_maybe_refresh_price_tile",
    "_run_system_identification",
    "async_simulate_plan",
    "diagnose_record",
)


class Counters:
    def __init__(self) -> None:
        self.steps = 0
        self.batch_rows = 0
        self.batch_calls = 0
        self.grad_calls = 0
        self.multi_start = 0
        self.optimize = 0
        self.by_path: dict[str, int] = {}

    def snapshot(self) -> dict:
        return dict(self.__dict__, by_path=dict(self.by_path))


def install(counters: Counters):
    """Hook the four production symbols. Returns a restore callable."""
    o_step = ThermalModel.simulate_step
    o_batch = ThermalModel.simulate_trajectory_batch
    o_ms = OPT._multi_start_minimize
    o_grad = OPT._batch_fd_gradient
    o_opt = OPT.HeatPumpOptimizer.optimize

    def step(self, *a, **k):
        counters.steps += 1
        return o_step(self, *a, **k)

    def batch(self, initial_state, power_matrix, *a, **k):
        counters.batch_calls += 1
        counters.batch_rows += int(len(power_matrix))
        return o_batch(self, initial_state, power_matrix, *a, **k)

    def multi_start(*a, **k):
        counters.multi_start += 1
        stack = [f.name for f in traceback.extract_stack()]
        tag = next((t for t in COORD_TAGS if t in stack), "other")
        counters.by_path[tag] = counters.by_path.get(tag, 0) + 1
        if MAXITER:
            k["maxiter"] = int(MAXITER)
        return o_ms(*a, **k)

    def grad(*a, **k):
        counters.grad_calls += 1
        return o_grad(*a, **k)

    def optimize(self, *a, **k):
        counters.optimize += 1
        return o_opt(self, *a, **k)

    ThermalModel.simulate_step = step
    ThermalModel.simulate_trajectory_batch = batch
    OPT._multi_start_minimize = multi_start
    OPT._batch_fd_gradient = grad
    OPT.HeatPumpOptimizer.optimize = optimize
    C._multi_start_minimize = getattr(C, "_multi_start_minimize", None)

    def restore():
        ThermalModel.simulate_step = o_step
        ThermalModel.simulate_trajectory_batch = o_batch
        OPT._multi_start_minimize = o_ms
        OPT._batch_fd_gradient = o_grad
        OPT.HeatPumpOptimizer.optimize = o_opt

    return restore


def neutralise_fetch(coord):
    """The three network fetches only fill the arrays this harness injected."""

    async def _noop(*a, **k):
        return None

    coord._fetch_tibber_prices = _noop
    coord._fetch_weather_forecast = _noop
    coord._fetch_solar_forecast = _noop
    coord._async_learn_price_shape = _noop


FUSE_CFG = {
    "fuse_guard_enabled": True,
    "main_fuse_amperes": 20,
    "main_fuse_phases": 3,
    "peak_tariff_enabled": True,
    "peak_tariff_price_per_kw": 45.0,
}


def run_cycle(profile: str, extra=None, *, advisor_ran=False) -> Counters:
    hass, coord = d9lib.build_coordinator(extra, profile=profile)
    if advisor_ran:
        # The state a persisted rate-limit would restore after a restart:
        # "the advisor ran just now, and for this month".
        from homeassistant.util import dt as dt_util
        from heatpump_optimizer.coordinator import month_key

        now = dt_util.now()
        coord._fuse_advisor_at = now
        coord._fuse_advisor = {"month": month_key(now), "candidate_kw": 1.0}
    if HORIZON:
        coord._opt_config.horizon_hours = float(HORIZON)
    neutralise_fetch(coord)
    restore_inline = d9lib.inline_solves()
    counters = Counters()
    restore = install(counters)
    try:
        asyncio.run(coord._async_update_data())
    finally:
        restore()
        restore_inline()
    return counters


def report(prefix: str, c: Counters) -> None:
    equiv = c.steps + c.batch_rows
    result(f"{prefix}.multi_start_entries", c.multi_start, "count")
    result(f"{prefix}.optimize_calls", c.optimize, "count")
    for tag, n in sorted(c.by_path.items()):
        result(f"{prefix}.multi_start_via_{tag}", n, "count")
    result(f"{prefix}.step_equivalents", equiv, "count")
    result(f"{prefix}.scalar_simulate_step", c.steps, "count")
    result(f"{prefix}.batch_rows", c.batch_rows, "count")
    result(f"{prefix}.batch_calls", c.batch_calls, "count")
    result(f"{prefix}.gradient_evaluations", c.grad_calls, "count")
    if c.grad_calls:
        result(
            f"{prefix}.steps_per_gradient", c.batch_rows / c.grad_calls, "count"
        )
    if c.multi_start:
        result(
            f"{prefix}.step_equivalents_per_multi_start",
            equiv / c.multi_start,
            "count",
        )


def main() -> None:
    result("baseline_sha", "ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1", "sha")
    result("maxiter_override", MAXITER or "none", "enum")
    result("horizon_override", HORIZON or "none", "enum")

    print("-- default install, one full coordinator cycle", flush=True)
    report("cycle", run_cycle("tibber_like"))

    print("-- NULL CONTROL: flat price profile, same cycle", flush=True)
    report("flat", run_cycle("flat"))

    print("-- single zone, no DHW", flush=True)
    report("single_zone_nodhw", run_cycle_nodhw())

    print("-- fuse guard on, FIRST cycle after a restart (advisor guard is None)",
          flush=True)
    report("fuse_first_cycle", run_cycle("tibber_like", extra=FUSE_CFG))

    print("-- the same install with the advisor rate-limit already satisfied",
          flush=True)
    report(
        "fuse_rate_limited",
        run_cycle("tibber_like", extra=FUSE_CFG, advisor_ran=True),
    )

    print("-- NULL CONTROL: the same pair at a flat price profile", flush=True)
    report("fuse_first_cycle_flat", run_cycle("flat", extra=FUSE_CFG))
    report(
        "fuse_rate_limited_flat",
        run_cycle("flat", extra=FUSE_CFG, advisor_ran=True),
    )

    telemetry()


def run_cycle_nodhw() -> Counters:
    hass, coord = d9lib.build_coordinator(None, profile="tibber_like", dhw=False)
    neutralise_fetch(coord)
    restore_inline = d9lib.inline_solves()
    counters = Counters()
    restore = install(counters)
    try:
        asyncio.run(coord._async_update_data())
    finally:
        restore()
        restore_inline()
    return counters


if __name__ == "__main__":
    main()
