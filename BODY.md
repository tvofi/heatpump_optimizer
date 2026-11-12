R10-DUTY-SWITCH-RESTART-LEARNING-PR-B, second pull request: the arbiter's split of a step serving both duties reads the learned estimate, as the group's ruling on rule c states. With thanks to Bankaifan, whose pull request 3420 found the duty-switch restart; its split function (order latched per step, the whole step given to the first duty when the second share is shorter than the minimum split plus the learned off time) is the starting point of `DutySwitchLearner.split` and `duty_switch.both_step_duty`, narrowed here by the ruling: the whole-step rule applies only where the plan's next step serves the denied duty, and `n` has a ceiling.

- **The reader and its first caller** (roster carry 0, item 1b22f416). `duty_switch.both_step_duty` takes the pump's record, the step's start, the plan's split and the plan's next step; `_share` in `pump_arbiter.py` delegates to it after its two collapses. The decision is `DutySwitchLearner.split`, latched on the record per step start; a record not yet loaded splits as before and latches nothing. The arbiter holds no learned state.
- **The rule.** Space goes first only where hot water to space is the one usable direction. The first duty keeps the whole step only when the switch into the second is usable, the second share is under `SPLIT_MIN_MINUTES` plus that direction's median off time, and the next step serves the second duty (or both). With no usable direction the decision is hot water first, not whole: today's split.
- **`n` has a ceiling**, `N_CAP` (twice `N_ON`), held at each booking and on each pass's decay by scaling both counts alike, so `p` does not move. A latched direction with no further episode unlatches just past two half-lives, and the default split re-tests it (verdict item n11).
- **Factory reset voids the duty-switch store** (roster carries 1 and 6, items 3c666f5b and 893e80d2), under the orchestrator's ruling under mandate 6715477401 of 2026-11-12T19:51:09Z. The store joins `_restored_stores` and `_FACTORY_VOID` as voided whole, so the existing mechanism also puts it in the undo point and the undo restores it. The entry is set up again with a new coordinator, whose record loads the voided store empty: that is the in-memory learner emptied in the reset's own step. The planner of R10-DUTY-SWITCH-PLANNER-PRICE reads the same record (`planner_fields`, on its unmerged branch), so after a reset it prices from the voided record too. A reversal is the `("duty_switch", None)` row, its `_FR_STORES` line and the reset check.
- **What the reader reads** (roster carries 4 and 5, items 90bc5153 and d088605d). Only the latches and the median off time. It reads no `n`, tally, `span_days` or published key, so a `span_days` of 0 beside non-zero tallies, or evidence accruing faster on one set-point unit, moves the split only through a latch.

The group's roster carries, by index:

