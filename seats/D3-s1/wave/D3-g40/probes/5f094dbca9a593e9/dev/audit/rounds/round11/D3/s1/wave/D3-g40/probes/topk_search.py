#!/usr/bin/env python3
# Shared input search for box D3-g40's _smooth_topk_sum / _smooth_topk_sum_batch probes (not itself a probe).
# One deterministic input corpus (seed 20261125), run through the mutated symbol AND its production caller
# (_plateau_aware_topk_sum / _plateau_aware_topk_sum_batch, the only callers, tau fixed at _PEAK_SMOOTH_TAU=0.05),
# on the baseline arm and the one-line-mutant arm (probe_lib). Metric: count of inputs whose returned value is
# not bit-identical between the arms (nan == nan counts identical), max |delta|, and RuntimeWarnings per arm.
# Families (each tagged `reach`: whether the production caller can hand the symbol such an input):
#   plateau   >k windows tied at the peak, the rest uniform below -- the caller's smooth branch (reach)
#   tieband   ties within _PEAK_TIE_BAND (1e-3) but not exact (reach)
#   uniform   random excess vectors, called directly (direct; the caller sends only plateau rows)
#   spread    one huge window over a plateau of small ones, |z| far beyond 60 (reach)
#   tiny      plateau peaks 1e-7 .. 5e-324, where tau*peak < 1e-9 (reach: excess = windows - threshold)
#   zero      all-zero rows, k >= m, m == 1 (reach for the batch caller: an all-zero row has n_at_peak = m)
#   negative  rows whose max is 0 with negative entries (direct only: excess = max(0, ...) is never negative)
#   exacttie  float-engineered inputs for the 1e-6 stop: n*w == k +- 1e-6 searched by bisection on the peak
import json

SNIP = r'''
import json, warnings, math
import numpy as np
from custom_components.heatpump_optimizer import tariff as T
rng = np.random.default_rng(20261125)
cases = []
def add(fam, reach, x, k):
    cases.append((fam, reach, np.asarray(x, dtype=float), int(k)))
for _ in range(600):
    m = int(rng.integers(2, 49)); k = int(rng.choice([1, 2, 3, 5]))
    peak = float(10 ** rng.uniform(-3, 2)); nt = int(rng.integers(min(k + 1, m), m + 1))
    x = rng.uniform(0, peak, m); x[rng.choice(m, nt, replace=False)] = peak; add("plateau", 1, x, k)
for _ in range(300):
    m = int(rng.integers(3, 49)); k = int(rng.choice([1, 2, 3]))
    peak = float(10 ** rng.uniform(-2, 2)); x = rng.uniform(0, peak, m)
    idx = rng.choice(m, min(m, k + 2), replace=False); x[idx] = peak - rng.uniform(0, 9e-4, idx.size); add("tieband", 1, x, k)
for _ in range(300):
    m = int(rng.integers(1, 49)); k = int(rng.integers(1, 7)); add("uniform", 0, rng.uniform(0, 10, m), k)
for big in (1e2, 1e3, 1e4, 1e6, 1e9):
    for k in (1, 2, 3):
        add("spread", 1, [big] + [1.0] * 8 + [0.5] * 5, k); add("spread", 1, [big] * (k + 1) + [1e-6] * 10, k)
for p in (1e-7, 2e-8, 1e-8, 1e-9, 1e-10, 1e-12, 1e-15, 1e-300, 1e-310, 5e-324):
    for k in (1, 2, 3):
        add("tiny", 1, [p] * (k + 2) + [p / 2, 0.0, p / 3], k); add("tiny", 1, [p] * (k + 3), k)
for m in (1, 2, 3, 6):
    for k in (1, 3, 7):
        add("zero", 1, [0.0] * m, k); add("zero", 1, [2.5] * m, k)
for k in (1, 2, 3, 4):
    add("negative", 0, [0.0, -1.0, -2.0, -3.0], k); add("negative", 0, [0.0, 0.0, -5.0], k)
# exacttie: scan peaks around 1 for k=1, n=2..6 plateaus with one lower window, many offsets
for n in (2, 3, 4, 5, 6):
    for j in range(200):
        add("exacttie", 1, [1.0] * n + [1.0 - (j + 1) * 1e-3 / 200.0], 1)
def call(fn, x, k):
    with warnings.catch_warnings(record=True) as rec:
        warnings.simplefilter("always")
        v = fn(x, k)
    return v, sum(1 for r in rec if issubclass(r.category, RuntimeWarning))
mode = "MODE"
out = []
for fam, reach, x, k in cases:
    if mode == "scalar":
        d, wd = call(lambda a, kk: T._smooth_topk_sum(a, kk, T._PEAK_SMOOTH_TAU), x, k)
        c, wc = call(T._plateau_aware_topk_sum, x, k) if x.size and np.max(x) > 0 else (None, 0)
    else:
        X = x[None, :]
        d, wd = call(lambda a, kk: T._smooth_topk_sum_batch(a, kk, T._PEAK_SMOOTH_TAU), X, k)
        d = float(d[0])
        if x.size:
            c, wc = call(T._plateau_aware_topk_sum_batch, X, min(max(1, k), x.size)); c = float(c[0])
        else:
            c, wc = None, 0
    out.append([fam, reach, float(d), None if c is None else float(c), wd, wc])
# batch multi-row: the same rows stacked, so row interaction (frozen rows, done.all()) is exercised
if mode == "batch":
    for m in (4, 9, 14):
        rows = [c for c in cases if c[2].size == m][:40]
        for k in (1, 2, 3):
            if rows:
                X = np.stack([c[2] for c in rows])
                d, wd = call(lambda a, kk: T._smooth_topk_sum_batch(a, kk, T._PEAK_SMOOTH_TAU), X, k)
                c2, wc = call(T._plateau_aware_topk_sum_batch, X, k)
                for i in range(X.shape[0]):
                    out.append(["stacked-reach" if rows[i][1] else "stacked-direct", rows[i][1], float(d[i]), float(c2[i]), wd if i == 0 else 0, wc if i == 0 else 0])
print(json.dumps(out))
'''


