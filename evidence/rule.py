"""Null control on the ref24 raise and per-class margins.
For each class (in-window CI tests/replay draws, body window = 800 ci.yml runs to 2026-11-05 end):
  forced window for cpu budget B: max(clean) < B <= 2*min(clean)  (cost_offenders: over, and 'cannot see 2x')
  body rule: B = sqrt(2) * sqrt(min*max) of the class's clean readings
Also the committed-table rule for ref24 (COST_CLASS_READINGS rows with ref_ms in the ref24 band)."""
import csv, math, os, sys
from collections import defaultdict
sys.path.insert(0, os.path.expanduser("~/wt/tests")); os.chdir(os.path.expanduser("~/wt"))
import replay
S = "synthetic-dhw-only.json"
CI = os.path.expanduser("~/ci")
runs = [l.rstrip("\n").split("\t") for l in open(f"{CI}/runs.tsv")][:1200]
win = {r[0] for r in sorted([r for r in runs if r[3] < "2026-11-06"], key=lambda r: r[3], reverse=True)[:800]}
d = defaultdict(list)
for r in csv.DictReader(open(f"{CI}/draws.tsv"), delimiter="\t"):
    if r["fixture"] == S and r["arm"] == "clean" and r["run"] in win and r["jobname"] == "tests / replay":
        d[replay.runner_class(S, float(r["ref_ms"])) or "fallback"].append(float(r["cpu_ratio"]))
fb = replay.fallback_budget(S)["cpu_ratio"]
for c, v in sorted(d.items()):
    B = replay.COST_CLASS_BUDGETS[S][c]["cpu_ratio"] if c != "fallback" else fb
    lo, hi = min(v), max(v)
    rule = math.sqrt(2) * math.sqrt(lo * hi)
    print(f"{c:8s} n={len(v):2d} clean {lo:.4g}-{hi:.4g}  forced window ({hi:.4g}, {2*lo:.4g}]  "
          f"rule {rule:.4g}  committed {B:.4g}  max/budget {hi/B:.1%}  budget/max x{B/hi:.3f}"
          + ("" if hi < B <= 2 * lo else "  <-- committed budget OUTSIDE the forced window"))
tab = [v for (x, k, v, _) in replay.COST_CLASS_READINGS[S] if k == "cpu_ratio" and replay.runner_class(S, x) == "ref24"]
print(f"ref24 committed table: {len(tab)} readings {min(tab)}-{max(tab)} rule {math.sqrt(2)*math.sqrt(min(tab)*max(tab)):.4g}; "
      f"old budget 3.630 holds max {max(tab)}: {max(tab) < 3.630}; 2*min {2*min(tab):.4g} >= 3.630: {2*min(tab) >= 3.630}")
