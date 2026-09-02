# D3 round 2 — verifier seat 1 of 3

Baseline `c398fc84eec25fc44b60d74aae05b9a2da205884`. Worktree
`audit-r2-D3` read-only (still detached at the baseline, `git status` shows
only `tools/audit/`; nothing committed, no gate lock taken). All my own work
ran in scratch copies under `/tmp/verify-D3-1/`, and the D3-10 reproduction in
a **private throwaway git repo** at `/tmp/verify-D3-1/drift` with a private
`DRIFT_CACHE_DIR` — the shared drift cache and the audit worktrees were never
written.

Interpreter `…/tvofi-claude/.venv/bin/python` (3.13.1, numpy 2.5.2 /
scipy 1.18.1), `PYTHONPATH=tests/hastub`, five BLAS variables pinned to 1.

**`RESULT thread_factor=1.000`** (600×600 matmul ×20 under the pin).
**`RESULT load1=3.49`** at the end of the run (1.64 at the start; the box was
busy throughout). Every number I report below is a **call count, a boolean, an
exit code or a leaf count** — contention-immune by the README's rule. I claim
no wall, CPU or RSS number anywhere, so the load1 ceiling does not bite.

## My harnesses

Four, all written for this verification, all under `/tmp/verify-D3-1/`:

| harness | what it produces |
|---|---|
| `mkprobe.py` + `census.sh` | the **branch census**: an instrumented copy of the baseline tree with a counter at each of the seven mutated sites, run over every gate script |
| `observable.py` | **observable(M)**: baseline vs mutant on the same probe, in separate interpreters, for all seven mutants |
| `callcensus.py` | **solves(script)** and **closure_precision(script)** from `sys.setprofile` call events (D3-08, D3-09) |
| `killpower.sh` | **kill_rate(script, S)** over a four-mutant sample with `features.py` as the positive control (D3-08) |
| `d10_setup.sh` | my own SENSITIVE-fixture mutant in a private repo (D3-10) |

### Metric definitions (mine, stated once)

1. **`branch_executions(M, script)`** — the number of times, while `script`
   runs *at the baseline*, that control reaches the code mutant `M` deletes.
   For M19 (whose deletion is a shortcut, not a behaviour) I refine this to
   **`differing_evaluations(M19, script)`**: the probe computes the mutant's
   would-be return alongside the baseline's and counts disagreements.
   `differing_evaluations == 0` is a **proof** that the script cannot kill the
   mutant, independent of what the script asserts. `> 0` with the script
   passing is a proof that the script reached the code and asserted nothing
   about it. Both are counts.

2. **`observable(M)`** — 1 when a legal production input exists for which
   baseline and mutant differ at the mutated site. **This is the number the
   finder never produced**, and it is the one that decides the
   equivalent-mutant refutation: a finding "the suite fails to kill M" is void
   unless `observable(M) == 1`.

3. **`solves(script)`** — entries into `HeatPumpOptimizer.optimize`, counted
   from `sys.setprofile` `call` events.

4. **`closure_precision(script)`** — `executed / |closure|`, where `closure` is
   the production `.py` set recorded in `tests/closures.json` and a module
   counts as *executed* when a **CO_OPTIMIZED** code object from it is entered
   (never a module or class body). I also report a stricter
   `executed_rt`: the same, but only while no *imported* module's `<module>`
   body is on the stack, so import-time execution does not count as use.

5. **`kill_rate(script, S)`** — fraction of a mutant sample `S` on which
   `script` exits non-zero.

6. **`sensitive_blindness`** — the pair (rc of `env_drift.py --all`, leaves
   moved in the SENSITIVE fixtures). The finding holds iff rc == 0 with a
   materially non-zero leaf count.

**Verdict summary: verify ×8, weaken ×2 — no refutations.** The two weakens
(D3-02, D3-05) are about the finder's stated *mechanism*, not the gap; in
D3-02's case my number makes the finding **worse**, not better.

---

## The full-gate confirmation (read, not re-run)

I read the six quiet-window logs rather than re-running them, as instructed.
All six carry `ALL TEST SCRIPTS PASSED`, `QUIET_EXIT=0`, ~200 s wall, a
distinct mutant `QUIET_HEAD`, and
`QUIET_CMD=… GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF=c398fc84… GATE_JOBS=1`.
I enumerated the scripts each log actually ran: **16**, plus
`SKIP: tests/golden.py (GOLDEN_MODE=drift checks fixtures via env_drift.py
instead)` and `SKIP: tests/rolling.py (set SLOW=1 …)`.

