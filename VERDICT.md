Fix review: blocked 594238bfda916f814ca54bb5e84725602b7005dd mutation-vacuous: X4 boost.py:368 mode-exit persist survives the closure, X1 X2 X3 X5 X7 X11 X13

bus-nonce: 94c84b49fde16424eb39fcbccbc84a32

## Block

The body lists `custom_components/heatpump_optimizer/boost.py:368 GUARD_OFF` under `## Unpinned sites` as "pinned by mutation-autofix". That lane pins only sites a test kills, and no test in this site's closure kills it. The line is `if old == MODE_BOOST: _schedule_persist(coord)` in `note_mode_change`. It is the only save of the settling tail that leaving the global boost mode starts. A scout read of every boost persist site at the head (boost.py:369, :465, :615, :630; pump_arbiter.py:1671) found no save at shutdown, at unload or on a timer. `apply`'s `held.space_settle_until != tail` test cannot see the change either, because the mode exit sets the tail outside `apply`. Under the mutant, a restart inside the 12 h after leaving boost mode drops the tail. That is brief item NEED's defect ("a restart inside the tail drops it") on the mode surface, so the mutant is not equivalent.

Mutant X4 is `if old == MODE_BOOST:` -> `if False:`, the lane's GUARD_OFF at that line. Its rc at this head:
- the part's features block (`features_block.py`, 12 checks): 0 red;
- tests/block_duty.py, tests/finite_boundary.py, tests/guard_pins.py, tests/entities.py, tests/boost_drift_replay.py (default arms) and tests/features.py (whole file): rc 0 on every script (ev/closure_X4.txt).

Owed: a check that leaving boost mode schedules a save whose payload carries `space_settle`, or a restart round trip after a mode exit. It must be shown red under X4 and green at the head.

Every other survivor my driver reports at this head (ev/xmut_head.txt for the block, ev/xmut_fast_scripts.txt for the fast scripts, ev/closure_X5.txt). For each, the fixer either pins it or names it equivalent with its reason:
- X1: `_clear_spent` without the `CHANNEL_SPACE not in self.until` test. My reading is that it is equivalent: a 12 h tail cannot run out inside a 2 h overlay without a clock step. The fixer should say so.
- X2: `_clear_spent` without `self.mode_since is None`. The sum clears while the mode is live once an earlier channel tail runs out under a mode held for more than 12 h. That breaks brief item (a), "clear the sum only when a tail has run out with no overlay live", over both surfaces. Survives the block and the fast scripts.
- X3: `_set_active` re-stamps `space_since` on a press made while the overlay is live. The sum then under-counts a boost that was extended. Brief item (a) says the start is stamped "at every press that finds no live overlay". Survives the block and the fast scripts.
- X5: `apply` persists only on `released`. It survives the whole closure (ev/closure_X5.txt). It is near-equivalent for the tail, because the stored `space/until` and `since` let `_restore_settle` rebuild the tail through its ended-while-down path. The sum of earlier boosts is lost on that path, though, and it comes back as the last boost alone.
- X7: `settle` may shorten a running tail. This breaks the brief's KEEP item "a tail that is running is never shortened". It is reachable only on a stepped-back clock. Survives the block and the fast scripts.
- X11: a negative `boosted_h` is accepted at restore. The store does not enforce `_Z0` on load (`store.py` `_sanitize` and `_bound_instants` only), so `_restore_settle` is the only guard. Survives the block and the fast scripts.
- X13: entering the mode does not clear a spent sum, so the sum of a boost from long ago carries into the mode's sum. Survives the block and the fast scripts.

X2, X3, X7, X11 and X13 were run against the block and three fast scripts only, not against `features.py` or `entities.py`, which were run whole only for X4 and X5. A kill elsewhere in the closure would settle that mutant: show it.

## Evidence

