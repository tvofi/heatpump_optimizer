_Requested by **tvofi**_

Main is red at 8fa06663: #1854's check "no job-level `if` leads with `always()`" refuses `mutation-ledger` and `mutation-ledger-push`, which #1848 brought in with `always() &&`. This swaps the leading `always() &&` for `!cancelled() &&` in exactly those two jobs and keeps the rest of each condition. Semantics: a status function in an `if` replaces the implicit `success()`, so `!cancelled()` behaves as `always()` for a skipped or failed `needs` -- `mutation-ledger` still runs when `recheck-gate` is skipped -- and differs only on a cancelled run. The push job still requires `needs.mutation-ledger.result == 'success'`. `tests/entities.py`'s reach evaluator `_gh_eval` knew only `always()`, so it now reads `!cancelled()` as true too, as its sibling evaluator at the `_ci_if_true` site already did (one line, same line count).

Part of #201

## Head

dae329dea8bf8dada73491dcef8d657e3825f16f, on `handoff/r9-hotfix-ledger-cancel`.

## Mutation proof

The mutant is the baseline: origin/main 8fa06663 is the two lines reverted. `PYTHONPATH=tests/hastub ~/hpo-seats/R9-F11.4-venv/bin/python3 tests/entities.py` at 8fa06663 prints `FAIL no job-level `if` leads with `always()`: a cancelled run stops (CI cancel)  [['tests.yml:mutation-ledger', 'tests.yml:mutation-ledger-push']]` and `1 of 2071 ENTITY CHECKS FAILED`, rc=1. At the head it prints `ALL 2071 ENTITY CHECKS PASSED`, rc=0. A first attempt that changed only the workflow turned that check green and another red (`a branch-ref dispatch reaches neither mutation-ledger nor mutation-ledger-push ... NameError: name 'cancelled' is not defined`), which is why the evaluator line is in the diff.

## Null control

The unmodified tree (8fa06663) is red on exactly that one check, run in a detached worktree of origin/main beside the fix. The check's own null control (a planted leading `always() && a` is refused, `!cancelled()` is not) is the `ok` line right after it.

## Figures

- one failing check at 8fa06663, none at the head: `PYTHONPATH=tests/hastub ~/hpo-seats/R9-F11.4-venv/bin/python3 tests/entities.py` (last line).

## Red checks

Main's `tests` job on `entities.py`, red at 8fa06663. Cheaper detector: none that runs before the merge. See Root cause.

## Forward-carry

none

## Friction

none

## Root cause

**Cause.** Two pull requests, each green on its own base, composed into a red main. #1854 (merged 5f87e25a) added the refusing check; #1848 (merged at 8fa06663) added two jobs that the check refuses. Neither PR touched the other's lines; the conflict is semantic and exists only in the merge.

**Process state: (d)** -- the process (grade a PR at a head containing current main) was sound and its precondition changed underneath it: main gained a new rule after #1848's CI ran, and nothing noticed that #1848's head no longer contained main.

**Why no gate caught it.** A PR is graded on its own base, not on the merge with a sibling that merges first. `git merge-base --is-ancestor 5f87e25a 9a096055` returns 1: #1848's merged head 9a096055 is a merge of main at 948671af, which precedes #1854; and #1854 is not in it. `mergewhen.sh` (`~/hpo-seats/bin/mergewhen.sh`) waits for GitHub's `CLEAN` plus no running check at the named head, then merges with `--match-head-commit`; it never compares the head with `origin/main`, and the ruleset does not require branches to be up to date. So #1848 merged at a head based before #1854.

**Would `merge_fastpath` / `update-branch` re-grading have caught it?** `update-branch` yes: a re-graded #1848 at a head containing #1854 runs the new check and goes red. `merge_fastpath.py` is not the instrument: it is an exemption from re-grading, and it refuses class `workflow` (either side touches `.github/`) -- #1854 and #1848 both changed `tests.yml` -- so it would have returned `FASTPATH REFUSED` and sent the PR to update-branch. But `mergewhen.sh` does not call it and does not demand an up-to-date head, so neither ran.

**Countermeasure: recorded, not built here.** The cheap detector is two lines in the orchestrator's `mergewhen.sh` (outside the repository): before merging, refuse when `git diff --name-only <head> origin/main -- .github/ tests/entities.py` is non-empty, i.e. main moved a gate file since the head, and run `update-branch`. Cost test: standing cost is one `git diff` per merge, under a second, and a forced re-grade only when main changed a gate file after the head -- one full CI run when it fires (the rate is the number of gate-file merges inside one PR's review window; two this round). Cost of the defect: one red main and a blocked stamp, plus this PR's round trip. One occurrence does not reach the recurrence trigger (about three), and the script is not repository policy, so it goes to the orchestrator as a proposal rather than into this diff; the repository-side change (a required up-to-date rule in the ruleset) is policy and the owner's call.

## Approval

`.github/workflows/tests.yml` is code-owned. The approval comes under tvofi's mandate (round-9 mandate, `r9-mandate-20261002`, session-only): CODEOWNER approval of this PR is the owner's, given through the mandate, not claimed here.
