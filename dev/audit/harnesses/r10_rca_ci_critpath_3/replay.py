#!/usr/bin/env python3
"""R10-RCA-CI-CRITPATH-3: replay main's third `GREW critical_path_minutes`.

Reads only the tree and runs.json beside this file (the ci.yml push runs on
main, 2026-11-01T23:43Z..2026-11-03T04:23Z, with their jobs). No network.

  1. reproduce  -- the graded window at 8f286293b, through tests/ci_ratchet.py's
                   own run_minutes and critical_path_minutes: 36.5, GREW
                   against budget 34.267 + band 1.3.
  2. cause      -- every graded window on 2026-11-02, the 8-run median beside
                   the count of runs whose `tests / closures` lane drew the
                   slow host class (> 30 min for the same 34-script plan), among the runs the median reads.
  3. candidate  -- the PLANNED critical path (tests/closure.py lane_plan over
                   tests/closures.json's recorded seconds, 3 lanes): its value
                   at this tree, a null control (the same tree twice), and a
                   perturbation (one script's recorded seconds +300) that it
                   must detect.

Exit 0 when all three hold as the report states, 1 otherwise.
"""
from __future__ import annotations

import json
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from tests import ci_ratchet as cr  # noqa: E402
import closure  # noqa: E402

BUDGET = 34.267
BAND = 1.3
RED_SHA = "8f286293b"
SLOW_CLOSURES_MIN = 30.0


def _runs() -> list[dict]:
    runs = json.loads((HERE / "runs.json").read_text())["workflow_runs"]
    return sorted(runs, key=lambda r: r["created_at"])


def _closures_minutes(r: dict) -> "float | None":
    for j in r["jobs"]:
        if j["name"] == "tests / closures" and j.get("started_at") and j.get("completed_at"):
            return (cr._at(j["completed_at"]) - cr._at(j["started_at"])).total_seconds() / 60
    return None


def reproduce(runs: list[dict]) -> bool:
    i = next(k for k, r in enumerate(runs) if r["head_sha"].startswith(RED_SHA))
    window = runs[max(0, i - 7):i] + [{**runs[i], "status": "in_progress"}]
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "runs.json"
        p.write_text(json.dumps({"workflow_runs": window}))
        graded = cr.critical_path_minutes(p)
    grew = graded > BUDGET + BAND
    print(f"1. reproduce: window at {RED_SHA} grades {graded} "
          f"(budget {BUDGET} + band {BAND} = {BUDGET + BAND:.3f}): "
          f"{'GREW' if grew else 'ok'}")
    return graded == 36.5 and grew


def cause(runs: list[dict]) -> bool:
    print("2. cause: graded median vs slow-host draws in the window")
    rows = []
    for i in range(8, len(runs) + 1):
        w = runs[i - 8:i]
        ms = [m for m in map(cr.run_minutes, w) if m is not None]
        counted = [r for r in w if cr.run_minutes(r) is not None]
        slow = sum(1 for r in counted if (_closures_minutes(r) or 0) > SLOW_CLOSURES_MIN)
        med = statistics.median(ms)
        rows.append((slow / len(counted), med))
        print(f"   after {w[-1]['head_sha'][:9]}  median {med:6.3f}  "
              f"slow closures draws {slow}/{len(counted)}  {'GREW' if med > BUDGET + BAND else 'ok'}")
    lo = [m for s, m in rows if s < 0.5]
    hi = [m for s, m in rows if s > 0.7]
    print(f"   windows where under half the graded runs drew the slow closures "
          f"host: {len(lo)}, max median {max(lo):.3f}; over 70%: {len(hi)}, "
          f"min median {min(hi):.3f}")
    return bool(lo and hi) and max(lo) <= BUDGET + BAND < min(hi)


def _planned(recorded: dict, scripts: list[str]) -> float:
    lanes = closure.lane_plan(scripts, recorded, 3)

    def secs(s: str) -> float:
        r = recorded.get(s)
        return float(r.get("seconds", 0.0)) if isinstance(r, dict) else 0.0
    return round(max(sum(secs(s) for s in ln) for ln in lanes), 1)


def candidate() -> bool:
    with tempfile.TemporaryDirectory() as td:
        subprocess.run([sys.executable, str(ROOT / "tests/closure.py"), "lane-plan",
                        "--all-scripts", "--lanes", "3", "--out-dir", td],
                       cwd=ROOT, check=True, capture_output=True, text=True)
        scripts = (Path(td) / "scripts.txt").read_text().split()
    recorded = json.loads((ROOT / "tests/closures.json").read_text())["recorded"]
    a, b = _planned(recorded, scripts), _planned(recorded, scripts)
    bumped = json.loads(json.dumps(recorded))
    bumped["tests/stress.py"]["seconds"] = float(bumped["tests/stress.py"]["seconds"]) + 300
    c = _planned(bumped, scripts)
    print(f"3. candidate: planned critical path {a}s over {len(scripts)} scripts; "
          f"null (same tree again) {b}s; stress.py +300s -> {c}s")
    return a == b and c > a


def main() -> int:
    runs = _runs()
    ok = [reproduce(runs), cause(runs), candidate()]
    print("RESULT:", "holds" if all(ok) else f"does NOT hold {ok}")
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
