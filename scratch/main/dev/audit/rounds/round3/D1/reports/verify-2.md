# D1 panel — verifier 2 of 3 (refute-first)

Baseline `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1`, run from
`.../audit-r3/verify/D1-2` with `PYTHONPATH=tests/hastub`. Python 3.11.5,
numpy 2.4.6, 8-core Apple M1.

**Conditions.** The box is shared. Across my runs `load1` ranged **23.68 –
48.36**, concurrent python processes **15 – 26**, and `thread_factor` **0.073 –
1.218** — both tails are contention on the shared `thread_factor` probe itself
(a few milliseconds of numpy), not a threaded BLAS: the five thread variables
are pinned to `"1"` before numpy is imported in every harness, mine and the
finder's. The README rejects a `thread_factor > 1.05` only for a *timing or
memory* RESULT. **No number in this report is a wall, CPU or RSS number** —
every one is a count, a byte count of a JSON payload, or a duration in
*simulated* minutes on a frozen clock. Nothing here needs a quiet window and
nothing here is marked `unresolved` for contention. I did not run
`tests/stress.py`, did not run `tests/run.sh`, and did not take the gate lock.

**Exposure.** `tools/audit/briefs/verifier.md`, `tools/audit/README.md`,
`tools/audit/briefs/COMMON.md` (severity rubric only), the finder's
`REPORT.md` and its three harnesses, and the production tree. No `gh`, no
GitHub, no register, no other verifier's output.

**Tree integrity.** One check below edits `custom_components/heatpump_optimizer/inputs.py`
in place; it is restored and the sha256 is verified identical
(`d276dc220a80c0e74e18ebf20ce6b3a553142166f4539aca4369b6ea47fadd10` before and
after). Everything else is monkeypatch-only. My own work is under
`tools/audit/round3/D1/verify-2/`.

| my harness | what it produces |
|---|---|
| `verify-2/strict_json_wedge.py` | D1-01 reachability through strictly valid JSON, on two loader routes, with the real solve |
| `verify-2/clock_sweep.py` | D1-03 blind window swept over 17 read offsets x 3 code arms, and over 4 sensor-silence durations |
| `verify-2/handover_exposure.py` | D1-02 exposure in published cycles, and whether the handover dict grows |
| `verify-2/*.log` | every run's raw output, including the two inline consequence checks |

---

## D1-01 — corrupt `thermal_learning` wedges every cycle — **verify**, severity **high**

### 1. The finder's harness, re-run as its header says

Single-mutant repro — exact match, no tolerance consumed:

```
PYTHONPATH=tests/hastub python3 tools/audit/round3/D1/store_fuzz.py --repro thermal_learning:163
  DIFF solar_aperture: {'n': 0.0, ...} -> {'n': nan, ...}
  RESULT repro_wedge=1        (finder: 1)
  RESULT repro_repeat=1       (finder: 1)
  cycle1 = cycle2 = 'UpdateFailed: Error updating data: cannot convert float NaN to integer'
  RESULT thread_factor=0.966  RESULT load1=37.46  concurrent_python_processes=19
```

Full 2400-mutant sweep — every RESULT line exact:

```
PYTHONPATH=tests/hastub python3 tools/audit/round3/D1/store_fuzz.py --mutants 200
  RESULT wedge_total=1  repeat_total=1  poison_total=0  silent_total=0
  RESULT store_thermal_learning_wedge=1 ... the other 11 stores 0 of 200 each
  RESULT stores=12  mutants_per_store=200  total_mutants=2400
  RESULT thread_factor=0.547  RESULT load1=48.36  concurrent_python_processes=24
```

Ran single-process in well under the header's stated ~8 min at load 140.

### 2. My own number, my own metric

