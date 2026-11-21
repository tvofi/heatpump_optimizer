"""Clean fixture: one lift owner, and the floor write priced by a plant gain."""
from .thermal_model import start_flow_min_lift_k


def _band_kw(params):
    return params.min_electrical_power, params.max_electrical_power


def _flow_target(inp, inlet_c):
    p_min, _p_max = _band_kw(inp.params)
    lift_k = max(start_flow_min_lift_k(inp.config), p_min * inp.lift_k_per_kw)
    return inlet_c + lift_k


def _nudged(inp):
    return _band_kw(inp.params)[0] or 0.0
