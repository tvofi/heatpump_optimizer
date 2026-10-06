Fix review: blocked 058a5f8018e87cb7861477c8e7382ba9c7daada8 conflict: docs/architecture.md and tools/audit/round4/D6/claims.json, claims.md, claims.py conflict with origin/main f07cd253; claimed_drift.txt MERGE-CLAIM refused

bus-nonce: 740ea45098b3a7b9c7dcfcff3ef78cc9

Round 1. Head measured 058a5f8018e87cb7861477c8e7382ba9c7daada8. Contract copy matches origin/main (empty brief diff). Worktree clean after the mutants.

## Conflict

`git merge-tree --write-tree origin/main 058a5f8018e87cb7861477c8e7382ba9c7daada8` against origin/main f07cd253c52f1012427d9869a808f1df39dafb93. GitHub `mergeStateStatus` is DIRTY. Content conflicts: `docs/architecture.md`, `tools/audit/round4/D6/claims.json`, `tools/audit/round4/D6/claims.md`, `tools/audit/round4/D6/claims.py`. Those are not the two golden claim files.

`MERGE-CLAIM: refused tests/golden/claimed_drift.txt`. Both sides rewrote the claim list: this branch claims `config_flow`; origin/main brings `coord_all_features`, `coord_dhw`, `coord_grid_fee`, `coord_minimal`, `coord_two_zone`. Orchestrator resolves that file by hand. `LEDGER-MERGE: resolved tests/structure_budgets.json` (`max_class_loc: 9068 + both deltas = 9048`).

## Mutation

The named domain guard, `if not needs <= item.keys() or not admitted("debug", {field: [item]})`, set to `if False:`: `tests/debug_collect.py` fails `a stored row inside its domain is kept, and one outside it is dropped` (1 of 30). Restored.

`if stamp is None` set to `if False:`: `ALL 30 DEBUG COLLECT CHECKS PASSED`. The equivalent triage holds. Restored.

Comment-only edit: `ALL 30 DEBUG COLLECT CHECKS PASSED`. The null control holds. Restored.

RESULT mutant_domain_guard=fail count
RESULT mutant_stamp_is_none=pass count
RESULT null_comment=pass count

Pin files in the three-dot diff: 51 under `killed_by`, 1 under `survivor_triage`. The mutation table was not re-run.

## Harness

No finder harness is committed for #1939. The pre-study at eae236d66 assigns the synthetic-week oracle to R9-DBG-3. The instrument here is the fixer's `tests/debug_collect.py` (d6c179e7).

At merge base 0a60e065 `debugger.py` is absent. At this head the same script prints `ALL 30 DEBUG COLLECT CHECKS PASSED`.

RESULT debug_collect_head=30 count
RESULT debugger_at_merge_base=absent count

The issue requires the first real bundle size in the body. The body has no such figure, and nothing in the tree records a waiver. That item remains `harness: design-trace-missing bundle-size` after the conflict is resolved.

The body names no enumeration rule. The issue states one seam-map obligation and a feature surface list, so this is not `class-rule-missing`.

## Claims and version

`env_drift.py --all` against current origin/main: `config_flow` moved and is claimed (3 `debug_collect_enabled` leaves). Five unclaimed drifts are `model_restart_advisor` on `coord_all_features`, `coord_dhw`, `coord_grid_fee`, `coord_minimal`, `coord_two_zone`. The three-dot diff does not touch those fixtures; they are the claims origin/main added. No card file is in the diff, so `card_drift.mjs` was not run.

RESULT env_drift_unclaimed_vs_origin_main=5 count
RESULT config_flow_claimed=1 count

`VERSION`, the manifest `version`, and the `RELEASE_NOTES.md` heading are untouched at 6.7.16.

## Numbers

Re-derived at this head: debug-collect 30; `structure.py` `STRUCTURE RATCHET PASSED` with `coordinator_private_reach=0`, `max_class_loc=9067`, `seam_cut_total=772`; closure list for `tests/debug_collect.py` length 81; killed-by count 51. The body's head line matches this SHA.

Not re-derived: entity-check count 2187, `MODE: SCOPED -- 30`, mutation inventory 4750/4699. Those figures are stamped at 6d5d796e against origin/main 6b1ccb68, and this head later merged 0a60e065.

The budget diff lowers `max_class_loc` 9068 to 9067. The measured value is 9067. The step-14 removal was not run, so that one-line drop is not called earned.

## Checks

This head's check-runs: `delivery-status` failure, job 112407698062, log `DELIVERY STATUS UNCHECKED — 38 rowed, 0 pending, 0 overdue` over main merge subjects `subject_number` does not recognise. The body names that check and the check itself. The diff adds `docs/delivery/1987.md`.

`nightly-status` failure, job 112407697386. The parent run was still open, so the log was not readable. The diff does not touch `tests/nightly_status.py`, `tests.yml`, `governance.yml`, the plan, or `docs/HANDOVER.md`. The body says the job graded main.

`pr-contract` success, job 112409254171: `red checks the body must answer: delivery-status,nightly-status` and `skip red-history` (no token), so every earlier head is UNCHECKED by that run. The body also names `closures`, `closures-autofix`, `fast (3.14)`, `mutation`, `mutation-autofix` from earlier heads.

`mutation` success, job 112407698159, completed 2026-10-06T17:50:09Z. The parent run was still open, so the log was not readable. A green conclusion is not read as "no survivor". `coverage` and `Analyze (python)` success. `fast (3.14)` job 112407698219 and `closures` job 112408061804 were still in progress at posting. `closure-scope` success.

## Carry

The body says forward-carry none. No later-stage control was established here beyond the missing bundle-size figure, which belongs in this body.

evidence: /Users/timmalmstrom/hpo-seats/r9-dbg-1-review-058a/evidence
