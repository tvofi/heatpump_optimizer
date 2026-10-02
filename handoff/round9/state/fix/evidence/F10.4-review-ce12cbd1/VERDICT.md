Fix review: merge ce12cbd10b4f58ab2b72311da79847f73cda988f

PR #1838, R9-F10.4, round 3, reviewing the resolution delta. Round 2 passed 9c4e4516 (F10.4-review-9c4e4516); round 1 blocked a980e165 on census-hole. The measured head is ce12cbd1, which is the PR head and handoff/r9-f10-gate-infra-4 at posting. Body fca2e4ff names ce12cbd1.

## The delta since 9c4e4516

1. **9f9e8bcc merges main 777c2318 (#1836, #1837) into 9c4e4516.** `git merge-tree --write-tree 777c2318 9c4e4516` exits 0 and yields tree a59bca5c, and `git diff a59bca5c 9f9e8bcc` is empty, so the committed merge is git's own merge with no hand resolution. The ledger driver printed `LEDGER-MERGE: resolved tests/closures.json`. `tests/entities.py` merged with no conflict.
2. **ce12cbd1 changes only tests/deployment_shape.py's #1218 docstring:** 83 pairs becomes 82, and it adds the doc_claims/manual_plan reason.

## The two-sided files, checked by measurement rather than by the clean merge

On Linux with strace, I recorded closures fresh at ce12cbd1 with `closure.py record` for tests/doc_claims.py, tests/structure.py, tests/deployment_shape.py and tests/entities.py, then ran `closure.py check --partial`. Result: rc=0, "committed closures cover every file this run touched". entities.py has 1 over-scoped file, which is safe. See closure_check_partial.txt and the *.log files.

The recordings' own runs at this head:
- doc_claims ALL 112 PASSED
- STRUCTURE RATCHET PASSED
- ALL DEPLOYMENT SHAPE CHECKS PASSED
- ALL 2055 ENTITY CHECKS PASSED (2053 at the branch plus main's two)

## The 82-pair figure, re-derived with my own count

I counted Jaccard overlap of production-module closures over tests/closures.json, using my own definition (the one the docstring describes). It may differ from deployment_shape's internals.
- At ce12cbd1: RESULT pairs=378, comparable=300, at_or_above_0.80=82; doc_claims/manual_plan = 0.787.
- At main 777c2318: 83.
- The −1 is the I5 arms' two new reads in doc_claims.py's closure, as the docstring now says.

## The PR's own work, unchanged by the merge

The merge brings no production code.
- structure.py: rc=0, every RESULT and budget equal to round 2 (dead_methods 3, coordinator_multiassigned_attrs 120).
- My field-collision probe: field_collision_unprinted=0, name_kept_reported=113.
- mutants.py: unmutated rc=0 []; all 13 mutants red.

## Carried from round 2, still owed to tvofi

- The budget re-baselines (`dead_methods` 0→3, `coordinator_multiassigned_attrs` 117→120). Both are redefinitions at measured values, under plan card B5.
- The `briefs` red: base-pinned brief_lint.mjs against the retired `coordinator_loc` pin. It cannot go green from inside this PR, and that is the owner's call.
- The brief_lint.mjs edit is policy and needs tvofi's approving review.
- CI's gate and mutation runs on ce12cbd1 are not cited here. The merge rule's CI-green condition still applies.
