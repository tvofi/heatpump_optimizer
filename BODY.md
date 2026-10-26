Roster for round 10, batch 16, at the roster tip `d373c351f7edb3e39b036f3e852505d33eb81637`: the five roster commits the roster seat made on `handoff/audit-r10-roster` after `d49603ff8cf154a13186933897fd05f60361a8ed` (the head of batch 15, which is on main), listed by command under Figures. They are four `append-carry` ops (R10-FLOW-JIDOKA, R10-FLY-LEDGER-SAMPLE, R10-FLY-DEPGRAPH-STALE, R10-ORCH-PLANPAGE) and one `set-stage` op, R10-PLAN-ISSUES-CHART to done. Part of #201. It closes nothing by keyword and leaves #201 open.

**Merge order: none.** Batch 15 is on main. Roster queue lines up to 359 are in this batch.

## Head

The authored head is `d373c351f7edb3e39b036f3e852505d33eb81637`, the tip of `handoff/audit-r10-roster`; its merge base with origin/main is `d49603ff8cf154a13186933897fd05f60361a8ed`, and the pull request merges origin/main (`7d2056970e08135bdc7c2cab4063427a2efa1c30`) into it. `git merge-tree --write-tree origin/main d373c351f7edb3e39b036f3e852505d33eb81637` prints the tree `e2acc8463d1ea2b48cd3575c1349e819103543fd` and no conflict. The only file these ops touch is `dev/programme/rosters/wave-r10-groups.json`, the pull request's own delivery row apart. `git diff --stat origin/main e2acc8463d1ea2b48cd3575c1349e819103543fd` prints:

```
 dev/programme/rosters/wave-r10-groups.json | 14 +++++++++-----
 1 file changed, 9 insertions(+), 5 deletions(-)
```

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

The blob hashes come from `git show <ref>:dev/programme/rosters/wave-r10-groups.json | git hash-object --stdin`: main prints `6c8e6f46ebc63c8cf352392c77944628ae9e8b0e` and the merged tree prints `36ed196b49ca16f48f11e04a35a09dce898fb7e4`. A script that loads both files as JSON and keys groups by their `group` field printed (lines reformatted here for the page):

```
groups main 195 head 195 (no group added or removed)
R10-FLOW-JIDOKA carry 21->22
R10-FLY-DEPGRAPH-STALE carry 3->4
R10-ORCH-PLANPAGE carry 6->7
R10-FLY-LEDGER-SAMPLE carry 1->2
R10-PLAN-ISSUES-CHART resume.stage queued->done
resume stages main {'done': 123, 'in-progress': 7, 'not-started': 45, 'queued': 11, 'absorbed': 4, 'carries-open': 5}
resume stages head {'done': 124, 'in-progress': 7, 'not-started': 45, 'queued': 10, 'absorbed': 4, 'carries-open': 5}
```

Exactly the five groups the five ops name differ, and done rises by one while queued falls by one, as the one `set-stage` op implies. `node tools/policy/brief_lint.mjs` was run on `git archive` extracts of origin/main and of the merged tree, each given a fresh `git init` (so no tag history): both print `TOTAL: 10 error(s) across 48 file(s)`, the same ten, none in a roster file (they are `carry-*.json` path citations that need tag history), so the delta is zero.

## Figures

`git log --no-merges --reverse --format='%h %s' d49603ff8cf154a13186933897fd05f60361a8ed..d373c351f7edb3e39b036f3e852505d33eb81637 -- dev/programme/rosters/` prints five commits, oldest first, tool name dropped:

```
e580153ed append-carry R10-FLOW-JIDOKA
a1cefa714 append-carry R10-FLY-LEDGER-SAMPLE
8e61c60c8 append-carry R10-FLY-DEPGRAPH-STALE
02f265488 set-stage R10-PLAN-ISSUES-CHART
d373c351f append-carry R10-ORCH-PLANPAGE
```

The per-group carry counts above come from the script named under Null control.

## Red checks

Not read by this seat for this body; this pull request changes only the roster JSON and its delivery row. The orchestrator reads the check-runs.

## Forward-carry

none

## Friction

none
