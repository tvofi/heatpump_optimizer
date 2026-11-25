# D14-s3 -- round 11, dimension D14, axis `nightly-replay`

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`, box B7 (4 vCPU, shared with two
compute seats; load1 5-12 throughout). Interpreter `/root/venv-ci/bin/python3`,
`PYTHONPATH=tests/hastub`, run from the worktree root. Every number below is a count
unless marked provisional.

Cells (`check_scopes.py --seat D14-s3`): `M1+M2+M3+M4+M5  nightly-replay  (any file)`.
Reading of the axis: each step of D14's method, carried out through the nightly replay
(`tests/replay.py:run_fixture` -- the real coordinator cycle over a recorded day), with
the fixtures mutated in memory to drive a class's seam; plus the stop rule's second
condition, "no new invariant break in the nightly replay".

## Method

All replay detectors share `replaykit.py`: it runs a mutated copy of a fixture through
the tree's own `replay.run_fixture` in a child interpreter and keeps what the lane throws
away (every entity record of every cycle, every service call). A `--tree DIR` argument
replays an older tree's own coordinator from a `git archive` export, which is how the
pre-fix re-finds were run.

| harness | class | what it replays |
|---|---|---|
| `p10_routes.py` | P10 | kernel calls by route (loop / executor / worker); kernel set widened past `tests/replay.py`'s to numpy.linalg, scipy minimize/linprog and the package's own replay helpers; arms: synthetic, synthetic-learner, synthetic-surfaces (diagnostics, every button, every options page), owner, owner-learner, owner-1h |
| `p8_currency.py` | P8 | EUR feed on a SEK instance: published leaves carrying SEK |
| `p8_surfaces.py` | P8 | HUF feed on a SEK instance: six money surfaces of one install |
| `staleness_quiet.py` | N-staleness | a quiet night (on-change probes silent 5 h / 7 h), a polling control, a mode-entity outage |
| `name_sort.py` | N-name-sort | the PUBLISHED roster of both fixtures, sorted en/sv/de and by entity id |
| `step_grid.py` | N-step-grid | every NumberSelector the flows build, plus every options page rendered from each fixture's stored entry |
| `reap_lock.py` | N-reap-lock | stop and reload against a long job in the real process worker |
| `registry_reload.py` | N-registry-leak | reloads with the production unload, then live coordinators after gc |

## Findings

### D14-s3-01 (P8, medium) -- money fields and the fee bound resolve the instance currency
`p8_surfaces.py`: with the feed declaring HUF on a SEK instance, 3 of 6 surfaces diverge:
the options money field is labelled `SEK/kWh` with max 5, the grid-fee rules page states
bound `10` / currency `SEK` and refuses `= 20` as `grid_fee_rules_implausible`, while the
entities publish `HUF`, the `price_currency` repair issue names `HUF` (and its text says
grid fees must be entered in HUF), and the coordinator's fee notice scales to HUF and
stays quiet. Null (HUF instance): 0. Perturbation (`config_flow.resolve_currency` takes
the feed first): 3 -> 0. Pre-fix tree 3490cb16: 5 (null 3).

### D14-s3-02 (N-reap-lock, medium) -- an unload orphans the solve it cancelled
`reap_lock.py`, real worker child, real `run_in_executor`: the stop seam is guarded
(0.00 s with a 6 s job in flight; 5.00 s when the kill is made a no-op). The unload seam
is not: `async_shutdown` cancels the refresh, the executor thread keeps `_PROCESS_LOCK`,
and nothing reaps the worker, so the new entry's first job waits 5.00 s (1.00 x the
orphan's remainder) after one reload and 17.00 s after three (every orphan still runs its
whole job). Null (no job in flight): 0.04 s. Perturbation (unload also runs
`_shutdown_process_pool`): 17.00 -> 0.04 s. Walls provisional.

### D14-s3-03 (P10, medium) -- schedule pricing simulates on the event loop
`p10_routes.py --arm owner-1h`: 384 `ThermalModel.simulate_step` calls on the loop over
2 replayed cycles of the owner's day (773 over 4 on the 2 h arm), every one on the stack
`_compute_baseline_power <- reference_day <- whatif.schedule_days <- async_simulate <-
_maybe_run_fuse_advisor`; 18.8 ms of loop CPU here (provisional). `tests/replay.py`'s P10
barrier replays only the DHW-only synthetic day and reads 0 (so does this harness on it).
Perturbation (`whatif.schedule_days` -> None): 384 -> 0.

## Non-findings (held, with the number)

- P10 synthetic arms: loop 0 / executor 0 on synthetic (12 cycles, 12802 in the worker),
  synthetic-learner (reaches `_async_learn_house_heat_loss`, `_replay_fabric`,
  `_replay_interval` in the worker), synthetic-surfaces (diagnostics, 6 buttons, every
  options page: 0 kernels off the worker). Owner arms: the lower-floor learner
  (`_async_learn_lower_floor_loss`) and the house learner replay in the worker.
  Re-introduction (`_await_off_loop` runs inline): 0 -> 59. Pre-F1.7 tree 3dfebc1690:
  96 loop calls of `topology._advisor_replay` (re-found); c4e1e0c07^ (3be1d4ac6e, the wip
  that already carries the fix): 0. The first cut of the widened kernel list counted
  `AccuracyTracker.replay` (12 loop calls / 6 h): a dict lookup, not a kernel -- dropped;
  `out/p10_all_arms.out` predates the drop.
- P8 entity units (`p8_currency.py`): EUR feed on SEK instance: 0 SEK leaves, 14 EUR
  leaves; null EUR/EUR 0; perturbation (`_feed_currency` -> None) 0 -> 14; pre-fix
  3490cb16: 14 SEK leaves (re-found).
- N-staleness quiet night (`staleness_quiet.py`): quiet5 0 entity-cycles unavailable
  beyond the polling control; perturbation (room/tank limits 60 min) 0 -> 56; pre-fix tree
  3e9f1878bd^ 56 (R9 D1-s5-51 re-found); quiet7 14 (the designed 360 min bound).
- Mode outage past MODE_LAST_GOOD (C5's second half): with the mode select unavailable
  5 h on the hot-water-only fixture, 3 cycles (from 180 min until it returns) plan
  30.5-33.3 kWh of space heat over their horizon the pump cannot serve -- the documented
  "full capability" direction, with its repair issue; pre-R9 tree 0. Measured, not filed.
- N-name-sort (`name_sort.py`): 0 split families in en/sv/de on both fixtures' published
  rosters (76 keyed entities, 15 families). By entity id 5 families split (away, dhw,
  heat, lifetime, wood): ids are frozen by the id-stability rule, so this is explained.
- N-step-grid (`step_grid.py`): 412 number fields (76 pages incl. options rendered from
  both fixtures' stored entries), 181 with a numeric step: 0 default/max/min off grid;
  perturbation (defaults + step/2) 0 -> 93.
- N-registry-leak (`registry_reload.py`): two reloads with the production unload and the
  entry's on_unload callbacks: 0 coordinators leaked beyond the never-unloaded last one;
  perturbation (`early_cutoff.detach` no-op) 0 -> 2.
- Stop rule, nightly replay: `python3 tests/replay.py` (both fixtures, 2291 s): every
  functional invariant ok (finite, unit, no_default, agreement, cycle, not_frozen, away)
  on both fixtures. The only reds are `cycle_cost` (owner cpu_ratio 534.6 / budget 332.8,
  loop 0.2487 / 0.2154; synthetic 2.163 / 2.084, 0.1635 / 0.1527), taken at load1 5-12
  on a shared box: provisional, for the quiet re-take.

## Unfinished

- M3/M4: N-future-clamp, N-period-rollover, N-confounded-learner, N-leaf-imports-solver,
  N-order-coupling, N-restore-race have no replay detector from this seat. Next: a
  time-shifted synthetic day across a month boundary (period rollover), a reload with a
  persisted future instant (future clamp; the lane's `away` invariant across the owner
  fixture's reloads already reads 0), a restore racing a cycle write (restore race).
- C4: of the barriered/detector production classes only N-staleness was swept through the
  replay for new seams.
- The `cycle_cost` reds need the quiet-window re-take before they mean anything (lead to D3-s3, whose cells hold tests/replay.py).

## Exposure

Read under the brief's exception: `dev/audit/config/bugclasses.json` (all classes); the
git history of listed instances: `3490cb16` (P8 pre-fix, exported and replayed),
`c4e1e0c07` / `3be1d4ac6e` / `31717a8f91` / `3dfebc1690` (P10 F1.7 chain, logs; the first
and last exported and replayed), `3e9f1878bd` / `d1ed32a810` (R9 F4.1, log and the
parent's const.py; parent exported and replayed), `9c988fc58`, `5dfa6684f` (log lines).
In-tree tests citing earlier ids were read as context: `tests/features.py` (R10
N-staleness census, R9 P8 HUF pins), `tests/entities.py` (#1760 family block),
`tests/replay.py` (P10 arms). The round-10 carries C1-C6 came in the task text. No
round-10 harness or report was opened.

## Harnesses

`p10_routes.py`, `p8_currency.py`, `p8_surfaces.py`, `staleness_quiet.py`, `name_sort.py`,
`step_grid.py`, `reap_lock.py`, `registry_reload.py` (driver: `replaykit.py`). Run logs:
`out/`.

## M1 class ledger as read (status, kind)

| class | status | kind |
|---|---|---|
| N-postreview-merge-red | open | instrument |
| R9-ROW-STALE | barriered | instrument |
| P1 | barriered | production |
| P2 | barriered | production |
| P3 | barriered | production |
| P4 | detector | production |
| P5 | barriered | production |
| P6 | barriered | production |
| P7 | barriered | production |
| P8 | open | production |
| P9 | barriered | production |
| P10 | open | production |
| I1 | barriered | instrument |
| I2 | barriered | instrument |
| I3 | barriered | instrument |
| I4 | barriered | instrument |
| I5 | barriered | instrument |
| N-future-instant | barriered | production |
| P11 | barriered | production |
| N-restart | barriered | production |
| N-solve-recompute | barriered | production |
| N-structure-blind | barriered | instrument |
| N-name-sort | open | production |
| N-shared-config | barriered | production |
| N-approval-rebuy | open | instrument |
| N-finally-return | open | instrument |
| N-step-grid | open | production |
| N-reap-lock | open | production |
| N-staleness | barriered | production |
| N-silent-zero | barriered | instrument |
| N-orphaned-handoff | prototype-only | instrument |
| N-silent-stop | detector | instrument |
| N-body-lint-bounce | barriered | instrument |
| N-train-only-predicate | barriered | instrument |
| N-registry-leak | open | production |
| N-future-clamp | open | production |
| N-no-expiry | barriered | production |
| N-log-flood | barriered | instrument |
| N-gate-yield | open | instrument |
| N-move-stale-path | barriered | instrument |
| N-period-rollover | open | production |
| N-confounded-learner | open | production |
| N-leaf-imports-solver | open | production |
| N-order-coupling | open | production |
| N-restore-race | open | production |
| N-p2b-assembly-reader | open | instrument |
| N-vocabulary-drift | barriered | instrument |
| N-unmetered-reference | detector | production |
| N-livehead-operator-cancel | detector | instrument |
| N-dispatch-overreach | open | instrument |
| N-relay-handoff-starvation | detector | instrument |
| R10-TOPIC-FAMILY | barriered | instrument |
| R10-SELFTEST-RED-INTRODUCED | barriered | instrument |
| N-stamp-claim-conflict | open | instrument |
| N-provisional-gate-red-read-final | barriered | instrument |
| R10-SELFTEST-TABLE-SHRINK | barriered | instrument |
