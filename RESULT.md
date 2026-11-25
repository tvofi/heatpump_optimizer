# merge-3835 — PR #3835 (R11-SEAM-learners) merge-main repair

New head: 0291a7d9a575c3cf1fb669b73e1446e063fbddb2, pushed to refs/heads/handoff/r11-seam-learners-pr as a fast-forward from 7e2f095c50 (an ancestor of e4d40de3).
Resolution delta for the reviewer: e4d40de37bc2c2c22e78d2397e0a49d379528c9e..0291a7d9a575c3cf1fb669b73e1446e063fbddb2
- 7c52e30309 merges origin/main (7c52e303^2) into e4d40de3
- 0291a7d9a5 re-records structure budgets (lowered only)

## Resolution per file

Files changed on both sides since the merge base (`comm -12` of the two `git diff --name-only` lists): docs/architecture.md, tests/closures.json, tests/entities.py, tests/features.py, tests/structure_budgets.json.

- tests/features.py (the one textual conflict): union. Both sides appended a section before `sys.exit(R.close(...))`: the HEAD side "R11-SEAM-learners: the one freeze predicate" first, then main's "R11-OWNER-CARD-EXTERNAL-HEAT". Only the conflict markers were removed. The two sections use distinct local-name prefixes (`_lf_`, `_oc_`), and `ast.parse` passes.
- tests/closures.json, tests/structure_budgets.json: resolved by the LEDGER-MERGE driver (`closures.tests/entities.py: merged as a set`).
- docs/architecture.md, tests/entities.py: auto-merged without conflict.
- Read-back (orchestrator.md s6), run on all five files at 7c52e303. Rule: every line in the merged file comes from one of the two parents, and every parent line missing from it is a line the other side deleted (present at the merge base, absent from the other parent). Result: 0 foreign lines and 0 unexplained missing lines in each file.
- dev/audit/rounds/round4/D6/claims.*: regenerated with `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` (rc=0). `git status` showed no change afterwards.
- tests/structure_budgets.json: `python3 tests/structure.py` at the merge read class_excess_loc 17297->17296 and module_excess_loc 21774->21773 as IMPROVED. At e4d40de3 alone it reads none. Recorded with `--record` in 0291a7d9a5, reason in the commit message. No budget raised.
- tests/closures.json re-record (Linux, strace present):
  - `./tests/derive_closures.sh --single tests/features.py`: rc=0 (166 files), no diff to the merged file.
  - `--single tests/entities.py`: refused, because the script exits 1 while recording (see the next section). Its closure stays as the driver's set union of the two sides.

## Gate

`GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) PYTHONPATH=tests/hastub ./tests/run.sh` at 0291a7d9a5:

    MODE: SCOPED -- 32 script(s) run, 2 scoped out.
    FAILED python3 tests/entities.py (741s)  -- 1 of 2762 ENTITY CHECKS FAILED
    1 TEST SCRIPT(S) FAILED

The one failing check is "and the lane's docstring records those measured numbers as the selection-cost note (#1218)", with missing markers `['184 of the 561']`.

- This red is not caused by the merge, and origin/main does not have it. The pair rule (copied from tests/entities.py `_d308_pairs`: Jaccard >= 0.80 over production closure files) gives these results on `tests/closures.json`:
  - origin/main: 182 of 561, with 121 production files
  - e4d40de3 (PR head, before the merge): 184 of 561, with 122 production files
  - 0291a7d9: 184 of 561, with 122 production files
- tests/deployment_shape.py says "182 of the 561" at all three of those commits. The PR updated its "all 122 files" marker but not the pair count, which came with its new learning_freeze.py.
- Not fixed here: this seat's brief covers reds the merge caused. Owner of the fix: the PR's fixer or orchestrator. The fix is the docstring count 182 -> 184 (with its history clause), followed by an entities.py `--single` closure re-record.

Other checks:
- `python3 tests/structure.py` after the re-record: no violations.
- `node tools/policy/brief_lint.mjs`: rc=0. The only errors it prints are its own fixture self-tests.
- Commit messages in the delta contain no Claude, Co-Authored-By or session trailers: `git log --format=%B` was checked with grep, and the grep returned nothing.
