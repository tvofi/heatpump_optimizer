"""D12-own-01 -- verifier seat 1 (panel D12-0, round 4), independent harness
for finding D12-01.  Written beside the finder's units.py; it shares the cell
builder (cells.py) and the coordinator builder (d12lib.build) but NOT the
finder's metric or its adoption evidence.

METRIC (one line): the number of DISTINCT configured input slots that publish
a non-metric ``unit_of_measurement`` (degF / Wh) AND whose RAW numeric state
is found verbatim among the values the coordinator adopted (published data
dict, current thermal state, thermal params, private measured fields) after
one full cycle -- i.e. misadoption proven from the coordinator's own state,
not from a read-return log -- together with the published plan's total heating
kWh, zero-power step count, repairs raised (hass.issues) and unavailable
entity count on the same plant driven twice (Celsius arm = null control).

RUN (from the repository root):

    PYTHONPATH=tests/hastub:tools/audit/round4/D12 \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D12/d12_own_01.py           # celsius + imperial + small plant
    ... d12_own_01.py --fix                          # + one-line production fix arm

EXPECTED at the baseline (counts and published values -- immune to box load):
  own_celsius_slots_misadopted=0, own_celsius_plan_kwh=4.752,
  own_imperial_slots_misadopted=9 (the finder's call-count metric says 10:
  wood_tank_top_entity is read twice -- coordinator.py:3247 and :5026),
  own_imperial_indoor_c=70.5, own_imperial_plan_kwh=0.0,
  own_imperial_plan_steps=96, own_imperial_zero_power_steps=96,
  own_imperial_repairs_raised=own_celsius_repairs_raised,
  own_imperial_entities_unavailable=own_celsius_entities_unavailable,
  own_small_imperial_slots_misadopted=4 (independent plant-shrink direction),
  own_fix_imperial_slots_misadopted=0 and own_fix_imperial_plan_kwh~=4.75.
  Tolerance exact on the counts, +-0.1 on the degC / kWh.
BASELINE: 7dd68dd327fe3dbfb09f3bd0fe38910c58877697 (tree under review is the
  branch head; production delta vs baseline is two version-string bumps).
MACHINE: 8-core Apple M1, 8 GB, macOS 25.6.0 (audit box, shared).
INSTRUMENTED SYMBOL: heatpump_optimizer.inputs:InputReader.read -- wrapped at
  the class level purely to emit the finder-comparable call-count; the metric
  above is computed from the coordinator's adopted state, NOT the spy log.
PERTURBATION: --fix installs the one-line conversion production does not have
  (degF->degC and Wh->kWh in InputReader.read): misadopted must fall 9 -> 0
  and plan kWh 0.0 -> ~4.75 (the Celsius arm's own value, modulo the 1-decimal
  rounding of the degF states).  The small-plant arm is the plant-shrink
  perturbation: the count must move 9 -> 4.
NULL CONTROL: the Celsius arm of the same harness, printed beside it.
"""
from __future__ import annotations

import asyncio  # noqa: E402
import sys  # noqa: E402

import d12lib  # noqa: F401  (thread pin before numpy, sys.path inserts)
from d12lib import PLATFORMS  # noqa: E402
import cells as cellmod  # noqa: E402
from harness import FakeState  # noqa: E402

from heatpump_optimizer import inputs as inputs_mod  # noqa: E402

TEMPERATURE_OK = {"°C", "C"}
ENERGY_OK = {"kWh"}
SUSPECT_UNITS = {"°F", "Wh"}


def _truth(raw: float, unit: str) -> float:
    """What the coordinator SHOULD have adopted for this raw state."""
    if unit == "°F":
        return (raw - 32.0) * 5.0 / 9.0
    if unit == "Wh":
        return raw / 1000.0
    return raw


def imperialise(states):
    """The same physical plant in degF/Wh, as a US-customary HA state machine."""
    out = {}
    for eid, st in states.items():
        unit = (st.attributes or {}).get("unit_of_measurement")
        if unit in TEMPERATURE_OK:
            f = round(float(st.state) * 9.0 / 5.0 + 32.0, 1)
            out[eid] = FakeState(str(f), unit="°F")
        elif unit in ENERGY_OK:
            out[eid] = FakeState(str(float(st.state) * 1000.0), unit="Wh")
        else:
            out[eid] = st
    return out