`verify-2/strict_json_wedge.py`. **My metric definition:** *out of N hand-written
`thermal_learning` payloads that contain no non-standard JSON token — each
re-parsed by a strict parser that raises on `NaN`/`Infinity`/`-Infinity`, and
only survivors counted — how many make three consecutive real
`_async_update_data()` cycles raise the same exception with the store never
rewritten.* (The finder's metric is a rate over 200 seeded mutants per store;
mine is an existence-and-reachability count over hand-built payloads. The judge
should treat them as answering different questions about the same mechanism.)

```
RESULT strict_json_payloads=7
RESULT nonstandard_token_payloads_rejected_by_strict_parser=1   (the finder's bare NaN)
RESULT strict_json_defect_candidates=4
RESULT wedge_direct=4 of 4        RESULT wedge_spawned=4 of 4
RESULT repeat3_direct=4 of 4      RESULT repeat3_spawned=4 of 4
RESULT finite_control_wedge_direct=0 of 3   RESULT finite_control_wedge_spawned=0 of 3
```

The four are `"n": "nan"`, `"n": "Infinity"`, `"n": "-inf"` (JSON **strings**)
and `"n": 1e400` (a JSON **number**). All four load to a non-finite float
because the loader's guard is `float(raw_ap.get(key, ...))`, and `float()`
parses those strings and that overflow happily — none of them raises
`TypeError`/`ValueError`/`OverflowError`, which is all the `except` at
`coordinator.py:2545` catches. Both wedge signatures appear:
`cannot convert float NaN to integer` and `cannot convert float infinity to
integer`, both from `int(self._solar_aperture["n"])` at `coordinator.py:6960`.

This ran with the **real L-BFGS-B solve**, not `CapturingOptimizer` — so it also
closes, for this payload, the `--real-solve` arm the finder recorded as
unfinished.

Restart persistence, with the **finder's own full healthy payload** mutated at
seed 163 (`verify-2/restart_persistence.log`):

```
RESULT restart_1_cycles_failed=2 of 2  thermal_store_saves=0  disk_n_after=nan
RESULT restart_2_cycles_failed=2 of 2  thermal_store_saves=0  disk_n_after=nan
RESULT restart_3_cycles_failed=2 of 2  thermal_store_saves=0  disk_n_after=nan
```

Six of six cycles across three simulated restarts. "Never quarantined, never
rewritten" is verified: zero writes to that store key.

### 3. Attacks run

**Stub artefact?** No. The wedge reproduces on two independent loader routes:
`direct`, where the loader coroutine is simply `await`ed under plain
`tests/harness.py:FakeHass` so no task scheduling is involved at all, and
`spawned`, where `d1lib.RealLoopHass` lets the constructor's own spawned task
run on a real loop. 4 of 4 on both. The claim does not depend on
`FakeHass.async_create_task` closing coroutines or on `RealLoopHass` replacing it.

**Grid artefact?** Not applicable in the damaging direction. The finder's 1 of
2400 is an existence claim, not an aggregate; the report already prints every
one of the 12 x 200 cells. Dropping the single favourable cell leaves 0 of 2200
— which is exactly the finder's own null control, and I reproduce it.

**Null control.** Present and passing on both my routes and the finder's: the
same slot with a finite value (`5.0`, `"5.0"`, `1e30`) is absorbed, 0 of 3,
direction `to_zero` as declared.

**The assigned attack — is a non-finite value reachable in a real `.storage`
file, given Home Assistant persists through `json.dumps`?** This is the finder's
own stated caveat and the answer moves *in the finding's favour*.

- The finder's exact bytes (a bare `NaN` token) are **not** strictly valid JSON;
  my strict parser rejects them, and `tests/hastub`'s Store uses lenient
  `json.loads`. So the finder's literal repro does depend on a lenient reader.
- But that does not matter, because **four payloads that any conforming JSON
  writer can emit and any conforming JSON reader must accept reach the same
  `int()`**: three JSON strings and one over-range JSON number. `1e400` is an
  ordinary JSON number token; Python's stdlib parses it to `inf`.
- `orjson` is **not installed on this box**, so I could not execute Home
  Assistant's actual writer/reader and I make no claim about it. I did not need
  to: the string route needs no non-standard extension of any kind.
