Fix review: merge 5723ce192e589a344de0ddb3b50929b19e90fec7

bus-nonce: 46f28f3be1c6369180e401cd8c3aa6e7
pending-ci: gate

Round 1 on the pull request, the second review of the group (the handoff review at a827c3d985b2 blocked `mutation-vacuous`; the fixer's body is at its round 3). Measured at 5723ce192e589a344de0ddb3b50929b19e90fec7, merge base 0a1ef512f42cbf380049b11b096eb89c5a222ccc; `git ls-remote` still names that head for fix/r10-cop-learner-draw-floor at the end of the review. The body's `## Head` names the same SHA. Reviewed whole: the four production files, the repair's checks, the ledger, the budgets and the body's figures.

## Findings

- Carries 0 and 1 have no finder harness; both ends were measured with `dev/audit/harnesses/cop_duty_floor.py`, the #2066 fixer's instrument extended by this diff, and the other-configuration rows in `ev/attack.py` are this reviewer's parameters on that builder's function. Carry: dismissed: the approved design names this committed harness as the control, and the handoff review recorded the same
- A pump that sets its own power under flat asks (asks within 2 % of 2.0 kW, draw 2.9 kW, 4 kW nameplate) folds 286 of 288 intervals to scale 0.500 at the merge base and at the head alike (`ev/attack_base.txt`, `ev/attack_head.txt`, row `rv2_selfset_flatask_max4`), where 1.000 is right. The head does not make it worse and does not close it: that is the built arm of the owner's pending decision on the unobtainable state (body `## Forward-carry`, item 870278d1), and this row is a second control for it beside `selfset_flat`; re-measure with `ev/attack.py` at the deciding head. Carry: R10-COP-LEARNER-DRAW-FLOOR

## Evidence

Mutation proof, reviewer's driver (`ev/driver.sh`: three blocks of `tests/features.py` through `features_block.py`, each behind the prelude emitted from the tree it runs on; unmutated at the head `ALL 37`, `ALL 34` and `ALL 78 FEATURES BLOCK PASSED`, the body's counts). 25 hand mutants written for this review (`ev/mutants_mk.py`), each alone in `mutant_run.py`'s archive copy of the head: 25 killed, none survived, `SURVIVED NULL` on each of the three streams (`ev/mutants.txt`).

- RESULT repair, block 1 of the handoff review: `judge_ratio` with `or state == ASK_FOLLOWS` deleted is KILLED by "once the meter shows the draw follows the ask, a departure under the nameplate third teaches" and by no other check of the three blocks (`ev/kill_R1.txt`).
- RESULT repair, block 2: the replay's `row.reference` replaced by `self._cop_reference_curve()` is KILLED by "a released interval is judged against the curve of the cycle it was read on" (`ev/kill_R2.txt`). The body's reason for not pinning a folded scale holds on reading `_fold_cop_evidence`: with no heat reading the reference decides only whether the row folds.
- RESULT repair, the span close's window argument dropped: KILLED by "the span close judges the duty floor capped by the stored running-draw window" (`ev/kill_R3.txt`). The handoff review dismissed this mutant as a no-op; the fixer's check shows a state where it is not.
- RESULT autofix survivor `accuracy.py:1004`, `0.0 <=` to `0.0 <`: KILLED by "release: a row stamped at the clock itself is zero seconds old and waits" (`ev/kill_R4.txt`). The line's two other bounds (`i >= over`, `<= COP_HOLD_HORIZON_S`) are killed too.
- RESULT autofix survivor `coordinator.py:962`, `<` to `<=`: KILLED by "the flow-lift fold takes an ask exactly at the floor and refuses one a nanowatt under it" (`ev/kill_R5.txt`). The check reads the floor from production and pins both literals (1.8 and 2.4 kW) beside it, so it does not re-implement the comparison it tests.
- RESULT the reviewer's 20 others, all KILLED: `release` on follows judged by base's rule, on does-not-follow returning the rows, aged rows dropped unjudged; a pending departure refused and not held; `_base_folds` exclusive and blind to the draw; the diagnostics' floor reading no window; the full-window boundary; a run ask exclusive of the configured minimum; the cap keyed to the configured minimum alone; `MIN_SAMPLES + 1`; the cap on the high percentile; `follows_ask` losing its False; the replay with ask and draw swapped; the held row stamped a month old; `judge_ratio` and `release` each reading no window; the live fold dropping its heat reading.
- RESULT failing-first: the head's three blocks on the merge base's `custom_components` cannot build the first two preludes (`ImportError: cannot import name 'CopInterval'`) and fail the span-close check in the third (`ev/failing_first.txt`).
- The triage this diff adds (`MeasuredCop.judge_ratio CMP_BOUND 9d967a75`) is equivalent: no double within 8 ulp of 1.15 or 0.85 gives `abs(r - 1.0) == 0.15` (`ev/tolerance_equiv.txt`). No triage answers either survivor the brief names; both have killing checks.
- The body's account of why the local step missed the two sites reproduces: `mutant_run.py --diff 0a1ef512f42c...HEAD --list` prints 91 mutants, `coordinator.py:962 CMP_BOUND` is its line 48, and its one CMP_BOUND on `accuracy.py:1004` moves `i >= over` only.

