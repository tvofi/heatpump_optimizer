# D1 panel — verifier 1 of 3

Baseline `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1`, run from this tree's root
with `PYTHONPATH=tests/hastub`. Box: 8-core Apple M1, 8 GB, python 3.11.5.
Stance: refute-first.

`exposure`: the three findings as handed to me (claim, harness, metric,
perturbation), `tools/audit/briefs/verifier.md`, `tools/audit/README.md`, the
finder's `REPORT.md` and harnesses, and the tree. No `gh`, no GitHub, no
register, no other verifier's output.

## Conditions

**Every number in this report is a count, a byte figure or a ratio of counts.**
No wall, CPU or RSS number is claimed anywhere, so no result here depends on a
quiet box and none needs a quiet-window re-take. Recorded per run all the same:

| run | `load1` | `thread_factor` | `swapins` | concurrent python |
|---|---|---|---|---|
| `stale_clock.py` (baseline) | 36.27 | 0.809 | 0 | 21 |
| `stale_clock.py --perturb` | 38.55 | 0.992 | 0 | 24 |
| `store_fuzz.py --repro` | 43.05 | 0.904 | 0 | 26 |
| `store_fuzz.py --mutants 200` | 51.02 | 1.002 | 0 | 20 |
| `lifecycle_realloop.py` (D1-02 arm) | 47.78 | 1.05 | 0 | 27 |
| `verify-1/v1_probe.py` (mine) | 57.39 | 1.002 | 0 | 19 |
| `verify-1/v1_scale_probe.py` (mine) | 45.50 | 0.432 | 0 | 15 |

The five BLAS thread variables are pinned to `"1"` before numpy is imported in
every script, mine included. I did not run `tests/stress.py`, did not run
`./tests/run.sh`, and did not take the gate lock.

## My own instruments

* `tools/audit/round3/D1/verify-1/v1_probe.py` — sections A/B/C, one per
  finding, each with a metric definition deliberately different from the
  finder's, stated in the file header beside the finder's.
* `tools/audit/round3/D1/verify-1/v1_scale_probe.py` — the side-probe that
  isolates *which* production line is the defect in D1-01.

Raw output: `verify-1/v1_probe_out.txt`, `verify-1/v1_scale_probe_out.txt`,
`verify-1/rerun_*.txt`.

---

## D1-01 — corrupt `thermal_learning` store wedges every cycle

**Vote: `verify`. Severity `high` (agree with the finder).**

### Step 1 — the finder's harness, re-run

Both commands reproduce exactly, no tolerance consumed.

```
store_fuzz.py --repro thermal_learning:163
  RESULT repro_wedge=1        (expected 1)
  RESULT repro_repeat=1       (expected 1)
  cycle1 = cycle2 = 'UpdateFailed: Error updating data: cannot convert float NaN to integer'

store_fuzz.py --mutants 200        (2400 mutants, 12 stores, ~9 min)
  RESULT wedge_total=1   repeat_total=1   poison_total=0   silent_total=0
  RESULT store_thermal_learning_wedge=1 ... every other store 0 of 200
```

### Step 2 — my own number, my own metric

**Finder's metric:** mutants, out of 200 seeded per Store key, whose corrupt
payload makes a real cycle raise and whose next cycle raises alike.

**My metric:** given a `thermal_learning` payload that is **strictly valid RFC
8259 JSON** — no bare `NaN`/`Infinity` token anywhere in the serialised bytes,
so any conforming parser round-trips it — how many of **five** consecutive real
`_async_update_data` cycles raise, and does the payload on disk change between
cycle 1 and cycle 5?

```
RESULT A_strict_json_ok=1
RESULT A_bare_nan_token_in_bytes=0
RESULT A_nan_string_cycles_failed=5 of 5        store_rewritten_between_cycles=0
RESULT A_infinity_string_cycles_failed=5 of 5   store_rewritten_between_cycles=0
RESULT A_null_control_finite_string_cycles_failed=0 of 5
```

### Step 3 — attacks

**Reachable in real Home Assistant, or a stub artefact? — the finder's own
caveat, and it is removable.** The finder flagged this itself and was right to:
its mutant is a Python `float('nan')` serialised by
`store_fuzz.py:_dumps` with `json.dumps(..., allow_nan=True)`, which emits the
bare token `NaN`; `tests/hastub`'s `Store` round-trips with stdlib `json`, which
accepts that token. Real Home Assistant writes and reads `.storage` with orjson,
which is RFC 8259 strict and emits/accepts neither. So against the finder's own
payload the caveat is live.

It does not survive contact with the code. `coordinator.py:2544` is

