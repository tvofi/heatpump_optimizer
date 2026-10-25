Roster for round 10, batch 11. It records the roster seat's four ops since #2793 (merged `f40142d66`): the set-after that adds R10-UPDATE-PR-SIGNALS to R10-FLOW-ROSTER-FREEZE, two carries on R10-FLOW-ROSTER-FREEZE (the P98 text re-cut and the #2792 review's mutant R1), two on R10-ORCH-BEATD (P97 re-cut and the arm (a) retirement note), and the new carry on R10-MERGE-SUBJECT-CASEARM from the #2697 r8 verdict. Part of #201. It closes nothing by keyword and leaves #201 open.

## Head

The authored head is `f57b6d52e`, the tip of `handoff/audit-r10-roster`. The pull request merges origin/main (`102f74975`) into it; the roster file is the only file those four ops touch, and main's copy has the blob `711deb853817`, the same as `8c9da6653` and `4a18b96b1`, so the merge is clean. Each op is a `roster_edit.py` push whose lint gate printed `TOTAL: 0 error(s)`. The change is one file, `dev/programme/rosters/wave-r10-groups.json`.

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

`git show origin/main:dev/programme/rosters/wave-r10-groups.json | git hash-object --stdin` and the same at `8c9da6653` both print `711deb853817afdbe746e7763c327f7cd0f0f156`, so main's roster equals the base of these four ops and nothing main wrote since is overwritten.

## Figures

The 4 ops, by roster SHA (`git log --format='%h %s' 8c9da6653..f57b6d52e` prints them after the one merge `4a18b96b1`): `461550d9a` set-after R10-FLOW-ROSTER-FREEZE; `c6097875c` append-carry R10-FLOW-ROSTER-FREEZE; `e78d7dedd` append-carry R10-ORCH-BEATD; `f57b6d52e` append-carry R10-MERGE-SUBJECT-CASEARM (read back: n_carry=1, exact match, length 469 of 469).

Measured by loading the roster at origin/main and at `f57b6d52e` as JSON and comparing groups by id: 189 then 189 groups, none removed, none new, 3 changed (R10-FLOW-ROSTER-FREEZE, R10-ORCH-BEATD, R10-MERGE-SUBJECT-CASEARM). Groups by `resume.stage`, main then this head: done 115 then 115, in-progress 12 then 12, not-started 50 then 50, queued 6 then 6, carries-open 5 then 5, absorbed 1 then 1.

## Red checks

Not read by this seat for this body; this pull request changes only the roster JSON, which no red check on main reads. The orchestrator reads main's check-runs.

## Forward-carry

none

## Friction

none
