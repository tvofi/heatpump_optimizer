# D1 — Robustness and stability (round 3)

Baseline `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1`. Box: 8-core Apple M1, 8 GB,
python 3.11.5, numpy 2.4.6. **The box was not quiet**: `load1` ran between 15
and 207 across the session (eleven other agent sessions, none of them mine).
Every number below is a **count**. No wall, CPU or RSS number is claimed
anywhere in this report, so nothing here needs a quiet-window re-take.

`exposure`: none. `docs/audit-*.md`, `docs/backlog.md` and `RELEASE_NOTES.md`
are absent from this export and were not sought; no `gh`, no GitHub, no earlier
round's findings. A `D1-02` id appears in a code comment at
`coordinator.py:1340`; that is context in the tree, not a finding I read.

## Method

### The harness gap this dimension lives or dies on

`tests/harness.py:FakeHass.async_add_executor_job` runs the job **inline on the
calling thread**, and `FakeHass.async_create_task` **closes** the coroutine and
returns `None`. Under that stub:

* a solve is never in flight, so no lifecycle race can exist to be measured;
* **none of the 13 store loaders the coordinator's constructor spawns ever
  runs** (`coordinator.py:1341-1357`), so a store-corruption claim built on it
  measures nothing at all.

`tools/audit/round3/D1/d1lib.py:RealLoopHass` subclasses `FakeHass` and
replaces both: `async_add_executor_job` parks on a real `ThreadPoolExecutor` on
a real `asyncio` loop, `async_create_task` schedules on that loop, and every
task it creates is tracked so a harness can await or count it. Every claim
below was taken through it.

### Real Home Assistant semantics

Every lifecycle transition in `lifecycle_realloop.py` goes through
`tests/harness.py:ha_setup_entry` / `ha_unload_entry`, which are the
config-entry state machine's own order (`SETUP_IN_PROGRESS` ->
`async_setup_entry` -> `LOADED`; unload -> `async_unload_entry` -> the
`async_on_unload` callbacks -> `runtime_data` deleted -> `NOT_LOADED`). No
lifecycle method is called outside that order, and no two lifecycle operations
overlap on one entry. The one concurrency the harness does create — a refresh
task still parked in the executor when the unload runs — is the case
`coordinator.py`'s own `#237` comments name ("the executor await above is
seconds wide, and an options save inside it unloads the entry"), so it is
reachable in real HA by an options save landing mid-solve.

`tests/hastub`'s `DataUpdateCoordinator` counts `async_config_entry_first_refresh`
instead of running it and never assigns `.data`; the harness drives the light
first refresh explicitly and assigns its result to `.data`, which is what the
real base class does and what `async_unload_entry` reads. That is stated here
because it is the one place the harness stands in for the base class.

### Cost note on the fuzz

The 2400-mutant fuzz replaces the **numerical solve** with
`tests/harness.py:CapturingOptimizer` — the picklable stub `tests/dst_checks.py`
already submits to the real process worker. Everything else in the cycle is
real and unmodified: all 13 loaders, every learner, the accuracy pairing, the
drift heartbeat, the actuation, the store writes, `_build_data_dict`, and the
executor/process boundary itself (`_solve_snapshot` is still called, still
deep-copies, and the job still crosses into the child interpreter). The
L-BFGS-B search costs ~1.0 s per cycle and 4800 cycles of it does not fit in a
fan-out; it is also D0/D2/D9's dimension, not D1's. `--real-solve` restores it
for a subset. **The one wedge found reproduces with the real solve too** — its
exception is raised in `_build_data_dict`, downstream of the solve.

---

## Findings

### D1-01 — a corrupt learner store turns into a permanent `UpdateFailed`, every cycle, forever (high)

`int(self._solar_aperture["n"])` at `coordinator.py:6960` is unguarded. A
`thermal_learning` store whose `solar_aperture.n` is non-finite passes the
loader's own type guard (`coordinator.py:2540-2553` catches
`TypeError/ValueError/OverflowError`, and `float("nan")` raises none of them;
only `scale` is clipped), and then every `_async_update_data` raises
`UpdateFailed("cannot convert float NaN to integer")` — cycle 1, cycle 2,
cycle 3, with the store never quarantined and never rewritten. The integration
is dead: `last_update_success` False, every entity unavailable, no plan, no
actuation, until the user deletes the `.storage` file by hand.

