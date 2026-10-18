Fix review: blocked 58dbe46a0eff6d217378ecd3bccc331eb20867a1 root-cause-unanswered: graders-head-copy went red at this head and the body's ## Red checks does not name it; pr-contract's re-run (job 117808979628, 22:33Z) refuses on exactly that, so a required check is red beyond the authorised wave-script exception

bus-nonce: ea5bcafd577125d7e6ea134fa9b354f5

Round: 1 (no earlier `Fix review:` comment on #2423).
Measured head: 58dbe46a0eff6d217378ecd3bccc331eb20867a1 (PR head re-read at the end of the review, unchanged). Merge base 07a09406 = origin/main. Roles contract current (`git diff merge-base...origin/main -- dev/governance/roles/` empty).

## Why blocked (the only defect found)

- `graders-head-copy` (tests.yml, job 117806212914, 22:20–22:22Z) is red. The steps that failed were the PR's own `policy_lint.mjs` (18 `required-contexts` errors: "recorded as a required context but the live set no longer returns it") and `field_coverage.mjs` (`REFUSED ruleset: ... unperturbed, is already red`).
- Cause: a transient change to the live ruleset, not the diff. Ruleset 23698884 `main-protect-checks` shows `updated_at 2026-10-18T22:29:10Z`. The required contexts were missing from the live boundary while the job ran. My local runs in the same window saw the same 18 errors at both head and base (ev/policy_lint.txt, ev/policy_lint_base.txt, identical ERROR lines).
- Re-run at this head after 22:29Z: `TOTAL: 0 error(s) across 41 policy file(s)` and `RESULT read=63 ignored=25 declared_none=34 blind=0 dead=0 refused=0` (ev/policy_lint_rerun.txt, ev/field_coverage_rerun.txt). These match the body's figures.
- Even so, the red check run stands at this head. pr-contract attempt 3 (run 39170938182, 22:33Z, after the last red concluded) failed `Check the body against the contract` with: `ERROR [pr-body] check graders-head-copy is red and ## Red checks does not name it`. pr-contract is a required context. Per fix-review.md step 11 this is `root-cause-unanswered`, and the dispatch's "any other red means blocked" applies.
- Remedy, no code change needed: re-run `graders-head-copy` now that the ruleset is restored, then re-run pr-contract; or name it in `## Red checks` as the ruleset-toggle transient. Either way, re-dispatch for the carry.

## The four asked points — all hold

(a) The head's readers give 0 divergent on origin/main's history. In a worktree at origin/main with only `tools/policy` checked out from the head: `pair merge-subject-pr: 4 readers, 813 items, 0 divergent`, `merge-subject guard: 0 first-parent commit(s) past 07a09406a, 45 merge call(s) in 9 file(s)`, `RESULT divergent=0 unregistered=0 dead=0 refused=0` (ev/agreement_main_with_head_readers.txt). The base readers on the same tree print `808 items, 2 divergent`, the two DIVERGENT lines for #2401 and #2379 (ev/agreement_base.txt). These are the same two lines CI's wave-script printed at this head (`809 items`, the extra item is the PR's own subjects). At the full head: 815 items, 0 divergent. The body's 813 and 0 commits were measured with HEAD at main, which my origin/main measurement reproduces exactly.

(b) Required contexts at this head (ev/check_runs.tsv, against tools/policy/fixtures/required-contexts.json):
- Green: Analyze ×3, briefs, browser, budget-raise-gate ×2, closure-scope, closures, env-matrix, fast (3.14), hassfest, mutation, policy-docs, typing, validate-hacs.
- Red: wave-script (the authorised exception, exactly the 2 known lines) and pr-contract's latest run (above).
- Not required: delivery-status red (OVERDUE #2413/#2412/#2407, main's, not this diff's); graders-head-copy red (above).

(c) The guard simulated on real merge commits of this head into origin/main, run with the head's readers (ev/guard_simulation.txt):
- `Merge pull request #2423 from tvofi/fix/r10-merge-subject-pr` → refused=0, 0 divergent.
- `R10-MERGE-SUBJECT: one merge-subject grammar across readers; subject guard (#2423)` (the PR_TITLE template) → refused=0.
- `Merge pull request #2423 (R10-MERGE-SUBJECT)` → REFUSED (refused=1).
- `Merge branch 'fix/r10-merge-subject-pr'` → REFUSED.
- wave-script checks out with `fetch-depth: 0`, so the walk past the cutoff has history on the push run. The ruleset carries no merge-queue rule, so no queue commit enters the walk.

(d) No check was weakened. The diff adds no workflow change, deletes no self-test probe (15→23) and removes no policy_lint pin (+2 pins plus 4 null controls).
- `mustAnswer` widened from ` from ` to `\b`: the null guard covers more, so it is stronger.
- `narrow` widened in the same way: the declared offline-mode asymmetry now covers hand subjects, and a stale narrow is still refused (pairsArm line 354).
- `MERGE_COMMIT_SUBJECT_RE` is used only in `resolvePrFromCommit`. It now recovers more merges and still answers null on the four null controls.

## Mutation proof (own mutants, each restored; ev/mutants.txt)
M1 policy_lint regex back to ` from ` → RESULT divergent=3, FIXTURE VACUOUS. M2 narrow back → divergent=3. M3 guard call deleted → self-test FAIL. M4 template widened → FAIL. M5 writer test blinded → 2 FAIL. M6 mustAnswer back → FAIL. M7 (not the fixer's: test-merge exemption at any index) → FAIL. M8 (not the fixer's: merge = ≥3 parents) → 3 FAIL. Every mutant was killed.

## Other figures re-derived at head
- Self-test `SELF-TEST 23 of 23 probes held`.
- Discovery `333 governance code files, 1529 distinct grammars, 27 shared`.
- `STRUCTURE RATCHET PASSED`.
- `merge-tree --write-tree` exit 0, no conflict.
- VERSION, manifest and notes untouched (also pr-contract's version-edit step).
- Class seams: my grep returns the same six regex definitions as the body. `orchestrator_tick.py MERGE_PR` is dispositioned in the body.
- `tests/entities.py` locally: `2 of 2349 ENTITY CHECKS FAILED`, the same two at the base (graders-head-copy delivery_status case, template arm), so this container's environment, not the diff. CI's fast/closures are green.
- Not re-derived: the stamp rule-4 window figure (140/135, blind []) and `seconds=1.0`.
- Forward-carry: the body names `dev/governance/roles/orchestrator.md` (merge section) as the destination and leaves the edit to the owner as policy. It is not yet there, so the guard's refusal line is the only carrier. This is not blocking alone, but the orchestrator owes that carry.
