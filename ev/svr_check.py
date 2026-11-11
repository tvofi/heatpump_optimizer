import sys, numpy as np
class _R:
  fails=0
  def check(self,name,cond,detail=""):
    print(("PASS " if cond else "FAIL ")+name[:70]); print("  ",detail[:600]);
    _R.fails+= (not cond)
R=_R()
# --- R10-SAV-VALUATION-RESIDUE: stored heat bought back at the part-load law ---
from heatpump_optimizer import optimizer as _svr_optmod  # noqa: E402
from heatpump_optimizer.optimizer import (  # noqa: E402
    HeatPumpOptimizer as _SVR_OPT,
    OptimizationConfig as _SVR_CFG,
)
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel as _SVR_MODEL,
    ThermalParameters as _SVR_PARAMS,
    ThermalState as _SVR_STATE,
    power_for_heat_per_cop_kw as _svr_inverse,
)

_SVR_HOURS = 0.25 * 96 * 0.25  # the cheapest quarter of the 24 h, 15 min horizon


def _svr_opt(derate):
    p = _SVR_PARAMS(min_electrical_power=0.5, max_electrical_power=6.0)
    p.cop_partload_derate = derate
    return _SVR_OPT(_SVR_MODEL(p), _SVR_CFG(horizon_hours=24, time_step_minutes=15)), p


def _svr_state(t):
    return _SVR_STATE(room_temperature=t, slab_temperature=t + 4.0, outdoor_temperature=-5.0,
                      upper_floor_temperature=t, lower_floor_temperature=t,
                      buffer_tank_temperature=30.0, dhw_temperature=50.0)


def _svr_figures(derate):
    opt, p = _svr_opt(derate)
    prices, out = np.linspace(0.5, 2.0, 96), np.full(96, -5.0)
    cost, batch = opt._terminal_cost(prices, out)
    cold = np.full(96, 12.0)
    term = cost(cold, cold, cold, cold, None)
    row = batch({k: cold[None, :] for k in ("room", "slab", "upper", "lower", "buffer")})[0]
    # A deficit whose refill rate sits on the band, below max power.
    mild = np.full(96, 20.6)
    band = cost(mild, mild, mild, mild, None)
    warm_end, cold_end = _svr_state(21.0), _svr_state(12.0)
    charge = opt._deferred_energy_cost(warm_end, cold_end, prices, out)
    credit = opt._deferred_energy_cost(cold_end, warm_end, prices, out)
    rp = float(np.percentile(prices, 25)) * opt.config.price_weight
    return dict(term=term, band=band, row=row, charge=charge, credit=credit, rp=rp, p=p, opt=opt)


_svr_lin, _svr_der = _svr_figures(0.0), _svr_figures(0.2)


def _svr_law(fig, key):
    hpc = _svr_lin[key] / fig["rp"]
    return fig["rp"] * np.copysign(
        float(_svr_inverse(fig["p"], abs(hpc), hours=_SVR_HOURS)), hpc)


R.check(
    "R10-SAV-VALUATION-RESIDUE: under a part-load derate the terminal cost and "
    "the deferred settlement buy stored heat back at the same law, the tree's "
    "own inverse at the deficit spread over the cheapest quarter of the "
    "horizon; the batch twin agrees bit for bit, a surplus is credited at the "
    "law a deficit is charged; null control: with no derate both laws are "
    "None and the figures are the linear ones",
    _svr_der["term"] > _svr_lin["term"] > 0.0
    and abs(_svr_der["term"] - _svr_law(_svr_der, "term")) <= 1e-9 * _svr_der["term"]
    and 1.0 < _svr_der["band"] / _svr_lin["band"] < 1.0 / (1.0 - 0.2)
    and abs(_svr_der["band"] - _svr_law(_svr_der, "band")) <= 1e-9 * _svr_der["band"]
    and _svr_der["row"] == _svr_der["term"] and _svr_lin["row"] == _svr_lin["term"]
    and _svr_der["charge"] > _svr_lin["charge"] > 0.0
    and abs(_svr_der["charge"] - _svr_law(_svr_der, "charge")) <= 1e-9 * _svr_der["charge"]
    and _svr_der["credit"] == -_svr_der["charge"]
    and _svr_optmod._refill_law(_svr_lin["p"], 96, 0.25) is None
    and _svr_optmod._refill_law(_svr_der["p"], 96, 0.25) is not None,
    f"linear {({k: _svr_lin[k] for k in ('term', 'band', 'row', 'charge', 'credit')})} "
    f"derated {({k: _svr_der[k] for k in ('term', 'band', 'row', 'charge', 'credit')})}",
)


sys.exit(1 if _R.fails else 0)
