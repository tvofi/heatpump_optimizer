R10-BODY-CONTRACT part 2: the carries #3227 left open, answered one by one (built, `Carry:` or dismissed). Policy files touched, so the owner's approving review is needed at merge: `tools/audit/carry_audit.py` (CODEOWNERS names it) and `tools/policy/brief_lint.mjs`; `dev/programme/rosters/wave-r9-groups.json` carries the 1795 move.

## Head

95a5cca4fe03875b2bcf02fd882db327d2aa9744 (merged with origin/main 4b7e1770ba81fa02a8dda531463eba68e987ff59, 2026-11-06T17:41Z; `tools/pr/prepr.sh` re-run after that merge).

## Mutation proof

Each predicate was reverted alone and `python3 -I tools/audit/carry_audit.py --self-test` run; the file restored byte for byte after each (`diff -q` against the saved copy):
- trailer back to `Round:\s*\d`: red on `a finding line 'Round: 3 of the audit missed a ref' is a finding, so unrouted`.
- separator back to `[|;,]`: red on the two arms `a ',' after the pointer is not the documented '|'` and `... nor is a ';'`.
- `FOLD_LINE` back to the lowercase, colon-adjacent form: 4 red (`**Fold (a)**:`, `Fold (A):`, `**Fold (a), added 2026-10-04 (owner)**:`, the uppercase answer).
- owner filter on issue comments removed: red on `... and not a non-owner's comment (null control)`.
- fold-answer roster read removed (`for m in ():`): red on the invented-group and the done-group arms.
- `tools/policy/brief_lint.mjs` (`node tools/policy/brief_lint.mjs`): default roster directory pointed at a missing dir: `LEGACY-CONTROL VACUOUS: a carry file at #2999, covered by a live group, is accepted with the default roster`; a clean member added to `LEGACY_CONTROL_FILES`: red `its controls lint clean without the exemption`; a member added past the cap: red `over its cap 14`.
- `pr-contract.yml` with ` --branch "$HEAD_REF"` deleted, `tests/entities.py` run: exactly 1 of the ENTITY CHECKS red, `pr-contract's carry step passes --branch "$HEAD_REF", bound to the PR head ref (plant and null)`; workflow restored, `git status` clean.

## Null control

The unmodified tree: at the merge base (cb48d97e2) the same self-test has no fold-spelling, owner-comment, fold-destination, `Round: <n> <prose>` or `,`/`;` arms, so none can fail; each new arm also carries its own null control (a stranger's comment, `Fold (ab):`, `Fold (a) do x`, a prose mention, a carry at 999999, `Carry: R10-OVER` alone, no roster handed to the fold check).

## Figures

- `python3 -I tools/audit/carry_audit.py --self-test` prints `carry_audit self-test: 388 checks, 0 failed` at this head (instrument: the self-test's own count line; at the merge base it printed 366 checks).
- `node tools/policy/brief_lint.mjs` rc 0 with the new `LEGACY-CONTROL ok:` line; `rosterIssues()` with no argument indexed 1 issue at the merge base and indexes the roster directory's issues now (command: `node -e "import('./tools/policy/brief_lint.mjs').then(m=>console.log(m.rosterIssues().size))"`; the count is a function of the rosters, so no number is quoted).
- `python3 tests/structure.py` PASSED; `python3 -I tools/audit/seat/tmp_paths.py --check` 0 refused; `bash tools/pr/prepr.sh` was refused once on `temp paths` (a temp-path literal in my pin; removed) and is clean after.
- Seam rule for the carry grammar (step 8): the readers of the fold lines are `FOLD_LINE` users, enumerated by `git grep -n FOLD_LINE tools/` : `fold_answered`, `fold_problems`, the issue side and the answer side share the one regex, so the spellings are accepted symmetrically; the sixth carry's live spelling was read from #1955's owner comment 5983672253 (`**Fold (e), added 2026-10-04 (owner)**:`).

## Red checks

`none` beyond the local `temp paths` refusal named under Figures (cheaper detector: `tmp_paths.py --check` is a `prepr.sh` step and already ran; standing cost nil).

## Forward-carry

How each of the nine carries was answered:
1. Card 7 (every body figure from a generated block): re-measured at this base, and the preconditions are still absent (`git grep -c figure tools/audit/seat/features_block.py` prints 0; `tools/policy/figure_lint.mjs` states it executes none of a body's commands; no workflow edits a body on synchronize). Nothing is buildable inside the existing contract without running PR-authored commands in `pr-contract`. Ruling needed from the owner in one sentence: may `pr-contract` run PR-authored figure commands (with a new generated-block format and marker, and a PR-template and `checkPrBody` change). Not built; the template and `checkPrBody` are untouched. Carry: R10-BODY-CONTRACT
2. A1 (`rosterIssues()` default): built. the carry file for #1795 moved into live group R9-UX-6's carry list (its four entries) and the file deleted; the default now reads `dev/programme/rosters`; control `assertLegacyControl` refuses a carry file at a live-group issue and accepts one at 999999. This also closes the finding-propagation item: the collision is now flagged. I did this edit directly in `wave-r9-groups.json` (`roster_edit.py` moved my worktree onto a roster commit; reverted, nothing pushed to a roster ref); the owner may prefer to re-apply it through the roster seat. Carry: dismissed: answered in this pull request
3. Fold grammar scope: built the cheap parts: owner comments are read (non-owner comments are not), a `Fold (x): Carry:` answer is checked against the roster in `check --body` and in `pr`. Not built: the `pr` wiring is not driven by a self-test arm because it needs live `gh` (the same `fold_problems` is covered offline). Carry: R10-BODY-CONTRACT
4. `body_push.sh` hot file: PR 3221 merged (788e8ceed is an ancestor of the base); this diff does not touch `body_push.sh` or `body_patch.sh`. Dismissed: nothing left to coordinate once 3221 merged. Carry: dismissed: 3221 merged, this diff touches neither file
5. Carry control lint narrowing: built the pin only: `LEGACY_CONTROL_CAP`, every member must still lint red without the exemption (a repaired file must leave the set), and the #1795 file left the set when consumed. The other 14 files each still carry unresolvable cites or no path (measured by removing them from the set and running `node tools/policy/brief_lint.mjs`); repairing them rewrites other groups' recorded controls, mostly in `dev/archive/carries`. Carry: R10-BODY-CONTRACT
6. Fold spellings: built (see mutation proof). Carry: dismissed: answered in this pull request
7. Dismissal pointer: built, narrowed the regex to the documented `|` (docs at the top of `carry_audit.py` already say `|`), arms either way. Carry: dismissed: answered in this pull request
8. `Round:` trailer: built; the null control failed on the old regex (a finding opening `Round: 3 of ...`), regex narrowed to `Round: <n>` alone on its line. Carry: dismissed: answered in this pull request
9. `--branch "$HEAD_REF"` pin: built in `tests/entities.py` beside the other `_PC_WF` pins, with mutant (see mutation proof). Carry: dismissed: answered in this pull request

## Friction

`none`
