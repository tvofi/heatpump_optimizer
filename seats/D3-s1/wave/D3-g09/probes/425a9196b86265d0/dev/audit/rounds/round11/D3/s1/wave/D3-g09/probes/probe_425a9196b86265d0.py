#!/usr/bin/env python3
# Metric: per one HeatPumpOptimizerCoordinator._run_system_identification(prices) with the experiment NOT active
#   (phases IDLE, DONE, ABORTED): (a) the adopted plan action and the experiment's scalar state, compared arm
#   against arm (behaviour), and (b) the number of off-loop sysid jobs dispatched (coordinator._await_off_loop:
#   the process-worker round trip), counted.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g09/probes/probe_425a9196b86265d0.py
# EXPECTED RESULT behaviour_differs_<phase>=0 for every inactive phase; offloop_jobs_<phase>_baseline=0,
#   offloop_jobs_<phase>_mutant=1 (or 0 where hold_reason stands it down first); null control: phase ARMED (active),
#   where the guard is not taken and both arms agree.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g09 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._run_system_identification
#   (coordinator.py:11057 `if not self._sysid.active:`).
# Perturbation: mutant 425a9196b86265d0, the guard -> `if False:`, in memory. Direction: behaviour unchanged
#   (sysid.step and stand_down/abort return at once on an inactive experiment, sysid.py:1510/1754); the cost moves
#   up by one off-loop job per cycle where hold_reason is None.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _probe_lib as L  # noqa: E402
import _sysid_common as S  # noqa: E402

OLD = "if not self._sysid.active:"
NEW = "if False:"
MUT = L.mutant(S.C, "_run_system_identification", OLD, NEW)
tried = []
for cfg_label, cfg in (("default", {}), ("rooms", dict(indoor_temp_entity="sensor.indoor",
                                                      outdoor_temp_entity="sensor.outdoor"))):
    for phase in ("PHASE_IDLE", "PHASE_DONE", "PHASE_ABORTED", "PHASE_ARMED"):
        out = {}
        for name, fn in (("baseline", None), ("mutant", MUT)):
            c = S.force_phase(S.fresh(**cfg), phase)
            out[name] = S.run(c, fn)
        (nb, ab, sb), (nm, am, sm) = out["baseline"], out["mutant"]
        differs = int(S.scrub(ab) != S.scrub(am) or sb != sm)
        tag = f"{cfg_label}_{phase.split('_')[1].lower()}"
        tried.append(tag)
        print(f"RESULT behaviour_differs_{tag}={differs}")
        print(f"RESULT offloop_jobs_{tag}_baseline={nb} offloop_jobs_{tag}_mutant={nm}")
        if differs:
            print(f"RESULT detail_{tag} baseline={ab} {sb} mutant={am} {sm}")
print(f"RESULT inputs_tried={' '.join(tried)}")
L.trailer()
