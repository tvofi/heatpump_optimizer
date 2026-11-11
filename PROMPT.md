CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-outside-dhw-charge-settle, at head 416afe9b254436757f936712a15bf352ac25e7a7. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fixer --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 416afe9b254436757f936712a15bf352ac25e7a7 for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-outside-dhw-charge-settle before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-outside-dhw-charge-settle, whose move updates the pull request. Hand off at your first clean `tools/pr/prepr.sh` head (the body check included), fixing what it refuses; a main that has moved since that run needs no re-merge and no second run, because the train re-proves the head on the current main. Merge origin/main and rerun prepr.sh only when `git merge-tree --write-tree origin/main HEAD` reports a conflict. If you must stop on a question, first push `BLOCKED.md` with a `Question:` line to refs/heads/handoff-wip/r10-outside-dhw-charge-settle, even with no code. Then push the code to refs/heads/handoff/r10-outside-dhw-charge-settle, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-outside-dhw-charge-settle <body.md>`, which pushes refs/heads/handoff-body/r10-outside-dhw-charge-settle; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-outside-dhw-charge-settle`. When body_push.sh exits 4 (its output ends `body_push: REFUSED CARRY-LANDED`), the carry lands on the roster you may not write: push a BLOCKED.md holding that output to refs/heads/handoff-wip/r10-outside-dhw-charge-settle and stop; the relay folds the carries and re-runs body_push.sh. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
A red is owed a `## Red checks` answer, and may block, only when its name is in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints (defect-root-cause.md); any other red is neither answered nor a block.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-outside-dhw-charge-settle and refs/heads/handoff-wip/r10-outside-dhw-charge-settle-body. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires; at most 5 inline search operations per prompt; never set FRUGAL_ALLOW_INLINE.

Brief (snapshotted when this payload was rendered):
REPAIR ROUND for R10-OUTSIDE-DHW-CHARGE-SETTLE (size S, an OUR-build of an outside request: top priority), pull request 3444, head 416afe9b254436757f936712a15bf352ac25e7a7 (branch fix/r10-outside-dhw-charge-settle; branch from the PR head and continue; do not re-cut). The review returned blocked: regression-unmeasured. The verdict was given at handoff head 8e2b7d99; review_carry.py prints CARRY for 8e2b7d99..416afe9b (a merge of main, the delivery row and "ci: pin killed mutants"), so it stands on the PR head.

SCOPE. Correct every point the verdict names, against the tree.

CLASS REPAIR. Because the defect class is regression-unmeasured (the fix changes a figure that no harness measured before and after), do not stop at the case the reviewer caught. Sweep the class: for every figure, forecast or draw the diff changes, find the finder's harness that measures it before and after, show it moving at both ends on the old and new code with a null control that does not move, and quote the numbers in the body. Any change you cannot measure leaves the PR, or is named in the body as unmeasured with the reason. Re-run the full handoff sequence (mutation proof where applicable, null controls, prepr) and hand off to handoff/r10-outside-dhw-charge-settle.

If `git merge-tree --write-tree origin/main HEAD` conflicts, MERGE origin/main into the branch; never rebase.

----- REVIEW VERDICT (verbatim; the nonce line is removed) -----
Fix review: blocked 8e2b7d99d0e99f3cbd00d49ceb9b4a1458b87257 regression-unmeasured: a draw within the settle window of a planned charge is zeroed, the heavy-day p90 falls 5.55 to 1.95 kWh at 07:45, and the body's charge arm measures only a draw before the charge


## Block

Round: first review of handoff/r10-outside-dhw-charge-settle, head `8e2b7d99d0e99f3cbd00d49ceb9b4a1458b87257`, base `8f97247fc1a6911b85788a73fe502ea0097bac13`.

