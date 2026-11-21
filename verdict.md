Fix review: blocked 1ab809af502ca1fbaae511e00d39a442ec809d37 mutation-vacuous: round-1 block unanswered: tools/ci/selftest_scope.py:1170 (not gaps; not broken), tools/audit/seat/orchestrator_tick.py:2092 and :2101, tools/audit/seat/selftest_absorb.py:141, :188 and :275 survive

bus-nonce: 591ec4059cf6ce0efc06164e27dc8a28
pending-ci: gate

Round: 2. Round 1 blocked head 76f30b596a. `review_carry.py 76f30b596a 1ab809af50` prints FRESH-REVIEW. Under step 12 this round reviews the delta: commits 880f254423 and 1ab809af50, each prior finding, and the live required checks.

## Block

The round-1 block was on mutation survivors. Neither delta commit touches `tools/ci/selftest_scope.py` or `tools/audit/seat/orchestrator_tick.py` (`git diff --quiet 76f30b596a 1ab809af50 -- <both>` exits 0). The PR body's `## Red checks` answers the CI reds of run 44939954319, but it does not answer or triage the round-1 survivors. The reviewer re-ran every round-1 mutant at this head, in a detached worktree, with the driver ev/mut.py; the output is in ev/reviewer-mutants.txt. Each survivor below is reported by that driver:

- **M1 `tools/ci/selftest_scope.py:1170`, `not broken` dropped from the absorb guard: SURVIVED** (`selftest_scope self-test: 171 checks, 0 failed`). **M2, same line, `not gaps` dropped: SURVIVED** (171 checks, 0 failed). These carry the block, as in round 1. Under either mutant, take a run with a wiring gap or a broken trace beside an absorbable read. `absorb_write` runs, and the `remain` that `drift()` recomputes never contains gaps or broken lines. So `absorbed` is True, and `check_cli` prints `0 refusal(s); ABSORB OWED`, which is the line governance.yml's drift grep accepts. Main's drift step would then go green over a gap or a broken trace. Owed: a `bot_run` case for each (a gap, and a broken trace, each beside an absorbable read) that asserts rc 1 with no `ABSORB OWED`, and each mutant killed.
- M5 `orchestrator_tick.py:2101`, `int(ahead) > 0` to `>= 0`: SURVIVED (391 checks, 0 failed). No case has the standing ref level with main. Add one, or triage the mutant as equivalent with its reason.
- M6 `orchestrator_tick.py:2092`, the `name.endswith(SELFTEST_JOB)` test dropped: SURVIVED. Pin the lane name with a case, or triage it.
- M9 `selftest_absorb.py:141` (round 1's :109), the jobs-page guard `total_count > len(jobs)` to `if False:`: SURVIVED (`selftest_absorb self-test: 44 checks, 0 failed`). The fixture at :362 plants `total_count: 2`, but no check fails without the guard. The instrument page still claims "one mutant per branch".
- M8 `selftest_absorb.py:188` (round 1's :155), `rc != 0 or` dropped: SURVIVED. It is near-equivalent. Triage it or pin it.
- M7 `selftest_absorb.py:275` (round 1's :242), `if rc != 1:` to `if rc == 2:`: SURVIVED. It is near-equivalent: it never yields VERIFIED. Triage it or pin it.

The round-1 policy finding is resolved. `node tools/policy/policy_lint.mjs` at this head prints `TOTAL: 0 error(s) across 58 policy file(s)`, and `--budgets` shows fix-review.md at 2775 against a cap of 2775 (ev/policy-lint-head.txt, ev/head-figures.txt).

Two of the delta's own production lines were mutated. Each is killed by the check the body names:
- M10, `"--no-renames"` dropped from `verify`'s diff: the selftest_absorb self-test still passes (44/0), but `tests/closure.py selftest` exits 1 (`1 of 118 closure shrink pins FAILED`) (ev/m10-closure.txt).
- M11, `stop_on_signal()` dropped from `main`: `pr_args.sh`'s `pr_pushers` prints `OPEN tools/audit/seat/selftest_absorb.py runner-py: a stop SIGKILLs or orphans its tool` (ev/m11-census.txt).

This is round 2 of 4. If the survivors stay unanswered, the next block on the same mutants is the third round, and from the fourth `fixer.md` owes a re-cut.

## Evidence

- Head measured: 1ab809af502ca1fbaae511e00d39a442ec809d37 (ev/HEAD.txt). The body's `## Head` names this head.
- `git merge-tree --write-tree origin/main 1ab809af50`: rc 0, no conflict (ev/merge-tree.txt).
- The three-dot paths from 63c6d1cff9 are in ev/three-dot-paths.txt. None of them is `VERSION`, the manifest, `RELEASE_NOTES.md`, a claim file or a `custom_components/` path.
- Delta figures re-derived at the head (ev/head-figures.txt): `tests/closure.py selftest` gives `ALL 118 closure shrink pins PASSED`; `check-wave-script.mjs` gives `298 passed, 0 failed`; `selftest_scope_mutants.sh --self-test` gives `SELFTEST-SCOPE MUTANTS: every mutant refused`; `throwaway_git.py --check` gives `0 raw git init or clone site(s) refused`; `selftest_absorb.py --self-test` gives `44 checks, 0 failed`. Each matches the body.
- Policy delta: commit 880f254423 rewords fix-review.md to fit its token cap. It also cuts step 12's sentence "Instrument, test, policy and body deltas never widen it", which the body dispositions as implied by the sentence before it. That is a policy wording change under the owner's approval route the body names (mandate 6893738184). This reviewer does not judge that approval.
- Finder's harness: none. This PR is a process countermeasure (R11-RCA-SELFTEST-TABLE-DRIFT), and its fixtures were re-run in round 1, which this delta leaves unchanged.
- CI: classify polled from 21:46 to 22:16 UTC (ev/classify.log). The last line is `WAIT 1ab809af502ca1fbaae511e00d39a442ec809d37 pending: gate red: none` (ev/classify-last.txt). `merge_train.py owed-reds` output is in ev/owed-reds.txt. The heavy gate and the mutation table were not re-run.
