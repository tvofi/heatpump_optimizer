#!/usr/bin/env python3
"""D3-s1 tabulation of the pre-screen state: the M2/M3/M5 tables the report carries.

Metric (one line): per driven mutant, its verdict over the fast net
(prescreen.py `pre`/`c2`/`c3c6`) and, where completed, over the full net
(`complete`); per driver, how many mutants it killed (first kill and, for
no-early-stop drives, every kill: the kill-overlap matrix).

Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/tabulate.py [--tsv]
Reads only dev/audit/rounds/round11/D3/s1/state/; exact counts, no timing claims.
Instrumented symbol: the verdicts of prescreen.py's drive of
tests/mutation_table.py:killed over each mutant's production line.
Perturbation: the positive-control sub (`posctl`, ledger-pinned sites) must
read KILLED and the null control (`null.json`) LIVES.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: owner macOS arm64.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RES = HERE / "state" / "results"


def load(sub):
    d = RES / sub
    return {p.stem: json.loads(p.read_text()) for p in sorted(d.glob("*.json"))} if d.exists() else {}


def main() -> int:
    tsv = "--tsv" in sys.argv
    subs = {s: load(s) for s in ("pre", "c2", "c3c6", "posctl", "complete")}
    comp = subs["complete"]
    for sub in ("pre", "c2", "c3c6", "posctl"):
        rs = subs[sub]
        c = Counter(r["verdict"] for r in rs.values())
        print(f"RESULT {sub}_driven={len(rs)}")
        for v in ("KILLED", "SURVIVED", "TIMEOUT"):
            print(f"RESULT {sub}_{v.lower()}={c.get(v, 0)}")
        kinds = Counter((r["mutant"]["kind"], r["verdict"]) for r in rs.values())
        for (k, v), n in sorted(kinds.items()):
            print(f"  {sub} {k} {v} {n}")
    c = Counter(r["verdict"] for r in comp.values())
    print(f"RESULT complete_driven={len(comp)}")
    for v in ("KILLED", "SURVIVED", "TIMEOUT"):
        print(f"RESULT complete_{v.lower()}={c.get(v, 0)}")
    first = Counter()
    every = defaultdict(set)
    for sub in ("pre", "c2", "c3c6"):
        for k, r in subs[sub].items():
            if r["killed_by"]:
                first[r["killed_by"][0]] += 1
    for k, r in comp.items():
        for s in r["killed_by"]:
            every[s].add(k)
    for s, n in first.most_common():
        print(f"  first-kill {s} {n}")
    for s, ks in sorted(every.items()):
        print(f"  complete-kill {s} {len(ks)}")
    if tsv:
        for sub in ("pre", "c2", "c3c6", "posctl"):
            for k, r in subs[sub].items():
                m = r["mutant"]
                cv = comp.get(k, {}).get("verdict", "-")
                cb = ",".join(comp.get(k, {}).get("killed_by", [])) or "-"
                print("\t".join([sub, k, f"{m['file'].rsplit('/', 1)[-1]}:{m['line']}",
                                 m["kind"], r["verdict"],
                                 ",".join(r["killed_by"]) or "-", cv, cb,
                                 m["old"].strip()[:80], m["new"].strip()[:80]]))
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT thread_factor=1.00")
    return 0


if __name__ == "__main__":
    sys.exit(main())
