#!/usr/bin/env python3
# Metric: FlowCurveBias.bias_k and .samples after observe(NaN, 25.0) on a seeded bias (3 samples of +2 K).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/probe_3885e472.py
# EXPECTED RESULT bias_baseline=2.0 K
# EXPECTED RESULT bias_mutant=nan K
# EXPECTED RESULT samples_baseline=3 count
# EXPECTED RESULT samples_mutant=4 count
# EXPECTED RESULT null_delta=0.0 K  (finite input: the guard is false either way)
# EXPECTED RESULT reach_nonfinite_supply_after_observe_temps=0 count  (see below)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-rem (4 vCPU Xeon @ 2.10GHz).
# Instrumented symbol: flow_lift:FlowCurveBias.observe, line 183 (non-finite guard).
# Perturbation: guard replaced by "if False:" in memory; NaN poisons bias_k (NaN passes "> FLOW_SUPPLY_MAX_C"
#   false, np.clip keeps NaN) and samples still increments. Direction: bias_k finite -> NaN.
# Reachability: the only production caller is coordinator.py:986 (coord._flow_bias.observe(supply, curve)),
#   supply from observe_temps (flow_lift.py:169-173, drops non-finite to None, coordinator.py:965 returns on None)
#   and curve from curve_supply_temp (flow_lift.py:117, None on non-finite, coordinator.py ~985 returns on None).
#   So the guard is defence in depth upstream-covered: unreachable via production.
# Null control: finite (27.0, 25.0) input.
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

SEQ = [(27.0, 25.0)] * 3
mut_fn = mutant_observe("        if not np.isfinite(measured_supply) or not np.isfinite(curve_supply):", "        if False:")
nan = float("nan")
b0 = run(SEQ + [(nan, 25.0)])
m0 = run(SEQ + [(nan, 25.0)], mut_fn)
nb = run(SEQ + [(29.0, 25.0)]).bias_k
nm = run(SEQ + [(29.0, 25.0)], mut_fn).bias_k
t = fl.FlowCurveBias()
t.observe_temps(nan, 20.0)
print(f"RESULT bias_baseline={b0.bias_k} K")
print(f"RESULT bias_mutant={m0.bias_k} K")
print(f"RESULT samples_baseline={b0.samples} count")
print(f"RESULT samples_mutant={m0.samples} count")
print(f"RESULT null_delta={nm - nb} K")
print(f"RESULT reach_nonfinite_supply_after_observe_temps={0 if t.last_supply_c is None else 1} count")
