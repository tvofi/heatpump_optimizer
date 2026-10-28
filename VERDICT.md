Fix review: merge 3dc9ae19b33be293d7eb9fb07116b014427a2aa5

bus-nonce: f6f116a23187ea37d896733dff8dfd9d

## Verdict

This is round 3 of PR #2633 (R10-FLOW-ARCH-PLANNER). I measured head `3dc9ae19b33be293d7eb9fb07116b014427a2aa5` from a detached worktree. Before writing this I re-read the head with `git ls-remote` and it had not moved (ev/HEAD.txt, ev/head_reread.txt).

**This PR is policy.** It edits `CLAUDE.md`, adds seven role contracts under `dev/governance/roles/`, and changes `orchestrator.md`, decision 0015 and `policy_budgets.json`. It merges only on the owner's approving review at this head, or on an approval citing the mandate in force with scope `all` (#201 comment 6329234399). Against origin/main, this PR still raises `files_tokens["CLAUDE.md"]` (3590 -> 3605) and `corpus_tokens` (62892 -> 66434), and adds the seven new caps. That is the raise justified in the body's `## Raise justification`, and `budget-raise-gate` stays red until that approval is given.

Contract currency: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, and main's later move to 5056615a2 (#2638) touches nothing under `roles/`.

## Brief checks

1. **Budgets.**
   - At the head, `policy_lint.mjs --budgets` prints `CLAUDE.md 213 221 3605 3605 yes`, `always-loaded: ~3605 tokens, cap 3349 +band 500 = 3849` and `corpus: ~66434 tokens, cap 66434 +band 500 = 66934` (ev/policy_budgets_head.txt). Both match the body.
   - Against the round-2 head `8cb08929c`, the round-3 delta to `policy_budgets.json` only lowers caps: `corpus_tokens` 66507 -> 66434 and `CLAUDE.md` 3609 -> 3605. No `*_budgets.json` key rose in round 3.
   - The three-dot diff against origin/main touches only `policy_budgets.json` among the budget files. Its raises are the ones listed above, which round 2 already judged and which go to the mandate.
2. **The two cuts of main's text.** Both are in origin/main's `CLAUDE.md` at lines 111 and 168 (ev/claude_md_vs_main.txt, ev/claude_md_round3.diff). Neither drops an obligation:
   - **"Each says what its role owes and what blocks it."** This was the lead sentence of the role-contracts table. It describes the contracts and binds no seat to do anything. Each row still names what its role owes, and each contract still states it: for example, `standing-merge.md` says "It never chooses what merges", and the triage contract opens with its gate. True duplicate.
   - **"state, not policy:"** on the `HANDOVER.md` line. `CLAUDE.md:67` at the head still says "Everything named here but `dev/programme/HANDOVER.md` is **policy**". `writing-for-agents.md` still rules the handover, and the line still cites it. True duplicate; the exception still stands in the same file.
   - The three shortened rows (`proposal-triage.md`, `standing-tick.md`, `standing-merge.md`) are rewordings with the same meaning: the cost/benefit gate comes first, only owed or new items are reported, and the merge seat never chooses what merges.
3. **DEFER check.** `roster_edit.py --self-test` at the head reads `117 checks, 0 failed` (ev/roster_selftest_head.txt). My mutants are in ev/reviewer_mutants.txt, and the file was restored after each one; the restored self-test reads `117 checks, 0 failed`.
   - **M1, the brief's mutant:** `if verdict != "ACCEPT":` changed to `if verdict not in ("ACCEPT", "DEFER"):`. Result: `3 failed`, first `FAIL triage gate: a DEFER ruling is refused: only an ACCEPT is routed`. Round 2 recorded `0 failed` for this mutant, so that survivor is now killed.
   - **M2, my own:** the cited-ruling gate never refuses. Result: `13 failed`, including the REJECT, DEFER, no-verdict and missing-entry checks.
   - **M3, my own:** `ruling_verdict` matches the first `## P<n>:` entry instead of the cited pid. Result: `13 failed`, including the DEFER check.
