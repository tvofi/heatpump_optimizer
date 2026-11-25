#!/usr/bin/env python3
# Metric: over topk_search.py's fixed corpus (seed 20261125; families plateau, tieband, uniform, spread, tiny,
#   zero, negative, exacttie, stacked), the count of inputs whose _smooth_topk_sum_batch value (direct) or _plateau_aware_topk_sum_batch
#   value (the production caller, tau = _PEAK_SMOOTH_TAU) is not bit-identical between baseline and mutant, the max
#   |delta| (kW of billed top-k excess) on caller-reachable families, and RuntimeWarnings raised per arm.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_754e4cb5fa60e129.py
# EXPECTED RESULT lines: inputs=<n> count; differing_reachable_caller; differing_reachable_direct; differing_all_direct;
#   max_delta_reachable_caller kW; runtime_warnings_baseline/mutant; null_differing=0 count (baseline vs baseline).
# Tolerance: bit-exact comparison.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g40 (4 vCPU Intel Xeon @ 2.10GHz).
# Instrumented symbol: custom_components.heatpump_optimizer.tariff:_smooth_topk_sum_batch (tariff.py:821 `z = np.clip((x - mid[:, None]) / scale[:, None], -60.0, 60.0)`),
#   production caller tariff:_plateau_aware_topk_sum_batch.
# Perturbation: `z = np.clip((x - mid[:, None]) / scale[:, None], -60.0, 60.0)` -> `z = ((x - mid[:, None]) / scale[:, None])` (key 754e4cb5fa60e129), CLAMP_DROP: the bisection loop's logistic clip; applied in a temp copy of the baseline package (probe_lib).
# Null control: the baseline arm run twice (null_differing must be 0: the corpus and the comparison are deterministic).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import probe_lib, topk_search

if __name__ == "__main__":
    snip = topk_search.SNIP.replace("MODE", 'batch')
    b, m = probe_lib.two_arms(snip, 821, 'z = np.clip((x - mid[:, None]) / scale[:, None], -60.0, 60.0)', 'z = ((x - mid[:, None]) / scale[:, None])')
    for arm, r in (("baseline", b), ("mutant", m)):
        if isinstance(r, dict):
            print(f"RESULT {arm}_error=1 count  ({r})"); sys.exit(1)
    topk_search.report(b, m)
    with tempfile.TemporaryDirectory() as d:
        b2 = probe_lib.run(snip, probe_lib._arm(d))
    nd = sum(f["diff_direct"] + f["diff_caller"] for f in topk_search.compare(b, b2).values())
    print(f"RESULT null_differing={nd} count")
    probe_lib.machine_lines()
