#!/usr/bin/env python3
"""Decide whether a heavy Tests lane may SKIP a rerun it provably cannot change.

The merge train re-asks the whole CI gate every time it carries a pull request
over a main that moved, and a re-dispatch re-asks it after a flake: the same
branch, the same three-dot diff, hours apart, at a cost the runner pays again
for an answer it already printed. This module is the lever the owner
commissioned (2026-10-12) that lets a lane report ``skipped`` instead -- a
conclusion the merge rule already accepts, measured on an isolated probe,
both arms (dev/programme/HANDOVER.md's ruleset notes) -- but only when a
fresh run provably cannot change the answer.

Two levels, because they have different safety arguments.

LEVEL 1 -- the identical-base case, no closures involved. A lane's last green
run for this diff is recorded with the commit it was based on (the merge
base, the same ref ``fast`` resolves as ``GOLDEN_REF``). If that commit is
still this run's merge base, then base tree and diff are both unchanged, so
the tree under test is the SAME TREE byte for byte: applying an identical
patch to an identical base yields an identical tree, and a lane that already
reported green on it cannot report anything else on a rerun. This holds for
every lane, including ones no closure has ever measured (``browser``); it is
the whole safety argument and it needs nothing but ``git``.

LEVEL 2 -- the closure-intersection case, for lanes whose scripts the
closures table measures (``fast``, ``coverage``). The base HAS moved: main
merged other pull requests while this one was open. The lane's run set is
still selected from THIS pull request's diff alone (``run.sh`` diffs against
the merge base, and the merge base's tip is what ``GOLDEN_REF`` resolves to),
so the same scripts would run -- but they would read them from a tree that
now carries main's delta. The rerun can only differ from the recorded green
run through a file main's delta touched that a selected script reads. So:
resolve main's delta (base..base) through tests/closures.json exactly as
``select`` resolves a diff, and skip only when NOTHING main changed lies in
any selected script's measured closure. Empty intersection -> skip; any
intersection -> run and pay.

The guard rails, each of which ``self-test`` pins by name:

* a planted defect in main's delta that intersects the selected closure
  MUST land on RUN (the planted-defect arm below -- the decision function's
  teeth, not a hope);
* a delta file no closure has measured and nothing declares INERT fails
  LOUD, the lane runs -- never a silent skip on the strength of a file the
  table never saw, the same refusal ``select`` makes for a diff;
* a gate file in the delta (tests.yml above all) runs every lane, because a
  gate file invalidates every closure at once;
* a push to main never reaches this code: the lanes that consult it are
  eligible on ``pull_request`` and the train's re-check dispatch only, and
  on every other event the workflow leaves the decision unset, which the
  lanes read as RUN. CLAUDE.md rule 1's forced ``full`` stays forced.

WHAT THE LEVER COSTS, said plainly. A main-side break that lands inside a
skipped lane's closure is no longer caught by this pull request's rerun: it
is caught one merge later, by the push-to-main run of the FULL unscoped
suite on the merged tree -- the same backstop that already underwrites
GATE_SCOPE=auto (CLAUDE.md rule 1: "main goes red within one merge instead
of never"). The lever extends the closures table's existing trust from the
pull request's own diff to main's delta; the table is wrong in exactly the
worlds where the scoped gate is already wrong, and the same full run
catches both.

This is an instrument, not a test: it never runs in the suite, it runs in
the workflow's decision steps. It is a gate file for the same reason
tests/run.sh is -- a change here changes what the lanes run.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import closure  # noqa: E402 - the closure semantics this decision extends

ROOT = Path(__file__).resolve().parent.parent

# Lanes whose scripts tests/closures.json measures: for these, Level 2 can
# resolve main's delta through the table. `fast` runs the suite run.sh
# selects; `coverage` measures the same selection under a tracer
# (coverage_tree.sh reads W5P_SCOPE from the same `closure.py select` plan),
# so a script whose inputs did not move cannot move either lane's verdict.
CLOSURE_LANES = ("fast", "coverage")

# The state is one small JSON file per (lane, branch, diff), restored from
# actions/cache by the workflow before this runs. The cache's eviction policy
# (LRU, seven-day unused) can make it disappear; a missing state is a RUN,
# never a skip, so eviction costs a runner and nothing else.
STATE_VERSION = 1


def _git(*args: str) -> str:
    out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit(f"lane_skip: git {' '.join(args)} failed: {out.stderr.strip()}")
    return out.stdout.strip()


def _run(reason: str, **extra: object) -> dict:
    return {"decision": "run", "reason": reason, **extra}


def _skip(level: int, reason: str, **extra: object) -> dict:
    return {"decision": "skip", "level": level, "reason": reason, **extra}


def decide(lane: str, *, prev_base: str | None, base: str,
           main_delta: list[str], plan: dict, payload: dict) -> dict:
    """One lane's skip decision. Pure: every input is data a test can forge.

    ``prev_base`` is the commit the recorded green run was based on (None
    when no state was restored); ``base`` is this run's merge base;
    ``main_delta`` is what changed between the two (empty when they are the
    same commit); ``plan`` is the `closure.select` plan for this pull
    request's three-dot diff; ``payload`` is the committed closures table.
    """
    if prev_base is None:
        return _run("no recorded green run for this lane and diff",
                    prev_base=None, base=base)
    if prev_base == base:
        return _skip(1, f"identical base {base} and identical diff: the tree "
                        f"under test is byte-for-byte the tree this lane "
                        f"already passed on",
                     prev_base=prev_base, base=base, level_hint=None)
    if lane not in CLOSURE_LANES:
        return _run(f"main moved ({prev_base[:12]} -> {base[:12]}) and {lane} "
                    f"has no measured closure, so only the identical-base "
                    f"case is provable",
                    prev_base=prev_base, base=base)

    # From here the argument is the closures table's, so every way the table
    # could be blind in main's delta has to fail LOUD -- onto RUN, the
    # expensive answer, never onto skip.
    m = list(main_delta)
    closures = payload["closures"]

    gate = sorted(f for f in m if closure.is_gate_file(f))
    if gate:
        return _run(f"main's delta touches the gate itself ({', '.join(gate[:3])}"
                    f"{' ...' if len(gate) > 3 else ''}), so every closure is "
                    f"suspect", prev_base=prev_base, base=base)

    known = {f for files_ in closures.values() for f in files_}
    unmapped = [f for f in m
                if closure.unit_of(f) not in known and not closure.is_inert(f)]
    if unmapped:
        return _run("main's delta touches files no recorded closure has "
                    "measured and nothing declares INERT: "
                    + ", ".join(unmapped[:6])
                    + (" ..." if len(unmapped) > 6 else "")
                    + " -- an unmeasured file is not a safe skip",
                    prev_base=prev_base, base=base)

    # The run set is the lane's own selection for THIS diff. A `full` plan
    # carries every selectable script in the same field, so the conservative
    # shape -- a plan that refuses to scope (this pull request edits a gate
    # file, say) is a plan whose lane runs everything -- falls out of the
    # same read; the fallback is for forged plans only.
    scripts = list(plan.get("run")) or closure.selectable_scripts()

    units = {closure.unit_of(f) for f in m}
    hits: dict[str, list[str]] = {}
    for s in scripts:
        found = sorted(units & set(closures[s]))
        if found:
            hits[s] = found
        elif f"tests/{s}" in m:
            # The script's own file IS its input; a closure does not have to
            # list it for this to change the script's answer.
            hits[s] = [f"tests/{s}"]
    # A recorded inert read is a recorded read (#2109): parity with
    # `affected`, which re-derives on the same evidence.
    for s, info in closure.inert_read_owners(
            m, payload.get("inert_reads", {}), set(scripts)).items():
        hits.setdefault(s, info["changed"] or ["inert read"])
    # `select`'s integration belt, applied to main's delta: env_drift runs a
    # behavioural diff over the whole package whether or not the closure saw
    # the file, so a package file in the delta moves its answer.
    if "tests/env_drift.py" in scripts and any(
            f.startswith("custom_components/")
            and not closure._is_frontend_asset(f) for f in m):
        hits.setdefault("tests/env_drift.py", ["custom_components/ (belt)"])

    if hits:
        named = ", ".join(f"{s} <- {hits[s][0]}" for s in list(hits)[:4])
        return _run(f"main's delta reaches {len(hits)} of the {len(scripts)} "
                    f"script(s) this lane would run: {named}"
                    + ("" if len(hits) <= 4 else " ..."),
                    prev_base=prev_base, base=base, hits=hits)

    return _skip(2, f"main moved ({prev_base[:12]} -> {base[:12]}, "
                    f"{len(m)} file(s)) but no selected script reads any of "
                    f"it: the recorded green run's inputs are unchanged",
                 prev_base=prev_base, base=base)


def read_state(path: str | None) -> dict | None:
    """The restored state file, or None. Malformed state is None: RUN."""
    if not path:
        return None
    p = Path(path)
    if not p.is_file():
        return None
    try:
        state = json.loads(p.read_text())
        if state.get("version") != STATE_VERSION:
            return None
        return state
    except (json.JSONDecodeError, OSError):
        return None


def new_state(lane: str, base: str, diff_hash: str) -> dict:
    return {"version": STATE_VERSION, "lane": lane, "base": base,
            "diff": diff_hash,
            "recorded_at": _dt.datetime.now(_dt.timezone.utc).isoformat()}


def _decide_cmd(lane: str, diff_ref: str, state_file: str | None,
                workdir: str) -> int:
    base = _git("merge-base", diff_ref, "HEAD")
    # The patch hash is over the committed three-dot diff only. In CI there
    # is nothing uncommitted; on a developer's box keying the state on the
    # committed diff means a dirty tree never reuses a proof.
    patch = subprocess.run(["git", "diff", f"{base}...HEAD"], cwd=ROOT,
                           capture_output=True, text=True, check=True).stdout
    diff_hash = hashlib.sha256(patch.encode()).hexdigest()
    files = closure.changed_files(diff_ref)
    payload = json.loads(closure.CLOSURES.read_text())
    try:
        plan = closure.select(files, closure.base_closures(diff_ref))
    except SystemExit as exc:
        plan = {"mode": "full", "reason": f"select refused: {exc}",
                "run": [], "skip": {}}

    state = read_state(state_file)
    prev_base = state["base"] if state and state.get("lane") == lane else None
    main_delta: list[str] = []
    if prev_base and prev_base != base:
        # An ancestor check, not optimism: the recorded base must lie on
        # main's history behind this one, or the two diffs name unrelated
        # trees and nothing can be concluded. Fail loud onto RUN.
        probe = subprocess.run(["git", "merge-base", "--is-ancestor",
                                prev_base, base], cwd=ROOT)
        if probe.returncode != 0:
            prev_base = None
            plan = dict(plan, reason=(plan.get("reason") + "; "
                                      "recorded base is not an ancestor"))
        else:
            main_delta = [l for l in _git("diff", "--name-only",
                                          prev_base, base).splitlines() if l]

    decision = decide(lane, prev_base=prev_base, base=base,
                      main_delta=main_delta, plan=plan, payload=payload)

    out = Path(workdir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "lane_skip.json").write_text(json.dumps(
        {**decision, "lane": lane, "diff": diff_hash}, indent=1))
    (out / "decision").write_text(decision["decision"] + "\n")
    (out / "base").write_text(base + "\n")
    (out / "diff").write_text(diff_hash + "\n")
    # The state a green run of this lane would record at exactly this base
    # and diff. The workflow's proof job catpures this file as an output and
    # saves it in the cache only once the lane has actually run green --
    # never here, where the lanes have not run yet.
    (out / "state.json").write_text(json.dumps(
        new_state(lane, base, diff_hash)) + "\n")

    level = f" (level {decision['level']})" if decision.get("level") else ""
    print("########## lane skip ##########")
    print(f"  LANE: {lane} -- {decision['decision'].upper()}{level}")
    print(f"  base: {base}" + (f" (recorded green: {decision.get('prev_base')})"
                              if decision.get("prev_base") else ""))
    print(f"  diff: {diff_hash}")
    for line in decision["reason"].splitlines() or [decision["reason"]]:
        print(f"  {line}")
    if main_delta:
        print(f"  main's delta ({len(main_delta)} file(s)):")
        for f in main_delta[:30]:
            print(f"      {f}")
        if len(main_delta) > 30:
            print(f"      ... and {len(main_delta) - 30} more")
    return 0


def self_test() -> int:
    """The decision's teeth, on forged inputs (no git, no tree).

    Every arm is a case the workflow can really meet, and the two mutants a
    careless edit of `decide` produces -- always-skip and always-run -- each
    redden a pinned arm below. Run with a mutant of `decide` patched in,
    this exits 1; the unmodified tree exits 0.
    """
    import tempfile

    payload = {
        "closures": {
            "tests/entities.py": ["README.md", "tests/harness.py"],
            "tests/env_drift.py": ["custom_components/heatpump_optimizer/const.py",
                                   "tests/golden/config_flow.json"],
            "tests/card.mjs": ["custom_components/heatpump_optimizer/const.py"],
        },
        "inert_reads": {"tests/card.mjs": ["docs/"]},
    }
    plan = {"mode": "scoped", "run": ["tests/entities.py", "tests/env_drift.py",
                                      "tests/card.mjs"], "skip": {}}
    BASE = "b" * 40
    PREV = "a" * 40
    results: list[tuple[str, bool, str]] = []

    def pin(name: str, cond: bool, detail: str = "") -> None:
        results.append((name, cond, detail))

    def d(lane="fast", prev=PREV, base=BASE, delta=(), p=plan, pay=payload):
        return decide(lane, prev_base=prev, base=base, main_delta=list(delta),
                      plan=p, payload=pay)

    # -- Level 1, the exact case ------------------------------------------
    r = d(base=PREV)
    pin("identical base skips at level 1",
        r["decision"] == "skip" and r.get("level") == 1, r["reason"])
    r = d(prev=None)
    pin("no recorded green runs", r["decision"] == "run", r["reason"])

    # -- Level 2, the disjoint case ---------------------------------------
    r = d(delta=["LICENSE"])              # INERT, and nothing watches it
    pin("an inert-only delta skips at level 2",
        r["decision"] == "skip" and r.get("level") == 2, r["reason"])
    r = d(delta=["README.md"])              # entities.py is selected and reads it
    pin("a delta file in a selected script's closure runs",
        r["decision"] == "run" and "tests/entities.py" in r.get("hits", {}),
        r["reason"])
    r = d(delta=["tests/card.mjs"])
    pin("the script's own file in the delta runs",
        r["decision"] == "run", r["reason"])
    # A file only a script OUTSIDE the run set reads: that script does not
    # run, so the lane's answer cannot move through it.
    narrow = {"mode": "scoped", "run": ["tests/entities.py"], "skip": {}}
    r = d(delta=["custom_components/heatpump_optimizer/const.py"], p=narrow)
    pin("a delta file only an unselected script reads skips",
        r["decision"] == "skip", r["reason"])
    # The planted defect, stated as the guard rail demands it: main merges a
    # change to the coordinator's const.py while the pull request's diff has
    # selected env_drift.py (an integration change did). The rerun MUST run.
    r = d(delta=["custom_components/heatpump_optimizer/const.py",
                 "docs/guide.md"])
    pin("a planted defect inside a selected closure runs",
        r["decision"] == "run" and r.get("hits", {}).get("tests/env_drift.py"),
        r["reason"])
    # The belt: a package file the closure never listed still runs env_drift.
    belted = {"mode": "scoped", "run": ["tests/entities.py",
                                        "tests/env_drift.py"], "skip": {}}
    payload_no_const = {"closures": {
        "tests/entities.py": ["README.md"],
        "tests/env_drift.py": ["tests/golden/config_flow.json"],
        "tests/card.mjs": ["custom_components/heatpump_optimizer/const.py",
                           "custom_components/heatpump_optimizer/coordinator.py"],
    }, "inert_reads": {}}
    r = d(delta=["custom_components/heatpump_optimizer/coordinator.py"],
          p=belted, pay=payload_no_const)
    pin("the integration belt runs env_drift on a package delta",
        r["decision"] == "run" and "tests/env_drift.py" in r.get("hits", {}),
        r["reason"])
    # A recorded inert read by a selected script.
    r = d(delta=["docs/"])                  # card.mjs watches docs/
    pin("a recorded inert read of the delta runs its owner",
        r["decision"] == "run" and "tests/card.mjs" in r.get("hits", {}),
        r["reason"])

    # -- Fail loud ---------------------------------------------------------
    r = d(delta=[".github/workflows/tests.yml", "docs/guide.md"])
    pin("a gate file in the delta runs",
        r["decision"] == "run", r["reason"])
    r = d(delta=["brandnew/unmeasured.py"])
    pin("an unmeasured delta file runs", r["decision"] == "run", r["reason"])
    r = d(delta=["tests/run.sh"])
    pin("tests/run.sh in the delta runs", r["decision"] == "run", r["reason"])
    # A full-mode plan intersects every script, so a delta file any script
    # reads runs -- the lane that refuses to scope cannot skip either.
    r = d(delta=["README.md"],
          p={"mode": "full",
             "run": ["tests/entities.py", "tests/env_drift.py",
                     "tests/card.mjs"], "skip": {}})
    pin("a full-mode plan still runs on a closure hit",
        r["decision"] == "run", r["reason"])

    # -- The no-closure lane ----------------------------------------------
    r = d(lane="browser", base=PREV)
    pin("browser skips only on the identical base",
        r["decision"] == "skip" and r.get("level") == 1, r["reason"])
    r = d(lane="browser", delta=["docs/guide.md"])
    pin("browser runs when the base moves",
        r["decision"] == "run", r["reason"])

    # -- State reading -----------------------------------------------------
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "state.json"
        p.write_text(json.dumps(new_state("fast", BASE, "d" * 16)))
        s = read_state(str(p))
        pin("a well-formed state file reads back",
            bool(s) and s["base"] == BASE and s["version"] == STATE_VERSION)
        p.write_text("{not json")
        pin("a malformed state file is no state", read_state(str(p)) is None)
        p.write_text(json.dumps({"version": 99, "lane": "fast", "base": BASE}))
        pin("a foreign state version is no state",
            read_state(str(p)) is None)
        pin("a missing state file is no state",
            read_state(str(Path(td) / "absent.json")) is None)
        # A state restored for a DIFFERENT lane must not skip this one.
        p.write_text(json.dumps(new_state("coverage", PREV, "d" * 16)))
        pin("a state for another lane is no state for this one",
            read_state(str(p))["lane"] != "fast")

    failed = [r for r in results if not r[1]]
    for name, ok, detail in results:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}"
              + ("" if ok else f"  -- {detail}"))
    print(f"lane_skip self-test: {len(results) - len(failed)}/{len(results)} "
          f"pins passed")
    return 1 if failed else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    dec = sub.add_parser("decide", help="one lane's skip decision, from git")
    dec.add_argument("--lane", required=True,
                     help="the lane deciding: fast, coverage, browser")
    dec.add_argument("--diff-ref", default="origin/main",
                     help="the ref the three-dot diff is taken against "
                          "(fast's GOLDEN_REF)")
    dec.add_argument("--state-file", default=None,
                     help="the restored proof-state JSON; absent means run")
    dec.add_argument("--workdir", required=True,
                     help="where the decision files are written")
    sub.add_parser("self-test", help="the decision's pins, on forged inputs")
    sub.add_parser("new-state", help="print a fresh state file's JSON")
    st = sub.add_parser("state", help="print the state JSON, base and diff "
                                      "given explicitly (no git needed)")
    st.add_argument("--lane", required=True)
    st.add_argument("--base", required=True)
    st.add_argument("--diff", required=True)
    args = ap.parse_args()

    if args.cmd == "self-test":
        return self_test()
    if args.cmd == "decide":
        return _decide_cmd(args.lane, args.diff_ref, args.state_file,
                           args.workdir)
    if args.cmd == "new-state":
        base = _git("merge-base", args.diff_ref, "HEAD")
        patch = subprocess.run(["git", "diff", f"{base}...HEAD"], cwd=ROOT,
                               capture_output=True, text=True,
                               check=True).stdout
        dh = hashlib.sha256(patch.encode()).hexdigest()
        print(json.dumps(new_state(args.lane, base, dh), indent=1))
        return 0
    if args.cmd == "state":
        print(json.dumps(new_state(args.lane, args.base, args.diff)))
        return 0
    raise SystemExit("lane_skip: unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
