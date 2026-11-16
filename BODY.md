R11-PRE-OWNER-CRITERIA (p2): the owner's acceptance criteria for D4, D5, D9 and D10, the product_green floor, the seat models, and the declared levels of the two NO-READ population axes, all in `dev/audit/config/objective.json`. p1 (#3631, the `POLICY_GLOBS` hunk of the BOOTSTRAP split) is on main, so this diff no longer carries it.

Cards closed, read at eval/r11 `c6ce415b7759b6eb72fc2ffc3fd33ee3aab9fc69`, the tip carrying the approving evaluation review: `.review.verdict` reads `approve` at sha `02a48db212e0e49af62863575cba86bc339d4958` (round 3). That tip also records the owner's rulings as final (`made final by "Final as given (Recommended)"`) and `gates_finders`: true for the four criterion cards, false for the floor and the seats. Diffed against the 9de7c2bdc7 tip the earlier cut was read at, no card this group closes changes its object, proposal or decision; the rulings lose "preliminary". Under decision 0018 section 6 this merge comes after 02a48db212, and eval/r11 is not rebased past it.

- E11-T-product_green_floor, accepted, ruled "Floor 0.90, rest unset": `thresholds.product_green_floor.value` is 0.9. The five sibling cards are `deferred`; their values stay null.
- E11-S-SEATS, accepted, ruled "Record Fable for both": `seats.evaluator_model` and `seats.reviewer_model` are `claude-fable-5-2`.
- E11-K-D4, -D5, -D9, -D10, accepted, ruled "All four before finders": `owner_criteria` names one file per dimension under `dev/governance/dimensions/criteria/`. The cards' proposal "the same change makes D<n>'s brief cite the criteria file" is built: `D4.md`, `D5.md`, `D9.md` and `D10.md` each name their file.
- Intake carry 175, this file's part (carry 0 of this group, items 803716a7): `tank_volume` (L: 50, 200, 1500) and `house_size` (heated area m² with heat loss kW/°C: 20 with 0.01, 140 with 0.15, 1000 with 1.0) carry `levels` as the flow rows' minimum, default and maximum and a `basis` naming those rows, re-read on this head: `config_flow.py` `_number(50, 1500, 10, 'L')` and `_number(20, 1000, 5, "m²")`, `RANGE_HOUSE_HEAT_LOSS: Final = (0.01, 1.0)`, `const.py` `DEFAULT_DHW_TANK_VOLUME` 200.0, `DEFAULT_HEATED_AREA` 140.0, `DEFAULT_HOUSE_HEAT_LOSS_COEFFICIENT` 0.15. Both stay `kind: null`: `check_scopes.py`'s `population` reads only `tuple`, `compare`, `regex` and `glob` kinds, none of which reads a declaration, so they stay NO-READ with a reason naming the builder R11-INTAKE-R10-RESIDUE.

**Wording declared under mandate 6893738184** (scope all, in force to 2026-12-15T12:00Z). This seat's line drafted the statements in all four criteria files: D4, D5 and D9 in full, and D10's Q1 to Q3. The edits to the four dimension briefs and `CLAUDE.md`, and the `corpus_tokens` raise, were made under the same mandate. Each criteria file says so and keeps the owner's words verbatim as a blockquote; the D10 target tier, platinum, is the owner's own word in `D10.md`.

