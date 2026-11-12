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

**Repair of the fix review's block at 594238bf (mutation-vacuous, second block on this part).** No production behaviour changed: the only `custom_components/` change since 594238bf moves store.py's `_Z0` onto its own line (`git diff 594238bf..HEAD -- custom_components/` is that hunk alone), so public names and signatures are as Part 3 was built on. Every survivor the verdict listed is pinned by a check shown red under it, and the fixer's own pass over every added line leaves only two survivors, each equivalent (below).

## Head

4ab8ea4dde67be62baee17c5b9d0feadc92e3041, on merge base 19baca76181cb019d9b1cfd93ee6bc0a08e20047 (origin/main at 19baca7618 at 2026-11-12T15:23Z; the head contains it, `git merge-tree --write-tree origin/main HEAD` reports no conflict). Measured 2026-11-12 UTC.

## Mutation proof

Instrument: `python3 dev/audit/harnesses/boost_tail_mutants.py`, run from the repository root with `PYTHONPATH=tests/hastub`. It applies each mutant to `custom_components/heatpump_optimizer/boost.py` in place, runs this part's block of `tests/features.py` through `tools/audit/seat/features_block.py` (from `# #1935 follow-up (R10-OUTSIDE-LEARNER-ROBUSTNESS-P2)` to `# A hot-water charge inside a counter span (the dwell saw it)`; 21 checks, all pass unmutated), and restores the file. A mutant is killed when the block exits non-zero, by a red check or a raise. Its subprocess now runs with `PYTHONDONTWRITEBYTECODE=1`: two equal-size mutants written inside one second shared a cached `.pyc`, so a run measured the previous mutant (seen on this seat: the same BOOLOP list gave different verdicts on two consecutive runs, identical once bytecode writing was off). Result at the head: `MUTANTS: as expected`.

