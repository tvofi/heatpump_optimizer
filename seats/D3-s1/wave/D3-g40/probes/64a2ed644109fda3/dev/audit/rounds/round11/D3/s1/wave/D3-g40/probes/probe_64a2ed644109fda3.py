#!/usr/bin/env python3
# Metric: over metering_search.py's fixed corpus (lengths 0..96 x window/step pairs x offsets), the count of
#   inputs whose metering_windows output (length or bit-exact values, nan == nan), Optimizer._n_peak_windows'
#   window count expression, or topology._window_peak differs between baseline and mutant; nan windows per arm;
#   result-aliases-input differences; RuntimeWarnings per arm.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_64a2ed644109fda3.py
# EXPECTED RESULT lines: inputs, differing_value_or_length, n_peak_windows_differing, nan_windows_mutant/baseline,
#   alias_differing, runtime_warnings_baseline/mutant, null_differing=0 count.
# Tolerance: bit-exact.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g40 (4 vCPU Intel Xeon @ 2.10GHz).
# Instrumented symbol: custom_components.heatpump_optimizer.tariff:metering_windows (tariff.py:573 `if per_window <= 1:`),
#   callers optimizer.Optimizer._n_peak_windows (optimizer.py:4163), topology._window_peak (topology.py:845).
# Perturbation: `if per_window <= 1:` -> `if False:` (key 64a2ed644109fda3), GUARD_OFF: per_window is max(1, ...) so this is the per_window == 1 case again; applied in a temp copy of the baseline package (probe_lib).
# Null control: the baseline arm run twice (null_differing must be 0).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import probe_lib, metering_search

if __name__ == "__main__":
    b, m = probe_lib.two_arms(metering_search.SNIP, 573, 'if per_window <= 1:', 'if False:')
    for arm, r in (("baseline", b), ("mutant", m)):
        if isinstance(r, dict):
            print(f"RESULT {arm}_error=1 count  ({r})"); sys.exit(1)
    metering_search.report(b, m)
    with tempfile.TemporaryDirectory() as d:
        b2 = probe_lib.run(metering_search.SNIP, probe_lib._arm(d))
    print(f"RESULT null_differing={sum(1 for x, y in zip(b, b2) if x != y)} count")
    probe_lib.machine_lines()
