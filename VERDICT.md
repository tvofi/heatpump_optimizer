Fix review: merge ae77c4150ee0245f5546c73fd9c3f35691e9a3c6

bus-nonce: e21fc36e00b37bad2d5f2e729ce16e2b

Round 1 review of #2708 (R10-FLY-ENVMATRIX-NOREMOTE), measured at head ae77c4150ee0245f5546c73fd9c3f35691e9a3c6. I re-read the head before writing this and it has not moved (ev/HEAD_rechecked.txt).

## Evidence

- RESULT roles-current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty. The contract was read from origin/main.
- RESULT merge: `git merge-tree --write-tree origin/main ae77c4150ee0245f5546c73fd9c3f35691e9a3c6` exits 0 with origin/main at e97f5749b441 (tree 53f75cd8aa74). There is no conflict and no claim-file driver call.
- RESULT diff: three-dot from merge base ac5788f26. Four files change: the driver, the new harness, its `tests/closures.json` entry (the ci_predict --apply-inert commit 9ab6bf1db) and the PR's own delivery row. VERSION, the manifest, RELEASE_NOTES.md and tests/golden/ are untouched. `env_drift.py --claims-only` prints ok, `structure.py` prints STRUCTURE RATCHET PASSED, `rules_sync.mjs --check` prints ok, and the scoped gate reads `MODE: SCOPED -- 1 script(s) run`. All match the body.
- RESULT mutation (step 1): M0 to M3 reproduce the body's table exactly (ev/mutants.txt). M1 and M2 each give `MATRIX MUTE: 1 of 2` and M3 gives `2 of 2`. The null run reaches the shapes. The self-check is not vacuous for the helper it guards.
- RESULT harness, finder's shape (step 2). The harness is the fixer's own: the finding had no committed harness. The body names it as built in this diff, and it reads governance.yml's own restore step, so it is CI's shape. I re-ran it without trusting the fixer's figures:
  - head over main e97f5749b, live: `16 declared outcome(s) held, 0 did not`, rc=0.
  - head over main, `--no-live`: `15 held, 1 did not`. The one is `pr / nothing skipped in a full clone` (API unreachable, its declared outcome).
  - merge base ac5788f26 over itself, `--no-live`: the same `15 held, 1 did not`, on the same row. This is flat at both ends, as designed.
  - 97ac438d6 over 47147487ba2b, live, base driver: `9 held, 7 did not`. The six exit-code rows end at a bare `rc=1` / `rc=1 pins=246`, and shallow already carried its ERROR.
  - The rebuilt probe over 47147487ba2b, live: `9 held, 7 did not`. These are the same 7 rows. Four read `37 ERROR line(s), first: ERROR [required-contexts] ... has \`gate\`` and three read `MUTANTS: the entry point exited 1 ...`. This confirms "changes what a row says, never whether it holds".
  - Not re-derivable by SHA: the body's probe commit 4c60235d9018 is not on the remote (`bad object`). I rebuilt it as 596b32d1ab86, which is 97ac438d6 plus the head's driver blob (ev/probe.txt). That is the same construction the body describes, so its figure is re-derived under my own rebuild, not from its SHA.
  - This seat's `gh` has no valid token, so the live arm here read the API unauthenticated. The figures still match the body.
- RESULT class (step 6): the body's rule `grep -cE "const (\w+) = sh\('node'"` returns 11 at the base and 11 at the head. Each is dispositioned in the body. At the head the 7 policy_lint/mutants rows all go through rcRow. No seam is open.
- Not re-derived: the CI-history figures (599 env-matrix jobs, 17 failed, 14 no-remote, job 119863295377's 18 ERROR lines). This seat has no authenticated `gh api` for job logs. They are the body's account. They bear on the cause narrative, not on the change, which the harness runs above verify directly.
- CI (step 11): at review time the head's check-runs show no failure. pr-contract, env-matrix, policy-docs, hassfest, codeql, tests/* and mutation are queued or in progress. Completed so far: closure-scope, briefs, nightly-status, delivery-status, validate-hacs, arch-score, budget-raise-gate, prelude, refresh and cancel-superseded, all success. The earlier head 369e7e20b's two CI runs concluded `cancelled` (superseded), not red. The body answers the instance's env-matrix red (the cheaper detector is the row's own detail, which this diff builds). This verdict does not cover a red that lands after it. The merge train reads the head's concluded CI.
- Forward-carry (step 10): the body dismisses it with a reason. The refuted "flake" reading is recorded in the body, and the roster carry correction is handed to the orchestrator under Friction. No later stage's brief changes.
- Architecture (step 15): one module, one helper and one self-check. Nothing breaches or departs from it. The departure from the roster's file list (governance.yml untouched) is justified: the job runs the driver from the head.

## Findings

- Surviving mutant M5: reverting any one row from `rcRow` back to `add(name, ok, \`rc=${r.rc}\`)` (tried on `no-remote / policy_lint rc=0`) passes the self-check (0 MATRIX MUTE). The self-check pins the helper and `why()` ranking, not that each exit-code row calls the helper, so a later edit can re-mute a row silently. A cheap closure is a structural count in the self-check, e.g. the driver's own source must have no `add(` whose detail is a bare `rc=${`. That is not needed for this PR's claim, which is about the helper's output. Carry: R10-FLY-ENVMATRIX-NOREMOTE
