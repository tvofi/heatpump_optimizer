Fix review: blocked 9f133225f72bc9581a411bdc40d544dd447f78ee lifecycle-leak: fault_log's state listener survives a failed setup (not released by the entry's on_unload callbacks), leaving a second live record writing the same store

bus-nonce: 846a0291c6e584e6d6d0a60f501be5c8

Round 1 (first review of #3870), full scope, head 9f133225f72bc9581a411bdc40d544dd447f78ee, merge base e3cb5c019b464a770cc7c6fe2fbc858ed29debf7.

## Block

- `custom_components/heatpump_optimizer/fault_log.py:312` registers the state listener only on `rec.releases`, which only `async_close` releases. The only callers of `async_close` are `async_unload_entry` and the stop hook. The stop hook is registered through `entry.async_on_unload` (`fault_log.py:317`).
- `__init__.async_setup_entry` runs `fault_log.async_setup` before `async_register_frontend` and `async_forward_entry_setups` (`__init__.py:363-371`). If either of those raises, Home Assistant does not call `async_unload_entry`. It runs only the entry's `async_on_unload` callbacks, which is the path `tests/features.py`'s #236/#237/#240 lifecycle section exists to pin.
  - On that path, those callbacks remove the stop hook.
  - The state listener and its `_Record` stay live. The record is closed by nothing.
  - The next `async_setup` for the entry pops `_RECORDS[entry]` without closing the old record, so two records then write the same `heatpump_optimizer_<entry_id>_fault_log` store.
- Measured with the PR's own fault-record harness (`_FlHass` and `_fl_entry` from the block). The probe is in `ev/probe_failed_setup.py`, run appended to a scratch copy of `tests/features.py` through `features_block.run`. Steps: setup, then the entry's `_on_unload` callbacks only (a failed setup), then setup again, then one `E5` event.
  - Result: **2 live state listeners and 2 store saves for one event**.
  - Null control, where the first setup is ended by `async_close` (the unload path): 1 listener, 1 save.
- The approved design (`design.md` at 3850f3368e69, "Stop and unload") keeps the listener off `async_on_unload` so that nothing fires after the save. It does not consider a setup that fails after `fault_log.async_setup`, so this is a gap in the design, not a departure from it.
- A fix should hold under that ordering. Two options:
  - release the listener and the timer from an `entry.async_on_unload` callback that is idempotent beside `async_close`. HA's unsubscribe raises if called twice, so guard it with the `closed` flag or clear `releases`;
  - or move `fault_log.async_setup` after the last step of setup that can raise.
- Either way, add a check that drives the failed-setup path. The probe above is that check.

Also settle these in the same round. They are test gaps in this diff's production lines: my mutants, each run against the fault-record block and against the four cheap closure scripts (`finite_boundary.py`, `config_flow_steps.py`, `manual_plan.py`, `debug_collect.py`), and each **SURVIVED** everywhere (`ev/mutants.txt`, `ev/mutants_closure.txt`). None is equivalent on the domain the store and the entity states admit.
- F `fault_log.py:134`, `if part.strip()` removed from `code_text`. A state of `"E5,"` or `"E5,,E6"` records an empty item (`"E5, "`), and no check feeds one.
- K `fault_log.py:185`, `[-EPISODES_MAX:]` removed from `loaded`. The store's `fault_log` domain admits any episode count, and `note` only trims one row per append, so an oversized document stays oversized. No check loads more than 200 rows.
- L `fault_log.py:106`, `max(now_s, start_s)` replaced by `now_s`. A reading stamped before the open row's start (a clock step, or a restored row against an earlier `last_changed`) gives a negative duration and a negative tally. No check feeds one.

## Evidence

- RESULT mutation proof (step 1): the fault-record block at the head passes (`ALL 20 FEATURES BLOCK PASSED`, `ev/block_head.log`). I ran 17 targeted mutants of `fault_log.py` through it (`ev/mut_driver.py`, `ev/mutants.txt`); 14 were killed, among them the body's M3, M7, M8, M10, M11, M13, M15, M16 (shapes A–E, G–J, N–R). The 3 survivors are listed under Block. Every file was restored after each run, and `git status` was clean at the end.
- RESULT finder's harness (step 2): the packet names none. The PR adds `dev/audit/harnesses/r11_owner_fault_text.py`, a bundle-reading counter built by the fixer. It is disclosed as the fixer's in the body, and it runs only on a real bundle the owner holds. I did not run it, because no bundle is committed.
- RESULT claims (step 4): `env_drift.py --all e3cb5c019b` at the head printed `NO UNCLAIMED DRIFT: 56 scenario(s) checked` and `NO STALE FIXTURE`, rc 0. The only claim is `config_flow`, which moves 3 leaves, each "present on one side only". `claims-for: 10.1.2` equals `VERSION` (`ev/env_drift.txt`).
- RESULT version (step 5): `VERSION`, `manifest.json` and `RELEASE_NOTES.md` have an empty three-dot diff.
- RESULT class enumeration (step 6): I re-ran the body's step-8 `git grep` at the head (`ev/step8_grep.txt`). Every row is dispositioned in the body. The line numbers differ only by the main merge (the body's `entry_config.py:109/132` at 41b57b2daf are `:140/:163` at the head, and I checked both).
- RESULT merge (step 13): `git merge-tree --write-tree origin/main 9f133225f7` exited 0 (`ev/merge-tree.txt`). origin/main is the merge base.
- RESULT head (step 7): the body's `## Head` names `9f133225f72bc9581a411bdc40d544dd447f78ee`, which is the head I measured.
- RESULT actuator (step 16): the diff adds no write path, so no refusal is owed.
- RESULT CI: `merge_train.py classify 9f133225f7 --pr 3870` printed `WAIT … pending: gate red: none` on every poll from 21:04Z to 21:13Z (`ev/classify.log`). The review packet refused `introduced-red: unreadable` because `instrument-self-tests` was still queued. This block rests on code, not on CI.
- RESULT figures I did not re-derive: I cite CI's heavy runs (the gate, the mutation table, the archscore, structure) and did not re-run them. That covers `module_excess_loc 21779 -> 21771`, `Architecture score: dS +0.0000 NULL`, the census `82 … 199`, and the 53-mutant list beyond the shapes above.
