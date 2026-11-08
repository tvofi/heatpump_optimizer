R10-BODY-CONTRACT part 3 (card 7, option B, registry blocks). `pr-contract` renders a figure block only from an instrument that `tools/pr/figure_registry.json` names in the BASE tree, and the body quotes it verbatim; the author chooses no command. Only registered figures are structurally non-stale.

New files: `tools/pr/figure_block.py` (renderer, refresh, verify, self-test), `tools/pr/figure_registry.json` (scope-line, structure-ratchet, merge-base), `tools/audit/seat/instruments/figure_block.py.md`. Option A refused (figure_lint reason 4 stands, header narrowed), option C is the writer (`body_push.sh` runs `figure_block.py refresh`; `prepr.sh` verifies, including the body-only path), `pr-contract` only verifies.

Legacy control (second item): dismissed citing `LEGACY_CONTROL_CAP` and `assertLegacyControl`; re-measured at the merge base, every member of `LEGACY_CONTROL_FILES` still draws a control error with the exemption removed (scratch driver calling `lintCarryFile` with an empty set), so none is dropped.

Carry dispositions (the packet's 1-based numbering; the brief's 0-based index plus one):

Carry 1 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 2 - answered by the card 7 build (option B).
Carry 3 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 4 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 5 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 6 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 7 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 8 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 9 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 10 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 11 - answered by the card 7 build (option B).
Carry 12 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 13 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 14 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 15 - dismissed: LEGACY_CONTROL_CAP and assertLegacyControl bound the set; all members still need the exemption.
Carry 16 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 17 - answered by the card 7 build (option B).
Carry 18 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 19 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 20 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 21 - dismissed: LEGACY_CONTROL_CAP and assertLegacyControl bound the set; all members still need the exemption.
Carry 22 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 23 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 24 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 25 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 26 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 27 - answered by the card 7 build (option B).
Carry 28 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 29 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 30 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 31 - dismissed: LEGACY_CONTROL_CAP and assertLegacyControl bound the set; all members still need the exemption.
Carry 32 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 33 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 34 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 35 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 36 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 37 - answered by the card 7 build (option B).
Carry 38 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 39 - dismissed: LEGACY_CONTROL_CAP and assertLegacyControl bound the set; all members still need the exemption.
Carry 40 - answered by the card 7 build (option B).
Carry 41 - dismissed: LEGACY_CONTROL_CAP and assertLegacyControl bound the set; all members still need the exemption.
Carry 42 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.

Carry 43 - built here (card 7 ruling; roster index 42, 0-based).
Carry 44 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.

Repair round (this push): the opener refused the previous head three times. Three causes, each fixed at its root.

1. `tools/pr/figure_block.py` built its self-test repository with a hand-written `git init`; it now goes through `tests/throwaway_git.py` (`throwaway_git_init`), and every git call in the self-test runs under that module's environment.
2. The prepr self-test read `513 passed, 2 failed`. The two failures were `a tree with no raw repository build passes the raw-git check (null control) (got 1, wanted 0)` and `and the ok line is the check's own, so it ran (got 0, wanted 1)`: both are `tests/throwaway_git.py --check` run at HEAD, refusing the raw `git init` at figure_block.py:223, so they were cause 1 and not separate defects. The assertions are untouched. Now `515 passed, 0 failed`.
3. `field_coverage.mjs REFUSED registry: pinned tools/pr/figure_block.py is unregistered`. The bootstrap entry (`pending:`) is NOT on main: `git log origin/main -S"pinned tools/pr/figure_block.py" -- tools/policy/field_coverage.mjs` is empty; topic r10-body-contract-p3-bootstrap is only on `handoff-wip/r10-body-contract-p3-bootstrap`. So this change carries the entry itself in the final shape (`none:` with no `pending`), in the same change that pins the program in governance.yml. `node tools/policy/field_coverage.mjs` reads `FIELD COVERAGE ok`, rc=0, here. CI grades policy-docs with the base's copy, so `governance / policy-docs` stays red on this head until the bootstrap lands on main; that is the one-time bootstrap ee2974270 describes, and it is named below. When the bootstrap merges first, this entry conflicts trivially: keep this one (no `pending`).

An earlier wip attempt (`handoff-wip/r10-body-contract-p3`, b4e835040) did the same repairs and stopped with BLOCKED.md on question (a)/(b)/(c); I took (b) as the brief directs and superseded that wip tip with a merge that keeps this tree.

## Head

86f9e729f12a3da493029c3c02ea9854bdb34ce7

## Mutation proof

`figure_block.py --self-test` mutants: hand-typed value, moved head, unregistered/head-only instrument, unknown name, non-zero exit each fail their check; `body_push.sh --self-test` deletes the `# mut:keep` refresh line and its arm fails; `policy_lint.mjs` registers `figureBlockProblems` as a return-mutant site. Repair: reverting the figure_block.py hunk makes `tests/throwaway_git.py --check` print `REFUSE tools/pr/figure_block.py:223` and the prepr self-test read `513 passed, 2 failed`; with it, `0 raw git init or clone site(s) refused` and `515 passed, 0 failed`.

## Null control

A body with no block and a free-form figure still passes (self-test arm); an unregistered instrument is refused as a block. The unmodified head 71cbfe6b1 is the failing control for the repair above.

## Figures

No block is used in this body: the registry does not exist at the base, so this pull request cannot use its own instrument. Free-form:

- `python3 -I tools/pr/figure_block.py --self-test` printed 11 checks, 0 failed.
- `bash tools/pr/prepr.sh --self-test` printed 515 passed, 0 failed.
- `python3 -I tests/throwaway_git.py --check` printed 0 raw sites.
- `node tools/policy/field_coverage.mjs` printed FIELD COVERAGE ok.

## Approval

Policy files touched (policy_lint.mjs, PULL_REQUEST_TEMPLATE.md, pr-contract.yml, field_coverage.mjs): owner approving review needed, or the card-7 mandate under which the orchestrator ruled this build.

## Red checks

`governance / policy-docs`: `field_coverage.mjs REFUSED registry: pinned tools/pr/figure_block.py is unregistered`, graded with the base's copy of field_coverage.mjs. Cheaper detector: `prepr.sh` ci predict already predicts it; it cannot be cleared here because the bootstrap entry is not on main (see cause 3). Standing cost of a detector that avoids it: none beyond landing the bootstrap first; this is the one-time bootstrap shape of ee2974270.

## Forward-carry

none

## Friction

none

