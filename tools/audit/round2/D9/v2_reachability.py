"""Verifier seat 2, panel D9: production reachability and consequence.

Independent metrics, none of them the finder's:

A. ``scalar_path_rate`` -- of the ``_multi_start_minimize`` entries a REAL
   coordinator cycle makes (FakeHass + a real ThreadPoolExecutor boundary,
   the production ``_async_update_data`` path), the fraction whose bounds
   carry at least one ``lo >= hi`` entry, i.e. that fall to scipy's scalar
   finite-difference gradient. Reported per config: default, the opt-in
   fuse guard at plausible Swedish fuse sizes, the learned capacity
   envelope, and one ``apply_manual_plan`` override built by production's
   own ``build_override``. This asks D9-01's reachability question against
   the coordinator, not against a hand-built bounds vector.

B. ``golden_scalar_scenarios`` -- of the committed golden plan fixtures,
   which are solved on the scalar path TODAY, with each one's
   ``simulate_step`` count. A population count, not a constructed case.

C. ``f0_x_identity`` -- of the jac evaluations on a batched solve, the
   fraction whose internal ``objective(x)`` (the f0 the batched gradient
   needs) is called at an ``x`` byte-identical to the objective call
   scipy made immediately before it. This is D9-03's premise: if scipy
   evaluates f at a different point than the jac's f0, no memo helps.

D. ``planner_share_1hook`` -- D9-04's planner share of solve CPU measured
   with ONE wrapper (``_build_dhw_requirements``, entered twice per solve)
   instead of the finder's seven, so the ``compute_cop_dhw`` counter that
   fires 14,168 times cannot inflate it.

Command (from the repository root):
    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub \
    python tools/audit/round2/D9/v2_reachability.py

Expected (baseline c398fc8; A, B and C are exact counts, D is +-15 %):
    coord.default.scalar_path_rate                  = 0
    coord.fuse_guard_3ph20a_10kwhouse.scalar_path_rate > 0
    coord.manual_plan_2h_space.scalar_path_rate     = 1
    golden_scalar_scenarios                          >= 1 (fuse_guard)
    f0_x_identity                                    = 1
    planner_share_1hook.single_zone_dhw             ~ 0.6

Perturbation (A): the same coordinator, same clock, same prices, with the
one config key flipped back -- fuse_guard_enabled False, or the manual
override cleared. The rate must fall to 0.

Instrumented symbols: optimizer:_bounds_supported_by_batch,
optimizer:_multi_start_minimize, thermal_model:ThermalModel.simulate_step,
thermal_model:ThermalModel.simulate_trajectory_batch,
optimizer:HeatPumpOptimizer._build_dhw_requirements,
optimizer:_scoped_minimize (for C, via the objective/jac closures).
Machine: Apple M1 8-core 8 GB (audit box).
"""
from __future__ import annotations

import asyncio
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round2", "D9"))
import d9lib  # noqa: E402  (thread pin before numpy)

import numpy as np  # noqa: E402

from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import optimizer as opt_mod  # noqa: E402
from heatpump_optimizer import thermal_model as tm_mod  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.manual_plan import build_override  # noqa: E402

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
import homeassistant.util.dt as dt_util  # noqa: E402


# ----------------------------------------------------------------------
# Hooks. Counting only -- no timing inside the hot loop for sections A-C.
# ----------------------------------------------------------------------
C: dict = {}


def reset() -> None:
    C.update(
        solves=0, scalar_solves=0, zero_range_vars=0, bound_checks=0,
        steps=0, batch_rows=0,
    )


reset()

_orig_supported = opt_mod._bounds_supported_by_batch
_orig_multi = opt_mod._multi_start_minimize
_orig_step = tm_mod.ThermalModel.simulate_step
_orig_batch = tm_mod.ThermalModel.simulate_trajectory_batch


def hooked_supported(bounds):
    C["bound_checks"] += 1
    out = _orig_supported(bounds)
    return out


def hooked_multi(objective, candidates, bounds, *a, **k):
    C["solves"] += 1
    zero = sum(1 for lo, hi in bounds if lo >= hi)
    if zero:
        C["scalar_solves"] += 1
        C["zero_range_vars"] += zero
    return _orig_multi(objective, candidates, bounds, *a, **k)


def hooked_step(self, *a, **k):
    C["steps"] += 1
    return _orig_step(self, *a, **k)


