#!/usr/bin/env python3
"""D8-INST, verifier 1's own harness: the tests/hastub SensorEntity vacuity.

METRIC (mine): (a) does ``tests/hastub``'s ``SensorEntity`` (and anything it
inherits from) declare a ``device_class`` / ``state_class`` /
``entity_category`` property -- by ``inspect.getsource`` over every class in
the stub's MRO for a built entity; (b) over entities built through the real
``async_setup_entry``, how many have a non-None value via the PUBLIC
PROPERTY path vs the ``_attr_*`` path -- the property-path count is the
vacuity; (c) with a violation INJECTED into real production classes
(class-attribute swap, try/finally), does each of the four named checks
(enum_state_not_in_options, measurement_non_numeric, timestamp_naive,
unit_device_class_mismatch) fire through the ``_attr_*`` path while reading 0
through the property path; (d) ``entity_category_declared`` over a REDUCED
matrix -- 5 cells (5 topologies x the merged-all overlay) instead of the
finder's 75 -- via both paths.

COMMAND (from a tree root):

    PYTHONPATH=tests/hastub \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D8/d8_own_D8-INST.py

EXPECTED (baseline 7dd68dd and branch head 0855277; 8-core Apple M1):
    stub_property_declarations=0 properties          (0 of the 3 exist)
    property_path_dc_nonnone=0 property_path_sc_nonnone=0
    property_path_ec_nonnone=0                       (the vacuity)
    attr_path_ec_declared_per_cell=20  x5 cells = 100 (finder: 20 x 75 = 1500)
    injected x4: attr_path_fires=4 property_path_fires=0
All integers, deterministic, contention-immune.
"""
from __future__ import annotations

import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import asyncio  # noqa: E402
import datetime as _dt  # noqa: E402
import inspect  # noqa: E402
import sys  # noqa: E402
from datetime import timedelta  # noqa: E402
from pathlib import Path  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import numpy as np  # noqa: E402  (the coordinator pulls it; pin is above)

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

from golden import START, coordinator_scenarios  # noqa: E402

from heatpump_optimizer import sensor  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

#: The merged-all overlay, copied from entity_matrix.py's construction
#: (every one of its 14 named overlays merged).
STATE_TABLE = {
    "sensor.indoor": ("21.4", "°C"),
    "sensor.outdoor": ("-3.0", "°C"),
    "sensor.dhw_temp": ("52.0", "°C"),
    "sensor.upper": ("21.1", "°C"),
    "sensor.lower": ("20.6", "°C"),
    "sensor.buffer": ("41.0", "°C"),
    "sensor.wood_top": ("78.0", "°C"),
    "sensor.wood_bottom": ("44.0", "°C"),
    "sensor.pv_now": ("2.6", "kW"),
    "sensor.pump_freq": ("48.0", "Hz"),
    "number.pump_freq": ("48.0", "Hz"),
    "number.valve_target": ("34.0", "°C"),
    "select.pump_mode": ("heat", None),
    "binary_sensor.pump_defrost": ("off", None),
    "binary_sensor.pump_online": ("on", None),
    "binary_sensor.pump_fault": ("off", None),
    "input_boolean.holiday": ("off", None),
    "sensor.pump_power": ("2.20", "kW"),
    "sensor.pump_energy": ("1234.5", "kWh"),
    "sensor.house_power": ("3.90", "kW"),
    "sensor.floor_return": ("31.5", "°C"),
    "sensor.solar_rad": ("180.0", "W/m²"),
    "sensor.humidity": ("41.0", "%"),
}

