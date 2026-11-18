R11-PRE-MACHINERY-LIMITER, part 2 of 3: the group's carries 5-9 (P742's routing, ratified by tvofi 2026-11-15; cards L2, L4 and L5 approved as policy text under the mandate if sound, card O2). Carries 10-13 belong to part 3. This part answers none of them.

**Carry 5, the stale budget key.** `policy_budgets.json` keys a moved file's caps at its old path, because `policy_lint.mjs` looks every listed file up by its `canon` (old) spelling. Grepping the live path finds no cap. Re-keying is not this part's to do: the base's grader canonicalises before the lookup, so new keys would be read as "no cap recorded" (a BOOTSTRAP split, `fixer.md` step 5), and the roster already gives the re-key to the move map's retirement (R9-RO-9; carry 2d5abee2 drops `dev/governance/config/` from the layout guard "since the keys stop being canon-spelt"). Instead, the reader's instrument answers the question. `node tools/policy/policy_lint.mjs --budgets` prints each row at the live path, and a moved file's row names its key (`dev/audit/README.md ... key tools/audit/README.md`). A `_keys` note in the budget file says so. Alternatives: a hand map of old to new keys in the JSON (refused: it is a second copy of `tests/layout.json` that goes stale), and accepting both spellings in the grader (refused: the base copy grades this pull request).

**Carry 6.** `dev/audit/README.md` names `dev/audit/rounds/round10/protection-census/CENSUS.md`, not its directory. The file joins `corpus_excluded.json`'s `excluded` as round evidence, the class that file's `_comment` names (a round baseline a later seat reads).

**Carry 7 (L2)**, in `root-cause.md` section 5: countermeasures go in rungs, in order: delete, then self-repair, then narrow, with a new refusal last. A later rung states why each earlier one is not possible, and a product check is exempt. A new refusal prints its own repair command and shows its refusal count on the last 20 healthy heads (a shadow run) before it gates. `proposal-triage.md`'s bar points to the rungs, and D11's mechanise-first (tvofi 2026-10-24) reads as repair before refuse, as the card says.

**Carry 8 (L4)**, in `defect-root-cause.md`'s cost test: the cost side prices induced work. That is the follow-up items expected (the instrument's offspring rate in `loop_ledger.py`, L1's enumerator, times an item's mean cost) plus the generated artifacts or pins the change stales in open branches. While the ledger reads `unread`, the rates are the loop study's per RCA and per machinery merge (round-10 round-end triage, P742). `proposal-triage.md`'s bar names induced work. The card's literal figures are not written into policy: their corpus is out of tree (`$HPO_STATE_DIR/s14/seat/loop-study-1114/`), so this seat cannot re-measure them, and the P742 entry carries them.

**Carry 9 (L5)**, in `proposal-triage.md`: the round-end triage makes one ruling per instrument named. An instrument's third change in a round is ruled retire, simplify, redesign (`designer.md`) or leave, never a patch.

Payment for the policy caps: `root-cause.md` lost its restatement of the separate-seat reason and of the (c)/(d)-as-(b) mistake (both carried by `defect-root-cause.md`), the duplicate "say which state it addresses" in section 5, a motivation sentence in section 3, and "Be brief and precise". `defect-root-cause.md` lost the scaffolding sentence on what countermeasures "may change", "Either of:", and the reworded state paragraph. `proposal-triage.md` lost the RULINGS clause (`CLAUDE.md` already binds every seat to it), the restated ruling quote, and the refusal clause `roster_edit.py`'s self-test pins. `root-cause.md` and `defect-root-cause.md` are recorded down to measured. `proposal-triage.md` is raised to measured (`## Raise justification`).

## Head

