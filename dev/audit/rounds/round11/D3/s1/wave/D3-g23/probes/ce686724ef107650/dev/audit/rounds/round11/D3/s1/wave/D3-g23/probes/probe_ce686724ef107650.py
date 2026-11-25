#!/usr/bin/env python3
# Metric: space release list _safety_release_steps returns when a pinned-ON step sits at floor+0.1 after a forced-off step; and optimize()'s plan signature over manual-plan inputs with on-blocks.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g23/probes/probe_ce686724ef107650.py
# EXPECTED RESULT direct_on_pin_at_floor_release_baseline=([],[])
# EXPECTED RESULT direct_on_pin_at_floor_release_mutant=([0],[])
# EXPECTED RESULT null_free_step_delta=0
# EXPECTED RESULT optimize_on_block_differing_plans=3 of 36
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g23 cloud (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux),
#   run from a scratch baseline worktree while the box's full gate ran (counts exact; no timing is claimed).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._safety_release_steps, line 5229 (pinned_off classification, and -> or).
# Perturbation: key ce686724ef107650, optimizer.py:5229 `pinned_off = not _pin_is_free(pin) and pin < 0.5` -> `pinned_off = not _pin_is_free(pin) or pin < 0.5`, applied in memory
#   (_g23_common.mutated re-compiles HeatPumpOptimizer._safety_release_steps with the one line replaced and patches the class);
#   direction: an on-pinned step at floor+0.1 goes from no breach to releasing the preceding off block.
# Null control: the same step free (NaN) instead of pinned on: both arms identical.
# Writes nothing. Helpers: _g23_common.py beside this file.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import _g23_common as c  # noqa: E402
NAN = c.NAN
MUT = ('_safety_release_steps', 'pinned_off = not _pin_is_free(pin) and pin < 0.5', 'pinned_off = not _pin_is_free(pin) or pin < 0.5')
room = [20.0, 20.0, 19.1, 20.0]; floors = [19.0] * 3
on = [0.0, 1.0, NAN]; free = [0.0, NAN, NAN]
res = {}
for arm in ("baseline", "mutant"):
    with (c.mutated(*MUT) if arm == "mutant" else c.contextlib.nullcontext()):
        res[arm] = (c.release_direct(room, floors, space_pins=on), c.release_direct(room, floors, space_pins=free))
print(f"RESULT direct_on_pin_at_floor_release_baseline={c.fmt(res['baseline'][0])}")
print(f"RESULT direct_on_pin_at_floor_release_mutant={c.fmt(res['mutant'][0])}")
print(f"RESULT null_free_step_delta={int(res['baseline'][1] != res['mutant'][1])}")
diff = tried = 0
for r0 in (16.8, 16.9, 17.0, 17.1, 17.2, 17.3, 17.4, 17.5, 17.6):
    for blocks in (((0, 2, 0.0), (2, 3, 1.0)), ((0, 4, 0.0), (4, 6, 1.0)), ((0, 8, 0.0), (8, 10, 1.0)), ((0, 4, 0.0), (4, 96, 1.0))):
        b = c.build("winter_extreme", "winter_cold", room_temperature=r0, slab_temperature=r0)
        p = c.pins(c.N, *blocks)
        base = c.plan_signature(c.solve(b, space_pins=p.copy()))
        with c.mutated(*MUT):
            mut = c.plan_signature(c.solve(b, space_pins=p.copy()))
        diff += int(base != mut); tried += 1
print(f"RESULT optimize_on_block_differing_plans={diff} of {tried}")
c.tail()
