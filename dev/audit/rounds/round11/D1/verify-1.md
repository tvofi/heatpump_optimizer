# D1 verify, unit D1#1 (finder seats D1-s1, D1-s2), round 11

I am the one verifier for these 11 findings, and I ran all three lenses on each.

**Tree.** Every finding here has scope D1-s1 or D1-s2, so all are planted-tree
findings. I took every number, V1 and V2, in a private copy of the planted export:
`/Users/timmalmstrom/hpo-orch/r10s6/r11/audit-r11-px-D1-1`. It is a fresh copy of
`plant-export/audit-r11-baseline`. The round-11 `s1/` and `leads/` evidence was
missing from the export, so I copied it in from `handoff/audit-r11-register`. The
`s2/` files already in the export were byte-identical to the branch. All runs used
`PYTHONPATH=tests/hastub` with Python 3.14.7 on macOS arm64.

**Contention.** The box was shared with other seats throughout. load1 ran from
42.7 to 175. thread_factor stayed between 0.998 and 1.017 on every run that
prints it. Every finding is a count, not a timing, so no vote depends on a timing.

**Resume.** An earlier copy of this seat crashed. It had written V2 harnesses into
`audit-r11-px-D1-1/dev/audit/rounds/round11/D1/verify-1/` but left no numbers. I
read each harness, kept it as my V2 instrument, and re-ran all of them. I also
copied them next to this report, under `verify-1/`.

The finder harnesses ran with their own header commands. For m4_race.py I set
`D1_CENSUS_DIR=dev/audit/rounds/round11/D1/s1`, which its header names. Without it,
the harness spends the whole 1500 s timeout on the census enumerator under this
load.

| id | vote | sev | V1 (finder harness: claim / null / perturb) | V2 (mine) | reachable in real HA | class | seam_rule enumerates |
|---|---|---|---|---|---|---|---|
| D1-s1-01 | weaken | low | 1 / 0 / 0 | 1 left after 3 fresh-process clears; null 0 | yes | new | yes |
| D1-s1-03 | verify | medium | 7 of 8 / 0 of 8 / 0 of 8 | 8 of 8 dropped; null 0 of 8 | yes | new | yes |
| D1-s1-51 | verify | low | 2 / 1 / 1 | 4 of 4 tie shapes multivalued; 20 of 40 seeds flip | yes | new | yes |
| D1-s2-01 | weaken | low | live 3, undecodable 3 / 0 / 0 | live 3, undecodable 0 under orjson save | partly | P1 | yes |
| D1-s2-02 | weaken | medium | 6 of 6, future 1 / 0 / 0 | 6 of 6; step-0 surplus 3.60 kW at night | yes | N-no-expiry (not P2) | yes, misses humidity |
| D1-s2-03 | verify | high | 5 of 5 / 0 / 0 | 4 of 5 held flat and fresh; null 0 of 2 | yes | N-no-expiry (not P2) | yes |
| D1-s2-04 | verify | medium | 2 / 0 / 0 | 9 of 9 cells; null 0 of 6 informative cells | yes, narrow window | N-restore-race | yes |
| D1-s2-05 | weaken | low | 142 of 1200 (54 + 88) / ctrl 0 / 0 | 4 of 8 keys at v7, same as v1 | only a hand-edited entry | P1 | partial |
| D1-s2-06 | weaken | low | 8 of 10 restarts / ctrl 0 / 0 | 4 of 8 values raise, at about 2.4e10 h and up | only a corrupt store | P1 | yes |
| D1-s2-51 | verify | medium | 15 of 15 / below-min 0 / 0 | 15 of 15 at hi+0.01; 85 degC accepted on 4 of 4 keys | yes | P1 (not new) | yes |
| D1-s2-52 | verify | low | 2 / 0 (fresh 0) / 0 | 8 of 9 cells; null 0 of 3 | yes | P2 (N-staleness secondary) | yes, by grep |

## D1-s1-01: a stop mid-solve leaves the fallback repair raised for good

**V1.** I ran `m1_stop_midsolve.py --arm stop_midsolve`. It printed
stale_fallback_issues_after_restart=1, issue_persistent=1,
in_process_solves_after_stop=1 and restart_two_solves_ok=1 (load1 51.95,
thread_factor 1.017). The null arm `--arm stop_idle` printed 0 / 0 / 0. The
perturbation `--perturb` moved the stale count from 1 to 0, in the stated direction.

