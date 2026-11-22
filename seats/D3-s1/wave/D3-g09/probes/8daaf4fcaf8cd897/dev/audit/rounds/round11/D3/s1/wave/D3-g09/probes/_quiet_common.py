"""_record_quiet_comfort_period arms shared by the three quiet-comfort probes of box D3-g09."""
import types
import numpy as np
from unittest import mock
import _probe_lib as L

C = L.HeatPumpOptimizerCoordinator


def tie_search(target, ratio_of, seeds):
    """First vector [*seed[:-1], x] (x walked float by float, 4000 ulps either side of seed[-1]) whose
    ratio_of(v) equals target exactly in float64; None when no such float exists in the walk."""
    for seed in seeds:
        for direction in (np.inf, -np.inf):
            x = float(seed[-1])
            for _ in range(4000):
                v = np.array(list(seed[:-1]) + [x], dtype=float)
                if ratio_of(v) == target:
                    return v
                x = float(np.nextafter(x, direction))
    return None


def evidence_delta(prices, power, dt_power_kw_steps=None, fn=None):
    """Change in the comfort learner's evidence after one _record_quiet_comfort_period on a flat plan
    (room trajectory constant at 21.0), and whether record_quiet_period was called (0/1)."""
    c = L.coord(comfort_learning_enabled=True)
    c._optimization_result = types.SimpleNamespace(
        prices=list(map(float, prices)), power_schedule=list(map(float, power)),
        room_temp_trajectory=[21.0] * (len(power) + 1))
    calls = []
    inner = c._comfort_learner.record_quiet_period

    def counted(*a, **k):
        calls.append(a)
        return inner(*a, **k)

    c._comfort_learner.record_quiet_period = counted
    before = float(c._comfort_learner.evidence)
    if fn is None:
        c._record_quiet_comfort_period()
    else:
        with mock.patch.object(C, "_record_quiet_comfort_period", fn):
            c._record_quiet_comfort_period()
    return round(float(c._comfort_learner.evidence) - before, 6), len(calls), c._opt_config.dt_hours
