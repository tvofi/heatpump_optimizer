Fix review: blocked c383169a50b6b9668a0e88d829bfc3127f4b3c73 ci-red: prelude and gate are red at this head (prelude's 8700 s wait expired while mutation-pins (1) was still running, and shards 2 and 3 left 8 surviving unpinned sites); ## Red checks does not name prelude and pr-contract refuses the body

bus-nonce: 50e00e14e4adc2387ac313acdd525433

Round: second fix review of #3195 (R10-SAV-COMFORT part 3). This is a delta review after verdict/3195 blocked `6f742a33e` on `tests / typing`. Measured head: `c383169a50b6b9668a0e88d829bfc3127f4b3c73`. It was still the PR head when this verdict was written (`git ls-remote origin refs/pull/3195/head`). `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the contract is current.

## Block

- The earlier block is cured. `tests / typing` (126895292455) concluded `success` at this head. Locally, with the pinned toolchain (`tests/requirements-typing.txt`, mypy 2.4.1), `.venv-typing/bin/python tests/typing_ruler.py --mypy` prints `ALL 9 typing-ruler checks PASSED` (`ev/typing_head.txt`). The repair is the real fix, not a pin. `_l` became `def _l(x: Any) -> list[Any]` and no `# type: ignore` was added. `tests/typing_budgets.json` is byte-identical to main. Putting the lambda back (`ev/typing_mutant.diff`) brings the red back exactly: `FAIL errors did not grow [recorded 0, measured 9 (+9)]` and `FAIL by_code[no-untyped-call] ... (+9)` (`ev/typing_lambda_mutant.txt`). `## Red checks` now answers `typing`.
- A new red blocks this head. `prelude` (126894633123, run 41921429772) concluded `failure` at 00:26:28Z with `FAIL run(s) [41921428453] still adding sources after 8700 s` (`ev/job_126894633123.tail.txt`). The run it waited on was the tests run, and its `tests / mutation-pins (1)` (126895296498) was still `in_progress` after 2.5 h. `gate` (126962980930) then concluded `FAIL prelude: failure` (`ev/job_126962980930.tail.txt`). `merge_train.py classify` returned rc=1: `RED c383169a... pending: none red: gate` (`ev/classify_final.txt`).
- `pr-contract / pr-contract` (126962601041), which started after prelude's red, refuses the body: `ERROR [pr-body] ...: check 'prelude' is red and '## Red checks' does not name it` (`ev/job_126962601041.tail.txt`).
- The long shard is this branch's own volume. `mutation-pins (2)` and `(3)` each drove 4 of this diff's new `optimizer.py` sites. Every mutant survived (`PIN KILLED: 0 pinned, 4 left unpinned (4 survived ...)`), so each one ran the whole closure. That took shard 2 2 h 20 min and shard 3 1 h 37 min. Shard 1 holds the remaining sites and outlived prelude's cap (`ev/pins_*.txt`).
- I do not post a root-cause class. Not all of the head's workflows had concluded (`mutation-pins (1)` was still running), so `ci-red` is the class.
- Owed:
  1. Name `prelude` (and `gate`) under `## Red checks` and answer it.
  2. Give each surviving site a killing check or a `tests/mutation_ledger/survivor_triage/` verdict. The body already promises this before merge. Several are the survivors verdict/3195 listed (below).
  3. Move the head so that CI re-runs with fewer surviving mutants to evaluate.

## Findings

- 8 sites the diff adds survive CI's pins lane. Shard 2: `optimizer.py:454 BOOLOP`, `:485 GUARD_OFF` (`if two_zone:` around `zone = lowers`, verdict/3195's M2), `:488 GUARD_OFF` (the buffer-tank state, M12) and `:494 CMP_BOUND` (the step COP floor, M5). Shard 3: `:454 CMP_BOUND`, `:494 GUARD_OFF`, `:499 GUARD_OFF` and `:519 CMP_BOUND`. Shard 1's sites were not reported. The body's `## Unpinned sites` gives every one of them `mutation-autofix`, but autofix pins only killed mutants, so these 8 still owe a killing check or a triage verdict. Carry: R10-SAV-COMFORT
- The survivors and comment defects that verdict/3195 listed carry over unchanged, because nothing under `custom_components/` or `tests/features.py` moved except `_l`:
  - M13: the schedule's `baseline_kw` is unpinned end to end through `get_current_action`.
  - M2: there is no two-zone comfort check.
  - M3: the midpoint rule is unpinned.
  - M9 and M10: calibrated-month scaling is unpinned.
  - M12: the buffer install's `stored_kw_th` is unpinned.
  - Comment defects: the `stored_heat_schedule` citation, the dead `before = after`, and the `_floor_demand_at_target` docstring.

  Carry: R10-SAV-COMFORT
