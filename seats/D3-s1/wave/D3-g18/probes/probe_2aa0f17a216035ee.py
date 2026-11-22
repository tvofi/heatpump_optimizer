#!/usr/bin/env python3
# Metric: FlowCurveBias.bias_k (K) after five residuals of +2 K then one of +12 K (curve 25 C), folded through
#   flow_lift:FlowCurveBias.observe (the sixth fold is the first one past the warm-up boundary).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_2aa0f17a216035ee.py
# EXPECTED RESULT bias_baseline=3.000000 K  (6th fold is the EWMA: 0.9*2 + 0.1*12)
# EXPECTED RESULT bias_mutant=3.666667 K    (FLOW_BIAS_MIN_SAMPLES=10: still the plain mean (5*2+12)/6)
# EXPECTED RESULT delta=0.666667 K
# EXPECTED RESULT null_delta=0.000000 K     (three folds: both arms are inside the plain-mean warm-up)
# EXPECTED RESULT folds_until_arms_agree_never=1 count  (bias after 40 folds of the same stream still differs)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g18 (4 vCPU Intel Xeon @ 2.10GHz, Linux).
# Instrumented symbol: heatpump_optimizer.flow_lift:FlowCurveBias.observe, which reads the module constant
#   FLOW_BIAS_MIN_SAMPLES (flow_lift.py:51) at line 188.
# Perturbation: mutant 2aa0f17a216035ee, FLOW_BIAS_MIN_SAMPLES = 5 -> 10, applied in memory with
#   mock.patch.object(flow_lift, "FLOW_BIAS_MIN_SAMPLES", 10); direction: the 6th..10th folds stay a plain mean, so
#   an outlier late in the warm-up moves the bias up by 0.67 K instead of 0.1*10 K.
# Null control: a stream of three folds, inside both warm-ups, where the constant cannot matter.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
from pathlib import Path


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "custom_components"))
from unittest import mock  # noqa: E402

from heatpump_optimizer import flow_lift as fl  # noqa: E402


def fold(seq, mutant):
    ctx = mock.patch.object(fl, "FLOW_BIAS_MIN_SAMPLES", 10) if mutant else mock.MagicMock()
    b = fl.FlowCurveBias()
    with ctx:
        for m, c in seq:
            b.observe(m, c)
    return b.bias_k


SEQ = [(27.0, 25.0)] * 5 + [(37.0, 25.0)]
base, mut = fold(SEQ, False), fold(SEQ, True)
null = [(27.0, 25.0)] * 2 + [(37.0, 25.0)]
long = SEQ + [(27.0, 25.0)] * 34
print(f"RESULT bias_baseline={base:.6f} K")
print(f"RESULT bias_mutant={mut:.6f} K")
print(f"RESULT delta={mut - base:.6f} K")
print(f"RESULT null_delta={abs(fold(null, True) - fold(null, False)):.6f} K")
print(f"RESULT folds_until_arms_agree_never={int(fold(long, True) != fold(long, False))} count")

import resource as _resource  # noqa: E402
import time as _time  # noqa: E402

print(f"RESULT thread_factor={_time.process_time() / max(_time.thread_time(), 1e-9):.3f} ratio")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print(f"RESULT swapins={_resource.getrusage(_resource.RUSAGE_SELF).ru_nswap} count")
