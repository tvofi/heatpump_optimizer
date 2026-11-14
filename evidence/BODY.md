Part 2 of outside pull request #3435. Thank you, Bankaifan, for the boost-tail work and the live-install report behind it. Your commit 7db392d8c2 is kept with your authorship, and our changes are separate later commits. This pull request does not close #3435. The orchestrator closes it with thanks after R10-OUTSIDE-LEARNER-ROBUSTNESS-P3 merges. Part of #201.

**Ruling applied (orchestrator, under the owner's mandate, option (A)).** The brief's absolute acceptance stays: every press arm must walk the house heat-loss scale no further than the whole window does under the full tail. Neither scaled-tail formula passes it (table under `## Figures`). The heat-free freeze arms show that a walk of that size comes from which samples the freeze skips, not from boost heat. So this part ships the boosted sum, the persisted tail and overlay start, and the store work, and every space boost owes the full `SPACE_SETTLE_TAIL` (12 h) from its own end, whatever time it ran. `settle_tail`, its slope, floor and press minimum, the const moves they needed (`HOUSE_LOSS_MAX_SAMPLE_HOURS`, `PUMP_MIN_ON_MINUTES`; `early_cutoff.py` is main's again) and their checks are gone. The press and freeze surfaces stay in `tests/boost_drift_replay.py`'s `cycle`. The tail policies and the walk report are in `dev/audit/harnesses/boost_press_tail_walk.py`.

What ships, by brief item:
- (a) `BoostState.space_boosted` sums the time each boost ran, over the channel overlay and the global mode, since the learners were last free of a boost. It is cleared only by `_clear_spent`, once a tail ran out with nothing live. An unseen start makes it `None`. No tail is priced on it in this part. It is recorded and persisted so that a later formula has the data after an upgrade. Short boosts back to back owe the full tail from the last end, so never less than one boost of their summed length.
- (b), (c) No floor and no press pricing exist without the scaling. Both are removed, not carried.
- (d) The mode's start is not persisted. A mode restored as boost leaves the sum `None` when left, and it owes the full tail like every boost. This fails closed and is pinned.
- (e) Siblings: `space_learning_frozen` and `interval_boosted` read the overlay and `space_settle_until`, unchanged in meaning, so they are covered. `heat_loss_refit` waits `SPACE_SETTLE_TAIL` after the last tagged pair (`coordinator.py`, `settle=boost.SPACE_SETTLE_TAIL`). Every boost length owes exactly that tail, pinned by a sweep, so the refit never reads evidence the interval learners refused.
- (f) The store: `BOOST_STORE_VERSION` is unchanged at 1. A store this build writes loads in main's loader with main's overlay and block. One main wrote loads here with no tail. `space_settle/until` declares its own look-ahead (`BOOST_SPACE_SETTLE_TAIL_HOURS`), and a tail past it is bounded by the store. A spent tail is not restored.

The group's roster entry holds two carries, both item 0aadbc91 (part 2 cut from the author's commit with authorship kept), and both land here. Numbered from 1 they are Carry 1 and Carry 2. The dispatch numbers the same two from 0 as Carry 0 and Carry 1.

- Carry 1 (roster entry 0, the dispatch's Carry 0): lands here. The persisted tail, the overlay start, the store entries and the mode-change call ship, cut from 7db392d8c2, whose author is Bankaifan. The scaling on the time the boost ran does not ship, by the ruling above, and goes forward to round 11 under `## Forward-carry`.
- Carry 2 (roster entry 1, the dispatch's Carry 1): the same part stated again by the round. It lands here with the same disposition as Carry 1.

Also fixed: one mypy `union-attr` in `_restore_settle` that the wip head carried. `tests/typing_ruler.py` measured 1 against a recorded 0. The tail record is now narrowed before it is read.

## Head

594238bfda916f814ca54bb5e84725602b7005dd, on merge base 2b4515dc52 (origin/main at 2b4515dc52; this head merges it). Measured 2026-11-12 UTC.

## Mutation proof

Instrument: `python3 dev/audit/harnesses/boost_tail_mutants.py`. It applies each mutant to `custom_components/heatpump_optimizer/boost.py` in place, runs this part's block of `tests/features.py` through `tools/audit/seat/features_block.py` (from `# #1935 follow-up (R10-OUTSIDE-LEARNER-ROBUSTNESS-P2)` to `# A hot-water charge inside a counter span (the dwell saw it)`; 12 checks, all pass unmutated), and restores the file. Result at 44103897f8: `MUTANTS: as expected`.

- M0 null (a comment edit): 0 red.
- M1 short tail (`until = utc_shift(end, SPACE_SETTLE_TAIL if self.space_boosted is None or self.space_boosted >= timedelta(hours=2) else timedelta(hours=1.5))`): 7 red. These are the 38 s/window/click check, back-to-back sum, sum clears, mode restored, restart keeps the sum, both store directions, and the refit sweep "every boost length, cancelled inside the window or expired past it, owes the full tail the refit waits".
- M2 sum dropped (`self.space_boosted = timedelta(...)` for `+=`, each boost counted alone): 3 red. These are "short boosts back to back owe no less than one boost of their summed length...", "the boosted sum clears once its tail ran out with nothing live, and not before" and "a restart keeps the boosted sum with the tail...".
- M3 persisted tail dropped (`_store_payload`'s `if held.space_settle_until is not None:` to `if False:`): 2 red. These are "a boost store from an install that never boosted is main's payload, field for field" and "a boost store this build wrote loads in main's loader...".
- M4 restore dropped (`_restore_settle(held, raw, now)` to `pass` in `restore`): 1 red, "a boost store this build wrote loads in main's loader ... this build's loader keeps the tail (null control)".
- M5 sum never clears (`_clear_spent` resets only the tail): 1 red, "the boosted sum clears once its tail ran out with nothing live, and not before".

## Null control

- No boost: `null_no_boost` walks the scale +0.0045 (worst) / +0.0236 (final) at the merge base 26072317b5 and at the head. The daily rows are identical (days 4 to 8: 1.0463, 1.0455, 1.0472, 1.0499, 1.051).
- A window run to its end settles 12 h from that end, as on main (first check of the block).
- An install that never boosted, or only blocked, persists main's payload field for field (block check; M3 turns it red).
- The order of the freeze reasons in `_learning_frozen` is main's (AST check of its returns).
- The walk harness's own equality verdict: the `none` policy must differ from `full` on at least one press arm, or the verdict is blind (see `## Figures`).

## Figures

<!-- figure-block: scope-line mb=2b4515dc52821ad721225090d329c224dbddafae head=594238bfda916f814ca54bb5e84725602b7005dd -->
~~~text
MODE: SCOPED -- 29 script(s) run, 4 scoped out.
~~~
<!-- /figure-block -->

With the scaling removed, every press arm and every freeze arm equals its full-tail figure, and `null_no_boost` reads as at the merge base. Walk of the house heat-loss scale per arm. `worst` is the largest signed excursion of a 03:00 daily row on or after day 5 from day 4's. `final` is the last value's excursion. Presses are at 07:00, 12:00 and 18:00 on days 5 and 6. Instrument: `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/boost_press_tail_walk.py production full none` at the head (`PRODUCTION: EQUAL to full on 10 of 10 arms`; `NULL CONTROL: none differs from full on 5 press arm(s): SEES`, exit 0).

| arm | production (head) | full | none |
|---|---|---|---|
| press 10x1 | -0.0045 / +0.0226 | -0.0045 / +0.0226 | -0.0010 / +0.0197 |
| press 30x1 | -0.0045 / +0.0229 | -0.0045 / +0.0229 | +0.0021 / +0.0227 |
| press 60x1 | -0.0045 / +0.0205 | -0.0045 / +0.0205 | +0.0077 / +0.0247 |
| press 120x1 | -0.0045 / +0.0216 | -0.0045 / +0.0216 | +0.0441 / +0.0295 |
| press 10x4 | -0.0045 / +0.0214 | -0.0045 / +0.0214 | +0.0052 / +0.0231 |
| freeze 10x1 | +0.0052 / +0.0252 | +0.0052 / +0.0252 | -0.0037 / +0.0197 |
| freeze 30x1 | +0.0052 / +0.0252 | +0.0052 / +0.0252 | -0.0037 / +0.0197 |
| freeze 60x1 | -0.0045 / +0.0236 | -0.0045 / +0.0236 | -0.0031 / +0.0214 |
| freeze 120x1 | -0.0045 / +0.0221 | -0.0045 / +0.0221 | -0.0079 / +0.0227 |
| freeze 10x4 | -0.0045 / +0.0221 | -0.0045 / +0.0221 | -0.0062 / +0.0209 |
| null_no_boost | +0.0045 / +0.0236 | | |

The scaled formulas are measured by the same harness with `slope6h slope3h`, which patches `BoostState.settle` per policy. That was run at 373f8fb942, whose `boost.py` differs from the head only by the narrowing in `_restore_settle`. Its production, full and none rows equal the head's above. Bound = `press_120x1_full`'s |worst| 0.0045:

| arm | slope6h (12 h + 6 h ln(r), floor 1.5 h) | slope3h (12 h + 3 h ln(r), floor 1.5 h, press >= 10 min) |
|---|---|---|
| press 10x1 | +0.0028 / +0.0227 PASS | -0.0237 / +0.0193 FAIL |
| press 30x1 | -0.0129 / +0.0204 FAIL | +0.0051 / +0.0239 FAIL |
| press 60x1 | -0.0045 / +0.0205 PASS | -0.0045 / +0.0205 PASS |
| press 120x1 | -0.0045 / +0.0216 PASS | -0.0045 / +0.0216 PASS |
| press 10x4 | -0.0045 / +0.0214 PASS | -0.0045 / +0.0214 PASS |
| freeze 10x1 (no heat) | -0.0032 / +0.0222 | -0.0232 / +0.0183 |
| freeze 30x1 (no heat) | -0.0207 / +0.0176 | +0.0067 / +0.0246 |

The freeze twin with no heat behind it walks -0.0232 against the press arm's -0.0237 (slope3h 10x1), and -0.0207 against -0.0129 (slope6h 30x1). `freeze_10x1_full` and `freeze_30x1_full` (+0.0052) and the no-boost null's own worst (+0.0045) are at or past the bound with no tail scaling at all.

- That run's first equality verdict was wrong. `arm_summary` carries the arm's name, so it printed `PRODUCTION: DIFFERS to full on 0 of 10 arms` and `NULL CONTROL: ... SEES` on names alone, though walks were equal to four places on all ten pairs. Fixed at ca6929d131 (`comparable` drops the name). The head's run above is after the fix.
- Feature block: `python3 tools/audit/seat/features_block.py "# #1935 follow-up (R10-OUTSIDE-LEARNER-ROBUSTNESS-P2)" "# A hot-water charge inside a counter span (the dwell saw it)" --prelude "<--emit-prelude output>"`: `ALL 12 FEATURES BLOCK PASSED`.
- Scoped gate: `GOLDEN_MODE=drift GATE_SCOPE=auto tests/run.sh` at 44103897f8: `MODE: SCOPED -- 29 script(s) run, 4 scoped out.`, `31 TEST SCRIPT(S) PASSED; 3 SCOPED OUT AND NOT RUN` (among them `tests/features.py`, `tests/boost_drift_replay.py`, `tests/typing_ruler.py`, `tests/stress.py`). The earlier run at c4fde362d4 failed only `tests/typing_ruler.py`, on the union-attr above.
- `python3 tests/structure.py`: exit 0 at the head merged with main. `class_excess_loc` and `max_class_loc` were re-recorded 3 lower (d12b459d6b; `async_set_mode`'s boost-mode exit is one call into `boost.note_mode_change`). Merging origin/main (6e100ef698, then 2b4515dc52) took main's `class_excess_loc` row, which left the 3 lines unrecorded (`structure.py` exit 2, IMPROVED and not yet recorded). 9a4e7bf85d records them again, 17526 to 17523. No budget is raised.
- `python3 tools/audit/archscore/score.py --diff 26072317b5`: `Architecture score: dS +0.0243 IMPROVES` (coord_footprint 2492 -> 2491, literal_clone_copies 122 -> 120 via store `_Z0`).
- `python3 tools/pr/ci_predict.py --apply-inert`: `no closures, fast, governance or instrument red predicted`, once three stale ledger pins on the rewritten `async_set_mode` and `apply` guards were deleted (c4fde362d4) and both new harnesses classified (`--apply-inert`).
- Production's payload builder is `_store_payload`, not `_payload`: `closure.py no-copies` (prepr.sh) refused the latter as copied by tests/features.py's existing module-level `_payload`.
- Goldens: no file under `tests/golden/` and neither claim file is in the diff (`git diff --stat 26072317b5...HEAD -- tests/golden` prints nothing).

## Unpinned sites

- custom_components/heatpump_optimizer/boost.py:137 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the six named mutants under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:143 CMP_BOUND: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the six named mutants under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:143 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the six named mutants under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:149 CMP_BOUND: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the six named mutants under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:155 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the six named mutants under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:240 BOOLOP: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the six named mutants under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:240 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the six named mutants under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:366 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the six named mutants under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:368 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the six named mutants under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:464 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the six named mutants under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:496 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the six named mutants under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:502 BOOLOP: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the six named mutants under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:502 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the six named mutants under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:504 RETURN_DEL: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the six named mutants under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:549 BOOLOP: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the six named mutants under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:549 CMP_BOUND: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the six named mutants under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:549 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the six named mutants under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:554 CMP_BOUND*2: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the six named mutants under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:557 BOOLOP: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the six named mutants under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:557 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the six named mutants under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:560 BOOLOP: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the six named mutants under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:560 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the six named mutants under ## Mutation proof

## Red checks

- `mutation` at 44103897f885: red by construction on the 22 site(s) under `## Unpinned sites`; mutation-autofix pins killed sites after the push. Cheaper detector: `tools/pr/ci_predict.py`, already run locally at no added standing cost, predicted every site before the push; the red is the lane's own pinning step, not a defect, so no countermeasure is owed.

## Forward-carry

- Round 11: the scaled settling tail. Measured on `dev/audit/harnesses/boost_press_tail_walk.py` (table above, both slopes, with the heat-free `freeze` twins as the null control): neither formula keeps every press arm within `press_120x1_full`'s |worst| on `tests/boost_drift_replay.py`'s replay. The freeze with no heat walks the scale as far as the press does (-0.0232 vs -0.0237), so the walk is the freeze's sample selection, not the heat. The walk is also not monotone in the tail (press 10x1: +0.0028 at a 1.5 h tail, -0.0237 at 4.55 h). Precondition a future formula must meet: every press arm of the harness within the absolute bound under `slope<new>` at its own merge base, re-measured and not carried from these figures, plus an explanation of the freeze-skip walk (why a heat-free freeze of these hours moves the interval learner, and why the formula's arms are not tuned to this scenario's hours). The data such a formula prices on already ships: `BoostState.space_boosted`, persisted as `space_settle/boosted_h`. Carry: R10-ROUND-PLAYBOOK-FINAL
- Part 3's frozen-until end is no longer "the overlay's end plus the tail P2 prices". It is the overlay's end plus the full `SPACE_SETTLE_TAIL` for every length, and while a tail runs it is `BoostState.space_settle_until`. P3 projects through `BoostState` (the live overlay's end, then `space_settle_until`) and does not recompute a tail. Its brief's "builds on the scaled tail" no longer holds. Carry: R10-OUTSIDE-LEARNER-ROBUSTNESS-P3

## Friction

none
