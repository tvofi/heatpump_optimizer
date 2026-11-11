R10-HOTFIX-DELTA-REVIEW, repair of #3379 after it went DIRTY against main. Owner ruling (tvofi 2026-11-09): "I though it was always only the delta that was reviewed in later review rounds? If not, make it so", with the exception "only if the delta touches production code in a way such that the functionality of the other already reviewed code has a risk of being affected in a non obvious way that CI would not detect". A later round covers `git diff <reviewed-head> <head>`, each prior finding resolved and the live required checks. Only a delta touching production code (`custom_components/`) that puts already-reviewed code's functionality at non-obvious risk, in a way CI would not detect, widens it, to exactly that code; the verdict names the path and the risk. Instrument, test, policy and body deltas never widen it. The same rule is stated in fix-review.md step 12, the packet's scope line (review_packet.py) and the reviewer prompt (cloud_dispatch.py).

## Head

Head f26d038f142a35b09ea309ca6b50989df4ef6a44, measured against origin/main d08ed31049cd3636cde4d2fdeb3bd7cd4b3c842a at 2026-11-11T01:31Z. This round's delta over the last reviewed head 1875f3ed3b0f38234ae30e11299c2e4632a4c422 is two commits:

- 4b7a5fc40bf82e1611ef3fd8d7a96bd9d1c0fb3e merges origin/main (a merge, not a re-cut: orchestrator.md section 7). `git merge-tree --write-tree --name-only origin/main 1875f3ed3b` named one conflicted path, tools/audit/seat/cloud_dispatch.py, in five hunks. Main's side added `carry_only`/`record_pr` to `dispatch_group`, `GROUP_FLAGS` and the `--group` call, passed `roster`/`fixer` to `group_brief`, and moved the reviewer prompt's packet sentence into a `where` string that branches on a handoff review (`at_handoff`). The resolution keeps both sides: every hunk carries main's arguments and `reviewed_head`. `--reviewed-head` is now spliced into the PR branch of `where`, beside the review_packet render command, and the later-round scope sentence follows `where`. Read back: each line either parent added to cloud_dispatch.py relative to the merge base is in the merged file, or re-wrapped into a union line that keeps every one of its arguments.
- f26d038f142a35b09ea309ca6b50989df4ef6a44, policy-only: main's compression of fix-review.md left the merged file at 139 lines and 2551 tokens. Dropping "of being affected" from step 12 makes it 138 lines and 2546 tokens. The lines cap goes back to main's 140, which withdraws the earlier raise to 143, and the files_tokens cap is re-recorded at the measured 2546 (it was 2549 on this branch).

## Mutation proof

`python3 dev/audit/harnesses/r10_hotfix_delta_review_mutants.py` at f26d038f142a35b09ea309ca6b50989df4ef6a44 ends `MUTANTS: 9 run, 0 not as required`. M0 (unmutated head) passes; M1 to M8 are KILLED. M6 removes `--reviewed-head` from the reviewer prompt, which now lives in the merged `where` string, and is killed by `FAIL a later round's reviewer renders its packet with --reviewed-head and is told its scope is the delta (fix-review.md 12); null: a first round's render names no reviewed head`. M7 and M8 are killed by `FAIL the packet's scope line: the exception names production code, non-obvious risk and CI's blindness, and the wider trigger wording is absent`.

## Null control

M0, the unmutated head, passes every self-test the mutants turn red. A first-round render names no `--reviewed-head` (the same cloud_dispatch self-test check), and a first round still renders the full diff (review_packet self-test).

## Figures

All at f26d038f142a35b09ea309ca6b50989df4ef6a44:

- `python3 tools/audit/seat/cloud_dispatch.py --self-test`: `151 checks, 0 failed`.
- `python3 -I tools/audit/seat/review_packet.py --self-test`: `94 checks, 0 failed`.
- `python3 dev/audit/harnesses/r10_hotfix_delta_review_mutants.py`: `MUTANTS: 9 run, 0 not as required`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED -- 2 script(s) run` (doc_claims.py, entities.py).
- `tests/doc_claims.py`: `ALL 297 checks PASSED`.
- `tests/entities.py`: `ALL 2707 ENTITY CHECKS PASSED`. The first run reported `1 of 2707 ENTITY CHECKS FAILED`; the failure was `hb:positive_control`, a timing positive control whose sampler did not name a 600 ms spin. A re-run at the head passed, and so did a run at origin/main d08ed31049cd3636cde4d2fdeb3bd7cd4b3c842a started in parallel as the control. This diff touches no file in that check's path.
- run_always steps: `env_drift.py --claims-only` ok, `closure.py selftest` 118 passed, `layout.py` ok, `harness_headers.py` 112 passed, `structure.py` `STRUCTURE RATCHET PASSED`.
- `node tools/policy/policy_lint.mjs`: exit 0. `--budgets` reads 138 lines (cap 140) and 2546 tokens (cap 2546) on the tools/audit/briefs/fix-review.md row.
- `python3 tools/audit/archscore/score.py --diff origin/main`: `Architecture score: dS +0.0000 NULL`.

## Raise justification

Raise: in dev/governance/config/policy_budgets.json, the files_tokens cap for tools/audit/briefs/fix-review.md goes from 2451 to 2546, the value `policy_lint.mjs --budgets` measures at this head. The lines cap stays at main's 140, so no lines raise remains, and `_band` is not widened. Approved by the orchestrator under mandate 6715477401, scope all.
Payments tried: (1) cutting redundant words from step 12 itself: taken, "of being affected" is redundant beside "at non-obvious risk", and the cut paid 5 tokens and 1 line. (2) Compressing other prose in fix-review.md down to 2451: refused, because the blocked verdict named exactly that compression of steps 6, 8, 9 and 13 as scope creep. Main has since compressed those steps itself, and the rule still needs about 95 tokens of its own.
Architecture score: dS +0.0000 NULL

## Approval

This change to `dev/governance/roles/fix-review.md` step 12 carries out the owner's ruling (tvofi, 2026-11-09): "I though it was always only the delta that was reviewed in later review rounds? If not, make it so". The ruling is not the approval. Merging still needs the owner's approving review at this PR's head (code-owner rule, decision 0009 step 6), and the same review covers the files_tokens raise under `## Raise justification`.

## Red checks

`budget-raise-gate / budget-raise-gate` is red by design: the files_tokens raise (2451 to 2546 for tools/audit/briefs/fix-review.md) stays red until tvofi approves at the head, which the code-owner rule requires. This body does not claim that approval. The cheaper detector is `node tools/policy/policy_lint.mjs --budgets`, which already prints the measured figure and the cap. It cannot approve a raise, so its standing cost is one owner review per raise; no cheaper detector for the approval itself exists.

`pr-contract / pr-contract` was red at 71b95e42daf4d32031ce116b01c469b81f2a23a0 because the body named `budget-raise-gate` by its short name. The cheaper detector is `node tools/policy/policy_lint.mjs --pr-body <body.md> --red 'budget-raise-gate / budget-raise-gate'`, which prepr.sh runs. This body names both contexts by their full names.

## Forward-carry

none

## Friction

none
