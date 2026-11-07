Study result for R10-HOTFIX-CODEQL-HEADROOM re-cut: no code change. Step 0 measured the headroom as short (p90 above 36 min), but the cause is runner-speed variance, not code shape, and the one lever the brief names cannot be resolved by a single CI run. Recommendation: do not merge a restructure of `tests/features.py` or `tests/entities.py` on this evidence; the owner re-scopes the group (below).

## Head

`aaaec2128e5d2efc2e0ad8ffe4918eec6cbb7f98` (origin/main at the time of measurement). No code branch was pushed.

## Mutation proof

n/a: no production or test change.

## Null control

Two main runs, same files, extraction logs read from the job logs. The unchanged files move with the two big ones, which is the null control for any before/after on one run:

| job | run | job min | features.py ms | entities.py ms | ratio | merge_train.py ms | stress.py ms |
|---|---|---|---|---|---|---|---|
| 128423079820 | 42379183423 | 26.45 | 739494 | 314673 | 2.35 | 7719 | 3222 |
| 128452047588 | 42387923316 | 43.93 | 1331876 | 673288 | 1.98 | 14688 | 6571 |

Every file's extraction time doubled between the two runs (stress.py 2.04x, merge_train.py 1.90x, entities.py 2.14x, features.py 1.80x), and the features/entities ratio sits in the normal 2.0 to 2.45 band both times. So the job's 26-to-45 minute spread is runner speed, and no code change at this size would show above it in n=1.

## Figures

- Python analysis job on main push, ci.yml, last 20 completed runs (42387923316 back to 42344243440): p50 41.4 min, p90 44.4 min, max 45.05 min against the 45-minute cap; 13 of 20 at or above 36 min, 5 at or above 44 min. Command: list `ci.yml` runs with `branch=main event=push` through `gh api repos/tvofi/heatpump_optimizer/actions/workflows/ci.yml/runs`, then `gh api repos/tvofi/heatpump_optimizer/actions/runs/<id>/jobs --paginate`, keep `codeql / Analyze (python)`, duration = completed_at - started_at. (Note `codeql.yml` push runs listed by workflow are not this job; the caller is ci.yml.)
- Of those 20 runs, 3 were cancelled at the cap (42383047802 at 45.0 min, 42344243440 at 45.05 min, and run 42335419215 just outside the window at 45.1 min), the rest succeeded.
- Extraction lines: `gh api repos/tvofi/heatpump_optimizer/actions/jobs/<job id>/logs`, grep `Extracted file .* in N ms`, jobs 128423079820 and 128452047588.
- Structure at the base: `tests/features.py` has 143 module-level `try` blocks (largest 159 lines at line 1676, max nesting 2) and about 52,000 module-level lines; `tests/entities.py` has 90 module-level `try` blocks (largest 88 lines) and about 26,000 module-level lines. Command: an `ast.parse` walk over `tree.body`. There is no 364-line block on main now, so the #3232 trigger is not present at the base.

## Red checks

none.

## Forward-carry

- The python job is cap-adjacent on main by runner variance alone (3 of 21 recent runs hit the cap with no growth of either file). A fix inside the two files cannot be measured against a 2x runner spread with one run; it needs either the owner's choice of a structural lever outside the brief's constraints (split the python job by path, a larger runner, or a cap raise, each of which the brief excluded) or a repeated-run protocol (at least 5 runs per arm, compare the features/entities ratio and the unchanged-file control, not minutes). Carry: R10-HOTFIX-CODEQL-HEADROOM
- Moving the 52,000 module-level lines of `tests/features.py` into once-called functions is a very large mechanical change whose benefit was only claimed for a block shape (a new 364-line try/finally) that is absent on main; every feature check would change its position and #3232's reshape lands in the same file. Carry: R10-HOTFIX-CODEQL-HEADROOM

## Friction

- codeql-dispatch: contradiction: the brief asked for p90 under 36 min as the refusal rule, but the p90 is high because of runner variance, which the rule does not distinguish from code-shape cost. Carry: R10-HOTFIX-CODEQL-HEADROOM
- seat-tooling: stale: no `codeql` binary in the cloud seat, so extraction time cannot be measured before a CI run. Carry: R10-HOTFIX-CODEQL-HEADROOM
