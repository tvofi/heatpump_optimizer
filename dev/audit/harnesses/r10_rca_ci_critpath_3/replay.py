#!/usr/bin/env python3
"""R10-RCA-CI-CRITPATH-3: replay main's third and fourth `GREW critical_path_minutes`.

Reads the tree, three git objects and the fixtures beside this file. No network.
Every grade runs the ratchet the red commit itself ran: tests/ci_ratchet.py as
of that commit, read with `git show` and imported by spec, so a later change to
the live file cannot move a reproduction (review of #3189: the live file graded
the third red's window 21.967 after #3180).

  runs.json      ci.yml push runs on main 3775..4056 with their jobs
  runs_red4.json ci.yml push runs on main 4009..4128 with their jobs
  ci_logs.json   lane-plan lines of two closures jobs, the per-script seconds of
                 three fast (3.14) jobs, every heavy-lane job's runner image

  1. reproduce  -- the window graded at 8f286293b, through that commit's
                   run_minutes and critical_path_minutes: 36.5, GREW against
                   budget 34.267 + band 1.3.
  2. cause      -- every graded window from 11-02, the 8-run median beside the
                   count of runs whose `tests / closures` lane drew the slow
                   host class (> 30 min for the same 34-script plan).
  3. candidate  -- the PLANNED critical path (tests/closure.py lane_plan over
                   tests/closures.json's recorded seconds, 3 lanes) at this tree;
                   a determinism check (the same input twice: it controls
                   nothing about hosts); a perturbation it must detect (one
                   script +300 s); and the lane totals CI printed in a 38.2-min
                   and a 20.6-min closures job, which must equal the tree's.
  4. fourth red -- the window graded at 8e90d8144, through that commit's
                   window_work_minutes: 29.067, GREW against 21.983 + 1.3; the
                   window one push earlier (616868bdc) ok; the fast (3.14)
                   price in each, the last fast (3.14) run under 26 min, and
                   the fast (3.14) price in the window #3180 recorded 21.983 from.
  5. host       -- the same 33 fast (3.14) scripts in runs 4009 and 4128: every
                   one slower, none added; the runner image of every heavy-lane
                   job, which does not separate fast from slow.
  6. at red 4   -- the planned path read from tests/closures.json at c3a279e32
                   (red 3) and 8e90d8144 (red 4): equal.

Exit 0 when every step holds as the record states, 1 otherwise.
"""
from __future__ import annotations

import importlib.util
import json
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


HERE = Path(__file__).resolve().parent
ROOT = repo_root(HERE)
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

import closure  # noqa: E402

RED3_SHA, RED3_BUDGET, RED3_BAND = "8f286293b", 34.267, 1.3
RED4_SHA, RED4_BUDGET, RED4_BAND = "8e90d8144", 21.983, 1.3
SLOW_CLOSURES_MIN = 30.0
FAST_HOST_FAST_LANE_MIN = 26.0
FAST_LANE = "tests / fast (3.14)"


