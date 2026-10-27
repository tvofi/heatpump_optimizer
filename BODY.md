#2814: a diagnostics download labelled its last-cycle sections with the moment they were published, not the moment the download was taken. Three residues were left by #2824, which already measured the plan's age at the export and carried the export time:

- **the input ages.** `InputReader` now stamps `InputHealth.read_at` — the instant it measured the ages from — and the payload publishes it as `input_ages_at`. `diagnostics._inputs_at` adds the time from that instant to the export clock to `input_ages_minutes` and to every `input_problems[].age_minutes`. A missing instant, or one ahead of the export clock, leaves them as published: an instant the clock cannot place is unknowable, never zero.
- **`plan_stale`.** `plan_stale_limit_minutes(config)` is one total module function — three intervals floored at 90 minutes, `None` when the config carries no readable `optimization_interval`. The coordinator's `_plan_is_stale` uses it, and the download re-judges at the export with the coordinator's live config, keeping the payload's verdict only when the limit is unreadable.
- **the stored self-tests' run time.** `DebugCollector` sets `self_tests_at` when `_async_finish` stores the results, persists it beside them in the debug document (`store.py`'s DOMAINS gains `self_tests_at`), clears it when a collection restarts, and `async_bundle`'s manifest states both it and `self_tests_age_hours` at the export.

`_plan_is_stale` also loses its early return — an unknown age and an unknown limit are one comparison — which is one class line fewer than before this branch (the ratchet below). `diagnostics._stale_limit`, the first cut's `try/except` wrapper, is gone: the limit's totality lives in the one function both callers use.

This second handoff pass closes the four mutation survivors the branch's predicates left, all at an arm the first cut never drove: a bool or a non-numeric interval read as a limit, a plan exactly at the limit on each of the two comparisons, and a stored run time with no stored results. `tests/debug_collect.py` gains one check per arm and nothing else changes; no production line moves. It also answers the transient `governance / wave-script` red below.

## Head

`37e10fa4b07d61052ec9015700547e8abbfb65f6` on merge base `4f3c7302046eccd1f869724a6de2cbf6f8183418`; origin/main's tip is `524c1896b6943b3da03d6cad61420ced31e14c9c`. Every diff and comparison here is three-dot against that merge base. The branch carries the fix commit `ec2384f70c89db880b6eb7d84b96550b3d205300`, a merge of origin/main (`c12356282`), the delivery row (`8b2fb8c55`), CI's `ci: pin killed mutants` (`e73ff68ca`), and this pass's commit `37e10fa4b`.

## Mutation proof

First pass, at `ec2384f70`: `sh mutants-2814.sh` (sha1 969c55b1f8f82b22892af9dcadd5b7122a33a87f) plants ten mutants, one predicate each, runs `PYTHONPATH=tests/hastub python3 tests/debug_collect.py` per mutant, and restores the file. M0 at the head: `ALL 144 DEBUG COLLECT CHECKS PASSED`. (A green run also prints seven `FAIL a16:…` lines — its py-spy fixture's own plant text; each mutant's count below is its real reds above those seven.) Every mutant was killed. Each kills at least the check that names its predicate, and M3 and M4 also kill the "cannot date" check below:

| # | file | mutation | the check that goes red |
|---|---|---|---|
| M1 | diagnostics.py | the re-base's elapsed time read as `None` | "the download's input ages are re-based to the export: read 2 minutes old and exported 14 minutes later, they read 16" |
| M2 | diagnostics.py | the `input_problems` re-base dropped | the same check |
| M3 | diagnostics.py | `plan_stale` copied from the payload | "the download judges plan_stale at the export with the coordinator's limit: at a 15-minute interval a plan solved 60 minutes ago is fresh, under the 90-minute floor, and stale 96 minutes after it", and "a plan the export clock cannot date keeps the payload's plan_stale, and one the payload never judged publishes none" |
| M4 | diagnostics.py | that comparison's `>` read as `<` | the same two checks |
| M5 | debugger.py | the run time not stored beside the results | "the self-tests' run time is stored with them, survives a reload, and the manifest states it and its age at the export" |
| M6 | debugger.py | the stored time not written into the bundle | the same check |
| M7 | debugger.py | the manifest's `self_tests_at` and `self_tests_age_hours` forced to `None` | the same check |
| M8 | debugger.py | a restart not clearing the run time | "starting a finished collection again clears its self-tests' run time" |
| M9 | coordinator.py | the 90-minute floor dropped (`max(...)` → the cycle product) | the plan_stale-at-the-export check |
| M10 | coordinator.py | the limit's `return` → `None` (no readable limit) | the plan_stale-at-the-export check |