```
PYTHONPATH=tests/hastub python3 tools/audit/round3/D1/store_fuzz.py --repro thermal_learning:163
  DIFF solar_aperture: {'n': 0.0, ...} -> {'n': nan, ...}
  RESULT repro_wedge=1
  RESULT repro_repeat=1
```

Out of the full sweep — **2400 seeded mutants, 200 per store, 12 stores, each
loaded through the real loader and run for two real cycles**:

| store | mutants | wedge | repeat | poison | silent |
|---|---|---|---|---|---|
| accuracy, away, boost, dhw_draws, dhw_legionella, dhw_profile, energy, ledger, manual_plan, price_model, snapshots | 200 each | 0 | 0 | 0 | 0 |
| **thermal_learning** | 200 | **1** | **1** | 0 | 0 |

`wedge_total=1`, `repeat_total=1`, `poison_total=0`, `silent_total=0`.

The 2399 mutants that are absorbed are the null control: the same operator
(`type-swap`) applied to the same slot with a **finite** value is absorbed
silently, and every non-finite value in a slot that is `float()`-ed rather than
`int()`-ed is absorbed too. The defect is the `int()`, not the corruption.

The sensor-level non-finite scrub (`HeatPumpOptimizerSensorBase.__init_subclass__`)
cannot help here: the exception is raised inside `_build_data_dict`, before any
sensor reads anything.

**Reachability caveat, stated rather than glossed.** The fuzzer writes the
payload as JSON that Python's `json` module round-trips (`NaN` is accepted on
read). Whether Home Assistant's own orjson writer can put a bare `NaN` in a
`.storage` file was not measured here and should be checked before the severity
is finalised — but a `.storage` file is also restored from backups, edited by
hand, and written by third-party tooling, and the loader at `:2540` is visibly
*trying* to sanitise this field. It is one `np.isfinite` short.

### D1-02 — the reload plan handover has no expiry: a 7-day-old plan is republished with `plan_age_minutes: 0.0` and `plan_stale: false` (medium)

`__init__.py:async_unload_entry` stashes `coordinator.data` in
`hass.data["heatpump_optimizer_plan_handover"]` and `async_setup_entry` pops it
and hands it to `_async_first_refresh_light`, which returns it **"as-is, with
no fetches at all"**. Two consequences, one mechanism:

1. The payload carries its own pre-unload `plan_stale` and `plan_age_minutes`.
   They are **not recomputed**, so the republished payload asserts the plan was
   solved this instant however long ago it actually was.
2. Nothing pops it if no setup follows — the entry disabled, removed, or its
   setup failing. The payload stays in `hass.data` for the life of the process.

```
PYTHONPATH=tests/hastub python3 tools/audit/round3/D1/lifecycle_realloop.py \
  --complete-solve --lifecycles 1 --solve-seconds 0
  RESULT stashed_plan_stale_flag=False
  RESULT republished_plan_is_the_prereload_one=1
  RESULT republished_plan_stale_flag=False
  RESULT republished_plan_age_minutes_published=0.0
  RESULT republished_plan_true_age_minutes=10080.0      <- 7 days
  RESULT republished_plan_optimization_status='optimal'
  RESULT republished_plan_next_optimization_in_past=1
  RESULT plan_handover_entries_after_plain_unload=1
  RESULT plan_handover_bytes_retained=81121
```

Two controls, both run:

* `--gap-days 0.0007` (one minute): published age `0.0`, true age `0.0`. The
  published number is right exactly when the gap is nil — it never moves,
  which is the point.
* `--no-plan` (the coordinator publishes nothing, so there is nothing to
  stash): `plan_handover_entries_after_plain_unload` `1 -> 0`,
  `plan_handover_bytes_retained` `81121 -> 0`.

