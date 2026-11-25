import numpy as np
from custom_components.heatpump_optimizer.external_heat import ExternalHeatObservation
OLD, NEW = "if not self._external_heat.suppressing:", "if False:"
MUT = mutant_method("_external_heat_forecast", OLD, NEW)
T0 = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)


def obs(i, override, **kw):
    base = dict(now=T0 + timedelta(minutes=30 * i), dhw_temp=None, buffer_temp=None, commanded_power_kw=0.0,
                measured_power_kw=0.0, override=override, outlet_temp=60.0, wood_top=80.0, wood_bottom=70.0,
                hp_tank_temp=40.0, space_demand_kw=5.0)
    base.update(kw)
    return ExternalHeatObservation(**base)


def states():
    """Detector states where suppressing is False, reached through update() alone."""
    out = {}
    c = coord(wood_furnace_enabled=True, external_heat_detection_enabled=True)
    c._external_heat.config.enabled = True
    out["fresh"] = c
    c = coord(wood_furnace_enabled=True, external_heat_detection_enabled=True)
    c._external_heat.config.enabled = True
    c._external_heat.update(obs(0, True))            # fire on, displacement > 0
    c._external_heat.update(obs(1, False))           # user says off: deactivate -> fading
    for i in range(2, 12):                            # 5 h later: decay over
        c._external_heat.update(obs(i, False))
    out["after_fire_decayed"] = c
    c = coord(wood_furnace_enabled=True, external_heat_detection_enabled=True)
    c._external_heat.config.enabled = True
    c._external_heat.update(obs(0, True))
    c._external_heat.config.enabled = False
    c._external_heat.update(obs(1, None))            # disabled: _reset
    out["disabled_after_fire"] = c
    c = coord(wood_furnace_enabled=True, external_heat_detection_enabled=True)
    c._external_heat.config.enabled = True
    c._external_heat.update(obs(0, False))
    out["override_off"] = c
    return out


moved = 0
for name, c in states().items():
    sup = c._external_heat.suppressing
    b, m = CLS._external_heat_forecast(c, 96), MUT(c, 96)
    same = (b is None and m is None) or (b is not None and m is not None and np.array_equal(b, m))
    moved += int(not same)
    print(f"RESULT {name} suppressing={sup} free_heat_kw={c._external_heat.state.free_heat_kw} "
          f"baseline={'None' if b is None else 'array'} mutant={'None' if m is None else 'array'}")
# positive arm: suppressing with free heat -- the guard is not consulted, both arms build the array
c = coord(wood_furnace_enabled=True, external_heat_detection_enabled=True)
c._external_heat.config.enabled = True
c._external_heat.update(obs(0, True))
b, m = CLS._external_heat_forecast(c, 96), MUT(c, 96)
print(f"RESULT positive_suppressing sum_baseline={float(np.sum(b)):.4f} sum_mutant={float(np.sum(m)):.4f} kW")
print(f"RESULT moved_states={moved} count")
tail()