`8081be96205450af575c6552d44c9de8b843393c`, merge base `76bbf637442f586fd9d91dd565b496445db282f0` (`origin/main` at this repair, read 2026-11-18 UTC). The head is the merge of that `origin/main` into `c610244de5`, which `#3688` was DIRTY against: `git merge-tree --write-tree origin/main c610244de5` printed `CONFLICT (content): Merge conflict in dev/governance/config/policy_budgets.json`. **The resolution changes reviewed content**: the last verdict (merge at `f7ef7c06`) read a budget file this merge rewrites, so the delta from `f7ef7c06` is a delta reviewer's to judge.

Resolution, by measurement, not by side. The only conflicted hunk was `files_tokens` for `dev/governance/roles/architect-planner.md` (branch side the base's 1261, main 1325); main's value is kept, since this branch never changed that row and `node tools/policy/policy_lint.mjs --budgets` at the merged tree reads it at 1325 of 1325. Every other main entry is kept as main wrote it (D16, D17, `architect-planner.md` lines, `plan-review.md`, `corpus_tokens`). This branch's raise is kept at the value the measure reads at the merged tree: `dev/governance/roles/proposal-triage.md` 42 lines and 594 tokens (unchanged from `f7ef7c06`, 40->42 and 563->594). The `d82c5b2f` drops of the `tools/audit/briefs/nudge.md` and `tools/audit/harnesses/README.md` token caps are no longer owed as a branch change: main deleted the same two rows, `git diff origin/main HEAD -- dev/governance/config/policy_budgets.json | grep -cE "nudge|harnesses/README"` prints 0, and neither file exists at the merged tree. No other raise is added: the three-dot diff's budget rows are `proposal-triage.md` up and `root-cause.md` / `defect-root-cause.md` down, as at `f7ef7c06`.

prepr: passed rc=0 at 8081be96205450af575c6552d44c9de8b843393c

## Mutation proof

The carry 5 check (`tests/entities.py`, "`policy_lint.mjs --budgets` prints a moved policy file at its live path, ...") was run alone through a scratch driver: the block copied verbatim, with a stub `R` that prints PASS or FAIL. Each mutant was applied to `tools/policy/policy_lint.mjs` and then restored:
- the change reverted (`git stash` of `policy_lint.mjs`): FAIL, rows `tools/audit/README.md ... 6059` (the old spelling) and no key;
- `const live = locate(r.file)` -> `const live = r.file`: FAIL;
- `const key = live === r.file ? '' : ...` -> the key on every row: FAIL, because the unmoved `tests/README.md` row names a key.
At the head: PASS.

Carry 6, re-run at the merged head `8081be9620`: with `corpus_excluded.json`'s new entry removed, `node tools/policy/policy_lint.mjs` prints `ERROR [named-docs] dev/audit/rounds/round10/protection-census/CENSUS.md: is named by tools/audit/README.md but has no cap ...` and `TOTAL: 1 error(s)`. With the entry restored: `TOTAL: 0 error(s)`.

Carries 7-9 are policy text with no executable predicate. Their check is `policy_lint.mjs`'s budgets class (refusing each file before its payment, `TOTAL: 2 error(s)` for `root-cause.md` and for `proposal-triage.md` in turn) and `rules_sync.mjs --check`. Re-run at the merged head for the resolved raise: `proposal-triage.md`'s `files_tokens` set back to 563 prints `ERROR [budgets] dev/governance/roles/proposal-triage.md: about 594 tokens across its lines exceeds its cap of 563 tokens (files_tokens)` and `TOTAL: 1 error(s)`; restored to 594, `TOTAL: 0 error(s)`. So 594 is the merged tree's measure, not a carried figure.

## Null control

- In the carry 5 check, `tests/README.md` (unmoved) prints with no key. A printer that names a key on every row fails it, as shown above.
- `git grep -c "dev/audit/README.md" 30f9caac90 -- dev/governance/config/policy_budgets.json` exits 1 (no match) at the base. That is the reported defect: no live path appears in the budget file.

## Figures

- The class enumerated (`fixer.md` step 8): `node -e 'import("./tools/policy/counts.mjs").then(c=>{const b=JSON.parse(require("fs").readFileSync("dev/governance/config/policy_budgets.json"));for(const k of Object.keys(b.files)) if(c.locate(k)!==k) console.log(k)})'` lists every `files` key spelt at a moved path: 24 of 56. `node tools/policy/policy_lint.mjs --budgets | grep -c " key "` prints 23. The one key with no row is `.claude/workflows/fixtures/policy-rot/budgets.md`, the `budgets` fixture's own cap (`comm -23` of the two lists), which is not a corpus row. Disposition: the other 23 are closed by this diff (each row names its key), and the re-key is the move map's retirement, R9-RO-9.
- `python3 -I tools/audit/seat/loop_ledger.py` at the merge base prints `unread` or `k none (no countermeasure)` for every week's `loop` read. That is the condition under which L4's fallback rates apply.
- `node tools/policy/policy_lint.mjs --budgets` at `8081be9620`: rc 0, every row within its cap; the three touched rows are at their recorded caps (`proposal-triage.md` 42/42, 594/594; `root-cause.md` 81/81, 990/990; `defect-root-cause.md` 151/151, 1885/1885); aggregates `corpus` 71371 against cap 71212 + band 500. `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s)`. `node tools/policy/rules_sync.mjs --check`: ok.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `python3 tools/audit/archscore/score.py --diff 76bbf637442f586fd9d91dd565b496445db282f0 HEAD` at `8081be9620` prints `Architecture score: dS +0.0000 NULL`. `git diff --stat 76bbf63744...HEAD -- custom_components` prints nothing, so NULL is the score's own scope.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` and `tests/harness_headers.py`, the two scripts `scope.run` names: both rc 0 at `8081be9620` (`ALL 2732 ENTITY CHECKS PASSED`, `ALL 115 HARNESS HEADER CHECKS PASSED`). The indented `FAIL` lines in `entities.py`'s log are its self-tests' negative-control fixtures; the script's exit code and its closing line are the verdict.

<!-- figure-block: scope-line mb=b98c78e0f6144a5ea5b48a032e30bf2d085c2d61 head=8081be96205450af575c6552d44c9de8b843393c -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->

## Raise justification

`dev/governance/config/policy_budgets.json`: `dev/governance/roles/proposal-triage.md`'s line cap goes from 40 to 42 and its token cap from 563 to 594, both the measured values `--budgets` prints. Cards L2, L4 and L5 each require text in this file. Raised under mandate 6893738184 (scope all, `dev/programme/RULINGS.md`), which `CLAUDE.md` rule 2 and decision 0013 allow once no payment that improves the architecture exists.
- Payments tried: taken, the duplicated RULINGS clause; the restated "once per round" quote; the `roster_edit.py` refusal clause (pinned by its self-test); a reflow of every paragraph. Together these took the overage from 5 lines and 87 tokens to 2 lines and 31 tokens.
- Considered and not taken: cutting the proposal sources "(sweep, seat results, verdict notes)" (refused: it says where the round-end consolidation gathers from); cutting the machinery paragraph's exemptions (refused: part 3 owns its narrowing); moving L5 into `dev/audit/README.md` (refused: the card makes it the triage seat's ruling, and the playbook's freeze section is part 3's); carrying L2 and L4 only in `root-cause.md` and `defect-root-cause.md` (refused: both cards name `proposal-triage.md`).
- Net across the three touched caps: lines 277 -> 274, tokens 3448 -> 3469 (unchanged by the main merge: none of the three files differs between `c610244de5` and `8081be9620`).
- The main merge (`76bbf63744`) is no payment and no raise: it keeps main's rows and the one raise above at its re-measured value.
- Architecture score: dS +0.0000 NULL

