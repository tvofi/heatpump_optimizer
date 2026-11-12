Fix review: merge 2aa65fa6d39b06bd67201d6658019ae38f05b0bd

bus-nonce: cb5c9cdf05b685b64301ebba137434ec
pending-ci: gate

## Evidence

- Round: second round of review on #3502 (prior verdict blocked at 1965559c0ce814ee36c37fce9b5d41f55ec3e5ef, introduced-red). Scope is the delta 1965559c..2aa65fa6 (fix-review.md step 12): `review_carry.py` prints FRESH-REVIEW, so the delta is reviewed rather than carried.
- Delta: the PR's own change is the single commit c4c904380bda20b138881849fd0c17f10cb7b99c (`tools/audit/seat/sweep_render.py`, `tools/audit/seat/sweep_template.md`); every other path in `git diff 1965559c 2aa65fa6` comes from the main merge at 2b4515dc52821ad721225090d329c224dbddafae. The PR's three-dot `--stat` against its merge base at each head differs only in those two files. No `custom_components/` change belongs to the PR, so the scope does not widen.
- Prior finding resolved: at the head, `python3 -I tools/audit/seat/sweep_render.py --self-test` prints `sweep_render self-test: 36 checks, 0 failed`, rc 0.
- Mutant A: drop `"sweep_record": "--sweep-record"` from `OPTIONAL_FLAGS`. The self-test dies with `Refused: unfilled: \`sweep_record\` is empty` and prints no tally, so the CI step's grep refuses it. The mutant is killed. It is killed by the existing null-control render (`sweep_record=""`), not by the new case as the body says. The body also quotes the message as `unused: sweep_record`, but the message is `unfilled`. The killing still holds.
- Mutant B: stop the template rendering `{{sweep_record}}` in step (4b). The output is `FAIL the tracked template renders from a complete overlay, every placeholder filled (null control)`, which reproduces round 1's red. The mutant is killed.
- Live check at the head, read from the job API rather than from the body: `governance / instrument-self-tests` job 131210914672, head_sha 2aa65fa6d39b06bd67201d6658019ae38f05b0bd, concluded success. Step 37 "Render the sweep template, and the policy re-read predicate" ran and concluded success, not skipped. Step 14, the scorecard self-test, concluded success. All 123 steps are success or skipped. No instrument-self-tests step is red at the head, so nothing is INTRODUCED.
- Merge with main: `git merge-tree --write-tree origin/main 2aa65fa6` exits 0. The driver printed `LEDGER-MERGE: resolved tests/closures.json`.
- The body's head paragraph names 2aa65fa6, which is the head I measured.
- VERSION, the manifest version and the RELEASE_NOTES heading have no PR-own change: those paths in the delta come only from main's stamp 4596f721f6.
- CI: classify reads `WAIT 2aa65fa6d39b06bd67201d6658019ae38f05b0bd pending: gate red: none` on every poll, 13:51 to 13:57 UTC (ev/classify.txt). The rendered digest showed `gate` failure and `tests / nightly-status` failure. `nightly-status` is not in `merge_train.py owed-reds`, so it is owed no answer. Classify reads `gate` as pending, not red. I stopped polling after about 10 minutes, short of the brief's 30, because the session's frugal PreToolUse hook refused the next inline poll (`inline search op 6 this prompt exceeds budget of 5`). I did not work around the hook. I did not hand the wait to a subagent because the dispatch forbids it. The relay posts this verdict only once CI is green at this head.
- Red-check answer for round 1's red (`governance / instrument-self-tests`): the body names the check and answers it. The cheaper detector is the step's own one-second self-test, which the scope selection omitted in round 1. That satisfies the trigger.
