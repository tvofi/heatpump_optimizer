import json, sys
from pathlib import Path
OUT = Path(sys.argv[1])
EXP = json.loads(Path(sys.argv[2]).read_text()) if len(sys.argv) > 2 and Path(sys.argv[2]).exists() else {}
SR = "custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._safety_release_steps"

P = {}
def add(key, line, fname, old, new, metric, symbol, null, body, perturb_note):
    P[key] = dict(line=line, fname=fname, old=old, new=new, metric=metric, symbol=symbol, null=null, body=body, note=perturb_note)

# ---- direct-call building blocks (all temperatures in C; floor 19.0) ----
add("c6679b9b114e5732", 5228, "_safety_release_steps",
    'pin = float(space_pins[i]) if i < len(space_pins) else float("nan")',
    'pin = float(space_pins[i]) if i <= len(space_pins) else float("nan")',
    "what _safety_release_steps returns (release lists or the exception name) when space_pins is shorter than the solved schedule; and whether optimize() output differs (count of differing plan signatures) for short pin arrays",
    SR + ", line 5228 (space-pin read past the pin array's end)",
    "pins of full length n: both arms identical ([],[])",
    '''
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
''', "direction: a short pin array goes from 'tail free' to IndexError")

add("8ef1027c9e221b64", 5229, "_safety_release_steps",
    "pinned_off = not _pin_is_free(pin) and pin < 0.5",
    "pinned_off = not _pin_is_free(pin) and pin <= 0.5",
    "space release list _safety_release_steps returns when a step carries a pin of exactly 0.5 at floor+0.1; and optimize()'s plan signature with 0.5 pins",
    SR + ", line 5229 (pinned_off classification, the 0.5 boundary)",
    "pin 1.0 (on) in place of 0.5: both arms identical",
    '''
room = [20.0, 20.0, 19.1, 20.0]; floors = [19.0] * 3
half = [0.0, 0.5, NAN]; on = [0.0, 1.0, NAN]
res = {}
for arm in ("baseline", "mutant"):
    with (c.mutated(*MUT) if arm == "mutant" else c.contextlib.nullcontext()):
        res[arm] = (c.release_direct(room, floors, space_pins=half), c.release_direct(room, floors, space_pins=on))
print(f"RESULT direct_half_pin_release_baseline={c.fmt(res['baseline'][0])}")
print(f"RESULT direct_half_pin_release_mutant={c.fmt(res['mutant'][0])}")
print(f"RESULT null_on_pin_delta={int(res['baseline'][1] != res['mutant'][1])}")
diff = tried = 0
for r0 in (16.6, 16.7, 16.8, 16.9, 17.0, 17.1, 17.2, 17.3, 17.4, 17.5, 17.6):
    for blocks in (((0, 2, 0.0), (2, 3, 0.5)), ((0, 4, 0.0), (4, 6, 0.5)), ((0, 1, 0.5),), ((0, 1, 0.0), (1, 8, 0.5)),
                   ((0, 4, 0.0), (4, 96, 0.5))):
        b = c.build("winter_extreme", "winter_cold", room_temperature=r0, slab_temperature=r0)
        p = c.pins(c.N, *blocks)
        base = c.plan_signature(c.solve(b, space_pins=p.copy()))
        with c.mutated(*MUT):
            mut = c.plan_signature(c.solve(b, space_pins=p.copy()))
        diff += int(base != mut); tried += 1
print(f"RESULT optimize_half_pin_differing_plans={diff} of {tried}")
''', "direction: a 0.5 pin at floor+0.1 goes from not-a-breach to a breach releasing the preceding off block")

add("ce686724ef107650", 5229, "_safety_release_steps",
    "pinned_off = not _pin_is_free(pin) and pin < 0.5",
    "pinned_off = not _pin_is_free(pin) or pin < 0.5",
    "space release list _safety_release_steps returns when a pinned-ON step sits at floor+0.1 after a forced-off step; and optimize()'s plan signature over manual-plan inputs with on-blocks",
    SR + ", line 5229 (pinned_off classification, and -> or)",
    "the same step free (NaN) instead of pinned on: both arms identical",
    '''
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
''', "direction: an on-pinned step at floor+0.1 goes from no breach to releasing the preceding off block")

