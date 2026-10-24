"""Lead L2 (catch-up verifier, group `leads`): pump_arbiter._bounded reads the range
keys `min`/`max`, which a number/input_number state carries, but a climate state
carries `min_temp`/`max_temp` (homeassistant.components.climate.const ATTR_MIN_TEMP /
ATTR_MAX_TEMP, 2026.9.3). config_flow offers climate for both arbiter set-point slots
(CONF_SPACE_SETPOINT_ENTITY, CONF_DHW_SETPOINT_ENTITY: number, input_number, climate).

Metric: out-of-range commands, counted over 4 commanded values {3, 10, 55, 70} degC
against an entity range [7, 50] degC: a returned value outside the range.
Arms: climate state {min_temp: 7, max_temp: 50}.
Null: number state {min: 7, max: 50, unit_of_measurement: degC} -> 0.
Second arm (reach to the arbiter's own entry point): pump_arbiter.desired() for duty
'dhw' with the dhw slot a climate entity and params.dhw_setpoint=55 -> dhw command.
Perturbation (in memory): _bounded's two reads fall back to min_temp/max_temp -> 0.
Expected: arm 2 of 4 (55, 70; the floor arg -1e9 leaves 3 unclamped too, so 3 of 4),
null 0, perturbed 0.
Command (tree root): PYTHONPATH=tests/hastub:custom_components python dev/audit/rounds/round10/catchup/leads/l2_bounded_climate.py
Baseline: origin/main d749c986d. Machine: tvofi mac, 8 cores, not timing-sensitive.
"""
import inspect
import textwrap
from types import SimpleNamespace

from heatpump_optimizer import pump_arbiter as pa

LO, HI = 7.0, 50.0
VALUES = (3.0, 10.0, 55.0, 70.0)
CLIMATE = SimpleNamespace(state="heat", attributes={"min_temp": LO, "max_temp": HI, "temperature": 45})
NUMBER = SimpleNamespace(state="45", attributes={"min": LO, "max": HI, "unit_of_measurement": "°C"})


def count(fn, state):
    out = [fn(state, v) for v in VALUES]
    return sum(1 for o in out if o < LO or o > HI), out


def perturbed():
    src = textwrap.dedent(inspect.getsource(pa._bounded))
    src = src.replace('attrs.get("min")', 'attrs.get("min", attrs.get("min_temp"))', 1)
    src = src.replace('attrs.get("max")', 'attrs.get("max", attrs.get("max_temp"))', 1)
    ns = dict(vars(pa))
    exec(src, ns)
    return ns["_bounded"]


for label, fn in (("main", pa._bounded), ("perturbed", perturbed())):
    for name, st in (("arm_climate", CLIMATE), ("null_number", NUMBER)):
        n, out = count(fn, st)
        print(f"RESULT {label} {name} out_of_range={n} of {len(VALUES)} returned={out}")

# Reach: the arbiter's own desired() builds the DHW write through _bounded.
cfg = {"dhw_setpoint_entity": "climate.dhw", "heat_pump_mode_entity": None,
       "space_setpoint_entity": None}
hass = SimpleNamespace(states=SimpleNamespace(get=lambda e: CLIMATE if e == "climate.dhw" else None))
inp = SimpleNamespace(config=cfg, hass=hass, params=SimpleNamespace(dhw_setpoint=55.0),
                      plan=None, disinfecting=False)
from datetime import datetime, timezone
now = datetime(2026, 10, 15, 12, tzinfo=timezone.utc)
orig = pa._bounded
for label, fn in (("main", orig), ("perturbed", perturbed())):
    pa._bounded = fn
    try:
        cmd = pa.desired(None, inp, "dhw", now)
    finally:
        pa._bounded = orig
    print(f"RESULT {label} reach_desired_dhw_slot_climate command.dhw={cmd.dhw_setpoint} outside_range={int(cmd.dhw_setpoint > HI)}")
