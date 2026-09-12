# D1 verifier 3 of 3 — round 4, panel D1-0

Stance: refute-first. Tree: branch head `0855277edc49cb3cce3b1095fa1e5edcda7663c8`
(findings were measured at baseline `7dd68dd`; every finder number reproduced
identically at the head, so there is no drift to explain). Machine: 8-core
Apple M1, 8 GB, CPython 3.11. Other agents were running throughout;
`load1` ranged 4.7–7.0 across my runs. Every number below is a **count** or a
plan-content delta, so none is contention-sensitive; the two `wall_s` figures
are provisional and load-bearing for nothing. `thread_factor=1.0000` on every
run (printed by each harness).

## Harnesses re-run (finder's, exact headers)

| harness | result | matches report? |
|---|---|---|
| `price_prior_zero.py` | `zero_priced_steps=4`, `control=0`, `null_control=0`, `bins_reaching_zero=14`, per-bin min/max 4/4, control price at the affected steps `0.6018` vs `0.0000` | yes, exact |
| `accuracy_wipe.py` | `fields_lost=3/3`, `control=0`, `bool_variant=3`, `warning_log_lines=0`, `log_lines=0`, `last_update_success_after=1`, exceptions `TypeError: 'float'/'bool' object is not iterable` | yes, exact |
| `real_loop.py --cycles 5 --inflight` | leaked 0/0/0, `first_cycle_ok=5`, `inflight_solves_discarded=5`, `handover_keys_retained=2`, `hass_data_keys=4` | yes, exact (non-findings 1, 2, 8 reproduce) |
| `store_fuzz.py --mutants 20` (reduced) | `exception_escaped_mutants=0`, `repeat_failure_mutants=0`, `nan_published_mutants=1` — a `price_model` mutant (`model.shapes.0.7`, `logs=0`) publishing NaN into `data.price_prior.weekday_shape`, i.e. D1-01's mechanism found independently by the corpus | yes, directionally at 20/corpus-cell |

## My own harnesses (the per-panel requirement)

Both under `tools/audit/round4/D1/`, runnable from this worktree root with
`PYTHONPATH=tests/hastub`, thread pin first, `RESULT` lines, private store
disk, no writes outside their own dir.

- `verify0_3_d1_01.py` — **a different metric**: not the price array but the
  PLAN. One full `_async_update_data` cycle (real solve) with the corrupt
  store (weekend bin 22 = the JSON string `"nan"`, 10 of 48 horizon-hours
  published, Saturday-noon anchor):
  - `zero_priced_steps=4`, `control=0`, `null_control=0` (finder's metric,
    reproduced independently);
  - **`energy_shift_kwh=4.85`** — kWh of electrical space heating the solved
    plan schedules in the four zero-priced steps, corrupt minus control
    (control schedules **0.000 kWh** there: the hour is genuinely expensive,
    the corrupt plan dumps 4.85 kWh into it believing it free);
  - `true_cost_regression_sek=+0.094` — the corrupt plan's cost at the real
    (control) prices minus the control plan's, over the horizon, in my mild
    0.6–1.1 SEK/kWh synthetic profile. The money magnitude is
    profile-dependent; the plan distortion is not.
  - `--perturb` (in-process `np.isfinite` guard inside
    `PriceShapeModel.from_dict`): `zero_priced_steps=0`, shift `0.000`.
