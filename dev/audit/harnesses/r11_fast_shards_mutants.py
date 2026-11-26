"""The fast shards' mutation proof (R11-CI-CASE-SELECT P2, #3885).

    python3 dev/audit/harnesses/r11_fast_shards_mutants.py WORKTREE

WORKTREE is a checkout of the head under test, never one a suite is running in: each mutant
deletes or inverts one production predicate in place, runs the self-test that closes over it,
prints KILLED with the failing check names (or SURVIVED), and restores the file. The BASELINE
lines are the same self-tests on the unmutated tree, the null control.
EXPECTED RESULT: every mutant KILLED; every BASELINE rc=0.
"""
import subprocess
import sys
from pathlib import Path

W = Path(sys.argv[1])
MUTANTS = [
    ("gate: the fast name is not expanded into shards", "tools/ci/gate.py",
     '.extend(fast if (u, n) == ("tests", FAST) else [n])', '.append(n)',
     ["python3", "-I", "tools/ci/gate.py", "--self-test"]),
    ("gate: a malformed shard list is not refused", "tools/ci/gate.py",
     '    if why_fast:\n        return False, [why_fast]\n', '',
     ["python3", "-I", "tools/ci/gate.py", "--self-test"]),
    ("shards.check: an empty shard is accepted", "tools/ci/shards.py",
     '    return set(s.values()) == set(range(1, n + 1))', '    return True',
     ["python3", "-I", "tools/ci/shards.py", "--self-test"]),
    ("shards.route: a shard of another count is accepted", "tools/ci/shards.py",
     'if p["n"] != n or not 1 <= k <= n:', 'if not 1 <= k <= n:',
     ["python3", "-I", "tools/ci/shards.py", "--self-test"]),
    ("shards.timings: a failed run's seconds are kept", "tools/ci/shards.py",
     'rec.get("rc", 0) != 0 or ', '',
     ["python3", "-I", "tools/ci/shards.py", "--self-test"]),
    ("shards.priced: an untimed script is dropped", "tools/ci/shards.py",
     'return {s: known.get(s, default) for s in scripts}', 'return {s: known[s] for s in scripts if s in known}',
     ["python3", "-I", "tools/ci/shards.py", "--self-test"]),
    ("closure.PRODUCERS: the setup render loses its writer", "tests/closure.py",
     '    "tests/setup_qa_render.mjs": ["tests/plan_view.py"],\n', '',
     ["python3", "-I", "tools/ci/shards.py", "--self-test"]),
    ("prelude: the planner's outputs are not emitted", "tools/ci/prelude.py",
     '        out.update(fast(', '        (fast(',
     ["python3", "-I", "tools/ci/prelude.py", "--self-test"]),
]
for name, rel, old, new, cmd in MUTANTS:
    p = W / rel
    orig = p.read_text()
    assert orig.count(old) == 1, (name, orig.count(old))
    p.write_text(orig.replace(old, new))
    try:
        r = subprocess.run(cmd, cwd=W, capture_output=True, text=True, timeout=600)
        out = r.stdout + r.stderr
        fails = [ln.strip() for ln in out.splitlines() if ln.strip().startswith(("FAIL", "Traceback"))]
        verdict = "KILLED" if r.returncode != 0 and fails else "SURVIVED"
        print(f"{verdict} [{name}] rc={r.returncode}")
        for f in fails[:4]:
            print(f"    {f[:170]}")
    finally:
        p.write_text(orig)
# baseline: every closure green with no mutant applied
for cmd in (["python3", "-I", "tools/ci/gate.py", "--self-test"], ["python3", "-I", "tools/ci/shards.py", "--self-test"],
            ["python3", "-I", "tools/ci/prelude.py", "--self-test"]):
    r = subprocess.run(cmd, cwd=W, capture_output=True, text=True, timeout=600)
    print(f"BASELINE rc={r.returncode} {(r.stdout.strip().splitlines() or [''])[-1]}")