def _floats(obj, seen=None):
    """Every float reachable in a nested dict/list/dataclass structure."""
    if seen is None:
        seen = set()
    if id(obj) in seen:
        return
    seen.add(id(obj))
    if isinstance(obj, float):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from _floats(v, seen)
    elif isinstance(obj, (list, tuple, set)):
        for v in obj:
            yield from _floats(v, seen)
    else:
        for v in vars(obj).values() if hasattr(obj, "__dict__") else ():
            yield from _floats(v, seen)


#: Independent small plant: BASE + DHW + four mapped slots only.
SMALL_EXTRA = {
    "indoor_temp_entity": "sensor.own_indoor",
    "outdoor_temp_entity": "sensor.own_outdoor",
    "dhw_temp_entity": "sensor.own_dhw",
    "heat_pump_energy_entity": "sensor.own_energy",
}


def arm(name, cfg, states, fix=False):
    """Drive one arm; return (adopted-surfaces float pool, data, hass facts)."""
    spy_log = []
    real_read = inputs_mod.InputReader.read

    def spy(self, key, **kw):
        reading = real_read(self, key, **kw)
        st = self.hass.states.get(reading.entity_id) if reading.entity_id else None
        unit = (getattr(st, "attributes", None) or {}).get("unit_of_measurement") if st else None
        if reading.value is not None:
            spy_log.append((key, unit, reading.value))
        return reading

    def fixed(self, key, **kw):
        reading = spy(self, key, **kw)
        st = self.hass.states.get(reading.entity_id) if reading.entity_id else None
        unit = (getattr(st, "attributes", None) or {}).get("unit_of_measurement") if st else None
        if reading.value is not None and unit in SUSPECT_UNITS:
            reading.value = _truth(reading.value, unit)
        return reading

    inputs_mod.InputReader.read = fixed if fix else spy
    try:
        hass, entry, coord = d12lib.build(cfg, states)
        d12lib.dt_util.freeze(d12lib.START)

        async def _cycle():
            await coord._update_current_state()
            status = await coord.async_run_optimization()
            coord.data = coord._build_data_dict()
            return status

        status = asyncio.run(_cycle())
        data = coord.data

        # The adopted-value pool: published data, the thermal state, the
        # thermal params, and the coordinator's private measured fields.
        pool = set()
        for surface in (data, coord._current_state, coord._thermal_params):
            for v in _floats(surface):
                pool.add(round(v, 6))
        for attr in ("_measured_energy", "_dhw_temperature", "_floor_return_temp",
                     "_solar_radiation", "_measured_power"):
            v = getattr(coord, attr, None)
            if isinstance(v, float):
                pool.add(round(v, 6))

        # Platform setup: unavailable count + the published indoor sensor.
        entry.runtime_data = coord
        unavailable = 0
        published = {}
        for pname, module in PLATFORMS:
            added = []
            try:
                asyncio.run(module.async_setup_entry(hass, entry, added.extend))
            except Exception:  # noqa: BLE001
                unavailable += 0
                continue
            for entity in added:
                try:
                    avail = bool(entity.available)
                except Exception:  # noqa: BLE001
                    unavailable += 1
                    continue
                if not avail:
                    unavailable += 1
                published[getattr(entity, "_key", type(entity).__name__)] = entity
        return {
            "name": name, "status": status, "data": data, "pool": pool,
            "hass": hass, "unavailable": unavailable, "published": published,
            "spy": spy_log,
        }
    finally:
        inputs_mod.InputReader.read = real_read
        d12lib.dt_util.freeze(None)


def slot_facts(cfg, states):
    """(slot, entity_id, unit, raw, truth) for every configured *_entity slot."""
    facts = []
    for key, eid in sorted(cfg.items()):
        if not key.endswith("_entity") or not isinstance(eid, str):
            continue
        st = states.get(eid)
        if st is None:
            continue
        try:
            raw = float(st.state)
        except (TypeError, ValueError):
            continue
        unit = (st.attributes or {}).get("unit_of_measurement")
        facts.append((key, eid, unit, raw, _truth(raw, unit) if unit in SUSPECT_UNITS else raw))
    return facts


