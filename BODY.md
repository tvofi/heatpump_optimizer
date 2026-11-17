R11-PRE-MACHINERY-LIMITER, part 2 of 3: the group's carries 5-9 (P742's routing, ratified by tvofi 2026-11-15; cards L2, L4 and L5 approved as policy text under the mandate if sound, card O2). Carries 10-13 belong to part 3. This part answers none of them.

**Carry 5, the stale budget key.** `policy_budgets.json` keys a moved file's caps at its old path, because `policy_lint.mjs` looks every listed file up by its `canon` (old) spelling. Grepping the live path finds no cap. Re-keying is not this part's to do: the base's grader canonicalises before the lookup, so new keys would be read as "no cap recorded" (a BOOTSTRAP split, `fixer.md` step 5), and the roster already gives the re-key to the move map's retirement (R9-RO-9; carry 2d5abee2 drops `dev/governance/config/` from the layout guard "since the keys stop being canon-spelt"). Instead, the reader's instrument answers the question. `node tools/policy/policy_lint.mjs --budgets` prints each row at the live path, and a moved file's row names its key (`dev/audit/README.md ... key tools/audit/README.md`). A `_keys` note in the budget file says so. Alternatives: a hand map of old to new keys in the JSON (refused: it is a second copy of `tests/layout.json` that goes stale), and accepting both spellings in the grader (refused: the base copy grades this pull request).

**Carry 6.** `dev/audit/README.md` names `dev/audit/rounds/round10/protection-census/CENSUS.md`, not its directory. The file joins `corpus_excluded.json`'s `excluded` as round evidence, the class that file's `_comment` names (a round baseline a later seat reads).

**Carry 7 (L2)**, in `root-cause.md` section 5: countermeasures go in rungs, in order: delete, then self-repair, then narrow, with a new refusal last. A later rung states why each earlier one is not possible, and a product check is exempt. A new refusal prints its own repair command and shows its refusal count on the last 20 healthy heads (a shadow run) before it gates. `proposal-triage.md`'s bar points to the rungs, and D11's mechanise-first (tvofi 2026-10-24) reads as repair before refuse, as the card says.

**Carry 8 (L4)**, in `defect-root-cause.md`'s cost test: the cost side prices induced work. That is the follow-up items expected (the instrument's offspring rate in `loop_ledger.py`, L1's enumerator, times an item's mean cost) plus the generated artifacts or pins the change stales in open branches. While the ledger reads `unread`, the rates are the loop study's per RCA and per machinery merge (round-10 round-end triage, P742). `proposal-triage.md`'s bar names induced work. The card's literal figures are not written into policy: their corpus is out of tree (`$HPO_STATE_DIR/s14/seat/loop-study-1114/`), so this seat cannot re-measure them, and the P742 entry carries them.

**Carry 9 (L5)**, in `proposal-triage.md`: the round-end triage makes one ruling per instrument named. An instrument's third change in a round is ruled retire, simplify, redesign (`designer.md`) or leave, never a patch.

Payment for the policy caps: `root-cause.md` lost its restatement of the separate-seat reason and of the (c)/(d)-as-(b) mistake (both carried by `defect-root-cause.md`), the duplicate "say which state it addresses" in section 5, a motivation sentence in section 3, and "Be brief and precise". `defect-root-cause.md` lost the scaffolding sentence on what countermeasures "may change", "Either of:", and the reworded state paragraph. `proposal-triage.md` lost the RULINGS clause (`CLAUDE.md` already binds every seat to it), the restated ruling quote, and the refusal clause `roster_edit.py`'s self-test pins. `root-cause.md` and `defect-root-cause.md` are recorded down to measured. `proposal-triage.md` is raised to measured (`## Raise justification`).

## Head

