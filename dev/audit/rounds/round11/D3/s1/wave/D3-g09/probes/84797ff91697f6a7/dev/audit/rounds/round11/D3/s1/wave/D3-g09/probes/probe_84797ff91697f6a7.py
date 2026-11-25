#!/usr/bin/env python3
# Metric: the adopted action's "power_normalized" after one HeatPumpOptimizerCoordinator._run_system_identification
#   whose armed experiment answers an override of 0.5 kW, for entries with heat_pump_max_power 5.0 (default-like),
#   1.0 (the config flow's minimum, config_flow.py:1851 _number(1, 20, ...)), 0.5, 0.05 and 0.0 (below the flow's
#   minimum: only a hand-edited entry), each resolved through the coordinator's own config path.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g09/probes/probe_84797ff91697f6a7.py
# EXPECTED RESULT differing_cells_flow_reachable=0 (every resolved max power >= 1.0 gives equal arms); cells
#   differ only where the resolved max power is < 0.1 (0.05: 5.0 vs 10.0; 0.0: ZeroDivisionError).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g09 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._run_system_identification
#   (coordinator.py:11091 `override / max(ctx._thermal_params.max_electrical_power, 0.1)`).
# Perturbation: mutant 84797ff91697f6a7, the max(..., 0.1) clamp dropped, in memory. Direction: none at a max power
#   >= 0.1 kW; a larger normalized power (or a ZeroDivisionError) below it.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _probe_lib as L  # noqa: E402
import _sysid_common as S  # noqa: E402

OLD = "override / max(ctx._thermal_params.max_electrical_power, 0.1)"
NEW = "override / (ctx._thermal_params.max_electrical_power)"
MUT = L.mutant(S.C, "_run_system_identification", OLD, NEW)
reach = other = 0
for entry_kw in (5.0, 1.0, 0.5, 0.05, 0.0):
    vals = {}
    for name, fn in (("baseline", None), ("mutant", MUT)):
        c = S.force_phase(S.fresh(indoor_temp_entity="sensor.indoor", outdoor_temp_entity="sensor.outdoor",
                                  heat_pump_max_power=entry_kw), "PHASE_ARMED")
        resolved = c._ctx._thermal_params.max_electrical_power
        n, action, _ = S.run(c, fn, override=0.5)
        vals[name] = action.get("power_normalized") if isinstance(action, dict) else action
    if vals["baseline"] != vals["mutant"]:
        if resolved >= 1.0:
            reach += 1
        else:
            other += 1
    print(f"RESULT entry_max_kw={entry_kw} resolved_max_kw={resolved} power_normalized_baseline={vals['baseline']}"
          f" power_normalized_mutant={vals['mutant']}")
print(f"RESULT differing_cells_flow_reachable={reach}")
print(f"RESULT differing_cells_below_flow_minimum={other}")
L.trailer()
