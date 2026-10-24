# D3 round 3 — verifier 2 of 2, refute-first

Baseline `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1`, detached worktree, nothing
committed to the checkout. Machine: 8-core Apple M1, macOS Darwin 25.6.0,
python3 3.11.5, numpy 2.4.6 / scipy 1.17.1, five BLAS thread variables pinned
to 1 before numpy in every process, `GATE_JOBS=1`. `tests/stress.py` never
run; the gate lock never taken. The box was shared throughout: `load1` moved
between **5.8 and 135.3** while these numbers were taken. **Every number below
is a count**, except the four wall-clock figures that are explicitly marked
provisional.

My assigned line of attack is the population and the consequence: are the 34
representative, does the per-module spread mean anything, do the survivors
matter, and do the two end-to-end solver scripts earn their runtime.

## What I ran

| harness | what it is | where |
|---|---|---|
| the finder's `prescreen.py` | re-run **exactly as its header says**, `--only M04,M09,M11,M12,M14,M26 --tier 1 --workers 3 --slot-prefix v2`, with my own fresh baseline capture | `verify-2/rerun_tier1.json` |
| the finder's `prescreen.py --tier 2` | `--only M24`, to re-take one survivor's `features.py` verdict | `verify-2/rerun_m24_tier2.json` |
| the finder's `verdicts.py` / `analyse.py` | re-run over the finder's stored record | reproduced byte-identically |
| `verify-2/sampling.py` | mine: re-weights the sample back to the uniform pool, survival by closure size, a permutation test on the module spread | counts only |
| `verify-2/reach.py` | mine: does the value gate even **execute** each mutated line (coverage.py 7.16.0 over the `--all` capture) | `cov/golden.cov` |
| `verify-2/summary_check.py` | mine: the finder's own kill rule **without** the 1200-character tail window | `verify-2/summary_check.json` |
| `verify-2/consequence.py` | mine: equivalent-mutant and consequence classification of all 22 survivors | counts only |
| `verify-2/arith.py` | mine: four **arithmetic** mutants against `validate.py`, `optimality.py`, the cheap scripts and the differential gate | `verify-2/arith.json` |

Reproduction of the finder's own record, first: `verdicts.py` re-run over
`prescreened_merged.json` rewrites `PRESCREENED.md` **byte-identically**
(`diff` empty), and `analyse.py` prints every RESULT the report cites —
`survivors=22`, `survival_rate=0.647`, `killed=12`,
`killed_only_by_differential_gate=5`, `survivors_loose=1`. The arithmetic in
the report matches the record it was taken from. What I dispute is the record.

## The null control the finding rests on, and it holds

Three `--all` captures of the **unmutated** tree — the finder's (hours
earlier, its slot), mine (fresh, my own `TMPDIR`), and a third taken under
coverage instrumentation — are the same file:

```
591ae2b59f7780b1  finder's  $TMPDIR/d3audit/base_all.json
591ae2b59f7780b1  mine      d3v2tmp/d3audit/base_all.json
591ae2b59f7780b1  mine      d3v2tmp/cov_capture_b.json   (under coverage)
```

`RESULT null_control_moved_fixtures=0`, `may_drift_exempt=0`, all 55 fixtures
present on both sides, compared with `env_drift._diff_leaves` /
`may_drift_judged_diffs` themselves. So on this box the differential gate has
no false-positive drift, and "55 fixtures byte-identical" means what the
finder says it means. The five drift-only kills (M01, M23, M25, M26, M28) are
signal, and my own re-run reproduces M26's (`rc 0 -> 1`, capture crashed on
`IndexError: list index out of range` at `tariff.py:308`).

## The verdict rule: the finder is right that the naive one is worthless, and wrong that its own one is safe

I re-ran `prescreen.py` exactly as its header says on six mutants —
`--only M04,M09,M11,M12,M14,M26 --tier 1 --workers 3 --slot-prefix v2`, three
worker slots, my own fresh baseline capture (`RESULT baseline_fixtures=55`,
`RESULT worker_slots=3`, final `load1=13.41`).