- I checked the live path too. `_fold_solar_aperture` (`coordinator.py:8503`)
  only ever does `m["n"] += 1.0` from a finite start and gates on
  `np.isfinite(y)`, so the integration cannot poison its own `n` in memory.
  The corruption must come from outside — a hand edit, a backup restore, or
  third-party tooling. **That is a real discount on the trigger**, and it is the
  one thing neither the finder nor I have an executed number for.
- Second entry point, code-read only: `_load_t4b_learners` is also called by the
  snapshot-rollback path (`coordinator.py:8742-8751`), so the `snapshots` store
  is a second route into the same unguarded `int()`. I did not drive it (it needs
  a drift alarm or the rollback service) and I do not count it.

**Honest correction to my own work.** My *minimal* payload (only
`solar_aperture`, no `house_heat_loss_anchor`) makes the loader take a
re-anchoring save *before* the T4b parse, which rewrites the file with
`n: 0.0`; that payload therefore self-heals on the next restart
(`minimal_restart1_wedge=1`, `minimal_restart2_wedge=0`). That is an artefact of
my minimal fixture, not of the defect: with a complete payload, zero saves occur
and the wedge is permanent, as measured above. I record it so the judge is not
surprised by the `store_rewrites=1` lines in my log.

**Severity by consequence.** Permanently dead integration until a `.storage`
file is edited by hand — a workaround exists but it is outside Home Assistant's
UI. Against the rubric's "`high` = a user-visible defect or a wrong published
value" versus "`medium` = a defect with a workaround or a bounded cost", the
loss of all function tips it to `high`. I did not measure `last_update_success`
or entity availability; those follow from `DataUpdateCoordinator`'s contract and
are code-read, not executed.

**Vote: `verify`, severity `high`.**

---

## D1-02 — the reload handover has no expiry — **verify**, severity **medium**

### 1. The finder's harness, re-run as its header says

```
PYTHONPATH=tests/hastub python3 tools/audit/round3/D1/lifecycle_realloop.py \
  --complete-solve --lifecycles 1 --solve-seconds 0
  RESULT stashed_plan_stale_flag=False                    (finder: False)
  RESULT republished_plan_is_the_prereload_one=1          (1)
  RESULT republished_plan_stale_flag=False                (False)
  RESULT republished_plan_age_minutes_published=0.0       (0.0)
  RESULT republished_plan_true_age_minutes=10080.0        (10080.0)
  RESULT republished_plan_optimization_status='optimal'   ('optimal')
  RESULT republished_plan_next_optimization_in_past=1     (1)
  RESULT plan_handover_entries_after_plain_unload=1       (1)
  RESULT plan_handover_bytes_retained=81420               (finder: 81121)
  RESULT thread_factor=1.003  RESULT load1=45.05
```

**One difference, and it is not evidence of anything:** `plan_handover_bytes_retained`
is 81420 against the finder's 81121, 0.37% apart. That RESULT is
`len(repr(payload))` over a dict full of solver floats, so its digit count is not
reproducible across BLAS builds — the same reason the repository does not
re-record value-bearing golden floats off a canonical box. It is a size
indicator, not a metric; my own harness reports the payload as **81346 JSON
bytes** instead, which is at least a portable definition. Every count in the run
matches exactly.

Both declared controls reproduce: `--no-plan` gives
`plan_handover_entries_after_plain_unload` 1 -> **0** and bytes 81420 -> **0**;
`--gap-days 0.0007` gives published age 0.0 against a true age of 0.0.

### 2. My own number, my own metric

`verify-2/handover_exposure.py`. **My metric definition:** *how many
**consecutive published payloads**, from the setup that pops the handover
onward, carry the frozen pre-unload `plan_age_minutes`; and how many entries and
JSON bytes the handover dict holds after K plain unloads.* The finder measures
one payload's value; I measure how many payloads carry it and whether the
retention grows.

