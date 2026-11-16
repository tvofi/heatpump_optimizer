Fix review: merge 36eb8805ec1eada0b267a5925116a9179bbdf759

bus-nonce: be9ae4f201ad1c0668c399d7e8f6c957

## Scope

Round 1 at this head. The packet's `## Review scope` reads `full` (no verdict names the reviewed head 5023cde196), so the whole three-dot diff was reviewed. The delta 5023cde196..36eb8805ec is a merge of main 030a4d377f: delivery rows and `tools/audit/seat/orchestrator_tick.py`. It touches no `custom_components/` path, and the three-dot diff touches no `custom_components/` path either. The diff is policy and configuration: four new criteria files, four dimension briefs, `CLAUDE.md`, the code-owned `dev/audit/config/objective.json`, `scopes.json`, `policy_budgets.json`, a harness, and closure classification.

## Notes

- Note: figure-unverified: the body's M1 and null-control counts include `E11-T-product_green_floor`. At this head that card cannot produce a gap. At eval/r11 the card reads `gates_finders: false` and `merged: null`, so `check_scopes.py` `continue`s past it before the unset test. Re-run with the PR's own harness: null control `gaps c6ce415b77 c6ce415b77` prints 9 gaps, not 10. M1 (floor and D4 back to null), `gaps <head+eval> <mutant+eval>`, goes from 5 to 6, not 7. Only `E11-K-D4` is added. So before the merge, no check reads `thresholds.product_green_floor.value`. A null there would show only after the card's `merged` is recorded. Carry: dismissed: a body figure on a non-gating card, which the post-merge `--round 11` check reads once `merged` is recorded
- Note: figure-stale: the body quotes the eval/r11 tip as `c6ce415b7759b6eb72fc2ffc3fd33ee3aab9fc69`. Origin refuses that object (`not our ref`). `refs/heads/eval/r11` is `c6ce415b7711d76cf6c08f926f30da91f7bda924`, with the same 10-hex prefix. Carry: dismissed: paperwork, the abbreviated SHA resolves
- Note: figure-stale: the `--budgets` rows in the body were measured before main moved. At this head: `CLAUDE.md 216 221 3598 3605`, `D9.md 64 65 898 901`, `corpus: ~69244 tokens, cap 69244 +band 500 = 69744`. The body says ~71765, and `policy_lint` reports 55 policy files, not 56. All are still within their caps. Carry: dismissed: paperwork, every cap holds at the head

## Evidence

- Head unchanged: the PR's head is 36eb8805ec1eada0b267a5925116a9179bbdf759, as named in the body's `## Head` and in `ev/HEAD.txt`.
- Role contract current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- Merge: `git merge-tree --write-tree origin/main 36eb8805ec` exits 0 (tree bb42e5bb81). No conflict.
- `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched (empty diff against main).
- CI: `merge_train.py classify 36eb8805ec --pr 3641` printed WAIT four times, then rc 4: `APPROVAL-OWED 36eb8805ec... 1 budget raise(s), first .claude/workflows/policy_budgets.json: corpus_tokens: 67155 -> 69244 (a cap went up): a raise is the owner's (0013): no decisive review by tvofi (id 70032254) on this pull request`. This head is judged GREEN; the raise's approval follows this verdict (`ev/classify.log`).
- Red checks: at this head, the only red in the owed set is `budget-raise-gate`, the approval the body answers. `tests / nightly-status` is red, but it is outside `merge_train.py owed-reds`, so it is neither owed nor a block. The body names and answers the earlier-head reds at 5023cde196 (`instrument-self-tests`, `tests / fast (3.14)`), which were inherited from main d1ee130c48 and fixed by #3661.
- Mutation M2, reproduced: dropping `dimensions/criteria,` from both `scopes.json` brace globs makes `check_scopes.py --repo .` exit 1 with `FAIL D6 ...` and four `classified in neither universe nor static: dev/governance/dimensions/criteria/D*-criteria.md`. Restored: exit 0.
- Mutation M1, D4 half reproduced: `owner_criteria.D4` set to null adds `E11-K-D4 is accepted for criterion D4, which dev/audit/config/objective.json still leaves unset`. The floor half is not reproduced (see Notes).
- Mutation M3: reproduced: removing the four criteria entries from `tests/closures.json` makes `PYTHONPATH=tests/hastub python3 tests/entities.py` print `FAIL every tracked file is either measured or deliberately classified  [these force the FULL suite when touched: dev/governance/dimensions/criteria/D10-criteria.md, ...]`; at the unmutated head `ALL 2723 ENTITY CHECKS PASSED` (`ev/m3-entities.txt`). Restored clean.
- Harness plants: `r11_owner_criteria.py plants` prints `plants: 9, wrong: 0`, rc 0. Each met plant FAILS and each unmet plant PASSES (D10 Q1 x3, D4 P2 4.478/4.542, D5 C5 41/11, D9 B1 65.0/18.0).
- `check_scopes.py --self-test`: `SELF-TEST passed`, `population arms: 13/13 held`. `--population`: `tank_volume` and `house_size` NO-READ with the declared-levels reason, `NO-READ AXES: 2`.
- `policy_lint.mjs`: `TOTAL: 0 error(s) across 55 policy file(s)`. `rules_sync.mjs --check`: ok. `tests/structure.py`: `STRUCTURE RATCHET PASSED`. `archscore --diff origin/main`: `dS +0.0000 NULL` at the head and at main.
- Raise earned (step 14): main 030a4d377f measures `corpus: ~67178 tokens, cap 67155`, and the head measures ~69244. With the four criteria files removed at the head, corpus is ~66976, which is below main's cap. The raise is therefore paid by the four new binding files and by nothing else in the diff. The listed payments are real: `D10.md` drops from 46/624 to 32/410, and `D4.md`, `D5.md` and `D9.md` sit at or under their caps. I hunted for a missed payment and found none that keeps the criteria's condition/procedure/pass/fail shape.
- Population levels re-read against the flow: the body's `_number(50, 1500, 10, 'L')`, `_number(20, 1000, 5, "m²")`, `RANGE_HOUSE_HEAT_LOSS (0.01, 1.0)` and defaults 200.0/140.0/0.15 are as cited by the PR and by `check_scopes --population`. Nothing reads them yet, as the `no_read` field says.
- Class: one seam per card (four criteria files, one floor, two seat models, two axes). The body routes no enumeration rule beyond its cards.
- Forward-carry: the body states `none`. The briefs that need the criteria (`D4.md`, `D5.md`, `D9.md`, `D10.md`) are edited in this diff.
- Policy and code-owned paths (`objective.json`, `CLAUDE.md`, dimension briefs): the owner's approving review is still required by `main-protect-checks`, which the body says itself. This verdict does not stand in for it.
