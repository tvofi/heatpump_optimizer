Fix review: merge 809ae0c7a82bba5ceb23bd189bcc1d4e0cf299e1
bus-nonce: 6b1fb4aadb8af37f3cdedcbdbb6a805a

Round: the fourth review of #3882. The three earlier verdicts on review/3882 are blocks: 96523195 tests-red, 49658957 merge-conflict and 1d027949 class-open. This is a delta review under the 2026-11-09 ruling: `git diff 1d027949b899f6f1491de54d1908a73d8d28c581 809ae0c7a82bba5ceb23bd189bcc1d4e0cf299e1`, plus whether the 1d027949 finding is resolved. The packet printed `Review scope: full`, because that verdict is on review/3882 and not on verdict/3882. The scope here is the delta the dispatch asked for. Measured in a detached worktree at 809ae0c7a82bba5ceb23bd189bcc1d4e0cf299e1, against main 265e061f65e452f8dd217a872f1e639d729a8467 (ev/main.txt).

## The delta

- The PR's own commits over 1d027949 are cee9cdf908 (two failing-first checks), b78d9c35a2 (the fix: `frost_hold._active` reads `if not (cfg.frost_hold and cfg.heat_pump_switch_entity):`) and 581d10e09a (it deletes the stale `_active.GUARD_OFF.6ce0bc82` pin).
- The rest comes from main, through merges 76d06dc863, e2e3c17253, c021578709, eab74c53e5 and 809ae0c7a8. `git show --remerge-diff` shows only driver resolutions: `LEDGER-MERGE` for structure_budgets.json, closures.json and the D6 register, and `MERGE-CLAIM: resolved tests/golden/claimed_drift.txt`. The one hand resolution is e2e3c17253, which sets `unloaded_package_imports` from -2 to 0. 0 is what `tests/structure.py` measures, and it does not differ from main.
- The three-dot interdiff between 1d027949 and 809ae0c7 differs only in these places:
  - frost_hold.py: the fix.
  - features.py: the two checks.
  - The deleted pin.
  - coordinator.py and pump_arbiter.py: two import-line hunks that main's #3931 shrank (`DHW_PROFILE_STORE_VERSION`, `quantise_setpoint_c`).
  - structure_budgets.json: re-based on main's lower table, with the same raise as at 1d027949 (module_excess_loc +17, max_class_loc +1, class_excess_loc -3).
- No other production change of this PR is in the delta. Nothing in main's production delta puts the reviewed functionality at a risk CI would not detect, so the scope stays narrow.

## Prior finding (1d027949 class-open: no power switch) -- resolved

- RESULT harness: this is the finder's harness for that finding, `ev/probe_noswitch.py` from review/3882 20172e18. It was run at both ends from the worktree root (ev/probe_noswitch_1d027949.txt, ev/probe_noswitch_809ae0c7.txt).
  - At 1d027949: `switch=None out=-3.0 gate(False)->None frost_holding=True`, and end to end `_served(duty=None)->'space' freeze_reason->'frost_hold'`.
  - At 809ae0c7: `switch=None out=-3.0 gate(False)->False frost_holding=False ran_until=None`, and end to end `frost_holding=False _served(duty=None)->None freeze_reason->None`.
  - Controls, the same at both ends: switch.hp at -3 C prints `gate(False)->None frost_holding=True` and `'space'`/`'frost_hold'`; the +5 C null control prints `False False`.
- RESULT take_off: I extended the harness with ev/probe_takeoff.py, which is mine and not the finder's. It reuses the probe's `inp`.
  - At 1d027949: `take_off switch=None out=-3.0 ->True frost_holding=True`.
  - At 809ae0c7: `->False frost_holding=False`.
  - Control: switch.hp at -3 C prints `->True` at both ends; +5 C prints `->False` at both ends.
- RESULT mutation: I reverted the fix line to `if not cfg.frost_hold:` in a separate worktree at the head (ev/mutant-diff.txt). Under it, `PYTHONPATH=tests/hastub python3 tests/features.py` prints `2 of 6367 FEATURE CHECKS FAILED`, rc=1. Both failures are the PR's new checks (ev/features-mutant-excerpt.txt):
  - `frost hold gate: no power switch configured: an OFF at -3 °C is not held  [[(None, True), (None, True)] != [(False, False), (False, False)]]`
  - `frost hold: no power switch configured: the cut-off cuts  [(True, True) != (False, False)]`
  - The worktree was restored afterwards.