```
RESULT published_cycles_carrying_frozen_age=1 of 3
  CYCLE 1 plan_age_minutes=0.0 plan_stale=False is_the_pregap_plan=1 frozen=1
  CYCLE 2 plan_age_minutes=0.0 plan_stale=False is_the_pregap_plan=0 frozen=0
  CYCLE 3 plan_age_minutes=0.0 plan_stale=False is_the_pregap_plan=0 frozen=0
RESULT cycle1_plan_age_minutes_published=0.0   RESULT cycle1_plan_age_minutes_true=10080.0
RESULT handover_entries_after_1_unload=1
RESULT handover_entries_after_5_unloads=1
RESULT handover_entries_after_5_unloads_2entries=2
RESULT handover_json_bytes_retained=81346
```

And the consequence half (`verify-2/handover_consequence.log`), taken after the
pop and **exactly one** cycle — the light refresh, nothing further:

```
RESULT published_plan_age_minutes=0.0   RESULT published_plan_stale=False
RESULT published_current_action={...the full pre-unload action dict...}
RESULT coordinator_current_action_is_empty=1
RESULT coordinator_last_optimization_is_none=1
RESULT plan_is_stale_would_refuse=0
RESULT actuations_from_light_refresh=0
RESULT actuations_if_the_published_action_is_acted_on=3
```

### 3. Attacks run

**Stub artefact / reachable in real HA?** The lifecycle transitions go through
`tests/harness.py:ha_setup_entry` / `ha_unload_entry`, which is the config-entry
state machine's own order, one operation at a time on one entry. No race is
required and none is claimed — the mechanism is a plain unconditional `pop` of a
dict with no timestamp (`__init__.py:223` against `__init__.py:331`), which I
read directly. The one place the harness stands in for the base class —
`tests/hastub`'s `DataUpdateCoordinator` counts `async_config_entry_first_refresh`
instead of running it, so `_skip_solve_once` is still latched when the harness
calls `_async_update_data` — is declared in the finder's header and is what makes
the harness's cycle 1 the real base class's first refresh. I reproduced it
independently in my own harness and got the same shape.

**Is the exposure unbounded, as the finder implies?** No, and this is my main
refinement. `async_setup_entry` schedules `coordinator.async_request_refresh()`
as a background task at the end of setup (`__init__.py:257-267`), and my sweep
shows the frozen values survive **exactly one published payload of three**:
cycle 2 is already a fresh plan. The window is therefore one refresh — seconds
here, and by the code's own comment "minutes" on Raspberry-Pi-class hardware.
That is a bounded cost, not an unbounded one.

**Is the retention a growing leak?** No. Five unloads of one entry leave **1**
entry in the dict; adding a second config entry takes it to **2**. It is keyed on
`entry.entry_id`, so it is bounded at one ~81 KB payload per config entry for the
life of the process. Real, worth fixing, not a leak that grows.

**Is the severity earned by consequence?** Partly, and less than the prose
suggests. The wrong values *are* published to entities — a week-old
`current_action`, `optimization_status: 'optimal'`, `next_optimization` in the
past, `plan_stale: false`. But nothing inside the integration acts on them: after
the pop the coordinator's own `_current_action` is empty and `_last_optimization`
is `None`, so `_apply_action()` makes **0** service calls. The stale guard is
genuinely disarmed (`plan_is_stale_would_refuse=0`, because
`_plan_age_minutes()` returns `None` on a coordinator that has never solved, and
`_plan_is_stale()` maps `None` to `False`) — but with no action loaded there is
nothing for it to refuse. Forcing the published action back in shows what would
follow if any path did load it: **3** service calls, unguarded. That is a latent
hazard, not an executed harm.

Rubric: a wrong published value, bounded to one refresh, with no actuation and a
bounded retention. `medium` is right. The finder's severity is not inflated.

**Vote: `verify`, severity `medium`.**

---

