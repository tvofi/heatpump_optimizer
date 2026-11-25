NOW = datetime(2026, 2, 1, 12, 0, tzinfo=UTC)
import dataclasses
from harness import FakeEntry as _FakeEntry, FakeHass as _FakeHass
from heatpump_optimizer.coordinator import (
    HeatPumpOptimizerCoordinator as _Coord,
)
def _two_zone_learner(*, lower_entity=None, ratio=1.0, **extra):
    cfg = {
        "tibber_token": "x",
        "weather_entity": "weather.home",
        "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor",
        # Two-zone is inferred from the presence of zone settings rather than a
        # flag, so a bare `two_zone_enabled` would silently do nothing.
        "upper_floor_thermal_mass": 3.0,
        "lower_floor_thermal_mass": 8.0,
    }
    if lower_entity:
        cfg["lower_floor_temp_entity"] = lower_entity
    cfg.update(extra)
    c = _Coord(_FakeHass({}), _FakeEntry(data=cfg))
    c._apply_lower_floor_loss_ratio(ratio)
    return c
from harness import FakeEntry, FakeHass
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
_T6 = datetime(2026, 3, 28, 12, 0, tzinfo=UTC)
_LC_DATA = {
    "price_source": "entity",
    "price_entity": "sensor.prices",
    "weather_entity": "weather.home",
}
from heatpump_optimizer.coordinator import _fold_flow_lift  # noqa: E402
def _fl_coord(supply=55.0, returned=47.0, action=None, **extra):
    """A real coordinator on an interval the flow-bias fold should accept."""
    c = _t2_coord(**extra)
    c._current_state.outdoor_temperature = -5.0
    c._current_action = (
        dict(action) if action else {"power": 3.0, "dhw_power": 0.0}
    )
    c._measured_power = 2.6
    c._flow_bias.observe_temps(supply, returned)
    return c
_T2_DATA = {"tibber_token": "x", "weather_entity": "weather.home"}
def _t2_coord(**config):
    """A live coordinator over the fake bus, with config overrides applied."""
    return HeatPumpOptimizerCoordinator(
        FakeHass(), FakeEntry(data=dict(_T2_DATA, **config))
    )
from heatpump_optimizer.inputs import (  # noqa: E402
    InputReader as _fmReader,
    normalize_flow_kg_s as _fm_norm,
)
from heatpump_optimizer import room_history as _rh  # noqa: E402
_rh._fit = lambda x, y: (np.array([0.05, 1.0, 0.0]), np.array([10.0, _rh.MIN_T, 0.0]))
