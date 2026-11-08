Root-cause analysis `dev/audit/rca/R10-RCA-STAMP-CLAIM-CONFLICT.md` for the stamp that left #3297, #3299 and #3308 refused by the claimnotes driver; the class is registered as `N-stamp-claim-conflict` in `dev/audit/config/bugclasses.json`. No production code, no policy landed. Process state (a); cost test favours building the countermeasure (section 4); it narrows a sentence of `claim-files.md`, so it waits for the owner's approving review (section 5).

## Head

1e87d78d98b361ffeb4d2ed1fb4d087e332bcf29, measured on a branch cut from origin/main 72940b795. Main has not moved to a conflict: `git merge-tree --write-tree origin/main HEAD` is clean.

## Mutation proof

n/a: no countermeasure is landed; the document records a prototype. Its null controls (edited-line and non-empty-stamp cases stay refused) are in section 5.

## Null control

The unmodified tree refuses the reproduction: `git merge-tree --write-tree 2a3c05644 <branch>` for a branch cut at the stamp's parent that appends one claim line prints `MERGE-CLAIM: refused`. A branch cut at `v7.1.5` (base without claims) resolves.

## Figures

- `fold_ledger.py check`: 0 violations (`python3 tools/audit/fold_ledger.py check`).
- Refused open heads, 3 of 4 claim-touching: `git merge-tree --write-tree origin/main <head>` per head, section 3.
- `finding-class-id` agreement lane: the new class id also joins `dev/audit/config/finding.schema.json` and the generated copies in `.claude/workflows/audit-find.js` (`fold_ledger.py sync`); `node tools/policy/agreement.mjs --py-json` printed one divergent id before, 0 after.
- Mutant run: none; the added lines are markdown and JSON, so `mutant_run.py --diff` has no site. Survivors 0.

## Red checks

prepr `closures` refused: `PYTHONPATH=tests/hastub python3 tests/entities.py` prints `3 of 2665 ENTITY CHECKS FAILED` (coverage-job cache key, release ZIP build, Pages workflow probe) on this head and on unmodified origin/main 72940b795, so this diff adds none; the cheaper detector is that same script, already run, and its red is environmental (no packaging tools in this container) and not in the required set.

## Forward-carry

The driver change, its entities test and its `claim_merge_mutants.py` case are owed after the owner's approval of the `claim-files.md` sentence. Carry: dismissed: proposal for the owner, no stage is waiting on it.

## Friction

none
