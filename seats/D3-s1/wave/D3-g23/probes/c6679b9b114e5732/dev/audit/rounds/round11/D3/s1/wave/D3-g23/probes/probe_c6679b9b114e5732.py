#!/usr/bin/env python3
# Metric: what _safety_release_steps returns (release lists or the exception name) when space_pins is shorter than the solved schedule; and whether optimize() output differs (count of differing plan signatures) for short pin arrays.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g23/probes/probe_c6679b9b114e5732.py
# EXPECTED RESULT direct_short_pins_baseline=([],[])
# EXPECTED RESULT direct_short_pins_mutant=IndexError
# EXPECTED RESULT direct_empty_pins_baseline=([],[]) direct_empty_pins_mutant=IndexError
# EXPECTED RESULT null_full_pins_delta=0
# EXPECTED RESULT optimize_short_pins_differing_plans=0 of 3
# EXPECTED RESULT reach_short_space_pins_calls=0 of 11 (over 7 manual-plan solves)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g23 cloud (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux),
#   run from a scratch baseline worktree while the box's full gate ran (counts exact; no timing is claimed).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._safety_release_steps, line 5228 (space-pin read past the pin array's end).
# Perturbation: key c6679b9b114e5732, optimizer.py:5228 `pin = float(space_pins[i]) if i < len(space_pins) else float("nan")` -> `pin = float(space_pins[i]) if i <= len(space_pins) else float("nan")`, applied in memory
#   (_g23_common.mutated re-compiles HeatPumpOptimizer._safety_release_steps with the one line replaced and patches the class);
#   direction: a short pin array goes from 'tail free' to IndexError.
# Null control: pins of full length n: both arms identical ([],[]).
# Writes nothing. Helpers: _g23_common.py beside this file.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import _g23_common as c  # noqa: E402
NAN = c.NAN
MUT = ('_safety_release_steps', 'pin = float(space_pins[i]) if i < len(space_pins) else float("nan")', 'pin = float(space_pins[i]) if i <= len(space_pins) else float("nan")')
room = [20.0, 20.0, 20.0, 20.0, 20.0]; floors = [19.0] * 4
short = [0.0, NAN, NAN]          # 3 pins for a 4-step schedule
full = [0.0, NAN, NAN, NAN]
arms = {}
for arm in ("baseline", "mutant"):
    with (c.mutated(*MUT) if arm == "mutant" else c.contextlib.nullcontext()):
        arms[arm] = (c.release_direct(room, floors, space_pins=short), c.release_direct(room, floors, space_pins=full),
                     c.release_direct(room, floors, space_pins=[]))
print(f"RESULT direct_short_pins_baseline={c.fmt(arms['baseline'][0])}")
print(f"RESULT direct_short_pins_mutant={c.fmt(arms['mutant'][0])}")
print(f"RESULT direct_empty_pins_baseline={c.fmt(arms['baseline'][2])} direct_empty_pins_mutant={c.fmt(arms['mutant'][2])}")
print(f"RESULT null_full_pins_delta={int(arms['baseline'][1] != arms['mutant'][1])}")
diff = 0
for length in (95, 50, 1):
    b = c.build("winter_extreme", "winter_cold", room_temperature=16.9, slab_temperature=16.9)
    p = c.pins(length, (0, 1, 0.0))
    base = c.plan_signature(c.solve(b, space_pins=p.copy()))
    with c.mutated(*MUT):
        mut = c.plan_signature(c.solve(b, space_pins=p.copy()))
    diff += int(base != mut)
print(f"RESULT optimize_short_pins_differing_plans={diff} of 3")
with c.Spy("_safety_release_steps", lambda self, r, t, sp, dp: sp is not None and len(sp) < len(r.power_schedule)) as spy:
    n = c.reach_solves()
print(f"RESULT reach_short_space_pins_calls={spy.hits} of {spy.calls} (over {n} manual-plan solves)")
c.tail()
