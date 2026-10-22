#!/usr/bin/env python3
"""R10-CI-LAYOUT P2b, unit U9a: the ci_ratchet.py re-key's two null controls.

    python3 -I dev/audit/harnesses/r10_u9a_ratchet_nulls.py [CI_RATCHET_PY]

CI_RATCHET_PY defaults to this tree's tests/ci_ratchet.py; pass a copy of
main's (`git show origin/main:tests/ci_ratchet.py > F`) for the other end.

(1) script_runs_per_push on a replayed push run: the closures lane's full
plan (`tests/closure.py lane-plan --all-scripts`), the coverage `fast`
stage's scripts (coverage_tree.sh's DERIVED rule, read off tests/run.sh),
and 19 `reused` coverage rows (push run 39213675232's copies), through the
module's own read_metrics and script_runs. The arch pair's closures rows are
named, so a reader that stopped counting them shows it (carry 3).

(2) critical_path_minutes over the last 8 pre-umbrella push runs of
tests.yml (OLD_WINDOW, listed 2026-10-22T23:1xZ through the API; the newest
was still in progress): the old reader and the re-keyed one must agree.
"""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OLD_WINDOW = [  # (run id, status, created_at, updated_at), Tests push runs on main
    (39864731659, "in_progress", "2026-10-22T22:24:32Z", "2026-10-22T22:51:22Z"),
    (39864627483, "completed", "2026-10-22T22:23:44Z", "2026-10-22T22:56:20Z"),
    (39854919993, "completed", "2026-10-22T21:09:23Z", "2026-10-22T21:51:07Z"),
    (39853011426, "completed", "2026-10-22T20:55:36Z", "2026-10-22T21:53:36Z"),
    (39847477925, "completed", "2026-10-22T20:16:58Z", "2026-10-22T21:14:33Z"),
    (39847222335, "completed", "2026-10-22T20:15:14Z", "2026-10-22T21:12:23Z"),
    (39847059133, "completed", "2026-10-22T20:14:08Z", "2026-10-22T20:50:45Z"),
    (39842087677, "completed", "2026-10-22T19:40:04Z", "2026-10-22T20:17:04Z"),
]
REUSED = 19


def load(path: Path):
    spec = importlib.util.spec_from_file_location("ci_ratchet_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main(argv: list[str]) -> int:
    cr = load(Path(argv[0]) if argv else ROOT / "tests/ci_ratchet.py")
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        subprocess.run([sys.executable, "tests/closure.py", "lane-plan", "--all-scripts", "--out-dir", str(d / "plan")],
                       cwd=ROOT, check=True, capture_output=True)
        closures = (d / "plan/scripts.txt").read_text().split()
        derived = list(dict.fromkeys(re.findall(r'run "\$PYTHON" tests/([a-z_]+)\.py', (ROOT / "tests/run.sh").read_text())))
        cover = [s for s in derived if s not in ("arch_score", "arch_score_head", "env_drift", "rolling", "stress",
                                                  "validate", "edge", "backtest", "optimality")]
        m = d / "metrics"
        m.mkdir()
        (m / "ci-metrics-fast.tsv").write_text("fast\tmode\tfull\t0\t0\tpush\t1\n")
        (m / "ci-metrics-closures.tsv").write_text("".join(f"closures\t{s}\tfull\t0\t1\tpush\t1\n" for s in closures))
        (m / "ci-metrics-coverage.tsv").write_text(
            "".join(f"coverage\ttests/{s}.py\tfull\t0\t1\tpush\t1\n" for s in cover)
            + "".join(f"coverage\ttests/reused{i}.py\treused\t0\t0\tpush\t1\n" for i in range(REUSED)))
        rows = cr.read_metrics(m)[("push", "1")]
        counted = [r["name"] for r in rows if r["lane"] in cr.LANES and r["class"] != "reused"]
        print(f"replay: closures {len(closures)}, coverage fast {len(cover)}, reused {REUSED}; "
              f"arch pair counted: {sorted(n for n in counted if 'arch_score' in n)}")
        print(f"RESULT script_runs_per_push={cr.script_runs(rows)}")
        f = d / "runs.json"
        f.write_text(json.dumps({"workflow_runs": [
            {"id": i, "name": "Tests", "path": ".github/workflows/tests.yml", "event": "push", "status": s,
             "created_at": c, "updated_at": u} for i, s, c, u in OLD_WINDOW]}))
        print(f"RESULT critical_path_minutes={cr.critical_path_minutes(f):.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