## D1-03 — the staleness watchdog fails open on a backward clock step — **weaken to `medium`**

### 1. The finder's harness, re-run as its header says

Every RESULT exact, both arms:

```
PYTHONPATH=tests/hastub python3 tools/audit/round3/D1/stale_clock.py
  RESULT guarded_readings=11   stale_honest=9   stale_stepped_back=0   stale_stepped_forward=11
  RESULT age_reported_stepped_back_min=0.0  ..._max=0.0   age_reported_honest_min=180.0
  RESULT learners_frozen_honest=4 of 4  ..._stepped_back=0 of 4  ..._stepped_forward=4 of 4
  health honest='9 stale'  stepped_back='ok'  stepped_fwd='11 stale'
  RESULT thread_factor=0.878  RESULT load1=38.55

PYTHONPATH=tests/hastub python3 tools/audit/round3/D1/stale_clock.py --perturb
  RESULT stale_stepped_back=11   (0 -> 11, direction up, as declared)
  RESULT stale_stepped_forward=11 and stale_honest=9 both unchanged
  RESULT age_reported_stepped_back_min/max=inf
```

### 2. The perturbation as a genuine production edit, not a monkeypatch

The assignment asks whether a monkeypatch satisfies the contract when the
obvious one-line deletion does not move the number. I settled it by editing the
tree. Two physical lines inserted before `inputs.py:352`:

```python
        if stamp > now:
            return float("inf")
        return max(0.0, (now - stamp).total_seconds() / 60.0)
```

Then the finder's harness run **without** `--perturb`, so no monkeypatch is in
play at all:

```
RESULT stale_stepped_back=11        (baseline tree: 0)
RESULT learners_frozen_stepped_back=4 of 4   (baseline tree: 0 of 4)
RESULT stale_honest=9  stale_stepped_forward=11   (both unchanged)
```

File restored; sha256 identical before and after. **The perturbation is a real
one-line production edit and it satisfies the harness contract.** The finder's
monkeypatch is faithful to it; the choice of a monkeypatch over the deletion is
correct, not a dodge.

### 3. The finder's trap claim, checked over 187 cells instead of one

The finder records that deleting `max(0.0, ...)` does **not** move the number. I
built `verify-2/clock_sweep.py` to test that properly rather than at one point.

**My metric definition:** *after a backward host-clock step of S minutes, the
number of (read-offset x guarded-reading) cells, over read offsets t = 0, 30,
... 480 min past the step, in which a reading whose sensor has been silent since
before the step is NOT flagged `problem == 'stale'`; and how many of those cells
change under each candidate one-line edit.* Three arms of the production line —
the tree, the bare deletion (`no_clamp`), and the `inf` guard (`inf_fix`) — 17
offsets x 11 guarded readings = 187 cells per arm. Sensors silent for A minutes
at the moment of the step; S = 240 min.

At the finder's own cell (A = 180):

```
RESULT back_sweep_cells=187  back_guarded_readings=11
RESULT back_nonstale_cells_baseline=62  back_nonstale_cells_no_clamp=62  back_nonstale_cells_inf_fix=40
RESULT back_cells_changed_baseline_vs_no_clamp=0     <- the finder is right, over 187 cells
RESULT back_cells_changed_baseline_vs_inf_fix=22
```

**The finder's trap claim is confirmed and it is stronger than they stated:** the
deletion changes **0 of 187** cells, not merely the one they measured. A bare
negative age fails `age > limit` exactly as `0.0` does, at every offset.

Forward-step null control, same sweep: all three arms identical, `fwd_nonstale_cells
= 0` for every arm at every offset, `fwd_cells_changed_* = 0`. The clamp cannot
fire in that direction and does not.

### 4. The attack that lands: the finder's number is the most favourable cell of a grid

The single number `0 of 11` is one read offset at one sensor-silence duration.
Sweeping the silence duration A at fixed S = 240 min:

