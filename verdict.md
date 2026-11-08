Fix review: blocked 5fca8c7042a0b1b11057b9694a55e9965a07bdf4 ci-red: both code-run gate jobs at this head concluded failure on the edit-run deferral and were never re-run, and gate-sweep is disabled, so GitHub's required gate stays red; no code change is owed, a re-run of the two gate jobs is the cure

bus-nonce: 9997cbd681337c7e692d381a7a4707d9

## Block

Round 5. This is the delta review the brief allows past three blocks with `--past-three`, and no re-cut is owed. On merit this head is `merge`. The range 17e891bf..5fca8c70 is a clean merge of main and nothing else, and every prior finding still holds (`## Evidence`). The verdict is blocked only because a required context is still red when the 60-minute wait ends. A red CI never carries (fix-review.md step 12).

- `merge_train.py classify 5fca8c7042a0b1b11057b9694a55e9965a07bdf4 --pr 3291` printed `RED 5fca8c7042a0b1b11057b9694a55e9965a07bdf4 pending: none red: gate` (rc 1) on all 13 reads from 19:00Z to 19:51:45Z (`ev/classify1.txt`, `ev/classify_log.txt`).
- The two red `gate` runs both concluded `failure`:
  - job 128826607391: code run 42501481491, attempt 4, 18:49:38Z to 18:50:21Z.
  - job 128826617125: code run 42501476955 (`workflow_dispatch`), attempt 2, 18:49:40Z to 18:50:24Z.
- Both logs read only `FAIL run(s) [42511845716] at this head are still being judged; their gate decides` and then exit 1 (`ev/gate-128826607391.log`, `ev/gate-128826617125.log`). This is gate.py's deferral, not a failed unit.
- Run 42511845716 is the edit run, started at 18:48:45Z by the body edit. Its `gate` (job 128827075024) concluded `success` with `PASS` at 18:52:09Z (`ev/gate-128827075024.log`).
- Every other required leg at this head concluded `success` or `skipped`. That includes `codeql / Analyze (python)` (128826648728 and 128826605921, both `success`), which cures round 4's block.
- The final read at 19:52Z (`ev/check-runs-final.tsv`, 94 runs on all pages) shows the same two gate failures and no other non-success run.
- Nothing will re-run the deferred gates by itself. `.github/workflows/gate-sweep.yml` is `disabled_manually` (updated 11:54:00Z), and its last run was 42479944954 at 12:22:30Z. GitHub's required-check evaluation counts both failed gate runs, which is why `platform_gate` keeps the head red (the PR's `mergeable_state` is `blocked`). Carry: R10-PARTLOAD-RESIDUE
- Cure: re-run the failed `gate` job in code runs 42501481491 and 42501476955. The edit run has concluded, so neither should defer again. Then classify again. If it prints GREEN at this unchanged head, every finding below stands as a `merge`, and no fixer round is owed. Carry: R10-PARTLOAD-RESIDUE

## Findings

- Partial pin on `_derated`'s tail (`wood_fuel.py:541`, `+ cops[len(partload):]`), carried unchanged from round 4. The code and test line at this head match 17e891bf. Carry: dismissed: equivalent in production, since every schedule is n_steps long by construction (optimizer.py:3599, 3081, 3103-3104, 3128-3130); only the test comment overstates the pin
- Partial pin on `_plan_partload`'s `finite_float(p, 0.0)` on the space draw, carried unchanged from round 4. Carry: dismissed: no traced production path publishes a non-finite draw (optimizer.py:4275 clip, coordinator.py:6490 rejects failed plans) and the mutant's outcome is the conservative one
- The body's `## Red checks` answers the round-4 reds at 17e891bf0, not this head's. This head's only reds are the two deferral `gate` failures above, which `## Red checks` does not name. They are not a code defect. Under fix-review.md step 11 they are a gate red with no cheaper detector (the deferral happens at CI time). The orchestrator should add one line naming them when re-running the jobs, or the re-run will clear them. Carry: R10-PARTLOAD-RESIDUE

## Friction

- With `gate-sweep.yml` disabled, a body edit on any PR at a code head starts an edit run. The code-run gate re-runs then defer to that edit run and stay red after it passes. This cost this head a full review round: the code is unchanged, the head's units are all green, and the head is red. Carry: dismissed: the sweep was disabled by hand and re-enabling it is the orchestrator's call; R10-HOTFIX-TRAIN-DEFER-WAIT and R10-RCA-CODESCAN-WAIT hold the class

## Evidence

