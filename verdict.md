Fix review: merge 1eadcbb3b41198cd4b74c7af16d6b6673308dd84

bus-nonce: b6b7eef21ab45576b05f20d961a0d9f6

## Scope

PR #3009, R10-COP-GATE item E (vent freeze), round 1. I measured head 1eadcbb3b41198cd4b74c7af16d6b6673308dd84 in a detached worktree. Its merge base with origin/main is 7d6a95e5e. I held the fix to the minimal fixer brief in the approved design (round-3 note d25be122; `Design review: approve ce5ca88b` at 74f35d42). Before posting, the remote branch and refs/pull/3009/head still read 1eadcbb3b, so the head did not move during the review. `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the contract I followed is current.

## Findings

- coordinator.py is code-owned, so tvofi's approving review is required at merge. This verdict does not replace it. Carry: dismissed: the code-owner rule in main-protect-checks enforces it at merge, and nothing passes to a later stage
- `tests / mutation-pins (1)` was still in_progress when I posted. The mutation-autofix lane owes the five ADDED UNPINNED pins listed below. If its bot commit only adds ledger pins, it should carry this verdict (review_carry.py), not re-open it. Carry: dismissed: the ci-autofix lane is already running for this PR, and any other head move is a re-review by rule

## Evidence

- RESULT seam: `_learning_frozen(self, *keys, room_air: bool = True)` fails closed. Only the `ventilation` branch is gated on `room_air`. External heat, pump signals, defrosting, unusable inputs, boost and `_tail_freeze` all keep their order and still fire. A mutant flipping the default to `False` fails 9 of 4611 features checks, so the fail-closed default is pinned.
- RESULT sites match the brief with no departure:
  - the DHW learner wiring at `:3405` is `functools.partial(..., room_air=False)`;
  - the probe at `:9926` passes `room_air=False`;
  - `_fold_measured_cop` reads `heat_kw` before the freeze (`:5017`) and passes `room_air=heat_kw is None and not counter` (`:5018`). That is the brief's "relevant only when this cycle has no measured heat", and `heat_kw` is not reassigned between the old and new read points;
  - `_fold_flow_lift` (`:878`) and `_freq_fold_blocked` (`:1152`) have no edit.
- RESULT class census: I ran `grep -n '_learning_frozen(' coordinator.py`. It returns the def plus 13 call sites (878, 1152, 5018, 5311, 5437, 5601, 8971, 9388, 9760, 9780, 9926, 10773, 10858). A grep for non-call references finds only the `:3405` partial. Other modules (boost, inputs, pump_signals, early_cutoff, topology, thermal_model) name it in comments or docstrings only. This matches the body's census and dispositions. `room_air` appears at 3 call sites plus the def.
- RESULT features at the head: `ALL 4611 FEATURE CHECKS PASSED`, rc=0, wall time 8m05s (ev/features_head.log).
- RESULT mutation proof: I ran each one-line mutant through the full tests/features.py (ev/mut_*.log). All were killed:
  - vent branch without `room_air`: 4 failed, matching the body;
  - vent GUARD_OFF: 12 failed (the body said "not run");
  - default `room_air=False`: 9 failed;
  - COP `room_air=True`: 3 failed, matching the body;
  - COP `room_air=False`: 1 failed (the inferred-COP check), matching the body;
  - COP `and`→`or`: 3 failed, matching the body;
  - COP GUARD_OFF: 5 failed (the body said "not run");
  - DHW partial reverted to the bare method: 1 failed, matching the body;
  - probe back to the default: 1 failed, matching the body;
  - probe GUARD_OFF: 3 failed (the body said "not run").
  
  So every site in the body's `## Unpinned sites` list has a killing driver. The three GUARD_OFF kills the body left unrun are now measured.
- RESULT null control: a run with no counter and no flow heat still gets COP_REFUSED_FROZEN under the latch, exactly as on main. The inferred-COP check pins this, and the COP `room_air=False` mutant breaks it. In the harness learners arm, the inferred `cop(_fold_measured_cop)` row reads `refused:learners_frozen` at both ends.
- RESULT finder's harness: I ran `dev/audit/harnesses/r10_cop_gate_vent.py` at the merge base (7d6a95e5e, the head's own copy of the harness against the base tree) and at the head. Both exited rc=0 with 118 output lines.
  - The output differs on exactly 3 lines, all in the learners arm. The counter row goes from `refused:learners_frozen` to `passes freeze (span_open)`, the flow-heat row from `refused:learners_frozen` to `passes freeze (None)`, and the dhw row from `frozen:ventilation` to `runs`. This re-derives the body's 3-line figure.
  - The `_fold_flow_lift under a window` block (19 lines, including latch-set `folds=0`) did not change. Nor did the cusum and window arms, or the buffer, sysid and house rows.
  - The latch arm (item 9) reads ventilation, ventilation, None, None, so the reason still resets each cycle.
  - Caveat: the harness is the design's Appendix A, committed by the fixer with two declared edits (the counter and flow rows, and the `**kw` forwarding). The packet lists no finder's harness. There is no separate finder copy, so I used this one.
- RESULT side harnesses at both ends: `r10_heat_meter.py` exits rc=0 and `r10_thermal_power_option.py` exits rc=1 at both the base and the head. In both, `diff` shows only the `TREE head` line and the paths in tracebacks, which matches the body.
- RESULT the brief's per-item checks:
  - **2b (stale reading):** the stale entity is refused by the input-health branch (`stale:...`) ahead of the vent branch. The check reads it through the real `observe_water`, and the fresh null folds.
  - **5 (latch-only learners):** the room-air check pins buffer, draw-range `frozen`, sysid, house, lower floor and `flow_bias_folds == 0`, with a latch-clear null.
- RESULT structure: `python3 tests/structure.py` rc=0 at the head.
- RESULT merge: `git merge-tree --write-tree origin/main(4d2f32b2e) 1eadcbb3b` rc=0, no conflict (ev/merge_tree.txt). The 3 main commits past the merge base touch no file in this diff.
- RESULT VERSION, the manifest, RELEASE_NOTES.md, tests/golden/ and both claim files are untouched by the three-dot diff.
- RESULT the ledger: deleting pin `286162d5` follows from the edited anchor line (a STALE PIN). The movement comes from the line change, not from editing the instrument. The five replacement sites are the CI's ADDED UNPINNED list.
- RESULT CI on 1eadcbb3b (check-runs API, read at review end):
  - Every check concluded success or skipped, except:
    - `tests / mutation`: failure;
    - `tests / mutation-pins (1)`: in_progress;
    - a duplicate `prelude` (run 41115103413): in_progress. The `prelude` run that belongs to the main run 41115104357 is green.
  - I read the `tests / mutation` log. It is `MUTATION TABLE REFUSED -- 3623 unpinned against 3620 at the ratchet base`. The 5 added sites are exactly the body's five (5018 BOOLOP and GUARD_OFF, 6641 BOOLOP and GUARD_OFF, 9926 GUARD_OFF). These are unpinned sites, not survivors: each is killed above.
  - The body answers this red per ci-autofix.md and defect-root-cause.md, naming ci_predict.py as the standing cheaper detector that predicted it.
  - No `pr-contract` run appears in this head's check-runs yet. The trigger is answered in the body, and I checked that it was answered, not the answer.
- RESULT forward-carry: the body states `none`. The packet's carry_audit routes its one Friction item as dismissed. The design's "serialize with #2262" does not name a PR (pulls/2262 returns 404). The counter path (#2261) is already in the base.