**Under the as-written rule (`rc` moved *or* any new `FAIL` line), 6 of 6 were
"killed"** — five of them credited to `entities.py`. So the naive rule is
worse than the finder says: on my subsample it kills 100%, not 97%, and
`survivors_loose=1` reproduces on the full record.

**Under `verdicts.py`'s strict rule my six verdicts match the finder's table
exactly**: M09 killed by `structure.py`, M26 killed by `env_drift.py --all`,
and M04, M11, M12, M14 survive. The distinction is real and it is load-bearing.

But the reason the loose rule kills everything is not only the negative arms
the finder identified. In my run all five spurious `entities.py` kills are the
*same* check, `a8:register_once`, with a **different** random `extra=[...]` set
each time — `['apply_manual_plan__dup', 'apply_schedule__dup',
'diagnose_interval__dup']` on M04, a different triple on M09, M11, M12 and
M14, and absent from the same slots' own unmutated baselines. That is a flaky
check, on five mutually unrelated mutations. The negative-arm story explains
some of the noise; nondeterminism explains the rest.

And the strict rule that replaced it has its own hole, in the opposite and
more dangerous direction. That is section 3 below.

## D3-01 — the number is real, the count is not, and the diagnosis is wrong

### 1. The sampling is sound. That was my first line of attack and it failed.

`mutant_pool.py` re-runs to the same **3367** candidates
(`pool_size_matches_finder=True`). The draw is weighted by
`module_weight x kind_weight`, so the 22/34 estimates the survival rate of the
*consequence-weighted* population, not of the pool. Re-weighting each mutant by
the reciprocal of its draw weight — `sum(s_i/w_i) / sum(1/w_i)`, the estimate
for a **uniform** draw from the 3367 —

```
RESULT unweighted_survival=0.647    (the finder's)
RESULT ipw_survival=0.644           (uniform-pool estimate)
RESULT weighted_survival=0.647      (consequence-weighted)
```

The weighting moves the rate by 0.003. (Caveat, stated because it bounds the
claim: the 17 sampled modules are 77.7% of the pool and 86.1% of the draw
weight; the 37 unsampled modules are not covered by this re-weighting.)

**Thin closures do not explain it either** — the opposite, if anything:

```
RESULT survival_by_closure_size={"6 scripts":"4/4","8 scripts":"0/2",
                                 "13 scripts":"10/15","18 scripts":"8/13"}
RESULT survival_closure_ge13=18/28 = 0.643
RESULT survival_closure_lt13=4/6  = 0.667
```

The 18-script closure — 931.6 recorded seconds, `stress.py`, `edge.py`,
`validate.py` and `optimality.py` in it — survives at 0.615, statistically
indistinguishable from the 13-script closure's 0.667, and `config_flow.py`'s
8-script closure kills **both** its mutants. Closure size buys nothing here,
which is an argument *for* the finding and against my own hypothesis.

### 2. The per-module spread the finder narrates is not established

`survivors_by_module` reads 4/4 optimizer, 4/4 sensor, 2/2 price_model against
0/3 tariff and 0/2 config_flow. A permutation test over the 17 module cells
(statistic: `sum (obs - n*p)^2 / (n*p*(1-p))`, 200 000 shuffles of the 22
survivor labels):

```
RESULT spread_statistic=22.323
RESULT spread_p=0.0652 (permutations=200000)
RESULT fisher_one_sided_optimizer_vs_tariff=0.0286
```

p = 0.065 for the whole spread, and the one pair the report names is the
post-hoc extreme of 17 cells (uncorrected p = 0.029). At n = 34 with cells of
1–4 the spread is what this sample size produces. The **aggregate** survives
leave-one-out (0.600–0.710, reproduced); the module story does not.

### 3. Seven of the 22 "survivors" were killed. The rule could not see it.

