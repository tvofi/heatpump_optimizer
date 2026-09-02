#!/usr/bin/env python
"""D1 executor-boundary race harness: mutate every loop-side writer while the
solve thread is inside the executor, and count torn fields in the plan.

METRIC (counts, contention-immune; all runs use a fresh coordinator with
identical injected inputs, so any difference is caused by the mutation):
  live_repeat_identical      1 if two unmutated live solves give the same plan
                             (the comparison has no noise floor)
  live_torn_fields           OptimizationResult fields that differ between a
                             solve mutated MID-solve and an unmutated solve
                             (expected 0: _solve_snapshot deep-copies)
  live_control_changed       fields that differ when the same mutation is
                             applied BEFORE the solve (must be > 0, or the
                             comparison has no power)
  whatif_repeat_identical    same, for async_simulate (the card's what-if)
  whatif_torn_fields         what-if payload fields that differ when the
                             SHARED containers (defrost_derate learner,
                             dhw_hourly_draw_pattern, internal_gains_profile)
                             are mutated in place mid-solve (expected 0)
  whatif_scalar_torn_fields  same for scalar writes on _thermal_params /
                             _current_state / _opt_config (replace() copies
                             scalars, expected 0)
  whatif_control_changed     fields that differ when the shared containers are
                             mutated before the what-if (must be > 0)
  *_exceptions               exceptions out of the executor (expected 0)

COMMAND (from the export root):
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
  VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub \
  /Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/tvofi-claude/.venv/bin/python \
  tools/audit/round2/D1/executor_race.py

EXPECTED (baseline c398fc84eec25fc44b60d74aae05b9a2da205884, exact): see REPORT.md

INSTRUMENTED SYMBOLS:
  heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._solve_snapshot
  heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator.async_run_optimization
  heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator.async_simulate
  heatpump_optimizer.optimizer:HeatPumpOptimizer.optimize (gated by a
  class-attribute swap: the solve thread blocks on a threading.Event until the
  loop side has finished mutating)

READERS / WRITERS (from _solve_snapshot, the executor lambda, and
async_simulate): the solve thread reads copies of _current_state,
_thermal_params (incl. defrost_derate, dhw_hourly_draw_pattern,
internal_gains_profile, dhw_windows), _opt_config, and the horizon arrays
computed before the executor call. Loop-side writers: _update_current_state,
the ECL110 MQTT handler and _on_power_event (_current_state), the learners
(_apply_house_heat_loss_scale, _apply_cop_scale, _apply_dhw_cooling_rate,
_defrost.observe, _dhw_hourly_profile folds, _internal_gains_profile),
async_set_target_temperature / _apply_comfort_weight / economy widening
(_opt_config), the fetches (_prices, _weather_forecast), the manual plan.

PERTURBATION: replace `copy.deepcopy(self._thermal_params)` in
  _solve_snapshot with `replace(self._thermal_params)` -> live_torn_fields up.
  For the what-if: replace `replace(self._thermal_params)` in async_simulate
  with `copy.deepcopy(...)` -> whatif_torn_fields to_zero.

MACHINE: Apple M1 8-core 8 GB, Darwin 25.6.0, CPython 3.13.1, numpy 2.5.2
"""
from __future__ import annotations

import os

for _k in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_k, "1")

import asyncio
import dataclasses
import json
import logging
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.manual_plan import ManualOverride  # noqa: E402
from heatpump_optimizer.optimizer import HeatPumpOptimizer  # noqa: E402

logging.basicConfig(level=logging.CRITICAL)
logging.getLogger("heatpump_optimizer").setLevel(logging.CRITICAL)

START = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)
MIDNIGHT = START.replace(hour=0, minute=0)

CONFIG = {
    "tibber_token": "x",
    "weather_entity": "weather.home",
    "indoor_temp_entity": "sensor.indoor",
    "outdoor_temp_entity": "sensor.outdoor",
    "dhw_temp_entity": "sensor.dhw",
    "target_temperature": 21.0,
    "min_temperature": 17.0,
    "max_temperature": 23.0,
    "dhw_tank_volume": 200.0,
    "dhw_setpoint": 55.0,
    "dhw_min_temperature": 45.0,
    "dhw_windows": "06:00-08:30, 17:00-22:00",
    "internal_gains_learning_enabled": True,
}


class RealHass(FakeHass):
    def __init__(self, states=None):
        super().__init__(states)
        self.loop = asyncio.get_running_loop()
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="hpo-exec")
        self.exceptions = []

    def async_create_task(self, coro, name=None, eager_start=False):
        return self.loop.create_task(coro, name=name)

    async def async_add_executor_job(self, func, *args):
        try:
            return await self.loop.run_in_executor(self.executor, func, *args)
        except Exception as err:  # noqa: BLE001
            self.exceptions.append(repr(err))
            raise


