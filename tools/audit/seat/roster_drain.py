#!/usr/bin/env python3
"""The manual roster-queue drain path: pending queue lines through roster_queue.py.

    roster_drain.py --queue FILE --work-dir DIR --edit-checkout DIR --worktree DIR --lint-clone DIR
                    [--branch handoff/audit-r10-roster] [--alive FILE] [--timeout 3600]
    roster_drain.py --self-test

Owner ruling (tvofi 2026-10-31): mechanical seat work goes into the sweep script. This is
the path for a session with no standing roster seat; the beat's `roster-drain` row
(`beat_jobs.py`) is the unattended one, and the two do not run together on one queue.
Drains the pending lines of QUEUE through `tools/audit/seat/roster_queue.py run`, marks
each line `#done` or `#refused` by exact-line match, and prints one line per problem for
the sweep runner to forward: ROSTER-REFUSED, ROSTER-SKIPPED, ROSTER-CASCADE, ROSTER-UNRUN.
Never releases a `#held` line (any line starting `#` is not pending). Run from a
checkout of the repository.
"""
import argparse, os, subprocess, sys


def pending(lines):
    """Pending = non-blank, not a comment. A line holding ' #' is skipped with a notice:
    roster_queue.parse_line would cut it at the comment."""
    pend = [l for l in lines if l.strip() and not l.startswith("#")]
    notes = [f"ROSTER-SKIPPED: ' #' in the line, parse_line would cut it; rewrite it: {l[:120]}" for l in pend if " #" in l]
    return [l for l in pend if " #" not in l], notes


def reconcile(pend, new, cur):
    """Fold the report lines `new` (one per pending op, in order) into the queue lines `cur`.
    Returns (new queue lines, output lines)."""
    cur = list(cur)
    out, cascade = [], 0
    for op, res in zip(pend, new):
        if op not in cur:
            continue
        i = cur.index(op)
        if " pushed " in res:
            cur[i:i + 1] = ["#done " + op, "#note " + res.split(" | ")[0].replace("roster: ", "") + " (sweep runner)"]
        elif "is on no origin ref" in res:
            cascade += 1  # an earlier refusal left the worktree detached: not this op's refusal; stays pending
        else:
            cur[i:i + 1] = ["#refused " + op, "#note " + res]
            out.append("ROSTER-REFUSED: " + op[:120] + " :: " + res[-200:])
    if cascade:
        out.append(f"ROSTER-CASCADE: {cascade} line(s) left pending behind an earlier refusal's detached worktree")
    for op in pend[len(new):]:
        out.append("ROSTER-UNRUN: " + op[:120] + " (no report line; the run stopped early)")
    return cur, out


def drain(a):
    lines = open(a.queue).read().split("\n")
    pend, notes = pending(lines)
    for n in notes:
        print(n)
    if not pend:
        return 0

    def sh(*cmd, **k):
        return subprocess.run(cmd, text=True, capture_output=True, **k)

    sh("git", "-C", a.edit_checkout, "fetch", "-q", "origin")
    sh("git", "-C", a.edit_checkout, "checkout", "-q", "-B", "roster-drain-main", "origin/main")
    sh("git", "-C", a.edit_checkout, "worktree", "remove", "--force", a.worktree)
    sh("git", "-C", a.edit_checkout, "worktree", "prune")
    qcopy, rep = os.path.join(a.work_dir, "roster-q.txt"), os.path.join(a.work_dir, "roster-rep.txt")
    open(qcopy, "w").write("\n".join(pend) + "\n")
    before = len(open(rep).read().splitlines()) if os.path.exists(rep) else 0
    cmd = ["python3", "-I", "tools/audit/seat/roster_queue.py", "run", "1", str(len(pend)), "--queue", qcopy,
           "--report", rep, "--edit-checkout", a.edit_checkout, "--worktree", a.worktree,
           "--lint-clone", a.lint_clone, "--branch", a.branch]
    if a.alive:
        cmd += ["--alive", a.alive]
    sh(*cmd, cwd=a.edit_checkout, timeout=a.timeout)
    new = open(rep).read().splitlines()[before:] if os.path.exists(rep) else []
    cur, out = reconcile(pend, new, open(a.queue).read().split("\n"))
    open(a.queue, "w").write("\n".join(cur))
    for o in out:
        print(o)
    return 0


def self_test():
    n = bad = 0

    def check(name, cond):
        nonlocal n, bad
        n += 1
        if not cond:
            bad += 1
            print(f"FAIL {name}")

    q = ["set-stage A done", "# comment", "#held set-stage H x", "", "set-stage B done", "set-stage C done # tail"]
    pend, notes = pending(q)
    check("held and comment lines are not pending", pend == ["set-stage A done", "set-stage B done"])
    check("a ' #' line is skipped with a notice", len(notes) == 1 and notes[0].startswith("ROSTER-SKIPPED"))
    cur, out = reconcile(pend, ["roster: A pushed abc | x", "roster: B refused: lint"], q)
    check("pushed -> #done + note", "#done set-stage A done" in cur and any(l.startswith("#note A pushed abc") for l in cur))
    check("refused -> #refused + ROSTER-REFUSED", "#refused set-stage B done" in cur and len(out) == 1 and out[0].startswith("ROSTER-REFUSED"))
    check("the held line is untouched", "#held set-stage H x" in cur)
    cur, out = reconcile(pend, ["roster: A refused: boom", "roster: B is on no origin ref"], q)
    check("cascade: later op stays pending, one ROSTER-CASCADE", "set-stage B done" in cur and any(o.startswith("ROSTER-CASCADE: 1") for o in out))
    cur, out = reconcile(pend, ["roster: A pushed abc | x"], q)
    check("unrun op is reported, stays pending", "set-stage B done" in cur and any(o.startswith("ROSTER-UNRUN: set-stage B") for o in out))
    cur, out = reconcile(pend, ["roster: A pushed abc | x", "roster: B pushed def | y"], q)
    check("null control: all pushed -> no problem line", out == [])
    cur, out = reconcile(pend, ["roster: A pushed abc | x"], [l for l in q if l != "set-stage A done"])
    check("an op removed from the queue meanwhile is not re-added", "#done set-stage A done" not in cur)
    print(f"roster_drain self-test: {n} checks, {bad} failed")
    return 1 if bad else 0


def main(argv):
    ap = argparse.ArgumentParser()
    for f in ("queue", "work-dir", "edit-checkout", "worktree", "lint-clone", "alive"):
        ap.add_argument("--" + f)
    ap.add_argument("--branch", default="handoff/audit-r10-roster")
    ap.add_argument("--timeout", type=int, default=3600)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    for f in ("queue", "work_dir", "edit_checkout", "worktree", "lint_clone"):
        if not getattr(a, f):
            ap.error("--" + f.replace("_", "-") + " is required")
    return drain(a)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
