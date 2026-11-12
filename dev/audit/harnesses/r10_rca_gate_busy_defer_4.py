#!/usr/bin/env python3
"""R10-RCA-GATE-BUSY-DEFER-4: the merge train's classifier reads gate.py's deferral red as RED.

    python3 -I dev/audit/harnesses/r10_rca_gate_busy_defer_4.py record     # prints fixture JSON (gh api)
    python3 -I dev/audit/harnesses/r10_rca_gate_busy_defer_4.py replay [--tree DIR]

An edit run's `gate` concludes `failure` with the deferral text at once (gate.py `deferral`)
while the code run it defers to is unfinished; gate-sweep.yml re-runs it after the code run
completes. A reader that keys on the check run's conclusion alone reads that as a verdict.

record  reads the check runs and the ci.yml runs listing of the three evidence heads (#3293
        fefaa492, #3267 cc6ee11f, #3268 64fe84b2) from the GitHub API, trimmed to the fields the
        train reads, for dev/audit/harnesses/r10_rca_gate_busy_defer_4.json.
replay  puts each scene through DIR's merge_train (default: this tree; a baseline is
        `git archive <sha> tools custom_components/heatpump_optimizer/manifest.json | tar -x -C $D`
        and `--tree $D`). The reader is `Train.classify_at` when the program has it, else
        `classify(latest_runs(runs), required)` -- the one-read `classify` subcommand's read.
        Scenes: the three evidence heads at the moment their edit gate concluded (the code run
        unfinished: the recorded listings, cut at that instant), a SETTLE-GAP scene (the same
        head with the code run's gate green and the edit gate not yet re-run: built from the
        #3293 fixture, synthetic, flagged so), and three null controls (a real code-run red, an
        all-green head, a red non-gate required context beside a running code run).
        Prints one `SCENE name state` line each, then `RESULT replay defects=<n> scenes=<m>`;
        rc 1 when a deferral scene reads RED (DEFERRAL-READ-RED) or a null control reads wrong.
        SETTLE-GAP reads are printed and counted apart (`settle_gap=`); they are not in `defects`.
"""
from __future__ import annotations

import copy
import importlib
import json
import subprocess
import sys
from datetime import datetime
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


ROOT = repo_root(__file__)
FIXTURE = Path(__file__).with_suffix(".json")
REPO = "tvofi/heatpump_optimizer"
HEADS = {"3293": "fefaa4926e36e9c571cc685e0b6aa2b391d14793", "3267": "cc6ee11ff27b8b57cd7e017121544dca9dbe6e30",
         "3268": "64fe84b24efb6e4f720e011b75b559b6a3bac7e9"}
CR_KEYS = ("id", "name", "status", "conclusion", "started_at", "completed_at")


def gh(path):
    out = subprocess.run(["gh", "api", "--paginate", "--jq", ".check_runs[]?, .workflow_runs[]?", path],
                         capture_output=True, text=True, check=True).stdout
    return [json.loads(x) for x in out.splitlines() if x.strip()]


def record():
    fx = {}
    for pr, sha in HEADS.items():
        crs = [dict({k: c.get(k) for k in CR_KEYS}, check_suite={"id": (c.get("check_suite") or {}).get("id")})
               for c in gh(f"repos/{REPO}/commits/{sha}/check-runs?per_page=100")]
        runs = [{k: r.get(k) for k in ("id", "check_suite_id", "display_title", "status", "conclusion",
                                       "created_at", "updated_at")}
                for r in gh(f"repos/{REPO}/actions/workflows/ci.yml/runs?head_sha={sha}&per_page=100")]
        fx[pr] = {"head": sha, "check_runs": crs, "runs": runs}
    print(json.dumps(fx, indent=1, sort_keys=True))


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def as_of(scene, t):
    """The listings as they read at instant <t>: a job or run not yet started is absent; one
    that concluded after <t> is in progress."""
    crs = []
    for c in copy.deepcopy(scene["check_runs"]):
        if c["started_at"] and ts(c["started_at"]) > t:
            continue
        if c["completed_at"] and ts(c["completed_at"]) > t:
            c["status"], c["conclusion"] = "in_progress", None
        crs.append(c)
    runs = []
    for r in copy.deepcopy(scene["runs"]):
        if r["status"] == "completed" and ts(r["updated_at"]) > t:
            r["status"], r["conclusion"] = "in_progress", None
        runs.append(r)
    return crs, runs


