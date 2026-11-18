#!/usr/bin/env python3
"""D3-s1 M5(b): the kill-overlap matrix -- every closure script on every sampled mutant, no early stop.

Metric (one line): over the mutants of state/matrix_mutants.json (the C2 and
C3/C6 samples, c2_mutants.json + c3c6_mutants.json, and every SURVIVED result
of state/results/{pre,c2,c3c6}), each driven by prescreen.py `run --full --sub
matrix` with D3S1_RELAX=0 and D3S1_ALL_DRIVERS=1 (every closure script of the
mutated file that mutation_table can drive, no early stop, only the gate's own
reach_skip), the per (script, mutant) outcome KILLED (mutation_table:killed) /
SURVIVED / TIMEOUT / SKIPPED (reach_skip: the traced baseline never executes
the line) / ABSENT (not in the file's closure); then per script: kills, unique
kills (mutants no other script kills), and duplicate kills (kills of mutants
>= 2 scripts kill). Count key: the run verdicts in results/matrix/*.json.

Instrumented symbols: tests/mutation_table.py:killed and run_script on each
mutated production line (the mutant's anchor) through prescreen.py:drive.
Perturbation: `--drop-script S` removes S's column -> every mutant only S
killed becomes unkilled (killed_mutants falls by S's unique kills, direction
down) and the unique kills of the scripts that shared S's kills rise; the
identity run is the null.

Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/m5_matrix.py build   # writes state/matrix_mutants.json
     D3S1_RELAX=0 D3S1_ALL_DRIVERS=1 D3S1_FRESH_TREE=1 PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/prescreen.py run --full --mutants dev/audit/rounds/round11/D3/s1/state/matrix_mutants.json --sub matrix --workers 4
     PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/m5_matrix.py table [--drop-script S] [--tsv]
Expected: exact counts (contention-immune); walls provisional.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
Machine: box D3-m5, Linux x86_64, nproc 4, Intel Xeon @ 2.30GHz.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, "tests")
import mutation_table as mt  # noqa: E402

HERE = Path(__file__).resolve().parent
RES = HERE / "state" / "results"
MUT = HERE / "state" / "matrix_mutants.json"


def key(m: dict) -> str:
    return hashlib.sha1((m["anchor"] + "|" + m["new"]).encode()).hexdigest()[:16]


def build() -> int:
    out, seen, src = [], set(), Counter()
    for name in ("c2_mutants.json", "c3c6_mutants.json"):
        for m in json.loads((HERE / name).read_text()):
            if key(m) not in seen:
                seen.add(key(m))
                out.append(m)
                src[name] += 1
    for sub in ("pre", "c2", "c3c6"):
        for p in sorted((RES / sub).glob("*.json")):
            r = json.loads(p.read_text())
            if r["verdict"] == "SURVIVED" and key(r["mutant"]) not in seen:
                seen.add(key(r["mutant"]))
                out.append(r["mutant"])
                src["survived:" + sub] += 1
    MUT.write_text(json.dumps(out, indent=1))
    for k, n in sorted(src.items()):
        print(f"  {k}: {n}")
    print(f"RESULT matrix_mutants={len(out)}")
    return 0


def table(drop: str | None, tsv: bool) -> int:
    muts = json.loads(MUT.read_text())
    clos = mt.load_closures()
    rows = {}
    for m in muts:
        p = RES / "matrix" / (key(m) + ".json")
        rows[key(m)] = (m, json.loads(p.read_text()) if p.exists() else None)
    scripts = sorted({s for _, r in rows.values() if r for s in
                      list(r["runs"]) + r["skipped"]} - {drop})
    killers: dict[str, set[str]] = {}
    cells = Counter()
    driven = 0
    for k, (m, r) in rows.items():
        if r is None:
            continue
        driven += 1
        ks = set()
        for s in scripts:
            if m["file"] not in clos.get(s, ()):
                v = "ABSENT"
            elif s in r["skipped"]:
                v = "SKIPPED"
            elif s in r["runs"]:
                x = r["runs"][s]
                v = "KILLED" if x["killed"] else ("TIMEOUT" if x["timed_out"] else "SURVIVED")
            else:
                v = "NOT-RUN"
            cells[v] += 1
            if v == "KILLED":
                ks.add(s)
            if tsv:
                print(f"{m['anchor']}\tL{m['line']}\t{k}\t{s}\t{v}")
        killers[k] = ks
    kills = Counter(s for ks in killers.values() for s in ks)
    uniq = Counter(next(iter(ks)) for ks in killers.values() if len(ks) == 1)
    dup = Counter(s for ks in killers.values() if len(ks) >= 2 for s in ks)
    killed = sum(1 for ks in killers.values() if ks)
    print("script\tkills\tunique_kills\tduplicate_kills")
    for s in scripts:
        print(f"{s}\t{kills[s]}\t{uniq[s]}\t{dup[s]}")
    redundant = [s for s in scripts if kills[s] and not uniq[s]]
    silent = [s for s in scripts if not kills[s]]
    print(f"RESULT matrix_mutants={len(muts)}")
    print(f"RESULT matrix_driven={driven}")
    print(f"RESULT killed_mutants={killed}")
    print(f"RESULT killed_by_two_or_more={sum(1 for ks in killers.values() if len(ks) >= 2)}")
    print(f"RESULT killed_by_exactly_one={sum(1 for ks in killers.values() if len(ks) == 1)}")
    for v, n in sorted(cells.items()):
        print(f"RESULT pairs_{v.lower().replace('-', '_')}={n}")
    print(f"RESULT scripts_with_kills_but_no_unique_kill={len(redundant)} {','.join(redundant)}")
    print(f"RESULT scripts_killing_nothing={len(silent)} {','.join(silent)}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT thread_factor=1.00")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("build", "table"))
    ap.add_argument("--drop-script")
    ap.add_argument("--tsv", action="store_true")
    a = ap.parse_args()
    return build() if a.cmd == "build" else table(a.drop_script, a.tsv)


if __name__ == "__main__":
    sys.exit(main())
