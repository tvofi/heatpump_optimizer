Roster for round 10, batch 17, at the roster tip `c22e7b2e13fa0d04549f12431fc34a7bd83cc7ff`: the eight roster commits the roster seat made on `handoff/audit-r10-roster` after `7d6ff74590e3b331099fb36066e661a6d840ba32` (the head of batch 16, which is on main as #2844, merge `21b45524d8b242c9520c9413966ff7bb26b72c7d`), listed by command under Figures. They are one `append-group` op (R10-HOTFIX-BATCH-ERREXIT), two `append-carry` ops (R10-ORCH-ROSTER-SCHEMA and R10-FLY-ROW-HEAD-CARRY), two `set-resume` ops that rewrite `next_step` on R10-THERMAL-POWER-OPTION and R10-FLOW-RECORD-PITCH, two `wire-issue --field fixes` ops (R10-FLY-CARRY-DISPOSITION takes #2428, R10-CARD-VOICE takes #2506) and one `set-stage` op (R10-DIAG-REDACT to done). Part of #201. It closes nothing by keyword and leaves #201 open.

**Why this batch is cut early, at eight ops:** the new group R10-HOTFIX-BATCH-ERREXIT is the critical-path fix for the nightly batch gate failing under `bash -e`, and that fix's pull request has a group check which reads main's roster, so the group must reach main before or with the hotfix. The orchestrator ruled on 2026-10-26 that this batch is cut as soon as #2844 merged, ahead of the usual eight-to-ten entries.

**Correction to #2844's record text:** the title and the delivery row of #2844 read "5 ops", and nine roster ops landed there (five `append-carry`, one `edit-brief`, three `set-stage`). The delta reviewer dismissed this as record text (probe/rev-2844-35c20883, 26ef56c6a); this body states the true count so the record is not left under-counted.

**Merge order: none.** Batch 16 is on main. Roster queue lines 364 to 371 are in this batch; lines 372 onward ride batch 18.

## Head

The authored head is `c22e7b2e13fa0d04549f12431fc34a7bd83cc7ff`, the tip of `handoff/audit-r10-roster`; its merge base with origin/main is `7d6ff74590e3b331099fb36066e661a6d840ba32`, and the pull request merges origin/main (`0dfc063fa56ef7c5d2b202933792caf87a2ed154`) into it. `git merge-tree --write-tree origin/main c22e7b2e13fa0d04549f12431fc34a7bd83cc7ff` prints the tree `3508b32b38aedc14f64664b8c79552aa6f0ccbf2` and no conflict. The only file these ops touch is `dev/programme/rosters/wave-r10-groups.json`, the pull request's own delivery row apart. `git diff --stat origin/main 3508b32b38aedc14f64664b8c79552aa6f0ccbf2` prints:

```
 dev/programme/rosters/wave-r10-groups.json | 68 +++++++++++++++++++++++++++---
 1 file changed, 61 insertions(+), 7 deletions(-)
```

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

The blob hashes come from `git show <ref>:dev/programme/rosters/wave-r10-groups.json | git hash-object --stdin`: main prints `b21289a28b8139c61ce5f022c8647dd60ce2f5c5` and the merged tree prints `679a4be14bcd0908d590cbdd8fa36872c7e72c7b`. A script that loads both files as JSON and keys groups by their `group` field printed:

```
groups main 195 head 196 added ['R10-HOTFIX-BATCH-ERREXIT'] removed []
R10-CARD-VOICE fixes changed
R10-THERMAL-POWER-OPTION resume.next_step changed
R10-FLOW-RECORD-PITCH resume.next_step changed
R10-FLY-ROW-HEAD-CARRY carry 3->4
R10-FLY-CARRY-DISPOSITION fixes changed
R10-ORCH-ROSTER-SCHEMA carry 21->22
R10-DIAG-REDACT resume.stage not-started->done
```

Exactly the eight groups the eight ops name differ (seven edited, one added), one op each, and nothing else moved. `node tools/policy/brief_lint.mjs` was run on `git archive` extracts of origin/main and of the merged tree, each given a fresh `git init`: both print `TOTAL: 10 error(s) across 48 file(s)`, so the delta is zero.

## Figures

`git log --no-merges --reverse --format='%h %s' 7d6ff74590e3b331099fb36066e661a6d840ba32..c22e7b2e13fa0d04549f12431fc34a7bd83cc7ff -- dev/programme/rosters/` prints eight commits, oldest first, tool name dropped:

```
ec3c75629 set-stage R10-DIAG-REDACT
3662863d2 append-group R10-HOTFIX-BATCH-ERREXIT
2720c93cd set-resume R10-THERMAL-POWER-OPTION
d0a908650 set-resume R10-FLOW-RECORD-PITCH
149b45b95 append-carry R10-ORCH-ROSTER-SCHEMA
d1c9dc98b wire-issue R10-FLY-CARRY-DISPOSITION
8396866d1 append-carry R10-FLY-ROW-HEAD-CARRY
c22e7b2e1 wire-issue R10-CARD-VOICE
```

The per-group counts above come from the script named under Null control.

## Red checks

Not read by this seat for this body; this pull request changes only the roster JSON and its delivery row. The orchestrator reads the check-runs.

## Forward-carry

none

## Friction

none