```python
self._solar_aperture[key] = float(raw_ap.get(key, self._solar_aperture[key]))
```

— a `float()` of whatever the parser returned. The JSON **string** `"nan"` is an
ordinary JSON string, contains no bare token, and `float("nan")` is NaN. I
seeded exactly that, asserted `json.dumps(payload, allow_nan=False)` succeeds
and that the resulting 884 bytes contain zero unquoted `NaN`/`Infinity` tokens,
and got 5 of 5 cycles raising with the loaded value `nan`. `"Infinity"` is the
same route with `OverflowError`. **The wedge does not need a payload orjson
would refuse.** Caveat discharged, in the finding's favour.

**Is the defect the `int()`, as claimed?** Measured, not argued. The same
strictly-valid `"nan"` seeded into the sibling slots that are `float()`-ed
rather than `int()`-ed:

```
RESULT scale_probe_solar_aperture_scale_cycles_failed=0 of 3
RESULT scale_probe_solar_aperture_var_cycles_failed=0 of 3
RESULT scale_probe_solar_aperture_n_cycles_failed=3 of 3
```

Absorbed in both `float()`-ed slots, fatal only in the `int()`-ed one. The
finder's causal claim holds under an independent probe.

**Is it self-inflicted rather than store-borne?** No, and this scopes the
finding correctly. `coordinator.py:8536-8539` (`_fold_solar_aperture`) only ever
does `m["n"] += 1.0`, behind an `np.isfinite(y)` guard, from a base of `0.0`, so
`n` cannot go non-finite in normal operation. The snapshot rollback at
`coordinator.py:8741-8745` resets it to `0.0` and re-parses through the same
`:2544` loader, so it is a second persistence route into the same defect, not a
separate one.

**Null control.** Present and passing, at two levels: the identical slot with an
identical-type finite value (`"0.0"`) is 0 of 5, and 2399 of 2400 of the
finder's mutants are absorbed.

**Severity earned?** `high`. The consequence is total and permanent —
`last_update_success` False, every entity unavailable, no plan, no actuation,
the store neither rewritten nor quarantined (`store_rewritten_between_cycles=0`
at cycle 5), until the user hand-edits `.storage`. Not `critical`: the pump
holds comfort on its own weather-compensated curve by design, so this is not
silent wrong comfort or wrong money, and it is not data loss or an unreachable
host. It does need a corrupt `.storage` file to start with (a restored backup,
hand editing, third-party tooling) — but the loader at `:2540` is visibly trying
to sanitise this field and is one `np.isfinite` short, which is what makes it a
defect rather than a hazard.

**One caveat about the finder's metric, for the judge.** "1 of 200" is the
probability that a *random* mutation lands in that one slot, not the probability
the defect fires. Conditional on the slot, it is 5 of 5 cycles, twice over (NaN
and inf). The rate is an artefact of the fuzzer's seeding and should not be read
as rarity of the defect. The two definitions measure different things and are
not comparable; mine is the conditional one.

---

## D1-02 — the reload plan handover has no expiry

**Vote: `verify`. Severity `medium` (agree with the finder; I would not raise it).**

### Step 1 — the finder's harness, re-run

```
lifecycle_realloop.py --complete-solve --lifecycles 1 --solve-seconds 0
  RESULT republished_plan_age_minutes_published=0.0        (expected 0.0)
  RESULT republished_plan_true_age_minutes=10080.0         (expected 10080.0)
  RESULT republished_plan_stale_flag=False
  RESULT republished_plan_is_the_prereload_one=1
  RESULT republished_plan_next_optimization_in_past=1
  RESULT plan_handover_entries_after_plain_unload=1        (expected 1)
  RESULT plan_handover_bytes_retained=81334                (finder: 81121)
```

The only difference is `plan_handover_bytes_retained`, 81334 against 81121
(+0.26%). That figure is `len(repr(v))` over a payload carrying ISO timestamps,
so it moves with the clock; it is not a discrepancy in the claim.

### Step 2 — my own number, my own metric

**Finder's metric:** the `plan_age_minutes` published for a handover payload
republished after `--gap-days`, against that payload's true age.

**My metric:** over the **first three** published payloads after the post-gap
setup, how many carry a `plan_age_minutes` that understates the true age of the
plan they describe by more than 60 minutes — i.e. how long the wrong value
survives, in cycles, not just what its first value is. Driven through the real
`async_unload_entry` (the stash, `__init__.py:331`) and the real
`_plan_handovers(hass).pop(...)` (`__init__.py:223`).

