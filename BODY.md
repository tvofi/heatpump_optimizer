HOTFIX for main's red Nightly `slow` lane ("3 of 33 ROLLING CHECKS FAILED", dispatch runs 40835853528 and 40948493872). **The harness is at fault, not production.** #2919 (`994b3dff`, #2508) made the house heat-loss learner freeze when no indoor temperature entity is configured (`learner_room_unread` returns `not_configured:indoor_temp_entity`). That is the intended behaviour: with no sensor, the learner would otherwise replay the 21.0 °C default as if it had been read. `tests/rolling.py`'s learner arm builds its coordinator from `profiles.house()`, which configures no indoor entity. So since #2919 the learner froze on every step and the three self-learning checks measured the freeze. The harness feeds the learner the plant's real room temperature, so it now declares the sensor that reading stands for. The samples check also prints the freeze reason, so a harness that stops driving the learner says why rather than only "0 samples".

The same rule found one more silent seam: the learner arm of `dev/audit/harnesses/scale_writer_seams.py` has measured the same freeze since #2919. It gets the same one-line fix.

No production code changes. `custom_components/` is untouched.

## Head

`44b41b0327ca6156bfe96cf0d1f907754c31ce6b`, on base `e5ddba1fad5e6eccfeceaeaaa249bc459963405b` (origin/main at handoff). The `tests/rolling.py` runs below were taken at `2244d6d0e59e27ac811925c85cfb096e1c8c6e87`, this branch's first commit. The second commit touches only `dev/audit/harnesses/scale_writer_seams.py`, which `tests/rolling.py` does not import.

## Mutation proof

- `tests/rolling.py`: in a detached worktree at `2244d6d`, revert the fix's production line `FakeEntry(data={**cfg, CONF_INDOOR_TEMP_ENTITY: "sensor.indoor"})` to `FakeEntry(data=cfg)`, then run `PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 tests/rolling.py` (Python 3.13, `tests/requirements-ci.txt`). Result: `3 of 33 ROLLING CHECKS FAILED`, exit 1. The failing checks:
  - `the learner takes samples  [0 samples over three days, freeze 'not_configured:indoor_temp_entity']`
  - `the learned correction moves towards the real error  [scale went 1.000 -> 1.000, truth 1.35]`
  - `learning reduces the comfort breach it exists to fix  [10.37 -> 10.37 degree-hours]`

  Restored at the head: `ALL 33 ROLLING CHECKS PASSED`, exit 0.
- `scale_writer_seams.py`: the same run without the `indoor_temp_entity` key (at `2244d6d`) prints `learner_empty_scale=1.8`, `learner_admitted_scale=1.8` and `learner_empty_equals_accept=true`. With the key (head) it prints `1.8032`, `1.8032` and `false`.

## Null control

The bisect runs the same `tests/rolling.py` command at four commits:

| commit | what it is | result |
|---|---|---|
| `ee4893758846` | last green schedule `slow` job (run 40806276912, job 123225871060) | `ok` on all three learner checks |
| `0b17333c2fec` | #2919's first parent | `ok` on all three learner checks |
| `994b3dff5995` | #2919's merge | `3 of 33 ROLLING CHECKS FAILED`, exit 1 (the same three checks) |
| `e5ddba1fad5e` | main | `3 of 33 ROLLING CHECKS FAILED` (the same three checks, as CI printed) |

So the red begins exactly at #2919, and nothing on main after #2919 changes it. `scale_writer_seams.py` at `0b17333` and at the head prints identical output once the `RESULT seam line=` rows are excluded (they shift by the line numbers of the later coordinator edits): `diff <(grep -v "RESULT seam line" a) <(grep -v "RESULT seam line" b) && echo IDENTICAL` printed IDENTICAL.

## Figures

- Bisect and mutant: `PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 tests/rolling.py` at each commit above. The summary line and the three learner checks are quoted above; degree-hours are solver/BLAS-dependent by the script's own note, so a CI run's figure may differ (CI printed 10.39 for the same check).
- Class rule, enumerating every driver of the learner: `grep -rln "_async_learn_house_heat_loss" tests dev/audit tools`, with `grep -c "indoor_temp_entity\|CONF_INDOOR_TEMP_ENTITY"` per file. Dispositions:
  - Gate-run drivers `tests/features.py`, `tests/dst_checks.py` and `tests/boost_drift_replay.py` configure the entity where they expect learning, and they were green on main's push gate. Already guarded.
  - `tests/rolling.py` is closed in this diff.
  - `dev/audit/harnesses/scale_writer_seams.py` (a real `FakeEntry`, no entity) is closed in this diff.
  - `dev/audit/harnesses/r10_heat_meter.py` stubs `_async_learn_house_heat_loss` to `return True` on a stub class (no coordinator, no config), so the freeze cannot reach it. Unaffected.
  - `dev/audit/harnesses/r10_vent_bias_window.py` and `r10_night_folds_learners.py` reference the entity. Already guarded.
  - The rest are recorded round evidence (`dev/audit/rounds/**`), mutation-ledger records, the archscore corpus and prose. A measurement record stays as written (fixer step 10).
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 1 script(s) run`, and `RUN tests/harness_headers.py` is green. The `run_always` scripts are green: `tests/env_drift.py --claims-only`, `tests/closure.py selftest`, `tests/layout.py` and `tests/harness_headers.py`.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`. `python3 tools/pr/ci_predict.py --base origin/main` predicts no closures, fast, wave-script or instrument red.

## Red checks

- `tests / nightly-status` (the Nightly `slow` lane, "Closed-loop simulation"). It graded main red from #2919 on. That is the defect this PR fixes, and it is not a red this branch caused.

  Root-cause answer (`defect-root-cause.md`): a cheaper detector exists. `tests/rolling.py` is in `tests/closure.py`'s `SLOW_GATED` set, so no pull request ever runs it, while its learner checks are exactly the property #2919 changed. The cheaper detector is to run just the self-learning section, the two 3-day `run_rolling(..., learn=True)` arms (a fraction of the about 6 minutes the whole script took here), on any PR whose diff reaches the learner's freeze path. A second, cheaper and standing detector already lands here: the samples check now prints the freeze reason, so the next harness that stops driving the learner reads as a named freeze, not a silent zero.

  The scoping change is left to `root-cause.md`'s seat, not this hotfix. It needs `rolling.py` split, and a closure recording that `closure.py` notes costs over an hour.

- Owed by the orchestrator after merge: `gh workflow run nightly.yml --ref main`, with its run id recorded against this PR. Only that run discharges `tests / nightly-status`.

## Forward-carry

none

## Friction

none
