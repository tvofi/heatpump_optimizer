"""D1.M1 real-loop lifecycle harness, round 11, seat D1-s1.

Metric: per line of `enumerate.py d1-lifecycle`, whether the call site ran
under a real-loop lifecycle (setup -> first refresh -> background solve ->
reload mid-solve -> unload mid-solve -> setup again -> stored away override
carried across a restore then resolved -> HA stop) and, after each teardown,
how many live registrations / tasks / executor futures registered at that
site still reach the torn-down coordinator (gc referents), plus escaped
exceptions and whether each new instance's first cycle completes.

Also C3: the count of `HeatPumpOptimizerCoordinator.async_shutdown` runs per
unload and the actuator writes / store saves made inside the unload, under
`tests/harness.py:ha_unload_entry` (the suite's instrument) against
`rl.ha_unload_faithful` (Home Assistant's `_async_process_on_unload` order:
popped LIFO, a returned coroutine scheduled and awaited).
Count key: `async_shutdown` entries counted by a wrapper on the class method
(production's own body runs); writes = `hass.services.calls` appended during
the unload; saves = `homeassistant.helpers.storage.SAVE_COUNTS` delta.

Run:   PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/s1/m1_lifecycle.py [--unload faithful|harness|harness_awaiting]
       (an export carrying macOS ._* files breaks enumerate.py; then set
       D1_CENSUS_DIR to a directory holding d1-lifecycle.txt, the enumerator's
       output on a clean tree)
Expect (faithful): RESULT census_lines_ran=41, leaks_total=0, escaped_exceptions=0,
       first_cycle_ok=3 of 3, resolve_after_restore=None, shutdown_runs_per_unload=2,
       dropped_coroutines=0, unload_saves=12; (harness): shutdown_runs_per_unload=1,
       dropped_coroutines=3, unload_saves=9; exact.
Positive control (the leak detector): `--perturb-leak` makes running_signal.detach a
       no-op; leaks_total 0 -> >0 and the torn-down coordinators stay alive.
Perturbation (C3): `--unload harness_awaiting` is ha_unload_entry with the one-line
       repair (await a callback's returned awaitable): shutdown_runs_per_unload
       1 -> 2 and dropped_coroutines 3 -> 0 against `--unload harness`.
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
import ast  # noqa: E402
import asyncio  # noqa: E402
import gc  # noqa: E402
import logging  # noqa: E402
import subprocess  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402
import warnings  # noqa: E402
import weakref  # noqa: E402
from datetime import timedelta  # noqa: E402

from homeassistant.const import EVENT_HOMEASSISTANT_STOP  # noqa: E402
from homeassistant.helpers import storage  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

import heatpump_optimizer as integ  # noqa: E402
from heatpump_optimizer import (  # noqa: E402
    away, const, coordinator as cm, early_cutoff, pump_arbiter, running_signal,
)

rl.patch_imported(cm, pump_arbiter, running_signal, away, early_cutoff)

PKG = "custom_components/heatpump_optimizer/"

# ---- census spans: enumerate.py line -> (file, first line, last line)
def census(universe):
    """The enumerator's lines; ``D1_CENSUS_DIR/<universe>.txt`` when the export
    carries files the enumerator cannot parse (macOS ``._*`` AppleDouble)."""
    d = os.environ.get("D1_CENSUS_DIR")
    if d:
        return open(os.path.join(d, universe + ".txt")).read().splitlines()
    return subprocess.run([sys.executable, "tools/audit/enumerate.py", universe],
                          capture_output=True, text=True, check=True).stdout.splitlines()


CENSUS = census("d1-lifecycle")


def spans():
    out = {}
    trees = {}
    for line in CENSUS:
        parts = line.split()
        if parts[0] == "entry":
            out[line] = ("entry", parts[1], None)
            continue
        f, ln = parts[1].rsplit(":", 1)
        ln = int(ln)
        if f not in trees:
            trees[f] = ast.parse(open(f, encoding="utf-8").read())
        end = ln
        for n in ast.walk(trees[f]):
            if isinstance(n, ast.Call) and n.lineno == ln:
                end = max(end, n.end_lineno)
        out[line] = (parts[0], f.split("custom_components/")[-1], (ln, end))
    return out


SPANS = spans() if CENSUS else {}

# ---- instrumentation
GATE = threading.Event()
GATE.set()
IN_SOLVE = threading.Event()
_orig_run = cm._run_in_process
FORCE_UNAVAILABLE = {"on": False}


def _gated(fn, args):
    if fn is cm.optimize_in_process:
        IN_SOLVE.set()
        GATE.wait(60)
    if FORCE_UNAVAILABLE["on"]:
        raise cm.ProcessWorkerUnavailable("harness: worker forced unavailable")
    return _orig_run(fn, args)


cm._run_in_process = _gated

SHUTDOWNS = []
_orig_shutdown = cm.HeatPumpOptimizerCoordinator.async_shutdown


async def _counted_shutdown(self):
    SHUTDOWNS.append(id(self))
    return await _orig_shutdown(self)


cm.HeatPumpOptimizerCoordinator.async_shutdown = _counted_shutdown

_orig_file = cm.HeatPumpOptimizerCoordinator._file_lead_predictions


def _counted_file(self, *a, **k):
    # On the instance, never keyed by id(): a collected coordinator's id is reused.
    self._d1s1_solves = getattr(self, "_d1s1_solves", 0) + 1
    return _orig_file(self, *a, **k)


cm.HeatPumpOptimizerCoordinator._file_lead_predictions = _counted_file

from heatpump_optimizer import legionella as _leg  # noqa: E402
_orig_tc = _leg.LegionellaGuard.async_track_cycle


async def _site_tc(self, *a, **k):
    rl.SITES.append(("async_track_cycle", rl._site(2)))
    return await _orig_tc(self, *a, **k)


_leg.LegionellaGuard.async_track_cycle = _site_tc

ENTRY_CALLS = {}
for _name in ("async_setup", "async_setup_entry", "async_unload_entry",
              "async_update_options", "async_migrate_entry", "async_remove_entry"):
    _f = getattr(integ, _name, None)
    if _f is None:
        continue

    def _mk(f, name):
        async def w(*a, **k):
            ENTRY_CALLS[name] = ENTRY_CALLS.get(name, 0) + 1
            return await f(*a, **k)
        return w
    setattr(integ, _name, _mk(_f, _name))


class Errs(logging.Handler):
    def __init__(self):
        super().__init__(logging.DEBUG)
        self.records = []
        self.warns = []

    def emit(self, record):
        if record.levelno >= logging.ERROR:
            self.records.append(record)
        elif record.name.startswith("heatpump_optimizer") and (
                record.levelno >= logging.WARNING or "price" in record.getMessage().lower()):
            self.warns.append(f"{record.levelname} {record.getMessage()[:150]}")


ERRS = Errs()
logging.getLogger().addHandler(ERRS)
logging.getLogger().setLevel(logging.WARNING)
logging.getLogger("heatpump_optimizer").setLevel(logging.DEBUG)
LOOP_EXC = []


def price_state():
    t0 = dt_util.now().replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
    rows = [{"start": (t0 + timedelta(hours=h)).isoformat(),
             "end": (t0 + timedelta(hours=h + 1)).isoformat(),
             "value": 0.5 + 0.4 * ((h % 12) / 12)} for h in range(48)]
    return rl.FakeState("0.6", attributes={"raw_today": rows, "unit_of_measurement": "SEK/kWh"})


STATES = {
    "sensor.indoor": rl.FakeState("21.0"),
    "sensor.outdoor": rl.FakeState("-3.0"),
    "sensor.dhw": rl.FakeState("unavailable"),
    "sensor.house_power": rl.FakeState("1.5", attributes={"unit_of_measurement": "kW"}),
    "sensor.hp_power": rl.FakeState("0.8", attributes={"unit_of_measurement": "kW"}),
    "switch.hp": rl.FakeState("on", last_updated=dt_util.now() - timedelta(hours=2)),
    "binary_sensor.defrost": rl.FakeState("off"),
    "person.me": rl.FakeState("home"),
    "calendar.holiday": rl.FakeState("off"),
    "select.hp_mode": rl.FakeState("auto", attributes={"options": ["auto", "heat", "dhw", "off"]}),
}
CONFIG = {
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_ENTITY,
    const.CONF_PRICE_ENTITY: "sensor.price",
    const.CONF_DHW_TANK_VOLUME: 180.0,
    const.CONF_DHW_TEMP_ENTITY: "sensor.dhw",
    const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.hp",
    const.CONF_HEAT_PUMP_DEFROST_ENTITY: "binary_sensor.defrost",
    const.CONF_PEAK_GUARD_ENABLED: True,
    const.CONF_HOUSE_POWER_ENTITY: "sensor.house_power",
    "heat_pump_power_entity": "sensor.hp_power",
    const.CONF_AWAY_PRESENCE_ENTITY: "person.me",
    const.CONF_HOLIDAY_CALENDAR_ENTITY: "calendar.holiday",
    const.CONF_PUMP_DUTY_MODE: "control",
    const.CONF_HEAT_PUMP_MODE_ENTITY: "select.hp_mode",
}
OPTIONS = {const.CONF_DEBUG_COLLECT: True}


async def _ha_unload_entry_awaiting(integration, hass, entry):
    """tests/harness.py:ha_unload_entry with the one-line instrument repair:
    a callback's returned awaitable is awaited (FIFO order kept as it is)."""
    import inspect
    ok = await integration.async_unload_entry(hass, entry)
    if ok:
        for cb in list(getattr(entry, "_on_unload", ())):
            if inspect.isawaitable(r := cb()):
                await r
        entry._on_unload.clear()
        if hasattr(entry, "runtime_data"):
            delattr(entry, "runtime_data")
        entry.state = rl.harness.ConfigEntryState.NOT_LOADED
    return ok


