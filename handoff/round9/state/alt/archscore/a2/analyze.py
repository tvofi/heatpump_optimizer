#!/usr/bin/env python3
"""Per-metric direction accuracy over the labelled corpus (corpus.tsv -> accuracy_tables.md).

Convention: GOOD expects delta <= 0, BAD expects delta >= 0 (a ratchet only ever wants down).
  right = moved the expected way strictly (GOOD < 0, BAD > 0)
  flat  = delta == 0            wrong = moved the unexpected way
  ok    = right + flat          (the brief's "points the right way": GOOD <= 0, BAD >= 0)
  sep   = (right - wrong) / n   (a metric that never moves scores 0, a size proxy scores high)
NEUTRAL rows are listed but never scored. NA deltas are excluded from that metric's n.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
rows = list(csv.DictReader(open(HERE / "corpus.tsv"), delimiter="\t"))
metrics = [k[2:] for k in rows[0] if k.startswith("d_")]
STRUCT = metrics[:25]


def val(r, m):
    v = r[f"d_{m}"]
    return None if v == "NA" else float(v)


def score(subset, m, expect):
    right = flat = wrong = 0
    for r in subset:
        v = val(r, m)
        if v is None:
            continue
        if v == 0:
            flat += 1
        elif (v < 0) == (expect == "down"):
            right += 1
        else:
            wrong += 1
    return right, flat, wrong


good = [r for r in rows if r["label"] == "GOOD"]
good_nc = [r for r in good if r["circ"] == "no"]
bad = [r for r in rows if r["label"] == "BAD"]
# the defect-shaped BAD commits: production diff <= 300 lines, so a size row cannot fire on feature growth alone
bad_small = [r for r in bad if float(r["d_null_pkg_loc"]) <= 300]
out = []
p = out.append
p(f"GOOD n={len(good)} (non-circular {len(good_nc)}), BAD n={len(bad)}, NEUTRAL n={sum(r['label']=='NEUTRAL' for r in rows)}\n")
p(f"BAD-small (production diff <= 300 lines) n={len(bad_small)}: {', '.join(r['sha'] for r in bad_small)}\n")
p("| metric | GOOD right/flat/wrong | GOOD ok% | GOOD-nc right/flat/wrong | BAD right/flat/wrong | BAD ok% | BAD-small right/flat/wrong | moved% (G+B) | sep |")
p("|---|---|---|---|---|---|---|---|---|")
summary = []
for m in metrics:
    g = score(good, m, "down")
    gn = score(good_nc, m, "down")
    b = score(bad, m, "up")
    bs = score(bad_small, m, "up")
    ng, nb = sum(g), sum(b)
    n = ng + nb
    right = g[0] + b[0]
    wrong = g[2] + b[2]
    moved = right + wrong
    sep = (right - wrong) / n if n else 0
    summary.append((m, sep))
    p(f"| {m} | {g[0]}/{g[1]}/{g[2]} | {100*(g[0]+g[1])/ng:.0f} | {gn[0]}/{gn[1]}/{gn[2]} | "
      f"{b[0]}/{b[1]}/{b[2]} | {100*(b[0]+b[1])/nb:.0f} | {bs[0]}/{bs[1]}/{bs[2]} | {100*moved/n:.0f} | {sep:+.2f} |")

# blind-spot matrix: which metrics rise on each BAD case
p("\n### BAD cases: which metrics rose (structure metrics | enumerators), and which fell\n")
p("| sha | class | structure metrics up | structure metrics down | enumerators up | pkg LOC delta |")
p("|---|---|---|---|---|---|")
for r in bad:
    up = [m for m in STRUCT if (val(r, m) or 0) > 0]
    down = [m for m in STRUCT if (val(r, m) or 0) < 0]
    eup = [m for m in metrics[25:-1] if (val(r, m) or 0) > 0]
    p(f"| {r['sha']} | {r['class']} | {', '.join(up) or '**none (blind)**'} | {', '.join(down) or '-'} | "
      f"{', '.join(eup) or 'none'} | {r['d_null_pkg_loc']} |")

p("\n### GOOD cases: which structure metrics fell / rose\n")
p("| sha | pr | circ | structure metrics down | structure metrics UP | enumerators down | pkg LOC delta |")
p("|---|---|---|---|---|---|---|")
for r in good:
    up = [m for m in STRUCT if (val(r, m) or 0) > 0]
    down = [m for m in STRUCT if (val(r, m) or 0) < 0]
    edown = [m for m in metrics[25:-1] if (val(r, m) or 0) < 0]
    p(f"| {r['sha']} | {r['pr']} | {r['circ']} | {', '.join(down) or '**none (blind)**'} | {', '.join(up) or '-'} | "
      f"{', '.join(edown) or 'none'} | {r['d_null_pkg_loc']} |")

# composite: the ratchet's own verdict (any structure metric up = fail)
def ratchet_fail(r):
    return any((val(r, m) or 0) > 0 for m in STRUCT)
def ratchet_gain(r):
    return any((val(r, m) or 0) < 0 for m in STRUCT)
p("\n### Composite: the ratchet's own decision rule (any of the 25 rows up => FAIL)\n")
bf = sum(ratchet_fail(r) for r in bad)
gf = sum(ratchet_fail(r) for r in good)
gg = sum(ratchet_gain(r) and not ratchet_fail(r) for r in good)
p(f"- BAD cases the ratchet would FAIL: {bf}/{len(bad)}")
p(f"- GOOD cases the ratchet would PASS with a recorded gain: {gg}/{len(good)}; FAIL: {gf}/{len(good)}; no row moved: {sum(not ratchet_fail(r) and not ratchet_gain(r) for r in good)}")
# size-matched: BAD that fail only because the package grew
p("\n### Size confound: sign agreement of each structure metric with raw package LOC (pkg LOC != 0 and metric moved)\n")
agree_rows = []
for m in STRUCT + metrics[25:-1]:
    a = d = 0
    for r in good + bad:
        v, s = val(r, m), val(r, "null_pkg_loc")
        if not v or not s:
            continue
        if (v > 0) == (s > 0):
            a += 1
        else:
            d += 1
    if a + d:
        agree_rows.append((m, a, d))
p("| metric | agrees with LOC sign | disagrees |")
p("|---|---|---|")
for m, a, d in agree_rows:
    p(f"| {m} | {a} | {d} |")
(HERE / "accuracy_tables.md").write_text("\n".join(out) + "\n")
print("\n".join(out))