Harness, both ends (`ev/harness_base.txt`, `ev/harness_head.txt`: the head's `cop_duty_floor.py`, sha1 396eb847b887af2460e75302c16f7a6b1f6d272f, on a worktree at the merge base and at the head): 44 lines each; `diff` lists the 17 rows of the body's table with the body's values, and every other row is identical, the null rows of `## Null control` among them.

Other configurations (`ev/attack.py`, `ev/attack_base.txt`, `ev/attack_head.txt`), 23 rows at both ends:

- RESULT efficiency shifts 0.5, 0.9 and 1.5 on 8, 10, 4 (no minimum) and 2.6 kW nameplates end at the base's scale to 0.001 on every row; the head folds more intervals on four rows, the same on four, and 2 to 8 fewer on four.
- RESULT zero evidence: the first 10, 30 and 47 intervals of a 0.6 pump on 4 kW fold 0 at the head (base 4, 24, 41), and at 49 intervals the head folds 43 of 49, as the base, scale 0.704 against 0.709. That is the hold and its release at `MIN_SAMPLES`, as designed.
- RESULT a self-setting pump with moving asks: 4 kW, base 23/288 scale 0.944, head 13/288 scale 1.003 (1.000 is right); 8 kW identical at both ends, 12/288.
- RESULT an overstated minimum the pump follows at half the ask (minimum 5 kW, nameplate 14): base 48/288, head 241/288, scale 1.600 at both.
- RESULT a window reloaded at tick 40 during the hold: 282/288 scale 0.603 at both ends.

Class, opened with the body's rule (`ev/class_enum.txt`): every code site it returns is in the diff or dispositioned under the body's "Sibling sites"; `flow_lift_power_floor_kw` has one code reader outside its definition, `draw_range.power_floor_kw`.

Departures from the design note: read again at this head and judged as the handoff review judged them, sound. The release sits past the freeze gate and the missing-reading guard; the replay returns before the health watch and the capacity envelope, which read the present cycle; the cap is keyed to the configured range (mutant "cap keyed to the configured minimum alone" is killed); `thermal_model.py` changes two docstrings and no code. Each is routed for its ruling in the body, on the roster at handoff/audit-r10-roster (entries 4 to 9 of this group's `carry` list at 30097de04722 and at the branch tip 89acffb1abf6).

Numbers the diff moves:

- RESULT structure: `STRUCTURE RATCHET PASSED` at the head; four rows down, each budget equal to what `tests/structure.py` measures at the head (`ev/structure_head.txt`, `ev/structure_base.txt`, `ev/budgets_diff.txt`); `class_excess_loc` is 17453 at both ends and its row is untouched. With the coordinator attribute put back (one assignment in `__init__`, one in `_fold_measured_cop`) the ratchet fails `coordinator_attrs`, `coordinator_multiassigned_attrs` and `seam_cut_total` by +1 and the two class-size rows by +2 (`ev/structure_null.txt`): earned by the move of the walking ratio.
- RESULT architecture score: `dS +0.0141 IMPROVES` (`ev/archscore.txt`), the body's figure.
- RESULT goldens: `env_drift.py --all 0a1ef512f42c` at the head: `NO UNCLAIMED DRIFT: 56 scenario(s)`, `NO STALE FIXTURE: 56`, rc 0 (`ev/env_drift.txt`); `git diff --stat 0a1ef512f42c...HEAD -- tests/golden VERSION RELEASE_NOTES.md custom_components/heatpump_optimizer/manifest.json` prints nothing (`ev/version_golden_diff.txt`).
- RESULT `ci_predict.py --base 0a1ef512f42c`: no red predicted, no `ADDED UNPINNED` and no `STALE PIN` line (`ev/ci_predict.txt`).
- RESULT ledger, three-dot: 43 `killed_by` pins added, 21 deleted, 4 renamed; 1 triage added, 3 deleted.
- RESULT carries: `carry_audit.py check --body`: `18 finding item(s): 18 routed, 0 unrouted, 0 bad destination(s)` (`ev/carry_audit_body.txt`); the four destination groups exist on the roster branch tip.
- RESULT merge: `git merge-tree --write-tree origin/main 5723ce192e58` exits 0 against origin/main dc46b1222fac, no `MERGE-CLAIM` line (`ev/merge_tree.txt`).
- The rest of the three-dot range is merges of main, the bot's `ci: merge main` and `ci: pin killed mutants`, and the delivery row `dev/programme/delivery/3593.md`.

This review did not re-derive the scoped gate's `29 TEST SCRIPT(S) PASSED` line or its per-script totals, the fixer's 38-mutant table beyond the mutants this driver repeats, the `2 of 5616 FEATURE CHECKS FAILED` figure at acf912282f, or the band harness's `fit=none` lines; the handoff review reproduced the last at a827c3d985b2. The role contracts are current: `git diff 0a1ef512f42c...origin/main -- dev/governance/roles/` touches `evaluator.md` and `orchestrator.md` only.

## Red checks

`tests / mutation` went red at 5cf3425240ac on the two sites above. The body names it and answers the trigger's question: the diff-mutant step uncapped for one site, the lane's own table narrowed to one driver for the other, process state (c), no countermeasure built here and the cause carried under `## Friction`. `policy_lint.mjs --pr-body` on the live body at this head prints `record red-history ... tests / mutation, tests / mutation-autofix, tests / nightly-status` and `PR-BODY: 0 error(s)` (`ev/body_check.txt`); the last two names are outside `merge_train.py owed-reds` (`ev/owed_reds.txt`). At this head no owed check has concluded red: the check runs read at 06:32 UTC show every concluded lane green, `governance / instrument-self-tests` among them, with `tests / fast (3.14)` and `tests / mutation` in progress; the `gate` failure in the listing is the aggregate of the still-running workflow and `classify` reads it as pending (`ev/classify_log.txt`).

CI at the return: `merge_train.py classify 5723ce192e589a344de0ddb3b50929b19e90fec7 --pr 3593` was polled from 06:07 to 06:39 UTC and printed `WAIT ... pending: gate red: none` every time (`ev/classify_log.txt`), so this verdict carries `pending-ci:` and is for the relay to post only on a green at this head.
