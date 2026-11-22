Fix review: blocked 6c5e3d867738e0406ed6eeb0f719ce0a3f047834 mutation-vacuous: round-1 and round-2 block unanswered: tools/ci/selftest_scope.py:1170 (not gaps; not broken), tools/audit/seat/orchestrator_tick.py:2092 and :2101, tools/audit/seat/selftest_absorb.py:141, :188 and :275 survive

bus-nonce: 82bf621dacffbe3689c0e02157b50291

Round: 3. Round 2 blocked head 1ab809af50 on these same survivors, and round 1 blocked head 76f30b596a on them. `review_carry.py 1ab809af50 6c5e3d8677` prints FRESH-REVIEW. Under step 12, this round reviews the delta. That delta is the branch commits e247f929d4, 9c947828a4 and 309c102332, the main merges up to 35c3e31cc9, each prior finding, and the live required checks. Round 3 of 4: under fix-review.md, the fourth round owes a re-cut.

## Block

The delta does not touch the three production files that hold the survivors. `git diff 1ab809af50 6c5e3d8677 -- tools/ci/selftest_scope.py tools/audit/seat/orchestrator_tick.py tools/audit/seat/selftest_absorb.py` is empty. The PR body's `## Mutation proof` and `## Red checks` do not answer or triage any round-1 or round-2 survivor. The reviewer re-ran every mutant in a detached worktree at this head, using the driver ev/mut.py, which is unchanged from round 2. The output is in ev/reviewer-mutants.txt, and each survivor it reports is listed here:

- **M1 `tools/ci/selftest_scope.py:1170`: `not broken` dropped from the absorb guard. SURVIVED** (`selftest_scope self-test: 171 checks, 0 failed`). **M2, same line: `not gaps` dropped. SURVIVED** (171 checks, 0 failed). These two carry the block. Take a run with a wiring gap or a broken trace beside a read that absorb can repair. Under either mutant, `absorb_write` runs, and the `remain` it recomputes never holds gaps or broken traces. So `check_cli` prints `0 refusal(s); ABSORB OWED`, which is the line governance.yml's drift grep accepts. Main's drift step would then pass over a real gap or broken trace. Owed: one `bot_run` case each (a gap, and a broken trace, each beside an absorbable read) asserting rc 1 and no `ABSORB OWED`, with both mutants killed.
- M5 `orchestrator_tick.py:2101`: `int(ahead) > 0` changed to `>= 0`. SURVIVED (391 checks, 0 failed). No case has the standing ref level with main. Add one, or triage the mutant as equivalent and give the reason.
- M6 `orchestrator_tick.py:2092`: the `name.endswith(SELFTEST_JOB)` test dropped. SURVIVED. Pin the lane name with a case, or triage it.
- M9 `selftest_absorb.py:141`: the jobs-page guard `total_count > len(jobs)` changed to `if False:`. SURVIVED (`selftest_absorb self-test: 44 checks, 0 failed`). Without the guard, a run whose instrument-self-tests job falls off the first page of the jobs API reads as unmeasured, and the window walks past a red run.
- M8 `selftest_absorb.py:188`: `rc != 0 or` dropped. SURVIVED. Near-equivalent. Triage it or pin it.
- M7 `selftest_absorb.py:275`: `if rc != 1:` changed to `if rc == 2:`. SURVIVED. Near-equivalent, since it never yields VERIFIED. Triage it or pin it.
- M10 `selftest_absorb.py:262`: `"--no-renames"` dropped. It survives the selftest_absorb self-test (44/0), but `tests/closure.py selftest` kills it (`1 of 118 closure shrink pins FAILED`, ev/m10-closure.txt). This is not a block.
- M11 `selftest_absorb.py:314`: `stop_on_signal()` dropped. It survives the selftest_absorb self-test (44/0). Round 2 showed that `pr_args.sh`'s `pr_pushers` census kills it, and the delta leaves both files unchanged. This is not a block.

## Evidence

- Head measured: 6c5e3d867738e0406ed6eeb0f719ce0a3f047834 (ev/HEAD.txt). The body's `## Head` names it.
- `git merge-tree --write-tree origin/main 6c5e3d8677` gives rc 0, tree eafb34234056, with no conflict (ev/merge-tree.txt).
- The 22 three-dot paths from 35c3e31cc9 are in ev/three-dot-paths.txt. None of them is `VERSION`, `RELEASE_NOTES.md`, a claim file or a `custom_components/` path.
- CI: `merge_train.py classify 6c5e3d8677 --pr 3834` prints `GREEN 6c5e3d867738e0406ed6eeb0f719ce0a3f047834 pending: none red: none` (ev/classify-last.txt, ev/classify.log). The `merge_train.py owed-reds` output is in ev/owed-reds.txt. The heavy gate and the mutation table were not re-run.
- Delta figures re-derived at the head. `node tools/policy/policy_lint.mjs` prints `TOTAL: 0 error(s) across 58 policy file(s)`. `--budgets` shows fix-review.md at 2774 against a cap of 2775, matching the body (ev/policy-lint-head.txt). `review_packet.py --self-test` prints `133 checks, 0 failed`, so 309c102332 restores the step-12 pin that turned 9103b628 red (ev/review-packet-selftest.txt). The body's doc_claims figure `ALL 441 checks PASSED` was not re-run in this round.
- Policy delta: 9c947828a4 and 309c102332 reword fix-review.md to fit its cap. 309c102332 restores "Other deltas never widen it." The body routes this through the owner's approval under mandate 6893738184. This reviewer does not judge that approval.
- The body's red-check answers for runs at 76f30b59, 1ab809af and 9103b628 are each present. All three reds are fixed on the branch, and no required check is red at this head.
- Body figure: `## Figures` still quotes `selftest_scope.py --self-test` as `159 checks`, and `selftest_absorb.py --self-test` as `41 checks`. At this head the counts are 171 and 44 (the driver tail lines in ev/reviewer-mutants.txt). The body's figures are stale.
- Finder's harness: none. The PR is a process countermeasure (R11-RCA-SELFTEST-TABLE-DRIFT), and its fixtures were re-run in round 1. This delta does not change them.
