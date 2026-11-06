"""Body-figure re-derivation over the reproduced window (800 ci.yml runs to 2026-11-05 end,
tests / replay jobs with a synthetic clean line): offenders at head and main, owner range."""
import csv, os, subprocess, sys
CI = os.path.expanduser("~/ci")
runs = [l.rstrip("\n").split("\t") for l in open(f"{CI}/runs.tsv")][:1200]
win = {r[0] for r in sorted([r for r in runs if r[3] < "2026-11-06"], key=lambda r: r[3], reverse=True)[:800]}
rows = [r for r in csv.DictReader(open(f"{CI}/draws.tsv"), delimiter="\t")
        if r["run"] in win and r["jobname"] == "tests / replay" and r["arm"] == "clean"]
own = [float(r["cpu_ratio"]) for r in rows if r["fixture"].startswith("owner")]
print(f"owner fixture clean cpu_ratio in window: n={len(own)} {min(own):.1f}-{max(own):.1f} (budget 337.8, floor 168.9)")
syn = [r for r in rows if r["fixture"] == "synthetic-dhw-only.json"]
code = r'''
import sys, os, json
os.chdir(sys.argv[1]); sys.path.insert(0, "tests"); import replay
S = "synthetic-dhw-only.json"
for ln in sys.stdin:
    j, ref, cpu, kib, loop = ln.split()
    b, refused = replay.class_budget(S, float(ref))
    off = refused or replay.cost_offenders({"cpu_ratio": float(cpu), "peak_kib": float(kib), "loop_cpu_ratio": float(loop)}, b)
    if off: print(f"  {j} ref_ms {float(ref):.2f}: {off[0][:110]}")
'''
inp = "".join(f"{r['job']} {r['ref_ms']} {r['cpu_ratio']} {r['peak_kib']} {r['loop_cpu_ratio']}\n" for r in syn)
for t in ("wt", "wmain"):
    out = subprocess.run([sys.executable, "-c", code, os.path.expanduser(f"~/{t}")], input=inp, capture_output=True, text=True).stdout
    n = out.count("\n")
    print(f"{t}: {n} of {len(syn)} in-window synthetic clean draws offend cycle_cost")
    print(out, end="")
