Fix review: merge 8db54b12cbcc5884f7bf0cefc032b082d5c5acec

bus-nonce: 5a88160025f065c3468048cbe86ffad3
pending-ci: gate

## Evidence

Round 2. This is a delta review over the reviewed head 2e97faf4c1. The head is on merge base cb2026c3b5, which is origin/main at review time.
- The delta is main merges (6dc6156688, 7c18ebb557, 8db54b12cb) plus one authored commit, cb3915f98e, merged through 1f676837ef. review_carry.py prints FRESH-REVIEW.
- I compared the PR's own diff at both heads file by file (e84856520d...2e97faf4c1 against cb2026c3b5...8db54b12cb). Only three files differ: the two deleted ledger rows and tests/structure_budgets.json. The custom_components/ own diff is unchanged.
- cb3915f98e deletes the killed_by rows for sysid.py SystemIdentification.conditions_met GUARD_OFF fa6ac820 (`if price > cutoff:`) and RETURN_DEL f2ae865e (`return True, "ready"`). Neither line is in conditions_met at the head. The test now goes through `_hour_price_refusal` (sysid.py:1491), and the function returns `why is None, why or "ready"`. CI's tests / mutation log at this head no longer prints the stale-disposition refusal; it prints only `118 of them added by this diff` ADDED UNPINNED.
- Widening check. Main's merge touched four files the PR also touches: coordinator.py, pump_arbiter.py, store.py and sysid.py. Main's edits are dead-state removals and signature narrowings: slab_mode_identifiability/adoption_decision lose `config`, `_observe_frequency` and `record_miss` lose `now`, `quantise_setpoint_c` and `DHW_PROFILE_STORE_VERSION` imports are dropped. The PR's added lines call none of these.
- store.py risk, checked: main's new `_unflag_numbers` reads a stored bool as None wherever a number is declared. That includes the PR's `draw/sweep/start_s`, `last_s`, `kwh` and `levels/#/#`. In draw_range.py `_stored_sweep`, `float(None)` raises TypeError, so the stored sweep reads as no record and nothing crashes. No other widening is warranted.
- RESULT tests/features.py at the head: ALL 6374 FEATURE CHECKS PASSED, rc=0 (ev/features-head.tail.log).
- RESULT mutation proof at the head: the body's mutant, draw_range.py:1070 `elif not sweep:` -> `else:`, gives `5 of 6374 FEATURE CHECKS FAILED`, rc=1. These are the five checks the body names. Tree restored (ev/mutant.summary.log, ev/run.sh).
- RESULT m5_tankfall at the head: booked_kwh_unplanned_max=3.0160 = booked_kwh_draw_then_charge_max=3.0160, unplanned_inputs_equal_draw_then_charge=True, short_max=0, as the body states (ev/m5.log).
- RESULT structure.py at the head: STRUCTURE RATCHET PASSED, module_excess_loc 21965 <= 21965 (ev/structure.log). The raise is still +365 over main's re-recorded 21600. Round 1 checked it under mandate 6893738184, and the delta adds no code.
- RESULT git merge-tree --write-tree origin/main head: rc 0 (ev/merge-tree.txt).
- CI: merge_train.py classify printed `WAIT 8db54b12cbcc5884f7bf0cefc032b082d5c5acec pending: gate red: none` on every poll from 09:10 to 09:41 UTC (ev/classify.log, ev/classify_final.out). The relay posts this verdict only once the head is green.
- The previous verdict's notes are all evidence or were answered then, and none is reopened by this delta.

## Notes

Note: stale-body: the body's `## Red checks` answers head 6dc61566, not this head. Its raise figure (21607 -> 21972) predates main's re-record; at this head the file holds 21600 -> 21965, the same +365. At this head, tests / mutation is red only on the 118 ADDED UNPINNED sites. The body's earlier-heads entry answers that as red by construction, pinned by mutation-autofix (ci-autofix.md). budget-raise-gate awaits the raise approval. Carry: dismissed: paperwork on a stale head reference; the reds are answered in kind and C8 holds the post until green