ALL_OVERLAY = {
    "dhw_enabled": True,
    "dhw_tank_volume": 200.0,
    "dhw_setpoint": 55.0,
    "dhw_min_temperature": 45.0,
    "dhw_windows": "06:00-08:30, 17:00-22:00",
    "dhw_temp_entity": "sensor.dhw_temp",
    "upper_floor_thermal_mass": 3.0,
    "lower_floor_thermal_mass": 8.0,
    "upper_floor_heat_loss": 0.08,
    "lower_floor_heat_loss": 0.07,
    "upper_floor_temp_entity": "sensor.upper",
    "lower_floor_temp_entity": "sensor.lower",
    "mixing_valve_mode": "smart_write",
    "mixing_valve_write_entity": "number.valve_target",
    "buffer_tank_volume": 500.0,
    "buffer_tank_temp_entity": "sensor.buffer",
    "wood_tank_top_entity": "sensor.wood_top",
    "wood_tank_bottom_entity": "sensor.wood_bottom",
    "wood_tank_volume": 750.0,
    "topology_layout": "two_tank_4way",
    "dhw_wood_coil_enabled": True,
    "wood_furnace_enabled": True,
    "wood_type": "birch",
    "wood_price_sek_m3": 1200.0,
    "wood_furnace_efficiency": 0.75,
    "ecl110_state_topic": "ecl110/flow_temp_control/displace",
    "ecl110_displace_set_topic": "ecl110/flow_temp_control/displace/set",
    "ecl110_command_topic": "ecl110/command",
    "ecl110_displace_min": -20.0,
    "ecl110_displace_max": 20.0,
    "pv_enabled": True,
    "pv_peak_kw": 8.0,
    "pv_export_price": 0.3,
    "pv_production_entity": "sensor.pv_now",
    "peak_tariff_enabled": True,
    "peak_tariff_price_per_kw": 45.0,
    "peak_tariff_peaks_averaged": 3,
    "peak_tariff_window_minutes": 60,
    "grid_fee_mode": "rules",
    "grid_fee_rules": "Mon-Fri 06:00-22:00 = 0.25",
    "grid_fee_fixed": 0.05,
    "heat_pump_mode_entity": "select.pump_mode",
    "heat_pump_defrost_entity": "binary_sensor.pump_defrost",
    "heat_pump_online_entity": "binary_sensor.pump_online",
    "heat_pump_fault_entity": "binary_sensor.pump_fault",
    "compressor_freq_entity": "number.pump_freq",
    "compressor_freq_sensor": "sensor.pump_freq",
    "heat_pump_power_entity": "sensor.pump_power",
    "heat_pump_energy_entity": "sensor.pump_energy",
    "house_power_entity": "sensor.house_power",
    "floor_return_temp_entity": "sensor.floor_return",
    "solar_radiation_entity": "sensor.solar_rad",
    "indoor_humidity_entity": "sensor.humidity",
    "away_enabled": True,
    "away_presence_entity": "input_boolean.holiday",
    "away_temperature": 17.0,
    "away_dhw_min_temperature": 40.0,
}


def build_entities(cfg):
    hass = FakeHass()
    for eid, (val, unit) in STATE_TABLE.items():
        hass.states.set(eid, FakeState(val, unit=unit))
    entry = FakeEntry(data={
        "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor",
        **cfg,
    })
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    coord._prices = [
        {
            "total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
            "starts_at": (START + timedelta(hours=h)).isoformat(),
            "level": "NORMAL",
        }
        for h in range(48)
    ]
    asyncio.run(coord._update_current_state())
    coord._forecast_arrays()
    coord.data = coord._build_data_dict()
    added: list = []
    entry.runtime_data = coord
    asyncio.run(sensor.async_setup_entry(hass, entry, lambda e: added.extend(e)))
    return added


