# D1 verification — seat 2 of 3, round 4

Worktree `../audit-r4-verify-D1-2` at branch head `0855277` (finder measured
baseline `7dd68dd`). Every number below is a **count** or a **categorical**
outcome; nothing rests on wall time. `load1` was 2.6–5.0 during the runs
(other agents sharing the box) — quoted, not gated, and load-bearing for
nothing here. `thread_factor=1.0000` on all runs. My own harnesses:
`verify2_d101.py`, `verify2_d102.py`, `verify2_d1inst.py` alongside the
finder's, in this directory.

## Harness re-runs (finder's own instruments)

| harness | finder said | I got |
|---|---|---|
| `price_prior_zero.py` | zero=4, control=0, null=0, bins=14, per-bin 4–4 | identical (zero=4 at steps 40–43, control 0.6018 → 0.0; 14 bins reaching, 4–4; null 0) |
| `accuracy_wipe.py` | fields_lost=3/3, control=0, bool=3, warn=0, log=0, lus=1 | identical (exc `TypeError: 'float' object is not iterable`) |
| `store_fuzz.py --mutants 200` | nan_pub=16, strict=4, silent=6, persisted=91, escaped=0, repeat=0, multi_log=0 | identical, per-store table identical (price_model 6/3/6/58) |
| `real_loop.py --cycles 5 --inflight` | all zeros, first_cycle_ok=5, inflight discarded=5 | identical (also `--break` sensitivity taken on trust of the same run pattern; not re-taken) |

## D1-01 — corrupt price-shape bin prices planning steps at 0.0 SEK/kWh

**Vote: verify, high.** My number: `solver_zero_steps=4` of 96 (control
0.4054 SEK/kWh at those steps → 0.0), control 0, null control 0.

