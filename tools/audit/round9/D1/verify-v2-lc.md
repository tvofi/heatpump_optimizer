# Verifier V2 (independent), unit lc — D1

## D1-s2-91: FlowCurveBias.observe raise aborts the cycle's accuracy pipeline

Step 1 (re-run finder's harness, `tools/audit/round9/D1/s2/leads/lc_flow_bias_containment.py`):
`perturbed_raises=5/5`, `perturbed_scored_after_fold=0/5`, `null_control_raises=0/5`,
`null_control_scored_after_fold=5/5`. cpu_s=0.008, thread_factor=1.0, load1=0.85, swapins=0.
Matches the finder's recorded value exactly (no mismatch).

Step 2 (own harness, `tools/audit/round9/D1/verify-v2/lc_v2_tail_containment.py`):
own metric — one level further out than the finder's. The finder measured
whether `_record_accuracy`'s own internal scoring calls run after
`_fold_flow_lift` raises. This harness (a) confirms via
`inspect.getsource(_async_update_data)` that `_record_accuracy()`,
`_track_realised_peak()`, `_async_save_accuracy()` and
`_async_save_energy_totals()` are four bare, sequential statements inside one
unguarded `try` block (`source_order_confirmed=1`), then (b) drives that exact
four-call sequence on an honestly-primed real coordinator: with
`samples=-1`, `perturbed_all_three_skipped=5/5` (0 of 3 downstream calls ran on
every cycle); with `samples=0` (null control), `null_all_three_ran=5/5` (all 3
ran every cycle). cpu_s=0.017, thread_factor=1.0, load1=0.37, swapins=0.

Metric definitions:
- Finder: of 5 real `_record_accuracy()` calls, count that raise
  `ZeroDivisionError`, and count whose post-fold accuracy-scoring calls still
  run that cycle.
- V2 (mine): of 5 real coordinators driven through the caller's own bare,
  unguarded four-call sequence (`_record_accuracy`, `_track_realised_peak`,
  `_async_save_accuracy`, `_async_save_energy_totals`), the count of the three
  post-fold calls that execute per cycle.
Both are comparable: the finder's is the inner seam (inside
`_record_accuracy`), mine is the outer seam (the caller's own bookkeeping),
same mechanism, same direction, same perturbation.

Attacks (verifier.md step 3, in order):
1. Contention: both harnesses are pure counts (no timing claim); load1 quoted
   above for both re-run and own harness. Not an issue for a count metric.
2. Wrong gate mode: not applicable — this is not a mutation/gate-mode claim,
   it is a live-code containment claim, reproduced directly against
   production `coordinator.py` and `flow_lift.py`.
3. Grid artefact: not an aggregate over a scenario grid; N=5 real,
   independent coordinator instances, no cell-dropping needed.
4. Null control: present in both the finder's harness and mine
   (`samples=0`), and both show the raise/skip effect vanishes at the control
   (`null_control_raises=0/5`, `null_all_three_ran=5/5`). Passes.
5. Real HA reachability: the mechanism is pure Python arithmetic
   (`self.samples + 1` denominator hitting 0), reached through the real
   `HeatPumpOptimizerCoordinator._record_accuracy` → `_fold_flow_lift` →
   `FlowCurveBias.observe` call chain and the real, unguarded caller sequence
   in `_async_update_data`; nothing here depends on `FakeHass`'s
   inline-executor shortcut (confirmed by reading `harness.py` — the fold and
   the caller's tail run entirely on the event loop, no
   `async_add_executor_job` in this path). Reachable identically in real HA.
6. Severity: `medium` is earned by consequence — this requires
   `_flow_bias.samples` to already be corrupted to a value the *existing*
   `flow_lift.py:210` guard exists to refuse (i.e. it is a second-line-of-
   defense/blast-radius gap, not independently reachable through normal
   operation), but once triggered it takes down the *entire* update cycle
   (peak tracking, accuracy persistence, energy-totals persistence) rather
   than just the one learner — a real amplification of an already-guarded
   failure mode, not itself a user-reachable defect. `medium` is not
   inflated.

Step 4: not a test-gap claim (this is a robustness/containment finding, not
a suite-gap finding); N/A.

**Vote: verify.** Both the finder's number and my own, independently-measured,
one-level-further-out number agree exactly, both null controls hold, and the
mechanism is confirmed by direct source reading (`flow_lift.py:170-173`,
`coordinator.py:9149-9171`, `coordinator.py:4671-4672` — no per-fold or
per-call try/except, only the outer blanket `except Exception` at
`coordinator.py`'s end of `_async_update_data`).
