Fix review: merge 60a26fee42f52571c681410c27e14a98415a9132

bus-nonce: 9d66d887932c9c32cb8e6dbf846ce9fc

## Scope

Delta review (owner ruling 2026-11-09) of `git diff c9ba955f30fc8f64b2e0c3865dcfe9dd609ef822 60a26fee42f52571c681410c27e14a98415a9132`: one content commit, 419fa71b5 "Gate the survivor-list self-test step on its own scope output", plus merges of origin/main. Round: eighth verdict on this PR, the second delta round after a merge verdict at c9ba955f; the previous four rounds ended in `merge`, so no re-cut is owed by this round's outcome.

## Previous verdict's finding

The merge verdict at c9ba955f (probe/rev-3341-7995f8f3) recorded one finding: the survivor-list step had no id and an unconditional `if:`, so `selftest_scope.py static` refused it as UNGATED and `governance / instrument-self-tests` went red. Resolved at this head: the step now has `id: survivor-list`, it reads `steps.scope.outputs.survivor-list`, and the closure is recorded in `tools/ci/selftest_closures.json`. `governance / instrument-self-tests` is green at the head.

## Evidence

- Finder's harness (`python3 -I tools/ci/selftest_scope.py static`) at both ends (`ev/static-both-ends.txt`): at c9ba955f it gives rc 1, `UNGATED step 'Show the survivor-list check ...'`, 107 gated steps, 1 problem. At 60a26fee42f52571c681410c27e14a98415a9132 it gives rc 0, 109 gated steps, 0 problems.
- Mutants on the gating change at the head (`ev/mutants-gating.txt`). Each one makes static refuse, and the tree was restored after each (`git status` clean):
  - M1 restores c9ba955f's `if: ${{ !cancelled() }}`. Result: UNGATED + STALE, 2 problems.
  - M2 makes the step read another step's output (`verdict-audit`). Result: UNGATED + STALE.
  - M3 drops the `survivor-list` entry from `selftest_closures.json`. Result: `STALE ... missing ['survivor-list']`.
  - M4 changes the step's run text. Result: `STALE ... run text changed ... ['survivor-list']`, which shows that run_sha is pinned.
- Selection and null control (`ev/mutants-gating.txt`):
  - `select --change M:tests/mutation_table.py` runs survivor-list.
  - `select --change M:tools/audit/seat/survivor_list.py` runs survivor-list.
  - `select --change M:README.md` (null control) does not select it: `MODE: SCOPED -- 17 step(s) run` with no survivor-list line.
- Closure re-derived: `selftest_scope.py record --step survivor-list` under strace at the head gives an entry byte-equal to the committed one (`re-recorded == committed: True`, `ev/record-survivor-list.txt`). `survivor_list.py --self-test` reports 20 checks, 0 failed.
- Merges: the branch's own three-dot diff at c9ba955f and at the head differ only by 419fa71b5's two hunks (`ev/branch-diff-delta.txt`). The `custom_components/` changes in the range (de.json, the card .js) come in from main and are not in the branch's diff, so there is no production-code delta and the review was not widened.
- Merge with main: `git merge-tree --write-tree origin/main 60a26fee42f52571c681410c27e14a98415a9132` gives rc 0, no conflict, against origin/main 5ab6030d (`ev/merge-tree.txt`).
- CI: `merge_train.py classify 60a26fee42f52571c681410c27e14a98415a9132 --pr 3341` returned rc 2, `REFUSE ci: the check runs at 60a26fee42f5 could not be read` (`ev/classify.txt`), so its read is unreadable from this seat. The cause is that its `gh api --paginate` follows a next-page link of the form `repositories/{id}/...`, which this cloud proxy refuses with HTTP 403. The head has 108 runs, so a second page exists. I read the check runs page by page through `repos/{owner}/{repo}` instead (`ev/check-runs-live.tsv`): 108 runs, 67 success, 41 skipped, 0 failure, 0 pending.
- Owed reds: `merge_train.py owed-reds` lists the required set (`ev/owed-reds.txt`). Each required context is completed, and each is success except `tests / ci-ratchet`, which is skipped (`ev/owed-set-state.txt`). There are no reds, so no `## Red checks` answer is owed.
- `dev/governance/roles/` is unchanged between the merge base and origin/main, so the contract I applied is current. VERSION, the manifest and RELEASE_NOTES are not touched by the branch. The PR head is still 60a26fee42f52571c681410c27e14a98415a9132 (`refs/pull/3341/head`), and the body's `## Head` names it.

## Findings

None.