**The wrong-gate-mode attack fails**: `tests/env_drift.py --all <baseline>` is
in every one of the six logs and passed. This is not a five-fixture-golden
artefact.

**The caveat, checked myself.** `tests/run.sh:306-309` gates `rolling.py`
behind `SLOW=1`, so the push/PR gate skips it, as the quiet agent said. I
answered "would `rolling.py` have killed it?" two ways:

*By census.* Running `rolling.py` under my instrumented tree
(`CENSUS rolling rc=0 wall=149s`, `ALL 33 ROLLING CHECKS PASSED`):

```
RESULT rolling_calls_M31=0  M13=0  M32=0  M21=0  M30=0  M15=0
RESULT rolling_calls_M19=417  branch=138  differ=106
```

Five of the six mutated sites are **never entered** by `rolling.py`. It
constructs the coordinator directly (`FakeHass()`, no states), so no
`InputReader` read (M15), no entity layer (M31), no `_dhw_setpoint_sweep`
(M13), no `_parse_rule` (M32), no `from_dict` (M21), no HTTP parse (M30).
Zero executions of the mutated code means the process cannot differ; those
five are settled without running anything.

*By execution*, for the one it does reach. `rolling.py` hits M19's difference
**106 times** — at hours 8.0, 18.0 and 20.0 inside demand windows, through
`optimizer.optimize → _optimize_with_dhw → _build_dhw_requirements`, where the
mutant would answer 12.0 / 10.0 / 9.0 instead of 0.0. I applied M19 to a
scratch tree and ran it directly (no lock taken):

```
RESULT rolling_M19_rc=0  wall=228s   ->  ALL 33 ROLLING CHECKS PASSED
```

**`rolling.py` kills none of the six.** The caveat is real but harmless: the
nightly `SLOW=1` run would not have caught any of them either. The reason is
structural — `next_window_in_hours` is a *published* value only
(`optimizer.py:3672 → 4887 → sensor.py:964/1012/1103`); nothing reads it back
into a schedule, so a closed-loop simulation that asserts on temperatures,
costs and plan stability is blind to it by construction.

---

## The branch census (D3-01 … D3-07)

One instrumented run per gate script, at the **baseline**. Cells are
`calls / branch / differ`.

```
script           M31        M19          M13     M32     M21     M30     M15
backtest         0/0/0      0/0/0        0/0/0   0/0/0   0/0/0   0/0/0   0/0/0
dst_checks       0/0/0      0/0/0        0/0/0   0/0/0   0/0/0   0/0/0   0/0/0
edge             0/0/0     38/0/0        0/0/0   0/0/0   0/0/0   0/0/0   0/0/0
entities         5/4/4      6/0/0        0/0/0   0/0/0   0/0/0   0/0/0  22/0/0
features         0/0/0    133/2/2        3/0/0  13/0/0  11/0/0   0/0/0  4642/13/13
golden           0/0/0     74/2/0        2/0/0   1/0/0   0/0/0   0/0/0   0/0/0
manual_plan      0/0/0     44/0/0        0/0/0   0/0/0   0/0/0   0/0/0   0/0/0
open_meteo       0/0/0      0/0/0        0/0/0   0/0/0   0/0/0  39/0/0   0/0/0
optimality       0/0/0      8/0/0        0/0/0   0/0/0   0/0/0   0/0/0   0/0/0
plan_view        0/0/0      2/0/0        0/0/0   0/0/0   0/0/0   0/0/0   0/0/0
solar_alignment  0/0/0      0/0/0        0/0/0   0/0/0   0/0/0   0/0/0   0/0/0
stress           0/0/0     87/2/0        0/0/0   0/0/0   0/0/0   0/0/0   0/0/0
validate         0/0/0     28/0/0        0/0/0   0/0/0   0/0/0   0/0/0   0/0/0
--- not in the push/PR gate ---
rolling          0/0/0    417/138/106    0/0/0   0/0/0   0/0/0   0/0/0   0/0/0
```

`golden.py` stands for what `env_drift.py --all` captures (55 scenarios). The
four Node scripts are trivially 0 — a Python mutant cannot move them.

**`RESULT gate_differing_evaluations: M31=4  M19=2  M13=0  M32=0  M21=0  M30=0  M15=13`**

