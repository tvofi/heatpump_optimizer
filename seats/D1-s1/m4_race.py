"""D1.M4 executor-boundary race harness, round 11, seat D1-s1.

Two parts, on a real asyncio loop with a ThreadPoolExecutor (rl.RealHass):

Part A (C2, aliasing): with the process worker forced unusable, the
in-process fallback hands `optimize_in_process(optimizer, inputs)` to the
executor. While that solve is held at its entry, every mutable object and
ndarray buffer reachable from (optimizer, inputs) is matched against every one
reachable from the coordinator; then every loop-side writer of the table below
runs, and the solve's inputs are fingerprinted again.
  RESULT shared_mutable_objects = objects (or overlapping ndarray buffers)
         reachable from both the in-flight fallback job and the coordinator.
  RESULT torn_inputs = fingerprint changes of the job's inputs across the writers.

Part B (C1, per line of `enumerate.py d1-solve-state`): a solve is put in flight
(`--origin debounced`: through `async_request_refresh`, the path every user
writer and the setup/first solve use; `--origin direct`: through
`async_refresh`, the scheduled interval's path), held in the process route, and
the line's loop-side writer runs; the solve is released and the loop settles.
  honoured = a `_solve_record` built after the write, before the loop settles.
  changed  = the builder's output for that line differs before/after the write.
  RESULT stale_plan_rows = rows with changed=1 and honoured=0 (the published
         plan was built on the pre-write value and nothing re-plans it).
Count key: `_solve_record` entries (wrapped, production body runs) after the
write; `changed` compares the builder's own return value on the loop.

Run:   PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/s1/m4_race.py [--origin debounced|direct] [--perturb-rerun] [--part A|B|AB]
Expect: Part A shared_mutable_objects=1 (inputs.forecast.pv_surplus IS coordinator._pv_surplus;
        both sides only rebind it), torn_inputs=0; positive control --control-inplace: torn_inputs=1.
        Part B --origin debounced: stale_request_refresh_rows=7 of 8 (stale_plan_rows=10; the other
        3 are the power-event and pv-export rows, which no writer re-plans by design);
        --origin direct (null control): 0 of 8 (stale_plan_rows=3). Exact.
        Census: D1_CENSUS_DIR=dev/audit/rounds/round11/D1/s1 (the committed enumerator output).
Perturbation (--perturb-rerun): `async_request_refresh` records the #1754
        re-run when a solve is in flight (one line in the coordinator):
        stale_request_refresh_rows (debounced) 7 -> 0.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B4 container, linux x86_64.
"""
from __future__ import annotations

import os
import sys

for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rl  # noqa: E402

import argparse  # noqa: E402
import asyncio  # noqa: E402
import dataclasses  # noqa: E402
import hashlib  # noqa: E402
import logging  # noqa: E402
import pickle  # noqa: E402
import subprocess  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402
import types  # noqa: E402
from datetime import timedelta  # noqa: E402

import numpy as np  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

import heatpump_optimizer as integ  # noqa: E402
from heatpump_optimizer import boost, const, coordinator as cm, manual_plan  # noqa: E402

logging.basicConfig(level=logging.ERROR)


def census(universe):
    d = os.environ.get("D1_CENSUS_DIR")
    if d:
        return open(os.path.join(d, universe + ".txt")).read().splitlines()
    return subprocess.run([sys.executable, "tools/audit/enumerate.py", universe],
                          capture_output=True, text=True, check=True).stdout.splitlines()


CENSUS = census("d1-solve-state")

# ---- the solve gate (process route) and the forced fallback
GATE = threading.Event()
GATE.set()
IN_SOLVE = threading.Event()
FORCE_UNAVAILABLE = {"on": False}
_orig_run = cm._run_in_process


def _gated(fn, args):
    if fn is cm.optimize_in_process:
        if FORCE_UNAVAILABLE["on"]:
            raise cm.ProcessWorkerUnavailable("harness: worker forced unavailable")
        IN_SOLVE.set()
        GATE.wait(120)
    return _orig_run(fn, args)


cm._run_in_process = _gated

RECORDS: list[float] = []
_orig_record = cm.HeatPumpOptimizerCoordinator._solve_record


def _counted_record(self, *a, **k):
    RECORDS.append(time.monotonic())
    return _orig_record(self, *a, **k)


