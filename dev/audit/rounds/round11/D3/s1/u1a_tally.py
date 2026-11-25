#!/usr/bin/env python3
"""D3-s1 box D3-u1a: the slice's D3.M2 pre-screen and D3.M3 full-net tally.

Metric (one line): over the keys in state/keys-D3-u1a.txt, the count of
fast-net verdicts (results/pre/) by status and first-killing driver, and over
the slice's fast-net survivors (state/keys-D3-u1a-surv.txt) the full-net
verdicts (results/complete/) by status and by every killing driver.

Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/u1a_tally.py [--tsv]
Expected: pre_driven=309 (exact; counts, no timing claims).
Instrumented symbol: tests/mutation_table.py:killed over each mutant's
production line, as prescreen.py recorded it.
Perturbation: --drop-driver S counts S's kills as absent -> killed falls and
survived rises by the mutants S alone killed (up); the identity run is the null.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-u1a,
Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse
import json
from collections import Counter
from pathlib import Path

STATE = Path(__file__).resolve().parent / "state"


def keys(name):
    return [k.strip() for k in (STATE / name).read_text().split() if k.strip()]


def verdict(r, drop):
    by = [d for d in r["killed_by"] if d != drop]
    if by:
        return "KILLED", by
    if any(x.get("timed_out") for x in r["runs"].values()):
        return "TIMEOUT", by
    if not r["runs"]:
        return "SKIPPED_BY_REACH", by
    return "SURVIVED", by


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tsv", action="store_true")
    ap.add_argument("--drop-driver")
    a = ap.parse_args()
    for sub, ks in (("pre", keys("keys-D3-u1a.txt")), ("complete", keys("keys-D3-u1a-surv.txt"))):
        st, first, every, missing = Counter(), Counter(), Counter(), 0
        for k in ks:
            p = STATE / "results" / sub / (k + ".json")
            if not p.exists():
                missing += 1
                continue
            try:
                r = json.loads(p.read_text())
            except ValueError:
                st["UNPARSEABLE"] += 1
                continue
            v, by = verdict(r, a.drop_driver)
            st[v] += 1
            if by:
                first[by[0]] += 1
                every.update(by)
            if a.tsv:
                m = r["mutant"]
                print(f"{sub}\t{k}\t{m['file']}:{m['line']}\t{m['kind']}\t{v}\t{','.join(by) or '-'}")
        print(f"RESULT {sub}_keys={len(ks)}")
        print(f"RESULT {sub}_driven={sum(st.values())}")
        print(f"RESULT {sub}_not_driven={missing}")
        for v in ("KILLED", "SURVIVED", "TIMEOUT", "SKIPPED_BY_REACH", "UNPARSEABLE"):
            print(f"RESULT {sub}_{v.lower()}={st[v]}")
        for d, n in first.most_common():
            print(f"RESULT {sub}_first_kill[{d}]={n}")
        for d, n in every.most_common():
            print(f"RESULT {sub}_every_kill[{d}]={n}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT thread_factor=1.00")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
