Roster for round 10, batch 20, at the roster tip `95e478db33eb2186227a3cab8d1995fd31f5e76f`: the ten roster commits the roster seat made on `handoff/audit-r10-roster` after `63b1cfd03d913abb3b1117a3d913506889024c74` (the head of batch 19, #2857), listed by command under Figures. They are three `drop-carry` ops (R10-HOTFIX-BATCH-ERREXIT carry 1, landed by #2848 `e0ffb12130436f1cef00e770aed436ac8b4f067e`; R10-RECORD-API-O1 carry 3, twice), four `append-carry` ops (that carry, scrubbed, twice; one each to R10-COP-GATE and R10-UX-HEALTH from #2854, review probe/rev-2854-084d74e7, quoted verbatim from its Forward-carry), one `set-stage` op (R10-LEGIONELLA-COMPLETION to done, #2832 `510787b769407ed25054177cfb0f6bd17e041e0e`, a group holding zero carries) and two `append-group` ops (R10-ERREXIT-COUNTERMEASURES, four carries from #2849; R10-RECORD-API-O1, three carries from #2852). Part of #201. It closes nothing by keyword and leaves #201 open.

**Merge order: after #2857 (batch 19).** Its head `63b1cfd03d913abb3b1117a3d913506889024c74` is an ancestor of this batch's head and is not yet on main, so this pull request opens on main only after #2857 merges, or carries batch 19's ten ops until it does. The two new groups must reach main for the carry audit of #2849 and #2852 to read them. Line 381 (R10-FLOW-DESIGN-STAGES) is still held for triage batch 33.

**Ordering note:** the R10-ERREXIT-COUNTERMEASURES brief was changed in one place against the dispatch seat's file: the harness path `dev/audit/harnesses/r10_errexit_capture.py` is followed by "(at e1a684789)", the commit carrying the file, because the brief linter reads cited tag refs only from the brief and refused the path without one. No other field changed. The R10-RECORD-API-O1 carry on the ref_privacy home-match finding was dropped and re-appended with four strings put in prose over two rounds, as the REF PRIVACY predictor refused them (orchestrator ruling (a)): the passwd-home path of the root account, the root-cause role contract's file path, the `/root/...` control phrase, and the CI runner's home in the control phrase (the predictor judges by that home); meaning unchanged.

## Head

The authored head is `95e478db33eb2186227a3cab8d1995fd31f5e76f`, the tip of `handoff/audit-r10-roster`. Its merge base with origin/main (`510787b769407ed25054177cfb0f6bd17e041e0e` at this reading) is `78d071da88f05099677c44c2ce089ea9c4fda6fe`, so the head still carries batch 19's ten ops until #2857 merges; the pull request merges origin/main into it. `git merge-tree --write-tree origin/main 95e478db33eb2186227a3cab8d1995fd31f5e76f` prints the tree `3867783b439f34ec732ee92095dc2058ebb5e086` and no conflict. The only file these ops touch is `dev/programme/rosters/wave-r10-groups.json`, the pull request's own delivery row apart. `git diff --stat 63b1cfd03d913abb3b1117a3d913506889024c74 95e478db33eb2186227a3cab8d1995fd31f5e76f` prints:

```
 dev/programme/rosters/wave-r10-groups.json | 101 +++++++++++++++++++++++++++--
 1 file changed, 101 insertions(+), 6 deletions(-)
```

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

The blob hashes come from `git show <ref>:dev/programme/rosters/wave-r10-groups.json | git hash-object --stdin`: origin/main prints `837833ae2a684a567dce1be473b6e5858b38befb`, batch 19's head prints `54e5b4f02dba11e20dac603001a2c37c3df9c97b` and this head prints `0a9bf035ac6f826b4ad2aa8176768ba87e334402`. A script that loads batch 19's file and this head's as JSON and keys groups by their `group` field printed:

```
groups 197 199 added ['R10-ERREXIT-COUNTERMEASURES', 'R10-RECORD-API-O1'] removed []
R10-LEGIONELLA-COMPLETION carry 0 -> 0 stage queued -> done
R10-COP-GATE carry 10 -> 11 stage not-started -> not-started
R10-UX-HEALTH carry 15 -> 16 stage not-started -> not-started
R10-HOTFIX-BATCH-ERREXIT carry 1 -> 0 stage done -> done
R10-RECORD-API-O1 carry 3 not-started
R10-ERREXIT-COUNTERMEASURES carry 4 not-started
```

Exactly the six groups the ten ops name differ, and nothing else moved. `node tools/policy/brief_lint.mjs` was run on `git archive` extracts of origin/main and of the merged tree, each given a fresh `git init`, `git add -A` and one commit: both print `TOTAL: 10 error(s) across 48 file(s)`, so the delta is zero.

## Figures

`git log --no-merges --reverse --format='%h %s' 63b1cfd03d913abb3b1117a3d913506889024c74..95e478db33eb2186227a3cab8d1995fd31f5e76f -- dev/programme/rosters/` prints ten commits, oldest first, tool name dropped:

```
a391746ee drop-carry R10-HOTFIX-BATCH-ERREXIT (carry 1)
24d768cce set-stage R10-LEGIONELLA-COMPLETION
5651cab9a append-group R10-ERREXIT-COUNTERMEASURES
9573269b1 append-group R10-RECORD-API-O1
7b56726d1 drop-carry R10-RECORD-API-O1 (carry 3)
20648ba3a append-carry R10-RECORD-API-O1
776cb858a drop-carry R10-RECORD-API-O1 (carry 3, again)
62b01c7a9 append-carry R10-RECORD-API-O1
3aab36e9a append-carry R10-COP-GATE
95e478db3 append-carry R10-UX-HEALTH
```

The per-group counts above come from the script named under Null control.

## Red checks

Not read by this seat for this body; this pull request changes only the roster JSON and its delivery row. The orchestrator reads the check-runs.

## Forward-carry

none

## Friction

none
