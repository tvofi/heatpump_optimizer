Fix review: merge 0648b3532de38c68cfb7b869a6542c35492dc2b1

bus-nonce: 80e8e1e5df2fa8e16b19d871403e6bf6
pending-ci: gate

## Scope

Round 1 (first dispatch, no reviewed head). Full three-dot diff `e30408f788...0648b3532d`, 17 files: a policy and configuration change with no `custom_components/` line, so no production mutant exists to draw; the mutation proof is the three configuration mutants the body names plus two of mine.

## Evidence

- Head: `0648b3532de38c68cfb7b869a6542c35492dc2b1` (ev/HEAD.txt) is the PR's head and the body's `## Head` line. Merge base `e30408f7881cd5602a2c4d7ea9517b0d765652f6`. `git diff $(merge-base)...origin/main -- dev/governance/roles/` empty: the contract read is current.
- `git merge-tree --write-tree origin/main 0648b3532d` (origin/main 47f0f18a7e): rc 0, tree 9a96e81bc5. Merges cleanly.
- `VERSION`, `manifest.json`, `RELEASE_NOTES.md`: three-dot diff empty.
- Owner rulings, read at eval/r11 `c6ce415b77` `EVALUATION.json`: `.review.verdict` approve at 02a48db212; E11-T-product_green_floor accepted "Floor 0.90, rest unset", five sibling T cards deferred; E11-K-D4/D5/D9/D10 accepted "All four before finders", `gates_finders` true; E11-S-SEATS accepted "Record Fable for both"; the seat-model value the diff writes is the one that card names. Every value the diff writes into `objective.json` matches its card.
- RESULT M1 (objective.json: `product_green_floor.value` and `owner_criteria.D4` nulled), `r11_owner_criteria.py gaps <head+c6ce415b77> <mutant+c6ce415b77>`: 5 -> 7 unset gaps, the two added are E11-K-D4 and E11-T-product_green_floor. KILLED.
- RESULT null control, `gaps c6ce415b77 <head+c6ce415b77>`: 10 -> 5; the five left are the deferred band/ceiling thresholds, as ruled. Reproduces the body.
- RESULT M2 (scopes.json brace globs without `dimensions/criteria`): `check_scopes.py --repo .` rc 1, `FAIL D6`, the four criteria files "classified in neither universe nor static" (ev/m2_mutant_check_scopes.txt); restored rc 0 (ev/m2_restored_check_scopes.txt). KILLED.
- RESULT M3 (the four criteria entries removed from `tests/closures.json`, entities.py's closure): `PYTHONPATH=tests/hastub python3 tests/entities.py` at the head `ALL 2723 ENTITY CHECKS PASSED` rc 0 (ev/entities_head.txt); at the mutant `2 of 2723 ENTITY CHECKS FAILED` rc 1 (ev/m3_entities_mutant.txt), the two added FAILs being "every tracked file is either measured or deliberately classified" and "every carry and every policy file this arm reads for citations selects this script", both naming the four criteria files (the other FAIL lines are the script's own planted arms, present at both). KILLED.
- RESULT plants, `r11_owner_criteria.py plants` at the head: `plants: 9, wrong: 0`, rc 0 (each met plant FAILS, each unmet PASSES; values 4.478/4.542, 41/11, 65.0/18.0 as the body states).
- D10 Q1's printed command, run verbatim over the live `quality_scale.yaml`: no line, rc 0 (the live register passes Q1).
- D10 tier-list cut: the hyphenated and single-word rule names of the merge base's `D10.md` "Rules, by tier" block against `quality_scale.yaml`'s `rules` keys: 54 = 54, both differences empty. The cut loses nothing.
- Population levels, re-read at the head: `config_flow.py:1798` `_number(50, 1500, 10, 'L')`, `:1246` `_number(20, 1000, 5, "m²")`, `:696` `RANGE_HOUSE_HEAT_LOSS: Final = (0.01, 1.0)`, `const.py` `DEFAULT_DHW_TANK_VOLUME` 200.0, `DEFAULT_HEATED_AREA` 140.0, `DEFAULT_HOUSE_HEAT_LOSS_COEFFICIENT` 0.15. Every declared level matches; both axes stay `kind: null` with a no_read naming builder R11-INTAKE-R10-RESIDUE.
- Criteria-file citations resolve at the head: `tests/stress.py:684` `def reference_solve`, `tests/card_drift.mjs --list`, `D9.md`'s "96 ... not ~9,300", the options flow's interval `_number(10, 120, 5, 'min')` (B1's 10 min; 365*24*6 = 52,560 cycles; 10 MiB / 52,560 = 199.5 bytes, B4's 199).
- RESULT budgets, `node tools/policy/policy_lint.mjs --budgets`: head `corpus: ~68000 tokens, cap 68000 +band 500`, `always-loaded: ~3598`, CLAUDE.md 216/221 lines 3598/3605 tokens, the four criteria rows and D4/D5/D9/D10 rows as the body lists; merge base `corpus: ~65934 tokens, cap 65926`, D10.md 46/624. rc 0 at both.
- Raise (step 14): `corpus_tokens` 65926 -> 68000 (+2074). Measured corpus +2066; the four criteria files alone are 656+641+546+425 = 2268 tokens, D10.md pays -214. With the criteria files removed the raise has nothing to carry, so it is earned by the change. Payments 1 and 3 are in the diff; payment 2 is not (Findings). Hunted a missed payment: the repeated three-line provenance in each criteria file is each file's own mandate declaration, and D10 Q1's inline command is the statement's procedure; cutting either loses a fact, so none found that truly improves the text.
- CI: `merge_train.py classify 0648b3532d --pr 3641` polled every ~77 s from 01:06 to 01:37 UTC, every run rc 3: `WAIT 0648b3532de38c68cfb7b869a6542c35492dc2b1 pending: gate red: none`. No red at the head; `gate` (MODE: FULL, since `tests/closure.py` is in the diff) still running, hence `pending-ci: gate`. The packet's `introduced-red: unreadable` refusal was `instrument-self-tests` in progress at render; classify, which decides, reports no red. `budget-raise-gate` is not in classify's red set at the last read. The PR head re-read at 01:38 UTC (`refs/pull/3641/head`) is still 0648b3532d.
- Self-audit: `carry_audit.py check` over this verdict and the body's `## Red checks`, `## Forward-carry` and `## Friction` sections (the packet audited the full body at the head: 0 items): rc 0.
- Owed reds (`merge_train.py owed-reds`) include `budget-raise-gate / budget-raise-gate`; the body's `## Red checks` names it and answers that no cheaper detector exists.
- carry_audit at the head (packet): 0 finding items.

