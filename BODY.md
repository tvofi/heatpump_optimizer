Capped cancellation of superseded `main` push CI runs (#3885; owner ruling 2026-11-25). Leaves #3885 open.

A push to `main` whose `CI` run is graded in full now cancels the older `ci.yml` main push run still in progress, through the existing bounded arm `cancel_superseded.py main`. The arm cancels nothing when:

- the push is light (any prelude `scope` but `full`, an unreadable one included);
- the cancel would leave more than three consecutive main runs with no concluded verdict (`MAIN_ROW_MAX`, unchanged);
- a run it would cancel has a job queued for `pause_queued_min` minutes, the train's pause signal `ci_pause.queued_minutes` over `dev/audit/config/ci_priority.json` (GitHub is not granting runners), or that run's jobs or the setting cannot be read;
- the push's own run is not listed yet (polled `MAIN_POLLS` times, `MAIN_POLL_S` apart) or is not the newest main run (a newer push decides).

It runs from a new workflow, `.github/workflows/main-cancel.yml`, not from `ci.yml`. The brief named `ci.yml`, but its workflow-level `CI-main` group (CI-5) holds the newer push's run pending until the older one ends, so no job of `ci.yml` can cancel that run. The new job runs `tools/ci/prelude.py` on the push event and reads its `scope` line, so the light decision is the prelude's own `push_range` + `light`. It sits in no concurrency group, holds `actions: write` and `contents: read`, and always exits 0 because the cancel is an optimisation and never a gate. `tests/entities.py` pins its shape, with a null control. The file is classified into the two recorded closures that glob every workflow (`tests/entities.py`, `tests/harness_headers.py`). `ci.yml` is unchanged.

Measured basis, from the #3885 brief and not re-derived here because no enumerator is in the tree: over 26 main pushes, about 1800 job-minutes were spent after a newer push. The capped cancel saves about 740 job-minutes (about 13%) and keeps a verdict at least every 3 pushes. An uncapped cancel would leave 7 verdicts in 26 and a 23.6 h gap.

## Head

290ea4687caea338d997d38fa2f61dd944f73dad (branch fix/ci-3885-main-cancel, cut from origin/main 0e1eba2b4a)

## Mutation proof

`python3 dev/audit/harnesses/r11_main_cancel_mutants.py` (extended with seven #3885 mutants): M0 null-ok, mutants=18, survived=0. The #3885 mutants are M-scope (light push cancels), M-health (queued run cancelled), M-health-age, M-health-read (unreadable reads healthy), M-listed, M-newest-push and M-poll. All seven are killed, with 1 to 4 self-test checks failing each. The harness now symlinks `tools/audit` into each copy because the health read imports `ci_pause`.

## Null control

Self-test at the base with the new cases added and no production change: `python3 -I tools/pr/cancel_superseded.py --self-test` exits 1 with `TypeError: main_arm() got an unexpected keyword argument 'sleep'`. At the head it prints `87 checks, 0 failed`. Within the self-test, the null controls are: a queued job of 1 min still cancels, so a healthy run is not refused; by hand (no `--scope`) the health gate still holds; and the existing 76 checks are unchanged. The mutant harness's M0 is the unmutated copy (failed=0).

## Figures

- `python3 -I tools/pr/cancel_superseded.py --self-test` -- check count, 0 failed
- `python3 dev/audit/harnesses/r11_main_cancel_mutants.py` -- mutants, survived
- the 26-push basis above: describe-only, no enumerator in the tree

## Red checks

none

## Forward-carry

none

## Friction

none
