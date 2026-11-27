#!/bin/bash
# r11_dead_state_mutants.sh -- MUTANT_CMD for the R11-SEAM-dead-state diff's mutants.
#
# The diff deleted state that production stores and nothing reads; its mutants (a deleted call, a
# swapped index, a dropped statement on the touched lines) are each held by one tests/features.py
# block. This chains those blocks through tools/audit/seat/features_block.py, which runs one block of
# the script instead of the tens of minutes the whole of it takes. A block reads names that earlier
# parts of features.py define, so each call carries the --prelude lines that bind them (the
# --emit-prelude derivation costs 7-22 s a block, too slow to repeat per mutant; block 8's derived
# prelude is embedded below). The command exits 0 only when every block passes, so a mutant is
# KILLED when any block fails.
#
#     bash dev/audit/harnesses/r11_dead_state_mutants.sh
#
# As the mutant driver's command (run from the repository root):
#     python3 tools/audit/seat/mutant_run.py --diff "$(git merge-base origin/main HEAD)...HEAD" \
#         --cmd "bash dev/audit/harnesses/r11_dead_state_mutants.sh" --max-mutants 40 --report-only
#
# Exits 0 on an unmutated tree and 1 at the first block that fails (its FAIL lines follow).
set -euo pipefail
export PYTHONPATH=tests/hastub
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
FB="python3 tools/audit/seat/features_block.py"
n=0
blk() { # <START> <END> <--prelude args...>: one features.py block
  local s=$1 e=$2; shift 2; n=$((n + 1))
  $FB "$@" "$s" "$e" >"$T/r$n.log" 2>&1 \
    || { echo "block $n ($s) FAILED"; grep -a 'FAIL\|Error' "$T/r$n.log" | head -5 | cut -c1-240; exit 1; }
}
# The T4 helpers (_t4_coord and friends) that features.py defines ahead of the sysid blocks.
T4="exec('_T4_DATA = {' + open('tests/features.py').read().split('_T4_DATA = {',1)[1].split('# -- \`_entity_state\`',1)[0])"
SIDP=(--prelude 'import ast as _p5_ast' --prelude 'import sys as _p5_sys' --prelude 'import logging as _p5_logging, inspect as _p5_inspect'
  --prelude 'import heatpump_optimizer.coordinator as _p5_coord_mod' --prelude 'from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator'
  --prelude 'from harness import FakeEntry' --prelude 'import asyncio as _asyncio' --prelude 'from heatpump_optimizer import sysid as _SysIdModule'
  --prelude 'from dataclasses import replace as _dc_replace' --prelude "$T4")
HARN=(--prelude 'from harness import FakeEntry as _FakeEntry, FakeHass as _FakeHass' --prelude 'import asyncio as _asyncio')
COORD=(--prelude 'from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as _Coord')

# curve_learning.record_miss, from record_day
blk '# --- #2 the heat-curve bias' '# --- round-5 D3-08' \
  --prelude 'from heatpump_optimizer.curve_learning import BIAS_MIN, COMFORT_MARGIN_C, DAYS_PER_STEP, STEP_K, CurveLearner'
# coordinator record_miss, from _track_curve_comfort
blk '_T2_LEARNER_T0 = datetime(2026, 1, 15, 6, 0, 0)' '# The quiet-period learner reads the SOLVED plan' \
  "${HARN[@]}" "${COORD[@]}" --prelude 'from types import SimpleNamespace as _NS' --prelude 'from homeassistant.util import dt as dt_util'
# async_shutdown awaits the background tasks it tracks
blk '# D1-02 hygiene: fire-and-forget tasks are tracked' '# A save that changes nothing must not reload.' \
  "${HARN[@]}" --prelude '_LC_DATA = {"price_source": "entity", "price_entity": "sensor.prices", "weather_entity": "weather.home"}'
# optimizer._peak_window_factors
blk 'R.section("R8-D2-s2-01 — the capacity bill' '# --- #1512 x #1499: the no-meter arm' \
  "${HARN[@]}" "${COORD[@]}" --prelude 'from heatpump_optimizer import grid_fee as _gf'
# sysid.adoption_decision and its coordinator caller
blk '# #1525: the adoption gate lives in one pure function' 'R.section("Actuation routing: every accepted domain' "${SIDP[@]}"
# SystemIdentification.arm's slab gate
blk '_g1401_plant = ThermalParameters()' 'R.section("#1329: the sysid arm/adopt gate opens' "${SIDP[@]}" \
  --prelude 'NOW = datetime(2026, 2, 1, 12, 0, tzinfo=UTC)' --prelude 'from heatpump_optimizer.sysid import SystemIdentification' \
  --prelude 'from heatpump_optimizer.thermal_model import ThermalParameters'
