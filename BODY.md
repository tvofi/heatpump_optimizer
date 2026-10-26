Roster for round 10, batch 18, at the roster tip `78d071da88f05099677c44c2ce089ea9c4fda6fe`: the nine roster commits the roster seat made on `handoff/audit-r10-roster` after `c22e7b2e13fa0d04549f12431fc34a7bd83cc7ff` (the head of batch 17, which is on main as #2850, merge `11b7a9d739db46a5a62e9f9cf01a8f527a974137`), listed by command under Figures. They are one `set-stage` op (R10-PROOF-CODEQL to done), seven `append-carry` ops (R10-TRAIN-OVERLAP-GRADE four, R10-FLOW-DESIGN-STAGES two, R10-ORCH-BEATD one) and one `append-group` op (R10-RCA-RATELIMIT-RECUR, kind rca, resume stage in-progress, its fixer already dispatched). Part of #201. It closes nothing by keyword and leaves #201 open.

**Merge order: none.** Batch 17 is on main. Roster queue lines 372 to 380 are in this batch.

**Ordering note:** the `append-carry` op for R10-ORCH-BEATD (35be2daa9, queue line 377) was pushed by the previous roster seat's runner just before it was stopped for the batch 17 hold, and was not reported at the time; the roster seat read it back from the handoff tree (carry index 25 of 26, text equal to the queue file's) and did not apply it twice. Queue lines 378 to 380 were applied after #2850 merged.

## Head

The authored head is `78d071da88f05099677c44c2ce089ea9c4fda6fe`, the tip of `handoff/audit-r10-roster`; its merge base with origin/main is `c22e7b2e13fa0d04549f12431fc34a7bd83cc7ff`, and the pull request merges origin/main (`11b7a9d739db46a5a62e9f9cf01a8f527a974137`) into it. `git merge-tree --write-tree origin/main 78d071da88f05099677c44c2ce089ea9c4fda6fe` prints the tree `ac375ff63fb32ae73847856040eb7f60dee9f637` and no conflict. The only file these ops touch is `dev/programme/rosters/wave-r10-groups.json`, the pull request's own delivery row apart. `git diff --stat origin/main ac375ff63fb32ae73847856040eb7f60dee9f637` prints:

```
 dev/programme/rosters/wave-r10-groups.json | 57 +++++++++++++++++++++++++++---
 1 file changed, 53 insertions(+), 4 deletions(-)
```

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

The blob hashes come from `git show <ref>:dev/programme/rosters/wave-r10-groups.json | git hash-object --stdin`: main prints `679a4be14bcd0908d590cbdd8fa36872c7e72c7b` and the merged tree prints `837833ae2a684a567dce1be473b6e5858b38befb`. A script that loads both files as JSON and keys groups by their `group` field printed:

```
groups main 196 head 197 added ['R10-RCA-RATELIMIT-RECUR'] removed []
R10-FLOW-DESIGN-STAGES carry 17->19
R10-TRAIN-OVERLAP-GRADE carry 11->15
R10-ORCH-BEATD carry 25->26
R10-PROOF-CODEQL resume.stage queued->done
```

Exactly the four groups that differ are the ones the nine ops name, one added and three carry-extended and one stage-set, and nothing else moved. `node tools/policy/brief_lint.mjs` was run on `git archive` extracts of origin/main and of the merged tree, each given a fresh `git init`: both print `TOTAL: 10 error(s) across 48 file(s)`, so the delta is zero.

## Figures

`git log --no-merges --reverse --format='%h %s' c22e7b2e13fa0d04549f12431fc34a7bd83cc7ff..78d071da88f05099677c44c2ce089ea9c4fda6fe -- dev/programme/rosters/` prints nine commits, oldest first, tool name dropped:

```
466c345df set-stage R10-PROOF-CODEQL
5d17ebe7d append-carry R10-TRAIN-OVERLAP-GRADE
b416158d0 append-carry R10-FLOW-DESIGN-STAGES
42cc77736 append-carry R10-FLOW-DESIGN-STAGES
492882021 append-carry R10-TRAIN-OVERLAP-GRADE
35be2daa9 append-carry R10-ORCH-BEATD
82dda60af append-carry R10-TRAIN-OVERLAP-GRADE
789feaaa7 append-carry R10-TRAIN-OVERLAP-GRADE
78d071da8 append-group R10-RCA-RATELIMIT-RECUR
```

The per-group counts above come from the script named under Null control.

## Red checks

Not read by this seat for this body; this pull request changes only the roster JSON and its delivery row. The orchestrator reads the check-runs.

## Forward-carry

none

## Friction

none