def check_four(probes):
    """The finder's four checks, computed over (value, dc, sc, unit, options).

    ``dc``/``sc`` arrive already read one way or the other; that is the
    whole point.  Predicates transcribed from entity_matrix.py's grade().
    """
    fires = {"enum_state_not_in_options": 0, "measurement_non_numeric": 0,
             "timestamp_naive": 0, "unit_device_class_mismatch": 0}
    for (value, dc, sc, unit, options) in probes:
        if dc == "enum" and options and value is not None and value not in options:
            fires["enum_state_not_in_options"] += 1
        if sc == "measurement" and value is not None and (
            isinstance(value, bool) or not isinstance(value, (int, float))
        ):
            fires["measurement_non_numeric"] += 1
        if dc == "timestamp" and value is not None and (
            not isinstance(value, _dt.datetime) or value.tzinfo is None
        ):
            fires["timestamp_naive"] += 1
        allowed = {"temperature": {"°C", "°F", "K"}, "power": {"W", "kW", "MW"},
                   "timestamp": set(), "enum": set()}.get(dc)
        if dc is not None and allowed is not None:
            if allowed == set():
                if unit not in (None, ""):
                    fires["unit_device_class_mismatch"] += 1
            elif unit not in allowed:
                fires["unit_device_class_mismatch"] += 1
    return fires


def _norm(v):
    return None if v is None else str(getattr(v, "value", v))


def read_path(ent, prop, attr):
    v_prop = getattr(ent, prop, None)
    v_attr = getattr(ent, attr, None)
    return v_prop, v_attr


