from heatpump_optimizer.optimizer import HeatPumpOptimizer as _PvOpt
from heatpump_optimizer.thermal_model import ThermalModel as _PvModel
from heatpump_optimizer.thermal_model import ThermalParameters as _PvParams
from profiles import house as _grad_house, prices as _grad_prices, weather as _grad_weather
from heatpump_optimizer import rooms as _rm  # noqa: E402
_RM_NOW = datetime(2026, 11, 16, 12, 0, tzinfo=UTC)
from heatpump_optimizer.optimizer import OptimizationConfig as _rl_Config  # noqa: E402
_RL_N = 48  # 12:00 to 24:00 at 15 min; the night floor holds from step 40 (22:00)
_rl_cfg = _rl_Config(min_temp=19.5, max_temp=23.0, target_temp=20.0,
                     comfort_temp_day=20.0, comfort_temp_night=20.0)
_RL_OPEN = dict(enabled=True, economy=False, open_window=False, away=False,
                manual_pin=False, two_zone=False)
class _RlOwner:
    """A stand-in coordinator: the side tables key on it weakly."""
def _rl_room(entity, temp, target, mode="heat", problem=None):
    return _rm.RoomReading(entity_id=entity, temperature_c=temp, target_c=target,
                           hvac_mode=mode, problem=problem)
_RL_A = _rl_room("climate.a", 18.0, 21.0)
_RL_REST = (_rl_room("climate.b", 20.4, 20.0), _rl_room("climate.c", 20.4, 16.0),
            _rl_room("climate.d", 17.0, 22.0, mode="off"))
_RL_ROOMS = (_RL_A,) + _RL_REST
def _rl_solve(readings=_RL_ROOMS, house=19.6, base=None, cfg=_rl_cfg, owner=None,
              start=_RM_NOW, n=_RL_N, **signals):
    """One scheduled solve's margins: (array or base, owner)."""
    owner = owner or _RlOwner()
    _rm.record(owner, readings)
    held = _rm.hold(owner, _rm.resolve(
        _rm.readings_of(owner), _rm.lift_of(owner), _rm.gate(**dict(_RL_OPEN, **signals)),
        cfg, house, start))
    return _rm.lifted(held, base, cfg, start, n), owner
