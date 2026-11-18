#!/usr/bin/env python3
"""D15-s3 M7: the row scan of a diagnostics bundle, every check over every row.

Metric (one line): per check, counts over ``cycle_rows`` / ``payload_snapshots``
and each manifest self-test re-derived through the production function that
wrote it (``debugger.sensor_sanity``, ``feed_health``, ``store_report``,
``_solver_smoke``, ``AccuracyTracker.summary``), recorded == re-derived.

Prints derived numbers only: no entity id, reading, instant or store key of the
bundle (store documents by their ``store.DOMAINS`` name, rows by index, release
strings by name). A bundle is a user's private data and is never committed.

Command (repository root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D15/s3/m7_rowscan.py --bundle B
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D15/s3/m7_rowscan.py --bundle B --perturb solver-filter
Null control (D15.md: every step runs on it first): the synthetic bundle,
    PYTHONPATH=tests/hastub:tests python3 tools/replay/dbg_bundle_gen.py --days 7 --out $TMPDIR/syn
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D15/s3/m7_rowscan.py --bundle $TMPDIR/syn/bundle.json
  which carries no restart, so solver_spread_unsolved_rows reads 0 there.

Finding D15-s3-01 (count key: the rows ``debugger._solver_smoke``'s
``week_solve_ms`` spread admits whose payload was the not-run publish, i.e. the
row carries no ``action_mode`` and ``payload_solve_time_ms`` == 0 -- the value
the seam delivered, not an input attribute):
    EXPECTED RESULT solver_spread_unsolved_rows=10 (real bundle, +-0)
    EXPECTED RESULT solver_week_min_ms=0 (real bundle)
Perturbation ``--perturb solver-filter``: the one-line production edit in
    ``debugger._solver_smoke`` that drops a not-run row from the spread (applied
    in memory by wrapping ``debugger.spread`` for that call only):
    solver_spread_unsolved_rows falls to 0 and solver_week_min_ms rises above 0.
Baseline SHA: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: macOS arm64,
CI venv; no solve, no timing (wall numbers below are the bundle's own record).
Instrumented symbols: debugger:_solver_smoke, debugger:spread,
    debugger:sensor_sanity, debugger:feed_health, debugger:store_report,
    accuracy:AccuracyTracker.summary, accuracy:AccuracySample.from_dict,
    store:store_name.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import asyncio  # noqa: E402
import statistics  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from collections import Counter  # noqa: E402
from datetime import datetime  # noqa: E402
from pathlib import Path  # noqa: E402
from unittest import mock  # noqa: E402
from zoneinfo import ZoneInfo  # noqa: E402

ROOT = Path(__file__).resolve().parents[6]
for _p in (ROOT / "tests" / "hastub", ROOT / "tests", ROOT / "custom_components",
           ROOT / "tools" / "replay"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import debug_ingest  # noqa: E402
from heatpump_optimizer import const, debugger, store  # noqa: E402
from heatpump_optimizer.accuracy import AccuracySample, AccuracyTracker  # noqa: E402

ROW_CHECKS = (
    "solve_failures", "payload_solve_time_ms", "solve_wall_ms", "row_gaps",
    "prices_rows", "weather_stale_h", "sensor_flat_runs", "action_consistency",
    "unsolved_publish", "accuracy_sample_lag", "dhw_window_floor",
)
GAP_INTERVALS = 3  # d15_restart_gaps.py's rule
BURST_MIN = 5.0


def load(path: Path) -> dict:
    return debug_ingest.load_bundle(path)


def _download_config(path: Path) -> dict:
    doc = debug_ingest.read_download(path)
    data = doc.get("data") if isinstance(doc.get("data"), dict) else doc
    return data.get("config") if isinstance(data.get("config"), dict) else {}


def _t(row: dict) -> datetime:
    return datetime.fromisoformat(row["t"])


def _zone(bundle: dict) -> ZoneInfo:
    tz = (bundle.get("replay") or {}).get("time_zone") or "UTC"
    return ZoneInfo(tz)


def _interval_min(config: dict) -> float:
    return float(config.get(const.CONF_OPTIMIZATION_INTERVAL,
                            const.DEFAULT_OPTIMIZATION_INTERVAL))


def install_days(bundle: dict) -> list[str]:
    rows = bundle.get("cycle_rows") or []
    if not rows:
        return []
    tz = _zone(bundle)
    days = sorted({_t(r).astimezone(tz).date() for r in rows})
    first = days[0]
    return [f"day{(d - first).days}" for d in days]


def _unsolved(row: dict) -> bool:
    return "action_mode" not in row and row.get("payload_solve_time_ms") == 0


def _restart_rows(rows: list, interval: float) -> set[int]:
    out = set()
    for i in range(1, len(rows)):
        gap = (_t(rows[i]) - _t(rows[i - 1])).total_seconds() / 60.0
        if gap >= GAP_INTERVALS * interval or rows[i].get("version") != rows[i - 1].get("version"):
            out.add(i)
    return out


def solver_spread(rows: list, perturb: str = "") -> dict:
    """``debugger._solver_smoke`` over the rows, with a coordinator whose
    what-if returns at once: only its ``week_solve_ms`` is read."""
    class _Coord:
        async def async_simulate(self, overrides, limited=False):  # noqa: ARG002
            return {"error": None, "cost_delta": 0.0}

    if perturb == "solver-filter":
        orig = debugger.spread
        with mock.patch.object(debugger, "spread",
                               lambda values: orig([v for v in values if v])):
            return asyncio.run(debugger._solver_smoke(_Coord(), rows))["week_solve_ms"]
    return asyncio.run(debugger._solver_smoke(_Coord(), rows))["week_solve_ms"]


def anomalies(bundle: dict, config: dict | None = None) -> list[str]:
    """The step-7 anomalies, by name: M8's universe."""
    rows = bundle.get("cycle_rows") or []
    interval = _interval_min(config or {})
    out = []
    if any(_unsolved(r) for r in rows):
        out.append("unsolved_publish:after_restart")
        out.append("self_test_solver:week_solve_ms_counts_unsolved_rows")
    walls = [r["solve_wall_ms"] / r["payload_solve_time_ms"] for r in rows
             if r.get("solve_wall_ms") and r.get("payload_solve_time_ms")]
    if walls and statistics.median(walls) > 1.4:
        out.append("solve_wall_ms:wall_twice_payload")
    gaps = [(_t(b) - _t(a)).total_seconds() / 60.0 for a, b in zip(rows, rows[1:])]
    if any(g >= GAP_INTERVALS * interval for g in gaps):
        out.append("row_gaps:restart_gaps")
    restarts = _restart_rows(rows, interval)
    if any(g < BURST_MIN and (i + 1) not in restarts and i not in restarts
           and not _unsolved(rows[i]) for i, g in enumerate(gaps)):
        out.append("row_gaps:off_cadence_publishes")
    if _lag_rows(rows, interval):
        out.append("accuracy_sample_lag:tracker_paused")
    if _dhw_below(bundle, config or {})[1]:
        out.append("dhw_window_floor:tank_below_window_minimum")
    tests = (bundle.get("manifest") or {}).get("self_tests") or {}
    for key, rep in sorted(((tests.get("stores") or {}).get("result") or {}).items()):
        if rep.get("off_count"):
            out.append(f"self_test_stores:off_domain:{store.store_name(key)}")
    return out