add("8fd14c249b86abf7", 5234, "_safety_release_steps",
    "if pinned_off:", "if False:",
    "space release list _safety_release_steps returns when a forced-off step ends at floor+0.1 (inside the pinned-off breach band, above the free-step band); and optimize()'s plan signature over short off blocks",
    SR + ", line 5234 (the pinned-off breach rule)",
    "the same step at floor-0.5 (both rules breach): both arms identical",
    '''
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
''', "direction: a forced-off step at floor+0.1 goes from released to not released")

add("0120a5a672990611", 5235, "_safety_release_steps",
    "breach = temp <= floor + 0.15", "breach = temp < floor + 0.15",
    "space release list _safety_release_steps returns when a forced-off step ends at exactly floor + 0.15 (the tie)",
    SR + ", line 5235 (pinned-off breach bound)",
    "floor+0.10 (both breach) and floor+0.20 (neither): both arms identical",
    '''
floors = [19.0]
tie = 19.0 + 0.15
res = {}
for arm in ("baseline", "mutant"):
    with (c.mutated(*MUT) if arm == "mutant" else c.contextlib.nullcontext()):
        res[arm] = [c.release_direct([20.0, t], floors, space_pins=[0.0]) for t in (tie, 19.1, 19.2)]
print(f"RESULT direct_tie_release_baseline={c.fmt(res['baseline'][0])}")
print(f"RESULT direct_tie_release_mutant={c.fmt(res['mutant'][0])}")
print(f"RESULT null_off_tie_delta={int(res['baseline'][1:] != res['mutant'][1:])}")
''', "direction: a forced-off step at exactly floor+0.15 goes from released to not released")

add("0ecb763c4bcb0828", 5237, "_safety_release_steps",
    "breach = temp < floor - 0.25", "breach = temp <= floor - 0.25",
    "space release list _safety_release_steps returns when a free step after a forced-off step ends at exactly floor - 0.25 (the tie)",
    SR + ", line 5237 (free-step breach bound)",
    "floor-0.30 (both breach) and floor-0.20 (neither): both arms identical",
    '''
floors = [19.0, 19.0]
tie = 19.0 - 0.25
res = {}
for arm in ("baseline", "mutant"):
    with (c.mutated(*MUT) if arm == "mutant" else c.contextlib.nullcontext()):
        res[arm] = [c.release_direct([20.0, 20.0, t], floors, space_pins=[0.0, NAN]) for t in (tie, 18.7, 18.8)]
print(f"RESULT direct_tie_release_baseline={c.fmt(res['baseline'][0])}")
print(f"RESULT direct_tie_release_mutant={c.fmt(res['mutant'][0])}")
print(f"RESULT null_off_tie_delta={int(res['baseline'][1:] != res['mutant'][1:])}")
''', "direction: a free step at exactly floor-0.25 goes from no breach to releasing the preceding off block")

add("f2894b5754c254fe", 5248, "_safety_release_steps",
    "for i in range(min(len(result.dhw_power_schedule), len(req))):",
    "for i in range((len(result.dhw_power_schedule))):",
    "what _safety_release_steps returns when the DHW requirement is shorter than the DHW schedule; and how many real manual-plan release calls ever carry such a requirement",
    SR + ", line 5248 (DHW loop bound)",
    "requirement as long as the schedule: both arms identical",
    '''
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
''', "direction: a short requirement goes from a truncated loop to IndexError")

add("bc3a42f14c903439", 5250, "_safety_release_steps",
    "if temp >= float(req[i]) - 0.5:", "if temp > float(req[i]) - 0.5:",
    "DHW release list _safety_release_steps returns when the tank ends a forced-off step at exactly requirement - 0.5 (the tie)",
    SR + ", line 5250 (DHW breach bound)",
    "requirement-0.4 (neither releases) and requirement-0.6 (both release): both arms identical",
    '''
room = [20.0, 20.0]; floors = [19.0]
res = {}
for arm in ("baseline", "mutant"):
    with (c.mutated(*MUT) if arm == "mutant" else c.contextlib.nullcontext()):
        res[arm] = [c.release_direct(room, floors, dhw_traj=[50.0, t], dhw_req=[50.0], dhw_pins=[0.0])
                    for t in (50.0 - 0.5, 49.6, 49.4)]
print(f"RESULT direct_tie_release_baseline={c.fmt(res['baseline'][0])}")
print(f"RESULT direct_tie_release_mutant={c.fmt(res['mutant'][0])}")
print(f"RESULT null_off_tie_delta={int(res['baseline'][1:] != res['mutant'][1:])}")
''', "direction: a tank at exactly requirement-0.5 goes from safe to releasing the forced-off step")