cm.HeatPumpOptimizerCoordinator._solve_record = _counted_record


def price_state():
    t0 = dt_util.now().replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
    rows = [{"start": (t0 + timedelta(hours=h)).isoformat(), "value": 0.5 + 0.4 * ((h % 12) / 12)}
            for h in range(48)]
    return rl.FakeState("0.6", attributes={"raw_today": rows, "unit_of_measurement": "SEK/kWh"})


def states():
    return {
        "sensor.indoor": rl.FakeState("21.0"), "sensor.outdoor": rl.FakeState("-3.0"),
        "sensor.price": price_state(), "sensor.humidity": rl.FakeState("45"),
        "sensor.house_power": rl.FakeState("1.5", attributes={"unit_of_measurement": "kW"}),
        "sensor.hp_power": rl.FakeState("0.8", attributes={"unit_of_measurement": "kW"}),
        "sensor.dhw": rl.FakeState("50.0"), "person.me": rl.FakeState("home"),
        "calendar.holiday": rl.FakeState("off"), "sensor.export": rl.FakeState("0.30"),
        "binary_sensor.fire": rl.FakeState("off"),
        "select.hp_mode": rl.FakeState("auto", attributes={"options": ["auto", "heat", "dhw", "off"]}),
    }


CONFIG = {
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor", const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_ENTITY, const.CONF_PRICE_ENTITY: "sensor.price",
    const.CONF_DHW_TANK_VOLUME: 180.0, const.CONF_DHW_TEMP_ENTITY: "sensor.dhw",
    const.CONF_HOUSE_POWER_ENTITY: "sensor.house_power", "heat_pump_power_entity": "sensor.hp_power",
    const.CONF_PEAK_TARIFF_ENABLED: True, const.CONF_PEAK_TARIFF_PRICE: 45.0,
    const.CONF_PEAK_GUARD_ENABLED: True, const.CONF_FUSE_GUARD_ENABLED: True,
    const.CONF_PV_ENABLED: True, const.CONF_PV_PEAK_KW: 6.0, const.CONF_PV_EXPORT_PRICE_ENTITY: "sensor.export",
    const.CONF_AWAY_PRESENCE_ENTITY: "person.me", const.CONF_HOLIDAY_CALENDAR_ENTITY: "calendar.holiday",
    const.CONF_EXTERNAL_HEAT_ENABLED: True, const.CONF_EXTERNAL_HEAT_ENTITY: "binary_sensor.fire",
    const.CONF_COMFORT_LEARNING_ENABLED: True, const.CONF_CAPACITY_CURVE_ENABLED: True,
    const.CONF_CONFIDENCE_MARGINS_ENABLED: True, const.CONF_MOLD_GUARD_ENABLED: True,
    const.CONF_INDOOR_HUMIDITY_ENTITY: "sensor.humidity",
    const.CONF_SOLAR_APERTURE_LEARNING_ENABLED: True, const.CONF_INTERNAL_GAINS_LEARNING_ENABLED: True,
    const.CONF_HEAT_PUMP_MODE_ENTITY: "select.hp_mode",
}


# ---- writers: each is a production loop-side writer of what the line reads
async def w_cycle(co, hass, changes):
    """The scheduled interval's cycle, after the inputs it reads changed."""
    for eid, st in changes.items():
        hass.states.set(eid, st)
    await co.async_refresh()


async def w_away(co, hass):
    await co.async_set_away(not co._away_state.override_active)


async def w_economy(co, hass):
    await co.async_set_mode(const.MODE_ECONOMY)


async def w_manual(co, hass):
    now = dt_util.now()
    o = manual_plan.build_override(
        dhw_slots=None,
        space_slots=[{"start": (now + timedelta(hours=1)).isoformat(),
                      "end": (now + timedelta(hours=3)).isoformat()}],
        expires_at=now + timedelta(hours=8), now=now)
    await co.async_apply_manual_plan(o)


async def w_boost(co, hass):
    await boost.set_channel(co, "space", True)


async def seed_comfort(co, hass):
    for _ in range(12):
        co.record_setpoint_override(23.0)


async def w_reset_comfort(co, hass):
    """The Reset Comfort Weight button: the reset, then the press's refresh (button.py)."""
    await co.async_reset_comfort_weight()
    await co.async_request_refresh()


async def w_reset_heatloss(co, hass):
    await co.async_reset_heat_loss_learners()


