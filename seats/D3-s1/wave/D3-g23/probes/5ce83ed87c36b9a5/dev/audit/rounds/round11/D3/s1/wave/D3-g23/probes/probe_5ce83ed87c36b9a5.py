#!/usr/bin/env python3
# Metric: space release list _safety_release_steps returns when a free-step breach is preceded by a 0.5 pin and then a forced-off step; and optimize()'s plan signature with 0.5 pins.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g23/probes/probe_5ce83ed87c36b9a5.py
# EXPECTED RESULT direct_half_pin_release_baseline=([0],[])
# EXPECTED RESULT direct_half_pin_release_mutant=([],[])
# EXPECTED RESULT null_on_pin_delta=0
# EXPECTED RESULT optimize_half_pin_differing_plans=5 of 15
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g23 cloud (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux),
#   run from a scratch baseline worktree while the box's full gate ran (counts exact; no timing is claimed).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._safety_release_steps._preceding_off, line 5213 (off-pin test, the 0.5 boundary).
# Perturbation: key 5ce83ed87c36b9a5, optimizer.py:5213 `if not _pin_is_free(pin) and pin < 0.5:` -> `if not _pin_is_free(pin) and pin <= 0.5:`, applied in memory
#   (_g23_common.mutated re-compiles HeatPumpOptimizer._safety_release_steps with the one line replaced and patches the class);
#   direction: a breach behind a 0.5 pin goes from releasing the off block to releasing nothing.
# Null control: pin 1.0 in place of 0.5: both arms identical.
# Writes nothing. Helpers: _g23_common.py beside this file.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import _g23_common as c  # noqa: E402
NAN = c.NAN
MUT = ('_safety_release_steps', 'if not _pin_is_free(pin) and pin < 0.5:', 'if not _pin_is_free(pin) and pin <= 0.5:')
room = [20.0, 20.0, 20.0, 18.0]; floors = [19.0] * 3
res = {}
for arm in ("baseline", "mutant"):
    with (c.mutated(*MUT) if arm == "mutant" else c.contextlib.nullcontext()):
        res[arm] = (c.release_direct(room, floors, space_pins=[0.0, 0.5, NAN]), c.release_direct(room, floors, space_pins=[0.0, 1.0, NAN]))
print(f"RESULT direct_half_pin_release_baseline={c.fmt(res['baseline'][0])}")
print(f"RESULT direct_half_pin_release_mutant={c.fmt(res['mutant'][0])}")
print(f"RESULT null_on_pin_delta={int(res['baseline'][1] != res['mutant'][1])}")
diff = tried = 0
for r0 in (16.9, 17.0, 17.1, 17.2, 17.3):
    for blocks in (((0, 2, 0.0), (2, 3, 0.5)), ((0, 4, 0.0), (4, 6, 0.5)), ((0, 1, 0.5),)):
        b = c.build("winter_extreme", "winter_cold", room_temperature=r0, slab_temperature=r0)
        p = c.pins(c.N, *blocks)
        base = c.plan_signature(c.solve(b, space_pins=p.copy()))
        with c.mutated(*MUT):
            mut = c.plan_signature(c.solve(b, space_pins=p.copy()))
        diff += int(base != mut); tried += 1
print(f"RESULT optimize_half_pin_differing_plans={diff} of {tried}")
c.tail()
