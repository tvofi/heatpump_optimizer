#!/usr/bin/env python3
"""P7 detector: every production seam that does wall-clock datetime arithmetic
across a DST transition, enumerated at run time from the real coordinator cycle.

METRIC (one line): `wrong_sites` = distinct production source lines (file:line)
at which a datetime subtraction, or a datetime + timedelta, executed on the
real coordinator cycle returned a duration different from the true (UTC)
duration between the same two instants.

COUNT KEY: the value production computes -- the timedelta a `-` returns, or the
true elapsed seconds between the operand and the result of a `+` -- compared
against `b.timestamp() - a.timestamp()`. The key is never an attribute of the
operands, so a fix that normalises to UTC (or adds in UTC) moves it and a
fix that only relabels a tzinfo does not.

HOW: `homeassistant.util.dt` (the hastub) is wrapped so every datetime it hands
production -- now(), utcnow(), as_local(), as_utc(), parse_datetime() -- is a
`TracedDatetime`, a datetime subclass whose `__sub__/__rsub__/__add__/__radd__`
record the innermost `custom_components/heatpump_optimizer/*.py` frame and the
error against the UTC truth. CPython 3.8+ keeps the subclass through `+`,
`-timedelta`, `replace`, `astimezone`, so values derived from the clock stay
traced. A datetime that production builds itself (datetime.fromisoformat of a
stored string) is untraced; arithmetic between two such values is the
detector's blind spot, printed as a RESULT (`untraced_note`).
Naive datetimes are judged as local wall times (HA's own reading of a naive
value); a naive UTC value would be a false positive, so each site carries the
category it was seen in (aware-shared-zone / naive / add).

DRIVER: tests/replay.py's shape, in-process: the committed replay day
(tests/replay/synthetic-dhw-only.json) shifted by dst_fixture.py onto the
2026 spring and autumn Europe/Stockholm transition days, the clock frozen at
every cycle instant (30 min), the real `_async_update_data`, and a read of
every entity of every platform. The process worker is substituted by an
in-process run_worker, exactly as the replay lane does.

CLOCK ARMS (--clock):
  zoneinfo  dt_util.now() carries the process-wide ZoneInfo instance, which is
            what Home Assistant hands an integration (the production truth).
  fixed     dt_util.now() carries the fixed-offset tzinfo that
            datetime.fromisoformat gives -- what tests/replay.py:run_fixture
            freezes (`dt_util.freeze(t)` with `t = _ts(...)`).

COMMAND (repository root; HASTUB_TZ is set by the harness before the stub loads):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
    /home/claude/venv314/bin/python tools/audit/round9/D14/s4/p7_dst_seams.py
  options: --day spring|autumn|plain|all (default all)  --clock zoneinfo|fixed
           --root <tree>  (import production + tests/harness from another tree,
           e.g. a pre-fix worktree; the fixture always comes from this tree)
           --reintroduce  (one-line re-introduction, in memory: coordinator.
           _utc_age_seconds subtracts the raw datetimes again -- #1299's shape)
           --steps N (cycles per day, default all 48)

EXPECTED at baseline 1936d5ca (see REPORT.md for the executed values):
  plain day: wrong_sites=0 (null control)
  zoneinfo clock, spring+autumn: wrong_sites>0; fixed clock: fewer (replay's blind spot)
  --reintroduce: wrong_sites rises by the coordinator age seams.
Tolerance: exact integers (no float from BLAS enters the count; contention-immune).
Machine: Linux container, 4 cores, python 3.14 (box B9).
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ["HASTUB_TZ"] = "Europe/Stockholm"

import argparse
import asyncio
import importlib
import io
import json
import sys
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument("--day", default="all")
ap.add_argument("--clock", default="zoneinfo", choices=("zoneinfo", "fixed"))
ap.add_argument("--root", default=".")
ap.add_argument("--reintroduce", action="store_true")
ap.add_argument("--steps", type=int, default=0)
ap.add_argument("--json", default="")
ap.add_argument("--arm", default="base", choices=("base", "tariff"),
                help="tariff: add a capacity tariff with an off-peak mask so tariff.window_factors is reached")
ap.add_argument("--fix-grid", action="store_true",
                help="perturbation: _forecast_arrays measures step_offset in UTC (one-line edit, in memory)")
ARGS = ap.parse_args()
ROOT = Path(ARGS.root).resolve()
sys.path[:0] = [str(ROOT / "tests" / "hastub"), str(ROOT / "tests"),
                str(ROOT / "custom_components"), str(HERE)]

import numpy as np  # noqa: E402,F401  (after the thread pin)

from homeassistant.util import dt as dt_util  # noqa: E402

import dst_fixture  # noqa: E402

ZONE = dt_util.DEFAULT_TIME_ZONE
assert isinstance(ZONE, ZoneInfo), "HASTUB_TZ did not take"
PKG = os.sep + "heatpump_optimizer" + os.sep
REC: dict[tuple, dict] = {}
UNTRACED = {"plain_plain": 0}
SKEW: list[float] = []


def _site():
    f = sys._getframe(1)
    while f is not None and f.f_code.co_filename == __file__:
        f = f.f_back
    # the first frame outside this harness is the one that did the arithmetic
    if f is not None and PKG in f.f_code.co_filename and "custom_components" in f.f_code.co_filename:
        return (Path(f.f_code.co_filename).name, f.f_lineno, f.f_code.co_name)
    return None


def _local_ts(x: datetime) -> float:
    if x.tzinfo is None:  # HA reads a naive value as local wall time
        return datetime.timestamp(datetime.replace(x, tzinfo=ZONE))
    return datetime.timestamp(x)


_QUIET = [0]  # >0 while a stdlib conversion runs: zoneinfo.fromutc adds internally


def _note(kind: str, err_s: float, crossing: bool):
    if _QUIET[0]:
        return
    site = _site()
    if site is None:
        return
    r = REC.setdefault(site + (kind,), {"hits": 0, "crossing": 0, "wrong": 0, "max_err_s": 0.0})
    r["hits"] += 1
    r["crossing"] += int(crossing)
    if abs(err_s) > 1e-6:
        r["wrong"] += 1
        r["max_err_s"] = max(r["max_err_s"], abs(err_s))


def _judge_sub(a: datetime, b: datetime, res: timedelta):
    if a.tzinfo is None and b.tzinfo is None:
        kind = "naive"
    elif a.tzinfo is not None and a.tzinfo is b.tzinfo and isinstance(a.tzinfo, ZoneInfo):
        kind = "aware-shared-zone"
    else:
        return  # differing tzinfo objects subtract in UTC: correct by construction
    true = _local_ts(a) - _local_ts(b)
    crossing = datetime.utcoffset(datetime.replace(a, tzinfo=ZONE)) != datetime.utcoffset(
        datetime.replace(b, tzinfo=ZONE)) if kind == "naive" else a.utcoffset() != b.utcoffset()
    _note(kind, res.total_seconds() - true, crossing)


def _judge_add(a: datetime, delta: timedelta, res: datetime):
    if a.tzinfo is None:
        kind = "add-naive"
    elif isinstance(a.tzinfo, ZoneInfo):
        kind = "add-shared-zone"
    else:
        return
    true = _local_ts(res) - _local_ts(a)
    _note(kind, true - delta.total_seconds(), abs(true - delta.total_seconds()) > 1e-6)


class TracedDatetime(datetime):
    def __sub__(self, other):
        res = datetime.__sub__(self, other)
        if isinstance(other, datetime) and res is not NotImplemented:
            _judge_sub(self, other, res)
        elif isinstance(other, timedelta) and res is not NotImplemented:
            _judge_add(self, -other, res)
        return res

    def __rsub__(self, other):
        if isinstance(other, datetime):
            res = datetime.__sub__(other, self)
            if res is not NotImplemented:
                _judge_sub(other, self, res)
            return res
        return NotImplemented

    def __add__(self, other):
        res = datetime.__add__(self, other)
        if isinstance(other, timedelta) and res is not NotImplemented:
            _judge_add(self, other, res)
        return res

    __radd__ = __add__

    # ZoneInfo.fromutc does `dt + offset` on the subclass from C; that is the
    # conversion itself, not production arithmetic, so it is not recorded.
    def astimezone(self, tz=None):
        _QUIET[0] += 1
        try:
            return datetime.astimezone(self, tz)
        finally:
            _QUIET[0] -= 1

    @classmethod
    def fromtimestamp(cls, ts, tz=None):
        _QUIET[0] += 1
        try:
            return super().fromtimestamp(ts, tz)
        finally:
            _QUIET[0] -= 1

    @classmethod
    def now(cls, tz=None):
        _QUIET[0] += 1
        try:
            return super().now(tz)
        finally:
            _QUIET[0] -= 1


def T(x):
    if isinstance(x, datetime) and not isinstance(x, TracedDatetime):
        return TracedDatetime(x.year, x.month, x.day, x.hour, x.minute, x.second,
                              x.microsecond, x.tzinfo, fold=x.fold)
    return x


# --- wrap the stub's clock so every datetime it hands production is traced ----
_orig = {n: getattr(dt_util, n) for n in ("now", "utcnow", "as_local", "as_utc", "parse_datetime")
         if hasattr(dt_util, n)}
for _n, _f in _orig.items():
    setattr(dt_util, _n, (lambda f: (lambda *a, **k: T(f(*a, **k))))(_f))


def freeze_at(t: datetime):
    if ARGS.clock == "zoneinfo":
        dt_util.freeze(TracedDatetime.fromtimestamp(t.timestamp(), ZONE))
    else:  # tests/replay.py's freeze: the fixed offset fromisoformat gives
        dt_util.freeze(T(t))


class InProcessWorker:
    """tests/replay.py:InProcessWorker, copied (it does not exist at pre-fix trees)."""

    def __init__(self) -> None:
        worker = self

        class Pipe(io.BytesIO):
            def flush(self) -> None:
                job = self.getvalue()
                self.seek(0)
                self.truncate()
                if job:
                    worker.serve(job)

        self.stdin = Pipe()
        self.stdout = io.BytesIO()

    def poll(self):
        return None

    def serve(self, job: bytes) -> None:
        from types import SimpleNamespace
        from heatpump_optimizer import process_worker

        reply = io.BytesIO()
        saved = sys.stdin, sys.stdout
        sys.stdin = SimpleNamespace(buffer=io.BytesIO(job))
        sys.stdout = SimpleNamespace(buffer=reply)
        try:
            process_worker.run_worker()
        finally:
            sys.stdin, sys.stdout = saved
        self.stdout.seek(0)
        self.stdout.truncate()
        self.stdout.write(reply.getvalue())
        self.stdout.seek(0)


def _at(rows, t):
    chosen = None
    for row in rows:
        if row[0] <= t:
            chosen = row
        else:
            break
    return chosen


def run_day(day: str) -> dict:
    from harness import FakeEntry, FakeHass, FakeState
    import heatpump_optimizer as integration
    from heatpump_optimizer import const
    from heatpump_optimizer import coordinator as cm

    fx = dst_fixture.build(day, HERE.parents[5])  # sweep/P7 wrapper: one dir deeper than D14/s4
    rows = {}
    for eid, rr in fx["states"].items():
        attrs, out = {}, []
        for updated, state, maybe, reported in rr:
            if maybe is not None:
                attrs = maybe
            out.append((datetime.fromisoformat(updated), state, attrs,
                        datetime.fromisoformat(reported) if reported else None))
        rows[eid] = out
    data, options = dict(fx["entry"]["data"]), dict(fx["entry"]["options"])
    if ARGS.arm == "tariff":
        options.update({"peak_tariff_enabled": True, "peak_tariff_price_per_kw": 60.0,
                        "peak_tariff_peaks_averaged": 3, "peak_tariff_window_minutes": 60,
                        "peak_tariff_hours": "07:00-20:00", "peak_tariff_weekdays_only": False,
                        "peak_tariff_offpeak_factor": 0.0, "peak_tariff_months": "Jan-Dec"})
    config = {**data, **options}
    start = datetime.fromisoformat(fx["window"]["start"])
    end = datetime.fromisoformat(fx["window"]["end"])
    step = timedelta(minutes=int(config.get(const.CONF_OPTIMIZATION_INTERVAL, 30)))

    worker = InProcessWorker()
    cm._ensure_worker = lambda: worker
    if ARGS.reintroduce:
        # One-line re-introduction of #1299's shape: the shared age helper
        # subtracts the two datetimes as handed (a shared ZoneInfo -> wall clock).
        cm._utc_age_seconds = lambda now, then: (now - then).total_seconds()

    if ARGS.fix_grid and not getattr(cm, "_P7_FIXED", False):
        import inspect, textwrap
        src = textwrap.dedent(inspect.getsource(cm.HeatPumpOptimizerCoordinator._forecast_arrays))
        old = "(now - midnight).total_seconds()"
        assert src.count(old) == 1, "the grid seam moved; re-anchor --fix-grid"
        src = src.replace(old, "(dt_util.as_utc(now) - dt_util.as_utc(midnight)).total_seconds()")
        ns: dict = {}
        exec(compile(src, cm.__file__, "exec"), cm.__dict__, ns)
        cm.HeatPumpOptimizerCoordinator._forecast_arrays = ns["_forecast_arrays"]
        cm._P7_FIXED = True
    # The consequence probe on the worst seam: where the price/weather grid's
    # step 0 lands against the solve anchor the plan is labelled with.
    real_ps = cm.HeatPumpOptimizerCoordinator._price_series
    if not getattr(real_ps, "_p7", False) and hasattr(cm, "_solve_anchor") and hasattr(cm, "_utc_step_starts"):
        def _ps(self, n_steps, midnight, step_offset):
            first = cm._utc_step_starts(midnight, 1, step_offset)[0]
            anchor = cm._solve_anchor(dt_util.now())
            SKEW.append((datetime.timestamp(first) - datetime.timestamp(anchor)) / 60.0)
            return real_ps(self, n_steps, midnight, step_offset)
        _ps._p7 = True
        cm.HeatPumpOptimizerCoordinator._price_series = _ps

    hass = FakeHass()
    weather_id = config.get(const.CONF_WEATHER_ENTITY)

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
    coord = cm.HeatPumpOptimizerCoordinator(hass, entry)
    entry.runtime_data = coord
    entities: list = []
    for platform in integration.PLATFORM_LIST:
        mod = importlib.import_module(f"heatpump_optimizer.{platform}")
        asyncio.run(mod.async_setup_entry(hass, entry, entities.extend))

    cycles = errors = 0
    t = start
    while t < end and (not ARGS.steps or cycles < ARGS.steps):
        freeze_at(t)
        for eid in fx["inputs"]:
            row = _at(rows.get(eid, []), t)
            if row is None:
                continue
            updated, state, attrs, reported = row
            lr = min(t, reported) if reported else updated
            hass.states.set(eid, FakeState(state, last_updated=T(updated.astimezone(timezone.utc)),
                                           last_reported=T(lr.astimezone(timezone.utc)),
                                           attributes=attrs))
        try:
            coord.data = asyncio.run(coord._async_update_data())
            coord.last_update_success = True
        except Exception as err:  # noqa: BLE001
            errors += 1
            if errors <= 3:
                print(f"  cycle {t.isoformat()}: {type(err).__name__}: {err}", file=sys.stderr)
        for e in entities:
            for attr in ("available", "native_value", "extra_state_attributes", "is_on",
                         "hvac_action", "hvac_mode", "current_temperature"):
                try:
                    getattr(e, attr, None)
                except Exception:  # noqa: BLE001
                    pass
        cycles += 1
        t += step
    dt_util.freeze(None)
    return {"cycles": cycles, "cycle_errors": errors, "entities": len(entities)}


def main() -> int:
    days = list(dst_fixture.DAYS) if ARGS.day == "all" else ARGS.day.split(",")
    began_cpu, began = time.process_time(), time.monotonic()
    per_day = {}
    for day in days:
        REC_before = {k: dict(v) for k, v in REC.items()}
        SKEW.clear()
        info = run_day(day)
        skewed = [x for x in SKEW if abs(x) > 1e-6]
        print(f"RESULT {day}_grid_skewed_cycles={len(skewed)}_of_{len(SKEW)} count")
        print(f"RESULT {day}_grid_skew_max_min={max((abs(x) for x in SKEW), default=0):.0f} minutes")
        wrong = sorted({k[:2] + (k[3],) for k, v in REC.items()
                        if v["wrong"] > REC_before.get(k, {}).get("wrong", 0)})
        per_day[day] = {**info, "wrong_sites": len(wrong)}
        print(f"RESULT {day}_cycles={info['cycles']} count")
        print(f"RESULT {day}_cycle_errors={info['cycle_errors']} count")
        print(f"RESULT {day}_wrong_sites={len(wrong)} count")
    reached = sorted({k[:2] for k in REC})
    wrong = sorted({k for k, v in REC.items() if v["wrong"]})
    print("# every arithmetic site reached (file:line func kind hits crossing wrong max_err_s):")
    for k, v in sorted(REC.items()):
        flag = "WRONG" if v["wrong"] else ("cross" if v["crossing"] else "")
        print(f"#  {k[0]}:{k[1]} {k[2]} {k[3]} hits={v['hits']} crossing={v['crossing']} "
              f"wrong={v['wrong']} max_err_s={v['max_err_s']:.0f} {flag}")
    print(f"RESULT clock={ARGS.clock}")
    print(f"RESULT arm={ARGS.arm}")
    print(f"RESULT reintroduce={int(ARGS.reintroduce)}")
    print(f"RESULT sites_reached={len(reached)} count")
    print(f"RESULT wrong_sites={len({k[:2] for k in wrong})} count")
    for kind in ("aware-shared-zone", "naive", "add-shared-zone", "add-naive"):
        print(f"RESULT wrong_sites_{kind}={len({k[:2] for k in wrong if k[3] == kind})} count")
    print("RESULT untraced_note=plain-plain_arithmetic_on_production_built_datetimes_not_seen")
    pc, wall = time.process_time() - began_cpu, time.monotonic() - began
    tc = time.thread_time()
    print(f"RESULT wall_s={wall:.1f} s provisional")
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = sum(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin"))
    except OSError:
        sw = -1
    print(f"RESULT swapins={sw}")
    if ARGS.json:
        Path(ARGS.json).write_text(json.dumps({"per_day": per_day, "sites": [
            {"file": k[0], "line": k[1], "func": k[2], "kind": k[3], **v} for k, v in sorted(REC.items())]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
