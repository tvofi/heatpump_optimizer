Fix review: merge 995398d8af12f2bbcd3da170c0c9446300bf38ed

bus-nonce: b43cdee1efd7a563c6a5c188c6ed02d3
pending-ci: tests / fast (3.14), tests / closures, tests / arch-instrument, tests / typing, tests / browser, tests / coverage, governance / instrument-self-tests

## Red checks

- `gate` (job 137343333840, run 45064364844): `FAIL run(s) [45064363719] at this head are still being judged; their gate decides` (ev/gate-job-137343333840.fail.txt). An edit-triggered run's gate deferring to run 45064363719, whose own gate decides; classify reports `gate red: none`, so it is not a defect of the head.

## Evidence

- Round: second (delta). Previous verdict blocked 107e630c704fe329de1169e48c1e5afd399f99b9 `introduced-red` on owner_only_channel.py P5b; role contracts unchanged between the merge base and origin/main. Reviewed from a detached worktree at 995398d8af12f2bbcd3da170c0c9446300bf38ed (ev/HEAD.txt).
- Scope: delta `git diff 107e630c70 995398d8af` is one file, dev/audit/harnesses/owner_only_channel.py, +3/-19 (ev/delta.diff): remerge_main.sh leaves `CREDENTIALED` and `WRITER_ARMS`, `w_remerge` is deleted, remerge_main_selftest.py's no-writer reason is reworded. An instrument delta, so the review is not widened (fix-review.md step 12).
- Previous block resolved: at this head `python3 -I dev/audit/harnesses/owner_only_channel.py` prints every P5b line `ok`, `RESULT arms=48 failed=0`, `OWNER-ONLY CHANNEL HELD`, rc 0 (ev/owner-only-channel-head.txt).
- The sibling command at this head no longer returns remerge_main.sh; its remaining push goes through tools/pr/app_push.sh, which keeps its own fail-closed arm and null (ev/sibling-and-remerge-surface.txt). remerge_main.sh holds no mint, key or openssl reference; its only leftover is a `declare -F mint_cleanup` guard in its exit trap, a no-op without app_mint.sh sourced.
- RESULT mutant A (delta reverted, remerge_main.sh back as a credentialed arm): `RESULT arms=14 failed=1`, FAIL P5b `no longer returned: ['tools/audit/seat/remerge_main.sh']` (ev/mutant-A-revert-delta.txt). Restored.
- RESULT mutant C, the body's (remerge_main.sh put back in `CREDENTIALED` only): `RESULT arms=14 failed=2`, the `no longer returned` FAIL and `the arm ran to its end -- KeyError`, as the body states (ev/mutant-C-credentialed-only.txt). Restored.
- RESULT mutant B, reviewer's own (remerge_main_selftest.py dropped from `NOT_WRITERS`): `RESULT arms=13 failed=1`, FAIL P5b `owes an arm: ['tools/audit/seat/remerge_main_selftest.py']` (ev/mutant-B-drop-selftest-notwriter.txt). Restored.
- RESULT reverse control, the body's (`# mint_token` appended to remerge_main.sh): `RESULT arms=13 failed=1`, FAIL P5b `owes an arm: ['tools/audit/seat/remerge_main.sh']` (ev/reverse-control-mint-token.txt), so the comparison still sees a key reader the list lacks. Restored.
- Figure: the body's 1.4 s for `--only P5b` is a per-seat wall clock; this seat measured 1.68 s (ev/p5b-timing.txt), the same order. Not re-derivable exactly.
- Merge with main: `git merge-tree --write-tree origin/main 995398d8af12f2bbcd3da170c0c9446300bf38ed` exits 0, tree 1ebb0fdca26eede749c541920afa68d75547b446 (ev/merge-tree.txt).
- VERSION, the manifest version, RELEASE_NOTES.md, golden fixtures and every *_budgets.json are untouched over the three-dot range (ev/untouched.txt).
- Head: the body's `## Head` names 995398d8af12f2bbcd3da170c0c9446300bf38ed, the head reviewed; it did not move during the review.
- Previous verdict's two findings (app_push.sh's caller-held fork boundary; the first adopted verdict as the live check) and its ruling-unrecorded note were dismissed there and the delta does not change them.
- CI: `merge_train.py classify 995398d8af12f2bbcd3da170c0c9446300bf38ed --pr 3867` printed `WAIT ... pending: gate red: none` (rc 3) on every run from 20:16 to 20:49 UTC (ev/classify-poll.log, ev/classify-last.txt). At 20:49 the check-runs API showed every completed required check green but the superseded gate above; still running or queued: the seven contexts on the `pending-ci:` line. Review complete, so the verdict is returned with that line for the relay to post once CI is green at this head.
