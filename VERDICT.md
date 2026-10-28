Fix review: blocked b79c3d4f69bb603ec559ceb2f19f974c917b72f3 retry-rule-unsound: urllib_wait retries a 404/401/422 that carries x-ratelimit-remaining: 0, four calls where the stated rule says one

Round 2 review of PR #2639 (R10-FLY-GH-READ-RETRY PR 2 of 2), measured at b79c3d4f69bb603ec559ceb2f19f974c917b72f3 in a detached worktree. I re-read the branch head before writing this, and it is still b79c3d4f69bb603ec559ceb2f19f974c917b72f3 (ev/head-recheck.txt). The merge base is origin/main 4200ea4c4, so the branch is 0 commits behind. dev/governance/roles/ shows no diff against main.

## Blocking

1. **The retry rule retries a 4xx (brief check 2).** `gh_read.urllib_wait` checks `x-ratelimit-remaining == "0"` before it checks the status (gh_read.py:106-109, ev/urllib_wait_excerpt.txt). So any HTTPError whose headers carry a spent bucket and a near reset gets the wait-and-retry arm, whatever its code. GitHub sends the rate-limit headers on every response, so this happens whenever the request that spends the last token returns its real status. Planted against the head's module (ev/plant.py, ev/plant.txt):
   - `RESULT plant=404 calls=1`: correct.
   - `RESULT plant=404_bucket0 calls=4 sleeps=[9.13, 15, 45] why='(after 4 attempts)'`: wrong. The same holds for 401, 422 and a permission 403, because that arm never reads the code.

   This contradicts the rule as INSTRUMENTS.md:329-331 states it ("every other failure (401, a permission 403, 404, 422 ...) after its one call") and as the body states it ("everything else refuses after its one call"). It also contradicts the body's "a spent bucket ... is never put on the schedule": settles 2 and 3 are the 15/45 schedule. The exposure is `record_row._api`; merge_train's path goes through `gh_wait`, which sees no headers. The cost per occurrence is bounded, at most four reads and 65 s, but the brief asked for exactly this check. The fix is small: consult the bucket only for 403/429 (the primary-limit shapes), then add a self-test row for a 404 with `remaining: 0` that makes 1 call.

2. **pr-contract is red at this head (check-run 120222982188), and the body does not answer it.** The body lint printed `ERROR [pr-body] ... check `nightly-status` is red and `## Red checks` does not name it`. That pr-contract run started at 03:25:13Z, after nightly-status concluded red at 03:25:12Z. nightly-status (120222854965) reads `NIGHTLY RUNNING: no scheduled run has CONCLUDED; run 39890399205 ... still in_progress`. That cause is not this diff's, but `## Red checks` must name it, because governance.yml is in the diff. This is a body-only repair, owed together with item 1.

## What passed (RESULT lines)

- **Round-1 causes are named in the code and dispositioned, not loosened:**
  - merge_pr.sh:166-168 names the ImportError.
  - PR_PUSHERS gains a `mention` row, and the census rule is unchanged.
  - ref_privacy PUSHERS gains a `fixture` row, and `_SITE` is unchanged.
  - I confirmed gh_read.py starts no subprocess (it has no subprocess or os import), so the "mention" and "fixture" dispositions are true.
- **Mutants that put each fix back** (ev/mutants.txt), each restored with `git diff --quiet` passing:
  - M-E: merge_pr `18 checks, 1 failed` on the exact CI line ("null control ... STALE").
  - M-F: pr_args `93 checks, 1 failed`.
  - M-G: ref_privacy --check `2 refused`.
- **The merge_pr null control is still honest:** it greps exactly `pr merge 42 --merge --match-head-commit $msha` (merge_pr.sh:200), it is red under M-E, and its refused-merge sibling arm passes.
- **My own mutants on the rule** (ev/mutants.txt), all killed:
  - Bound removed (`if n == READ_TRIES` -> False): `2 failed`.
  - READ_TRIES 4 -> 5: `5 failed`.
  - 4xx made transient: `19 failed`.
  - Wait cap removed: `2 failed`.
  - `is_read` field/input write test removed: `9 failed`.
  - Train.run wrapper removed: merge_train `229 checks, 5 failed`.
- **Planted failures** (ev/plant.txt):
  - A 404 takes 1 call, and so do 422 and a permission 403.
  - A 500 takes 4 calls with settles 5/15/45, then "(after 4 attempts)". A 500 twice and then 200 is answered on call 3.
  - A secondary-limit 403 and a URLError are both transient.
  - `is_read` refuses -X PATCH, -fbody=1, --input and `gh pr merge`, and accepts GET and `gh pr view`.
  - Apart from item 1, every arm behaves as stated.
- **Self-tests at head** (ev/selftests.txt, /opt/hpo/venv-ci, Python 3.14). These match the body's figures:

  | instrument | result |
  |---|---|
  | merge_train | 229 checks, 0 failed |
  | queue_pre_flight | 43 checks, 0 failed |
  | gh_read | 112 checks, 0 failed (`self_test()` returned 0) |
  | record_row | all checks passed |
  | app_approve | 254 checks, 0 failed |
  | merge_pr | 18 checks, 0 failed |
  | pr_args | 93 checks, 0 failed (`--pushers` rc=0) |
  | ref_privacy self-test | 66 checks, 0 failed |
  | ref_privacy --check | 25 files, 12 guarded, 0 refused |

  ref_privacy --check judged 1161 added lines since 4200ea4c4; the body's 1160 was taken against e30b24bbc.
- **The other checks at head:** structure.py prints `STRUCTURE RATCHET PASSED`. `carry_audit.py pr 2639` prints `4 routed, 0 unrouted, 0 bad`, which matches the brief.
- **The merge with main is clean:** `git merge-tree --write-tree origin/main b79c3d4f69bb603ec559ceb2f19f974c917b72f3` gives rc=0 with no conflict (ev/merge-tree.txt).
- **CI at head** (one bulk check-runs read, ev/check-runs.tsv):
  - instrument-self-tests 120222854741 is **success**, so round 1's red is cleared.
  - Red: pr-contract 120222982188 (item 2) and nightly-status (not this PR's cause).
  - Still in progress when I read them: closures, coverage, fast (3.14), Analyze (python).
- **Code-owned paths:**
  - tools/pr/app_approve.sh is **not** code-owned, which confirms the brief.
  - The diff does touch two owned paths: `.github/workflows/governance.yml` (`/.github/workflows/`) and `tests/closure.py`. So the merge needs @tvofi's approving review (already requested).

## Not re-derived

- The sweep's `mutants=524 killed=494 equivalent=30 survivors=0`: this is a heavy run, so I cite it and did not re-run it.
- The 72-command job run: CI's instrument-self-tests is green and covers it.
- The archscore dS line.

This is round 2.

bus-nonce: 369e5c9b438daa3ce602c8037eff8aa2
