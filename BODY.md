R11-PRE-OWNER-CRITERIA: the owner's acceptance criteria for D4, D5, D9 and D10, the product_green floor, the seat models, and the declared levels of the two NO-READ population axes, all in `dev/audit/config/objective.json`.

Cards closed, read at eval/r11 `9de7c2bdc73361a5428d85bc444bf973c43bb593`. That tip carries the approving evaluation review: `.review` reads `approve` at sha `02a48db212e0e49af62863575cba86bc339d4958`, revision 2. It also carries the owner's recorded rulings (ca3f872430). Revision 2's rewrite of the four criterion cards is built here. Every card is accepted as built: product_green_floor, the four criteria and the seats are accepted, and the five other thresholds are deferred, so they stay unset. Under decision 0018 section 6 this merge must come after 02a48db212, and eval/r11 is not rebased past it. The cards:

- E11-T-product_green_floor, ruled "Floor 0.90, rest unset": `thresholds.product_green_floor.value` is 0.9, and the other five stay null.
- E11-S-SEATS, ruled "Record Fable for both": `seats.evaluator_model` and `seats.reviewer_model` are `claude-fable-5-2`.
- E11-K-D4, -D5, -D9, -D10, ruled "All four before finders": `owner_criteria` names one criteria file per dimension under the new `dev/governance/dimensions/criteria/`. Revision 2 adds "the same change makes D<n>'s brief cite the criteria file", so each of `D4.md`, `D5.md`, `D9.md` and `D10.md` now names its file.
- Intake carry 175, this file's part: `tank_volume` and `house_size` carry `levels` (minimum, default, maximum) and a `basis` naming the flow rows they were taken from. Both stay `kind: null`, because nothing reads the declaration yet. The builder stays R11-INTAKE-R10-RESIDUE.

**Wording declared under mandate 6893738184** (scope all, in force to 2026-12-15T12:00Z). This seat drafted the statements in all four criteria files: D4, D5 and D9 in full, and D10's Q1 to Q3. The edits to the four dimension briefs and to `CLAUDE.md`, the new `POLICY_GLOBS` pattern in `tools/policy/policy_lint.mjs`, and the `corpus_tokens` raise were also made under this mandate. Each criteria file says so, and keeps the owner's words verbatim as a blockquote. The owner's target tier for D10, platinum, is the owner's own word.

**Where the directory sits, and why.** It is `dev/governance/dimensions/criteria/`, not a sibling of `dimensions/`. The baseline export's `CURRENT_PATHS` (`tools/audit/prepare_baseline.sh`), `audit-find.js`'s `CURRENT` and `orchestrator_tick.py`'s `POLICY_PATHS` already carry `dev/governance/dimensions` whole. So every finder receives the criteria with no change to those three. The alternative, `dev/governance/criteria/`, needed all three edited, and lost on that count. Basenames are `D<n>-criteria.md`, not `D<n>.md`: `check_scopes.py`'s `read_harnesses` keys briefs by stem, and a second `D4.md` would overwrite the brief. The new directory had to be classified in four places, each refused without it (`## Mutation proof`):

- `POLICY_GLOBS`: the coverage check.
- `tests/layout.json`.
- `tests/closure.py`'s `_CITATION_POLICY`: an edit selects `tests/entities.py`, as an edit to a brief does.
- `dev/audit/config/scopes.json`: the files sit in D6's universe and in seat s2, beside the briefs.

`tests/closures.json` records the four files in `tests/entities.py`'s closure.

## Head

da868a90ffa56ba62502dde5b1268bbb093c8cd2

## Mutation proof

Each mutant was run on a copy of this head, then restored.

