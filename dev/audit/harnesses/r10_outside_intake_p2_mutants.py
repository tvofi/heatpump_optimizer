#!/usr/bin/env python3
"""R10-OUTSIDE-INTAKE part 2: each behaviour the landing's self-tests pin dies alone.

The roster carry's MUTANTS OWED AT LANDING: roster_lib.discharged (each
conjunct), replan's discharged arm in dependency_graph, flow_merge_wait (the
verdict-before-merge comparison and the at-head test), train_batches (the done
flag and the skip attribution to the current batch), plan_page's discharged
label and done set, the beat row's memory and UNREADABLE arms, and
roster_edit mark-carry's closing arm.

Each mutant is one exact one-occurrence replacement in one file. The driver
applies it, runs that file's own `--self-test` and the extra self-tests the
row names, restores the file byte for byte (mutant_guard), and refuses to start
on a file with uncommitted edits. One line per mutant:

  RESULT mutant=<name> rc=<rc> fails=<n> verdict=killed|SURVIVED|CRASHED

then the FAIL lines. A mutant that kills only by crashing (no FAIL line) is
CRASHED, not killed. Null control: M0, nothing replaced, every self-test run,
must print rc=0 fails=0; a replacement whose text is not found exactly once
aborts.

    python3 dev/audit/harnesses/r10_outside_intake_p2_mutants.py [NAME ...]
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from r10_plan_page_mutants import fail_name, repo_root  # noqa: E402 -- the FAIL-line grammar and root walk
import mutant_guard  # noqa: E402 -- restores the mutated file on a kill and refuses a leftover mutant

ROOT = repo_root(__file__)
LIB = "tools/audit/seat/roster_lib.py"
PLAN = "tools/plan/replan.py"
MT = "tools/audit/merge_throughput.py"
PAGE = "tools/audit/seat/plan_page.py"
BEAT = "tools/audit/seat/beat_jobs.py"
EDIT = "tools/audit/seat/roster_edit.py"
BOTTLE = "tools/audit/seat/bottleneck_check.py"
#: The self-test argv per file; beat_jobs' own mutants are its own self-test's.
SELF = {LIB: ["--self-test"], PLAN: ["--self-test"], MT: ["--self-test"], PAGE: ["--self-test"],
        BEAT: ["--self-test", "--no-mutants"], EDIT: ["--self-test"], BOTTLE: ["--self-test"]}

#: (name, file, old, new, extra self-tests run besides the file's own)
MUTANTS = [
    ("M0", None, None, None, ()),
    # The memory key reduced to the kind alone: the behaviour case "two metrics
    # tripped together each print their own line" is among its FAIL lines, apart
    # from the in-file anchor guard that also fires on any edit of `state_of`.
    ("state-of-kind-only", BOTTLE,
     'distinct states."""\n    return " ".join(line.split()[:2])',
     'distinct states."""\n    return line.split()[0]', ()),
    ("discharged-any-stage", LIB, 'return (resume.get("stage") == "carries-open"',
     'return (resume.get("stage") in ("carries-open", "in-progress", "not-started")', ()),
    ("discharged-no-commit", LIB,
     '            and isinstance(resume.get("commit"), str)\n'
     '            and bool(SHA_RE.match(resume["commit"]))\n',
     "            and True\n", ()),
    ("discharged-any-commit", LIB, 'and bool(SHA_RE.match(resume["commit"]))',
     'and bool(resume["commit"])', ()),
    ("discharged-carries-ignored", LIB, "            and not pending_carries(group, legacy))",
     "            and True)", ()),
    ("discharged-legacy-ignored", LIB, "and not pending_carries(group, legacy))",
     "and not pending_carries(group, {}))", ()),
    ("replan-discharged-arm", PLAN, "if is_done(g) or roster_lib.discharged(g, legacy or {})}",
     "if is_done(g)}", ()),
    ("replan-legacy-dropped", PLAN, "roster_lib.discharged(g, legacy or {})",
     "roster_lib.discharged(g, {})", ()),
    ("wait-after-merge-verdict", MT, 'if v[1] <= move["t"]]', "]", ()),
    ("wait-at-head", MT, '"at_head": last[4] == move["head"]', '"at_head": True', ()),
    ("train-done-flag", MT, '            out[-1]["done"] = True\n', "            pass\n", ()),
    ("train-skip-first-batch", MT, 'out[-1]["skips"].append(', 'out[0]["skips"].append(', ()),
    ("page-discharged-label", PAGE, 'label += ", every carry discharged" + (', 'label += "" + (', ()),
    # The merge with #3326 moved the discharged edge release from `done` into
    # build_rows' blocked list; `done`'s own `| discharged` feeds only the
    # row's wave/start/finish, which replan already nulls for a discharged group.
    ("page-discharged-edge", PAGE,
     "if a in G and a not in discharged and roster_lib.gates(G[a])]",
     "if a in G and roster_lib.gates(G[a])]", ()),
    ("page-merged-set", PAGE,
     "merged = {g for g in done if _stage(G[g]) in roster_lib.DONE_STAGES} | discharged",
     "merged = {g for g in done if _stage(G[g]) in roster_lib.DONE_STAGES}", ()),
    ("beat-memory-dropped", BEAT,
     '                          "--memory", str(ctx.digest / "state" / "bottleneck.json"))',
     "                          )", ()),
    ("beat-rc-clean", BEAT, '    if rc != 0:\n        return write_job(ctx, "bottleneck"',
     '    if False:\n        return write_job(ctx, "bottleneck"', ()),
    ("beat-unreadable-dropped", BEAT, 'ln.startswith(("BOTTLENECK: ", "BOTTLENECK-UNREADABLE: "))',
     'ln.startswith(("BOTTLENECK: ",))', ()),
    ("beat-missing-key-runs", BEAT, 'got = ctx.need("bottleneck", "train_log", "plan_slots")',
     'got = [str(ctx.overlay.get("train_log")), str(ctx.overlay.get("plan_slots"))]', ()),
    ("mark-close-off", EDIT,
     'closed = a.op == "mark-carry" and close_discharged(roster, a.group, legacy)',
     "closed = False", ()),
    ("mark-close-any-stage", EDIT,
     'if resume.get("stage") != HOLD_STAGE or roster_lib.pending_carries(g, legacy or {}):',
     "if roster_lib.pending_carries(g, legacy or {}):", ()),
    ("mark-close-no-hold", EDIT,
     "        closed = a.op == \"mark-carry\" and close_discharged(roster, a.group, legacy)\n"
     "        if closed or a.op == \"set-stage\"",
     "        closed = a.op == \"mark-carry\" and close_discharged(roster, a.group, legacy)\n"
     "        if a.op == \"set-stage\"", ()),
    ("mark-legacy-dropped", EDIT, 'if a.op in ("set-stage", "set-resume", "mark-carry"):',
     'if a.op in ("set-stage", "set-resume"):', ()),
]


