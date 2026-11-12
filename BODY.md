Part 1 of the r10 hotfix (BOOTSTRAP class: a registration literal inside a pinned grader). The legacy-control file list moves out of `tools/policy/brief_lint.mjs` into the unpinned data file `tools/policy/legacy_control_files.json`, which the grader reads, failing closed to an empty set. The cap stays a literal in the grader. Entries unchanged; no carry is repaired or delisted here (part 2, after this merges).

## Head
b4a663ebe57af9f9ab83cc9d70452f8a642026ab on base 19baca76181cb019d9b1cfd93ee6bc0a08e20047.

## Mutation proof
New self-test arm `assertLegacyListedClean` drives the exported `staleLegacyMembers` (the listed-but-clean check, extracted from `assertLegacyControl`). Mutant: loop over `[]` instead of the labels. Result: `LEGACY-LISTED-CLEAN VACUOUS: a listed carry whose controls lint clean is not refused`, rc=1; restored, rc=0. The arm also drives a vacuous check as a second mutant it must tell apart. Failing test first: the arm was added before `staleLegacyMembers` existed and threw a ReferenceError.

## Null control
`node tools/policy/brief_lint.mjs` at base (copy saved before the edit) against this head, on the same tree: the only diff is the added `LEGACY-LISTED-CLEAN ok` arm line (`diff before.txt after.txt`, 3 added lines, nothing removed). A listed carry that still needs the exemption (a copy of the correct fixture whose control names no path) is not refused by the arm. Entries compared by script: the data file's list equals the base literal, 14 entries.

## Figures
- `python3 tools/policy/…` n/a; entries: a script comparing the base literal to `legacy_control_files.json` printed `entries equal: True 14`.
- `tools/pr/prepr.sh` at b4a663eb: every step ok except `closures`, which refused "failed while being recorded: tests/entities.py (exit 1)". Not reproduced: `PYTHONPATH=tests/hastub python3 tests/entities.py` exits 0, and `bash tests/derive_closures.sh --scripts-from <file naming tests/entities.py> --record-only` exits 0 on this head. The first prepr run had been killed by a `timeout` and may have left a competing run; the cause is unconfirmed.

## Red checks
none

## Forward-carry
Part 2 (repair `carry-1412.json`, delist it from the data file, survey the other listed files) is dispatched after this merges. Carry: dismissed: the brief names part 2 as its own dispatch.

## Friction
none
