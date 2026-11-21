"""Clean fixture: the lift's owner chain."""
FLOW_MIN_LIFT_K = 5.0


def configured_flow_min_lift_k(config):
    v = (config or {}).get("flow_min_lift_k", FLOW_MIN_LIFT_K)
    return v if v and v > 0 else FLOW_MIN_LIFT_K


def start_flow_min_lift_k(config, hysteresis=None):
    lift = configured_flow_min_lift_k(config)
    return lift if hysteresis is None else max(lift, hysteresis)
