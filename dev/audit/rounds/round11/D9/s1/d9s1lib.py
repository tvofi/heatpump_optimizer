"""Shared helpers for round-11 D9-s1 harnesses (not itself a harness).

Imported AFTER the caller's thread pin. Paths are relative to the repository
root, which every harness runs from with PYTHONPATH=tests/hastub.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
"""
from __future__ import annotations

import datetime as _dt
import inspect
import os
import resource
import sys
import time

ROOT = os.getcwd()
for _p in (os.path.join(ROOT, "custom_components"), os.path.join(ROOT, "tests"),
           os.path.join(ROOT, "tests", "hastub")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np  # noqa: E402

START = _dt.datetime(2026, 1, 15, 0, 0)


def result(name, value, unit="1"):
    if isinstance(value, float):
        value = f"{value:.6g}"
    print(f"RESULT {name}={value} {unit}", flush=True)


def load1() -> float:
    try:
        return float(os.getloadavg()[0])
    except OSError:
        return float("nan")


def swapins() -> int:
    try:
        with open("/proc/vmstat") as fh:
            for line in fh:
                if line.startswith("pswpin "):
                    return int(line.split()[1])
    except OSError:
        pass
    return -1


class Clock:
    """process CPU / this-thread CPU over a section -> thread_factor."""

    def __init__(self):
        self.p0 = time.process_time()
        self.t0 = time.thread_time()

    def factor(self, subtract: float = 0.0) -> float:
        dp = time.process_time() - self.p0 - subtract
        dt = time.thread_time() - self.t0
        return dp / dt if dt > 0 else float("nan")


def tail(clock: Clock | None = None, subtract: float = 0.0, swap0: int | None = None):
    if clock is not None:
        result("thread_factor", clock.factor(subtract), "1")
    result("load1", load1(), "1")
    s = swapins()
    result("swapins", (s - swap0) if (swap0 is not None and s >= 0) else s, "count")
    result("ru_maxrss_self_mb",
           resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, "MB")


# --------------------------------------------------------------------------
# Solve scenarios (tests/profiles.py builders)
# --------------------------------------------------------------------------

def make_solve(kind: str, horizon_hours: int = 24, price="winter_typical",
               wx="winter_cold"):
    """(optimizer, SolveInputs) for one named scenario.

    kinds: two_zone_dhw (default install shape), single_zone (no DHW),
    single_zone_dhw, dhw_cap_zero_range (flat cap 0.8*p_max -> (0,0) space
    bounds inside DHW blocks), manual_pin (one-slot manual plan: 1 step on,
    23 forced off, rest free).
    """
    from profiles import DT, house, prices, solve_inputs, weather
    from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
    from heatpump_optimizer.thermal_model import (ThermalModel, ThermalParameters,
                                                  ThermalState)

    two_zone = kind == "two_zone_dhw" or kind == "dhw_cap_zero_range"
    dhw = kind != "single_zone"
    cfg = house(two_zone=two_zone, dhw=dhw)
    params = ThermalParameters.from_config(cfg)
    params.dhw_enabled = dhw
    opt_cfg = OptimizationConfig(
        horizon_hours=horizon_hours, time_step_minutes=15,
        target_temp=cfg["target_temperature"], min_temp=cfg["min_temperature"],
        max_temp=cfg["max_temperature"])
    n = int(horizon_hours / DT)

    def fit(arr):
        arr = np.asarray(arr, dtype=float)
        return arr[:n] if len(arr) >= n else np.tile(arr, int(np.ceil(n / len(arr))))[:n]

    p = fit(prices(price, START))
    outdoor, wind, rain, solar = (fit(a) for a in weather(wx, START))
    state = ThermalState(
        room_temperature=21.0, slab_temperature=22.0,
        outdoor_temperature=float(outdoor[0]), upper_floor_temperature=21.0,
        lower_floor_temperature=21.0, dhw_temperature=50.0,
        dhw_hours_since_legionella=20.0, buffer_tank_temperature=40.0)
    caps = None
    space_pins = None
    if kind == "dhw_cap_zero_range":
        caps = np.full(n, 0.8 * params.max_electrical_power)
    if kind == "manual_pin":
        space_pins = np.full(n, np.nan)
        space_pins[0] = 1.0
        space_pins[1:24] = 0.0
    inputs = solve_inputs(initial_state=state, prices=p, outdoor_temps=outdoor,
                          wind_speeds=wind, precipitation=rain, solar_radiation=solar,
                          start_time=START, power_caps_extra=caps, space_pins=space_pins)
    return HeatPumpOptimizer(ThermalModel(params), opt_cfg), inputs, n


# --------------------------------------------------------------------------
# Counting hooks on the production symbols
# --------------------------------------------------------------------------

PATH_FUNCS = ("_avoid_priced_switches", "_co_optimize", "_optimize_with_dhw",
              "_optimize_space_only", "_relaxed_plans", "_held_solve",
              "_maybe_refresh_price_tile", "_maybe_run_fuse_advisor",
              "async_simulate", "steady_pair", "async_run_optimization",
              "_async_update_data", "diagnose_record", "async_diagnose_interval",
              "_run_system_identification", "estimate_recovery_hours",
              "_commit_runs", "_resolved_runs", "_lbfgsb_restart", "move_starts",
              "_dhw_build", "_dhw_coil_wood_forecast", "_multi_start_minimize",
              "_co_optimize_dhw_replan")


def caller_path(skip: int = 2) -> str:
    """The innermost-first chain of PATH_FUNCS on the stack, outermost first."""
    names = []
    f = inspect.currentframe()
    for _ in range(skip):
        f = f.f_back if f is not None else None
    while f is not None:
        n = f.f_code.co_name
        if n in PATH_FUNCS and (not names or names[-1] != n):
            names.append(n)
        f = f.f_back
    return ">".join(reversed(names)) or "?"


class Counters:
    """Hooks ThermalModel.simulate_step / simulate_trajectory_batch rows and
    optimizer._scoped_minimize / _multi_start_minimize / _batch_fd_gradient."""

    def __init__(self):
        self.sse = 0          # simulate_step calls + batch rows
        self.steps = 0
        self.rows = 0
        self.fd_grads = 0
        self.msm = []         # per _multi_start_minimize: dict
        self.runs = []        # per _scoped_minimize: dict
        self._stack = []
        self.by_path = {}     # caller_path -> sse
        self._patches = []

    def install(self):
        from heatpump_optimizer import optimizer as om
        from heatpump_optimizer import thermal_model as tm

        c = self
        real_step = tm.ThermalModel.simulate_step
        real_batch = tm.ThermalModel.simulate_trajectory_batch
        real_msm = om._multi_start_minimize
        real_min = om._scoped_minimize
        real_fd = om._batch_fd_gradient

        def step(self_, *a, **k):
            c.sse += 1
            c.steps += 1
            kp = caller_path()
            c.by_path[kp] = c.by_path.get(kp, 0) + 1
            return real_step(self_, *a, **k)

        def batch(self_, *a, **k):
            pm = k.get("power_matrix", a[1] if len(a) > 1 else None)
            r = int(np.shape(pm)[0]) if pm is not None and np.ndim(pm) == 2 else 1
            c.sse += r
            c.rows += r
            kp = caller_path()
            c.by_path[kp] = c.by_path.get(kp, 0) + r
            return real_batch(self_, *a, **k)

        def fd(*a, **k):
            c.fd_grads += 1
            return real_fd(*a, **k)

        def scoped(*a, **k):
            s0 = c.sse
            res = real_min(*a, **k)
            nj = int(getattr(res, "njev", 0) or 0)
            nf = int(getattr(res, "nfev", 0) or 0)
            c.runs.append({"sse": c.sse - s0, "njev": nj, "nfev": nf,
                           "jac": k.get("jac"), "path": caller_path(),
                           "nvar": len(k.get("bounds") or [])})
            return res

        def msm(*a, **k):
            s0, f0 = c.sse, c.fd_grads
            r0 = len(c.runs)
            rec = {"path": caller_path(), "t0": time.process_time()}
            try:
                return real_msm(*a, **k)
            finally:
                runs = c.runs[r0:]
                rec.update(sse=c.sse - s0, fd=c.fd_grads - f0,
                           njev=sum(r["njev"] for r in runs),
                           run_sse=sum(r["sse"] for r in runs),
                           nruns=len(runs), cpu=time.process_time() - rec["t0"],
                           nvar=runs[0]["nvar"] if runs else 0)
                c.msm.append(rec)

        for obj, name, new in ((tm.ThermalModel, "simulate_step", step),
                               (tm.ThermalModel, "simulate_trajectory_batch", batch),
                               (om, "_multi_start_minimize", msm),
                               (om, "_scoped_minimize", scoped),
                               (om, "_batch_fd_gradient", fd)):
            self._patches.append((obj, name, getattr(obj, name)))
            setattr(obj, name, new)
        return self

    def uninstall(self):
        for obj, name, old in reversed(self._patches):
            setattr(obj, name, old)
        self._patches.clear()


# --------------------------------------------------------------------------
# Coordinator cycle rig: the real HeatPumpOptimizerCoordinator on injected
# series, its three fetches no-ops, the clock frozen, and -- unlike FakeHass
# -- a REAL ThreadPoolExecutor behind async_add_executor_job, so the loop
# thread and the executor are different threads.
# --------------------------------------------------------------------------

CYCLE_NOW = _dt.datetime(2026, 1, 15, 6, 0, tzinfo=_dt.timezone.utc)


def make_loop_hass(loop, pool, states=None):
    from harness import FakeHass

    class LoopHass(FakeHass):
        async def async_add_executor_job(self, func, *args):
            return await loop.run_in_executor(pool, func, *args)

        def async_create_task(self, coro, *a, **k):
            return loop.create_task(coro)

    hass = LoopHass(states)
    hass.loop = loop
    return hass


def make_coordinator(hass, extra=None, entry_id="d9s1"):
    from datetime import timedelta
    from harness import FakeEntry, FakeState
    from heatpump_optimizer import const
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator

    hass.states.set("sensor.indoor", FakeState("21.0"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    entry = FakeEntry(data={const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
                            const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
                            **(extra or {})}, entry_id=entry_id)
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    feed(coord, CYCLE_NOW)

    async def noop(*_a, **_k):
        return None

    coord._fetch_tibber_prices = noop
    coord._fetch_weather_forecast = noop
    coord._fetch_solar_forecast = noop
    return coord


def feed(coord, now):
    from datetime import timedelta
    coord._prices = [
        {"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
         "starts_at": (now + timedelta(hours=h - 2)).isoformat(), "level": "NORMAL"}
        for h in range(50)]
    coord._weather_forecast = [
        {"datetime": (now + timedelta(hours=h)).isoformat(), "temperature": -5.0,
         "wind_speed": 3.0, "precipitation": 0.0, "humidity": 85.0}
        for h in range(48)]


def inline_worker(tags):
    """Replace coordinator._await_process with an in-process twin.

    Same pickle round trip both ways as _run_in_process, on the executor
    thread, so the solve is countable by in-process hooks. The coroutine-side
    caller path is captured at submission (``tags`` list) and exposed on
    ``TAG`` for the executor-side counters.
    """
    import pickle
    from heatpump_optimizer import coordinator as cm

    async def ap(hass, fn, *args):
        tag = caller_path()
        tags.append((tag, getattr(fn, "__qualname__", str(fn))))

        def job():
            TAG[0] = tag + "|" + getattr(fn, "__qualname__", "?")
            f2, a2 = pickle.loads(pickle.dumps((fn, args), protocol=pickle.HIGHEST_PROTOCOL))
            out = f2(*a2)
            return pickle.loads(pickle.dumps(out, protocol=pickle.HIGHEST_PROTOCOL))
        return await hass.async_add_executor_job(job)

    old = cm._await_process
    cm._await_process = ap
    return lambda: setattr(cm, "_await_process", old)


TAG = [""]


ENTITY_PROPS = ("available", "state", "native_value", "is_on", "current_temperature",
                "target_temperature", "hvac_mode", "hvac_action", "preset_mode",
                "extra_state_attributes", "icon", "native_unit_of_measurement",
                "name", "unique_id", "device_info", "entity_category")


async def setup_entities(hass, coord):
    """Every platform's entities, through the real async_setup_entry."""
    import importlib
    added = []

    def add(entities, *_a, **_k):
        for e in entities:
            e.hass = hass
        added.extend(entities)

    coord.entry.runtime_data = coord
    for plat in ("sensor", "binary_sensor", "button", "climate", "switch", "datetime"):
        mod = importlib.import_module(f"heatpump_optimizer.{plat}")
        await mod.async_setup_entry(hass, coord.entry, add)
    return added


def write_states(entities, as_json=False):
    """What HA reads on the loop when a coordinator update writes each state."""
    import json
    nbytes = 0
    for e in entities:
        attrs = None
        for p in ENTITY_PROPS:
            try:
                v = getattr(e, p, None)
            except Exception:  # noqa: BLE001 - an unavailable sensor may raise
                v = None
            if p == "extra_state_attributes":
                attrs = v
        if as_json and attrs:
            nbytes += len(json.dumps(attrs, default=str))
    return nbytes


def ref_ms(k: int = 5) -> float:
    """Median process-CPU ms of tests/stress.py:reference_solve over k calls."""
    import statistics
    import stress
    return statistics.median(stress.reference_solve()[1] for _ in range(k))
