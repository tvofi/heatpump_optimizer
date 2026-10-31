#!/usr/bin/env python3
"""arch-s6 catch-up verifier, V2 for D7-s6-91 / D12-s3-01: real Home Assistant as the oracle.

Stage 1 (seat venv, FakeHass): drive the production pump_arbiter._write for slot dhw_setpoint with
55.0 degC against climate.dhw whose target attribute reads 122 (degF instance) and capture the
service payload value. Stage 2 (real-HA venv, ~/.local/state/hpo/venv-ha): build a real
HomeAssistant core with US-customary units, a real ClimateEntity subclass whose temperature_unit is
degC (a pump reporting in Celsius), and push the captured payload through HA's own
climate.async_service_temperature_set; read the target the device receives (degC).
Metric:   delivered_error_K = |device_target_C - 55.0|; plus reach facts: the climate entity's
          unit_of_measurement, and whether 'unit_of_measurement' is in its state/capability attrs.
Null:     same with a metric-units instance (payload captured with a degC instance): error 0.
Command:  cd TREE && PYTHONPATH=tests/hastub:tests:custom_components python3 realha_climate.py
          (stage 2 is spawned with the real-HA venv automatically).
Expected: main d749c986d -> imperial error 42.222, metric 0.000; P2 tree -> 0.000 / 0.000.
"""
import asyncio, json, os, subprocess, sys
from datetime import datetime, timezone
from types import SimpleNamespace

HA_PY = os.path.expanduser("~/.local/state/hpo/venv-ha/bin/python")


def stage1(instance_unit, attr):
    sys.path[:0] = ["tests/hastub", "tests", "custom_components"]
    from harness import FakeHass, FakeState
    from heatpump_optimizer import pump_arbiter as pa
    from heatpump_optimizer.entry_config import EntryConfig

    class C(SimpleNamespace):
        __hash__ = object.__hash__
    st = FakeState("heat", attributes={"temperature": attr})
    hass = FakeHass({"climate.dhw": st})
    hass.config.units = SimpleNamespace(temperature_unit=instance_unit)
    cfg = EntryConfig.from_mapping({"pump_duty_mode": "control", "dhw_setpoint_entity": "climate.dhw"})
    coord = C(hass=hass, entry=SimpleNamespace(entry_id=f"v2{instance_unit}"))
    asyncio.run(pa._write(coord, SimpleNamespace(hass=hass, config=cfg), "dhw_setpoint", 55.0,
                          datetime(2026, 1, 10, 6, tzinfo=timezone.utc)))
    calls = [c for c in hass.services.calls if (c[2] or {}).get("entity_id") == "climate.dhw"]
    return calls[-1][2]["temperature"] if calls else None


STAGE2 = r'''
import asyncio, json, sys, tempfile
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.util.unit_system import US_CUSTOMARY_SYSTEM, METRIC_SYSTEM
from homeassistant.components import climate
from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature, HVACMode
from homeassistant.const import UnitOfTemperature, ATTR_TEMPERATURE

class Pump(ClimateEntity):
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_hvac_modes = [HVACMode.HEAT]
    _attr_hvac_mode = HVACMode.HEAT
    _attr_min_temp = 5; _attr_max_temp = 70
    _attr_target_temperature = 50.0
    async def async_set_temperature(self, **kw):
        self._attr_target_temperature = kw[ATTR_TEMPERATURE]

async def run(imperial, payload):
    with tempfile.TemporaryDirectory() as d:
        hass = HomeAssistant(d)
        hass.config.units = US_CUSTOMARY_SYSTEM if imperial else METRIC_SYSTEM
        e = Pump(); e.hass = hass; e.entity_id = "climate.dhw"
        attrs = {**(e.capability_attributes or {}), **(e.state_attributes or {})}
        call = ServiceCall(hass, "climate", "set_temperature", {ATTR_TEMPERATURE: payload})
        await climate.async_service_temperature_set(e, call)
        out = dict(uom=e.unit_of_measurement, uom_in_attrs="unit_of_measurement" in attrs,
                   attr_temperature=attrs.get("temperature"), device_C=e.target_temperature)
        await hass.async_stop(force=True)
        return out

imperial, payload = sys.argv[1] == "1", float(sys.argv[2])
print(json.dumps(asyncio.run(run(imperial, payload))))
'''

if __name__ == "__main__":
    import time
    t0p, t0t = time.process_time(), time.thread_time()
    for name, unit, attr, imperial in (("imperial", "°F", 122.0, "1"), ("null_metric", "°C", 50.0, "0")):
        payload = stage1(unit, attr)
        r = json.loads(subprocess.run([HA_PY, "-c", STAGE2, imperial, str(payload)], check=True,
                                      capture_output=True, text=True, cwd="/").stdout.strip().splitlines()[-1])
        print(f"RESULT {name}: payload={payload} device_C={r['device_C']:.3f} "
              f"delivered_error_K={abs(r['device_C'] - 55.0):.3f} climate_uom={r['uom']} "
              f"uom_in_attrs={r['uom_in_attrs']} attr_temperature_shown={r['attr_temperature']}")
    print(f"RESULT thread_factor={(time.process_time()-t0p)/max(time.thread_time()-t0t,1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