- M1: delete the criteria pattern from `POLICY_GLOBS` in `tools/policy/policy_lint.mjs`. `node tools/policy/policy_lint.mjs` then prints `[coverage] dev/governance/dimensions/criteria/D10-criteria.md: sits in a policy directory and matches no POLICY_GLOBS pattern`, plus `[budgets] ... has a cap ... but is matched by no POLICY_GLOBS pattern` and `[named-docs]`. It prints each line for all four files.
- M2: set `thresholds.product_green_floor.value` and `owner_criteria.D4` back to null. `python3 dev/audit/harnesses/r11_owner_criteria.py gaps <head merged with eval/r11> <mutant merged with eval/r11>` goes from 5 to 7 unset gaps. The two added are `E11-K-D4 is accepted for criterion D4, which dev/audit/config/objective.json still leaves unset` and the same line for `E11-T-product_green_floor`.
- M3: remove `dimensions/criteria` from the two `scopes.json` globs. `python3 tools/audit/check_scopes.py --repo .` then prints `FAIL D6 ... classified in neither universe nor static: dev/governance/dimensions/criteria/D10-criteria.md` (and D4, D5, D9), with rc=1.
- M4: before `tests/closures.json` recorded the files, `tests/entities.py` printed `2 of 2723 ENTITY CHECKS FAILED`. One was `every tracked file is either measured or deliberately classified [these force the FULL suite when touched: dev/governance/dimensions/criteria/D10-criteria.md, ...]`. The other was `every carry and every policy file this arm reads for citations selects this script [... selecting no script or the whole suite: [...criteria files...] of 57]`.

## Null control