- `verify0_3_d1_02.py` — **the real-HA reachability re-measure**: the finder's
  harness calls `_async_load_accuracy()` directly and catches the exception
  itself; mine never touches the loader. It seeds the corrupt store, drives
  the FULL `ha_setup_entry` on a real loop with a real `ThreadPoolExecutor`
  and real `async_create_task` (so `_spawn` schedules the loader as a genuine
  background task), drains, runs two ordinary `_async_update_data` cycles
  (the scheduled-interval one calls `_async_save_accuracy`,
  `coordinator.py:4249`), then reads the store:
  - `fields_lost=3` (`peaks`, `defrost_factors`, `mode`), `control=0`;
  - `setup_ok=1`, `last_update_success_after=1`;
  - **`failure_time_loop_logs=0`, `warning_log_lines=0`** — nothing surfaces
    at failure time; the exception appears only later as the loop's deferred
    `Task exception was never retrieved` (1 line, at GC, not from the
    integration's logger). The finder's "zero log lines" holds at failure
    time with that one nuance, which their own "unretrieved background-task
    exception" wording already implies.
  - perturbation, variant 2 from the finding (`from_dict` skipping a
    non-list `samples`): `fields_lost=0`, peaks `[7.4, 6.8, 5.9]` and mode
    `economy` intact on disk. My first attempt wrapped the WHOLE loader in
    try/except — `warning_log_lines=1` but `fields_lost=3` still, because
    catching after the line that dies cannot restore the fields after it.
    That is not a failed perturbation, it is the wrong guard shape; the
    finding's wording ("wrap **the decode block**", or guard `from_dict`)
    is the correct one and behaves exactly as claimed.
- D1-INST probe (inline, script in the transcript of this report): after
  `ha_setup_entry`, three base-class refresh calls give
  `refresh_requests_counter=4`, `update_calls_via_base_class=0`,
  `flag_still_armed_after_refreshes=1`; one DIRECT `_async_update_data` call
  gives `flag_after_direct_update_call=0`.

## Attacks, in the contract's order

1. **Contention** — all metrics are counts or plan-content deltas;
   `load1` quoted above; no timing claim anywhere in these findings rests on
   my numbers.
2. **Wrong gate mode** — not applicable: neither finding is a mutant/golden
   claim; both hook production symbols (`PriceShapeModel.from_dict`,
   `extend_price_series`, `_async_load_accuracy`/`_async_save_accuracy`) and
   the numbers move under the stated perturbations.
3. **Aggregate artefact** — D1-01: the finder's 24-cell leave-one-out re-ran
   in their harness (14 cells reach, every one exactly 4 steps; range 4–4).
   I additionally corrupted the WEEKDAY bin at a Wednesday-noon anchor: also
   exactly 4 zero-priced steps, min price 0.0 — the mechanism is
   profile-symmetric, not a weekend artefact. (My first weekday probe
   returned 0; that was my own bug — `entry_id` mismatch meant the store key
   never matched and `days` loaded as `[0,0]`, prior unused. Corrected probe
   reproduces.) D1-02: I compared **all six** store keys in both arms, not
   just the finder's three: `peaks.peaks`, `defrost.factors` and `mode` are
   exactly the separating set — the control arm also rewrites `comfort`
   (configured weight 2.0 → 5.0 even on a healthy load) and adds additive
   `window_*` bookkeeping keys, so including them would have inflated BOTH
   arms. The finder's exclusion of `comfort`, with the reason stated in their
   harness, is honest.
4. **Null control** — present and passing in both findings (D1-01: whole
   horizon published → 0 zero steps and no plan shift; D1-02: well-formed
   `samples` → 0 fields lost). Both re-executed by me.
5. **Reachability in real HA vs the stub** —
   - D1-01: the corrupt payload is **strict JSON** — a plain string `"nan"`
     in the shapes list round-trips `json.dumps(..., allow_nan=False)` and
     `float("nan")` is NaN; no dependence on the stub's permissive `NaN`
     literal. `max(0.0, nan)` is `0.0` in CPython (checked). The price array
     feeds the real solve (`coordinator.py:4383`), and the real solve acts
     on it (4.85 kWh moved). The writer/reader asymmetry is real:
     `observe_day:137` rejects non-finite days, `from_dict:309-323` checks
     none.
   - D1-02: re-measured on a real loop with a real executor through the
     production `_spawn` path — setup succeeds, nothing surfaces at failure
     time, the store is wiped by the next ordinary cycle. The one thing a
     real loop adds over the finder's harness is the deferred loop-level
     GC complaint, recorded above; it does not change the consequence.
   - The trigger for both is an externally corrupted store file (the repo's
     own manual-plan loader names "a corrupted or hand-edited `.storage`
     file" as its threat model, and the ledger carries a "same corruption
     barrier" comment), so the threat model is the project's own.
6. **Severity earned by consequence** —
   - D1-01 high: a silently wrong money signal (free electricity) that the
     optimizer acts on maximally, no log, `last_update_success` untouched,
     persistent in memory (the NaN bin blends with every later observation:
     `(1-α)·NaN + α·x` stays NaN). My one softening datum: the measured
     true-cost regression in a mild synthetic profile is +0.09 SEK/horizon;
     with real winter profiles the loss scales with the peak-to-trough
     spread. High stands.
   - D1-02 high: permanent, silent loss of the month's billed capacity
     peaks, the learned defrost derate and the user's mode, on one corrupt
     scalar, with setup reporting success. High stands.
   - D1-INST: see the vote.

## D1-INST (instrument finding)

Executed: the stub's `async_refresh` / `async_config_entry_first_refresh` /
`async_request_refresh` only increment `refresh_requests`
(`update_calls_via_base_class=0` after three calls) — so **no gate-suite test
can run a cycle through the base class**, and the base-class refresh wiring
(the real debouncer, `UpdateFailed` → `last_update_success`, listener fan-out
on refresh) is unexercised by the suite. That much is real and I could not
refute it.

But both conjuncts of the finding's evidence are overstated:

- **"`_skip_solve_once` is never consumed in the suite" is false.**
  `tests/features.py:16688-16698` asserts the flag armed on the reloaded
  coordinator (`_ho_new._skip_solve_once`), consumes it with a direct
  `_async_update_data()` call at `:16691`, and asserts it cleared at
  `:16698` ("the handover is single-use on the coordinator too"). My probe
  confirms the same behaviour through `ha_setup_entry`. The set→consume
  transition IS covered — by a direct call, not by a base-class refresh,
  which is a narrower claim than the finding makes.
- **"no test in the tree" needs the nightly caveat.** `tests/nightly_ha.py`
  runs the integration inside the real `homeassistant/home-assistant` Docker
  image, where `async_config_entry_first_refresh` genuinely calls
  `_async_update_data` (its `_await_plan` even falls back to a real
  `async_refresh()` at `:2154`). It is in the tree but excluded from the
  gate (`tests/run.sh:289` skips it; it needs Docker and minutes). "No test
  in the gate suite" is true; "no test in the tree" is not.

What survives, corrected: *the stub's refresh entry points are counters, so
the base-class refresh path is unexercised by the gate suite.* That is a real
instrument gap of the kind `tools/audit/README.md` says must travel the
ordinary route — but with the `_skip_solve_once` evidence struck and the
nightly lane acknowledged. I vote **weaken**, severity **low**: no production
defect is demonstrated to hide behind it (the finder's own non-findings show
the cycles they drove directly behave), and the one concrete consequence the
finding claimed (the flag never consumed) is disproven by an existing suite
check.

## Votes

| id | vote | severity | my number |
|---|---|---|---|
| D1-01 | verify | high | `zero_priced_steps=4` (finder metric, independently reproduced; control 0, null 0) and `energy_shift_kwh=4.85` end-to-end through the real solve; perturbation 4→0 |
| D1-02 | verify | high | `fields_lost=3` through the real spawn path on a real loop (control 0, `setup_ok=1`, `last_update_success=1`, 0 failure-time log lines); perturbation 3→0 |
| D1-INST | weaken | low | `update_calls_via_base_class=0`, `refresh_requests_counter=4` (stub gap real); `flag_after_direct_update_call=0` and `tests/features.py:16688-16698` (the "never consumed" claim false); nightly lane in-tree but gate-excluded |