def hooked_batch(self, *a, **k):
    matrix = k.get("power_matrix", a[1] if len(a) > 1 else None)
    arr = np.asarray(matrix)
    C["batch_rows"] += int(arr.shape[0]) if arr.ndim > 1 else 1
    return _orig_batch(self, *a, **k)


opt_mod._bounds_supported_by_batch = hooked_supported
opt_mod._multi_start_minimize = hooked_multi
tm_mod.ThermalModel.simulate_step = hooked_step
tm_mod.ThermalModel.simulate_trajectory_batch = hooked_batch


# ----------------------------------------------------------------------
# A. The real coordinator cycle.
# ----------------------------------------------------------------------
START = datetime(2026, 1, 15, 0, 0)
BASE_CONFIG = {
    "tibber_token": "x",
    "weather_entity": "weather.home",
    "target_temperature": 21.0,
    "min_temperature": 17.0,
    "max_temperature": 23.0,
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    "dhw_tank_volume": 200.0,
    "dhw_setpoint": 55.0,
    "dhw_min_temperature": 45.0,
    "dhw_windows": "06:00-08:30, 17:00-22:00",
    "upper_floor_thermal_mass": 3.0,
    "lower_floor_thermal_mass": 8.0,
    "upper_floor_heat_loss": 0.08,
    "lower_floor_heat_loss": 0.07,
}


class LoopHass(FakeHass):
    """FakeHass with a REAL executor boundary, as Home Assistant has."""

    def __init__(self, states=None):
        super().__init__(states)
        self.pool = ThreadPoolExecutor(max_workers=1)

    async def async_add_executor_job(self, func, *args):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self.pool, func, *args)


