# Round 9 · D1 · verifier V1 (reproduce): lc unit (D1-s2-91)

Evidence tree: origin/handoff/audit-r9-evidence at 79aa98ec (baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1). Python 3.14.0rc2, numpy 2.4.6, scipy 1.17.1. Machine: 4 vCPU cloud container (box G1-V1). load1 2.21–2.44, thread_factor 1.0.

Tally: 1 verify.

## D1-s2-91 — FlowCurveBias.observe raise aborts the cycle's accuracy pipeline · VERIFY (medium)
- **Re-run** (`lc_flow_bias_containment.py`, load1 2.21):
  - perturbed arm (samples=-1): perturbed_raises=5/5, perturbed_scored_after_fold=0/5;
  - null control (samples=0): null_control_raises=0/5, null_control_scored_after_fold=5/5.

  Exact match.
- **Perturbation:** the harness's two arms (samples=-1, guard bypassed, against samples=0) move 0→5 raises and 5→0 scored, as stated.
- **Leave-one-out:** the 5 cells repeat one deterministic scenario, so any single drop preserves the ratios.
- **Reach:** `coordinator.py:4671` calls `self._record_accuracy()` unwrapped. Its siblings `_command_frequency` and `_async_drive_pumps` are each wrapped in try/except with a "never allowed to break the cycle" comment. The only catch is the outer `except Exception` at `:4698`, which fails the whole cycle as `UpdateFailed`. This is a plain synchronous call, not executor-routed, so it is not a FakeHass artefact.
- **Trigger:** `flow_lift.py:210`'s `from_dict` refuses `samples < 0`, so the -1 state is reachable only through corruption or a separate regression. Medium stands.
- **Metric:** count of 5 real `_record_accuracy()` calls, with `_flow_bias.samples` forced to -1, that raise uncaught, and the count that still score post-fold, against samples=0.
