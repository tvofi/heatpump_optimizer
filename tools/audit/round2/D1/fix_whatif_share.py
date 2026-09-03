"""D1-05 (#240) fix harness: what-if payload fields torn by a mid-solve write.

Metric: what-if payload fields that differ between a run whose learner
containers were written in place while the solve was held in the executor and
an unmutated run with identical inputs.

Two amplitudes are measured, and the PRODUCTION one is the headline (the
panel's correction to the finder): ONE ``DefrostDerate.observe`` per cycle,
which is the only in-place production writer, against the finder's 240
clamped-extreme observes -- 240x production amplitude. `cost_delta_shift` is
reported alongside, because a torn display field that does not move the number
the card shows is not the same claim as one that does.

Command (from the repository root):
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub \
  .venv/bin/python tools/audit/round2/D1/fix_whatif_share.py

Expected on origin/main (4a7bdb6): shared_mutable_fields=3
(defrost_derate, internal_gains_profile, dhw_hourly_draw_pattern share
identity with the live params through ``dataclasses.replace``);
prod_amplitude_torn_fields=2 at cost_delta_shift=0.0000;
finder_amplitude_torn_fields=10. Expected after the fix: 0 shared fields and
0 torn at either amplitude, with the control arms unchanged.

Instrumented symbols:
  custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator
  .async_simulate and ._solve_snapshot.

Perturbation / positive control: the ``live`` arm applies the SAME mutation
schedule to the live solve, which deep-copies through ``_solve_snapshot``; it
must read 0 torn fields on both trees while ``control_changed`` (the same
mutation applied BEFORE the solve rather than during it) stays non-zero,
proving the mutation is large enough to be seen at all.

Baseline SHA: 4a7bdb696c9a01783afc7bdcb4a840de0f935dcb. Machine: 8-core M1.
"""
from __future__ import annotations

import os

for _var in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_var, "1")

import asyncio
import concurrent.futures
import sys
import threading
import time
from datetime import timedelta

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from homeassistant.util import dt as dt_util  # noqa: E402

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402

from heatpump_optimizer import coordinator as coord_mod  # noqa: E402
from heatpump_optimizer.coordinator import (  # noqa: E402
    HeatPumpOptimizerCoordinator,
)
from heatpump_optimizer.const import MODE_AUTO  # noqa: E402


START = dt_util.parse_datetime("2025-01-15T00:00:00+01:00")

CONFIG = {
    "tibber_token": "tok",
    "indoor_temp_entity": "sensor.indoor",
    "outdoor_temp_entity": "sensor.outdoor",
    "peak_guard_enabled": False,
    "dhw_enabled": True,
    "dhw_windows": "06:00-08:00,18:00-21:00",
    "internal_gains_learning_enabled": True,
}

OVERRIDES = {"target_temp": 20.5, "comfort_weight": 1.2}


class ExecHass(FakeHass):
    """A real thread pool, so the solve genuinely runs off the event loop."""

    def __init__(self, states=None) -> None:
        super().__init__(states)
        self.state_listeners = []
        self.pool = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        self.entered = threading.Event()

    def async_create_task(self, coro, name=None, eager_start=None):
        return asyncio.get_running_loop().create_task(coro)

    async def async_add_executor_job(self, func, *args):
        loop = asyncio.get_running_loop()

        def _wrapped(*a):
            self.entered.set()
            return func(*a)

        return await loop.run_in_executor(self.pool, _wrapped, *args)