async def w_power_event(co, hass):
    st = rl.FakeState("9.5", attributes={"unit_of_measurement": "kW"}, last_updated=dt_util.now())
    ev = type("E", (), {"data": {"entity_id": "sensor.house_power", "new_state": st,
                                 "old_state": hass.states.get("sensor.house_power")}})()
    hass.states.set("sensor.house_power", st)
    co._on_power_event(ev)


async def w_state_event(co, hass, changes):
    """A state change as Home Assistant delivers it: the state, then every listener on it."""
    for eid, st in changes.items():
        old = hass.states.get(eid)
        hass.states.set(eid, st)
        ev = type("E", (), {"data": {"entity_id": eid, "old_state": old, "new_state": st}})()
        for ids, act in list(getattr(hass, "state_listeners", [])):
            if eid in ids:
                act(ev)
    await asyncio.sleep(0.2)  # a listener's refresh request is a task


async def w_state_only(co, hass, changes):
    """A state change of an entity the record reads through hass, with no listener."""
    for eid, st in changes.items():
        hass.states.set(eid, st)


def _kw(v):
    return rl.FakeState(v, attributes={"unit_of_measurement": "kW"}, last_updated=dt_util.now())


CYCLE_INPUTS = {
    "sensor.house_power": _kw("4.5"), "sensor.humidity": rl.FakeState("78"),
    "sensor.dhw": rl.FakeState("41.0"), "binary_sensor.fire": rl.FakeState("on"),
    "select.hp_mode": rl.FakeState("dhw", attributes={"options": ["auto", "heat", "dhw", "off"]}),
    "sensor.outdoor": rl.FakeState("-9.0"),
}

#: line name -> (writer kind, writer)
WRITERS = {
    "_accuracy": ("cycle", lambda co, h: w_cycle(co, h, CYCLE_INPUTS)),
    "_away_state": ("request_refresh", w_away),
    "_baseline_house_load": ("cycle", lambda co, h: w_cycle(co, h, CYCLE_INPUTS)),
    "_capacity_tariff": ("options", None),  # config and the calendar month; an options save reloads
    "_comfort_weight": ("request_refresh", w_reset_comfort),
    "_dhw_plan_fields": ("cycle", lambda co, h: w_cycle(co, h, CYCLE_INPUTS)),
    "_effective_cycling_cost": ("cycle", lambda co, h: w_cycle(co, h, CYCLE_INPUTS)),
    "_external_heat_active": ("cycle", lambda co, h: w_cycle(co, h, CYCLE_INPUTS)),
    "_floor_widening": ("request_refresh", w_economy),
    "_model_corrections": ("cycle", lambda co, h: w_cycle(co, h, CYCLE_INPUTS)),
    "_outage_dhw_hold": ("cycle", lambda co, h: w_cycle(co, h, CYCLE_INPUTS)),
    "_outage_recovery_active": ("cycle", lambda co, h: w_cycle(co, h, CYCLE_INPUTS)),
    "_peak_guard": ("event", w_power_event),
    "_peak_tracker": ("event", w_power_event),
    # Writers that ask for a re-plan (async_request_refresh) are the rows the
    # stale count keys on: kinds request_refresh and state_listener.
    "_pv_export_price": ("state", lambda co, h: w_state_event(co, h, {"sensor.export": rl.FakeState("1.10")})),
    "hass": ("state_listener", lambda co, h: w_state_event(co, h, {"calendar.holiday": rl.FakeState("on")})),
    "_capacity_caps": ("cycle", lambda co, h: w_cycle(co, h, CYCLE_INPUTS)),
    "_confidence_margins": ("cycle", lambda co, h: w_cycle(co, h, CYCLE_INPUTS)),
    "_current_action": ("cycle", lambda co, h: w_cycle(co, h, CYCLE_INPUTS)),
    "_external_heat_forecast": ("cycle", lambda co, h: w_cycle(co, h, CYCLE_INPUTS)),
    "_fuse_kw": ("options", None),  # only an options save writes it, and that reloads the entry
    "_manual_pins": ("request_refresh", w_manual),
    "_mode": ("request_refresh", w_economy),
    "_mold_floor_series": ("cycle", lambda co, h: w_cycle(co, h, CYCLE_INPUTS)),
    "_pump_signals": ("cycle", lambda co, h: w_cycle(co, h, CYCLE_INPUTS)),
    "_solve_hubs": ("request_refresh", w_away),
}


