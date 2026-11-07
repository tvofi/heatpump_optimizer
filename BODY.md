R10-BODY-CONTRACT part 3 (card 7, option B, registry blocks). `pr-contract` renders a figure block only from an instrument that `tools/pr/figure_registry.json` names in the BASE tree, and the body quotes it verbatim; the author chooses no command. Only registered figures are structurally non-stale.

New files: `tools/pr/figure_block.py` (renderer, refresh, verify, self-test), `tools/pr/figure_registry.json` (scope-line, structure-ratchet, merge-base), `tools/audit/seat/instruments/figure_block.py.md`. Option A refused (figure_lint reason 4 stands, header narrowed), option C is the writer (`body_push.sh` runs `figure_block.py refresh`; `prepr.sh` verifies, including the body-only path), `pr-contract` only verifies.

Legacy control (second item): dismissed citing `LEGACY_CONTROL_CAP` and `assertLegacyControl`; re-measured at the merge base, every member of `LEGACY_CONTROL_FILES` still draws a control error with the exemption removed (scratch driver calling `lintCarryFile` with an empty set), so none is dropped.

Carry dispositions (roster indexes, 0-based):

Carry 0 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 1 - answered by the card 7 build (option B).
Carry 2 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 3 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 4 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 5 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 6 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 7 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 8 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 9 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 10 - answered by the card 7 build (option B).
Carry 11 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 12 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 13 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 14 - dismissed: LEGACY_CONTROL_CAP and assertLegacyControl bound the set; all members still need the exemption.
Carry 15 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 16 - answered by the card 7 build (option B).
Carry 17 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 18 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 19 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 20 - dismissed: LEGACY_CONTROL_CAP and assertLegacyControl bound the set; all members still need the exemption.
Carry 21 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 22 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 23 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 24 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 25 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 26 - answered by the card 7 build (option B).
Carry 27 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 28 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 29 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 30 - dismissed: LEGACY_CONTROL_CAP and assertLegacyControl bound the set; all members still need the exemption.
Carry 31 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 32 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 33 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 34 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 35 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 36 - answered by the card 7 build (option B).
Carry 37 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 38 - dismissed: LEGACY_CONTROL_CAP and assertLegacyControl bound the set; all members still need the exemption.
Carry 39 - answered by the card 7 build (option B).
Carry 40 - dismissed: LEGACY_CONTROL_CAP and assertLegacyControl bound the set; all members still need the exemption.
Carry 41 - held by the group's other part; part 3 takes card 7 and its legacy-control item only.
Carry 42 - built here (card 7 ruling).

## Head

71cbfe6b1ecce22a23159f4c5284717fc6a7b5f8

## Mutation proof

`figure_block.py --self-test` mutants: hand-typed value, moved head, unregistered/head-only instrument, unknown name, non-zero exit each fail their check; `body_push.sh --self-test` deletes the `# mut:keep` refresh line and its arm fails; `policy_lint.mjs` registers `figureBlockProblems` as a return-mutant site (the mutants lane was not run locally).

## Null control

A body with no block and a free-form figure still passes (self-test arm); an unregistered instrument is refused as a block.

## Figures

No block is used in this body: the registry does not exist at the base, so this pull request cannot use its own instrument (the point of the rule). Free-form:

- structure ratchet: `python3 tests/structure.py` printed STRUCTURE RATCHET PASSED at the head.
- gate scope: `python3 tests/closure.py select --diff \$(git merge-base origin/main HEAD) --workdir \$D` prints MODE: FULL (gate files touched).
- `PYTHONPATH=tests/hastub python3 tests/entities.py` exits 0.

Counts: `python3 -I tools/pr/figure_block.py --self-test`; `node tools/policy/policy_lint.mjs --self-test`; `bash tools/audit/seat/body_push.sh --self-test`.

## Approval

Policy files touched (policy_lint.mjs, PULL_REQUEST_TEMPLATE.md, pr-contract.yml): owner approving review needed, or the card-7 mandate 6624093439 under which the orchestrator ruled this build.

## Red checks

none

## Forward-carry

none

## Friction

none
