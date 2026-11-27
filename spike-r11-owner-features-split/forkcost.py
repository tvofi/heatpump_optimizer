"""Spike: the fork drive's cost model from recorded span seconds, and the sample's measured shares.

    PYTHONPATH=tests/hastub:tests SPIKE=<swap_run dir> python3 forkcost.py LINES.json PARTS.json SCRIPT [SAMPLE.jsonl]

Ceiling per function-body row: recorded seconds of every span from its first reaching span to the
end of the script (no fail-fast). Module-level row: header + every span. With SAMPLE (forkdrive.py
output), the measured mean CPU-s per driven row by kind, extrapolated over the population.
"""
import json
import os
import sys
from collections import Counter

sys.path[:0] = ["tests", os.environ["SPIKE"], os.path.dirname(os.path.abspath(__file__))]
import case_select as cs  # noqa: E402
import forkdrive  # noqa: E402

lines_path, parts_path, script = sys.argv[1:4]
parts = json.load(open(parts_path))
rows, spans = forkdrive.rows_for(lines_path, parts, script)
e = cs.entry(cs.load(), "tests/features.py")
sec = [e["spans"].get(s.id, {}).get("seconds", 0.0) for s in spans]
suffix = [0.0] * (len(sec) + 1)
for i in range(len(sec) - 1, -1, -1):
    suffix[i] = suffix[i + 1] + sec[i]
head = float(os.environ.get("HEAD_S", "6.9"))
kind = Counter()
ceil = Counter()
for r in rows:
    k = "none" if r["first"] is None else ("module" if r["module_level"] else "function")
    kind[k] += 1
    if k == "function":
        ceil[k] += suffix[r["first"]]
    elif k == "module":
        ceil[k] += head + suffix[0]
print(f"rows {len(rows)} by kind {dict(kind)}; script span seconds {suffix[0]:.0f}, header {head}")
print("ceiling CPU-s (no fail-fast):", {k: round(v) for k, v in ceil.items()}, "total", round(sum(ceil.values())))
if len(sys.argv) > 4:
    res = [json.loads(l) for l in open(sys.argv[4])]
    by = {r["anchor"]: r for r in rows}
    agg = {}
    nulls = [x for x in res if x.get("null")]
    for x in res:
        if x.get("null") or "cpu_s" not in x:
            continue
        r = by[x["anchor"]]
        k = "module" if r["module_level"] else "function"
        a = agg.setdefault(k, {"n": 0, "cpu": 0.0, "killed": 0, "refused": 0, "in_reach": 0, "ceil": 0.0})
        a["n"] += 1
        a["cpu"] += x["cpu_s"]
        a["killed"] += x.get("verdict") == "killed"
        a["refused"] += x.get("verdict") == "refused"
        a["in_reach"] += x.get("verdict") == "killed" and x.get("part") in r["reach_parts"]
        a["ceil"] += (head + suffix[0]) if k == "module" else suffix[r["first"]]
    tot = 0.0
    for k, a in agg.items():
        mean = a["cpu"] / max(1, a["n"])
        ext = mean * kind[k]
        tot += ext
        print(f"{k}: driven {a['n']}, killed {a['killed']}, killed in a reaching part {a['in_reach']}, refused {a['refused']}, "
              f"CPU-s mean {mean:.1f} (sum {a['cpu']:.0f}; their no-fail-fast ceiling {a['ceil']:.0f}) x {kind[k]} rows = {ext:.0f}")
    print(f"extrapolated children CPU-s {tot:.0f}")
    print("nulls:", [(x["fork_span"], x.get("verdict"), x["cpu_s"]) for x in nulls])
