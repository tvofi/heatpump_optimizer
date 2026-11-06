"""Reproduce the body's window: the 800 most recent ci.yml runs as listed on
2026-11-05 (cutoff = end of that day), their tests / replay jobs that ran.
Print per-class clean synthetic draws, and every ref53 draw ever."""
import csv, os, sys
from collections import defaultdict
CI = os.path.expanduser("~/ci")
sys.path.insert(0, os.path.expanduser("~/wt/tests")); os.chdir(os.path.expanduser("~/wt"))
import replay
runs = [l.rstrip("\n").split("\t") for l in open(f"{CI}/runs.tsv")]
ci_runs = [r for r in runs if r[1] != "schedule" and not r[0] in ()]
# nightly runs are those with event schedule or workflow_dispatch on branch main titled Nightly;
# runs.tsv mixes both workflows: the first 1200 lines are ci.yml (pages 1-12), the rest nightly.
ci_runs = runs[:1200]
nightly = runs[1200:]
cut = "2026-11-06T00:00:00Z"
win = sorted([r for r in ci_runs if r[3] < cut], key=lambda r: r[3], reverse=True)[:800]
winids = {r[0] for r in win}
print(f"window: {len(win)} ci.yml runs, {win[-1][3]} .. {win[0][3]}")
draws = [r for r in csv.DictReader(open(f"{CI}/draws.tsv"), delimiter="\t")
         if r["fixture"] == "synthetic-dhw-only.json" and r["arm"] == "clean"]
def cls(x):
    return replay.runner_class("synthetic-dhw-only.json", x) or "none"
def table(rows, label):
    d = defaultdict(list)
    for r in rows:
        d[cls(float(r["ref_ms"]))].append(r)
    print(f"{label}: {len(rows)} jobs")
    for c, lst in sorted(d.items()):
        cpu = [float(r["cpu_ratio"]) for r in lst]; refs = [float(r["ref_ms"]) for r in lst]
        loop = [float(r["loop_cpu_ratio"]) for r in lst]
        print(f"  {c:5s} n={len(lst):2d} ref {min(refs):.2f}-{max(refs):.2f} cpu {min(cpu):.4g}-{max(cpu):.4g} loop {min(loop):.4g}-{max(loop):.4g}")
inwin = [r for r in draws if r["run"] in winids and r["jobname"] == "tests / replay"]
table(inwin, "BODY WINDOW tests / replay jobs that ran")
table([r for r in draws if r["run"] in winids and r["jobname"] == "tests / replay" and r["created"] >= "2026-11-03"], "  of which created >= 2026-11-03")
table([r for r in draws if r["jobname"] == "slow"], "NIGHTLY slow jobs (all)")
table(draws, "ALL draws")
print("every ref53-band draw:")
for r in sorted(draws, key=lambda r: r["created"]):
    if cls(float(r["ref_ms"])) == "ref53":
        print(f"  {r['job']} {r['jobname']} {r['created']} {r['conclusion']} ref {float(r['ref_ms']):.2f} cpu {r['cpu_ratio']} loop {r['loop_cpu_ratio']}")
print("cpu_ratio by date (median per day, all classes):")
by = defaultdict(list)
for r in draws: by[(r["created"][:10], cls(float(r["ref_ms"])))].append(float(r["cpu_ratio"]))
for k in sorted(by):
    v = sorted(by[k]); print(f"  {k[0]} {k[1]:5s} n={len(v):2d} cpu {v[0]:.3f}-{v[-1]:.3f}")
