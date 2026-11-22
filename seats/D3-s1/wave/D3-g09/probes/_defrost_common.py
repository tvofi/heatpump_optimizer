"""_settle_defrost arms shared by probe_0c99189b7639f1bd.py and probe_df697cc04154fbdd.py."""
import types
from unittest import mock
import _probe_lib as L

C = L.HeatPumpOptimizerCoordinator


def observed(seconds, fn=None, interval_min=30):
    """observe_duty calls (0/1) from one _settle_defrost on a measured-duty window `seconds` long."""
    c = L.coord(optimization_interval=interval_min)
    calls = []
    c._defrost.observe_duty = lambda *a, **k: calls.append(a)
    sample = types.SimpleNamespace(outdoor_temp=-2.0, humidity=85.0)
    window = types.SimpleNamespace(observed=True, seconds=float(seconds), duty=0.12, events=2)
    if fn is None:
        c._settle_defrost(sample, window)
    else:
        with mock.patch.object(C, "_settle_defrost", fn):
            c._settle_defrost(sample, window)
    return len(calls), c._config.optimization_interval * 60.0
