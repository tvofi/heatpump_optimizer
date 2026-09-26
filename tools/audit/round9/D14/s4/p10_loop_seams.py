#!/usr/bin/env python3
"""P10 detector: every production seam that holds the GIL in Home Assistant's
process long enough to starve the event loop, on the real coordinator cycle.

METRIC (one line): `seams` = distinct production functions that, on a real
asyncio loop with a real ThreadPoolExecutor and the real process worker, run
>= HOLD_MS of CPU inside ONE loop-thread handle or ONE executor job (the unit
the loop cannot preempt), attributed to the innermost heatpump_optimizer frame
by a 1 ms stack sampler.

COUNT KEY: thread CPU (`time.thread_time`) of the loop thread per
`asyncio.events.Handle._run`, and of the executor thread per submitted job --
what production spends holding the GIL in HA's process -- never the job's
declared route. A solve that the process worker carries costs the executor
thread only the pickle transport, so a fix that moves work to the worker
moves the count; one that renames the route does not.

RATIO METRIC (contention-immune): `starved_share` = sum of 1 ms heartbeat gaps
> 5 ms / cycle wall, against the idle-loop null arm measured in the same run.

DRIVER: the committed replay day (tests/replay/synthetic-dhw-only.json, plain
January day, no DST), every 30 min for --cycles cycles: the clock frozen, the
recorded inputs set, `await coord._async_update_data()` on ONE persistent loop,
then every entity of every platform read on the loop (as HA's state writer
does). FakeHass's inline executor and its create_task-that-closes are replaced
by the loop's own (the README trap: FakeHass measures nothing about the
executor boundary). The worker is the real child (`_ensure_worker`).

ARMS (--arm):
  worker    as shipped (default)
  fallback  perturbation: `_ensure_worker` raises ProcessWorkerUnavailable, so `_await_optimize`
            degrades to optimize_in_process on the executor thread (#511's
            degrade, capped by WORKER_FALLBACK_CAP #783) -- the class's
            original shape re-introduced in one line, in memory.
COMMAND (repository root):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
    /home/claude/venv314/bin/python tools/audit/round9/D14/s4/p10_loop_seams.py [--arm fallback] [--cycles N]
  --root <tree>: run from that tree's root instead (a pre-fix export); the
  fixture always comes from this harness's tree.
EXPECTED: see REPORT.md. Counts of seams are exact given HOLD_MS; CPU ms and
starved_share are provisional (re-taken in the quiet window).
Machine: Linux container, 4 cores, python 3.14 (box B9).
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import asyncio
import asyncio.events
import importlib
import json
import sys
import threading
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--arm", default="worker", choices=("worker", "fallback"))
ap.add_argument("--cycles", type=int, default=12)
ap.add_argument("--hold-ms", type=float, default=10.0)
ap.add_argument("--json", default="")
ap.add_argument("--naive-clock", action="store_true",
                help="feed naive local datetimes (trees older than the aware clock, e.g. pre-#290)")
ap.add_argument("--config", default="fixture", choices=("fixture", "rich"),
                help="rich: space heating on (mode select) plus coord_all_features' options")
ARGS = ap.parse_args()
HERE = Path(__file__).resolve().parent
FIXTURE = HERE.parents[4] / "tests/replay/synthetic-dhw-only.json"
sys.path[:0] = [str(Path("tests/hastub").resolve()), str(Path("tests").resolve()),
                str(Path("custom_components").resolve())]

import numpy as np  # noqa: E402,F401

from homeassistant.util import dt as dt_util  # noqa: E402

PKG = os.sep + "heatpump_optimizer" + os.sep
MAIN = threading.main_thread().ident
HOLD = ARGS.hold_ms / 1000.0

# ---- attribution: a 1 ms sampler over the loop thread and executor threads ----
_active: dict[int, object] = {}  # thread ident -> current unit key (handle / job)
_samples: dict[tuple, dict] = defaultdict(lambda: defaultdict(int))  # unit -> {func: n}
_stop = threading.Event()


def _prod_frame(frame):
    inner = None
    f = frame
    while f is not None:
        fn = f.f_code.co_filename
        if PKG in fn and "custom_components" in fn and "process_worker" not in fn:
            inner = f"{Path(fn).name}:{f.f_code.co_qualname}"
            break
        f = f.f_back
    return inner


SAMPLER_CPU = [0.0]


def _sampler():
    try:
        _sampler_loop()
    finally:
        SAMPLER_CPU[0] = time.thread_time()


def _sampler_loop():
    while not _stop.is_set():
        time.sleep(0.001)
        frames = sys._current_frames()
        for ident, unit in list(_active.items()):
            fr = frames.get(ident)
            if fr is not None:
                who = _prod_frame(fr)
                if who:
                    _samples[unit][who] += 1


UNITS: list[dict] = []  # every unit over HOLD: thread, cpu_s, attributed func


def _close_unit(thread: str, unit, cpu: float, label: str):
    if cpu >= HOLD and CYCLE[0] >= 0:  # setup (imports, platform setup) is not a cycle
        s = _samples.get(unit, {})
        top = max(s.items(), key=lambda kv: kv[1])[0] if s else f"(unattributed) {label}"
        UNITS.append({"thread": thread, "cpu_ms": cpu * 1000.0, "func": top, "label": label,
                      "cycle": CYCLE[0]})
    _samples.pop(unit, None)


CYCLE = [-1]
_real_run = asyncio.events.Handle._run


def _timed_run(self):
    if threading.get_ident() != MAIN:
        return _real_run(self)
    unit = ("loop", id(self), time.perf_counter_ns())
    _active[MAIN] = unit
    t0 = time.thread_time()
    try:
        return _real_run(self)
    finally:
        cpu = time.thread_time() - t0
        _active.pop(MAIN, None)
        if cpu >= HOLD:
            cb = getattr(self, "_callback", None)
            label = repr(getattr(cb, "__self__", cb))[:120]
        else:
            label = ""
        _close_unit("loop", unit, cpu, label)


asyncio.events.Handle._run = _timed_run


JOBS: list = []  # (wall start, wall end, func qualname, cpu s) of every executor job


def _job(func, args):
    ident = threading.get_ident()
    unit = ("exec", ident, time.perf_counter_ns())
    _active[ident] = unit
    t0 = time.thread_time()
    w0 = time.perf_counter()
    try:
        return func(*args)
    finally:
        cpu = time.thread_time() - t0
        _active.pop(ident, None)
        _close_unit("executor", unit, cpu, getattr(func, "__qualname__", repr(func)))
        JOBS.append((w0, time.perf_counter(), getattr(func, "__qualname__", repr(func)), cpu, CYCLE[0]))
        EXEC_CPU[0] += cpu


EXEC_CPU = [0.0]


def _at(rows, t):
    chosen = None
    for row in rows:
        if row[0] <= t:
            chosen = row
        else:
            break
    return chosen


BEATS: list = []  # (end, gap) of every heartbeat during the cycles


async def heartbeat(gaps: list, stop: asyncio.Event):
    last = time.perf_counter()
    while not stop.is_set():
        await asyncio.sleep(0.001)
        now = time.perf_counter()
        gaps.append(now - last)
        if CYCLE[0] >= 0:
            BEATS.append((now, now - last))
        last = now


async def drive() -> dict:
    from harness import FakeEntry, FakeHass, FakeState
    import heatpump_optimizer as integration
    from heatpump_optimizer import const
    from heatpump_optimizer import coordinator as cm

    loop = asyncio.get_running_loop()
    pool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="hass-exec")
    if ARGS.arm == "fallback":
        def _refuse():
            raise cm.ProcessWorkerUnavailable("p10 perturbation: the worker cannot start")
        cm._ensure_worker = _refuse

    fx = json.loads(FIXTURE.read_text())
    from zoneinfo import ZoneInfo
    _tz = ZoneInfo(fx.get("time_zone") or "UTC")

    def _d(raw):
        v = datetime.fromisoformat(raw)
        return v.astimezone(_tz).replace(tzinfo=None) if ARGS.naive_clock else v
    rows = {}
    for eid, rr in fx["states"].items():
        attrs, out = {}, []
        for updated, state, maybe, reported in rr:
            if maybe is not None:
                attrs = maybe
            out.append((_d(updated), state, attrs, _d(reported) if reported else None))
        rows[eid] = out
    data, options = dict(fx["entry"]["data"]), dict(fx["entry"]["options"])
    if ARGS.config == "rich":
        options.update({"peak_tariff_enabled": True, "peak_tariff_price_per_kw": 45.0,
                        "pv_enabled": True, "pv_peak_kw": 8.0, "pv_export_price": 0.3,
                        "away_enabled": True, "external_heat_detection_enabled": True,
                        "comfort_learning_enabled": True, "system_identification_enabled": True,
                        "compressor_cycling_cost": 0.5})
        mode = "select.heat_pump_operating_mode"
        rows[mode] = [(r[0], "Heating + hot water", r[2], r[3]) for r in rows[mode]]
    hass = FakeHass()
    tasks: list = []

    async def _exec(func, *args):
        return await loop.run_in_executor(pool, _job, func, args)

    hass.async_add_executor_job = _exec
    hass.async_add_import_executor_job = _exec
    hass.async_create_task = lambda coro, *a, **k: tasks.append(loop.create_task(coro)) or tasks[-1]
    hass.loop = loop
    weather_id = data.get(const.CONF_WEATHER_ENTITY)

    async def forecasts(call):
        now = dt_util.now()
        rs = rows.get(weather_id, [])
        out = []
        for h in range(48):
            t = now + timedelta(hours=h)
            row = next((r for r in reversed(rs) if r[0] <= t), rs[0] if rs else None)
            if row is None:
                break
            a = row[2]
            out.append({"datetime": t.isoformat(), "temperature": a.get("temperature"),
                        "wind_speed": a.get("wind_speed", 0.0),
                        "precipitation": a.get("precipitation", 0.0), "condition": row[1]})
        return {weather_id: {"forecast": out}} if out else {}

    if weather_id:
        hass.services.async_register("weather", "get_forecasts", forecasts)
    entry = FakeEntry(data=data, options=options)
    if hasattr(entry, "async_create_background_task"):
        entry.async_create_background_task = (
            lambda h, coro, *a, **k: tasks.append(loop.create_task(coro)) or tasks[-1])
    coord = cm.HeatPumpOptimizerCoordinator(hass, entry)
    entry.runtime_data = coord
    if not getattr(cm, "_entity_price_source", lambda c: False)({**data, **options}):
        # a tree older than the price-entity source: tests/replay.py's Tibber
        # substitution -- the price fetch answers from the recorded price entity
        price_id = fx.get("price_series_entity") or data.get("price_entity")

        async def recorded_prices() -> None:
            now = dt_util.now()
            day0 = now.replace(hour=0, minute=0, second=0, microsecond=0)
            out, t = [], day0
            while t < day0 + timedelta(days=2 if now.hour >= 13 else 1):
                row = _at(rows.get(price_id, []), t)
                if row is not None:
                    out.append({"total": float(row[1]), "starts_at": t.isoformat(), "level": "NORMAL"})
                t += timedelta(minutes=15)
            coord._prices = out

        coord._fetch_tibber_prices = recorded_prices
    entities: list = []
    for platform in integration.PLATFORM_LIST:
        mod = importlib.import_module(f"heatpump_optimizer.{platform}")
        await mod.async_setup_entry(hass, entry, entities.extend)

    # null arm: the idle loop, same process, same moment
    gaps: list = []
    stop = asyncio.Event()
    hb = loop.create_task(heartbeat(gaps, stop))
    await asyncio.sleep(1.0)
    idle = list(gaps)
    gaps.clear()

    start = _d(fx["window"]["start"])
    step = timedelta(minutes=30)
    per_cycle = []
    t = start
    failures = 0
    for c in range(ARGS.cycles):
        CYCLE[0] = c
        dt_util.freeze(t)
        for eid in fx["inputs"]:
            row = _at(rows.get(eid, []), t)
            if row is None:
                continue
            updated, state, attrs, reported = row
            lr = min(t, reported) if reported else updated
            hass.states.set(eid, FakeState(state, last_updated=updated, last_reported=lr,
                                           attributes=attrs))
        gaps.clear()
        w0 = time.perf_counter()
        try:
            coord.data = await coord._async_update_data()
            coord.last_update_success = True
        except Exception as err:  # noqa: BLE001
            failures += 1
            print(f"# cycle {c}: {type(err).__name__}: {str(err)[:160]}", file=sys.stderr)
        await asyncio.sleep(0)
        for e in entities:  # HA's state writer reads these on the loop
            for attr in ("available", "native_value", "extra_state_attributes", "is_on",
                         "hvac_action", "hvac_mode", "current_temperature"):
                try:
                    getattr(e, attr, None)
                except Exception:  # noqa: BLE001
                    pass
        await asyncio.sleep(0.01)
        wall = time.perf_counter() - w0
        starved = sum(g for g in gaps if g > 0.005)
        per_cycle.append({"wall_s": wall, "starved_s": starved,
                          "max_gap_ms": 1000 * max(gaps, default=0.0)})
        t += step
    stop.set()
    await hb
    for tk in tasks:
        if not tk.done():
            tk.cancel()
    pool.shutdown(wait=True)
    dt_util.freeze(None)
    try:
        cm._shutdown_process_pool()
    except Exception:  # noqa: BLE001
        pass
    idle_starved = sum(g for g in idle if g > 0.005) / max(1e-9, sum(idle))
    return {"per_cycle": per_cycle, "idle_starved_share": idle_starved,
            "idle_max_gap_ms": 1000 * max(idle, default=0.0), "failures": failures,
            "entities": len(entities)}


def main() -> int:
    th = threading.Thread(target=_sampler, daemon=True)
    th.start()
    began_cpu, began = time.process_time(), time.monotonic()
    out = asyncio.run(drive())
    _stop.set()
    th.join()
    seams: dict[tuple, dict] = {}
    for u in UNITS:
        k = (u["thread"], u["func"])
        s = seams.setdefault(k, {"units": 0, "cpu_ms_total": 0.0, "cpu_ms_max": 0.0,
                                 "labels": set()})
        s["units"] += 1
        s["cpu_ms_total"] += u["cpu_ms"]
        s["cpu_ms_max"] = max(s["cpu_ms_max"], u["cpu_ms"])
        s["labels"].add(u["label"][:60])
    print(f"# units >= {ARGS.hold_ms} ms of GIL-holding CPU, by thread and innermost production frame:")
    for k, s in sorted(seams.items(), key=lambda kv: -kv[1]["cpu_ms_max"]):
        print(f"#  {k[0]:8s} {k[1]:60s} units={s['units']} max_ms={s['cpu_ms_max']:.1f} "
              f"total_ms={s['cpu_ms_total']:.1f} via={sorted(s['labels'])[:2]}")
    pc = out["per_cycle"][1:] or out["per_cycle"]  # cycle 0 pays imports/first calls
    share = sum(c["starved_s"] for c in pc) / max(1e-9, sum(c["wall_s"] for c in pc))
    # the loop's longest stall while each executor job ran: a job that holds
    # the GIL without releasing it shows here, one that yields does not
    import bisect
    ends = [b[0] for b in BEATS]
    hold_by_func: dict = {}
    for w0, w1, fn, cpu, cyc in JOBS:
        i = bisect.bisect_left(ends, w0)
        worst = 0.0
        while i < len(BEATS) and BEATS[i][0] - BEATS[i][1] <= w1:
            worst = max(worst, BEATS[i][1])
            i += 1
        h = hold_by_func.setdefault(fn, {"jobs": 0, "max_gap_ms": 0.0, "cpu_ms_max": 0.0})
        h["jobs"] += 1
        h["max_gap_ms"] = max(h["max_gap_ms"], worst * 1000.0)
        h["cpu_ms_max"] = max(h["cpu_ms_max"], cpu * 1000.0)
    print("# executor jobs: func jobs max_loop_gap_during_job_ms max_job_cpu_ms")
    for fn, h in sorted(hold_by_func.items()):
        print(f"#  {fn} jobs={h['jobs']} max_gap_ms={h['max_gap_ms']:.1f} cpu_ms_max={h['cpu_ms_max']:.1f}")
    starving_jobs = sorted(fn for fn, h in hold_by_func.items() if h["max_gap_ms"] >= 5.0 and h["cpu_ms_max"] >= ARGS.hold_ms)
    print(f"RESULT executor_funcs_starving_loop={len(starving_jobs)} count {starving_jobs}")
    loop_seams = {k for k in seams if k[0] == "loop"}
    exec_seams = {k for k in seams if k[0] == "executor"}
    print(f"RESULT arm={ARGS.arm}")
    print(f"RESULT config={ARGS.config}")
    print(f"RESULT cycles={len(out['per_cycle'])} count")
    print(f"RESULT cycle_failures={out['failures']} count")
    print(f"RESULT hold_ms={ARGS.hold_ms}")
    print(f"RESULT seams={len(seams)} count")
    print(f"RESULT loop_thread_seams={len(loop_seams)} count")
    print(f"RESULT executor_thread_seams={len(exec_seams)} count")
    print(f"RESULT max_unit_cpu_ms={max((u['cpu_ms'] for u in UNITS), default=0.0):.1f} ms provisional")
    print(f"RESULT max_loop_unit_cpu_ms={max((u['cpu_ms'] for u in UNITS if u['thread'] == 'loop'), default=0.0):.1f} ms provisional")
    print(f"RESULT starved_share={share:.4f} ratio provisional")
    print(f"RESULT null_idle_starved_share={out['idle_starved_share']:.4f} ratio provisional")
    print(f"RESULT max_gap_ms={max(c['max_gap_ms'] for c in pc):.1f} ms provisional")
    print(f"RESULT null_idle_max_gap_ms={out['idle_max_gap_ms']:.1f} ms provisional")
    print(f"RESULT executor_cpu_s={EXEC_CPU[0]:.2f} s provisional")
    total_cpu = time.process_time() - began_cpu
    # deliberate threads: the executor jobs and the sampler; residual factor as the README asks
    main_cpu = time.thread_time()
    print(f"RESULT deliberate_thread_cpu_s={EXEC_CPU[0] + SAMPLER_CPU[0]:.2f} s provisional (executor jobs + sampler)")
    resid = (total_cpu - EXEC_CPU[0] - SAMPLER_CPU[0]) / main_cpu if main_cpu else 1.0
    print(f"RESULT thread_factor={resid:.3f}")
    print(f"RESULT wall_s={time.monotonic() - began:.1f} s provisional")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=" + str(sum(int(l.split()[1]) for l in open("/proc/vmstat")
                                      if l.startswith("pswpin"))))
    if ARGS.json:
        Path(ARGS.json).write_text(json.dumps({"units": UNITS, **out}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
