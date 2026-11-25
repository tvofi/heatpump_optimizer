"""_pv_forecast arms shared by the four PV probes of box D3-g09."""
import numpy as np
from unittest import mock
import _probe_lib as L
from harness import FakeState

C = L.HeatPumpOptimizerCoordinator
N = 8
SOLAR = np.array([0.0, 100.0, 300.0, 500.0, 600.0, 500.0, 300.0, 100.0])  # W/m2; step 0 is dark


class HAStates:
    """Home Assistant core's StateMachine.get, transcribed from homeassistant 2025.1.0 core.py:2151-2158
    (`return self._states_data.get(entity_id) or self._states_data.get(entity_id.lower())`); hacs.json
    requires >= 2025.2.0. tests/harness.py:FakeStates.get is a plain dict.get, which tolerates None."""

    def __init__(self, mapping):
        self._states_data = dict(mapping)

    def get(self, entity_id):
        return self._states_data.get(entity_id) or self._states_data.get(entity_id.lower())


def make(peak_kw=6.0, meter_kw=None, real_states=False, entity=None):
    states = {}
    cfg = dict(pv_enabled=True, pv_peak_kw=peak_kw)
    if meter_kw is not None:
        entity = entity or "sensor.pv_power"
        states[entity] = FakeState(str(meter_kw), unit="kW")
    if entity is not None:
        cfg["pv_production_entity"] = entity
    c = L.coord(states, **cfg)
    if real_states:
        c.hass.states = HAStates(states)
    return c


def run(c, name=None, fn=None):
    """(surplus list, summary dict) or the exception's name."""
    try:
        if fn is None:
            s, summ = c._pv_forecast(SOLAR, N)
        else:
            with mock.patch.object(C, name, fn):
                s, summ = c._pv_forecast(SOLAR, N)
        return [round(float(v), 4) for v in s], dict(summ)
    except Exception as exc:
        return f"raised {type(exc).__name__}: {exc}"
