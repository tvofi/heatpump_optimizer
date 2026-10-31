"""Reviewer attacks at the head: (b) legacy store adopts then a later swap fires; swap + nameplate edit
in one options change; repeated saves on a legacy store."""
import asyncio, sys, os
WT = os.path.abspath(sys.argv[1]); sys.argv=[sys.argv[0], WT]
sys.path[:0] = [os.path.dirname(__file__)]
import probe
from swap_energy import Store, BASE, mk, written
def load(cfg, st):
    c = mk(cfg, st); asyncio.run(c._async_load_thermal_learning()); return c
def show(tag, c, st):
    print(f"RESULT {tag:<52} scale={c._house_heat_loss_scale:.4f} ratio={c._lower_floor_loss_ratio:.4f} "
          f"n=({c._house_heat_loss_samples},{c._lower_floor_loss_samples}) saves={st.saves} "
          f"rec={(st.saved or {}).get('heat_loss_zone_entities')}")
# (b) legacy -> first load adopts -> second load with a swap must void
st = written(legacy=True); c = load(BASE, st); show("b1 legacy first load, same sensors", c, st)
st.saves = 0; c = load(dict(BASE, lower_floor_temp_entity="sensor.t6"), st); show("b2 then lower swap", c, st)
st.saves = 0; c = load(dict(BASE, lower_floor_temp_entity="sensor.t6"), st); show("b3 then reload same", c, st)
# swap + nameplate edit beyond gate, same options change
EDIT = dict(lower_floor_heat_loss=0.3, upper_floor_heat_loss=0.2)
for name, sw in (("lower", dict(lower_floor_temp_entity="sensor.t6")), ("indoor", dict(indoor_temp_entity="sensor.bthome")),
                 ("both", dict(indoor_temp_entity="sensor.bthome", lower_floor_temp_entity="sensor.t6")), ("none", {})):
    st = written(); c = load(dict(BASE, **EDIT, **sw), st); show(f"e {name} swap + nameplate edit", c, st)
# order check: void first then edit separately (two options changes)
st = written(); c = load(dict(BASE, lower_floor_temp_entity="sensor.t6"), st); st.saves=0
c = load(dict(BASE, **EDIT, lower_floor_temp_entity="sensor.t6"), st); show("e' lower swap, then nameplate edit separately", c, st)
# snapshot restore of a pre-swap snapshot under the swapped sensors
st = written(); c0 = mk(BASE, st); asyncio.run(c0._async_load_thermal_learning()); snap = c0._learner_snapshot_payloads()
c = load(dict(BASE, lower_floor_temp_entity="sensor.t6"), written()); c._apply_learner_payloads(snap); show("s restore pre-swap snapshot under swapped sensor", c, st)
# reset then service default via coordinator method; other learners untouched checked in tests
st = written(); c = load(BASE, st); st.saves=0
asyncio.run(c.async_reset_heat_loss_learners()); show("r reset both", c, st)
d = probe.solve(probe.CFG, {"house_heat_loss_scale": c._house_heat_loss_scale, "lower_floor_loss_ratio": c._lower_floor_loss_ratio}, 22.0)
print(f"RESULT r plan after reset (finder solve) plan_kWh={d['kwh']:.2f} UA={d['ua']:.3f}")
