Roster for round 10, batch 20, at the roster tip `c8d51c464e84d36732855f21f962287d9b1405f7`: the seventeen roster commits the roster seat made on `handoff/audit-r10-roster` after `63b1cfd03d913abb3b1117a3d913506889024c74` (the head of batch 19, #2857), listed by command under Figures. They are nine `drop-carry` ops (R10-HOTFIX-BATCH-ERREXIT carry 1, landed by #2848 `e0ffb12130436f1cef00e770aed436ac8b4f067e`; R10-RECORD-API-O1 carry 3, twice; the six carries of R10-CARD-VOICE, landed by #2841 `75ac453534e10c0a6ef88533ad5ff375cd6ca333`), two `set-stage` ops (R10-LEGIONELLA-COMPLETION to done, #2832 `510787b769407ed25054177cfb0f6bd17e041e0e`, zero carries; R10-CARD-VOICE to done after its drops), two `append-group` ops (R10-ERREXIT-COUNTERMEASURES, four carries from #2849; R10-RECORD-API-O1, three carries from #2852) and four `append-carry` ops (the R10-RECORD-API-O1 carry, scrubbed, twice; one each to R10-COP-GATE and R10-UX-HEALTH from #2854, review probe/rev-2854-084d74e7, quoted verbatim from its Forward-carry). Part of #201. It closes nothing by keyword and leaves #201 open.

**Merge order: after #2857 (batch 19), which has merged** as `2563e29228a9c2b075afed4f13b89839fcc281b2`. Batch 19's head `63b1cfd03d913abb3b1117a3d913506889024c74` is an ancestor of both main and this head, so the diff carries only this batch's seventeen ops. The two new groups must reach main for the carry audit of #2849 and #2852 to read them. Line 381 (R10-FLOW-DESIGN-STAGES) is still held for triage batch 33.

**Ordering note:** the R10-ERREXIT-COUNTERMEASURES brief was changed in one place against the dispatch seat's file: the harness path `dev/audit/harnesses/r10_errexit_capture.py` is followed by "(at e1a684789)", the commit carrying the file, because the brief linter reads cited tag refs only from the brief and refused the path without one. No other field changed. The R10-RECORD-API-O1 carry on the ref_privacy home-match finding was dropped and re-appended with four strings put in prose over two rounds, as the REF PRIVACY predictor refused them (orchestrator ruling (a)): the passwd-home path of the root account, the root-cause role contract's file path, the `/root/...` control phrase, and the CI runner's home in the control phrase (the predictor judges by that home); meaning unchanged.

## Head

The authored head is `c8d51c464e84d36732855f21f962287d9b1405f7`, the tip of `handoff/audit-r10-roster`. Its merge base with origin/main (`2563e29228a9c2b075afed4f13b89839fcc281b2` at this reading) is `63b1cfd03d913abb3b1117a3d913506889024c74`, so the head carries nothing of batch 19 beyond what main holds; the pull request merges origin/main into it. `git merge-tree --write-tree origin/main c8d51c464e84d36732855f21f962287d9b1405f7` prints the tree `7d139f3728e460d51c267b1057331d6d97cbfea6` and no conflict. The only file these ops touch is `dev/programme/rosters/wave-r10-groups.json`, the pull request's own delivery row apart. `git diff --stat 63b1cfd03d913abb3b1117a3d913506889024c74 c8d51c464e84d36732855f21f962287d9b1405f7` prints:

```
 dev/programme/rosters/wave-r10-groups.json | 118 +++++++++++++++++++++++++----
 1 file changed, 103 insertions(+), 15 deletions(-)
```

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

The blob hashes come from `git show <ref>:dev/programme/rosters/wave-r10-groups.json | git hash-object --stdin`: origin/main (which now holds batch 19) prints `54e5b4f02dba11e20dac603001a2c37c3df9c97b` and this head prints `fb90f3cffe328f5c7ab765ab1d10b22dc0b9202a`. A script that loads origin/main's file and this head's as JSON and keys groups by their `group` field printed:

```
groups 197 199 added ['R10-ERREXIT-COUNTERMEASURES', 'R10-RECORD-API-O1'] removed []
R10-LEGIONELLA-COMPLETION carry 0 -> 0 stage queued -> done
R10-CARD-VOICE carry 6 -> 0 stage not-started -> done
R10-COP-GATE carry 10 -> 11 stage not-started -> not-started
R10-UX-HEALTH carry 15 -> 16 stage not-started -> not-started
R10-HOTFIX-BATCH-ERREXIT carry 1 -> 0 stage done -> done
R10-RECORD-API-O1 carry 3 not-started
R10-ERREXIT-COUNTERMEASURES carry 4 not-started
```

Exactly the seven groups the seventeen ops name differ, and nothing else moved. `node tools/policy/brief_lint.mjs` was run on `git archive` extracts of origin/main and of the merged tree, each given a fresh `git init`, `git add -A` and one commit: both print `TOTAL: 10 error(s) across 48 file(s)`, so the delta is zero.

## Figures

`git log --no-merges --reverse --format='%h %s' 63b1cfd03d913abb3b1117a3d913506889024c74..c8d51c464e84d36732855f21f962287d9b1405f7 -- dev/programme/rosters/` prints seventeen commits, oldest first, tool name dropped:

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
052968159 drop-carry R10-CARD-VOICE (carry 1)
dabe254b5 drop-carry R10-CARD-VOICE (carry 2)
8c3a3562b drop-carry R10-CARD-VOICE (carry 3)
756fab0ce drop-carry R10-CARD-VOICE (carry 4)
a2a4e9d58 drop-carry R10-CARD-VOICE (carry 5)
c3fbc7407 drop-carry R10-CARD-VOICE (carry 6)
c8d51c464 set-stage R10-CARD-VOICE
```

The per-group counts above come from the script named under Null control.

## Red checks

Not read by this seat for this body; this pull request changes only the roster JSON and its delivery row. The orchestrator reads the check-runs.

## Forward-carry

none

## Friction

none