def probe(co, name):
    """What the line's reader takes from ``name``, computed on the loop now."""
    now = dt_util.now()
    try:
        hz = co._forecast_arrays(now)
        n = len(hz.prices)
        rec = _orig_record(co, cm.plan_step_start(now), hz)
    except Exception as err:  # noqa: BLE001
        return f"err:{err!r}"
    fields = {
        "config": dataclasses.asdict(rec.config) if dataclasses.is_dataclass(rec.config) else vars(rec.config),
        "params": dataclasses.asdict(rec.params) if dataclasses.is_dataclass(rec.params) else vars(rec.params),
        "state": dataclasses.asdict(rec.inputs.state),
        "limits": dataclasses.asdict(rec.inputs.limits),
        "ext": rec.inputs.forecast.external_heat_kw,
        "running": rec.inputs.compressor_running,
    }
    try:
        own = getattr(co, name) if name != "hass" else None
        if callable(own):
            own = {"_baseline_house_load": lambda: own(n), "_dhw_plan_fields": lambda: own(now),
                   "_model_corrections": lambda: own(now), "_outage_dhw_hold": lambda: own(now),
                   "_outage_recovery_active": lambda: own(now), "_confidence_margins": lambda: own(n),
                   "_external_heat_forecast": lambda: own(n), "_mold_floor_series": lambda: own(hz.outdoor_temps),
                   "_capacity_caps": lambda: own(hz.outdoor_temps, hz.humidity, cm.ThermalModel(rec.params)),
                   "_manual_pins": lambda: own(cm.plan_step_start(now), n),
                   "_solve_hubs": lambda: None,
                   }.get(name, own)()
        fields["own"] = own
    except Exception as err:  # noqa: BLE001
        fields["own"] = f"err:{err!r}"
    return hashlib.sha1(pickle.dumps(_plain(fields), protocol=4)).hexdigest()


def _plain(o, depth=0):
    if depth > 6:
        return repr(type(o))
    if isinstance(o, np.ndarray):
        return ("nd", o.shape, o.tobytes())
    if isinstance(o, dict):
        return {str(k): _plain(v, depth + 1) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_plain(v, depth + 1) for v in o]
    if dataclasses.is_dataclass(o) and not isinstance(o, type):
        return _plain(dataclasses.asdict(o), depth + 1)
    if isinstance(o, (int, float, str, bool, type(None))):
        return o
    if hasattr(o, "__dict__"):
        return _plain({k: v for k, v in vars(o).items() if not callable(v)}, depth + 1)
    return repr(o)


async def setup():
    hass = rl.RealHass(states())
    entry = rl.RecordingEntry(data=CONFIG)
    assert await rl.harness.ha_setup_entry(integ, hass, entry)
    co = entry.runtime_data
    t = time.time()
    while not RECORDS or getattr(co, "_last_optimization", None) is None:
        await asyncio.sleep(0.05)
        if time.time() - t > 120:
            raise RuntimeError("first solve did not complete")
    await settle(co)
    co._debounced_refresh.cooldown = 0.3  # the drop happens while executing; the cooldown only paces the wait
    await asyncio.sleep(0.6)
    return hass, entry, co


async def settle(co, quiet=1.0, timeout=120.0):
    t = time.time()
    last = len(RECORDS)
    still = time.time()
    while time.time() - t < timeout:
        await asyncio.sleep(0.1)
        busy = co._optimization_running or co._debounced_refresh._executing \
            or co._debounced_refresh._timer_task is not None
        if len(RECORDS) != last or busy:
            last, still = len(RECORDS), time.time()
        elif time.time() - still >= quiet:
            return


SEEDS = {"_comfort_weight": seed_comfort}


