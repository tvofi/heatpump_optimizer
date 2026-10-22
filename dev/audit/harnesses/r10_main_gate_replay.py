#!/usr/bin/env python3
"""R10-FLOW-MAIN-GATE: replay the train's --overlap main gate on main e7c66485's live check runs.

    python3 dev/audit/harnesses/r10_main_gate_replay.py <merge_train.py> [--pending NAME ...]

<merge_train.py> is the train under test (a base export or a head). The check
runs at e7c664856776542bf60bd770c98aba1eaadb4041 are read live from GitHub's
public API (unauthenticated GET, one page of 100), and the required contexts
from the public branch-rules endpoint for main, less the train's own PR_ONLY.
Each --pending NAME is rewritten queued-to-in-progress (status in_progress,
conclusion null) to re-create the 2026-10-21 moment the study observed (K15:
7 checks in flight, `record` and `record-autofix` red), which has since
concluded live. With no --pending the replay is the settled tip, the null
control. Prints every line `Train.main_green` logs under --overlap, then
`END`; rc 1 when either API read fails.
"""
import importlib.util
import json
import sys
import tempfile
import urllib.request
from pathlib import Path

SHA = "e7c664856776542bf60bd770c98aba1eaadb4041"
API = "https://api.github.com/repos/tvofi/heatpump_optimizer"


def get(url: str):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})) as r:
        return json.load(r)


def main(argv: list[str]) -> int:
    path, pending = argv[0], argv[argv.index("--pending") + 1:] if "--pending" in argv else []
    spec = importlib.util.spec_from_file_location("mt_replay", path)
    mt = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mt)
    try:
        runs = get(f"{API}/commits/{SHA}/check-runs?per_page=100")["check_runs"]
        rules = get(f"{API}/rules/branches/main")
    except OSError as e:
        print(f"UNREADABLE: {e}")
        return 1
    req = sorted({c["context"] for r in rules if r["type"] == "required_status_checks"
                  for c in r["parameters"]["required_status_checks"]} - set(mt.PR_ONLY))
    for c in runs:
        if c["name"] in pending:
            c.update(status="in_progress", conclusion=None)
    body = "\n".join(json.dumps(c) for c in runs)
    with tempfile.TemporaryDirectory() as d:
        mt.Train("tvofi/heatpump_optimizer", Path(d), None, "", (), 1,
                 run=lambda a, cwd=None, stdin=None: (0, body), sleep=lambda s: None,
                 overlap=True, base="batch/replay").main_green(
            SHA, req, "after #N's unproved merge: revert it first")
    print("END")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