def compare(b, m):
    """Per family: n, differing (direct), differing (caller), max |delta|, warnings baseline/mutant."""
    fams = {}
    def same(u, v):
        if u is None and v is None:
            return True
        if u is None or v is None:
            return False
        return (u != u and v != v) or u == v
    def delta(u, v):
        if u is None or v is None:
            return 0.0
        if u != u or v != v:
            return float("inf") if (u != u) != (v != v) else 0.0
        return abs(u - v)
    for rb, rm in zip(b, m):
        f = fams.setdefault(rb[0], {"reach": rb[1], "n": 0, "diff_direct": 0, "diff_caller": 0, "max_delta_direct": 0.0,
                                    "max_delta_caller": 0.0, "nan_mutant": 0, "warn_baseline": 0, "warn_mutant": 0,
                                    "example": None})
        f["n"] += 1
        if not same(rb[2], rm[2]):
            f["diff_direct"] += 1; f["max_delta_direct"] = max(f["max_delta_direct"], delta(rb[2], rm[2]))
            f["example"] = f["example"] or {"baseline": rb[2], "mutant": rm[2]}
        if not same(rb[3], rm[3]):
            f["diff_caller"] += 1; f["max_delta_caller"] = max(f["max_delta_caller"], delta(rb[3], rm[3]))
        f["nan_mutant"] += int(rm[2] != rm[2])
        f["warn_baseline"] += rb[4] + rb[5]; f["warn_mutant"] += rm[4] + rm[5]
    return fams


def report(b, m):
    fams = compare(b, m)
    for name, f in fams.items():
        print(f"FAMILY {name} {json.dumps(f)}")
    reach = [f for f in fams.values() if f["reach"]]
    tot = lambda key, fs: sum(f[key] for f in fs)
    print(f"RESULT inputs={sum(f['n'] for f in fams.values())} count")
    print(f"RESULT differing_reachable_caller={tot('diff_caller', reach)} count")
    print(f"RESULT differing_reachable_direct={tot('diff_direct', reach)} count")
    print(f"RESULT differing_all_direct={tot('diff_direct', fams.values())} count")
    md = max([f["max_delta_caller"] for f in reach] + [0.0])
    print(f"RESULT max_delta_reachable_caller={md:.6g} kW")
    print(f"RESULT runtime_warnings_baseline={tot('warn_baseline', fams.values())} count")
    print(f"RESULT runtime_warnings_mutant={tot('warn_mutant', fams.values())} count")
    return fams
