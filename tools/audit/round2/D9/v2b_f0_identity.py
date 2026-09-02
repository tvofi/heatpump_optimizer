"""Verifier seat 2, panel D9: is the jac's f0 at scipy's own last f(x)?

D9-03 claims the batched jac recomputes ``objective(x)`` that scipy has
just evaluated at the same point. If scipy in fact evaluates f somewhere
else, the proposed one-entry memo would never hit and the finding is
empty. This measures the point identity directly.

Metric: ``f0_x_identity`` = of the ``_batch_fd_gradient`` calls in one
solve, the fraction whose ``x0`` is byte-identical (``ndarray.tobytes()``)
to the ``x`` of the objective call scipy made immediately before it, with
no other objective call in between. ``f0_x_identity_any`` relaxes
"immediately before" to "at any earlier point in this L-BFGS-B run", which
is what a one-entry memo would need if the order ever varied.
``scalar_trajectories_per_gradient`` is the count a memo would halve.

Also section A2: the one config key that isolates the fuse ADVISOR from
the fuse GUARD -- the advisor's weekly shadow solve runs a capped solve on
any install that entered its main fuse size, whether or not the guard is
switched on.

Command (from the repository root):
    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub \
    python tools/audit/round2/D9/v2b_f0_identity.py

Expected (baseline c398fc8, exact counts):
    f0_x_identity = 1, batch_fd_calls = 103 on the two-zone DHW solve
    a2.fuse_configured_guard_off.scalar_solves   > 0
    a2.no_fuse_configured.scalar_solves          = 0   (the perturbation)

Perturbation: remove ``main_fuse_amperes`` from the same config, same
clock, same prices and the same 10 kW house-power reading. The scalar
solves must fall to zero.

Instrumented symbols: optimizer:_batch_fd_gradient, optimizer:_scoped_minimize
(objective wrapper), optimizer:_multi_start_minimize,
thermal_model:ThermalModel.simulate_trajectory.
Machine: Apple M1 8-core 8 GB (audit box).
"""
from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round2", "D9"))
import d9lib  # noqa: E402

import numpy as np  # noqa: E402

from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import optimizer as opt_mod  # noqa: E402
from heatpump_optimizer import thermal_model as tm_mod  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
import homeassistant.util.dt as dt_util  # noqa: E402

# ----------------------------------------------------------------------
# C. f0 point identity.
# ----------------------------------------------------------------------
S: dict = {
    "fun_x": [], "last_fun": None, "seen": set(), "batch_fd": 0,
    "match_last": 0, "match_any": 0, "traj": 0, "njev": 0,
}

_orig_scoped = opt_mod._scoped_minimize
_orig_fd = opt_mod._batch_fd_gradient
_orig_traj = tm_mod.ThermalModel.simulate_trajectory


def hooked_traj(self, *a, **k):
    S["traj"] += 1
    return _orig_traj(self, *a, **k)


def hooked_fd(batch_objective, args, x0, f0, eps, bounds):
    S["batch_fd"] += 1
    key = np.asarray(x0, dtype=float).tobytes()
    if S["last_fun"] == key:
        S["match_last"] += 1
    if key in S["seen"]:
        S["match_any"] += 1
    return _orig_fd(batch_objective, args, x0, f0, eps, bounds)


def watch_scoped(objective, guess, *a, **k):
    def watched_obj(x, *args):
        key = np.asarray(x, dtype=float).tobytes()
        S["last_fun"] = key
        S["seen"].add(key)
        return objective(x, *args)

    res = _orig_scoped(watched_obj, guess, *a, **k)
    S["njev"] += int(getattr(res, "njev", 0) or 0)
    return res


opt_mod._scoped_minimize = watch_scoped
opt_mod._batch_fd_gradient = hooked_fd
tm_mod.ThermalModel.simulate_trajectory = hooked_traj

stress = d9lib.load_stress_prefix()
build_case = stress["build_case"]

for label, kw in (
    ("two_zone_dhw", dict(season="winter", two_zone=True, dhw=True)),
    ("single_zone_dhw", dict(season="winter", two_zone=False, dhw=True)),
):
    S.update(fun_x=[], last_fun=None, seen=set(), batch_fd=0,
             match_last=0, match_any=0, traj=0, njev=0)
    build_case(**kw)
    fd = max(S["batch_fd"], 1)
    d9lib.result(f"{label}.batch_fd_calls", S["batch_fd"], "count")
    d9lib.result(f"{label}.njev", S["njev"], "count")
    d9lib.result(f"{label}.f0_x_identity", S["match_last"] / fd, "ratio")
    d9lib.result(f"{label}.f0_x_identity_any", S["match_any"] / fd, "ratio")
    d9lib.result(f"{label}.scalar_trajectories", S["traj"], "count")
    d9lib.result(f"{label}.scalar_trajectories_per_gradient",
                 S["traj"] / max(S["njev"], 1), "count")