M9 is why that check runs at a 15-minute interval: at the default interval three cycles are exactly the 90-minute floor, so dropping the floor is invisible there. That case was added in the first commit, after M9 survived its first table.

Second pass, at `e73ff68ca`: `python3 tests/mutation_table.py --scope changed --base origin/main --max 10 --jobs 3` printed the four sites the diff adds as `ADDED UNPINNED` and their mutants survived. Each is now killed by a check this pass adds to `tests/debug_collect.py`:

| site | mutant | the check that goes red |
|---|---|---|
| `coordinator.py:738` | `GUARD_OFF` → `if False:` | "a stale limit needs a numeric interval: a bool is no interval, a string is no interval, and zero is a number the 90-minute floor still lifts" — the bool read is `None` guarded, `90.0` unguarded |
| `coordinator.py:7547` | `CMP_BOUND` → `age >= limit` | "a plan exactly at the limit is not stale, and a tenth of a minute past it is" — 90.0 fresh, 90.1 stale |
| `debugger.py:511` | `BOOLOP` → `... or tests` | "a stored run time with no stored results is left out of the document: the two are written together or not at all" — the unguarded arm writes `self_tests_at` with no results |
| `diagnostics.py:193` | `CMP_BOUND` → `age / 60.0 >= stale_limit` | "a plan exactly at the limit is fresh at the export, and one a minute past it is stale" — 90 minutes fresh, 91 stale |

Each was re-driven on this head with its ledger anchor and `--scripts tests/debug_collect.py`; every one printed `killed by tests/debug_collect.py`, `REACH SKIP: 0 driver run(s) not started`, baseline `rc=0 failed=0`:

- `custom_components/heatpump_optimizer/coordinator.py:plan_stale_limit_minutes GUARD_OFF 482b8551`
- `custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._plan_is_stale CMP_BOUND 1e075bcb`
- `custom_components/heatpump_optimizer/debugger.py:DebugCollector.as_dict BOOLOP 81d62bfa`
- `custom_components/heatpump_optimizer/diagnostics.py:_plan_summary CMP_BOUND 7abd2715`

`python3 tests/mutation_table.py --pin-killed --scripts tests/debug_collect.py --base origin/main` then recorded the four rows under `tests/mutation_ledger/killed_by/` — `PIN KILLED: 4 pinned, 0 left unpinned`. Each row's reason is the measured transition: `GUARD_OFF` (`if False:`), `CMP_BOUND` (`age >= limit`), `BOOLOP` (`... or tests`) and `CMP_BOUND` (`age / 60.0 >= stale_limit`) each took `tests/debug_collect.py` from `rc=0 failed=0` to `rc=1 failed=1`. No `survivor_triage` record exists for any of them.

## Null control

- The out-of-tree probe (sha1 c91b44b1e8fe8c87ac5c61d32c63c4147bd839a7) drives the download through `async_get_config_entry_diagnostics` and the collector through `finalize`/`async_bundle`: 0/3 at merge base 6fe5170cd, 3/3 at the head.
  - base: `FAIL input ages … [ages={'indoor': 2.0} problem_age=2.0]`, `FAIL plan_stale … [14min=False 96min=False]`, `FAIL the stored self-tests … [self_tests_at=None age_h=None]` — `0/3 checks passed`.
  - head: `PASS` on all three, `3/3 checks passed`.
