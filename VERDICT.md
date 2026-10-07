Fix review: blocked e0f87d5b9e4dcec8c39ed1bdf0ebbc7368dad909 conflict: head does not contain main 09ba95d0 (#2015 RO-8); merge-tree conflicts on dev/audit/rounds/round4/D6/claims.json (content) and tools/audit/round4/D6/claims.md (modify/delete), so the PR is DIRTY and no CI ran at this head

bus-nonce: 322be6f94b59266d262351fe4c749c4d

Reviewer seat r9c-rev-2025, round 2. Detached worktree /Users/timmalmstrom/hpo-seats/r9c-rev-2025 at e0f87d5b. Its parents are a390f589 and 2f987a6d. Live head re-read at posting.

## Blocking

1. **Conflict with main, outside the claim files.** The dispatch says e0f87d5b carries an update_pr main merge that includes #2015. It does not. `git log -1 --format=%P e0f87d5b` = a390f589 2f987a6d, and the merge base with origin/main is still e0f0b6fb. `git merge-tree --write-tree origin/main(09ba95d0) e0f87d5b` exits 1:
   - `CONFLICT (content): dev/audit/rounds/round4/D6/claims.json`
   - `CONFLICT (modify/delete): tools/audit/round4/D6/claims.md deleted in origin/main and modified in e0f87d5b`

   The ledger driver resolved tests/closures.json (`LEDGER-MERGE: resolved`). Neither conflicting path is a claim file, so the conflict is fix-review.md step 13's to block on. GitHub reports `mergeable_state: dirty`.
2. **No CI exists at this head.** The commit check-runs API returns `total_count 0` for e0f87d5b. There are no runs at 2f987a6d, 057028f3 or eaaa6c2f either. A DIRTY PR does not queue Tests (claim-files.md). So `typing`, `closures` and `fast (3.14)` cannot be cited at the head. Their greens are owed after the main merge. The verdict cannot carry them.

## The delta since a390f589, judged against round 1 (all local, at e0f87d5b)

1. **typing (9 -> 0): not verified.** mypy is not installed in any local venv (venv-ci has none). The relevant diff is a typed local in binary_sensor `_margin_c` and `_one_of(Container[str])`. CI's `typing` at the head does not exist (blocking item 2).
2. **closures: verified locally.** The diff adds 31 `entry_config.py` lines to tests/closures.json. entry_config.py is now in 26 closures, and all 20 closures that contain coordinator.py include it (missing=[]). My stand-in from round 1, `closure.py select --files custom_components/heatpump_optimizer/entry_config.py`, now prints `MODE: SCOPED -- 26 script(s) run, 6 scoped out` and RUNs entities, features, typing_ruler, structure, golden and stress. In round 1 it SKIPped them. The fixer's "21 scripts" was not re-derived. CI's `closures` job at the head does not exist.
3. **Mutation: killed.** My round-1 mutants were re-run in place on entry_config.py/coordinator.py and restored with `git checkout`; the tree was clean afterwards. All were run against tests/entities.py:
   - M0 null: ALL 2210 PASSED.
   - M1 (`_number` keeps NaN/inf): KILLED, 1 failed. The failing check is "a stored NaN or infinity reads the declared default ...".
   - M7 (`_nonzero_number` keeps 0): KILLED, 1 failed (the same check).
   - M9 (the live-apply line `self._ctx = replace(...)` deleted): KILLED, 1 failed. The failing check is "... applies live through a new parse that equals the saved entry (no reload) ...".
   - Restored pins: both `apply_config_keys.GUARD_OFF` pins are byte-identical to main.
   - Deleted pins: I read the 7 deleted pins at main. Six record `killed_by: tests/features.py`, and IndoorTempSensor records `tests/entities.py`. For all 7, the anchored `old` line is absent at the head (`old_line_present_at_head=0` each), so their anchors are stale and deleting them is sound. The features.py re-kills of the six rewritten lines are unverified: features.py is CI's, and CI has not run.
   - The 55+ added sites are left to CI's chain, as the body says.
4. **Live apply: restored, and equal to main.** My driver (`quiet_reload_driver.py`), at the head:
   - quiet-only call: `live_spec='09:00-09:30' live_off_steps=2 live_fraction=0.8 reloaded=0`, and the rebuilt coordinator gives the same.
   - null (empty call): `reloaded=0`, no spec.

   These match main's round-1 numbers exactly. `quiet_windows.py` is byte-identical to main e0f0b6fb (`git diff --quiet` passes). The round-1 user-visible reload change is therefore gone.

   The mechanism is a new design. The coordinator replaces `self._ctx` with a copy carrying a re-parsed EntryConfig. Objects that captured the old `ctx._config` at construction keep the old object, for example `_disinfection_switch(hass, ctx._config)` at coordinator.py:2723. None of those reads quiet keys, so I found no divergence. Disclosed as judgement, not measurement.
5. **fast (3.14): the stand-in fix holds locally.** `tests/manual_plan.py` at the head prints `ALL 128 manual plan checks PASSED`, rc 0. The `fast` check-run at the head does not exist.

   `## Red checks` names every non-green check-run that existed at a390f589: typing, closures, closures-autofix, fast (3.14), mutation, mutation-autofix, delivery-status, nightly-status, pr-contract, budget-raise-gate (cancelled), and the two in dispatch run 37640455476. That matches pr-contract's own list at a390f589: "closures,closures-autofix,delivery-status,fast (3.14),mutation,mutation-autofix,nightly-status,typing".

Structure: `STRUCTURE RATCHET PASSED`, with max_class_loc 8877 <= 8877, seam_cut_total 760 <= 760 and duplication_copies 38 <= 38. The budgets only go down against main (9104 -> 8877, 766 -> 760). My scan at the head: ATTR-NOT-A-FIELD 0, HOLDER-MAPPING-READS 0, UNDEFINED {}.

## Author "Tvofi2"

Commit 5947316c is authored `Tvofi2 <70032254+tvofi@users.noreply.github.com>`. pr-contract does not read commit authors. `.github/workflows/pr-contract.yml` passes `--author` the PR's `user.login` (`hpo-author[bot]` here), and `tools/policy/policy_lint.mjs`'s author check (decision 0011) keys on that login only. The pr-contract run at a390f589 whose range contains 5947316c (run 37647008682) concluded success. The failed twin (run 37647009251) failed on the unanswered reds, not on the author.

## What is owed

1. The fixer, or the orchestrator's update_pr, merges origin/main 09ba95d0. The claims.json/claims.md resolution must follow #2015's move: modify the moved `dev/audit/rounds/round4/D6/claims.md`, not the deleted `tools/audit/` copy. Then regenerate claims with the moved `claims.py`.
2. Let CI run, then cite `typing`, `closures`, `fast (3.14)` and the mutation chain at that head.

The judgement of the delta above (points 2 to 5) is the resolution baseline for the next round. Only the main-merge resolution delta and the CI results remain to judge.

Evidence: /Users/timmalmstrom/hpo-seats/r9c-rev-2025-ev2 (HEAD.txt, merge_tree_main.txt, quiet_reload.txt, quiet_reload_round1.txt, scan_head.txt, mutation_entities.txt, entities_M*.txt, manual_plan_head.txt, structure_head.txt, select_entry_config_only.txt, pins_old_lines.txt, joblog_prcontract_*.txt, pr-body.md, and the reviewer-built scan_attrs.py, quiet_reload_driver.py, mutate.py and mutate_coord.py). Round 1: /Users/timmalmstrom/hpo-seats/r9c-rev-2025-ev.
