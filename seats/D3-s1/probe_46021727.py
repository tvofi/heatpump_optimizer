#!/usr/bin/env python3
# Metric: slab_mode_tau_fast(c_r, c_s, k_s) in hours (baseline 0.0 on unset/degenerate constants), over the
#   boundary inputs where one constant is <= 1e-9, and how many production callers can pass such an input.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/probe_46021727.py
# EXPECTED RESULT tau_k_tiny_baseline=0.0 h   (k_s=5e-10, c_r=10, c_s=20)
# EXPECTED RESULT tau_k_tiny_mutant=1.333333e+10 h
# EXPECTED RESULT tau_k_zero_baseline=0.0 h   (k_s=0)
# EXPECTED RESULT tau_k_zero_mutant=ZeroDivisionError
# EXPECTED RESULT tau_cr_neg_baseline=0.0 h   (c_r=-1, c_s=2, k_s=1)
# EXPECTED RESULT tau_cr_neg_mutant=-2.0 h
# EXPECTED RESULT tau_cr_zero_delta=0.0 h     (c_r=0 and c_s=0: the mutant also returns 0.0 -- inert there)
# EXPECTED RESULT null_delta=0.0 h            (c_r=10, c_s=20, k_s=1: guard false either way)
# EXPECTED RESULT reach_callers_with_degenerate=SEE_OUTPUT count
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-rem (4 vCPU Xeon @ 2.10GHz).
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:slab_mode_tau_fast (line 610
#   `    if not (c_r > 1e-9 and c_s > 1e-9 and k_s > 1e-9):`), called at sysid.py:682
#   (slab_mode_identifiability, config plant) and sysid.py:2441 (fitted two-state result).
# Perturbation: line 610 -> `    if False:` (GUARD_OFF 460217277822d5bd), in memory (function recompiled from its own
#   source; mutant arm calls the recompiled function directly). Direction: 0.0 -> huge/negative/ZeroDivisionError
#   for k_s<=1e-9 or negative c; unchanged for c_r=0 or c_s=0 (numerator zero).
# Reach: slab_mode_identifiability(params, config) is driven with params whose slab_heat_transfer is 0 (the
#   unset config the docstring names); the baseline gate must refuse it (see sysid.py:682-690) and the
#   mutant is observed through the same entry point with slab_mode_tau_fast patched to the mutant.
# Null control: positive constants, where the guard is false either way.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT))
from custom_components.heatpump_optimizer import sysid  # noqa: E402

OLD = "    if not (c_r > 1e-9 and c_s > 1e-9 and k_s > 1e-9):"
NEW = "    if False:"


def mutant_fn():
    src = textwrap.dedent(inspect.getsource(sysid.slab_mode_tau_fast))
    old, new = OLD.strip(), NEW.strip()
    assert src.count(old) == 1, "anchor line moved"
    ns = dict(sysid.__dict__)
    exec(compile(src.replace(old, new, 1), sysid.__file__, "exec"), ns)
    return ns["slab_mode_tau_fast"]


def run(fn, *a):
    try:
        return fn(*a)
    except Exception as exc:
        return type(exc).__name__


mut = mutant_fn()
base = sysid.slab_mode_tau_fast
for name, args in (("k_tiny", (10.0, 20.0, 5e-10)), ("k_zero", (10.0, 20.0, 0.0)), ("cr_neg", (-1.0, 2.0, 1.0))):
    print(f"RESULT tau_{name}_baseline={run(base, *args)} h")
    print(f"RESULT tau_{name}_mutant={run(mut, *args)} h")
zd = max(abs(run(mut, *a) - run(base, *a)) for a in ((0.0, 20.0, 1.0), (10.0, 0.0, 1.0)))
print(f"RESULT tau_cr_zero_delta={zd} h")
print(f"RESULT null_delta={abs(run(mut, 10.0, 20.0, 1.0) - run(base, 10.0, 20.0, 1.0))} h")

# Reach: the production gate with an unset slab pair.
try:
    from custom_components.heatpump_optimizer.thermal_model import ThermalParameters
    params = ThermalParameters(slab_heat_transfer=0.0)
    cfg = sysid.SysIdConfig()
    seen = []
    real = sysid.slab_mode_tau_fast

    def spy(c_r, c_s, k_s):
        seen.append((c_r, c_s, k_s))
        return real(c_r, c_s, k_s)

    with mock.patch.object(sysid, "slab_mode_tau_fast", spy):
        verdict_b = sysid.slab_mode_identifiability(params, cfg)
    degenerate = sum(1 for t in seen if not all(v > 1e-9 for v in t))
    print(f"RESULT reach_callers_with_degenerate={degenerate} count")
    print(f"RESULT reach_gate_verdict_baseline={verdict_b}")
    with mock.patch.object(sysid, "slab_mode_tau_fast", mut):
        print(f"RESULT reach_gate_verdict_mutant={run(sysid.slab_mode_identifiability, params, cfg)}")
except Exception as exc:
    print(f"RESULT reach_drive_error={type(exc).__name__}: {str(exc)[:160]}")