def failures(out: str) -> list[str]:
    """Every self-test's FAIL lines, at any indent: each self-test run here prints its own."""
    return [ln.strip() for ln in out.splitlines() if ln.strip().startswith("FAIL")]


def main(argv: list[str]) -> int:
    want = set(argv)
    mutant_guard.arm(sorted(SELF))
    survived = 0
    for name, rel, old, new, extra in MUTANTS:
        if want and name not in want:
            continue
        path = ROOT / rel if rel else None
        orig = path.read_bytes() if path else b""
        try:
            if old is not None:
                text = orig.decode()
                if text.count(old) != 1:
                    print(f"abort: {name}: {old!r} occurs {text.count(old)} times in {rel}")
                    return 2
                path.write_text(text.replace(old, new), encoding="utf-8")
            files = sorted(SELF) if rel is None else [rel, *extra]
            runs = [subprocess.run([sys.executable, "-I", str(ROOT / f), *SELF[f]], cwd=ROOT,
                                   capture_output=True, text=True) for f in files]
        finally:
            if path:
                path.write_bytes(orig)
        fails = [ln for r in runs for ln in failures(r.stdout)]
        rc = max(r.returncode for r in runs)
        if name == "M0":
            verdict = "null" if rc == 0 and not fails else "SURVIVED"
        elif fails and rc:
            verdict = "killed"
        elif rc:
            verdict = "CRASHED"
        else:
            verdict = "SURVIVED"
        survived += verdict in ("SURVIVED", "CRASHED")
        print(f"RESULT mutant={name} rc={rc} fails={len(fails)} verdict={verdict}", flush=True)
        for ln in fails[:6]:
            print("   ", fail_name(ln))
    print(f"RESULT survived={survived}")
    return 1 if survived else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
