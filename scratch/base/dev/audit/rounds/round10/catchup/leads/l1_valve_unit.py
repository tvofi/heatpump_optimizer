"""Lead L1 (catch-up verifier, group `leads`): smart_write commands the valve target
without unit conversion.

Metric: abs error (in the entity's own unit) between the number
`HeatPumpOptimizerCoordinator._command_valve_target` passes to the service and the
target expressed in the unit Home Assistant interprets that service value in
(climate.set_temperature: hass.config.units.temperature_unit, per
homeassistant/components/climate/__init__.py 2026.9.3; number/input_number.set_value: the
entity's declared unit_of_measurement). One target, 21.0 degC.
Arms: climate entity on a degF instance; number entity declaring degF on a degC instance.
Null: climate on a degC instance, number declaring degC -> 0.
Perturbation (in memory, exec of the method source with one line added): convert the
target with inputs.temperature_from_c in the unit HA reads it in before the write ->
both arms 0.
Expected: arms > 0 at main, null 0, perturbed 0.
Command (tree root): PYTHONPATH=tests/hastub:custom_components python dev/audit/rounds/round10/catchup/leads/l1_valve_unit.py
Baseline: origin/main d749c986d. Machine: tvofi mac, 8 cores, not timing-sensitive.
"""
import asyncio
import inspect
import textwrap
from types import SimpleNamespace

from heatpump_optimizer import coordinator as cmod
from heatpump_optimizer import mixing_valve
from heatpump_optimizer.inputs import temperature_from_c

TARGET_C = 21.0


class Services:
    def __init__(self):
        self.calls = []

    async def async_call(self, domain, service, data, blocking=False):
        self.calls.append((domain, service, data))


def fake(entity_id, instance_unit, entity_unit):
    attrs = {} if entity_unit is None else {"unit_of_measurement": entity_unit}
    state = SimpleNamespace(state="21" if entity_unit else "heat", attributes=attrs)
    hass = SimpleNamespace(
        services=Services(),
        config=SimpleNamespace(units=SimpleNamespace(temperature_unit=instance_unit)),
        states=SimpleNamespace(get=lambda e: state),
    )
    params = SimpleNamespace(
        mixing_valve_mode=mixing_valve.MODE_SMART_WRITE,
        mixing_valve_target=TARGET_C, comfort_ceiling=22.0, two_zone_enabled=False,
    )
    cfg = SimpleNamespace(mixing_valve_write_entity=entity_id,
                          mixing_valve_write_target_kind=mixing_valve.WRITE_TARGET_INDOOR)
    obj = SimpleNamespace(hass=hass, _mode="auto", _current_action={},
                          _valve_commanded_target=None)
    obj._ctx = SimpleNamespace(_thermal_params=params, _config=cfg)
    return obj


def expected(entity_id, instance_unit, entity_unit):
    unit = instance_unit if entity_id.startswith("climate.") else entity_unit
    return round(temperature_from_c(TARGET_C, unit), 1)


ARMS = [
    ("arm_climate_on_degF_instance", "climate.valve", "°F", None),
    ("arm_number_degF_on_degC_instance", "number.valve", "°C", "°F"),
    ("null_climate_on_degC_instance", "climate.valve", "°C", None),
    ("null_number_degC", "number.valve", "°C", "°C"),
]


def run(method, label):
    for name, eid, inst, ent in ARMS:
        obj = fake(eid, inst, ent)
        asyncio.run(method(obj))
        domain, service, data = obj.hass.services.calls[-1]
        written = data.get("temperature", data.get("value"))
        exp = expected(eid, inst, ent)
        print(f"RESULT {label} {name} written={written} expected={exp} abs_err={abs(written - exp):.1f}")


def perturbed():
    src = textwrap.dedent(inspect.getsource(cmod.HeatPumpOptimizerCoordinator._command_valve_target))
    anchor = '    domain = entity_id.split(".", 1)[0]\n'
    assert anchor in src, "anchor moved"
    fix = ('    _st = self.hass.states.get(entity_id); target = _tfc(target, '
           'self.hass.config.units.temperature_unit if entity_id.startswith("climate.") '
           'else (_st.attributes or {}).get("unit_of_measurement"))\n')
    src = src.replace(anchor, fix + anchor, 1)
    ns = dict(vars(cmod))
    ns["_tfc"] = temperature_from_c
    exec(src, ns)
    return ns["_command_valve_target"]


run(cmod.HeatPumpOptimizerCoordinator._command_valve_target, "main")
run(perturbed(), "perturbed")

# Sibling site (not L1 itself): the arbiter's set-point write at main converts with
# state_unit(state), which a climate state never declares, so a climate slot on a degF
# instance gets degC too. arch3-s6 replaces it with inputs.write_setpoint_c (hass units).
from heatpump_optimizer import pump_arbiter as pa  # noqa: E402
from heatpump_optimizer.inputs import state_unit  # noqa: E402

class Coord:
    pass


for inst in ("°F", "°C"):
    base = fake("climate.space", inst, None)
    obj = Coord()
    obj.hass = base.hass
    st = obj.hass.states.get("climate.space")

    async def go():
        held = pa.state_for(obj)
        held.written.clear()
        inp = SimpleNamespace(config={"space_setpoint_entity": "climate.space"}, hass=obj.hass)
        orig = pa._persist
        async def _np(c):
            return None
        pa._persist = _np
        try:
            await pa._write(obj, inp, "space_setpoint", TARGET_C, None)
        finally:
            pa._persist = orig
    try:
        asyncio.run(go())
        written = obj.hass.services.calls[-1][2]["temperature"]
        exp = expected("climate.space", inst, None)
        print(f"RESULT sibling_arbiter_climate instance={inst} written={written} expected={exp} abs_err={abs(written - exp):.1f}")
    except Exception as err:  # noqa: BLE001
        print(f"RESULT sibling_arbiter_climate instance={inst} not_driven={type(err).__name__}: {err}")
