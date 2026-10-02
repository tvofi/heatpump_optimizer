"""Mutation proof for the mandate refusal arms: each mutant disables one
predicate, the self-test must go red on the arm's own checks, then restore."""
import shutil
import subprocess
import sys

F = ".claude/workflows/budget_raise_gate.py"
ORIG = "/tmp/claude-0/ev/gate.orig.py"
MUT = {
    "M1 expired": ('    if end is not None and at >= end:\n',
                   '    if False and end is not None and at >= end:\n'),
    "M2 revoked": ('        if r and int(r.group(1)) == cid and _is_owner(c.get("user")):\n',
                   '        if False and r and int(r.group(1)) == cid and _is_owner(c.get("user")):\n'),
    "M3 not-tvofi author": ('    if not _is_owner(comment.get("user")):\n',
                            '    if False and not _is_owner(comment.get("user")):\n'),
    "M4 scope": ('    if scope not in MANDATE_COVERS_RAISE:\n',
                 '    if False and scope not in MANDATE_COVERS_RAISE:\n'),
    "M5 non-head": ('    if last.get("commit_id") != head:\n',
                    '    if False and last.get("commit_id") != head:\n'),
}
src = open(ORIG).read()
for name, (a, b) in MUT.items():
    assert src.count(a) == 1, name
    open(F, "w").write(src.replace(a, b))
    out = subprocess.run([sys.executable, F, "--self-test"], capture_output=True, text=True).stdout
    print(f"{name}: {out.strip().splitlines()[-1]}")
    for line in out.splitlines():
        if line.strip().startswith("FAIL"):
            print("   ", line.strip())
shutil.copy(ORIG, F)
out = subprocess.run([sys.executable, F, "--self-test"], capture_output=True, text=True).stdout
print("M0 restored:", out.strip().splitlines()[-1])