`__init__.py`'s own comment says "a stale payload must never outlive the one
reload it was made for". It does: the pop is keyed on the next setup of that
entry id, whenever that is, with no timestamp and no age check. On the ordinary
options-save reload the lie is seconds wide and harmless; on a
disable-then-re-enable it is unbounded. `plan_age_minutes`/`plan_stale` are
published (`coordinator.py:7130-7135`) and `_apply_action` declines to actuate
a stale plan (`:6710`) — but on this path both read the frozen pre-unload
values, so the guard that exists cannot fire.

### D1-03 — the staleness watchdog is entirely off while any state is stamped ahead of `now` (high)

`inputs.py:InputReader._age_minutes` ends
`return max(0.0, (now - stamp).total_seconds() / 60.0)`. A state whose
`last_reported` is ahead of `now` therefore reports **age 0.0** — "reported this
instant" — rather than "not knowable". `_age_gate` only flags stale when
`age > limit`, so 0.0 is maximum freshness, and every consumer downstream reads
it that way: `InputHealth`, the published `input_health` string, and
`_learning_frozen`.

The module's own docstring commits to the opposite: *"A dead sensor stops
reporting too, so the fail-closed intent is preserved"*, and
`_learning_frozen`'s comment records what the freeze is for — *"A flat battery
or a dropped Zigbee sensor walked the house heat-loss scale from 1.0 to ~0.37
inside 48 h, saved every 10 samples, and the corruption outlived the sensor
outage by weeks."* That is what this re-enables.

Twelve configured entities, all silent for three hours, one real
`_update_current_state()` cycle each:

| arm | stale flagged | learners frozen | published `input_health` |
|---|---|---|---|
| honest (no clock step) | 9 of 11 | 4 of 4 | `'9 stale'` |
| host clock **back** 4 h | **0 of 11** | **0 of 4** | **`'ok'`** |
| host clock **forward** 4 h | 11 of 11 | 4 of 4 | `'11 stale'` |

Every reading in the backward arm reports `age_minutes` exactly `0.0`
(`age_reported_stepped_back_min=0.0`, `..._max=0.0`).

```
PYTHONPATH=tests/hastub python3 tools/audit/round3/D1/stale_clock.py
PYTHONPATH=tests/hastub python3 tools/audit/round3/D1/stale_clock.py --perturb
```

`--perturb` applies the one-line fix by monkeypatch (a stamp ahead of `now`
returns `inf` instead of `max(0.0, ...)`), without touching the tree:
`stale_stepped_back` moves **0 -> 11**, while both control arms are unchanged
(`stale_stepped_forward` 11 -> 11, `stale_honest` 9 -> 9).

**A trap worth recording**: merely *dropping* the clamp does not move the
number. A bare negative age fails `age > limit` exactly as 0.0 does, so the fix
has to name the future stamp rather than stop clamping it. I measured that
first, got `0 -> 0`, and would have handed the judge a perturbation that voids
the finding.

Trigger class: any backward step of the host clock between a state being
written and being read — an NTP correction after the clock ran fast, a manual
clock set, a VM or container resumed with a fast clock. Whether Home Assistant
core can itself produce a `last_reported` ahead of `utcnow()` was not measured.

---

## Non-findings — what was checked and held

1. **Store corruption, 11 of 12 stores.** 2200 seeded mutants across
   `accuracy, away, boost, dhw_draws, dhw_legionella, dhw_profile, energy,
   ledger, manual_plan, price_model, snapshots` — field type swaps, deletions,
   `NaN`/`+-inf`, `1e400`, `+-1e30`, list truncation, dict truncation,
   re-nesting, and whole-payload swaps to `None`/`[]`/`""`/`0`/`"corrupt"`.
   Every one: cycle completes, next cycle completes, no published guard value
   leaves its physical envelope. `wedge=0 repeat=0 poison=0 silent=0` for all
   eleven.
   `PYTHONPATH=tests/hastub python3 tools/audit/round3/D1/store_fuzz.py --mutants 200`
2. **No listener, task or coordinator leak across reloads.** Three complete
   lifecycles, each with a solve parked in a real executor thread when the
   unload lands: `state_listeners_after=0`, `bus_listeners_after=0`,
   `live_tasks_referencing_dead_coord=0`,
   `dead_coordinators_held_by_tasks=0`, `escaped_exceptions=0`,
   `new_instance_first_cycle_ok=1`.
   `PYTHONPATH=tests/hastub python3 tools/audit/round3/D1/lifecycle_realloop.py`
