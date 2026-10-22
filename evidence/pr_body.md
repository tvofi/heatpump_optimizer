Group: R10-FLOW-YIELD-PROBE

Pinned pack file: `dev/programme/flow-study/roster/groups/R10-FLOW-YIELD-PROBE.json` at pack commit 78117030 on branch `claude/dazzling-gauss-7l3u2b`.

R10-FLOW-YIELD-PROBE (owner ruling R13) explains why real-catch blocks per reviewed PR fell from 0.52 to 0.15. The record is `dev/audit/rounds/round10/D13/yield-probe.md`, and every figure in it comes from `tools/audit/seat/review_strength.py`, which reads the verdict bus over git only. No production code, budget, `VERSION`, manifest or claim file is touched.

Round 6 split the guardrail out to R10-ORCH-MACHINERY (item b8b28b28), killed H1, H9 and H5 by fixtures, extended the sweep's literal class to regex characters, and registered the `--fetch` fixture's push in `ref_privacy.py`'s `PUSHERS`.

Round 7 answers the round-6 block (review/2579 f7a6bdf0c) with exactly the two edits the reviewer named, and nothing else:

- **The probe-slice survivor is killed.** PR 16's fixture nonce was `"09abcdef" * 4`, so its first, second and last 8 hex were one string, and `load`'s probe match survived `nonce[:8]` → `nonce[-8:]` and → `nonce[8:16]`. It is now `09abcdef1234567876543210fedcba98`, whose first 8 hex recur nowhere in it.
- **The GROUP_RE disposition carries no count.** It now reads "every roster group and every delivery row's group token holds two or more characters after the dash". The roster at origin/main holds 151 groups, the shortest with 2 characters after the dash, so the equivalence still holds.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01LAMi8aEnSdjgc3vbMjxMrM

## Head

`632d2fe261b5293e718363485cd816909bf3290c` merges the authored code head `8a01caf2eaad3955fa0ddc40b05603430c49e88b` and then merges origin/main `738d950aa` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

Code head `8a01caf2eaad3955fa0ddc40b05603430c49e88b`: one commit on the reviewed head `45754ede263322459d69936f5898d26fe64654f4`, touching two lines of fixture and comment in `_self_test_seams` and one string in the harness's `DISPOSED`. `git diff -U0 45754ede2 8a01caf2e | grep '^@@'` names hunks at `DISPOSED` and `_self_test_seams` only, so no line `load` or the bundle runs has changed. The head is not merged with origin/main (`47147487ba2b` at 2026-10-22T13:42Z, 3 commits ahead): the handoff froze the branch.

## Mutation proof

The reviewer's two survivors, applied one at a time to `load` in this worktree and restored identical:

- `(int(m[1]), nonce[:8]) in probes` → `nonce[-8:]`: `FAIL: cloud: the nonce is the line-start bus-nonce, read in full hex, matched to a probe ref (16)`, `review_strength self-test: 87 checks, 1 failed`, rc=1.
- `nonce[:8]` → `nonce[8:16]`: the same `FAIL` line, `87 checks, 1 failed`, rc=1.

The class rule is the command `python3 dev/audit/harnesses/r10_review_strength_mutants.py --jobs 4`. Its header states the classes and BOUNDS. At the code head it prints `RESULT mutants=2350 killed=2306 survived=44 disposed=44 undisposed=0 stale=0`, rc=0. Each survivor is keyed and reasoned in the harness's `DISPOSED`.

## Null control

- **M0.** With the fixture changed and `load` unmutated, `python3 -I tools/audit/seat/review_strength.py --self-test` prints `review_strength self-test: 87 checks, 0 failed`, and so does the sweep's M0 run. The same two mutants on the old fixture passed 87/0 (the round-6 verdict, ev/hand_mutants.txt X2 and X2b), so the fixture is what now separates them.
- **The sweep's mutant set is unchanged.** `cmp list_before.txt list_after.txt && echo MUTANT-LIST-IDENTICAL` over `--list` at `45754ede2` (a `git archive` copy) and at the code head prints `MUTANT-LIST-IDENTICAL` (2351 lines each).
- **No bundle figure moves.** The diff touches no line the bundle runs (Head), so the record's figures and the round-6 bundle null control (`BUNDLE-IDENTICAL`) stand unchanged.

## Figures

- `python3 -I tools/audit/seat/review_strength.py --self-test` prints `review_strength self-test: 87 checks, 0 failed` at the code head (Python 3.11).
- `python3 dev/audit/harnesses/r10_review_strength_mutants.py --jobs 4` prints `RESULT mutants=2350 killed=2306 survived=44 disposed=44 undisposed=0 stale=0`, rc=0 at the code head (2026-10-22T13:41Z to 14:22Z).
- `python3 -I tools/audit/seat/ref_privacy.py --check` prints `0 refused`, and `tmp_paths.py --check` prints `0 refused`.
- Roster group count, rule: `len(groups)` of `dev/programme/rosters/wave-r10-groups.json` at origin/main `47147487ba2b`, and the minimum length after the first dash: 151 groups, minimum 2.

## Red checks

- **`instrument-self-tests`** was red at `6ad8089c`: `ref_privacy: REFUSE tools/audit/seat/review_strength.py:854`. It is fixed by the `PUSHERS` entry. The cheaper detector is `python3 -I tools/audit/seat/ref_privacy.py --check`, which takes seconds and was not run before the push. It now prints 0 refused.
- **`pr-contract`** was red at 10:12Z on `6ad8089c`: `check instrument-self-tests is red and ## Red checks does not name it`. It follows from the red above, because the body was written before that check concluded. The cheaper detector is `policy_lint.mjs --pr-body <body> --red <name>`, run once every check on the head has concluded. This body names the red.
- **`nightly-status`** was red at `81d617cec`, `468781122`, `816b1e20f`, `eb9f7e89d`, `6ad8089c1` and `45754ede2`. It grades main's scheduled run, not this diff, which touches nothing it reads. Carry: dismissed: grades main, not this diff
- The 13 `cancelled` runs at `81d617cec` were superseded by the next push within a minute. None failed.
- **Local**, with `PYTHONPATH=tests/hastub` and `PREPR_SKIP_CLOSURES=1`: `tests/closure.py select` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out`. At 3.13 with `tests/requirements-ci.txt`, both pass at the code head: `ALL 2388 ENTITY CHECKS PASSED` and `ALL 109 HARNESS HEADER CHECKS PASSED`. `tests/structure.py` prints `STRUCTURE RATCHET PASSED`, and `tests/closure.py selftest` prints `ALL 112 closure shrink pins PASSED`.

## Forward-carry

- The guardrail is split out of this PR to R10-ORCH-MACHINERY. The orchestrator wrote its two corrected points into that group's brief: commit `c98fb4c27` on `handoff/audit-r10-roster` ("roster_edit append-carry R10-ORCH-MACHINERY") appends a carry citing review/2579 f7a6bdf0c. It states (1) P(X ≤ 4 | n = 30, p = 0.28) = 0.0495, so the 30-PR arm trips at 4 or fewer, and (2) any `ALPHA` the guardrail adopts must be checked at P = 0.0526 (k = 2 of 20). This PR does not edit the roster. Destination: `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-ORCH-MACHINERY (item b8b28b28)

## Friction

none