- The tree's own harness at the base aborts before running a check: `AttributeError: 'InputHealth' object has no attribute 'read_at'` (base tree, `tests/debug_collect.py:1707`); at the head, `ALL 148 DEBUG COLLECT CHECKS PASSED`.
- Inside the suite the null control for the re-base is the download taken at the publish instant: it reads the published 2.0, so the arithmetic is what moves, not the field. A read instant ahead of the export leaves the ages as published, and a run time at the export reads age `0.0`, not `None`.
- A plan the export clock cannot date keeps the verdict it was published with, and one the coordinator never judged publishes none: the re-judge never invents "fresh" from a missing age. This check, like the floor case, was added in the first commit — the first cut published `False` for a payload with no verdict and no dateable plan.
- The group's own null control, as its brief states it: a download taken at the publish instant reads the same ages before and after — `2.0` at the base probe, `2.0` in the suite at the head.
- The second pass's checks are measured at both arms of each boundary: a bool interval reads `None` while 30 reads `90.0`; 90.0 minutes is fresh while 90.1 is stale; 90 minutes is fresh at the export while 91 is stale; an instant with no results writes no `self_tests_at`, and the existing "the self-tests' run time is stored with them" check reads it present when both are stored.
- The mutation lane's own null control, a comment-only `NULL_COMMENT` edit, survived every driver in play at each of the four anchors: the driver is not red for any mutation.
- Stress is the same tree measurement at both ends: `python3 tests/stress.py` fails 1 of 113 at the base and 1 of 113 at the head, the same line `shoulder: cheaper than holding the setpoint [4.67 vs 3.96]` (first pass, at `ec2384f70`; this pass's delta is the test file only, and the local stress run was left to CI — see `## Figures`).

## Figures

- Suite: `PYTHONPATH=tests/hastub python3 tests/debug_collect.py` → `ALL 148 DEBUG COLLECT CHECKS PASSED` at `37e10fa4b`.
- Mutants, first pass at `ec2384f70`: `sh mutants-2814.sh` (sha1 969c55b1f8f82b22892af9dcadd5b7122a33a87f) → 10 planted, 10 killed (table above).
- Mutants, second pass at `37e10fa4b`: `python3 tests/mutation_table.py --pin-killed --scripts tests/debug_collect.py --base origin/main` → `PIN KILLED: 4 pinned, 0 left unpinned`; each anchor re-run (`--anchor … --scripts tests/debug_collect.py`) → `killed by tests/debug_collect.py`, `REACH SKIP: 0`, baseline `rc=0 failed=0`.
- Probe: `PYTHONPATH=tests/hastub python3 probe-2814.py` (sha1 c91b44b1e8fe8c87ac5c61d32c63c4147bd839a7), run from each tree → `0/3 checks passed` at the base, `3/3 checks passed` at the head.
- Ratchet: `python3 tests/structure.py` → `STRUCTURE RATCHET PASSED` at `37e10fa4b` (first pass re-recorded `class_excess_loc` 18079 → 18078 and `max_class_loc` 8236 → 8235 in its commit; this pass adds no production line, so no row moves).
- Architecture: `python3 tools/audit/archscore/score.py --diff origin/main` → `Architecture score: dS +0.0012 IMPROVES`, `coord_footprint 2412 -> 2410`.
- Scoped gate: the first pass's run at `ec2384f70` was `GATE_SCOPE=auto PREPR_SKIP_CLOSURES=1 bash tests/run.sh` → `MODE: SCOPED -- 27 script(s) run, 6 scoped out`; `5 TEST SCRIPT(S) FAILED`, each reproduced at merge base 6fe5170cd in the same environment (see `## Red checks`); `4386s  TOTAL (1 lane(s))`. **At this head the local gate was not re-run**: the four heavy-slot leases were held by four wedged `prepr` runs for the whole pass (`prepr-72444`, `prepr-91597`, `prepr-99026`, `run.sh-39229`; the orchestrator's `PREPR WEDGE` directive says not to queue behind them), so `harness_headers.py` and `golden.py` waited a lease and were left unrun. The `gate` check at `37e10fa4b` is CI's; this pass's delta is `tests/debug_collect.py` and its four ledger rows, and the delta's own driver ran green above.
- Run-always lines that did run at `37e10fa4b`: `python3 tests/env_drift.py --claims-only 4f3c7302046eccd1f869724a6de2cbf6f8183418` → `claims hygiene: … ok`; `python3 tests/closure.py selftest` → `ALL 117 closure shrink pins PASSED`; `python3 tests/layout.py` → `layout self-test: ok`.
- Golden, first pass: `GOLDEN_MODE=drift GOLDEN_REF=origin/main … python3 tests/golden.py` at `ec2384f70` → rc 0, `NO UNCLAIMED DRIFT: 56 scenario(s) checked against origin/main`; `GOLDEN_MODE=strict GOLDEN_REF=6fe5170cd7ce01e60ffebfc93e598c216e628fa3 …` → `55 of 56` at both the base tree (against its own HEAD) and the head. Both under `tests/gate_lock.py slot-auto-lease`.
- Golden, second pass at this head: `GOLDEN_MODE=drift GOLDEN_REF=4f3c7302046eccd1f869724a6de2cbf6f8183418 python3 tests/golden.py` at `37e10fa4b` → rc 0 after 12m25s, `NO UNCLAIMED DRIFT: 56 scenario(s) checked against 4f3c7302046eccd1f869724a6de2cbf6f8183418` and `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`.
- Baseline control for every script the first-pass gate reddened, at merge base 6fe5170cd in the same environment: `python3 tests/plan_view.py` rc 0; `node tests/card.mjs` rc 134; `python3 tests/optimality.py` 1 of 84 failed; `python3 tests/entities.py` 4 of 2463 failed; `python3 tests/stress.py` 1 of 113 failed; `python3 tests/golden.py` (strict, against its own HEAD) 55 of 56.

