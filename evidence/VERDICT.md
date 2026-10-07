Fix review: merge 1e91aa59b449c3d51cdee4160d1a10523741e5e2

bus-nonce: 87d35353b29f443e942a66c07c29156f

Round 8, a delta review of the three commits since the round-7 block at `4e3f09b6a7230b9fdbaad3ea6b144a82466ccc87`. Measured detached at `1e91aa59b449c3d51cdee4160d1a10523741e5e2`, which the body's `## Head` names. It is the live PR head. origin/main is `e7479ad19f9643a59dd61cfaca5e871c75bc1a6d`. `git diff $(git merge-base origin/main HEAD)...origin/main -- tools/audit/briefs/ dev/governance/roles/` is empty. `VERSION`, the manifest version and the `RELEASE_NOTES.md` heading are untouched (three-dot diff empty). `git merge-tree --write-tree origin/main HEAD` exits 0.

## The round-7 block is cleared

The block was `mutation-unpinned: quiet_windows.py:507 GUARD_OFF`.
- `93ddd53e` adds `tests/mutation_ledger/killed_by/quiet_windows.py/configured_specs.GUARD_OFF.b6ab8a95.json`. It records `killed_by: tests/manual_plan.py` and `old: "    if silent_unenforceable(config, get_state):"`. Line 507 of `quiet_windows.py` at this head is that line.
- The pin's reason text says `failed=2`. My run printed `1 of 129 manual plan checks FAILED`. Round 6 flagged the same text, and the ledger reads the kill, not the count.
- RESULT mutant_guard_off_507=fail  (line 507 replaced with `if False:`, `FAIL configured_specs returns the stored rows and the not-enforced marker`; restored, `git status` clean)
- RESULT null_manual_plan=pass  (ALL 129 manual plan checks PASSED)
- RESULT mutation_table_local=ok  (`python3 tests/mutation_table.py --scope changed --base origin/main` first line: `4693 unpinned site(s) of 5820 candidate sites, 4693 at the ratchet base e7479ad1...; the ledger agrees with the deterministic inventory`. It does not refuse; at `4e3f09b6` it refused 4695 against 4694.)
- RESULT ci_mutation=success  (job 112944372646: the same agreeing line, no `INCONCLUSIVE`, no `REFUSED`. The `NULL_COMMENT` null controls survive every driver, which is what a comment mutant should do.)

## Merge resolutions

- `b4838124` (main `09ba95d0`). `git merge-tree` of its parents reports content conflicts in `README.md`, `docs/architecture.md`, `docs/configuration.md`, `tests/deployment_shape.py`, `dev/audit/rounds/round4/D6/claims.json`, `claims.py` and the old `tools/audit/round4/D6/claims.md`, and a ledger-merge on `tests/closures.json`. The body names all of them and the resolution of each:
  - The entity-count prose is 79, with 5 buttons and 6 switches. `dev/audit/rounds/round4/D6/claims.py` run at this head leaves the tree clean, so the committed `claims.json` and `claims.md` equal a fresh regeneration. The claims counter measures the same census the prose states.
  - The `tests/deployment_shape.py` docstring conflict took main's text, which `6ac742aa` then recounted to 120 of 528 pairs. That commit changes only the docstring.
  - `tools/audit/round4/D6/claims.md` is absent because main moved the D6 files.
- `0cf18f23` merges `6ac742aa`. The final merge `1e91aa59` (main `e7479ad1`, #2018 and a record commit) is clean: `git merge-tree --write-tree 0cf18f23 e7479ad1` exits 0 with tree `94ab9815...`, equal to the commit's tree.
- RESULT structure=pass  (`python3 tests/structure.py`: STRUCTURE RATCHET PASSED)
- Nothing from either side reverted. The patch is unchanged from the round-6 pass, apart from the pin and the docstring recount.
- Not run locally. `tests/entities.py` needs Python 3.12 or later, and this seat has 3.11. Its result is CI's (`fast (3.14)`, below).

## CI at the head (API check-runs, 0 failed calls)

All 31 runs are complete.
- `mutation` success (112944372646). `closures` success (112944477769). `fast (3.14)` success (112944372714), which runs `entities.py` and `deployment_shape.py`. `coverage`, `env-matrix`, `hassfest`, `typing`, `browser` and `briefs` are green.
- `pr-contract` success (112944371190, 112962506844). `closures-autofix` and `mutation-autofix` skipped.
- `budget-raise-gate`: run 112944371180 was cancelled and I reran it, `gh run rerun 37665742426 --job 112944371180`. Both the twin (112944382424) and the rerun (112949596438) are success.
- Red: `delivery-status` (112944371696) and `nightly-status` (112944372135). These are main's, and the body's `## Red checks` answers both.

## Body

- `## Delta since the last verdict` lists the three commits that follow `4e3f09b6` and what each changed, and it is accurate against `git log 4e3f09b6..HEAD`.
- `## Red checks` names every check that went red in the range, with a cheaper detector for each: `closures`, `closures-autofix`, `fast`, `mutation`, `mutation-autofix`, `env-matrix`, `pr-contract`, `delivery-status` and `nightly-status`. The two `mutation` and `mutation-autofix` items for `4e3f09b6` are named and pinned in `93ddd53e`. None is left unanswered.
- `## Friction` records the third `stress.py` recording failure, and `## Forward-carry` is "none".
- The body's `## Head` names `1e91aa59`.

## Not blocking

- The body's top section describes `4e3f09b6`, which it says in its own words.
- The `failed=2` text in the pin's reason is stale, as noted above.
