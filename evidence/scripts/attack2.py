"""Round-2 reviewer attacks (mine): one load vs two loads over several edit shapes and swaps; snapshot
restore of a pre-swap snapshot onto a swapped AND edited configuration."""
import asyncio, sys, os
WT = os.path.abspath(sys.argv[1]); sys.argv=[sys.argv[0], WT]
sys.path[:0] = [os.path.dirname(__file__)]
import probe
from swap_energy import BASE, mk, written
def load(cfg, st):
    c = mk(cfg, st); asyncio.run(c._async_load_thermal_learning()); return c
def S(c): return (round(c._house_heat_loss_scale,4), round(c._lower_floor_loss_ratio,4), c._house_heat_loss_samples, c._lower_floor_loss_samples)
U, L = BASE["upper_floor_heat_loss"], BASE["lower_floor_heat_loss"]
EDITS = {"both x1.5": dict(upper_floor_heat_loss=U*1.5, lower_floor_heat_loss=L*1.5),
         "owner 0.2/0.3": dict(upper_floor_heat_loss=0.2, lower_floor_heat_loss=0.3),
         "lower only x2": dict(lower_floor_heat_loss=L*2), "upper only x0.6": dict(upper_floor_heat_loss=U*0.6),
         "below gate x1.02": dict(upper_floor_heat_loss=U*1.02, lower_floor_heat_loss=L*1.02)}
SW = {"none": {}, "lower": dict(lower_floor_temp_entity="sensor.t6"), "indoor": dict(indoor_temp_entity="sensor.bthome"),
      "both": dict(indoor_temp_entity="sensor.bthome", lower_floor_temp_entity="sensor.t6"),
      "lower removed": dict(lower_floor_temp_entity=None)}
for en, ed in EDITS.items():
    for sn, sw in SW.items():
        st = written(); one = S(load(dict(BASE, **sw, **ed), st))
        st = written(); load(dict(BASE, **sw), st); two = S(load(dict(BASE, **sw, **ed), st))
        print(f"RESULT edit={en:<16} swap={sn:<13} one={one} two={two} {'AGREE' if all(abs(a-b)<1e-3 for a,b in zip(one,two)) else 'DIFFER'}")
# snapshot: pre-swap snapshot onto swapped+edited config, vs a fresh load of the same store
for en in ("both x1.5", "owner 0.2/0.3"):
    for sn in ("lower", "both"):
        st = written(); c0 = load(BASE, st); snap = c0._learner_snapshot_payloads()
        cfg = dict(BASE, **SW[sn], **EDITS[en])
        c = load(cfg, written()); c._apply_learner_payloads(snap)
        ref = S(load(cfg, written()))
        print(f"RESULT snapshot edit={en:<14} swap={sn:<5} restored={S(c)} fresh_load={ref} {'AGREE' if S(c)==ref else 'DIFFER'}")
