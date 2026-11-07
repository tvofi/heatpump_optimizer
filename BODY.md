R10-BODY-CONTRACT part 3 (card 7, option B, registry blocks). `pr-contract` renders a figure block only from an instrument that `tools/pr/figure_registry.json` names in the BASE tree, and the body quotes it verbatim; the author chooses no command. Only registered figures are structurally non-stale.

New files: `tools/pr/figure_block.py` (renderer, refresh, verify, self-test), `tools/pr/figure_registry.json` (scope-line, structure-ratchet, merge-base), `tools/audit/seat/instruments/figure_block.py.md`. Option A refused (figure_lint reason 4 stands, header narrowed), option C is the writer (`body_push.sh` runs `figure_block.py refresh`; `prepr.sh` verifies, including the body-only path), `pr-contract` only verifies.

Legacy control (second item): dismissed citing `LEGACY_CONTROL_CAP` and `assertLegacyControl`; re-measured at the merge base, every member of `LEGACY_CONTROL_FILES` still draws a control error with the exemption removed (scratch driver calling `lintCarryFile` with an empty set), so none is dropped.

Carry dispositions (roster indexes, 0-based):

Carry 0: not in this part's scope (part 3 takes card 7 and its legacy-control item only); stays with the group's other parts.
Carry 1: answered by the card 7 build (option B).
Carry 2: not in this part's scope (part 3 takes card 7 and its legacy-control item only); stays with the group's other parts.
Carry 3: not in this part's scope (part 3 takes card 7 and its legacy-control item only); stays with the group's other parts.
Carry 4: not in this part's scope (part 3 takes card 7 and its legacy-control item only); stays with the group's other parts.
Carry 5: not in this part's scope (part 3 takes card 7 and its legacy-control item only); stays with the group's other parts.
Carry 6: not in this part's scope (part 3 takes card 7 and its legacy-control item only); stays with the group's other parts.
Carry 7: not in this part's scope (part 3 takes card 7 and its legacy-control item only); stays with the group's other parts.
Carry 8: not in this part's scope (part 3 takes card 7 and its legacy-control item only); stays with the group's other parts.
Carry 9: not in this part's scope (part 3 takes card 7 and its legacy-control item only); stays with the group's other parts.
Carry 10: answered by the card 7 build (option B).
Carry 11: not in this part's scope (part 3 takes card 7 and its legacy-control item only); stays with the group's other parts.
Carry 12: not in this part's scope (part 3 takes card 7 and its legacy-control item only); stays with the group's other parts.
Carry 13: not in this part's scope (part 3 takes card 7 and its legacy-control item only); stays with the group's other parts.
Carry 14: dismissed: LEGACY_CONTROL_CAP and assertLegacyControl bound the set; all members still need the exemption.
Carry 15: not in this part's scope (part 3 takes card 7 and its legacy-control item only); stays with the group's other parts.
Carry 16: answered by the card 7 build (option B).
Carry 17: not in this part's scope (part 3 takes card 7 and its legacy-control item only); stays with the group's other parts.
Carry 18: not in this part's scope (part 3 takes card 7 and its legacy-control item only); stays with the group's other parts.
Carry 19: not in this part's scope (part 3 takes card 7 and its legacy-control item only); stays with the group's other parts.
Carry 20: dismissed: LEGACY_CONTROL_CAP and assertLegacyControl bound the set; all members still need the exemption.
Carry 21: not in this part's scope (part 3 takes card 7 and its legacy-control item only); stays with the group's other parts.
Carry 22: not in this part's scope (part 3 takes card 7 and its legacy-control item only); stays with the group's other parts.
Carry 23: not in this part's scope (part 3 takes card 7 and its legacy-control item only); stays with the group's other parts.
Carry 24: not in this part's scope (part 3 takes card 7 and its legacy-control item only); stays with the group's other parts.
Carry 25: not in this part's scope (part 3 takes card 7 and its legacy-control item only); stays with the group's other parts.
Carry 26: answered by the card 7 build (option B).
Carry 27: not in this part's scope (part 3 takes card 7 and its legacy-control item only); stays with the group's other parts.
Carry 28: not in this part's scope (part 3 takes card 7 and its legacy-control item only); stays with the group's other parts.
Carry 29: not in this part's scope (part 3 takes card 7 and its legacy-control item only); stays with the group's other parts.
Carry 30: dismissed: LEGACY_CONTROL_CAP and assertLegacyControl bound the set; all members still need the exemption.
Carry 31: not in this part's scope (part 3 takes card 7 and its legacy-control item only); stays with the group's other parts.
Carry 32: not in this part's scope (part 3 takes card 7 and its legacy-control item only); stays with the group's other parts.
Carry 33: not in this part's scope (part 3 takes card 7 and its legacy-control item only); stays with the group's other parts.
Carry 34: not in this part's scope (part 3 takes card 7 and its legacy-control item only); stays with the group's other parts.
Carry 35: not in this part's scope (part 3 takes card 7 and its legacy-control item only); stays with the group's other parts.
Carry 36: answered by the card 7 build (option B).
Carry 37: not in this part's scope (part 3 takes card 7 and its legacy-control item only); stays with the group's other parts.
Carry 38: dismissed: LEGACY_CONTROL_CAP and assertLegacyControl bound the set; all members still need the exemption.
Carry 39: answered by the card 7 build (option B).
Carry 40: dismissed: LEGACY_CONTROL_CAP and assertLegacyControl bound the set; all members still need the exemption.
Carry 41: not in this part's scope (part 3 takes card 7 and its legacy-control item only); stays with the group's other parts.
Carry 42: built here (card 7 ruling).

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
