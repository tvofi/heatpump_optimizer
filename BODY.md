This is the countermeasure from #2056's root cause, in group R9-CI-2. `nightly-ha` runs only on `schedule` and `workflow_dispatch`, so #2041's A16 check, whose container half no pull-request lane executes, merged unrun. Both arms then went red at the next schedule on `main` (run 37753990323).

With this change, `nightly-ha` runs, still unrequired, on a pull request whose three-dot diff touches what the lane's driver reads outside the package:

- **`closure-scope`** emits a new output, `nightly_ha`. It is `true` when `git diff --quiet "$BASE"..."$HEAD" -- <pathspecs>` finds a change.
- **`nightly-ha`** now `needs: [closure-scope]`, and its `if:` admits `pull_request` only when that output is `'true'`. `!cancelled()` keeps it running on `schedule` and `workflow_dispatch`, where `closure-scope` is skipped.
- **The pathspecs are measured, not guessed.** `closure.py record` was run over a real run of the lane (throwaway branch `handoff/r9-nightly-ha-measure`, run 37764931838). Both images opened the same 127 repository files, 37 of them outside `custom_components/`: `tests/nightly_ha.py`, `tests/ha_contract.py`, `tests/harness.py`, `tests/golden/config_flow.json` and 33 files under `tests/hastub/`. The pathspecs are those paths, plus `tests/requirements-nightly-ha.txt`, which the job installs.
- **The package itself is not a trigger.** Catching a product change late in real Home Assistant is this lane's charter, and running it on every product pull request would put a registry outage or a Home Assistant release on all of them. `tests/ha_floor.py` is not a trigger either: the PR gate already checks its snapshot offline.
- **`tests/entities.py` pins three things.**
  - REACH: `nightly-ha`'s `if:` is evaluated over five events and three values of the output. It runs on schedule, on dispatch, and on a pull request with `nightly_ha == 'true'`, and on nothing else.
  - THE OUTPUT: it is declared from the `decide` step.
  - COVERAGE: every repository file outside the package that `_stage` opens is matched by the pathspecs. This is re-measured on each gate run with an audit hook around a real `_stage`.
- **`nightly-ha` declares `HPO_JOB_GRADES: nothing`.** Once a pull request can reach the job, `codeowners_gap.py` sees it running `tests/nightly_ha.py` and `tests/ha_floor.py` from the pull request's own copy, and refuses that for a grading job: `prepr.sh` printed `RESULT uncovered_files=2 ... REFUSED` at `1c072bed`. The job is unrequired, and on a pull request its verdict is about that pull request's own driver, so it grades nothing. `codeowners_gap.py --check` now tags both files `NO-PR-JOB`.
- **The reporter's derivation** in `tests/entities.py` no longer counts a diff-gated pull-request admission as visibility. So `nightly-ha` stays in `nightly_status.REQUIRED_LANES`, and `nightly-status` still grades it on `main`.

This head does not touch any of the pathspecs, so on its own pull request run `closure-scope` should answer `nightly_ha=false` and `nightly-ha` should be skipped. That is the "does not fire" half of the proof. The next head adds a docstring line to `tests/nightly_ha.py` for the "fires" half.

## Head

`fb8d449f9a405a4aeba33fa8f835d1766813fce5`

## Mutation proof

Each mutant was applied at `4a7c846f` (the code, before the main merge) in a scratch worktree, then `PYTHONPATH=tests/hastub python3 tests/entities.py` was run (seat venv-ci). Unmutated, it prints `ALL 2212 ENTITY CHECKS PASSED`.

- N1: the `pull_request` clause deleted from `nightly-ha`'s `if:`. Exit code 1, `FAIL nightly-ha runs on schedule, on dispatch, and on a pull request whose diff touches its driver's reads, and on nothing else` [`('pull_request', 'true', False)`].
- N2: the flag condition deleted, so every pull request runs it. Exit code 1, 2 failing: the same reach check [`('pull_request', 'false', True), ('pull_request', '', True)`] and `FAIL the reporter watches exactly the lanes a pull request cannot see`.
- N3: `tests/ha_contract.py` deleted from the pathspecs. Exit code 1, `FAIL every file nightly-ha's driver stages from outside the package is a path whose change runs nightly-ha on the pull request`.
- N4: the `nightly_ha` output line deleted from `closure-scope`. Exit code 1, the reach check fails.
- N5: `_stage` made to copy `tests/layout.py` into the driver mount as well. Exit code 1, the coverage check fails.

## Null control

At `main`'s `tests.yml` (merge base `816547ef`), the new checks run with this branch's `tests/entities.py` (N0) exit 1 with 2 of 2212 failing:

- The reach check: `('pull_request', 'true', False)`.
- The coverage check: no pathspecs, and `_stage`'s reads uncovered, starting `tests/golden/config_flow.json`, `tests/ha_contract.py`, `tests/hastub/...`.

## Figures

- **Measured read set**: run 37764931838, jobs 113270143734 (stable) and 113270143203 (2025.2.0). Each printed the record between `MEASURED-READS-BEGIN` and `MEASURED-READS-END`, and both printed 127 paths, with identical sets. Paths outside `custom_components/` were counted with `grep -v '^custom_components/'`. These are CI's results, read through `gh api repos/tvofi/heatpump_optimizer/actions/jobs/<id>/logs`.
- **Gate scope**: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` reports `MODE: FULL` (`tests.yml` changes the gate), so CI runs the full suite. Locally, at `fb8d449f`: `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`, and `PYTHONPATH=tests/hastub python3 tests/entities.py` printed `ALL 2214 ENTITY CHECKS PASSED`.

## Red checks

none

## Forward-carry

none

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