That splits the seven into two kinds, which the finder's report does not
distinguish and which have different fixes:

* **Assertion gaps (M31, M19, M15)** — the gate *executes the differing code*
  and passes anyway. No new fixture is needed; an assertion is.
* **Input-coverage gaps (M13, M32, M21, M30)** — the gate calls the enclosing
  site 5 / 14 / 11 / 39 times and never on the input that matters. A fixture
  is needed.

### The equivalent-mutant attack, run and failed

```
RESULT observable_M31=1  observable_M19=1  observable_M13=1  observable_M32=1
RESULT observable_M21=1  observable_M30=1  observable_M15=1
RESULT observable_total=7 of 7
```

Baseline vs mutant, same probe, separate interpreters:

| M | baseline | mutant |
|---|---|---|
| M31 | 20 attribute keys, `solar_reduction_factor=0.6` | `{}`, 0 keys |
| M19 | `18h→0.0`, `7h→0.0`, `12h→5.0` | `18h→12.0`, `7h→10.0`, `12h→5.0` |
| M13 | negative price: rec **48**, `hotter_costs_more=True`, costs +2.83…+3.63 | rec **60**, `hotter_costs_more=False`, costs **−2.83…−3.63** |
| M32 | `is_valid_spec('…= nan'/'= inf'/'= -inf')` all False | all **True**; `rate = nan` reaches `parse_rules` |
| M21 | `from_dict` loads `{1.0: 0.25}`, skips `'abc'` | raises `ValueError: could not convert string to float: 'abc'` |
| M30 | keeps 3 of 4 samples, drops the bad stamp | raises `ValueError: Invalid isoformat string: 'NOT-A-TIME'` out of `_parse_block` |
| M15 | future stamp → `0.0`, past → `30.0` | future → **−90.0**, past → `30.0` |

No mutant is equivalent. No refutation is available on that ground.

---

### D3-01 (M31) — **verify**, medium

*Deciding number:* `entities.py` enters the branch **4 times**, builds
**20** attributes each time (not 21 — the patch removes 20 keys, and my probe
counts `n_keys=20`; a small factual correction), and **passes 538 checks**.
`golden.py` / `env_drift --all` enter it **0 times** — the coordinator capture
is `_build_data_dict()`, never an entity's attributes.

*The missing assertion, named.* The production mutation is one line in
`custom_components/heatpump_optimizer/sensor.py:1086`. Grep over
`tests/*.py` + `tests/*.mjs`:

```
predictive_optimization_insight   -> 0 files
PredictiveInsightSensor           -> 0 files
predictive_insight                -> 0 files
wind_anticipation_factor          -> 0 files
rain_anticipation_factor          -> 0 files
dhw_preheat_lead_hours            -> 0 files
dhw_idle_min_temperature          -> 0 files
dhw_planned_heating_hours         -> 0 files
future_solar_6_12h_kwh            -> 0 files
avg_future_precip_mmh             -> 0 files
dhw_required_temperature_now      -> 0 files
```

`solar_reduction_factor` and `pre_heat_urgency` appear **only** in
`tests/golden/*.json` — recorded *coordinator* payloads, not entity
attributes, so they are the wrong layer.

I attacked the two generic sweeps that could have caught it and both are
blind by construction: `entities.py:1064` walks every entity's
`extra_state_attributes` but asserts only **non-finiteness** — `{}` passes
trivially; `entities.py:595-608` asserts only that a list of sensor classes
does not *crash* before the first update, and `PredictiveInsightSensor` is not
in that list. The missing check is one key-set assertion on the collected
`sensor.*_predictive_optimization_insight` entity.

The mutation is in a production file, not a test file (brief item 4). The path
is reachable in real Home Assistant — this is the published entity, not a
`FakeHass` artefact.

**Vote: verify at medium.** 20 published attributes vanish; 16 gate scripts,
`env_drift --all` (55 scenarios) and `rolling.py` all pass.

---

### D3-02 (M19) — **verify the finding, weaken the mechanism**

*Deciding number:* **`differing_evaluations(M19) = 2` in `features.py` and
106 in `rolling.py`; 0 everywhere else in the gate.**

The finder's claim ("no script fails") is correct and confirmed by the quiet
full gate. Its **mechanism is wrong**, and the correction makes the finding
stronger, not weaker:

> "The published value is only ever computed at hour 0.0 in the golden set …
> the branch is dead to the suite."

