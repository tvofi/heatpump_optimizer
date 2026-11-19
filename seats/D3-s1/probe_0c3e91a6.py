#!/usr/bin/env python3
# Metric: learned FlowCurveBias.bias_k (K) after 5 warm-up residuals of +2 K then 5 residuals of +6 K (curve 25 C).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/probe_0c3e91a6.py
# EXPECTED RESULT bias_baseline=3.638040 K
# EXPECTED RESULT bias_mutant=4.689280 K
# EXPECTED RESULT delta=1.051240 K
# EXPECTED RESULT null_delta=0.0 K  (warm-up only: alpha unread while samples < FLOW_BIAS_MIN_SAMPLES)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-rem (4 vCPU Xeon @ 2.10GHz).
# Instrumented symbol: flow_lift:FlowCurveBias.observe, line 194-195 reading FLOW_BIAS_ALPHA (constant at line 47).
#   FLOW_BIAS_ALPHA is read as a module global at call time; no other module imports it (grep), so one
#   mock.patch.object(flow_lift, "FLOW_BIAS_ALPHA", 0.2) covers every production binding.
# Perturbation: 0.1 -> 0.2 applied in memory; bias moves up (more weight on the +6 K residuals).
# Null control: 5-sample warm-up only, plain-mean branch, alpha unused.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT))
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import flow_lift as fl  # noqa: E402


def mutant_observe(old, new):
    src = textwrap.dedent(inspect.getsource(fl.FlowCurveBias.observe))
    old = textwrap.dedent(old + "\n    pass").splitlines()[0]
    new = textwrap.dedent(new + "\n    pass").splitlines()[0]
    assert src.count(old) == 1, "anchor line moved"
    ns = dict(fl.__dict__)
    exec(compile(src.replace(old, new, 1), fl.__file__, "exec"), ns)
    return ns["observe"]


def run(seq, mutant=None):
    b = fl.FlowCurveBias()
    ctx = mock.patch.object(fl.FlowCurveBias, "observe", mutant) if mutant else mock.MagicMock()
    with ctx:
        for m, c in seq:
            b.observe(m, c)
    return b

SEQ = [(27.0, 25.0)] * fl.FLOW_BIAS_MIN_SAMPLES + [(31.0, 25.0)] * 5
WARM = SEQ[: fl.FLOW_BIAS_MIN_SAMPLES]
base = run(SEQ).bias_k
nb = run(WARM).bias_k
with mock.patch.object(fl, "FLOW_BIAS_ALPHA", 0.2):
    mut = run(SEQ).bias_k
    nm = run(WARM).bias_k
print(f"RESULT bias_baseline={base:.6f} K")
print(f"RESULT bias_mutant={mut:.6f} K")
print(f"RESULT delta={mut - base:.6f} K")
print(f"RESULT null_delta={nm - nb} K")
