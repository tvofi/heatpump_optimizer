"""_predicted_next_room_temp arms shared by probe_33d708ab867fe5e7.py and probe_3dcdfbdd2542f33e.py."""
import types
from unittest import mock
import _probe_lib as L

C = L.HeatPumpOptimizerCoordinator


def make(interval, time_step=15.0):
    c = L.coord(optimization_interval=interval)
    c._mode = L.coord_mod.MODE_AUTO
    assert c._config.optimization_interval == interval
    oc = c._ctx._opt_config
    if oc.time_step_minutes != time_step:
        object.__setattr__(oc, "time_step_minutes", time_step)
    assert c._opt_config.time_step_minutes == time_step
    return c


def call(c, traj, fn=None):
    res = types.SimpleNamespace(room_temp_trajectory=list(traj), upper_temp_trajectory=[],
                                sensor_trajectory=lambda two_zone: list(traj))
    c._optimization_result = res
    try:
        if fn is None:
            return c._predicted_next_room_temp()
        with mock.patch.object(C, "_predicted_next_room_temp", fn):
            return c._predicted_next_room_temp()
    except Exception as exc:  # the mutant arm may raise where the baseline answers
        return f"raised {type(exc).__name__}"