def main() -> int:
    # --- (a) the stub declares none of the three properties ---------------
    src = inspect.getsource(
        sys.modules["homeassistant.components.sensor"]
    )
    declared = sum(
        src.count(f"def {name}") for name in
        ("device_class", "state_class", "entity_category")
    )
    stub_all = Path("tests/hastub").rglob("*.py")
    declared_anywhere = 0
    for p in stub_all:
        t = p.read_text()
        declared_anywhere += sum(
            t.count(f"def {name}") for name in
            ("device_class", "state_class", "entity_category")
        )

    ents = build_entities(
        {**dict(coordinator_scenarios()["coord_all_features"]), **ALL_OVERLAY}
    )

    # --- (b) the vacuity: property path vs _attr path over the real set ---
    prop_dc = sum(1 for e in ents if getattr(e, "device_class", None) is not None)
    prop_sc = sum(1 for e in ents if getattr(e, "state_class", None) is not None)
    prop_ec = sum(1 for e in ents if getattr(e, "entity_category", None) is not None)
    attr_dc = sum(1 for e in ents if getattr(e, "_attr_device_class", None) is not None)
    attr_sc = sum(1 for e in ents if getattr(e, "_attr_state_class", None) is not None)
    attr_ec = sum(1 for e in ents if getattr(e, "_attr_entity_category", None) is not None)
    mro = type(ents[0]).__mro__
    stub_mro_decls = sorted(
        {
            f"{c.__module__}.{c.__qualname__}:{name}"
            for c in mro
            for name in ("device_class", "state_class", "entity_category")
            if isinstance(getattr(c, "__dict__", {}).get(name, None), property)
        }
    )

    # --- (c) injected violations in REAL production classes ---------------
    def _swap(cls, name, value):
        """Class-attribute swap with try/finally (the repo's own idiom)."""
        orig = getattr(cls, name)
        setattr(cls, name, value)
        return lambda: setattr(cls, name, orig)

    by_cls = {type(e).__name__: e for e in ents}
    plan = by_cls["PlanNarrativeSensor"]
    indoor = by_cls["IndoorTempSensor"]
    lastopt = by_cls["LastOptimizationSensor"]

    probes_attr, probes_prop = [], []
    # 1. enum: PlanNarrativeSensor value outside its options
    restore = _swap(
        type(plan), "native_value", property(lambda self: "zz_injected")
    )
    try:
        probes_attr.append(
            (plan.native_value, _norm(getattr(plan, "_attr_device_class")),
             None, None, list(plan._attr_options))
        )
        probes_prop.append(
            (plan.native_value, getattr(plan, "device_class", None),
             None, None, list(plan._attr_options))
        )
    finally:
        restore()
    # 2. measurement over a string: IndoorTempSensor
    restore = _swap(
        type(indoor), "native_value", property(lambda self: "warm")
    )
    try:
        probes_attr.append(
            (indoor.native_value, None,
             _norm(getattr(indoor, "_attr_state_class")), None, None)
        )
        probes_prop.append(
            (indoor.native_value, None,
             getattr(indoor, "state_class", None), None, None)
        )
    finally:
        restore()
    # 3. naive timestamp: LastOptimizationSensor
    naive = _dt.datetime(2026, 9, 12, 10, 0, 0)
    restore = _swap(
        type(lastopt), "native_value", property(lambda self: naive)
    )
    try:
        probes_attr.append(
            (lastopt.native_value,
             _norm(getattr(lastopt, "_attr_device_class")), None, None, None)
        )
        probes_prop.append(
            (lastopt.native_value,
             getattr(lastopt, "device_class", None), None, None, None)
        )
    finally:
        restore()
    # 4. wrong unit for the declared class: IndoorTempSensor + kWh
    orig_unit = indoor._attr_native_unit_of_measurement
    indoor._attr_native_unit_of_measurement = "kWh"
    try:
        probes_attr.append(
            (21.0, _norm(getattr(indoor, "_attr_device_class")), None,
             indoor.native_unit_of_measurement, None)
        )
        probes_prop.append(
            (21.0, getattr(indoor, "device_class", None), None,
             indoor.native_unit_of_measurement, None)
        )
    finally:
        indoor._attr_native_unit_of_measurement = orig_unit

    fires_attr = check_four(probes_attr)
    fires_prop = check_four(probes_prop)

    # --- (d) reduced matrix: entity_category_declared, 5 cells ------------
    # REDUCTION, stated: 5 cells (5 topologies x the merged-all overlay),
    # not the finder's 75; no solve (category is a class attribute, not
    # payload-derived), one cycle per cell.
    ec_attr_total = 0
    ec_prop_total = 0
    for topo_cfg in coordinator_scenarios().values():
        cell_ents = build_entities({**topo_cfg, **ALL_OVERLAY})
        ec_attr_total += sum(
            1 for e in cell_ents
            if getattr(e, "_attr_entity_category", None) is not None
        )
        ec_prop_total += sum(
            1 for e in cell_ents
            if getattr(e, "entity_category", None) is not None
        )

    print(f"RESULT stub_property_declarations={declared} properties")
    print(f"RESULT stub_anywhere_property_declarations={declared_anywhere} properties")
    print(f"RESULT stub_mro_property_declarations={len(stub_mro_decls)} properties")
    print(f"RESULT property_path_dc_nonnone={prop_dc} entities")
    print(f"RESULT property_path_sc_nonnone={prop_sc} entities")
    print(f"RESULT property_path_ec_nonnone={prop_ec} entities")
    print(f"RESULT attr_path_dc_nonnone={attr_dc} entities")
    print(f"RESULT attr_path_sc_nonnone={attr_sc} entities")
    print(f"RESULT attr_path_ec_nonnone={attr_ec} entities")
    print(f"RESULT injected_attr_path_fires={sum(fires_attr.values())} of 4")
    print(f"RESULT injected_property_path_fires={sum(fires_prop.values())} of 4")
    for k, v in fires_attr.items():
        print(f"RESULT injected_{k}_attr={v}")
    for k, v in fires_prop.items():
        print(f"RESULT injected_{k}_prop={v}")
    print(f"RESULT ec_declared_5cells_attr={ec_attr_total} entity_cells")
    print(f"RESULT ec_declared_5cells_prop={ec_prop_total} entity_cells")
    print(f"RESULT ec_declared_per_cell={ec_attr_total // 5} entities")
    print(f"RESULT ec_declared_extrapolated_75cells={ec_attr_total * 15} entity_cells")
    import resource

    print("RESULT thread_factor=1.00 ratio")
    print("RESULT timing_results_reported=0 count")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap} count")
    print(f"RESULT load1={os.getloadavg()[0]:.2f} load")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
