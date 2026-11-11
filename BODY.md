Triage batch 173 rules queue line 269, 2026-11-11. It holds one ruling.

- **P590, ACCEPT, re-pointed: TRAIN-DEFER-WAIT-UNDER-RUN and POLICY-REFUSAL-REVIEW-MISREAD.**
  - The train skipped #3398 as TIMEOUT. Its wait ran out after 24 polls, about 5832 s, while code run 42969771406 took 5863 s and concluded success. The job cap was not the cause: queueing on the critical path was 385 s, against a `tests / mutation` job that ran 5282 s. The ruling therefore rejects the proposal's "count from the run's start".
  - `policy_refusal` collapses same-named rollup contexts. In 66 of 66 lines it named "a review" as the missing requirement while the PR was APPROVED. 8 of those 66 (12.1%) were followed by a deferral read, against a 1.4% base rate and 0 of 9 other park lines.
  - The ruling adds a PART 2 ITEM carry to R10-TRAIN-RESIDUE. A started sibling code run bounds the deferral wait by its own deadline, and `polls` stays the bound otherwise. A same-named deferral `gate` returns `wait`, never "a review".

The diff is one file against the merge base: `dev/programme/triage/s6-batch173.md`, the ruling. No product behaviour changes.

## Head

`2465295835be18b6e55739b3b24fd60f3cfe7ff4`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P590 as ACCEPT, and a citation of it passes (`None`).
- With the verdict flipped to REJECT in the file text, the citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P591 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat e67b79c9fc...2465295835be18b6e55739b3b24fd60f3cfe7ff4`: 1 file, 1 commit.
- The figures come from the merge train's log (lines 19707-19850, and counts over the whole log) and one Actions jobs read of run 42969771406 (41 jobs). Each is cited beside its source in the ruling.

## Red checks

none

## Forward-carry

none

## Friction

none
