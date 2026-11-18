# ADR-007: the fabric learners leave the coordinator, and the round's footprint is paid there

Group: `R11-ARCH-fabric-learner`, a refactor group with no finding. The shape
is not fixed here: `designer.md` is dispatched for it.

**What this ADR is for.** Its driver is the round's admissibility: the
coordinator's footprint must end at or below the fork's, main is already
above it, and this move is the only one that pays. The seam argument below is
why the payment is taken here and not elsewhere; it is not why the group
exists. The number that decides whether the payment is enough, the fall `F`
of the whole cut, is not in this ADR. It is owed with the design.

## Context

`COMPONENTS.md` lists the learners seam as owning every parameter fitted from
observed intervals. The house heat-loss scale, the buffer cooling rate and the
internal-gains fold are fitted inside the coordinator class. Thirteen methods
carry them, at `coordinator.py:5461-5864` and `:9413-9453` at the fork:

| method | part |
|---|---|
| `_async_learn_buffer_cooling` | the buffer fold: gates, the decay estimate, the envelope step |
| `_async_learn_house_heat_loss` | the house fold: gates, the replay, the residual, the Newton step |
| `_fold_internal_gains` | the hourly gains fold |
| `_reanchor_house_heat_loss_scale` | re-expressing the learned scale against a changed nameplate |
| `_close_fabric_interval` | the baseline both folds share |
| `_buffer_cooling_bounds`, `_house_heat_loss_anchor`, `_heat_loss_anchors` | values the folds read |
| `_apply_buffer_cooling_rate`, `_apply_house_heat_loss_scale`, `_apply_lower_floor_loss_ratio` | the apply into the model |
| `_void_heat_loss_learners`, `async_reset_heat_loss_learners` | reset |

The first eight are the ones the design moves or empties. The last five are
the coordinator's side of the contract (apply, reset) and stay.

`coord_footprint` reads nine statements above the fork on main already, at
`f567988b51`: `score.py --diff` over the merge of #3678 reads 2496 to 2502
and over #3662 reads 2502 to 2505, each explained in its PR, and
`plan_audit.py end-to-end --fork <fork> --head origin/main` reads
`coord_footprint` -0.0052. Both are product merges; none of this plan's
groups has merged. Fourteen groups of this plan name `coordinator.py`, and a
fix adds statements. End-to-end admissibility needs the metric at or below
its fork value at the stamp.

## Decision

1. The folds move to a module of the learners seam as functions or objects
   that are handed interval values (temperatures, elapsed time, the freeze
   answer of ADR-008) and return the new parameter; the coordinator keeps the
   call, the publish and the store write.
2. The group runs after `R11-SEAM-learners`, which fixes which intervals these
   folds may ingest and their arithmetic (D7-s2-01, D2-s3-08, D2-s3-09,
   D2-s3-11): the code is moved once, after it is right.
3. Every other group touching `coordinator.py` is footprint-neutral in its
   own PR where the fix has an owning module to land in; a rise it cannot
   avoid is explained in its body and counted against this group's fall.
4. **The budget.** The stamp reads `2496 + R - 6 - F`: `R` is every
   statement any merge has added since the fork, the six are ADR-004's
   payment (`prototypes.py --only circ`) and `F` is this group's fall. The
   round is admissible on this metric only while `R <= 6 + F`. `F` is
   measured at 28 for two of the folds (below), so the budget for `R` is 34
   statements until the designer's note carries a larger measured `F`. `R`
   stands at 9 before this plan's first merge.
5. The orchestrator re-reads `plan_audit.py end-to-end --fork <fork> --head
   origin/main` after each coordinator merge and keeps the running `R`. When
   `R` passes 26, or the designer's measured `F` leaves `6 + F` below the `R`
   merged by then, the plan returns to the owner with the options; the target
   is not declared met.
6. The group is not last on `coordinator.py`. Its position is the
   projection's (`PLAN.md`, "Hot-file order"); the budget is read end to end,
   so a rise merged after it counts the same as one merged before.
