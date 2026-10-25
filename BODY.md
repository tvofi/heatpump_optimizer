R10-LEARNER-ETA (G-ID-4, STUDY R10-IDENT Q3). Part of #2260: the roster's
`fixes` is empty for this group, so it does not close here; the orchestrator
verifies it after the merge.

The learning view publishes `learner_progress`, one entry per thermal learner
(`house`, `lower`, `solar`, `gains`) with `phase` (off, waiting, counting,
settling), `progress`, `waiting_for`, `samples`, `samples_needed` and
`eta_days`. `eta_days` is set only while counting: it is the time until the
learner's own gate predicate opens at the measured sample rate, never a time
to convergence, which the study found weeks early. The rule lives in the pure
module `learner_progress.py`; `coordinator.learner_progress_view` is a
module-level adapter handed explicit values.

This round makes the field reach the card. The Health tab reads only
`ModelStatusSensor`'s attributes (`HEALTH_MODEL_SUFFIX = "_learning_model_status"`),
which dropped the field. The sensor now publishes the view's `learner_progress`
unchanged as its `learner_progress` attribute, in `_unrecorded_attributes`
beside `system_identification` because `progress` and `eta_days` change every
cycle; it is None when the view has none. `waiting_for` also gains `darker`:
the house, lower and gains folds take no sunlit interval (`is_sunlit_interval`,
#2223), so in the sun with nothing counted they wait for dark. The aperture
folds ahead of that gate and behind the ΔT gate only, so it waits on
`sunnier` or `colder`. Alternatives: keep the strict subset and say so in the
docstring. That lost because a learner the weather blocks would report itself
as not waiting.

No split: the wiring is one sensor attribute, so the card or sensor work
stays here. Only the card's rendering is R10-UX-HEALTH's.

## Head

`0c4dff1770e941dd0c9a033dc6b5c2c283d823e6` is the code head, measured throughout: PR head
`3b5ffde573c4557f8af68a4905f1ffe94bba7da8` plus this round's commits. Merge
base and origin/main tip `ab00437c94bd8d8ca7b47b69095c47535f3e645a`, which was
main's tip at 2026-10-25T06:44:00Z (`date -u`). `git merge --no-edit origin/main` printed
`Already up to date.` At 2026-10-25T06:48Z (`date -u`) main had moved to `21a1e04a7e838545f43a6f9a8545f4bb2bc0548f`. `git merge-tree --write-tree origin/main HEAD` reports no conflict, so the branch is not re-merged before the handoff (fixer.md step 6). Every figure below was taken in this pass, against `ab00437c9`.

## Mutation proof

Failing test first: `R10-LEARNER-ETA: the Health tab's source sensor publishes
learner_progress as the view has it`, run on the PR head's production files,
printed `FAIL ... pub [(..., None), (..., None)]` and `1 of 4383 FEATURE CHECKS
FAILED`, because the sensor attribute was absent at a counting and at a settling
state. It is green at the head.

Each mutant is one exact text replacement in a fresh detached worktree at
`7774f7e2d855e770c13562f117dd425a90622134` (this round's production commit),
driven by `PYTHONPATH=tests/hastub python3 tests/features.py`. Every mutant
exited 1. The null mutant exited 0 with `ALL 4384 FEATURE CHECKS PASSED`.

| mutant | production text replaced | red checks |
|---|---|---|
| MS | the sensor's `"learner_progress": data.get("learner_progress"),` deleted | `R10-LEARNER-ETA: the Health tab's source sensor publishes learner_progress as the view has it` |
| MU | `"learner_progress"` dropped from `_unrecorded_attributes` | the same check |
| MD | `darker = "darker" if is_sunlit_interval(...) else None` -> `darker = None` | `R10-LEARNER-ETA: in the sun the dark-gated learners wait for dark, and the aperture counts` |
| MH | `house_wait = house_cold or darker` -> `house_wait = house_cold` | the same check |
| ML | the lower learner's `colder(...) or darker` -> `colder(...)` | the same check |
| MA | `solar_wait = ... else house_cold` -> `else house_wait` | `... no settling learner carries a day count, on any weather or rate`; `... in the sun the dark-gated learners wait for dark, and the aperture counts`; `... the ΔT and irradiance edges admit a sample, and the gate count settles` |
| M1 | `if needed is not None and needed > n:` -> `if needed is not None:` | `... no settling learner carries a day count, on any weather or rate`; `... settling progress is the learner's own EWMA walk, never a time`; `... off when disabled or unmeasurable; zero evidence counts with no ETA`; `... the ΔT and irradiance edges admit a sample, and the gate count settles`; `... the Health tab's source sensor publishes learner_progress as the view has it` |
| NULL | `MIN_RATE_WINDOW_DAYS = 1.0` gains a trailing comment | none, exit 0 |

## Unpinned sites

- `custom_components/heatpump_optimizer/coordinator.py:1435 CMP_BOUND` (`learner_progress_view`), the `solar_wait` line (`irradiance < SOLAR_APERTURE_MIN_IRRADIANCE`), which this round edited to end in `house_cold`: pinned by `mutation-autofix`. Its stale killed-by pin for the old text is deleted by hand, because `ci_predict.py` named it a STALE PIN. Locally, `tests/mutation_table.py --pin-killed --base origin/main --scope changed` printed `MUTATION TABLE INCONCLUSIVE`, because the two environment-red `tests/entities.py` checks (`## Figures`) make its baseline red here. The mutant itself (`<` -> `<=`), run as in `## Mutation proof`, exited 1 on `R10-LEARNER-ETA: the ΔT and irradiance edges admit a sample, and the gate count settles`.

## Null control

- The new check's null arm: the same coordinator's payload with
  `learner_progress` removed publishes `learner_progress: None`, and every
  other attribute is equal to the full payload's. So the card falls back as
  before, and nothing else on the sensor moves.
- The dark-gate check's null arm: the same coordinator at zero irradiance has
  no learner waiting on `darker`, and the house is counting.
- The null mutant in the table above.
- The finder's harness reads flat at both ends (`## Figures`). It scores
  estimators the tree never shipped, so flat is the expected reading, and the
  companion carries the measurement.

## Figures

- Companion harness, `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_learner_eta.py --study "$X/dev/audit/rounds/round10/study-ident"`
  (`$X` = `git archive 4f2d513c9 dev/audit/rounds/round10/study-ident`
  extracted; harness sha1 `3c60bc36a4aa21adef7245b0ced2f6192ece22e8`, the
  head's file run from each tree's root), all seven plants. At the base
  `ab00437c9` it printed `RESULT field=absent`. At the PR head `3b5ffde57` and at
  this round's `7774f7e2d` it printed the same lines: `field=present`,
  `eta_on_settling=0`, `gate_err.p10=-0.0 p50=+0.1 p90=+0.1 n=8`,
  `settle_err.p10=-36.2 p50=-35.8 p90=-35.8 n=7`, `phase_counting=22`,
  `phase_settling=1147`, `phase_waiting=7`. The dark gate moves no
  checkpoint: each daily checkpoint that reads a blocked gate also has a rate.
  `eta_on_settling` is a regression detector: on unmutated code it cannot be
  non-zero, because `eta` is set only inside `needed > n`.
- Finder's harness, `$X/dev/audit/rounds/round10/study-ident/eta_rolling.py`
  (sha1 `ea7de4d76e3a698650b4b2be9608efa8f918b48a`, `ident_rolling.py` sha1
  `3755ee80dd71a8d05e2ea2a4c6b317c63fa4ed79`), all plants, at `ab00437c9` and
  `7774f7e2d`, 99 lines each:
  `diff <(grep -v "wall_s\|load1\|thread_factor" base.txt) <(grep -v "wall_s\|load1\|thread_factor" head.txt) && echo IDENTICAL_EXCEPT_TIMING`
  printed `IDENTICAL_EXCEPT_TIMING`.
- Step 8, the class: a learning-view field that no entity the card reads
  carries. Rule (repository root): parse `LearningView`'s annotated keys from
  `payload.py`, and list each key that appears as no `"<key>"` string literal in
  `sensor.py`, `binary_sensor.py`, `button.py`, `climate.py` or `switch.py`.
  At `ab00437c9` it returns 13 of 37 keys. At `3b5ffde57` it returns 14 of 38,
  and the extra one is `learner_progress`, the block. At `7774f7e2d` it returns
  13 of 38. Dispositions for the 13:
  `house_heat_loss_samples`, `lower_floor_loss_samples` and
  `lower_floor_loss_learned` reach `ModelStatusSensor` through
  `_learner_row`'s `f"{stem}_samples"` and `f"{stem}_learned"`, which a literal
  rule cannot see (already carried). `buffer_cooling_rate`,
  `buffer_cooling_samples`, `buffer_cooling_rate_learned`,
  `defrost_measured_samples`, `defrost_flag_configured`,
  `defrost_store_migrated`, `immersion_active`, `immersion_evidence`,
  `heat_curve` and `snapshots` are read neither by the card (`grep -c` in
  `heatpump-optimizer-card.js`: 0 each) nor by an entity. They reach the
  diagnostics download, whose `"learning"` entry copies every `LearningView`
  key (`diagnostics.py`, `LearningView.__annotations__`). They are
  diagnostics-only by design, not a card contract, so this is not a finding.
- `PYTHONPATH=tests/hastub python3 tests/features.py` at `7774f7e2d`:
  `ALL 4384 FEATURE CHECKS PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: `2 of 2440 ENTITY CHECKS
  FAILED` at `7774f7e2d` and at `ab00437c9`, and the non-self-test FAIL lines are
  the same two: `gate-sweep.yml: on CI's completion, ...` and
  `graders-head-copy's delivery_status step is red only when ...`. They are this
  environment's: `tests / fast (3.14)` and `tests / graders-head-copy` are green
  on the PR head. The `_PUBLISHED_ATTRS` pin for `ModelStatusSensor` now
  lists `learner_progress`.
- Scoped gate, `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) PYTHONPATH=tests/hastub ./tests/run.sh`
  at `7774f7e2d`: `MODE: SCOPED -- 28 script(s) run, 5 scoped out.` Two
  scripts were red: `tests/entities.py` (the two checks above) and
  `tests/env_drift.py --all`, because `5 COMMITTED FIXTURE(S) ARE STALE`. The
  five `coord_*` fixtures lacked the sensor's new attribute. The next commit
  grafts it in. Then
  `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all ab00437c9...`
  printed `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE: 56`, with
  each `coord_*` reading `CLAIMED ...: 2 leaves moved`.
  `--claims-only` printed `claims hygiene: origin/main ok`. Each graft equals that fixture's
  `data.learner_progress` (asserted while grafting), and no other leaf was
  re-recorded. `claims-for:` is unchanged, and `card_claimed_drift.txt` is
  untouched.
- `PYTHONPATH=tests/hastub python3 tests/structure.py` at `7774f7e2d`:
  `STRUCTURE RATCHET PASSED`. No `*budgets*.json` differs from origin/main.
- `python3 tools/audit/archscore/score.py --diff origin/main`: `Architecture
  score: dS +0.0006 IMPROVES` (`coord_footprint 2463 -> 2462`).
- `node tools/policy/brief_lint.mjs` with the restated carry: `TOTAL: 0
  error(s) across 48 file(s)`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` at `0c4dff177`: `CI PREDICT: no closures, fast, wave-script or instrument red predicted against ab00437c94bd`, plus the one unpinned-site warning above.
- `bash tools/pr/prepr.sh <body>` at `0c4dff177`: `PRE-PR: 0c4dff1770e941dd0c9a033dc6b5c2c283d823e6 000000000000000000000000000`, with the one unpinned-site warning; `python3 tools/audit/carry_audit.py check --body <body>`: `CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)`.
- `VERSION`, the manifest version and `RELEASE_NOTES.md`: no diff against
  origin/main.

## Red checks

none: every check on the PR head `3b5ffde57` concluded success or was skipped,
including `gate`, `pr-contract`, `tests / fast (3.14)`, `tests / mutation` and
`tests / closures`. This round's local reds were repaired before the
handoff (`## Figures`): the stale fixtures and the stale mutation pin that
`ci_predict.py` named.

## Forward-carry

- R10-UX-HEALTH renders `learner_progress`. The carry is restated in place in
  `dev/programme/rosters/wave-r10-groups.json` (group R10-UX-HEALTH, the
  `From R10-LEARNER-ETA` entry). It names the entity attribute the card reads
  (`learner_progress` on the model status sensor, the `HEALTH_MODEL_SUFFIX`
  entity) and adds `darker` to the `waiting_for` values. The precondition and
  control stay unchanged. Carry: R10-UX-HEALTH

## Friction

none
