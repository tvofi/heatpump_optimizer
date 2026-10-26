Roster for round 10, batch 16, at the roster tip `7d6ff74590e3b331099fb36066e661a6d840ba32`: the nine roster commits the roster seat made on `handoff/audit-r10-roster` after `d49603ff8cf154a13186933897fd05f60361a8ed` (the head of batch 15, which is on main), listed by command under Figures. They are five `append-carry` ops (R10-FLOW-JIDOKA, R10-FLY-LEDGER-SAMPLE, R10-FLY-DEPGRAPH-STALE, R10-ORCH-PLANPAGE, R10-ORCH-BEATD), one `edit-brief` op on R10-IMMERSION-LATCH that re-pins `const.py:1144` to `const.py:1149` (where `IMMERSION_FACTOR` sits on main) so the roster lints clean, and three `set-stage` ops: R10-PLAN-ISSUES-CHART, R10-THERMAL-POWER-OPTION and R10-FLOW-RECORD-PITCH, each to done. Part of #201. It closes nothing by keyword and leaves #201 open.

**Merge order: none.** Batch 15 is on main. Roster queue lines up to 363 are in this batch.

## Head

The authored head is `7d6ff74590e3b331099fb36066e661a6d840ba32`, the tip of `handoff/audit-r10-roster`; its merge base with origin/main is `d49603ff8cf154a13186933897fd05f60361a8ed`, and the pull request merges origin/main (`28800999b9ce23793f191101bdfc1e4f598168fc`) into it. `git merge-tree --write-tree origin/main 7d6ff74590e3b331099fb36066e661a6d840ba32` prints the tree `a52bdaca57ef168d7603d30d62d4723726b72cf7` and no conflict. The only file these ops touch is `dev/programme/rosters/wave-r10-groups.json`, the pull request's own delivery row apart. `git diff --stat origin/main a52bdaca57ef168d7603d30d62d4723726b72cf7` prints:

```
 dev/programme/rosters/wave-r10-groups.json | 23 ++++++++++++++---------
 1 file changed, 14 insertions(+), 9 deletions(-)
```

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

The blob hashes come from `git show <ref>:dev/programme/rosters/wave-r10-groups.json | git hash-object --stdin`: main prints `6c8e6f46ebc63c8cf352392c77944628ae9e8b0e` and the merged tree prints `b21289a28b8139c61ce5f022c8647dd60ce2f5c5`. A script that loads both files as JSON and keys groups by their `group` field printed (lines reformatted here for the page):

```
groups main 195 head 195 (no group added or removed)
R10-THERMAL-POWER-OPTION resume.stage in-progress->done
R10-FLOW-JIDOKA carry 21->22
R10-FLOW-RECORD-PITCH resume.stage not-started->done
R10-FLY-DEPGRAPH-STALE carry 3->4
R10-ORCH-BEATD carry 24->25
R10-ORCH-PLANPAGE carry 6->7
R10-IMMERSION-LATCH brief changed, carry count 1->1
R10-FLY-LEDGER-SAMPLE carry 1->2
R10-PLAN-ISSUES-CHART resume.stage queued->done
resume stages main {'done': 123, 'in-progress': 7, 'not-started': 45, 'queued': 11, 'absorbed': 4, 'carries-open': 5}
resume stages head {'done': 126, 'in-progress': 6, 'not-started': 44, 'queued': 10, 'absorbed': 4, 'carries-open': 5}
```

Exactly the nine groups the nine ops name differ, one op each, and done rises by three, taken one each from in-progress, not-started and queued, as the three `set-stage` ops imply. `node tools/policy/brief_lint.mjs` was run on `git archive` extracts of origin/main and of the merged tree, each given a fresh `git init` (so no tag history): both print `TOTAL: 10 error(s) across 48 file(s)`, the same ten, none in a roster file, so the delta is zero. Before the `edit-brief` op, the roster seat's lint at a full clone refused the roster with one error, the R10-IMMERSION-LATCH `const.py:1144` pin; that op is the repair.

## Figures

`git log --no-merges --reverse --format='%h %s' d49603ff8cf154a13186933897fd05f60361a8ed..7d6ff74590e3b331099fb36066e661a6d840ba32 -- dev/programme/rosters/` prints nine commits, oldest first, tool name dropped:

```
e580153ed append-carry R10-FLOW-JIDOKA
a1cefa714 append-carry R10-FLY-LEDGER-SAMPLE
8e61c60c8 append-carry R10-FLY-DEPGRAPH-STALE
02f265488 set-stage R10-PLAN-ISSUES-CHART
d373c351f append-carry R10-ORCH-PLANPAGE
f802d728c edit-brief R10-IMMERSION-LATCH
b56e9e570 set-stage R10-THERMAL-POWER-OPTION
0f3251614 set-stage R10-FLOW-RECORD-PITCH
7d6ff7459 append-carry R10-ORCH-BEATD
```

The per-group carry counts above come from the script named under Null control.

## Red checks

Not read by this seat for this body; this pull request changes only the roster JSON and its delivery row. The orchestrator reads the check-runs.

## Forward-carry

none

## Friction

none