It is not dead. My probe caught it live, with the stack:

```
dhw_schedule.py:433 hours_until_next_window
  <- optimizer.py:3624 _build_dhw_requirements
  <- optimizer.py:4503/1604 _optimize_with_dhw
  <- optimizer.py:2196 _solve  <- optimizer.py:2199 optimize
  <- features.py:16663 _lg_e2e     hour=18.0 -> 0.0 vs 12.0
```

So the suite runs the branch through the **whole optimizer stack**, the value
it feeds `_build_dhw_requirements` moves by **12 hours**, and 1576 `features.py`
checks plus 15 other gate scripts pass anyway.

I also attacked the one place the drift gate could have caught it. `grep -l
dhw_next_window_in_hours tests/golden/*.json` → **44 fixtures**, of which 43
record `6.0` and one, `dhw_schedule_off.json`, records `0.0`. That looked like
a live kill until I checked the fixture: its windows are `"00:00-24:00"` and
`START` is hour 0.0, so the following window also starts at 0.0 and **the
mutant returns 0.0 too**. My probe agrees independently:
`golden.py` shows `M19 74/2/0` — the branch is taken twice, differs zero
times. Same for `stress.py` (`87/2/0`). The attack fails.

*The missing assertion, named.* Production line
`custom_components/heatpump_optimizer/dhw_schedule.py:433-434`. Grep over
`tests/*.py` + `tests/*.mjs`:

```
hours_until_next_window    -> 0 occurrences
dhw_next_window_in_hours   -> 0 occurrences (outside tests/golden/*.json)
hour_in_windows            -> 7 occurrences (rolling, validate, stress, features)
```

The function has **no test at all**; only its sibling `hour_in_windows` does.

