Roster for round 10, batch 14: the 25 roster commits the roster seat made on `handoff/audit-r10-roster` after `9442cb4ea` (the head of batch 13, #2812, merged as `f54f40cc`), listed by command under Figures. They are: the stage derivations for #2817 and #2819 (`roster_sync.py`) and R10-DEMAND-OVERBOOK done, an R10-ORCH-ROSTER-SCHEMA carry, four `set-after` edges, two `set-stage` ops on R10-UPDATE-PR-SIGNALS, the new group R10-LEGIONELLA-COMPLETION, the R10-HEAT-METER design carries routed to R10-COP-GATE, R10-UX-HEALTH and R10-RATIO-ANCHOR, and the D15 live-bundle leads L1 to L9 as carries on their owning groups. Part of #201. It closes nothing by keyword and leaves #201 open.

**Merge order: none.** The roster file's earlier batches, #2812 and #2813, are on main. Roster queue line 334 and the CLOSEOUT carry wait for #2822, so this batch ends at `9e5f5cf1c`.

## Head

The authored head is `9e5f5cf1c0336ba42981b3ed421d5588b0a9fb5d`, the tip of `handoff/audit-r10-roster`; its merge base with origin/main is `20e9f0219119c89a9840fd6b337387adec3a8ecf`, and the pull request merges origin/main (`dfcd8d9be`, which moved after the handoff) into it, with `git merge-tree --write-tree origin/main 9e5f5cf1c` printing a tree and no conflict. The only file these ops touch is `dev/programme/rosters/wave-r10-groups.json`; the pull request's own delivery row apart. `git diff --stat origin/main <merged tree>` prints:

```
 dev/programme/rosters/wave-r10-groups.json | 111 ++++++++++++++++++++++-------
 1 file changed, 85 insertions(+), 26 deletions(-)
```

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

The blob hashes come from `git show <ref>:dev/programme/rosters/wave-r10-groups.json | git hash-object --stdin`: main prints `b7f33d15eed0b6d23974e784a52ad56382471e66` and the merged tree prints `98bf056affd7635e08facf871657f03030e8c3b0`. The group figures come from a script that loads both roster files as JSON and keys groups by their `group` field; its output, pasted unedited:

```
groups main 190 head 191 removed [] new ['R10-LEGIONELLA-COMPLETION']
changed 18
  R10-ARCH-DOCS ['after'] 
  R10-ARCH-SHAPES ['resume'] 
  R10-BUFFER-STORE ['carry'] carry 2->4
  R10-CLOSEOUT-CLEANUP ['after'] 
  R10-COP-GATE ['carry'] carry 7->10
  R10-DEMAND-OVERBOOK ['resume'] 
  R10-DIAG-REDACT ['carry'] carry 2->3
  R10-FLOW-DESIGN-STAGES ['carry'] carry 11->12
  R10-HEAT-METER ['carry'] carry 10->13
  R10-ORCH-DISPATCH-REG ['after'] 
  R10-ORCH-ROSTER-SCHEMA ['carry'] carry 16->17
  R10-PARAMS-OWNER ['resume'] 
  R10-RATIO-ANCHOR ['carry'] carry 3->4
  R10-ROUND-PLAYBOOK ['after'] 
  R10-SAV-ACTUATION ['carry'] carry 1->2
  R10-TRAIN-OVERLAP-GRADE ['carry'] carry 7->8
  R10-UPDATE-PR-SIGNALS ['resume'] 
  R10-UX-HEALTH ['carry'] carry 14->15
stages main {'absorbed': 4, 'carries-open': 5, 'done': 120, 'in-progress': 7, 'not-started': 48, 'queued': 6}
stages head {'absorbed': 4, 'carries-open': 5, 'done': 121, 'in-progress': 8, 'not-started': 46, 'queued': 7}
```

`node tools/policy/brief_lint.mjs` on the merged tree prints `TOTAL: 0 error(s) across 48 file(s)`.

## Figures

`git log --no-merges --reverse --format='%h %s' 9442cb4ea..9e5f5cf1c -- dev/programme/rosters/` prints 25 commits, oldest first, tool path suffix dropped:

```
6c428b63d roster_sync: derive stages from pull requests
d99761d3e roster_sync: derive stages from pull requests
2d45acb7a roster_edit append-carry R10-ORCH-ROSTER-SCHEMA
aa679f28b roster_edit set-stage R10-DEMAND-OVERBOOK
29b0b8ff2 roster_edit set-after R10-ORCH-DISPATCH-REG
3b5942aac roster_edit set-after R10-CLOSEOUT-CLEANUP
d87475fe1 roster_edit set-stage R10-UPDATE-PR-SIGNALS
558125209 roster_edit set-after R10-ROUND-PLAYBOOK
0378e16f9 roster_edit append-carry R10-HEAT-METER
42008e799 roster_edit append-carry R10-COP-GATE
33c505efc roster_edit append-carry R10-UX-HEALTH
1ac59f510 roster_edit append-carry R10-RATIO-ANCHOR
121417d60 roster_edit set-stage R10-UPDATE-PR-SIGNALS
5f420bfa5 roster_edit append-group R10-LEGIONELLA-COMPLETION
7ea11e81c roster_edit append-carry R10-FLOW-DESIGN-STAGES
f0b011d33 roster_edit append-carry R10-TRAIN-OVERLAP-GRADE
fac3e1de0 roster_edit append-carry R10-COP-GATE
96aa9bc6f roster_edit append-carry R10-COP-GATE
006990549 roster_edit append-carry R10-BUFFER-STORE
50742450e roster_edit append-carry R10-BUFFER-STORE
22fe609e0 roster_edit append-carry R10-SAV-ACTUATION
02ee07bea roster_edit append-carry R10-HEAT-METER
78e5a4d84 roster_edit append-carry R10-DIAG-REDACT
460d9f19b roster_edit append-carry R10-HEAT-METER
9e5f5cf1c roster_edit set-after R10-ARCH-DOCS
```

`6c428b63d` and `d99761d3e` are `roster_sync.py` stage derivations: they set R10-PARAMS-OWNER (#2817) and R10-ARCH-SHAPES (#2819) from not-started to in-progress and record their pull requests, and `aa679f28b` sets R10-DEMAND-OVERBOOK done at main `da12aa37d`. `d87475fe1` and `121417d60` move R10-UPDATE-PR-SIGNALS to carries-open and back to in-progress. `29b0b8ff2` empties R10-ORCH-DISPATCH-REG's `after` (it listed R10-ORCH-LEDGER), `3b5942aac` drops R10-ARCH-DOCS and R10-ROUND-PLAYBOOK from R10-CLOSEOUT-CLEANUP's, `558125209` drops R10-ARCH-DOCS from R10-ROUND-PLAYBOOK's, and `9e5f5cf1c` adds R10-LEGIONELLA-COMPLETION to R10-ARCH-DOCS' `after`. `5f420bfa5` appends the group R10-LEGIONELLA-COMPLETION. The remaining carries are `2d45acb7a` (R10-ORCH-ROSTER-SCHEMA, from #2818's round 1: `roster_lib.is_open` tests only `DONE_STAGES`, so an `absorbed` group passes the carry destination check), the R10-HEAT-METER design carries (`0378e16f9`, `02ee07bea`, `460d9f19b`), their routing to R10-COP-GATE, R10-UX-HEALTH and R10-RATIO-ANCHOR (`42008e799`, `33c505efc`, `1ac59f510`, `fac3e1de0`), `7ea11e81c` and `f0b011d33` (the pool and train-overlap instruments), and the D15 live-bundle leads, each marked unverified in its text and routed to the group that owns the seam: L1 and L2 to R10-COP-GATE (`fac3e1de0`, `96aa9bc6f`), L3 and L4 to R10-BUFFER-STORE (`006990549`, `50742450e`), L5 to R10-SAV-ACTUATION (`22fe609e0`), L6 to R10-HEAT-METER (`02ee07bea`), L7 to R10-DIAG-REDACT (`78e5a4d84`), and L9 to R10-HEAT-METER (`460d9f19b`).

## Red checks

Not read by this seat for this body; this pull request changes only the roster JSON and its delivery row. The orchestrator reads the check-runs.

## Forward-carry

none

## Friction

none
