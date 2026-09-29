#!/usr/bin/env python3
"""Calibration accuracy of three gate variants on the same cases and frozen weights (reported, not chosen by fit).

G-strict  no score metric may rise (the prototype's definition)
G-class   only the metrics that guard a register class may rise-refuse; floor metrics enter the score only
G-none    no gate: the verdict is the sign of delta-S alone
"""
import sys
sys.argv = [sys.argv[0]]
import arch_score as A

CLASS = [m for m, (c, _) in A.SCORE_METRICS.items() if c]
for name in ("G-strict", "G-class", "G-none"):
    tally = {}
    for c in A.cases():
        d = A.delta(c["base"], c["cur"])
        rises = [r.split()[0] for r in d["rises"]]
        adm = {"G-strict": not rises, "G-class": not any(r in CLASS for r in rises), "G-none": True}[name]
        v = "IMPROVES" if adm and d["dS"] > 0 else "NULL" if adm and d["dS"] == 0 else "WORSENS"
        k = (c["set"], c["label"])
        ok = A.expected_ok(c["label"], v)
        t = tally.setdefault(k, [0, 0, 0])
        t[0] += ok
        t[1] += 1
        t[2] += (not ok) and v != "NULL"
    print(name, "  ".join(f"{s}/{l} {t[0]}/{t[1]} (wrong-way {t[2]})" for (s, l), t in sorted(tally.items())))
