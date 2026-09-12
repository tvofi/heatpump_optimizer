# D1 verify-0-1 (round 4, panel D1-0, seat 1 of 3)

Stance: refute-first. Worktree `../audit-r4-verify-D1-1` at `0855277`
(branch head of `claude/13-dimension-audit-920935`), created fresh after
removing the dead seat's worktree. Production code unchanged since the
baseline: `git diff --stat 7dd68dd..HEAD -- custom_components/` reports
only `manifest.json` and `www/heatpump_optimizer-card.js` (one line each,
version stamps); every `*.py` under `custom_components/heatpump_optimizer/`
is byte-identical. No file under `custom_components/` or `tests/` was
modified by me (`git status` shows only my three harnesses).

Every number below is a **count**; none is timing-sensitive. `load1` during
my runs ranged 2.4–12.2 (other agents on the box); quoted, not gated, and
load-bearing for nothing here. `thread_factor=1.0000` on every harness
(five-variable thread pin before the numpy import, per the harness
contract). Python: `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`,
run from the worktree root with `PYTHONPATH=tests/hastub`.

## Finder harnesses re-run (exactly as their headers say)

| harness | command | result vs header/finder |
|---|---|---|
| `price_prior_zero.py` | header command | `zero_priced_steps=4`, `control=0`, `null_control=0`, `bins_reaching_zero=14`, `zero_steps_per_bin_min/max=4/4`, differing steps `[40,41,42,43]`, corrupt `0.0000` vs control `0.6018` — **exact** |
| `accuracy_wipe.py` | header command | `fields_lost=3`, `fields_checked=3`, `control=0`, `bool_variant=3`, `warning_log_lines=0`, `log_lines=0`, `last_update_success_after=1`; exceptions `TypeError: 'float'/'bool' object is not iterable` — **exact** |
| `store_fuzz.py` | `--mutants 200` | per-store table identical to the finder's, `exception_escaped=0`, `nan_published=16` (price_model 6, dhw_profile 10), `silent=6`, `corrupt_persisted=91` (price_model 58), `repeat_failure=0`, `multi_log=0` — **exact** |
| `real_loop.py` | `--cycles 5 --inflight` | `first_cycle_ok=5`, all leak counts 0, `handover_keys_retained=2`, `hass_data_keys=4`, `inflight_unloads=5`, all five solves `"shutdown"`, `escaped_exceptions=0` — **exact** |

Root-rule check: all four harnesses live in and were run from the tree
under test (`sys.path.insert(0, "tests")` / `(0, "custom_components")`
relative to cwd), so they measured this worktree, not the evidence tag.

## My own harnesses (the seat's obligation)

Beside the finder's, three files, each printing its own RESULT lines:

### `d1_own_D1-01.py` — D1-01 at three seams, my own anchor

Metric: planning steps priced exactly 0.0 that are **not** price-known,
after loading a price-model store whose one shape bin is the strict-JSON
string `"nan"`; matched control = identical store, finite bin. Anchor
Wednesday 06:00, weekday profile, 6 published hours (finder: Saturday
12:00, weekend profile, 10 published) — agreement across anchors is
evidence the number is not an anchor artefact.

```
RESULT fromdict_nonfinite_spellings_accepted=6   # nan NaN inf Infinity -Infinity -inf
RESULT seam_zero_priced_guessed_steps=4          # extend_price_series called directly
RESULT seam_control_zero_steps=0
RESULT e2e_zero_priced_steps=4                   # corrupt steps [36..39] at 0.0 vs 0.5809 control
RESULT e2e_control_zero_priced_steps=0
RESULT e2e_fixed_zero_priced_steps=0             # isfinite guard monkeypatched onto from_dict
RESULT e2e_differing_steps=4
RESULT calibration_mispriced_steps=72            # my own second symptom, see below
RESULT calibration_mean_shift_sek=0.0920
RESULT e2e_log_lines=0
```

