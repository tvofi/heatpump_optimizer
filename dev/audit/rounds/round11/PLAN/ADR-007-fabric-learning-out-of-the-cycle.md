# ADR-007: the fabric learners leave the coordinator, and the round's footprint is paid there

Group: `R11-ARCH-fabric-learner`, a refactor group with no finding. The shape
is not fixed here: `designer.md` is dispatched for it.

## Context

`COMPONENTS.md` lists the learners seam as owning every parameter fitted from
observed intervals. The house heat-loss scale, the buffer cooling rate and the
internal-gains fold are fitted inside the coordinator class
(`_async_learn_house_heat_loss`, `_async_learn_buffer_cooling`,
`_fold_internal_gains`, `_reanchor_house_heat_loss_scale` and four helpers),
with their constants at module level in `coordinator.py`.

`coord_footprint` reads six statements above the fork on main already
(`score.py --diff` over the merge of #3678 reads 2496 to 2502, explained in
that PR). Every group of this plan whose hot files name `coordinator.py`
fixes behaviour there, and a fix adds statements. End-to-end admissibility needs the metric at or below
its fork value at the stamp.

## Decision

1. The three fabric learners move to a module of the learners seam as objects
   that are handed interval values (temperatures, elapsed time, the freeze
   answer of ADR-008) and return the new parameter; the coordinator keeps the
   call, the publish and the store write.
2. The group runs after `R11-SEAM-learners`, which fixes which intervals these
   folds may ingest (D7-s2-01, D2-s3-08, D2-s3-09): the predicate's final
   owner is the prerequisite.
3. Every other group touching `coordinator.py` is footprint-neutral in its
   own PR where the fix has an owning module to land in; a rise it cannot
   avoid is explained in its body and counted against this group's fall.
4. The orchestrator re-reads `score.py --diff <fork> origin/main` after each
   coordinator merge. If the designer's cut cannot bring `coord_footprint`
   under its fork value with the rises merged by then, the plan returns to the
   owner with the options; the target is not declared met.

## Alternatives

- Module-level functions in `coordinator.py` handed the coordinator: the
  footprint charges every function handed it; nothing moves.
- A mixin or a subclass: C4 measures the whole class hierarchy.
- Packing statements: C25 reads each packed statement as its plain ones.
- No payback group, neutrality by rule alone: one unavoidable rise makes the
  round inadmissible with no move left to answer it.

## Consequences

- `max_class_loc`, `class_excess_loc` and `coordinator_attrs` in
  `tests/structure.py` fall and are re-recorded downward in the PR.
- The stored documents of the three learners keep their keys and versions;
  `store.DOMAINS` is unchanged. A changed key is a migration, out of scope.
- Value-bearing golden fixtures must stay byte-identical: the move changes
  no arithmetic and no order of operations.

## Evidence and scenario

Prediction, no prototype: the eight methods hold 151 AST statements at the
fork (`ast.walk` over `coordinator.py:5461-5864` and `:9413-9453`); about 100
are expected to leave the charged set once the folds take values. Scenario
served: maintainability, second scenario (S13, T13) and physical sanity,
third scenario (S8).

## Move and fitness functions

`coord_footprint` down by about 100 statements; `coordinator_multiassigned_attrs`
may fall and is named. Acceptance: the learner harnesses of D2 s3 and D7 s2
(`m3_learner_freeze.py`) read the same values before and after; `tests/golden/`
byte-identical; `params_over_10` does not rise (the new entry points take a
value object, not eleven arguments; C11); `seam_cut_total` not above budget;
mutation kill rate on the new module not below the fork's package rate.