**V2.** `v2_s1_01_fallback_clear.py` calls the production functions directly
across two interpreters. The first interpreter creates a persistent issue, as
`created_persistent=1` shows. A fresh interpreter then calls
`_clear_worker_fallback` 3 times, and the issue is still there afterwards
(`left_after_fresh_process_clears=1`). Clearing in the same interpreter removes it
(`null_same_process_left=0`).

The cause is in `coordinator.py`. `_clear_worker_fallback` returns early when
`_WORKER_FALLBACK_CAUSES.pop(entry_id)` is None, and that dict starts empty in
every process.

**V3.**
- **Reachable.** Real HA restores issues created with `is_persistent=True`, and a
  stop during a solve is an ordinary restart path.
- **Severity.** The issue is `is_fixable=False` and a WARNING. It has no effect on
  the plan or on any actuator: it is a stale, non-fixable notice the user can only
  ignore. That puts it at low, not medium.
- **Seam rule.** The grep lists all 6 `is_persistent=True` sites, so it
  enumerates the seams.
- **Class.** new. No class covers a clear path that keys on in-process state.

## D1-s1-03: a write during a debounced in-flight solve is dropped

**V1.** I ran `m4_race.py --part B`.
- `--origin debounced`: stale_request_refresh_rows=7 of 8, stale_plan_rows=10,
  rows=29 (load1 148.95, thread_factor 1.012).
- `--origin direct` (null): 0 of 8, stale_plan_rows=3.
- `--perturb-rerun`: 7 → 0.

Leave-one-out: dropping any single row leaves at least 6 of 7, so the count is not
a grid artefact.

**V2.** `v2_s1_03_debounce.py` uses the inherited `DataUpdateCoordinator` with a
gated counter, which the integration does not override. A
`request_refresh` issued while a refresh is executing produced no later run in
8 of 8 trials when the first refresh came through `async_request_refresh`, and
in 0 of 8 when it came through `async_refresh`.

**V3.**
- **Reachable in real HA.** Upstream `helpers/debounce.py`
  `_async_schedule_or_call_now` returns False when the execute lock is held. Its
  comment reads "Locked means a call is in progress. Any call is good, so abort."
  The stub reproduces that branch (`_executing` returns False), and
  `tests/ha_contract.py` lists the Debouncer as matching upstream's
  cooldown/immediate semantics.
- **Severity.** medium. A user write is not re-planned until the next interval.
- **Seam rule.** The grep finds 18 `async_request_refresh()` callers, so it
  enumerates.
- **Class.** new.

## D1-s1-51: a tied slot reason follows PYTHONHASHSEED

**V1.** The harness printed distinct_tie=2 and distinct_null=1 (load1 42.70). The
seeds that published `cheap` were 1, 2, 6, 7, 8, 9 and 12; the rest published
`preheat`. `--perturb` gave distinct_tie=1.

**V2.** Over 40 seeds and 4 tie shapes, 4 of 4 shapes published more than one
reason. 20 of 40 seeds disagreed with seed 0 on `a,a,b,b`. The no-tie control
gave 1 value.

**V3.**
- **Reachable.** Real HA does not pin PYTHONHASHSEED, so the published reason can
  change across a restart.
- **Severity.** low. Only the label changes, never the plan.
- **Seam rule.** The finding gives none. My rule, `grep -n 'max(set('`, finds
  1 site (`plan_slots.py:87`), so it enumerates.
- **Class.** new.

## D1-s2-01: NaN passes the store-load boundary

**V1.** With `--sub NaN`:
- nan_boundary_passes=1
- leaves_reaching_live=3 of 515
- leaves_making_disk_undecodable=3
- stores_affected=2

load1 was 72.93. The three leaves are accuracy `comfort/learned_weight`, accuracy
`comfort/evidence` and dhw_profile `cooling_rate`. `--sub Infinity` (null) gave 0,
and `--fix` gave 0.

**V2.** `v2_s2_01_nan_realsave.py`.
- **Real save encoding.** Real HA's `Store` saves through orjson, which writes a
  non-finite float as `null`. The stub's `async_save` uses `json.dumps`, which
  writes a bare `NaN` token.
- **Re-run with null encoding.** I re-ran the finder's harness with the stub save
  changed to that null encoding and nothing else. It gave leaves_reaching_live=3
  and leaves_making_disk_undecodable=0.
