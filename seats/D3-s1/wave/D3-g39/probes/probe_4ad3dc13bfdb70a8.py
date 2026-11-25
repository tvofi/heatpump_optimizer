#!/usr/bin/env python3
# Box D3-g39 step-4 probe for mutant 4ad3dc13bfdb70a8 (tariff.py:465 CMP_BOUND).
# Metric: PeakTracker.from_dict of a mid-window payload whose window_factor is 0.0 (what sample_factor returns in a masked month): restored window state, and peaks after the next window closes it.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g39/probes/probe_4ad3dc13bfdb70a8.py
#   (run from a baseline worktree at the SHA below, never the gate's tree while a gate runs)
# EXPECTED RESULT f0_state baseline keeps the window (factor 0.0), mutant restarts it empty with a warning; f0_peaks equal both arms (a factor-0 window contributes nothing)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g39 (4 vCPU Intel Xeon @ 2.30GHz, 16 GB); provisional.
# Instrumented symbol: custom_components.heatpump_optimizer.tariff:PeakTracker.from_dict (line 465).
# Perturbation: '            or not 0.0 <= tracker._window_factor <= 1.0' -> '            or not 0.0 < tracker._window_factor <= 1.0', applied in memory to a sibling copy of the module
#   (_mutload.load; the file on disk is not written). Direction: factor == 0.0: window kept -> window discarded and a 'outside what the tracker writes' warning logged.
# Null control: window_factor 1.0, 0.5 and -0.1 (both arms agree).
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _mutload import load, arm  # noqa: E402
import math  # noqa: E402,F401
from datetime import datetime  # noqa: E402,F401
import numpy as np  # noqa: E402,F401

OLD = '            or not 0.0 <= tracker._window_factor <= 1.0'
NEW = '            or not 0.0 < tracker._window_factor <= 1.0'
B, M, LINE = load('tariff', OLD, NEW, 465)


def show(v):
    if isinstance(v, float):
        return repr(v)
    return str(v)


T = None
def restore(m, factor, wsum=2.0, samples=1):
    d = {"month": "2026-01", "peaks": [1.0], "peak_days": ["2026-01-05"],
         "window_key": "2026-01-10T07:00:00|60", "window_sum": wsum,
         "window_samples": samples, "window_factor": factor}
    return m.PeakTracker.from_dict(d)
def state(m, factor):
    t = restore(m, factor)
    return (t._window_key, t._window_sum, t._window_samples, t._window_factor)
def peaks_after_close(m, factor):
    t = restore(m, factor)
    tar = m.CapacityTariff(enabled=True, price_per_kw=50.0, peaks_averaged=3)
    t.observe(datetime(2026, 1, 10, 9, 0), 0.5, tar)  # a later window closes the restored one
    return tuple(round(p, 6) for p in t.peaks)
CASES = [
    ("f0_state", lambda m: state(m, 0.0), False),
    ("f0_peaks", lambda m: peaks_after_close(m, 0.0), False),
    ("f1_state", lambda m: state(m, 1.0), True),
    ("f05_state", lambda m: state(m, 0.5), True),
    ("fneg_state", lambda m: state(m, -0.1), True),
]

moved = 0
nulls_moved = 0
for label, fn, is_null in CASES:
    b, m = show(arm(fn, B)), show(arm(fn, M))
    print(f"RESULT {label}_baseline={b}")
    print(f"RESULT {label}_mutant={m}")
    if b != m and is_null is not None:
        if is_null:
            nulls_moved += 1
        else:
            moved += 1
print(f"RESULT cases_moved={moved}")
print(f"RESULT null_cases_moved={nulls_moved}")
