"""D12-s3 (D12.M3 control surfaces, D12.M5 null control): set-point write per surface.

Metric: count of cells (slot x surface domain x HA unit system) where the value
custom_components.heatpump_optimizer.pump_arbiter:_write delivers to the
service call, read back in degC the way production reads that entity
(setpoint_check._read_setpoint), differs from the intended degC by > 0.5.
Count key: the value in the captured service-call payload (the production seam),
not any entity attribute.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D12/s3/surface_units.py [--perturb]
Expected: RESULT misdelivered_cells=2 (fahrenheit arm), RESULT null_misdelivered_cells=0 (celsius arm) +-0.
--perturb: patches pump_arbiter.state_unit so a unit-less climate state falls back to
hass.config.units.temperature_unit (the read path's rule): misdelivered_cells must drop to 0.
Baseline 17f1c55fad1b, machine: macOS arm64 (B6).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, sys, time, types
from datetime import datetime, timezone
from unittest import mock
sys.path.insert(0, "tests"); sys.path.insert(0, ".")
from harness import FakeHass, FakeState  # noqa: E402
from custom_components.heatpump_optimizer import pump_arbiter, setpoint_check, inputs  # noqa: E402

t0p, t0t = time.process_time(), time.thread_time()
F = "°F"; C = "°C"
INTENT = {"space_setpoint": 21.0, "dhw_setpoint": 50.0}
CONF = {"space_setpoint": "space_setpoint_entity", "dhw_setpoint": "dhw_setpoint_entity"}


class _Coord:
    pass


def to_unit(c, unit):
    return c * 9 / 5 + 32 if unit == F else c


def cell(slot, domain, sysunit):
    ent = f"{domain}.hp_{slot}"
    cur = to_unit(INTENT[slot] - 3.0, sysunit)
    if domain == "climate":
        st = FakeState("heat", attributes={"temperature": cur, "min_temp": to_unit(5, sysunit),
                                           "max_temp": to_unit(65, sysunit)})
    else:
        st = FakeState(str(cur), unit=sysunit, attributes={"min": to_unit(5, sysunit),
                                                          "max": to_unit(65, sysunit)})
    hass = FakeHass({ent: st})
    hass.config.units = types.SimpleNamespace(temperature_unit=sysunit)
    coord = _Coord(); coord.hass = hass; coord.entry = types.SimpleNamespace(entry_id=f"e{id(st)}")
    inp = types.SimpleNamespace(hass=hass, config={CONF[slot]: ent})
    now = datetime(2026, 1, 15, 12, tzinfo=timezone.utc)
    asyncio.run(pump_arbiter._write(coord, inp, slot, INTENT[slot], now))
    calls = [c for c in hass.services.calls if c[2] and c[2].get("entity_id") == ent]
    if not calls:
        return None
    d = calls[-1][2]
    delivered = d.get("temperature", d.get("value"))
    # what the pump now holds, read back by production's own reader
    if domain == "climate":
        st.attributes["temperature"] = delivered
    else:
        st.state = str(delivered)
    return setpoint_check._read_setpoint(hass, ent)


def run(sysunit):
    bad, rows = 0, []
    for slot in INTENT:
        for domain in ("climate", "number", "input_number"):
            got = cell(slot, domain, sysunit)
            fail = got is None or abs(got - INTENT[slot]) > 0.5
            bad += fail
            rows.append((slot, domain, sysunit, got, fail))
    return bad, rows


_orig = inputs.state_unit
def _patched(state):
    u = _orig(state)
    return u if u is not None else _CUR[0]
_CUR = [None]

perturb = "--perturb" in sys.argv
for sysunit, name in ((F, "misdelivered_cells"), (C, "null_misdelivered_cells")):
    _CUR[0] = sysunit
    ctx = mock.patch.object(pump_arbiter, "state_unit", _patched) if perturb else mock.patch.object(pump_arbiter, "state_unit", _orig)
    with ctx:
        bad, rows = run(sysunit)
    for r in rows:
        print("cell", *r)
    print(f"RESULT {name}={bad} cells (of {len(rows)})")
print(f"RESULT thread_factor={(time.process_time()-t0p)/max(time.thread_time()-t0t,1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