def site_hit(span, kinds_sites):
    kind, f, rng = span
    if kind == "entry":
        return ENTRY_CALLS.get(f, 0) > 0
    lo, hi = rng
    for k, s in kinds_sites:
        if not s.startswith(f + ":"):
            continue
        ln = int(s.rsplit(":", 1)[1])
        if lo <= ln <= hi:
            return True
    return False


async def settle(t=0.3):
    for _ in range(3):
        await asyncio.sleep(t / 3)


async def wait_cycle(co, since=None, timeout=90.0):
    """A solve of THIS instance completed (not a handover's restored stamp)."""
    t = time.time()
    n0 = getattr(co, "_d1s1_solves", 0) if since is not None else 0
    while time.time() - t < timeout:
        if getattr(co, "_d1s1_solves", 0) > n0:
            return True
        await asyncio.sleep(0.05)
    return False


def leaks_of(hass, entry, old_ref):
    """Live holders at each registration site that reach the torn-down coordinator."""
    old = old_ref()
    if old is None:
        return []
    out = []
    for rec in list(rl.REGISTRY.values()):
        if rl.reaches(rec["obj"], old):
            out.append((rec["kind"], rec["site"]))
    for t in list(hass.tasks):
        if not t.done() and rl.reaches(t, old):
            out.append(("task", getattr(t, "get_name", lambda: "?")()))
    for name, site, fut, job in hass.executor_jobs:
        if not fut.done() and rl.reaches(job, old):
            out.append(("executor", site))
    for ids, act in list(getattr(hass, "state_listeners", [])):
        if rl.reaches(act, old):
            out.append(("state_listener", repr(ids)))
    for kind, fn in list(hass.bus.listeners):
        if rl.reaches(fn, old):
            out.append(("bus", kind))
    loaded = getattr(entry, "runtime_data", None) is not None
    if len(entry.update_listeners) > (1 if loaded else 0):
        out.append(("update_listener", f"{len(entry.update_listeners)} live, loaded={loaded}"))
    return out


