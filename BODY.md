Roster for round 10, batch 15, at the roster tip `d49603ff8cf154a13186933897fd05f60361a8ed`: the 52 roster commits the roster seat made on `handoff/audit-r10-roster` after `709ee1929fc7e6673d167fef9e47d82528d4a68e` (the head of batch 14, #2823, which is on main), listed by command under Figures. They are: 43 `append-carry` ops (the largest runs on R10-FLOW-DESIGN-STAGES, R10-ORCH-ROSTER-SCHEMA, R10-ORCH-DISPATCH-REG and R10-ROUND-PLAYBOOK), three `append-group` ops (R10-PROOF-CODEQL, R10-996-RUNNER-CLAIMS, R10-ARCH-SHAPES-CLASSIFIER), three `drop-carry` ops on R10-FLOW-MQ-PROBE, one `set-after` on R10-FLOW-RECORD-PITCH, and two `set-stage` ops: R10-FLOW-MQ-PROBE to done and R10-PARAMS-OWNER to done (its #2817 merged at `5261ba84`). Part of #201. It closes nothing by keyword and leaves #201 open.

**Merge order: none.** The roster file's earlier batches, through #2823, are on main. Roster queue lines up to 354 are in this batch.

## Head

The authored head is `d49603ff8cf154a13186933897fd05f60361a8ed`, the tip of `handoff/audit-r10-roster`; its merge base with origin/main is `709ee1929fc7e6673d167fef9e47d82528d4a68e`, and the pull request merges origin/main (`5261ba84139d9459465ccd842b61b04c2b1329d8`) into it, with `git merge-tree --write-tree origin/main d49603ff8cf154a13186933897fd05f60361a8ed` printing the tree `9ebb6bae9e45bbe322326bf48e1c0425651e8d8e` and no conflict. The only file these ops touch is `dev/programme/rosters/wave-r10-groups.json`; the pull request's own delivery row apart. `git diff --stat origin/main 9ebb6bae9e45bbe322326bf48e1c0425651e8d8e` prints:

```
 dev/programme/rosters/wave-r10-groups.json | 223 +++++++++++++++++++++++++----
 1 file changed, 196 insertions(+), 27 deletions(-)
```

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

The blob hashes come from `git show <ref>:dev/programme/rosters/wave-r10-groups.json | git hash-object --stdin`: main prints `bdc22109539294e43f26872fb0d8579c4f473219` and the merged tree prints `6c8e6f46ebc63c8cf352392c77944628ae9e8b0e`. The group figures come from a script that loads both roster files as JSON and keys groups by their `group` field; its output, pasted unedited:

```
groups main 192 head 195 removed [] new ['R10-PROOF-CODEQL', 'R10-996-RUNNER-CLAIMS', 'R10-ARCH-SHAPES-CLASSIFIER']
changed 20
  R10-ADVISOR-RESIDUE ['carry'] carry 9->11
  R10-CI-LAYOUT-P2 ['carry'] carry 19->20
  R10-CLOSEOUT-CLEANUP ['carry'] carry 1->2
  R10-FLOW-BODY-ONLY ['carry'] carry 9->10
  R10-FLOW-DESIGN-STAGES ['carry'] carry 12->17
  R10-FLOW-MQ-PROBE ['carry', 'resume'] carry 3->0
  R10-FLOW-RECORD-PITCH ['after', 'carry'] carry 7->10
  R10-FLOW-TOOLKIT-MODEL ['carry'] carry 7->8
  R10-FLY-CARRY-DOC-CONTEXT ['carry'] carry 1->3
  R10-FLY-OPENPR-ATOMIC ['carry'] carry 9->11
  R10-FLY-ROW-HEAD-CARRY ['carry'] carry 1->3
  R10-ORCH-DISPATCH-REG ['carry'] carry 10->15
  R10-ORCH-LEDGER ['carry'] carry 13->15
  R10-ORCH-REVIEW-PACKET ['carry'] carry 3->4
  R10-ORCH-ROSTER-SCHEMA ['carry'] carry 17->21
  R10-PARAMS-OWNER ['resume']
  R10-RCA-HEADMOVED ['carry'] carry 1->2
  R10-ROUND-PLAYBOOK ['carry'] carry 1->7
  R10-TRAIN-OVERLAP-GRADE ['carry'] carry 8->11
  R10-UPDATE-PR-SIGNALS ['carry'] carry 5->6
stages main {'absorbed': 4, 'carries-open': 5, 'done': 121, 'in-progress': 8, 'not-started': 46, 'queued': 8}
stages head {'absorbed': 4, 'carries-open': 5, 'done': 123, 'in-progress': 7, 'not-started': 45, 'queued': 11}
```

`node tools/policy/brief_lint.mjs` on the merged tree prints `TOTAL: 0 error(s) across 48 file(s)`. The stage counts agree with the ops: done rises by two (R10-PARAMS-OWNER from in-progress, R10-FLOW-MQ-PROBE from not-started) and queued rises by the three new groups.

## Figures

`git log --no-merges --reverse --format='%h %s' 709ee1929fc7e6673d167fef9e47d82528d4a68e..d49603ff8cf154a13186933897fd05f60361a8ed -- dev/programme/rosters/` prints 52 commits, oldest first, tool path and tool name dropped:

```
e8b692b0f append-carry R10-FLOW-RECORD-PITCH
23b0a4cbc set-after R10-FLOW-RECORD-PITCH
c5b71ebe8 append-carry R10-ROUND-PLAYBOOK
63d8938eb append-carry R10-FLOW-RECORD-PITCH
362a47062 append-group R10-PROOF-CODEQL
632ce575b append-carry R10-FLY-CARRY-DOC-CONTEXT
283b24abd append-carry R10-ORCH-ROSTER-SCHEMA
b152ce8e1 append-carry R10-FLY-OPENPR-ATOMIC
3ad414423 append-carry R10-FLOW-DESIGN-STAGES
e5d35f421 append-carry R10-ORCH-DISPATCH-REG
a0e47a55b append-carry R10-FLOW-DESIGN-STAGES
4067e63ff append-carry R10-TRAIN-OVERLAP-GRADE
f9467b704 append-carry R10-ORCH-ROSTER-SCHEMA
7096e9c51 append-carry R10-FLOW-TOOLKIT-MODEL
647b22f78 append-carry R10-ORCH-LEDGER
64a242042 append-carry R10-FLOW-DESIGN-STAGES
87685b81e append-carry R10-ORCH-ROSTER-SCHEMA
3e02edbef append-carry R10-ORCH-DISPATCH-REG
940245170 append-carry R10-ORCH-REVIEW-PACKET
f5d3478aa append-carry R10-ORCH-DISPATCH-REG
6fe16e66c append-carry R10-ORCH-LEDGER
ad257341b append-carry R10-ORCH-DISPATCH-REG
07fb78581 append-carry R10-ORCH-ROSTER-SCHEMA
048706d6e append-carry R10-ORCH-DISPATCH-REG
ea2de744e append-carry R10-CLOSEOUT-CLEANUP
05a6870ac append-carry R10-ROUND-PLAYBOOK
d3f9a3ade append-carry R10-ROUND-PLAYBOOK
0d89a0e5d append-carry R10-ROUND-PLAYBOOK
b4535b9ab drop-carry R10-FLOW-MQ-PROBE
1f647d21e drop-carry R10-FLOW-MQ-PROBE
60b405dbc drop-carry R10-FLOW-MQ-PROBE
5caa24d5b set-stage R10-FLOW-MQ-PROBE
ff73617e7 append-carry R10-RCA-HEADMOVED
b3c12fdee append-carry R10-CI-LAYOUT-P2
5748f6e23 append-carry R10-FLOW-RECORD-PITCH
e2f93d8f0 append-carry R10-FLOW-BODY-ONLY
525e3260a append-carry R10-FLY-ROW-HEAD-CARRY
6e90528a4 append-carry R10-FLY-CARRY-DOC-CONTEXT
32ffe43c0 append-carry R10-TRAIN-OVERLAP-GRADE
12dddd429 append-carry R10-ROUND-PLAYBOOK
2b7fe35c6 append-carry R10-ROUND-PLAYBOOK
86da909ee append-carry R10-ADVISOR-RESIDUE
af7a2ee20 append-group R10-996-RUNNER-CLAIMS
12993ed8c append-group R10-ARCH-SHAPES-CLASSIFIER
0d81adc14 append-carry R10-FLOW-DESIGN-STAGES
8449d8686 append-carry R10-ADVISOR-RESIDUE
8e6f82c9e append-carry R10-FLY-OPENPR-ATOMIC
7ee1d5b30 append-carry R10-FLOW-DESIGN-STAGES
7a9c6b603 append-carry R10-UPDATE-PR-SIGNALS
f176e044b append-carry R10-TRAIN-OVERLAP-GRADE
6073f1668 append-carry R10-FLY-ROW-HEAD-CARRY
d49603ff8 set-stage R10-PARAMS-OWNER
```

The three new groups are `362a47062` (R10-PROOF-CODEQL, a train batch proof analyzing every CodeQL leg, triage ruling P158 in PR #2829), `af7a2ee20` (R10-996-RUNNER-CLAIMS, reopening the claim-grammar decision of issue #996) and `12993ed8c` (R10-ARCH-SHAPES-CLASSIFIER, split from R10-ARCH-SHAPES at its round 4 under the three-round rule, with `after` on R10-996-RUNNER-CLAIMS and R10-ARCH-SHAPES). `23b0a4cbc` is the one `set-after` op, on R10-FLOW-RECORD-PITCH. `b4535b9ab`, `1f647d21e` and `60b405dbc` drop the three open carries on R10-FLOW-MQ-PROBE and `5caa24d5b` sets it done, so its carry list is empty at the tip (3 to 0 above). `d49603ff8` sets R10-PARAMS-OWNER done after #2817 merged at `5261ba84`. The other 43 commits each append one carry to the group they name; the per-group carry counts above are the net figures.

## Red checks

Not read by this seat for this body; this pull request changes only the roster JSON and its delivery row. The orchestrator reads the check-runs.

## Forward-carry

none

## Friction

none
