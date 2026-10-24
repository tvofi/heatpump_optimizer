#!/usr/bin/env python3
"""D12-b (round 5): heat-pump axes x control surfaces, one coordinator cycle per cell.

METRIC (one line): cells_failed = count of cells in the derived heat-pump-axis x
control-surface grid whose setup + first coordinator cycle violates the D12
usable bar -- setup fails, no plan is published and no named refusal explains
why, the coordinator WRITES to a control surface the cell's plant does not have
(mqtt.publish with no ECL110 device behind the config, switch writes with no
switch mapped, number.set_value outside frequency-control), or the cycle raises.
The count is keyed on the service calls the production seam delivers
(coordinator._apply_action / _publish_ecl110_topics / _command_frequency /
_command_valve_target -> hass.services.async_call records), never on an input
config attribute alone.

COMMAND (from the repository root):
  PYTHONPATH=tests/hastub python3 tools/audit/round5/D12/seat-b/cells.py [--cell NAME]

EXPECTED at baseline 1cc89e020fff9040a9d0090a27bf22bc1dd497f0 (Apple M1, macOS,
python3.11): cells=14, cells_failed=3 -- the three cells whose config carries
no ecl110 key and whose plant has no ECL110 (onoff_switch, onoff_advisor,
mod_num_control_default), each publishing ECL110 MQTT on the shipped default
topics ("invented ECL110 MQTT surface"); all other cells usable. Numbers:
mqtt_publish_onoff_switch=2, mqtt_publish_onoff_advisor=2,
mqtt_publish_onoff_switch_eclblank=0, mqtt_publish_ecl_mod_custom=2,
mqtt_publish_null_all_features=2; switch_writes_onoff_switch=1,
switch_writes_onoff_advisor=0; freq_writes_mod_num_control=1,
freq_writes_mod_num_observe=0, freq_writes_mod_num_control_nostate=0;
valve_writes_valve_climate=1, valve_writes_valve_number=1.

NULL CONTROL: cell null_all_features (tests/golden.py coordinator_scenarios
"coord_all_features", the fully-mapped reference plant) runs the same driver;
its mqtt publishes are the intended surface there (the default ECL110 topics
ARE the reference plant's own), so it does NOT count as a generalization
failure; any OTHER check failing there would name its owning dimension
instead.

PERTURBATION (judge runs it): (a) adding "ecl110_displace_set_topic": "" and
"ecl110_command_topic": "" to cell onoff_switch's config (dropping the ECL110
surface the plant never had) moves that cell mqtt_publish 2 -> 0, its verdict
fail -> usable, and cells_failed 3 -> 2; (b) removing
heat_pump_switch_entity from onoff_switch moves switch_writes 1 -> 0;
(c) replacing cell mod_num_control's compressor_freq_entity with nothing
(modulating -> on/off) moves freq_writes 1 -> 0. A run whose numbers do not
move under (a)/(b)/(c) is void.

In-memory harness drives (no production or test file is modified): the weather
service is served through FakeServices.async_register the way a real weather
integration serves it; freq-control cells get _freq_last_write=None (the
5-minute write rate limit starts armed at setup, dt_util.now()) and a
pre-evidenced frequency map (>= FREQ_MIN_SAMPLES in two deciles) so the control
stage's single write path is reachable in ONE cycle; these simulate elapsed
time and prior observation, which the first cycle cannot.

HPO_PLANDATA: not used (no Node harness). Writes nothing outside stdout.
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys
import time

# Thread pin FIRST, before any numpy import (tests/audit README contract).
for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import (  # noqa: E402
    FakeEntry,
    FakeHass,
    FakeState,
    ha_setup_entry,
)

# The D12-b grid: heat-pump axis (on/off vs modulating) x control surface the
# tree already exposes (switch, ECL110 MQTT topics default/blank/custom,
# frequency number observe/control, frequency sensor only, mixing-valve
# smart_write to climate/number). Derived from const.py's CONF_* surface and
# config_flow.py's entity/heat_curve sections, not carried from anywhere.
ECL_DEFAULT_SENTINEL = object()  # cell ships no ecl110 keys at all


def _base_config(ecl=ECL_DEFAULT_SENTINEL, **extra):
    cfg = {
        "price_source": "entity",
        "price_entity": "sensor.prices",
        "weather_entity": "weather.home",
        "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor",
        "target_temperature": 21.0,
        "min_temperature": 17.0,
        "max_temperature": 23.0,
    }
    if ecl is not None and ecl is not ECL_DEFAULT_SENTINEL:
        cfg.update(ecl)
    cfg.update(extra)
    return cfg


ECL_BLANK = {
    "ecl110_displace_set_topic": "",
    "ecl110_command_topic": "",
}
ECL_CUSTOM = {
    "ecl110_displace_set_topic": "home/ecl/flow_temp/displace/set",
    "ecl110_command_topic": "home/ecl/command",
}

CELLS: dict[str, dict] = {
    # -- on/off axis ----------------------------------------------------
    # The shipped-default on/off install: a switch mapped, no ecl110 key in
    # the config at all (what config_flow leaves when the heat_curve page
    # is never opened -- the DEFAULT_*_TOPIC strings stand in _init_ecl110).
    "onoff_switch": {
        "config": _base_config(heat_pump_switch_entity="switch.pump"),
        "plant": {"switch"},
    },
    # The same install with the ECL110 surface explicitly dropped.
    "onoff_switch_eclblank": {
        "config": _base_config(ECL_BLANK, heat_pump_switch_entity="switch.pump"),
        "plant": {"switch"},
    },
    # Advisor-only on/off install (no actuation surface mapped at all),
    # shipped defaults.
    "onoff_advisor": {
        "config": _base_config(),
        "plant": set(),
    },
    "onoff_advisor_eclblank": {
        "config": _base_config(ECL_BLANK),
        "plant": set(),
    },
    # -- modulating axis -------------------------------------------------
    # The reference-plant shape: ECL110 MQTT topics the user chose.
    "ecl_mod_custom": {
        "config": _base_config(ECL_CUSTOM),
        "plant": {"ecl"},
    },
    # Modulating via frequency sensor only (#1067): observe-only by design.
    "mod_sensor_switch": {
        "config": _base_config(
            ECL_BLANK,
            heat_pump_switch_entity="switch.pump",
            compressor_freq_sensor="sensor.compressor_frequency",
            heat_pump_power_entity="sensor.hp_power",
        ),
        "plant": {"switch", "freq_sensor"},
    },
    "mod_sensor_advisor": {
        "config": _base_config(
            ECL_BLANK,
            compressor_freq_sensor="sensor.compressor_frequency",
            heat_pump_power_entity="sensor.hp_power",
        ),
        "plant": {"freq_sensor"},
    },
    # Modulating via a frequency number entity, observe (the default stage).
    "mod_num_observe": {
        "config": _base_config(
            ECL_BLANK,
            heat_pump_switch_entity="switch.pump",
            compressor_freq_entity="number.compressor_frequency",
            heat_pump_power_entity="sensor.hp_power",
        ),
        "plant": {"switch", "freq_number"},
    },
    # Control stage, everything mapped and evidenced.
    "mod_num_control": {
        "config": _base_config(
            ECL_BLANK,
            heat_pump_switch_entity="switch.pump",
            compressor_freq_entity="number.compressor_frequency",
            compressor_freq_sensor="sensor.compressor_frequency",
            freq_control_mode="control",
            heat_pump_power_entity="sensor.hp_power",
        ),
        "plant": {"switch", "freq_number", "freq_sensor"},
        "seed_freq_map": True,
    },
    # Control mode on the shipped-default topics (no ecl110 key in config).
    "mod_num_control_default": {
        "config": _base_config(
            compressor_freq_entity="number.compressor_frequency",
            freq_control_mode="control",
            heat_pump_power_entity="sensor.hp_power",
        ),
        "plant": {"freq_number"},
        "seed_freq_map": True,
    },
    # Control mode but the number entity publishes no state (hardware gone):
    # an omitted optional control must leave the path inert, not crashed.
    "mod_num_control_nostate": {
        "config": _base_config(
            ECL_BLANK,
            heat_pump_switch_entity="switch.pump",
            compressor_freq_entity="number.compressor_frequency",
            freq_control_mode="control",
        ),
        "plant": {"switch"},
        "number_state": False,
        "seed_freq_map": True,
    },
    # freq_control_mode="control" with a SENSOR only: control needs a number,
    # so the stage in force must read observe -- no invented write path.
    "mod_control_sensor_only": {
        "config": _base_config(
            ECL_BLANK,
            compressor_freq_sensor="sensor.compressor_frequency",
            freq_control_mode="control",
            heat_pump_power_entity="sensor.hp_power",
        ),
        "plant": {"freq_sensor"},
    },
    # -- valve write surface (climate / number domains) -------------------
    "valve_climate": {
        "config": _base_config(
            ECL_BLANK,
            mixing_valve_mode="smart_write",
            mixing_valve_write_entity="climate.valve",
        ),
        "plant": {"valve_climate"},
    },
    "valve_number": {
        "config": _base_config(
            ECL_BLANK,
            mixing_valve_mode="smart_write",
            mixing_valve_write_entity="number.valve_target",
        ),
        "plant": {"valve_number"},
    },
    # -- null control ------------------------------------------------------
    "null_all_features": {
        "config": _base_config(
            dhw_tank_volume=200.0,
            peak_tariff_enabled=True,
            peak_tariff_price_per_kw=45.0,
            pv_enabled=True,
            pv_peak_kw=8.0,
            pv_export_price=0.3,
            away_enabled=True,
            external_heat_detection_enabled=True,
            comfort_learning_enabled=True,
            system_identification_enabled=True,
            compressor_cycling_cost=0.5,
        ),
        "plant": set(),
        "null": True,
    },
}


def _seed_states(hass: FakeHass, spec: dict) -> None:
    """The plant's entities, as FakeHass states (entities only the cell has)."""
    from datetime import timedelta
    from homeassistant.util import dt as dt_util

    now = dt_util.now().replace(minute=0, second=0, microsecond=0)
    # Price feed: a Nord-Pool-style entity sensor (tests/features.py _seed_prices).
    hass.states.set(
        "sensor.prices",
        FakeState(
            "0.5",
            attributes={
                "raw_today": [
                    {
                        "start": (now + timedelta(hours=h)).isoformat(),
                        "value": round(0.2 + 0.1 * (h % 4), 3),
                    }
                    for h in range(48)
                ]
            },
        ),
    )
    # Cold enough indoors that the first plan asks the pump for heat.
    hass.states.set("sensor.indoor", FakeState("19.0"))
    hass.states.set("sensor.outdoor", FakeState("-5.0"))
    if "switch" in spec["plant"]:
        hass.states.set("switch.pump", FakeState("on"))
    if "freq_sensor" in spec["plant"]:
        hass.states.set("sensor.compressor_frequency", FakeState("45.0", unit="Hz"))
    if "freq_number" in spec["plant"] and spec.get("number_state", True):
        hass.states.set(
            "number.compressor_frequency",
            FakeState("45.0", attributes={"min": 20.0, "max": 120.0, "unit_of_measurement": "Hz"}),
        )
    if "heat_pump_power_entity" in spec["config"]:
        hass.states.set("sensor.hp_power", FakeState("2.5", unit="kW"))
    if "valve_climate" in spec["plant"]:
        hass.states.set(
            "climate.valve", FakeState("heat", attributes={"temperature": 30.0})
        )
    if "valve_number" in spec["plant"]:
        hass.states.set(
            "number.valve_target",
            FakeState("30.0", attributes={"min": 10.0, "max": 50.0}),
        )

    # The weather service, served the way a real weather integration serves it.
    async def _get_forecasts(call):
        return {
            call.data["entity_id"]: {
                "forecast": [
                    {
                        "datetime": (now + timedelta(hours=h)).isoformat(),
                        "temperature": -5.0 + 3.0 * (h % 24) / 24.0,
                        "wind_speed": 3.0,
                        "precipitation": 0.0,
                        "humidity": 85.0,
                    }
                    for h in range(48)
                ]
            }
        }

    hass.services.async_register("weather", "get_forecasts", _get_forecasts)


