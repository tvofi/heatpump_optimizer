Fix review: merge ce9cba9a44f30005eee75749dbb3a1c48afc6150

bus-nonce: 973615d681c014c58b469518809d6b13
pending-ci: gate

## Scope

Delta review, a7a9c09806e600bd3f8f5f38c6741004fe81ad71..ce9cba9a44f30005eee75749dbb3a1c48afc6150: one commit, e0d5bf5618, merged by ce9cba9a44, touching dev/programme/carries/carry-3885.json only (3 lines). The previous verdict's block (introduced-red tests / briefs: carry 0 cited dev/audit/harnesses/ci3885_light.py, which is not in the tree) is the only finding in scope. A records delta does not widen the scope.

## Evidence

- Each of the three citations of the harness in carry 0 (`from`, `control`, `remeasure`) now names it "(at 7eb9b2fd81bbe71be048e730481470de62c0932c)", the form brief-citations.md rule 1 accepts for a tag-only path. `git ls-tree -r --name-only 7eb9b2fd81` lists dev/audit/harnesses/ci3885_light.py, and the commit resolves on origin (the GitHub commits API returns it; it is on origin/handoff/ci-3885-nonprod-scope and origin/fix/ci-3885-nonprod-scope-pr).
- `node tools/policy/brief_lint.mjs` at the head: rc 0, `dev/programme/carries/carry-3885.json -- 0 error(s), 0 warning(s)` (ev/brief_lint_head.log).
- Mutation: with the three "(at 7eb9b2fd...)" clauses deleted, `node tools/policy/brief_lint.mjs dev/programme/carries/carry-3885.json` prints `ERROR [carry-3885.json carry 0 control] path: dev/audit/harnesses/ci3885_light.py: not in the tree, and no tag SHA is cited alongside it`, `TOTAL: 1 error(s)`, rc 1; restored, 0 errors. The citation is what clears the linter.
- CI at this head: `tests / briefs` completed success (check run 139051029303).
- `git merge-tree --write-tree origin/main ce9cba9a44` exits 0: merges cleanly.
- `merge_train.py classify ce9cba9a44 --pr 3889` printed `WAIT ce9cba9a44f30005eee75749dbb3a1c48afc6150 pending: gate red: none` on 31 polls over about 30 minutes (ev/classify.log), with `tests / coverage` and `tests / closures` still in progress. Hence the pending-ci line.
- The cited commit lives on the #3885 light-grading branch, not on main; the carry's commit message scopes it "until #3888 lands it", the brief-citations.md rule 3 use of a tag citation.
