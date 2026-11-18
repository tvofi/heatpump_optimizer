# D1 panel — verifier 3 of 3 (refute-first)

Baseline `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1`. Box: 8-core Apple M1, 8 GB,
macOS 25.6, python 3.11.5, shared with other sessions — `load1` ran 23–50 across
this session. **Every number below is a count, a byte figure or a minute figure
derived from a frozen clock.** No wall, CPU or RSS number is claimed, so nothing
here needs a quiet-window re-take. `thread_factor` ran 0.68–1.001 on the five
BLAS variables pinned to `"1"` before numpy, which is the un-threaded regime; it
gates nothing here because no timing number is claimed.

`tests/stress.py` was not run, `./tests/run.sh` was not run, the gate lock was
not taken. No `gh`, no GitHub, no register, no other verifier's output.

My work is under `tools/audit/round3/D1/verify-3/`.

---

## 1. Re-running the finder's harnesses, exactly as their headers say

| command | result | vs expected |
|---|---|---|
| `store_fuzz.py --mutants 200` | `wedge_total=1 repeat_total=1 poison_total=0 silent_total=0`, `stores=12 total_mutants=2400`, `store_thermal_learning_wedge=1`, every other store 0 | **exact** on all four totals and all twelve per-store lines. `thread_factor=1.0 load1=49.42` |
| `stale_clock.py` | `guarded_readings=11 stale_honest=9 stale_stepped_back=0 stale_stepped_forward=11`, `age_reported_stepped_back_min=max=0.0`, learners frozen `4 / 0 / 4`, `health stepped_back='ok'` | **exact**. `thread_factor=1.0 load1=41.95` |
| `stale_clock.py --perturb` | `stale_stepped_back` 0 → **11**; controls `stale_honest` 9 → 9, `stale_stepped_forward` 11 → 11 | **exact**. `thread_factor=0.821 load1=43.05` |
| `lifecycle_realloop.py --complete-solve --lifecycles 1 --solve-seconds 0` | `republished_plan_age_minutes_published=0.0`, `republished_plan_true_age_minutes=10080.0`, `plan_handover_entries_after_plain_unload=1` | **exact** on every count. `plan_handover_bytes_retained=81332` against the report's `81121` (+0.26 %) — that is a `len(repr(...))` of a payload containing floats, not a stated-tolerance metric, and the metric the finding rests on is the age, which matched to the digit. `thread_factor=1.001 load1=50.45` |

Logs: `verify-3/store_fuzz_200.log`, `stale_clock_base.log`,
`stale_clock_perturb.log`, `lifecycle_d102.log`.

No reproduction mismatch anywhere. Everything below is an attack on method, not
on reproducibility.

---

## 2. The foundation attack: is `d1lib.RealLoopHass` faithful where these claims lean on it?

All three findings were taken through `RealLoopHass`, so a load-bearing
infidelity would refute more than one at once. I checked each divergence against
the production call sites that would feel it.

| divergence from real HA | load-bearing here? |
|---|---|
| `async_add_executor_job` is an `async def` returning the value; real HA's is a sync method returning a `Future` | **No.** All five production call sites (`coordinator.py:828,870,928`, `services.py:962`, `frontend.py:188`) `await` it immediately. Nothing holds, gathers or cancels the future. |
| `async_create_task` ignores `eager_start`; real HA's defaults to `True` and runs the coroutine to its first suspension synchronously | **No.** The single production call site is `coordinator.py:1384 self.hass.async_create_task(coro)` with one positional argument, and both harnesses drain the created tasks (`store_fuzz._settle`, `lifecycle_realloop`'s `asyncio.wait`) before reading any number, so eager and lazy reach the same end state. |
| `FakeEntry` has no `async_create_background_task`, so `__init__.py:258` takes the `hass.async_create_task` fallback that real HA never takes | **No.** Both branches schedule the same `coordinator.async_request_refresh()`. I sidestepped it anyway by driving `_async_update_data()` directly. |
| `tests/hastub`'s `DataUpdateCoordinator.async_config_entry_first_refresh` **counts** the call instead of running it, and `last_update_success` is never set False | **Yes — and it runs against the finder, not for it.** See D1-01 below: because the stub never runs the first refresh, the finder could not see that the corrupt store kills *setup itself*. |
| `hass.states` is a plain dict; `FakeState.last_reported` is settable | **No** for D1-03 — the harness sets the stamp once under a frozen clock at a time real HA would itself have stamped, then moves the clock. The mechanism under test is arithmetic on `state.last_reported` vs `dt_util.utcnow()`, and `InputReader` is constructed with no `now=` at both call sites (`coordinator.py:3182`, `:5335`), so `_utcnow()` is the real `dt_util.utcnow()`. |

