Roster for round 10, batch 19, at the roster tip `63b1cfd03d913abb3b1117a3d913506889024c74`: the ten roster commits the roster seat made on `handoff/audit-r10-roster` after `78d071da88f05099677c44c2ce089ea9c4fda6fe` (the head of batch 18, #2851), listed by command under Figures. They are two `set-stage` ops (R10-UPDATE-PR-SIGNALS and R10-HOTFIX-BATCH-ERREXIT to done), six `drop-carry` ops (all six carries of R10-UPDATE-PR-SIGNALS) and two `append-carry` ops (R10-REPLAY-REAL-DAY one, R10-FLOW-JIDOKA one). Part of #201. It closes nothing by keyword and leaves #201 open.

**Merge order: after #2851 (batch 18).** Its head `78d071da88f05099677c44c2ce089ea9c4fda6fe` is an ancestor of this batch's head and is not yet on main, so this pull request opens on main only after #2851 merges. Queue lines 382 and the orchestrator's rulings of 2026-10-26 (#2825 review 6407989264, #2848) are in this batch; line 381 (R10-FLOW-DESIGN-STAGES) is held for triage batch 33.

**Ordering note:** `set-stage ... done` was applied only after the group's carries were re-routed or dropped (done-before-reroute): carry 4 of R10-UPDATE-PR-SIGNALS went to R10-FLOW-JIDOKA verbatim (fad659b01); carries 1, 2, 3, 5 and 6 were dropped as landed by #2825 or superseded by the flock design, each reason in its commit message. R10-HOTFIX-BATCH-ERREXIT was set to done with its one carry still held; the drop of that carry (landed by #2848 `e0ffb12130436f1cef00e770aed436ac8b4f067e`) is the first op of batch 20.

## Head

The authored head is `63b1cfd03d913abb3b1117a3d913506889024c74`, the tip of `handoff/audit-r10-roster`. Its merge base with origin/main (`ed1c9045e140b14e6a98fdb642942b6fa39aca71` at this reading) is `c22e7b2e13fa0d04549f12431fc34a7bd83cc7ff`, so the head still carries batch 18's nine ops until #2851 merges; the pull request merges origin/main into it. `git merge-tree --write-tree origin/main 63b1cfd03d913abb3b1117a3d913506889024c74` prints the tree `5305e9488289861345b7ebd62c5a2f57509094c6` and no conflict. The only file these ops touch is `dev/programme/rosters/wave-r10-groups.json`, the pull request's own delivery row apart. `git diff --stat 78d071da88f05099677c44c2ce089ea9c4fda6fe 63b1cfd03d913abb3b1117a3d913506889024c74` prints:

```
 dev/programme/rosters/wave-r10-groups.json | 19 +++++++------------
 1 file changed, 7 insertions(+), 12 deletions(-)
```

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

The blob hashes come from `git show <ref>:dev/programme/rosters/wave-r10-groups.json | git hash-object --stdin`: batch 18's head prints `837833ae2a684a567dce1be473b6e5858b38befb` and this head prints `54e5b4f02dba11e20dac603001a2c37c3df9c97b`. A script that loads both files as JSON and keys groups by their `group` field printed:

```
groups 197 197 added [] removed []
R10-UPDATE-PR-SIGNALS carry 6->0 stage in-progress->done
R10-FLOW-JIDOKA carry 22->23 stage in-progress->in-progress
R10-REPLAY-REAL-DAY carry 3->4 stage not-started->not-started
R10-HOTFIX-BATCH-ERREXIT carry 1->1 stage not-started->done
```

Exactly the four groups the ten ops name differ, and nothing else moved. `node tools/policy/brief_lint.mjs` was run on `git archive` extracts of origin/main and of the merged tree, each given a fresh `git init`, `git add -A` and one commit: both print `TOTAL: 10 error(s) across 48 file(s)`, so the delta is zero.

## Figures

`git log --no-merges --reverse --format='%h %s' 78d071da88f05099677c44c2ce089ea9c4fda6fe..63b1cfd03d913abb3b1117a3d913506889024c74 -- dev/programme/rosters/` prints ten commits, oldest first, tool name dropped:

```
8c918fd2b append-carry R10-REPLAY-REAL-DAY
fad659b01 append-carry R10-FLOW-JIDOKA
b8ea207f7 drop-carry R10-UPDATE-PR-SIGNALS (carry 1)
4a86cc07b drop-carry R10-UPDATE-PR-SIGNALS (carry 2)
b982ff6ee drop-carry R10-UPDATE-PR-SIGNALS (carry 3)
17df9bf02 drop-carry R10-UPDATE-PR-SIGNALS (carry 4)
2dfbbe603 drop-carry R10-UPDATE-PR-SIGNALS (carry 5)
fb259f02e drop-carry R10-UPDATE-PR-SIGNALS (carry 6)
c6f5863fd set-stage R10-UPDATE-PR-SIGNALS
63b1cfd03 set-stage R10-HOTFIX-BATCH-ERREXIT
```

The per-group counts above come from the script named under Null control.

## Red checks

Not read by this seat for this body; this pull request changes only the roster JSON and its delivery row. The orchestrator reads the check-runs.

## Forward-carry

none

## Friction

none
