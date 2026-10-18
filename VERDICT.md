Fix review: merge 4a4dee5c0525606ec628856b7f5f8b29a0a26234

bus-nonce: 2843fe84f8299e525446bf530a1361a1

Round 2. Reviewed head `4a4dee5c0525606ec628856b7f5f8b29a0a26234`, which is the authored code head `5359dd138` with origin/main `f1b21daab` merged in. `git diff <mb>...origin/main -- dev/governance/roles/` is empty, so this contract is current. I judged the delta since round 1's `fbba2ccb5` against the round-1 finding.

## Round-1 finding: closed

- **The fix.** The workflow no longer runs porcelain `git diff`. The `scope` job now calls `codeql_scope.py changed`, which runs `git diff --name-only --no-renames BASE...HEAD`. A git failure exits 2. `set -euo pipefail` then fails the step, every leg reads an empty output, and every leg analyzes.
- **RESULT self_test_head.** `codeql_scope self-test: 46 checks, 0 failed` (seat venv, python 3.14.7).
- **RESULT ci_self_test.** The `instrument-self-tests` job at this head prints `46 checks, 0 failed`, including the rename arm's three checks.
- **RESULT rename probe and its null control.** The throwaway repo's `git mv lib.py lib.md` lists `['lib.md', 'lib.py']` through `changed`, so the python leg returns `analyze`. Porcelain `git diff` over the same commit lists `['lib.md']`. That matches my round-1 reproduction. Because the probe is built through `tests/throwaway_git.py`, an inherited `diff.renames` setting cannot change the result.
- **Mutation proof, my own mutants on scratch copies:**

  | Mutant | Result |
  |---|---|
  | `--no-renames` deleted | 46 checks, 2 failed: both rename checks, got `['lib.md']` and `skip`. Matches the body. |
  | `changed` returning 0 on a git failure | 1 failed |
  | `check=False` in `changed_files` | 1 failed |
  | suffix allow-list deleted | 11 failed. Matches the body's re-taken figure. |

- **A surviving mutant, in the safe direction.** `BASE...HEAD` changed to `BASE..HEAD` survives. A two-dot diff against the current base tip lists main's files too, so it widens the list toward analyze. It could drop a file only in the case where main and the PR made the identical change. I note it and do not block on it. It is the same three-dot form round 1 used.
- **RESULT workflow_null_control.** The `scope` log (job 117699131047) shows the new `changed --base` invocation and `analyze: .github/CODEOWNERS changes the analysis itself` for all three legs. `Analyze (actions)` and `Analyze (javascript-typescript)` concluded success after a full analysis.

## Resolution delta

- **RESULT resolution_delta.** `git diff --stat f1b21daab 4a4dee5c0` lists only the PR's own five files: CODEOWNERS, codeql.yml, governance.yml, the delivery row and `codeql_scope.py`. The main merges added nothing else.
- **RESULT merge_tree.** `git merge-tree --write-tree origin/main(003c3731c) 4a4dee5c0` exits 0.

## Other steps

- **Step 7 (head).** The body's Head section names `4a4dee5c0` and its code head `5359dd138`.
- **Step 10 (forward-carry).** The body carries the same rename class to #2406, `handoff/r10-roster-fastpath`. That PR has a blocked verdict on it (comment 6250514050, `level-0-rename-hole`), so the finding is a precondition there and not only in this PR's comments.
  - That verdict names `closure.changed_files` and the `lane_skip` Level 0 skip.
  - The shell-level `git diff --name-only` producers in `tests.yml` (around lines 1888, 2297, 2308 and 2465 at #2406's head) are not named in it.
  - The orchestrator should confirm #2406's re-brief covers them. That PR's fix is described as one `--no-renames` producer.
- **Step 11 (red checks).** RESULT ci_conclusions: at `4a4dee5c0` all 46 check-runs have concluded, 31 success and 15 skipped, with no failure or cancellation (check-runs API). The intermediate commits `accf00130`, `5359dd138` and `3027d062e` have no check-runs (they were pushed together). Round 1's head had no red. The body's "Red checks: none" holds.
- **Step 14 (instruments).** No budget, ratchet, golden or claim moved in the PR's own files.
- **Step 15 (architecture).** `changed` moves the list into the code-owned, self-tested script. No YAML flag is left unpinned. The least-privilege split is unchanged.
- **VERSION, manifest and notes.** None of them is among the PR's files.
- **Unpinned.** The skip arm still has no CI proof at any head, because this PR touches `.github/`. The body discloses this as a projection for the first roster or record head after merge, and I have not verified it.

Evidence: ~/hpo-seats/r10s3/review-2405/evidence-r2/