**Verdict on the foundation: `RealLoopHass` is faithful in every respect these
three claims depend on.** It does not manufacture any of them. D1-03 does not
even use it in a load-bearing way — its number comes from one direct
`_update_current_state()` call.

### One instrument defect found in the same family (bears on a non-finding, not on my three votes)

`lifecycle_realloop.py` prints
`state_listeners_after=len(getattr(hass, 'state_listeners', []))`.
Neither `FakeHass` nor `RealLoopHass` defines `state_listeners`;
`tests/hastub/homeassistant/helpers/event.py` creates it lazily on the first
registration. Production registers two state listeners
(`coordinator.py:7743` defrost, `:7792` peak guard), and **both are
config-gated** — on `_HEAT_PUMP_DEFROST_ENTITY` and on
`CONF_PEAK_GUARD_ENABLED` plus a power meter. `lifecycle_realloop`'s config is
`d1lib.BASE_CONFIG` plus `heat_pump_switch_entity`, which satisfies neither. So
no listener is ever registered and `state_listeners_after=0` is a green arm over
dead code: it cannot tell a correct unsubscribe from a listener that never
existed. The finder's non-finding 2 ("no listener leak across reloads") is
unsupported by that particular number. Recorded for the judge; it does not touch
D1-01/02/03.

Minor: `store_fuzz.py --repro`'s help text and `REPORT.md` both say it "runs
three cycles instead of two"; `one_trial` runs two. Cosmetic.

---

## 3. D1-01 — corrupt learner store → permanent `UpdateFailed`

### My own harness and my own metric

`verify-3/nonfinite_census.py`.

> **My metric:** the number of *addressable positions* in each persisted Store
> payload — every position, enumerated, no sampling — at which substituting a
> value that (a) survives a strict RFC-8259 JSON round trip, as Home Assistant's
> own orjson reader demands, and (b) reaches a non-finite float through the
> loader's own `float()`, makes **three** consecutive real `_async_update_data`
> cycles raise with the same signature.

**Executed number (`verify-3/census_all.log`):**

```
RESULT positions_enumerated_total=1199              (all 12 stores)
RESULT strict_reachable_nonfinite_wedge_positions=3
RESULT strict_reachable_nonfinite_repeat_positions=3
RESULT finite_control_wedge_positions=0             <- the null control
RESULT cycles_per_trial=3   RESULT stores=12
```

The 3 is three *encodings* landing on one position. Per store, only
`thermal_learning` is non-zero, and within it exactly **1 of 42** positions:

```
census_thermal_learning_str_nan_wedge_positions=1   of 42   (token "nan")
census_thermal_learning_str_inf_wedge_positions=1   of 42   (token "inf")
census_thermal_learning_num_1e400_wedge_positions=1 of 42   (token 1e400)
census_thermal_learning_str_1e30_wedge_positions=0  of 42   (finite control)
  KILLS at 'solar_aperture.n' ... saves_of_this_key=0
```

1199 positions × 3 encodings × 3 cycles = **10 791 driven update cycles**;
one position wedges, all three cycles, identical signature.

### Attacks

**Is the aggregate a grid artefact? — Yes, the finder's is; the finding is not.**
"1 of 200 thermal_learning mutants" is a lottery draw: `mutate()` picks one
random path out of 42, then one operator out of seven, then one value out of
fifteen. That number measures the RNG, not the code — re-seed and it moves. My
census deletes the grid: the defect is a **single deterministic position**, and
the honest denominator is 1 of 1199 positions across the whole persisted
surface, not 1 of 2400 dice rolls. **The metric should be replaced; the finding
survives it intact.**

**Is the null control present and passing? — Yes.** The same operator at the same
1199 positions with a strict-JSON-reachable *finite* value (`"1e30"`) wedges
**0**. The defect is the non-finiteness reaching an `int()`, not the corruption.