- Class: every writer of `frost_holding` is in frost_hold.py: `gate` at line 125 (a True write clears it), line 128 (`_active`) and `take_off` at line 148, after `_active`. Every reader in coordinator.py, pump_arbiter.py and diagnostics.py reads that field, or `holding`/`freeze_reason`, which read it. Both setting paths now pass through the one predicate, so the domain the finding named is closed. No other seam sets the latch.

## Checked

- RESULT structure: `python3 tests/structure.py` at the head prints `STRUCTURE RATCHET PASSED` (ev/structure-at-head.txt). It reports class_excess_loc 17201 <= 17201, max_class_loc 7760 <= 7760, module_excess_loc 21624 <= 21624 and unloaded_package_imports 0 <= 0. The raise over main's table is the one reviewed and approved at 1d027949: module_excess_loc +17 and max_class_loc +1. The delta adds no structural growth.
- RESULT merge: `git merge-tree --write-tree origin/main 809ae0c7` exits 0 (ev/merge-tree.txt).
- RESULT version: VERSION, manifest.json and RELEASE_NOTES.md are untouched in the three-dot diff. The claim files carry only the `claimed_drift.txt` line that was already present at 1d027949, merged by the driver. The delta changes no solver code, so `env_drift.py` was not re-run.
- RESULT body: `## Head` names 809ae0c7a82bba5ceb23bd189bcc1d4e0cf299e1, the head measured here. Its repair paragraph quotes the same harness outputs I re-derived above.

## Checks at the head (live, ev/checks-809ae0c7a82bba5ceb23bd189bcc1d4e0cf299e1.txt; required context: `gate`)

- RESULT required: `gate` is not settled. Its run 140884116155 concluded failure with `FAIL run(s) [46113911461] at this head are still being judged; their gate decides` (ev/gate-job-excerpt.txt). Run 46113911461 still has `tests / closures` and `tests / mutation-pins (1)` in progress at 2026-11-28T07:21Z. `merge_train.py classify --pr 3882 809ae0c7` reads `WAIT 809ae0c7a82bba5ceb23bd189bcc1d4e0cf299e1 pending: gate red: none` (ev/classify.txt), and a pending check never refuses.
- RESULT green: these lanes concluded success: fast (3.14) 1/4 to 4/4, coverage, typing, replay, browser, arch-instrument, briefs, closure-scope, graders-head-copy, arch-score, CodeQL, hassfest, validate-hacs and governance env-matrix, instrument-self-tests, policy-docs and wave-script.
- Confirm (C8) grades the gate at the live head when it concludes.

- Note: owed-red: `tests / mutation` reports `ADDED UNPINNED custom_components/heatpump_optimizer/frost_hold.py:101 BOOLOP` and `... GUARD_OFF` (ev/mutation-job-excerpt.txt). These are two killed mutants left unpinned: 581d10e09a deleted the old pin, and `mutation-autofix` re-pins killed sites. My BOOLOP-shaped mutant above is killed by 2 checks, and the body reports GUARD_OFF failing 7 of 66 checks of the block. Answered by naming it: `ci-autofix.md` (killed unpinned mutants). `tests / mutation-pins (1)` is the repair in flight, and a bot commit inside the ledger's paths carries this verdict (`review_carry.py`). Carry: dismissed: evidence, not a finding
- Note: approval-owed: `budget-raise-gate` prints `REFUSED: tvofi's approval is on 1d027949b899, not this head 809ae0c7a82b` (ev/brg-job-excerpt.txt). The raise is unchanged from the approved one (module_excess_loc +17, max_class_loc +1). The approval has to be given again at the head and follows this review (APPROVAL-OWED). Carry: dismissed: evidence, not a finding
- Note: non-required: `tests / nightly-ha (stable)`, `tests / nightly-ha (2025.2.0)` and `tests / nightly-status` are red. None is required. nightly-ha prints `FAIL a5:pages_ok [raised=['grid:InvalidData'] ...]`, the same as main 7b0ddc20's own nightly-ha (stable) (ev/nightly-ha-stable-excerpt.txt, ev/nightly-ha-stable-main-7b0ddc20.txt). The cause is inherited, so these block nothing. Carry: dismissed: evidence, not a finding
- Note: recut-missing: this is the fourth round, and the body has no `## Re-cut` note. The three earlier blocks were a tests-red, a merge conflict and one class-open seam, now closed. That is paperwork for the dispatcher. Carry: dismissed: evidence, not a finding
