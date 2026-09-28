"""H3: ThermalParameters.dhw_hourly_draw_pattern has two writers: the
DhwProfileLearner (pooled profile: load / learn_usage / apply_payload) and,
per solve, _prepare_dhw_inputs (today's day-type BLEND). Who reads which?

Rig: real coordinator, DHW on, the learner given day-type evidence
(weekday+weekend profiles with a morning/evening spike, 30 distinct days each)
so today's blend differs from the pooled profile.  Null: zero day-type
samples, so pattern_for() returns the pooled profile byte for byte.

Readers probed after a real async_run_optimization:
  R1 learner.hourly_profile (what async_learn_usage copies from)     -> pooled?
  R2 learner.normalize_profile(<corrupt>) fallback (dhw_learning ~132) -> which?
  R3 learner.apply_payload({hourly_profile: <corrupt>, ...}) i.e. the #42
     snapshot-rollback path with an unusable row -> what the POOLED profile
     (persisted by the next async_save_profile) becomes
  R4 _dhw_setpoint_sweep() (published as data['dhw_advisor']) with the
     pattern as the solve left it vs as the learner's own writer leaves it
  R5 learner seed (dhw_learning ~96): constructed once in __init__
     (coordinator ~2152), before any solve -> reported statically.
"""
import asyncio
import math

import rig


def spiky(a, b):
    p = [0.3] * 24
    p[a] = 5.0
    p[b] = 4.0
    return p


def dist(x, y):
    return round(max(abs(float(i) - float(j)) for i, j in zip(x, y)), 4)


async def arm(name, evidence):
    c = rig.make(f"h3_{name}", extra={"dhw_enabled": True, "dhw_temp_entity": "sensor.dhw"})
    c.hass.states.set("sensor.dhw", rig.FakeState("50.0", unit="°C"))
    L = c._dhw_learner
    pooled = list(L.hourly_profile)
    L.profile_weekday = L.normalize_profile(spiky(6, 20))
    L.profile_weekend = L.normalize_profile(spiky(9, 18))
    L.daytype_samples = [evidence, evidence]
    weekend = rig.dt_util.now().weekday() >= 5
    blend = L.pattern_for(weekend)
    r = await c.async_run_optimization()
    params = c._thermal_params
    after_solve = list(params.dhw_hourly_draw_pattern)
    out = {"arm": name, "solve": r, "|blend-pooled|": dist(blend, pooled),
           "params after solve == blend": after_solve == blend,
           "R1 learner.hourly_profile == pooled": L.hourly_profile == pooled}
    fb = L.normalize_profile([float("nan")] * 24)
    out["R2 fallback: |fb-pooled|"] = dist(fb, pooled)
    out["R2 fallback: |fb-blend|"] = dist(fb, blend)
    sweep_blend = c._dhw_setpoint_sweep()
    # R3: the #42 rollback path with an unusable pooled row
    snap = L.payload()
    bad = list(snap["hourly_profile"])
    bad[3] = float("nan")  # one non-finite hour -> normalize_profile quarantines to its fallback (R5-D1-05)
    snap = dict(snap, hourly_profile=bad)
    L.apply_payload(snap)
    out["R3 pooled after rollback: |.-pooled|"] = dist(L.hourly_profile, pooled)
    out["R3 pooled after rollback: |.-blend|"] = dist(L.hourly_profile, blend)
    out["R3 persisted payload hourly_profile == blend"] = L.payload()["hourly_profile"] == blend
    # R4: learner's own writer (apply_payload with the ORIGINAL pooled) -> params = pooled
    L.apply_payload(dict(L.payload(), hourly_profile=pooled))
    sweep_pooled = c._dhw_setpoint_sweep()
    diff = {k: (sweep_blend.get(k), sweep_pooled.get(k)) for k in sweep_blend if sweep_blend.get(k) != sweep_pooled.get(k) and not isinstance(sweep_blend.get(k), (list, dict))}
    out["R4 sweep keys that differ (blend-state, pooled-state)"] = diff or "none"
    return out


async def main():
    rows = [await arm("probe/daytype_evidence=30", 30), await arm("null/daytype_evidence=0", 0)]
    for r in rows:
        print(f"== {r.pop('arm')}")
        for k, v in r.items():
            print(f"  {k}: {v}")


asyncio.run(main())