4. **policy_lint.** At the head: `TOTAL: 0 error(s) across 50 policy file(s)` (ev/policy_lint_head.txt).
   - `git merge-tree --write-tree origin/main <head>` against 4e38e7d7b exits 0, and the merged tree is identical to the head's tree (ev/merge-tree.txt).
   - Main then moved to 5056615a2 (#2638, which touches `policy_lint.mjs` and `tests/entities.py`). The merge is still clean: rc=0, tree f51c71e36, no stderr (ev/merge-tree-new-main.txt).
   - On that merged tree, policy_lint reads `TOTAL: 0 error(s) across 50 policy file(s)`, with CLAUDE.md at 3605/3605 and the corpus at 66434/66434 (ev/policy_lint_merged.txt). `tests/entities.py` reads `ALL 2404 ENTITY CHECKS PASSED`, rc=0 (ev/entities_merged.txt).
5. **Figures, re-run at the head.** They match the body (ev/figures_head.txt):
   - pulse: 37 checks, 0 failed. roster_edit: 117, 0 failed. r10_roster_ops_mutants self-test: 78, 0 failed. sweep_render: 21, 0 failed.
   - `RULES-SYNC ok`, and `brief_lint` `TOTAL: 0 error(s) across 47 file(s)`.
   - Null `RESULT mutant=null rc=0 fails=0`. T1..T5 give rc=1 with fails 11, 12, 1, 16 and 16, exactly as the body states.
   - `STRUCTURE RATCHET PASSED`. `score.py --diff d6308d77c HEAD` gives `Architecture score: dS +0.0000 NULL`.
   - Claims hygiene ok, and `ALL 112 closure shrink pins PASSED`.
   - `VERSION`, `RELEASE_NOTES.md`, the manifests and the rosters are untouched in the three-dot diff.
   - **tests/entities.py.** On Linux (`/opt/hpo/venv-ci`) the head reads `ALL 2402 ENTITY CHECKS PASSED`, rc=0 (ev/entities_head.txt). The body's 2399 is the authored code head's count over `d6308d77c`. origin/main 4e38e7d7b on its own also reads 2402 (ev/entities_origin_main.txt), so the +3 comes from main through the automatic merge, not from this PR. The four py-spy heartbeat failures the fixer saw on macOS do not appear on Linux, and CI's `fast (3.14)` and `closures` are green on this head.
6. **CI at the head**, read from the commit's check-runs once every workflow had concluded (ev/check_runs.tsv, 41 rows). The only red check is `budget-raise-gate`, on both of its runs. That is by design until approval (decision 0013), and `## Red checks` answers it. `pr-contract` ran after the last red concluded (started 01:58:30, after budget-raise-gate concluded at 01:58:15) and passed.
   - `nightly-status` and `fast (3.14)`, which the body also answers, are green on this head.
   - Everything else is green, skipped or neutral: fast, closures, coverage, coverage-ratchet, instrument-self-tests, policy-docs, mutation, arch-score, typing, browser, briefs, closure-scope, delivery-status, env-matrix, wave-script, hassfest, validate-hacs, CodeQL and its Analyze runs.
7. **Policy.** See the top of this verdict: this is a policy PR, and it merges on the owner's approval or the scope-`all` mandate.

## Findings

- Not blocking: the body's earlier round says the cut AGENTS.md sentence (POLICY_GLOBS and the cap) is something that "`ratchet-budgets.md` carries". That rule names `AGENTS.md` only in its `paths:` frontmatter. The mechanics the sentence described are still enforced by `policy_lint.mjs` (the `^AGENTS\.md$` glob, at :246) and `policy_budgets.json` (AGENTS.md is capped at 13 lines and 183 tokens). The cut sentence stated a fact the instruments enforce, not an obligation on a seat, so nothing binding was lost; only the body's citation is loose. Carry: R10-FLOW-ARCH-PLANNER | dismissed: a body wording point, no rule dropped

## Not verified

- I did not re-run CI's heavy runs (the full gate and the mutation table), per step 11; I cite CI for those.
- I did not re-plant the pulse.py mutants. `pulse.py` is unchanged since round 2 (the body says so, and its self-test re-reads 37/0).
