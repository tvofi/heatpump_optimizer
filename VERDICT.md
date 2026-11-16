Fix review: merge b197da1e6bf2c51ad95aa819a78ed020b3db2549

bus-nonce: c83873262dc02e68b7c49a40c8c08537

## Round

Third round, over the reviewed head da36537f137ad9bb8a1cbc8c2fdc60bd7c81df8e (previous verdict: merge). The packet's `## Review scope` reads delta. `review_carry.py da36537f13 b197da1e6b` prints `FRESH-REVIEW`: b197da1e6b is not the automatic merge of its parents. The delta is two merges of main and no branch commit. 911384553f is the bot's `ci: merge main`. b197da1e6b is a hand merge of origin/main 31255c3289 with one conflict, resolved by hand. Neither merge touches `custom_components/`, so nothing widens past the delta.

## Evidence

- Delta resolution (ev/delta-resolution.txt). `git merge-tree --write-tree 911384553f 31255c3289` conflicts only in `tools/audit/seat/beat_jobs.py`, and only in ROWS and RUN. The head differs from that merge-tree output only in those two hunks. Each hunk keeps main's `cp-owed` and the PR's `toolchain-promote` (ROWS: `..., "outside-intake", "cp-owed", "bottleneck", "scorecard", "ci-attempt", "toolchain-promote", "darwin-selftest"`; RUN carries both callables). Everything else came from git's own resolution. Apart from hunk offsets and context lines, the PR's own three-dot diff matches the previous round's diff; the only change is how these two lines are spelled (ev/own-diff-compare.txt). `tools/audit/seat/toolchain.py`, `tools/ci/gate.py`, `tools/audit/seat/prune_refs.py` and `dev/audit/harnesses/r11_toolchain_mutants.py` do not change in the delta.
- Reviewer's mutants on the hand resolution (ev/reviewer-merge-mutants.txt): all 4 were killed by `beat_jobs.py --self-test`. Dropping `toolchain-promote` from ROWS gives 3 failed; dropping it from RUN gives a KeyError; dropping `cp-owed` from ROWS gives 3 failed; dropping it from RUN gives a KeyError.
- Self-tests at this head: `toolchain self-test: 42 checks, 0 failed`; `gate self-test: 120 checks, 0 failed`; `SELF-TEST PASS (79 checks)`; `beat_jobs self-test: 281 checks, 0 failed` (ev/selftest-*.txt).
- Fixer's harness (the builder's, not a finder's), at this head: `RESULT mutants=26`, `RESULT survived=0`, and each M0 reads `null-ok` (ev/selftest-r11_toolchain_mutants.py.txt).
- Step 13: `git merge-tree --write-tree origin/main b197da1e6b` against origin/main b94425b94f exits 0. The only driver line is `LEDGER-MERGE: resolved tests/closures.json`, and there is no MERGE-CLAIM line (ev/merge-tree.txt).
- Step 7: the body's `## Head` names b197da1e6b.
- Steps 4, 5, 16: the delta touches no claim file, `VERSION`, manifest, `RELEASE_NOTES.md`, `custom_components/` or actuator write.
- The role contract is current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` touches only COMMON.md.
- CI, classify: `merge_train.py classify b197da1e6b --pr 3654` was polled from 08:16 to 08:46 UTC (ev/classify.log). It printed `WAIT ... pending: gate red: none` until 08:29. From 08:30 on it exits 2 (unreadable) with `REFUSE selftests: the base's governance / instrument-self-tests job 133162504346 is in_progress, which reads no step: an introduced red cannot be ruled out (fail closed)`. A one-off run at 08:47 gave the same result. classify never read GREEN at this head.
- CI, the head's reds come from main and are not this PR's. `governance / instrument-self-tests` (job 133168108912) is red only on the `orchestrator_tick.py --self-test` step: `NameError: name 'SEAT_WINDOW_MIN' is not defined` at orchestrator_tick.py:1730 `outside_chain_idle`. `tests / fast (3.14)` (job 133168381856) reads `1 of 2723 ENTITY CHECKS FAILED`. The one non-planted FAIL there is `orchestrator_tick.py --self-test passes (it reads roster_lib's closed set)`, the same NameError. The PR's diff does not touch `orchestrator_tick.py`. The same self-test fails identically at base 31255c3289 and at current origin/main b94425b94f (ev/orchestrator_tick-at-*.txt). So the red is inherited, not introduced by this PR, and no `## Red checks` answer is owed by the PR (defect-root-cause.md). `tests / closures` was still in_progress at 08:46. `gate` and `tests / nightly-status` are red, and neither of those two is in `owed-reds`. Main needs its `SEAT_WINDOW_MIN` reference repaired, and this head needs re-merging over that repair, before the head can read green; the relay refuses this verdict over a red.
- review_packet render: `REFUSE introduced-red: unreadable` (instrument-self-tests in_progress at render). classify decides (ev/review-packet.md).

## Notes

- Note: body-figure: the body quotes `beat_jobs self-test: 261 checks, 0 failed`, but this head prints 281 checks, 0 failed. The other rows came in with main's merges. The body's `## Head` also repeats the da36537f13 paragraph three times. Carry: dismissed: paperwork on a body the orchestrator re-renders at each recarry
- Note: red-checks: the body's `## Red checks` reads `none` while the head is red on two required contexts. Both are main's `orchestrator_tick.py` NameError, so neither is owed by this PR (see Evidence). Carry: dismissed: inherited from main 31255c3289, not owed by this PR

## Findings

- Follow-up: the previous verdict's finding is not resolved by this delta, because `toolchain.py` does not change. `choose`'s walk bound `[:SCAN_RUNS]` is still unpinned: removing it leaves the self-test green. It bounds cost and is not a correctness predicate. Carry: R11-PRE-TOOLCHAIN-PIN