- **Boundary check.** `_poisoned` passes 4 of the 7 non-finite spellings I tried.

**V3.**
- **Undecodable half.** That half of the claim depends on the stub. Real HA
  produces 0 undecodable documents.
- **Live-model half.** That half stands, but only for a store that already holds
  the string "NaN". Real HA's own save never writes that string, so the realistic
  sources are hand edits or external corruption.
- **Severity.** low. That is weakened from high.
- **Seam rule.** The seam is the single function `store._poisoned`, and the rule
  covers every leaf through it, so it enumerates.
- **Class.** P1, confirmed.

## D1-s2-02: PV production is read with no age check

**V1.** The baseline run gave stale_cells_published=6 of 6 and future_published=1
(load1 102.16). `--fresh` (null) gave 0, and `--fix` gave 0 / 0.

**V2.** `v2_s2_02_pv_direct.py` checks the reader on its own.
- At 6 of 6 stale ages, `_pv_measured_production` returned 4.0 kW while an
  InputReader built with the entry's settings withheld the reading.
- The two fresh ages (null) agreed, 2 of 2.
- At 22:00 UTC, with the model at about 0, step 0 of the PV surplus was 3.60 kW.

**V3.**
- **Reachable.** A cloud PV integration that stops reporting keeps its last state.
- **Severity.** medium, weakened from high. The plan effect I measured is step 0
  only, and I did not show a wider plan effect.
- **Seam rule.** `consumers.py` enumerates the input slots that bypass InputReader:
  PV production, the price entity, the PV export price and the holiday calendar.
  It reports the humidity slot as `getters=[]` and so misses D1-s2-52.
- **Class.** N-no-expiry, corrected from P2: "a last-known value is published and
  booked as current with no age bound". P2 is the secondary class.

## D1-s2-03: a forecast that stopped advancing is published as fresh

**V1.** The baseline run gave stuck_published_fresh=5 of 5 and
cells_all_rows_past=5 (load1 100.09). `--advancing` (null) gave 0, and `--fix`
gave 0.

**V2.** On my own grid:
- At +2, +3, +72 and +168 h, the outdoor step 0 was held flat at the last row's
  0.70 degC with stale_hours=None. That is 4 of 5.
- At +0.5 h the rows still covered the current hour, which correctly does not count.
- The control offsets of -40 and -10 h flagged 0 of 2.

The seam-rule run, `price_weather.py`, gave weather_stale_hidden=1 and
price_stuck_hidden=0. The price feeds hold; weather does not.

**V3.**
- **Reachable.** A weather entity whose source stalls keeps answering
  `get_forecasts` with old rows.
- **Severity.** high, confirmed. The whole horizon runs on a flat, past outdoor
  temperature with no stale signal.
- **Seam rule.** It covers all three feeds, so it enumerates.
- **Class.** N-no-expiry, corrected from P2.

## D1-s2-04: `_armed_record` is marked loaded before its read lands

**V1.** The baseline run gave consequences=2: hold_not_released=1 and
baseline_lost_on_disk=1 (load1 83.78). `--serial` (null) gave 0, and `--fix`
gave 0.

**V2.** `v2_s2_04_race_orders.py` runs 3 orderings at 3 read delays: 0, 1 ms and
10 ms.
- The concurrent second caller saw an empty armed map in 9 of 9 cells, even at
  `sleep(0)`.
- Run serially, it saw an empty map in 3 of 9 cells. All 3 are restore-then-armed,
  where the restore releasing the hold first is correct by design. On the 6
  informative cells the serial count is 0.

**V3.**
- **Reachable.** Real HA's store read awaits an executor job, so the interleaving
  is real. The window is the first load per entry per process, which is narrow.
- **Severity.** medium. The consequence is a held heat-curve displacement that is
  never released and a baseline lost on disk.
- **Seam rule.** The grep finds 4 sites (`coordinator.py:9766`, `frontend.py:112`,
  `off_restore.py:126`, `pump_arbiter.py:2204`), so it enumerates.
- **Class.** N-restore-race, confirmed as the nearest class. The mechanism differs
  slightly: a check-then-act lazy load, where the empty snapshot is then saved over
  the persisted one.

## D1-s2-05: a wrong-typed numeric option fails setup or every cycle

**V1.** Over 200 mutants for each of v1 to v6:
- build_fail by version was 8, 11, 10, 9, 5, 11, which sums to 54.
- permanent_cycle_fail was 17, 14, 16, 12, 17, 12, which sums to 88.

