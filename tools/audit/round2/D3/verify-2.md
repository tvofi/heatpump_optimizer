# D3 — verifier seat 2 (consequence and reachability)

Worktree `v-D3-2` at `c398fc84eec25fc44b60d74aae05b9a2da205884`, clean before
and after every run (`git status --porcelain` empty; verified at the end).
Interpreter `tvofi-claude/.venv/bin/python` (3.13.1, numpy 2.5.2, scipy
1.18.1). Every command pinned the five BLAS thread variables. All my numbers
are **counts, exit codes or ratios of counts** — no wall, CPU or RSS number
enters a verdict, so the load1 range on this box during the fan-out (2.9 to
56) cannot move any of them. Harnesses in
`/private/tmp/claude-501/audit-scratch/D3-2/`.

**Disclosure.** `round2/D3/panel.json` is not a `verify-*.md` and I read it
before I realised it carries seat 1's votes and note block. I did not read
`verify-1.md` or `verify-3.md`. Every verdict below rests on a number I
executed in my own worktree; where my conclusion happens to agree or
disagree with that note block, it is because of my own measurement, and I
have flagged the two places where I reached a *different* mechanism.

**Method note — why I did not run `prescreen.py` as written.** Its header
requires HEAD to be a throwaway branch with the mutant committed
(`env_drift.py` refuses a ref that resolves to HEAD), and SEAT_COMMON
forbids `git commit`/`git checkout`. I re-ran the same measurement two ways
instead:

* `closure_run.sh` — applies the mutant to the **working tree** and runs the
  fast closure (features, entities, manual_plan, open_meteo,
  solar_alignment, validate, optimality, plan_view, frontend, card.mjs),
  counting non-zero exits. Ten scripts, a superset of the finder's nine.
* `drift_run.py` — runs `tests/env_drift.py --all <baseline>` with `_rev`
  patched to answer a synthetic SHA for the literal rev `"HEAD"` and the
  real SHA for everything else. Nothing else is touched: env_drift's branch
  side already captures the working tree (`capture_tree(repo)`), so the
  uncommitted mutant is visible, and the baseline worktree, both captures,
  the claim/may-drift parsing, `_diff_leaves` and the entire verdict block
  are the shipping code. **Null control:** clean tree → `rc=0`,
  `NO UNCLAIMED DRIFT: 55 scenario(s) checked`, all five SENSITIVE printed
  as `may-drift ... did not move here`. `wall_s=85.2`.

**Null control for the closure re-run:** `NULL.fast_closure_scripts_failing=0`
on the clean tree — the ten scripts pass with nothing applied.

**My own metric, used on D3-01…D3-07** (one line):

> `consequence_delta` = the number of user-facing published values that
> differ between the shipping code and the mutant under **one legal Home
> Assistant input a real deployment can produce**, together with
> `load_bearing_evaluations` = the number of times, during a gate script,
> the mutated site is evaluated on an input for which the two sides
> disagree.

`load_bearing_evaluations` separates the two kinds of gap the finder does
not distinguish, and it is the number this seat cares about:

* `n_eval = 0` → the gate never runs the line;
* `n_eval > 0, n_load = 0` → **input-coverage gap**: the gate runs it, never
  on the input that matters;
* `n_load > 0` and the script still passes → **assertion gap**: the gate
  computes a different value and asserts nothing about it.

Harness `loadbearing.py` wraps each site, computes both branches and returns
the shipping one, so the script under measurement behaves exactly as in the
gate (every instrumented run exited 0).

**Quiet-window logs read.** `quiet/D3-M{13,19,21,30,31,32}.gate.log`: six
mutants, `GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF=<baseline>
GATE_JOBS=1`, 16 scripts including `env_drift.py --all` (44 s) and
`stress.py` (61-64 s), `QUIET_EXIT=0`, `ALL TEST SCRIPTS PASSED`, 200-205 s
each, `QUIET_LOAD_BEFORE` 1.47-2.21. They support the six claims they are
cited for. **M15 (D3-07) has no gate log** — `quiet_window_request.top_six`
excludes it ("then M15", never run). `rolling.py` and `dst_checks.py` appear
in none of the six wall-clock tables, so the gate that ran is the CI gate,
not more.