# identify_slab's series unpack
blk '# -- the sysid-estimator wave, first act' '# -- the three service entry points, and what each one costs' "${SIDP[@]}" \
  --prelude 'NOW = datetime(2026, 2, 1, 12, 0, tzinfo=UTC)' --prelude 'from heatpump_optimizer.sysid import SystemIdentification' \
  --prelude 'from heatpump_optimizer.thermal_model import ThermalParameters' --prelude 'from profiles import house as _grad_house' \
  --prelude "exec('from stress import BUILDINGS as _b942' + open('tests/features.py').read().split('from stress import BUILDINGS as _b942',1)[1].split('_g942_unseeded = ',1)[0])" \
  --prelude 'from heatpump_optimizer import presets' --prelude '_bar = _SysIdModule.UA_ADOPTION_HALFWIDTH_BAR'
# identify's two-column lstsq fallback
blk 'R.section("W5-G8 i: the system-identification experiment' '# -- W5-G8 j: the wood night advisory'
# flow_meter.observe_water: the fold and the supply slot (prelude derived with --emit-prelude)
cat >"$T/fm.py" <<'EOF_PRE'
NOW = datetime(2026, 2, 1, 12, 0, tzinfo=UTC)
from dataclasses import replace
from harness import FakeEntry, FakeHass
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
from homeassistant.util import dt as dt_util
_T2_DATA = {"tibber_token": "x", "weather_entity": "weather.home"}
def _t2_coord(**config):
    """A live coordinator over the fake bus, with config overrides applied."""
    return HeatPumpOptimizerCoordinator(
        FakeHass(), FakeEntry(data=dict(_T2_DATA, **config))
    )
def _t2_count_saves(coord):
    """Record every thermal-learning save, so "it persisted" is observable."""
    coord._t2_saves = []
    inner = coord._async_save_thermal_learning

    async def counted():
        coord._t2_saves.append(coord._buffer_cooling_rate)
        return await inner()

    coord._async_save_thermal_learning = counted
_T2_HOUSE_CFG = {
    "indoor_temp_entity": "sensor.indoor",
    "outdoor_temp_entity": "sensor.outdoor",
}
_T2_TWO_ZONE_CFG = {
    "upper_floor_thermal_mass": 3.0,
    "lower_floor_thermal_mass": 8.0,
    "lower_floor_temp_entity": "sensor.lower",
}
_T2_HOUSE_STATE = ThermalState(
    room_temperature=21.0,
    upper_floor_temperature=21.0,
    lower_floor_temperature=20.0,
    slab_temperature=27.0,
    outdoor_temperature=-5.0,
)
def _t2_house(
    *,
    observed=20.9,
    lower=None,
    hours=0.5,
    power=2.0,
    outdoor=-5.0,
    two_zone=False,
    **config,
):
    """A coordinator holding one replayable interval, not yet learned from."""
    cfg = dict(_T2_HOUSE_CFG)
    if two_zone:
        cfg.update(_T2_TWO_ZONE_CFG)
    cfg.update(config)
    c = _t2_coord(**cfg)
    _t2_count_saves(c)
    previous = replace(_T2_HOUSE_STATE, outdoor_temperature=outdoor)
    c._last_house_sample = previous
    c._last_house_sample_time = dt_util.now() - timedelta(hours=hours)
    c._current_state = replace(
        previous,
        room_temperature=observed,
        upper_floor_temperature=observed,
        lower_floor_temperature=(
            previous.lower_floor_temperature if lower is None else lower
        ),
    )
    c._current_action = {"power": power}
    return c
def _t2_drive(coord, method):
    """Run one learner and capture anything that escapes it."""
    coord._t2_escaped = None
    try:
        _asyncio.run(getattr(coord, method)(coord._close_fabric_interval()))
    except Exception as err:  # noqa: BLE001
        coord._t2_escaped = err
    return coord
from heatpump_optimizer import const as _fb_const
from heatpump_optimizer import flow_meter as _fm
from heatpump_optimizer.inputs import (  # noqa: E402
    InputReader as _fmReader,
    normalize_flow_kg_s as _fm_norm,
)
_FM_LEARN_KW = 5.22
_FM_FLOW_CFG = {
    _fb_const.CONF_FLOW_METER_ENTITY: "sensor.flow",
    _fb_const.CONF_HEAT_PUMP_SUPPLY_TEMP_ENTITY: "sensor.sup",
    _fb_const.CONF_HEAT_PUMP_RETURN_TEMP_ENTITY: "sensor.ret",
}
def _fm_plant(coord, flow="15.0", unit="L/min", age_min=1):
    """Plant this cycle's three water states and run the production fold."""
    coord.hass.states.set(
        "sensor.flow",
        # Polled: re-reported ``age_min`` ago (#2234).
        FakeState(flow, last_updated=minutes_ago(age_min + 3, NOW),
                  last_reported=minutes_ago(age_min, NOW), unit=unit),
    )
    coord.hass.states.set(
        "sensor.sup",
        FakeState("45.0", last_updated=minutes_ago(1, NOW), unit="°C"),
    )
    coord.hass.states.set(
        "sensor.ret",
        FakeState("40.0", last_updated=minutes_ago(1, NOW), unit="°C"),
    )
    # The outranked arm configures the pump's power meter, and its learner has
    # to reach the replay for that arm's refusal to mean something other than
    # "the learner never ran": the fixture builds no cycle, so the meter's
    # value is planted the way `_update_current_state` would have left it.
    coord.hass.states.set(
        "sensor.hp_power",
        FakeState("2000", last_updated=minutes_ago(1, NOW), unit="W"),
    )
    reader = _fmReader(coord.hass, coord.effective_config, now=lambda: NOW)
    _fm.observe_water(coord._flow_bias, reader, coord.effective_config)
    return coord