Two things the finder did not report, both strengthening:

1. **A second symptom of the same missing check.** With the corrupt bin
   parked inside the *published* window (bin 9 of a 6-hour window), no
   step is priced zero — instead `extend_price_series`'s level calibration
   (`np.mean(shape_values)` at price_model.py:430) swallows the NaN, the
   `shape_mean > 1e-6` guard fails silent, and the **entire guessed tail
   (72 of 96 steps) is mispriced by +0.0920 SEK/kWh mean** vs the matched
   control, with zero log lines. One corrupt bin, two silent wrong-pricing
   modes depending on where it sits.
2. **The `quarter_factors` branch has the same hole** (price_model.py:342,
   `float(v)` in try/except, no finiteness check); `residual_var` is
   accidentally safe only because `max(0.0, float(v))` clamps NaN to 0.0
   (line 359). The finding names the shapes branch; the fix should cover
   both.

Mechanism confirmed at each layer: `float("nan")` parses (all six
spellings accepted by `from_dict`); `predict` multiplies the NaN shape bin
through; `max(0.0, nan)` is `0.0` in this interpreter (printed in the
harness output); the writer `observe_day` rejects non-finite days at
price_model.py:137 while the reader accepts them — the asymmetry is real
and in the directions claimed.

Debug note for the judge, because it is itself evidence about the
finding's shape: my first draft returned zero priced steps everywhere. The
cause was mine — a storage key that did not match
`f"{DOMAIN}_{entry_id}_price_model"` (coordinator.py:1727), so no store
was loaded at all, plus a corrupt weekday bin under a weekend clock. Both
are the kind of silent no-op that makes this bug class easy to
under-measure. The harness now asserts the corrupt arm *differs* from
control (4 differing steps) so a future key regression cannot pass unnoticed.

### `d1_own_D1-02.py` — D1-02 through a full solving cycle

Metric: money- or physics-bearing fields on disk (month peaks, defrost
derate table, operation mode) that no longer equal the healthy payload
after (i) a REAL background task runs `_async_load_accuracy` exactly as
`_spawn` creates it in real HA — exception deliberately unretrieved until
after the measurement — and (ii) ONE FULL `_async_update_data()` cycle
with seeded prices/weather and noop'd network fetches. Not the save-slice
the finder drove: the whole cycle, solve included.

```
RESULT strict_json_payload=1                  # json.dumps(..., allow_nan=False) OK: no non-standard literals
RESULT full_cycle_fields_lost=3  RESULT fields_checked=3
RESULT control_fields_lost=0
RESULT bool_variant_fields_lost=3             # samples = true
RESULT fixed_fields_lost=0                    # guarded from_dict monkeypatch: loss vanishes
RESULT cycle_completed_and_success=1          # payload published, last_update_success True
RESULT warning_log_lines=0  RESULT all_log_lines=3   # the 3 are ordinary solve INFO lines
RESULT solve_produced_result=1                # MPC ran: "96 steps (96 from published prices) ... optimal"
RESULT spawned_task_raised_typeerror=1        # retrieved only after the cycle: 'float' object is not iterable
```

On disk after one cycle: `peaks [7.1, 6.3, 5.2] -> []`, `mode economy ->
auto`, defrost factors replaced by defaults. The integration emitted its
normal solve INFO lines and nothing about the wipe.

### `d1_own_D1-INST.py` — the instrument, measured

```
RESULT stub_refresh_runs_update_cycles=0      # a Probe subclass with _async_update_data, all three entry points awaited
RESULT setup_spied_update_cycles=0            # class-level spy during full ha_setup_entry
RESULT setup_flag_still_latched=1             # _skip_solve_once still True after setup's "first refresh"
RESULT direct_cycle_consumes_flag=1           # control: hand-driven cycle consumes it; the code works
```

