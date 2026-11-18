# ADR-006: where a batch twin is bit-equal by construction, the scalar is its one-row call

Group: `R11-SEAM-money` (D2-s3-06).

## Context

`tariff._exact_topk_sum` sums the k smallest window excesses while
`_plateau_aware_topk_sum_batch` takes the largest (D2-s3-06): a scalar and its
batch twin disagreeing. `_smooth_topk_sum` and `_smooth_topk_sum_batch` are a
second pair, kept equal by a parity grid in `tests/features.py`; the batch's
docstring states a row is the scalar bisection on that row to the bit, through
`batchmath.row_sums`. The pair and `peak_cost_batch` are one clone class.

## Decision

1. The top-k sort rule has one expression; `_exact_topk_sum` takes the
   largest, as the batch does.
2. `_smooth_topk_sum` becomes one row of `_smooth_topk_sum_batch`. The parity
   grid stays as the batch's own regression test against recorded values.
3. This applies only where bit-equality is by construction. The thermal
   model's and the optimizer's scalar and batch twins are not changed: their
   equality is measured on one BLAS build, and a one-row call would move
   solver floats and golden fixtures.

## Alternatives

- The batch running the scalar body per row: `peak_cost_batch`'s docstring
  records that form at 62 % of a winter capacity-tariff solve; refused.
- Leaving both and adding a third agreement test: D2-s3-06 is what an
  agreement test did not catch.

## Consequences

- Tradeoff T1: the scalar path pays array overhead per call. If the D9 solve
  harness regresses, or any value-bearing golden fixture moves, part 2 is
  dropped and recorded; part 1 stands alone.
- Published money changes for a tariff with k above one off a plateau (T7):
  the release notes owe the step first.

## Scenarios served

Physical sanity, second scenario (S7, T7); price optimality (T1).

## Move and fitness functions

`duplication_copies` down one copy (`prototypes.py --only topk`). Acceptance:
`tests/golden/` byte-identical with no claim added; the parity grid's rows
all equal; `tests/stress.py` solve time not above the fork's; D2 s3's harness
for D2-s3-06 reads zero disagreement.