add("856aa341a89a6ab0", 5211, "_safety_release_steps",
    "while j >= 0:", "while j > 0:",
    "steps optimize() releases (result.manual_released_space) for a winter_extreme house starting at 16.9 C with only step 0 forced off",
    SR + "._preceding_off, line 5211 (the backward walk's lower bound)",
    "the same solve with steps 0-3 forced off (the walk finds step >= 1 first): both arms identical",
    '''
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
''', "direction: a breach whose only preceding forced-off step is step 0 goes from releasing step 0 to releasing nothing")

add("7303435ec1ab7701", 5212, "_safety_release_steps",
    'pin = float(pins[j]) if j < len(pins) else float("nan")',
    'pin = float(pins[j]) if j <= len(pins) else float("nan")',
    "what _safety_release_steps returns when a breach lies past the end of a short pin array; and optimize()'s plan signature for short pin arrays",
    SR + "._preceding_off, line 5212 (pin read past the array's end)",
    "pins of full length: both arms identical",
    '''
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
''', "direction: a breach past a short pin array goes from releasing the off step to IndexError")

add("5ce83ed87c36b9a5", 5213, "_safety_release_steps",
    "if not _pin_is_free(pin) and pin < 0.5:", "if not _pin_is_free(pin) and pin <= 0.5:",
    "space release list _safety_release_steps returns when a free-step breach is preceded by a 0.5 pin and then a forced-off step; and optimize()'s plan signature with 0.5 pins",
    SR + "._preceding_off, line 5213 (off-pin test, the 0.5 boundary)",
    "pin 1.0 in place of 0.5: both arms identical",
    '''
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
''', "direction: a breach behind a 0.5 pin goes from releasing the off block to releasing nothing")

add("fe3e41de6bdc640a", 5213, "_safety_release_steps",
    "if not _pin_is_free(pin) and pin < 0.5:", "if not _pin_is_free(pin) or pin < 0.5:",
    "steps optimize() releases (result.manual_released_space) for a winter_extreme house starting at 17.0 C with steps 0-1 forced off and step 2 forced on",
    SR + "._preceding_off, line 5213 (off-pin test, and -> or)",
    "the same solve without the on-pin at step 2 (steps 0-1 off only): both arms identical",
    '''
b = c.build("winter_extreme", "winter_cold", room_temperature=17.0, slab_temperature=17.0)
with_on = c.pins(c.N, (0, 2, 0.0), (2, 3, 1.0)); off_only = c.pins(c.N, (0, 2, 0.0))
base = c.solve(b, space_pins=with_on.copy()); base_null = c.plan_signature(c.solve(b, space_pins=off_only.copy()))
with c.mutated(*MUT):
    mut = c.solve(b, space_pins=with_on.copy()); mut_null = c.plan_signature(c.solve(b, space_pins=off_only.copy()))
print(f"RESULT released_space_baseline={c.fmt(sorted(base.manual_released_space))}")
print(f"RESULT released_space_mutant={c.fmt(sorted(mut.manual_released_space))}")
print(f"RESULT space_kwh_first_hour_baseline={sum(base.power_schedule[:4]) * 0.25:.4f} mutant={sum(mut.power_schedule[:4]) * 0.25:.4f}")
print(f"RESULT null_off_only_delta={int(base_null != mut_null)}")
''', "direction: a breach behind an on-pin goes from releasing the preceding off block to releasing nothing")

add("f25414a9d4e32d19", 5292, "_seed_pinned_guess",
    "for i in range(min(len(out), len(bounds))):", "for i in range((len(out))):",
    "what _seed_pinned_guess returns for a guess longer than its bounds; and how many real solve calls pass a guess whose length differs from the bounds",
    "custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._seed_pinned_guess, line 5292 (loop bound)",
    "guess as long as the bounds: both arms identical",
    '''
import numpy as np
res = {}
for arm in ("baseline", "mutant"):
    with (c.mutated(*MUT) if arm == "mutant" else c.contextlib.nullcontext()):
        out = []
        for g, bnd in (([5.0, 5.0, 5.0], [(0.0, 1.0), (0.0, 2.0)]), ([5.0, -1.0], [(0.0, 1.0), (0.5, 2.0)])):
            try:
                out.append([float(x) for x in c.OPT._seed_pinned_guess(np.array(g), bnd)])
            except Exception as exc:
                out.append(type(exc).__name__)
        res[arm] = out
print(f"RESULT direct_long_guess_baseline={c.fmt(res['baseline'][0])}")
print(f"RESULT direct_long_guess_mutant={c.fmt(res['mutant'][0])}")
print(f"RESULT null_equal_length_delta={int(res['baseline'][1] != res['mutant'][1])}")
with c.Spy("_seed_pinned_guess", lambda g, bnd: len(g) != len(bnd)) as spy:
    n = c.reach_solves()
print(f"RESULT reach_length_mismatch_calls={spy.hits} of {spy.calls} (over {n} solves)")
''', "direction: a long guess goes from an unclamped tail to IndexError")

