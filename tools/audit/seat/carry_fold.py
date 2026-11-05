#!/usr/bin/env python3
"""carry_fold.py -- the orchestrator writes each `Carry: <GROUP>` body item into its destination brief.

    python3 tools/audit/seat/carry_fold.py --body FILE --pr '#N' --topic T --worktree DIR
        [--checkout DIR] [--roster-ref REF] [--branch BR]
    python3 tools/audit/seat/carry_fold.py --self-test

WHY. A seat that cannot write the roster strands its carry: `body_push.sh` refuses a body whose
`Carry: <GROUP>` item is missing from that group's brief, prints the `roster_edit.py append-carry`
op it needs, and stops (#2612's row). The orchestrator writes the roster, so it runs this step
before merging: it takes the items `carry_audit.py landed` reports missing, appends each with
`roster_edit.py append-carry --push` (its one write path), re-reads the roster branch it wrote, and
ASSERTS AFTER THE FOLD that every item id is now in its group's brief or carries. An op that exited
0 and left the item out is the failure this step exists to catch: rc 1 names each id still absent.

Refusals (rc 1, nothing written for the first): a body item whose destination is no valid group
(`bad destination`); an item still missing after the fold. rc 0: nothing missing, or all folded and
asserted. rc 3: the roster is unreadable. The merge-time writer is `roster_sync.py`; this runs
before it and `roster_edit.py` refuses an exact repeat, so the two never double-write.
`--self-test` prints `carry_fold self-test: N checks, 0 failed`.
"""
from __future__ import annotations

import argparse
import shlex
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import carry_audit  # noqa: E402
import roster_lib  # noqa: E402


def fold(body: str, load, apply, pr: str = "", topic: str = "") -> tuple[int, list[str]]:
    """(rc, lines). `load()` reads the destination roster as a `Dests` now; `apply(op)` runs one
    `append-carry` op line and returns its rc."""
    source = f"{pr} {topic}".strip()
    missing = carry_audit.landed(body, load(), source)
    bad = [m for m in missing if m["why"].startswith("bad destination")]
    if bad:
        return 1, [f"carry_fold: REFUSED item {m['id']} -> {m['group']}: {m['why']}; nothing written" for m in bad]
    lines = []
    for op in carry_audit.land_ops(missing, pr, topic):
        rc = apply(op)
        lines.append(f"carry_fold: rc={rc} {op.split(' ', 2)[0]} {op.split(' ', 2)[1]}")
        if rc:
            return 1, lines + [f"carry_fold: REFUSED: the write of {op.split(' ', 2)[1]} failed (rc {rc})"]
    after = carry_audit.landed(body, load(), source)  # mut:postfold
    if after:
        return 1, lines + [f"carry_fold: POST-FOLD item {m['id']} is not in {m['group']}'s brief or carries: {m['why']}"
                           for m in after]
    return 0, lines + [f"carry_fold: {len(missing)} item(s) folded; every id asserted in its destination after the write"]


def main(argv=None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if argv == ["--self-test"]:
        return _self_test()
    import roster_edit  # late: it imports carry_audit
    p = argparse.ArgumentParser(prog="carry_fold.py")
    p.add_argument("--body", required=True)
    p.add_argument("--pr", default="")
    p.add_argument("--topic", default="")
    p.add_argument("--worktree", required=True)
    p.add_argument("--checkout", default=".")
    p.add_argument("--roster-ref", default=None)
    p.add_argument("--branch", default=None)
    a = p.parse_args(argv)
    git = roster_lib.git_in(a.checkout)
    branch = a.branch or a.roster_ref or roster_lib.round_ref(git)
    if not branch:
        print("carry_fold: no roster branch (give --branch)")
        return 3
    branch = branch.removeprefix("origin/")

    def load():
        git(["fetch", "--quiet", "origin", f"+refs/heads/{branch}:refs/remotes/origin/{branch}"])
        return carry_audit.load_dests(Path(a.checkout), f"origin/{branch}")

    def apply(op: str) -> int:
        parts = shlex.split(op)
        return roster_edit.main(parts + ["--worktree", a.worktree, "--checkout", a.checkout,
                                         "--branch", branch, "--push"])

    try:
        rc, lines = fold(Path(a.body).read_text(), load, apply, a.pr, a.topic)
    except (roster_lib.RosterNotFound, ValueError, OSError) as e:
        print(f"carry_fold: UNREAD the roster: {e}")
        return 3
    print("\n".join(lines))
    return rc


def _self_test() -> int:
    passed = failed = 0

    def check(name, ok):
        nonlocal passed, failed
        if ok:
            passed += 1
        else:
            failed += 1
            print(f"FAIL {name}")

    def gr(name, stage, carry=()):
        return {"group": name, "after": [], "resume": {"stage": stage}, "brief": "", "carry": list(carry)}

    body = ("## Summary\n\nx\n\n## Forward-carry\n\n- the lost ask. Carry: R10-DEST\n")
    state = {"R10-DEST": gr("R10-DEST", "not-started"), "R10-GONE": gr("R10-GONE", "done")}

    def load():
        return carry_audit.Dests({"groups": list(state.values())}, set(), None)

    calls = []

    def writes(op):
        calls.append(op)
        group = op.split(" ", 2)[1]
        state[group]["carry"].append(op.split(" ", 2)[2])
        return 0

    def forgets(op):  # rc 0 and nothing written: a seat's op that did not land
        calls.append(op)
        return 0

    rc, out = fold(body, load, writes, "#9", "r10-x")
    check("a missing item is written once and asserted after the fold", rc == 0 and len(calls) == 1)
    calls.clear()
    rc, out = fold(body, load, writes, "#9", "r10-x")
    check("null control: the same body again writes nothing (the id is in the brief now)", rc == 0 and calls == [])
    state["R10-DEST"]["carry"].clear()
    calls.clear()
    rc, out = fold(body, load, forgets, "#9", "r10-x")
    check("an op that returned 0 but wrote nothing fails after the fold, naming the id",
          rc == 1 and any("POST-FOLD" in x and "R10-DEST" in x for x in out) and len(calls) == 1)
    calls.clear()
    rc, out = fold(body.replace("R10-DEST", "R10-GONE"), load, writes, "#9", "r10-x")
    check("a done destination is refused before any write", rc == 1 and calls == [] and "bad destination" in out[0])
    rc, out = fold(body, load, lambda op: 2, "#9", "r10-x")
    check("a failed write refuses and says so", rc == 1 and "REFUSED" in out[-1])
    print(f"carry_fold self-test: {passed + failed} checks, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
