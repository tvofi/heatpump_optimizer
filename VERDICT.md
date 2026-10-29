Fix review: blocked 196a75a9f32d87445f48a266ea37a961bfa1089a merge-conflict: tests/config_flow_steps.py conflicts with origin/main 0265f524e after arm A (#2912) merged

bus-nonce: a3739c1d9669513e7839f6118c9dc87c

## Block

Round 2 (a repair after `verdict/2915` class-open). The authored repair is sound and the round-1 class is closed (see Evidence). Main moved while this review ran. At the start of the review, `git merge-tree --write-tree origin/main 196a75a9f` against `077dee856` exited 0 (ev/merge_tree.txt). At verdict time `origin/main` is `0265f524e`, which includes arm A's merge `ba19d13c4` (#2912, which touches `tests/config_flow_steps.py` in `8bdab62ce`, `d1dc4a480` and `9d043f781`). The same command now exits 1 with `CONFLICT (content): Merge conflict in tests/config_flow_steps.py` (ev/merge_tree_final.txt). That is not a claim file, so I cannot know the merged result is correct (fix-review.md step 13). The head did not move; only the base did.

The ledger driver printed `LEDGER-MERGE: resolved tests/structure_budgets.json` (`class_excess_loc: 18037 + both deltas = 17875`). That path is settled by the driver, but the body says the second of A and C to merge re-measures that row on the merged tree.

To unblock: merge origin/main into the branch and resolve `tests/config_flow_steps.py`, keeping arm A's checks and this PR's `setup_widgets_are_the_registry_rows` and its `main()` call. Then re-run `tests/config_flow_steps.py` and `tests/structure.py` on the merged tree, and quote the measured `class_excess_loc`. A re-review then judges only the resolution delta.

## Findings

- The finder's harness `wizard_widgets.py` (sha1 `66b390554c0aa54c8960eacb532b04ff827ca8cf`) still lives only at `3930b421a` and is not in the tree. It is not in the R10-CONFIGFLOW-PAGES roster brief at origin/main either (searched `dev/programme/rosters/wave-r10-groups.json` for `wizard_widgets` and `66b390554`: no match). It is owed for arm B's merge resolution and for arm D. Carry: R10-CONFIGFLOW-PAGES
- `class_excess_loc` in `tests/structure_budgets.json` was resolved by the ledger driver to 17875 across arms A and C. It has not been measured on a merged tree. Whichever lands second owes `tests/structure.py` on the merged tree and the measured value in its commit message. Carry: R10-CONFIGFLOW-PAGES

## Evidence

- Head measured: `196a75a9f32d87445f48a266ea37a961bfa1089a` (ev/HEAD.txt). It is the PR's head at verdict time, and the body's `## Head` names it. Roles diff merge-base...origin/main is empty, so the contract is current.
- RESULT config_flow_steps head: `ALL 508 checks PASSED`, rc 0 (ev/cfs_head.txt). That includes `no setup field spells a second widget for a setting the options registry declares`.
- Class closure, round 1's `class-open: reauth_confirm tibber_token`. The census domain is now every `async_step_*` of `HeatPumpOptimizerConfigFlow` minus the declared `NON_FORM_SETUP_STEPS` = {building, finish_setup, reconfigure}, and it asserts its own reach.
  - My independent static enumeration is every widget construction in `config_flow.py` outside `_OPTION_FIELDS` (`_number(`, `_entity_of(`, `_select(`, `selector.*Selector(`, the solar factories). It returns only keys absent from the registry: after_save; building_structure/era/foundation, heated_area_m2 and upper/lower emitter (the shared `_building_question_fields`); the quick-setup question booleans (two_zone, buffer_tank, dhw_tank, wood_furnace, wood_buffer_tank); dhw_enabled; prefill_device. Every one tested `in {row.key for row in _OPTION_FIELDS}` is False.
  - `_tibber_token_selector` has no remaining reference in custom_components or tests. The PASSWORD TextSelector is built only on the registry row (config_flow.py:1548).
  - The only other flow, `repairs.py`'s `DhwSetpointRepairFlow`, renders one form with no data_schema and does not import config_flow (read by a scout worker). The options flow renders from `_OPTION_FIELDS` itself.
  - Result: the class is closed across reauth and every other form site.
- Mutants, each applied to the head, run with `tests/config_flow_steps.py`, then restored:
  - m1, reauth_confirm spells its own TextSelector(PASSWORD): `1 of 508 checks FAILED`, `['reauth:tibber_token', 'reauth_confirm:tibber_token']`. Killed.
  - m2, `_wizard_fields` copies the row widget: `1 of 508 FAILED`, 44 spelled twice. Killed.
  - m3, a new unlisted `async_step_zz_probe` spells `_number` for price_weight: `1 of 508 FAILED`, `['zz_probe:price_weight']`. Killed. This shows a new step joins the census without being listed.
  - m4, `user` price_entity back to `_entity_of("sensor")`: `1 of 508 FAILED`, `['user:price_entity']`. Killed.
  - Outputs are in ev/m1_*.txt to ev/m4_*.txt.
- Null control, re-run: m1 under `f74f6cbb2`'s `tests/config_flow_steps.py` (the old hand-kept domain) gives `ALL 507 checks PASSED`, rc 0 (ev/null_m1_old_domain.txt). This matches the body: the kill comes from the domain change.
- Structure: `STRUCTURE RATCHET PASSED`, `class_excess_loc=17921` at the head. With config_flow.py at `b0b2d7697` it reads 18037, `FAIL ... (+116)` (ev/structure_base_configflow.txt). The drop is earned by the deleted wizard spellings.
- Archscore:
  - `--diff b0b2d7697` gives `dS +0.5850 IMPROVES`, `literal_clone_copies 185 -> 123`.
  - `--diff f74f6cbb2` gives `dS +0.0000 NULL`.
  - Both match the body.
- VERSION, RELEASE_NOTES.md, manifest and both claim files: `git diff --name-only b0b2d7697...HEAD` over the five prints 0.
- Figures I did not re-derive: the finder's harness lines (`wizard_fields=46 in_registry=44 spelled_twice=0 disagree=0 golden_equal=1`, `--all`, `--bump`). The harness is not in the tree and I did not fetch `3930b421a`. The census's `steps=18` and `registry-backed fields>=66` pass as asserted.
- CI on the head, all concluded (ev/ci_state.txt): every check is success or skipped except `governance / delivery-status` = failure.
  - Its log reads `DELIVERY STATUS OVERDUE` on rows #2921, #2910, #2873 and #2909, none of them this PR's. The log states: "This check is NOT a required context and a red here blocks no merge."
  - This PR's own row `dev/programme/delivery/2915.md` is not among the overdue rows. Under fix-review.md step 11 the red is not this pull request's, and it owes no `## Red checks` answer.
  - `review_packet.py` nevertheless refused `red-unanswered` on it (ev/review-packet.md). Evidence only.
- The forward-carry for arm D (the `device_registry as dr` import and `unused_boundary_imports` 1 -> 0; re-record `literal_clone_copies`) is in the roster at origin/main as a "Forward-carried precondition" (ev/roster_carry.txt).