async def race_row(name, origin, perturb):
    kind, writer = WRITERS[name]
    cls = cm.HeatPumpOptimizerCoordinator
    if perturb:
        # The perturbation is the coordinator's own async_request_refresh recording
        # the #1754 re-run while a solve is in flight. Patched on the class before
        # setup, because listeners capture the bound method at construction.
        base = cls.async_request_refresh

        async def request_refresh(self):
            if self._optimization_running:
                self._optimization_rerun_requested = True
            await base(self)
        cls.async_request_refresh = request_refresh
    try:
        hass, entry, co = await setup()
    finally:
        if perturb:
            pass
    if name in SEEDS:
        await SEEDS[name](co, hass)
    try:
        if writer is None:
            return {"kind": kind, "changed": 0, "honoured": 0, "note": "no loop-side writer outside an options reload"}
        GATE.clear()
        IN_SOLVE.clear()
        flight = hass.async_create_task(
            co.async_request_refresh() if origin == "debounced" else co.async_refresh())
        ok = await asyncio.to_thread(IN_SOLVE.wait, 60)
        if not ok:
            GATE.set()
            return {"kind": kind, "changed": -1, "honoured": -1, "note": "no solve went in flight"}
        await co._resolve_away()  # what a solve resolves first; done alike before both probes
        before = probe(co, name)
        t_write = time.monotonic()
        wtask = hass.async_create_task(writer(co, hass))
        await asyncio.wait([wtask], timeout=30)  # the write lands; the solve is still held
        writer_done = wtask.done()
        held = not GATE.is_set() and co._optimization_running
        await co._resolve_away()
        after = probe(co, name)
        GATE.set()
        await asyncio.wait([flight, wtask], timeout=120)
        await settle(co)
        honoured = sum(1 for t in RECORDS if t > t_write)
        final = probe(co, name)
        note = f"writer_exc={wtask.exception()!r}" if wtask.done() and wtask.exception() else ""
        if not writer_done:
            note += " writer-still-awaiting-at-30s"
        if not held:
            note += " solve-not-held-at-write"
        return {"kind": kind, "changed": int(before != after), "honoured": honoured, "note": note}
    finally:
        GATE.set()
        await rl.ha_unload_faithful(integ, hass, entry)
        hass.executor.shutdown(wait=False)
        if perturb:
            cls.async_request_refresh = base


# ---- Part A
def mutables(root, skip_ids=(), limit=400000):
    """id -> path of mutable containers / dataclass instances, plus ndarray buffers."""
    out, bufs = {}, []
    seen = set(skip_ids)
    stack = [(root, "root", 0)]
    while stack and len(seen) < limit:
        o, path, d = stack.pop()
        if id(o) in seen:
            continue
        seen.add(id(o))
        if isinstance(o, (types.ModuleType, type, types.FunctionType, types.BuiltinFunctionType,
                          types.MethodType, str, bytes, int, float, bool, type(None),
                          asyncio.AbstractEventLoop, threading.Thread)):
            continue
        if isinstance(o, np.ndarray):
            base = o
            while isinstance(base.base, np.ndarray):
                base = base.base
            if o.nbytes:
                p = o.__array_interface__["data"][0]
                bufs.append((p, p + o.nbytes, path))
            continue
        if isinstance(o, (list, dict, set, bytearray)):
            out[id(o)] = path
        elif hasattr(o, "__dict__") or dataclasses.is_dataclass(o):
            if not (dataclasses.is_dataclass(o) and getattr(type(o), "__dataclass_params__").frozen):
                out[id(o)] = path
        if d > 9:
            continue
        if isinstance(o, dict):
            for k, v in list(o.items()):
                stack.append((v, f"{path}[{k!r}]"[:200], d + 1))
        elif isinstance(o, (list, tuple, set, frozenset)):
            for i, v in enumerate(list(o)[:5000]):
                stack.append((v, f"{path}[{i}]", d + 1))
        else:
            try:
                attrs = vars(o)
            except TypeError:
                attrs = {f.name: getattr(o, f.name, None) for f in dataclasses.fields(o)} \
                    if dataclasses.is_dataclass(o) else {}
            for k, v in list(attrs.items()):
                stack.append((v, f"{path}.{k}", d + 1))
    return out, bufs


SHARED: list = []
TORN: list = []