**Production-file rule.** All seven mutants patch files under
`custom_components/heatpump_optimizer/` (sensor.py, dhw_schedule.py,
coordinator.py, grid_fee.py, accuracy.py, open_meteo.py, inputs.py). No
finding in this set rests on a test-file mutation, so none is voided on that
ground.

---

## D3-01 — PredictiveInsightSensor attributes (M31, sensor.py:1086)

**Re-run.** `RESULT M31.fast_closure_scripts_failing=0 count` (10 scripts).
`load1=2.5` at the run, `thread_factor=1.0` (counts). Quiet log
`D3-M31.gate.log`: `QUIET_EXIT=0`.

**My number.** `consequence_delta = 20 → 0 published attributes`, all 20
non-`None` under a realistic `predictive_info` payload. The finding's title
says 21; the correct count is **20** (`consequence.py`,
`M31_predictive_insight_attributes`).

`load_bearing_evaluations`: **entities.py `n_eval=5`, `n_load_bearing=4`** —
the gate constructs this sensor and builds a non-empty attribute dict four
times, and asserts nothing about it. This is an **assertion gap**, not an
input gap. `features.py n_eval=0` (sensor.py is not in features.py's
closure).

**Perturbation** (add the named check): I did not add the assertion, but the
converse holds — `grep -c predictive_optimization_insight tests/*.py
tests/*.mjs` = **0 references in the whole suite**, and the number the
finding rests on (0 failing scripts) sits against a null control that is
also 0, so the harness distinguishes nothing by itself. What makes it a real
gap is my 4 load-bearing evaluations that the gate watches and ignores.

**Attacks.** (a) Reachability: the entity ships on every install
(`sensor.py:1063`), is named and translated (`en.json`,
`sv.json`), and `README.md:591` tells users to *read this sensor* when
predictive optimization looks idle. (b) Consequence: no plan changes. The
sensor's **state** (a mode word) is computed from `predictive_info`
separately at sensor.py:1070-1082 and survives the mutant; only the 20
diagnostic attributes go. The shipped card does not read them
(`grep` in `www/heatpump-optimizer-card.js`: 0 hits), so the loss lands on
user dashboards and templates only. (c) `env_drift --all` cannot see it by
construction: golden records `_build_data_dict()`, not entity attributes.

**Vote: weaken(low).** Decisive number: **0 of 96 published power-schedule
steps and 0 of 55 drift scenarios change; the loss is 20 diagnostic
attributes on one sensor.** A documented troubleshooting surface going
silently blank is real and the suite is completely blind to it (0
references, 4 load-bearing evaluations ignored) — but nothing a user pays
for moves, which is what separates medium from low in this set.

---

## D3-02 — `hours_until_next_window` inside-a-window branch (M19, dhw_schedule.py:433)

**Re-run.** `RESULT M19.fast_closure_scripts_failing=0 count`. My own
`env_drift --all` with M19 on the working tree: **`rc=0`, `NO UNCLAIMED
DRIFT: 55 scenario(s)`, and not one scenario moved** (`drift-M19.log`,
`wall_s` ~190, load1 40 — a count, unaffected). Quiet log `D3-M19.gate.log`:
`QUIET_EXIT=0`.

**My number.** `consequence_delta = 7 of 24 hours of the day` change the
published `dhw_next_window_in_hours` for the shipped window text
`06:00-08:30, 17:00-22:00`: hours reading `0.0` drop from 8 to 2, and
inside-window hours read 9.0-12.0 instead of 0.0 (e.g. 18:00 → `12.0`).

`load_bearing_evaluations`: **entities.py 6 of 6**, **features.py 4 of 133**
→ **10 load-bearing evaluations across the gate, all green**. Assertion gap,
not the dead branch the finding describes.

**Perturbation.** The finding's perturbation is "add the named check". I ran
the sharper one and it moves: with the mutant, entities.py computes a
different value six times and still exits 0.

