Fix review: blocked f6af0c50c47ec3e0d1d6de12e85635eb2cc3d9ca root-cause-unanswered: wave-script and policy-docs went red, unanswered; both are base-pinned graders that cannot pass on the landing PR

bus-nonce: 1d131a974d5c10c0ec7000664cb03af9

Round 2 (round 1 was the cloud reviewer's prep at e35026f6, `handoff/r9-f11-governance-4-review` a0791786; its findings are taken over here). Measured head f6af0c50c47ec3e0d1d6de12e85635eb2cc3d9ca, live head re-read before posting: unchanged. Main at measurement af7660c7. Contract diff `tools/audit/briefs/` merge-base...origin/main: empty.

## Blocking

1. **Three required checks are red at the head, and the body says no CI run exists** (`## Red checks`: "No CI run exists yet at this head"). Commit check-runs API, read by me:
   - `wave-script` failure: the agreement lane runs over readers restored from the base (af7660c7), not the PR's. `REFUSED rule-frontmatter-paths: a reader threw: pl.rulePaths is not a function` (the base `policy_lint.mjs` does not export `rulePaths`; this PR adds it) and `DIVERGENT merge-subject-pr "fix: a squash (#1234)"`: base `resolvePrFromCommit`=null (the D13-s1-01 bug this PR fixes). `RESULT divergent=1 refused=1`.
   - `policy-docs` failure: `field_coverage.mjs` is restored from the base, so e166a15a's three DECLARED entries are not in the copy that runs. `REFUSED registry: pinned .claude/workflows/agreement.mjs / agreement_py.py / tests/structure.py is unregistered`, `refused=3`. e166a15a fixes the refusal only for prepr's unpinned run. The pinned copy CI uses still refuses.
   - `pr-contract` failure: `check wave-script is red and ## Red checks does not name it`.
   I reproduced both lane reds from scratch. I simulated the merge with `git merge-tree` against origin/main (rc 0, no conflict), then restored the files `governance.yml` pins from origin/main. Unpinned lane: `RESULT divergent=0 ... refused=0`, rc 0. Pinned lane: `divergent=1 refused=1`, rc 1. Pinned field_coverage: `refused=3`, rc 1. Evidence: `lane_unpinned.txt`, `lane_pinned.txt`, `fc_pinned.txt`.

   This is more than a missing sentence. The governance.yml comment says "the pull request that lands it runs its own". That holds for `agreement.mjs`, but the readers it loads are pinned from the base, so **the landing PR cannot turn `wave-script` green as wired**. A body answer alone does not unblock it. The fixer must either guard the agreement step until the base carries the lane, as the `field coverage` step already does with "the base does not carry it ... skipped", or get a decision from the orchestrator or tvofi on how a pinned-grader bootstrap lands. The `policy-docs` red has the same bootstrap shape for new pinned inputs. Is that red expected for any PR that extends the pinned list, and is it answered by naming? That is the orchestrator's call to state. The body must name it either way.
   Process note for the RCA seat if this recurs: prepr's new `agreement lane` step runs the lane unpinned, so a local prepr goes green while the pinned CI copy goes red. That is how this reached handoff unseen.

## Round-1 items, re-verified with my own runs at the head

| item | my measurement |
|---|---|
| 1 codeowners_gap | `codeowners_gap.py --check`: `RESULT uncovered_files=0`, rc 0 (round 1: 9 at e35026f6). Fixed. |
| 2 dead-member-liveness boundary | mutant `dead = []` in `structure.dead_members`: `RESULT divergent=1`, rc 1. Unmutated: 0. The probe now detects a reader that stops finding dead members. Fixed. The disclosure that structure.py's counting-rule self-check detects D7-s3-02 itself is in the body. |
| 3 governance-workflow-jobs reads a copy | disclosed in the body and registered `identical:`. Accepted as disclosure. |
| 4 bugclasses I4 lists five pairs | lane prints six pairs, including entity-names. Fixed. |

## Mutation proof (my mutants, `mutants.sh`; `git status` clean after)

| instance | mutant | lane |
|---|---|---|
| D14-s2-03 | `CLASS_GUESS = /^([PI][0-9]+\|new)$/` | divergent=15, rc 1 |
| D13-s1-01 | `resolvePrFromCommit` without the `MERGE_SUBJECT_RE` alternative (merge-commit shape only) | divergent=1, rc 1 (the body's 405 is for its opposite-direction mutant, which I did not re-derive) |
| D11-s1-72 | `_GOV_FILES = [_GOV_WF]` | divergent=4, rc 1 |
| D7-s3-02 | `dead = []` | divergent=1, rc 1 |

Null control at the head: lane `RESULT divergent=0 unregistered=0 dead=0 refused=0`, rc 0, six pairs. `--self-test`: 13 of 13. field_coverage unpinned: `refused=0`.

## The two new commits

- e166a15a, the `'tests/structure*'` glob: git's default pathspec matches `tests/structure.py` and `tests/structure_budgets.json` (`git ls-files`). The `git diff --quiet` guard's path set therefore only grows, and field coverage can only run more often, never be skipped more often. The skip does not widen. The DECLARED entries are fine as content, but see Blocking 1: CI cannot see them on this PR.
- 4a3b49de, the prepr `agreement lane` step: it sits on the body path after `field coverage` and is not reached by `--self-test` or `--version-edit`, the two modes CI runs. `prepr.sh --self-test`: 148 passed, 0 failed, no agreement output. For other PRs it adds a local run of the unpinned lane, which needs full history. That is fine in seat worktrees, but see the process note above.

## Other steps

- Step 7: the body names code head 4a3b49de and the PR head f6af0c50, matching what I measured.
- Step 10: the carry is present in the R9-F11.5 brief on `handoff/audit-r9-fixplan` ("registers the concept in the agreement lane (I4 RCA)"), not only in the ledger. The body checked only the ledger and can say so.
- Step 13: `git merge-tree --write-tree origin/main f6af0c50`: rc 0, no conflict.
- Not run here (numpy is absent): `tests/entities.py` and `tests/harness_headers.py`. `fast (3.14)` was still in progress at posting, so they are uncited.
- Step 6 enumerator: not re-run, because `enumerate.py` is outside the tree. The body's export figures are unverified by me.

Evidence: `evidence/` (HEAD.txt names the head).
