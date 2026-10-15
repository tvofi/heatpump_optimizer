"""Probe for sweep-P8 seam coordinator._command_valve_target (both arms).

Drives the real method with a fake self on a FakeHass and reads the captured
service-call payload back in degC the way production reads a set-point
(setpoint_check._read_setpoint, instance-unit fallback for climate).
Cells: domain {climate, number} x unit system {degC, degF}; target 45 degC.
Metric: cells whose read-back differs from 45 degC by > 0.5.
Expected at 9355f107d: RESULT misdelivered=2 (degF arm), null degC arm 0.
--perturb: convert the payload with temperature_from_c and the
_setpoint_and_unit unit (the read path's rule) -> 0.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/sweep-P8/p8_valve_probe.py [--perturb]
"""
import asyncio, sys, types
from unittest import mock
sys.path.insert(0, "tests"); sys.path.insert(0, ".")
from harness import FakeHass, FakeState  # noqa: E402
from custom_components.heatpump_optimizer import coordinator as co, setpoint_check, inputs, mixing_valve  # noqa: E402

F, C, T = "°F", "°C", 45.0
PERTURB = "--perturb" in sys.argv


def to_unit(c, u):
    return c * 9 / 5 + 32 if u == F else c


def cell(domain, sysunit):
    ent = f"{domain}.valve"
    st = (FakeState("heat", attributes={"temperature": to_unit(40, sysunit)}) if domain == "climate"
          else FakeState(str(to_unit(40, sysunit)), unit=sysunit))
    hass = FakeHass({ent: st})
    hass.config.units = types.SimpleNamespace(temperature_unit=sysunit)
    params = types.SimpleNamespace(mixing_valve_mode=mixing_valve.MODE_SMART_WRITE,
                                   mixing_valve_target=T, comfort_ceiling=T, two_zone_enabled=False)
    cfg = types.SimpleNamespace(mixing_valve_write_entity=ent, mixing_valve_write_target_kind=None)
    me = types.SimpleNamespace(hass=hass, _thermal_params=params, _config=cfg, _mode="auto",
                               _current_action={}, _valve_commanded_target=None)
    me._ctx = me
    orig = hass.services.async_call
    if PERTURB:
        async def conv(d, s, data, **kw):
            unit = setpoint_check._setpoint_and_unit(hass, ent)[1]
            k = "temperature" if "temperature" in data else "value"
            data = {**data, k: round(inputs.temperature_from_c(data[k], unit), 1)}
            return await orig(d, s, data, **kw)
        hass.services.async_call = conv
    asyncio.run(co.HeatPumpOptimizerCoordinator._command_valve_target(me))
    calls = [c for c in hass.services.calls if c[2] and c[2].get("entity_id") == ent]
    d = calls[-1][2]
    v = d.get("temperature", d.get("value"))
    if domain == "climate":
        st.attributes["temperature"] = v
    else:
        st.state = str(v)
    back = setpoint_check._read_setpoint(hass, ent)
    return abs(back - T) > 0.5, v, back


bad = {C: 0, F: 0}
for u in (C, F):
    for dom in ("climate", "number"):
        mis, v, back = cell(dom, u)
        bad[u] += mis
        print(f"CELL {dom} {u} delivered={v} readback_c={back:.1f} {'MISDELIVERED' if mis else 'ok'}")
print(f"RESULT misdelivered={bad[F]}")
print(f"RESULT null_misdelivered={bad[C]}")
