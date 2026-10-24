# D1 round 8 — single verifier (v1) report

Tree: `/home/claude/audit-r8/seats/D1-v1` (copy tree at baseline `cdf82daa`), with
the D1-s1/s2/s3 evidence copied in. No finder harness hard-codes a seat path, so
none needed rewriting. The box was a shared 4-vCPU container with load1 between 16
and 24 throughout. Every number below is a count and therefore final; no timing
is relied on. Production files are byte-identical to the export (`diff -rq`
shows only `tools/audit/round8/D1`). Every perturbation was applied in-process
and restored in a `finally`.

This panel has one verifier, so this report covers both halves of `verifier.md`.
For each finding it records the finder's harness re-run (with its perturbation and
null control), my own harness under my own metric, and the attacks in the
contract's order.

| id | finder value | re-run | own harness value | vote | severity |
|---|---|---|---|---|---|
| D1-s1-01 | 2 | 2 (perturb 0, control 0) | 2 live / 2 published, and the next solve's inputs reverted 2 (perturb 0, control 0) | verify | medium |
| D1-s1-02 | 3 | 3 (perturb 0) | service 1 off-loop call on the live params, 1 torn; button 0 (perturb 0) | verify | low |
| D1-s2-01 | 0.324 | 0.3240 (finder's perturbation 0.0000) | 3/3 cycles fail, but with 4 ERROR logs, 3/3 cycles still actuate, and setup gives ConfigEntryNotReady (perturb 0) | weaken | medium |
| D1-s3-01 | 4 (4 to 0 under perturbation) | 4, but 4 to **1** under the stated perturbation | 5/6 cycles fail and 0 of them actuate; an immediate retry succeeds (finder's edit gives 1, a fence gives 0) | weaken | medium |

## D1-s1-01 — the away-setback unwind reverts DHW minimums written mid-solve

- **Re-run.** `s1_setback_race.py` gave race_reverted_live=2, race_reverted_published=2,
  race_in_solve_at_call=1 and control=0, at load1=23.65 and thread_factor 1.083.
  That factor comes from the real worker thread, and counts are not affected by it.
  With `--perturb`, race goes to 0. The number matches the finding exactly.
- **Own harness: `v1_setback_race.py`.** Metric: of the fields written through
  `async_update_thermal_params` (what `handle_set_thermal_params` calls once it has
  validated) while `async_run_optimization` is parked on `_await_process`, count
  those whose live and published values differ from the written value once the
  cycle returns; away mode is inactive. The harness uses no wall-clock race: the
  write is injected deterministically at the solve's await point.
  Results: race 2/2, control 0/0. In the "late" arm (a second full cycle after the
  racing write), `late_next_solve_inputs_reverted=2`, so the **next solve's own
  snapshot** carries 45.0/20.0 and not the requested 37.0/29.0. I used my own
  fix-shaped perturbation, a compare-and-swap `restore_setback` that restores a
  field only if it still holds the setback's value. It gives 0 on every arm.
- **Attacks.** Timing: counts only. The finder's window widths are marked
  provisional and are not relied on. FakeHass: the finder used a real loop with a
  real executor and a real process worker, and I forced the same interleave that a
  real loop allows at that await. Reachable in real HA: yes, because service
  handlers run on the loop while the solve is parked for seconds. Null control:
  present and passing. Scope: `restore_setback` also rewrites `target_temp`,
  `min_temp`, `comfort_temp_day` and `comfort_temp_night`, so a
  `set_temperature` write (`coordinator.py:2389`) that lands mid-solve is exposed
  to the same unwind. I did not measure that; it is noted for the judge. Severity:
  the service acknowledges the setting, then loses it silently until it is called
  again, but it only happens when a call lands inside a solve window. Medium is
  earned.
- **Mechanism.** This is separate from D1-s1-02; the two only share the theme of
  live params touched concurrently.

## D1-s1-02 — the diagnose_interval service runs a bound coordinator method on the executor

- **Re-run.** `s1_thread_reads.py` gave offloop_attrs=3 (`_ctx`,
  `_last_diagnosis`, `_last_interval_record`), button=0 and cycle=0. With
  `--perturb` it gives 0. This matches the finding.
- **Own harness: `v1_diag_offloop.py`.** Metric: for each path, count the
  `diagnose_record` calls that run off the loop thread while holding the live
  `ctx._thermal_params` object (by identity), and of those, the calls that
  computed on a value the loop wrote while they were in flight. The executor is a
  real `ThreadPoolExecutor`; FakeHass would hide the defect. Results: service 1
  and torn 1, button 0 and 0. With `--perturb` (the handler routed through
  `async_diagnose_interval`), all four are 0.
- **Attacks.** The torn read is forced by construction: the loop write is
  scheduled while the worker waits. It shows that the path is possible, not how
  often it happens. The finder's "3" counts attribute names and is not a count of
  consequences. `diagnose_record` works on a `replace(params)` copy, so nothing is
  written back into the live params, and the `_last_diagnosis` write is a single
  assignment. The finder's "only off-loop coordinator access in the whole
  lifecycle" covers only the phases its harness exercised. Real HA runs executor
  jobs on real threads, so the path is reachable. The consequence is at most an
  inconsistent diagnostic report, so low is earned.
- **Mechanism.** Not shared with any other finding.

## D1-s2-01 — MonthlyLedger.from_dict skips leaf validation

- **Re-run.** `s2_ledger_fuzz.py` gave ledger_escape_rate=0.3240, repeat 1.0,
  accuracy 0.0 and price_model 0.0. The finder's harness has no perturbation flag,
  so I applied the stated perturbation (a leaf guard in `from_dict` that drops the
  month) in-process with `v1_s2_perturb_runner.py`. It gives
  **0.0000 (250/250 quarantined clean)**, which confirms that direction.
- **Own harness: `v1_ledger_cycles.py`.** Metric: with one plausible hand-edit
  (`savings_baseline.sek = "12,5"`) loaded through the real `QuarantiningStore`
  and `_async_load_ledger`, count how many of 3 real `async_refresh` cycles end
  with `last_update_success` False, alongside ERROR records, actuating cycles and
  the result of the setup first refresh. Results:
  - current month: failed=3, error_logs=4, actuated=3, first_refresh_not_ready=1
  - a month 20 months back: identical
  - null (a float value): 0, 0, 3, 0
  - perturbation (a try/except in `MonthlyLedger.line`): 0 on every arm
- **Attacks.**
  1. **The claim's "with no log line" is refuted by measurement.**
     `_async_update_data`'s outer `except Exception` logs at ERROR with a traceback
     on every cycle: 4 records over 3 cycles, including the coordinator's
     transition log.
  2. The claim's "crashes every cycle" understates one thing and overstates
     another. `_apply_action` runs before `_build_data_dict`, so actuation
     continues (3/3). What is lost is publication: entities become unavailable and
     the data goes stale.
  3. It is worse than claimed at setup. If the ledger has loaded before the first
     refresh, `async_config_entry_first_refresh` raises `ConfigEntryNotReady`
     (measured: 1). The load is `_spawn`ed, so in real HA the ordering is a race.
  4. "Forever" is bounded by `KEEP_MONTHS=24` pruning, and that bound is
     effectively forever.
  5. The null control is not "the identical 250-mutant pool". The control stores
     are mutated by a different generator (`_apply_generic_leaf_mutation`) on
     different payloads. Their 0.0 is still meaningful, but it is not a
     like-for-like comparison.
  6. 0.324 is a grid artefact. It depends on the mutation mix: 55% of mutants are
     leaf type-confusions, and meta, nesting and missing-key mutants never escape.
     The per-mutant fact underneath is binary.
  7. The harness prints a hard-coded `thread_factor=1.00` instead of a measured
     one. That is a contract defect, although it does not matter for a ratio of
     counts.
  8. Reachability: the integration never writes a non-float leaf. `add()` refuses
     non-finite values, and the store sanitizer only turns non-finite values into
     `None`. The trigger is therefore an external edit or corruption of `.storage`.
- **Vote: weaken, critical to medium.** The consequence (entities unavailable
  indefinitely, possibly a setup retry loop) is real, but actuation continues,
  every cycle logs an ERROR, and the trigger is external.
- **Mechanism.** Not the same as D1-s3-01, although both fail through the same
  channel: a wrong-typed leaf gets past a validator that checks only structure and
  lands in `_async_update_data`'s outer `except` as `UpdateFailed`. The code sites
  and fixes are different.

## D1-s3-01 — a malformed Open-Meteo `hourly` field fails the whole cycle

- **Re-run.** `s3_openmeteo_hostile.py` gave cycles_crashed=4 of 5 and
  control_crashed=0. The header expects 5, which is inconsistent with its own
  result: `[]` falls through `or {}`.
  - The harness has no perturbation flag. I applied the stated perturbation
    (`if not isinstance(block, dict): return _EMPTY`) in-process with
    `v1_s3_perturb_runner.py`. The result is **cycles_crashed=1, not 0**: the shape
    `{"time": "not-a-list", "shortwave_radiation": 5}` is a dict, so the guard
    passes it, and `zip` then raises `TypeError`.
  - The finding's "observed: 4 to 0" is therefore not reproducible from the stated
    edit. The harness does move in its stated direction ("strictly decreases"), so
    the finding is not void.
  - The harness prints no load1, thread_factor or swapins. It also drives only
    `async_refresh`, not a cycle, so the name "cycles_crashed" is not what it
    measures.
- **Own harness: `v1_openmeteo_cycle.py`.** Metric: of 6 wrong-shaped valid-JSON
  bodies, count how many make one full coordinator cycle (Open-Meteo source
  selected, auto mode, real solve) end with `last_update_success` False, and
  record whether those cycles actuated. Results: **failed=5/6, and
  failed_actuated=0**, so the solve and the actuation are lost along with the
  cycle. The null control gives 0. With `--perturb=finder` the result is 1; with
  `--perturb=fence` (the docstring's "never raises") it is 0.
- **Attacks.**
  - The cycle-level claim holds, and it is stronger than the finder's evidence
    showed.
  - The refresh gate bounds it. `_last_attempt` is set before the fetch, so an
    immediate second cycle skips the fetch and succeeds (second_cycle_failed=0 in
    all 6 cases). At the default 30-minute interval, which is at or above the
    20-minute gate, every scheduled cycle refetches and fails for as long as the
    body stays malformed. At a 10-minute interval roughly every other cycle fails.
  - Reachability: `_get_json` already refuses a non-dict top level and error
    bodies. The trigger needs an Open-Meteo 200 response whose member has the wrong
    type, which means an API schema change or a mangling intermediary.
- **Vote: weaken, high to medium.** The consequence when triggered is high: no
  solve and no actuation, cycle after cycle. But the trigger is a
  schema-nonconformant 200 response from a stable API, and the evidence record's
  4-to-0 perturbation result is wrong: the stated edit leaves 1.
- **Mechanism.** It shares the same failure channel as D1-s2-01; the mechanism
  differs, as noted there.

## Harnesses written by this seat

- `v1_setback_race.py`
- `v1_diag_offloop.py`
- `v1_ledger_cycles.py`
- `v1_openmeteo_cycle.py`
- `v1_s2_perturb_runner.py`
- `v1_s3_perturb_runner.py`

All are under `tools/audit/round8/D1/`, and the command for each is in its header.
