"""Grade every CI synthetic draw with a tree's own class_budget + cost_offenders.

usage: python3 analyse.py <tree>   (tree = worktree root whose tests/replay.py is graded)
Prints per-draw verdicts for the clean reading and planted 1.5x / 2x of each
metric, a per-class summary (max clean, budget, margin), and loop figures.
"""
import csv, math, os, sys
from collections import defaultdict

tree = sys.argv[1]
os.chdir(tree)
sys.path.insert(0, os.path.join(tree, "tests"))
import replay  # noqa: E402

SYN = "synthetic-dhw-only.json"
rows = [r for r in csv.DictReader(open(os.path.expanduser("~/ci/draws.tsv")), delimiter="\t")
        if r["fixture"] == SYN]
clean = [r for r in rows if r["arm"] == "clean"]
print(f"TREE {tree}: {len(clean)} clean synthetic draws from {len({r['job'] for r in clean})} jobs")


def grade(ref_ms, figs):
    budget, refused = replay.class_budget(SYN, ref_ms)
    if refused:
        return "REFUSED-no-budget", budget
    off = replay.cost_offenders(figs, budget)
    return ("RED " + "; ".join(off)) if off else "pass", budget


rc_cls = getattr(replay, "runner_class", None)
by_class = defaultdict(list)
fails = 0
plant_surv = defaultdict(list)
for r in sorted(clean, key=lambda r: float(r["ref_ms"])):
    ref = float(r["ref_ms"])
    figs = {"cpu_ratio": float(r["cpu_ratio"]), "peak_kib": float(r["peak_kib"]),
            "loop_cpu_ratio": float(r["loop_cpu_ratio"])}
    cls = rc_cls(SYN, ref) if rc_cls else next(
        (c for c, (lo, hi) in replay.COST_RUNNER_CLASSES.items() if lo <= ref <= hi), None)
    cls = cls or "FALLBACK"
    v, budget = grade(ref, figs)
    fails += v != "pass"
    by_class[cls].append((ref, figs, budget))
    plants = {}
    for k in figs:
        for s in (1.5, 2.0):
            pv, _ = grade(ref, {**figs, k: figs[k] * s})
            plants[f"{k}x{s}"] = "RED" if pv != "pass" else "PASS"
            if pv == "pass":
                plant_surv[f"{k}x{s}"].append((cls, ref))
    print(f"  {r['job']} {r['event'][:4]} {r['created'][:10]} ref_ms {ref:6.2f} loop_ref {float(r['loop_ref_ms']):6.2f} "
          f"{cls:8s} cpu {figs['cpu_ratio']:.4g} loop {figs['loop_cpu_ratio']:.4g} kib {figs['peak_kib']:.0f}"
          f" -> {v[:90]} | " + " ".join(f"{k}:{v2}" for k, v2 in plants.items()))
print(f"CLEAN NOT PASSING: {fails} of {len(clean)}")
print("PER CLASS (clean): n, ref_ms range, cpu max/budget/margin, loop max/budget/margin")
for c, lst in sorted(by_class.items()):
    b = lst[0][2] or {}
    cpu = [f["cpu_ratio"] for _, f, _ in lst]
    loop = [f["loop_cpu_ratio"] for _, f, _ in lst]
    refs = [x for x, _, _ in lst]
    def m(vals, k):
        return f"{min(vals):.4g}-{max(vals):.4g} / {b.get(k, float('nan')):.4g} / x{b.get(k, float('nan')) / max(vals):.3f}" if b else "no budget"
    print(f"  {c:8s} n={len(lst):3d} ref {min(refs):.2f}-{max(refs):.2f}  cpu {m(cpu, 'cpu_ratio')}  loop {m(loop, 'loop_cpu_ratio')}")
print("PLANTS SURVIVING (metric x scale: count, classes):")
for k in sorted({f"{k}x{s}" for k in ("cpu_ratio", "peak_kib", "loop_cpu_ratio") for s in (1.5, 2.0)}):
    lst = plant_surv.get(k, [])
    print(f"  {k}: {len(lst)} survive " + str(sorted({c for c, _ in lst})))
# arms as measured in CI: each doubled arm graded at its own ref_ms
arms = [r for r in rows if r["arm"] != "clean"]
key = {"cpu": "cpu_ratio", "memory": "peak_kib", "loop": "loop_cpu_ratio"}
miss = []
for r in arms:
    ref = float(r["ref_ms"])
    k = key[r["arm"]]
    budget, refused = replay.class_budget(SYN, ref)
    if refused:
        miss.append((r["job"], r["arm"], ref, "refused"))
        continue
    if not float(r[k]) > budget[k]:
        miss.append((r["job"], r["arm"], ref, f"{k} {r[k]} <= {budget[k]}"))
print(f"MEASURED CI ARMS: {len(arms)}; not over budget: {len(miss)} {miss[:10]}")
