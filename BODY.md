Roster for round 10, the next landing after #2799. It puts the roster seat's ops that are on `handoff/audit-r10-roster` and not on main onto main, so the merge train's pre-flight, which reads only main's roster, stops parking pull requests whose carries name branch-only groups (#3062 parks on R10-USER-DOCS-VERIFY). Part of #201. It leaves #201 open.

## Summary

The roster file is the branch's, with three host paths scrubbed relative to the branch: the lines holding `/Users/timmalmstrom/hpo-orch/...` (in the R10-CLOSEOUT-CLEANUP carry and two R10-FLY-STANDING-CONTRACTS carries) read `~/hpo-orch/...` here, by `ref_privacy.py scrub --write`, because `prepr.sh` refused them under ref privacy. `git diff 75278a0e05a95904dd4ec392c34f26a4a9eea452 origin/handoff/audit-r10-roster -- dev/programme/rosters/wave-r10-groups.json` is those three lines and nothing else. The branch keeps the unscrubbed text until its three carries are dropped and re-appended.

## Head

`75278a0e05a95904dd4ec392c34f26a4a9eea452` is one commit on origin/main `1d28de9936ef` (merge-base is main itself). It changes one file, `dev/programme/rosters/wave-r10-groups.json`; the opener adds the pull request's own delivery row.

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

Main's roster has no group the head lacks. With groups keyed on the `group` field: main 236, head 302, none removed, 66 new, 50 of main's groups changed. The git blob of the roster on main is `6c5728808f6fac8adc760d57482e7af234bf08dc` and at the head `8a4dcc3fd3861d4ad32c0c658090d318c64d2db9`. `git diff --stat origin/main HEAD` prints one file, 3783 insertions and 185 deletions.

## Figures

`node tools/policy/brief_lint.mjs dev/programme/rosters/wave-r10-groups.json` at the head prints `TOTAL: 0 error(s) across 1 file(s)`, with one warning (R10-FLY-GH-CALL-LOG, `tools/audit/seat/record_row.py:882`: no anchor text extracted near the citation). `tools/pr/prepr.sh` at the head prints `PRE-PR: 75278a0e05a95904dd4ec392c34f26a4a9eea452 000000000000000000 rc=0`.

## Red checks

None known at this head; `prepr.sh` and `ci_predict` predict none. The orchestrator reads the check-runs.

## Forward-carry

none

## Friction

none
