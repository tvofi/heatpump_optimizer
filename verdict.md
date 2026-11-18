Fix review: merge 54b8b9d469c448d54d5d8e204e651c908682e511

bus-nonce: 40fae36d014307bd6a97f6712f5b9d4c
pending-ci: gate

Round 1 (full scope, first review). Reviewed at head 54b8b9d469c448d54d5d8e204e651c908682e511; the body's figures were taken at 5cc4bd2c44e8, and `review_carry.py 5cc4bd2c44e8 54b8b9d469` prints `CARRY` (the delta is a clean main merge plus the delivery row). Every figure below was re-taken at 54b8b9d469 by this seat.

## Evidence

- Merge with main: `git merge-tree --write-tree origin/main 54b8b9d469` rc=0 (origin/main fd847a550c12); `LEDGER-MERGE: resolved tests/closures.json`, no claim-file conflict.
- Mutation proof, re-run in detached worktrees at the head (driver `ev/mutants/run.py`, results `ev/mutants/*.res`). The five mutants the body names are all killed, with the body's counts: M1 `placed` everything to data -> config_flow_steps 7 failed; M2 migrate minor clause deleted -> entities.py fails "a 7.1 entry migrates to 7.2 ..."; M3 `of(saving)`->`of(current)` -> 2 failed; M4 `**_WINDOW_PLACEHOLDERS` deleted -> 1 failed; M5 `>= 1.0`->`> 1.0` -> 3 failed. This seat's own mutants: M6 setup entry written unplaced -> killed (1); M7 `undone_settings` unplaced -> killed by features.py (1); M9 `_PREFILL_PAIRED` emptied -> killed (2); M10 reconfigure writes no options -> killed; M11 migration stamps without placing -> killed (entities.py); M12 uncapped refusal guard off -> killed (3); M8 `factory_settings` unplaced -> survives features.py (see Notes).
- Finder harnesses from plan/r11 50a932de3b2a: all 7 sha1s equal the body's. Each was run at base 8751943e17ef and at head 54b8b9d469 (`ev/finder_summary*.txt`, per-run logs `ev/finder_*.log`). These reproduce the body: h_computed `computed_kept_value_lost` 8->0, null 0/0; reconfig_shadow `shadowed_options_saved` 2->0, `prefill_shows_running_indoor` 0->1, null 0/0; cfg_data_options `continue_settings_in_data` 41->0, null 0/0; after_save_stray `entries_with_after_save` 2->0; prefill_placeholders `config_refusal_missing` 2->0, `config_refusal_changed_vs_preview` 3->0, `options_refusal_missing` 0/0; silent_prefill reads flat (cap deltas 0.000/-2.000 -> 0.000/0.000), as the body discloses.
- flow_errors.py at the head reads `cells_fired=7` of 9, not 9. Its two config.device_prefill cells raise `ValueError: not enough values to unpack`, because the harness plants `f._device_prefill = (key,)` and this diff changes that private attribute to a (keys, notes) pair. Those were the two cells holding all 8 base unfilled placeholders, so the head's 0 is 0 by construction. This seat changed only that one line, to the pair shape (`ev/flow_errors_adaptation.diff`; the adaptation is this seat's, not the finder's), and re-ran at the head: `cells_fired=9`, `unfilled_placeholders_total=0` (`ev/flow_errors_adapted_head.log`). The fix therefore holds on the finder's cells.
- Companion harness (the fixer's, disclosed as such in the body), run at both ends: `fraction_shown_beside_windows` 0->1, `uncapped_schedule_accepted` 1->0, nulls `capped_schedule_refused` 0/0 and `no_schedule_refused` 0/0 (`ev/companion_*.txt`). The base run used the head's copy of the harness, which falls back to `_prefill_schema` at the defect.
- Class enumeration, re-derived with this seat's own AST walk (`ev/class_enum.txt`): `async_update_entry`/`async_create_entry` calls with a `data` keyword return exactly the body's 7 sites. 5 write `placed` pairs; `OptionsFlow._save` and `DhwSetpointRepairFlow` are dispositioned in the body. No per-key `entry.data[...]`/`entry.data.get` reader remains in `custom_components/`. The options-only readers (`CONF_PREFILL_OFFER`, `CONF_DEBUG_COLLECT`) read the side that placement now guarantees.
- `VERSION`, manifest, `RELEASE_NOTES.md` and `tests/golden/` untouched in the three-dot diff; no claim file touched.
- Structure: `python3 tests/structure.py` -> `STRUCTURE RATCHET PASSED`. The only budget move is `class_excess_loc` 17382->17370, a lowering, with its reason in commit 6f6ce5f58e. It is earned by two identical `async_show_form` bodies becoming one `_prefill_page`.
- config_flow_steps.py at the head: `ALL 608 checks PASSED`. entities.py and features.py hit this seat's 230 s local cap (rc=124, no failure), so for those suites this verdict cites CI.
- No actuator-write refusal is added (step 16 n/a). The new `_uncapped_schedule_errors` is a form refusal, and its release is on the same page (lower the fraction or clear the schedule; null arms above).
- CI: `merge_train.py classify 54b8b9d469 --pr 3742` polled from 21:19 UTC for over 30 min; every run rc=3 `WAIT ... pending: gate red: none` (`ev/classify-log.txt`), so this returns under `pending-ci:`. The review packet's `introduced-red` refusal was `unreadable` (instrument-self-tests queued), not a red.
- PR comments: none. Owed-reds set: `ev/owed-reds.txt`.

## Notes

- Note: figure: the body's `flow_errors.py` line says `8 -> 0 over its 9 cells, all fired at both ends`; at the head 7 of 9 fire unmodified (see Evidence). The 0 holds only under this seat's pair-shape adaptation. Carry: dismissed: paperwork on this PR's body; the head's figure is re-taken here with its adaptation in ev/
- Note: equivalent-mutant: M8 (`factory_settings` returning `with_settings(...)` unplaced) survives features.py. Under the migration invariant, a loaded entry's data is `{name}` alone, so `placed()` there is a no-op on every reachable state; the predictor's `entry_config.py:430 RETURN_DEL` is a different mutant and is left to mutation-autofix. Carry: dismissed: equivalent on every reachable entry (migration runs before setup); no behaviour to pin

## Findings

none