- `python3 dev/audit/harnesses/r11_owner_criteria.py gaps origin/eval/r11 <head merged with eval/r11>`. Both refs get a scratch overlay that accepts every `E11-T-*` and `E11-K-*` card (10 cards). At eval/r11 (main's `objective.json`) it prints 10 unset gaps: the six thresholds and the criteria D4, D5, D9 and D10. At the merge it prints 5: `band_closure_slip`, `band_lead_time`, `band_model_gap`, `band_tokens_per_change` and `closure_slip_ceiling`. Those five stay unset as ruled, and each is still carried by its card. Without the overlay, `--round 11` at the merge prints no `is unset and no card carries it` line.
- `python3 tools/audit/check_scopes.py --repo . --self-test` at main with this head's `scopes.json`: no `SELF-TEST FAILED` line. At the head before the scopes commit, `SELF-TEST FAILED` printed three arms false: `the default verdict passes the live scopes`, `null control: the live D5 and D6 pass the cap and the line` and `the verdict's plant in .claude/workflows/ is a D5 unit`. After it, `SELF-TEST passed`.
- The D10 rule list cut is a duplicate, not a loss. A set comparison of the bracketed rule names in `D10.md`'s old tier list against `yaml.safe_load(quality_scale.yaml)['rules']` printed `54 54 [] []`: both directions empty. A rule present in only one would print in that direction's list.

## Figures

<!-- figure-block: scope-line mb=26dbf7c43ec3742101398b098dbdcc61bbee8f19 head=da868a90ffa56ba62502dde5b1268bbb093c8cd2 -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->

- `python3 tools/audit/check_scopes.py --repo . --self-test` at the head: `SELF-TEST passed (every perturbed scope refused)`.
- `python3 tools/audit/check_scopes.py --repo . --population` at the head: rc 0. `tank_volume` and `house_size` print as `NO-READ` with the new reason. LEVELS, PAIRS and NO-READ AXES are unchanged from main, because a NO-READ axis adds no level.
- `python3 tools/audit/check_scopes.py --repo . --ref <ref> --round 11 | grep -c 'still leaves unset\|is unset and no card'` on the ruled record. At eval/r11 9de7c2bdc7 it prints 5: criteria D4, D5, D9 and D10, and product_green_floor, each `accepted ... still leaves unset`. At this head merged with 9de7c2bdc7 it prints 0. The five deferred thresholds print no `unset and no card` line, because their cards still carry them.
- `python3 dev/audit/harnesses/r11_owner_criteria.py gaps origin/eval/r11 <head merged with eval/r11>`: 10 unset gaps at the control and 5 at the head (`## Null control`).
- `python3 dev/audit/harnesses/r11_owner_criteria.py plants`: `plants: 9, wrong: 0`, rc 0. Each criteria file gets one planted finding that meets it (prints FAILS) and one that does not (prints PASSES):
  - D10 Q1: `has-entity-name: todo` FAILS, and `async-dependency: exempt` with no comment FAILS. The live register PASSES, with no row printed.
  - D4 P2: `#777777` on `#ffffff` at 4.478 FAILS, and `#767676` at 4.542 PASSES.
  - D5 C5: a 41-word sentence FAILS, and an 11-word one PASSES.
  - D9 B1: 13.0 s of host CPU × F=5 = 65 Pi-s FAILS, and 3.6 s × 5 = 18 Pi-s PASSES.
  - A plant reading the wrong way prints `<-- WRONG` and the harness exits 1.
- `node tools/policy/policy_lint.mjs` at the head: `TOTAL: 0 error(s)`. `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
- `python3 tools/audit/archscore/score.py --diff origin/main` at the head: `Architecture score: dS +0.0000 NULL`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/pr/ci_predict.py --base origin/main`: `no closures, fast, governance or instrument red predicted`.
- Rows from `node tools/policy/policy_lint.mjs --budgets` for each policy file this group grows or re-records: `CLAUDE.md`; `tools/audit/briefs/D4.md`, `D5.md`, `D9.md` and `D10.md` (the move map's names for `dev/governance/dimensions/D<n>.md`); the four `dev/governance/dimensions/criteria/D<n>-criteria.md`; and the `corpus:` line. The four new files' `files` and `files_tokens` caps are the measured values. `D10.md`'s caps are re-recorded down to the measured value, and `corpus_tokens` is set to the value the `corpus:` line prints. No other cap moved.

## Raise justification

`corpus_tokens`, raised to the value `node tools/policy/policy_lint.mjs --budgets` prints on its `corpus:` line. At the merge base the corpus sat under its cap plus band. The four criteria files are new binding text that finders grade against (cards E11-K-*), and no edit of existing prose can carry them.

Payments tried: four cuts (items 1 to 3 below taken, 4 and 5 not), each measured by `--budgets`.

1. `D10.md`'s tier list restated the 54 rule names in `quality_scale.yaml` exactly (set comparison in `## Null control`). It is replaced by a pointer to the register and to Q1. Taken.
2. `CLAUDE.md`'s root-cause sentence listed what `defect-root-cause.md` and `root-cause.md` hold, which the two policy tables already state. Cut. It paid for the index line naming the four criteria files, and `CLAUDE.md` is under its per-file cap. Taken.
3. `D4.md`'s inline rubric is now the criteria file's F3, F4 and I1 to I3. `D9.md`'s extrapolation paragraph is now the criteria file's F. `D5.md`'s step-4 restatement now names the criteria file. Each is replaced by a citation. Taken, and each brief is at or under its own per-file cap.
4. Shortening the criteria files: not taken past the present text. Each statement carries a condition, a procedure, a pass and a fail, and the owner's words verbatim. A shorter statement loses one of those, which `writing-for-agents.md` ranks below precision.
5. Excluding the files from the corpus through `corpus_excluded.json`: refused. They bind finder seats, so they are policy and must be measured, which is the escape `checkNamedDocs` exists to close.

Architecture score: dS +0.0000 NULL (`python3 tools/audit/archscore/score.py --diff origin/main`, a prose and configuration diff). Approved under mandate 6893738184 (scope all, `CLAUDE.md` rule 2's exception, decision 0013). The reason is in the commit message of 0cea81273b.

## Approval

This is a policy change: it touches `CLAUDE.md`, four dimension briefs, the four new criteria files and the code-owned `objective.json`. The wording and the raise were made under mandate 6893738184 (scope all, in force to 2026-12-15T12:00Z), so the approval is the orchestrator's declared review under that mandate, given before the merge. The owner's approving review is still required wherever `CODEOWNERS` requires it (`main-protect-checks`).

## Red checks

- `budget-raise-gate`: red by construction until the raise of `corpus_tokens` is approved at this head, here under mandate 6893738184 after review (decision 0013). No cheaper detector exists: the gate is the approval itself, and `prepr.sh` already predicts it before the push.

## Forward-carry

none

## Friction

- brief-roster: unclear: the brief says R11-PRE-OWNER-CRITERIA "is being written to the roster branch origin/handoff/audit-r10-roster by a queued roster op". At that branch's tip at this handoff, `jq '.groups[]|select(.group=="R11-PRE-OWNER-CRITERIA")'` prints nothing, so no carry could be read from the group. Carry: dismissed: the relay's roster op owns the write; nothing for this seam to build.
