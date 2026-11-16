Fix review: merge 3dd9afda8c2d748c125401746164d1ea15e18913

bus-nonce: 1f5e52a5e5de442ea666fb13703c97c4

## Summary

Round 2 (a delta round over the reviewed head e5bf20c3b9b8af81663cd787de2460efb18656dc, which had a `merge` verdict). The head I measured is `3dd9afda8c2d748c125401746164d1ea15e18913`. It is the PR head and the head the body names. The delta is one commit: the merge of origin/main d4968fe08b into the reviewed head. `review_carry.py` prints FRESH-REVIEW because the merge is not automatic. An automatic `git merge-tree` of the two parents conflicts in one file only, `tools/audit/seat/beat_jobs.py` (ev/auto_merge_parents.txt). The hand resolution differs from the automatic tree only in that file's two conflict hunks (ev/resolution_vs_auto.diff). Both hunks take the union: `ROWS` keeps this PR's `cp-owed` and main's `ci-attempt`, and so does `RUN`. The PR's three-dot diff touches no `custom_components/` path, no VERSION, manifest or RELEASE_NOTES file, and no claim file or golden fixture (ev/pr_files.txt). The delta brings main's own production commits (v10.0.2) through the merge, but those are main's own reviewed changes, not this PR's, so the review is not widened. Since the head's merge base, `dev/governance/roles/` changed on main only in `orchestrator.md`, so the fix-review contract is current.

## Findings

- Note: body-stale: the body's `## Head` section repeats the same `3dd9afda8c...` recarry paragraph three times, and its Figures line `beat_jobs self-test: 259 checks, 0 failed` now reads 271 at this head, because main's `ci-attempt` row added cases. This is paperwork, and no code is affected. Carry: dismissed: a body figure moved by main's merged rows, re-derived here as 271

## Evidence

- Prior finding resolution: the round-1 surviving FIXER-OWED filter mutant was carried to R11-INTAKE-R10-RESIDUE, and the delta does not touch `owed_watch.py`, so its carry stands unchanged. The round-1 notes (design-departure, doc-precision) were dismissed with reasons, and the delta does not touch their files.
- RESULT resolution mutants (ev/resolution_mutants.txt): I planted four mutants on the merge resolution, and all four were killed by `beat_jobs.py --self-test --no-mutants`. They drop `cp-owed` from RUN (Traceback, rc 1), drop `ci-attempt` from RUN (Traceback, rc 1), drop `cp-owed` from ROWS (3 failed) and drop `ci-attempt` from ROWS (4 failed). Both sides of the union are pinned.
- RESULT self-tests at the head: `beat_jobs self-test: 271 checks, 0 failed` with the in-file mutants, every `mutant ... killed by:` line ok (ev/beat_jobs_selftest_mutants.txt). The same self-test with `--no-mutants` reads 161 checks, 0 failed (ev/beat_jobs_selftest.txt). `owed_watch self-test: 73 checks, 0 failed` (ev/owed_watch_selftest.txt). `orchestrator_tick self-test: 319 checks, 0 failed` (ev/tick_selftest.txt). `STRUCTURE RATCHET PASSED` (ev/structure.txt).
- Auto-merged by git (no hand edit): `.github/workflows/governance.yml`, `tests/closure.py`, `tools/audit/seat/beat_jobs_selftest.py`, `tools/audit/seat/beatd.jobs.json` (both the `cp-owed` and `ci-attempt` rows are present) and `tools/ci/selftest_closures.json`. `tests/closures.json` was resolved by the LEDGER-MERGE driver as a set union.
- Merge with main: `git merge-tree --write-tree origin/main 3dd9afda8c` (origin/main 4ce615b5e6) exits 0, with the ledger driver printing `LEDGER-MERGE: resolved tests/closures.json` (ev/merge_tree.txt). There is no conflict.
- Red checks: I read the owed-reds set (ev/owed_reds.txt). The body answers `none`, and no check is red at this head.
- CI: `merge_train.py classify 3dd9afda8c2d748c125401746164d1ea15e18913 --pr 3651` exits 0 and prints `GREEN 3dd9afda8c2d748c125401746164d1ea15e18913 pending: none red: none` at 06:46:41 UTC, after polling from 06:20 (ev/classify.log).
- Not re-derived at this head: the body's diff-mutant counts, the agreement-lane RESULT and the selftest_scope figures. Round 1 left these to CI's heavy lanes, and the delta does not touch the files they measure beyond the union resolution.
- Harness: none was named by a finder. This is a feature built to the approved design's part-1 plan, which is committed as `owed_watch.py --self-test` and `beat_jobs_selftest.py` (unchanged from round 1).