**Where the directory sits.** `dev/governance/dimensions/criteria/`: the baseline export's `CURRENT_PATHS` (`tools/audit/prepare_baseline.sh`), `audit-find.js`'s `CURRENT` and `orchestrator_tick.py`'s `POLICY_PATHS` already carry `dev/governance/dimensions` whole, so every finder receives the criteria with no edit to those three; `dev/governance/criteria/` needed all three edited and lost on that count. Basenames are `D<n>-criteria.md`: `check_scopes.py`'s `read_harnesses` keys briefs by stem, and a second `D4.md` would overwrite the brief. The directory is classified in `tests/layout.json`, `tests/closure.py`'s `_CITATION_POLICY` (an edit selects `tests/entities.py`, as a brief's does), `dev/audit/config/scopes.json` (D6's universe and seat s2, beside the briefs) and `tests/closures.json`; p1 put it in `POLICY_GLOBS`.

**The merge of origin/main** (acf0f209c8) conflicted in `D4.md`, `D10.md` and `policy_budgets.json` against r11-pre-briefs-text (02d85c00e7). `D4.md` and `D10.md` keep that group's added lines (the wrong-physical-kind option probe, the diagnostics location drive) and its pointer to `owner_criteria`, which now names the criteria file the same sentence cites; `D10.md`'s tier list stays the pointer to `quality_scale.yaml`. The budgets file takes main's caps, then 1fd39aaa87 re-measures this group's rows.

**The merge of origin/main 921214bf42** (cb52dc931e) conflicted in `CLAUDE.md` against #3626 (R11-PRE-RULINGS-FILE). Main replaced the `## Root-cause remediation` section whole with `## What the repository may carry`; this branch's hunk there only deleted words inside that section (payment 2 below) and added none, so the union of the two edits is main's section verbatim. Every other #3626 line merged clean. This group's own added paragraph, the index line naming the four criteria files, merged clean and was shortened to fit `CLAUDE.md`'s `files_tokens` cap, from three lines to two that open `Finder criteria (` and name `owner_criteria` and the four files; the directory is dropped because each basename is unique in the tree, and `objective.json` because `owner_criteria` is its key. Read back at the head, both sides present (`grep -n` on `CLAUDE.md`): #3626's ``AGENTS.md` binds a harness``, `### The suite, the register, the rulings, the handover`, ``dev/programme/RULINGS.md` — the owner's rulings`` and `## What the repository may carry` with its six lines, and the steward line without its `babysit/` sentence; this group's line opening `Finder criteria (`. `git diff origin/main HEAD -- CLAUDE.md` is that one added paragraph alone.

## Head

cb52dc931ec43cf6b4f23f975d9d530adf41bc15 on origin/main 921214bf4246 (Mon Nov 16 00:19 UTC 2026). The mutation proof, the null control and the `plants` run were taken at 1fd39aaa87 on 31117b1029de; this merge's delta is `CLAUDE.md` alone, which none of them reads, and the figures below marked as re-taken were re-run at cb52dc931e.

## Mutation proof

Each mutant was run in a scratch worktree of this head, then restored.

- M1 (`objective.json`): `thresholds.product_green_floor.value` and `owner_criteria.D4` set back to null. `python3 dev/audit/harnesses/r11_owner_criteria.py gaps <head merged with c6ce415b77> <mutant merged with c6ce415b77>` goes from 5 to 7 unset gaps; the two added read `E11-K-D4 is accepted for criterion D4, which dev/audit/config/objective.json still leaves unset` and the same for `E11-T-product_green_floor`.
- M2 (`scopes.json`): `dimensions/criteria,` dropped from the two brace globs. `python3 tools/audit/check_scopes.py --repo .` exits 1 with `FAIL D6 ...` and `classified in neither universe nor static: dev/governance/dimensions/criteria/D10-criteria.md` (and D4, D5, D9). Restored: exit 0.
- M3 (`tests/closures.json`): the four criteria entries removed from `tests/entities.py`'s closure. `PYTHONPATH=tests/hastub python3 tests/entities.py` prints `2 of 2723 ENTITY CHECKS FAILED`, rc 1: `every tracked file is either measured or deliberately classified [these force the FULL suite when touched: dev/governance/dimensions/criteria/D10-criteria.md, ...D4, D5, D9]` and `every carry and every policy file this arm reads for citations selects this script ... selecting no script or the whole suite: [the four criteria files]`. At the head: `ALL 2723 ENTITY CHECKS PASSED`, rc 0.

## Null control

- `python3 dev/audit/harnesses/r11_owner_criteria.py gaps c6ce415b77 <head merged with c6ce415b77>`: both refs get a scratch overlay accepting every `E11-T-*` and `E11-K-*` card (10). At c6ce415b77 (main's `objective.json`) it prints 10 unset gaps: the six thresholds and criteria D4, D5, D9, D10. At the merge it prints 5: `band_closure_slip`, `band_lead_time`, `band_model_gap`, `band_tokens_per_change`, `closure_slip_ceiling`, still unset as ruled.
- `--round 11` at origin/main merged with c6ce415b77 against this head merged with it (`diff` of the two sorted outputs): the only gap lines removed are the five `accepted ... still leaves unset` lines for E11-K-D4, -D5, -D9, -D10 and E11-T-product_green_floor; the gap count goes from 51 to 46; the other differences are D5, D6, D11 and coverage counting the four new files. No gap line is added.
- D10's tier list cut is a duplicate, not a loss: the hyphenated rule names in origin/main's `D10.md` `Rules, by tier:` block against `yaml.safe_load(quality_scale.yaml)['rules']` printed `54 54 [] []`, both set differences empty; a rule present in only one would print in that direction's list.

## Figures

<!-- figure-block: scope-line mb=5825e1346c14eecace5c87c046558774145a94dc head=cb52dc931ec43cf6b4f23f975d9d530adf41bc15 -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->

`tests/closure.py` is in the diff, so the gate runs everything in CI; locally `tests/entities.py` (the script the closure change and the criteria files select) was run at 1fd39aaa87: `ALL 2723 ENTITY CHECKS PASSED`, rc 0; re-taken at cb52dc931e: `ALL 2723 ENTITY CHECKS PASSED`, rc 0.

- `python3 tools/audit/check_scopes.py --repo . --self-test`: `SELF-TEST passed (every perturbed scope refused)`, `population arms: 13/13 held`.
- `python3 tools/audit/check_scopes.py --repo . --population`: rc 0; `tank_volume` and `house_size` print `NO-READ` with the declared-levels reason; `NO-READ AXES: 2`, as at main.
- `python3 tools/audit/check_scopes.py --repo . --ref <ref> --round 11 | grep -c 'still leaves unset'`: 5 at c6ce415b77, 0 at this head merged with it. `grep -c 'is unset and no card'`: 0 at both, so the five deferred thresholds stay carried by their cards.
- `python3 dev/audit/harnesses/r11_owner_criteria.py plants` (sha1 e3b1350b1f4b5693b38317eaf895ff5cd82e9b82): `plants: 9, wrong: 0`, rc 0, re-taken at cb52dc931e. Per criteria file, a planted finding that meets the statement (FAILS) and one that does not (PASSES):
  - D10 Q1: `has-entity-name: todo` FAILS; `async-dependency` exempt with no comment FAILS; the live register PASSES.
  - D4 P2: `#777777` on `#ffffff`, 4.478, FAILS; `#767676`, 4.542, PASSES.
  - D5 C5: a 41-word sentence FAILS; an 11-word one PASSES.
  - D9 B1: 13.0 s host solver CPU × F=5 = 65.0 FAILS; 3.6 s × 5 = 18.0 PASSES.
  - A plant reading the wrong way prints `<-- WRONG` and exits 1.
- `node tools/policy/policy_lint.mjs`, re-taken at cb52dc931e: `TOTAL: 0 error(s) across 56 policy file(s)`; `FIXTURE ok`. Before the index line was shortened it printed `ERROR [budgets] CLAUDE.md: about 3624 tokens across its lines exceeds its cap of 3605 tokens`, the control that the cap reads this file. `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
- Re-taken at cb52dc931e: `python3 tools/audit/archscore/score.py --diff origin/main`: `Architecture score: dS +0.0000 NULL`; `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`; `python3 tools/audit/check_scopes.py --repo .`: rc 0; `python3 tools/pr/ci_predict.py --base origin/main`: `no closures, fast, governance or instrument red predicted against 921214bf4246`.
- `node tools/policy/policy_lint.mjs --budgets` re-taken at cb52dc931e, the row of each policy file this group grows or re-records (columns: lines, cap, ~tokens, cap, always), and the aggregates:
  - `CLAUDE.md 216 221 3604 3605 yes`
  - `tools/audit/briefs/D4.md 53 53 670 678`
  - `tools/audit/briefs/D5.md 48 48 620 624`
  - `tools/audit/briefs/D9.md 62 65 854 857`
  - `tools/audit/briefs/D10.md 32 32 410 410` (re-recorded down to the measured value)
  - `dev/governance/dimensions/criteria/D4-criteria.md 52 52 656 656`
  - `dev/governance/dimensions/criteria/D5-criteria.md 43 43 546 546`
  - `dev/governance/dimensions/criteria/D9-criteria.md 49 49 641 641`
  - `dev/governance/dimensions/criteria/D10-criteria.md 30 30 425 425`
  - `always-loaded: ~3604 tokens, cap 3349 +band 500 = 3849`
  - `corpus: ~71814 tokens, cap 71765 +band 500 = 72265`

  `tools/audit/briefs/D<n>.md` is the move map's name for `dev/governance/dimensions/D<n>.md`. The four criteria files' `files` and `files_tokens` caps are new rows at their measured values; beside them only `corpus_tokens` and `D10.md`'s two caps moved (`git diff origin/main -- dev/governance/config/policy_budgets.json`).

## Raise justification

`corpus_tokens`, raised to the value `node tools/policy/policy_lint.mjs --budgets` printed on its `corpus:` line at 1fd39aaa87. At cb52dc931e it prints `~71814 tokens, cap 71765 +band 500 = 72265`, and origin/main 921214bf4246 prints `~69748 tokens, cap 69333 +band 500 = 69833`; the cap is not re-recorded, since the measurement sits inside the band. At the merge base origin/main 31117b1029de the same line prints `~69740 tokens, cap 69333 +band 500 = 69833`: main already sits above its own cap, inside the band, and this group's four criteria files are new binding text finders grade against (cards E11-K-*, `gates_finders: true`), which no edit of existing prose can carry.

Payments tried: five, each measured by `--budgets` (1 to 3 taken, 4 and 5 not):

1. `D10.md`'s tier list restated the 54 rule names in `quality_scale.yaml` exactly (set comparison in `## Null control`); it is a pointer to the register and to Q1. Taken; `D10.md`'s caps re-recorded down.
2. `CLAUDE.md`'s root-cause sentence listed what `defect-root-cause.md` and `root-cause.md` hold, which the two policy tables already name. Cut, paying for the index line naming the four criteria files. #3626 has since removed that section whole on main, so this payment no longer appears in the diff; the index line was shortened instead (see the merge of 921214bf42), and `CLAUDE.md` and always-loaded are under their caps. Taken.
3. `D4.md`'s inline rubric is the criteria file's F3, F4 and I1 to I3, `D9.md`'s extrapolation paragraph its F, `D5.md`'s step-4 restatement its file: each replaced by a citation. Taken; each brief at or under its per-file cap.
4. Shortening the criteria files: not taken. Each statement carries a condition, a procedure, a pass and a fail beside the owner's words; a shorter one loses one of those, which `writing-for-agents.md` ranks below precision.
5. Excluding the files through `corpus_excluded.json`: refused. They bind finder seats, so they are policy and measured, the escape `checkNamedDocs` exists to close.

Architecture score: dS +0.0000 NULL (`python3 tools/audit/archscore/score.py --diff origin/main`, a prose and configuration diff). Approved under mandate 6893738184 (scope all, `CLAUDE.md` rule 2's exception, decision 0013) after review. The reason is in the commit messages of 0cea81273b and 1fd39aaa87.

## Approval

A policy change: `CLAUDE.md`, four dimension briefs, the four new criteria files and the code-owned `objective.json`. The wording and the raise were made under mandate 6893738184 (scope all, in force to 2026-12-15T12:00Z), so the approval is the orchestrator's declared review under that mandate, before the merge; the owner's approving review is still required wherever `CODEOWNERS` requires it (`main-protect-checks`).

## Red checks

- `budget-raise-gate`: red by construction until the `corpus_tokens` raise is approved at this head, here under mandate 6893738184 after review (decision 0013). No cheaper detector exists: the gate is the approval itself, and `prepr.sh` already predicts it before the push.

## Forward-carry

none

## Friction

none
