#!/usr/bin/env python3
"""Mutation proof for every line #354 adds: revert it, watch a named check die.

WHAT IT MEASURES
    For each mutation -- a production line of this change put back the way it
    was, or bent one step -- whether the check that is supposed to notice
    actually fails. A mutation that leaves every check green is a line nothing
    pins.

    Metric definition, one line: mutations killed / mutations applied, where
    "killed" means the named check reports FAIL (or the run dies) with the
    mutation applied and passes without it.

RUN IT
    python3 tools/audit/round3/closures-gate/mutations.py

    Every mutation is applied in a throwaway git worktree of HEAD, so this
    never touches the tree you are working in.

EXPECTED
    RESULT killed=<n> applied=<n>, equal. Roughly two minutes: most mutations
    re-run tests/entities.py, which takes about four seconds.

BASELINE
    Measured against this branch's HEAD on darwin 25.6.0. No timing is
    claimed, so the harness contract's thread pin does not apply.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]

CLOSURE = "tests/closure.py"
DERIVE = "tests/derive_closures.sh"
WORKFLOW = ".github/workflows/tests.yml"

# (label, file, find, replace, the check whose FAIL proves the line is pinned)
#
# `find` must appear exactly once; the harness refuses a mutation that does not
# bite, which is how a mutation that silently applied to nothing was caught.
EDITS = [
    ("gate files no longer force a full re-derive", CLOSURE,
     """    gate = [f for f in files if is_gate_file(f)]
    if gate:""",
     """    gate = [f for f in files if is_gate_file(f)]
    if False:""",
     "a gate file re-derives everything, as it does for selection"),

    ("a subprocess-driven script no longer forces a full re-derive", CLOSURE,
     """    driven = [f for f in files if Path(f).name in DRIVEN_BY_OTHERS]
    if driven:""",
     """    driven = [f for f in files if Path(f).name in DRIVEN_BY_OTHERS]
    if False:""",
     "a change to a subprocess-driven script re-derives everything"),

    ("an unmeasured file no longer forces a full re-derive", CLOSURE,
     """    unmapped = [f for f in files if f not in known and not is_inert(f)]
    if unmapped:""",
     """    unmapped = [f for f in files if f not in known and not is_inert(f)]
    if False:""",
     "a file in no recorded closure re-derives everything, wherever it lives"),

    # THE mutation for the widened rule: the narrower draft, restored.
    ("the unmeasured rule is narrowed back to custom_components/", CLOSURE,
     "    unmapped = [f for f in files if f not in known and not is_inert(f)]",
     "    unmapped = [f for f in files if f not in known and not is_inert(f)\n"
     "                and f.startswith('custom_components/')]",
     "a file in no recorded closure re-derives everything, wherever it lives"),

    ("an empty diff no longer fails closed", CLOSURE,
     """    if not files:
        return _full("no changed files could be determined")""",
     """    if not files and False:
        return _full("no changed files could be determined")""",
     "an empty diff re-derives everything rather than nothing"),

    ("a script with no closure no longer forces a full re-derive", CLOSURE,
     """    uncovered = [s for s in scripts if s not in closures]
    if uncovered:""",
     """    uncovered = [s for s in scripts if s not in closures]
    if False:""",
     "a selectable script with no closure forces the full re-derivation"),

    # The ordering bug the first draft had: ask the hand list before the table.
    ("the INERT list is asked before the table", CLOSURE,
     "    gate = [f for f in files if is_gate_file(f)]",
     "    if all(is_inert(f) for f in files):\n"
     "        return {'case': 'skip', 'reason': 'all inert', 'rederive': [],\n"
     "                'why': {}, 'changed': files}\n"
     "    gate = [f for f in files if is_gate_file(f)]",
     "a file that is both INERT and inside a recorded closure is not skipped"),

    ("a scoped re-derive drops the producer it needs", CLOSURE,
     """    for consumer, producers in PRODUCERS.items():
        if consumer in why:""",
     """    for consumer, producers in PRODUCERS.items():
        if False:""",
     "a scoped re-derive pulls in the producer of anything it selects"),

    ("nothing intersecting no longer skips", CLOSURE,
     """    if not rederive:
        # Everything that changed is absent from every closure, and `unmapped`""",
     """    if False:
        # Everything that changed is absent from every closure, and `unmapped`""",
     "a docs-only change still costs the closures check nothing"),

    ("the scoped list stops being the whole plan", CLOSURE,
     '    (workdir / "affected.scripts").write_text(\n'
     '        "".join(f"{s}\\n" for s in plan["rederive"]))',
     '    (workdir / "affected.scripts").write_text("")',
     "the files the workflow reads carry the plan the predicate made"),

    ("the case file stops being the case", CLOSURE,
     '    (workdir / "affected.case").write_text(plan["case"] + "\\n")',
     '    (workdir / "affected.case").write_text("full\\n")',
     "the files the workflow reads carry the plan the predicate made"),

    ("--partial stops being honoured", CLOSURE,
     """    unmeasured = [] if partial else [
        s for s in selectable_scripts() if s not in records]""",
     """    unmeasured = [
        s for s in selectable_scripts() if s not in records]""",
     "and is accepted when it does"),

    ("--partial drops the under-approximation check too", CLOSURE,
     "        missing = sorted(set(files) - have)",
     "        missing = [] if partial else sorted(set(files) - have)",
     "but a partial check still fails on a closure that under-approximates"),
]


def run(cmd, cwd, env=None, **kw):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                          env=env, **kw)


