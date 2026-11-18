"""D2 verify-1 V2: independent metrics for D2-s1-01/02, D2-s1-51, D2-s2-01/02/03.

Run from the export root:
  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D2/verify1/v2_independent.py [--perturb]
--perturb applies the five one-line fixes in memory (each metric must go to 0).
"""
import os
import sys
for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from heatpump_optimizer import thermal_model as tm, mixing_valve as mv, defrost as df, presets as ps, const  # noqa

P = "--perturb" in sys.argv
if P:
    orig = tm.ThermalModel.flow_lift_factor

    def fixed_lift(self, o, f):
        r = orig(self, o, f)
        return r if r == 1.0 else max(0.25, 1.0 / r)
    tm.ThermalModel.flow_lift_factor = fixed_lift
    mv.emitter_delivery = lambda *, mix_temp, zone_temp, ua: max(0.0, ua * (mix_temp - zone_temp))
    df.derate_from_duty = lambda d: min(df.DERATE_MAX, max(df.DERATE_MIN, 1.0 - min(max(d, 0.0), df.DEFROST_DUTY_MAX) * df.DEFROST_LOSS_MULTIPLIER))
    ps._ERA_LOSS_W_PER_M2K[ps.ERA_LOW_ENERGY] = 0.40
    _dm = tm.declared_modulation
    tm.declared_modulation = lambda c: False if (c or {}).get(const.CONF_COMPRESSOR_MODULATION) == const.COMPRESSOR_MODULATION_ON_OFF else _dm(c)

m = tm.ThermalModel(tm.ThermalParameters())
# A: lift. outdoor [-20,20] x flow (35,70] at 1 K: count flow_lift_factor > 1 (a lift is a cost).
lift_gt1 = sum(1 for o in range(-20, 21) for f in range(36, 71)
               if m.flow_lift_factor(float(o), float(f)) > 1.0 + 1e-12)
dhw_inv = sum(1 for o in range(-20, 21)
              if m.compute_cop_dhw(float(o), 55.0) > m.compute_cop_dhw(float(o), 40.0) + 1e-12)
print("RESULT A.lift_gt1=%d of %d" % (lift_gt1, 41 * 35))
print("RESULT A.lift_at_out0_flow60=%.4f" % m.flow_lift_factor(0.0, 60.0))
print("RESULT A.dhw55_gt_dhw40=%d of 41" % dhw_inv)
print("RESULT A.cop_dhw(0;35/55/60)=%.3f/%.3f/%.3f" % tuple(m.compute_cop_dhw(0.0, t) for t in (35.0, 55.0, 60.0)))
# B: emitter. mix [10,40] x zone [15,25] at 1 K, ua=0.4: count negative deliveries.
neg = sum(1 for x in range(10, 41) for z in range(15, 26)
          if mv.emitter_delivery(mix_temp=float(x), zone_temp=float(z), ua=0.4) < 0)
print("RESULT B.emitter_negative=%d of %d" % (neg, 31 * 11))
# C: presets. (structure, foundation, area 100/180): cells where derive(low_energy) loss >= post_2005.
inv = cells = 0
rat = []
for s in ps.STRUCTURES:
    for fnd in ps.FOUNDATIONS:
        for a in (100.0, 180.0):
            L = {e: ps.derive(ps.BuildingPreset(structure=s, era=e, foundation=fnd, heated_area_m2=a))[
                "house_heat_loss_coefficient"] for e in ps.ERAS}
            cells += 1
            inv += L[ps.ERA_LOW_ENERGY] >= L[ps.ERA_POST_2005]
            rat.append(L[ps.ERA_LOW_ENERGY] / L[ps.ERA_POST_2005])
print("RESULT C.low_energy_ge_post2005=%d of %d ratio=%.3f..%.3f" % (inv, cells, min(rat), max(rat)))
# D: defrost. duty 0.01..0.30: count derate_from_duty(d) >= 1 (no derate at a positive duty).
nod = sum(1 for k in range(1, 31) if df.derate_from_duty(k / 100) >= 1.0)
print("RESULT D.no_derate_at_positive_duty=%d of 30; derate(0.2)=%.3f" % (nod, df.derate_from_duty(0.2)))
# E: modulation. levels_clamped / probe_install.on_off for each declaration.
for mode in ("auto", "on_off", "modulating"):
    cfg = {const.CONF_COMPRESSOR_MODULATION: mode}
    print("RESULT E.%s declared=%s levels_clamped=%s probe_on_off=%s"
          % (mode, tm.declared_modulation(cfg), tm.levels_clamped(cfg), tm.probe_install(cfg).on_off))
