Roster for round 10, batch 11. It records the roster seat's five ops since #2793 (merged `f40142d66`): a set-after adding R10-UPDATE-PR-SIGNALS to R10-FLOW-ROSTER-FREEZE; a carry on R10-FLOW-ROSTER-FREEZE (the #2792 review's mutant R1); a carry on R10-ORCH-BEATD (arm (a), the standing roster seat's retirement); the carry on R10-MERGE-SUBJECT-CASEARM from the #2697 r8 verdict; and a set-after on R10-ORCH-BEATD adding the edge after R10-FLOW-ROSTER-FREEZE that the arm (a) carry already states (coordinator ruling on verdict/2797). Part of #201. It closes nothing by keyword and leaves #201 open.

## Head

The authored head is `2c5b1b612`, the tip of `handoff/audit-r10-roster`. The pull request merges origin/main (`102f74975`) into it. The roster file is the only file these five ops touch; main's copy has the blob `711deb853817`, the same as at `8c9da6653` and `4a18b96b1`, so the merge is clean. Each op is a `roster_edit.py` push whose lint gate printed `TOTAL: 0 error(s)`. The change is one file, `dev/programme/rosters/wave-r10-groups.json`.

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

`git show origin/main:dev/programme/rosters/wave-r10-groups.json | git hash-object --stdin` and the same at `8c9da6653` both print `711deb853817afdbe746e7763c327f7cd0f0f156`, so main's roster equals the base of these five ops and nothing main wrote since is overwritten. P97 and P98 were already on main; no op here re-cuts them (the single-line diff in `c6097875c` and `e78d7dedd` is the trailing comma after the old last carry).

## Figures

The 5 ops, by roster SHA: `461550d9a` set-after R10-FLOW-ROSTER-FREEZE (+R10-UPDATE-PR-SIGNALS); `c6097875c` append-carry R10-FLOW-ROSTER-FREEZE (#2792 mutant R1); `e78d7dedd` append-carry R10-ORCH-BEATD (arm (a) retirement); `f57b6d52e` append-carry R10-MERGE-SUBJECT-CASEARM (read back: n_carry=1, exact match, 469 of 469); `2c5b1b612` set-after R10-ORCH-BEATD (after is now R10-ORCH-DISPATCH-REG, R10-POLICY-FIXER-MD, R10-ORCH-REVIEW-PACKET, R10-FLOW-ROSTER-FREEZE, read back from the pushed roster).

Measured by loading the roster at origin/main and at `2c5b1b612` as JSON and comparing groups by id: 189 then 189 groups, none removed, none new, 3 changed (R10-FLOW-ROSTER-FREEZE, R10-ORCH-BEATD, R10-MERGE-SUBJECT-CASEARM). Groups by `resume.stage` are unchanged: done 115, in-progress 12, not-started 50, queued 6, carries-open 5, absorbed 1.

## Red checks

Not read by this seat for this body; this pull request changes only the roster JSON, which no red check on main reads. The orchestrator reads main's check-runs.

## Forward-carry

none

## Friction

none