`d82c5b2fd24828d2bea5d88683b64a859d26c8a8`, merge base `b08346b222450ad15868e5ead43d56757554d0f4` (`git merge-base origin/main HEAD`; `origin/main` was `8f39313a44a4baec18b239ba925f6e164eb26bd2` at this repair). Its one commit after the previous head `f7ef7c069865bdf254044c6c334b9b5e1b22c30e` deletes the `files_tokens` caps of `tools/audit/briefs/nudge.md` and `tools/audit/harnesses/README.md` from `dev/governance/config/policy_budgets.json`: neither file is in the tree, and `main` deleted the same two lines (#3668). `git merge-tree --write-tree origin/main HEAD` exits 0, so `main` was not merged. The figures below that name `794f78f5013274a8ba31b1589400b7d6c98fa830` or `b8561131ab` were taken there; this commit touches no file they read except `policy_budgets.json`, re-measured in `## Figures`.

prepr: passed rc=0 at d82c5b2fd24828d2bea5d88683b64a859d26c8a8

## Mutation proof

The carry 5 check (`tests/entities.py`, "`policy_lint.mjs --budgets` prints a moved policy file at its live path, ...") was run alone through a scratch driver: the block copied verbatim, with a stub `R` that prints PASS or FAIL. Each mutant was applied to `tools/policy/policy_lint.mjs` and then restored:
- the change reverted (`git stash` of `policy_lint.mjs`): FAIL, rows `tools/audit/README.md ... 6059` (the old spelling) and no key;
- `const live = locate(r.file)` -> `const live = r.file`: FAIL;
- `const key = live === r.file ? '' : ...` -> the key on every row: FAIL, because the unmoved `tests/README.md` row names a key.
At the head: PASS.

Carry 6: with `corpus_excluded.json`'s new entry removed, `node tools/policy/policy_lint.mjs` prints `ERROR [named-docs] dev/audit/rounds/round10/protection-census/CENSUS.md: is named by tools/audit/README.md but has no cap ...` and `TOTAL: 1 error(s)`. With the entry restored: `TOTAL: 0 error(s)`.

Carries 7-9 are policy text with no executable predicate. Their check is `policy_lint.mjs`'s budgets class (refusing each file before its payment, `TOTAL: 2 error(s)` for `root-cause.md` and for `proposal-triage.md` in turn) and `rules_sync.mjs --check`.

## Null control

- In the carry 5 check, `tests/README.md` (unmoved) prints with no key. A printer that names a key on every row fails it, as shown above.
- `git grep -c "dev/audit/README.md" 30f9caac90 -- dev/governance/config/policy_budgets.json` exits 1 (no match) at the base. That is the reported defect: no live path appears in the budget file.

## Figures

- The class enumerated (`fixer.md` step 8): `node -e 'import("./tools/policy/counts.mjs").then(c=>{const b=JSON.parse(require("fs").readFileSync("dev/governance/config/policy_budgets.json"));for(const k of Object.keys(b.files)) if(c.locate(k)!==k) console.log(k)})'` lists every `files` key spelt at a moved path: 24 of 56. `node tools/policy/policy_lint.mjs --budgets | grep -c " key "` prints 23. The one key with no row is `.claude/workflows/fixtures/policy-rot/budgets.md`, the `budgets` fixture's own cap (`comm -23` of the two lists), which is not a corpus row. Disposition: the other 23 are closed by this diff (each row names its key), and the re-key is the move map's retirement, R9-RO-9.
- `python3 -I tools/audit/seat/loop_ledger.py` at the merge base prints `unread` or `k none (no countermeasure)` for every week's `loop` read. That is the condition under which L4's fallback rates apply.
- `node tools/policy/policy_lint.mjs --budgets`: every row within its cap at the head; the three touched rows are at their recorded caps. `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s)`. `node tools/policy/rules_sync.mjs --check`: ok.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `python3 tools/audit/archscore/score.py --diff 30f9caac90735c402c8e3ae60fbaa80c45dc6d26 HEAD` prints `Architecture score: dS +0.0000 NULL`. `git diff --stat 30f9caac90..HEAD -- custom_components` prints nothing, so NULL is the score's own scope.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` and `tests/harness_headers.py`, the two scripts `scope.run` names: both rc 0 at `b8561131ab` (`ALL 2724 ENTITY CHECKS PASSED`, `ALL 115 HARNESS HEADER CHECKS PASSED`); the head adds only a comment to `tests/entities.py`.

- The repair of `governance / policy-docs` and `governance / env-matrix`: CI runs `main`'s pinned `tools/policy/policy_lint.mjs` against this branch's budget file. Driven locally by running, with node from the tree root, a scratch copy of the file `git show origin/main:tools/policy/policy_lint.mjs` prints, placed beside the branch's `tools/policy/policy_lint.mjs` and deleted after (stated without a runnable command, since the copy is not in the tree): at `f7ef7c069865bdf254044c6c334b9b5e1b22c30e` rc 1 with the two `ERROR [budgets] ... has a cap in ... files_tokens but is matched by no POLICY_GLOBS pattern` lines the CI logs print (the control: the defect reads); at `d82c5b2fd24828d2bea5d88683b64a859d26c8a8` rc 0 and `grep -c ERROR` 0. The branch's own `node tools/policy/policy_lint.mjs` exits 0 at the new head.
- At `d82c5b2fd24828d2bea5d88683b64a859d26c8a8`: `python3 tests/structure.py` prints STRUCTURE RATCHET PASSED; the branch's `python3 tests/closure.py select --diff b08346b222450ad15868e5ead43d56757554d0f4` prints `MODE: SCOPED` and its `scope.run` names `tests/entities.py` and `tests/harness_headers.py`, both rc 0 under `PYTHONPATH=tests/hastub` (`ALL 2724 ENTITY CHECKS PASSED`, `ALL 115 HARNESS HEADER CHECKS PASSED`). The registered block below is rendered with `origin/main`'s instruments over this head and prints `MODE: FULL`: CI runs the full suite on this head, which the scoped local run does not discharge.

<!-- figure-block: scope-line mb=b08346b222450ad15868e5ead43d56757554d0f4 head=d82c5b2fd24828d2bea5d88683b64a859d26c8a8 -->
~~~text
MODE: SCOPED -- 2 script(s) run, 31 scoped out.
~~~
<!-- /figure-block -->

## Raise justification

`dev/governance/config/policy_budgets.json`: `dev/governance/roles/proposal-triage.md`'s line cap goes from 40 to 42 and its token cap from 563 to 594, both the measured values `--budgets` prints. Cards L2, L4 and L5 each require text in this file. Raised under mandate 6893738184 (scope all, `dev/programme/RULINGS.md`), which `CLAUDE.md` rule 2 and decision 0013 allow once no payment that improves the architecture exists.
- Payments tried: taken, the duplicated RULINGS clause; the restated "once per round" quote; the `roster_edit.py` refusal clause (pinned by its self-test); a reflow of every paragraph. Together these took the overage from 5 lines and 87 tokens to 2 lines and 31 tokens.
- Considered and not taken: cutting the proposal sources "(sweep, seat results, verdict notes)" (refused: it says where the round-end consolidation gathers from); cutting the machinery paragraph's exemptions (refused: part 3 owns its narrowing); moving L5 into `dev/audit/README.md` (refused: the card makes it the triage seat's ruling, and the playbook's freeze section is part 3's); carrying L2 and L4 only in `root-cause.md` and `defect-root-cause.md` (refused: both cards name `proposal-triage.md`).
- Net across the three touched caps: lines 277 -> 274, tokens 3448 -> 3469.
- Architecture score: dS +0.0000 NULL