`refresh_requests=1` after setup: the stub counted the refresh
`__init__.py:288` requested and ran zero cycles. The flag production
latches there is still latched afterwards — within the stub suite nothing
ever consumes the setup-latched flag through the base class.

## Attacks run, and their outcomes

**D1-01**

- *Grid artefact?* No. My anchor (different day type, window, bin, shape)
  gives the same 4; the finder's 24-cell sweep gives 4 for every reaching
  bin; and the calibration symptom appears at a bin position their sweep
  codes as "no effect" (their `bins_reaching_zero` excludes bins inside
  the published window — those bins do have an effect, just not a zero).
- *Null control / control?* Both clean: 0 zeros with the whole horizon
  published; 0 zeros with a finite bin. Effect present only when the prior
  is both loaded and consulted.
- *Reachability in real HA?* The trigger is an externally corrupted
  `.storage` payload. `"nan"` is strict JSON (dumps under
  `allow_nan=False`), so it survives orjson where a bare `NaN` literal
  would not — the finder's strict/loose distinction is correct and matters.
  The learner cannot write the NaN itself (`observe_day:137` rejects), so
  this needs disk corruption, hand edit, or partial restore. That caps
  likelihood, not consequence; D1 is the dimension that exists to price
  exactly this. `corrupt_persisted=58/200` (price_model, store_fuzz)
  confirms a restart does not clear it.
