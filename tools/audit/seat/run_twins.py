#!/usr/bin/env python3
"""Count the cancelled `pull_request` runs of one workflow by what cancelled them.

    python3 tools/audit/seat/run_twins.py --fetch <workflow-file> <cache-dir> [pages]
    python3 tools/audit/seat/run_twins.py <page.json>...
    python3 tools/audit/seat/run_twins.py --self-test

R9-CI-2a's instrument. A cancelled `pull_request` run is a SAME-SHA TWIN when
another `pull_request` run of the same workflow sits at the same head SHA,
created within 10 s of it: two events at one head (an author push and the
body PATCH that follows it), not a supersession. Any other cancelled run is
OTHER (an older head superseded, a manual cancel). A twin cancellation
leaves a cancelled check run beside a finished one at a live head.

`--fetch` writes `/actions/workflows/<file>/runs` pages (100 runs each,
default 3) into <cache-dir> through `gh api`, 1.5 s apart, and classifies
them; the positional form classifies pages already on disk, so a figure is
re-derivable from the cached pages without the API.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

REPO = "tvofi/heatpump_optimizer"
WINDOW_S = 10


def classify(runs: "list[dict]") -> "tuple[int, int, list[tuple]]":
    """(twins, others, twin rows) over the cancelled pull_request runs."""
    pr = [r for r in runs if r.get("event") == "pull_request"]
    ts = {r["id"]: datetime.fromisoformat(r["created_at"].replace("Z", "+00:00"))
          for r in pr}
    by_sha: "dict[str, list[dict]]" = {}
    for r in pr:
        by_sha.setdefault(r["head_sha"], []).append(r)
    twins, others, rows = 0, 0, []
    for r in pr:
        if r.get("conclusion") != "cancelled":
            continue
        sib = [s for s in by_sha[r["head_sha"]] if s["id"] != r["id"]
               and abs((ts[s["id"]] - ts[r["id"]]).total_seconds()) <= WINDOW_S]
        if sib:
            twins += 1
            rows.append((r["created_at"], r["head_sha"][:10], r["id"],
                         ",".join(f"{s['id']}:{s.get('conclusion')}" for s in sib)))
        else:
            others += 1
    return twins, others, sorted(rows)


def load(paths: "list[str]") -> "list[dict]":
    runs: "dict[int, dict]" = {}
    for p in paths:
        for r in json.loads(Path(p).read_text())["workflow_runs"]:
            runs[r["id"]] = r
    return list(runs.values())


def fetch(workflow: str, cache: str, pages: int) -> "list[str]":
    out = []
    Path(cache).mkdir(parents=True, exist_ok=True)
    for page in range(1, pages + 1):
        dest = Path(cache) / f"{workflow}-{page}.json"
        body = subprocess.run(
            ["gh", "api", f"repos/{REPO}/actions/workflows/{workflow}/runs"
             f"?per_page=100&page={page}"], check=True, capture_output=True, text=True).stdout
        dest.write_text(body)
        out.append(str(dest))
        time.sleep(1.5)
    return out


def report(paths: "list[str]") -> None:
    runs = load(paths)
    twins, others, rows = classify(runs)
    pr = [r for r in runs if r.get("event") == "pull_request"]
    span = sorted(r["created_at"] for r in runs)
    print(f"runs={len(runs)} pull_request={len(pr)} span={span[0]}..{span[-1]}")
    print(f"cancelled pull_request runs: same-sha-twin={twins} other={others}")
    for row in rows[-8:]:
        print("  twin", *row)


def self_test() -> int:
    def run(i, sha, concl, t, ev="pull_request"):
        return {"id": i, "event": ev, "head_sha": sha, "conclusion": concl,
                "created_at": f"2026-10-08T05:00:{t:02d}Z"}
    cases = [
        ("a cancelled run with a same-SHA sibling 1 s later is a twin",
         [run(1, "a" * 40, "cancelled", 0), run(2, "a" * 40, "success", 1)], (1, 0)),
        ("a cancelled run at an older SHA is other, not a twin (null control)",
         [run(1, "a" * 40, "cancelled", 0), run(2, "b" * 40, "success", 1)], (0, 1)),
        ("a same-SHA sibling 30 s apart is not a twin",
         [run(1, "a" * 40, "cancelled", 0), run(2, "a" * 40, "success", 30)], (0, 1)),
        ("a review run at the same SHA is not a pull_request sibling",
         [run(1, "a" * 40, "cancelled", 0),
          run(2, "a" * 40, "success", 1, ev="pull_request_review")], (0, 1)),
    ]
    fail = 0
    for name, runs, want in cases:
        got = classify(runs)[:2]
        ok = got == want
        fail += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {name}" + ("" if ok else f"  [{got} != {want}]"))
    print(f"run_twins self-test: {len(cases)} checks, {fail} failed")
    return 1 if fail else 0


def main(argv: "list[str]") -> int:
    if argv[:1] == ["--self-test"]:
        return self_test()
    if argv[:1] == ["--fetch"]:
        if len(argv) not in (3, 4):
            print(__doc__, file=sys.stderr)
            return 2
        report(fetch(argv[1], argv[2], int(argv[3]) if len(argv) == 4 else 3))
        return 0
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    report(argv)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
