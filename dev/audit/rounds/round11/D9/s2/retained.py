#!/usr/bin/env python3
"""D9-s2 retained bytes: growth per coordinator cycle after warm-up, per root and per production file.

METRIC (D9.md "Retained bytes"): after W warm-up cycles of the real coordinator cycle
(``HeatPumpOptimizerCoordinator._async_update_data`` + an entity sweep), the slope in
bytes/cycle of (a) tracemalloc's traced memory, harness frames filtered out, between the
checkpoint at cycle W and the last (tracing starts --lead cycles before W, so wholesale
replacements of pre-trace structures are already traced at W), attributed to the innermost
``custom_components/heatpump_optimizer/*`` frame of each surviving allocation; (b) a deep
``sys.getsizeof`` of every coordinator attribute, every entity, and every container-valued
module global of each production module (``lru_cache`` sizes by ``currsize``). B4 budget:
slope x 52,560 cycles <= 10 MiB, i.e. <= 199 B/cycle. Count key: bytes alive at the
checkpoint, as the production objects hold them.

RUN:   HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D9/s2/retained.py \
         --fixture owner --cycles 900 --warmup 200 [--perturb NAME] [--json OUT]
       (the --subprocess flag re-runs itself in a child and adds the child's ru_maxrss)
PERTURBATIONS (in memory): see PERTURB below; each names the production symbol it moves.
EXPECTED: printed per run; the finding blocks quote values with tolerance.
BASELINE: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. MACHINE: printed (platform line).
Wall/CPU/RSS lines are provisional (quiet-window re-take); bytes and counts are final.
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import collections
import functools
import gc
import json
import platform
import resource
import subprocess
import sys
import time
import tracemalloc
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import _drive  # noqa: E402

PKG = "custom_components/heatpump_optimizer/"
SKIP_TYPES = (type, types.ModuleType, types.FunctionType, types.BuiltinFunctionType,
              types.MethodType, types.CodeType, types.FrameType, types.CoroutineType,
              types.GeneratorType, functools.partial)


def deep_size(obj, seen: set) -> int:
    import numpy as np
    total = 0
    stack = [obj]
    while stack:
        o = stack.pop()
        i = id(o)
        if i in seen or isinstance(o, SKIP_TYPES):
            continue
        seen.add(i)
        try:
            total += sys.getsizeof(o)
        except TypeError:
            continue
        if isinstance(o, np.ndarray):
            if o.base is not None and isinstance(o.base, np.ndarray):
                stack.append(o.base)
            continue
        if isinstance(o, (str, bytes, bytearray, int, float, complex, bool)) or o is None:
            continue
        if isinstance(o, dict):
            for k, v in o.items():
                stack.append(k); stack.append(v)
            continue
        if isinstance(o, (list, tuple, set, frozenset, collections.deque)):
            stack.extend(o)
            continue
        d = getattr(o, "__dict__", None)
        if isinstance(d, dict):
            stack.append(d)
        for cls in type(o).__mro__:
            for s in getattr(cls, "__slots__", ()) or ():
                if isinstance(s, str) and hasattr(o, s):
                    try:
                        stack.append(getattr(o, s))
                    except Exception:  # noqa: BLE001
                        pass
    return total


def worker_rss_kib(drv) -> int:
    """VmRSS of production's solving child (coordinator._PROCESS_WORKER), 0 if none.
    A long-lived child that kept per-solve state would show a rising RSS here."""
    proc = getattr(drv.cm, "_PROCESS_WORKER", None)
    pid = getattr(proc, "pid", None)
    if not pid:
        return 0
    try:
        for line in Path(f"/proc/{pid}/status").read_text().splitlines():
            if line.startswith("VmRSS:"):
                return int(line.split()[1])
    except OSError:
        pass
    return 0


def roots(drv) -> dict[str, object]:
    """Every coordinator attribute, every entity, every container module global."""
    out: dict[str, object] = {}
    for k, v in vars(drv.coord).items():
        out[f"coord.{k}"] = v
    for e in drv.entities:
        out[f"entity.{type(e).__name__}.{getattr(e, '_attr_unique_id', id(e))}"] = e
    for name, mod in sorted(sys.modules.items()):
        if not name.startswith("heatpump_optimizer") or mod is None:
            continue
        for g, v in vars(mod).items():
            if hasattr(v, "cache_info") and callable(getattr(v, "cache_info")):
                out[f"module.{name}.{g}[lru]"] = v
            elif isinstance(v, (dict, list, set, collections.deque, collections.OrderedDict)) \
                    and not g.startswith("__"):
                out[f"module.{name}.{g}"] = v
    return out


def measure_roots(drv) -> dict[str, int]:
    seen = {id(drv.coord), id(drv.hass), id(drv.entry)}
    for e in drv.entities:
        seen.add(id(e))
    sizes = {}
    for name, obj in roots(drv).items():
        if name.endswith("[lru]"):
            info = obj.cache_info()
            sizes[name] = int(info.currsize)  # entries, not bytes: reported as a count
            continue
        if name.startswith("entity."):
            seen.discard(id(obj))
        sizes[name] = deep_size(obj, seen)
    return sizes


HARNESS_FILES = (str(Path(__file__).resolve()), str((HERE / "_drive.py").resolve()))


def production_view(snapshot):
    """The snapshot less every block whose most recent frame is this harness's own
    (the checkpoint rows it keeps, deep_size's scratch): harness memory is not retained
    production memory."""
    return snapshot.filter_traces([tracemalloc.Filter(False, f) for f in HARNESS_FILES])


def by_file(snapshot) -> dict[str, int]:
    out: dict[str, int] = collections.Counter()
    for stat in snapshot.statistics("traceback"):
        owner = "other"
        for fr in reversed(list(stat.traceback)):  # tracemalloc: oldest first; take the most recent prod frame
            if PKG in fr.filename.replace("\\", "/"):
                owner = fr.filename.replace("\\", "/").split(PKG, 1)[1]
                break
        out[owner] += stat.size
    return dict(out)


PERTURB = {}


def perturbation(name: str | None, drv_factory):
    """Apply one in-memory perturbation BEFORE the coordinator is built."""
    if not name:
        return
    PERTURB[name](drv_factory)


def _p_accuracy_unbounded(_):
    # accuracy.py:HISTORY_LENGTH bounds AccuracyTracker.samples (deque maxlen); lifted,
    # the per-cycle sample is never dropped and the slope must go UP past cycle 672.
    from heatpump_optimizer import accuracy
    accuracy.HISTORY_LENGTH = 10 ** 9


PERTURB["accuracy_unbounded"] = _p_accuracy_unbounded


def run(args) -> dict:
    t_start = time.time()
    perturbation(args.perturb, None)
    drv = _drive.Driver(args.fixture, step_minutes=args.step_minutes)
    checkpoints = sorted(set([args.warmup] + list(range(args.warmup, args.cycles + 1, args.every))
                             + [args.cycles]))
    series: list[dict] = []
    snap0 = None
    cpu0 = time.process_time()
    for c in range(1, args.cycles + 1):
        drv.cycle()
        drv.sweep()
        if c == max(1, args.warmup - args.lead):
            # Tracing starts --lead cycles BEFORE the reference checkpoint: a structure the
            # cycle replaces wholesale (coordinator.data, the plan) was allocated untraced
            # before tracing began, so its first traced replacement would read as growth.
            # By cycle W every such structure has been replaced at least once.
            gc.collect()
            tracemalloc.start(args.frames)
        if c in checkpoints:
            gc.collect()
            snap = production_view(tracemalloc.take_snapshot())
            row = {"cycle": c, "traced": sum(st.size for st in snap.statistics("filename")),
                   "roots": measure_roots(drv), "worker_rss_kib": worker_rss_kib(drv), "cpu_s": round(time.process_time() - cpu0, 1)}
            if c == args.warmup:
                snap0 = snap
            del snap
            series.append(row)
            if args.progress:
                with open(args.progress, "a") as fh:
                    fh.write(json.dumps({"cycle": c, "traced": row["traced"], "cpu_s": row["cpu_s"],
                                         "top": sorted(row["roots"].items(), key=lambda kv: -kv[1])[:5]}) + "\n")
    gc.collect()
    snap1 = production_view(tracemalloc.take_snapshot())
    files = by_file(snap1)
    files0 = by_file(snap0) if snap0 else {}
    tracemalloc.stop()
    drv.close()
    n = args.cycles - args.warmup
    first, last = series[0], series[-1]
    root_slope = {k: (last["roots"].get(k, 0) - first["roots"].get(k, 0)) / n
                  for k in set(first["roots"]) | set(last["roots"])}
    # Late window: from the first checkpoint at or past --late-from to the last, so a
    # structure bounded at a cap reached mid-run (accuracy.py HISTORY_LENGTH = 672) shows
    # its plateau directly rather than averaged into the B4 slope.
    late0 = next((r for r in series if r["cycle"] >= args.late_from), None)
    late = None
    if late0 is not None and late0 is not last:
        ln = last["cycle"] - late0["cycle"]
        late = {"from": late0["cycle"], "traced_slope": (last["traced"] - late0["traced"]) / ln,
                "root_slope": {k: (last["roots"].get(k, 0) - late0["roots"].get(k, 0)) / ln
                               for k in set(late0["roots"]) | set(last["roots"])}}
    file_slope = {k: (files.get(k, 0) - files0.get(k, 0)) / n for k in set(files) | set(files0)}
    growth = []
    for st in snap1.compare_to(snap0, "traceback")[: args.top]:
        if st.size_diff <= 0:
            continue
        # tracemalloc's Traceback runs oldest -> most recent; report the most recent first.
        recent = list(reversed(list(st.traceback)))
        frames = [f"{fr.filename.split('/')[-1]}:{fr.lineno}" for fr in recent]
        prod = next((f"{fr.filename.replace(chr(92), '/').split(PKG, 1)[1]}:{fr.lineno}"
                     for fr in recent if PKG in fr.filename.replace(chr(92), "/")), "other")
        growth.append({"bytes_per_cycle": st.size_diff / n, "count_diff": st.count_diff,
                       "prod_frame": prod, "frames": frames[:6]})
    return {"fixture": args.fixture, "cycles": args.cycles, "warmup": args.warmup,
            "step_minutes": args.step_minutes,
            "perturb": args.perturb, "errors": drv.errors[:5], "n_errors": drv.n_errors,
            "traced_slope": (last["traced"] - first["traced"]) / n, "late": late,
            "root_slope": root_slope, "file_slope": file_slope, "growth": growth, "series": series,
            "maxrss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            # the solving child (production's _ensure_worker), reaped by Driver.close()
            "worker_maxrss_kib": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
            "wall_s": round(time.time() - t_start, 1), "cpu_s": round(time.process_time(), 1),
            "thread_factor": round(time.process_time() / max(1e-9, time.thread_time()), 3)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", default="owner", choices=sorted(_drive.FIXTURES))
    ap.add_argument("--cycles", type=int, default=900)
    ap.add_argument("--warmup", type=int, default=200)
    ap.add_argument("--every", type=int, default=50)
    ap.add_argument("--frames", type=int, default=12)
    ap.add_argument("--top", type=int, default=30)
    ap.add_argument("--lead", type=int, default=20)
    ap.add_argument("--late-from", type=int, default=700)
    ap.add_argument("--perturb", default=None, choices=[None, *PERTURB])
    ap.add_argument("--step-minutes", type=int, default=None,
                    help="time-warp arm: clock step between cycles (default: the 10 min interval)")
    ap.add_argument("--json", default=None)
    ap.add_argument("--progress", default=None)
    ap.add_argument("--subprocess", action="store_true")
    args = ap.parse_args()
    if args.subprocess:
        cmd = [sys.executable, __file__] + [a for a in sys.argv[1:] if a != "--subprocess"]
        before = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        rc = subprocess.call(cmd)
        print(f"RESULT child_ru_maxrss={resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss} KiB "
              f"(provisional; before={before})")
        return rc
    out = run(args)
    if args.json:
        Path(args.json).write_text(json.dumps(out))
    print(f"# machine {platform.platform()} {platform.processor()} py{platform.python_version()}")
    print(f"# fixture={out['fixture']} cycles={out['cycles']} warmup={out['warmup']} "
          f"step_minutes={out['step_minutes']} perturb={out['perturb']} cycle_errors={out['n_errors']} {out['errors'][:2]}")
    n = out["cycles"] - out["warmup"]
    print(f"RESULT traced_slope={out['traced_slope']:.1f} B/cycle")
    print(f"RESULT traced_year_mib={out['traced_slope'] * _drive.CYCLES_PER_YEAR / 2**20:.2f} MiB "
          f"(B4 budget 10 MiB = 199 B/cycle)")
    for k, v in sorted(out["root_slope"].items(), key=lambda kv: -abs(kv[1]))[:25]:
        if v:
            print(f"RESULT root_slope[{k}]={v:.1f} {'entries' if k.endswith('[lru]') else 'B'}/cycle")
    for k, v in sorted(out["file_slope"].items(), key=lambda kv: -abs(kv[1]))[:25]:
        if v:
            print(f"RESULT file_slope[{k}]={v:.1f} B/cycle")
    if out["late"]:
        lt = out["late"]
        print(f"RESULT late_traced_slope={lt['traced_slope']:.1f} B/cycle (from cycle {lt['from']})")
        for k, v in sorted(lt["root_slope"].items(), key=lambda kv: -abs(kv[1]))[:12]:
            if v:
                print(f"RESULT late_root_slope[{k}]={v:.1f} {'entries' if k.endswith('[lru]') else 'B'}/cycle")
    for g in out["growth"][:15]:
        print(f"#   growth {g['bytes_per_cycle']:.1f} B/cycle (+{g['count_diff']} blocks) at {g['prod_frame']} via {g['frames'][:4]}")
    for row in out["series"]:
        print(f"# checkpoint cycle={row['cycle']} traced={row['traced']} worker_rss_kib={row.get('worker_rss_kib')} cpu_s={row['cpu_s']}")
    ws = [r for r in out["series"] if r.get("worker_rss_kib")]
    if len(ws) >= 2:
        print(f"RESULT worker_rss_slope={(ws[-1]['worker_rss_kib'] - ws[0]['worker_rss_kib']) * 1024 / max(1, ws[-1]['cycle'] - ws[0]['cycle']):.0f} "
              f"B/cycle (solving child VmRSS, cycles {ws[0]['cycle']}..{ws[-1]['cycle']}; provisional)")
    print(f"RESULT ru_maxrss={out['maxrss_kib']} KiB (coordinator process, incl. tracemalloc overhead; provisional)")
    print(f"RESULT worker_ru_maxrss={out['worker_maxrss_kib']} KiB (solving child; provisional; B5 128 MB)")
    print(f"RESULT wall_s={out['wall_s']} s (provisional)")
    print(f"RESULT thread_factor={out['thread_factor']}")
    print(f"RESULT load1={_drive.load1()}")
    print(f"RESULT swapins={_drive.swapins()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