def report(name, r, cfg, states):
    facts = slot_facts(cfg, states)
    misadopted, unproven, converted = [], [], []
    for key, eid, unit, raw, truth in facts:
        if unit not in SUSPECT_UNITS:
            continue
        if round(raw, 6) in r["pool"]:
            misadopted.append((key, unit, raw))
        elif round(truth, 6) in r["pool"]:
            converted.append((key, unit, truth))
        else:
            unproven.append((key, unit, raw))
    data = r["data"] or {}
    sched = data.get("schedule") or []
    kwh = sum(float(s.get("power", 0.0) or 0.0) * 0.25 for s in sched)
    zeros = sum(1 for s in sched if not float(s.get("power", 0.0) or 0.0))
    repairs = len(getattr(r["hass"], "issues", None) or [])
    calls_misread = sum(
        1 for key, unit, value in r["spy"]
        if unit in SUSPECT_UNITS and value is not None
    )
    indoor = data.get("indoor_temperature")
    print(f"RESULT own_{name}_slots_misadopted={len(misadopted)} count")
    print(f"RESULT own_{name}_read_calls_misread={calls_misread} count")
    print(f"RESULT own_{name}_slots_converted={len(converted)} count")
    print(f"RESULT own_{name}_indoor_c={indoor} degC")
    print(f"RESULT own_{name}_plan_kwh={round(kwh, 3)} kWh")
    print(f"RESULT own_{name}_plan_steps={len(sched)} count")
    print(f"RESULT own_{name}_zero_power_steps={zeros} count")
    print(f"RESULT own_{name}_solve_status={r['status']!r}")
    print(f"RESULT own_{name}_repairs_raised={repairs} count")
    print(f"RESULT own_{name}_entities_unavailable={r['unavailable']} count")
    for key, unit, raw in sorted(misadopted):
        print(f"  misadopted {name}: {key:32s} unit={unit!r:6s} raw_adopted={raw}")
    for key, unit, raw in sorted(unproven):
        print(f"  unproven   {name}: {key:32s} unit={unit!r:6s} raw={raw}")
    # The statistics attack: the published indoor sensor's class/availability.
    for k, entity in r["published"].items():
        if "indoor" in str(k):
            dc = getattr(entity, "_attr_device_class", None)
            sc = getattr(entity, "_attr_state_class", None)
            try:
                val = entity.native_value
                avail = bool(entity.available)
            except Exception:  # noqa: BLE001
                val = avail = None
            print(f"  indoor sensor {k}: device_class={getattr(dc, 'value', dc)} "
                  f"state_class={getattr(sc, 'value', sc)} value={val} available={avail}")
            break
    print()
    return misadopted


def main(argv):
    fix = "--fix" in argv

    cfg_full, states_c = cellmod.fully_mapped()
    states_f = imperialise(states_c)

    r_c = arm("celsius", cfg_full, states_c)
    report("celsius", r_c, cfg_full, states_c)                       # NULL CONTROL
    r_f = arm("imperial", cfg_full, states_f)
    report("imperial", r_f, cfg_full, states_f)
    if fix:                                                          # PERTURBATION 1
        r_fix = arm("fix_imperial", cfg_full, states_f, fix=True)
        report("fix_imperial", r_fix, cfg_full, states_f)

    # PERTURBATION 2 (plant shrink, independent of the finder's drop list):
    # BASE + DHW + four mapped slots.
    cfg_small = dict(cellmod.BASE)
    cfg_small.update(cellmod.DHW_ON)
    cfg_small.update(SMALL_EXTRA)
    states_small_c = {
        SMALL_EXTRA["indoor_temp_entity"]: FakeState("21.4", unit="°C"),
        SMALL_EXTRA["outdoor_temp_entity"]: FakeState("-3.0", unit="°C"),
        SMALL_EXTRA["dhw_temp_entity"]: FakeState("52.0", unit="°C"),
        SMALL_EXTRA["heat_pump_energy_entity"]: FakeState("1234.5", unit="kWh"),
    }
    r_s = arm("small_imperial", cfg_small, imperialise(states_small_c))
    report("small_imperial", r_s, cfg_small, imperialise(states_small_c))

    print("RESULT thread_factor=1.0")
    print(f"RESULT load1={d12lib.load1()}")
    print(f"RESULT swapins={d12lib.swapins()}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
