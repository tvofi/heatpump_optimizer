# ADR-009: a ratchet row that was blind is repaired at its measured value, after the kernel

Group: `R11-SEAM-tests` (D7-s1-01, D7-s1-02, D7-s1-03, D7-s1-04, D14-s2-03).

## Context

Four findings show `tests/structure.py` rows that do not see what they name:
const fan-out through a module binding, a window written twice in one
function, a package import nothing reads, and `coordinator.py`'s lines outside
its class. Repairing a row changes what it reads; adding one creates a budget
at zero headroom (tradeoff T13). The architecture score reads five of its
metrics from `tests/structure.py`.

## Decision

1. New rows are recorded at the value measured after `R11-SEAM-kernel` has
   merged, since its removals (unused imports, dead state) set those values.
2. A repaired row whose reading rises because the measure was corrected
   (`const_modules_over_50` under D7-s1-01) is a budget raise: the owner's
   explicit confirmation is obtained before the branch is pushed
   (`CLAUDE.md`, rule 2), and the stamp's holdout compare names it with
   `--allow structure:const_modules_over_50`.
3. The fix leaves unchanged every `tests/structure.py` function the score
   reads: `private_reach_sites`, `coordinator_writers`, `import_cycle_modules`,
   `dead_members` and `duplicate_clones`'s window. D7-s1-02's repair of the
   score's own census (`counters.gapped_clones`) is the scorer: this plan does
   not plan it, and it goes to the round-end proposal triage.
4. Until that repair exists, the in-function copy is refused by review
   (ADR-001's `fold` control).

## Alternatives

- Recording the new rows before the kernel: each kernel removal then needs a
  re-record, and a row recorded high is headroom nobody chose.
- Repairing the score's census in this round: P3 may not plan a scorer edit,
  and the instrument freeze defers it.

## Consequences

- The end-to-end reading and the holdout compare run both sides on the fork's
  instrument (`plan_audit.py snapshot --instrument <fork>`), so a row repaired
  in this round cannot move the round's own reading.
- From this group's merge, a fix that grows `coordinator.py` outside the class
  is priced.

## Scenarios served

Maintainability, second scenario (S13, T13).

## Move and fitness functions

Score-neutral: no scored metric moves. Acceptance: each finder's perturbation
moves its repaired row (`m1_ratchet_census.py`); `tests/arch_score.py` passes
unchanged; `score.py --diff` over the PR reads NULL.