- RESULT round 5: a delta review of 17e891bf00140d79e166d95901391294002b513c..5fca8c7042a0b1b11057b9694a55e9965a07bdf4. Measured from detached worktrees at 5fca8c7042a0b1b11057b9694a55e9965a07bdf4 (`ev/HEAD.txt`). The head was still 5fca8c7042a0b1b11057b9694a55e9965a07bdf4 on `refs/pull/3291/head` and on the branch at 19:52Z (`ev/head-final.txt`). The roles diff (`git diff <mb>...origin/main -- dev/governance/roles/`) is empty.
- RESULT the range is main's merge and nothing else:
  - First-parent log: one commit, 5fca8c704 `ci: merge main` (author `github-actions[bot]`), with parents 17e891bf0 and 16f3d9cc3 (`ev/range-firstparent.txt`).
  - `git merge-tree --write-tree 17e891bf 16f3d9cc` gives tree 0e5b9d05b3a8260a1dddf4c570dca6b5a90668cf. That is byte-identical to the head's tree, so the merge commit adds no hand resolution.
  - The ledger driver resolved `tests/structure_budgets.json` (`class_excess_loc: 17560 + both deltas = 17557`) and `tests/closures.json` (`inert_reads` set merge) (`ev/merge-tree.txt`).
  - `git diff 17e891bf 5fca8c70` touches 85 files, the same set main's own `git diff 73365699 16f3d9cc` touches. Each of the 82 files the branch does not touch has a patch-id identical to main's (`ev/range-vs-main.txt`). The 3 the branch also touches (`tests/closures.json`, `tests/features.py`, `tests/structure_budgets.json`) are the driver-resolved and clean-merged files above. No stray change reaches the production package or tests.
- RESULT the branch's own patch is unchanged in substance:
  - The three-dot patch at the new head (16f3d9cc..5fca8c70) and at the old head (73365699..17e891bf) touch the same 10 files (`ev/patch-old.diff`, `ev/patch-new.diff`).
  - Their +/- lines differ only in `tests/structure_budgets.json` (`ev/patch-interdiff.txt`). There, `class_excess_loc` is now 17558 -> 17557, against 17560 -> 17559 before: the same -1 on main's newer baseline. The `recorded_at` line no longer moves. `max_class_loc` 7933 -> 7932 is unchanged.
  - `tools/audit/seat/review_carry.py 17e891bf 5fca8c70` prints `review_carry: CARRY` (0 of 1 branch-only commits is a non-merge) (`ev/review_carry.txt`). The CARRY applies to the patch only. Round 4's verdict was blocked, so no merge verdict carries.
- RESULT merges cleanly with current main: `git merge-tree --write-tree origin/main 5fca8c70` exits 0 at origin/main 996ded2a6dc52816bd4c7dd873c048d85fc6adad, tree 317504cc (`ev/merge-tree.txt`).
- RESULT cheap checks re-run at this head (`ev/checks-summary.txt`):
  - `tests/structure.py` prints `STRUCTURE RATCHET PASSED` (`ev/structure.txt`).
  - `tools/audit/archscore/score.py --diff 16f3d9cc HEAD` prints `Architecture score: dS +0.0000 NULL`, rc 0 (`ev/archscore_diff.txt`).
  - `tests/wood_advisor.py` prints `ALL 25 wood-advisor checks PASSED` (`ev/wood_advisor.txt`).
  - `tests/features.py` prints `ALL 4978 FEATURE CHECKS PASSED` (`ev/features.txt`).
  - The earlier rc=1 lines in `ev/checks-summary.txt` for wood_advisor, features and entities are my first attempt. It ran without `PYTHONPATH=tests/hastub` and died on `ModuleNotFoundError: homeassistant`, an error in my setup, not the code. All three were re-run with the stub that `tests/run.sh:101` sets.
- RESULT `tests/entities.py` ran plainly (no `BASH_ENV` or `PREPR_SKIP_CLOSURES` workaround, only `PYTHONPATH=tests/hastub` as the suite sets it) and ran clean: `ALL 2668 ENTITY CHECKS PASSED`, rc 0 (`ev/entities.txt`).
- RESULT mutants re-taken at this head, in a second worktree that was restored afterwards and whose `git status` was clean (`ev/mutants.txt`, `ev/features_mutA.txt`):
  - Null control: a no-op comment in `wood_fuel.py` leaves 25/25 passing.
  - Mutant C (`_derated` drops the factor, `c * f` -> `c`) fails 3 `wood_advisor` checks, rc 1.
  - Mutant A (coordinator drops `partload_at=partload_factor`, `coordinator.py:8313`) passes `wood_advisor` but fails `features.py`: `1 of 4978 FEATURE CHECKS FAILED`. The failing check is "the published wood advisor prices a max-power step's pump heat at the derated COP".
  - Both match round 4's kills. The other round-4 mutants were not re-taken: the production patch is identical.
- RESULT the review packet (`ev/review-packet.md`) shows `Refusals: none` and `CARRY-AUDIT: 5 finding item(s): 5 routed, 0 unrouted`, with `FIGURES: 5 resolved, 0 not verified, 0 refused`. Its gate digest reads green, but only because it shows the newest run per name (edit gate 128827075024). The ruleset reads both code gates, which is why classify stays RED.
- RESULT `VERSION`, `RELEASE_NOTES.md` and `custom_components/heatpump_optimizer/manifest.json` are untouched in the three-dot range.
- RESULT the body's `## Head` figures re-derive: the parents, the patch-id identity apart from the budget lines, the `class_excess_loc` 17558 -> 17557 against 17560 -> 17559, and the clean merge-tree at 996ded2a6 all match my reads above. The CPU and wood figures are round 4's and were not re-taken. They read code this range does not move.
- RESULT CI at this head, all 94 check runs (`ev/check-runs.tsv` at 19:00Z, `ev/check-runs-final.tsv` at 19:52Z): the only non-success, non-skipped runs are the two `gate` failures in `## Block`. Mutation, coverage, closures, arch-score, budget-raise-gate, pr-contract and all three CodeQL analyses concluded `success`.
