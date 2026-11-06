#!/usr/bin/env python3
"""R10-CI-SLIM card C7: the job-minutes (a), (b) and (c) remove, replayed on a
recorded sample with the PRODUCTION rules.

    python3 dev/audit/harnesses/r10_ci_slim/c7_replay.py SAMPLE.json [--tree DIR]

--tree is the checkout whose tools/ci/prelude.py and tools/pr/codeql_scope.py
decide (default: this tree; give a merge-base worktree for the control: it
has no prelude.machinery or pins_due, and its decide analyzes any .py, so it
idles nothing it did not idle in the window).

THE RULE. Each pull_request run of kind `code` in SAMPLE.json (edit_runs.py
--fetch) is judged on its own diff: `git diff --name-only --no-renames
B...H`, H its head, B the newest first-parent commit of origin/main created
before the run (the PR's base at run time; the commits must be fetchable,
and a run whose diff cannot be read is left as it ran and counted). A job
costs completed_at - started_at.
  (a) prelude.machinery(diff) false: tests / arch-instrument, tests / closures,
      governance / env-matrix are priced at their shortest instance in the
      sample (a stand-down still starts a runner); governance /
      instrument-self-tests at 0 (it skips whole).
  (b) codeql_scope.decide(leg, "pull_request", diff) skip where the run
      analyzed: codeql / Analyze (leg) priced at its shortest instance.
  (c) prelude.pins_due(delta) false, delta = git diff P...H with P the head of
      the same PR's previous code run in the sample (none: due), counted only
      where a code run of that PR at P concluded the pins measurement
      (prelude.pins_measured) on the jobs that had COMPLETED by this run's
      created_at -- a job finishing later is unfinished when this run's prelude
      reads it, as production reads it: every tests / mutation-pins shard and
      tests / mutation-autofix at 0. A tree without pins_measured (round 2's
      rule) takes the delta from P whatever P's runs concluded.
Push and dispatch runs are unchanged by construction (each rule reads a pull
request only) and are counted in the total only.
"""
from __future__ import annotations

import argparse
import importlib.util
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


def load(path: Path, name: str):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(f"{name}_{abs(hash(str(path)))}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp() if s else None


def minutes(j) -> float:
    a, b = ts(j.get("started_at")), ts(j.get("completed_at"))
    return (b - a) / 60 if a is not None and b is not None and b >= a else 0.0


def git(*a) -> "str | None":
    p = subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True)
    return p.stdout if p.returncode == 0 else None


def diff(base: str, head: str) -> "list[str] | None":
    out = git("diff", "--name-only", "--no-renames", f"{base}...{head}")
    return None if out is None else [x for x in out.splitlines() if x]


MACHINE = ("tests / arch-instrument", "tests / closures", "governance / env-matrix")