*Consequence attack.* I traced the value: `next_window_in_hours` flows only to
`predictive_info` and three sensor attribute dicts. **Nothing reads it back
into a schedule**, which is why 106 differing evaluations inside `rolling.py`
still leave all 33 checks green. That caps the harm at a wrong published
number and it is why the finder's proposed fix is mis-scoped: "one golden
scenario whose START lies inside a DHW window" would **not** have caught this
(the fixture that already starts inside one does not discriminate), and no
end-to-end scenario will, because the value never reaches an asserted output.
The fix that works is the direct unit check the finder also proposes —
`hours_until_next_window(18.0, parse_windows('06:00-08:30, 17:00-22:00')) == 0.0`
— plus an attribute assertion on the published key (which is D3-01's fix).

**Vote: verify the gap at medium; weaken the stated mechanism.** The finding's
"dead to the suite" reasoning and half its fix scope should be replaced by the
executed number: reached 2× in the gate and 106× in the nightly, differing by
up to 12 h, killed by nothing.

---

### D3-03 (M13) — **verify**, medium

*Deciding number:* **`branch_executions(M13) = 0` across the whole gate**, on
`call_executions = 5` (`features.py` 3, `golden.py` 2). The sweep runs five
times; its mean price is positive every time.

*The missing assertion, named.* Production line
`custom_components/heatpump_optimizer/coordinator.py:1676-1677`. All three
sweep checks live at `features.py:7744-7790` and every one of them sets
`_prices = [{"total": 1.0}] * 24`. `tests/profiles.py` ships a
`summer_negative` profile that is never used here.

The check that is missing is **already written** — `features.py:7770`:

> `"hotter tanks cost more per day — the trade the sweep exists to show"`
> `_sweep["candidates"][-1]["cost_per_day"] > _sweep["candidates"][0]["cost_per_day"]`

My observable probe drove the real `_dhw_setpoint_sweep` on a real coordinator
(built with `features.py`'s own two-liner) at three price levels:

| mean price | baseline rec | mutant rec | baseline `hotter_costs_more` | mutant |
|---|---|---|---|---|
| +1.0 | 48 | 48 | True | True |
| **0.0** | 48 | 48 | True | **False** |
| **−0.4** | **48** | **60** | True | **False** |

So the existing assertion **fails under the mutant** the moment it is handed a
non-positive price. The gap is one fixture line, not a new check — that is a
cleaner fix scope than the finder gives, and it makes the finding cheaper to
close.

**Vote: verify at medium.** The consequence is a published `dhw_advisor`
recommendation that flips from 48 °C to 60 °C on a worthless-energy day —
money and comfort, on the path the code comment explicitly protects.

---

### D3-04 (M32) — **verify**, low

*Deciding number:* **`branch_executions(M32) = 0`** on `call_executions = 14`
(`features.py` 13, `golden.py` 1). `_parse_rule` runs fourteen times in the
gate and never once on a non-finite rate.

*The missing assertion, named.* Production line
`custom_components/heatpump_optimizer/grid_fee.py:141-142`. The negative
family is `features.py:6351-6353`:

```python
not _gf.is_valid_spec("Nov-Mar = banana")     # unparsable token
and not _gf.is_valid_spec("Frunday = 0.2")    # unparsable weekday
and not _gf.is_valid_spec("06:00-22:00")      # no rate at all
```

Three negatives, none of them the one `float()` accepts. Grepping the whole
suite for a `nan`/`inf` **rate spec** finds none — every `float("nan")` in
`tests/` is a sensor value, a pin array or a COP humidity, never a grid-fee
rule.

My probe: baseline rejects `= nan`, `= inf`, `= -inf` (all False) and raises
`GridFeeError` from `parse_rules`; the mutant accepts all three and hands back
`rate = nan`. Two `not is_valid_spec(...)` lines close it.

**Vote: verify at low.** A NaN rate reaches `fee_vector` and the coordinator's
magnitude audit compares with `>`, which NaN never satisfies — so it is a
silent poisoning rather than a crash. Low is the right severity: it needs a
hand-typed `nan` in the config to reach.

---

### D3-05 (M21) — **verify the gap, weaken the stated consequence**

*Deciding number:* **`branch_executions(M21) = 0`** on `call_executions = 11`
(all `features.py`). The `lead_sigma` key loop runs eleven times; every key is
a numeric string.

*The missing assertion, named.* Production line
`custom_components/heatpump_optimizer/accuracy.py:382-383`. The corruption
barrier is `features.py:9842-9861`:

```python
"lead_sigma": {"1.0": float("nan"), "3.0": 0.4, "6.0": "junk"},
```

Written entirely from the **values** side — a NaN value and a `'junk'` value.
Every key is `"1.0"`, `"3.0"`, `"6.0"`. Adding `"abc": 0.4` to that dict is
the whole fix. My probe confirms: baseline loads `{1.0: 0.25}` and skips
`'abc'`; the mutant raises `ValueError`.

*The severity attack, which partly succeeds.* The finding's title says a
corrupt key "**would abort coordinator setup**". I checked the call chain and
it does not. `coordinator.py:7230 _async_load_accuracy` has its `try/except`
around **only** `await self._accuracy_store.async_load()`; the
`AccuracyTracker.from_dict(...)` calls sit outside it — so far the finding is
right. But the caller at `coordinator.py:676-690` launches it through
`self._spawn(load())`, one of twelve **fire-and-forget** background tasks.
An unhandled `ValueError` there does not abort setup; it kills one task and
silently skips everything after it in that method — `dhw_accuracy`, the
defrost derate, the peak tracker, the stored mode and the comfort learner all
stay unloaded, every startup, with only a task-exception log.

That is still a real consequence (learned state lost after any store
corruption, invisibly), and low is still the right severity — but the
mechanism sentence should be corrected before it goes in the register.

**Vote: verify at low; weaken the consequence wording** from "would abort
coordinator setup" to "kills one background load task and silently leaves five
learned stores unloaded".

---

### D3-06 (M30) — **verify**, low

*Deciding number:* **`branch_executions(M30) = 0`** on `call_executions = 39`
(all `open_meteo.py`). Thirty-nine timestamps parsed in the gate, none
malformed.

*The missing assertion, named.* Production line
`custom_components/heatpump_optimizer/open_meteo.py:194-195`. `tests/open_meteo.py`
builds five `"time"` arrays (lines 120, 155, 174, 231, 308); every stamp in
all five is a well-formed ISO string. Its 30 checks cover nulls,
out-of-range values, missing variables and a barely-overlapping window — not a
bad stamp.

My probe, on a block of four samples with one `"NOT-A-TIME"`:

```
baseline: {"ok": true,  "kind": "IrradianceSeries", "n_samples": 3}
mutant  : {"ok": false, "raised": "ValueError: Invalid isoformat string: 'NOT-A-TIME'"}
```

The baseline drops the bad sample and keeps three; the mutant lets the
`ValueError` escape `_parse_block`, losing the whole forecast block. One
malformed-stamp sample closes it.

**Vote: verify at low.** The blast radius is one upstream API hiccup costing a
whole forecast block instead of one sample. Low is earned.

---

### D3-07 (M15) — **verify the finding, weaken the mechanism**

*Deciding number:* **`differing_evaluations(M15) = 13` in `features.py`**, on
4642 calls — and `features.py` passes.

The finder's mechanism says:

> "No freshness check uses a future timestamp."

That is **false**. My probe caught thirteen, with the stacks:

```
inputs.py:352 _age_minutes <- inputs.py:413 _age_gate <- inputs.py:484 read_state
  <- features.py:328 / 339 / 345      age = -306705.072 min
inputs.py:352 _age_minutes <- … <- inputs.py:512 read_bool
  <- features.py:373 / 387            age = -306705.072 min
```

These come from `FakeState(...)` constructed without an explicit
`last_updated`, so the state carries the **real wall clock** while the reader's
`_utcnow()` is frozen in the fixture's past — a ~213-day future stamp. Two
consequences worth recording:

1. The clamp is exercised, thirteen times, by the gate — so this is an
   **assertion** gap, not a coverage gap, and no new fixture is needed.
2. The count is **date-dependent**: it exists because the box's clock has
   drifted past the fixture's frozen `NOW`. A judge re-taking this number on a
   different date may see a different count. The *finding* does not depend on
   it — the branch census gives 0 differing evaluations everywhere else, and
   `observable(M15)=1` is date-independent — but the 13 is not a stable number
   and I flag it as such.

*Why nothing notices.* `inputs.py:402-408 _age_gate` compares
`age > limit`; −306705 passes that gate exactly as 0.0 does, and `reading.ok`
is unaffected. The suite has **one** age assertion — `features.py:309`,
`_old_mode.age_minutes > 89` — and it is fed `minutes_ago(90, NOW)`, a
positive age where the clamp does not bind. The negative value survives into
the published input-health details (`inputs.py:141-160`,
`"age_minutes": round(reading.age_minutes, 1)`) with nothing asserting on it.
The missing check is one line: a future-stamped state reads `0.0`, not
negative.

**Vote: verify at low; weaken the mechanism.** "No freshness check uses a
future timestamp" should become "thirteen readings in `features.py` already
carry a future timestamp and no assertion looks at the resulting age".

---

## D3-08 — solves versus kills — **verify**

Re-derived my own way, from `sys.setprofile` `call` events on
`HeatPumpOptimizer.optimize` (the finder used a different instrument):

```
RESULT solves: manual_plan=21  validate=22  optimality=9  plan_view=1
RESULT solves: solar_alignment=0  open_meteo=0  entities=0  features=93
RESULT minimize: manual_plan=64  validate=44  optimality=18  plan_view=2  features=190
RESULT solves_of_the_six_no_kill_scripts = 21+22+9+1+0+0 = 53
```

**53**, exactly the finder's number, from a different instrument. `minimize`
matches on every script (64, 44, 18, 2, 190). `optimize` on `features.py` I
make **93** against the finder's 94 — a one-call difference I did not chase;
it is not load-bearing for any claim. My `simulate*` counts are much larger
than the finder's (e.g. `optimality.py` 2,981,442 vs 30,498) because I count
every `simulate_*` method entry including per-step inner calls while the
finder counted top-level `simulate_trajectory*`; different granularity, not a
disagreement.

*The "killed none" half, which I did not have to take on trust.* The finder's
30–34-mutant pre-screen is theirs; I ran an independent spot check with a
**positive control**. Sample: four mutants the pre-screen records `features.py`
killing (M01 `thermal_model`, M05 `price_model`, M20 `away`, M33 `defrost`) —
i.e. mutants that are demonstrably detectable.

```
RESULT kill_rate(features.py)        = 4/4    <- positive control holds
RESULT kill_rate(solar_alignment.py) = 0/4
RESULT kill_rate(plan_view.py)       = 0/4
RESULT kill_rate(manual_plan.py)     = 0/4
RESULT kill_rate(validate.py)        = 0/4
RESULT kill_rate(optimality.py)      = 0/4
RESULT no_kill_scripts_total         = 0 kills in 20 script-runs
```

Twenty runs of the five Python no-kill scripts on a sample `features.py` kills
outright, zero kills, while those five spend 53 solves. (The sixth,
`card.mjs`, is Node; a Python mutant cannot move it, which is itself part of
the point.) Add the quiet window's six mutants × those six scripts and the
independent evidence is 6 no-kill scripts × 10 mutants with no kill.

**Vote: verify.** I record the finder's own caveat as correct and important:
this is not an argument to delete those scripts — they guard solver quality,
which guard-deletion mutants do not probe. The number stands as the input to
the closure question, not as a deletion proposal.

---

## D3-09 — closure precision — **verify**

Re-derived with `sys.setprofile` call events (the finder inspected code
objects at exit — a different mechanism):

| script | closure | executed (CO_OPTIMIZED) | forced | finder's forced |
|---|---|---|---|---|
| `validate.py` | 38 | **8** | **30** | 30 |
| `solar_alignment.py` | 38 | 8 | 30 | 30 |
| `optimality.py` | 38 | 8 | 30 | 30 |
| `plan_view.py` | 38 | 9 | 29 | 29 |
| `manual_plan.py` | 38 | 16 | 22 | 22 |
| `entities.py` | 45 | 36 | 9 | 9 |
| `features.py` | 40 | 38 | 2 | 2 |
| `open_meteo.py` | 2 | 1 | 1 | 1 |

**`RESULT validate_executed=8 of 38 closure modules`** — the finder's headline
number, reproduced exactly. Not only the counts: my `forced` **list** for
`validate.py` is name-for-name identical to the finder's 30
(`accuracy.py … wear.py`). Two independent instruments, the same set.

My stricter run-time definition (import-time execution excluded) gives
`validate.py` **6 of 38**, `solar_alignment.py` 5, `plan_view.py` 7 — so the
finder's number is if anything generous. `features.py` is 38 either way, and
`entities.py` 36 either way, which is the sanity check that the stricter
definition is not simply undercounting.

*The mechanism attack.* I confirmed the finder's diagnosis independently:
`custom_components/heatpump_optimizer/__init__.py` pulls in `coordinator.py`
and with it the whole integration, so `sys.modules` at exit — which
`closure.py` records — names every module for every script. The finder's own
`const.py` caveat is right and I reproduce it (`open_meteo.py` forced = exactly
`['const.py']`, a genuine import-time-constants dependency that the metric
mis-labels).

**Vote: verify.** Two different instruments, the same counts and the same
module names.

---

## D3-10 — the drift gate cannot fail on the five SENSITIVE fixtures — **verify**

*Reproduced with my own mutant, not the finder's M01.*

**V1**: one line in `custom_components/heatpump_optimizer/thermal_model.py:547`
(`wood_tank_heat_loss_coefficient`), the wood tank's standby loss ×25. Chosen
because the wood store is simulated only in the three `wood_*` golden
scenarios, and all three sit in `env_drift.SENSITIVE` — so the mutant moves
sensitive fixtures and nothing else, which is exactly the condition the
finding needs. Run in a **private git repo** with a private
`DRIFT_CACHE_DIR`; the shared cache and the audit worktrees were untouched.

```
RESULT d10_envdrift_rc=0
RESULT d10_scenarios_byte_identical=50
RESULT d10_may_drift_moved=3   (wood_coil 841 leaves, wood_two_tank 675,
                                wood_two_tank_smart_write 595 = 2111 leaves)
RESULT d10_baseline_cost_move: wood_coil 156.162896 -> 152.914614  (-2.08 %)
                               wood_two_tank 147.909569 -> 144.661287 (-2.20 %)
                               wood_two_tank_smart_write 147.909569 -> 144.661287
RESULT d10_final_line = "NO UNCLAIMED DRIFT: 55 scenario(s) checked"
```

**2111 leaves moved, money moved, exit code 0.** The finding is reproduced
with an independent mutant.

*The mechanism, read out of the source.* `env_drift.py:1021-1027` — a diff in
a `may_drift` scenario appends to `may_drift_hits` and prints, and
`may_drift_hits` is **never** folded into `drifted`; only `drifted or stale`
returns 1 (`env_drift.py:1092-1093`). There is no magnitude test anywhere on
that path. And the committed `tests/golden/claimed_drift.txt` at the baseline
marks **all five** SENSITIVE fixtures `may-drift`, in a block the file's own
header says "does not expire with the stamp and is not part of the
inherited-claims comparison" — so this is a standing condition, not a
per-release accident. `valve_storage_smart_write` and `valve_upper_direct_slab`
printed `may-drift … did not move here` in my run, which is the same
unjudged verdict from the other direction.

*One honest negative.* I tried a second, far larger mutant (×10000) to show
the blindness is magnitude-independent by measurement rather than by reading
the code. It returned **rc=1**, but not because the drift gate caught the
move: the branch capture itself raised and `env_drift` failed on a subprocess
error. That is a crash, which any gate catches, so it demonstrates nothing
about drift judging and I do not count it. The blindness claim rests on V1's
executed rc=0 plus the code path above.

**Vote: verify.** I would rate this the most consequential of the ten. It is
not a missing test — it is a gate that structurally *cannot* fail on five
fixtures, three of which include the money leaf `baseline_cost`, and it holds
for every future change, not just this release.

---

## Attacks run and their outcomes

| attack (brief item 3) | outcome |
|---|---|
| taken under contention | Not applicable: **every** number I report is a call count, boolean, exit code or leaf count. I claim no wall/CPU/RSS number. `thread_factor=1.000`, load1 3.49 recorded for the record. |
| wrong gate mode | **Fails.** All six quiet logs run `env_drift.py --all <baseline>` under `GOLDEN_MODE=drift`, and I re-derived the same blindness for M13/M32/M21/M30 by census (`branch=0` in `golden.py`, which is what `--all` captures). |
| aggregate is a grid artefact | Not applicable to D3-01…07 (per-mutant, not aggregated). For D3-08/09 I dropped no cells and re-derived per script; both aggregate to the finder's number. |
| null control missing | Present on both sides: `observable=7/7` is the null control for the mutants (none is equivalent), and `kill_rate(features.py)=4/4` is the positive control for D3-08's sample. |
| reachable only through the test stub | Checked per finding. D3-01 is the real published entity. D3-05 goes the *other* way — `_spawn`'s "the bare test stub closes the coroutine" is exactly why the load path is untested, and it changes the consequence (recorded above). Nothing here rests on `FakeHass.async_add_executor_job`. |
| severity earned by consequence | D3-03 raised in confidence (48→60 °C recommendation, an existing assertion already fails), D3-05's consequence sentence corrected downward, D3-10 argued as the panel's most consequential. |
| the killing mutation is in a test file (item 4) | **No.** All seven live in `custom_components/heatpump_optimizer/`: `sensor.py:1086`, `dhw_schedule.py:433`, `coordinator.py:1676`, `grid_fee.py:141`, `accuracy.py:382`, `open_meteo.py:194`, `inputs.py:352`. My D3-10 mutant is `thermal_model.py:547`. |
| the mutant is equivalent | **Fails, 7 of 7.** |

## Votes

| finding | vote | deciding number |
|---|---|---|
| D3-01 (M31) | **verify** medium | branch reached 4× in `entities.py` building 20 attributes, 0 suite references to the entity or any of its 11 unique keys, 538 checks pass |
| D3-02 (M19) | **verify** medium / **weaken mechanism** | 2 differing evaluations in the gate, **106 in `rolling.py`**, 0 suite references to `hours_until_next_window`; "dead to the suite" is wrong |
| D3-03 (M13) | **verify** medium | `branch=0` on 5 calls; the mutant flips the recommendation 48 → 60 and `features.py:7770`'s existing assertion would fail under one negative-price fixture |
| D3-04 (M32) | **verify** low | `branch=0` on 14 `_parse_rule` calls; 3 negatives in the suite, none float-parsable |
| D3-05 (M21) | **verify** low / **weaken consequence** | `branch=0` on 11 calls; every key numeric; consequence is a dead background task, not aborted setup |
| D3-06 (M30) | **verify** low | `branch=0` on 39 timestamp parses; baseline keeps 3 of 4 samples, mutant loses the block |
| D3-07 (M15) | **verify** low / **weaken mechanism** | **13 differing evaluations in `features.py`**, which passes; the suite's one age assertion is fed a positive age |
| D3-08 | **verify** | 53 solves in the six; 0 kills in 20 runs against a sample `features.py` kills 4/4 |
| D3-09 | **verify** | `validate.py` 8 of 38, forced list name-identical to the finder's, from a different instrument |
| D3-10 | **verify** | own mutant: rc **0** with 2111 leaves and −2.1 % `baseline_cost` moved in 3 of the 5 SENSITIVE fixtures |

No refutations. No verdict of mine rests on a timing mismatch, so nothing here
should be recorded as `unresolved`.