The verdict's survivors, each with the check that kills it (each check is new in this pass, so each was red under its mutant before it was green at the head):
- X1 (`_clear_spent` without `CHANNEL_SPACE not in self.until`): **not equivalent.** A press in the tail's last two hours keeps the overlay live past the tail's end, with no clock step; the mutant's expiry then clears the sum and the tail under the live overlay. Red: "the boosted sum is not cleared while an overlay or the mode is live past an earlier boost's tail, so the live boost adds to it, over both surfaces".
- X2 (`_clear_spent` without `self.mode_since is None`): the same check, a mode held 14 h past a 20-minute overlay's tail.
- X3 (`_set_active` re-stamps `space_since` on a live press): "an extended overlay sums from its first press; the mode entered after a spent tail sums only itself".
- X4 (`note_mode_change`'s `if old == MODE_BOOST:` to `if False:`): "leaving the boost mode, and a cycle whose expiry starts a tail, each schedule a save carrying the tail and its sum; entering the mode, another mode change and a quiet cycle schedule none". It records `_schedule_persist` and reads `_store_payload`'s `space_settle` record for the left mode (`boosted_h` 1.0).
- X5 (`apply` saves only on `released`): the same check, which drives `boost.apply` on a coordinator whose overlay ran out three hours after its press (`boosted_h` 2.0), then a second, quiet cycle that saves nothing.
- X7 (`settle` may shorten a running tail, `if True:`): "a settle ending before the running tail's end leaves it; one ending later moves it".
- X11 (a negative `boosted_h` restored): "a restored boosted sum outside [0, inf) is unknown; 0 and 0.5 h restore as stored" (-1, NaN, inf and `True` read as unknown).
- X13 (entering the mode keeps a spent sum): "an extended overlay sums from its first press; the mode entered after a spent tail sums only itself".

The fixer's own pass over every added line: `python3 -I tools/audit/seat/mutant_run.py --diff 19baca7618...HEAD --cmd "env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py <START> <END> --prelude <emitted prelude>" --max-mutants 0 --report-only --in-place` drew 74 mutants (every one `--list` prints for this diff) and reported 2 `SURVIVED`. Every other mutant was killed. mutant_run refuses a command that fails on the unedited tree, so its rc 0 is also the null control. The pass before these pins left 14 alive. Each was pinned by a check in this diff, or dispositioned below:
- `boost.py` `BoostState.settle` CMP_BOUND (`> 0` to `>= 0`): equivalent. The arms differ only when the new end equals the held tail, and the body then writes the value the tail already holds. Triaged in `tests/mutation_ledger/survivor_triage/boost.py/BoostState.settle.CMP_BOUND.d5a2c82b.json`.
- `boost.py` `BoostState._expire_one` CALL_DEL (`self.settle(end, self.space_since)`): equivalent. It sits under `if settle and channel == CHANNEL_SPACE:`, and the only call of `_expire_one`, `expire`'s block loop, passes `settle=False`. That is the same reason as the existing GUARD_OFF triage `BoostState._expire_one.GUARD_OFF.50e15df0.json`. No ledger row: `tests/mutation_table.py`'s inventory does not generate this mutant, and `tests/entities.py` refused the row as stale (`and every mark still names a mutant this tree generates`), so the disposition is here.
- `store.py` `_Z` CONST_SWAP (main's `_Z = Domain("real", 0.0)` to 1.0) survived `tests/entities.py` whole (rc 0 under it). It was main's declaration, which this diff had rewritten only to append `_Z0`. `_Z0` now has its own line, so the site is main's again, and `_Z0`'s domain is pinned ("... a boosted sum of any length from zero, or unknown; a negative one is out of its domain").

The ledger inventory's BOOLOP sites (`and` to `or`), which `mutant_run.py` does not draw, are in the harness. B240 and B557 turn a check red. B502 raises `KeyError: 'space'` in `_store_payload`, where `persist`'s `except` would drop the save. B549 and B560 raise in `_restore_settle` on a store with no tail or no overlay. B557 was alive until "a restart restores a running settling tail ..." asserted that an overlay restored as ended-while-down leaves no start (`_bt_down.space_since is None`).

The verdict asked for the closure where the block was not enough: no verdict mutant survives the block, so none needed a closure run.

## Null control

- M0 (a comment edit) exits 0 with 0 red in the harness at the head.
- `mutant_run.py` refuses a command that fails on the unedited tree; it ran (rc 0).
- No boost: `null_no_boost` walks the scale +0.0045 (worst) / +0.0236 (final) at the merge base 26072317b5 and at 44103897f8, with identical daily rows.
- An install that never boosted, or only blocked, persists main's payload field for field. A spent tail, once expired, stores `{}` again.
- The save checks' own nulls: entering the mode, a change between two other modes and a quiet `apply` cycle schedule no save.
- The order of the freeze reasons in `_learning_frozen` is main's (AST check of its returns).

## Figures

<!-- figure-block: scope-line mb=19baca76181cb019d9b1cfd93ee6bc0a08e20047 head=4ab8ea4dde67be62baee17c5b9d0feadc92e3041 -->
~~~text
MODE: SCOPED -- 29 script(s) run, 4 scoped out.
~~~
<!-- /figure-block -->

- Scoped gate: `GOLDEN_MODE=drift GATE_SCOPE=auto tests/run.sh` at 4ab8ea4dde: `MODE: SCOPED -- 29 script(s) run, 4 scoped out.`, `31 TEST SCRIPT(S) PASSED; 3 SCOPED OUT AND NOT RUN` (scoped out: `tests/arch_score.py`, `tests/ha_contract.py`, `tests/md_tables.mjs`; `tests/layout.py` ran under `run_always`), gate rc 0. `tests/features.py`, `tests/entities.py` and `tests/boost_drift_replay.py` ran whole.
- `tests/entities.py` alone at 05f19fcbf5 (after the stale triage row was dropped): `ALL 2709 ENTITY CHECKS PASSED`. At 81f0a1fc4c it failed 1 of 2709, the stale row above.
- Feature block: `ALL 21 FEATURES BLOCK PASSED` at the head.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED` (exit 0). No budget moved.
- `python3 tools/audit/archscore/score.py --diff 19baca7618`: `Architecture score: dS +0.0246 IMPROVES` (coord_footprint 2492 -> 2491, literal_clone_copies 120 -> 118).
- `python3 tools/pr/ci_predict.py`: `no closures, fast, governance or instrument red predicted`. It lists 21 added sites as unpinned, all under `## Unpinned sites`.
- Walk of the house heat-loss scale: unchanged from the 44103897f8 measurement, because no production line that the harness reaches moved since then (`git diff 594238bf..HEAD -- custom_components/` is the `_Z0` line move alone). Instrument: `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/boost_press_tail_walk.py production full none` (`PRODUCTION: EQUAL to full on 10 of 10 arms`; `NULL CONTROL: none differs from full on 5 press arm(s): SEES`). The table and the scaled-formula measurements behind the ruling are in this pull request's history at handoff 594238bf. Neither scaled formula keeps every press arm inside `press_120x1_full`'s |worst| 0.0045. Their worst press arms are slope6h 30x1 at -0.0129 and slope3h 10x1 at -0.0237, against heat-free freeze twins at -0.0207 and -0.0232.
- Goldens: no file under `tests/golden/` and neither claim file is in the diff (`git diff --stat 19baca7618...HEAD -- tests/golden` prints nothing).

## Unpinned sites

- custom_components/heatpump_optimizer/boost.py:137 GUARD_OFF: killed by tests/features.py's part block (the added-line pass under `## Mutation proof`, 0 survivors at this site); pinned by mutation-autofix (its lane mutates custom_components/)
- custom_components/heatpump_optimizer/boost.py:143 GUARD_OFF: killed by tests/features.py's part block (the added-line pass under `## Mutation proof`, 0 survivors at this site); pinned by mutation-autofix (its lane mutates custom_components/)
- custom_components/heatpump_optimizer/boost.py:149 CMP_BOUND: killed by tests/features.py's part block (the added-line pass under `## Mutation proof`, 0 survivors at this site); pinned by mutation-autofix (its lane mutates custom_components/)
- custom_components/heatpump_optimizer/boost.py:155 GUARD_OFF: killed by tests/features.py's part block (the added-line pass under `## Mutation proof`, 0 survivors at this site); pinned by mutation-autofix (its lane mutates custom_components/)
- custom_components/heatpump_optimizer/boost.py:240 BOOLOP: killed by tests/features.py's part block (the added-line pass under `## Mutation proof`, 0 survivors at this site); pinned by mutation-autofix (its lane mutates custom_components/)
- custom_components/heatpump_optimizer/boost.py:240 GUARD_OFF: killed by tests/features.py's part block (the added-line pass under `## Mutation proof`, 0 survivors at this site); pinned by mutation-autofix (its lane mutates custom_components/)
- custom_components/heatpump_optimizer/boost.py:366 GUARD_OFF: killed by tests/features.py's part block (the added-line pass under `## Mutation proof`, 0 survivors at this site); pinned by mutation-autofix (its lane mutates custom_components/)
- custom_components/heatpump_optimizer/boost.py:368 GUARD_OFF: killed by tests/features.py's part block (the added-line pass under `## Mutation proof`, 0 survivors at this site); pinned by mutation-autofix (its lane mutates custom_components/)
- custom_components/heatpump_optimizer/boost.py:464 GUARD_OFF: killed by tests/features.py's part block (the added-line pass under `## Mutation proof`, 0 survivors at this site); pinned by mutation-autofix (its lane mutates custom_components/)
- custom_components/heatpump_optimizer/boost.py:496 GUARD_OFF: killed by tests/features.py's part block (the added-line pass under `## Mutation proof`, 0 survivors at this site); pinned by mutation-autofix (its lane mutates custom_components/)
- custom_components/heatpump_optimizer/boost.py:502 BOOLOP: killed by tests/features.py's part block (the added-line pass under `## Mutation proof`, 0 survivors at this site); pinned by mutation-autofix (its lane mutates custom_components/)
- custom_components/heatpump_optimizer/boost.py:502 GUARD_OFF: killed by tests/features.py's part block (the added-line pass under `## Mutation proof`, 0 survivors at this site); pinned by mutation-autofix (its lane mutates custom_components/)
- custom_components/heatpump_optimizer/boost.py:504 RETURN_DEL: killed by tests/features.py's part block (the added-line pass under `## Mutation proof`, 0 survivors at this site); pinned by mutation-autofix (its lane mutates custom_components/)
- custom_components/heatpump_optimizer/boost.py:549 BOOLOP: killed by tests/features.py's part block (the added-line pass under `## Mutation proof`, 0 survivors at this site); pinned by mutation-autofix (its lane mutates custom_components/)
- custom_components/heatpump_optimizer/boost.py:549 CMP_BOUND: killed by tests/features.py's part block (the added-line pass under `## Mutation proof`, 0 survivors at this site); pinned by mutation-autofix (its lane mutates custom_components/)
- custom_components/heatpump_optimizer/boost.py:549 GUARD_OFF: killed by tests/features.py's part block (the added-line pass under `## Mutation proof`, 0 survivors at this site); pinned by mutation-autofix (its lane mutates custom_components/)
- custom_components/heatpump_optimizer/boost.py:554 CMP_BOUND*2: killed by tests/features.py's part block (the added-line pass under `## Mutation proof`, 0 survivors at this site); pinned by mutation-autofix (its lane mutates custom_components/)
- custom_components/heatpump_optimizer/boost.py:557 BOOLOP: killed by tests/features.py's part block (the added-line pass under `## Mutation proof`, 0 survivors at this site); pinned by mutation-autofix (its lane mutates custom_components/)
- custom_components/heatpump_optimizer/boost.py:557 GUARD_OFF: killed by tests/features.py's part block (the added-line pass under `## Mutation proof`, 0 survivors at this site); pinned by mutation-autofix (its lane mutates custom_components/)
- custom_components/heatpump_optimizer/boost.py:560 BOOLOP: killed by tests/features.py's part block (the added-line pass under `## Mutation proof`, 0 survivors at this site); pinned by mutation-autofix (its lane mutates custom_components/)
- custom_components/heatpump_optimizer/boost.py:560 GUARD_OFF: killed by tests/features.py's part block (the added-line pass under `## Mutation proof`, 0 survivors at this site); pinned by mutation-autofix (its lane mutates custom_components/)
- custom_components/heatpump_optimizer/boost.py:143 CMP_BOUND (`> 0` to `>= 0` in `BoostState.settle`): equivalent, triaged in tests/mutation_ledger/survivor_triage/boost.py/BoostState.settle.CMP_BOUND.d5a2c82b.json (the equal arm writes the value the tail already holds)
- custom_components/heatpump_optimizer/boost.py:186 CALL_DEL (`self.settle(end, self.space_since)` in `BoostState._expire_one`): equivalent, unreachable: it sits under `settle and channel == CHANNEL_SPACE`, and the only caller passes `settle=False`; no ledger row, because tests/mutation_table.py's inventory does not generate it (see ## Mutation proof)

## Red checks

- `tests / mutation` at the earlier heads: red by construction on the added sites above, before mutation-autofix pins them. Cheaper detector: `tools/pr/ci_predict.py`. It already runs locally at no added standing cost, and it predicted every site before the push. The red is the lane's own pinning step, not a defect, so no countermeasure is owed. Every site is now killed by the part's block (above), so the pins it writes are real.

## Forward-carry

- Round 11: the scaled settling tail. Measured on `dev/audit/harnesses/boost_press_tail_walk.py`, with both slopes and the heat-free `freeze` twins as the null control: neither formula keeps every press arm within `press_120x1_full`'s |worst| on `tests/boost_drift_replay.py`'s replay. The freeze with no heat walks the scale as far as the press does (-0.0232 vs -0.0237), so the walk comes from the freeze's sample selection, not from the heat. Precondition a future formula must meet: every press arm of the harness within the absolute bound under `slope<new>` at its own merge base, re-measured and not carried from these figures, plus an explanation of the freeze-skip walk. The data such a formula prices on already ships: `BoostState.space_boosted`, persisted as `space_settle/boosted_h`. Carry: R10-ROUND-PLAYBOOK-FINAL
- Part 3's frozen-until end is the overlay's end plus the full `SPACE_SETTLE_TAIL` for every length, and while a tail runs it is `BoostState.space_settle_until`. P3 projects through `BoostState` (the live overlay's end, then `space_settle_until`) and does not recompute a tail. Carry: R10-OUTSIDE-LEARNER-ROBUSTNESS-P3
- A mutation harness that rewrites a module in place and re-imports it in a subprocess measures a stale `.pyc` when two equal-size mutants land in one second. Seen in this part's harness and a scratch driver, fixed here with `PYTHONDONTWRITEBYTECODE=1`. Not established for `tools/audit/seat/mutant_run.py`: its two passes here agreed with bytecode on and off. Carry: dismissed: not measured beyond this part's own harness; no later stage's practice changes on an unshown hazard

## Friction

none
