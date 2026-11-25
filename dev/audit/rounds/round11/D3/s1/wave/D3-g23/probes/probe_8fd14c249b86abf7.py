#!/usr/bin/env python3
# Metric: space release list _safety_release_steps returns when a forced-off step ends at floor+0.1 (inside the pinned-off breach band, above the free-step band); and optimize()'s plan signature over short off blocks.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g23/probes/probe_8fd14c249b86abf7.py
# EXPECTED RESULT direct_off_step_at_floor_plus_0.1_release_baseline=([0],[])
# EXPECTED RESULT direct_off_step_at_floor_plus_0.1_release_mutant=([],[])
# EXPECTED RESULT null_deep_breach_delta=0
# EXPECTED RESULT optimize_off_block_differing_plans=11 of 55
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g23 cloud (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux),
#   run from a scratch baseline worktree while the box's full gate ran (counts exact; no timing is claimed).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._safety_release_steps, line 5234 (the pinned-off breach rule).
# Perturbation: key 8fd14c249b86abf7, optimizer.py:5234 `if pinned_off:` -> `if False:`, applied in memory
#   (_g23_common.mutated re-compiles HeatPumpOptimizer._safety_release_steps with the one line replaced and patches the class);
#   direction: a forced-off step at floor+0.1 goes from released to not released.
# Null control: the same step at floor-0.5 (both rules breach): both arms identical.
# Writes nothing. Helpers: _g23_common.py beside this file.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import _g23_common as c  # noqa: E402
NAN = c.NAN
MUT = ('_safety_release_steps', 'if pinned_off:', 'if False:')
floors = [19.0] * 2
band = [20.0, 19.1, 20.0]; deep = [20.0, 18.5, 20.0]
p = [0.0, NAN]
res = {}
for arm in ("baseline", "mutant"):
    with (c.mutated(*MUT) if arm == "mutant" else c.contextlib.nullcontext()):
        res[arm] = (c.release_direct(band, floors, space_pins=p), c.release_direct(deep, floors, space_pins=p))
print(f"RESULT direct_off_step_at_floor_plus_0.1_release_baseline={c.fmt(res['baseline'][0])}")
print(f"RESULT direct_off_step_at_floor_plus_0.1_release_mutant={c.fmt(res['mutant'][0])}")
print(f"RESULT null_deep_breach_delta={int(res['baseline'][1] != res['mutant'][1])}")
diff = tried = 0
for r0 in (16.6, 16.7, 16.8, 16.9, 17.0, 17.1, 17.2, 17.3, 17.4, 17.5, 17.6):
    for blocks in (((0, 1, 0.0),), ((0, 2, 0.0),), ((0, 4, 0.0),), ((0, 8, 0.0),), ((40, 48, 0.0),)):
        b = c.build("winter_extreme", "winter_cold", room_temperature=r0, slab_temperature=r0)
        pp = c.pins(c.N, *blocks)
        base = c.plan_signature(c.solve(b, space_pins=pp.copy()))
        with c.mutated(*MUT):
            mut = c.plan_signature(c.solve(b, space_pins=pp.copy()))
        diff += int(base != mut); tried += 1
print(f"RESULT optimize_off_block_differing_plans={diff} of {tried}")
c.tail()