## Unpinned sites

`prepr.sh`'s diff-mutant step draws only added `.py` lines outside `tests/` and `dev/`. This diff adds none: its one code change is in `tools/policy/policy_lint.mjs`, and the hand mutants above cover it.

## Red checks

The owed set is what `python3 tools/audit/seat/merge_train.py owed-reds` prints at this repair; `python3 tools/audit/seat/merge_train.py classify c610244de5a4833485a54e570329618a687f2de9 --pr 3688` printed `RED ... pending: none red: gate` and no INTRODUCED line.
- `gate` (in the owed set): red only on `budget-raise-gate` (`tvofi approval is on f7ef7c069865, not this head`). The raise of `files` and `files_tokens` for `dev/governance/roles/proposal-triage.md` (`prepr.sh` body check `budget_raises`) needs an approving review at the head, `## Raise justification` and `## Approval`; the merge moves the head, so the approval at `f7ef7c06` no longer reads. No cheaper detector exists: the gate is the approval itself, and `prepr.sh` predicts it before the head moves. Clearing it is the orchestrator's re-approval under the mandate after a delta reviewer, not this seat's.
- `governance / env-matrix` (in the owed set): red on a commit of this branch before `d82c5b2fd2`, green at `c610244de5` (job 134333096756, `success`). Cause, per `d82c5b2fd2`'s message: main retired `tools/audit/briefs/nudge.md` and `tools/audit/harnesses/README.md` (#3668), and main's pinned `policy_lint.mjs` (`checkOrphanCaps` reading `files_tokens`, 18eba6b397) refused this branch's budget file, which still carried their two `files_tokens` rows; `governance / policy-docs` refused the same rows. Fixed by `d82c5b2fd2` (the two rows dropped); at `8081be9620` main's merge carries the same deletion, and `node tools/policy/policy_lint.mjs` prints `TOTAL: 0 error(s)`. Process state (d): the branch was clean when last proven, and main's grader and file set changed underneath it. Cheaper detector: none beyond the one that ran. The change on main was semantic, not textual, so `git merge-tree` showed no conflict, and the detector that sees it is CI's pinned grader run against the current main, which is what the train re-runs on every head. No countermeasure built.
- `tests / briefs` (in the owed set): red at `c610244de5` (job 134333097057): `FIXTURE VACUOUS: shape-defects acceptance pins missing: [gates-not-bool]`. Cause: main's `9fb327ecb3` added that pin to `tools/policy/brief_lint.mjs`'s acceptance and the matching entry to `tools/policy/fixtures/shape-defects.json`. CI graded `c610244de5`'s fixture, which predates the entry (`git merge-base --is-ancestor 9fb327ecb3 c610244de5` exits 1), with main's pinned grader. At `8081be9620` (`9fb327ecb3` is an ancestor) `node tools/policy/brief_lint.mjs` exits 0, prints `ERROR [gates-not-bool] shape: ...` among the fixture's pinned errors, and prints no `VACUOUS` line; at `c610244de5` locally (its own grader) it prints neither. Fixed by this merge, with no change of its own. Process state (d): main's grader and fixture moved together after the branch's base, and the branch carried only the old fixture. Cheaper detector: none beyond the one that ran. The pinned-grader run against the current main is the detector, and the train re-runs it on every head. No countermeasure built.
- `budget-raise-gate / budget-raise-gate` is outside the owed set and is answered only through `gate` above.

## Approval`. No cheaper detector exists: the gate is the approval itself, and `prepr.sh` already predicts it before the pull request opens.
- `gate`: follows the one above and has no failure of its own.

## Approval

This diff changes policy that `.github/CODEOWNERS` assigns to @tvofi (`dev/governance/roles/root-cause.md`, `dev/governance/roles/proposal-triage.md`, `dev/governance/rules/defect-root-cause.md` and its generated copies, `dev/audit/README.md`) and raises a cap in a `*_budgets.json`. It merges only on an approving review at the head (decision 0009 step 6, decision 0013). That review is the owner's, or one posted under mandate 6893738184 (scope all) citing it. Card O2 approves L2, L4 and L5's policy text under the mandate if sound.

## Forward-carry

none

## Friction

none