def fire_all(hass, value_for, listeners=None):
    """Call every recorded state listener once, as a state-changed event would."""
    for ids, act in list(listeners if listeners is not None else getattr(hass, "state_listeners", [])):
        for eid in ids:
            ev = type("E", (), {"data": {"entity_id": eid, "old_state": hass.states.get(eid),
                                         "new_state": rl.FakeState(value_for(eid))}})()
            try:
                act(ev)
            except Exception as err:  # noqa: BLE001
                LOOP_EXC.append(f"listener {eid}: {err!r}")


def _value(eid):
    return ("not_home" if eid.startswith("person") else
            "on" if eid.startswith(("binary_sensor", "calendar")) else
            "26.5" if eid == "sensor.indoor" else "52.0" if eid == "sensor.dhw" else
            "3.0" if eid.endswith("power") else "on" if eid.startswith("switch") else "heat")


def alive_holders(old_ref):
    """After the scenario: what (if anything) still keeps the old coordinator alive."""
    gc.collect()
    old = old_ref()
    if old is None:
        return []
    names = []
    for r in gc.get_referrers(old):
        if isinstance(r, dict):
            names.append("dict:" + ",".join(sorted(str(k) for k in list(r)[:4])))
        else:
            names.append(type(r).__name__)
    return names


async def scenario(unload_mode: str):
    loop = asyncio.get_running_loop()
    loop.set_exception_handler(lambda l, ctx: LOOP_EXC.append(ctx.get("message")))
    hass = rl.RealHass({**STATES, "sensor.price": price_state()})
    import tempfile
    tmp = tempfile.mkdtemp(prefix="d1s1-m1-")
    hass.config.path = lambda *p: os.path.join(tmp, *p)
    hass.config.time_zone = "UTC"
    from homeassistant.components import recorder as _rec
    _inst = _rec.install(hass)
    _inst.async_add_executor_job = hass.async_add_executor_job  # the recorder's pool, on the real loop

    async def reload(entry_id):
        e = hass.config_entries.async_get_entry(entry_id)
        await unload(e)
        return await rl.harness.ha_setup_entry(integ, hass, e)
    hass.config_entries.async_reload = reload

    entry = rl.RecordingEntry(data=CONFIG, options=OPTIONS)
    per_unload = []

    async def unload(e):
        n0, c0 = len(SHUTDOWNS), len(hass.services.calls)
        s0 = dict(storage.SAVE_COUNTS)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            if unload_mode == "harness":
                await rl.harness.ha_unload_entry(integ, hass, e)
            elif unload_mode == "harness_awaiting":
                await _ha_unload_entry_awaiting(integ, hass, e)
            else:
                await rl.ha_unload_faithful(integ, hass, e)
            await settle(0.2)
            gc.collect()
            dropped = sum("never awaited" in str(x.message) for x in w)
        per_unload.append({
            "shutdowns": len(SHUTDOWNS) - n0,
            "writes": [c[:2] for c in hass.services.calls[c0:]],
            "saves": sum(storage.SAVE_COUNTS.values()) - sum(s0.values()),
            "saved_keys": sorted(k.split("_entry_")[-1] for k, v in storage.SAVE_COUNTS.items() if v != s0.get(k, 0)),
            "dropped_coroutines": dropped,
        })

    leak_rows = []
    first_ok = []

    # 1. setup -> first refresh (in setup) -> background solve
    assert await rl.harness.ha_setup_entry(integ, hass, entry)
    co1 = entry.runtime_data
    first_ok.append(await wait_cycle(co1, None))
    # Drive the event-side sites on the live instance.
    fire_all(hass, _value)
    await settle(0.5)
    await co1.async_set_mode("boost", refresh=False)
    await co1.async_set_mode("auto", refresh=False)
    from heatpump_optimizer import button as button_mod, debugger as dbg
    added = []
    await button_mod.async_setup_entry(hass, entry, added.extend)
    for b in added:
        b.hass = hass
    force = next(b for b in added if type(b).__name__ == "ForceOptimizationButton")
    await force.async_press()
    col = dbg.collector_for(co1)
    if col is not None:
        try:
            await col.async_bundle(co1, {}, entry)
        except Exception as err:  # noqa: BLE001
            LOOP_EXC.append(f"bundle: {err!r}")
    await settle(0.5)
    # The cut-off's switch-off task (early_cutoff.py:326) needs a plan step whose
    # duty is space; the exemption is bypassed for this one drive so the
    # registration it makes is in the lifecycle census.
    _ex = early_cutoff._exempt
    early_cutoff._exempt = lambda *a, **k: None
    try:
        fire_all(hass, lambda eid: "27.5", [x for x in hass.state_listeners if x[0] == ["sensor.indoor"]])
    finally:
        early_cutoff._exempt = _ex
    await settle(0.5)
    del added, force, col, b
    await co1.async_set_away(True, refresh=False)

    # 2. reload mid-solve (an options save, through async_update_options)
    since = co1._last_optimization
    GATE.clear()
    IN_SOLVE.clear()
    task = hass.async_create_task(co1.async_run_optimization())
    await asyncio.to_thread(IN_SOLVE.wait, 30)
    ref1 = weakref.ref(co1)
    entry.options = {**entry.options, "price_risk_lambda": 0.1}
    await integ.async_update_options(hass, entry)
    GATE.set()
    await asyncio.wait([task], timeout=60)
    await settle(0.5)
    del co1, task
    leak_rows.append(("reload", leaks_of(hass, entry, ref1)))
    co2 = entry.runtime_data
    first_ok.append(await wait_cycle(co2, None))
    away_restored = bool(co2._away_state.override_active)

    # 3. unload mid-solve, with one in-process fallback cycle first
    FORCE_UNAVAILABLE["on"] = True
    await co2.async_refresh()
    FORCE_UNAVAILABLE["on"] = False
    stale = list(getattr(hass, "state_listeners", []))
    GATE.clear()
    IN_SOLVE.clear()
    task = hass.async_create_task(co2.async_run_optimization())
    await asyncio.to_thread(IN_SOLVE.wait, 30)
    ref2 = weakref.ref(co2)
    await unload(entry)
    # An event dispatched before the unsubscribe runs after it (queued call_soon).
    fire_all(hass, _value, stale)
    del stale
    GATE.set()
    await asyncio.wait([task], timeout=60)
    await settle(0.5)
    del co2, task
    leak_rows.append(("unload", leaks_of(hass, entry, ref2)))

    # 4. setup again -> first cycle; the stored override resolves
    assert await rl.harness.ha_setup_entry(integ, hass, entry)
    co3 = entry.runtime_data
    first_ok.append(await wait_cycle(co3, None))
    away_restored_2 = bool(co3._away_state.override_active)
    plan_away = co3.data.get("away_active") if co3.data else None
    await co3.async_set_away(False, refresh=False)
    ERRS.warns.append("---- resolve after restore")
    resolved = await co3.async_run_optimization()
    ERRS.warns.append(f"---- resolved={resolved!r} prices={len(co3._prices)} running={co3._optimization_running}")

    # 5. HA stop (the worker reap), then final unload and removal
    for fn in hass.bus.listeners_for(EVENT_HOMEASSISTANT_STOP):
        await fn(None)
    ref3 = weakref.ref(co3)
    await unload(entry)
    await integ.async_remove_entry(hass, entry)
    if hasattr(integ, "async_migrate_entry"):
        try:
            await integ.async_migrate_entry(hass, entry)
        except Exception as err:  # noqa: BLE001
            LOOP_EXC.append(f"migrate: {err!r}")
    await settle(0.5)
    del co3
    leak_rows.append(("final", leaks_of(hass, entry, ref3)))
    holders = {k: alive_holders(r) for k, r in (("reload", ref1), ("unload", ref2), ("final", ref3))}
    hass.executor.shutdown(wait=True)
    return {
        "leak_rows": leak_rows, "first_ok": first_ok, "per_unload": per_unload,
        "away_restored": (away_restored, away_restored_2), "resolved": resolved, "plan_away": plan_away,
        "holders": holders,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--unload", choices=("faithful", "harness", "harness_awaiting"), default="faithful")
    ap.add_argument("--perturb-leak", action="store_true",
                    help="positive control: running_signal.detach becomes a no-op, so the "
                         "signal's listener outlives every teardown (leaks_total must go up)")
    a = ap.parse_args()
    if a.perturb_leak:
        running_signal.detach = lambda sig: None
    t0, p0 = time.thread_time(), time.process_time()
    r = asyncio.run(scenario(a.unload))
    sites = set(rl.SITES)
    leaks_total = sum(len(x) for _, x in r["leak_rows"])
    print(f"census_lines={len(CENSUS)}")
    hit = 0
    for line in CENSUS:
        h = site_hit(SPANS[line], sites)
        hit += h
        leaks = [k for _, rows in r["leak_rows"] for k in rows
                 if SPANS[line][0] != "entry" and k[1].startswith(SPANS[line][1] + ":")
                 and SPANS[line][2][0] <= int(k[1].rsplit(":", 1)[1]) <= SPANS[line][2][1]]
        print(f"LINE {'ran ' if h else 'NOT '} leaks={len(leaks)} | {line}")
    for phase, rows in r["leak_rows"]:
        for k in rows:
            print(f"LEAK {phase}: {k}")
    for phase, h in r["holders"].items():
        print(f"ALIVE-AFTER {phase}: {h}")
    for i, u in enumerate(r["per_unload"]):
        print(f"UNLOAD {i}: {u}")
    errs = [rec.getMessage()[:160] for rec in ERRS.records]
    for e in errs:
        print("ERRLOG", e)
    for w in ERRS.warns:
        print("WARNLOG", w)
    for e in LOOP_EXC:
        print("LOOPEXC", e)
    print(f"RESULT census_lines_ran={hit} lines")
    print(f"RESULT leaks_total={leaks_total} holders")
    print(f"RESULT escaped_exceptions={len(LOOP_EXC)} count")
    print(f"RESULT error_logs={len(errs)} count")
    print(f"RESULT first_cycle_ok={sum(r['first_ok'])} of {len(r['first_ok'])}")
    print(f"RESULT away_override_restored={int(r['away_restored'][0])},{int(r['away_restored'][1])} flags")
    print(f"RESULT resolve_after_restore={r['resolved']!r} (None = solved)")
    print(f"INFO away_active published on restored instance: {r['plan_away']!r}")
    sh = [u["shutdowns"] for u in r["per_unload"]]
    print(f"RESULT shutdown_runs_per_unload={max(sh) if sh else 0} count ({a.unload}; per unload {sh})")
    print(f"RESULT dropped_coroutines={sum(u['dropped_coroutines'] for u in r['per_unload'])} count")
    print(f"RESULT unload_writes={sum(len(u['writes']) for u in r['per_unload'])} calls")
    print(f"RESULT unload_saves={sum(u['saves'] for u in r['per_unload'])} saves")
    rl.env_results(t0, p0)


if __name__ == "__main__":
    main()
