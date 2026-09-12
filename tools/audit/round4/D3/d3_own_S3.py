#!/usr/bin/env python3
"""Verifiers' own harness for D3-S3 (verifier seat 1 of panel D3-0, round 4).

FINDING: tariff.py:507 `k = max(1, min(int(k), x.size))` in
_smooth_topk_sum replaced by `pass`. Claimed: a no-op on the one fixture that
calls it directly (features.py:1277, k=3 over 5 values) and equivalent
through the only production caller (tariff.py:600 inside peak_cost, which
pre-clamps k with the same expression at tariff.py:598 before calling).

METRIC: (a) direct probe on three inputs — the suite's own fixture shape
(k=3, 5 values), a k>size call (k=8, 5 values) no test makes, and the
production path peak_cost(peaks_averaged=8 over a 3-window excess) — each as
|base - mutant|; (b) kill rule — tests/features.py (the only script that
greps for _smooth_topk_sum) and tests/entities.py (greps peak_cost) against
a passing baseline arm on the same tree.

RUN (from this worktree's root; mutates ONLY ../audit-r4-verify-D3-1-scratch):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D3/d3_own_S3.py

EXPECTED: fixture-path diff 0.0, k>size diff > 0 (the clamp is live code the
suite never calls), peak_cost-path diff 0.0; killed_by=none.
BASELINE: measured against worktree HEAD 0855277 (finder used 7dd68dd)
MACHINE: 8-core Apple M1, macOS 25.6.0, python 3.11
"""
from __future__ import annotations

import sys

sys.path.insert(0, "tools/audit/round4/D3")
from d3_own_common import (arms, heavy_neighbours, load1, swapins,
                           thread_factor)

REL = "custom_components/heatpump_optimizer/tariff.py"
LINE, OLD, NEW = 507, "k = max(1, min(int(k), x.size))", "pass"

PROBE = r"""
import json
import numpy as np
from custom_components.heatpump_optimizer.tariff import (
    _smooth_topk_sum, peak_cost,
)

tie = np.array([20.0, 20.0, 20.0, 5.0, 1.0])          # features.py:1276 shape
plateau = np.array([3.0, 3.0, 3.0, 3.0, 3.0])          # forces the smooth path
out = {
    "fixture_k3_n5": _smooth_topk_sum(tie, 3, 0.05),
    "k_gt_size_8n5": _smooth_topk_sum(plateau, 8, 0.05),
    "k_gt_size_7n5": _smooth_topk_sum(plateau, 7, 0.05),
    "k_gt_size_tie8n5": _smooth_topk_sum(tie, 8, 0.05),
    # the production path: peak_cost pre-clamps k (tariff.py:598) before the
    # call, so the deleted line cannot move through it. Second variant has
    # fewer windows than peaks_averaged so the CALLER's clamp binds.
    "peakcost_path_k8": peak_cost(
        np.full(12, 4.0), np.zeros(12), 2.0, 60.0, 60, 1.0,
        peaks_averaged=8,
    ),
    "peakcost_path_short": peak_cost(
        np.full(4, 4.0), np.zeros(4), 2.0, 60.0, 60, 1.0,
        peaks_averaged=8,
    ),
}
print(json.dumps(out))
"""


def main() -> int:
    print(f"D3-S3 own harness — mutant {REL}:{LINE} {OLD!r} -> {NEW!r}")
    print(f"heavy neighbours (stress.py/run.sh procs): {heavy_neighbours()}")
    out = arms(
        REL, LINE, OLD, NEW,
        scripts=["tests/features.py", "tests/entities.py"],
        finding="S3",
        probes={"code": PROBE},
    )
    b = out["probes"]["base"]["value"]
    m = out["probes"]["mut"]["value"]
    diffs = {k: abs(b[k] - m[k]) for k in b}
    for script, rec in out["scripts"].items():
        base, mut = rec["base"], rec["mut"]
        if mut is None:
            print(f"RESULT S3_{script.replace('/', '_')}_verdict=void")
            continue
        print(f"RESULT S3_{script.replace('/', '_')}_rc={base['rc']}->{mut['rc']} delta_rc")
        print(f"RESULT S3_{script.replace('/', '_')}_failed={base['failed']}->{mut['failed']} count")
    print(f"RESULT S3_fixture_path_diff={diffs['fixture_k3_n5']:.6g} currency")
    print(f"RESULT S3_k_gt_size_diff={max(diffs['k_gt_size_8n5'], diffs['k_gt_size_7n5'], diffs['k_gt_size_tie8n5']):.6g} currency")
    print(f"RESULT S3_peakcost_path_diff={diffs['peakcost_path_k8']:.6g} currency")
    print(f"RESULT S3_clamp_is_live_code={max(diffs['k_gt_size_8n5'], diffs['k_gt_size_7n5'], diffs['k_gt_size_tie8n5']) > 1e-9} bool")
    print(f"RESULT S3_killed_by={out['killed_by'] or 'none'} script")
    print(f"RESULT thread_factor={thread_factor()}")
    print(f"RESULT load1={load1():.2f}")
    print(f"RESULT swapins={swapins()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
