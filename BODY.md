Refs #3885

This PR leaves #3885 open.

## Summary

R11-CI-CASE-SELECT P2 as the owner directed on 2026-11-25 ("Do the sharding", then "make it dynamic"): `tests / fast (3.14)` becomes one job per shard. The prelude sizes and packs the shards on every run. No file is edited when a script grows or a new one lands.

- **Planner** (`tools/ci/shards.py`, new; a gate file under `tools/ci/`).
  - Its script set is every script that a `run`/`run_always` line of `tests/run.sh` names, read from run.sh itself.
  - Seconds come from `tests/closures.json` `recorded` and from the span sums of #3896's `tests/case_closures.json`. Both are read with `git show <base>:` (the PR base sha, a push's `before`), so a rerun of the same event draws the same plan.
  - A recording with `rc != 0`, a non-positive or NaN figure, or one of the two stub-timed differential guards (#934) is not used as a timing. Those scripts, and any script with no timing, are priced at the upper quartile of the timings that remain.
  - Shard count is `ceil(load / 720 s)`, clamped to [2, 4]. The load is the scripts `closure.select` picks from the prelude's changed list, plus the `run_always` lines. It is every script on a full run.
  - Packing is `closure.lane_plan` (longest group first, into the least-loaded shard), reused rather than re-implemented. Each `closure.lane_edges` group stays in one shard: the plan payload's writer `plan_view.py` and its readers.
  - The plan assigns every script, not only the selected ones (unselected scripts weigh 0). Each shard runs the scripts both assigned to it and in its own run.sh scope. So the shards together run exactly what one unsharded run would, and a wrong estimate can only unbalance the shards.
- **Prelude** (`prelude.outputs(fast=)`, `main`). The prelude emits `fast_shards` (a JSON list of `K/N`) and `fast_plan`. Any exception in the planner leaves both empty, and an empty output is the old unsharded job.
- **`tests.yml` fast job.**
  - `matrix.shard: fromJSON(inputs.fast_shards || '[""]')`. Each job is named `fast (3.14, K/N)`, or `fast (3.14)` when unsharded.
  - `fail-fast: false`, so one shard's red does not hide another's.
  - `HPO_FAST_SHARD` and `HPO_FAST_PLAN` are passed to run.sh.
  - The drift-baseline key, restore, warm and save steps run only in the shard that owns `tests/env_drift.py`, read off the same plan.
  - The `ci-metrics-fast` row and artifact come from shard 1 (or the unsharded job) only. Every shard takes the same scope decision, and two artifacts with one name in one run would collide.
- **`tests/run.sh`.** The script asks `shards.py route` for the plan, which refuses anything that is not a partition over `1..N` or whose shard is not of it. A refusal exits 1 before any script runs (fail closed). `run_always` skips another shard's script by name (`SKIP: <script> (fast shard j/N runs it)`), so the accounting's TEST NEVER RAN check holds per shard. A script the plan does not name runs in shard 1.
- **`tools/ci/gate.py`.**
  - `fast_names` expands the required `tests / fast (3.14)` into every `tests / fast (3.14, K/N)` the prelude planned. The list comes through `FAST_SHARDS` in ci.yml's gate step.
  - A missing, skipped or red shard is red. The unsharded job does not stand in for planned shards. A shard list that is not exactly `1/N..N/N` is red.
  - `status()` reads the shards in place of the one job.
  - `gate` is still the only required check, and it still aggregates through `needs: [prelude, pr-contract]`.
- **`governance.yml` instrument-self-tests** gains `ci-shards`, which runs `tools/ci/shards.py --self-test`. It has no `tools/ci/selftest_closures.json` entry yet: the table reads stale, so pull requests run every step, and the next main push measures the step and `selftest-absorb` commits its entry (`selftest_scope.py` THE BOT'S HALF). `tests/closures.json` records the three new harnesses as `harness_headers.py` inert reads (`ci_predict.py --apply-inert`).
- **`tests/closure.py` `PRODUCERS`** gains `tests/setup_qa_render.mjs` -> `plan_view.py`. run.sh's lane_e2e runs it on the payload `plan_view.py` writes. It is not selectable (`NOT_A_TEST`), so only `lane_edges` reads the entry.

Bootstrap. On a pull request the prelude and the gate run the base's `tools/ci/*.py`. This PR's own runs therefore get no plan, run the one unsharded `fast (3.14)`, and are judged by the base gate as before. Sharding first runs on the push to main that merges this, where both programs are the head's.

Waits. The change adds no runner-held wait: no poll, sleep, retry or backoff. The plan step reads two files with `git show` and exits, the shards start together with no wait-for-sibling step, and `gate` reads them through `needs:`.

Code-owned paths: `.github/workflows/ci.yml` and `tests.yml`. The owner's approving review is required (under mandate 6893738184). No budget moved, so `budget-raise-gate` is not involved.

## Head

`23eb36c87a583355843337dc9dee5b4cf18527d7`, on `origin/handoff/r11-ci-case-select` 58c73880 merged with `origin/main` 91f6e91b (merge ea95bdd3). Measured 2026-11-25T22:43Z.

## Mutation proof

`python3 dev/audit/harnesses/r11_fast_shards_mutants.py <detached worktree at HEAD>`: each mutant is applied in place, the self-test closing over it is run, and the file is restored. All 8 KILLED:
- gate, fast name not expanded (`.extend(fast if ...)` to `.append(n)`): `FAIL null: every fast shard green passes`, `FAIL a missing fast shard is red`, `FAIL a skipped fast shard is red`, `FAIL the unsharded job does not stand in for claimed shards`.
- gate, malformed shard list not refused: `FAIL a shard list that is not 1..N (['1/3', '3/3']) is red` and 3 more.
- shards.check, empty shard accepted: `FAIL route refuses an empty shard`.
- shards.route, shard of another count accepted: `FAIL route refuses a shard of another count`.
- shards.timings keeps a failed run's seconds: `FAIL timings drop a failed run, a stub, a NaN and a zero; ...`.
- shards.priced drops an untimed script: `FAIL an untimed script is priced at the upper quartile, never dropped`.
- closure.PRODUCERS without the setup render: `FAIL every payload reader shares the writer's shard: got {2, 4}, want {4}`.
- prelude, planner outputs not emitted: `FAIL P2: the prelude emits the planner's two outputs`.

Failing first: the gate's 9 new checks read FAIL before `fast_names` existed (`gate self-test: 130 checks, 9 failed`). The payload-reader check read FAIL before the PRODUCERS entry. Baseline: gate 132/0, shards 21/0, prelude 147/0.

## Null control

- run.sh routing, driven as `r11_fast_shards_random.sh` drives it (CI's env, one shard per run). A 2-shard plan run as `HPO_FAST_SHARD=1/2` ran its 4 scripts, skipped 30 by name, printed `SHARD 1/2: 4 TEST SCRIPT(S) PASSED HERE`, and exited 0. The same plan run as `3/2` printed `shards: REFUSE shard 3/2 does not belong to a plan of 2 shard(s)` and `SHARD: REFUSED`, and exited 1 with no script run.
- Shard balance against a random assignment (Figures).
- Split assessment against the same split with `needs` dropped (Figures).

## Figures

Prices are CI medians over the closing wall-clock tables of the 14 FULL `tests / fast (3.14)` push runs 45089960324 45099631369 45116277653 45328633907 45328796343 45533729403 45549222867 45557285296 45565356610 45581667044 45596992195 45615385751 45632212603 45666185535. Logs were read with `dev/audit/harnesses/ci_script_seconds.py`'s job_log, one file per run, and fed to `python3 dev/audit/harnesses/r11_fast_shards_balance.py LOGDIR` at HEAD:
- CALIBRATION: the unsharded lane model reads 2736 s against the logs' median TOTAL of 2360 s (ratio 1.159). The model overstates the wall, so the shard figures below are upper bounds.
- PLAN: 4 shards, modelled walls 1/4=600 s, 2/4=1080 s, 3/4=712 s, 4/4=588 s. Makespan 1080 s (18.0 min), against the measured unsharded median TOTAL of 2360 s (39.3 min).
- NULL: random assignment to 4 shards over 200 draws (seed 0) gives a median makespan of 1409 s and a best of 1020 s.
- FLOOR: `tests/features.py` takes 1018 s. The plan's makespan is the floor plus the 62 s of other units-lane scripts sharing its shard. The 12-15 min goal cannot be met at script level while features.py alone takes 17 min.
- Shard count from the planner at origin/main, full: `["1/4",...,"4/4"]` (`python3 -I tools/ci/shards.py plan --ref origin/main`). With `--changed` naming only `tests/doc_claims.py` it is 3 shards: that selection pulls `tests/entities.py` (1388 s recorded) and the run_always lines.
- Plan step wall time: 0.43-0.76 s over 6 runs of `/usr/bin/time -p python3 -I tools/ci/shards.py plan --ref origin/main [--changed FILE]` on the seat host.
- Script split table, from `r11_fast_shards_balance.py`'s SPLIT lines (recorded span seconds) and the CI medians above:

  | script | CI median | over 10 min / dominates | sound split? | larger half, sound | null (needs dropped) | saving |
  |---|---|---|---|---|---|---|
  | `tests/features.py` | 1018 s | yes / yes (the floor) | no: each half must re-run its `needs` closure (median 37.5 needs/span, `@random` chains every drawing span) | 947 of 1022 s = 0.926 | 0.508 | about 7%; not split |
  | `tests/entities.py` | 600 s | at 10 min / no (shard 1/4 alone, under features' shard) | no: one span, `#558 D6 numeric schedule companion`, holds 1094 of 1388 recorded s | 1373 of 1388 s = 0.989 | 0.867 | about 1%; not split |
  | `tests/env_drift.py` | 380 s | no / no | not measured: one differential capture, not a span script | - | - | - |
  | `tests/stress.py` | 302 s | no / no | out of scope by the design (its memory pass is one span) | - | - | - |

  Follow-up: features.py is the critical path. Splitting it soundly needs fewer `needs` edges (the `@random` chain), not a different splitter. Carry: #3885.
- Independence: unmeasured, running. `bash dev/audit/harnesses/r11_fast_shards_random.sh 1 OUT 3` (seed 1, 3 random shards, PRODUCERS groups drawn whole) is running on the seat host at this head; its per-shard rc and the RAN/TWICE lines replace this line on this body ref when it ends.
- Architecture score: `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD`: `Architecture score: dS +0.0000 NULL` (no scored production file changed)
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`; `PYTHONPATH=tests/hastub python3 tests/doc_claims.py`: `ALL 443 checks PASSED`; `pairnote_check.py --repo . --ref HEAD`: `PAIRNOTE OK HEAD: 184 of 561 pairs, 122 files`.

Gate scope: `closure.py select` reads `MODE: FULL` for this diff (`tests/run.sh`, `tests/closure.py`, `tools/ci/`, `tests.yml` and `ci.yml` are gate files). The randomized run above runs every script once, across its three shards, so it is the local full gate. CI runs the rest.

## Red checks

none

## Forward-carry

- features.py is the fast lane's floor at 1018 s. A span split saves about 7% while each span's `needs` closure stays as recorded; the lever is the `needs` density (the `@random` chain, the dynamic module moves), measured by `r11_fast_shards_balance.py`'s SPLIT lines against their no-needs null. Carry: #3885

## Friction

none
