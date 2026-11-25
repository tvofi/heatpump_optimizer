Fix review: merge 7748bdc269efb9758d85b4ee81130a4f60534948

bus-nonce: 2d8a19c8ad154f7cf4f551340539ac96
pending-ci: gate

Round 4 on #3835, the first over the re-cut. Reviewed in full, three-dot against origin/main from merge base 3be37247e6, because the orchestrator's dispatch says the re-cut replaces the reviewed diff. The packet's scope line reads `delta` over fab2d371ed. The delta is the re-cut, so the two scopes cover the same production code.

## Notes

- Note: figure: the body's D12-s3-03 line ("`space_spans_folded` 2 -> 0 ... each pair's two ends in one hour") holds when the harness starts at 12Z. When it starts at 13Z it reads 3 -> 1. `inflated_spans_folded` 2 -> 0, `cop_records` 4 -> 2 and `inflated_space_spans` 2 at both ends hold in both hours (`ev/counter_spans_pinned.txt`). `counter_spans.py:128` takes its day from `dt_util.now()`, floored to the hour, so an unpinned run reproduces neither pair in some hours. Run unpinned at about 14:3xZ, base and head read the same (`ev/h_counter_spansseesdhwnomode_*.log`). The `--plan-only` null's `space_spans_folded` reads 4 at both ends here against the body's 3, flat as a null should be. The fix's claim (the head folds no inflated span) holds in every hour this seat pinned. Carry: dismissed: a body figure that depends on the hour the harness starts, and the claim it supports holds

## Evidence

- Prior findings, each re-checked with this reviewer's own mutants. Driver: `tools/audit/seat/features_block.py`, with a prelude from `--emit-prelude` at this head, on `R.section("R11-SEAM-learners: the one freeze predicate")`. Each mutant ran in its own worktree (`ev/mutants.py`, `ev/runmut.sh`, `ev/mut_*.log`, `ev/mut_summary.log`). Unmutated: `ALL 28 FEATURES BLOCK PASSED` (`ev/block_clean.log`).
  - `coordinator.py:1121` (now `:1124`), mutation-vacuous twice before. `tank.value if tank.ok else None` -> `tank.value` fails 1 of 28: "a stale first tank read is no evidence ...", reading `((50.0, 53.0), None)`. -> `None` fails 2 of 28. Resolved.
  - `coordinator.py:6134` (now `:6119-6120`), class-open before. The site reads `HeatEnergyMeter.served_space_alone` on `_pending_prediction["split"]`, and the step now runs before `_record_accuracy`.
    - Back to the next plan's channel kW through the meter (Ra): fails 1 of 28.
    - `_accumulate` counting every cycle as space (Rc): fails 1.
    - `served_space_alone` dropping its unplanned-charge conjunct (Rb): fails 2.
    - The same returning True with no split (Rd): fails 1.
    - Resolved: built, not excluded.
  - The prior round's O and P survivors (the house and lower-floor per-cycle asks without `evidence=_space_evidence(...)`, now `:5771` and `:5931`): each fails 1 of 28 on "an unplanned charge pauses the house and lower-floor learners ...", reading `{'house': ...}` or `{'lower': ...}` alone. Resolved.
  - Six further mutants on the evidence path, all killed:
    - X1: the meter's tank pair never shifts. Fails 2.
    - X2: the span's opening tank read is never set. Fails 1.
    - X3: `close_span`'s unplanned flag forced False. Fails 1.
    - X4: `booked_dhw_share` without the unplanned branch. Fails 1.
    - X5: `unplanned_charge` ignores `observed`. Fails 2.
    - X6: the draw-range gate with `NO_EVIDENCE`. Fails 1.
  - My mutants: 14 of 14 killed.
