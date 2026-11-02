R10-MACHINERY-RATCHETS Part 1 (unblocking; the orchestrator opens this under group R10-MACHINERY-RATCHETS). CI grades policy-docs with main's `policy_lint.mjs`, which would refuse the new `dev/governance/config/machinery_budgets.json` as an uncovered policy path. This lands the grader hunk first: `POLICY_DIR_EXCLUDE` gains `/^dev\/governance\/config\/[a-z0-9_]+\.json$/` (a grader's data is never prose), plus the config arm in `assertAcceptance` (two pins: the data file drives clean; `dev/governance/config/notes.md` beside it still reports, so the exclusion covers JSON only).

**The `field_coverage.mjs` hunk does NOT ride Part 1.** Judged honestly: a DECLARED `pinned tools/audit/machinery_ratchet.py` entry is refused as DEAD on main, because the pinned set is derived from `codeowners_gap.py`'s `# PINNED` lines (governance.yml), and nothing pins that file until Part 2. It rides Part 2.

Part 2 follows: from 5042e8bc, merge main, re-run prepr, hand off on `handoff/r10-machinery-ratchets`, with the field_coverage entry and the governance.yml pin together.

## Head

50c8e3b32a1d6329bd1519ae87edcbbb9bd5079f

## Mutation proof

Mutant: the same tree with only the regex line dropped (`diff` shows exactly `318d317`). `node tools/policy/policy_lint.mjs` goes red: `FIXTURE OVER-FIRES: checkCoverage reported the grader data dev/governance/config/machinery_budgets.json`, rc=1. Restored: rc=0.

## Null control

- origin/main's `policy_lint.mjs`: fixture `258 pins`; with the hunk `260 pins` (the two new), rc=0.
- Non-widening: the arm's second pin requires `dev/governance/config/notes.md` to report exactly once; it holds (rc=0), and the mutant/hunk pair shows the regex is what separates data from prose.
- field_coverage.mjs, hunk applied on main: `DEAD registry: DECLARED \`pinned tools/audit/machinery_ratchet.py\` is no longer in the derived set`, rc=1; hence deferred.

## Figures

- `node tools/policy/policy_lint.mjs` (acceptance and fixture self-test): 260 pins, rc=0.
- `node tools/policy/field_coverage.mjs` with the deferred hunk applied: dead=1, rc=1 (control for the deferral).
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: MODE: SCOPED, runs tests/entities.py.

## Red checks

none

origin/main had moved to 8f286293 after prepr ran at base 907d29f0 (`git merge-tree --write-tree origin/main HEAD` reports no conflict, so the brief's merge-only-on-conflict rule held and the branch was not merged); prepr rc=0 describes the tree on 907d29f0.

## Forward-carry

none

## Friction

none