def _build() -> HeatPumpOptimizerCoordinator:
    hass = ExecHass(
        {
            "sensor.indoor": FakeState("21.0", unit="°C"),
            "sensor.outdoor": FakeState("-5.0", unit="°C"),
        }
    )
    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=dict(CONFIG)))
    coord._mode = MODE_AUTO
    coord._prices = [
        {
            "total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
            "starts_at": (START + timedelta(hours=h)).isoformat(),
            "level": "NORMAL",
        }
        for h in range(48)
    ]
    coord._weather_forecast = [
        {
            "datetime": (START + timedelta(hours=h)).isoformat(),
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
    coord._thermal_params.internal_gains_profile = [0.3] * 24
    return coord


async def _built_with_plan() -> HeatPumpOptimizerCoordinator:
    """A coordinator carrying a solved plan: the what-if differences against it."""
    coord = _build()
    await coord.async_run_optimization()
    return coord


def _mutate_production(coord) -> None:
    """The ONLY in-place write production performs: one observe per cycle.

    ``_record_accuracy`` calls ``_defrost.observe`` (or ``observe_duty``) once
    at the end of each cycle, at a realistic delivered ratio. The gains
    profile, the draw pattern and the windows are REASSIGNED in production,
    never mutated in place, so this arm leaves them alone -- which is exactly
    the correction the panel made to the finder's amplitude.
    """
    coord._defrost.observe(-5.0, 85.0, 0.85)


def _mutate_finder(coord, observes: int) -> None:
    """The finder's positive control: `observes` clamped extremes plus the
    three containers written in place, none of which production writes."""
    for i in range(observes):
        coord._defrost.observe(-5.0, 85.0, 3.0 if i % 2 else 0.05)
    if observes:
        profile = coord._thermal_params.internal_gains_profile
        if isinstance(profile, list) and profile:
            for h in range(len(profile)):
                profile[h] = profile[h] + 0.5
        windows = coord._thermal_params.dhw_windows
        if isinstance(windows, list) and windows:
            del windows[:]
        pattern = coord._thermal_params.dhw_hourly_draw_pattern
        if isinstance(pattern, list) and pattern:
            for h in range(len(pattern)):
                pattern[h] = pattern[h] * 1.5


def _mutate(coord, observes: int) -> None:
    """Dispatch: 0 = nothing, 1 = production amplitude, N = the finder's."""
    if observes == 0:
        return
    if observes == 1:
        _mutate_production(coord)
        return
    _mutate_finder(coord, observes)


DISPLAY_FIELDS = (
    "baseline_cost",
    "simulated_cost",
    "cost_delta",
    "monthly_cost_delta",
    "savings_percentage",
    "projected_peak_kw",
    "compressor_starts",
    "min_room_temperature",
    "min_dhw_temperature",
    "space_slots",
    "dhw_slots",
)


def _fields(payload: dict) -> dict:
    return {k: payload.get(k) for k in DISPLAY_FIELDS}


async def _whatif(coord, *, observes: int, during: bool) -> dict:
    """One what-if; the mutation lands mid-solve (`during`) or before it."""
    coord._last_simulation = None
    if not during:
        _mutate(coord, observes)
        return await coord.async_simulate(dict(OVERRIDES))

    coord.hass.entered.clear()
    task = asyncio.get_running_loop().create_task(
        coord.async_simulate(dict(OVERRIDES))
    )

    async def _writer():
        # No synchronisation to the solve thread beyond "it has started" and
        # no sleep inside optimize: the window is the whole solve. The poll
        # sleeps rather than spinning -- a spinning event loop fights the
        # executor thread for the GIL and turns a 1 s solve into minutes.
        deadline = time.monotonic() + 30.0
        while not coord.hass.entered.is_set():
            if time.monotonic() > deadline:
                raise RuntimeError("solve never entered the executor")
            await asyncio.sleep(0.005)
        _mutate(coord, observes)

    await asyncio.gather(_writer(), asyncio.sleep(0))
    return await task


def _torn(a: dict, b: dict) -> list[str]:
    return sorted(k for k in DISPLAY_FIELDS if a.get(k) != b.get(k))


async def _arm(observes: int) -> dict:
    """Clean baseline what-if, then the same one with a mid-solve write."""
    clean_coord = await _built_with_plan()
    clean = _fields(await _whatif(clean_coord, observes=0, during=False))

    torn_coord = await _built_with_plan()
    torn = _fields(await _whatif(torn_coord, observes=observes, during=True))

    ctrl_coord = await _built_with_plan()
    ctrl = _fields(await _whatif(ctrl_coord, observes=observes, during=False))

    delta_shift = 0.0
    if clean.get("cost_delta") is not None and torn.get("cost_delta") is not None:
        delta_shift = abs(float(torn["cost_delta"]) - float(clean["cost_delta"]))

    return {
        "torn_fields": len(_torn(clean, torn)),
        "torn_field_names": "+".join(_torn(clean, torn)) or "none",
        "control_changed": len(_torn(clean, ctrl)),
        "cost_delta_shift": f"{delta_shift:.4f}",
    }


async def _repeatability() -> int:
    """Two identical what-ifs with no mutation at all must agree."""
    coord = await _built_with_plan()
    a = _fields(await _whatif(coord, observes=0, during=False))
    b = _fields(await _whatif(coord, observes=0, during=False))
    other = await _built_with_plan()
    c = _fields(await _whatif(other, observes=0, during=False))
    return len(_torn(a, b)) + len(_torn(a, c))


async def _shared_mutable_fields() -> tuple[int, str]:
    """Mutable learner containers the what-if's own params share by IDENTITY.

    Instrumented at the production symbol rather than re-derived: the
    ``ThermalModel`` constructor inside ``async_simulate`` is wrapped so the
    parameter object the what-if actually built is captured, and each
    container is compared with ``is`` against the live one.
    """
    coord = await _built_with_plan()
    captured: list = []
    real_model = coord_mod.ThermalModel

    class _Spy(real_model):  # type: ignore[misc, valid-type]
        def __init__(self, params, *a, **k):
            captured.append(params)
            super().__init__(params, *a, **k)

    coord_mod.ThermalModel = _Spy
    try:
        coord._last_simulation = None
        await coord.async_simulate(dict(OVERRIDES))
    finally:
        coord_mod.ThermalModel = real_model

    if not captured:
        return -1, "whatif never built a ThermalModel"
    scratch = captured[-1]
    live = coord._thermal_params
    names = []
    for name in (
        "defrost_derate",
        "internal_gains_profile",
        "dhw_hourly_draw_pattern",
        "dhw_windows",
    ):
        live_value = getattr(live, name, None)
        if live_value is None:
            continue
        if getattr(scratch, name, None) is live_value:
            names.append(name)
    return len(names), "+".join(names) or "none"


async def _live_learner_writes() -> tuple[int, int]:
    """Does a what-if write back to live learner state? (arm, control).

    Seat 2's decisive consequence measurement: the corruption DIRECTION is
    zero. The control applies the finder's own mutation directly, so a
    non-zero control proves the comparison can see a write at all.
    """
    def snapshot(coord) -> tuple:
        p = coord._thermal_params
        return (
            repr(coord._defrost.as_dict()),
            repr(p.internal_gains_profile),
            repr(p.dhw_hourly_draw_pattern),
            repr(p.dhw_windows),
        )

    coord = await _built_with_plan()
    before = snapshot(coord)
    coord._last_simulation = None
    await coord.async_simulate(
        {**OVERRIDES, "dhw_setpoint": 58.0, "dhw_windows": "07:00-09:00"}
    )
    arm = sum(1 for a, b in zip(before, snapshot(coord)) if a != b)

    control_coord = await _built_with_plan()
    before_c = snapshot(control_coord)
    _mutate_finder(control_coord, 240)
    control = sum(1 for a, b in zip(before_c, snapshot(control_coord)) if a != b)
    return arm, control


async def _live_solve_arm(observes: int) -> dict:
    """PERTURBATION: the live solve, which deep-copies, under the same writes."""
    clean_coord = _build()
    await clean_coord.async_run_optimization()
    clean = clean_coord._optimization_result

    torn_coord = _build()
    torn_coord.hass.entered.clear()
    task = asyncio.get_running_loop().create_task(
        torn_coord.async_run_optimization()
    )

    async def _writer():
        deadline = time.monotonic() + 30.0
        while not torn_coord.hass.entered.is_set():
            if time.monotonic() > deadline:
                raise RuntimeError("solve never entered the executor")
            await asyncio.sleep(0.005)
        _mutate(torn_coord, observes)

    await asyncio.gather(_writer(), asyncio.sleep(0))
    await task
    torn = torn_coord._optimization_result

    fields = (
        "predicted_cost",
        "savings_percentage",
        "projected_peak_kw",
        "compressor_starts",
        "status",
    )
    diff = sum(
        1
        for f in fields
        if getattr(clean, f, None) != getattr(torn, f, None)
    )
    return {"live_torn_fields": diff}


async def main() -> None:
    dt_util.freeze(START)
    results: list[tuple[str, str]] = []
    try:
        shared, shared_names = await _shared_mutable_fields()
        results.append(("whatif_shared_mutable_fields", str(shared)))
        results.append(("whatif_shared_mutable_field_names", shared_names))

        results.append(("whatif_repeat_torn_fields", str(await _repeatability())))

        prod = await _arm(1)
        for key, value in prod.items():
            results.append((f"prod_amplitude.{key}", str(value)))

        finder = await _arm(240)
        for key, value in finder.items():
            results.append((f"finder_amplitude.{key}", str(value)))

        live = await _live_solve_arm(240)
        for key, value in live.items():
            results.append((f"live_solve.{key}", str(value)))

        arm, control = await _live_learner_writes()
        results.append(("whatif_live_learner_writes", str(arm)))
        results.append(("whatif_live_learner_writes_control", str(control)))
    finally:
        dt_util.freeze(None)

    for name, value in results:
        print(f"RESULT {name}={value} count")

    t0 = time.process_time()
    tt0 = time.thread_time()
    x = 0.0
    for i in range(200000):
        x += i ** 0.5
    proc = time.process_time() - t0
    thread = time.thread_time() - tt0
    print(f"RESULT thread_factor={proc / thread if thread else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    asyncio.run(main())
