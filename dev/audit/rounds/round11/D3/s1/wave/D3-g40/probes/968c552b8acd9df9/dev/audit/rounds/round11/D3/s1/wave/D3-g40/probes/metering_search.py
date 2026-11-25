#!/usr/bin/env python3
# Shared input search for box D3-g40's metering_windows probes (not itself a probe).
# One fixed corpus run through tariff.metering_windows and each production caller that can be reached without a
# live coordinator: the window-count expression of Optimizer._n_peak_windows (optimizer.py:4163,
# `metering_windows(np.zeros(n_steps), window_minutes, dt, offset_steps).size`), topology._window_peak
# (topology.py:845), tariff._peak_charge's windows (tariff.py:906 guards size 0 first) and tariff.py:1227's
# max-window helper (guards size 0 first). Metric per input: output length, values (bit-exact, nan == nan),
# whether the result aliases the input array, RuntimeWarnings.
SNIP = r'''
import json, warnings
import numpy as np
from custom_components.heatpump_optimizer import tariff as T
from custom_components.heatpump_optimizer import topology as TOP
rng = np.random.default_rng(20261125)
cases = []
for n in (0, 1, 2, 3, 4, 5, 7, 12, 96):
    for wm, dt in ((15, 0.25), (60, 0.25), (60, 1.0), (30, 0.5), (60, 0.5), (15, 1.0), (5, 0.25)):
        for off in (0, 1, 2, 3, 5):
            cases.append((n, wm, dt, off))
out = []
for n, wm, dt, off in cases:
    x = rng.uniform(0, 8, n)
    with warnings.catch_warnings(record=True) as rec:
        warnings.simplefilter("always")
        w = T.metering_windows(x, wm, dt, off)
        nwin = T.metering_windows(np.zeros(n), wm, dt, off).size
        try:
            tp = TOP._window_peak(list(x), wm, dt)
        except Exception as e:
            tp = "raise " + type(e).__name__
    vals = [None if v != v else float(v) for v in np.asarray(w, dtype=float).ravel()]
    out.append({"case": [n, wm, dt, off], "len": int(np.asarray(w).size), "vals": vals,
                "nan": int(np.sum(np.isnan(np.asarray(w, dtype=float)))), "alias": bool(w is x),
                "n_windows": int(nwin), "topology_peak": tp,
                "warn": sum(1 for r in rec if issubclass(r.category, RuntimeWarning))})
print(json.dumps(out))
'''


def report(b, m):
    keys = ("len", "vals", "nan", "n_windows", "topology_peak")
    diff = [(rb["case"], {k: (rb[k], rm[k]) for k in keys if rb[k] != rm[k]}) for rb, rm in zip(b, m)
            if any(rb[k] != rm[k] for k in keys)]
    alias = sum(1 for rb, rm in zip(b, m) if rb["alias"] != rm["alias"])
    for case, d in diff[:12]:
        print("DIFF", case, d)
    print(f"RESULT inputs={len(b)} count")
    print(f"RESULT differing_value_or_length={len(diff)} count")
    print(f"RESULT n_peak_windows_differing={sum(1 for rb, rm in zip(b, m) if rb['n_windows'] != rm['n_windows'])} count")
    print(f"RESULT nan_windows_mutant={sum(r['nan'] for r in m)} count")
    print(f"RESULT nan_windows_baseline={sum(r['nan'] for r in b)} count")
    print(f"RESULT alias_differing={alias} count  (result is / is not the input array object; values equal)")
    print(f"RESULT runtime_warnings_baseline={sum(r['warn'] for r in b)} count")
    print(f"RESULT runtime_warnings_mutant={sum(r['warn'] for r in m)} count")
    return diff
