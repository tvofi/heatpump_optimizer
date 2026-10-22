Group: R10-FLOW-YIELD-PROBE

Pinned pack file: `dev/programme/flow-study/roster/groups/R10-FLOW-YIELD-PROBE.json` at pack commit 78117030 on branch `claude/dazzling-gauss-7l3u2b`.

R10-FLOW-YIELD-PROBE (owner ruling R13, expedite): why real-catch blocks per reviewed PR fell from 0.52 to 0.15, and a recommended threshold for the review-strength guardrail. The study record is `dev/audit/rounds/round10/D13/yield-probe.md`; the enumerator behind every figure is `tools/audit/seat/review_strength.py` (bus read over git only, fact strata taken `--as-of` the latest window's until, self-tested and wired into `governance.yml` `instrument-self-tests`). No production code, budget, `VERSION`, manifest or claim file is touched.

Round 3 body, re-cut minimal under the three-round rule: the diff, the figures and the mutation table.

**This round's diff** (`git diff 889c39e59 573d5cbff`, `tools/audit/seat/review_strength.py` self-test only, +27 lines): seven fixture checks, 24 → 31. Plus `tests/closures.json` +1 line (commit `aba00fbf2`): the `INERT READS` entry for `tools/audit/seat/review_strength.py` under `tests/entities.py`, written by `python3 tools/pr/ci_predict.py --base origin/main --apply-inert` after the predictor predicted a `closures` red for it against `5a755f53efda`; afterwards it prints `CI PREDICT: no closures or fast red predicted against 5a755f53efda`.

- PR 7 merged twice (20 lines, then 700 more) from branch `fix/r1-fix-pr`: its size reads the newest merge, `L>=600`.
- PR 7 joins, with `-pr` stripped, to roster group R1-FIX, which lists `fixes` alone: fixer `haiku`, origin `finding`.
- PR 7's verdict is confirmed on `verdict/7` by id `seat-7-cloud`: reviewer `cloud`.
- A guardrail at N=3 over six PRs: the latest three (5, 6, 7) read 1/3, the oldest three (1, 2, 3) would read 2/3.
- `as_of(main, 10-02T12Z)` resolves to first-parent `m1`, never side-branch `c2` (10-02T03Z), which is dated nearer T.
- PR 6's branch adds 200 lines to its own delivery row: excluded, so its size stays `S<150`.
- A verdict exactly at a window's until (PR 2's block at 04:00) is excluded.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_015LvCRXFLR1MXCcuxXZfV6R

## Head

`eb9f7e89d0b258ca66a8d9757df0156a776b7332` merges the authored code head `aba00fbf2f367b134c73d7404c344dc673859c88` and then merges origin/main `46e368127` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

The code head is `aba00fbf2f367b134c73d7404c344dc673859c88` (self-test commit `573d5cbff`, then the closures entry). It merges `origin/main` at `5a755f53efda8c099af7d6a98fb0b22828a0593c` into the reviewed head `816b1e20fdfd0a4b99bcc2b81361b70bd3007acb` (merge `889c39e59`, never a rebase; one conflict in `.github/workflows/governance.yml`, resolved by keeping both main's new step and this PR's review-strength step). Measured 2026-10-21T22:30Z (`date -u`).

The fix review's items:

- R2, the 600-line cut: killed by the PR 7 size check. Carry: dismissed: fixed in this pull request (item a1f0c2e1)
- R4, the guardrail's last-N slice: killed by the six-PR guardrail check. Carry: dismissed: fixed in this pull request (item b72d4e93)
- R5, `--first-parent` in `as_of`: killed by the `m1`/`c2` check. Carry: dismissed: fixed in this pull request (item c3e85a07)
- The self-test cases R2, R4 and R5 owed in round 3: landed. Carry: dismissed: fixed in this pull request (item d4a96b18)
- The six figure-neutral survivors R7, R8, R9, R13, R14, R15: each pinned by a case, none dismissed (table below). Carry: dismissed: fixed in this pull request (item e58b7c24)
- The `pr-contract` red at 816b1e20 (run 39681234360): answered under Red checks. Carry: R10-FLY-GH-READ-RETRY (item f6093d35)

## Mutation proof