- `## Unpinned sites` says it is "the whole 6d output at this tree" with 24 sites, and `## Head` names `c383169a`. At `c383169a`, `ci_predict.py` (prepr step 6d) lists 12 sites (`ev/unpinned_6d_head.txt`). Bot commit `26d52a2fb` pinned the other 12 and is a parent of `c383169a`, not an ancestor of the handoff `4cb24054d`. The 24 was true at `4cb24054d`. All 12 sites still unpinned are in the body's list, so no site lacks a disposition. Only the count is stale. Carry: R10-SAV-COMFORT
- Carries 5 and the summer start-bound limit stay residual on #2492, as the body's `## Forward-carry` says. Carry: #2492

## Evidence

- RESULT finder `dev/audit/harnesses/r10_sav_null_settled.py` at this head, rc=0 (`ev/null_settled_head.txt`). Vary: settled saved 32.16 (19.23 %), `stored_heat_sek` 13.15, `comfort_sek` 8.28, comfort-matched 23.88 (+14.28 %), SOUND. Const: saved 6.62 (4.77 %), `stored_heat_sek` −11.15, `comfort_sek` 6.23, comfort-matched 0.39 (+0.28 %), SOUND. Control without the new readings: vary 12.34 %, const 11.86 %. Every figure in the body's `## Figures` and null control re-derives exactly.
- RESULT mutation proof at this head (`ev/mutproof.diff`): `baseline_sek = ... * scale + stored_sek` becomes `... * scale`. `tests/features.py` prints `1 of 4797 FEATURE CHECKS FAILED`, rc=1. The FAIL is `R10-SAV-COMFORT: the month row settles the plan's stored-heat change at the row's metered kWh price`. `r10_sav_null_settled.py const` prints `const: DEFECT`, rc=1 (`ev/mutproof_features_tail.txt`, `ev/mutproof_null_const.txt`). The body's 4783 was counted at an earlier head, and main's merges have since added checks. CI's `tests / fast (3.14)` is green for the unmutated head.
- The PR's delta since `6f742a33e` under `custom_components/` and `tests/` (excluding the ledger) is `_l` alone. A three-dot diff of diffs differs only in hunk offsets and the `_l` lines. Verdict/3195's scope carries for everything else: its mutants, `env_drift --all` and the null control.
- Merge: `git merge-tree --write-tree origin/main c383169a` exits 0 against `086a59da4` with tree `23ad83061`. Its stderr reads `LEDGER-MERGE: resolved tests/closures.json` and has no MERGE-CLAIM line (`ev/merge_tree.txt`).
- `VERSION`, `manifest.json`, `RELEASE_NOTES.md`, `tests/golden/`, `tests/structure_budgets.json`, `tests/mutation_budgets.json` and `tests/typing_budgets.json` have an empty three-dot diff against the merge base `2a9cd3476`.
- CI at this head (`ev/check_runs_final.tsv`): green on `typing`, `fast (3.14)`, `coverage`, `closures`, `replay`, `browser`, `arch-score`, `instrument-self-tests` and `budget-raise-gate`. `tests / mutation` is red on the unpinned-site refusal, which the body answers. `tests / nightly-status` is red and inherited; the body answers it, and it does not read this diff. `prelude`, `gate` and `pr-contract` are red, as stated in the Block.
- Figures I did not re-derive: the per-scenario production-call table (CI `fast` green stands for it), `r10_sav_volume.py`, `r10_sav_actuation_phase.py` and the 5000-input bit-identity script, which is outside the tree.

## Friction

- The container restarted twice during the CI wait. The background classify watchers were lost and re-armed. No local result was lost.
