Carry 21 repair: pin the hotfix-scope classifier seam that the first review at a81d7f15 found uncovered.

## Review scope

`git diff a81d7f15293fc2101f42e48ade37ef7022c35517 becbe652ab6b321a680e5b45b61bfd897f2e0669` -- the two instrument files, plus the `tests/closures.json` re-record of `tests/harness_headers.py`.

## Head

`b53bbf1604a3720aeb665a3b51219eb54df1fe6a` merges the authored code head `16c571f7783b3f9f0c53e0778f8c805fc07d65f4`.

## Mutation proof

(see the pull request; G5, G5b, P8, G3, P7, P9b KILLED; NULL SURVIVED)

## Null control

The carry's null control is the non-hotfix branch.

## Repair round 2

`--self-test` now runs `unset PREPR_SKIP_CODE PREPR_SKIP_CLOSURES` once at entry.

An extra probe, `HPO_GATE_PRIORITY=2` exported, gives 549/1 on "this repository's own wired hooks pass" (`.claude/hooks/pre-edit.sh`, 21 passed, 1 failed). Not in the brief's set, not measured at becbe652 or the merge base, cause not investigated.

## Carry status

This part builds carry 21 only. Each other dispatched carry keeps the disposition its own text carries in the brief and is not built here: carry 0 (dismissed: moved to round 11), carry 1 (dismissed: moved to round 11), carry 2 (dismissed: moved to round 11), carry 3 (dismissed: moved to round 11), carry 4 (implemented at 6e100ef6980216a81eaa0438bdc215d62b19271f), carry 5 (moved: R11-INTAKE-R10-RESIDUE), carry 6 (dismissed in pull request 3479), carry 7 (dismissed: moved to round 11), carry 8 (dismissed: superseded by carries 14 to 17), carry 9 (dismissed: superseded by carries 14 to 17), carry 10 (dismissed: superseded by carries 14 to 17), carry 11 (dismissed: superseded by carries 14 to 17), carry 12 (dismissed: duplicate of carry 20), carry 13 (dismissed: moved to round 11), carry 14 (moved: R11-INTAKE-R10-RESIDUE), carry 15 (moved: R11-INTAKE-R10-RESIDUE), carry 16 (moved: R11-INTAKE-R10-RESIDUE), carry 17 (moved: R11-INTAKE-R10-RESIDUE), carry 18 (dismissed: moved to round 11), carry 19 (dismissed: roster instruction done), carry 20 (moved: R11-INTAKE-R10-RESIDUE), carry 22 (moved: R10-CARRY-AUDIT-P5), carry 23 (moved: R10-CARRY-AUDIT-P5), carry 24 (moved: R10-PROCESS-SLIM), carry 25 (moved: R11-INTAKE-R10-RESIDUE).

## Figures

- `python3 tools/pr/gate_priority.py --self-test`: 21 checks, 0 failed at this head.
- `bash tools/pr/prepr.sh --self-test`: 550 passed, 0 failed at this head.

## Red checks

`instrument-self-tests` step prepr.sh `--self-test` went red at becbe652 under update_pr.sh's environment (above). Root-cause answer: process state (c).

## Forward-carry

none

## Friction

none
