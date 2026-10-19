Fix review: merge 83e212a1b4823c3e1d9144bde1424a4906302af3

bus-nonce: 73f755f538566aeb25bdfca88040113c

Round 2. Round 1's verdict was `blocked 733ac350 carry-missing: not carried to R10-BRIEFS-FOLD`. Measured head `83e212a1b4823c3e1d9144bde1424a4906302af3` (ev/HEAD). At 11:36 UTC it was still `origin/fix/r10-archscore-census`. The merge base is origin/main `fb9b3fc1f`. The role contract has not changed between the merge base and origin/main (the three-dot diff of `dev/governance/roles/` is empty).

## Round-1 blockers, re-checked

- **Step 10, forward-carry.** The body now names roster SHAs. Both are ancestors of `handoff/audit-r10-roster`, and its tip is `557f7537`.
  - R10-BRIEFS-FOLD's `carry` at `cbdfc9e08` and at `557f7537` holds "Source: #2441 Forward-carry. `archscore.family_orphan_overrides` has no planted census ... `ENTITY_FAMILY_OVERRIDES` dict in place".
  - R10-CI-LAYOUT's `carry` at `557f7537` holds the governance.yml field-coverage path-filter item. It states its control: an M1-shape uncap is caught by the schedule run, not on the PR's own run (ev/carry-ci-layout.txt). It also holds the body_push friction item.
  - R10-STAMP's `carry` holds the bugclasses ledger-row item.
  - All three groups are `not-started` on origin/main's in-tree roster, so each is a live destination.
- **The R2 survivor is now killed.** `RUNS.census` with `censusRegistry` dropped fails the self-test with `FAIL main's census arm runs the registry pass (an ungated row is REFUSED) and then the planted runs`, rc=1 (ev/R2-selftest.txt).

## RESULT lines (finder's instrument: `node tools/policy/field_coverage.mjs`, PYTHONPATH=tests/hastub)

- RESULT head null `--only census`: `read=8 ignored=0 declared_none=0 blind=0 dead=0 refused=0`, `FIELD COVERAGE ok`, rc=0. All 8 per-row figures match the body: 0->1, 1->2, 38->39, 0->1, 1->2, 1->2, 0->1, 1->2 (ev/null-head-census.txt).
- RESULT base `fb9b3fc1f` `--only census`: `read=3`, the three structure.py censuses only, rc=0 (ev/null-base-census.txt). I measured this at the current merge base, not at the body's `90557e39e`, and it agrees.
- RESULT M3 at head (card census entry deleted): `REFUSED census registry: row archscore.card_dead_definitions counts unreached definitions and no census plants it`, `read=7 refused=1`, rc=1 (ev/M3-census.txt). Matches the body.
- RESULT R2 at head: self-test 1 FAILED, rc=1. Matches the body.
- RESULT R6 (my mutant: the planted `run` dropped from `RUNS.census`): the same self-test arm fails, rc=1 (ev/R6-selftest.txt).
- RESULT R7 (my mutant: the `census` key deleted from `RUNS`): the self-test crashes with `TypeError: RUNS.census is not a function`, rc=1 (ev/R7-selftest.txt).
- Self-test at head: `FIELD COVERAGE SELF-TEST ok`, rc=0, 33 ok lines.
- Each other arm is rc=0 with `blind=0 dead=0 refused=0`: `--only hooks`, `--only ruleset`, `--only budgets`, `--only approvals` and `--only registry`.
- `--only bogus` prints `--only bogus: no such arm`, rc=2.
- After every mutant the worktree was restored, and `git status --short | wc -l` printed 0.
- M1, M2 and M4 were measured by the body and by round 1 at earlier heads. The diff `733ac350..HEAD` of `field_coverage.mjs` touches only `censusRegistry`'s `rows` default, the new `RUNS` table, its self-test arms and `main()`'s dispatch. It does not touch the ci-ratchet instrument, `ratchetRow` or `metrics/card.py`. I did not re-run M1, M2 or M4 at this head.

## Other checks

- Step 6, class rule: `jq -r 'keys[]' tests/structure_budgets.json tests/ci_budgets.json | grep -iE 'dead|kept|unused|unread|orphan'` returns 9 rows at head (ev/class-rule.txt).
  - 8 are gated by CENSUSES.
  - `archscore.family_orphan_overrides` is exempt, with its reason, and carried to R10-BRIEFS-FOLD.
  - No seam is open.
- Body figures re-derived at this head:
  - `ALL 2350 ENTITY CHECKS PASSED`, rc=0 (ev/entities.txt);
  - `MODE: SCOPED -- 1 script(s) run, 32 scoped out.` (ev/closure-select.txt).
  - I did not re-run the remaining local rc=0 list (structure.py, layout.py, closure selftest, env_drift claims-only, fold_ledger, policy_lint --budgets). CI's arch-score, budget-raise-gate, policy-docs and closure-scope are green on this head.
- Step 7: the body names `83e212a1` as its head. Its figures were taken at `da6b4520`. The resolution delta `da6b4520..83e212a1` is 6 files, all `dev/programme/delivery/*.md` rows, and is empty on the PR's three code files (ev/resolution-delta.txt). So the body's figures carry to this head.
- Merge: `git merge-tree --write-tree origin/main 83e212a1` gives rc=0, tree `156f565b1`, no conflict.
- Step 5 and step 4: `VERSION`, the manifest, `RELEASE_NOTES.md` and `tests/golden` are untouched in the three-dot diff. No claim file is touched, so step 4 is vacuous.
- Step 14: no budget, closures, INERT, score or ledger file moves. The diff is `bugclasses.json`, `delivery/2441.md`, `tests/ci_ratchet.py` and `field_coverage.mjs`.
- Step 15: `RUNS` replaces six hand-written `if` lines with one table that both `main()` and the self-test drive. This is sound. One nit, not blocking: the usage string still lists the arm names by hand, beside `RUNS`.

## CI at this head (commit check-runs API, 49 runs, ev/check-runs.txt, read 11:36 UTC)

- No run is red.
- Green: pr-contract (2 runs), arch-score (2), env-matrix, validate-hacs, coverage, coverage-ratchet, fast (3.14), browser, instrument-self-tests, mutation, nightly-status and the rest.
- CodeQL is neutral. `Analyze (python)` was still in_progress at read time.
- Earlier heads `da6b4520` and `808166206` carry no non-green check runs.
- Round 1's reds at `733ac350` (rate-limit failures and nightly-status) are answered in the body's `## Red checks`. Step 11 is satisfied.
