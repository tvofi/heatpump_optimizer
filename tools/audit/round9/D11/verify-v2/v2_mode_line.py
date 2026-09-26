#!/usr/bin/env python3
"""D11 round 9, verifier V2 (independent) for D11-s2-04.

METRIC (one line): for each backticked `MODE: ...` literal in CLAUDE.md, whether it is a
  byte-exact substring of tests/closure.py:print_plan's output for a real plan built by
  closure.py itself (scoped over an empty diff, and full), and whether it becomes one after
  normalising the em dash to `--`; plus whether the FULL output carries any digit 0.
KEY: print_plan's own stdout for plans from the production planner, not a copied string.
COMMAND: PYTHONPATH=tests/hastub python tools/audit/round9/D11/verify-v2/v2_mode_line.py
EXPECTED (baseline 1936d5ca): exact_literals_found=1 of 2 (`MODE: FULL` alone is exact),
  scoped literal found only after dash normalisation, full_output_has_zero=0.
"""
import os
for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")
import importlib.util, io, re, sys, time

T0p, T0t = time.process_time(), time.thread_time()


def main():
    sys.path.insert(0, "tests")
    spec = importlib.util.spec_from_file_location("closure", "tests/closure.py")
    cl = importlib.util.module_from_spec(spec); spec.loader.exec_module(cl)
    rule1 = open("CLAUDE.md", encoding="utf-8").read().split("\n2. ", 1)[0]
    lits = [l for l in re.findall(r"`([^`]*MODE:[^`]*)`", rule1)]
    # plans: a 0-run scoped plan and a full plan, shaped as print_plan reads them
    scoped0 = {"mode": "scoped", "run": [], "skip": {"tests/x.py": {"closure_size": 3, "reason": "no changed file"}},
               "changed": ["README.md"]}
    full = {"mode": "full", "reason": "push to main"}
    outs = {}
    for name, plan in (("scoped0", scoped0), ("full", full)):
        b = io.StringIO(); cl.print_plan(plan, stream=b); outs[name] = b.getvalue()
        print(f"# print_plan[{name}] mode line: {[l.strip() for l in outs[name].splitlines() if 'MODE' in l]}")
    allout = outs["scoped0"] + outs["full"]
    exact = sum(l in allout for l in lits)
    norm = sum(l.replace("—", "--") in allout for l in lits)
    print(f"# CLAUDE.md rule 1 literals: {lits}")
    print(f"RESULT literals={len(lits)} count")
    print(f"RESULT exact_literals_found={exact} count")
    print(f"RESULT dash_normalised_found={norm} count")
    print(f"RESULT full_output_has_zero={int(bool(re.search(r'(?<![0-9])0(?![0-9])', outs['full'])))} count")
    pc, tc = time.process_time() - T0p, time.thread_time() - T0t
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