- Review round: the second handoff of this part, and its first fix review. The earlier handoff was refused at `body_push.sh` (structure, brief-carries) before any verdict. Fewer than four rounds, so no re-cut is owed.
- Earlier refusal, item 1 (structure): `python3 tests/structure.py` passes at the head (ev/structure_head.txt) and with the head merged with origin/main c67ab5f0e0 (ev/structure_merged_main.txt): `STRUCTURE RATCHET PASSED`, exit 0 both. No budget is raised: `tests/structure_budgets.json` moves only `class_excess_loc`/`max_class_loc` down. Answered.
- Earlier refusal, item 2 (brief-carries): the body names Carry 1 and Carry 2 with their dispositions. `carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body BODY.md --pr-group R10-OUTSIDE-LEARNER-ROBUSTNESS-P2`: `2 routed, 0 unrouted, 0 bad destination(s)`, rc 0 (ev/carry_audit_body.txt). Both forward-carries are on the roster at c1787f33c7: groups[354].carry[39] (item 4b518e5d, R10-ROUND-PLAYBOOK-FINAL), which states the control (the heat-free freeze twins) and the precondition (absolute bound re-measured at its own merge base), and groups[464].carry[3] (item e8e004db, R10-OUTSIDE-LEARNER-ROBUSTNESS-P3). Answered.
- Head: the body's `## Head` names 594238bfda916f814ca54bb5e84725602b7005dd, the handoff tip measured here. No pull request, review packet or CI exists yet, so no check runs were read and no red is answered or owed. The body's pre-emptive `mutation` answer is in a red that `merge_train.py owed-reds` lists (ev/owed_reds.txt), and this block's survivors bear on it.
- Merge: `git merge-tree --write-tree origin/main 594238bf` against c67ab5f0e0 gives rc 0, with `LEDGER-MERGE: resolved tests/closures.json` (ev/HEAD.txt). No conflict.
- VERSION, the manifest, RELEASE_NOTES.md, tests/golden/ and both claim files are untouched (`git diff mb...head --stat` prints nothing for them). `env_drift.py --all` was not run: the diff moves no fixture.
- Mutation proof as stated: `python3 dev/audit/harnesses/boost_tail_mutants.py` at the head gives M0 0 red, M1 7, M2 3, M3 2, M4 1, M5 1, and `MUTANTS: as expected` (ev/mutants_head.txt). It matches the body exactly. X6, X8, X9 and X12 (ended-while-down, payload `since`, restored `since`, spent tail restored) are killed by the block (ev/xmut_head.txt).
- Finder's harness at both ends: `tests/boost_drift_replay.py null_no_boost` at the merge base and at the head prints identical null_no_boost lines (days 5 to 7: 1.0455, 1.0472, 1.0499; final 1.071), and 26 checks pass at both ends (ev/replay_null_base.txt, ev/replay_null_head.txt). The default arms at the merge base give `ALL 46 BOOST DRIFT CHECKS PASSED` (ev/replay_default_base.txt). `boost_press_tail_walk.py` cannot run at the merge base, which has no `BoostState.settle` to patch, so the null was compared through the replay arm.
- Walk table: `boost_press_tail_walk.py production full none` at the head, in a clean worktree, gives `PRODUCTION: EQUAL to full on 10 of 10 arms` and `NULL CONTROL: none differs from full on 5 press arm(s): SEES`, exit 0 (ev/walk_head.txt). Every production, full and none figure and the null_no_boost row (+0.0045 / +0.0236) equal the body's table. The slope6h and slope3h rows were measured at 373f8fb942 and not re-run here: not verified by this seat.
- Downgrade claim: main's loader (merge base, store.py `_sanitize`/`_bound_instants`/`async_load`; boost.py `restore` reads only `until`) ignores `space_settle` and `space/since` and refuses no file, so the claim holds against main's real loader. The block's own test only stubs `_restore_settle`.
- Architecture: `score.py --diff 2b4515dc52` at the head gives `Architecture score: dS +0.0246 IMPROVES` (coord_footprint 2492 -> 2491, literal_clone_copies 120 -> 118) (ev/archscore_diff_mb.txt). The body's +0.0243 is against the older base 26072317b5 and was not re-derived there. `_Z0` names a literal already repeated twice in the table beside `_R`/`_Z`/`_N`, a sound dedupe and not a re-spelling.
- My mutant drivers are in ev/xmut.py, ev/xmut2.py and ev/xmut_defs.py: the builder's instruments, not the finder's.

## Findings

none
