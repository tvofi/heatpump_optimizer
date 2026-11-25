#!/usr/bin/env python3
# Metric: the outcome of HeatPumpOptimizerCoordinator._pv_forecast(solar, 8) (sum of surplus kW, or the exception
#   raised) for an enabled 6 kWp array with NO production entity configured (pv_production_entity None, the
#   entry_config default, and ""), under two `hass.states`: tests/harness.py:FakeStates (dict.get) and
#   Home Assistant core's StateMachine.get (transcribed in _pv_common.HAStates from homeassistant 2025.1.0).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g09/probes/probe_326b26f53972df61.py
# EXPECTED RESULT fake_none: baseline == mutant (why the suite cannot fail); ha_none: baseline a surplus,
#   mutant `raised AttributeError` ('NoneType' object has no attribute 'lower'); ha_empty: equal.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g09 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._pv_measured_production
#   (coordinator.py:9810 `if not entity_id:`), reached through _pv_forecast (coordinator.py:9826).
# Perturbation: mutant 326b26f53972df61, the guard -> `if False:`, in memory. Direction: under HA's state machine
#   the forecast for every PV install without a production meter raises instead of answering.
# Null control: the FakeStates arm, and the arm with a meter configured (the guard is not taken there).
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _probe_lib as L  # noqa: E402
import _pv_common as V  # noqa: E402

OLD = "if not entity_id:"
NEW = "if False:"
MUT = L.mutant(V.C, "_pv_measured_production", OLD, NEW)
print(f"RESULT default_pv_production_entity={L.coord()._config.pv_production_entity!r}")
print(f"RESULT empty_string_entity_resolves_to={L.coord(pv_production_entity='')._config.pv_production_entity!r}")
for label, kw in (("fake_none", dict()), ("fake_empty", dict(entity="")),
                  ("ha_none", dict(real_states=True)), ("ha_empty", dict(real_states=True, entity="")),
                  ("ha_meter", dict(real_states=True, meter_kw=3.0))):
    for name, fn in (("baseline", None), ("mutant", MUT)):
        r = V.run(V.make(6.0, **kw), "_pv_measured_production", fn)
        out = r if isinstance(r, str) else f"surplus_sum={sum(r[0]):.4f}"
        print(f"RESULT {label}_{name}: {out}")
L.trailer()
