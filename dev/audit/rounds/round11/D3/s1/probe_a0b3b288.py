#!/usr/bin/env python3
# Metric: bias_k after FLOW_BIAS_MIN_SAMPLES (=5) residuals of +2 K then one residual of +12 K (the sample with
#   samples == FLOW_BIAS_MIN_SAMPLES on entry), curve 25 C.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/probe_a0b3b288.py
# EXPECTED RESULT bias_baseline=3.0 K  (EWMA: 0.9*2 + 0.1*12)
# EXPECTED RESULT bias_mutant=3.666667 K  (plain mean: (5*2 + 12)/6)
# EXPECTED RESULT delta=0.666667 K
# EXPECTED RESULT null_delta=0.0 K  (samples=2 and samples=8: both arms agree)
# EXPECTED RESULT reach_samples_eq_min=1 count
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-rem (4 vCPU Xeon @ 2.10GHz).
# Instrumented symbol: flow_lift:FlowCurveBias.observe, line 188 (< -> <=).
# Perturbation: in memory; the 6th sample is folded as a plain mean instead of EWMA; bias_k moves up.
# Reachability: every install folding >5 samples through coordinator.py:986 passes samples==5 once; the count
#   below is how many calls enter observe with samples==5 over 20 folds.
# Null control: samples=2 and samples=8 entry states.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap
from pathlib import Path
from unittest import mock

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

mut_fn = mutant_observe("        if self.samples < FLOW_BIAS_MIN_SAMPLES:", "        if self.samples <= FLOW_BIAS_MIN_SAMPLES:")
SEQ = [(27.0, 25.0)] * fl.FLOW_BIAS_MIN_SAMPLES + [(37.0, 25.0)]
base = run(SEQ).bias_k
mut = run(SEQ, mut_fn).bias_k
nd = max(abs(run(s, mut_fn).bias_k - run(s).bias_k) for s in ([(27.0, 25.0)] * 2 + [(37.0, 25.0)], [(27.0, 25.0)] * 8 + [(37.0, 25.0)]))
hits = []
real = fl.FlowCurveBias.observe
def spy(self, m, c):
    hits.append(self.samples)
    return real(self, m, c)
b = fl.FlowCurveBias()
with mock.patch.object(fl.FlowCurveBias, "observe", spy):
    for _ in range(20):
        b.observe(27.0, 25.0)
print(f"RESULT bias_baseline={base:.6f} K")
print(f"RESULT bias_mutant={mut:.6f} K")
print(f"RESULT delta={mut - base:.6f} K")
print(f"RESULT null_delta={nd} K")
print(f"RESULT reach_samples_eq_min={sum(1 for s in hits if s == fl.FLOW_BIAS_MIN_SAMPLES)} count")
