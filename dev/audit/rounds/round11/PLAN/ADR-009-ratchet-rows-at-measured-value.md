# ADR-009: a ratchet row that was blind is repaired at its measured value, after the deletions that set it

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

1. New rows are recorded at the value measured when `R11-SEAM-ratchets`
   merges. `R11-SEAM-dead-state` deletes the fourteen unused import bindings
   D7-s1-03 lists and D7-s3-05's dead constants (ADR-001 part 4); if it
   merges later, its deletions re-record the import row downward to zero.
   `R11-SEAM-ratchets` adds the row and deletes nothing in production. No
   edge leads into the ratchet groups: the edge from `R11-SEAM-dead-state`
   was dropped as an ordering preference (decided 2026-11-18, orchestrator under mandate, pending owner confirmation).
2. The two owner-gated rows are their own group, `R11-SEAM-ratchet-raise`, so
   the owner's confirmation holds two findings and not the other three. A
   repaired row whose reading rises because the measure was corrected
   (`const_modules_over_50` under D7-s1-01) is a budget raise: the owner's
   explicit confirmation is obtained before the branch is pushed
   (`CLAUDE.md`, rule 2). D7-s1-04's row is recorded at the limit the owner
   states with the same confirmation. `R11-SEAM-ratchet-raise` carries no
   edge: D7-s1-04's row moves with every group that edits `coordinator.py`
   and D7-s1-01's with every group that edits `const.py`, so an edge from one
   of them is an ordering preference. Each row is recorded at the value
   measured when the owner confirms it; a later merge that lowers it
   re-records the row downward in its own PR, as any ratchet row is.
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
  edits `R11-SEAM-dead-state` already makes on the same lines.
- Recording the import row before those deletions: it is then recorded at
  fourteen, and a row recorded high is headroom nobody chose.
- An edge from the deletions into `R11-SEAM-ratchet-raise` too (revision 1):
  the two owner-set rows do not read what that group deletes any more than
  what thirteen other groups change. Removed.
- Paying D7-s1-01 by narrowing `entry_config.py`'s reads of `const`: the
  module reads its 118 configuration keys because it is their reader; moving
  them would hide the fan-out, not lower it.
- Repairing the score's census in this round: P3 may not plan a scorer edit,
  and the instrument freeze defers it.

## Consequences

- The end-to-end reading and the holdout compare run both sides on the fork's
  instrument (`plan_audit.py snapshot --instrument <fork>`), so a row repaired
  in this round cannot move the round's own reading. For that reason the
  compare declares no `--allow`: revision 1 declared `--allow
  structure:const_modules_over_50` beside this sentence, and one of the two
  was unnecessary. The fork's `tests/structure.py` reads the row as it read
  it at the fork on both sides.
- From `R11-SEAM-ratchet-raise`'s merge, a fix that grows `coordinator.py`
  outside the class is priced.
- The edge from `R11-SEAM-dead-state` into `R11-SEAM-ratchets` is dropped
  (2026-11-18): the recorded value of one new row depends on what was
  deleted, and a later deletion re-records it downward.

## Scenarios served

Maintainability, second scenario (S13, T13); test-suite reach, second
scenario (S27, T27); recurring classes, first scenario (S30).

## Move and fitness functions

Score-neutral: no scored metric moves. Acceptance: each finder's perturbation
moves its repaired row (`m1_ratchet_census.py`; `logflood_shape.py` for the
barrier); `tests/arch_score.py` passes unchanged; `score.py --diff` over each
PR reads NULL.
