"""Per-script wall seconds on main's push runs, read from the `fast` job logs.

    python3 dev/audit/harnesses/ci_script_seconds.py SINCE SCRIPT [SCRIPT ...]
    python3 dev/audit/harnesses/ci_script_seconds.py 2026-10-04 \\
        tests/boost_drift_replay.py tests/features.py tests/stress.py

One row per Tests run (workflow `CI`, job `tests / fast (3.14)`, once the layout
cut-over landed; `Tests` before it, so the series stays continuous) with event
`push` on `main` created at or after SINCE:
created time, head SHA, and each script's seconds from run.sh's closing
timing table (`   1152s  python3 tests/x.py`), or `none` when the log has no
such row (the script did not exist or did not run). A run whose jobs or log
could not be read is counted and printed, never dropped: the last line is the
failure count beside the row count.

GitHub's runner pool has more than one machine class, so compare a script
against another script in the SAME run (the ratio), not across runs.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys

REPO = "tvofi/heatpump_optimizer"
WORKFLOWS = ("Tests", "CI")        # the push runs of `Tests` end at the cut-over, `CI`'s begin


def is_fast(job_name: str) -> bool:
    """`fast (3.14)` before the cut-over, `tests / fast (3.14)` after."""
    return job_name.split(" / ", 1)[-1].startswith("fast")


def selftest() -> int:
    got = [is_fast(n) for n in ("fast (3.14)", "tests / fast (3.14)", "tests / browser", "gate")]
    want = [True, True, False, False]
    print(f"SELFTEST is_fast got={got} want={want} {'ok' if got == want else 'FAIL'}")
    return 0 if got == want else 1


def gh(*args: str) -> str:
    return subprocess.run(["gh", *args, "-R", REPO], check=True,
                          capture_output=True, text=True).stdout


def main() -> int:
    if sys.argv[1:] == ["--selftest"]:
        return selftest()
    since, scripts = sys.argv[1], sys.argv[2:]
    # Filtered here, not by `--event push`: that server-side filter answered
    # with runs weeks old (2026-10-07), which read as zero rows.
    runs = [r for w in WORKFLOWS for r in json.loads(gh(
        "run", "list", "-w", w, "--branch", "main", "--limit", "200",
        "--json", "databaseId,headSha,createdAt,event")) if r["event"] == "push"]
    rows = failed = 0
    for run in sorted(runs, key=lambda r: r["createdAt"]):
        if run["createdAt"] < since:
            continue
        head = f"{run['createdAt']} {run['headSha'][:8]}"
        try:
            jobs = json.loads(gh("run", "view", str(run["databaseId"]),
                                 "--json", "jobs"))["jobs"]
            fast = next(j for j in jobs if is_fast(j["name"]))
            log = gh("run", "view", "--job", str(fast["databaseId"]), "--log")
        except (subprocess.CalledProcessError, StopIteration):
            failed += 1
            print(f"{head} UNREADABLE")
            continue
        cells = []
        for s in scripts:
            m = re.search(r"\s(\d+)s  python3 " + re.escape(s) + r"\s*$",
                          log, re.M)
            cells.append(f"{s}={m.group(1) + 's' if m else 'none'}")
        rows += 1
        print(head, " ".join(cells))
    print(f"rows={rows} unreadable={failed}")
    # No row is a broken listing, never a measurement of zero runs.
    return 0 if rows else 1


if __name__ == "__main__":
    sys.exit(main())
