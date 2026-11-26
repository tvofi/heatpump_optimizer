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
- **`governance.yml` instrument-self-tests** gains `ci-shards`, which runs `tools/ci/shards.py --self-test`. Its `tools/ci/selftest_closures.json` entry is measured on Linux by `selftest_scope.py record --step ci-shards` in a plain scratch clone (4c267409). `selftest_scope.py grows` over the old and new tables reports `0 read(s) of the old table the new one drops`. `tests/closures.json` records the three new harnesses as `harness_headers.py` inert reads (`ci_predict.py --apply-inert`).
- **Readers of the fast job name (#3902 review, class-open).** The rule: every file under `tools/`, `tests/` and `.github/` whose text names the job (`fast (3.14`) is a reader. `shards.READERS` routes each of the 45 such files to one disposition, and `shards.py --self-test` greps the tree and refuses a file missing from it or listed there and no longer naming the job (it caught this PR's own new `sweep.py` comment). The name is read through one owner, `shards.FAST`, `is_fast` and `owed_fast`; `gate.FAST` and `prelude.UNITS` take it from there.
  - Fixed (`sharded`, 8 files):
    - `prelude.owed_needs`: the fast lane owes every `tests / fast (3.14, K/N)` of the one count the run lists, else the unsharded name. `judging()` and `requeued()` read it, and so do their callers `gate.busy`, `prelude.wait_sources` and `sweep.py`. A completed sharded run was read as not judging before the fix.
    - `gate.status`: it owes every shard of the listed count, so a listing missing one reads unread.
    - `sweep.code_red`: a red shard is the fast unit's red, so a STALE-PIN dispatch is not fired over it.
    - `probe_bridge.bridge`: a successful shard implies a reference over the scripts it ran.
    - `replan._ingest_check_runs`: the shards fold into one `fast (3.14)` row, running from the first shard's start to the last one's end and red when any shard is red. A commit missing a shard has no row; before the fix, a sharded main gave no rows and the median raised.
    - `ci.yml`, `tests.yml`, `gate.py` and `shards.py` emit or read the shard names themselves.
  - Unaffected:
    - `ruleset` (4): `merge_train.py`, `orchestrator_tick.py`, `record_row.py` and `ci-watch.sh` read the required set from the ruleset, which requires `gate` alone (main-protect-checks, read 2026-11-26). Their lines naming the job are self-test fixtures.
    - `generic` (3): `tests/ci_ratchet.py` counts every `tests / ` job and prices by probe step; `ci_critpath.py`'s `MATRIX_RE` maps `fast (3.14, K/N)` to job `fast`; `policy_lint.mjs` asks the body to name each red check by its own name.
    - `label` (1): `ci_predict.py`'s `JOB["fast"]` is the lane named in a PREDICT line, never matched against a listing.
    - `fixture` (22) and `prose` (7).
- **`tests/run.sh` routing, driven in CI (#3902 review, mutation-vacuous).** The shard block is the function `shard_setup`. `shards.py --self-test` sources `shard_setup`, `shard_of`, `run_always` and `skip` from run.sh, stubs only the lease, and drives them over a 2-shard and a 3-shard fixture plan. It checks that every script runs exactly once across the shards, that an unnamed script runs in shard 1, that no shard runs everything, and that `3/2` is refused with nothing run. The step is governance's `ci-shards`.
- **`tests/closure.py` `PRODUCERS`** gains `tests/setup_qa_render.mjs` -> `plan_view.py`. run.sh's lane_e2e runs it on the payload `plan_view.py` writes. It is not selectable (`NOT_A_TEST`), so only `lane_edges` reads the entry.

Bootstrap. On a pull request the prelude and the gate run the base's `tools/ci/*.py`. This PR's own runs therefore get no plan, run the one unsharded `fast (3.14)`, and are judged by the base gate as before. Sharding first runs on the push to main that merges this, where both programs are the head's.

Waits. The change adds no runner-held wait: no poll, sleep, retry or backoff. The plan step reads two files with `git show` and exits, the shards start together with no wait-for-sibling step, and `gate` reads them through `needs:`.

Code-owned paths: `.github/workflows/ci.yml` and `tests.yml`. The owner's approving review is required (under mandate 6893738184). No budget moved, so `budget-raise-gate` is not involved.

## Head

`4c267409f8badb005ac49e5de3142d6d464cf40f`: the ci-shards step's measured `tools/ci/selftest_closures.json` entry, on `5f068649ae921257a4725846fd0fc4d0ec0b75be`. Review delta from 791d83e7 (5f068649 merged): `git diff 5f068649 4c267409`, that one file. 5f068649 itself is the reviewed head `f03b95f36ebcb0cc4481ca138c953a96f951f269` plus two commits, the fast-job readers and run.sh routing (fc14b732) and the readers harness's inert read (5f068649), `git diff f03b95f3 5f068649`, 10 files. Everything else below was measured at `a486d863340304d6f6a37d2deaa28380fa0cd70f`, the code head before the delta. The readers figures were measured at this head on 2026-11-26.

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

Readers (#3902 review): `python3 dev/audit/harnesses/r11_fast_shards_readers.py <detached worktree at fc14b732>` reverts each reader's fix in place, or plants the review's run.sh mutant, runs that reader's own self-test, and restores the file. Its output is `BASELINE gate=green prelude=green probe=green replan=green shards=green sweep=green`, then `READERS MUTANTS: 7 of 7 killed`:
- review's run.sh mutant (`${FAST_SHARD%/*}` to `${FAST_SHARD#*/}`): killed by the 2- and 3-shard routing checks.
- prelude, fast owed as the unsharded name: killed (`a completed sharded run is judging`, `owed_needs owes every shard`, `a re-run's re-queued shard is requeued`).
- gate.status, the listed shards only: killed (`a sharded push run whose listing lacks one shard reads PRODUCT unread`).
- sweep.code_red, required names only: killed (`a red fast shard is the fast unit's red`).
- probe_bridge, the unsharded lane only: killed (`two fast shards ... each imply 20 s`).
- replan, shards not folded: killed (`a sharded fast lane is one row`).
- census, a reader dropped from READERS: killed.

Each reverted fix is the reading at f03b95f3, so these are the new checks failing first. Baselines at 5f068649: gate 133/0, prelude 153/0, shards 28/0, sweep 124/0, probe_bridge 10/0, replan `self-test: 0 failed`.

Failing first: the gate's 9 new checks read FAIL before `fast_names` existed (`gate self-test: 130 checks, 9 failed`). The payload-reader check read FAIL before the PRODUCERS entry. Baseline: gate 132/0, shards 21/0, prelude 147/0.

## Null control

- run.sh routing, driven as `r11_fast_shards_random.sh` drives it (CI's env, one shard per run). A 2-shard plan run as `HPO_FAST_SHARD=1/2` ran its 4 scripts, skipped 30 by name, printed `SHARD 1/2: 4 TEST SCRIPT(S) PASSED HERE`, and exited 0. The same plan run as `3/2` printed `shards: REFUSE shard 3/2 does not belong to a plan of 2 shard(s)` and `SHARD: REFUSED`, and exited 1 with no script run.
- Readers: each fixed reader's unsharded case still passes beside the new check: `a completed unsharded run is judging`, `run.sh with no shard runs every script`, and a job only resembling a shard name implies nothing in probe_bridge.
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
- Independence: inconclusive. `bash dev/audit/harnesses/r11_fast_shards_random.sh 1 OUT 3` (seed 1, 3 random shards, PRODUCERS groups drawn whole) started on 23eb36c8's run.sh:
  - Coverage holds: the union of the scripts the shards ran is all 33 fast-lane scripts, none missing and none extra. The two TWICE lines are not double routing. `env_drift.py` has two run lines in one shard, `--claims-only` and `--all`, as unsharded. `harness_headers.py` ran twice in shard 2 because I rewrote `tests/run.sh` in place (the `shard_setup` commit, fc14b732) while that shard's bash was reading it. Its stress lane re-ran, then it stopped at `run.sh: line 829: syntax error near unexpected token `fi'` (rc 2) before replaying its lane reports.
  - Pass/fail is not a measurement of ordering:
    - Shard 1/3 rc 1: `typing_ruler.py` (`mypy is pinned at 2.4.1 [found 2.3.1]`, this host's interpreter) and `card.mjs` (V8 out of heap at 2 GB, exit 250).
    - Shard 2/3 rc 2: `optimality.py` and `entities.py` marked FAILED, with their logs lost to the crash above.
    - Shard 3/3 rc 1: `stress.py` 3 of 122. Two are its memory-budget checks (attributable RSS on a host at load 32-54), and one is `shoulder: cheaper than holding the setpoint [4.67 vs 3.96]`, which passes in the 14 CI push runs above. No unsharded local run on this host exists to separate host from order.
  - The routing invariant (every script exactly once across the shards) is now pinned in CI by `shards.py --self-test`'s run.sh driver (Mutation proof). Per-script independence is left to CI's first sharded push run, where a shard that fails beside a green unsharded history names the script.
- Architecture score: `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD`: `Architecture score: dS +0.0000 NULL` (no scored production file changed)
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`; `PYTHONPATH=tests/hastub python3 tests/doc_claims.py`: `ALL 443 checks PASSED`; `pairnote_check.py --repo . --ref HEAD`: `PAIRNOTE OK HEAD: 184 of 561 pairs, 122 files`.

Prepr at 4c267409: `PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh` exits 0, and `selftest_scope.py static` exits 0. `ci_predict.py --base origin/main` then predicts no closures, fast, governance or instrument red. `structure.py`: `STRUCTURE RATCHET PASSED`. `comment_ratchet.py --base origin/main`: `comment_ratchet: OK`. `harness_headers.inline_scan()` exits 0.

Gate scope: `closure.py select` reads `MODE: FULL` for this diff (`tests/run.sh`, `tests/closure.py`, `tools/ci/`, `tests.yml` and `ci.yml` are gate files). The randomized run above runs every script once, across its three shards, so it is the local full gate. CI runs the rest.

## Red checks

Both reds are inherited from #3896's own history, at its delivery-row commit `3797b416d9`, which is an ancestor of this head. Neither is red at this head.

- `tests / fast (3.14)` was red at `3797b416d9`: `tests/doc_claims.py`'s comment ratchet refused four sentences of over 40 words in `tests/entities.py` and `tests/case_select.py`. #3896 fixed it at `58c73880ee`, which this branch is built on. Cheaper detector: `python3 tests/comment_ratchet.py --base origin/main`, which runs in seconds and which `prepr.sh` already runs. No new detector is owed here.
- `tests / closures` was red at `3797b416d9` with `UNDER-SCOPED`: `tests/doc_claims.py` and `tests/entities.py` read `tests/case_select.py`, which their committed closures did not list. #3896 fixed it at `58c73880ee` by adding that path to both closures. Cheaper detector: `tools/ci/ci_predict.py`, which the body push and `prepr.sh` already run. No new detector is owed here.
- At this PR's merge head `6c222ef249`, the only failure is `tests / nightly-status`, which is not required.
- `governance / instrument-self-tests` would be red at `791d83e7` (the #3902 review there). Its selftest-scope step runs `python3 -I tools/ci/selftest_scope.py static`, which exits 1 at 5f068649 with `STALE tools/ci/selftest_closures.json: its steps differ from the workflow's: missing ['ci-shards'], extra []` and `129 gated step(s), 1 problem(s)`. Fixed at 4c267409 by the step's Linux `record`: `static` now reads `129 gated step(s), 0 problem(s)`, rc 0. Cheaper detector: `selftest_scope.py static` runs in under a second, and `ci_predict.py`'s `selftest-scope` arm did not refuse a new gated step with no entry. I predicted the step would read stale and run every step until main absorbed it. `static` refuses that instead, so the entry is owed before the merge. I did not run `static` before the handoff, and running it is the countermeasure.

## Forward-carry

- features.py is the fast lane's floor at 1018 s. A span split saves about 7% while each span's `needs` closure stays as recorded; the lever is the `needs` density (the `@random` chain, the dynamic module moves), measured by `r11_fast_shards_balance.py`'s SPLIT lines against their no-needs null. Carry: #3885

## Friction

none
