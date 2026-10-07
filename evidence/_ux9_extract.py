# Reviewer-built extract (not the finder's): the R9-UX-9 block of tests/features.py
# at f455915c, lines 59927-60103, behind features.py's own prelude names.
from __future__ import annotations
import sys
from datetime import datetime
from harness import FakeHass, FakeState, Results, UTC, minutes_ago
R = Results("UX-9 extract")
NOW = datetime(2026, 2, 1, 12, 0, tzinfo=UTC)
# --- #1956 the card recommends a feedback sensor on an unmetered install ---
# The probe is #1955's own: power and frequency come from ``probe_install``;
# the energy and flow entities are the classes the probe does not carry. The
# flow class is guarded on its config key existing in ``const`` (#2016).
from harness import FakeCoordinator as _fb_coord  # noqa: E402
from harness import FakeEntry as _fb_entry  # noqa: E402
from heatpump_optimizer import const as _fb_const  # noqa: E402
from heatpump_optimizer.sensor import SensorGapAdvisorSensor as _FbGapSensor  # noqa: E402
from heatpump_optimizer.thermal_model import feedback_gaps as _fb_gaps  # noqa: E402

_FB_KEYS = {
    _fb_const.CONF_POWER_ENTITY,
    _fb_const.CONF_ENERGY_ENTITY,
    _fb_const.CONF_COMPRESSOR_FREQ_SENSOR,
    _fb_const.CONF_FLOW_METER_ENTITY,
}
_fb_bare = _fb_gaps({})
R.check(
    "an install with no power, energy, frequency or flow signal is told which four classes to add",
    {g["key"] for g in _fb_bare} == _FB_KEYS
    and [g["class"] for g in _fb_bare] == ["power", "energy", "frequency", "flow"],
    f"{_fb_bare}",
)
R.check(
    "any one of the signals silences the recommendation (null control: each alone)",
    all(
        _fb_gaps({_fb_key: "sensor.x"}) == []
        for _fb_key in (
            _fb_const.CONF_POWER_ENTITY,
            _fb_const.CONF_ENERGY_ENTITY,
            _fb_const.CONF_COMPRESSOR_FREQ_ENTITY,
            _fb_const.CONF_COMPRESSOR_FREQ_SENSOR,
            _fb_const.CONF_FLOW_METER_ENTITY,
        )
    ),
)
R.check(
    "an unrelated entity does not count as feedback",
    len(_fb_gaps({_fb_const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.hp"})) == 4,
)
# The guard: a class whose config key const does not define is not offered.
_fb_saved_flow_key = _fb_const.CONF_FLOW_METER_ENTITY
del _fb_const.CONF_FLOW_METER_ENTITY
try:
    _fb_unkeyed = _fb_gaps({})
finally:
    _fb_const.CONF_FLOW_METER_ENTITY = _fb_saved_flow_key
R.check(
    "guard: with no flow key in const the table emits no flow row, and with it the row appears",
    [g["class"] for g in _fb_unkeyed] == ["power", "energy", "frequency"]
    and _fb_bare[-1] == {"class": "flow", "key": "flow_meter_entity"},
    f"{_fb_unkeyed}",
)


def _fb_attr(cfg):
    coord = _fb_coord({}, _config=dict(cfg))
    gap = _FbGapSensor(coord, _fb_entry())
    gap.hass = FakeHass()
    return gap.extra_state_attributes


R.check(
    "the gap advisor publishes the probe's list for the card to read",
    _fb_attr({}).get("feedback_gaps") == _fb_bare
    and _fb_attr({_fb_const.CONF_POWER_ENTITY: "sensor.p"}).get("feedback_gaps") == [],
    f"{_fb_attr({}).get('feedback_gaps')}",
)

# --- #2016 the flow meter: unit, conversion, and the thermal-output estimate --
from heatpump_optimizer import flow_meter as _fm  # noqa: E402
from heatpump_optimizer.inputs import (  # noqa: E402
    InputReader as _fmReader,
    normalize_flow_kg_s as _fm_norm,
)

_FM_KG_PER_L = 0.998
R.check(
    "L/min, L/s, m3/h and kg/s all convert to kg/s at 0.998 kg/L",
    abs(_fm_norm(60.0, "L/min") - _FM_KG_PER_L) < 1e-9
    and abs(_fm_norm(1.0, "L/s") - _FM_KG_PER_L) < 1e-9
    and abs(_fm_norm(3.6, "m³/h") - _FM_KG_PER_L) < 1e-9
    and abs(_fm_norm(2.0, "kg/s") - 2.0) < 1e-9
    and _fm_norm(5.0, "furlongs/fortnight") is None
    and _fm_norm(5.0, None) is None,
)
# A planted flow and temperature difference: 0.25 kg/s of water cooling 5 K
# at c_p 4.186 kJ/(kg K) hands over 0.25 * 4.186 * 5 = 5.2325 kW.
R.check(
    "a planted 0.25 kg/s over a 5 K drop is 5.2325 kW",
    abs(_fm.thermal_output_kw(0.25, 45.0, 40.0) - 5.2325) < 1e-9,
    f"{_fm.thermal_output_kw(0.25, 45.0, 40.0)}",
)
R.check(
    "no drop, a rise or a missing temperature is no estimate",
    _fm.thermal_output_kw(0.25, 40.0, 40.0) is None
    and _fm.thermal_output_kw(0.25, 38.0, 40.0) is None
    and _fm.thermal_output_kw(0.25, None, 40.0) is None
    and _fm.thermal_output_kw(0.25, 45.0, None) is None
    and _fm.thermal_output_kw(None, 45.0, 40.0) is None,
)


def _fm_reader(cfg, flow_state, unit="L/min"):
    states = {
        "sensor.flow": FakeState(flow_state, last_updated=minutes_ago(1, NOW), unit=unit),
        "sensor.sup": FakeState("45.0", last_updated=minutes_ago(1, NOW), unit="°C"),
        "sensor.ret": FakeState("40.0", last_updated=minutes_ago(1, NOW), unit="°C"),
    }
    full = {
        _fb_const.CONF_FLOW_METER_ENTITY: "sensor.flow",
        _fb_const.CONF_HEAT_PUMP_SUPPLY_TEMP_ENTITY: "sensor.sup",
        _fb_const.CONF_HEAT_PUMP_RETURN_TEMP_ENTITY: "sensor.ret",
        **cfg,
    }
    return _fmReader(FakeHass(states), full, now=lambda: NOW), full


_fm_r, _fm_cfg = _fm_reader({}, "15.0")
_fm_kw = _fm.read_heat_output_kw(_fm_r, _fm_cfg)
R.check(
    "the estimate follows the sensor: 15 L/min over a 5 K drop",
    _fm_kw is not None and abs(_fm_kw - 15.0 / 60.0 * 0.998 * 4.186 * 5.0) < 1e-6,
    f"{_fm_kw}",
)
_fm_r2, _fm_cfg2 = _fm_reader({}, "30.0")
R.check(
    "doubling the flow doubles the estimate (null control for the follow claim)",
    abs(_fm.read_heat_output_kw(_fm_r2, _fm_cfg2) - 2 * _fm_kw) < 1e-9,
)
R.check(
    "an unavailable or negative flow reading is absent",
    all(
        _fm.read_heat_output_kw(*_fm_reader({}, bad)) is None
        for bad in ("unavailable", "unknown", "-3.0", "nan")
    ),
)
R.check(
    "a power or a frequency signal keeps the estimate off (the signal outranks the flow meter)",
    _fm.read_heat_output_kw(*_fm_reader({_fb_const.CONF_POWER_ENTITY: "sensor.p"}, "15.0")) is None
    and _fm.read_heat_output_kw(
        *_fm_reader({_fb_const.CONF_COMPRESSOR_FREQ_SENSOR: "sensor.hz"}, "15.0")
    ) is None,
)
_fm_unset = _fm_reader({}, "15.0")
_fm_unset[1].pop(_fb_const.CONF_FLOW_METER_ENTITY)
R.check(
    "null control: with the flow key unset nothing is estimated",
    _fm.read_heat_output_kw(*_fm_unset) is None,
)
from heatpump_optimizer.sensor import CurrentPowerSensor as _FmPowerSensor  # noqa: E402


def _fm_power_attrs(data):
    sens = _FmPowerSensor(_fb_coord(data), _fb_entry())
    sens.hass = FakeHass()
    return sens.extra_state_attributes


R.check(
    "the thermal-output estimate is published on the recommended-power sensor, and absent stays None",
    _fm_power_attrs({"measured_heat_output_kw": 1.23456})["measured_heat_output_kw"] == 1.235
    and _fm_power_attrs({"measured_heat_output_kw": None})["measured_heat_output_kw"] is None
    and _fm_power_attrs({})["measured_heat_output_kw"] is None,
)
from heatpump_optimizer.config_flow import _OPTION_FIELDS as _fm_fields  # noqa: E402

R.check(
    "the options step asks for the flow sensor beside the compressor frequency sensor",
    any(f.key == _fb_const.CONF_FLOW_METER_ENTITY and f.group == "compressor" for f in _fm_fields),
)
R.check(
    "an unknown flow unit is absent rather than guessed",
    _fm.read_heat_output_kw(*_fm_reader({}, "15.0", unit="gal/min")) is None,
)


sys.exit(R.close("UX9 EXTRACT CHECKS"))
