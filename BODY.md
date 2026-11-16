R11-PRE-BRIEFS-TEXT part 2 (part 1 merged as #3618): `dev/governance/dimensions/D11.md` step 3 gains the policy-set duplication screen (carry 3) and the rulings-file check (carry 4). Step numbering is unchanged: both are bullets of step 3, the structure's own health. Policy, for the owner's review.

**Wording drafted under mandate 6893738184** (scope all, in force to 2026-12-15T12:00Z; tvofi 2026-11-15, verbatim: "The owners own words can also be you under the mandate."): the two new bullets and the two shortened step-3 bullets are the seat's wording, declared here; the quoted sentences in them are tvofi's verbatim. The rulings are tvofi's of 2026-11-15, verbatim: "policy files and policy related files should follow good data integrity practice, no duplication, that creats risks of divergence"; "Yes, it applies everywhere. Yes, fold such screening into the d11 dimension"; and, on the rulings file's purpose, "This is exactly how I see it".

Evaluation: built at eval/r11 tip `c6ce415b77`, whose `dev/audit/yardstick/round11/EVALUATION.json` `review` reads `approve` of the evaluation at `02a48db212`. Carries 3 and 4 are owner rulings, not evaluation cards; card E11-D11 was built by part 1, and this diff changes no sentence part 1 wrote for it.

What each check names:
- Duplication: the units are the sentences `{ git ls-files | node tools/policy/policy_lint.mjs --corpus-filter; git ls-files dev/governance/decisions dev/programme/RULINGS.md; } | xargs python3 tools/audit/text_ledger.py units --dim D6` prints: the policy corpus (`CLAUDE.md`, the role contracts, the rules, the dimension briefs, the pull-request template among it), the decision records (a superset of those policy cites, so none is missed) and the rulings file, which `corpus_excluded.json` leaves out of the corpus on #3626. No file is hand-listed. Null control in the brief: a pointer, and a `.claude/rules/` copy `rules_sync.mjs --check` holds to its source. A recorded restatement (`CLAUDE.md` and `orchestrator.md` section 8) is still reported with its reason.
- Rulings file: entry count by `awk '/^## Superseded/{exit} /^- /{n++} END{print n+0}' dev/programme/RULINGS.md` (in-force bullets only; the closing section holds the superseded) and `wc -c`, against the previous round's baseline. Null control in the brief: an entry naming the current mandate or the round's direction is not a graduation candidate.

Carries of this group:
- Carry 0 (scorecard paragraphs, triage P668): built by part 1, #3618; `dev/governance/dimensions/D11.md` and `D13.md` each name `tools/audit/seat/scorecard.py` at this head (`grep -c scorecard.py` prints 1 for each). Unchanged here.
- Carry 1 (D6 reads `tests/doc_claims.py` only for registered claims): built by part 1, #3618; D6 step 1 states that `text_ledger.py units --dim D6` holds every sentence, so a claim the register lacks is still a unit. Unchanged here.
- Carry 2 (D11 half of the census): built by part 1, #3618; D11 step 1 makes a row with no control one decision 0018 section 1 reads as NO-READ. Unchanged here.
- Carry 3 (duplication screen) and Carry 4 (rulings-file check): built in this diff.

**Merge order: after #3626.** `dev/programme/RULINGS.md` lands on #3626 (R11-PRE-RULINGS-FILE), open at this head. At this head the rulings `awk` exits 2 (`cannot open`), and the duplication enumerator exits 0 without the rulings file's units (`git ls-files` prints nothing for an absent path). On #3626's head both run (Figures). This is the one acceptance item not met at this head.

Budget rows, from `node tools/policy/policy_lint.mjs --budgets` (lines, cap, tokens, cap; the policy file is `dev/governance/dimensions/D11.md`, keyed `tools/audit/briefs/D11.md` in `dev/governance/config/policy_budgets.json`): row `tools/audit/briefs/D11.md`, and the `corpus:` line. Both raised (Raise justification).

## Raise justification

Raised: `files` and `files_tokens` for `tools/audit/briefs/D11.md`, to the values `--budgets` prints at the head; `corpus_tokens` by this diff's own growth only (the corpus measurement at the head less the same command at `origin/main`, added to main's recorded cap), so no other group's band is spent. Under mandate 6893738184 (scope all, `CLAUDE.md` rule 2, decision 0013); the reason is also in the commit message.