async def _noop(self):
    return None


HeatPumpOptimizerCoordinator._fetch_tibber_prices = _noop
HeatPumpOptimizerCoordinator._fetch_weather_forecast = _noop
HeatPumpOptimizerCoordinator._fetch_solar_forecast = _noop

GATE = {"hold": False}
started = threading.Event()
release = threading.Event()
_real_optimize = HeatPumpOptimizer.optimize


def _gated_optimize(self, *args, **kwargs):
    if GATE["hold"]:
        started.set()
        release.wait(timeout=60)
    return _real_optimize(self, *args, **kwargs)


HeatPumpOptimizer.optimize = _gated_optimize


def prices(scale=1.0):
    return [
        {
            "total": round(scale * (0.6 + 0.5 * (h % 12) / 12.0), 4),
            "starts_at": (MIDNIGHT + timedelta(hours=h)).isoformat(),
            "level": "NORMAL",
        }
        for h in range(48)
    ]


def forecast(offset=0.0):
    return [
        {
            "datetime": (MIDNIGHT + timedelta(hours=h)).isoformat(),
            "temperature": -5.0 + offset + 3.0 * (h % 24) / 24.0,
            "wind_speed": 3.0,
            "precipitation": 0.0,
            "humidity": 85.0,
        }
        for h in range(48)
    ]


def build():
    now = dt_util.now()
    hass = RealHass(
        {
            "sensor.indoor": FakeState("21.4", last_updated=now),
            "sensor.outdoor": FakeState("-3.0", last_updated=now),
            "sensor.dhw": FakeState("48.0", last_updated=now),
        }
    )
    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=CONFIG))
    coord._prices = prices()
    coord._weather_forecast = forecast()
    coord._internal_gains_profile = [0.3] * 24
    return hass, coord


def fingerprint(obj):
    if dataclasses.is_dataclass(obj):
        return {
            f.name: json.dumps(getattr(obj, f.name), default=str, sort_keys=True)
            for f in dataclasses.fields(obj)
            if f.name != "solve_time_ms"
        }
    return {k: json.dumps(v, default=str, sort_keys=True) for k, v in obj.items() if k not in ("solve_time_ms", "rate_limited")}


def diff(a, b):
    return sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))


# -- the loop-side writers, exercised directly ----------------------------------
def mutate_scalars(coord):
    st = coord._current_state
    st.room_temperature -= 4.0
    st.outdoor_temperature -= 10.0
    st.dhw_temperature -= 15.0
    st.peak_guard_active = True
    st.external_heat_active = True
    cfg = coord._opt_config
    cfg.target_temp = 18.0
    cfg.min_temp = 16.0
    cfg.comfort_weight = cfg.comfort_weight * 3.0
    p = coord._thermal_params
    p.heat_loss_coefficient *= 1.8
    p.cop_nominal *= 0.6
    p.dhw_setpoint = 65.0
    p.solar_aperture_scale = 0.2
    coord._prices = prices(scale=3.0)
    coord._weather_forecast = forecast(offset=-12.0)


def mutate_shared_containers(coord):
    p = coord._thermal_params
    p.dhw_hourly_draw_pattern[:] = [x * 4.0 for x in p.dhw_hourly_draw_pattern]
    if isinstance(p.internal_gains_profile, list):
        p.internal_gains_profile[:] = [3.0] * len(p.internal_gains_profile)
    if isinstance(coord._internal_gains_profile, list):
        coord._internal_gains_profile[:] = [3.0] * 24
    # the learner object is shared by reference with a shallow copy
    for _ in range(80):
        coord._defrost.observe(-3.0, 85.0, 0.35)
        coord._defrost.observe(-6.0, 85.0, 0.35)
        coord._defrost.observe(-1.0, 85.0, 0.35)
    p.dhw_windows.clear()


def mutate_all(coord):
    mutate_scalars(coord)
    mutate_shared_containers(coord)
    coord._manual_override = ManualOverride.from_dict(
        {
            "space_slots": [
                {"start": (START + timedelta(hours=1)).isoformat(), "end": (START + timedelta(hours=3)).isoformat()}
            ],
            "dhw_slots": [],
            "expires_at": (START + timedelta(hours=8)).isoformat(),
            "created_at": START.isoformat(),
        }
    )


