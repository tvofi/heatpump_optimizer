#!/usr/bin/env python3
"""D3-s1 enumerator: the step universe for D3.M1-M5 over the seat's cells.

Metric: every candidate site tests/mutation_table.py's ratcheted inventory
generates in the 12 cell files, with its disposition (unpinned / killed_by /
triaged), one line per site: `<file>:<line>\t<kind>\t<anchor>\t<disposition>`.
The universe of M1/M2/M3/M4 is the UNPINNED lines (`--unpinned`); M5's is the
closure scripts reaching the cell files (`--scripts`).

Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/enumerate.py [--unpinned|--all|--scripts|--summary]
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, machine: owner macOS (arm64).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
from collections import Counter
sys.path.insert(0, "tests")
import mutation_table as mt  # noqa: E402

CELLS = ["coordinator", "optimizer", "thermal_model", "sysid", "defrost",
         "flow_lift", "process_worker", "batchmath", "price_model", "tariff",
         "grid_fee", "dhw_planner"]
FILES = [mt.PRODUCTION / f"{c}.py" for c in CELLS]
RELS = {mt.PKG + c + ".py" for c in CELLS}


def sites():
    budgets = mt.load_budgets()
    inv = mt.inventory(sorted(FILES))
    loose = {id(s) for s in mt.unpinned_sites(budgets, inv)}
    disp = mt.dispositions(budgets)
    out = []
    for s in inv:
        if id(s) in loose:
            d = "unpinned"
        else:
            e = disp.get(s["anchor"], {})
            if "killed_by" in e:
                d = "killed_by:" + str(e.get("killed_by"))
            else:
                d = "triage:" + str(e.get("verdict"))
        out.append((s, d))
    return out


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--unpinned"
    if mode == "--scripts":
        clos = mt.load_closures()
        for s, files in sorted(clos.items()):
            hit = sorted(f.rsplit("/", 1)[-1] for f in files if f in RELS)
            if hit:
                print(f"{s}\t{','.join(hit)}")
        return
    rows = sites()
    if mode == "--summary":
        c = Counter((s["file"].rsplit("/", 1)[-1], d.split(":")[0])
                    for s, d in rows)
        for k in sorted(c):
            print(k[0], k[1], c[k])
        print("RESULT sites_total=%d" % len(rows))
        print("RESULT sites_unpinned=%d"
              % sum(1 for _, d in rows if d.startswith("unpinned")))
        return
    for s, d in rows:
        if mode == "--unpinned" and not d.startswith("unpinned"):
            continue
        print(f"{s['file']}:{s['line']}\t{s['kind']}\t{s['anchor']}\t{d}")


if __name__ == "__main__":
    main()
