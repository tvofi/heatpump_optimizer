"""Null control for the sample's kill signal: the unmutated run of N seeded killed drives' plans.

    cd <base tree>; SPIKE=... TREES=... PYTHONPATH=tests/hastub:tests python3 baselines.py LINES.json SAMPLE.jsonl [--n 4] [--seed 11]

A kill counted a FAIL or an uncaught exception inside the driven part's spans; the same plan
unmutated must print none there, or the kill is the plan's, not the mutant's.
"""
import json, os, random, sys, threading
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sample_drive as sd

a = sys.argv[1:]
n = int(a[a.index("--n") + 1]) if "--n" in a else 4
seed = int(a[a.index("--seed") + 1]) if "--seed" in a else 11
rows = {r["anchor"]: r for r in sd.rows_with_reach(a[0])}
sample = [json.loads(l) for l in open(a[1])]
killed = [(s["anchor"], d["part"]) for s in sample for d in s["drives"] if d["killed"]]
pick = random.Random(seed).sample(killed, min(n, len(killed)))
trees = []
for w in range(len(pick)):
    t = Path(os.environ["TREES"]) / f"w{w}"
    for src in (sd.ROOT / "custom_components").rglob("*.py"):
        (t / src.relative_to(sd.ROOT)).write_bytes(src.read_bytes())
    trees.append(t)
out = [None] * len(pick)

def go(i):
    anchor, part = pick[i]
    plan = next(p for _, x, p in rows[anchor]["drives"] if x == part)
    fails, other, first, cpu, scoped = sd.run_plan(trees[i], plan, part, failfast=False)
    out[i] = {"anchor": anchor, "part": part, "spans": len(plan), "in_part_fails": fails,
              "other_part_fails": other, "first": first, "completed": scoped, "cpu_s": round(cpu, 1)}

th = [threading.Thread(target=go, args=(i,)) for i in range(len(pick))]
[t.start() for t in th]; [t.join() for t in th]
for o in out:
    print(json.dumps(o))
print("in-part fails over", len(out), "baselines:", sum(o["in_part_fails"] for o in out))