def load_train(tree):
    for m in [k for k in sys.modules if k in ("merge_train", "gh_read")]:
        del sys.modules[m]
    sys.path.insert(0, str(Path(tree) / "tools/audit/seat"))
    try:
        return importlib.import_module("merge_train")
    finally:
        sys.path.pop(0)


def read(mt, crs, runs, head):
    """(state, pending, red) as the train's one-read classifier gives it at <head>."""
    req = [mt.GATE]
    if not hasattr(mt.Train, "classify_at"):
        return mt.classify(mt.latest_runs(crs), req)
    t = object.__new__(mt.Train)
    t.repo, t.log = REPO, lambda *a, **k: None
    t.run = lambda argv: (0, "\n".join(json.dumps(r) for r in runs))
    # the wall clock `sweep_settling` reads: five seconds after the newest completion in the scene
    now = max([ts(c["completed_at"]) for c in crs if c.get("completed_at")] or [0]) + 5
    t.wall = lambda: now
    return t.classify_at(head, crs, req)


def unit(name, suite, status="completed", conclusion="success", at="2026-11-07T21:05:00Z", cid=1):
    return {"id": cid, "name": name, "status": status, "conclusion": conclusion if status == "completed" else None,
            "started_at": at, "completed_at": at if status == "completed" else None, "check_suite": {"id": suite}}


def scenes():
    fx = json.loads(FIXTURE.read_text())
    out = []
    for pr, sc in fx.items():
        gate = next(c for c in sc["check_runs"] if c["name"] == "gate")
        out.append((f"#{pr}-edit-gate-just-failed", "WAIT", "defect", sc["head"], *as_of(sc, ts(gate["completed_at"]) + 5)))
    sc = fx["3293"]
    gate = next(c for c in sc["check_runs"] if c["name"] == "gate")
    crs, runs = as_of(sc, ts(gate["completed_at"]) + 5)
    code = next(r for r in runs if "code" in r["display_title"])
    code["status"], code["conclusion"] = "completed", "success"
    crs = crs + [unit("gate", code["check_suite_id"], at="2026-11-07T21:20:00Z", cid=9)]
    out.append(("#3293-settle-gap(synthetic)", "WAIT", "settle-gap", sc["head"], crs, runs))
    code_red = [dict(c) for c in crs]
    code_red[-1] = dict(code_red[-1], conclusion="failure")
    out.append(("null-code-run-red(synthetic)", "RED", "null", sc["head"], code_red, runs))
    all_green = [dict(c, conclusion="success") if c["name"] == "gate" else c for c in crs]
    out.append(("null-all-green(synthetic)", "GREEN", "null", sc["head"], [c for c in all_green if c["name"] != "gate"
                or c["check_suite"]["id"] == code["check_suite_id"]], [dict(r, status="completed") for r in runs]))
    return out


def replay(tree):
    mt = load_train(tree)
    defects = gap = bad = 0
    fx = json.loads(FIXTURE.read_text())
    rows = scenes()
    for name, want, kind, head, crs, runs in rows:
        state, pending, red = read(mt, crs, runs, head)
        got = state.upper()
        print(f"SCENE {name} want={want} got={got} pending={pending} red={red}")
        if got != want:
            if kind == "defect" and got == "RED":
                defects += 1
            elif kind == "settle-gap":
                gap += 1
            else:
                bad += 1
    # the non-gate null: a red non-gate required context beside a running code run is RED for any program
    crs, runs = as_of(fx["3293"], ts("2026-11-07T21:07:00Z"))
    crs = crs + [unit("fast", 99, conclusion="failure")]
    req = ["fast"]
    idle = (mt.gate_busy([], []),) if hasattr(mt, "Busy") else ()  # a tree whose classify requires busy: none at this head
    st = (mt.classify(mt.latest_runs(crs), req, *idle))[0].upper()
    print(f"SCENE null-red-non-gate want=RED got={st}")
    bad += st != "RED"
    print(f"RESULT replay defects={defects} settle_gap={gap} null_bad={bad} scenes={len(rows) + 1}")
    return 1 if defects or bad else 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["record"]:
        record()
    elif a[:1] == ["replay"]:
        sys.exit(replay(a[a.index("--tree") + 1] if "--tree" in a else ROOT))
    else:
        print(__doc__)
        sys.exit(2)
