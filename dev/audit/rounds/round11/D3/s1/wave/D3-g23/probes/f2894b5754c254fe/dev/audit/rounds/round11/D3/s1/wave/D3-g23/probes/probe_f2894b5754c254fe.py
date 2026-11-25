#!/usr/bin/env python3
# Metric: what _safety_release_steps returns when the DHW requirement is shorter than the DHW schedule; and how many real manual-plan release calls ever carry such a requirement.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g23/probes/probe_f2894b5754c254fe.py
# EXPECTED RESULT direct_short_req_baseline=([],[])
# EXPECTED RESULT direct_short_req_mutant=IndexError
# EXPECTED RESULT null_full_req_delta=0
# EXPECTED RESULT reach_short_requirement_calls=0 of 11 (over 7 manual-plan solves)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g23 cloud (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux),
#   run from a scratch baseline worktree while the box's full gate ran (counts exact; no timing is claimed).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._safety_release_steps, line 5248 (DHW loop bound).
# Perturbation: key f2894b5754c254fe, optimizer.py:5248 `for i in range(min(len(result.dhw_power_schedule), len(req))):` -> `for i in range((len(result.dhw_power_schedule))):`, applied in memory
#   (_g23_common.mutated re-compiles HeatPumpOptimizer._safety_release_steps with the one line replaced and patches the class);
#   direction: a short requirement goes from a truncated loop to IndexError.
# Null control: requirement as long as the schedule: both arms identical.
# Writes nothing. Helpers: _g23_common.py beside this file.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import _g23_common as c  # noqa: E402
NAN = c.NAN
MUT = ('_safety_release_steps', 'for i in range(min(len(result.dhw_power_schedule), len(req))):', 'for i in range((len(result.dhw_power_schedule))):')
room = [20.0] * 5; floors = [19.0] * 4
traj = [50.0, 50.0, 50.0, 50.0, 50.0]
res = {}
for arm in ("baseline", "mutant"):
    with (c.mutated(*MUT) if arm == "mutant" else c.contextlib.nullcontext()):
        res[arm] = (c.release_direct(room, floors, dhw_traj=traj, dhw_req=[45.0, 45.0], dhw_pins=[0.0] * 4),
                    c.release_direct(room, floors, dhw_traj=traj, dhw_req=[45.0] * 4, dhw_pins=[0.0] * 4))
print(f"RESULT direct_short_req_baseline={c.fmt(res['baseline'][0])}")
print(f"RESULT direct_short_req_mutant={c.fmt(res['mutant'][0])}")
print(f"RESULT null_full_req_delta={int(res['baseline'][1] != res['mutant'][1])}")
with c.Spy("_safety_release_steps", lambda self, r, t, sp, dp: dp is not None and self._dhw_requirement is not None
           and len(self._dhw_requirement) < len(r.dhw_power_schedule)) as spy:
    n = c.reach_solves()
print(f"RESULT reach_short_requirement_calls={spy.hits} of {spy.calls} (over {n} manual-plan solves)")
c.tail()
