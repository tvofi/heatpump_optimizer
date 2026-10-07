Fix review: merge 95ad5034d4e41b5440b3c08350a2964c57867a84

bus-nonce: 617b099659054169f754a9568bc84315

Measured detached at 95ad5034d4e41b5440b3c08350a2964c57867a84. The body names this head. Parents 8d2be1a27a815ea88a823873ed44868caf97f461 and 618d014f0b91ac39d77250bf887618002f628307. origin/main is bcea74883bec1e3395377ff70d8640737c97fc3e. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty. The three-dot diff does not touch `VERSION`, the manifest version, or the `RELEASE_NOTES.md` heading.

`git merge-tree --write-tree origin/main 95ad5034d4e41b5440b3c08350a2964c57867a84` exits 0. stdout is tree `4f4980e0cf27c193238b6ecfee5a77ec96781f43`. stderr is only `LEDGER-MERGE: resolved tests/closures.json` (`closures.tests/harness_headers.py` merged as a set, 363 entries).

`dev/programme/delivery/1987.md` is the row. `git ls-files` does not list `docs/delivery/1987.md`.

Held, not re-derived: `tests/manual_plan.py` printed `failed=1`. The ledger reason text still says `failed=2`; that text is not the measurement. The ratchet base held from the prior inventory is `6001b09a557259f37319b400d219cf83e02c563f`. The mutation table was not re-run.

Job 112608980305 (`env-matrix`, success) checks out this head's `tools/policy/policy_lint_envmatrix.mjs` and runs `node tools/policy/policy_lint_envmatrix.mjs`. `lintScript` prefers `tools/policy/policy_lint.mjs`. The log's shallow arm is `ok shallow / policy_lint rc=0`. `16 declared outcome(s) held, 0 did not`. It does not start `.claude/workflows/policy_lint.mjs`.

`CLAIM_HEAD` `python3 tests/env_drift.py --claims-only` against the merge base exits 0: `claims hygiene: 618d014f0b91ac39d77250bf887618002f628307 ok`.

Check-runs on this head: `delivery-status` and `nightly-status` are failure; `## Red checks` names both in backticks. `env-matrix` and both `pr-contract` runs are success. `closures`, `mutation`, `fast (3.14)`, `coverage`, `browser` and `Analyze (python)` were in progress. The gate and the mutation table were not re-run.

evidence: /Users/timmalmstrom/hpo-seats/r9-dbg-1-review-95ad/evidence