```
RESULT B_payloads_with_wrong_age=1 of 3
RESULT B_true_plan_age_minutes=10080.0
  cycle1: plan_age_minutes=0.0 plan_stale=False is_prereload_plan=1 understated_by=10080.0  miss=1
  cycle2: plan_age_minutes=0.0 plan_stale=False is_prereload_plan=0 understated_by=0.0      miss=0
  cycle3: plan_age_minutes=0.0 plan_stale=False is_prereload_plan=0 understated_by=0.0      miss=0
RESULT B_retained_entries_no_setup=1
RESULT B_retained_json_bytes=63975
RESULT B_integration_defines_async_remove_entry=0
```

**The lie is exactly one published payload wide.** Cycle 2 consumes
`_skip_solve_once`, solves, sets `_last_optimization`, and recomputes
`_plan_age_minutes()` honestly — `is_prereload_plan=0`, so the 0.0 it publishes
is the true age of a genuinely fresh plan. `__init__.py:255-258`'s comment
("replaces it within the first update cycle") is accurate. The finder did not
measure this; it is the number that decides the severity.

Note on units: my `B_retained_json_bytes=63975` is `json.dumps` bytes; the
finder's `81334` is `len(repr(v))`. Different rulers over the same object — the
judge should not treat them as the same figure.

### Step 3 — attacks

**Reachable in real HA, or a stub artefact?** Reachable, and no stub trap
applies. This is not a concurrency claim, so `FakeHass.async_add_executor_job`
running inline and `FakeHass.async_create_task` closing coroutines are both
irrelevant to it — and the finder used `d1lib.RealLoopHass` anyway. The finder's
arm drives `tests/harness.py:ha_setup_entry`/`ha_unload_entry`, which I read
against HA's config-entry order (`SETUP_IN_PROGRESS` → `async_setup_entry` →
`LOADED`; unload → `async_unload_entry` → `async_on_unload` callbacks →
`runtime_data` deleted → `NOT_LOADED`) and found faithful, one operation at a
time per entry. Disable-then-re-enable is an ordinary user action that produces
exactly this unload/setup pair with an unbounded gap.

**Is the severity earned by consequence?** `medium` is right, and the finder did
not overstate it. Two things bound the harm, and both are measured or read:

1. **Nothing actuates on the stale plan.** `coordinator.py:4592-4595` returns
   from `_async_first_refresh_light()` before `_apply_action` is ever reached,
   so the 7-day-old action is published but never commanded. No wrong money, no
   wrong comfort — which is what would have made it `high` or above.
2. **One payload, then it self-corrects** (`B_payloads_with_wrong_age=1 of 3`).
   And if the post-gap solve fails instead, `coordinator.data` keeps the
   handover but `CoordinatorEntity.available` (`sensor.py:187`, `super().available`)
   turns every entity unavailable, so the stale payload is not shown either way.

A wrong published value nominally meets the stated `high` bar, but one payload
wide, driving no output, on a path the user reaches by re-enabling a disabled
entry, is a `medium`. I would not raise it and I would not lower it.

**The retention half.** Confirmed and correctly worded. `1` entry retained after
a plain unload with no setup following, ~64 KB, and the integration defines no
`async_remove_entry` to clear it. It is bounded — one payload per entry id,
never persisted, gone at restart — so "retained for the life of the process" is
exactly right and "leak" would overstate it.

**Grid artefact?** Not applicable; no aggregate over a grid is claimed. Null
control present and passing (`--no-plan`: entries 1 → 0, bytes 81121 → 0), plus
the finder's own `--gap-days 0.0007` arm showing the published number is right
only when the gap is nil.

---

## D1-03 — the staleness watchdog is off after a backward clock step

**Vote: `verify`. Severity `high` (agree with the finder).**

### Step 1 — the finder's harness, re-run

Every expected value hit exactly.

```
stale_clock.py
  RESULT guarded_readings=11        stale_honest=9
  RESULT stale_stepped_back=0       stale_stepped_forward=11
  RESULT age_reported_stepped_back_min=0.0   ..._max=0.0
  RESULT learners_frozen_honest=4 of 4       learners_frozen_stepped_back=0 of 4
  health stepped_back = 'ok'
```

### Step 2 — my own number, my own metric

**Finder's metric:** guarded readings flagged `problem=='stale'` in one real
`_update_current_state()` cycle over 12 configured entities all silent for 3 h,
under no step / a 4 h backward step / a 4 h forward step.

