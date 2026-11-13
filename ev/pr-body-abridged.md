Carry 21 repair: pin the hotfix-scope classifier seam (abridged copy of the live PR #3547 body at 2a1a7de0; narrative sections shortened, Carry status/Red checks/Forward-carry/Friction verbatim).

## Carry status

This part builds carry 21 only. Each other dispatched carry keeps the disposition its own text carries in the brief and is not built here: carry 0 (dismissed: moved to round 11), carry 1 (dismissed: moved to round 11), carry 2 (dismissed: moved to round 11), carry 3 (dismissed: moved to round 11), carry 4 (implemented at 6e100ef6980216a81eaa0438bdc215d62b19271f), carry 5 (moved: R11-INTAKE-R10-RESIDUE), carry 6 (dismissed in pull request 3479), carry 7 (dismissed: moved to round 11), carry 8 (dismissed: superseded by carries 14 to 17), carry 9 (dismissed: superseded by carries 14 to 17), carry 10 (dismissed: superseded by carries 14 to 17), carry 11 (dismissed: superseded by carries 14 to 17), carry 12 (dismissed: duplicate of carry 20), carry 13 (dismissed: moved to round 11), carry 14 (moved: R11-INTAKE-R10-RESIDUE), carry 15 (moved: R11-INTAKE-R10-RESIDUE), carry 16 (moved: R11-INTAKE-R10-RESIDUE), carry 17 (moved: R11-INTAKE-R10-RESIDUE), carry 18 (dismissed: moved to round 11), carry 19 (dismissed: roster instruction done), carry 20 (moved: R11-INTAKE-R10-RESIDUE), carry 22 (moved: R10-CARRY-AUDIT-P5), carry 23 (moved: R10-CARRY-AUDIT-P5), carry 24 (moved: R10-PROCESS-SLIM), carry 25 (moved: R11-INTAKE-R10-RESIDUE).

## Red checks

`instrument-self-tests` step prepr.sh `--self-test` went red at becbe652 under update_pr.sh's environment (above). Root-cause answer (defect-root-cause.md second trigger): process state (c), the self-test ran and was obeyed but assumed an unexported caller. The cheaper detector is the same self-test run once with `PREPR_SKIP_CLOSURES=1` exported, in the fixer's pre-handoff checks; standing cost about 9 minutes of one background run per handoff that touches prepr.sh, against one red PR update cycle. The scrub makes the exported run equal the unexported one, so the extra run only guards a future row that bypasses the scrub.

## Forward-carry

none

## Friction

none
