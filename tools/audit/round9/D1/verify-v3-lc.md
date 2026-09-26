# D1 verify, lens V3 (reach and class), unit lc: D1-s2-91, box G1-V3

Evidence tree 79aa98ec (baseline 1936d5ca). The harnesses are in `tools/audit/round9/D1/verify-v3-lc/`, and the real-HA rig is `_realha_rig.py`.

## D1-s2-91: a FlowCurveBias.observe raise aborts the cycle's accuracy pipeline

- **Re-run** of `lc_flow_bias_containment.py` on the stub venv (CPython 3.14.0rc2):
  - Perturbed arm: 5/5 raises, and 0/5 cycles scored after the fold.
  - Null arm: 0/5 raises, 5/5 scored.
  - load1 0.00. The box owner re-ran it and got an exact match.
- **Own measurement**, `D1-s2-91_containment_via_fold_patch.py`. It patches the module-level `_fold_flow_lift` to raise and drives the real `_record_accuracy`.
  - Result: 5/5 exceptions propagate, and 0/5 cycles are scored.
  - Null arm: 0/5 and 5/5.
  - The same result from a trigger other than `samples=-1` puts the gap in the call shape.
- **Real HA**, `D1-s2-91_realha_reach.py`: a real coordinator on HA 2026.2.3 with no hastub.
  - Result: 5/5 raises, 0/5 scored.
  - load1 0.08, thread_factor 1.005.
  - The box owner re-ran it with the same result.
- **Mechanism.** At coordinator.py:4657-4674, `_command_frequency` and `_async_drive_pumps` each carry a local try/except. `_record_accuracy` has none, so its raise falls to the outer `except`, which turns it into `UpdateFailed`.
- **Trigger.** `samples<0` is rejected only in `FlowCurveBias.from_dict`, so reaching it needs a corrupted or rolled-back store. Once reached, it repeats every cycle.
- **Severity:** medium. The whole cycle fails loudly and persistently, and there is no self-recovery.
- **Seam rule:** enumerates all. It lists the 4 unfenced outer calls at :4671-4674.
- **Class:** P2. This is my correction of the sub-seat's `new`: the fence is present on sibling calls and missing on this one. It is the same phenomenon as leads D1-s2-51.
- **Vote:** verify.
