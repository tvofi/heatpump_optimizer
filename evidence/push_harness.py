"""Reviewer's push-half harness for #1848: real inventory, real ledger, real git."""
import json, subprocess, sys, tempfile, os
from pathlib import Path
sys.path.insert(0, "tests")
import mutation_table as m
def sh(*a): return subprocess.run(a, capture_output=True, text=True)
head = sh("git", "rev-parse", "HEAD").stdout.strip()
b = m.load_budgets(); s = m.inventory(); u = m.unpinned_sites(b, s); c = m.load_closures()
al = [x for x in m.DEFAULT_SCRIPTS.split(",") if x]
d = [x for x in u if m.drivers_for(x["file"], c, al)]
print("RESULT stock", len(s), len(u), len(d), len({x["anchor"] for x in u}))
pool = m.drain_pool(u, c, al, 20261002, 40)
print("RESULT slice20261002", len(pool), "anchors", len({x["anchor"] for x in pool}),
      "whole", all(sum(1 for y in pool if y["anchor"]==a)==sum(1 for y in u if y["anchor"]==a) for a in {x["anchor"] for x in pool}))
pool2 = m.drain_pool(u, c, al, 20261003, 40)
print("RESULT slice-overlap-next-night", len({x["anchor"] for x in pool} & {x["anchor"] for x in pool2}))
# Fake a measurement: every anchor in the slice "killed" by its first driver.
anchors = {}
for x in pool: anchors.setdefault(x["anchor"], x)
entries = {a: {"killed_by": x["drivers"][0], "old": x["old"], "reason": "reviewer synthetic"} for a, x in anchors.items()}
out = Path(tempfile.mkdtemp(prefix="rv1848-"))
print("RESULT write_drain", m.write_drain(out, entries, head, []))
print("RESULT apply1", m.apply_drained(str(out), head, []))
st = sh("git", "status", "--porcelain", "--untracked-files=all").stdout
lines = [l for l in st.splitlines() if l.strip()]
print("RESULT porcelain-lines", len(lines), "problems", m.drain_write_set_problems(st))
print("RESULT apply2", m.apply_drained(str(out), head, []))
st2 = sh("git", "status", "--porcelain", "--untracked-files=all").stdout
print("RESULT porcelain-after-apply2-equal", st == st2)
sh("git", "clean", "-fdq", "tests/mutation_ledger"); sh("git", "checkout", "-q", "--", ".")
# Moved head: pretend the measurement was at the merge base; changed = real diff.
mb = sh("git", "merge-base", "origin/main", "HEAD").stdout.strip()
old = sh("git", "rev-list", "-n1", "--before=2026-09-25", "origin/main").stdout.strip()
for at in (mb, old):
    (out / "head").write_text(at + "\n")
    changed = sh("git", "diff", "--name-only", at, head).stdout.split()
    drop = m.stale_pins(entries, changed, m.load_closures())
    r = m.apply_drained(str(out), head, changed)
    n = len([l for l in sh("git", "status", "--porcelain", "--untracked-files=all").stdout.splitlines() if l.strip()])
    print("RESULT moved-from", at[:9], "changed", len(changed), "dropped", len(drop), "of", len(entries), "status", r, "rows", n)
    sh("git", "clean", "-fdq", "tests/mutation_ledger"); sh("git", "checkout", "-q", "--", ".")
# Null control for the drop: a diff touching only README.md drops nothing.
(out / "head").write_text("0"*40 + "\n")
print("RESULT null-README dropped", len(m.stale_pins(entries, ["README.md"], m.load_closures())))
# Unreadable diff: changed None => nothing applied.
print("RESULT unreadable", m.apply_drained(str(out), head, None))
