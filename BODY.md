Triage batch 200 rules P626 (queue line 304), 2026-11-11. It holds one ruling.

- **P626, ACCEPT: R10-RCA-PUSHER-CENSUS-ESCAPE countermeasure C1, as the new group R10-INTRODUCED-REDS-BARRIER (M, opus).**
  - The review packet and `merge_train.py classify` list each `instrument-self-tests` step that is red at the head and not at the base as an introduced red, which the reviewer blocks on. Inherited reds stay unowed, as the 2026-11-07 ruling holds.
  - The RCA's demo and null pair were re-run: #3425's head against main gives 4 introduced steps and rc 1; the null pair gives 0 and rc 0. The 3.7-day window and its 3 instances check out.
  - It is a new group because no live group owns the seam. R10-GATE-DEFER-BARRIER is a different class, has 7 carries and waits on R10-TICK-RESIDUE.
  - In the same group: the stale `governance.yml` comment, a `bugclasses.json` key, sentences in `fix-review.md` and `defect-root-cause.md`, and the RCA document. That PR is policy, and it merges on the mandate approval.

The diff is one file against the merge base: `dev/programme/triage/s6-batch200.md`, the ruling. No product behaviour changes.

## Head

`20439b037235258fd6c1bd03243ee6ee9f765831`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P626 as ACCEPT, and a citation of it passes (`None`).
- With P626's verdict text flipped, the citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P627 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat 60413046e3...20439b037235258fd6c1bd03243ee6ee9f765831`: 1 file, 81 insertions, 1 commit. `tests/layout.py --guard`: 0 refusals.
- The figures come from:
  - the roster at `b679c2850b`;
  - the RCA's step-conclusion JSON for jobs 130479299736, 130415622883 and 130402966157, re-run through its probe;
  - `git show -s 234ff52c75` and `gh pr view 3361` for the window.

## Red checks

none

## Forward-carry

none

## Friction

none
