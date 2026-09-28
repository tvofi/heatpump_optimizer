# S5 class sweep: user state not surviving restart

New class (round 9), `rca: true`, `n: 2`: D1-s2-52, D1-s2-53. **Already `barriered: true`** in
`CLASSES-DRAFT.json`, per the barrier on `handoff/r9-rc2-user-state-durable` (PR #1641, merged at
`4f25b5e3`, already an ancestor of this sweep's checkout). Per the brief: any instance here sets
`rca` and must be checked against that barrier's classification.

## Checked against the RC2 barrier first

Read the actual diff of #1641 (`git diff 1936d5c 5188eb5`, its merge-base and tip): it touches
only `button.py`, `entity.py` and 2 lines of `coordinator.py`. The mechanism it fixes is HA 2026.5
routing single-entity service calls through `async_request_call` (a `PARALLEL_UPDATES=1`
semaphore): four button presses (`ForceOptimizationButton`, `SystemIdentificationButton`,
`ResetComfortWeightButton`, `DiagnoseIntervalButton`) now return immediately via a new
`entity.off_the_action` helper instead of awaiting the coordinator call inline, so a restart mid
press no longer cancels the queued action; `async_reset_comfort_weight` additionally now awaits
`self._accuracy_store.async_wait_for_read()` before resetting. **This is a different shape**
(button-press cancellation under HA's per-entity call semaphore) from D1-s2-52 (five *other* store
writers racing their own startup load) and D1-s2-53 (`set_thermal_parameters` fields never
persisted at all) — RC2's barrier does not name or exercise either seam.

## Enumerator

Two D1-leads harnesses (already class-shaped, built by the D1-s2 finder), copied here unchanged
as `enumerate_store_race.py` and `enumerate_params_restart.py`:

- **`enumerate_store_race.py`** (D1-s2-52's harness): a real asyncio loop with a real
  `ThreadPoolExecutor`; for each of the coordinator's 5 stores plus the one writer that already
  waits (`async_set_mode`), starts the coordinator (which fires the startup load
  fire-and-forget), immediately calls that store's own writer, and reports whether the persisted
  marker survives once every load lands.
- **`enumerate_params_restart.py`** (D1-s2-53's harness): calls
  `async_update_thermal_params` once per field (26 of 28 schema fields actually change coordinator
  state), restarts the coordinator on the same entry/store disk, and reports which fields'
  footprints do not survive.

Both needed CPython >= 3.12 (`asyncio.Task(..., eager_start=True)`, matching the finder's own
"CPython 3.14.0rc2" baseline note) — this cloud container's default `python3` is 3.11, so both
runs used a throwaway `python3.12 -m venv` with the same pins as `tests/requirements-ci.txt`.

## Controls (re-run on this box, this session, on the current tip -- post #1641/#1642/#1643)

- **`enumerate_store_race.py`, baseline**: `lost=5 stores_of_5`
  (`energy,ledger,thermal,price,accuracy`), `mode_arm_lost=0 of_1`. Exact match to the finder's
  documented "lost=5 of 5 (exact)".
- **`--after-read`** (**null control**: writers run only after the loads land): `lost=0 stores_of_5`.
- **`--wait`** (**perturbation**: every save first awaits `QuarantiningStore.async_wait_for_read`):
  `lost=0 stores_of_5`. Moves in the documented direction.
- **`enumerate_params_restart.py`, baseline**: `changed_fields=26 of_28`, `lost=24 of_changed`,
  `survived=dhw_cooling_rate,buffer_cooling_rate`. Exact match to the finder's documented
  "lost=24 of 26 changed fields (exact)".
- **`--persist`** (**perturbation**: the changed fields are also written into `entry.options`):
  `lost=0 of_changed`. Moves in the documented direction.

**Both seams reproduce, unfixed, on the current checkout tip (which already carries #1641, #1642,
#1643).** RC2 did not touch either.

## Disposition

- **D1-s2-52, instance, confirmed unfixed by the barrier**: 5 of 5 stores lose their persisted
  marker to a writer that races the startup load; `async_set_mode` (the one seam that already
  waits) loses nothing, showing the fix is a targeted `async_wait_for_read()` at each of the 5
  writer call sites, the same shape `--wait` already proves works.
- **D1-s2-53, instance, confirmed unfixed by the barrier**: 24 of 26 `set_thermal_parameters`
  fields have no persistence path at all (they change in-memory coordinator/config state and nothing
  else); `--persist` proves the fix is to route those fields through `entry.options` the same way
  the two surviving fields (`dhw_cooling_rate`, `buffer_cooling_rate`) already do through the
  thermal-learning store.
- **0 guarded, 0 not applicable, 0 new instances** beyond the two named findings — the enumerator
  is exhaustive over its own scope (every one of the coordinator's 5 stores; every one of
  `set_thermal_parameters`'s 26 state-changing fields), so there is no wider seam left to sweep
  within this class's two mechanisms.

## Count and RCA

N = 2 verified findings (D1-s2-52, D1-s2-53) + 0 additional sweep-confirmed instances = 2.
**rca: true** is set anyway per the brief's explicit rule for this class ("any instance in a class
already `barriered`... sets the class's RCA flag", PLAN Sec.7.5) and per the brief's own table
already carrying `rca: yes` — not because N >= 3.

## Barrier proposal (the two seams RC2 left open)

1. For D1-s2-52: add `await self.<store>.async_wait_for_read()` at the start of each of the 5
   writer methods the enumerator names (mirroring `async_set_mode`'s existing pattern), then a
   `tests/` regression using `enumerate_store_race.py` (no flags) asserting `lost == 0`.
2. For D1-s2-53: route the remaining 24 fields through `entry.options` on
   `async_update_thermal_params`, mirroring `dhw_cooling_rate`/`buffer_cooling_rate`'s existing
   path, then a `tests/` regression using `enumerate_params_restart.py` (no flags) asserting
   `lost == 0`.
Both barriers are the harnesses already committed; cost is one asyncio session per gate run
(~1-2s each, measured this session, uncontended).

## Unfinished / exposure

- Did not search for additional store-writer or settable-field seams beyond the two enumerators'
  own scope (e.g. other config-entry option paths, other `async_create_task`-spawned loaders) —
  the enumerators are exhaustive over the coordinator's 5 stores and the 26 `set_thermal_parameters`
  fields specifically, not over every persistence path in the integration.
- Read `git diff 1936d5c 5188eb5` (the #1641 merge range) to establish the barrier's actual
  mechanism, per the exposure rule (the ledger exception covers reading fix diffs to classify a
  barrier, not general GitHub browsing).