def main(argv) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("sample")
    ap.add_argument("--tree", default=str(ROOT))
    a = ap.parse_args(argv)
    tree = Path(a.tree)
    pre = load(tree / "tools" / "ci" / "prelude.py", "prelude")
    cq = load(tree / "tools" / "pr" / "codeql_scope.py", "codeql_scope")
    machinery = getattr(pre, "machinery", lambda f: True)
    pins_due = getattr(pre, "pins_due", lambda f: True)
    runs = json.loads(Path(a.sample).read_text())["runs"]
    total = sum(minutes(j) for r in runs for j in r["jobs"])
    floor: dict[str, float] = {}
    for r in runs:
        for j in r["jobs"]:
            m = minutes(j)
            if j.get("completed_at") and m > 0:
                floor[j["name"]] = min(floor.get(j["name"], m), m)
    code = sorted((r for r in runs if r["event"] == "pull_request"
                   and (pre.parse_title(r["title"]) or ("",))[0] == "code"), key=lambda r: r["created_at"])
    pins_measured = getattr(pre, "pins_measured", None)
    seen_head: dict[str, str] = {}
    at_head: dict[tuple, list] = {}       # (pr, head) -> that PR's code runs at head, in created order
    kept: dict[str, set] = {}             # product PRs whose lanes ran, and the files that kept them
    saved = {"a": 0.0, "b": 0.0, "c": 0.0}
    before = {"a": 0.0, "b": 0.0, "c": 0.0}
    n = {"runs": 0, "unread": 0, "a": 0, "b_legs": 0, "c": 0}
    for r in code:
        pr = pre.parse_title(r["title"])[1]
        head = r["head_sha"]
        base = (git("rev-list", "-1", "--first-parent", f"--before={r['created_at']}", "origin/main") or "").strip()
        files = diff(base, head) if base else None
        prev = seen_head.get(pr)
        seen_head[pr] = head
        at_head.setdefault((pr, head), []).append(r)
        n["runs"] += 1
        jobs = r["jobs"]
        for j in jobs:
            m = minutes(j)
            if j["name"] in MACHINE or j["name"] == "governance / instrument-self-tests":
                before["a"] += m
            elif j["name"].startswith("codeql / Analyze"):
                before["b"] += m
            elif j["name"].startswith(("tests / mutation-pins", "tests / mutation-autofix")):
                before["c"] += m
        if files is None:
            n["unread"] += 1
            continue
        if any(f.startswith("custom_components/") for f in files) and machinery(files):
            keep = sorted({"/".join(f.split("/")[:2]) for f in files if machinery([f])})
            kept[pr] = kept.get(pr, set()) | set(keep)
        if not machinery(files):
            n["a"] += 1
            for j in jobs:
                m = minutes(j)
                if j["name"] in MACHINE:
                    saved["a"] += max(0.0, m - floor.get(j["name"], 0.0))
                elif j["name"] == "governance / instrument-self-tests":
                    saved["a"] += m
        for leg in cq.LEGS:
            if cq.decide(leg, "pull_request", files)[0] == "skip":
                for j in jobs:
                    if j["name"] == f"codeql / Analyze ({leg})":
                        s = max(0.0, minutes(j) - floor.get(j["name"], 0.0))
                        if s > 0:
                            n["b_legs"] += 1
                        saved["b"] += s
        t0 = ts(r["created_at"])

        def as_of(run):
            return {j["name"]: ("completed", j.get("conclusion")) if ts(j.get("completed_at")) is not None
                    and ts(j["completed_at"]) <= t0 else ("in_progress", None) for j in run["jobs"]}
        concluded = pins_measured is None or any(pins_measured(as_of(q)) for q in at_head.get((pr, prev), ()))
        if prev and prev != head and not concluded:
            n["c_unmeasured"] = n.get("c_unmeasured", 0) + 1
        delta = diff(prev, head) if prev and prev != head and concluded else None
        if delta is not None and not pins_due(delta):
            pins = [j for j in jobs if j["name"].startswith(("tests / mutation-pins", "tests / mutation-autofix"))]
            if any(minutes(j) > 0 for j in pins):
                n["c"] += 1
            saved["c"] += sum(minutes(j) for j in pins)
    print(f"tree {tree}: {n['runs']} pull_request code runs ({n['unread']} diffs unreadable, left as run); "
          f"ci.yml job-minutes in the sample {total:.0f}")
    for k, label in (("a", f"(a) machinery lanes, {n['a']} product-only runs idled"),
                     ("b", f"(b) CodeQL on pull requests, {n['b_legs']} analyzed legs now skipped"),
                     ("c", f"(c) mutation-pins + autofix, {n['c']} runs whose delta had no product file")):
        print(f"{label}: {before[k]:.0f} -> {before[k] - saved[k]:.0f} job-minutes on pull_request code runs "
              f"(saving {saved[k]:.0f}, {100 * saved[k] / total:.1f}% of the sample)")
    print(f"(a) product pull requests (diff reaches custom_components/) that kept the machinery lanes: {len(kept)}; "
          f"files that kept them, by top two path parts: "
          f"{sorted({k for v in kept.values() for k in v})}")
    print(f"(c) runs whose previous head had not concluded its pins measurement (delta not taken, measures): "
          f"{n.get('c_unmeasured', 0)}")
    s = sum(saved.values())
    print(f"together: saving {s:.0f} of {total:.0f} job-minutes ({100 * s / total:.1f}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
