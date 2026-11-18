#!/usr/bin/env python3
"""D3-s1 box D3-u1c slice: tally of the K1 pre-screen and K2 full net over
state/keys-D3-u1c.txt, and D3.M4's answer per survivor.

Metric (one line): per key of the slice, its verdict (`mutation_table.killed`
over the fast net, then over every closure driver for the full net); per
survivor, the mutated production line and the closure drivers whose traced,
unmutated run EXECUTES that line (`exec`) -- the checks that should have
failed -- versus those that never reach it.
Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/slice_u1c.py [--tsv] [--surv-keys]
Expected: driven + not-driven = 309 keys; counts exact (contention-immune);
no timing claims except the provisional per-mutant wall sums it prints.
Instrumented symbol: tests/mutation_table.py:killed / reach_skip on each
mutant's production line, via prescreen.py's drive and its traced baselines
(state/baselines.json, re-taken on box D3-u1c).
Perturbation: deleting one results/pre/<key>.json lowers `driven` by one and
raises `not_driven`; prescreen.py's positive control (posctl-D3-u1c) must read
KILLED, its null control LIVES.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-u1c, Linux
x86_64, nproc 4, Intel Xeon @ 2.10GHz, venv-ci CPython 3.14.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
_argv, sys.argv = sys.argv, sys.argv[:1]
import prescreen as p  # noqa: E402

KEYS = p.STATE / "keys-D3-u1c.txt"


def load(sub):
    d = p.RESULTS / sub
    return {q.stem: json.loads(q.read_text()) for q in d.glob("*.json")} if d.exists() else {}


def main() -> int:
    keys = [k.strip() for k in KEYS.read_text().split() if k.strip()]
    pre, comp = load("pre"), load("complete")
    base = p.load_base()
    driven = [k for k in keys if k in pre]
    c = Counter(pre[k]["verdict"] for k in driven)
    first = Counter(pre[k]["killed_by"][0] for k in driven if pre[k]["killed_by"])
    noexec_all = sum(1 for k in driven if not pre[k]["runs"])
    skipped_runs = sum(len(pre[k]["skipped"]) for k in driven)
    relaxed_runs = sum(len(pre[k].get("relaxed_skipped", [])) for k in driven)
    red_unparsed = sum(1 for k in driven for r in pre[k]["runs"].values()
                       if r["rc"] != 0 and not r["killed"] and not r["timed_out"])
    print(f"RESULT keys={len(keys)}")
    print(f"RESULT driven={len(driven)}")
    print(f"RESULT not_driven={len(keys) - len(driven)}")
    for v in ("KILLED", "SURVIVED", "TIMEOUT"):
        print(f"RESULT pre_{v.lower()}={c.get(v, 0)}")
    for s, n in first.most_common():
        print(f"RESULT first_kill[{s}]={n}")
    print(f"RESULT mutants_no_driver_ran={noexec_all}")
    print(f"RESULT driver_runs_skipped_by_reach={skipped_runs}")
    print(f"RESULT driver_runs_relaxed_skipped={relaxed_runs}")
    print(f"RESULT driver_runs_red_unparsed={red_unparsed}")
    surv = [k for k in driven if pre[k]["verdict"] == "SURVIVED"]
    cc = Counter(comp[k]["verdict"] for k in surv if k in comp)
    print(f"RESULT full_net_driven={sum(cc.values())}")
    for v in ("KILLED", "SURVIVED", "TIMEOUT"):
        print(f"RESULT full_net_{v.lower()}={cc.get(v, 0)}")
    ck = Counter(s for k in surv if k in comp for s in comp[k]["killed_by"])
    for s, n in ck.most_common():
        print(f"RESULT full_net_kill[{s}]={n}")
    wall = sum(pre[k]["wall"] for k in driven)
    print(f"RESULT pre_wall_sum={wall:.0f} s (provisional)")
    if "--surv-keys" in _argv:
        for k in surv:
            print(k)
        return 0
    if "--tsv" in _argv:
        for k in surv:
            r = comp.get(k, pre[k])
            m = r["mutant"]
            ds = [s for s in base if m["file"] in p.mt.load_closures().get(s, ())]
            cls = {s: p.classify(base, s, m) for s in ds}
            ex = sorted(s for s, v in cls.items() if v == "exec")
            sym = m["anchor"].split(":", 1)[1].rsplit(" ", 2)[0]
            print("\t".join([
                k, f"{m['file'].rsplit('/', 1)[-1]}:{m['line']}", sym, m["kind"],
                m["old"].strip(), m["new"].strip(),
                "full:" + r["verdict"] if k in comp else "fast:SURVIVED",
                ",".join(s.split("/")[-1] for s in ex) or "NONE",
            ]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
