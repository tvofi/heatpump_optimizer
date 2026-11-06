R10-BODY-CONTRACT part 2, repair round 1: the carries #3227 left open, answered one by one, and the fix review's block cured (the `check --body` and `pr` fold-destination wiring was unpinned by the self-test). Policy files touched, so the owner's approving review is needed at merge: `tools/audit/carry_audit.py` (CODEOWNERS names it) and `tools/policy/brief_lint.mjs`; `dev/programme/rosters/wave-r9-groups.json` carries the 1795 move.

## Head

804fc041947b08cd180f2f0d8e1308096a75f8aa (the handoff code; origin/main at merge 28482eceeb6b9809e44b12d80fc994282cc21645, taken 2026-11-06T22:00Z, is the merge base; `tools/pr/prepr.sh` run on this head).

## Mutation proof

Each predicate was reverted alone and `python3 -I tools/audit/carry_audit.py --self-test` run; the file restored byte for byte after each (`diff` against the saved copy, `git diff --stat` back to the committed arms only).

The review's block, now killed (each mutant red, then restored, 392 checks, 1 failed each):
- A, `fold_rc = folds_rc(body, a.repo, a.issue_folds_file, dests)` with `dests` dropped: red on `check --body refuses a fold answered Carry: a group the roster lacks`.
- B, `if FOLD_LINE.search(body):  # a fold` changed to `if False:`: red on the same arm.
- C, the `pr` subcommand's `| folds_rc(body, a.repo, None, dests)` with `dests` dropped: red on `pr refuses a fold answered Carry: a group the roster lacks`.
- Null controls: `Fold (a): Carry: R10-CONS` (a live group) exits 0 through both `check --body` and `pr`.

Earlier round, still holding:
- trailer back to `Round:\s*\d`: red on `a finding line 'Round: 3 of the audit missed a ref' is a finding, so unrouted`.
- separator back to `[|;,]`: red on `a ',' after the pointer is not the documented '|'` and `... nor is a ';'`.
- `FOLD_LINE` back to the lowercase, colon-adjacent form: 4 red.
- owner filter on issue comments removed: red on `... and not a non-owner's comment (null control)`.
- fold-answer roster read removed (`for m in ():`): red on the invented-group and the done-group arms.
- `tools/policy/brief_lint.mjs`: default roster directory pointed at a missing dir: `LEGACY-CONTROL VACUOUS`; a clean member added to `LEGACY_CONTROL_FILES`: red; a member past the cap: red `over its cap`.
- `pr-contract.yml` with ` --branch "$HEAD_REF"` deleted, `tests/entities.py` run: exactly 1 entity check red; workflow restored.

## Null control

The unmodified tree: at the merge base the same self-test has none of the fold-spelling, owner-comment, fold-destination, `Round: <n> <prose>`, `,`/`;` or CLI/`pr` fold-wiring arms, so none can fail (the mutants A, B and C above all survived there, per the review). Each new arm carries its own null control.

## Figures

- Self-test: instrument `python3 -I tools/audit/carry_audit.py --self-test` prints its own count line; run at this head and in a detached worktree at the merge base, the two lines differ by the arms this diff adds. The count is a function of the tree and is not quoted (the prior body's 366 was wrong).
- `node tools/policy/brief_lint.mjs` rc 0 with the `LEGACY-CONTROL ok:` line; `rosterIssues()` with no argument indexes the roster directory's issues (command: `node -e "import('./tools/policy/brief_lint.mjs').then(m=>console.log(m.rosterIssues().size))"`; the count is a function of the rosters, so no number is quoted).
- `python3 tests/structure.py` PASSED; `python3 tests/entities.py` ALL ENTITY CHECKS PASSED; both run at this head.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: FULL` (the diff deletes `dev/programme/carries/carry-1795.json`, which no recorded closure mentions); CI runs the full gate.
- Seam rule for the carry grammar: the readers of the fold lines are `FOLD_LINE` users, enumerated by `git grep -n FOLD_LINE tools/`; the fold-destination read has two CLI call sites (`check --body`, `pr`), both now pinned by an arm.

## Red checks

`none` locally. CI: any concluded red of this head is named here by the orchestrator's classify read; the known main-wide one is `governance / instrument-self-tests` cancelled at its 30-minute timeout, cured by R10-PROCESS-SLIM #3245 (cheaper detector: that group's slimming of the job; standing cost: none added here). Carry: R10-PROCESS-SLIM

## Forward-carry

The roster entry lists 39 carries (the round roster ref `origin/handoff/audit-r10-roster`; the count is a function of that ref, taken now). The nine this PR owns are answered first; the rest map onto them or are not touched.

1. Card 7 (every body figure from a generated block; roster carries 2, 11, 17, 27, 37): re-measured, the preconditions are still absent (`tools/policy/figure_lint.mjs` executes none of a body's commands; no workflow edits a body on synchronize). Needs the owner's one-sentence ruling: may `pr-contract` run PR-authored figure commands. Not built; destination `tools/policy/figure_lint.mjs` and `.github/PULL_REQUEST_TEMPLATE.md` once ruled. Carry: R10-BODY-CONTRACT
2. A1 (`rosterIssues()` default; roster carries 8, 12, 18, 28): built; the carry file for #1795 moved into live group R9-UX-6's carry list (`dev/programme/rosters/wave-r9-groups.json`) and the file deleted; edited directly in the roster file, which the owner may prefer to re-apply through the roster seat. Carry: dismissed: answered in this pull request
3. Fold grammar scope (roster carries 5, 13, 19, 29, 38): built, owner comments read, a `Fold (x): Carry:` answer checked against the roster in `check --body` and in `pr`, both now pinned by self-test arms in `tools/audit/carry_audit.py` (this round closes carry 38's "not driven by a self-test arm"). Carry: dismissed: built and pinned in this pull request
4. `body_push.sh` hot file (roster carries 14, 20, 30): PR 3221 merged; this diff touches neither `tools/audit/seat/body_push.sh` nor `body_patch.sh`. Carry: dismissed: 3221 merged, this diff touches neither file
5. Carry control lint narrowing (roster carries 15, 21, 31, 39): pin built (`LEGACY_CONTROL_CAP` in `tools/policy/brief_lint.mjs`); the remaining files carry unresolvable cites, mostly under `dev/archive/carries`, and repairing them rewrites other groups' recorded controls. Carry: R10-BODY-CONTRACT
6. Fold spellings (roster carries 22, 32): built. Carry: dismissed: answered in this pull request
7. Dismissal pointer (roster carries 23, 33): narrowed to the documented `|`. Carry: dismissed: answered in this pull request
8. `Round:` trailer (roster carries 4, 24, 34): built. Carry: dismissed: answered in this pull request
9. `--branch "$HEAD_REF"` pin (roster carries 25, 35): built in `tests/entities.py`. Carry: dismissed: answered in this pull request

Remaining roster carries, each named: Carry 16, Carry 26 and Carry 36 are the `rosterIssues()` collision flag, answered with item 2 (the collision is flagged by `assertLegacyControl`). Carry 1 (`body_patch.sh` without `--roster-ref`), Carry 3 (`trackedFiles()` at the head), Carry 6 (carry-missing predictor), Carry 7 (`seg_dests` dismissal of a done group), Carry 9 and Carry 10 (`body_push.sh` refused-body ref) predate this part and this diff touches none of `tools/audit/seat/body_patch.sh`, `tools/audit/seat/body_push.sh` or `roster_lib.py`; they stay on the roster entry. Carry: R10-BODY-CONTRACT

## Friction

`none`
