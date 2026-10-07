#!/usr/bin/env python3
"""F10.3 mutation proof for the new pins: each mutant edits one production
line of the gate scripts in a scratch worktree, runs tests/entities.py there,
and prints the checks that fail beyond the unmutated run's. M0 is the null
control (a comment line). Run from a detached worktree at the head.
"""
import re, subprocess, sys
from pathlib import Path
ROOT = Path.cwd()
PY = sys.executable
M = [
    ("M0 null", "tests/mutation_table.py", "def _scope_tail(", "# null control\ndef _scope_tail("),
    ("M1 refusal ignores added", "tests/mutation_table.py",
     "    if ((ratchet_refusal(base_count, unpinned) == 1 or added)",
     "    if ((ratchet_refusal(base_count, unpinned) == 1)"),
    ("M2 no move match", "tests/mutation_table.py",
     "        if s[\"file\"] in added and gone.get(k, 0):",
     "        if False:"),
    ("M3 no twin preference", "tests/mutation_table.py",
     "        group.pop(same[-1] if same else -1)", "        group.pop(-1)"),
    ("M4 per-site identity off", "tests/mutation_table.py",
     "        if not group:\n            out.append(s)\n            continue",
     "        if not group or True:\n            continue"),
    ("M5 GUARD_OFF back to bare if", "tests/mutation_table.py",
     "                and node.test.lineno == ln and kw in (\"if\", \"elif\")):",
     "                and node.test.lineno == ln and kw in (\"if\",) and not node.orelse):"),
    ("M6 numpy clamps out", "tests/mutation_table.py",
     "            and (func.value.id, func.attr) in _CLAMP_ATTRS)",
     "            and False)"),
    ("M7 drift leaf comparison deleted", "tests/env_drift.py",
     "        _diff_leaves(baseline[name], branch[name], name, diffs)\n",
     "        pass\n"),
    ("M8 stress budget comparison off", "tests/stress.py",
     "    if ratio > allowed:\n", "    if False:\n"),
    ("M9 strace union dropped", "tests/closure.py",
     "    rec[\"files\"] = sorted(set(rec[\"files\"]) | seen)",
     "    rec[\"files\"] = sorted(set(rec[\"files\"]))"),
    ("M10 strace keeps INERT reads", "tests/closure.py",
     "            if r and _is_real_file(r) and not is_inert(r):",
     "            if r and _is_real_file(r):"),
    ("M11 strace counts every child", "tests/closure.py",
     "        if pid not in py:\n            continue\n",
     "        if False:\n            continue\n"),
]
FAIL = re.compile(r"^  FAIL (.+?)  \[", re.M)

def run() -> set[str]:
    out = subprocess.run([PY, "tests/entities.py"], cwd=ROOT, capture_output=True, text=True,
                         env={**__import__("os").environ, "PYTHONPATH": "tests/hastub"}).stdout
    return {f for f in FAIL.findall(out) if not re.match(r"a\d+:", f)}

if "--only" in sys.argv:
    _ids = sys.argv[sys.argv.index("--only") + 1].split(",")
    M = [m for m in M if m[0].split()[0] in _ids]
base = run()
print(f"baseline: {len(base)} failing check(s)")
for name, rel, old, new in M:
    p = ROOT / rel
    src = p.read_text()
    assert src.count(old) == 1, (name, src.count(old))
    p.write_text(src.replace(old, new))
    try:
        got = sorted(run() - base)
    finally:
        p.write_text(src)
    print(f"{name}: {'KILLED' if got else 'survived'} by {len(got)} check(s)")
    for g in got:
        print(f"    FAIL {g}")