That is 142 of 1200, exact. `--fix` gave 0 for every version. Leave-one-version-out
keeps every remaining version at 17 to 28 failures.

**V2.** `v2_s2_05_config_exhaustive.py` substitutes "abc" or None into each of the
8 non-bool numeric keys, exhaustively rather than seeded.
- At the current CONFIG_ENTRY_VERSION, v7, where no migration runs, 4 of 8 keys
  fail.
- v1 fails on the same 4 keys: dhw_tank_volume, min_temperature, max_temperature
  and target_temperature.
- The healthy control gave 0 of 2.

The claim's framing around earlier versions and migration is therefore wrong. The
gap is the same at every version.

**V3.**
- **Reachable.** The config flow writes typed values, so a wrong type arises only
  from a hand-edited or corrupt `core.config_entries`.
- **Severity.** low.
- **Seam rule.** Partial. The grep covers `thermal_model.py` and `comfort_band.py`,
  but the dhw_tank_volume failure lives outside those two files.
- **Class.** P1, confirmed.

## D1-s2-06: a huge stored `boosted_h` kills the boost restore task

**V1.** The baseline run gave restarts_raising=8 of 10, per_cell=[0, 2, 2, 2, 2],
with the control at 0 and the DHW boost still restored. `--fix` gave 0.

**V2.** Calling `_restore_settle` directly: 8 of 8 values pass `store._sanitize`.
The 4 values at or above 2.41e10 h raise OverflowError, and each of those 4 leaves
space_since unrestored. 2.39e10 h does not raise. The threshold matches
timedelta.max, about 2.4e10 h.

**V3.**
- **Reachable.** Only through a corrupt or hand-edited boost store. Production
  never writes 2.4e10 h.
- **Severity.** low.
- **Seam rule.** The grep finds 79 `timedelta(...=` sites, so it enumerates broadly.
- **Class.** P1, confirmed.

## D1-s2-51: InputReader accepts readings above the plausible window

**V1.** above_max_accepted=15 of 15 and below_min_accepted=0 (load1 77.14).
`--perturb` gave 0.

**V2.** `v2_s2_51_upper.py`:
- At hi+0.01, 15 of 15 keys delivered the reading.
- At hi+50, 15 of 15 delivered.
- At lo-0.01, 0 of 15 delivered.
- At hi exactly, 15 of 15 delivered.
- 85 degC, the DS18B20 power-on value, was accepted on 4 of 4 keys whose window
  tops out below 85, the indoor window (-30, 60) among them.

`inputs.plausible_c` checks only `window[0] <= value_c`, although its docstring
names the 85 degC case as one the window must refuse.

**V3.**
- **Reachable.** Real sensors read 85 degC on a power-on reset.
- **Severity.** medium. An indoor reading of 85 degC is delivered as a measurement.
  I did not measure what the plan does downstream.
- **Seam rule.** `plausible_c` is the single seam, so it enumerates.
- **Class.** P1, corrected from new: an out-of-domain value crosses an input
  boundary with no guard.

## D1-s2-52: the humidity read ignores the entry's staleness settings

**V1.** config_arms_disagree=2, null_disagree=0, fresh_disagree=0, at
limit_scale1=360 min (load1 83.78). `--perturb` gave 0.

**V2.** Over 3 arms (watchdog off, scale 2.0, scale 3.0) and 3 ages (1.2×, 1.8× and
2.5× the 360-minute limit):
- `_indoor_humidity_value` returned None while the entry-configured reader
  delivered 55.0 in 8 of 9 cells.
- In scale2 at 900 min, both readers withhold, which is correct.
- The default arm (null) disagreed in 0 of 3 cells.

**V3.**
- **Reachable.** `coordinator.py:9175` builds `InputReader(self.hass, {})`.
- **Severity.** low. Withholding the reading drops the mold floor, which is the
  fail-safe direction, but it overrides the user's explicit staleness settings.
- **Seam rule.** The finding gives none. My rule,
  `grep -n 'InputReader(' custom_components/heatpump_optimizer/*.py`, finds 4 sites,
  and only 9175 omits the entry's enabled/scale settings. That enumerates.
  `consumers.py` misses this site.
- **Class.** P2: one fact decided by divergent predicates, a guard at one reader
  missing at its sibling. N-staleness, the finder's guess, is secondary.