SC = "custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._settlement_caps"
BUF = '''
import numpy as np
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState


def make():
    p = ThermalParameters(two_zone_enabled=True, buffer_tank_volume=750.0, mixing_valve_mode="manual", buffer_max_temp=70.0)
    cfg = c.om.OptimizationConfig(horizon_hours=24, time_step_minutes=15, target_temp=21.0, min_temp=19.0, max_temp=23.0)
    return c.OPT(ThermalModel(p), cfg)


outdoor = np.full(96, -20.0)
o = make()
o._initial_buffer_temp = None
ceiling = o._settlement_caps(outdoor)["buffer"]
caps = {}
for arm in ("baseline", "mutant"):
    with (c.mutated(*MUT) if arm == "mutant" else c.contextlib.nullcontext()):
        o._initial_buffer_temp = 60.0
        hot = o._settlement_caps(outdoor)["buffer"]
        o._initial_buffer_temp = 30.0
        cool = o._settlement_caps(outdoor)["buffer"]
        caps[arm] = (hot, cool)
print(f"RESULT charge_ceiling={ceiling:.3f} C")
print(f"RESULT buffer_cap_initial60_baseline={caps['baseline'][0]:.3f} C")
print(f"RESULT buffer_cap_initial60_mutant={caps['mutant'][0]:.3f} C")
print(f"RESULT null_initial30_delta={abs(caps['baseline'][1] - caps['mutant'][1]):.6f} C")
# through optimize(): a valve house, a -20 C day, tank starting at 60 C
from profiles import prices, weather
_o, wind, rain, solar = weather("winter_cold", c.START)
outd = np.full(len(_o), -20.0)
state = ThermalState(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=float(outd[0]),
                     upper_floor_temperature=21.0, lower_floor_temperature=21.0, buffer_tank_temperature=60.0)
from profiles import solve_inputs
def run():
    return make().optimize(inputs=solve_inputs(initial_state=state, prices=prices("winter_typical", c.START),
                           outdoor_temps=outd, wind_speeds=wind, precipitation=rain, solar_radiation=solar, start_time=c.START))
rb = run()
with c.mutated(*MUT):
    rm = run()
d = c.result_diff(rb, rm)
print(f"RESULT optimize_tank60_differing_fields={len(d)} {c.fmt(d[:8])}")
'''
add("70791cdb98f8ddd7", 6027, "_settlement_caps",
    "if initial is not None:", "if False:",
    "the buffer settlement cap (C) _settlement_caps returns for a 750 L valve tank on a -20 C day (charge ceiling 35 C) when the solve starts with the tank at 60 C (above the charge ceiling); and how many OptimizationResult fields optimize() changes",
    SC + ", line 6027 (floor of the buffer cap at the initial tank temperature)",
    "initial tank 30 C (below the ceiling): both arms identical",
    BUF, "direction: the cap falls from 60 C to the 35 C charge ceiling, so pre-stored heat above it settles at zero")
add("7516dd3d9e66d3ef", 6029, "_settlement_caps",
    "float(p.buffer_max_temp), max(ceiling, float(initial))", "float(p.buffer_max_temp), (ceiling)",
    "the buffer settlement cap (C) _settlement_caps returns for a 750 L valve tank on a -20 C day (charge ceiling 35 C) when the solve starts with the tank at 60 C (above the charge ceiling); and how many OptimizationResult fields optimize() changes",
    SC + ", line 6029 (max(ceiling, initial))",
    "initial tank 30 C (below the ceiling): both arms identical",
    BUF, "direction: the cap falls from 60 C to the 35 C charge ceiling, so pre-stored heat above it settles at zero")
