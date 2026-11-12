Hotfix: `pr_group_of` (tools/audit/carry_audit.py) resolved a pull request's own roster group from main's roster only, so a fixer's own `Carry N:` status lines were refused (body_push CARRY-LANDED) when the group exists only on the round's roster branch. It now reads the union of main's groups and the round roster branch's groups, the two sources the destination check already reads; main wins on a name collision. body_push.sh's default roster ref is unchanged.

## Head

04129e8498f2fb40adfb781ca11f877541823af8

## Mutation proof

Mutant `R-roundgroup` (dev/audit/harnesses/r10_carry_parser_mutants.py) restores the main-only read at the `# mut:roundgroup` line. `python3 dev/audit/harnesses/r10_carry_parser_mutants.py R-roundgroup` reports the self-test row "landed: an own-group status line whose group is on the round's roster branch only lands nothing" FAIL and `survived=0`.

## Null control

The self-test row "landed: a status line whose own group is on neither roster still refuses (null control)" passes: `pr_group_of` returns None and no status is recorded. Unmutated, `python3 tools/audit/carry_audit.py --self-test` reports 0 failed.

## Figures

- `python3 tools/audit/carry_audit.py --self-test`: 0 failed.
- `python3 dev/audit/harnesses/r10_carry_parser_mutants.py R-roundgroup`: survived=0.

## Red checks

none

## Forward-carry

none

## Friction

- tests/entities.py: unenforced: one run at this head failed the diagnostics check "the location is redacted whole, from data and from options, not coarsened"; the same suite passed at the base head and on a rerun at this head, so it is nondeterministic and unrelated to this diff. Carry: dismissed: nondeterministic check outside this group's seam, not reproduced on rerun