This is the refutation. `verdicts.py:strict_kill` scores a kill from three
things — a changed exit code, the literal string `Traceback (most recent call
last)`, or a changed `N of M ... FAILED` count — and reads all three out of
`tail`, which `prescreen.py:run_script` truncates to the **last 1200
characters**. `entities.py` and `features.py` print log noise after their
summary line, so for exactly those two scripts the summary is regularly
outside the window; `summary_failed()` then returns `None`, and the slot
baseline already exits 1 (fresh `git init`, no commit), so the exit code does
not separate them either. A genuinely new failing check is then filed as "a
changed FAIL *detail* string".

It is in the finder's own stored record. Six recorded survivors carry a new
**named** failing check (name-level, `a8:register_once` excluded — see below),
and a seventh carries a traceback:

| id | production line | the check that went red, in the finder's own record |
|---|---|---|
| M07 | `sensor.py:1283` | `entities.py` — *the state summarises the same signals, and says so when there are none (#246)* |
| M19 | `accuracy.py:378` | `features.py` — *a corrupt store loads what survives and never bricks the score loop* |
| M24 | `external_heat.py:457` | `features.py` — `TypeError` at `external_heat.py:461`, 1.6 s against a 137 s median |
| M27 | `sensor.py:2115` | `entities.py` — *the learned comfort weight is visible* |
| M30 | `inputs.py:390` | `features.py` — *a missing entity is reported as such* (+2 more) |
| M32 | `dhw_schedule.py:118` | `features.py` — *and renders back to the string the user typed* (+1) |
| M33 | `sysid.py:234` | `features.py` — *a recent run blocks another* |

Every one of those names is the semantic twin of its mutation — M30 turns
`missing_entity` into `unavailable` and the check that fails is named
`missing_entity`; M33 disables the minimum-days guard and the check is named
*a recent run blocks another*. These are not negative arms reporting.

**Re-executed, not argued.** `verify-2/summary_check.py` runs the same script
on the same mutant in a fresh slot and reads the whole output:

```
sum-0 BASELINE tests/entities.py rc=1  1 of 1294 ENTITY CHECKS FAILED
M07   tests/entities.py rc=1  2 of 1294 ENTITY CHECKS FAILED  delta=1
      new_names=['the state summarises the same signals, and says so when there are none (#246)']
M27   tests/entities.py rc=1  2 of 1294 ENTITY CHECKS FAILED  delta=1
      new_names=['the learned comfort weight is visible']
sum-1 BASELINE tests/features.py rc=1  1 of 2136 FEATURE CHECKS FAILED
M19   tests/features.py rc=1  2 of 2136 FEATURE CHECKS FAILED  delta=1
      new_names=['a corrupt store loads what survives and never bricks the score loop']
M30   tests/features.py rc=1  5 of 2136 FEATURE CHECKS FAILED  delta=4
      new_names=['a configured entity that does not exist is missing_entity',
                 'a missing entity is reported as such',
                 'and the freeze reason names both the condition and the key (missing_entity)',
                 "the reap Home Assistant's stop fires keeps the loop running (#525)"]
M32   tests/features.py rc=1  3 of 2136 FEATURE CHECKS FAILED  delta=2
      new_names=['and in the weekly grammar when the configuration names days',
                 'and renders back to the string the user typed']
M33   tests/features.py rc=1  2 of 2136 FEATURE CHECKS FAILED  delta=1
      new_names=['a recent run blocks another']
RESULT rechecked=6 recorded-survivors
RESULT actually_killed=6 mutants (M07,M27,M19,M30,M32,M33)
```

Six of six, each with the reporter's own count moving against the same slot's
own unmutated run. (One of M30's four is the `#525` wall-clock check the
finder itself records as flaky; the other three are the mutation's own
semantics.)

**M24, with the finder's own harness.** `prescreen.py --only M24 --tier 2`
reproduces the crash: slot baseline `features.py` rc=1 with one known git-only
failure (`recorded_at = 'unknown'`, #363), mutant `features.py` rc=1 in
**1.5 s** ending

```
File ".../external_heat.py", line 461, in _decay
    elapsed = (now - state.last_active).total_seconds() / 60.0
TypeError: unsupported operand type(s) for -: 'datetime.datetime' and 'NoneType'
```

The direction of the defect matters: it can only turn a kill into a survivor,
so it inflates the finding, and it does so precisely on the two scripts that
do the most checking.

*Why `a8:register_once` is excluded and nothing else is:* it fires on five
mutually unrelated mutants in my own re-run (M04 optimizer, M09 coordinator,
M11 optimizer, M12 sensor, M14 price_model) with a **different** random
`extra=[...]` set each time and is absent from the same slots' unmutated
baselines. It is flaky, not a kill. Every other new name I counted appears on
exactly one mutant and matches its semantics. (That flake is worth its own
look by whoever owns `entities.py`; I did not chase it.)

### 4. Five of the remaining survivors cannot be killed by any test

An equivalent mutant is not a suite gap. Each of these is settled by a line in
production, not by an opinion:

| id | line | why no input can distinguish it |
|---|---|---|
| M05 | `optimizer.py:4771` `max(c_dhw, 0.05)` -> `c_dhw` | `optimizer.py:4000` is the **only** assignment of `c_dhw` and it is `max(params.dhw_tank_thermal_mass, 0.05)`; `_repair_dhw_floor` has one caller (4335) which passes it. The clamp is re-clamping an already-clamped value. |
| M06 | `optimizer.py:1134` | the only production producer is `coordinator.py:8950` `np.full(n_steps, baseline)`, so `values.size == n_steps` and the mutant's `concatenate([values, np.full(0, ...)])` is the same array |
| M10 | `coordinator.py:2293` | every action in `_async_drive_pumps` is already inside `if vvc_entity:` (2298) or `if space_entity:` (2317); with both falsy the mutated body reaches neither |
| M17 | `thermal_model.py:2435` | `_Horizon.solar_radiation` is typed `np.ndarray` (optimizer.py:1180) and `optimize()` replaces `None` at 2243, so both batch call sites pass an array; the only caller that could pass `None` is `tests/features.py:2424` |
| M31 | `thermal_model.py:324` | the cached value is an immutable `str` computed purely from `key`; disabling the cache is a CPU change, and only `stress.py` — excluded by the D3 brief — could notice |

M05 and M10 are **two of the five bullets D3-01 leads with**. The M10 bullet
also states a contract wrongly: *"the 'only entities the user explicitly
configured are ever touched' contract is unpinned in that direction"* — that
contract is enforced by the two inner guards, not by the early return, and the
mutation leaves it intact.

### 5. What the survivors actually are: an input gap, not an oracle gap

`verify-2/reach.py` measures whether the value-comparing gate even executes
each mutated line (coverage.py line data over the `--all` capture; a second
run with `--branch` for the arcs):

```
RESULT golden_reach_all=16/34 mutants
RESULT golden_reach_survivors=8/22    RESULT golden_reach_killed=8/12
RESULT kill_rate_given_executed=0.500  RESULT kill_rate_given_unexecuted=0.222
RESULT golden_reach_by_module={"sensor.py":"0/4","coordinator.py":"0/4",
   "optimizer.py":"4/4","tariff.py":"3/3","thermal_model.py":"3/3", ...}
```

and the arcs, for the survivors whose line *is* executed:

```
M04 optimizer.py:3838     arcs -> [3818]        guarded body never entered
M06 optimizer.py:1134     arcs -> [1136]        guarded body never entered
M17 thermal_model.py:2435 arcs -> [2438]        guarded body never entered
M18 topology.py:570       arcs -> [572]         guarded body never entered
M31 thermal_model.py:324  arcs -> [325, 326]    both arcs taken (equivalent anyway)
```

So **not one** of the 22 survivors is a case of "a fixture produced a different
value and the comparison ignored it". Fourteen lines are never executed by the
value gate at all; four are executed with the guarded branch never taken, so
`if False:` is literally a no-op on every path the 55 fixtures walk; M05 is
provably inert, M11's clamp never binds, M29's rail is never reached, M31 is a
cache. That reframes the finding and its remedy: the fast gate's value oracle
is byte-exact and did not look away — the suite lacks **inputs**. Assertions
would not have caught most of these; fixtures would.

### 6. The corrected numbers

```
RESULT finder_survival=22/34 = 0.647
RESULT mis_scored_kills=7        (M07,M19,M24,M27,M30,M32,M33)
RESULT equivalent_mutants=5      (M05,M06,M10,M17,M31)
corrected survival            = 15/34 = 0.441
RESULT consequential_survival = 10/29 = 0.345   (real gaps / killable mutants)
```

Per module, after both corrections: `optimizer.py` 2/2 (was 4/4),
`thermal_model.py` 0/1 (was 2/3), `coordinator.py` 1/3 (was 2/4),
`external_heat.py` 0/1 (was 1/1), `sensor.py` 2/4 (was 4/4). The same
permutation test on the corrected labels gives
`corrected_spread_p=0.2066` (200 000 shuffles, 29 killable, rate 0.345) — the
module spread does not survive the correction either.

The ten that remain, each a single production line, with the check that should
have failed (`verify-2/consequence.py` carries the table):

| id | production line | what a user gets |
|---|---|---|
| M03 | `coordinator.py:3898` | learned house heat loss is never written to the store; every restart forgets it |
| M04 | `optimizer.py:3838` | the legionella run-up keeps demanding heat below a floor it already meets |
| M11 | `optimizer.py:3234` | a warm start may sit below a pinned lower bound |
| M12 | `sensor.py:1002` | `UpperFloorTempSensor` publishes `None` in every state |
| M14 | `price_model.py:137` | a `nan`/`inf` day is admitted into the learned price shape |
| M15 | `dhw_learning.py:344` | the tank's cooling coefficient never learns |
| M16 | `sensor.py:885` | `extra_state_attributes` returns `None` where HA is owed a mapping |
| M18 | `topology.py:570` | the wood-coil caption disappears from the topology description |
| M20 | `wood_fuel.py:232` | a tz-aware stamp against a naive store misorders or raises |
| M29 | `price_model.py:70` | the shape guard rail doubles, 3x -> 6x |

**Vote: `weaken` to `medium`.** A third of a consequence-weighted sample
surviving the fast gate is still a real and useful finding, and the ten
survivors that remain are genuine gaps with named consequences — the ones I
would not want shipped are `coordinator.py:3898` (learned heat loss never
persisted, so every restart forgets it), `price_model.py:137` (below),
`sensor.py:1002` and `sensor.py:885` (a published value and an attribute
mapping that go `None` in every state), and `dhw_learning.py:344` (the tank's
cooling coefficient never learns). But the headline as written is 64.7% when
the measured number is 44.1%, five of its members cannot be killed by anything,
two of the five bullets it leads with are equivalent mutants, and its
"22 of 34 survive the whole fast gate" reads as an oracle indictment of a gate
whose oracle is byte-exact and whose real deficit is fixtures. `high` is not
earned by ten gaps, two of which are one `entities.py` line each and two of
which (M18, M29) a user would struggle to notice.

## D3-02 — the mechanism is right, the universal is false

`sensor.py` is the thinnest closure sampled (6 scripts, reproduced below), and
my reach measurement is blunt about why its mutants live: **0 of 4** mutated
`sensor.py` lines is executed while all 55 fixtures are built. The fixtures
record `coordinator.data`; no entity property is evaluated. That part I
confirm, independently of the finder's reasoning.

The claim itself does not survive. *"Between them nothing asserts what number a
sensor publishes. Every published value in the integration is in this gap."*
`tests/entities.py` carries **70** `native_value` references, including exact
equalities — `by_name["Measured Power"].native_value == 2.4`,
`by_name["Comfort Weight"].native_value == 6.4`,
`IndoorTempSensor(...).native_value == 21.4`. And two of the four `sensor.py`
mutants are killed by those very checks once the tail window is gone:

* M27 `sensor.py:2115` (`ComfortWeightSensor.native_value`) — `entities.py`
  goes `1 of 1294` -> `2 of 1294`, the new name being *the learned comfort
  weight is visible*. **Executed by me.**
* M07 `sensor.py:1283` (the predictive-info sentence) — same, new name *the
  state summarises the same signals, and says so when there are none (#246)*.
  **Executed by me.**

So the sensor gap is 2 of 4, not 4 of 4, and it is specific rather than
universal: `UpperFloorTempSensor.native_value` (M12) and
`HeatPumpActionSensor.extra_state_attributes` (M16) are unpinned, and the
sensors the owner already cared about are pinned by name in `entities.py`. The
consequence the finding leads with is real for M12 — the sensor goes
permanently blank in Home Assistant and merges green — and the fix is one line
beside the sixty that are already there.

**Vote: `weaken` to `medium`.** Number: 2 of 4 `sensor.py` mutants survive
(0.500), not 4 of 4; 0 of 4 lines reached by the value gate.

## D3-03 — one guard stands, one is caught, and the consequence is worse than claimed

`price_model.py:137` survives, and I executed what it costs rather than
describing it. With the guard disabled, one `nan` hour in a 24-hour day:

```
UNMUTATED: observe_day(nan day) -> False   days [0,0]   shape clean
MUTANT   : observe_day(nan day) -> True    days [1,0]
           nan hours in the learned shape: 24 of 24
           shape_for(+7d, same profile): 24/24 nan, trust=0.2
           predict(level=1.0) -> nan
           as_dict() serialises NaN into the store
```

The `mean <= 1e-6` guard below it cannot catch this (`nan <= 1e-6` is False),
one bad hour poisons all 24 of that profile's hours, and the poison is
*persisted*. Reach: the line is never executed by the value gate (0/2 for this
finding's two lines), so no fixture observes a non-finite day at all.

The other half does not survive. `accuracy.py:378` (M19) is killed by
`tests/features.py` — *a corrupt store loads what survives and never bricks the
score loop* — in the finder's own record, and the guard's own comment is the
check's subject. The finding's own sentence, *"the guard's own author wrote
down the consequence; nothing in the suite reproduces it"*, is wrong: the suite
reproduces it and the harness lost the verdict.

**Vote: `weaken` to `medium`.** Number: 1 of the 2 named guards is unpinned,
not 2 of 2; the surviving one poisons 24 of 24 shape hours and `predict()`
returns `nan`.

## D3-04 — verified, and I ran the step the finder did not

Reproduced end to end in my own slot, with the mutant applied from
`mutants.json` and a real commit in the slot so `recorded_at` resolves:

```
structure.py on the mutant            rc=1   cut_fetch 132 -> 131  BETTER
                                      "1 STRUCTURE BUDGET(S) IMPROVED AND NOT YET RECORDED
                                       Nothing here is a violation."
structure.py --record                 rc=0   cut_fetch = 131  recorded_at = 1dbc817...
structure.py after the record         rc=0   STRUCTURE RATCHET PASSED
solar_alignment.py on the mutant      rc=0   ALL SOLAR ALIGNMENT CHECKS PASSED
```

My independent `prescreen.py` re-run of M09 agrees: `structure.py` rc 0 -> 1,
every other script in its closure green. The differential gate is not re-taken
by me — `prescreen.py` skips the capture once an assertion has moved — but the
finder's record has it as a full 333 s capture with `killed: false, moved: []`,
which is consistent with the byte-identical fixtures I measured on the
unmutated tree. So the whole distance between a dead
Open-Meteo fallback and a green gate is a documented one-line command, and I
executed the "after the record" half that the report asserted.

One correction of emphasis. The report leans on *"`tests/solar_alignment.py` —
the script whose one job is that irradiance lands on the right optimizer
steps — runs and passes"*. That script's own docstring scopes it to
`_forecast_arrays`, the coordinator-to-optimizer seam; the mutated line is in
`_update_current_state`, deciding whether Open-Meteo is consulted at all. It
passes because the defect is outside the seam it names, not because it is
weak at its job. (My arithmetic mutant A3, which shifts solar gain by one step
*inside* the objective, also leaves it green — same reason.)

**Vote: `verify`, severity `medium` as filed.** Number: 1 of 12 scripts moves,
it reports `BETTER`, and `--record` then returns rc=0 with the fallback still
disabled.

## D3-05 — the restraint is right, and the reason is measurable

### The line-deletion result reproduces; it is the wrong operator

`validate.py` and `optimality.py` each ran for 8 mutants and killed 0
(reproduced from the record). I built the class the finder declined to build:
four **arithmetic** single-line mutants on the solve path, nothing deleted, no
line count moved (`verify-2/arith.py`):

| id | line | what it does |
|---|---|---|
| A1 | `optimizer.py:1960` | `np.sum(prices * p)` -> `np.sum(np.roll(prices,1) * p)` — every step priced at the previous step's price |
| A2 | `optimizer.py:1556` | overshoot penalty `* 5.0` -> `* 0.5` — the house may run hot |
| A3 | `optimizer.py:2344` | solar gain shifted one step late |
| A4 | `thermal_model.py:1464` | `1.0 + wind_sensitivity*w` -> `1.0 - ...` — wind now *reduces* modelled heat loss |

Every script of the closure that this box may run, plus the differential gate,
against each of the four:

```
RESULT kills_typing_ruler=0/4      RESULT kills_deployment_shape=0/4
RESULT kills_plan_view=0/4         RESULT kills_solar_alignment=0/4
RESULT kills_manual_plan=0/4       RESULT kills_config_flow_steps=0/4
RESULT kills_structure=0/4         RESULT kills_entities=0/4
RESULT kills_validate=0/4          RESULT kills_optimality=2/4
RESULT kills_env_drift_all=4/4     RESULT arith_survivors=0/4
```

* `optimality.py` kills **A1** and **A4**, both on the same check — *the
  forced-off pin is honoured, or reported as safety-released*, `1 of 14
  OPTIMALITY CHECKS FAILED`. A mispriced objective and a sign-flipped wind
  term both move the plan enough that its quality floor notices.
* `validate.py` kills **none of the four**, at 22.8 assertions per solve
  against `optimality.py`'s 2.8. Assertion density is not what catches
  arithmetic; asking whether the plan is still *good* is.
* The differential gate kills A1 (12+ moved leaves across `away_setback`,
  `building_preset`, …), A2 (`capacity_tariff_15min.compressor_starts 7 vs
  6`) and A3 (`shoulder_two_zone` 447 leaf diffs). **A4's capture is
  unresolved, not a kill I measured**: it returned `rc=-15`, a SIGTERM under
  `load1=135.31`, and my harness scores a non-zero capture as a kill exactly
  as `prescreen.py` does. Counted honestly: 3 of 4 measured, 1 unresolved.
  (The finder's own record has one crashed capture, M26, and that one is
  `rc=1` — a real `IndexError` in `tariff.py:308`, which my re-run
  reproduces through `entities.py`. No false kill there.)

So the finder's restraint is **right**, and for a reason it did not have:
line deletion is the wrong operator for an end-to-end solver script, and
`optimality.py` does catch the right operator. What neither script has on
these 12 mutants is a **unique** kill — the differential gate was there
first every time. Their case is not "they catch what nothing else catches",
it is "a fixture diff cannot tell a better plan from a worse one and a
quality floor can", and that case is worth 82.4 recorded seconds. Two things
follow for whoever prices the suite next: the 8 line-deletion mutants said
nothing about these scripts, and a larger arithmetic sample is the
measurement that would.

### The resource inversion is real, deliberate, and its seconds are wrong

`closure.py select --files` re-derived by me, both `MODE: SCOPED`:

```
tariff.py       MODE: SCOPED -- 18 script(s) run, 3 scoped out
coordinator.py  MODE: SCOPED -- 13 script(s) run, 8 scoped out
sensor.py       MODE: SCOPED --  6 script(s) run, 15 scoped out
config_flow.py  MODE: SCOPED --  8 script(s) run, 13 scoped out
```

The mechanism is dependency direction, and it is correct: `stress.py`,
`edge.py`, `validate.py`, `optimality.py` and `backtest.py` all have
`tariff.py` in their measured closure and **none** has `coordinator.py` —
those scripts import the optimizer chain, which imports `tariff`,
`thermal_model`, `dhw_schedule` and `wood_fuel`; nothing imports the
coordinator, because the coordinator is the Home Assistant glue *above* the
solver. A closure is "what can change this script's answer", and a
coordinator-only change genuinely cannot change a solver script's answer. Not
an error — the price of measuring the right thing.

The seconds, though, should not be quoted as the cost of a change.
`derive_closures.sh:58-59` records `golden.py` with `--only
__no_such_scenario__` and `env_drift.py` with `--cache-key <ref> --all` — both
no-ops — so `closures.json` carries `tests/env_drift.py: 0.7s` and
`tests/golden.py: 0.4s`. Every one of the 17 sampled modules selects the drift
gate (it runs whenever anything under `custom_components/` changes, by rule),
and one `--all` capture measured **164.9 s** in my run (*provisional, load1
13.4*) against a **313 s** median in the finder's own 32 recorded captures
(*provisional*), with the gate taking two of them. So the table's 152.2 s for a
`coordinator.py` change omits its largest term, and the 6.1x inversion it
reports (931.6 vs 152.2) is nearer 2x once the omitted lane is counted on both
sides. `stress.py` at 586.6 s of 932.8 s total recorded (62.9%) reproduces
exactly.

**Vote: `verify`, severity `low` as filed.** Number: `validate.py` kills **0 of
4** arithmetic mutants, `optimality.py` **2 of 4**, the differential gate 3 of
4 measured (the fourth capture SIGTERMed under load) — so across 12 mutants of
two operator classes neither end-to-end script has a **unique** kill, and the
restraint against deleting them rests on what a fixture diff cannot *say*
(better or worse), not on what it cannot catch.

## Attacks I ran that changed nothing

* **Contention.** Every headline number is a count. The four wall-clock
  figures are marked provisional and none carries a claim.
* **Wrong gate mode.** The differential arm is `--all` throughout, with
  `env_drift`'s own `_diff_leaves`, `SENSITIVE` and `may_drift_judged_diffs`;
  four of the five drift-only kills are outside the five `SENSITIVE` fixtures,
  so the default five-fixture mode would have missed them. CI runs `--all`.
* **Grid artefact.** Leave-one-out over 17 modules (0.600–0.710) reproduces,
  and the re-weighted estimate (0.644) says the cells are not driving the
  aggregate. The *spread* between cells is the part that does not survive.
* **Null control.** Three unmutated captures, byte-identical. The
  `price_model` consequence has its own null control (unmutated returns
  `False`, shape stays clean).
* **`FakeHass` versus real Home Assistant.** The survivors I kept are
  properties and store paths (`native_value`, `extra_state_attributes`,
  `async_save`), not executor or coroutine behaviour, so the stub's
  serialisation is not what is holding them up.

## What I did not do

* `tests/stress.py`, `tests/edge.py`, `tests/backtest.py` — never run (box
  rule). `edge.py` is still the most likely killer of the ten remaining
  survivors, and every survivor verdict here stays provisional against it.
* No `GATE_SCOPE=full` run; no gate lock taken.
* I re-screened 6 of the 34 mutants with the finder's harness and re-took the
  verdict on 7 more with my own; the other 21 verdicts are read from the
  finder's stored record, which reproduces.
* The Node lane was not driven.
