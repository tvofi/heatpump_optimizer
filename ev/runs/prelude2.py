from dataclasses import replace as _dhw_store_with  # noqa: E402
def _dhw_ctx(*, prices, outdoor, n, dt, c_dhw, p_dhw_max, params,
             min_run_power=0.1, max_lead_steps=24, humidity=None,
             import_prices=None, tank_exo_kw=None):
    """The DHW planners' shared record for direct calls (#1776). The floor
    repair ranks at ``import_prices``, defaulting to the same series. The
    store is ``params``' own (its UA and limits) at capacity ``c_dhw``."""
    return _DhwPlanContext(
        prices=prices, import_prices=prices if import_prices is None
        else import_prices,
        outdoor_temps=outdoor, humidity=humidity,
        n_steps=n, dt=dt, store=_dhw_store_with(params.dhw_store, capacity_kwh_per_c=c_dhw),
        p_dhw_max=p_dhw_max, min_run_power=min_run_power,
        max_lead_steps=max_lead_steps, tank_exo_kw=tank_exo_kw)
from types import SimpleNamespace
from heatpump_optimizer import mixing_valve as _mv  # noqa: E402
from heatpump_optimizer.optimizer import (  # noqa: E402
    HeatPumpOptimizer as _StoreOpt,
    OptimizationConfig as _StoreCfg,
    OptimizationResult as _StoreRes,
    _Horizon,
    _price_ranked_start,
)
from heatpump_optimizer import thermal_model as _ct_tm  # noqa: E402
_CT_UA_KW = 0.111 / 45.0
_CT_RATE = _CT_UA_KW * 25.0 / (_ct_tm.WATER_SPECIFIC_HEAT * 544.0)
def _ct_params(combi=True, eps=0.85, potable=40.0, **kw):
    base = dict(buffer_tank_volume=504.0, mixing_valve_mode=_mv.MODE_SMART_WRITE,
                dhw_enabled=True, dhw_tank_volume=200.0, buffer_cooling_rate=_CT_RATE)
    base.update(kw)
    try:
        return ThermalParameters(dhw_combi_tank_enabled=combi, combi_dhw_effectiveness=eps,
                                 combi_potable_volume_l=potable, **base)
    except TypeError:
        return None
_CT_PRICES = np.full(96, 1.5)
_CT_PRICES[:20] = 0.8
_CT_PRICES[64:80] = 4.0
def _space234(self, h):
    if h.extra_starts:
        raise _Got234(
            tuple(np.asarray(s, dtype=float).copy() for s in h.extra_starts),
            np.asarray(h.prices, dtype=float).copy(),
            None if h.power_caps is None else np.asarray(h.power_caps, dtype=float).copy(),
            float(h.dt),
        )
    return _fake234
def _tight234(self, weather, initial_state, result, power_caps, *a, **kw):
    _fired234["n"] += 1
    if _fired234["n"] != 1:
        return False
    power_caps[:] = np.minimum(
        power_caps, np.maximum(np.asarray(result.power_schedule, dtype=float) * 0.5, 0.05)
    )
    return True
_StoreOpt._optimize_space_only = _space234
_StoreOpt._tighten_buffer_caps = _tight234
_fired_keep234 = {"n": 0}
def _space_keep234(self, h):
    if h.extra_starts:
        _keep234["seeded"] += 1
        return _seeded_keep234
    _keep234["unseeded"] += 1
    return _unseeded_keep234
def _tight_keep234(self, weather, initial_state, result, power_caps, *a, **kw):
    _fired_keep234["n"] += 1
    if _fired_keep234["n"] != 1:
        return False
    power_caps[:] = np.minimum(
        power_caps, np.maximum(np.asarray(result.power_schedule, dtype=float) * 0.5, 0.05)
    )
    return True
_StoreOpt._optimize_space_only = _space_keep234
_StoreOpt._tighten_buffer_caps = _tight_keep234
import heatpump_optimizer.optimizer as _hsr_om  # noqa: E402
from heatpump_optimizer.thermal_model import (  # noqa: E402
    MIN_RUNNING_DRAW_KW as _HSR_RUNS_AT,
    ThermalModel as _HsrTM,
    ThermalParameters as _HsrTP,
    ThermalState as _HsrTS,
)
def _hsr_opt(cost, clamp, p_min, loss=0.4):
    params = _HsrTP()
    params.mixing_valve_mode = "none"
    params.buffer_tank_volume = 750.0
    params.min_electrical_power, params.max_electrical_power = p_min, 5.5
    params.dhw_enabled, params.house_heat_loss_scale = False, loss
    return _hsr_om.HeatPumpOptimizer(
        _HsrTM(params), _hsr_om.OptimizationConfig(clamp_planned_levels=clamp, cycling_cost=cost))
def _hsr_p2_restart(best, objective, *args, **kwargs):
    out = _hsr_p2_real_restart(best, objective, *args, **kwargs)
    _hsr_p2_polished.append((float(objective(best.x)), float(objective(out.x)), np.array(out.x, float)))
    return out
_hsr_om._lbfgsb_restart = _hsr_p2_restart