## Architecture score

No rise to explain: `dS +0.0012 IMPROVES`, `coord_footprint 2412 -> 2410` at `37e10fa4b`. The first cut of this branch measured `dS -0.0012 WORSENS (coord_footprint 2421 -> 2423)` through a `try/except` wrapper charged as coordinator work; folding the limit into the one total function removed the wrapper and `_plan_is_stale`'s early return, and the trend is now down.

## Red checks

Each red script the scoped gate names, with the control that shows whether this diff moved it:

- `governance / wave-script`: at `e73ff68ca` this job failed once on a transient checkout error in its own runner — `ENOENT: no such file or directory, open '…/.claude/workflows/audit…'` (209 passed, 1 failed) — and passed on the immediate re-run at the same head. This branch touches no `.claude/` file: the diff is `custom_components/` and `tests/`, so the failure is the runner's checkout race, not the tree. The cheaper detector is the re-run the job itself performed; its standing cost is one job run at the head, already paid.
- `node tests/card.mjs`: rc 134, `FATAL ERROR: Ineffective mark-compacts near heap limit Allocation failed - JavaScript heap out of memory` at 2046 MB after 162 s. It is red identically at merge base 6fe5170cd in the same environment (`card` rc 134 in the baseline control), and this diff touches no card, entity or frontend file, so the harness's own memory budget is the detector and this branch did not move it.
- `python3 tests/optimality.py`: 1 of 84, `one|summer_negative|shoulder: a recorded claim still has a gap (not stale) [claimed but gap 0.0000% is at or below the bar -- the claim closed and should be removed]`. The baseline control prints the identical line, so the stale claim is on main already; removing a claimed fixture row is the optimality lane's, not a change to this branch.
- `python3 tests/entities.py`: 4 of 2463, the `hb:positive_control` checks. Root cause: the test's py-spy stub branches on `case $(wc -l < calls) in 1)`, and BSD `wc -l` reading stdin pads the count to eight columns, so the `1)` branch never matches and every case falls to `*)`. Reproduction on this host: the padded stub answers `LAST/LAST`, the same stub with `tr -d " "` answers `HANG` then `SPIN`. The cheaper detector is the suite's portable count (`grep -c .`); the base control prints the same four check names at merge base 6fe5170cd, so this diff did not turn it red.
- `python3 tests/stress.py`: 1 of 113, `shoulder: cheaper than holding the setpoint [4.67 vs 3.96]`; the base control prints the same line, so the measurement is the tree's on this host already.
- `python3 tests/golden.py`: `55 of 56 GOLDEN SCENARIOS CHANGED`. `tests/run.sh` defaults `GOLDEN_MODE` to strict, and strict does not reproduce on this host at all: the merge-base tree run against its own HEAD (`GOLDEN_MODE=strict GOLDEN_REF=6fe5170cd… python3 tests/golden.py`, from the merge-base worktree) prints the same `55 of 56` with the same first diffs (`baseline_cost: 123.221414 -> 124.869053`, `dhw_heating_cost: 8.206833 -> 8.779495`, …). In the mode this round's other gates ran, `GOLDEN_MODE=drift`, the same head prints `NO UNCLAIMED DRIFT: 56 scenario(s) checked against origin/main` and `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`, rc 0. The detector is the drift lane (`tests/env_drift.py`), which is what rule 3 names for solver floats across builds.
- `tests / mutation`: at `37e10fa4b` the four sites the diff adds are pinned by `--pin-killed` (`PIN KILLED: 4 pinned, 0 left unpinned`), so the lane names no added unpinned site — the state the first pass predicted as a warning. The detector is the lane; its standing cost is one CI run per head.

