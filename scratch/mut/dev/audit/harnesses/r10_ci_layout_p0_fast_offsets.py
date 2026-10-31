#!/usr/bin/env python3
"""R10-CI-LAYOUT PR 0's FULL-run control: where `fast (3.14)` ends, per Tests run.

    python3 dev/audit/harnesses/r10_ci_layout_p0_fast_offsets.py \
        --before RUN [RUN ...] --after RUN [RUN ...]

Read-only: one `actions/runs/<id>` and one `actions/runs/<id>/jobs` GET per
run, through `gh api`, 2 s apart. For each run it prints the event, head,
attempt, and for its `fast (3.14)` job the queue (job start minus run
creation), the job's own duration and the offset (job end minus run
creation, the control's measure), all in minutes. Then the median offset and
duration of each set, and `RESULT saved_offset=<before - after>` with
`bar=5.0` and PASS or FAIL. A run without a completed `fast (3.14)` job is
listed as NOT COUNTED with its reason, and the counts are printed beside the
medians. The caller picks comparable runs: completed FULL runs (push runs are
FULL by construction; a pull_request run is FULL when its fast job prints
`MODE: FULL`), and never a push run re-run to make one.
"""
from __future__ import annotations

import json
import statistics
import subprocess
import sys
import time
from datetime import datetime

REPO = "repos/tvofi/heatpump_optimizer"


def _get(path: str) -> dict:
    out = subprocess.run(["gh", "api", f"{REPO}/{path}"], capture_output=True,
                         text=True, check=True).stdout
    time.sleep(2)
    return json.loads(out)


def _t(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def measure(run_id: str) -> "tuple[dict | None, str]":
    run = _get(f"actions/runs/{run_id}")
    jobs = _get(f"actions/runs/{run_id}/jobs?per_page=100")["jobs"]
    fast = [j for j in jobs if j["name"] == "fast (3.14)"]
    head = f"{run_id} {run['event']} {run['head_sha'][:9]} attempt={run['run_attempt']}"
    if not fast or fast[0]["status"] != "completed":
        return None, f"{head} NOT COUNTED: no completed fast (3.14) job"
    j, c = fast[0], _t(run["created_at"])
    s, e = _t(j["started_at"]), _t(j["completed_at"])
    row = {"queue": (s - c).total_seconds() / 60, "dur": (e - s).total_seconds() / 60,
           "offset": (e - c).total_seconds() / 60}
    return row, (f"{head} {j['conclusion']} queue={row['queue']:.2f} "
                 f"dur={row['dur']:.2f} offset={row['offset']:.2f}")


def main(argv: list[str]) -> int:
    if "--before" not in argv or "--after" not in argv:
        print(__doc__)
        return 2
    b, a = argv.index("--before"), argv.index("--after")
    sets = {"before": argv[b + 1:a] if b < a else argv[b + 1:],
            "after": argv[a + 1:] if a > b else argv[a + 1:b]}
    med = {}
    for name, ids in sets.items():
        rows = []
        for rid in ids:
            row, line = measure(rid)
            print(f"{name} {line}")
            if row:
                rows.append(row)
        if not rows:
            print(f"{name}: no countable run")
            return 1
        med[name] = (statistics.median(r["offset"] for r in rows),
                     statistics.median(r["dur"] for r in rows))
        print(f"{name}: counted {len(rows)} of {len(ids)}; median offset="
              f"{med[name][0]:.2f} median dur={med[name][1]:.2f}")
    saved = med["before"][0] - med["after"][0]
    print(f"RESULT saved_offset={saved:.2f} bar=5.0 {'PASS' if saved >= 5.0 else 'FAIL'}")
    return 0 if saved >= 5.0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
