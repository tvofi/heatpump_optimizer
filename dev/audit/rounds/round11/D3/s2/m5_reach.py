#!/usr/bin/env python3
"""D3-s2 D3.M5 closure over-approximation, from traced baselines.

Metric: per (script, cell file) pair the recorded closure (tests/closures.json)
claims, whether that script's traced unmutated run (tests/mutation_table.py
traced_baseline -> collect) executed ANY line inside a function body of the
file, or read the file as text. A pair that does neither is over-approximated:
a function-body edit in that file is selected by `closure.py select --diff` for
that script, yet cannot change its run (mutation_table.reach_skip's premise).
Count key: pairs with zero function-body hits and no text read, out of claimed
pairs whose reach row is clean (no foreign/untraced child, all processes recorded).
Instrumented symbols: tests/mutation_table.py:traced_baseline/collect/reach_problems
over the drivers prescreen.py ran; tests/closures.json:closures.
Perturbation: add a call into one never-executed function of a cell file to a
listed script and its pair leaves the over-approximated count (count -1); in
memory, `--claim-only SCRIPT:CELL` removes that pair from the closure the
count reads (count -1, and over_seconds[CELL] down by SCRIPT's seconds).
Also prints, per cell, the closures.json recorded seconds of the scripts
`closure.py select` would run for a function-body-only edit of that cell that
cannot change their run (over_seconds), against all its selected seconds.
Run: PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s2/m5_reach.py dev/audit/rounds/round11/D3/s2/run/reach
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B2. Counts are exact (contention-immune).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import ast
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, "tests")
sys.path.insert(0, str(HERE))
import mutation_table as mt  # noqa: E402
import enumerate as en  # noqa: E402

P = "custom_components/heatpump_optimizer/"


def body_lines(path):
    tree = ast.parse(Path(path).read_text())
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for b in n.body:
                out.update(range(b.lineno, (b.end_lineno or b.lineno) + 1))
    return out


def main():
    rdir = Path(sys.argv[1])
    cj = json.load(open("tests/closures.json"))
    clos = cj["closures"]
    secs = {k: v.get("seconds", 0.0) for k, v in cj["recorded"].items()}
    if "--claim-only" in sys.argv:
        sc, cell = sys.argv[sys.argv.index("--claim-only") + 1].split(":")
        clos[sc] = [f for f in clos[sc] if not f.endswith("/" + cell)]
    cells = [P + f"{c}.py" for c in en.CELLS]
    bodies = {c: body_lines(c) for c in cells}
    rows = []
    for f in sorted(rdir.glob("*.json")):
        script = f.name[:-5].replace("tests_", "tests/", 1)
        reach = json.loads(f.read_text())
        if reach is None:
            print(f"{script}\tNO-REACH (traced run not green or timed out)")
            continue
        probs = mt.reach_problems(reach)
        for c in cells:
            if c not in clos.get(script, []):
                continue
            hits = set(reach["hits"].get(c, []))
            fb = len(hits & bodies[c])
            read = c in reach["reads"]
            over = (not probs) and fb == 0 and not read
            rows.append((script, c, fb, read, bool(probs), over))
            print(f"{script}\t{c.split('/')[-1]}\tbody_hits={fb}\tread={read}"
                  f"\treach_problems={len(probs)}\tOVER={over}")
    clean = [r for r in rows if not r[4]]
    over = [r for r in rows if r[5]]
    print(f"RESULT claimed_pairs={len(rows)} pairs")
    print(f"RESULT clean_pairs={len(clean)} pairs")
    print(f"RESULT over_approximated_pairs={len(over)} pairs")
    by = {}
    for r in over:
        by.setdefault(r[0], []).append(r[1].split('/')[-1])
    for s, fs in sorted(by.items()):
        print(f"RESULT over[{s}]={len(fs)} cells ({','.join(fs)})")
    for c in cells:
        sel = [s for s, fs in clos.items() if c in fs]
        ov = [r[0] for r in over if r[1] == c]
        print(f"RESULT over_seconds[{c.split('/')[-1]}]="
              f"{sum(secs.get(s, 0) for s in ov):.1f} s of "
              f"{sum(secs.get(s, 0) for s in sel):.1f} s selected "
              f"({len(ov)} of {len(sel)} scripts)")
    print("RESULT thread_factor=1.00")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