async def part_a(control_inplace=False):
    hass, entry, co = await setup()
    job = {}
    held = threading.Event()
    release = threading.Event()
    orig_add = hass.async_add_executor_job

    async def add(func, *args):
        if func is cm.optimize_in_process and "fp0" not in job:
            # Only the first fallback job is held and fingerprinted: a re-run the
            # writers record (#1754) is a second job and must not overwrite it.
            def run():
                job["fp0"] = _fingerprint(args)
                job["args"] = args
                held.set()
                release.wait(120)
                job["fp1"] = _fingerprint(args)
                return func(*args)
            return await orig_add(run)
        return await orig_add(func, *args)
    hass.async_add_executor_job = add
    FORCE_UNAVAILABLE["on"] = True
    try:
        flight = hass.async_create_task(co.async_run_optimization())
        assert await asyncio.to_thread(held.wait, 60), "fallback solve not reached"
        jm, jb = mutables(job["args"])
        cmut, cb = mutables(co, skip_ids={id(hass), id(entry), id(job["args"])})
        for i, p in jm.items():
            if i in cmut:
                SHARED.append((p, cmut[i]))
        for lo, hi, p in jb:
            for clo, chi, cp in cb:
                if lo < chi and clo < hi:
                    SHARED.append((p, cp))
                    break
        if control_inplace and getattr(co, "_pv_surplus", None) is not None:
            shared_buf = co._pv_surplus
            print(f"INFO control: same object={shared_buf is job['args'][1].forecast.pv_surplus} "
                  f"shape={getattr(shared_buf, 'shape', None)}")
            shared_buf += 1.0  # positive control: an in-place write to the one shared buffer
        for name, (kind, writer) in WRITERS.items():
            if writer is None:
                continue
            try:
                await asyncio.wait_for(writer(co, hass), 30)
            except Exception as err:  # noqa: BLE001
                job.setdefault("writer_errs", []).append(f"{name}: {err!r}")
        release.set()
        await asyncio.wait([flight], timeout=120)
        print(f"INFO fingerprints {job.get('fp0')} {job.get('fp1')}")
        if job.get("fp0") != job.get("fp1"):
            TORN.append("inputs fingerprint moved")
        return len(jm), len(jb), len(cmut), len(cb), job.get("writer_errs", [])
    finally:
        FORCE_UNAVAILABLE["on"] = False
        release.set()
        await settle(co)
        await rl.ha_unload_faithful(integ, hass, entry)
        hass.executor.shutdown(wait=False)


def _fingerprint(args):
    return hashlib.sha1(pickle.dumps(_plain(args), protocol=4)).hexdigest()


async def main_async(a):
    rows = []
    if "A" in a.part:
        na = await part_a(a.control_inplace)
        print(f"INFO part A: job mutables={na[0]} job buffers={na[1]} coordinator mutables={na[2]} coordinator buffers={na[3]}")
        for e in na[4]:
            print(f"INFO part A writer error: {e}")
        for s in SHARED:
            print(f"SHARED job {s[0]} <-> coordinator {s[1]}")
        print(f"RESULT shared_mutable_objects={len(SHARED)} count")
        print(f"RESULT torn_inputs={len(TORN)} count")
    if "B" in a.part:
        cache = {}
        for line in CENSUS:
            reader, attr = line.split()
            if a.only and attr.replace("self.", "") not in a.only.split(","):
                continue
            name = attr.replace("self.", "")
            key = name
            if key not in cache or a.per_line:
                cache[key] = await race_row(name, a.origin, a.perturb_rerun)
            r = cache[key]
            rows.append((line, r))
            print(f"ROW kind={r['kind']:<15} changed={r['changed']} honoured={r['honoured']} | {line} {r['note']}")
        stale = [l for l, r in rows if r["changed"] == 1 and r["honoured"] == 0]
        rr = [l for l, r in rows if r["kind"] in ("request_refresh", "state_listener")]
        print(f"RESULT rows={len(rows)} lines")
        print(f"RESULT stale_plan_rows={len(stale)} lines (origin={a.origin}, perturb_rerun={a.perturb_rerun})")
        print(f"RESULT stale_request_refresh_rows={sum(1 for l in stale if l in rr)} of {len(rr)} lines")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--origin", choices=("debounced", "direct"), default="debounced")
    ap.add_argument("--perturb-rerun", action="store_true")
    ap.add_argument("--part", default="AB")
    ap.add_argument("--per-line", action="store_true", help="re-race a name shared by both readers")
    ap.add_argument("--control-inplace", action="store_true",
                    help="Part A positive control: mutate the shared pv_surplus buffer in place mid-solve")
    ap.add_argument("--only", default="", help="comma-separated names to race (default: every line)")
    a = ap.parse_args()
    t0, p0 = time.thread_time(), time.process_time()
    asyncio.run(main_async(a))
    cm._shutdown_process_pool()
    rl.env_results(t0, p0)


if __name__ == "__main__":
    main()
