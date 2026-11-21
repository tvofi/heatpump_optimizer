Fix review: blocked 76f30b596a707c13d432dc2f37997d398a7bc889 mutation-vacuous: tools/ci/selftest_scope.py:1170 (not gaps; not broken), tools/audit/seat/orchestrator_tick.py:2092 and :2101, tools/audit/seat/selftest_absorb.py:109, :155 and :242 survive

bus-nonce: 4047d07d4c9057456563682b6bf03f9c
pending-ci: gate

Round: 1 (first review of #3834; no --reviewed-head).

## Block

Every survivor found by the reviewer's own targeted mutants at this head (ev/reviewer-mutants.txt, driver ev/mut.py, run in a detached worktree at the head). Each mutant changed one new production line. The test named in the comment was then run, and the line restored.

- **M1 `tools/ci/selftest_scope.py:1170`, `not broken` dropped: SURVIVED** (`selftest_scope self-test: 171 checks, 0 failed`). **M2, same line, `not gaps` dropped: SURVIVED** (171 checks, 0 failed). These two block. Reading `check_cli` shows the harm. Take a run with a wiring gap, or a broken trace, beside a read that absorb can repair. Under either mutant, `absorb_write` runs and `remain = drift(graded, measured, steps)[0]`. That remain never contains `gaps` or `broken`, so `absorbed` is True and `check_cli` returns 0. It then prints `0 refusal(s); ABSORB OWED`, which matches governance.yml's drift grep. Main's drift step would go green while a gap or a broken trace is present. The guard is correct in the code, but no test pins it. Repair: two `bot_run` cases in the self-test, each planting a gap or a broken trace beside an absorbable read and asserting rc 1 with no ABSORB OWED. A mutant per guard must be killed.
- M5 `orchestrator_tick.py:2101`, `int(ahead) > 0` to `>= 0`: SURVIVED (391 checks, 0 failed). No case has the standing ref level with main, where compare returns `0 null`. Under the mutant the brief reads `held by selftest-absorb null (...)`. Add that case, or triage the mutant as equivalent with its reason.
- M6 `orchestrator_tick.py:2092`, the `name.endswith(SELFTEST_JOB)` test dropped: SURVIVED. This is near-equivalent today, because no other job has a step named DRIFT. Triage it, or pin the lane name with a case.
- M9 `selftest_absorb.py:109`, the jobs-page guard (`total_count > len(jobs)`) to `if False:`: SURVIVED (`41 checks, 0 failed`). Without this guard, a run whose instrument-self-tests job falls off the first page reads as no measurement, and the window walks past a red run. No case pins it. This contradicts the instrument doc's "one mutant per branch".
- M8 `selftest_absorb.py:155`, `rc != 0 or` dropped: SURVIVED. Near-equivalent, because `absorb_cli` prints the ADDED line only on rc 0. Triage it or pin it.
- M7 `selftest_absorb.py:242`, `if rc != 1:` to `if rc == 2:`: SURVIVED. A CLEAN (rc 0) or RECORD-OWED (rc 4) regeneration then reads a table that was never written and crashes, where it should print VERIFY-REFUSED. It never prints VERIFIED, so this is near-equivalent. Triage it or pin it.

- **Policy budget breach, introduced by this PR.** `node tools/policy/policy_lint.mjs` reports `ERROR [budgets] tools/audit/briefs/fix-review.md: about 2962 tokens across its lines exceeds its cap of 2775 tokens (files_tokens)` at this head, and `TOTAL: 0 error(s)` at merge base 63c6d1cff9a2 (ev/policy-lint-head.txt, ev/policy-lint-base.txt). The new bullet "The standing absorb pull request" in `dev/governance/roles/fix-review.md` causes it. Repair: cut the bullet, or other text in the contract, to fit the cap. A higher cap needs its case stated in the body and the owner's approval. The session's stop hook refused on this same error.

## Evidence

- Head measured: 76f30b596a707c13d432dc2f37997d398a7bc889 (ev/HEAD.txt). The PR body's `## Head` names this head.
- `git merge-tree --write-tree origin/main 76f30b596a707c13d432dc2f37997d398a7bc889`: rc 0, no conflict (ev/merge-tree.txt).
- `VERSION`, the manifest, `RELEASE_NOTES.md` and both claim files are untouched three-dot from 63c6d1cff9a2 (ev/version-untouched.txt). No `custom_components/` path is in the diff.
- Self-tests at the head, recorded in ev/selftests-summary.txt. These were cheap runs; the gate and the mutation table were not re-run:
  - `selftest_scope.py --self-test`: 171 checks, 0 failed
  - `selftest_absorb.py --self-test`: 41 checks, 0 failed
  - `beat_jobs.py --self-test`: 309 checks, 0 failed
  - `orchestrator_tick.py --self-test`: 391 checks, 0 failed
  - `selftest_wiring.py --check`: 0 index gap(s)
  - `selftest_scope.py static`: 128 gated step(s), 0 problem(s)
  - `tests/structure.py`: STRUCTURE RATCHET PASSED
  - `app_push.sh --self-test`: 235 checks, 0 failed (Linux)
- The PR's own named mutants on `absorbed = bool(added) and not remain` (`= False`, `= bool(added)`) were re-run, and each is KILLED by the check the body names (ev/fixer-named-mutants-rerun.txt). Its other mutants (M3 MISSING-step drop, M4 remain count) were killed in the reviewer's set.
- Null control re-run: this head's `selftest_scope.py --self-test --workflow <origin/main governance.yml>` gives `171 checks, 3 failed` (ev/null-control-main-workflow.txt).
- Figure re-derived: `selftest_absorb.py beat --repo-dir . --run 44922703115 --at c037e9bfe15285692c5f7412732a1c13a3159968` gives `SELFTEST-ABSORB OWED 738 read(s), 7 step(s)`, rc 1 (ev/beat-defect.txt). Run 44922703115 is at a8efe1d1c2a8 and concluded failure (gh API).
- Hand-repair equivalence: the absorbed table, less its own `selftest-absorb` entry, parses equal to hotfix 25238b470a's `tools/ci/selftest_closures.json`, with 0 differing steps (ev/hotfix-equivalence.txt). This is parsed equality, by the reviewer's own definition; bytes were not compared.
- Body figure: `selftest_scope.py --self-test` is `159 checks` in the body (taken at c037e9bfe152, before the main merge), and 171 at this head. The other figures in the body re-derive at the head.
- Body wording: it names the beat's input as `selftest-measured` artifacts; the code reads `selftest-closures` (selftest_absorb.py MEASURED).
- Class instance count: `non_round_instances` lists 17 PRs, matching the body's 17.
- Finder's harness: none. This PR is a process countermeasure from R11-RCA-SELFTEST-TABLE-DRIFT, whose file exists at both ends, not an audit finding. The defect run 44922703115 is its fixture and was re-run above.
- Policy: `dev/governance/roles/fix-review.md` gains a bullet. The body routes it to the owner's approving review under mandate 6893738184. This reviewer does not judge that approval.
- CI: classify polled from 19:20 to 19:52 UTC (ev/classify.log). The last line is `WAIT 76f30b596a707c13d432dc2f37997d398a7bc889 pending: gate red: none` (ev/classify-last.txt). `merge_train.py owed-reds` is in ev/owed-reds.txt.