- Carry 0 (item 1b22f416): implemented; `both_step_duty` is the reader and `_share` its first caller, and `dead_top_level_symbols` does not move.
- Carry 1 (item 3c666f5b): implemented per the ruling in Carry 8; the store is voided by a factory reset.
- Carry 2 (item ef5d3875): settled in part 1 (`N_ON` is a decayed weight); the split reads the latch it sets and adds nothing.
- Carry 3 (item c7d068a1): settled in part 1 (the publication's resolution); the ceiling now also bounds the published `n` at 10.
- Carry 4 (item 90bc5153): implemented; the reader reads no `span_days` and no published key, pinned by "the split reads the latches and nothing published…".
- Carry 5 (item d088605d): implemented; the reader reads no `n`, so a unit gating fewer switches moves the split only through a latch, same check.
- Carry 6 (item 893e80d2): implemented by the void; the planner's read on R10-DUTY-SWITCH-PLANNER-PRICE's unmerged branch reads the same record, voided alike.
- Carry 7 (item b30e2dd2): the leg-order owner it names exists only on R10-DUTY-SWITCH-PLANNER-PRICE's unmerged branch, not at this base; reconciled by whichever merges second, under `## Forward-carry`.
- Carry 8 (the orchestrator's ruling of 2026-11-12T19:51:09Z): implemented with its owed failing-first test and its restart null control.

Alternatives. Keeping the time-share in `_share` and passing the coordinator to the reader: `tools/audit/archscore/score.py --diff` read that as `coord_footprint` 2506 -> 2517, refused by the gate, and it kept learned decisions in a coordinator-handed function. Putting the order latch on `ArbiterState`: the approved design keeps learned state off the arbiter's record. Voiding the store by a separate `duty_switch` call in the reset: that is a parallel path beside `_FACTORY_VOID`, and the undo would not restore it.

## Head

29370fdbb59aeb18da82ebe9612e7c036e9dc29c, on `handoff/r10-duty-switch-restart-learning-pr-b-p2`, built on part 1 (`handoff/r10-duty-switch-restart-learning-pr-b` at 6b9e873394a02ec82ec24d23dc454a99418e2366) merged with main at 4145f2852642fd0b5ccb8b7af60d41e896a5eea3.

## Mutation proof

Each mutant applied alone, then `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_duty_switch_section.py`, restored after (70 section checks at the head):

- `split` order: space first whenever hot water to space is usable (`"dhw_space" in usable`): 6 fail, among them "null control, an empty learner…", "the first duty keeps the whole step only when…", "the split is latched per step…", "a record whose store is not read yet…" and "with the whole-step rule active…" (with both directions usable, space now goes first).
- `split` order: space first where only space to hot water is usable: 2 fail, "where only hot water to space is usable the both step serves space first…" and "the split reads the latches and nothing published…".
- The next-step condition dropped: 1 fails, "the first duty keeps the whole step only when…".
- The off time dropped from the whole-step bound: 5 fail.
- The whole-step bound made inclusive (`<=`): 1 fails, "the first duty keeps the whole step only when…" (its 150 s row sits on the bound).
- The ceiling at booking dropped (`scale = 1.0`): 1 fails, "n has a ceiling…".
- The share's end made inclusive (`<=`): 1 fails, "on the bounds…".
- A censored direction counting one second off (`or 1.0`): 1 fails, "on the bounds…".
- The ceiling on decay dropped: 1 fails, "n has a ceiling…" (the record stored over the cap).
- `both_step_duty` ignoring `whole`: 5 fail.
- An unloaded record latching: 1 fails, "a record whose store is not read yet splits as today and latches nothing…".
- The latch decided on every read: 2 fail, "the split is latched per step…" and "null control, an empty learner…".
- `("duty_switch", None)` dropped from `_FACTORY_VOID`, then the factory-reset block by `tools/audit/seat/features_block.py` from `from heatpump_optimizer import const as _fr_const` to `R.section("Runtime parameter updates")`, its prelude from `--emit-prelude`: 2 of 32 fail, "a learners reset drops every learned key…" and "a learners reset leaves no stored duty-switch estimate and no latch…".

The reset check was failing first: at the commit before the coordinator change it failed with the stored record and its latch read back after the reset (`after (True, 6.0)`), while its null control (a plain restart keeps both) passed.

## Null control

- Below the threshold and on an install where no switch stops: an empty learner, one at `N_ON - 0.1` with p = 1, and one holding `N_CAP` of kept episodes split as today (`dddddddd` then `sssssss`) and write identical commands, with and without a stop on the install; the flat-price scenario `tests/golden/flat_prices.json` the same, both steps for all three. Non-vacuity: a latched learner splits the same step whole.
- The latch: the re-solved plan and empty learner read from the step's start split as today, where the latched run stays whole.
- Delivery: with the whole-step rule active, room and tank summed over the denied step and the next equal the plan's sum, the next step serving the denied duty whole. Per duty the two steps do not balance: the first duty is served the denied share and the denied duty gets back only its planned next step. This is the ruling's "delivery moves one step", not a per-duty catch-up.
- Factory reset: a plain restart keeps the stored record, its weight and its latch.
- No golden moves and neither claim file is touched.

## Figures

<!-- figure-block: scope-line mb=4145f2852642fd0b5ccb8b7af60d41e896a5eea3 head=29370fdbb59aeb18da82ebe9612e7c036e9dc29c -->
~~~text
MODE: SCOPED -- 22 script(s) run, 11 scoped out.
~~~
<!-- /figure-block -->

- `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_duty_switch_section.py`: all section checks pass at the head; the mutants above as listed.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0000 NULL` at the head; `coord_footprint 2506 -> 2517` WORSENS at the commit where `_share` kept the time-share and the reader took the coordinator, the control.
- `python3 tests/structure.py`: the ratchet passes; `class_excess_loc` read +1 before `_restored_stores`' tuple went back to two lines, paid by that.

## Unpinned sites

Each killed by `MUTANT_CMD` in `prepr.sh` (the section harness, then the factory-reset block), which listed no survivor at this head; each is pinned by `mutation-autofix` once the pull request exists.

- custom_components/heatpump_optimizer/duty_switch.py:193 CLAMP_DROP: the cap on decay; killed by "n has a ceiling…"; pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_switch.py:193 CMP_BOUND: the empty direction's guard; killed by the section (an empty learner divides by zero); pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_switch.py:223 CLAMP_DROP: the cap at booking; killed by "n has a ceiling…"; pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_switch.py:403 GUARD_OFF: the whole-step precondition; killed by "the first duty keeps the whole step only when…"; pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_switch.py:406 CMP_BOUND: the whole-step bound; killed by "the first duty keeps the whole step only when…" (its 150 s row); pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_switch.py:406 RETURN_DEL: the whole-step decision; killed by "the first duty keeps the whole step only when…"; pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_switch.py:551 GUARD_OFF: the unloaded record; killed by "a record whose store is not read yet…"; pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_switch.py:552 GUARD_OFF: the per-step latch; killed by "the split is latched per step…"; pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_switch.py:556 CMP_BOUND: the share's end; killed by "on the bounds…"; pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_switch.py:556 GUARD_OFF: the share's switch; killed by "null control, an empty learner…"; pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_switch.py:558 RETURN_DEL: the second duty's leg; killed by "null control, an empty learner…"; pinned by mutation-autofix

## Red checks

- `tests / mutation`, predicted by `tools/pr/ci_predict.py` in `prepr.sh` at this head: the sites this diff adds in `duty_switch.py` carry no ledger pin yet (each under `## Unpinned sites`, each killed by the checks above), which `mutation-autofix` pins once the pull request exists (`ci-autofix.md`; `--pin-killed` is that job's, not the fixer's). Cheaper detector: `prepr.sh`'s prediction step itself, which ran locally before the handoff and named every site at no standing cost beyond the prepr run; none cheaper exists. The two pins the diff made stale (`Direction.decay` CMP_BOUND 50222946 and `_share` RETURN_DEL 0008eae9, whose lines this diff replaced) are removed here.

## Forward-carry

- R10-DUTY-SWITCH-PLANNER-PRICE's branch (`handoff/r10-duty-switch-planner-price`, unmerged) adds the same `N_CAP` (twice `N_ON`), at booking only, moves `SPLIT_MIN_MINUTES` and the both step's legs into a leaf module of its own, and rewrites the same lines of `_share`. Whichever of the two merges second resolves by one rule. The leg order and the whole-step decision belong in the leg rule the planner prices, fed by `DutySwitchLearner.split`. The cap is held on decay as well as at booking, or a stored record over it stays latched past two half-lives (the mutant "ceiling on decay dropped"). Control: this pull request's section checks "the first duty keeps the whole step only when…" and "n has a ceiling…". Re-measure at that merge's base. Lands in `dev/programme/rosters/wave-r10-groups.json`, that group's carries, on `handoff/audit-r10-roster`. Carry: R10-DUTY-SWITCH-PLANNER-PRICE

## Friction

none