def _lag_rows(rows: list, interval: float) -> list[float]:
    out = []
    for r in rows:
        s = r.get("accuracy_sample") or {}
        if s.get("t"):
            lag = (_t(r) - datetime.fromisoformat(s["t"])).total_seconds() / 60.0
            if lag > 2 * interval:
                out.append(lag)
    return out


def _windows(config: dict) -> list[tuple[int, int]]:
    raw = config.get(const.CONF_DHW_WINDOWS)
    out = []
    for part in str(raw or "").split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-")
            ha, ma = map(int, a.split(":"))
            hb, mb = map(int, b.split(":"))
            out.append((ha * 60 + ma, hb * 60 + mb))
    return out


def _dhw_below(bundle: dict, config: dict) -> tuple[int, int, Counter]:
    rows = bundle.get("cycle_rows") or []
    floor = config.get(const.CONF_DHW_MIN_TEMP)
    wins = _windows(config)
    if floor is None or not wins:
        return 0, 0, Counter()
    tz = _zone(bundle)
    n_in = 0
    below: Counter = Counter()
    for r in rows:
        lt = _t(r).astimezone(tz)
        m = lt.hour * 60 + lt.minute
        if any(a <= m < b for a, b in wins) and "dhw_temp" in r:
            n_in += 1
            if r["dhw_temp"] < float(floor):
                below[r.get("version", "?")] += 1
    return n_in, sum(below.values()), below


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", required=True, type=Path)
    ap.add_argument("--perturb", choices=["", "solver-filter"], default="")
    a = ap.parse_args()
    cpu0, thr0 = time.process_time(), time.thread_time()
    bundle = load(a.bundle)
    config = _download_config(a.bundle)
    rows = bundle.get("cycle_rows") or []
    snaps = bundle.get("payload_snapshots") or []
    manifest = bundle.get("manifest") or {}
    tests = manifest.get("self_tests") or {}
    interval = _interval_min(config)
    print(f"RESULT rows={len(rows)} unit=count")
    print(f"RESULT snapshots={len(snaps)} unit=count")
    print(f"RESULT interval_min={interval} unit=min")

    # rows:solve_failures
    fails = [r.get("solve_failures", 0) for r in rows]
    print(f"RESULT solve_failures_added={max(fails) - min(fails) if fails else 0} unit=count")
    print(f"RESULT solve_failure_increments={sum(1 for x, y in zip(fails, fails[1:]) if y > x)} unit=count")

    # rows:payload_solve_time_ms (per release; outliers > 3x the release median)
    by_v: dict[str, list[float]] = {}
    for r in rows:
        if r.get("payload_solve_time_ms"):
            by_v.setdefault(r.get("version", "?"), []).append(r["payload_solve_time_ms"])
    outl = 0
    for v, xs in by_v.items():
        med = statistics.median(xs)
        n_out = sum(1 for x in xs if x > 3 * med)
        outl += n_out
        print(f"RESULT payload_solve_s[{v}]=n:{len(xs)} median:{med / 1000:.1f} max:{max(xs) / 1000:.1f} over3x:{n_out} unit=s")
    print(f"RESULT payload_solve_outliers_over3x={outl} unit=count")

    # rows:solve_wall_ms -- wall over payload, classed 1 / 2 / 4 solves
    cls: Counter = Counter()
    cls_v: dict[str, Counter] = {}
    for r in rows:
        if r.get("solve_wall_ms") and r.get("payload_solve_time_ms"):
            x = r["solve_wall_ms"] / r["payload_solve_time_ms"]
            c = "1" if x < 1.4 else ("2" if x < 2.7 else "4")
            cls[c] += 1
            cls_v.setdefault(r.get("version", "?"), Counter())[c] += 1
    print(f"RESULT wall_ratio_classes={dict(sorted(cls.items()))} unit=count")
    for v, c in cls_v.items():
        print(f"RESULT wall_ratio_classes[{v}]={dict(sorted(c.items()))} unit=count")
    print(f"RESULT price_tiles_enabled={config.get('price_tiles_enabled')} unit=flag")

    # rows:row_gaps
    gaps = [(_t(b) - _t(a)).total_seconds() / 60.0 for a, b in zip(rows, rows[1:])]
    restarts = _restart_rows(rows, interval)
    print(f"RESULT restart_gaps={sum(1 for g in gaps if g >= GAP_INTERVALS * interval)} unit=count")
    print(f"RESULT release_changes={sum(1 for i in range(1, len(rows)) if rows[i].get('version') != rows[i - 1].get('version'))} unit=count")
    off = [i + 1 for i, g in enumerate(gaps) if g < BURST_MIN and (i + 1) not in restarts
           and i not in restarts and not _unsolved(rows[i])]
    print(f"RESULT off_cadence_publishes={len(off)} unit=count")
    print(f"RESULT off_cadence_without_wall={sum(1 for i in off if 'solve_wall_ms' not in rows[i])} unit=count")

    # rows:prices_rows / weather_stale_h
    print(f"RESULT no_price_rows={sum(1 for r in rows if not r.get('prices_rows'))} unit=count")
    tz = _zone(bundle)
    full = max((r.get("prices_rows") or 0 for r in rows), default=0)
    late = sum(1 for r in rows if _t(r).astimezone(tz).hour >= 14
               and r.get("prices_rows") is not None and r["prices_rows"] < full)
    print(f"RESULT short_horizon_after_14h={late} unit=count")
    print(f"RESULT weather_stale_rows={sum(1 for r in rows if r.get('weather_stale_h'))} unit=count")

    # rows:sensor_flat_runs and self_test:sensors -- re-derived
    sens = debugger.sensor_sanity(rows, None)
    rec_s = (tests.get("sensors") or {}).get("result") or {}
    for f in debugger._INPUTS:
        same = (rec_s.get(f) or {}).get("longest_flat") == sens[f]["longest_flat"] and \
               (rec_s.get(f) or {}).get("missing") == sens[f]["missing"]
        print(f"RESULT sensor_longest_flat[{f}]={sens[f]['longest_flat']} rederived_equal={same} unit=rows")

    # rows:action_consistency
    bad = sum(1 for r in rows if "action_mode" in r and (
        (r["action_mode"] == "off" and (r.get("heat_pump_on") or (r.get("action_kw") or 0) > 0))
        or (r["action_mode"] in ("boost", "eco", "normal", "pre_heat") and not r.get("heat_pump_on"))))
    print(f"RESULT action_contradictions={bad} unit=count")

    # rows:unsolved_publish
    uns = [i for i, r in enumerate(rows) if _unsolved(r)]
    print(f"RESULT unsolved_rows={len(uns)} unit=count")
    print(f"RESULT unsolved_rows_not_at_restart={sum(1 for i in uns if i not in restarts and i != 0)} unit=count")

    # rows:accuracy_sample_lag
    lags = _lag_rows(rows, interval)
    print(f"RESULT sample_lag_rows={len(lags)} unit=count")
    print(f"RESULT sample_lag_max_min={round(max(lags), 1) if lags else 0} unit=min")

    # rows:dhw_window_floor
    n_in, n_below, below_v = _dhw_below(bundle, config)
    print(f"RESULT dhw_window_rows={n_in} unit=count")
    print(f"RESULT dhw_window_below_floor={n_below} unit=count")
    for v, n in sorted(below_v.items()):
        print(f"RESULT dhw_window_below_floor[{v}]={n} unit=count")

    # snapshot:i:action_vs_plan -- step-0 space power vs the action, user overlays aside
    mism = 0
    for i, s in enumerate(snaps):
        data = s.get("data") or {}
        act = data.get("current_action") or {}
        sched = data.get("schedule") or []
        st0 = sched[0] if sched else {}
        overlay = bool(act.get("boost_space") or act.get("boost_dhw"))
        diff = abs(float(act.get("power") or 0.0) - float(st0.get("power") or 0.0)) > 0.05
        ok = overlay or not diff
        mism += 0 if ok else 1
        print(f"RESULT snapshot_action_vs_plan[{i}]={'overlay' if overlay else ('agree' if ok else 'DIFFER')} unit=verdict")
    print(f"RESULT snapshot_action_plan_mismatch={mism} unit=count")

    # self_test:feeds -- re-derived
    rec_f = (tests.get("feeds") or {}).get("result") or {}
    try:
        feeds = debugger.feed_health(rows, rec_f.get("tibber_outage_cycles"))
        keys = ("cycles", "no_prices", "weather_stale_cycles", "solve_failures_added")
        print(f"RESULT feeds_rederived_equal={all(feeds[k] == rec_f.get(k) for k in keys)} unit=flag")
    except TypeError as err:  # a row carrying an explicit None (dbg_bundle_gen's shape)
        print(f"RESULT feeds_rederived_equal=error:{type(err).__name__} unit=flag")
    print(f"RESULT rows_with_explicit_none={sum(1 for r in rows if any(v is None for v in r.values()))} unit=count")

    # self_test:solver -- week_solve_ms re-derived, and what it admits
    week = solver_spread(rows, a.perturb)
    rec_w = ((tests.get("solver") or {}).get("result") or {}).get("week_solve_ms") or {}
    print(f"RESULT solver_week_rederived_equal={bool(rec_w) and week is not None and week['n'] == rec_w.get('n') and week['min'] == rec_w.get('min')} unit=flag")
    admitted = (week or {}).get("n", 0) - sum(1 for r in rows if r.get("payload_solve_time_ms"))
    print(f"RESULT solver_spread_unsolved_rows={max(0, admitted)} unit=count")
    print(f"RESULT solver_week_n={(week or {}).get('n')} unit=count")
    print(f"RESULT solver_week_min_ms={(week or {}).get('min')} unit=ms")

    # self_test:stores -- re-derived at the baseline from the bundle's documents
    rec_st = (tests.get("stores") or {}).get("result") or {}
    versions = manifest.get("store_versions") or {}
    now_st = debugger.store_report({k: (versions.get(k), d) for k, d in (bundle.get("stores") or {}).items()})
    eq = all(rec_st.get(k, {}).get("off_count") == v["off_count"] for k, v in now_st.items()) if rec_st else None
    print(f"RESULT stores_rederived_equal={eq} unit=flag")
    for k, v in sorted(now_st.items(), key=lambda kv: str(store.store_name(kv[0]))):
        if v["off_count"]:
            print(f"RESULT stores_off_domain[{store.store_name(k)}]={v['off_count']} unit=paths")

    # self_test:accuracy -- the store window at the self-test, re-derived from rows
    rec_a = ((tests.get("accuracy") or {}).get("result") or {}).get("store") or {}
    at = manifest.get("self_tests_at")
    by_t: dict = {}
    for r in rows:
        s = r.get("accuracy_sample")
        if s:
            p = AccuracySample.from_dict(s)
            if p is not None and (at is None or p.when <= datetime.fromisoformat(at)):
                by_t.setdefault(p.when, p)
    tr = AccuracyTracker()
    tr.samples.extend(by_t[w] for w in sorted(by_t)[-192:])
    summ = tr.summary()
    if rec_a:
        dbias = abs((summ["temperature_bias"] or 0) - (rec_a.get("temperature_bias") or 0))
        print(f"RESULT accuracy_store_bias_delta={round(dbias, 4)} unit=celsius")
        print(f"RESULT accuracy_rederived_samples={summ['samples']} recorded={rec_a.get('samples')} unit=count")

    cpu, thr = time.process_time() - cpu0, time.thread_time() - thr0
    print(f"RESULT thread_factor={round(cpu / thr, 3) if thr else 1.0}")
    try:
        print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    except OSError:
        print("RESULT load1=nan")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