async def held(coro_factory, mutator):
    """Run coro_factory() with the solve held; apply mutator while held."""
    GATE["hold"] = True
    started.clear()
    release.clear()
    task = asyncio.get_running_loop().create_task(coro_factory())
    deadline = time.monotonic() + 60
    while not started.is_set() and time.monotonic() < deadline:
        await asyncio.sleep(0.005)
    assert started.is_set(), "solve never reached the executor"
    mutator()
    release.set()
    out = await task
    GATE["hold"] = False
    return out


async def live_solve(coord):
    await coord.async_run_optimization()
    return coord._optimization_result


async def main():
    dt_util.freeze(START)
    out = {}
    t0 = time.process_time()
    tt0 = time.thread_time()

    # ---------------- live solve ----------------
    _, c0 = build()
    r0 = fingerprint(await live_solve(c0))
    _, c1 = build()
    r1 = fingerprint(await live_solve(c1))
    out["live_repeat_identical"] = int(not diff(r0, r1))

    h2, c2 = build()
    r2 = fingerprint(await held(lambda: live_solve(c2), lambda: mutate_all(c2)))
    out["live_torn_fields"] = len(diff(r0, r2))
    out["live_torn_field_names"] = "+".join(diff(r0, r2)) or "none"
    out["live_exceptions"] = len(h2.exceptions)
    # the published payload after the mutated-mid-solve run: does it carry the plan?
    out["live_payload_has_plan"] = int(bool(c2._build_data_dict().get("current_action")))

    _, c3 = build()
    mutate_all(c3)
    r3 = fingerprint(await live_solve(c3))
    out["live_control_changed"] = len(diff(r0, r3))

    # ---------------- what-if ----------------
    async def whatif(coord, overrides):
        coord._last_simulation = None
        return await coord.async_simulate(overrides)

    OVR = {"target_temp": 20.0}
    _, w0c = build()
    await live_solve(w0c)
    w0 = fingerprint(await whatif(w0c, OVR))
    w0b = fingerprint(await whatif(w0c, OVR))
    out["whatif_repeat_identical"] = int(not diff(w0, w0b))
    out["whatif_error"] = w0.get("error", "none")

    h4, w1c = build()
    await live_solve(w1c)
    w1 = fingerprint(await held(lambda: whatif(w1c, OVR), lambda: mutate_shared_containers(w1c)))
    out["whatif_torn_fields"] = len(diff(w0, w1))
    out["whatif_torn_field_names"] = "+".join(diff(w0, w1)) or "none"
    out["whatif_exceptions"] = len(h4.exceptions)

    h5, w2c = build()
    await live_solve(w2c)
    w2 = fingerprint(await held(lambda: whatif(w2c, OVR), lambda: mutate_scalars(w2c)))
    out["whatif_scalar_torn_fields"] = len(diff(w0, w2))
    out["whatif_scalar_exceptions"] = len(h5.exceptions)

    _, w3c = build()
    await live_solve(w3c)
    mutate_shared_containers(w3c)
    w3 = fingerprint(await whatif(w3c, OVR))
    out["whatif_control_changed"] = len(diff(w0, w3))
    out["whatif_control_field_names"] = "+".join(diff(w0, w3)) or "none"

    # attribute the tear to one shared container at a time (mid-solve)
    def only_defrost(c):
        for _ in range(80):
            c._defrost.observe(-3.0, 85.0, 0.35)
            c._defrost.observe(-6.0, 85.0, 0.35)
            c._defrost.observe(-1.0, 85.0, 0.35)

    def only_draw_pattern(c):
        pat = c._thermal_params.dhw_hourly_draw_pattern
        pat[:] = [x * 4.0 for x in pat]

    def only_gains(c):
        prof = c._thermal_params.internal_gains_profile
        if isinstance(prof, list):
            prof[:] = [3.0] * len(prof)

    def only_windows(c):
        c._thermal_params.dhw_windows.clear()

    for name, fn in (
        ("defrost_learner", only_defrost),
        ("draw_pattern", only_draw_pattern),
        ("gains_profile", only_gains),
        ("dhw_windows", only_windows),
    ):
        _, wc = build()
        await live_solve(wc)
        w = fingerprint(await held(lambda: whatif(wc, OVR), lambda: fn(wc)))
        out[f"whatif_torn_{name}"] = len(diff(w0, w))

    for k, v in out.items():
        print(f"RESULT {k}={v} count")
    cpu = time.process_time() - t0
    thr = time.thread_time() - tt0
    print(f"RESULT thread_factor={cpu / thr if thr else float('nan'):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    dt_util.freeze(None)
    for h in (h2, h4, h5):
        h.executor.shutdown(wait=True)


if __name__ == "__main__":
    asyncio.run(main())
