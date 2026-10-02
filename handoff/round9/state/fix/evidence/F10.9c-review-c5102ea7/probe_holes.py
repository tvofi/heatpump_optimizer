"""Reviewer's own probe (F10.9c review): feed decide() the real tables at the
checked-out head and find merges it calls ELIGIBLE that the scoped gate would
have graded differently on the merged tree."""
import json, sys, subprocess, pathlib, re
ROOT = pathlib.Path.cwd()
sys.path.insert(0, str(ROOT / "tools/audit")); sys.path.insert(0, str(ROOT / "tests"))
import merge_fastpath as m, closure
t = json.loads((ROOT / "tests/closures.json").read_text())
tables = {"main": t, "head": t}
wf = [p.read_text() for p in sorted((ROOT / ".github/workflows").glob("*.yml"))]
g = m.grader_specs(wf)
cl = t["closures"]
tracked = subprocess.run(["git","ls-files"],capture_output=True,text=True).stdout.split()
# --- A: env_drift belt
env = set(cl["tests/env_drift.py"])
known = {f for fs in cl.values() for f in fs}
integ = [f for f in tracked if f.startswith("custom_components/") and not closure._is_frontend_asset(f)
         and closure.unit_of(f) in known]
outside = [f for f in integ if closure.unit_of(f) not in env]
print("A: integration files measured but outside env_drift's closure:", len(outside), outside[:5])
found = None
for M in outside:
    for P in integ:
        if P == M: continue
        if not m.decide([P], [M], tables, g, None):
            plan = closure.select([P])
            found = (P, M, "tests/env_drift.py" in plan["run"]); break
    if found: break
print("A: eligible pair (PR file, main file, env_drift selected for PR):", found)
# --- B: run_always harness_headers and INERT docs
for d in ["DISCLAIMER.md", "docs/backlog.md", "docs/audit-2026-09.md"]:
    print("B:", d, "inert:", closure.is_inert(d), "in hh closure:", d in cl["tests/harness_headers.py"])
for pr in (["docs/setup.md"], ["DISCLAIMER.md"]):
    for mn in (["DISCLAIMER.md"], ["docs/audit-2026-09.md"], ["docs/setup.md"]):
        if pr == mn: continue
        print("B: pr", pr, "main", mn, "->", m.decide(pr, mn, tables, g, None) or "ELIGIBLE")
claims = (ROOT / "tools/audit/round4/D6/claims.py")
if claims.exists():
    s = claims.read_text()
    print("B: claims.py names:", sorted(set(re.findall(r"DISCLAIMER\.md|docs/backlog\.md|docs/audit-2026-09\.md", s))))
