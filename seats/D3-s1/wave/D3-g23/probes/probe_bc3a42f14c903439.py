#!/usr/bin/env python3
# Metric: DHW release list _safety_release_steps returns when the tank ends a forced-off step at exactly requirement - 0.5 (the tie).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g23/probes/probe_bc3a42f14c903439.py
# EXPECTED RESULT direct_tie_release_baseline=([],[])
# EXPECTED RESULT direct_tie_release_mutant=([],[0])
# EXPECTED RESULT null_off_tie_delta=0
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g23 cloud (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux),
#   run from a scratch baseline worktree while the box's full gate ran (counts exact; no timing is claimed).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._safety_release_steps, line 5250 (DHW breach bound).
# Perturbation: key bc3a42f14c903439, optimizer.py:5250 `if temp >= float(req[i]) - 0.5:` -> `if temp > float(req[i]) - 0.5:`, applied in memory
#   (_g23_common.mutated re-compiles HeatPumpOptimizer._safety_release_steps with the one line replaced and patches the class);
#   direction: a tank at exactly requirement-0.5 goes from safe to releasing the forced-off step.
# Null control: requirement-0.4 (neither releases) and requirement-0.6 (both release): both arms identical.
# Writes nothing. Helpers: _g23_common.py beside this file.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import _g23_common as c  # noqa: E402
NAN = c.NAN
MUT = ('_safety_release_steps', 'if temp >= float(req[i]) - 0.5:', 'if temp > float(req[i]) - 0.5:')
room = [20.0, 20.0]; floors = [19.0]
res = {}
for arm in ("baseline", "mutant"):
    with (c.mutated(*MUT) if arm == "mutant" else c.contextlib.nullcontext()):
        res[arm] = [c.release_direct(room, floors, dhw_traj=[50.0, t], dhw_req=[50.0], dhw_pins=[0.0])
                    for t in (50.0 - 0.5, 49.6, 49.4)]
print(f"RESULT direct_tie_release_baseline={c.fmt(res['baseline'][0])}")
print(f"RESULT direct_tie_release_mutant={c.fmt(res['mutant'][0])}")
print(f"RESULT null_off_tie_delta={int(res['baseline'][1:] != res['mutant'][1:])}")
c.tail()
