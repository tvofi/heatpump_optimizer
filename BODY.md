Round-10 roster record, v7.1.15 landing: puts the roster seat's ops that are on `handoff/audit-r10-roster` and not on main onto main, so the entities arm of the closure-chain pull request #3553 finds the carries re-homed to roster group R11-INTAKE-R10-RESIDUE in main's roster (its minimum is roster commit `d17111784f`). Part of #201. It closes nothing by keyword and leaves #3394 open.

## Summary

The change is roster state only: one file, `dev/programme/rosters/wave-r10-groups.json`, 468 insertions and 189 deletions (`git diff --numstat origin/main...HEAD`; a figure that is a function of main's tip is stale once main moves). No production or test code is touched, and the opener adds the pull request's own delivery row.

The roster branch tip is `ce60e9925f278fc6e3bfb5b9a85edb11ce803dd9`, a `roster_sync` derivation. The range `origin/main..ce60e9925f278fc6e3bfb5b9a85edb11ce803dd9` holds 134 non-merge commits and no merge: 124 `roster_edit` ops (84 `mark-carry`, 29 `append-carry`, 3 `set-stage`, 3 `append-group`, 2 `wire-issue`, 2 `batch`, 1 `set-files`) and 10 `roster_sync:` derivations. Roster commit `d17111784f` is an ancestor of the branch tip and of this head (`git merge-base --is-ancestor d17111784f HEAD` exits 0).

## Head

`b36236d2e9d8e5ec823d7c52214870b36b0d546d` is a merge of `ce60e9925f278fc6e3bfb5b9a85edb11ce803dd9` into `origin/main` `3038b9deaf915a4b3defedd52307f5c57e574a50` (v7.1.15), as the earlier roster landing #3377 was. It is a merge and not a copy of the branch's file because main's roster moved after the branch's merge base `3853ed23d61bee4a8dec2c783bfed48298c3df2f`: R10-CATALOG-PR changed on main (4 lines in, 2 out), and a blob copy would revert it. The merge is clean (`git merge-tree --write-tree origin/main ce60e9925f278fc6e3bfb5b9a85edb11ce803dd9` exits 0), and the merged roster differs from the branch tip's in that one group only. The roster blob at this head is `d1cd7d85689b2c2af2d515a2d3b4c3a4a71b046a`. Read the diff three-dot: a two-dot diff shows main's own newer commits.

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

Keyed on the `group` field, main's roster has 504 groups and this head's has 508: 4 added, none removed, 42 of main's groups changed. Had the keying been vacuous, a roster that differs would print `added 0 changed 0`; it does not. The lint control: `node tools/policy/brief_lint.mjs` on `origin/main` exits 0.

## Figures

- `git diff --numstat origin/main...HEAD` prints `468 189` for the roster file, one file.
- Carries across all groups go from 2002 on main to 2093 at this head (a group's `carry` list, summed).
- `node tools/policy/brief_lint.mjs` at this head: `TOTAL: 0 error(s)`.
- `python3 tools/pr/ci_predict.py` at this head predicts no closures, fast, governance or instrument red.

## Red checks

None known at this head; the orchestrator reads the check-runs.

## Forward-carry

none

## Friction

none
