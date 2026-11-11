Hotfix: main's `governance / instrument-self-tests` is red for every pull request on three checks from #3425; this clears all three so the job goes green (triage P621, ruling P622).

## Head

4f2a40a2f2b3adedb2018d76f1224096f6858c48 (merge base 0a2139b1ddaf7831b32c443d438fa14e90938bcb)

## Mutation proof

Each fix is data in a table the check reads. Removing the PR_PUSHERS entry in tools/audit/seat/pr_args.sh makes the census print `OPEN tools/audit/seat/remerge_main_selftest.py: undispositioned` (the check "the pusher census: ..." fails). Removing the OPTIONAL_FLAGS entry for plan_coordinator_cap in tools/audit/seat/sweep_render.py makes `sweep_render.py --self-test` raise `Refused: unused: plan_coordinator_cap`.

## Null control

At 0a2139b1dd: `bash tools/audit/seat/pr_args.sh --pushers` printed the OPEN line above; `python3 -I tools/audit/seat/sweep_render.py --self-test` crashed with the unused refusal. At the head: the census prints 23 ok lines and no OPEN (against 23 PR_PUSHERS entries, rc 0) and the self-test prints "34 checks, 0 failed". Fixing the flag first exposed one self-test check ("null control: an overlay with no seat_alives ...") because its `empty` overlay kept plan_coordinator_cap; the overlay now blanks it too, so bare == empty again. The census rule is not loosened.

## Figures

- `bash tools/audit/seat/pr_args.sh --pushers | grep -c '^ok'` : 23; `... | grep -c OPEN` : 0
- `python3 -I tools/audit/seat/sweep_render.py --self-test` : 34 checks, 0 failed
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh` : rc 0 (the interpreter lacks homeassistant, skip ruled allowed)
- tools/ci/selftest_closures.json: a union of six reads, 6 added lines, 0 deleted (`git diff --stat`): app-push += tools/audit/seat/gh_read.py; gh-call-log-shim += tests/throwaway_git.py; hooks-setup, open-pr, pr-args, update-pr += tools/audit/seat/remerge_main_selftest.py. Not compared against the Linux recording of run 43010208881: this seat has no way to read that artifact, so the set is unchecked against it and the main-push re-measure is the check. The `probes misses` line of the sweep-template step and the entries PR #3446 adds are untouched.

## Red checks

`governance / instrument-self-tests` is not in `merge_train.py owed-reds`, so no answer is owed; for the record, #3425's gate did not run the pr_args self-test on its diff because the pr_args closure did not list the new file's name-match (state c/d: the scoped closure was measured before the file existed); the cheapest detector is the full self-test the main push forces, which is what caught it.

## Forward-carry

none

## Friction

none