**Is the path reachable in real HA, or only through the stub? — The finder left
this open and it closes in the finding's favour.**
`tests/hastub/.../storage.py` reads with stdlib `json.loads`, which accepts a
bare `NaN`; real HA reads `.storage` with `homeassistant.util.json.load_json` →
`orjson.loads`, which is strict RFC 8259 and rejects bare `NaN`/`Infinity`, and
writes with `orjson.dumps`, which emits `null` for a non-finite. So a bare-`NaN`
mutant *is* a statement about the stub. But it does not need to be. I probed
every encoding against a strict parser (`parse_constant` raising, exactly
orjson's rule) and then through the loader's own
`float(raw_ap.get(key, default))` at `coordinator.py:2544`:

| JSON token | strict RFC 8259 | reaches the slot as | `int()` |
|---|---|---|---|
| `NaN`, `Infinity`, `-Infinity` | **rejected** | — | stub-only route |
| `1e400` / `-1e400` (a plain number) | accepted | `inf` / `-inf` | `OverflowError` |
| `"nan"` / `"NaN"` (a **string**) | accepted | `nan` | `ValueError` |
| `"inf"` / `"Infinity"` / `"1e400"` | accepted | `inf` | `OverflowError` |
| `null`, `"abc"` | accepted | `float()` raises → loader `continue`s, slot keeps its default | safe |

**Six encodings survive a real orjson read and reach a non-finite**, and my
census confirms three of them wedge in the running integration. The loader's
`float()` — the very line that is trying to sanitise the field — is what
converts the string `"nan"` into a NaN. The finder's caveat is answered, and
answered the other way from how it was hedged.

**Is the severity earned by consequence? — Yes, and it is worse than reported.**
`verify-3/setup_path_probe.log`:

```
RESULT setup_first_refresh_raises_str_nan=1
    setup light-refresh = 'UpdateFailed: ... cannot convert float NaN to integer'
    later cycles        = [same, same]
RESULT setup_first_refresh_raises_finite_control=0
```

The setup-time light first refresh raises too. In real Home Assistant
`async_config_entry_first_refresh()` runs for real and turns `UpdateFailed` into
`ConfigEntryNotReady`, so `async_setup_entry` **fails and the entry never
reaches LOADED** — HA retries setup with backoff, forever. The finder could not
see this because the hastub base class only *counts* that call. And
`saves_of_this_key=0` across three cycles confirms the corrupt payload is never
rewritten and never quarantined.

**One limit on likelihood the judge should carry.** The in-memory learner cannot
produce a non-finite `n` on its own: `_fold_solar_aperture` does `m["n"] += 1.0`
from a `0.0` seed (`coordinator.py:1437`, `:8538`). So the corruption must
arrive from outside the process — a restored backup, a hand edit, third-party
tooling, a torn write. That bounds how often this fires; it does not bound what
happens when it does.

**Vote: `verify`, severity `high`.**

---

## 4. D1-02 — the reload plan handover has no expiry

### My own harness and my own metric

`verify-3/handover_exposure.py`, driving the real `async_setup_entry` /
`async_unload_entry` through `ha_setup_entry` / `ha_unload_entry` on
`RealLoopHass`, with the republishing cycle reached the production way (the
`_skip_solve_once` flag routing `_async_update_data` into
`_async_first_refresh_light`), not by calling the light refresh by hand.

> **My metric:** after an entry is unloaded with a solved plan and set up again
> `--gap-days` later, (a) how many of the published payload's keys carry a value
> the clock at republish time contradicts, (b) for how many consecutive
> published cycles those values survive, and (c) how many service calls the
> integration makes to the world while that payload is the published one.

**Executed numbers (`verify-3/handover_gap7.log`, `handover_gap0.log`):**

| | 7-day gap | 0-day gap (null control) |
|---|---|---|
| `contradicted_keys_in_republished_payload` | **2** (of `republished_payload_keys=160`) | **0** |
| `cycles_publishing_a_contradicted_plan_age` | **1** | **0** |
| `service_calls_during_the_republishing_cycle` | **0** | 0 |
| `handover_entries_after_final_unload` / bytes | 1 / 82 037 | 1 / 81 617 |

The two contradicted keys are exactly the two the finder named:
`plan_age_minutes` (0.0 published against 10 080.0 true) and `plan_stale`
(`False` against a plan 7 days old). Nothing else in the payload is
contradicted — `next_optimization` did not land in the past in my arm.

### Attacks

**Mechanism: confirmed, verbatim.** `__init__.py:331` stashes `coordinator.data`
under `_PLAN_HANDOVER_KEY` with no timestamp; `:223` pops it on the next setup of
that entry id, whenever that is; `coordinator.py:4731-4735` returns it "as-is".
`_plan_age_minutes()` reads the *new* coordinator's `_last_optimization`, so the
republished payload's staleness fields are the pre-unload ones. Not disputed.

**Is the severity earned by consequence? — No. This is where I part from the
finder.** Three measured reasons:

1. **Nothing acts on it.** `service_calls_during_the_republishing_cycle=0`,
   against **3 per cycle** once real solves resume (cycles 1–3 in my log).
   `_async_first_refresh_light` returns the handover *before* `_apply_action` is
   reached, so the 7-day-old action is never actuated. The finder writes that
   the `_apply_action` stale guard "cannot fire" — true, and irrelevant: on this
   path `_apply_action` is not reached at all, so there is nothing for it to
   guard.
2. **It is one cycle wide and self-correcting.** `cycles_publishing_a_
   contradicted_plan_age=1`. The very next cycle re-solves and publishes
   truthful values (cycle 1: `true_plan_age=0.0 published_plan_age=0.0`), and
   `async_setup_entry` already schedules that cycle as a background task at the
   end of setup. The exposure is the debounce plus one cold solve.
3. **The blast radius is 2 keys of 160**, not the payload. And the retention is
   one ~82 KB payload per entry, bounded and non-growing — a retention, not a
   leak.

**Null control: present and passing.** `--gap-days 0` takes every contradicted
count to zero, which is the direction the perturbation demands.

**Reachable in real HA? — Yes**, but note the divergence honestly: `FakeEntry`
lacks `async_create_background_task`, so the harness takes the
`hass.async_create_task` fallback at `__init__.py:265` that real HA never takes.
Both branches schedule the identical coroutine, and I measured the republish by
driving `_async_update_data()` itself, so nothing rests on which branch runs.

**Vote: `weaken` → severity `low`.** The mechanism is exactly as claimed and the
code's own comment ("a stale payload must never outlive the one reload it was
made for") is indeed violated. But `medium` prices a consequence that is not
there: two published keys, one cycle, zero actuations, bounded memory. It is a
real defect with a small blast radius and an obvious one-line fix (stamp the
handover, drop it past an age).

---

## 5. D1-03 — the staleness watchdog is off while a stamp is ahead of `now`

### My own harness and my own metric

`verify-3/clock_window.py`. The finder measured one cycle at one offset. A
single-cycle count cannot separate a watchdog that is off for one tick from one
that is off for a week, and severity here is entirely (duration × learner fold
rate). So I swept the step size and bisected the recovery point.

> **My metric:** for a backward host-clock step of size Δ landing on sensors
> already silent for A = 180 min, the first offset after the step at which
> (a) any of the 11 guarded readings is flagged `stale` and (b) all four
> learners are frozen — against the same quantities with no step.

**Executed numbers (`verify-3/clock_window.log`):**

| backward step Δ | `reported_age_max` at step+0 | first stale | first all-4-frozen | stale/frozen at step+0 |
|---|---|---|---|---|
| none (control) | 180.0 | 0 min | 0 min | 9 of 11 / 4 of 4 |
| 15 min | **165.0** | 0 min | 0 min | 9 of 11 / 4 of 4 |
| 1 h | **120.0** | 0 min | 0 min | 9 of 11 / 4 of 4 |
| 4 h | **0.0** | **90 min** | **120 min** | 0 of 11 / 0 of 4, health `'ok'` |
| 24 h | **0.0** | **1 290 min** | **1 320 min** | 0 of 11 / 0 of 4, health `'ok'` |
| 7 d | **0.0** | **9 930 min** | **9 960 min** | 0 of 11 / 0 of 4, health `'ok'` |

The `reported_age_max` column is the whole mechanism in one number:
**reported age = true age − Δ, exactly** (180−15=165, 180−60=120), and the
`max(0.0, ...)` clamp turns the remainder into a floor of 0.0. The recovery
points fall out of it exactly: 240−180+30 = 90, 240−180+60 = 120,
10 080−180+30 = 9 930, 10 080−180+60 = 9 960, against the 30- and 60-minute
limits in `const.INPUT_MAX_AGE_MINUTES`. So this is not "the watchdog is off for
a moment": **every verdict on every un-refreshed state is displaced later by
exactly Δ, permanently.** That is a stronger statement than the finder made, and
it is mine.

### Attacks

**Reachable in real HA, or only through the stub? — Reachable.** `_age_minutes`
is arithmetic on `state.last_reported` against `self._utcnow()`, and
`InputReader` is constructed with no `now=` at both production call sites, so
`_utcnow()` is `dt_util.utcnow()` — the host wall clock. `RealLoopHass` is not
load-bearing here at all: the number comes from one direct
`_update_current_state()` call.

**Null control and perturbation: both clean.** The forward-step and no-step arms
are unchanged under `--perturb` (11→11, 9→9) while the backward arm moves 0→11.
The finder's own recorded trap — that merely dropping the clamp moves nothing,
because a negative age fails `age > limit` exactly as 0.0 does — is correct and
is why the perturbation names the future stamp.

**Is the severity earned by consequence? — Not at `high`.** My sweep shows the
damage is *exactly linear in Δ*, so severity is a question about the magnitude
of backward clock steps real HA hosts produce, and the honest answer is: small.

- **DST cannot do it.** `last_reported` and `utcnow()` are both UTC; a DST
  transition moves neither. (The finder says the same.)
- **A Pi with no RTC steps *forward* at boot.** `fake-hwclock` restores the last
  *saved* time, which is in the past, so NTP corrects upward — the safe arm,
  which this harness shows is identical to honest (11 of 11 stale).
- **A restored VM snapshot does step backward**, and it restores the in-memory
  state machine with it, which is exactly this harness's shape — but
  `systemd-timesyncd` then steps forward to true time within seconds of the
  network coming back, so the blind window is seconds, not the days the 7-day
  arm models.
- **The reliably-backward event is an NTP correction of a clock that ran fast.**
  Crystal drift is tens of ppm, so realistic offsets are seconds to minutes. My
  Δ = 15 min arm is that case, and it never reaches the fully-blind state at
  all: 9 of 11 still flagged, all 4 learners still frozen, verdicts displaced by
  15 minutes.

The hours-and-days arms that make the table read `high` are constructed. The one
class that could restore `high` — a host whose clock was grossly *ahead* (a dead
RTC battery reading a future date) and is then corrected backwards, leaving
stamps in the future for as long as the original error — is real, but I have no
executed number for how often it happens and did not manufacture one.

**What keeps it well above `low`:** the failure is **fail-open and silent**.
Published `input_health` reads `'ok'` (my re-run: `health stepped_back = 'ok'`,
`stale keys back = []`), no WARNING is logged, and the module docstring commits
to the opposite — *"A dead sensor stops reporting too, so the fail-closed intent
is preserved"*. And it is perfectly correlated with the condition it guards:
only never-refreshed states carry future stamps, which is precisely the set the
watchdog exists for. A watchdog that reports `ok` while blind is a defect in
kind. The one-line fix is proven by the built-in perturbation (0 → 11).

**Vote: `weaken` → severity `medium`.**

---

## 6. Summary

| id | vote | severity | my executed number |
|---|---|---|---|
| D1-01 | `verify` | `high` (as filed) | 1 of 1 199 enumerated store positions wedges 3 of 3 cycles under all 3 strict-RFC-8259-reachable non-finite encodings; finite control 0 of 1 199; store rewritten 0 times; setup-time first refresh also raises (1, control 0) |
| D1-02 | `weaken` | `low` (filed `medium`) | 2 of 160 published keys contradicted, for 1 cycle, with 0 service calls while it stands; null control 0 and 0 |
| D1-03 | `weaken` | `medium` (filed `high`) | reported age = true age − Δ exactly (`reported_age_max` 180/165/120/0/0/0); first stale slips 0 → 90 → 1 290 → 9 930 min and first all-frozen 0 → 120 → 1 320 → 9 960 min for Δ = 4 h/24 h/7 d |

No refute rests on a timing mismatch; nothing here is marked `unresolved`.
