#!/usr/bin/env python3
"""D3-s1 M5: closure over-approximation and per-script cost, from traced baselines.

Metric (one line): for each gate script S whose tests/closures.json closure
contains cell file F, the number of F's executable lines S's traced unmutated
run executed (sys.monitoring LINE events, `tests/mutation_table.py:REACH_HOOK`)
and whether S read F as text; a (S, F) pair with 0 executed lines and no text
read is an over-approximated closure edge (touching F forces S, S cannot see F).
Also per-script measured wall vs closures.json `recorded.seconds` (provisional).

Instrumented symbol: tests/closure.py's measured closure (tests/closures.json
`closures`) against mutation_table:traced_baseline's reach of each cell file.
Perturbation: delete one cell file's import from a script's traced reach (the
`--drop FILE` flag zeroes its hits) -> over_approx_pairs goes up by the number
of scripts that executed it; the identity run is the null control.

Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/m5_closure_reach.py [--drop FILE]
Needs: state/baselines.json written by prescreen.py baseline (same directory).
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: owner macOS arm64, shared.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json
import sys
from pathlib import Path

sys.path.insert(0, "tests")
import mutation_table as mt  # noqa: E402

HERE = Path(__file__).resolve().parent
CELLS = ["coordinator", "optimizer", "thermal_model", "sysid", "defrost",
         "flow_lift", "process_worker", "batchmath", "price_model", "tariff",
         "grid_fee", "dhw_planner"]
RELS = [mt.PKG + c + ".py" for c in CELLS]


def main() -> int:
    drop = None
    if "--drop" in sys.argv:
        drop = sys.argv[sys.argv.index("--drop") + 1]
    base = json.loads((HERE / "state" / "baselines.json").read_text())
    clos = mt.load_closures()
    rec = mt.recorded_seconds()
    exe = {r: mt.executable_lines(mt.ROOT / r) for r in RELS}
    over, pairs, refused = [], 0, []
    print("script\trc\twall_s\trecorded_s\tratio\treach_ok\tcell_lines_hit")
    for s in sorted(base):
        b = base[s]
        reach = b["reach"]
        probs = mt.reach_problems(reach)
        hits_tot = 0
        for r in RELS:
            if r not in clos.get(s, ()):
                continue
            pairs += 1
            if probs:
                continue
            hits = set(reach["hits"].get(r, ())) & exe[r]
            if r == drop:
                hits = set()
            read = r in reach["reads"]
            hits_tot += len(hits)
            if not hits and not read:
                over.append((s, r))
        if probs:
            refused.append((s, probs[0]))
        w = b["run"]["seconds"]
        rs = rec.get(s, 0.0)
        print(f"{s}\t{b['run']['rc']}\t{w:.1f}\t{rs:.1f}\t"
              f"{(w / rs if rs else 0):.2f}\t{not probs}\t{hits_tot}")
    print()
    for s, r in over:
        print(f"OVER-APPROX {s} -> {r.rsplit('/', 1)[-1]}")
    for s, p in refused:
        print(f"REACH-REFUSED {s}: {p}")
    print(f"RESULT closure_pairs={pairs}")
    print(f"RESULT over_approx_pairs={len(over)}")
    print(f"RESULT scripts_reach_refused={len(refused)}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT thread_factor=1.00")
    return 0


if __name__ == "__main__":
    sys.exit(main())