## Unpinned sites

The four sites this diff adds against merge base `4f3c7302046eccd1f869724a6de2cbf6f8183418` are each killed by a check this commit adds to `tests/debug_collect.py` and each recorded under `tests/mutation_ledger/killed_by/` by `--pin-killed` (no `survivor_triage` exists for any of them):

- `custom_components/heatpump_optimizer/coordinator.py:738 GUARD_OFF`: pinned by the value check "a stale limit needs a numeric interval…".
- `custom_components/heatpump_optimizer/coordinator.py:7547 CMP_BOUND`: pinned by the value check "a plan exactly at the limit is not stale…".
- `custom_components/heatpump_optimizer/debugger.py:511 BOOLOP`: pinned by the value check "a stored run time with no stored results is left out…".
- `custom_components/heatpump_optimizer/diagnostics.py:193 CMP_BOUND`: pinned by the value check "a plan exactly at the limit is fresh at the export…".

## Forward-carry

1. `tests/entities.py`'s py-spy stub reads `case $(wc -l < calls) in 1)`, and BSD `wc -l` pads a stdin count to eight columns, so on macOS the branch never matches and four `hb:positive_control` checks read red on every run (control: the identical four at merge base 6fe5170cd in this session's baseline log). The file is outside this group's seam and the group that owns it is open. Control: `printf 'x\n' | wc -l` on this host prints `       1`. Carry: R10-FLY-SUITE-ENV-FLAKES

## Friction

- dev/governance/roles/fixer.md#3: unclear: "an instant ahead of the clock is unknowable, never 0" fixes the age arithmetic but says nothing about the `plan_stale` verdict at such an instant; this branch keeps the payload's verdict where the limit is readable and the age is not, which follows the payload rather than the clock. Carry: dismissed: the payload's `plan_stale` was computed by the coordinator at publish, so it is the only defensible answer when the export clock cannot date the plan.
- gate-scoping.md: cost: four wedged `prepr` runs held every heavy-slot lease for this pass (`prepr-72444`, `prepr-91597`, `prepr-99026`, `run.sh-39229`), so `harness_headers.py`, `golden.py` and the scoped gate could not run locally at `37e10fa4b`; left to CI's `gate` at this head. Carry: dismissed: the orchestrator's `PREPR WEDGE` directive clears the leases and runs the pushes serially; a local re-run behind them would queue, not measure.