def _ratchet_at(sha: str, td: str):
    """tests/ci_ratchet.py exactly as `sha` ran it."""
    src = subprocess.run(["git", "show", f"{sha}:tests/ci_ratchet.py"], cwd=ROOT,
                         check=True, capture_output=True, text=True).stdout
    path = Path(td) / f"ci_ratchet_{sha}.py"
    path.write_text(src)
    spec = importlib.util.spec_from_file_location(f"ci_ratchet_{sha}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _runs(name: str) -> list[dict]:
    runs = json.loads((HERE / name).read_text())["workflow_runs"]
    return sorted(runs, key=lambda r: r["created_at"])


def _lane_minutes(cr, r: dict, lane: str) -> "float | None":
    for j in r["jobs"]:
        if j["name"] == lane and j.get("started_at") and j.get("completed_at"):
            return (cr._at(j["completed_at"]) - cr._at(j["started_at"])).total_seconds() / 60
    return None


def _graded_window(runs: list[dict], sha: str, width: int) -> list[dict]:
    """What ci-ratchet's gather read on `sha`'s own push run: that run, still
    in progress, and the `width - 1` runs before it."""
    i = next(k for k, r in enumerate(runs) if r["head_sha"].startswith(sha))
    return runs[max(0, i - width + 1):i] + [{**runs[i], "status": "in_progress"}]


def reproduce(cr3, td: str) -> bool:
    window = _graded_window(_runs("runs.json"), RED3_SHA, 8)
    p = Path(td) / "red3.json"
    p.write_text(json.dumps({"workflow_runs": window}))
    graded = cr3.critical_path_minutes(p)
    grew = graded > RED3_BUDGET + RED3_BAND
    print(f"1. reproduce: window at {RED3_SHA} grades {graded} with ci_ratchet.py as of "
          f"{RED3_SHA} (budget {RED3_BUDGET} + band {RED3_BAND} = "
          f"{RED3_BUDGET + RED3_BAND:.3f}): {'GREW' if grew else 'ok'}")
    return graded == 36.5 and grew


def cause(cr3) -> bool:
    runs = _runs("runs.json")
    print("2. cause: graded median vs slow-host draws in the window")
    rows = []
    for i in range(8, len(runs) + 1):
        w = runs[i - 8:i]
        counted = [r for r in w if cr3.run_minutes(r) is not None]
        ms = [cr3.run_minutes(r) for r in counted]
        slow = sum(1 for r in counted
                   if (_lane_minutes(cr3, r, "tests / closures") or 0) > SLOW_CLOSURES_MIN)
        med = statistics.median(ms)
        rows.append((slow / len(counted), med))
        print(f"   after {w[-1]['head_sha'][:9]}  median {med:6.3f}  "
              f"slow closures draws {slow}/{len(counted)}  "
              f"{'GREW' if med > RED3_BUDGET + RED3_BAND else 'ok'}")
    lo = [m for s, m in rows if s < 0.5]
    hi = [m for s, m in rows if s > 0.7]
    graded = sum(1 for r in runs if cr3.run_minutes(r) is not None)
    print(f"   windows where under half the graded runs drew the slow closures "
          f"host: {len(lo)}, max median {max(lo):.3f}; over 70%: {len(hi)}, "
          f"min median {min(hi):.3f}")
    print(f"   runs.json: {len(runs)} runs {runs[0]['run_number']}..{runs[-1]['run_number']}, "
          f"{graded} graded by run_minutes")
    return bool(lo and hi) and max(lo) <= RED3_BUDGET + RED3_BAND < min(hi)


def _secs(recorded: dict, s: str) -> float:
    r = recorded.get(s)
    return float(r.get("seconds", 0.0)) if isinstance(r, dict) else 0.0


def _planned(recorded: dict, scripts: list[str]) -> float:
    lanes = closure.lane_plan(scripts, recorded, 3)
    return round(max(sum(_secs(recorded, s) for s in ln) for ln in lanes), 1)


def _scripts(td: str) -> list[str]:
    out = Path(td) / "lane-plan"
    subprocess.run([sys.executable, str(ROOT / "tests/closure.py"), "lane-plan",
                    "--all-scripts", "--lanes", "3", "--out-dir", str(out)],
                   cwd=ROOT, check=True, capture_output=True, text=True)
    return (out / "scripts.txt").read_text().split()


def candidate(scripts: list[str]) -> bool:
    recorded = json.loads((ROOT / "tests/closures.json").read_text())["recorded"]
    a, b = _planned(recorded, scripts), _planned(recorded, scripts)
    bumped = json.loads(json.dumps(recorded))
    bumped["tests/stress.py"]["seconds"] = float(bumped["tests/stress.py"]["seconds"]) + 300
    c = _planned(bumped, scripts)
    print(f"3. candidate: planned critical path {a}s over {len(scripts)} scripts; "
          f"determinism (same input again) {b}s; stress.py +300s -> {c}s")
    logs = json.loads((HERE / "ci_logs.json").read_text())["closures_lane_plan"]
    ci_ok = True
    for job, lines in logs.items():
        totals = [float(ln.split("(")[1].split("s recorded")[0]) for ln in lines[1:]]
        print(f"   CI job {job}: {lines[0].strip()!r}, lane totals {totals}, longest {max(totals)}")
        ci_ok = ci_ok and max(totals) == a and len(totals) == 3
    return a == b and c > a and ci_ok


def fourth(cr4, td: str) -> bool:
    runs = _runs("runs_red4.json")
    out = []
    for sha in ("616868bdc", RED4_SHA):
        window = _graded_window(runs, sha, cr4.PUSH_WINDOW)
        p = Path(td) / f"red4-{sha}.json"
        p.write_text(json.dumps({"workflow_runs": window}))
        graded = cr4.critical_path_minutes(p)
        fast = [(round(m, 2), r["run_number"]) for r in window
                if cr4._walk(r) is not None
                for j in r["jobs"] if j["name"] == FAST_LANE and j["conclusion"] == "success"
                for m in [_lane_minutes(cr4, r, FAST_LANE)]]
        floor = statistics.median(m for m, _ in fast) * cr4.OTHER_WORK_FRACTION
        price = min((m, n) for m, n in fast if m >= floor)
        under = [n for m, n in fast if m < FAST_HOST_FAST_LANE_MIN]
        grew = graded > RED4_BUDGET + RED4_BAND
        print(f"4. window at {sha} (runs {window[0]['run_number']}..{window[-1]['run_number']}) "
              f"grades {graded} with ci_ratchet.py as of {RED4_SHA} (budget {RED4_BUDGET} + "
              f"band {RED4_BAND}): {'GREW' if grew else 'ok'}; fast (3.14) priced {price[0]} "
              f"(run {price[1]}) over {len(fast)} success runs, under "
              f"{FAST_HOST_FAST_LANE_MIN:.0f} min: {under or 'none'}")
        out.append((graded, grew, price, under))
    (_, grew3, _, under3), (g4, grew4, price4, under4) = out
    rec = _record_fast_price(cr4)
    print(f"   #3180's record: its largest window ({rec[2]}) reads {rec[0]}, fast (3.14) "
          f"priced {rec[1]}; red 4 reads {g4 - rec[0]:.3f} over it, fast (3.14) "
          f"{price4[0] - rec[1]:.2f} over")
    return (not grew3 and grew4 and g4 == 29.067 and under3 == [4009] and not under4
            and price4 == (27.33, 4035) and rec[0] == RED4_BUDGET)


def _record_fast_price(cr4) -> tuple[float, float, str]:
    """The fast (3.14) price in the window #3180 recorded its budget from:
    its own runs.json, read as critical_path_minutes(stat="record") reads it."""
    p = ROOT / "dev/audit/harnesses/r10_hotfix_ci_critpath_3/runs.json"
    runs = sorted(json.loads(p.read_text())["workflow_runs"],
                  key=lambda r: r.get("created_at") or "", reverse=True)
    spans = [runs[i:i + cr4.PUSH_WINDOW] for i in range(len(runs) - cr4.PUSH_WINDOW + 1)]
    value, span = max(((cr4.window_work_minutes(s), s) for s in spans), key=lambda t: t[0])
    seen = [w["work"] for r in span for w in (cr4._walk(r) or [])
            if w["name"] == FAST_LANE and w["priced"]]
    floor = statistics.median(seen) * cr4.OTHER_WORK_FRACTION
    price = round(min(x for x in seen if x >= floor) / 60, 2)
    nums = [r.get("run_number") for r in span]
    return value, price, f"runs {min(nums)}..{max(nums)}"


def host() -> bool:
    logs = json.loads((HERE / "ci_logs.json").read_text())
    fast_run, slow_run = logs["fast_lane_scripts"]["4009"], logs["fast_lane_scripts"]["4128"]
    f, s = fast_run["script_seconds"], slow_run["script_seconds"]
    same = set(f) == set(s)
    ratios = sorted(s[k] / f[k] for k in f if f[k] >= 10)
    print(f"5. host: fast (3.14) job {fast_run['job']} (run 4009) vs {slow_run['job']} (run 4128): "
          f"{len(f)} vs {len(s)} scripts, same set {same}; summed {sum(f.values())}s vs "
          f"{sum(s.values())}s (x{sum(s.values()) / sum(f.values()):.2f}); per-script ratio "
          f"{ratios[0]:.2f}..{ratios[-1]:.2f} over the {len(ratios)} scripts of >= 10 s")
    jobs = logs["lane_jobs"]
    fast_lane = [j for j in jobs if j["name"] == FAST_LANE]
    by_img: dict[str, list[float]] = {}
    for j in fast_lane:
        by_img.setdefault(j["image"], []).append(j["minutes"])
    span = {k: (len(v), min(v), max(v)) for k, v in sorted(by_img.items())}
    first = [j for j in fast_lane if j["run"] <= 4009]
    later = [j for j in fast_lane if j["run"] > 4009]
    nf = sum(j["minutes"] < FAST_HOST_FAST_LANE_MIN for j in first)
    nl = sum(j["minutes"] < FAST_HOST_FAST_LANE_MIN for j in later)
    cl = [j for j in jobs if j["name"] == "tests / closures" and j["run"] > 4009]
    ncl = sum(j["minutes"] < 27 for j in cl)
    print(f"   fast (3.14) by runner image (n, min, max): {span}")
    img_pair = (next(j["image"] for j in fast_lane if j["run"] == 4009),
                next(j["image"] for j in fast_lane if j["run"] == 4128))
    print(f"   the 4009 vs 4128 comparison crosses an image change: {img_pair[0] != img_pair[1]} "
          f"({img_pair[0]} vs {img_pair[1]}); same-image slow job, run 4035: "
          f"{next(j['minutes'] for j in fast_lane if j['run'] == 4035)} min on "
          f"{next(j['image'] for j in fast_lane if j['run'] == 4035)}")
    print(f"   fast (3.14) under {FAST_HOST_FAST_LANE_MIN:.0f} min: {nf} of {len(first)} "
          f"runs 3770..4009, {nl} of {len(later)} after; closures under 27 min after "
          f"4009: {ncl} of {len(cl)}")
    img_4009_4116 = {j["image"] for j in fast_lane if 4009 <= j["run"] <= 4116}
    return same and ratios[0] > 1 and nl == 0 and nf > 0 and len(img_4009_4116) == 1


def at_red4(scripts: list[str]) -> bool:
    vals = {}
    for sha in ("c3a279e32", RED4_SHA):
        rec = json.loads(subprocess.run(["git", "show", f"{sha}:tests/closures.json"], cwd=ROOT,
                                        check=True, capture_output=True, text=True).stdout)["recorded"]
        vals[sha] = _planned(rec, scripts)
    print(f"6. planned critical path from tests/closures.json at red 3 / red 4: {vals}")
    return len(set(vals.values())) == 1


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        cr3, cr4 = _ratchet_at(RED3_SHA, td), _ratchet_at(RED4_SHA, td)
        scripts = _scripts(td)
        ok = [reproduce(cr3, td), cause(cr3), candidate(scripts), fourth(cr4, td),
              host(), at_red4(scripts)]
    print("RESULT:", "holds" if all(ok) else f"does NOT hold {ok}")
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