def make_coord(extra: dict, states: dict | None = None):
    st = {"sensor.indoor": FakeState("21.4"), "sensor.outdoor": FakeState("-3.0")}
    st.update(states or {})
    hass = LoopHass(st)
    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data={**BASE_CONFIG, **extra}))
    coord._prices = [
        {"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
         "starts_at": (START + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
        for h in range(48)
    ]
    coord._weather_forecast = [
        {"datetime": (START + timedelta(hours=h)).isoformat(),
         "temperature": -5.0 + 3.0 * (h % 24) / 24.0, "wind_speed": 3.0,
         "precipitation": 0.0, "humidity": 85.0}
        for h in range(48)
    ]
    coord._solar_radiation_forecast = [
        max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)
    ]

    async def noop():
        return None

    coord._fetch_tibber_prices = noop
    coord._fetch_weather_forecast = noop
    coord._fetch_solar_forecast = noop
    return hass, coord


def run_cycle(label: str, extra: dict, states=None, override=None, envelope=None):
    hass, coord = make_coord(extra, states)
    loop = asyncio.new_event_loop()
    when = START + timedelta(hours=8, minutes=3)
    try:
        if override is not None:
            coord._manual_override = build_override(
                space_slots=override.get("space_slots"),
                dhw_slots=override.get("dhw_slots"),
                expires_at=when + timedelta(hours=20),
                now=when,
            )
        if envelope is not None:
            coord._capacity_envelope.update(envelope)
        dt_util.freeze(when)
        reset()
        t0 = time.thread_time()
        coord.data = loop.run_until_complete(coord._async_update_data())
        cpu = (time.thread_time() - t0) * 1000.0
    finally:
        dt_util.freeze(None)
        loop.close()
        hass.pool.shutdown(wait=True)
    solves = max(C["solves"], 1)
    d9lib.result(f"coord.{label}.solves", C["solves"], "count")
    d9lib.result(f"coord.{label}.scalar_solves", C["scalar_solves"], "count")
    d9lib.result(f"coord.{label}.scalar_path_rate", C["scalar_solves"] / solves, "ratio")
    d9lib.result(f"coord.{label}.zero_range_vars", C["zero_range_vars"], "count")
    d9lib.result(f"coord.{label}.simulate_step_calls", C["steps"], "count")
    d9lib.result(f"coord.{label}.batch_rows", C["batch_rows"], "count")
    d9lib.result(f"coord.{label}.loop_thread_cpu", cpu, "ms_provisional")
    return C["scalar_solves"], C["steps"]


HOUSE_10KW = {"sensor.house": FakeState("10000", unit="W")}
HOUSE_2KW = {"sensor.house": FakeState("2000", unit="W")}
FUSE_ON = {
    const.CONF_FUSE_GUARD_ENABLED: True,
    const.CONF_HOUSE_POWER_ENTITY: "sensor.house",
}

# The default install: nothing opted in.
run_cycle("default", {})
# The fuse guard on, 3-phase 20 A (13.8 kW), with the house pulling 10 kW at
# the moment of the solve -- an EV charging, say. The cap is 3.8 kW.
run_cycle("fuse_guard_3ph20a_10kwhouse",
          {**FUSE_ON, const.CONF_MAIN_FUSE_A: 20, const.CONF_MAIN_FUSE_PHASES: 3},
          states=HOUSE_10KW)
# The same guard with a quiet house (2 kW): cap 11.8 kW, far above the pump.
run_cycle("fuse_guard_3ph20a_2kwhouse",
          {**FUSE_ON, const.CONF_MAIN_FUSE_A: 20, const.CONF_MAIN_FUSE_PHASES: 3},
          states=HOUSE_2KW)
# 1-phase 16 A (3.68 kW), the smallest rung on FUSE_LADDER_A, quiet house.
run_cycle("fuse_guard_1ph16a_2kwhouse",
          {**FUSE_ON, const.CONF_MAIN_FUSE_A: 16, const.CONF_MAIN_FUSE_PHASES: 1},
          states=HOUSE_2KW)
# The perturbation for the two above: the guard switched off, same states.
run_cycle("perturb_fuse_guard_off_10kwhouse",
          {const.CONF_HOUSE_POWER_ENTITY: "sensor.house",
           const.CONF_MAIN_FUSE_A: 20, const.CONF_MAIN_FUSE_PHASES: 3},
          states=HOUSE_10KW)
# One apply_manual_plan call: "run space heating 18:00-20:00", nothing else.
run_cycle("manual_plan_2h_space", {},
          override={"space_slots": [
              {"start": (START + timedelta(hours=18)).isoformat(),
               "end": (START + timedelta(hours=20)).isoformat()}]})
# The DHW channel pinned instead, space left automatic.
run_cycle("manual_plan_2h_dhw_only", {},
          override={"dhw_slots": [
              {"start": (START + timedelta(hours=18)).isoformat(),
               "end": (START + timedelta(hours=20)).isoformat()}]})
# The learned capacity envelope (#17) tightened to its 0.6 x nameplate floor
# in the coldest bucket, which is what a cold snap produces.
run_cycle("capacity_envelope_cold", {const.CONF_CAPACITY_CURVE_ENABLED: True},
          envelope={b: (0.9, 40) for b in range(-6, 3)})


# ----------------------------------------------------------------------
# B. Which committed golden fixtures are on the scalar path today.
# ----------------------------------------------------------------------
import golden  # noqa: E402  (has a __main__ guard; import runs nothing)

scalar_names = []
per_scenario = []
for name, spec in golden.SCENARIOS.items():
    reset()
    t0 = time.thread_time()
    try:
        golden.capture(name, spec)
    except Exception as err:  # noqa: BLE001 - a fixture that will not build
        d9lib.result(f"golden.{name}.error", type(err).__name__, "error")
        continue
    cpu = (time.thread_time() - t0) * 1000.0
    per_scenario.append((name, C["scalar_solves"], C["solves"], C["steps"], cpu))
    if C["scalar_solves"]:
        scalar_names.append(name)
        d9lib.result(f"golden.{name}.scalar_solves", C["scalar_solves"], "count")
        d9lib.result(f"golden.{name}.solves", C["solves"], "count")
        d9lib.result(f"golden.{name}.zero_range_vars", C["zero_range_vars"], "count")
        d9lib.result(f"golden.{name}.simulate_step_calls", C["steps"], "count")
        d9lib.result(f"golden.{name}.cpu", cpu, "ms_provisional")

d9lib.result("golden_scenarios_total", len(per_scenario), "count")
d9lib.result("golden_scalar_scenarios", len(scalar_names), "count")
d9lib.result("golden_scalar_names", ",".join(scalar_names) or "none", "names")
_batched = [r for r in per_scenario if not r[1]]
_scalar = [r for r in per_scenario if r[1]]
if _batched:
    d9lib.result("golden.batched_median_steps",
                 float(np.median([r[3] for r in _batched])), "count")
    d9lib.result("golden.batched_median_cpu",
                 float(np.median([r[4] for r in _batched])), "ms_provisional")
if _scalar:
    d9lib.result("golden.scalar_median_steps",
                 float(np.median([r[3] for r in _scalar])), "count")
    d9lib.result("golden.scalar_median_cpu",
                 float(np.median([r[4] for r in _scalar])), "ms_provisional")
    d9lib.result("golden.scalar_over_batched_cpu",
                 float(np.median([r[4] for r in _scalar]))
                 / max(float(np.median([r[4] for r in _batched])), 1e-9), "ratio")


# ----------------------------------------------------------------------
# C. Is the jac's f0 really at scipy's own last f(x)?
# ----------------------------------------------------------------------
X: dict = {"last_fun": None, "jac_calls": 0, "f0_matched": 0, "in_jac": False,
           "fun_calls": 0, "extra_fun_in_jac": 0}

_orig_scoped = opt_mod._scoped_minimize
_orig_batch_fd = opt_mod._batch_fd_gradient


def watch_scoped(objective, guess, *a, **k):
    """Wrap the objective and the jac scipy is handed, and record the x each
    is called at. The jac's f0 is computed by calling the objective from
    inside the jac closure, so a flag distinguishes the two."""
    jac = k.get("jac")

    def watched_obj(x, *args):
        key = np.asarray(x, dtype=float).tobytes()
        if X["in_jac"]:
            X["extra_fun_in_jac"] += 1
            if X["last_fun"] == key:
                X["f0_matched"] += 1
        else:
            X["fun_calls"] += 1
            X["last_fun"] = key
        return objective(x, *args)

    if jac is None:
        return _orig_scoped(watched_obj, guess, *a, **k)

    def watched_jac(x, *args):
        X["jac_calls"] += 1
        X["in_jac"] = True
        try:
            return jac(x, *args)
        finally:
            X["in_jac"] = False

    k = {**k, "jac": watched_jac}
    return _orig_scoped(watched_obj, guess, *a, **k)


opt_mod._scoped_minimize = watch_scoped

stress = d9lib.load_stress_prefix()
build_case = stress["build_case"]
unit_ms, _unit_tf = d9lib.reference_unit_ms(stress, 5)
d9lib.result("reference_solve_cpu", unit_ms, "ms_provisional")

reset()
build_case(season="winter", two_zone=True, dhw=True)
d9lib.result("f0.jac_calls", X["jac_calls"], "count")
d9lib.result("f0.scipy_fun_calls", X["fun_calls"], "count")
d9lib.result("f0.objective_calls_inside_jac", X["extra_fun_in_jac"], "count")
d9lib.result("f0.f0_at_scipys_last_x", X["f0_matched"], "count")
d9lib.result("f0_x_identity",
             X["f0_matched"] / max(X["extra_fun_in_jac"], 1), "ratio")
opt_mod._scoped_minimize = _orig_scoped


# ----------------------------------------------------------------------
# D. The DHW planner share with ONE hook.
# ----------------------------------------------------------------------
tm_mod.ThermalModel.simulate_step = _orig_step
tm_mod.ThermalModel.simulate_trajectory_batch = _orig_batch
opt_mod._multi_start_minimize = _orig_multi
opt_mod._bounds_supported_by_batch = _orig_supported

HP = opt_mod.HeatPumpOptimizer
_orig_req = HP._build_dhw_requirements
P: dict = {"calls": 0, "cpu": 0.0}


def one_hook_req(self, *a, **k):
    P["calls"] += 1
    t0 = time.thread_time()
    try:
        return _orig_req(self, *a, **k)
    finally:
        P["cpu"] += time.thread_time() - t0


HP._build_dhw_requirements = one_hook_req

tfs = []
for label, kw in (
    ("two_zone_dhw", dict(season="winter", two_zone=True, dhw=True)),
    ("single_zone_dhw", dict(season="winter", two_zone=False, dhw=True)),
):
    P.update(calls=0, cpu=0.0)
    with d9lib.Clocks() as c:
        build_case(**kw)
    tfs.append(c.thread_factor)
    d9lib.result(f"planner_1hook.{label}.calls", P["calls"], "count")
    d9lib.result(f"planner_1hook.{label}.planner_cpu", P["cpu"] * 1000.0, "ms_provisional")
    d9lib.result(f"planner_1hook.{label}.solve_cpu", c.thread_ms, "ms_provisional")
    d9lib.result(f"planner_1hook.{label}.planner_share_of_solve",
                 P["cpu"] * 1000.0 / max(c.thread_ms, 1e-9), "ratio")
    d9lib.result(f"planner_1hook.{label}.planner_over_reference",
                 P["cpu"] * 1000.0 / unit_ms, "ratio")

d9lib.closing(float(np.median(tfs)))
