_Requested by **tvofi**_

R9-F11.4 precursor: `resolvePrFromCommit` reads the squash shape too (D13-s1-01), and `policy_lint.mjs` exports `rulePaths`.

Part of #1650
Part of #201

Before: when `/commits/<sha>/pulls` answered `[]`, `resolvePrFromCommit` recovered a number only from the `Merge pull request #N from` shape, so a squash-shape subject (`fix: a squash (#1234)`, which `stamp.py`'s `pr_from_subject` and `delivery_status.py`'s `subject_number` both read) came back null and the merge was dropped from the window. `rulePaths`, the one place a rule's frontmatter paths are parsed for the role budgets, was not exported.

After: `resolvePrFromCommit` reads both shapes and still returns null for a stamp subject. `rulePaths` is exported. Nothing else changes.

Why a separate PR: the landing PR for the I4 agreement lane (#1847) cannot be graded by main's base-pinned copies of `policy_lint.mjs` until main carries these two. The lane's `rule-frontmatter-paths` reader throws on `pl.rulePaths is not a function`, and its `merge-subject-pr` pair diverges on the squash shape, on main's copies. Same route as #1842 before #1838. The three `field_coverage.mjs` DECLARED entries are not here: on main alone they are DEAD (`DECLARED ... is no longer in the derived set`, measured at `af7660c7`), because the pins they describe arrive with #1847.

## Head

`9d03708beaffc5af90336fbf81068524df606707` is one commit on origin/main `af7660c749a65762934d45b7c91957102253e209`.

## Mutation proof

Both tests were written first and red on main's code, then green with the fix, and each fix line was removed again:
- Removing `|| MERGE_SUBJECT_RE.exec(String(subject))` from `resolvePrFromCommit`: `node .claude/workflows/policy_lint.mjs` prints `FIXTURE VACUOUS: resolvePrFromCommit [... squash-shape subject ... did not recover the PR number ...]`.
- Removing `rulePaths` from the export list: `node .claude/workflows/check-wave-script.mjs` prints `FAIL rulePaths is exported typeof undefined` and `FAIL and reads every declared path glob of a real rule ... declared 2, read -1`, so 151 passed, 2 failed (the deliberate harness probe's own FAIL is discounted by the script).

## Null control

Main's own checks stay green with the change: `check-wave-script.mjs` 153 passed, 0 failed (151 at main plus the two new rows); `policy_lint.mjs` fixture ok, 233 pins (232 plus the one new row), 92 errors held; `policy_lint.mjs --budgets`, `rules_sync.mjs --check`, `brief_lint.mjs` and `field_coverage.mjs` (refused=0) all ok. The stamp-subject row (`v6.3.19: stamp ...`) still resolves to null, which is the fix's own null control that it did not become an unanchored subject scan. The null control for the `rulePaths` row is that the rule it reads (`.claude/rules/gate-scoping.md`) declares 2 globs (`want > 0`).

`tests/entities.py`, the one script the scoped gate selects (`MODE: SCOPED -- 1 script(s) run`), was run in a venv with numpy: 1 of 2060 failed, `the template arm turns the acceptance red ...`, and the same single check fails the same way at pristine main `af7660c7` in a second worktree, so it is main's, in this environment.

## Figures

- Fixture, 233 pins: `node .claude/workflows/policy_lint.mjs`
- Wave script, 153 passed, 0 failed: `node .claude/workflows/check-wave-script.mjs`
- Budgets: `node .claude/workflows/policy_lint.mjs --budgets`
- Rules sync: `node .claude/workflows/rules_sync.mjs --check`
- Field coverage, 0 refused: `node .claude/workflows/field_coverage.mjs`
- Scoped gate, `MODE: SCOPED`: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`
- Entities, 2060 checks: `tests/entities.py`

## Red checks

none expected, and no CI run exists yet at this head. `policy_lint.mjs` and `check-wave-script.mjs` are base-pinned graders, so on this PR CI runs main's copies and the two new rows first run on main after the merge.

Local `tools/audit/prepr.sh` refused four steps at this head, none of them in this diff: `policy_lint`, `mutants` and `field coverage` read the live `main-protect-checks` ruleset (23698884), whose `bypass_actors` no longer match `.claude/workflows/fixtures/required-contexts.json` (5 `required-contexts` errors); the same 5 errors print on a pristine `af7660c7` checkout (`node .claude/workflows/policy_lint.mjs`, `node .claude/workflows/field_coverage.mjs --only ruleset` prints `the live main-protect-checks ruleset object, unperturbed, is already red`). The fourth, `self-test` (146 passed, 2 failed, two PreToolUse-matcher null controls), is green when run alone at this head and at main (`bash tools/audit/prepr.sh --self-test`: 148 passed, 0 failed); I attribute the in-run failure to the same live-ruleset read but did not isolate it.

## Forward-carry

- `tools/audit/bugclasses.json`: the I4 entry's `barrier` text records that the agreement lane (#1847) reads `resolvePrFromCommit` and `rulePaths`; the lane itself lands there.

## Friction

none