7. **This budget pays for one metric.** A rise in any other scored metric or
   gate-only tripwire has no payment in this plan. `PLAN.md`'s neutral rule
   makes such a rise a review block for a group of this roster; this group
   itself may raise none (its fitness functions below).

## Alternatives

- Module-level functions in `coordinator.py` handed the coordinator: the
  footprint charges every function handed it; nothing moves.
- A mixin or a subclass: C4 measures the whole class hierarchy.
- Packing statements: C25 reads each packed statement as its plain ones.
- No payback group, neutrality by rule alone: one unavoidable rise makes the
  round inadmissible with no move left to answer it, and main already holds
  nine.
- Prototyping the house fold and the re-anchor in this plan, so that `F` is
  measured here: the house fold's gates run across two awaits and feed the
  open-window detector between them, so an exact-text arm of it would be a
  design decision made without design review. Left to the designer.

## Consequences

- `max_class_loc`, `class_excess_loc` and `coordinator_attrs` in
  `tests/structure.py` fall and are re-recorded downward in the PR.
- The stored documents of the three learners keep their keys and versions;
  `store.DOMAINS` is unchanged. A changed key is a migration, out of scope.
- Value-bearing golden fixtures must stay byte-identical: the move changes
  no arithmetic and no order of operations.

## Evidence and scenario

Prototype, `prototypes.py --only fabric`: the buffer fold's gate arithmetic
and the gains fold, written as two functions of values in a new module, with
the coordinator keeping the baseline advance, the freeze question, the apply,
the log and the store write. It reads `coord_footprint` 2496 to 2468, 28
statements, and no other metric or tripwire moves.

The bound, `prototypes.py --only ceiling`: all thirteen methods deleted reads
2496 to 2359, 137 statements. That tree is broken and is not a design; it
says no cut of these methods can pay more than 137.

The house fold and the re-anchor are not prototyped. Their arithmetic already
sits in `learner_newton_step` and `reanchor_heat_loss`; what remains in the
class is gates, logging and state, so their fall depends on whether the
design moves the learner's state with it. **The designer's note carries
`prototypes.py`-style readings of its own cut**, as an arm added to that file,
before design review; design review reads `F` from it.

Scenarios: maintainability, second scenario (S13, T13) is the one this move
serves, in its own terms: growth of `coordinator.py` is priced and the class
shrinks. Physical sanity, third scenario (S8) is a constraint on the move and
not a driver: the freeze predicate the folds ask is ADR-008's, and the move
must not change which intervals they ingest. No scenario in `SCENARIOS.md`
states the round's admissibility; that is a condition of the target
(`architect-planner.md`), and it is this ADR's driver.

## What is owed

- The design, by `designer.md`, with a measured `F` for its whole cut. Until
  design review has read it, the plan can state that the round is admissible
  only while `R <= 34`.
- `designer.md` pipelines the designer behind the group's last predecessor,
  `R11-SEAM-learners`. By then most coordinator groups have merged and most
  of `R` is spent. This designer starts in the first wave instead (`PLAN.md`
  open point 4, decided 2026-11-18, orchestrator under mandate, pending owner confirmation), so `F` is measured
  before `R` is spent; the fixer still waits on `R11-SEAM-learners`.

## Move and fitness functions

`coord_footprint` down 28 statements (prototype), up to 137 by the bound;
`coordinator_multiassigned_attrs` may fall and is named. Acceptance: the
learner harnesses of D2 s3 and D7 s2 (`m3_learner_freeze.py`) read the same
values before and after; `tests/golden/` byte-identical; `params_over_10`
does not rise (the new entry points take a value object, not eleven
arguments; C11); `dead_members` and `public_unused` do not rise (the bound's
tree reads them 1 to 21 and 1 to 9: a method left behind with no caller is
the failure this names); `seam_cut_total` not above budget; mutation kill
rate on the new module not below the fork's package rate.