**My metric:** over a **grid** of (sensor silence × backward step) — 7 silences
× 8 steps = 56 cells, one guarded read per cell — the fraction of cells in which
the reading's *true* silence exceeds that read's own `max_age_minutes` but
`_age_gate` did not set `problem=='stale'` (a "watchdog miss"). Driven straight
through `inputs.py:InputReader.read` with an injected `now`, so no clock
freezing and no coordinator are involved.

```
RESULT C_grid_cells=56
RESULT C_watchdog_misses=13
RESULT C_watchdog_miss_fraction=0.2321
RESULT C_misses_at_zero_step=0 of 7
RESULT C_misses_at_nonzero_step=13 of 49
RESULT C_misses_reporting_age_exactly_zero=11

  back  0.00 h  misses 0/7        back  2.00 h  misses 2/7
  back  0.25 h  misses 0/7        back  4.00 h  misses 2/7
  back  0.50 h  misses 0/7        back  8.00 h  misses 3/7
  back  1.00 h  misses 1/7        back 24.00 h  misses 5/7
```

### Step 3 — attacks

**Grid artefact?** This is the attack the finding most needed, because the
finder reported a single (3 h silence, 4 h step) cell and one cell cannot
distinguish a structural failure from a lucky coordinate. It is structural: 0
misses at zero step, and the miss count rises monotonically with the step
magnitude across seven non-zero steps and seven silences. Dropping any single
row or column leaves the pattern intact.

**Perturbation — does the number move?** Executed, and it moves in the stated
direction with both controls flat, so the finding is not void:

```
stale_clock.py --perturb
  stale_stepped_back      0 -> 11    (UP)
  stale_stepped_forward  11 -> 11    (control, flat)
  stale_honest            9 ->  9    (control, flat)
  learners_frozen_stepped_back 0 of 4 -> 4 of 4
```

**Reachable in real HA, or a stub artefact?** Reachable. Neither `InputReader`
construction site (`coordinator.py:3182`, `coordinator.py:5335`) passes a `now=`
callable, so `_utcnow()` falls through to `dt_util.utcnow()` — the wall clock.
The stub's `utcnow()` is `datetime.now(timezone.utc)`, the same wall-clock read
real HA makes, and `State.last_reported`/`last_updated` are wall-clock datetimes
in both. No executor and no task scheduling are involved, so the two `FakeHass`
traps do not touch this path at all. **One part I could not execute:** whether
HA core interposes any clamp of its own between the system clock and
`last_reported`. I read no such thing in the stub contract and know of none, but
I have no HA core checkout here, so that step is reasoned, not measured.

**Severity earned?** `high`. Two consequences, both measured: `input_health`
publishes `'ok'` while all 11 guarded readings are unreadable (a wrong published
value), and the learner freeze is entirely off (`0 of 4`) — the freeze whose own
comment at `_learning_frozen` records a dropped sensor walking the house
heat-loss scale from 1.0 to ~0.37 in 48 h with the corruption outliving the
outage by weeks. That is a persisted-parameter corruption, which is the
expensive direction. Not `critical`: it needs a backward clock step to coincide
with a dead sensor, and the exposure is bounded by the step width.

**A correction to the finder's framing, and a warning about its own fix.** The
claim says a backward step makes "every configured input ... report age 0.0".
The real mechanism is broader: a backward step under-reports *every* reading's
age **by the step**, and `max(0.0, ...)` floors it at 0.0 only once the step
exceeds the silence. 11 of my 13 misses report exactly 0.0; the other two
(back 1 h/silence 2 h and back 2 h/silence 3 h) report `60.0` and are missed
because the under-reported age no longer exceeds the 60-minute limit.

That matters for the remedy, not the verdict: **the finder's own perturbation —
return `inf` when `stamp > now` — leaves those two cells still missed**, because
in them the stamp is not in the future. It is a valid perturbation (it moves the
finding's number 0 → 11) and it is not a complete fix. Worth handing forward to
whoever fixes this.

---

## Side-note, not a vote

`v1_scale_probe.py` shows a strictly-valid `"nan"` in `solar_aperture.scale`
is absorbed (0 of 3 cycles fail) but leaves `solar_aperture.scale=nan` in the
**data dict** returned by `_build_data_dict`. This does **not** contradict the
finder's `poison_total=0`: `HeatPumpOptimizerSensorBase.__init_subclass__`
scrubs non-finite values out of `native_value` and `extra_state_attributes`, so
the finder measured downstream of the scrub and I measured upstream of it. Two
measurement points, no disagreement. (`peak_threshold_kw=inf` appears in the
control arm too and is a healthy "no peak limit" sentinel, not corruption.)
Recording it because a consumer of `coordinator.data` that is not a sensor would
not get the scrub.