| A (silent at the step) | cells changed by the fix | clamp-attributable blind window | stale at t+0 |
|---|---|---|---|
| 60 min | **66** of 187 | **180 min** | 0 of 11 |
| 180 min (the finder's) | **22** of 187 | **60 min** | 0 of 11 |
| 300 min | **0** of 187 | **0 min** | 2 of 11 |
| 600 min | **0** of 187 | **0 min** | 11 of 11 |

The clamp-attributable blind window is **`max(0, S - A)`** — the backward step
minus how long the sensor had already been silent. Two consequences the report
does not carry:

1. **The effect vanishes entirely for any sensor already silent longer than the
   clock step.** At A = 600 min all 11 readings are flagged stale and all four
   learners are frozen at t+0, with no fix applied.
2. **That is precisely the population the freeze exists for.** The report quotes
   `_learning_frozen`'s comment — a dropped sensor walked the heat-loss scale
   from 1.0 to ~0.37 *inside 48 h* — and says "that is what this re-enables". My
   measurement says it does not: a sensor dead for 48 h under a 4 h backward step
   is still flagged stale and still freezes its learners. What is re-enabled is
   at most `S` minutes of unfrozen learning, and only for sensors that fell
   silent within `S` of the step.

The named fix is also narrower than "the watchdog is entirely off" implies: it
recovers 22 of the 62 non-stale cells at A = 180, leaving 40. Those 40 are not
the clamp's fault — once the stamp is no longer in the future, the whole
watchdog is simply reading a clock that is `S` minutes behind, which no change
to `_age_minutes` can repair. So the clamp destroys the *evidence* that the
clock moved (0.0 instead of -60.0), and the finder's fix restores the detection
for the sub-window where the stamp is in the future. Both true; neither is "the
watchdog is entirely off".

### 5. Other attacks

**Stub artefact?** No. My sweep uses plain `tests/harness.py:FakeHass` — no
`RealLoopHass`, no executor, no task scheduling — and reproduces the finder's
numbers cell for cell at their grid point. The mechanism is one arithmetic line
read synchronously.

**Reachable in real Home Assistant?** Partly unmeasured, and I will not paper
over it. The production half I can confirm from the tree:
`InputReader._utcnow()` resolves to `dt_util.utcnow()`, i.e. wall clock. The
other half — that Home Assistant stamps `State.last_reported` from the same wall
clock and never rewrites it after a step — is not in this tree (no real HA, no
vendored source) and I did not execute it. The finder flags the same gap. If HA
ever stamped from a monotonic source the mechanism would not arise at all.

**Null control.** Present and passing: the forward-step arm is unchanged under
every arm at every offset, in both the finder's harness and mine.

**Severity by consequence.** A bounded blind window of at most `S` minutes,
requiring the coincidence of a backward host-clock step and a sensor that fell
silent within that step's width, during which `input_health` reads `ok` and up
to four learners run unfrozen. The window scales with the step, so a large
backward correction is worse — but a host whose clock is days wrong is broken in
ways this integration cannot own. Against the rubric that is "a defect with a
bounded cost" = `medium`, not "a user-visible defect or a wrong published value"
without qualification. The `high` rests on the 48-hour corruption story, and
that story does not reproduce.

**Vote: `weaken` to `medium`.** The number, the mechanism and the perturbation
are all verified exactly; the severity is not earned by the consequence I could
measure.

---

## Side observations, not findings

- `coordinator.py:6689` uses the same `max(0.0, (dt_util.now() - ...))` idiom in
  `_plan_age_minutes`, so a backward clock step makes a genuinely old plan
  report age 0.0 there too. Same mechanism, second site. Recorded for the fixer's
  scope; I did not measure it.
- The 2400-mutant fuzz emits one
  `price_model.py:233: RuntimeWarning: invalid value encountered in multiply`
  during the `price_model` block. It is absorbed (`poison=0`, `wedge=0`) under
  the finder's guard envelope, so it is not a finding, but it is a non-finite
  value reaching a numpy op from a corrupt store.