**Attacks — the finder's mechanism is wrong in detail.** The claim "every
golden solve starts at 00:00 [outside every window]" is false. My census
(`census.py`) shows **2 of 49 plan scenarios start *inside* a window**:
`dhw_schedule_off` and `dhw_learned_windows`. The reason the mutant survives
the golden set is different and I measured it: both carry the window
`[(0.0, 24.0)]`, so at `hour=0.0` the shipping branch returns `0.0` and the
mutant's loop returns `(0.0-0.0) % 24 = 0.0` — the guard is *entered* and
cannot disagree. Half the finder's proposed fix ("one golden scenario
starting inside a window") therefore would not catch this unless the window
starts at a different hour.

**Consequence.** `next_window_in_hours` is **published-only**. Its three
production producers (optimizer.py:3672/4887, coordinator.py:4121/6704) feed
sensor attributes; nothing reads it back. The one behavioural consumer,
`pump_schedule.vvc_should_run`, calls it *after* testing
`hour_in_windows(hour, windows)` itself (pump_schedule.py:50-56), so the
deleted branch is unreachable from the only decision path.

**Vote: weaken(low).** Decisive number: **10 load-bearing evaluations, 0
scenarios moved in `env_drift --all`, and 0 production decisions read the
value** — a wrong number on a dashboard for 7 hours a day, never a wrong
plan.

---

## D3-03 — DHW setpoint advisor's negative-price floor (M13, coordinator.py:1676)

**Re-run.** `RESULT M13.fast_closure_scripts_failing=0 count`. Quiet log
`D3-M13.gate.log`: `QUIET_EXIT=0`, 202 s.

**My number.** A coordinator with a legal 500 l cylinder and a 48 h price
array at a constant `total`:

| mean total | shipping `recommended_setpoint` | mutant | negative `cost_per_day` entries |
|---|---|---|---|
| +1.20 | 50 °C | 50 °C | 0 |
| 0.00 | 50 °C | 50 °C | 0 |
| **−0.40** | **50 °C** | **60 °C** | **7 of 7** |

`consequence_delta = 8` published fields (the recommendation plus all seven
`cost_per_day` entries) at a non-positive mean price; **0** at a positive or
zero one.

`load_bearing_evaluations`: **features.py 0 of 5, entities.py 0 of 6** — the
gate runs the sweep 11 times and never once with `mean_price <= 1e-6`. A
clean **input-coverage gap**.

**Perturbation.** Sweeping the price from +1.20 through 0.0 to −0.40 moves
the recommendation only in the last cell — the harness is not measuring a
constant, and the guard is exactly as load-bearing as its comment says.

**Attacks.** (a) Reachability: `total` is Tibber's consumer total
(coordinator.py:5426), so it must be the *48 h mean including tax and grid
fee* that goes non-positive, not one negative spot hour. That is rarer than
the finding implies — but the repo asserts the input itself, in the sibling
comment 60 lines above at coordinator.py:1611: "negative spot spells are
real in a Nordic spring", and `tests/profiles.py` ships an unused
`summer_negative`. (b) Consequence: the advisor is read-only — it publishes
a recommendation, it never writes a setpoint. The damage needs a user to act
on a one-day artefact, and a raised setpoint then persists.

**Vote: weaken(low).** Decisive number: **the flip 50 → 60 °C happens on
exactly one of the three price levels I fed, and the gate evaluates the site
11 times without ever reaching it.** Real, cheap to close (one
`summer_negative` sweep check), but advisory-only and behind an input the
median install never sees — that is a low, not a medium.

---

## D3-04 — non-finite grid-fee rate (M32, grid_fee.py:141)

**Re-run.** `RESULT M32.fast_closure_scripts_failing=0 count`. Quiet log
`D3-M32.gate.log`: `QUIET_EXIT=0`, 200 s.

**My numbers — this is the one the finder under-rates.**

1. `is_valid_spec` flips **False → True** for `= nan`, `= inf` and `= -inf`
   (unchanged True for `= 0.25`). `config_flow.py:2467` is the only
   validator on that text field, so the mutated build **accepts the string a
   user types**.