def _svc_calls(hass: FakeHass, domain: str, service: str) -> list[tuple]:
    return [c for c in hass.services.calls if c[0] == domain and c[1] == service]


def run_cell(name: str, quiet: bool = False) -> dict:
    """Drive one cell: setup, one full coordinator cycle, judge the bar."""
    spec = CELLS[name]
    hass = FakeHass()
    _seed_states(hass, spec)

    import heatpump_optimizer as integ

    out = {"cell": name, "fail_step": None, "notes": []}
    entry = FakeEntry(data=dict(spec["config"]))
    try:
        ok = asyncio.run(ha_setup_entry(integ, hass, entry))
    except Exception as err:  # noqa: BLE001 - the bar asks what escapes setup
        out["fail_step"] = "setup-crash"
        out["notes"].append(f"setup raised {type(err).__name__}: {err}")
        return out
    if not ok:
        out["fail_step"] = "setup"
        return out
    coord = getattr(entry, "runtime_data", None)
    if coord is None:
        out["fail_step"] = "setup (no runtime_data)"
        return out

    # Harness drive, in-memory only (see header): age the freq write
    # rate-limit and pre-evidence the map so ONE cycle can reach the
    # control stage's write path.
    if spec.get("seed_freq_map"):
        from heatpump_optimizer.freq_control import FREQ_MIN_SAMPLES

        coord._freq_map.buckets = {
            2: [0.05, FREQ_MIN_SAMPLES + 1],
            7: [0.06, FREQ_MIN_SAMPLES + 1],
        }
        coord._freq_last_write = None

    try:
        asyncio.run(coord.async_refresh())
    except Exception as err:  # noqa: BLE001
        out["fail_step"] = "cycle-crash"
        out["notes"].append(f"refresh raised {type(err).__name__}: {err}")
        return out

    data = coord.data or {}
    status = data.get("optimization_status")
    schedule = data.get("schedule") or []
    action = dict(coord.current_action or {})

    # 1) A plan is published or a named refusal explains why not.
    if not status or status == "not_run":
        out["fail_step"] = "no plan and no named refusal"
        out["notes"].append(f"optimization_status={status!r}")
    elif not schedule and status and "fail" not in str(status):
        out["fail_step"] = "no plan and no named refusal"
        out["notes"].append(f"status={status!r} schedule=0")

    # 2) No write to a control surface the cell's plant does not have.
    mqtt_calls = _svc_calls(hass, "mqtt", "publish")
    switch_calls = (
        _svc_calls(hass, "switch", "turn_on") + _svc_calls(hass, "switch", "turn_off")
    )
    freq_calls = [
        c for c in _svc_calls(hass, "number", "set_value")
        if c[2].get("entity_id") == "number.compressor_frequency"
    ]
    valve_calls = (
        _svc_calls(hass, "climate", "set_temperature")
        + [
            c for c in _svc_calls(hass, "number", "set_value")
            if c[2].get("entity_id") == "number.valve_target"
        ]
    )
    ecl_keys_present = any(
        k.startswith("ecl110_") for k in spec["config"]
    ) or any(
        k.startswith("ecl110_") for k in spec["config"].values() if isinstance(k, str)
    )
    ecl_configured = any(
        spec["config"].get(k) for k in
        ("ecl110_displace_set_topic", "ecl110_command_topic")
    )
    has_ecl_surface = ecl_configured or "ecl" in spec["plant"]

    if mqtt_calls and not has_ecl_surface and not spec.get("null"):
        # The config carries no ECL110 surface (no key at all, or both
        # topics blank) yet the cycle published displace commands to the
        # shipped default topics -- a heat-curve displacement invented for
        # a plant with no ECL110.
        out["fail_step"] = out["fail_step"] or "invented ECL110 MQTT surface"
        out["notes"].append(
            f"mqtt.publish x{len(mqtt_calls)} with no ECL110 in config "
            f"(topics: {[c[2].get('topic') for c in mqtt_calls][:2]})"
        )
    if switch_calls and "switch" not in spec["plant"]:
        out["fail_step"] = out["fail_step"] or "invented switch surface"
        out["notes"].append(f"switch writes x{len(switch_calls)} with no switch")
    if freq_calls and "freq_number" not in spec["plant"]:
        out["fail_step"] = out["fail_step"] or "invented frequency write"
        out["notes"].append(f"number.set_value x{len(freq_calls)} outside control")
    if freq_calls and spec["config"].get("freq_control_mode") != "control":
        out["fail_step"] = out["fail_step"] or "frequency write outside control stage"
    if valve_calls and not ({"valve_climate", "valve_number"} & spec["plant"]):
        out["fail_step"] = out["fail_step"] or "invented valve write"

    # 3) No invented compressor mode: the freq view's stage must match the
    # CONFIG (coordinator._freq_mode is a config judgment: control needs
    # the number entity id AND the opt-in AND no watchdog latch; a number
    # whose state is absent leaves the WRITE path inert but the stage
    # reading control -- that arm is checked by freq_writes instead).
    fcfg = spec["config"]
    wants_control = (
        fcfg.get("freq_control_mode") == "control"
        and fcfg.get("compressor_freq_entity")
    )
    has_freq_any = fcfg.get("compressor_freq_entity") or fcfg.get(
        "compressor_freq_sensor"
    )
    expected_stage = (
        "control" if wants_control else "observe" if has_freq_any else "unconfigured"
    )
    got_stage = (data.get("freq_control") or {}).get("mode")
    if got_stage != expected_stage and not spec.get("null"):
        out["fail_step"] = out["fail_step"] or "invented compressor stage"
        out["notes"].append(
            f"freq stage {got_stage!r} != expected {expected_stage!r}"
        )

    out.update(
        {
            "mqtt_publish": len(mqtt_calls),
            "switch_writes": len(switch_calls),
            "freq_writes": len(freq_calls),
            "valve_writes": len(valve_calls),
            "freq_map_samples": sum(
                int(e[1]) for e in coord._freq_map.buckets.values()
            ),
            "status": status,
            "schedule_steps": len(schedule),
            "heat_pump_on": action.get("heat_pump_on"),
            "freq_stage": got_stage,
            "ecl_keys_present": bool(
                [k for k in spec["config"] if k.startswith("ecl110_")]
            ),
        }
    )
    if not quiet:
        print(
            f"  cell {name}: setup=ok status={status!r} steps={len(schedule)} "
            f"on={action.get('heat_pump_on')} mqtt={len(mqtt_calls)} "
            f"switch={len(switch_calls)} freq={len(freq_calls)} "
            f"valve={len(valve_calls)} stage={got_stage!r} "
            f"map={out['freq_map_samples']} "
            f"{'FAIL: ' + out['fail_step'] if out['fail_step'] else 'usable'}"
        )
        for note in out["notes"]:
            print(f"      - {note}")
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cell", choices=sorted(CELLS))
    args = parser.parse_args()

    import socket
    import subprocess

    proc_cpu_0 = time.process_time()
    thread_cpu_0 = time.thread_time()
    wall_0 = time.perf_counter()

    print(f"D12-b cells: heat-pump axes x control surfaces (grid of {len(CELLS)})")
    results = []
    if args.cell:
        results.append(run_cell(args.cell))
    else:
        for name in CELLS:
            results.append(run_cell(name))

    failed = [r for r in results if r["fail_step"]]
    # The null control is reported but never counted: a failure there is
    # owned by another dimension, not a generalization cell.
    counted = [r for r in results if not CELLS[r["cell"]].get("null")]
    counted_failed = [r for r in failed if not CELLS[r["cell"]].get("null")]

    print()
    for r in results:
        if "mqtt_publish" in r:
            print(
                f"RESULT mqtt_publish_{r['cell']}={r['mqtt_publish']} calls"
            )
    for r in results:
        if "switch_writes" in r:
            print(f"RESULT switch_writes_{r['cell']}={r['switch_writes']} calls")
    for r in results:
        if "freq_writes" in r:
            print(f"RESULT freq_writes_{r['cell']}={r['freq_writes']} calls")
    for r in results:
        if "valve_writes" in r:
            print(f"RESULT valve_writes_{r['cell']}={r['valve_writes']} calls")
    for r in results:
        if "freq_map_samples" in r:
            print(f"RESULT freq_map_samples_{r['cell']}={r['freq_map_samples']} samples")
    print(f"RESULT cells={len(counted)} cells")
    print(f"RESULT cells_failed={len(counted_failed)} cells")
    if any(CELLS[r["cell"]].get("null") for r in results):
        null_r = next(r for r in results if CELLS[r["cell"]].get("null"))
        print(
            f"RESULT null_all_features_failed={int(bool(null_r['fail_step']))} "
            f"({null_r['fail_step'] or 'usable; mqtt publishes there are the reference plant surface'})"
        )

    proc_cpu = time.process_time() - proc_cpu_0
    thread_cpu = time.thread_time() - thread_cpu_0
    wall = time.perf_counter() - wall_0
    try:
        load1 = float(subprocess.run(["sysctl", "-n", "vm.loadavg"], capture_output=True, text=True).stdout.split()[1])
    except Exception:  # noqa: BLE001
        load1 = -1.0
    try:
        swapins = int(
            subprocess.run(["sysctl", "-n", "vm.swapin"], capture_output=True, text=True).stdout.strip() or 0
        )
    except Exception:  # noqa: BLE001
        swapins = -1
    concurrent = int(subprocess.run(
        ["sh", "-c", "ps aux | grep -E '[s]tress\\.py|[t]ests/run\\.sh' | wc -l"],
        capture_output=True, text=True).stdout.strip() or 0)
    print(f"RESULT thread_factor={proc_cpu / max(thread_cpu, 1e-9):.3f}")
    print(f"RESULT load1={load1}")
    print(f"RESULT swapins={swapins}")
    print(f"RESULT concurrent_test_procs={concurrent}")
    print(f"RESULT wall_s={wall:.1f} (provisional, load-quoted; hostname={socket.gethostname()})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
