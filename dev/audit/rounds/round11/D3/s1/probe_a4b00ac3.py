#!/usr/bin/env python3
# Metric: cold-water inlet temperature (C) ThermalParameters.seasonal_inlet_temp returns when the seasonal
#   amplitude (swing) is exactly 0.0, over every day of the year. EQUIVALENT-MUTANT probe.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/probe_a4b00ac3.py
# EXPECTED RESULT max_abs_delta_swing0=0.0 C  (over day 1..366 and inlet means 4, 10, 15 C)
# EXPECTED RESULT null_delta_swing3=0.0 C  (swing>0: guard false in both arms)
# EXPECTED RESULT null_delta_swing_negative=0.0 C  (swing<0: guard true in both arms)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-rem (4 vCPU Xeon @ 2.10GHz).
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:ThermalParameters.seasonal_inlet_temp,
#   line 835 `if swing <= 0.0:`.
# Perturbation: key a4b00ac3ca662eec, `<= 0.0` -> `< 0.0`, in memory (method re-compiled, patched on the class for
#   the mutant arm). Only swing == 0.0 changes arm; there the fall-through returns
#   dhw_inlet_temp - 0.0*cos(phase) == dhw_inlet_temp exactly (cos is finite on finite day_of_year), so the
#   outputs are bit-identical: equivalent mutant. Direction: none (delta 0).
# Null control: swing = 3.0 and swing = -2.0, where the guard has the same value in both arms.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import dataclasses, inspect, sys, textwrap
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
from custom_components.heatpump_optimizer import thermal_model as tm  # noqa: E402

cls = tm.ThermalParameters
src = textwrap.dedent(inspect.getsource(cls.seasonal_inlet_temp))
assert src.count("    if swing <= 0.0:") == 1, "anchor moved"
ns = dict(tm.__dict__)
exec(compile(src.replace("    if swing <= 0.0:", "    if swing < 0.0:", 1), tm.__file__, "exec"), ns)
mut = ns["seasonal_inlet_temp"]
base_fn = cls.seasonal_inlet_temp


def worst(swing):
    d = 0.0
    for mean in (4.0, 10.0, 15.0):
        p = dataclasses.replace(cls(), dhw_inlet_temp=mean, dhw_inlet_seasonal_amplitude=swing)
        for day in range(1, 367):
            b = p.seasonal_inlet_temp(day)
            with mock.patch.object(cls, "seasonal_inlet_temp", mut):
                m = p.seasonal_inlet_temp(day)
            d = max(d, abs(b - m))
    return d


print(f"RESULT max_abs_delta_swing0={worst(0.0)} C")
print(f"RESULT null_delta_swing3={worst(3.0)} C")
print(f"RESULT null_delta_swing_negative={worst(-2.0)} C")