3. **Nothing actuates after the entry is released.** `actuations_after_release=0`
   over three unload-mid-solve cycles. **Disproved lead, gap named:** the
   `#237` `_entry_released` latch is not what produces that zero on this path —
   `async_shutdown` cancels the in-flight refresh outright
   (`refresh_cancelled=3`), so the coroutine never resumes past the executor
   await to consult the latch. Running the same harness with `--no-latch`
   (the latch disabled by monkeypatch) still gives `actuations_after_release=0`.
   The latch is belt-and-braces on the path this harness reaches; a harness
   that wanted to exercise it would have to let the refresh survive the
   cancellation, which real HA does not do either.
4. **The forward clock step is safe.** A host clock stepping *forward* 4 h over
   the same dead sensors flags all 11 guarded readings stale and freezes all
   four learners — identical to the honest arm. Only the backward direction
   fails open (D1-03).
   `PYTHONPATH=tests/hastub python3 tools/audit/round3/D1/stale_clock.py`
5. **The plan-staleness surface exists and is published.** `plan_age_minutes`
   and `plan_stale` are in `_build_data_dict` (`coordinator.py:7130-7135`) and
   `_apply_action` refuses to actuate a stale plan in `auto`/`economy`
   (`:6710`). Both are correct on the ordinary path; D1-02 is only about the
   handover path, where they are copied rather than recomputed.
6. **A fresh instance always comes up.** After every corrupt-store trial and
   every torn-down lifecycle, `new_instance_first_cycle_ok=1` / the next cycle
   completes — with the single exception of D1-01's mutant, where it never does.

---

## What I could not finish

* **`_run_in_process` has no read timeout, and holds `_PROCESS_LOCK` across the
  whole IPC** (`coordinator.py:844-865`). A child that stops answering — as
  opposed to dying, which is handled and falls back correctly — blocks that
  executor thread forever, and every later solve blocks on the lock behind it;
  `_shutdown_process_pool` takes the same lock, so `EVENT_HOMEASSISTANT_STOP`
  would block too. I have no executed number for how a real child comes to hang,
  so this is **an argument, not a finding**, and it is recorded here rather than
  returned. `d1lib.RealLoopHass` plus `lifecycle_realloop.py:SlowSolve` is the
  scaffolding a follow-up would use.
* **The `--real-solve` arm of the fuzz.** 2400 mutants with the true L-BFGS-B
  solve is ~2.5 h of CPU and did not fit; the box reached `load1` 207 during
  the first attempt and it was killed. The flag exists and the one wedge
  reproduces under it.
* **DST transitions.** `tests/dst_checks.py` and `HASTUB_TZ` were not driven.
  The clock arms above are UTC steps, which is the mechanism `_age_minutes`
  actually sees; a DST arm would test `as_local`, a different surface.
* **Leave-one-out** does not apply: no number here is a mean over a grid. The
  fuzz table already reports every cell (12 stores x 200) rather than an
  aggregate.

## Harnesses

| path | what it produces |
|---|---|
| `tools/audit/round3/D1/d1lib.py` | `RealLoopHass`, the coordinator/input builders, the conditions RESULT lines. Not a harness; imported by all three. |
| `tools/audit/round3/D1/store_fuzz.py` | the 2400-mutant table, and `--repro thermal_learning:163` for D1-01 |
| `tools/audit/round3/D1/stale_clock.py` | the three clock arms for D1-03, and `--perturb` |
| `tools/audit/round3/D1/lifecycle_realloop.py` | the lifecycle leak counts and the handover numbers for D1-02, with `--no-plan` and `--no-latch` |

Every one runs from the repository root with `PYTHONPATH=tests/hastub`, pins
the five BLAS thread variables before numpy is imported, writes nothing outside
its own directory, and prints `thread_factor`, `load1` and the concurrent
python-process count beside its results. Nothing in the tree was modified: every
fault is injected by monkeypatch from the harness.
