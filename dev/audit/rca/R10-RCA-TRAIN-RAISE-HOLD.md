# R10-RCA-TRAIN-RAISE-HOLD: the train decided a raise by its path, and pre-flight by a second copy

A root-cause seat ran beside the fix, not inside it (`dev/governance/roles/root-cause.md`,
`dev/governance/rules/defect-root-cause.md`). The fix landed in the same pull request
(R10-TRAIN-RAISE-HOLD).

**Trigger.** 2026-10-18: merge trains t11, t12 and t13 each stopped at `approve` on #2401
(head `311e9de3e0`) with `code-owned and a budget file changed (tests/ci_budgets.json): a
raise is the owner's (0013)`. On the same head CI's required `budget-raise-gate` printed
`budget_raises=0` and PASS. #2401 adds four `archscore.*` rows to `tests/ci_budgets.json`
and moves none, and the gate reads a new `max` row as no raise.

## 1. Named cause

Two definitions of one concept, "this pull request is a budget raise", disagreed (class I4):

- `budget_raise_gate.py` (CI) reads the **direction**. `file_raises` compares each budget
  leaf from the merge base to the head, under the file's SCHEMA.
- `merge_train.py`'s `approve` and `queue_pre_flight.py`'s `entry` read the **path**. Any
  changed file ending `_budgets.json` was treated as a raise.

Commit `957633266` (#2305) made the train's owner check (`_owner_at_head`) the gate's own
reading: `approval` plus the gate's `justification` of the body, its mandate judged at the
merge. That was half the port. The guard that decides whether a raise exists at all stayed
the path predicate, and `decide`'s no-raise branch ("no owner review is owed") was not
ported. Three faults followed:

- A head that only adds rows was held to the raise standard and stopped.
- `_owner_at_head` returned `why if ok else None`, so the Stop never printed the gate's
  reason, here the body's missing `Payments tried:` and `Architecture score: dS` lines.
- `queue_pre_flight.budget_gate` kept a second copy of the reading. It called `approval()`
  without `justify` and judged the mandate at review time, so pre-flight PASSED the heads
  that approve then stopped.

## 2. Process state: (c), followed, with the wrong result

The process ran. #2305 had a fix review, a mutation proof and green self-tests, and
`957633266` killed that review's surviving mutants. The defect lived where none of its
arms could reach:

- Every budget world in `merge_train.py`'s self-test (`carry_world`, the code-owned budget
  arm) named `tests/structure_budgets.json` in the diff and held **no blob** at either end.
  "A budget path changed" and "a raise" were therefore the same fact in every fixture, and
  no arm drove a budget change that is not a raise.
- Pre-flight's budget arms reused the path-only fixture. No arm compared its verdict with
  approve's on the same world.

This is the shape `defect-root-cause.md` names: a check half-ported out of its lane. It
is not (b), because no step was skipped. It is not (d), because the gate's direction
reading predates the train's budget arm, so the precondition was false when the arm was
born.

## 3. Cost test

- `cost(defect)`: at least **2.4 h** of PR-wait this session. That counts #2401 across
  t11-t13 and the entries queued behind it, since the train stops at the first refusal.
  The seat counted **8** budget halts this session and **none** was a raise.
- `cost(countermeasure, recurring)`: about **81 ms** per budget entry, the median of 20
  runs of the no-raise arm (one `merge-base`, two `ls-tree`, the changed files' `show`s,
  measured by the seat's timing case). Entries with no budget file pay nothing, because
  the method returns before any read. The self-test arms add a few checks to a self-test
  of about 3.5 minutes.
- `P(recurrence)`: about **0.8** per session. Budget-row PRs recur in every
  archscore-coverage part, and #2373 has the same shape as #2401 (below). Each recurrence
  costs at least **10 min**: one stopped train plus a re-queue.
- 81 ms per entry is far below 0.8 × 10 min, so the countermeasure passes. I4 is also
  `barriered`, and any instance of a barriered class owes the barrier.

## 4. Demonstration

The seat ran its replay (`demo.py` + `cases_all.py`, demo.out sha1 `fa78eecc28a5`)
read-only against live reviews and mandates. The arms are main's approve arm, main's
pre-flight, and the proposed single reader:

| case | main approve | main pre-flight | proposed (`raise_hold`) |
|---|---|---|---|
| #2401, original body (the defect) | STOP; why discarded: body lacks both justification lines | PASS | PASS: no raise, `file_raises`: 0, ordinary path |
| #2401, live body | owner (held) | PASS | PASS: no raise, ordinary path |
| planted raise on #2401 (`hub_solve_writes` 41 -> 42), original body | STOP; why discarded | PASS (divergent) | STOP, naming the raise and both missing lines |
| planted raise, live body | owner (held) | PASS | PASS under mandate 6175172275 |
| planted raise, no owner review | STOP; why discarded | PARK | STOP: no decisive review by the owner |
| null control: #2311, a real raise (38 -> 41), healthy body and review | owner (held) | PASS | PASS under the mandate |
| #2368, a real raise (stress override None -> 6), no review | STOP | PARK | STOP: no decisive review |
| #2373, the #2401 shape, no review | STOP | PARK | PASS: no raise |
| planted raise, body unreadable | -- | -- | fails closed (`gh pr view` exited 1) |

The proposed column is the reading the gate gives on every row. The main columns
disagree with it, and with each other, on four rows.

## 5. Countermeasure and verification

- **The fix** (this pull request): `Train.raise_hold` is the one reader. It calls
  `budget_raise_gate.raises_between`, extracted from `gate()`, which now calls it too.
  `approve` and `queue_pre_flight.entry` both call `raise_hold`, and the Stop or PARK
  carries the gate's `why`.
- **The barrier**: the concept is registered in `tools/policy/agreement.mjs` as
  `budget-raise`. On one corpus it drives the gate's `raises_between` (restored from the
  base in CI) and the train's `raise_hold` (the pull request's copy, the graded
  artifact). The corpus is every tracked budget file under eight edits: same, new-row,
  sibling-row (#2401's shape), bump, unbump, deleted, added and unparsable. With the
  defect planted back (the path decides), 20 of the 56 items diverge and the lane exits
  1; at the fix, 0 diverge. The train's self-test fixtures now carry blobs
  (`RAISE_FIXTURE`, `NEW_ROWS_FIXTURE`), so a budget path and a raise are separate facts
  in every arm.
- **A detector shown to detect**: before the fix, 6 of the new `merge_train.py` arms fail,
  and 7 of 36 pre-flight checks (4 new arms, 3 reworded to approve's step); after it, all
  pass. The per-mutant kills are in `dev/audit/harnesses/r10_train_raise_hold_mutants.sh`,
  and the pull request body carries the run.
