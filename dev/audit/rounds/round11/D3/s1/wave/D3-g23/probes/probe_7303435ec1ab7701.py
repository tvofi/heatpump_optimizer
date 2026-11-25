#!/usr/bin/env python3
# Metric: what _safety_release_steps returns when a breach lies past the end of a short pin array; and optimize()'s plan signature for short pin arrays.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g23/probes/probe_7303435ec1ab7701.py
# EXPECTED RESULT direct_short_pins_baseline=([0],[])
# EXPECTED RESULT direct_short_pins_mutant=IndexError
# EXPECTED RESULT null_full_pins_delta=0
# EXPECTED RESULT optimize_short_pins_differing_plans=0 of 3
# EXPECTED RESULT reach_short_pins_calls=0 of 11 (over 7 manual-plan solves)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g23 cloud (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux),
#   run from a scratch baseline worktree while the box's full gate ran (counts exact; no timing is claimed).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._safety_release_steps._preceding_off, line 5212 (pin read past the array's end).
# Perturbation: key 7303435ec1ab7701, optimizer.py:5212 `pin = float(pins[j]) if j < len(pins) else float("nan")` -> `pin = float(pins[j]) if j <= len(pins) else float("nan")`, applied in memory
#   (_g23_common.mutated re-compiles HeatPumpOptimizer._safety_release_steps with the one line replaced and patches the class);
#   direction: a breach past a short pin array goes from releasing the off step to IndexError.
# Null control: pins of full length: both arms identical.
# Writes nothing. Helpers: _g23_common.py beside this file.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import _g23_common as c  # noqa: E402
NAN = c.NAN
MUT = ('_safety_release_steps', 'pin = float(pins[j]) if j < len(pins) else float("nan")', 'pin = float(pins[j]) if j <= len(pins) else float("nan")')
room = [20.0, 20.0, 20.0, 18.0]; floors = [19.0] * 3
res = {}
for arm in ("baseline", "mutant"):
    with (c.mutated(*MUT) if arm == "mutant" else c.contextlib.nullcontext()):
        res[arm] = (c.release_direct(room, floors, space_pins=[0.0]), c.release_direct(room, floors, space_pins=[0.0, NAN, NAN]))
print(f"RESULT direct_short_pins_baseline={c.fmt(res['baseline'][0])}")
print(f"RESULT direct_short_pins_mutant={c.fmt(res['mutant'][0])}")
print(f"RESULT null_full_pins_delta={int(res['baseline'][1] != res['mutant'][1])}")
diff = 0
for length in (95, 50, 1):
    b = c.build("winter_extreme", "winter_cold", room_temperature=16.9, slab_temperature=16.9)
    p = c.pins(length, (0, 1, 0.0))
    base = c.plan_signature(c.solve(b, space_pins=p.copy()))
    with c.mutated(*MUT):
        mut = c.plan_signature(c.solve(b, space_pins=p.copy()))
    diff += int(base != mut)
print(f"RESULT optimize_short_pins_differing_plans={diff} of 3")
with c.Spy("_safety_release_steps", lambda self, r, t, sp, dp: any(x is not None and len(x) < n for x, n in
           ((sp, len(r.power_schedule)), (dp, len(r.dhw_power_schedule or []))))) as spy:
    n = c.reach_solves()
print(f"RESULT reach_short_pins_calls={spy.hits} of {spy.calls} (over {n} manual-plan solves)")
c.tail()
