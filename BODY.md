Bootstrap of r10-closeout-prep part 2 (PR 3553): CI's `briefs` job runs main's copy of `tools/policy/brief_lint.mjs` over the head's data, so part 2's data change (retiring `carry-201.json` from the legacy set) is refused until the linter change is on main. This lands that 8-line hunk alone: the narrowing arm of `assertCarryControl` reads its legacy example from `LEGACY_CONTROL_FILES` instead of naming `carry-201.json`, and refuses an empty set as vacuous. Not closure-gating; unmerged at the v10.0.0 stamp it goes to round 11.

## Head

7b2f46be31725d0b003b36e7d4ad0e462f42f847, cut from origin/main e23124ff6e.

## Mutation proof

Mutant: line of `const LEGACY_CONTROL_FILES = readLegacyControlFiles()` replaced by `new Set()`. `node tools/policy/brief_lint.mjs` exits 1 with `CONTROL VACUOUS: carry control: the legacy set is empty, so the narrowing is unexercised` (the new arm); restored, exit 0.

## Null control

Part 2's data shape (the diff 154dbb4c61..78325190f8 minus the linter file, applied to this tree; `carry-201.json` absent from `tools/policy/legacy_control_files.json`): with the hunk reverted (main's linter) `node tools/policy/brief_lint.mjs` exits 1, `CONTROL VACUOUS ... a legacy carry file is refused (the narrowing)`; with the hunk it exits 0 and prints `CONTROL ok`. On main's own data the hunk exits 0.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none
