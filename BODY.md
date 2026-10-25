Roster for round 10, batch 10. It records the roster seat's nine ops since #2787 (head `54f6f50e6`, merged `1aa765fdd`): the P96 (a) and (b) carries, the R10-FLOW-ROSTER-FREEZE resume note, R10-FLY-YIELD-GUARD done (#2765), the new group R10-MERGE-SUBJECT-CASEARM (the #2697 three-round split) and the batch-21 carries P97, P98 and P100 (triage #2790, merged `ab3aade49`). Part of #201. It closes nothing by keyword and leaves #201 open.

## Head

The authored head is `4a18b96b1643be0145f863d5f66eb70fd4c07f07`, the tip of `handoff/audit-r10-roster`: the last op `8c9da6653` plus a merge of `origin/main` `ab3aade49` whose one conflict (the roster file) is resolved to the branch tip, which is byte-identical to `8c9da6653`'s (`cmp` rc 0); `git diff --stat origin/main HEAD` prints that one file. Main's roster file at `ab3aade496371f1da01e96730188e2b0997e5536` has the same blob as `c57fa3768` (`64bf29ca58ca`), the last op #2787 carried, so the diff is exactly the nine ops after it (`git rev-list --count c57fa3768..8c9da6653` prints 9). Each op is a `roster_edit.py` push whose lint gate printed `TOTAL: 0 error(s)`. The change is one file, `dev/programme/rosters/wave-r10-groups.json`.

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

`git show origin/main:dev/programme/rosters/wave-r10-groups.json | git hash-object --stdin` and the same for `c57fa3768:` both print `64bf29ca58cab83d366faef6519c219096c0a7cc`, so main's roster equals the base of these nine ops and nothing main wrote since is overwritten. The `removed` list below is empty.

## Figures

The 9 ops, by roster SHA (`git log --format='%h %s' c57fa3768..8c9da6653` prints them):

- `6a623f81c` append-carry R10-FLOW-POSTMERGE (P96 (a)); `6a0ffc48c` append-carry R10-FLOW-AUTOTRAIN (P96 (b)).
- `1b867726e` and `bcf29986c` set-resume R10-FLOW-ROSTER-FREEZE: the note (arm (b) merged #2779 `c01d54b98`, arm (a) owed as its own PR, six carries ride arm (a)) and next_step "dispatch arm (a) fixer". Stage stays `not-started`.
- `041d307c4` set-stage R10-FLY-YIELD-GUARD done at `8a11b8bdd6bfdca0b5f6bd356638fad2b234525f` (#2765). Its two forward-carries are on R10-ORCH-DISPATCH-REG, the rest in `dev/programme/carries/carry-201.json`.
- `cfb203cab` append-group R10-MERGE-SUBJECT-CASEARM (lane IN, class instrument, size S, after R10-MERGE-SUBJECT-HARDEN, not-started), the orchestrator's three-round split of #2697.
- `afeb76c02`, `9a019e994`, `8c9da6653` append-carry of P97 to R10-ORCH-BEATD, P98 to R10-FLOW-ROSTER-FREEZE (arm (b2), a later opener after arm (a) merges) and P100 to R10-FLY-CARRY-DISPOSITION, each citing `triage: dev/programme/triage/s6-batch21.md#P9x`.

Measured with `B=origin/main`, `H=8c9da6653` (same roster file as the head), `R=dev/programme/rosters/wave-r10-groups.json`, by loading `git show $B:$R` and `git show $H:$R` as JSON and comparing the groups by id: 188 then 189 groups, none removed, 1 new (R10-MERGE-SUBJECT-CASEARM) and 6 changed (R10-FLOW-POSTMERGE, R10-FLOW-ROSTER-FREEZE, R10-FLOW-AUTOTRAIN, R10-FLY-CARRY-DISPOSITION, R10-ORCH-BEATD, R10-FLY-YIELD-GUARD). Groups by `resume.stage`, main then this head: done 114 then 115, in-progress 13 then 12, not-started 49 then 50, queued 6 then 6, carries-open 5 then 5, absorbed 1 then 1. `node tools/policy/brief_lint.mjs` on the roster at `H` is the lint gate each op ran, `TOTAL: 0 error(s)`.

## Red checks

Read 2026-10-25 from `repos/tvofi/heatpump_optimizer/commits/ab3aade496371f1da01e96730188e2b0997e5536/check-runs` (main's tip, 47 runs), failures only: `governance / record` completed `failure` (job 121096360528, run 40169156796, still in progress, so no log yet). Five runs were still in progress. This pull request changes only the roster JSON, which the record job does not read, so it did not cause the failure; the cheaper detector is the record check itself, which already caught it. I did not diagnose the cause; main's red is the orchestrator's to read once the run ends.

## Forward-carry

none

## Friction

none