# The rule under test lives in `affected`; several of its lines read the same
# as lines in `select` above it, so the mutation is confined to that function
# or it would bite twice and prove nothing about either.
REGION = ("def affected(files: list[str]) -> dict:", "def main() -> int:")


def entities_failures(wt: Path) -> set[str]:
    env = dict(os.environ, PYTHONPATH="tests/hastub")
    p = run([sys.executable, "tests/entities.py"], wt, env)
    out = p.stdout + p.stderr
    if "Traceback" in out:
        return {"<the run died>"}
    # A failing line is "  FAIL  <name>  [<detail>]"; the name is what a
    # mutation is expected to kill, so the detail is cut off here.
    return {m.group(1).strip()
            for m in re.finditer(r"^\s*FAIL\s+(.*?)(?:\s\s+\[.*)?$", out, re.M)}


def apply_edit(src: str, find: str, repl: str, region: bool) -> str | None:
    """Replace `find` exactly once.

    Inside the `affected` region first -- several of its lines read the same as
    lines in `select` -- and over the whole file when the pattern is not there
    at all (the `check --partial` mutations, which live elsewhere).
    """
    spans = [(0, len(src))]
    if region and REGION[0] in src and REGION[1] in src:
        spans.insert(0, (src.index(REGION[0]), src.index(REGION[1])))
    for lo, hi in spans:
        body = src[lo:hi]
        if body.count(find) == 1:
            return src[:lo] + body.replace(find, repl) + src[hi:]
    return None


# ---------------------------------------------------------------------------
# two mutations whose subject is not a Python line


def probe_record_only(wt: Path, mutated: bool) -> bool:
    """--single --record-only must leave tests/closures.json alone.

    Before this change --single ignored --record-only and always merged, which
    on the scoped path would overwrite the committed table with what the run
    just measured -- and the check that follows would compare the file against
    itself.
    """
    if mutated:
        p = wt / DERIVE
        src = p.read_text()
        src = src.replace(
            """  if [ "$MERGE" -eq 1 ]; then
    $PYTHON tests/closure.py merge --in-dir "$OUTDIR" --partial
    exit $?
  fi""",
            """  $PYTHON tests/closure.py merge --in-dir "$OUTDIR" --partial
  exit $?""")
        p.write_text(src)
    out = wt / "rec"
    env = dict(os.environ, PYTHONPATH=str(wt / "tests" / "hastub"))
    run(["./tests/derive_closures.sh", "--single", "tests/open_meteo.py",
         "--record-only", "--out-dir", str(out)], wt, env)
    dirty = run(["git", "status", "--porcelain", "tests/closures.json"], wt)
    shutil.rmtree(out, ignore_errors=True)
    return bool(dirty.stdout.strip())        # True == the table was rewritten


def probe_workflow(wt: Path, mutated: bool) -> bool:
    """The replay harness must fail when the workflow's `if:` stops fitting.

    Mutation: drop `always()`, the line whose absence silently switches the
    closures check off on main -- a failure mode this repository has had.
    """
    if mutated:
        p = wt / WORKFLOW
        src = p.read_text()
        assert src.count("      always() && (\n") == 1
        p.write_text(src.replace("      always() && (\n", "      (\n"))
    r = run([sys.executable, "tools/audit/round3/closures-gate/replay.py"], wt)
    return r.returncode != 0                 # True == the harness noticed


def main() -> int:
    head = run(["git", "rev-parse", "HEAD"], ROOT).stdout.strip()
    print(f"HEAD {head}")
    with tempfile.TemporaryDirectory(prefix="hpo-mut-") as td:
        wt = Path(td) / "wt"
        run(["git", "worktree", "add", "--detach", str(wt), head], ROOT)
        try:
            base_fail = entities_failures(wt)
            if base_fail:
                print(f"the unmutated tree already fails: {sorted(base_fail)}")
                return 1
            print("baseline: tests/entities.py green, 0 failures\n")

            applied = killed = 0
            for label, rel, find, repl, expect in EDITS:
                p = wt / rel
                src = p.read_text()
                bent = apply_edit(src, find, repl, region=(rel == CLOSURE))
                if bent is None:
                    print(f"UNAPPLIED (the pattern does not bite once): {label}")
                    applied += 1
                    continue
                p.write_text(bent)
                fails = entities_failures(wt)
                p.write_text(src)
                applied += 1
                hit = expect in fails or "<the run died>" in fails
                killed += hit
                print(f"{'KILLED' if hit else 'SURVIVED':9s} {label}")
                print(f"          expected FAIL: {expect}")
                print(f"          got: {sorted(fails) or 'nothing failed'}")

            # The unmutated tree must NOT rewrite the table; the mutated one must.
            for label, probe in (("--single --record-only merges anyway",
                                  probe_record_only),
                                 ("always() is dropped from the closures if:",
                                  probe_workflow)):
                clean = probe(wt, mutated=False)
                run(["git", "checkout", "--", "."], wt)
                dirty = probe(wt, mutated=True)
                run(["git", "checkout", "--", "."], wt)
                applied += 1
                hit = dirty and not clean
                killed += hit
                print(f"{'KILLED' if hit else 'SURVIVED':9s} {label}")
                print(f"          unmutated={clean} mutated={dirty} "
                      f"(the probe must fire only when mutated)")
        finally:
            run(["git", "worktree", "remove", "--force", str(wt)], ROOT)

    print()
    print(f"RESULT applied={applied}")
    print(f"RESULT killed={killed}")
    return 0 if killed == applied else 1


if __name__ == "__main__":
    raise SystemExit(main())
