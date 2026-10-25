Roster for round 10, batch 12. It records the roster seat's four ops after `2c5b1b612`, the tip #2797 carries: a brief re-pin on R10-IMMERSION-LATCH, R10-CONFIG-NOTICES set done at #2762, and the #2798 precondition carry on R10-MERGE-SUBJECT-HARDEN and on R10-MERGE-SUBJECT-CASEARM. Part of #201. It closes nothing by keyword and leaves #201 open.

## Head

The authored head is `00ceb9aa4`, the tip of `handoff/audit-r10-roster`. This branch also holds #2797's five ops (`461550d9a` to `2c5b1b612`), which are not in this batch. #2797 is open at `19674e803`, verdicted MERGE, so until it merges this pull request's diff against main carries those five ops as well; after it merges the diff is the four below. The pull request merges origin/main (`de794b537`) into the head. The roster file is the only file the ops touch, and main's copy has the blob `711deb853817`, the same as at `8c9da6653`, so the merge is clean. Each op is a `roster_edit.py` push whose lint gate printed `TOTAL: 0 error(s)`. The change is one file, `dev/programme/rosters/wave-r10-groups.json`.

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

`git show origin/main:dev/programme/rosters/wave-r10-groups.json | git hash-object --stdin` prints `711deb853817afdbe746e7763c327f7cd0f0f156`, the blob at `8c9da6653` that both batches build on, so nothing main wrote since is overwritten. Before the re-pin, `node tools/policy/brief_lint.mjs` on main's own unmodified roster at `de794b537` printed `TOTAL: 2 error(s)`, both in the R10-IMMERSION-LATCH brief; after, each op's gate printed 0.

## Figures

The 4 ops, by roster SHA: `5f94b943b` edit-brief R10-IMMERSION-LATCH ("line shift after #2762; pins only"): coordinator.py:8860-8919 became 8761-8820 (holds `def _detect_immersion` and `max_electrical_power`) and coordinator.py:10221-10235 became 10122-10136 (the immersion_excess block in `_accumulate_energy`), both a 99-line shift, each range checked in source, no other word changed (read back byte-equal to the edited text); `fe2648fe7` set-stage R10-CONFIG-NOTICES done at `de794b53765388da42b2b5f22da455ccfe3fe912` (#2762), its next_step left as it was; `3cd2bab6a` append-carry R10-MERGE-SUBJECT-HARDEN and `00ceb9aa4` append-carry R10-MERGE-SUBJECT-CASEARM, the #2798 precondition control text (read back: n_carry 5 and 2, exact match, 434 of 434 each).

Measured by loading the roster as JSON at `2c5b1b612` and at `00ceb9aa4` and comparing groups by id: 189 then 189 groups, none removed, none new, 4 changed (R10-IMMERSION-LATCH, R10-CONFIG-NOTICES, R10-MERGE-SUBJECT-HARDEN, R10-MERGE-SUBJECT-CASEARM). Groups by `resume.stage`, before then after: done 115 then 116, in-progress 12 then 11, others unchanged (not-started 50, queued 6, carries-open 5, absorbed 1).

## Red checks

Not read by this seat for this body; this pull request changes only the roster JSON. Its re-pin clears the brief_lint red on main's roster. The orchestrator reads main's check-runs.

## Forward-carry

none

## Friction

none
