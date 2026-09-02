"""Verifier-3, D9-01 blast radius: which golden scenarios are on the scalar path,
and what does the proposed fix do to each of their fixtures?

Metric: per golden scenario, ``zero_range_bounds`` seen by
``optimizer._bounds_supported_by_batch`` during the capture, and
``fev_per_jev = nfev/njev`` from scipy's own counters (1.0 batched, n+1 scalar).
Pass 1 runs every scenario WITH the proposed fix (so the affected ones are
fast) and records which ones had a zero-range bound; pass 2 re-runs only those
WITHOUT the fix and diffs the two captured payloads field by field, at the
fixture's own stored precision (``golden.PRECISION`` = 6, compared exactly).

Command (from the repository root):
    PYTHONPATH=tests/hastub python tools/audit/round2/D9/v3_d901_golden_scan.py

Expected (baseline c398fc8): the CAP_SCENARIOS / ENVELOPE_CAP_SCENARIOS
fixtures are the ones with zero-range bounds; the fix takes them from the
scalar path to the batched one and moves their stored values by ~1e-5.

Instrumented symbols: optimizer:_bounds_supported_by_batch,
optimizer:_batch_fd_gradient, optimizer:_scoped_minimize.
Baseline c398fc84eec25fc44b60d74aae05b9a2da205884; Apple M1 8-core 8 GB.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round2", "D9"))
import d9lib  # noqa: E402

import numpy as np  # noqa: E402

from heatpump_optimizer import optimizer as opt_mod  # noqa: E402

sys.path.insert(0, os.path.join(os.getcwd(), "tests"))
import golden  # noqa: E402

C = {"zero": 0, "njev": 0, "nfev": 0, "gate_false": 0}

_orig_gate = opt_mod._bounds_supported_by_batch
_orig_bfd = opt_mod._batch_fd_gradient
_orig_scoped = opt_mod._scoped_minimize


def census(bounds):
    C["zero"] += sum(1 for lo, hi in bounds
                     if np.isfinite(lo) and np.isfinite(hi) and lo >= hi)


def hooked_scoped(*a, **k):
    res = _orig_scoped(*a, **k)
    C["njev"] += int(getattr(res, "njev", 0) or 0)
    C["nfev"] += int(getattr(res, "nfev", 0) or 0)
    return res


def gate_current(bounds):
    census(bounds)
    out = _orig_gate(bounds)
    if not out:
        C["gate_false"] += 1
    return out


def gate_fixed(bounds):
    census(bounds)
    if not bounds:
        C["gate_false"] += 1
        return False
    for lo, hi in bounds:
        if not (np.isfinite(lo) and np.isfinite(hi)) or lo > hi:
            C["gate_false"] += 1
            return False
    return True


def bfd_fixed(batch_objective, args, x0, f0, eps, bounds):
    lb = np.array([b[0] for b in bounds], dtype=float)
    ub = np.array([b[1] for b in bounds], dtype=float)
    free = lb < ub
    g = np.zeros_like(x0, dtype=float)
    if not free.any():
        return g
    with np.errstate(invalid="ignore", divide="ignore"):
        raw = _orig_bfd(batch_objective, args, x0, f0, eps, bounds)
    g[free] = raw[free]
    return g


opt_mod._scoped_minimize = hooked_scoped

NAMES = sorted(golden.SCENARIOS)
d9lib.result("scenarios", len(NAMES), "count")


def run(name, fixed):
    C.update(zero=0, njev=0, nfev=0, gate_false=0)
    opt_mod._bounds_supported_by_batch = gate_fixed if fixed else gate_current
    opt_mod._batch_fd_gradient = bfd_fixed if fixed else _orig_bfd
    try:
        payload = golden.capture(name, golden.SCENARIOS[name])
    finally:
        opt_mod._bounds_supported_by_batch = _orig_gate
        opt_mod._batch_fd_gradient = _orig_bfd
    return payload, dict(C)


affected = {}
for name in NAMES:
    payload, stats = run(name, fixed=True)
    if stats["zero"]:
        affected[name] = payload
    d9lib.result(f"scan.{name}.zero_range_bounds", stats["zero"], "count")

d9lib.result("scenarios_with_zero_range_bounds", len(affected), "count")
d9lib.result("affected_scenarios", ",".join(sorted(affected)) or "-", "labels")


def diff(a, b, path, out):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in a:
            diff(a[k], b.get(k), f"{path}.{k}", out)
        return
    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for i, (x, y) in enumerate(zip(a, b)):
            diff(x, y, f"{path}[{i}]", out)
        return
    if isinstance(a, float) and isinstance(b, float):
        if a != b:
            out.append((abs(a - b), path))
        return
    if a != b:
        out.append((float("inf"), path))


for name in sorted(affected):
    cur, stats_cur = run(name, fixed=False)
    fix = affected[name]
    njev = max(stats_cur["njev"], 1)
    d9lib.result(f"{name}.current_fev_per_jev", stats_cur["nfev"] / njev, "ratio")
    d9lib.result(f"{name}.current_path",
                 "scalar" if stats_cur["nfev"] / njev > 2.0 else "batched", "path")
    d9lib.result(f"{name}.current_gate_false", stats_cur["gate_false"], "count")
    out: list = []
    diff(cur, fix, name, out)
    d9lib.result(f"{name}.fields_changed_at_precision6", len(out), "count")
    if out:
        out.sort(reverse=True)
        d9lib.result(f"{name}.max_abs_delta", out[0][0], "unit")
        d9lib.result(f"{name}.max_delta_field", out[0][1], "label")
    d9lib.result(f"{name}.payload_identical", int(cur == fix), "bool")

d9lib.closing(1.0)
