#!/usr/bin/env python3
"""D3.M2/M3/M4 enumerator and pre-screen table for seat D3-s3, round 11.

Reads the pre-screen record prescreen.py wrote (prescreen_all.json) and prints
one line per mutant: verdict (KILLED by <first killing script>, LIVES, or
SKIP-*), the site, and the closure scripts that ran / were reach-skipped.
--survivors prints only the LIVES lines (the D3.M3/M4 universe).
--matrix prints, per script, the mutants it killed (kill overlap; complete
only for a record taken with prescreen.py --overlap).

Metric: per mutant, the number of closure scripts whose run on the mutated
tree names more failing checks than the unmutated baseline
(tests/mutation_table.py:killed); LIVES = 0 with every driver run.
Command:  python3 dev/audit/rounds/round11/D3/s3/survivors.py \
          [--json dev/audit/rounds/round11/D3/s3/prescreen_all.json] [--survivors|--matrix]
Source-only: reads the committed record, runs nothing; exact.
Perturbation: the record's null control (away.py:57 NULL_COMMENT) is killed
by no script, printed as the first line.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box B3.
"""
import json
import sys
from collections import defaultdict

args = sys.argv[1:]
path = "dev/audit/rounds/round11/D3/s3/prescreen_all.json"
if "--json" in args:
    path = args[args.index("--json") + 1]
d = json.load(open(path))
outc = d["outcomes"]
verd = d["verdicts"]
order = {}
for r in d["runs"]:
    order.setdefault(r["mutant"], []).append(r["script"])
print("# null control: comment-only edit; killed by none (mutation_table refuses the lane otherwise)")
matrix = defaultdict(list)
for m in d["pool"]:
    key = f"{m['file']}:{m['line']} {m['kind']}"
    o = outc.get(key, {})
    killers = sorted(s for s, v in o.items() if v is True)
    ran = sorted(s for s, v in o.items() if v in (True, False))
    skipped = sorted(s for s, v in o.items() if v == "reach-skip")
    timed = sorted(s for s, v in o.items() if v is None)
    for s in killers:
        matrix[s].append(key)
    v = verd.get(key, "NOT-RUN")
    if "--survivors" in args and (killers or not str(v).startswith("LIVES")):
        continue
    if "--matrix" in args:
        continue
    print(f"{'KILLED' if killers else v}\t{key}\t{m['anchor']}\t"
          f"killers={','.join(k.split('/')[-1] for k in killers) or '-'}\t"
          f"ran={','.join(k.split('/')[-1] for k in ran)}\t"
          f"reach_skipped={len(skipped)}\ttimed_out={','.join(timed) or '-'}\t"
          f"new={m['new'].strip()[:60]!r}")
if "--matrix" in args:
    for s, ks in sorted(matrix.items(), key=lambda x: -len(x[1])):
        print(f"{s}\t{len(ks)}\t{' '.join(k.split('/')[-1] for k in ks)}")
