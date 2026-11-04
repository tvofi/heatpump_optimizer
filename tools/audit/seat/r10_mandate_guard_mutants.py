#!/usr/bin/env python3
"""R10-FLY-MANDATE-REVOKE-GUARD: every plant the two self-tests must refuse.

Metric, one line per plant: `RESULT mutant=<name> rc=<rc> fails=<n>`, then the
failing check names. Each plant is one exact one-occurrence replacement in
tools/pr/gh_comment.py or tools/policy/budget_raise_gate.py; the driver applies
it, runs both files' self-tests, and restores the file byte for byte (on an
exception or SIGTERM too). It refuses to start when either file differs from
HEAD, so a restore cannot overwrite work. Expected: every plant rc=1 with
fails>=1 -- a FAIL line, not a crash (a crash is rc=1 with fails=0 and prints
its tail).

Plants, one per predicate of the guard (triage P336) and the dS value check:
  G1  gh_comment.py copies the id test without the gate's `(?<!\\d)` (the
      mutant P336 names), so an id inside a longer number is refused.
  G2  a patch is never judged as a #201 comment (the patch path unguarded).
  G3  --withdraw-mandate lets the body through whatever id it names.
  G4  run() never calls the guard (the wiring).
  B1  the gate's revokes() drops `(?<!\\d)`: both files' rows must see it.
  B2  a well-formed section is never compared with the measured figure.
  B3  the scorer runs from the head, which a pull request can edit.
  B4  the dS is compared and the verdict word is not.

    python3 tools/audit/seat/r10_mandate_guard_mutants.py [plant ...]
    python3 tools/audit/seat/r10_mandate_guard_mutants.py --null
    python3 tools/audit/seat/r10_mandate_guard_mutants.py --self-test

Null control: `--null` runs both self-tests with no plant, which must print
rc=0 fails=0. `--self-test` does not run the plants: it pins that every
anchor occurs exactly once in its target and that each planted text compiles.
"""
import signal
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
GHC = "tools/pr/gh_comment.py"
GATE = "tools/policy/budget_raise_gate.py"
SELF_TESTS = ((GHC, "self-test"), (GATE, "--self-test"))

PLANTS = {
    "G1": (GHC, 'if g.revocable(c, now) and g.revokes(body, c.get("id"))}',
           'if g.revocable(c, now) and g.MANDATE_REVOKED.search(body)'
           ' and re.search(rf"{c.get(\'id\')}(?!\\d)", body)}'),
    "G2": (GHC, 'on = str(fetch(repo, comment).get("issue_url") or "").endswith(g.MANDATE_ISSUE_URL)',
           "on = False"),
    "G3": (GHC, "} - {withdraw})", "}) if withdraw is None else []"),
    "G4": (GHC, "        mandate_guard(a.repo, body,", "        (lambda *_a, **_k: None)(a.repo, body,"),
    "B1": (GATE, 'rf"(?<!\\d){cid}(?!\\d)"', 'rf"{cid}(?!\\d)"'),
    "B2": (GATE, "        return score_check(body, score_fn())", "        return ok, why"),
    "B3": (GATE, '_git("worktree", "add", "-q", "--detach", wt, base)',
           '_git("worktree", "add", "-q", "--detach", wt, head)'),
    "B4": (GATE, "    if want in got:", "    if want[0] in [a for a, _ in got]:"),
}


def run_self_tests():
    rc, fails, tail = 0, [], []
    for target, flag in SELF_TESTS:
        r = subprocess.run([sys.executable, target, flag], cwd=ROOT, capture_output=True, text=True)
        rc |= r.returncode != 0
        fails += [f"{target}: {ln.strip()}" for ln in r.stdout.splitlines() if ln.strip().startswith("FAIL ")]
        tail += (r.stdout + r.stderr).strip().splitlines()[-3:]
    return int(rc), fails, tail


def report(name, rc, fails, tail):
    print(f"RESULT mutant={name} rc={rc} fails={len(fails)}")
    for f in fails:
        print(f"    {f}")
    if rc and not fails:
        print("    crash tail:")
        for ln in tail:
            print(f"      {ln}")


def clean(target):
    return subprocess.run(["git", "diff", "--quiet", "HEAD", "--", target], cwd=ROOT).returncode == 0


def plant(name):
    target, old, new = PLANTS[name]
    path = ROOT / target
    text = path.read_text()
    if text.count(old) != 1:
        print(f"RESULT mutant={name} rc=2 fails=0 (anchor occurs {text.count(old)} times)")
        return False
    try:
        path.write_text(text.replace(old, new))
        rc, fails, tail = run_self_tests()
    finally:
        path.write_text(text)
    report(name, rc, fails, tail)
    return rc == 1 and bool(fails)


def self_test():
    failed = 0
    for name, (target, old, new) in PLANTS.items():
        text = (ROOT / target).read_text()
        ok = text.count(old) == 1
        try:
            compile(text.replace(old, new), target, "exec")
        except SyntaxError:
            ok = False
        failed += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {name}: its anchor occurs exactly once and the plant compiles")
    print(f"r10_mandate_guard_mutants self-test: {len(PLANTS)} checks, {failed} failed")
    return 1 if failed else 0


def main(argv):
    if argv == ["--self-test"]:
        return self_test()
    if argv == ["--null"]:
        rc, fails, tail = run_self_tests()
        report("null", rc, fails, tail)
        return 1 if rc or fails else 0
    names = argv or list(PLANTS)
    unknown = [n for n in names if n not in PLANTS]
    if unknown:
        print(f"unknown plant(s): {' '.join(unknown)}", file=sys.stderr)
        return 2
    dirty = [t for t in (GHC, GATE) if not clean(t)]
    if dirty:
        print(f"refused: {', '.join(dirty)} differs from HEAD; commit it first", file=sys.stderr)
        return 2
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))  # the finally above restores
    killed = [plant(n) for n in names]
    print(f"RESULT plants={len(names)} killed={sum(killed)}")
    return 0 if all(killed) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
