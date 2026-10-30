Fix review: merge f44cef1f257979538fb581bc897e779c7e59664e

bus-nonce: 5cf97e4fe9340fb8e121c66b9b469719

## Summary

Resolution-delta review of PR #2872 (R10-COP-PARTLOAD), 27bb23875cf0248028d243b4643523e6f4c7f04e..f44cef1f257979538fb581bc897e779c7e59664e, from a detached worktree at the head. This follows the merge verdict at 27bb2387. `review_carry.py 27bb2387 f44cef1f` prints `FRESH-REVIEW` because the merge changed `tests/golden/claimed_drift.txt` to something other than the union of its parents, so I reviewed that resolution. The branch's authored diff is unchanged by the merge. The claim list is correct. There is no budget raise, and no check is red at the head.

## Evidence

- Head: the PR head read from the API is still f44cef1f257979538fb581bc897e779c7e59664e when I return this verdict (`ev/HEAD.txt`). f44cef1f has the same tree as 7d9ac8b8 (`git diff 7d9ac8b8 f44cef1f` is empty). 7d9ac8b8 is the fixer's one merge of origin/main 1148ee635 into 27bb2387.
- Authored diff unchanged: I compared the three-dot diff against each merge base (27bb2387 against its base, and the head against 1148ee635). Its +/- lines are identical for `custom_components`, `dev/audit/harnesses`, `dev/audit/rounds`, `docs`, `tests/features.py` and `tests/golden/config_flow.json`. The mutation-ledger name-status list is the same set at both ends. The `_buffer_charge_ceiling` re-key from 110923c2 to 0531d42a was already in the 27bb2387 diff.
- Claim list (brief item 2): `git show --remerge-diff 7d9ac8b8` shows a single conflict, in `tests/golden/claimed_drift.txt`, and the `MERGE-CLAIM: refused` marker (`ev/remerge_7d9ac8b8.txt`). The hand resolution keeps main's list verbatim and adds one line, `config_flow # R10-COP-PARTLOAD`. It drops the nine R10-BUFFER-STORE lines that the older base had and that main 1148ee635 had already removed. The three-dot diff of the claim file is exactly that one added line (`ev/threedot_claims_budgets.diff`). The brief described coord_all_features, coord_dhw, coord_grid_fee, coord_minimal and coord_two_zone as this branch's own claims. They are not: they are main's R10-COP-GATE (#2262/#2917) lines, they sit unchanged in main's list, and this diff does not move them. So "main's claims plus this branch's own" means main's list plus config_flow, and that is what the head carries. This follows claim-files.md.
- Null control, re-run: `GOLDEN_MODE=drift PYTHONPATH=tests/hastub python3 tests/env_drift.py --all` at the head exits 0. It prints `CLAIMED config_flow: 2 leaves moved`, `NO UNCLAIMED DRIFT: 56 scenario(s) checked against origin/main` and `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`. These match the body's figures (`ev/env_drift_all.log`). Disclosure: my two mutants below ran in the same worktree while this was running. The clean result is the one expected from the unmutated tree, because any contamination would only have added drift.
- Ledger merges: the LEDGER-MERGE driver resolved `tests/structure_budgets.json` and `tests/closures.json` (closures as a set union). `python3 tests/structure.py` at the head prints `STRUCTURE RATCHET PASSED`, with `class_excess_loc 17672 <= 17672` (`ev/structure.log`).
- Raise (brief item 3): the three-dot diff of `tests/structure_budgets.json` moves `class_excess_loc` from 17724 down to 17672 and raises no cap. The body correctly carries no `## Raise justification`, and `budget-raise-gate / budget-raise-gate` is success on this head.
- Red checks (brief item 3; fix-review step 11): I read the check-runs of the head from the API (`ev/check_runs.txt`). No run is failure, cancelled or timed_out. tests / fast (3.14), typing, closures, coverage, browser, replay, mutation, nightly-status, governance / delivery-status, env-matrix, instrument-self-tests, arch-score, hassfest and codeql all succeeded. tests / mutation-pins and mutation-autofix are skipped. `## Red checks` names and answers each check that went red on earlier heads: nightly-status (main's), delivery-status, budget-raise-gate, fast, typing and mutation/mutation-autofix. Each answer names a cheaper detector or finds that none exists. The trigger is answered.
- Not concluded when I return this verdict: `pr-contract / pr-contract` is queued, a re-run started after the others concluded. One `prelude` job in run 41018221986 has been in_progress since 07:08Z; the same-named prelude in run 41018220815 succeeded. Neither has concluded red. The pr-contract result on this head is left to the orchestrator's merge train to read.
- Mutation re-run (step 1), on the merged tree, with `tests/features.py`. M1: `config_flow._partload_errors` guard `derate >= limit` changed to `derate > limit + 99`, which gives `2 of 4604 FEATURE CHECKS FAILED`. M2: `thermal_model.partload_factor` with `x` zeroed after the clip, which gives `7 of 4604 FEATURE CHECKS FAILED`. Both are killed, and the tree was restored clean (`ev/M_cf_guard.log`, `ev/M_tm_factor.log`). I did not re-run CI's mutation table, which is green on this head.
- Merge with main: `git merge-tree --write-tree origin/main HEAD` exits 0 against 1148ee635 (`ev/merge_tree.txt`). It also exits 0 against main's newer aced258937628590b92265eea4c01276cac43b24 (#2955), where the closures ledger driver resolved (`ev/merge_tree_aced2589.txt`).
- VERSION, the manifest version and RELEASE_NOTES.md: the three-dot diff of these paths is empty.
- Forward-carry: the body's four carries are each routed `Carry: R10-COP-PARTLOAD`. The packet's carry_audit reads `4 routed, 0 unrouted, 0 bad destination(s)`. They are unchanged from the verdict at 27bb2387.
- Figures: the packet's figure_lint reads `8 resolved, 0 not verified, 0 refused`. I re-derived the env_drift, structure, merge-tree and budget figures above. I did not re-derive the scoped-gate counts (`30 script(s) run, 3 scoped out`; `32 TEST SCRIPT(S) PASSED; 2 SCOPED OUT`), `ci_predict.py` or the archscore `dS +0.0000 NULL` at 7d9ac8b8. CI's green closure-scope, fast and arch-score runs on this head are the evidence for those.
- Finder's harness: the packet names none. This round's delta adds no production line, so I did not re-run the harnesses the earlier rounds recorded.
- Round: this is a resolution-delta review that follows a merge verdict, not a new review round.
- RESULT review_carry=FRESH-REVIEW branch_only_commits=2
- RESULT env_drift_all exit=0 claimed=config_flow unclaimed=0 stale=0 checked=56
- RESULT structure=PASSED class_excess_loc=17672
- RESULT mutants killed=2/2
- RESULT merge_tree_exit=0 (1148ee635 and aced25893)
- RESULT red_checks_at_head=0

## Findings

none
