Round-10 roster record, second v7.1.15 landing: puts the roster's `remeasure` amendment for R11-INTAKE-R10-RESIDUE onto main, so the entities arm of the closure-chain pull request #3553 finds a carry naming `carry-201 entry 6 (file removed)` and the command for `dev/audit/rounds/round6/D11/fix/codeowners_gap.py`. Part of #201. It closes nothing by keyword and leaves #3394 open.

## Summary

The R11-INTAKE-R10-RESIDUE carry for carry-201 entry 6 had been folded without that entry's `remeasure` text, so nothing in the tree cited `codeowners_gap.py` (#3553's fixer is blocked on it, `BLOCKED.md` at `4d8b3effaab2b84f094e6527b4c991d1ac90e974` on `handoff-wip/r10-closeout-prep-p2`). The orchestrator ruled that the roster is amended. One `roster_edit append-carry` op, queued on `roster-drain.queue`, applied by the beat's roster-drain row and pushed as `b1697d36f98add0a34f925a30017175219cafdaa`, carries the text `carry-201 entry 6 (file removed), remeasure (verbatim from carry-201.json carries[6], omitted when the entry was folded): ` followed by `carries[6].remeasure` of `dev/programme/carries/carry-201.json` at `origin/main` `ad95665ea3`, verbatim. Read back with `roster_queue.py readback b1697d36f98add0a34f925a30017175219cafdaa R11-INTAKE-R10-RESIDUE <carry file>`: `n_carry=84 exact-match-index=[83] len=772/772`, exit 0.

The roster branch's two other commits since main are `roster_sync` stage derivations (`R10-HOTFIX-TICK-SELFTEST-CHECKOUT`, `R10-HOTFIX-OPENER-REFUSALS`). The change is roster state only: one file, `dev/programme/rosters/wave-r10-groups.json`, 6 insertions and 5 deletions (`git diff --numstat origin/main...HEAD`; a figure that is a function of main's tip is stale once main moves). No production or test code is touched, and the opener adds the pull request's own delivery row.

## Head

`a08433aa58bb67a9bc78b3741ea39588fd15def8` is a merge of `b1697d36f98add0a34f925a30017175219cafdaa` (tip of `handoff/audit-r10-roster`) into `origin/main` `ad95665ea316`, as the first landing (#3554) was; the opener adds the delivery row on top. It is a merge and not a copy of the branch's file because main's roster differs from the tip's in R10-CATALOG-PR, which a blob copy would revert. Roster commit `d17111784f` is an ancestor of this head. The roster blob at this head is `f47f21caa6b6da5e3f77713ea623b1920ad3083a`. Read the diff three-dot.

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

Keyed on the `group` field, main's roster and this head's both hold 508 groups, none added, none removed; three of main's groups change (R11-INTAKE-R10-RESIDUE, R10-HOTFIX-TICK-SELFTEST-CHECKOUT, R10-HOTFIX-OPENER-REFUSALS). Had the keying been vacuous, a roster that differs would print zero changed; it does not. The blob on main is `d1cd7d85689b2c2af2d515a2d3b4c3a4a71b046a`.

## Figures

- `git diff --numstat origin/main...HEAD` prints `6 5`, one file.
- `node tools/policy/brief_lint.mjs` at this head: `TOTAL: 0 error(s) across 45 file(s)`.
- `python3 tools/pr/ci_predict.py` at this head predicts no closures, fast, governance or instrument red.
- `tests/entities.py` was not run locally: the host is loaded and its timing check flakes, so CI is the authority and no local figure is quoted.

## Red checks

None known at this head; the orchestrator reads the check-runs.

## Forward-carry

none

## Friction

none