opt_mod._scoped_minimize = _orig_scoped
opt_mod._batch_fd_gradient = _orig_fd
tm_mod.ThermalModel.simulate_trajectory = _orig_traj


# ----------------------------------------------------------------------
# A2. The fuse ADVISOR, isolated from the fuse GUARD.
# ----------------------------------------------------------------------
from concurrent.futures import ThreadPoolExecutor  # noqa: E402

C: dict = {"solves": 0, "scalar_solves": 0, "zero": 0, "steps": 0}
_orig_multi = opt_mod._multi_start_minimize
_orig_step = tm_mod.ThermalModel.simulate_step


def hooked_multi(objective, candidates, bounds, *a, **k):
    C["solves"] += 1
    zero = sum(1 for lo, hi in bounds if lo >= hi)
    if zero:
        C["scalar_solves"] += 1
        C["zero"] += zero
    return _orig_multi(objective, candidates, bounds, *a, **k)


def hooked_step(self, *a, **k):
    C["steps"] += 1
    return _orig_step(self, *a, **k)


opt_mod._multi_start_minimize = hooked_multi
tm_mod.ThermalModel.simulate_step = hooked_step

START = datetime(2026, 1, 15, 0, 0)
BASE_CONFIG = {
    "tibber_token": "x", "weather_entity": "weather.home",
    "target_temperature": 21.0, "min_temperature": 17.0, "max_temperature": 23.0,
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    "dhw_tank_volume": 200.0, "dhw_setpoint": 55.0, "dhw_min_temperature": 45.0,
    "dhw_windows": "06:00-08:30, 17:00-22:00",
    "upper_floor_thermal_mass": 3.0, "lower_floor_thermal_mass": 8.0,
    "upper_floor_heat_loss": 0.08, "lower_floor_heat_loss": 0.07,
}


class LoopHass(FakeHass):
    def __init__(self, states=None):
        super().__init__(states)
        self.pool = ThreadPoolExecutor(max_workers=1)

    async def async_add_executor_job(self, func, *args):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self.pool, func, *args)


def cycle(label: str, extra: dict):
    hass = LoopHass({"sensor.indoor": FakeState("21.4"),
                     "sensor.outdoor": FakeState("-3.0"),
                     "sensor.house": FakeState("10000", unit="W")})
    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data={**BASE_CONFIG, **extra}))
    coord._prices = [
        {"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
         "starts_at": (START + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
        for h in range(48)]
    coord._weather_forecast = [
        {"datetime": (START + timedelta(hours=h)).isoformat(),
         "temperature": -5.0 + 3.0 * (h % 24) / 24.0, "wind_speed": 3.0,
         "precipitation": 0.0, "humidity": 85.0} for h in range(48)]
    coord._solar_radiation_forecast = [
        max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)]

    async def noop():
        return None

    coord._fetch_tibber_prices = noop
    coord._fetch_weather_forecast = noop
    coord._fetch_solar_forecast = noop
    loop = asyncio.new_event_loop()
    C.update(solves=0, scalar_solves=0, zero=0, steps=0)
    try:
        dt_util.freeze(START + timedelta(hours=8, minutes=3))
        coord.data = loop.run_until_complete(coord._async_update_data())
    finally:
        dt_util.freeze(None)
        loop.close()
        hass.pool.shutdown(wait=True)
    d9lib.result(f"a2.{label}.solves", C["solves"], "count")
    d9lib.result(f"a2.{label}.scalar_solves", C["scalar_solves"], "count")
    d9lib.result(f"a2.{label}.zero_range_vars", C["zero"], "count")
    d9lib.result(f"a2.{label}.simulate_step_calls", C["steps"], "count")


HOUSE = {const.CONF_HOUSE_POWER_ENTITY: "sensor.house"}
# The fuse guard is OFF in both arms. The only difference is whether the
# user told the integration their main fuse size.
cycle("fuse_configured_guard_off",
      {**HOUSE, const.CONF_MAIN_FUSE_A: 20, const.CONF_MAIN_FUSE_PHASES: 3})
cycle("no_fuse_configured", {**HOUSE})

d9lib.closing(1.0)