The fix zeroes the drop of every charge-affected interval in the draw-statistics fold and skips it in the usage learner. That covers a heated interval, an interval that started on a heated sample, and any interval ending within `DHW_CHARGE_SETTLE_HOURS` (0.25 h) of the last heated sample. The body says this costs "a real draw during a charge, or within 15 min after one". It then says "The charge arm below measures what that costs against the dip-free truth trace". The fixer's harness `dev/audit/harnesses/r10_dhw_charge_settle_p90.py` places the draw only at 07:00–07:15 and the charge only at 07:30–07:40. In that geometry no draw falls in the zeroed window, so the measured cost (truth 5.5346 to 5.5326 kWh) shows nothing about the case the body names.

Step 6 attack: I ran the same harness `run()` with the draw moved, using `ev/r_draw_after_charge.py`. That file is the reviewer's variant and is not the finder's. It runs at both ends with `PYTHONPATH=tests/hastub:custom_components` from a `git archive` of the base and from the head worktree. Here is the `truth` arm, which has no dip, so every change in it is the fix's cost on a real draw:

| draw start | base p90 kWh (usage pts) | head p90 kWh (usage pts) |
|---|---|---|
| 07:00 (body's geometry) | 5.5346 (84) | 5.5326 (84) |
| 07:35 (during the charge) | 3.6706 (28) | 0.1438 (0) |
| 07:45 (5 min after the last heated sample) | 5.5488 (84) | 1.9468 (28) |
| 08:00 (outside the window, control) | 5.5490 (84) | 5.5487 (84) |

The `flat` arm, which has no DHW flag, is identical at both ends for every offset (3.6706 / 5.5488 / 5.5490). The movement therefore comes from the charge gate and not from the instrument. A draw that starts within 15 min after a planned charge loses about 65 % of its heavy-day p90 and two thirds of its usage-profile updates. A draw during a charge drops to about zero, where before it was a lower bound.

This geometry is reachable in normal use and is not a corner case. The planner pins each window's ready temperature at the step just before the window opens (`dhw_planner.py:939-940`, `ready_temps[start_idx - 1]`). `dhw_heating_active` is the plan's scheduled power and not a device state (`optimizer.py:6054`). A charge whose last slot ends right at a window start, with the window's draw following within 15 min, is therefore the case the plan aims for. The statistic that loses the draw is the heavy-day target that sizes that same charge.

The defect the PR fixes is a +0.62 kWh phantom on the p90 (6.1506 to 5.5346 in the body's geometry). The head trades it for a −3.6 kWh loss at a geometry the planner produces. Neither the design-choices paragraph nor the figures measure that trade, and the body states the opposite.

Owed before re-handoff: measure the draw-near-charge geometry at both ends with a flat control, as above or better, and either bound the cost or change the gate. One option keeps the in-charge and settle intervals' drop only where it exceeds the dip bound, or folds the in-charge drop as before. A second option settles on the reading recovering rather than on a fixed window. The body then states the measured trade. If the owner accepts the trade as it stands, that is the owner's ruling to record, not the review's.

## Evidence

- No pull request exists yet, so there is no review packet and no CI run to read. `owed-reds` (`ev/owed_reds.txt`, from `merge_train.py owed-reds`) is the set; with no checks, no red is owed an answer at this head.
- Head re-read: `git ls-remote origin refs/heads/handoff/r10-outside-dhw-charge-settle` gives `8e2b7d99d0e99f3cbd00d49ceb9b4a1458b87257`, the head measured (`ev/head_reread.txt`). The body's `## Head` names the same SHA. Its p90 figures were taken at `348e0c8ca623`, and the last commit `8e2b7d99d0` touches only `tests/features.py`. I re-ran them at `8e2b7d99d0` and they are identical (`ev/p90_head.txt`).
- Authorship: commit `7aa8f9c5d5` (Bankaifan) has the same stable patch-id as live `refs/pull/3434/head` `3c518449ef` (`da3c8c2dc325…`).
- Merge: `git merge-tree --write-tree origin/main 8e2b7d99d0` exits 0 (tree `a7504e4587`), with `LEDGER-MERGE: resolved tests/closures.json`.
- `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched. No golden or claim file is in the three-dot diff, so `env_drift.py --all` was not run, because nothing claims or could move a fixture (`dhw_learning.py` is not solver code).
- Failing test first reproduced. With main's `dhw_learning.py` in the head tree, the block gives `2 of 2 FEATURES BLOCK FAILED`, with the same arm values as the body. At the head it gives `ALL 2 FEATURES BLOCK PASSED` (`ev/features_block_main_production.txt`, `ev/features_block_head.txt`).
- Mutation proof re-run with the body's CMD through `mutant_run.py` copy-tree at the head (`ev/mutants.json`, `ev/mutants_block.txt`). `SURVIVED NULL`. All 11 of the body's block mutants are KILLED: SETTLE_ARM_OFF, SETTLE_SHORT, SETTLE_LONG, STAMP_DEL, ZERO_DROP_OFF, USAGE_HEATING_ONLY, COOLING_HEATING_ONLY, OVERFLOW_DROP, RESTORE_SKIP_OFF, RESTORE_LEN_OFF, RESTORE_CLAMP_DROP. Of the reviewer's own mutants, R_SINCE_ARM_OFF, R_STAMP_ALWAYS and R_STAMP_PREV are KILLED, and R_FOLD_SKIP and R_SETTLE_STRICT SURVIVE the block (see Findings).
- Null control: the space-heating arm is `ok` in the block at both ends. In the p90 harness the `flat` arm is bit-identical at both ends (5.5346, 84 points). This is true by construction, since the flag is never set.
- p90 figures re-derived exactly at both ends with the fixer's harness, sha1 `df1bc6619db4b95b19a9472316524a98f4ce8549` (`ev/p90_base.txt`, `ev/p90_head.txt`). The finding came from an outside pull request with no committed harness. That harness is the fixer's (builder's) instrument, built as the brief required, and not the finder's.
- Structure: `class_excess_loc` is 17537 at the base and 17535 at the head, `STRUCTURE RATCHET PASSED` (`ev/structure_base.txt`, `ev/structure_archscore_head.txt`). The budget file's only metric move is that row, down. It is earned by `_restore_daytypes` folding the two duplicated restore loops.
- `closure.py select --diff <base>` at the head gives `MODE: SCOPED -- 22 script(s) run, 11 scoped out.` (`ev/closure_select.txt`). The gate itself was not re-run.
- Class seams: the enumerator's dispositions in the body were read and are not contested. The one consumer path, `async_learn_dynamics` and its three callees, is the whole diff.

## Findings

- Figure not re-derived: the body quotes archscore `reflective_writes 11 -> 9` and `computed_attr_access 28 -> 26`. At the head, `score.py --diff <base>` prints `11 -> 10` and `28 -> 27` (gate-only rows; `dS +0.0237 IMPROVES` and `literal_clone_copies 122 -> 120` match). The body must quote what the tool prints at its head. Carry: dismissed: owed by this group's re-cut under ## Block, no other stage affected
- Surviving mutant R_SETTLE_STRICT (`<= DHW_CHARGE_SETTLE_HOURS` to `<`) survives the features block. At a 5-min cadence an interval ending exactly 0.25 h after the last heated sample is a normal case, so the boundary decides whether the third post-charge sample is learned and is unpinned.; it also survives the whole of `tests/features.py` in place (`ev/mutants_survivors_features_full.txt`: `SURVIVED NULL`, `SURVIVED R_SETTLE_STRICT`). Carry: dismissed: owed by this group's re-cut under ## Block, no other stage affected
- Surviving mutant R_FOLD_SKIP (skip the draw-stat fold on a charge-affected interval instead of folding zero) survives the features block. The body's claim "still folded, so occurrence accounting is unchanged" is unpinned there.; it also survives the whole of `tests/features.py` in place (`SURVIVED R_FOLD_SKIP`). Carry: dismissed: owed by this group's re-cut under ## Block, no other stage affected

## Friction

none
