#!/usr/bin/env python3
# Metric: steps optimize() releases (result.manual_released_space) for a winter_extreme house starting at 17.0 C with steps 0-1 forced off and step 2 forced on.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g23/probes/probe_fe3e41de6bdc640a.py
# EXPECTED RESULT released_space_baseline=[0,1]
# EXPECTED RESULT released_space_mutant=[]
# EXPECTED RESULT space_kwh_first_hour_baseline=4.8809 mutant=3.0000
# EXPECTED RESULT null_off_only_delta=0
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g23 cloud (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux),
#   run from a scratch baseline worktree while the box's full gate ran (counts exact; no timing is claimed).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._safety_release_steps._preceding_off, line 5213 (off-pin test, and -> or).
# Perturbation: key fe3e41de6bdc640a, optimizer.py:5213 `if not _pin_is_free(pin) and pin < 0.5:` -> `if not _pin_is_free(pin) or pin < 0.5:`, applied in memory
#   (_g23_common.mutated re-compiles HeatPumpOptimizer._safety_release_steps with the one line replaced and patches the class);
#   direction: a breach behind an on-pin goes from releasing the preceding off block to releasing nothing.
# Null control: the same solve without the on-pin at step 2 (steps 0-1 off only): both arms identical.
# Writes nothing. Helpers: _g23_common.py beside this file.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import _g23_common as c  # noqa: E402
NAN = c.NAN
MUT = ('_safety_release_steps', 'if not _pin_is_free(pin) and pin < 0.5:', 'if not _pin_is_free(pin) or pin < 0.5:')
b = c.build("winter_extreme", "winter_cold", room_temperature=17.0, slab_temperature=17.0)
with_on = c.pins(c.N, (0, 2, 0.0), (2, 3, 1.0)); off_only = c.pins(c.N, (0, 2, 0.0))
base = c.solve(b, space_pins=with_on.copy()); base_null = c.plan_signature(c.solve(b, space_pins=off_only.copy()))
with c.mutated(*MUT):
    mut = c.solve(b, space_pins=with_on.copy()); mut_null = c.plan_signature(c.solve(b, space_pins=off_only.copy()))
print(f"RESULT released_space_baseline={c.fmt(sorted(base.manual_released_space))}")
print(f"RESULT released_space_mutant={c.fmt(sorted(mut.manual_released_space))}")
print(f"RESULT space_kwh_first_hour_baseline={sum(base.power_schedule[:4]) * 0.25:.4f} mutant={sum(mut.power_schedule[:4]) * 0.25:.4f}")
print(f"RESULT null_off_only_delta={int(base_null != mut_null)}")
c.tail()
