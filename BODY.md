Roster for round 10, batch 13, re-taken whole at the authored head. It records the roster seat's five commits since #2799 (merged `022d4aaec`, roster tip `54d78f9bb`), listed by command under Figures: an R10-MERGE-SUBJECT-CASEARM carry, a coordinator.py pin re-pin with R10-LEARNER-ETA set done, the roster_sync stage derivation for R10-MUTANT-SKIP, R10-MUTANT-SKIP and R10-FLOW-AUTOTRAIN set done, and the #2712 PIN-DRIVE carry on R10-FLY-LEDGER-SAMPLE. Part of #201. It closes nothing by keyword and leaves #201 open.

## Head

The authored head is `e64be204d8ba3255eb20d6f4df130cba364be0f4`, the tip of `handoff/audit-r10-roster`; the pull request merges origin/main `c29f3089beff847adbdd0ae3dc739f4a071f5756` into it (a clean merge, `git merge-tree --write-tree origin/main HEAD` printed a tree and no conflict). The only file these ops touch is `dev/programme/rosters/wave-r10-groups.json`; the pull request's own delivery row apart. `git diff --stat origin/main <merged tree>` prints:

```
 dev/programme/rosters/wave-r10-groups.json | 24 ++++++++++++++----------
 1 file changed, 14 insertions(+), 10 deletions(-)
```

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

The blob hashes come from `git show <ref>:dev/programme/rosters/wave-r10-groups.json | git hash-object --stdin`: main prints `d3b890726e4c580732d1d257318efe78730a7b34` and the merged tree prints `c3d331ec4ffe0732c1052a3a540311d9decc59ba`. The group figures come from `fig.py`, which loads both roster files as JSON and keys groups by their `group` field; it takes a group as an object holding both `group` and `resume`. Its output, pasted unedited:

```
groups main 189 head 189 removed [] new []
changed 7
  R10-FLOW-AUTOTRAIN ['resume'] stage in-progress->done
  R10-FLY-LEDGER-SAMPLE ['carry'] carry 0->1
  R10-IMMERSION-LATCH ['brief'] 
  R10-LEARNER-DEFAULT ['brief'] 
  R10-LEARNER-ETA ['resume'] stage in-progress->done
  R10-MERGE-SUBJECT-CASEARM ['carry'] carry 2->3
  R10-MUTANT-SKIP ['resume'] stage in-progress->done
stages main {'absorbed': 4, 'carries-open': 5, 'done': 117, 'in-progress': 10, 'not-started': 47, 'queued': 6}
stages head {'absorbed': 4, 'carries-open': 5, 'done': 120, 'in-progress': 7, 'not-started': 47, 'queued': 6}
```

## Figures

`git log --no-merges --reverse --format='%h %s' origin/main..HEAD -- dev/programme/rosters/` prints five commits, oldest first, tool path suffix dropped:

```
dbd592fe4 roster_edit append-carry R10-MERGE-SUBJECT-CASEARM
e96f70d34 roster: re-pin R10-LEARNER-DEFAULT and R10-IMMERSION-LATCH coordinator.py ranges to origin/main 60cd447a0; set-stage R10-LEARNER-ETA done
027c38705 roster_sync: derive stages from pull requests
eaf10309d roster: set-stage R10-MUTANT-SKIP and R10-FLOW-AUTOTRAIN done
e64be204d roster_edit append-carry R10-FLY-LEDGER-SAMPLE
```

Two of the five are `roster_edit` carries; `e96f70d34` is a brief re-pin plus a set-stage, `027c38705` is the stage derivation by `roster_sync.py`, and `eaf10309d` sets two stages. Each push passed the roster lint gate.

## Red checks

Not read by this seat for this body; this pull request changes only the roster JSON and its delivery row. The orchestrator reads the check-runs.

## Forward-carry

none

## Friction

none