def _fm_spy(coord):
    """The next replay's call to ``simulate_step``: its kwargs and its result."""
    seen = {"kwargs": {}, "state": None}
    real = coord._thermal_model.simulate_step

    def spy(*args, **kwargs):
        seen["kwargs"] = kwargs
        seen["state"] = real(*args, **kwargs)
        return seen["state"]

    coord._thermal_model.simulate_step = spy
    return seen
def _fm_replay(
    method,
    *,
    flow_cfg=True,
    two_zone=False,
    action=None,
    config=None,
    meter=None,
    **plant,
):
    """One frozen-clock learner run over one planted interval.

    Frozen because the fit is a Newton step on ``dt_hours`` and a live clock
    leaves whatever gap the scheduler happens to have (#812's note above).
    Returns ``(seen, coordinator)``.
    """
    dt_util.freeze(NOW)
    try:
        cfg = dict(_FM_FLOW_CFG) if flow_cfg else {}
        cfg.update(config or {})
        coord = _t2_house(two_zone=two_zone, **cfg)
        if action is not None:
            coord._current_action = dict(action)
        if meter is not None:
            coord._measured_power = float(meter)
        _fm_plant(coord, **plant)
        seen = _fm_spy(coord)
        _t2_drive(coord, method)
    finally:
        dt_util.freeze(None)
    return seen, coord
_HOUSE_LEARNER = "_async_learn_house_heat_loss"
_LOWER_LEARNER = "_async_learn_lower_floor_loss"
EOF_PRE
blk '_fm_seen, _fm_coord = _fm_replay(_HOUSE_LEARNER)' '# The precedence rule and the refused-reading paths' \
  "${HARN[@]}" --prelude "exec(open('$T/fm.py').read())"
# optimizer._build_result's set-point list
blk "# The tank's ceiling is a hard constraint in the solve" '# and they must lead the multi-start list.' \
  --prelude 'from heatpump_optimizer import mixing_valve as _mv' \
  --prelude 'from heatpump_optimizer.optimizer import HeatPumpOptimizer as _StoreOpt, OptimizationConfig as _StoreCfg' \
  --prelude 'from heatpump_optimizer.thermal_model import WeatherSeries' \
  --prelude 'def _WS(outdoor, wind=None, rain=None, solar=None, humidity=None, ext=None): return WeatherSeries(outdoor_temps=outdoor, wind_speeds=wind, precipitation=rain, solar_radiation=solar, humidity=humidity, external_heat_kw=ext)'
# coordinator._record_accuracy's one frequency sample
blk 'R.section("Free heat skips the accuracy sample (D7-05)")' '# --- D7-03 (#279): open window skips the accuracy sample' \
  --prelude 'from homeassistant.util import dt as dt_util' --prelude 'from harness import FakeEntry as _FakeEntry, FakeHass as _FakeHass' "${COORD[@]}" \
  --prelude '_METER = {"sensor.indoor": FakeState("21.0", unit="°C"), "sensor.outdoor": FakeState("-5.0", unit="°C"), "sensor.house_power": FakeState("6500", unit="W"), "sensor.hp_power": FakeState("2000", unit="W")}' \
  --prelude 'def _t2_coord(states=None, **extra): return _Coord(_FakeHass(dict(_METER, **(states or {}))), _FakeEntry(data={"tibber_token": "x", "weather_entity": "weather.home", "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor", **extra}))'
# optimizer._optimize_with_dhw's baseline economics: every DHW-enabled solve reaches it
python3 tests/manual_plan.py >"$T/manual_plan.log" 2>&1 \
  || { echo "tests/manual_plan.py FAILED"; grep -a 'FAIL\|Error' "$T/manual_plan.log" | head -5 | cut -c1-240; exit 1; }
echo "r11_dead_state_mutants: $n blocks and tests/manual_plan.py passed"