Each mutant edits one predicate of `review_strength.py` by an exact one-occurrence string replacement, runs `python3 tools/audit/seat/review_strength.py --self-test`, and restores; after all of them the file is `filecmp`-identical to a saved copy (`restored identical: True`). Unmutated (M0): `review_strength self-test: 31 checks, 0 failed`.

| mutant | edit | result | failing check |
|---|---|---|---|
| R2 | `lines < 600` → `lines < 100000` | 1 failed | size: PR 7 merged twice reads its newest merge (700 lines, L>=600) |
| R4 | guardrail `[-n:]` → `[:n]` | 1 failed | guardrail: the LATEST N by first verdict (5, 6, 7: 1/3), not the oldest (1, 2, 3: 2/3) |
| R5 | `--first-parent` removed from `as_of` | 1 failed | as of: --tree resolves to its first-parent commit (m1), never side-branch c2 dated nearer T |
| R7 | delivery-row exclusion → `if True:` | 1 failed | size: merged PR 5 reads its merge diff (160 lines, M<600); unmerged 6 its verdict head (20, S<150) |
| R8 | `and int(m[1]) not in merges` removed (oldest merge wins) | 1 failed | size: PR 7 merged twice reads its newest merge (700 lines, L>=600) |
| R9 | `or rid.endswith("-cloud")` removed | 1 failed | bus-confirmed *-cloud id marks the verdict cloud |
| R13 | `or grp.get("fixes")` removed | 1 failed | origin: a group listing fixes alone is finding |
| R14 | `branch.removesuffix("-pr")` removed | 2 failed | join: merge branch fix/r1-fix-pr, -pr stripped, finds R1-FIX's resume.branch (fixer haiku); origin: a group listing fixes alone is finding |
| R15 | window `< b` → `<= b` | 1 failed | window: [from, until) excludes a verdict at until (PR 2's block at 04:00) |

The earlier rounds' mutants (M1–M8, P1–P7, and the reviewer's killed R1, R3, R6, R10, R11, R12) touch predicates this diff does not change; their checks are all among the 31 and pass at M0.

## Null control

- The mutation table's null is M0: the same runner over the unmutated file prints `31 checks, 0 failed`, so each failure above is the mutant's.
- Each new case's null is the mutant it kills: a case that did not separate the two predicates would have printed `0 failed` for that mutant, as R2, R4 and R5 did at 816b1e20 (`24 checks, 0 failed`).
- The figures' null is unchanged: the tool reproduces the study's hand-taken baselines, 112 PRs / 0.52 (58) and 47 PRs / 0.15 (7), below.

## Figures

Every figure re-measured at `573d5cbff` (the closures commit after it changes no file the tool reads) between 22:20Z and 22:30Z. The bundle: `python3 tools/audit/seat/review_strength.py --fetch --window E=2026-10-15T12:37Z..2026-10-19T14:50Z --window L=2026-10-19T14:50Z..2026-10-21T14:50Z --window P1=2026-10-15T12:37Z..2026-10-18T08:00Z --window P2=2026-10-18T08:00Z..2026-10-19T14:50Z --window L1=2026-10-19T14:50Z..2026-10-21T13:00Z --window S=2026-10-21T13:00Z..2026-10-21T15:15Z --by kind --by prior-merge --by origin --by size --by product --by fixer --by class --by kind+origin --roster origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json`. It prints `facts as of 2026-10-21T15:15Z: tree e7c664856776 roster 2c76c3128bf6` (unchanged: both refs are resolved at 15:15Z, so neither main's nor the roster's later commits move them).