## Unpinned sites

`prepr.sh`'s diff-mutant step draws only added `.py` lines outside `tests/` and `dev/`. This diff adds none: its one code change is in `tools/policy/policy_lint.mjs`, and the hand mutants above cover it.

## Red checks

- `budget-raise-gate / budget-raise-gate` (predicted by `prepr.sh`'s body check: `budget_raises` for `files` and `files_tokens` of `dev/governance/roles/proposal-triage.md`): red by design until an approving review at the head, `## Raise justification` and `
- `governance / policy-docs` and `governance / env-matrix` (red at `f7ef7c069865bdf254044c6c334b9b5e1b22c30e`): `policy_lint.mjs` refused the `files_tokens` caps of `tools/audit/briefs/nudge.md` and `tools/audit/harnesses/README.md` as caps on no corpus file. Cause: CI pins `main`'s `policy_lint.mjs`, whose orphan-cap check reads `files_tokens` (`18eba6b397`), and `main` retired both files and their caps (#3668); both landed on `main` after this head's last merge of it, so the branch's budget file still carried the two rows. Repaired at `d82c5b2fd24828d2bea5d88683b64a859d26c8a8` by the same deletion (`## Figures`). Cheaper detector: none exists before the red — no check on this branch could see a checker and a deletion that were not yet on `main`; after `main` moves, the train re-proves the head on the current `main`, which is where the skew is first readable.
- `pr-contract / pr-contract` (red at `f7ef7c069865bdf254044c6c334b9b5e1b22c30e`): the body's `## Red checks` did not name the two reds above. This body names them; `prepr.sh`'s body check, which `pr-contract` re-executes, passed on it. No cheaper detector: the check is the body check itself, and the reds it requires answered appeared after the body was written.

## Approval`. No cheaper detector exists: the gate is the approval itself, and `prepr.sh` already predicts it before the pull request opens.
- `gate`: follows the one above and has no failure of its own.

## Approval

This diff changes policy that `.github/CODEOWNERS` assigns to @tvofi (`dev/governance/roles/root-cause.md`, `dev/governance/roles/proposal-triage.md`, `dev/governance/rules/defect-root-cause.md` and its generated copies, `dev/audit/README.md`) and raises a cap in a `*_budgets.json`. It merges only on an approving review at the head (decision 0009 step 6, decision 0013). That review is the owner's, or one posted under mandate 6893738184 (scope all) citing it. Card O2 approves L2, L4 and L5's policy text under the mandate if sound.

## Forward-carry

none

## Friction

none
