Roster for round 10, fifth landing: brings main's `dev/programme/rosters/wave-r10-groups.json` (plus `critical-path.json` and `carry-201.json`) up to the roster branch tip, so that open pull requests' carries resolve against the tree's roster (finding-propagation.md). Part of #201.

## Head

`a72c01ddd30d0eee1b6aa94d7b06b93cf903624d` merges the authored code head `31e162fd3a1207db596539b2330af1d274c36c85` and then merges origin/main `289426c1f` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`103b1118b2b2e23a18b413ec6b983c0127c9d7ec` merges the authored code head `31e162fd3a1207db596539b2330af1d274c36c85` and then merges origin/main `03b49e152` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

The authored code head is `31e162fd3a1207db596539b2330af1d274c36c85` (`handoff/audit-r10-roster`). `git diff --name-only origin/main...31e162fd` lists exactly three files: `dev/programme/rosters/wave-r10-groups.json`, `dev/programme/rosters/critical-path.json` (new) and `dev/programme/carries/carry-201.json`; the PR head adds only this PR's own delivery row.

The diff, enumerated from the JSON at `origin/main` (03b49e15) and at `31e162fd` (groups 91 to 108, stage `done` 43 to 51, carries 201 to 254):

- New groups (17): R10-HANDOFF-ARCHIVE and R10-DEPENDABOT-AIOHTTP (done); R10-ORCH-MACHINERY, R10-CARD-VOICE, R10-THERMAL-POWER-OPTION, R10-LEARNER-DEFAULT, R10-MUTANT-SKIP, R10-CI-LAYOUT-P1, R10-CI-LAYOUT-P2 (not-started); R10-TICK-OWED-LEVEL, R10-REPLAY-CAP, R10-RCA-HANDOFF-SLIP, R10-HANDOVER-REFRESH, R10-RCA-ORCH-CONTINUITY, R10-TICK-RELAY-DECOUPLE, R10-PLAN-ARTIFACT, R10-ROSTER-PUSH-RACE (in-progress). No group is removed.
- Stage changes (18): to done: R10-SAV-REASONS, R10-TRAIN-HOLD, R10-DEEPLINK-HANDLERS, R10-STAMP, R10-RCA-NIGHTLY-PYSPY, R10-FOLLOWER-DEBOUNCE, R10-SETPOINT-BOOST, R10-UPDATE-PR-LOCK; to in-progress: R10-NIGHT-FOLDS, R10-FREQ-DEFROST, R10-ADVISOR, R10-I5-DOCS, R10-REPLAY-LANE, R10-RCA-FRICTION, R10-CI-LAYOUT, R10-UPDATE-PR-SIGNALS, and back from done to in-progress R10-PREPR-CAP, R10-CI-RATCHET-RED.
- Carries appended (14 existing groups, 32 in all; the other 21 of the 53 are carried by the 17 new groups), among them R10-CI-LAYOUT 14 to 27 and R10-BRIEFS-FOLD 19 to 20 (from #2521: a wrong harness path in `tests/README.md`), R10-ORCH-MACHINERY 8 to 10 (from #2524: `daemonize.py --self-test` position; and update_pr.sh leaving its worktree on the branch, #2513, #2544, #2547), R10-REGISTRY-LEAK 1 to 3 (the second handoff r10-earlycutoff-coverage at ecaf178c, the test-coverage residual of #2329), and R10-REPLAY-LANE (one carry replaced by the #2548 round-2 text, count 3 to 5 in all), R10-REGISTRY-LEAK, R10-ROSTER-OPS 3 to 6 (the last three: this PR's own, from the fix review of #2513, comment 6314156311, item 3b97e1aa: three fail-closed surviving mutants of `roster_edit.py` and the key-less-group note).
- Text edits (brief, issues, fixes, findings) on 16 existing groups; R10-CI-LAYOUT's `findings` now says four pull requests with PR 1 and PR 2 split into the -P1 and -P2 groups, where it said two.
- `carry-201.json`: one carry added (the nightly-ha py-spy positive control, from #2479) and the `stage` text extended to name it.

This PR leaves #201 open and closes nothing by keyword.

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

n/a: no measured claim. The lists above enumerate a JSON diff between `origin/main` and the head.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none