**My own method** (`verify2_d101.py`, differs from the finder's): Wednesday
noon anchor (finder: Saturday), WEEKDAY profile bin 3 (finder: weekend bin
22), 8 published hours (finder: 10), and the price array read as the *solver
input* of a real `async_run_optimization()` (the finder read
`_forecast_arrays()[0]` without solving). Executed:

```
RESULT solver_zero_steps=4  control=0  null=0  differing_steps=4 (idx 60-63)
RESULT plan_slots_shifted=1  (space slot 1: 4.41 -> 4.43 kW; moved 0.00 kWh)
RESULT perturb_solver_zero_steps=0  perturb_control=0
price_prior.weekday_shape[3] published as nan in coord.data
max(0.0, nan) == 0.0   (verified)
```

Metric definitions differ in anchor/profile/bin/window and in reading the
array from inside a real solve; both give 4. The finder's metric
(`_forecast_arrays()[0]` zeros) and mine (zeros in the same array the solver
consumed) are the same quantity measured at two depths — I judge them
comparable, and the plan consequence (slots shifted) is mine alone.

**Attacks, in the contract's order:**

1. *Contention*: counts only; immune. (wall_s 0.1–4.2, load1 2.6–3.3 quoted.)
2. *Gate mode*: no golden-fixture or mutant-selection claim rests here; N/A.
3. *Aggregate artefact*: the finder's 24-cell leave-one-out re-executed
   (14 cells reach the tail in a 24 h horizon, every one gives exactly 4,
   drop-most-favourable 52). My cell is a 25th, different anchor and
   profile: 4. Not a grid artefact.
4. *Null control*: present and passing in both harnesses — full 48 h
   published ⇒ prior never consulted ⇒ 0 zeros.
5. *Reachability, real HA vs stub*: the mechanism needs only (a) a
   strict-JSON string `"nan"` surviving any parser real HA uses, (b) CPython
   `float("nan")`, (c) `max(0.0, nan) → 0.0`. No FakeHass semantics on the
   path; the storage stub only stands in for disk. Two preconditions worth
   stating: `days[profile] >= 1` (a learned store — the harnesses use 30;
   with days=0 the prior is not consulted and the effect vanishes), and the
   guessed tail must cover the corrupt hour. Both hold for any real
   learned install before the afternoon price publication. Caveat I could
   not close: whether real HA's storage serializer round-trips the NaN back
   to disk across a restart (orjson not installed here; the stub's `json`
   emits the non-finite literal, `corrupt_persisted=58` for price_model).
   This affects only restart persistence, not the in-session free pricing;
   the finder also did not rest on it.
6. *Severity*: silent wrong solver input (4 of 96 steps at 0.0 vs 0.4–0.6
   SEK/kWh) plus a `nan` in the published `price_prior.*_shape` attributes
   (my run; also the fuzz's `nan_pub` column). "Wrong published value" is
   the `high` definition; `critical`'s "wrong money silently" is arguable
   but the trigger is an externally corrupted store — `high` as filed is
   earned, not inflated.

Code confirmed by reading: `price_model.py:320-323` (`float(v)` in a
try/except with no finiteness check), `observe_day:137` (writer rejects
non-finite — strictly stronger than the reader), `extend_price_series:445`
(`max(0.0, model.predict(...))`). The perturbation works exactly as stated
and I executed it: an `np.isfinite` gate inside `from_dict`'s shape branch
(must raise *inside* the existing try — note `_async_load_price_model`
does **not** wrap `from_dict`, coordinator.py:6767) drops the corrupt arm
to 0 with the control at 0.

## D1-02 — one corrupt scalar in the accuracy store destroys the store

**Vote: verify, high.** My number: `fields_lost=3` of 3 **on a real loop
through the real setup path**, `unretrieved_exceptions=1`, `setup_ok=1`,
`last_update_success=1`, `warn_log_lines=0`.

**My own method** (`verify2_d102.py`): the finder called
`_async_load_accuracy` directly on a `FakeHass` and caught the exception
itself — the real-HA claim (spawned task, setup survives, silent) rested on
code reading. I closed that gap: `RealHass` (executor on a
`ThreadPoolExecutor`, `async_create_task` schedules), corrupt store seeded
on disk *before* `ha_setup_entry`, then the ordinary cycle the real
integration runs (`_async_update_data` light, then full — the full path
itself saves accuracy at coordinator.py:4249). Executed:

```
control : setup=1 lus=1 task_excs=[] warn=0 lost=[]
corrupt : setup=1 lus=1 task_excs=["TypeError: 'float' object is not iterable"]
          warn=0 lost=[peaks, defrost_factors, mode]
          peaks [7.4,6.8,5.9] -> []   mode economy -> auto
perturbB: setup=1 lus=1 task_excs=[] warn=0 lost=[]   (from_dict skips
          a non-list samples)
```

The loop itself printed the real-HA trace at task GC on stderr ("Task
exception was never retrieved … `_async_load_accuracy` … TypeError") — that
is the one line a real install eventually sees, from the `asyncio` logger,
naming no store and no recovery path.

**Attacks:**

1. *Contention*: counts; immune. 2. *Gate mode*: N/A. 3. *Aggregate*: not
   an aggregate; the fuzzer's 2400-mutant run confirms 0 escapes elsewhere
   and its note that the random walk rarely selects `accuracy.samples`
   (reproduced: `exception_escaped_mutants=0`, so the targeted harness is
   the right instrument). 4. *Null control*: healthy store ⇒ 0 lost, 0
   exceptions — passing in both harnesses. 5. *Reachability*: executed on
   a real loop (above); `_spawn` (coordinator.py:1450-1462) keeps the task
   in `_background_tasks` with a discard-only done callback, so the
   exception is never retrieved; nothing in the scheduled refresh depends
   on the accuracy load. One honest correction to the finder's wording:
   "zero log lines at any level" holds for the integration's loggers; the
   `asyncio` GC line above does appear in a real install (once, at GC).
   6. *Severity*: silent, permanent-until-relearned destruction of
   money-bearing state (the capacity-tariff peaks the tariff is billed on,
   the defrost derate table) plus an immediate user-visible behaviour
   change (mode `economy → auto`). `critical`'s "data loss" is arguable;
   the corruption precondition supports `high` as filed. Not inflated.

Code confirmed: `_async_load_accuracy` (coordinator.py:6857) wraps only
`async_load()`; `accuracy.py:363` iterates `data.get("samples", []) or []`
(a *truthy* scalar raises — `1.0`, `True`; falsy scalars fall to `[]` and
are safe, a smaller exposure than "a scalar" suggests). Sibling asymmetry
confirmed: `_async_load_thermal_learning` guards each field,
`MonthlyLedger.from_dict` is internally defensive (ledger.py:228+,
quarantine + warning), and the fuzz shows 0 escapes over 2400 mutants
everywhere except this one key.

**One imprecision found** (does not change the vote): the stated
perturbation promises `fields_lost → 0` *and* `warning_log_lines → 1` from
either variant. Executed: variant A (wrap the whole decode, one warning)
gives `perturbA_fields_lost=3, perturbA_warning_lines=1` — it announces but
still loses the fields, because the raising line precedes the peaks/mode
assignments; variant B (skip non-list samples) gives `fields_lost=0` with
no warning. Only a per-field or from_dict-level fix (B) prevents the loss.

## D1-INST — the update_coordinator stub never runs a cycle

**Vote: weaken.** The instrument defect is real and I executed it; the
finding's stated consequences are two-thirds wrong.

**Executed** (`verify2_d1inst.py`, real `async_setup_entry` under the stub):

```
RESULT stub_refresh_cycles_run=0     (two awaited refresh methods, 0 cycles)
RESULT refresh_requests=3
RESULT skip_flag_after_setup=1       (armed through setup; stub consumed it
                                      not)
RESULT skip_flag_after_direct_call=0
```

So claim (A) — `tests/hastub/.../update_coordinator.py`'s
`async_refresh` / `async_config_entry_first_refresh` / `async_request_refresh`
only increment a counter and never call `_async_update_data` — is true by
execution and by reading the 54-line stub.

But the consequence sentence has two parts, both overstated:

- *"`_skip_solve_once` … is never consumed [in the suite]"* — **false.**
  `tests/features.py:16284-16299` sets the flag and consumes it via a
  direct `_async_update_data()`, with the check "the flag is consumed by
  the light refresh" at :16296; `tests/features.py:16660-16698` builds the
  coordinator through the real `_ha_setup_entry`, checks "the reloaded
  coordinator arrives with the skip-solve flag armed" (so
  `__init__.py:288`'s set is covered), then consumes it and checks it is
  cleared. features.py runs in the gate (not in run.sh's skip list). A
  mutation deleting `coordinator._skip_solve_once = True`
  (`__init__.py`) or the consume (`coordinator.py:4163`) is caught by
  these checks — I re-executed the same transitions in my probe.
- *"no test in the tree runs a cycle through the base class"* — **false
  without a scope qualifier.** `tests/nightly_ha.py` runs the integration
  inside the real `homeassistant/home-assistant` container and awaits
  `coordinator.async_refresh()` (:1237, :1252, :2154) against the *real*
  base class, including failure/unavailability semantics (its A4 checks)
  and the deferred first solve (`_await_plan`, :2141-2157). It is,
  however, excluded from the local gate (`tests/run.sh:286-289` skips it;
  Docker, nightly only). The correct statement is: **no gate-suite test
  runs a cycle through the base class; the real base-class cycle runs only
  in the nightly container lane.**

What genuinely remains uncovered in the gate: the base class's *reaction*
to the integration's contract — `UpdateFailed → last_update_success False →
entities unavailable` is asserted nowhere under the stub (features.py:16330
checks only that the fetch *raises* `UpdateFailed`); nightly_ha.py's A4
owns exactly that. The wiring call itself is covered
(features.py:16793-16816 patches `async_config_entry_first_refresh` to
raise `ConfigEntryNotReady` and requires setup to fail).

Severity: `low` as an instrument finding — a gate-lane coverage hole with
two compensating controls in the tree (features.py direct-call checks,
nightly real-HA lane), not a silent vacuum. The finder's own framing
("recorded here so the next auditor does not spend the same hour") is
closer to a non-finding note than a finding; per the README's
instrument-defect rule it may still travel, but with the corrected
consequence and severity.

## Metric definitions I measured under

- D1-01: steps of the 96-step planning price series (read as the input of a
  real solve) priced exactly 0.0 SEK/kWh with one strict-JSON `"nan"` bin in
  the persisted weekday shape, 8 of 48 horizon hours published; matched
  control = finite bin; null control = whole horizon published.
- D1-02: of {peaks, defrost_factors, mode} in the accuracy store on disk,
  how many differ from the seeded healthy payload after real
  `async_setup_entry` + one full ordinary cycle on a real loop, plus the
  count of unretrieved exceptions among setup's spawned tasks.
- D1-INST: how many times `_async_update_data` executes when the stub's
  `async_refresh` and `async_config_entry_first_refresh` are awaited (0),
  and whether `_skip_solve_once` survives setup armed (1) and is cleared by
  one direct call (0).
