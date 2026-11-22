#!/usr/bin/env python3
# Metric: steps optimize() releases (result.manual_released_space) for a winter_extreme house starting at 16.9 C with only step 0 forced off.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g23/probes/probe_856aa341a89a6ab0.py
# EXPECTED RESULT released_space_baseline=[0]
# EXPECTED RESULT released_space_mutant=[]
# EXPECTED RESULT space_kwh_first_hour_baseline=4.8809 mutant=4.5000
# EXPECTED RESULT null_block_delta=0
# EXPECTED RESULT direct_breach_after_step0_off_baseline=([0],[]) mutant=([],[])
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g23 cloud (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux),
#   run from a scratch baseline worktree while the box's full gate ran (counts exact; no timing is claimed).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._safety_release_steps._preceding_off, line 5211 (the backward walk's lower bound).
# Perturbation: key 856aa341a89a6ab0, optimizer.py:5211 `while j >= 0:` -> `while j > 0:`, applied in memory
#   (_g23_common.mutated re-compiles HeatPumpOptimizer._safety_release_steps with the one line replaced and patches the class);
#   direction: a breach whose only preceding forced-off step is step 0 goes from releasing step 0 to releasing nothing.
# Null control: the same solve with steps 0-3 forced off (the walk finds step >= 1 first): both arms identical.
# Writes nothing. Helpers: _g23_common.py beside this file.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import _g23_common as c  # noqa: E402
NAN = c.NAN
MUT = ('_safety_release_steps', 'while j >= 0:', 'while j > 0:')
b = c.build("winter_extreme", "winter_cold", room_temperature=16.9, slab_temperature=16.9)
only0 = c.pins(c.N, (0, 1, 0.0)); block = c.pins(c.N, (0, 4, 0.0))
base = c.solve(b, space_pins=only0.copy()); base_null = c.plan_signature(c.solve(b, space_pins=block.copy()))
with c.mutated(*MUT):
    mut = c.solve(b, space_pins=only0.copy()); mut_null = c.plan_signature(c.solve(b, space_pins=block.copy()))
print(f"RESULT released_space_baseline={c.fmt(sorted(base.manual_released_space))}")
print(f"RESULT released_space_mutant={c.fmt(sorted(mut.manual_released_space))}")
print(f"RESULT space_kwh_first_hour_baseline={sum(base.power_schedule[:4]) * 0.25:.4f} mutant={sum(mut.power_schedule[:4]) * 0.25:.4f}")
print(f"RESULT null_block_delta={int(base_null != mut_null)}")
res = {}
for arm in ("baseline", "mutant"):
    with (c.mutated(*MUT) if arm == "mutant" else c.contextlib.nullcontext()):
        res[arm] = c.release_direct([20.0, 20.0, 18.0], [19.0, 19.0], space_pins=[0.0, NAN])
print(f"RESULT direct_breach_after_step0_off_baseline={c.fmt(res['baseline'])} mutant={c.fmt(res['mutant'])}")
c.tail()
