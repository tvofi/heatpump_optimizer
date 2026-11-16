Fix review: blocked 43c1c7dbfd7a642a3543c1912469b2ce30f05584 introduced-red: merging main pushes tools/audit/briefs/orchestrator.md to 4286 tokens, over its 4251 files_tokens cap, so policy_lint exits 1 and governance / policy-docs and governance / env-matrix go red

bus-nonce: e507e1814e2144e10fd3a6a5ed07a2c8

Round: third. This is a delta review over the reviewed head 56fda94e8568b6ae57d1af8227386f8dc096f61c. The delta is 2fa85b69db, which merges origin/main e30408f788 (#3566, the nudge.md retirement) into the branch, and 43c1c7dbfd, which merges that commit in. The delta touches nothing under custom_components/, so the review is not widened.

## Block

- `node tools/policy/policy_lint.mjs` at 43c1c7dbfd exits 1 with `ERROR [budgets] tools/audit/briefs/orchestrator.md: about 4286 tokens across its lines exceeds its cap of 4251 tokens (files_tokens)` (`ev/policy_lint_head.txt`). The `--budgets` row for that file (`ev/budgets_orchestrator.txt`, `ev/budgets_prev_head.txt`) reads:
  - 4248 at the previously reviewed head 56fda94e85, inside the cap;
  - 4172 at origin/main e30408f788, inside the cap;
  - 4286 at this head, over the cap.
- Neither side breaks the cap alone. The branch's edits to `dev/governance/roles/orchestrator.md` (`ev/orchestrator_own_diff.txt`, 2608 to 2673 words) left 3 tokens of headroom, and main's #3566 re-pointing then added text to the same file. The auto-merged result is over the cap.
- `dev/governance/config/policy_budgets.json` is not in this PR's diff, so no cap raise covers the overflow.
- The same error is the cause of both new CI reds at this head, and both are in `merge_train.py owed-reds`:
  - `governance / policy-docs` (job 133020850696): `TOTAL: 1 error(s) across 51 policy file(s)`, `by check: {"budgets":1}`.
  - `governance / env-matrix` (job 133020850695): 7 of its 16 declared outcomes fail. Every failing outcome is either `policy_lint rc=0` with that same ERROR line or the follow-on `MUTANTS: the entry point exited 1 on the corpus as it stands`.
- Both checks were green at 56fda94e85, according to the previous verdict.
- The PR body has no `## Red checks` answer for either, and review_packet refuses `red-unanswered` for both.
- To resolve: cut orchestrator.md by about 35 tokens, or raise its cap with the case stated in the body (a budget raise, so the owner's approval under budget-raise-gate). Then re-run `policy_lint.mjs`.

## Findings

- Note: figure: the branch's change to `dev/governance/roles/proposal-triage.md` conflicted with main's #3566 and was resolved by taking main's text verbatim. The head's file equals main's, so the PR no longer changes that file (own-diff stat goes from 13 files to 12: `ev/own_diff_stat_old.txt`, `ev/own_diff_stat_new.txt`). Main's wording carries the same rule (repair at any severity; a red required check on main, a blocked production PR, a root-cause countermeasure, closeout or an owner directive skip the bar). Any body text that claims this PR rewrites proposal-triage.md is now stale. Carry: R11-PRE-MACHINERY-LIMITER
- Note: instrument: the previous verdict's `gate_raise_only` note (classify reads RED, not APPROVAL-OWED, when a gate run was superseded) still stands and was not re-examined here. Carry: dismissed: an instrument defect outside this PR's diff, handed to the orchestrator in the previous verdict

## Evidence

- Head reviewed: 43c1c7dbfd7a642a3543c1912469b2ce30f05584 (`ev/HEAD.txt`), checked out in a detached worktree.
- Merge resolution: `git merge-tree --write-tree 56fda94e85 e30408f788` conflicts only in `dev/governance/roles/proposal-triage.md`. The head tree dfee30d92b differs from that auto-merge only in that file, where main's side was taken. No other hand edit rides in the merge.
- Own diff: `git diff e30408f788...43c1c7dbfd` and `git diff 66865be375...56fda94e85` agree, line for line, in every file except proposal-triage.md, which dropped out. Untouched by this PR: VERSION, the manifest, RELEASE_NOTES.md, tests/golden and custom_components.
- Merge with main: `git merge-tree --write-tree origin/main 43c1c7dbfd` exits 0 with tree dfee30d92b (`ev/merge-tree.txt`). The head already contains origin/main e30408f788.
- Self-tests at the head (`ev/selftest_*.txt`):
  - machinery_ratchet: 72 checks, 0 failed;
  - pr_cap: 32 checks, 0 failed;
  - orchestrator_tick: 322 checks, 0 failed.
- Mutants re-applied at the head (`ev/mutants.txt`), each killed:
  - `pr_cap.py:230` with `and v > PRODUCTION_SLOTS` removed: 1 check fails;
  - `machinery_ratchet.py:359` with `max(0, ...)` removed: 1 check fails.
- `machinery_ratchet.py --check --base origin/main --head HEAD --pr 3627` exits 0 (`ev/check.txt`):
  - ok nonproduction_merges 481 <= 478 + band 5;
  - ok churn 13948 <= 14797 + 3636;
  - ok target 481 <= 478 + band 5 (17 merges past anchor).
- `--measure --head HEAD` prints `merges_past_anchor 3`.
- CI: `merge_train.py classify 43c1c7dbfd --pr 3627` read `WAIT ... pending: gate red: none` from 00:53:09 to 00:59:34 UTC (`ev/classify.log`). The wait was stopped once the block was established. The block rests on the policy_lint failure reproduced locally, not on classify.
- Owed reds (`ev/owed-reds.txt`) include governance / env-matrix and governance / policy-docs.
- I ran the env-matrix driver locally, but it produced no output within 230 s (timeout rc 124). The CI log above is the evidence for that check.

## Friction

- The local `policy_lint_envmatrix.mjs` run exceeds a 240 s tool call. CI's log was read instead.