2. `GridFeeSchedule.from_config` then yields
   **`n_nonfinite_in_fee_vector = 24 of 24`** (shipping: 0 — `from_config`
   catches `GridFeeError` and degrades to no rules).
3. The coordinator's implausible-fee audit is blind:
   `max_abs_component` returns **`worst = 0.0`, audit does not fire**, because
   `abs(nan) > worst` is False (grid_fee.py:299, coordinator.py:6217).
4. **The plan silently degrades.** `nanplan.py`, `winter_single_dhw`,
   one NaN in 96 price steps:

   | | status | Σ commanded power over 96 steps | non-finite entries in the schedule |
   |---|---|---|---|
   | clean | `optimal` | 138.54 | 0 |
   | one NaN step | `failed (no usable starting point)` | **202.87 (+46.5 %)** | **0** |

   The published schedule contains no NaN, so
   `HeatpumpOptimizerSensorBase.__init_subclass__`'s non-finite scrub never
   sees it, and the heat pump is commanded 46.5 % more power.

`load_bearing_evaluations`: **features.py 0 of 15** `_parse_rule`
evaluations carry a non-finite rate; the existing negatives at
features.py:6351-6353 are `banana`, `Frunday` and a missing rate. Input
coverage gap, and it is a one-line fix (two more `not is_valid_spec(...)`).

**Perturbation.** Sweeping the rate token across `nan`/`inf`/`-inf`/`0.25`
moves `is_valid_spec` on three of four and leaves the fourth alone; sweeping
the NaN count 0 → 1 → 96 moves the solver status and the commanded power.
Neither number is a constant.

