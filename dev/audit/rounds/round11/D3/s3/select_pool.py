#!/usr/bin/env python3
"""D3.M1 consequence-weighted pre-screen pool for the local relaunch, seat D3-s3.

Metric (one line): per unpinned site of enumerate.py's universe, its M1 weight
(enumerate.weight) and the recorded seconds (tests/closures.json) of the
pre-screen drivers that tests/mutation_table.py would actually run on it --
its closure's drivers minus those whose clean B3 reach row (reach/*.json)
never executed the line and never read the file (mutation_table.never_reaches).
Count key: the reach rows' production LINE hits, never a script attribute.
Prints one line per chosen site, `FILE:LINE KIND  # w=.. cost=..s`, in the
order chosen: weight descending, then cost ascending, at most --per-file per
production file, until --n sites.
Command:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 \
          dev/audit/rounds/round11/D3/s3/select_pool.py [--n 36] [--per-file 1]
Perturbation: --drop-reach removes every reach row, so every closure driver
runs on every site: each printed cost rises (never falls).
Expected: deterministic at baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
Machine: any (source and committed rows only; no timing is taken).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse
import json
import sys
from pathlib import Path

ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(HERE))
import mutation_table as mt  # noqa: E402
import enumerate as en  # noqa: E402
import prescreen as ps  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=36)
    ap.add_argument("--per-file", type=int, default=1)
    ap.add_argument("--drop-reach", action="store_true")
    ap.add_argument("--exclude", default="", help="file of FILE:LINE KIND to skip")
    a = ap.parse_args()
    closures = mt.load_closures()
    allow = [s for s in mt.DEFAULT_SCRIPTS.split(",")
             if s and s not in ps.PRESCREEN_SKIP]
    secs = {}
    raw = json.loads((ROOT / "tests/closures.json").read_text())
    for s, e in raw.get("recorded", {}).items():
        secs[s] = float(e.get("seconds", 0) if isinstance(e, dict) else 0)
    rows = {}
    if not a.drop_reach:
        for p in (HERE / "reach").glob("tests_*.py.json"):
            r = json.loads(p.read_text())
            if r.get("reach") and not r["reach"]["problems"] and r["rc"] == 0:
                rows[r["script"]] = {"hits": r["reach"]["hits"],
                                     "reads": r["reach"]["reads"],
                                     "foreign": [], "untraced": [],
                                     "processes": r["reach"]["processes"],
                                     "rc": 0}
    skip = set()
    if a.exclude:
        skip = {ln.split("#")[0].strip() for ln in open(a.exclude)
                if ln.split("#")[0].strip()}
    scored = []
    for s in en.universe():
        key = f"{s['file'].rsplit('/', 1)[-1]}:{s['line']} {s['kind']}"
        if key in skip:
            continue
        drv = mt.drivers_for(s["file"], closures, allow)
        run = [d for d in drv if not (d in rows and mt.reach_skip(rows[d], s))]
        cost = sum(secs.get(d, 0.0) for d in run)
        scored.append((-en.weight(s), cost, key, s["file"]))
    scored.sort()
    per = {}
    out = 0
    for nw, cost, key, f in scored:
        if per.get(f, 0) >= a.per_file:
            continue
        per[f] = per.get(f, 0) + 1
        print(f"{key}  # w={-nw} cost={cost:.0f}s")
        out += 1
        if out >= a.n:
            break
    print(f"# RESULT chosen={out} count of universe={len(scored)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