add("65e0ffa75d60d319", 6038, "_settlement_caps",
    "if p.two_tank_modelled:", "if False:",
    "whether _settlement_caps returns a 'wood' cap (and its value, C) for a two-tank 4-way-valve house; and how many OptimizationResult fields optimize() changes with the wood tank starting at 99 C (a probe reading above the 95 C rating)",
    SC + ", line 6038 (the wood-tank settlement cap)",
    "a single-tank house (no wood probe): both arms identical",
    '''
import numpy as np
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
base_cfg = {"indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor", "upper_floor_thermal_mass": 3.0,
            "lower_floor_thermal_mass": 4.5, "buffer_tank_volume": 750.0, "mixing_valve_mode": "manual"}
def make(wood, hours=24):
    cfg = dict(base_cfg)
    if wood:
        cfg["wood_tank_top_entity"] = "sensor.wood_top"
    p = ThermalParameters.from_config(cfg)
    oc = c.om.OptimizationConfig(horizon_hours=hours, time_step_minutes=15, target_temp=21.0, min_temp=19.0, max_temp=23.0)
    return c.OPT(ThermalModel(p), oc)
outdoor = np.full(96, -5.0)
caps = {}
for arm in ("baseline", "mutant"):
    with (c.mutated(*MUT) if arm == "mutant" else c.contextlib.nullcontext()):
        caps[arm] = (make(True)._settlement_caps(outdoor), make(False)._settlement_caps(outdoor))
print(f"RESULT two_tank_modelled={int(make(True).model.params.two_tank_modelled)}")
print(f"RESULT wood_cap_baseline={caps['baseline'][0].get('wood')}")
print(f"RESULT wood_cap_mutant={caps['mutant'][0].get('wood')}")
print(f"RESULT null_single_tank_delta={int(caps['baseline'][1] != caps['mutant'][1])}")
from profiles import prices, weather, solve_inputs
outd, wind, rain, solar = weather("winter_cold", c.START)
st = dict(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=float(outd[0]), upper_floor_temperature=21.0,
          lower_floor_temperature=21.0, buffer_tank_temperature=45.0)
fields = {f.name for f in __import__("dataclasses").fields(ThermalState)}
for k, v in (("wood_tank_temperature", 99.0), ("wood_tank_top_temperature", 99.0)):
    if k in fields:
        st[k] = v
state = ThermalState(**st)
# the cap's one reader: _stored_thermal_energy(state, caps=...) on a state whose wood tank reads 99 C
e = {arm: make(True)._stored_thermal_energy(state, caps=caps[arm][0]) for arm in ("baseline", "mutant")}
print(f"RESULT stored_kwh_wood99_baseline={e['baseline']:.4f} kWh")
print(f"RESULT stored_kwh_wood99_mutant={e['mutant']:.4f} kWh")
for hours in (24, 2, 1):
    n = int(hours * 4)
    def run():
        return make(True, hours).optimize(inputs=solve_inputs(initial_state=state, prices=prices("winter_typical", c.START)[:n],
                                   outdoor_temps=outd[:n], wind_speeds=wind[:n], precipitation=rain[:n], solar_radiation=solar[:n],
                                   start_time=c.START))
    rb = run()
    with c.mutated(*MUT):
        rm = run()
    d = c.result_diff(rb, rm)
    print(f"RESULT optimize_two_tank_wood99_{hours}h_differing_fields={len(d)} {c.fmt(d[:8])}")
''', "direction: the wood store loses its settlement cap ('wood' key absent)")

for key, s in P.items():
    exp = EXP.get(key, ["(filled from the first run)"])
    hdr = [
        "#!/usr/bin/env python3",
        f"# Metric: {s['metric']}.",
        f"# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g23/probes/probe_{key}.py",
    ] + [f"# EXPECTED {e}" for e in exp] + [
        "# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g23 cloud (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux),",
        "#   run from a scratch baseline worktree while the box's full gate ran (counts exact; no timing is claimed).",
        f"# Instrumented symbol: {s['symbol']}.",
        f"# Perturbation: key {key}, optimizer.py:{s['line']} `{s['old']}` -> `{s['new']}`, applied in memory",
        f"#   (_g23_common.mutated re-compiles HeatPumpOptimizer.{s['fname']} with the one line replaced and patches the class);",
        f"#   {s['note']}.",
        f"# Null control: {s['null']}.",
        "# Writes nothing. Helpers: _g23_common.py beside this file.",
        "import os",
        'for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):',
        '    os.environ.setdefault(_v, "1")',
        "import _g23_common as c  # noqa: E402",
        "NAN = c.NAN",
        f"MUT = ({s['fname']!r}, {s['old']!r}, {s['new']!r})",
    ]
    (OUT / f"probe_{key}.py").write_text("\n".join(hdr) + "\n" + s["body"].lstrip("\n") + "c.tail()\n")
print("wrote", len(P))