## Findings

- Note: stale-figures: the body's `--budgets` figures predate 92af7f3f9b: it quotes `corpus: ~71765 tokens, cap 71765`, CLAUDE.md `214 ... 3590` and `always-loaded ~3590`, and a merge base of 31117b1029de with `~69740 / cap 69333`; at this head the line prints `~68000, cap 68000`, CLAUDE.md 216/3598, and the merge base e30408f788 prints `~65934, cap 65926`. The diff's cap (68000) is the measured value, so only the body is stale. Carry: dismissed: paperwork on this PR's body, the reviewed numbers are in this verdict
- Note: stale-figures: `## Raise justification` payment 2 (the CLAUDE.md root-cause sentence cut) is no longer in this PR's three-dot diff: main carries that cut at the merge base, which is why main's cap fell to 65926; the PR's CLAUDE.md change is now only the three-line index addition. Carry: dismissed: paperwork; the raise is re-derived above without that payment
- Note: stale-head: `## Head` names two heads, 0648b3532d and the superseded 4197060a38, with the same sentence. Carry: dismissed: paperwork on this PR's body
- Note: owner-approval: the diff edits `objective.json` ("Only the owner changes this file (CODEOWNERS)"), `CLAUDE.md` and four briefs, all policy; this verdict is not the owner's approving review, which `main-protect-checks` still requires. Carry: dismissed: the merge gate enforces it, the body's `## Approval` states it
