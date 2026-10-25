Roster for round 10, batch 12. It records the roster seat's 57 ops since #2797 (merged `b89fea13e`, roster tip `2c5b1b612`): the R10-IMMERSION-LATCH brief re-pin and carry, the R10-CONFIG-NOTICES done stage, the #2798 precondition carries, the rehome carries and carry drops of the 2026-10-25 hygiene pass, the three consolidation folds (R10-FLY-RECORD-BEAT, R10-FLY-POOL-INSTRUMENT and R10-ROUTING-INVARIANTS each set absorbed), and two carries on R10-ORCH-ROSTER-SCHEMA. Part of #201. It closes nothing by keyword and leaves #201 open.

## Head

The authored head is `a654772a1`, the tip of `handoff/audit-r10-roster`. The pull request merges origin/main (`b89fea13e`) into it. The roster file is the only file these ops touch (`git log --no-merges --format=%h 2c5b1b612..a654772a1` lists them; the delivery row apart). Each op is a `roster_edit.py` push whose lint gate printed `TOTAL: 0 error(s)`. The change is one file, `dev/programme/rosters/wave-r10-groups.json`.

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

`git show 2c5b1b612:dev/programme/rosters/wave-r10-groups.json | git hash-object --stdin` and the same at `origin/main` both print a blob starting `ae5988d3415d`, so main's roster equals the base of these ops and nothing main wrote since is overwritten. Before the IMMERSION-LATCH re-pin, `node tools/policy/brief_lint.mjs` on main's unmodified roster at `de794b537` printed `TOTAL: 2 error(s)`, both in that brief; the re-pin cleared it.

## Figures

By op, from `git log --no-merges --format=%s 2c5b1b612..a654772a1` over the roster file: 20 append-carry, 16 drop-carry, 12 wire-issue, 4 set-stage, 3 set-resume, 1 set-after, 1 edit-brief; 57 in all.

- edit-brief R10-IMMERSION-LATCH (`5f94b943b`, "line shift after #2762; pins only"): coordinator.py:8860-8919 became 8761-8820 and 10221-10235 became 10122-10136, each range checked in source for the cited symbol, no other word changed.
- set-stage R10-CONFIG-NOTICES done at `de794b537` (#2762): `fe2648fe7`.
- The 16 drop-carry ops (`fa2de4493` to `3bbb06c33`) each name one entry by a unique `--match` prefix and dropped it; the pushed commit is the readback.
- Folds: R10-FLY-RECORD-BEAT, R10-FLY-POOL-INSTRUMENT and R10-ROUTING-INVARIANTS are stage absorbed (`2553c1974`, `5993ed9fa`, `eb30e6233`), their carries and issues re-homed to R10-FLOW-POSTMERGE, R10-FLOW-DESIGN-STAGES and R10-ORCH-ROSTER-SCHEMA. R10-ARCH-DOCS's after list (`c4c2a2ed1`) dropped exactly those three: 82 edges to 79, none added.

Measured by loading the roster as JSON at origin/main and at the head and comparing groups by id: 189 then 189 groups, none removed, none new, 27 changed. Groups by `resume.stage`, main then head: done 115 then 116, in-progress 12 then 11, not-started 50 then 47, queued 6 then 6, absorbed 1 then 4, carries-open 5 then 5.

## Red checks

Not read by this seat for this body; this pull request changes only the roster JSON, which no red check on main reads. The orchestrator reads main's check-runs.

## Forward-carry

none

## Friction

`roster_queue.py run` passed a trailing `# comment` on a queue line as arguments to `roster_edit.py` (16 drop-carry ops refused rc=2); I re-ran them with the comments stripped. The orchestrator is routing the tool defect.
