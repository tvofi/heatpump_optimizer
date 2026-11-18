# ADR-009: a ratchet row that was blind is repaired at its measured value, after the kernel

Groups: `R11-SEAM-ratchets` (D7-s1-02, D7-s1-03, D14-s2-03) and
`R11-SEAM-ratchet-raise` (D7-s1-01, D7-s1-04).

## Context

Four findings show `tests/structure.py` rows that do not see what they name:
const fan-out through a module binding, a window written twice in one
function, a package import nothing reads, and `coordinator.py`'s lines outside
its class. A fifth shows a barrier in `tests/entities.py` that matches two of
the logger's methods. Repairing a row changes what it reads; adding one
creates a budget at zero headroom (tradeoff T13). The architecture score reads
five of its metrics from `tests/structure.py`.

Two of the five need the owner before a branch is pushed: D7-s1-01's
corrected row reads 4 against a budget of 3, and D7-s1-04's own scope says the
module-span limit is the owner's to choose. The other three need nobody:
`tools/policy/budget_raise_gate.py` reads a new cap as no raise.

## Decision

1. New rows are recorded at the value measured after `R11-SEAM-kernel` has
   merged. The kernel's dead-state part deletes the fourteen unused import
   bindings D7-s1-03 lists and D7-s3-05's dead constants (ADR-001 part 4), so
   the import row is recorded at zero and the const row at what is left.
   `R11-SEAM-ratchets` adds the row and deletes nothing in production.
2. The two owner-gated rows are their own group, `R11-SEAM-ratchet-raise`, so
   the owner's confirmation holds two findings and not the other three. A
   repaired row whose reading rises because the measure was corrected
   (`const_modules_over_50` under D7-s1-01) is a budget raise: the owner's
   explicit confirmation is obtained before the branch is pushed
   (`CLAUDE.md`, rule 2), and the stamp's holdout compare names it with
   `--allow structure:const_modules_over_50`. D7-s1-04's row is recorded at
   the limit the owner states with the same confirmation.
3. The fix leaves unchanged every `tests/structure.py` function the score
   reads: `private_reach_sites`, `coordinator_writers`, `import_cycle_modules`,
   `dead_members` and `duplicate_clones`'s window. D7-s1-02 gets a row of its
   own, keyed by place, beside `duplicate_clones`. Its repair of the score's
   own census (`counters.gapped_clones`) is the scorer: this plan does not
   plan it, and it goes to the round-end proposal triage.
4. Until that repair exists, the in-function copy is refused by review
   (ADR-001's `fold` control).

## Alternatives

- One group for all five: the owner's confirmation for one raise then holds
  three rows that need none.
- The ratchet group deleting the bindings itself: it would join the order on
  six production files, `coordinator.py` among them, for fourteen one-name
  edits the kernel's dead-state part already makes on the same lines.
- Recording the new rows before the kernel: each kernel removal then needs a
  re-record, and a row recorded high is headroom nobody chose.
- Paying D7-s1-01 by narrowing `entry_config.py`'s reads of `const`: the
  module reads its 118 configuration keys because it is their reader; moving
  them would hide the fan-out, not lower it.
- Repairing the score's census in this round: P3 may not plan a scorer edit,
  and the instrument freeze defers it.

## Consequences

- The end-to-end reading and the holdout compare run both sides on the fork's
  instrument (`plan_audit.py snapshot --instrument <fork>`), so a row repaired
  in this round cannot move the round's own reading.
- From `R11-SEAM-ratchet-raise`'s merge, a fix that grows `coordinator.py`
  outside the class is priced.
- The edge from the kernel is the weakest in the roster: it is the same pair
  as a file order on `tests/structure_budgets.json`, and it is an edge only
  because the recorded value depends on what the kernel removed. If the
  kernel's dead-state part merges alone, the edge is satisfied by that part.

## Scenarios served

Maintainability, second scenario (S13, T13); test-suite reach, second
scenario (S27, T27); recurring classes, first scenario (S30).

## Move and fitness functions

Score-neutral: no scored metric moves. Acceptance: each finder's perturbation
moves its repaired row (`m1_ratchet_census.py`; `logflood_shape.py` for the
barrier); `tests/arch_score.py` passes unchanged; `score.py --diff` over each
PR reads NULL.