Payments tried: in order (`ratchet-budgets.md`):
- Taken: step 3's "Detector health" bullet, which restated step 1's control column (step 1 already makes a dead control a finding); taken whole.
- Taken: the Recurrence bullet's threshold clause, which restated the recurring-error rule; it now points to `CLAUDE.md`'s rule.
- Taken: the new bullets' own wording, cut until each clause carries an input, a control or a ruling.
- Not taken: other D11 sentences, because each left is a step, an input, a standard or a control a finder runs from (deleting working functionality is not a payment).
- Not taken: moving text out of D11, because it moves prose without deleting it, and the finder reads only its own brief.
- Not taken: paying the corpus by cutting exact duplicates the new screen already prints in other files (for example the `UNDER-SCOPED` sentence in both `fixer.md` and `fix-review.md`). Those files belong to other groups (`fixer.md` is in #3626's diff), and choosing which copy owns each mandate is the D11 finder's finding for the owner to rule, which this check exists to produce.

No code payment applies: the diff is text and data.

Architecture score: dS +0.0000 NULL

## Approval

Pending. A policy change to `dev/governance/dimensions/D11.md` and `dev/governance/config/policy_budgets.json`: the owner approves before merging, or, under mandate 6893738184 (scope all, in force to 2026-12-15T12:00Z), the orchestrator's declared approving review after review. It covers the wording drafted under the mandate (top of this body) and the budget raise (Raise justification).

## Head

`4f6b8c57ca90ad987a063a2682a4ab9dc2b4ef00` on `origin/main` `e30408f7881cd5602a2c4d7ea9517b0d765652f6` (merge base the same commit), taken 2026-11-16 UTC; diff three-dot.

## Mutation proof

Text and data only; the check that pins the diff is `policy_lint.mjs`'s budgets class. With `dev/governance/config/policy_budgets.json` restored to `origin/main`'s copy, `node tools/policy/policy_lint.mjs` printed `TOTAL: 3 error(s)`: `[budgets] (whole corpus)`, `[budgets] tools/audit/briefs/D11.md: 126 lines exceeds its cap of 109` and the `files_tokens` arm. With the head's copy restored it printed `TOTAL: 0 error(s)`.

## Null control

- Duplication null control: the generated `.claude/rules/` copies share sentence ids with their `dev/governance/rules/` sources (the awk over the units' ids in Figures prints a non-zero count). Without the brief's exclusion every generated rule would read as a duplicate, so the exclusion is load-bearing.
- Duplication positive control: outside the generated copies, the same units print exact sentences in two or more files (Figures), so the screen has instances to find at this head.
- Rulings count null control: `printf '# x\n## Superseded\n- a\n' | awk '/^## Superseded/{exit} /^- /{n++} END{print n+0}'` printed `0`, so a closed entry is not counted.

## Figures

<!-- figure-block: scope-line mb=e30408f7881cd5602a2c4d7ea9517b0d765652f6 head=4f6b8c57ca90ad987a063a2682a4ab9dc2b4ef00 -->
~~~text
MODE: SCOPED -- 1 script(s) run, 32 scoped out.
~~~
<!-- /figure-block -->

- duplication units at the head: the units command (top of body) exited 0; `wc -l` over its output and `cut -f1 | sed 's/#.*//' | sort -u | wc -l` printed `3952` units over `80` files.
- generated-copy overlap: `awk -F'\t' '{split($1,a,"#"); print a[2]"\t"a[1]}'` over the units, counting ids found under both `.claude/rules/` and `dev/governance/rules/`, printed `376`.
- exact multi-file sentences: ids over 60 characters found in two or more files outside `.claude/rules/`, by awk over the same units, printed `11`.
- on #3626's head (`git worktree add --detach <tmp> origin/fix/r11-pre-rulings-file`): the units command printed `189` units under `dev/programme/RULINGS.md#`; the rulings `awk` exited 0 and printed `88`; `wc -c < dev/programme/RULINGS.md` printed `26389`. At this head the `awk` exited 2 (`cannot open`).
- budgets: `node tools/policy/policy_lint.mjs --budgets` printed `tools/audit/briefs/D11.md 126 126 1939 1939` and `corpus: ~66226 tokens, cap 66218 +band 500 = 66718`; at `origin/main` the same command printed `109 109 1647 1647` and `corpus: ~65934 tokens, cap 65926`; cap = 65926 + 292 growth.
- policy lint: `node tools/policy/policy_lint.mjs` printed `TOTAL: 0 error(s) across 51 policy file(s)`.
- `node tools/policy/brief_lint.mjs` exited 0; `node tools/policy/check-wave-script.mjs` printed `223 passed, 0 failed`; `node tools/policy/rules_sync.mjs --check` printed `RULES-SYNC ok`.
- structure: `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`.
- scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed `MODE: SCOPED -- 1 script(s) run`, naming `tests/entities.py`; `PYTHONPATH=tests/hastub python3 tests/entities.py` printed `ALL 2723 ENTITY CHECKS PASSED`.
- architecture: `python3 tools/audit/archscore/score.py --diff origin/main` printed `Architecture score: dS +0.0000 NULL`.
- text_ledger.py is unchanged, so its `--self-test` is not owed.

## Red checks

- `budget-raise-gate`: red by design until an approving review lands at the head, because this pull request raises D11's caps and `corpus_tokens` in `dev/governance/config/policy_budgets.json` (Raise justification). Not a defect a cheaper detector could have caught: the gate is the intended stop, `policy_lint.mjs --pr-body` already predicts it locally at no added standing cost, and it clears on the owner's review or the mandated one under 6893738184. No countermeasure owed.

## Forward-carry

none

## Friction

none