**Attacks.** Reachability is the **highest of the seven**: a config-flow
text field, no third party, no corrupt store, no rare market. Consequence is
the only one in the set that *silently changes a plan* — the seat's own
dividing line. Against the finding: the shipped code has a second net
(`from_config`'s `except GridFeeError`) for the hand-edited-store path, so
only the config-flow path is exposed; and the deletion is hypothetical.

**Vote: verify — and the severity is understated.** Decisive number: **+46.5 %
commanded power from a legal config-flow string, with 0 non-finite values in
the published schedule and the magnitude audit reporting `worst = 0.0`.**
I record this as `low → medium`; I am voting `verify` rather than
`weaken(...)` because the vote vocabulary has no term for raising a
severity, and refusing to verify a correct finding over an understated
severity would be the wrong error.

---

## D3-05 — corrupt `lead_sigma` key (M21, accuracy.py:382)

**Re-run.** `RESULT M21.fast_closure_scripts_failing=0 count`. Quiet log
`D3-M21.gate.log`: `QUIET_EXIT=0`, 200 s.

**My number.** `AccuracyTracker.from_dict({"lead_sigma": {"abc": 0.4,
"2.0": 0.7}})`: shipping returns a tracker with 1 entry; mutant raises
`ValueError`. Numeric-key stores with a `nan` or `"junk"` **value** behave
identically on both sides (0 entries) — which is exactly what
features.py:9845 tests (`{"1.0": nan, "3.0": 0.4, "6.0": "junk"}`, every key
numeric).

`load_bearing_evaluations`: **features.py 0 of 6** — the gate calls
`from_dict` six times, never with a non-numeric key. Input-coverage gap.

**Attacks — the finding's consequence claim is wrong, and I measured it in
the shipping code.** The title says the ValueError "would abort coordinator
setup". It would not. `_async_load_accuracy` (coordinator.py:7230) wraps
only `await self._accuracy_store.async_load()` in its `try`;
`AccuracyTracker.from_dict` is *outside* it — and the coroutine is one of
**twelve fire-and-forget `self._spawn(load())` calls**
(coordinator.py:672-690). Setup completes. What actually happens is quieter
and permanent: the task dies at its first line of work, so `_accuracy`,
`_dhw_accuracy`, `_defrost`, `_peak_tracker`, `_mode` and `_comfort_learner`
(six pieces of learned state, including the user's operating mode) stay at
their constructor defaults **on every restart**, with a `_LOGGER` line
nobody reads.

Reachability: JSON object keys are always strings and the integration only
ever writes numeric ones (`as_dict`), so the input needs external
corruption — a hand-edited or damaged `.storage` file.

**Vote: verify (low).** Decisive number: **0 of 6 `from_dict` calls in the
gate carry a non-numeric key**, so the handler is genuinely untested; the
severity stays low because the trigger is store corruption, not anything a
user or the integration can produce. The stated consequence ("abort
coordinator setup") should be corrected to "one of twelve background loads
dies and six learners silently reset every startup".

---

## D3-06 — unparsable Open-Meteo timestamp (M30, open_meteo.py:194)

**Re-run.** `RESULT M30.fast_closure_scripts_failing=0 count` —
`tests/open_meteo.py` itself exits 0 with the mutant applied. Quiet log
`D3-M30.gate.log`: `QUIET_EXIT=0`, 205 s.

**My number.** A 6-sample block with one malformed `time` entry:
`consequence_delta` = **5 usable samples → 0, and a `ValueError` out of
`_parse_block`**.

`load_bearing_evaluations`: not obtainable through my instrument, and the
reason is itself the answer — `tests/open_meteo.py` loads the production
module with `importlib.util.spec_from_file_location` into a fresh module
object (tests/open_meteo.py:84-94), bypassing `sys.modules`, so it is
isolated from the package copy. Its 38 checks cover nulls, out-of-range
values and missing variables; every `time` fixture in the file is a valid
ISO string. Input-coverage gap, confirmed by reading the fixtures rather
than by instrumentation.

**Attacks — the consequence is worse than the finding says, in a way that
argues for keeping it low.** The finding says the ValueError "would
propagate out of `fetch()` and lose the block". I traced it: nothing catches
it between `_parse_block` and the coordinator's outer handler —
`_fetch_forecast` (open_meteo.py:422-431) has no `try`, `async_refresh`
(whose docstring at open_meteo.py:315 promises "Never raises") has none
around line 327, `_fetch_solar_forecast` (coordinator.py:5655) has none, and
`_async_update_data`'s `except Exception` at coordinator.py:4444 converts it
to `UpdateFailed`. So the whole coordinator cycle fails and every entity
goes unavailable until Open-Meteo fixes its response. That is loud, not
silent — the failure mode this seat cares least about — and the trigger is a
third-party API contract change, not anything a user does.

**Vote: verify (low).** Decisive number: **one bad stamp takes 5 good
samples to 0 and the suite's 38 open-meteo checks all pass**; low is right,
because when the guard is gone the integration stops with an error rather
than planning wrongly.

---

## D3-07 — negative published `age_minutes` (M15, inputs.py:352)

**Re-run.** `RESULT M15.fast_closure_scripts_failing=0 count`.
**There is no quiet-window gate log for M15** — `quiet/` holds
`D3-M{13,19,21,30,31,32}.gate.log` only, and `quiet_window_request.top_six`
does not include it. So this finding, alone in the set, has never faced
`stress.py`, `edge.py` or `backtest.py`. (Reading those three: none
constructs an `InputReader`, so I expect nothing there, but it is an
evidence gap the report presents as if closed.)

**My number.** `consequence_delta = 1` published field: a state stamped 45
min in the future reads `age_minutes = -45.0` instead of `0.0`. A past stamp
and an exact-now stamp are identical on both sides.

`load_bearing_evaluations`: **features.py 13 of 4642** — the gate does
compute a negative age 13 times and passes, so this is an assertion gap, not
an input gap, and the finding's mechanism ("No freshness check uses a future
timestamp") is **false on this box**. But the 13 is a calendar artefact, and
I say so against my own number: features.py freezes `NOW = 2026-02-01 12:00`
(tests/features.py:88) while some fixtures carry a real-clock
`last_reported`; today is 2026-09-02, so those states are ~213 days "in the
future" relative to the frozen now. On a machine whose wall clock is before
2026-02-01 the count is 0. The suite does not *deliberately* reach the
branch — `grep minutes_ago(-` in tests/features.py: 0 hits.

**Attacks.** Consequence: the value is displayed in the input-health
details and nothing else. The staleness rail is `age > limit`; a negative
age is "fresh" under both the shipping code and the mutant
(`stale_verdict_future_60limit = False` on both sides), so **no decision
changes** — only a cosmetic minus sign on a dashboard, in the presence of
clock skew.

**Vote: weaken(low).** It is already low, and I am voting `weaken(low)` to
carry the two corrections rather than to lower the number: the stated
mechanism is wrong, and the evidence is one full gate short of the other
six. Decisive number: **0 decisions change (`stale_verdict` identical on
both sides); 1 displayed field changes, and only under clock skew.**

---

## D3-08 — six scripts, 30-34 mutants, 0 kills, 53 solves

**Re-run.** All seven mutants leave validate.py, optimality.py,
manual_plan.py, plan_view.py, solar_alignment.py and card.mjs at `rc=0` —
reproduced, seven for seven, in `closure-M*.log`. Solve census reproduced
with my own counter (`solvecount.py`, wraps
`HeatPumpOptimizer.optimize`): **validate 22, optimality 9, manual_plan 21,
plan_view 1 = 53 optimize() calls per gate**, exactly the finder's number.

**Stated perturbation — it moves.** Delete one `run(...)` line from
tests/validate.py → `SOLVECOUNT tests/validate.py optimize_calls=21`
(from 22). Down by exactly 1, as stated. Reverted.

**My own numbers, and they split the finding in two.**

1. **Reachability.** Of the seven mutated production sites, each of the four
   solver scripts executes **exactly one** (the M19 site):
   validate.py `n_eval=28`, manual_plan.py `44`, optimality.py `8`,
   plan_view.py `2` — and `n_load_bearing=0` in all four. So "killed none of
   30" is mostly arithmetic: they never run the code. That is not a defect.

2. **Positive control — does the class of mutation they *do* guard kill
   them?** One-line production change,
   `optimizer.py:2863 maxiter=200 → maxiter=1` (cripple the space-heating
   solve; not a guard deletion):

   | script | rc | evidence |
   |---|---|---|
   | optimality.py | **1** | `FAIL the production iteration budget buys a materially better plan [full-budget 82.17 vs starved 67.76 (-21.3 % gap)]` |
   | validate.py | 0 | `NO ISSUES` |
   | manual_plan.py | 0 | — |
   | plan_view.py | 0 | — |
   | entities.py | 0 | — |

   So optimality.py **does** guard solver quality and the finder's defence of
   it holds; its 0/30 is a property of the deletion-mutant sample.
   validate.py's is not. With the solver crippled, validate.py's own printed
   table moves **2 of its 21 scenarios by +40.9 % and +177.0 % cost**
   (`winter, no DHW` 23.28 → 64.49; `2zone winter, no DHW` 58.30 → 82.17)
   and it prints `NO ISSUES` and exits 0. (Only two moved because the
   DHW-enabled scenarios go through the other call site,
   optimizer.py:4716, which I left at `maxiter=300`.)

**Vote: verify (low).** Decisive number: **validate.py solves 22 plans, 22
of them at 223 recorded CI seconds, and does not notice one costing 177 %
more.** The finding is right that these scripts spend 53 solves without
killing a guard deletion; its own defence ("they guard solver quality") is
true for optimality.py and refuted for validate.py, which is where the
resource case actually is.

---

## D3-09 — measured closures are the transitive package import

**Re-run.** `closure_precision.py` with `ROOT` pinned to my worktree (the
original derives it from `__file__`, which points at the audit-register
checkout, currently `6914370` — a different tree):

`RESULT validate.py.closure_prod=38`, `RESULT validate.py.executed_prod=8`,
`RESULT validate.py.forced_modules=30` — the finding's headline number,
reproduced exactly. Also optimality 8/38, solar_alignment 8/38,
plan_view 9/38, manual_plan 16/38, entities 36/45, open_meteo 1/2.
`RESULT modules_forced_somewhere=34`.

**Perturbation.** The harness header's own perturbation is inert as written:
it names `pump_mode`, which validate.py **already executes** (the executed
set is `__init__, const, dhw_schedule, mixing_valve, optimizer, pump_mode,
tariff, thermal_model`), and adding a call to it left `executed_prod=8`. I
substituted a module that is actually in the forced list — prepend
`from heatpump_optimizer.narrative import render; render([], 'en')` to
tests/validate.py → **`executed_prod=8 → 9`, `forced_modules=30 → 29`**. The
number moves in the stated direction; the harness is not measuring a
constant. Reverted.

**Is it a hole a careless commit could walk through? No — measured.**
`executed_not_in_closure=[]` for all seven scripts I ran: the closure is a
strict **over**-approximation everywhere. An over-approximate closure runs
*more* scripts than needed under `GATE_SCOPE=auto`; it can cost CI seconds,
it cannot let a regression past. I checked the reverse direction directly
from `tests/closures.json`: every script that imports the package carries
38-45 production modules and the only omissions are modules the script
cannot reach (`binary_sensor`, `button`, `climate`, `config_flow`; and
features.py, which does not import `sensor.py`, correctly omits it). There
is no under-approximation to walk through.

**And the proposed fix moves risk in.** "Make the package import lazy so
closures shrink to what runs" would replace a guaranteed over-approximation
with a *recorded* one, and a closure recorded from a run that did not take a
lazy import path is exactly the under-approximation the current design
cannot have. That is worth saying in the register next to the fix.

**Vote: verify (low), as a resource finding only.** Decisive number:
**`executed_not_in_closure = 0` on 7 of 7 scripts** — the over-approximation
is total in one direction and absent in the other, so this is CI seconds,
not a gate hole. The finding says as much in `proposed_fix_scope` ("either
accept…"); the register should carry it as hygiene and should not adopt the
lazy-import fix without re-deriving and re-checking closures.

---

## D3-10 — the drift gate cannot fail on the five SENSITIVE fixtures

The most consequential claim in the set, so I established it with two runs
of my own that differ in exactly one line.

**Re-run / reproduction.** M01 applied to the working tree,
`env_drift.py --all c398fc84…` through `drift_run.py`:

```
  MAY-DRIFT wood_coil: 458 leaves moved (machine-sensitive; ...)
         wood_coil.baseline_cost: 156.162896 vs 677.817758
  1 MAY-DRIFT SCENARIO(S) MOVED, unjudged
NO UNCLAIMED DRIFT: 55 scenario(s) checked against c398fc84…
RESULT env_drift_rc=0 count
```

458 leaves, `baseline_cost` ×4.34, **`rc=0`** — the finder's number, from a
harness that never commits. **Only `wood_coil` moved**: the other 54
scenarios are byte-identical, so this is precisely the escape route the
finding describes and not a broad regression that something else would
catch.

**The finding's stated perturbation does not move the number, and I say why.**
It proposes removing `wood_coil` from `SENSITIVE` at env_drift.py:109 and
records `rc=0` — no movement. That is not a property of the gate: with
`wood_coil` gone from `SENSITIVE` but still listed in
`tests/golden/claimed_drift.txt`, `may_drift_error` should return
`MAY-DRIFT OUT OF SCOPE` and `main()` should return 1 at line 863, so the
recorded `rc=0` is not reproducible as described. The finding does not
depend on it.

**My perturbation, which does move it.** Same tree, same mutant, same 458
leaves; delete the one line
`# may-drift: wood_coil -- machine-sensitive; ...` from
`tests/golden/claimed_drift.txt` (verified: `_may_drift` then returns four
names, not five) and re-run:

```
  DRIFT wood_coil: 458 leaves moved vs c398fc84…
1 UNCLAIMED DRIFT(S) vs c398fc84…
RESULT env_drift_rc=1 count
```

**rc 0 → 1 on one committed comment line.** The exemption is the entire
cause; nothing else in the run changed. Restored afterwards.

**Mechanism, read in the shipping code.** `may_drift_hits` is appended at
env_drift.py:1022 and never folded into `drifted`; the verdict at line 1091
is `if drifted or stale: return 1`. There is no magnitude test on that path.
All five SENSITIVE names are committed as `may-drift:` in
`claimed_drift.txt`, and `_may_drift`'s docstring says outright that the
block "does not expire with VERSION" — so this is permanent, not a stale
claim someone forgot to remove.

**Attack — how wide is the blind spot?** My census (`census.py`) measures
what a regression would have to avoid to escape through it. Every SENSITIVE
fixture shares 9 or 10 of its scenario switches with *judged* scenarios:

| fixture | switches | unique to it | judged scenarios sharing a switch |
|---|---|---|---|
| valve_storage_smart_write | 6 | **0** | 10 |
| wood_two_tank | 9 | **0** | 10 |
| wood_two_tank_smart_write | 9 | **0** | 10 |
| valve_upper_direct_slab | 7 | 1 (`topology_layout`) | 10 |
| wood_coil | 9 | 1 (`dhw_wood_coil_enabled`) | 9 |

So three of the five carry nothing the judged 50 do not also carry, and the
escape route is exactly two config switches wide — which is precisely where
M01 sits (`dhw_coil_draw_reduction`, behind `dhw_wood_coil_enabled`). The
blind spot is real, permanent, and narrower than "the gate cannot fail on
five fixtures" makes it sound. Note also that the finding's own description
of M01 ("the `max(0, ...)` clamp deleted") understates the patch: it is an
operator-precedence scramble,
`draw_kw * max(0.0, dhw_setpoint - t_in) / span` →
`draw_kw * dhw_setpoint - t_in / span`, which is why one fixture moves by
4.34× rather than a little. And M01 is not a survivor — features.py kills it
("coil identity holds at T_w=70"), so the second net held here.

**Vote: verify (medium).** Decisive number: **`rc=0` with 458 leaves moved
and `baseline_cost` 156.16 → 677.82, flipping to `rc=1` when one comment
line is deleted from `tests/golden/claimed_drift.txt`.** The repo's
behavioural gate is structurally unable to fail on 5 of its 55 scenarios,
by design and permanently; the finder's proposed fix (judge SENSITIVE on a
coarse BLAS-stable projection such as `baseline_cost` within 5 %, keeping
the exact comparison unjudged) would have caught a 334 % move.

---

## Summary

| id | vote | decisive number |
|---|---|---|
| D3-01 | weaken(low) | 20 attributes → 0; 4 load-bearing evaluations in entities.py, gate green; 0 plan or drift changes |
| D3-02 | weaken(low) | 10 load-bearing evaluations, 0 of 55 scenarios moved, 0 production decisions read the value |
| D3-03 | weaken(low) | 50 → 60 °C only at mean total ≤ 0; 0 of 11 gate evaluations reach it |
| D3-04 | verify (severity understated: low → medium) | +46.5 % commanded power from a legal config-flow string, 0 non-finite values published, audit `worst=0.0` |
| D3-05 | verify (low) | 0 of 6 `from_dict` calls carry a non-numeric key; consequence is 6 learners silently reset, not an aborted setup |
| D3-06 | verify (low) | 5 samples → 0 plus a `ValueError` that reaches `UpdateFailed`; 38 open-meteo checks all pass |
| D3-07 | weaken(low) | 0 decisions change; 13 of 4642 load-bearing evaluations, and the 13 is a calendar artefact; no quiet-window gate log exists |
| D3-08 | verify (low) | 53 optimize() calls reproduced; validate.py misses a plan costing +177 % and prints `NO ISSUES` |
| D3-09 | verify (low), resource only | `executed_not_in_closure = 0` on 7 of 7 scripts — over-approximation only, not a gate hole |
| D3-10 | verify (medium) | 458 leaves, `baseline_cost` ×4.34, `rc=0` → `rc=1` on deleting one `may-drift:` line |

Nothing in this set is voided: every perturbation I ran moved its number in
the stated direction, except D3-10's as written by the finder, for which I
supplied and executed a substitute that does move it, and D3-09's
harness-header perturbation, for which I supplied a module the script does
not already execute.