- Ordering, read in `coordinator.py`. `_observe_heat_energy` (`:6802`) and the per-cycle learners (`:6845`) run inside `_update_current_state`, before the solve adopts the next action. So `_commanded_split()` at `:5771` and `:5931` reads the interval that just settled. The room-history step reads that same interval's `_pending_prediction` split, before `_record_accuracy` replaces it.
- Class enumeration (step 6), design §5 E1-E3, patterns verbatim from design bee723ac4d (`ev/class_enum.txt`):
  - d3d66c4040: E1 35, E2 57, E3 15. The current merge base 3be37247e6 reads the same.
  - Head: E1 43, E2 57, E3 14.
  - The sorted lines, with line numbers stripped, are identical between d3d66c4040 and 3be37247e6 for each grep, so main adds no site since the body's enumeration.
  - E3 at the head no longer prints the room-history line.
- Finder's harnesses (step 2): the head's files copied into a 3be37247e6 worktree, with sha1 equal at both ends. Run on Linux, venv-ci python3, `OPENBLAS_CORETYPE=Haswell`, every run rc 0 (`ev/h_*_{base,head}.log`). Each body figure re-derives:
  - `m3_learner_freeze.py`: `contaminated_ingest` 3 -> 0.
  - `m3_away_drift.py`: `gains_profile_mean_over_g0_absent100pct_14d` 0.3796 -> 1.0000.
  - `m5_tankfall.py`: `booked_kwh_long_max` 3.0160 -> 0.0000 and `booked_kwh_short_max` 0.0389 -> 0.0000. `booked_kwh_unplanned_max` reads 3.0160 at both ends, carried to #3769.
  - `m5_drawrange.py --run-samples 200`: `narrowing_censored_kw` 4.100 -> 0.000. Null `uncensored_overstated_learned_max_kw` 4.000 at both ends.
  - `m5_crosscov.py`: `gain_recovery_mean` 0.5573 -> 0.7748, `gain_recovery_max` 0.5687 -> 0.8017, `scale_bias_nogain_mean` +0.0201 -> +0.0186, and the cost `gain_spurious_max` 0.0293 -> 0.0571.
  - `cop_duty_floor.py`: `defrost_inferred_selfset_2.2_2C_ignored` factor 0.684 count 96 -> factor 1.000 count 0. The null `defrost_inferred_matched_2C_ignored` reads factor 1.000 at both ends.
  - `counter_spans.py --plan-only`: `inflated_spans_folded` 0 and `cop_records` 3 at both ends (`space_spans_folded`: see the Note).
  - `counter_spans.py --sees-dhw --no-mode`: see the Note.
  - Not re-run: `m5_sysid.py`, `m2_sysid_plant.py`, `comments.py`, `m5_crosscov.py --perturb-ridge0`. These are cited from the body and not verified by this seat.
- Merge with main (step 13): `git merge-tree --write-tree origin/main 7748bdc269` exits 0, tree 80305f4284, with origin/main at 0e1eba2b4a (`ev/merge_tree.log`).
- Role contract current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- Claims (step 4): the diff touches no golden fixture and no claim file. `env_drift.py --claims-only 3be37247e6` prints `claims hygiene: ... ok` (`ev/env_drift_claims.log`). `--all` is CI's lane.
- Versions (step 5): `VERSION`, `manifest.json` and `RELEASE_NOTES.md` are untouched (three-dot `git diff --quiet` rc 0).
- Ratchet (step 14): `tests/structure.py` at the head prints `STRUCTURE RATCHET PASSED` (`ev/structure.log`). `structure_budgets.json` moves `class_excess_loc`, `max_class_loc` and `module_excess_loc` down only, and raises nothing. `node tools/policy/brief_lint.mjs` rc 0.
- Step 16: the diff adds no refusal of a pump write.
- CI: `merge_train.py classify 7748bdc269efb9758d85b4ee81130a4f60534948 --pr 3835` read rc=3 on every run, polled from 14:2xZ to 14:51Z. The last run printed `WAIT 7748bdc269efb9758d85b4ee81130a4f60534948 pending: gate red: none` (`ev/classify.log`). Hence `pending-ci: gate`. No red check exists at this head, so no `## Red checks` answer is owed. The body answers the earlier commits' reds (`tests / mutation`, `tests / briefs`, `tests / fast (3.14)`) under its `## Red checks`.
