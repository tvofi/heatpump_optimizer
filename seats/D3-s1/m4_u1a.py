#!/usr/bin/env python3
"""D3-s1 box D3-u1a: D3.M4's answer for every full-net survivor of this box's slice.

Metric (one line): per full-net survivor (results/complete/<key>.json, verdict
SURVIVED, key in state/keys-D3-u1a-surv.txt), the mutated production line and
file, and the drivers whose traced UNMUTATED run executed that line (reach
`hits` in state/baselines.json); `executed_by=0` means no gate script reaches
the line at all, `executed_by>0` means a script runs it and asserts nothing
its value changes. The check that should have failed is derived from the
mutant kind and named in the row.

Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/m4_u1a.py [--json]
Expected: one row per survivor; `RESULT survivors=<n>` equals tabulate's
complete-SURVIVED count for this slice (exact; counts, no timing).
Instrumented symbol: tests/mutation_table.py:traced_baseline's reach of each
survivor's production line (state/baselines.json, taken on box D3-u1a).
Perturbation: `--drop-driver S` removes S's reach -> executed_by falls by one
on every row S executed (down); the identity run is the null control.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-u1a,
Linux x86_64, nproc 4, Intel Xeon @ 2.30GHz.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATE = HERE / "state"

WANT = {
    "CMP_BOUND": "a check driving {sym} with the compared value exactly at the boundary, asserting the branch the original operator takes",
    "GUARD_OFF": "a check driving {sym} with the guard's condition true, asserting the guarded branch's effect (its return or state change)",
    "CLAMP_DROP": "a check feeding {sym} a value outside the clamp's range, asserting the bounded result",
    "CONST": "a check whose expected value depends on the constant's value in {sym} (a recorded number or a threshold crossing)",
    "BOOLOP": "a check driving {sym} with exactly one operand of the boolean true, asserting the original conjunction/disjunction",
    "RETURN_DEL": "a check driving {sym} down the early-return path, asserting nothing after it runs (state or result unchanged)",
    "RAISE_DEL": "a check driving {sym} into the raise, asserting the exception",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--drop-driver")
    a = ap.parse_args()
    base = json.loads((STATE / "baselines.json").read_text())
    if a.drop_driver:
        base.pop(a.drop_driver, None)
    keys = [k.strip() for k in (STATE / "keys-D3-u1a-surv.txt").read_text().split() if k.strip()]
    rows = []
    for k in keys:
        p = STATE / "results" / "complete" / (k + ".json")
        if not p.exists():
            continue
        r = json.loads(p.read_text())
        if r["verdict"] != "SURVIVED":
            continue
        m = r["mutant"]
        ex = sorted(s for s, v in base.items()
                    if v.get("reach") and m["line"] in set(v["reach"]["hits"].get(m["file"], ())))
        sym = m["anchor"].split(":", 1)[1].rsplit(" ", 2)[0]
        rows.append({"key": k, "file": m["file"], "line": m["line"], "kind": m["kind"],
                     "symbol": sym, "old": m["old"].strip(), "new": m["new"].strip(),
                     "drivers_run": sorted(r["runs"]), "executed_by": ex,
                     "should_fail": WANT.get(m["kind"], "a check on {sym}").format(sym=sym)})
    if a.json:
        print(json.dumps(rows, indent=1))
    else:
        for x in rows:
            print(f"{x['key']}\t{x['file'].rsplit('/', 1)[1]}:{x['line']}\t{x['kind']}\t{x['symbol']}\t"
                  f"executed_by={len(x['executed_by'])}\t{x['old'][:70]} -> {x['new'][:50]}")
    print(f"RESULT survivors={len(rows)}")
    print(f"RESULT executed_by_none={sum(1 for x in rows if not x['executed_by'])}")
    c = Counter(s for x in rows for s in x["executed_by"])
    for s, n in c.most_common():
        print(f"RESULT executes_survivor_line[{s}]={n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
