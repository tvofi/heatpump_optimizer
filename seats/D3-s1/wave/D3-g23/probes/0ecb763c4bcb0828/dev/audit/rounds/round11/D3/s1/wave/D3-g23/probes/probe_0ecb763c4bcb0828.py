#!/usr/bin/env python3
# Metric: space release list _safety_release_steps returns when a free step after a forced-off step ends at exactly floor - 0.25 (the tie).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g23/probes/probe_0ecb763c4bcb0828.py
# EXPECTED RESULT direct_tie_release_baseline=([],[])
# EXPECTED RESULT direct_tie_release_mutant=([0],[])
# EXPECTED RESULT null_off_tie_delta=0
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g23 cloud (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux),
#   run from a scratch baseline worktree while the box's full gate ran (counts exact; no timing is claimed).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._safety_release_steps, line 5237 (free-step breach bound).
# Perturbation: key 0ecb763c4bcb0828, optimizer.py:5237 `breach = temp < floor - 0.25` -> `breach = temp <= floor - 0.25`, applied in memory
#   (_g23_common.mutated re-compiles HeatPumpOptimizer._safety_release_steps with the one line replaced and patches the class);
#   direction: a free step at exactly floor-0.25 goes from no breach to releasing the preceding off block.
# Null control: floor-0.30 (both breach) and floor-0.20 (neither): both arms identical.
# Writes nothing. Helpers: _g23_common.py beside this file.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import _g23_common as c  # noqa: E402
NAN = c.NAN
MUT = ('_safety_release_steps', 'breach = temp < floor - 0.25', 'breach = temp <= floor - 0.25')
floors = [19.0, 19.0]
tie = 19.0 - 0.25
res = {}
for arm in ("baseline", "mutant"):
    with (c.mutated(*MUT) if arm == "mutant" else c.contextlib.nullcontext()):
        res[arm] = [c.release_direct([20.0, 20.0, t], floors, space_pins=[0.0, NAN]) for t in (tie, 18.7, 18.8)]
print(f"RESULT direct_tie_release_baseline={c.fmt(res['baseline'][0])}")
print(f"RESULT direct_tie_release_mutant={c.fmt(res['mutant'][0])}")
print(f"RESULT null_off_tie_delta={int(res['baseline'][1:] != res['mutant'][1:])}")
c.tail()