- *Severity earned?* Yes: 4/96 planning steps at 0.0000 SEK/kWh against
  0.5809–0.6018 control is a wrong money signal the optimizer plans
  against (`_forecast_arrays` is the solve's input, coordinator.py:4383),
  silent at every log level, persistent across restarts — plus my
  72-step calibration variant. High stands.

**D1-02**

- *Only through the test stub?* No. The payload is strict JSON (a plain
  number / `true`); the loader is `_spawn`ed fire-and-forget
  (coordinator.py:1422/1430), which in real HA is an unretrieved
  background-task exception — reproduced here with a real task. The wipe
  needs only that the next cycle's `_async_save_accuracy` (coordinator.py:4249)
  writes the in-memory defaults, which my full-cycle run demonstrates with
  the solve running normally around it.
- *Sibling comparison?* Holds. `_async_load_ledger` guards its day-book
  decode with an explicit "Same corruption barrier as the other riders"
  comment (coordinator.py:6811); `_async_load_price_model` relies on a
  `from_dict` that cannot raise; `AccuracyTracker.from_dict` can raise
  (iterating `samples`, accuracy.py:363 — the one branch in that
  classmethod without its own try/except) and `_async_load_accuracy` wraps
  only `async_load()` (coordinator.py:6857-6866). It is the outlier.
- *"Zero log lines at any level" — overbroad by one.* In real HA an
  unretrieved task exception is logged by asyncio's default handler at
  task destruction ("Task exception was never retrieved", ERROR, with
  traceback) — late, unattributed to any entity, and after the wipe has
  already landed. Under the stub: exactly 0. I count this a precision
  note, not a weaken: no log line exists at the point of failure, names
  the store, or stops the wipe.
- *Ordering attack (load vs first save).* Any order wipes: the in-memory
  state is defaults from construction whether or not the corrupt load
  raised, so whichever cycle saves first writes defaults over the corrupt
  store. Measured, not assumed: peaks/mode/defrost all gone after one cycle.
- *Severity earned?* Yes: permanent, silent loss of the capacity-tariff
  billing peaks, the learned defrost derate and the user's mode, from one
  scalar, with a one-line fix (verified: guarded `from_dict` -> 0 lost,
  no exception). High stands.

**D1-INST**

- *Is the stub fact true?* Yes — read the file
  (tests/hastub/homeassistant/helpers/update_coordinator.py:
  `async_request_refresh` increments `refresh_requests`;
  `async_refresh` and `async_config_entry_first_refresh` delegate to it;
  none calls `_async_update_data`), and measured: 0 cycles through all
  three entry points, 0 spied cycles during a full production setup, flag
  still latched.
- *Does any test in the tree run the base-class cycle anyway?* Grep of
  every `async_refresh` / `async_config_entry_first_refresh` /
  `async_request_refresh` call site under `tests/` and `tools/`:
  features.py:29008 and 31230 *replace* `async_request_refresh` with a
  counter (asserting production calls it, not that a cycle runs);
  features.py:16793-16816 patch the first refresh to *raise*
  ConfigEntryNotReady; entities.py:13643-13662 spy `__init__`'s signature
  only; open_meteo.py's `async_refresh` is a different class. Everything
  that needs a cycle hand-drives `_async_update_data()` — features.py,
  entities.py (`_d801_publications`), real_loop.py:290 (comment says so),
  my own harnesses.
- *The exception the finder's wording misses:* **tests/nightly_ha.py** runs
  the integration in the real `homeassistant/home-assistant` Docker image
  with the REAL `DataUpdateCoordinator` — its A4 check awaits
  `coordinator.async_refresh()` and asserts `last_update_success` flips
  (only meaningful if a cycle runs), and `_await_plan` (nightly_ha.py:2141)
  explicitly discusses the first refresh consuming the solve skip. So "no
  test in this tree" is overbroad: no test in the **stub-driven suite the
  gate and every audit lane run** — `tests/run.sh` excludes nightly_ha.py
  (run.sh:286-294, own nightly job, needs Docker). The instrument gap in
  the instrument this audit actually uses is exactly as claimed.
- *The one-line production mutation the suite cannot see* (verifier
  contract §4): delete `coordinator._skip_solve_once = True` at
  `custom_components/heatpump_optimizer/__init__.py:288`. In the stub suite
  nothing observes it — no test asserts the flag after a real setup, and
  the stub's first refresh is a no-op — while in real HA it reintroduces
  the minutes-long blocking cold solve during `async_setup_entry` that the
  flag exists to prevent (the comment at `__init__.py:280-287` says
  exactly this). The consumption side IS tested (features.py:16284-16299
  sets the flag manually and drives `_async_update_data` directly), so the
  gap is precisely the wiring: set-at-setup -> consumed-by-base-class.
  Not full-gate-verified (I did not run the gate with the mutation); it
  rests on the spied-cycle count of 0 during setup, which is direct.
- *"Never consumed" precision.* The flag *instance* that `__init__.py`
  latches is never consumed in the stub suite (measured: still latched
  after setup). The consumption *code* is exercised directly by
  features.py. Both halves of the finder's sentence are true in their
  natural reading; the report's phrasing "never consumed in the suite"
  could be read to deny the features.py check and should say "never
  consumed through the base-class refresh".

## Votes

| id | vote | severity | my number |
|---|---|---|---|
| D1-01 | verify | high | 4 zero-priced steps of 96 (control 0, null 0, fixed 0); + my 72-step / +0.0920 SEK/kWh calibration variant |
| D1-02 | verify | high | 3 of 3 fields lost via a full solving cycle with a real unretrieved spawned task (control 0, fixed 0, 0 WARNING lines) |
| D1-INST | verify (with the nightly_ha.py caveat above; wording narrowed to the stub-driven suite) | low (instrument coverage gap; the named mutation ships a user-visible setup hang green) | stub/base-class cycles through setup: 0; setup-latched `_skip_solve_once` consumed: 0 |

Both product findings reproduce exactly under the finder's harnesses and
under mine, through different anchors and a fuller cycle respectively;
neither survived a single attack. The instrument finding's core is
measured true, with one wording correction recorded.

## Files

- `tools/audit/round4/D1/d1_own_D1-01.py` (mine)
- `tools/audit/round4/D1/d1_own_D1-02.py` (mine)
- `tools/audit/round4/D1/d1_own_D1-INST.py` (mine)
- this report: `tools/audit/round4/D1/verify-0-1.md`

All uncommitted, as instructed.