- Baselines: `--window A=2026-10-15T12:37Z..2026-10-21T11:00Z` prints `PRs 112 ... real 58 (0.52/PR) book 65 (0.58/PR)`; the bundle's `all L` row `PRs 47 ... real 7 (0.15/PR) book 30 (0.64/PR)`; `--window A=2026-10-19T11:00Z..2026-10-21T11:00Z` prints `PRs 35 ... real 2 (0.06/PR)`.
- `--window L13=2026-10-21T13:00Z..2026-10-21T14:50Z`: `PRs 11 verdicts 16 real 4`.
- `all` rows: P1 0.90 (43/48), P2 0.36 (14/39), L1 0.08 (3/39), S 0.36 (5/14); incidence 25/48, 10/39, 3/39, 4/14.
- Strata (P1 / P2 / L1): finding 1.08 (40/37), 0.29 (5/17), 0.08 (1/13); `L>=600` 1.10 (22/20), 0.69 (11/16), 0.08 (1/13); product True 1.21 (17/14), 0.22 (2/9), 0.14 (1/7).
- Re-weights 0.50, 0.89, 0.85: L1's per-stratum PR counts times P1's per-stratum real/PR over 39, from those rows (the rows are unchanged, so the products are).
- Reviewer kind real/PR: cloud 6/31 (P2), 3/24 (L1), 5/14 (S); local 43/48 (P1), 8/14 (P2), 0/20 (L1). P2 cloud+finding 3/13, local+finding 2/8.
- Fixer first-pass (P1 / P2 / L1): opus 7/22, 2/14, 5/7; sonnet 5/15, 0/3, 3/6.
- Prior-merge: `after-a-merge-verdict` 0 real in every window; 22 verdicts in E, 12 in L; `--window A=2026-10-15T12:37Z..2026-10-21T11:00Z --by prior-merge` prints `after-a-merge-verdict A PRs 22 verdicts 33 real 0`.
- Classes (P1 / P2 / L1): `harness` 25 / 3 / 2; `carry-missing` 3 / 15 / 7.
- Extended list (`--real-extra regression,flaky-arm,claim-false,control-failed,claim-refuted,rule-dropped,null-control-false,red-at-head,tests-red`, windows P1, P2, L1, S, POST=2026-10-18T08:00Z..2026-10-21T15:15Z, `--by kind`): P2 0.49 (19/39), L1 0.21 (8/39); cloud incidence 8/31, 7/24, 4/14; local L1 0/20; POST incidence 24/85.
- Back-test: the extended list with `--guardrail 30 --p0 0.28` at ten `until` points, 2026-10-20T01:00Z to 2026-10-21T13:00Z in 4-hour steps (W from 2026-10-15T12:37Z): incidence 8, 8, 8, 8, 7, 7, 6, 5, 5, 5 of 30; every line `ok`, the lowest 5/30 at P = 0.116. (Round 2's maximum 19/30 lay at earlier cut points not swept here, so it is not quoted.)
- Self-test: `review_strength self-test: 31 checks, 0 failed`. Wiring: see Red checks.

## Red checks

None locally at `aba00fbf2` (`PYTHONPATH=tests/hastub`, `PREPR_SKIP_CLOSURES=1`, the CI venv interpreter). `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out` (`tests/entities.py`, `tests/harness_headers.py`): `ALL 2382 ENTITY CHECKS PASSED`, `ALL 109 HARNESS HEADER CHECKS PASSED`. Also `tests/structure.py` `STRUCTURE RATCHET PASSED`; `tests/closure.py selftest` `ALL 124 closure shrink pins PASSED`; `tests/env_drift.py --claims-only <merge base>` rc=0; `tmp_paths.py --check` 0 refused; `selftest_wiring.py --check` `73 self-testing, 73 wired, 0 unwired`; `ci_predict.py --base origin/main` no predicted red. CI has not run on this head: the orchestrator pushes it to the PR.

- **`pr-contract` at 816b1e20 (run 39681234360, job 119504172159).** Its "Read the body off the API" step got non-JSON from `gh api` ("invalid character 'S' looking for beginning of value"), and every later body step failed on the missing body file; the sibling run 39681233356, a second earlier on the same head and body, passed. It is a transient read, not this diff: the diff touches no `pr-contract` reader. The cheaper detector is a retry around that read, the class owned by R10-FLY-GH-READ-RETRY. No run exists yet at `aba00fbf2` to read against; the orchestrator's push starts one. Carry: R10-FLY-GH-READ-RETRY (item f6093d35)
- **`nightly-status`** grades `main`'s scheduled run, not this diff, which touches nothing it reads. Carry: dismissed: grades main, not this diff (item 2579n1)
- **`ci-ratchet` on main** is runner-speed variance. Carry: R10-CI-LAYOUT (item 2579c1)

## Forward-carry

- The guardrail threshold, extended class list, seat-family arm and planted-defect calibration are on R10-ORCH-MACHINERY's roster carry (round 2, confirmed by the reviewer at `c9140d299f9c`); the reviewer-model-in-dispatch control is routed to the same group. Destination: `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-ORCH-MACHINERY (item b8b28b28)

## Friction

none

