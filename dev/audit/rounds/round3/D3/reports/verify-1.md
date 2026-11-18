# D3 verifier 1 of 2 — refute-first

Baseline `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1`, in the detached worktree
`.../audit-r3/verify/D3-1`. Machine: 8-core Apple M1, 8 GB, macOS Darwin
25.6.0, python3 3.11.5, numpy 2.4.6 / scipy 1.17.1 on OpenBLAS, the five BLAS
thread variables pinned to `"1"` in every harness before numpy is imported,
`GATE_JOBS=1`. The box was shared with other live sessions throughout;
`load1` moved between **5.9 and 79.6** while these numbers were taken. Every
number below is a **count or an exit code**, never a time, except the
wall-clock figures in §5, which are that section's subject rather than
evidence for anything else.

`tests/stress.py` was not run and the gate lock was never taken; nothing here
runs `tests/run.sh`. Written under `tools/audit/round3/D3/verify-1/`.

## Method — where my rule differs from the finder's

**My metric definition, one line:** a mutant is **killed** when some script of
its file's measured closure, run against the mutated tree in a real checkout,
**exits non-zero where the same script on the unmutated checkout exits zero**,
or — where a script is red on both sides — when **its own reporter's
`N of M … FAILED` count, read out of the WHOLE output, is larger than the
unmutated run's**. A survivor is a mutant no script in its closure kills.

Two deliberate differences from `verdicts.py`:

1. **The tree is a real git checkout at the baseline, not a copy.** The mutant
   is applied in place, committed (`git commit -a`, so the untracked audit
   directory is never in the commit), the scripts run, and the tree is
   `git reset --hard`ed back to the baseline SHA — checked, not assumed, at the
   start of every mutant. The finder's worker slots were `git init`'d copies
   with **no commit**, which is why two git-dependent checks failed on their
   unmutated baseline; in a real checkout they pass, and the exit code becomes
   a usable detector again.
2. **The summary line is searched over the whole output, never a tail.**

   `tests/entities.py` prints hundreds of lines of integration log *after* its
   own `N of M ENTITY CHECKS FAILED` line, so the finder's 1200-character
   `tail` never contains it.

Harnesses, all under `tools/audit/round3/D3/verify-1/`, each with the header
`tools/audit/README.md` requires and each printing `RESULT <name>=<value>`:

| harness | what it produces |
|---|---|
| `closure_gap.py` | runs named scripts against named mutants in the real checkout; writes `closure_gap.json`, `entities_pass.json`, `features_pass.json`, `node_pass.json` |
| `summary.py` | every aggregate in this report, from those four records |
| `d304_record_green.py` | the whole D3-04 sequence: mutate, ratchet, `--record`, re-run the closure; writes `d304.json` |
| `g525_race.py` | the `#525` null control's race, against the production reap; writes `g525_race.json` |
| `rescore.py` | how many of the pre-screen's script-runs could report a failing check at all |

## The numbers, in one block

`python3 tools/audit/round3/D3/verify-1/summary.py` (every aggregate below is
printed by a harness, from this seat's own run records):

```
RESULT reruns_total=103 script-runs
RESULT reruns_by_script={"tests/backtest.py": 12, "tests/card.mjs": 13,
  "tests/card_drift.mjs": 13, "tests/edge.py": 12, "tests/entities.py": 22,
  "tests/features.py": 18, "tests/plan_view.py": 13}
RESULT killed_that_were_scored_survivors=7 mutants (M07,M19,M24,M27,M30,M32,M33)
RESULT killers={"M07": ["tests/entities.py"], "M19": ["tests/features.py"],
  "M24": ["tests/features.py"], "M27": ["tests/entities.py"],
  "M30": ["tests/features.py"], "M32": ["tests/features.py"],
  "M33": ["tests/features.py"]}
RESULT survivors_verifier1=15 of 34 mutants
  (M03,M04,M05,M06,M10,M11,M12,M14,M15,M16,M17,M18,M20,M29,M31)
RESULT survival_rate_verifier1=0.441 fraction
RESULT sensor_survivors=2 of 4 mutants (M12,M16)
RESULT isfinite_guards_unpinned=1 of 2 guards (M14)
RESULT edge_backtest_kills=0 of 24 runs
RESULT node_lane_kills=0 of 39 runs
RESULT survivors_by_module_verifier1={"optimizer.py": "4/4", "price_model.py": "2/2",
  "coordinator.py": "2/4", "sensor.py": "2/4", "thermal_model.py": "2/3",
  "topology.py": "1/2", "dhw_learning.py": "1/1", "wood_fuel.py": "1/1",
  "accuracy.py": "0/1", "battery.py": "0/1", "config_flow.py": "0/2",
  "dhw_schedule.py": "0/2", "external_heat.py": "0/1", "grid_fee.py": "0/1",
  "inputs.py": "0/1", "sysid.py": "0/1", "tariff.py": "0/3"}
RESULT loo_min=0.367 fraction (dropping optimizer.py)
RESULT loo_max=0.484 fraction (dropping tariff.py)
```
```
RESULT blind_runs=50 of 317 pre-screen script-runs   (rescore.py)
RESULT entities_value_pin_sites=63 sites
RESULT rederived_identical=34 of 34 mutants          (mutant_pool.py, seed 20260910)
RESULT structure_rc_before_record=1 code             (d304_record_green.py)
RESULT structure_rc_after_record=0 code
RESULT green_after_record=11 of 12 scripts
RESULT race_rate=0.50 fraction at a 0.02 s head start, 0.00 at 0.05 s and 1.0 s
RESULT handler_delay_max=0.0476 s against a 0.05 s budget   (g525_race.py)
```

## 0. The finding that dominates everything below: the pre-screen could not see
## a failing check in the suite's two largest scripts

I verified the finder's kill rule before relying on it, as instructed, and it
is right about *why* a `FAIL` line is not a kill — `harness.Results.check` and
`nightly_ha.Checks` share the format and negative arms quote mutated values.
Re-derived from the finder's own recorded rows, a naive "new FAIL line"
rule scores **31 of 34** mutants killed against the strict rule's 12, and
**29 of those 31** come from `tests/entities.py` alone. That part holds.

What does not hold is the *implementation* of the strict rule. `verdicts.py`
keys on three things — a moved exit code, a traceback, or a moved
`N of M … FAILED` count — and reads the last two out of `prescreen.py`'s
recorded `tail`, which is `out[-1200:]`:

```
RESULT script_runs=317 runs
RESULT blind_runs=50 runs (0.158 fraction)
  tests/entities.py: 32 of 34 runs carry no summary and cannot move rc
  tests/features.py: 18 of 19 runs carry no summary and cannot move rc
RESULT scripts_with_a_usable_detector=["tests/config_flow_steps.py",
  "tests/deployment_shape.py", "tests/env_drift.py --all", "tests/manual_plan.py",
  "tests/optimality.py", "tests/plan_view.py", "tests/solar_alignment.py",
  "tests/structure.py", "tests/typing_ruler.py", "tests/validate.py"]
```
(`python3 tools/audit/round3/D3/verify-1/rescore.py`, deterministic over the
committed `prescreened_verdicts.json`.)

Two things compound:

* **Only `optimality.py` and `env_drift.py --all` ever recorded a summary
  line.** `entities.py` prints hundreds of lines of integration log *after*
  `N of 1294 ENTITY CHECKS FAILED`, so a 1200-character tail never contains
  it. The count arm never fired for it, in 34 runs.
* **The worker slots were `git init`'d copies with no commit**, so
  `entities.py` and `features.py` were *already red* there (`baseline_rc 1`).
  With the count arm dark and the exit code pinned at 1 on both sides, the
  only arm left for those two scripts was "a traceback appears" — i.e. a
  crash. A mutant that merely made a check **fail** was scored `SURVIVOR`.

`entities.py` holds **1294** checks and `features.py` **2136**: the pre-screen
was blind to the outcome of 3430 of the suite's assertions on 50 of its 317
script-runs, and every one of the 22 survivors has one of those runs in it.

**In a real checkout both scripts are green on the baseline** — I measured it,
because it is the whole reason my numbers differ:

```
RESULT BASELINE.tests/entities.py.rc=0 code  summary='ALL 1294 ENTITY CHECKS PASSED'
RESULT BASELINE.tests/features.py.rc=0 code  summary='ALL 2136 FEATURE CHECKS PASSED'
```

So I re-ran them, mutant by mutant, in the real checkout.

## 1. What I executed

| pass | scripts | mutants | runs | command |
|---|---|---|---|---|
| the missing end-to-end scripts | `edge.py`, `backtest.py` | M09, M12, M14, M19 (the finder's top four) + every survivor whose closure contains them: M04, M05, M06, M11, M17, M20, M31, M32 | 24 + 2 baseline | `closure_gap.py --mutants … --scripts tests/edge.py,tests/backtest.py` |
| the blind script, re-scored | `entities.py` | all 22 survivors | 22 + 1 baseline | `closure_gap.py --mutants … --scripts tests/entities.py` |
| the other blind script | `features.py` | every survivor whose closure contains it (18) | 18 + 1 baseline | `closure_gap.py --mutants … --scripts tests/features.py` |
| the D3-04 sequence | `structure.py`, then all 11 CI-run scripts of `coordinator.py`'s closure | M09 | 14 | `d304_record_green.py` |
| the `#525` race | the production reap | — | 47 trials over 3 head starts | `g525_race.py` |
| the sample | `mutant_pool.py --seed 20260910 --n 34` | — | — | re-derivation |

`tests/stress.py` was not run, no gate lock was taken, no branch was created or
moved, nothing was pushed. The tree was `git reset --hard`ed to
`ae36eff` after every mutant and is at `ae36eff` now.

### The provisional gap, closed: `edge.py` and `backtest.py` kill nothing

```
RESULT BASELINE.tests/edge.py.rc=0 code (35.9s)
RESULT BASELINE.tests/backtest.py.rc=0 code (30.1s)
… M09 M12 M14 M19 M04 M05 M06 M11 M17 M20 M31 M32, edge.py and backtest.py …
RESULT <every one>.rc=0 code
RESULT edge_backtest_kills=0 of 24 runs
```

Eight of those twelve — every `optimizer.py`, `thermal_model.py`,
`wood_fuel.py` and `dhw_schedule.py` survivor — have **both scripts in their
measured closure**, so this is the gate's own selection, not an extra. The
other four (M09 `coordinator.py`, M12 `sensor.py`, M14 `price_model.py`,
M19 `accuracy.py`) have neither script in their closure: `edge.py`'s closure
names ten production modules and none of those four is among them, so I ran
them as a check on the *closure* rather than on the finding, and they came
back green as the closure predicts. **The finder's "any survivor may die on
`edge.py`" does not happen on this sample: 0 of 24.** That is the one attack
that would have shrunk D3-01 and D3-03, and it fails.

## 2. D3-02 — the strongest claim, and the one that breaks

The claim is *"entity values pinned by shape never by value: 4 of 4 sensor.py
mutants survive"*, and the report's mechanism sentence is *"Between them
nothing asserts what number a sensor publishes. Every published value in the
integration is in this gap."*

**`tests/entities.py` has 63 check sites that compare a published
`native_value`, `extra_state_attributes` entry or `current_temperature`
against an expected value** (`entities.py:914` `Measured Power == 2.4`,
`:919` `Observed COP == 3.1`, `:988` accuracy `== 0.3`, `:993` peak `== 7.2`,
`:1053` PV surplus `== 5.4`, `:1060` comfort weight `== 6.4`, `:2313`,
`:2463`, `:6810` the irradiance sensor value, …). The quantifier is false on
its face, and two of those sites kill two of the four mutants:

```
RESULT BASELINE.tests/entities.py.rc=0  'ALL 1294 ENTITY CHECKS PASSED'
RESULT M07.tests/entities.py.rc=1       '1 of 1294 ENTITY CHECKS FAILED'
RESULT M12.tests/entities.py.rc=0       'ALL 1294 ENTITY CHECKS PASSED'
RESULT M16.tests/entities.py.rc=0       'ALL 1294 ENTITY CHECKS PASSED'
RESULT M27.tests/entities.py.rc=1       '1 of 1294 ENTITY CHECKS FAILED'
RESULT sensor_survivors=2 of 4 mutants
```

The single failing check, in each case, is a value pin:

* **M27** (`sensor.py:2115`, `ComfortWeightSensor.native_value`'s rounding
  return deleted) — `FAIL the learned comfort weight is visible  [an
  invisible self-adjusting objective would be alarming]`. That is
  `entities.py:1059`, `by_name["Comfort Weight"].native_value == 6.4`.
  The finder's report names this mutant as an example of the gap.
* **M07** (`sensor.py:1283`, `PredictiveOptimizationInsightSensor`'s
  `if not info:`) — `FAIL the state summarises the same signals, and says so
  when there are none (#246)  [with a forecast 'solar_anticipation', without
  'normal']`. That is `entities.py:6564`, which pins **both** arms of that
  sensor's published string.

Both are `rc 0 -> 1`: merge-blocking on any pull request that touches
`sensor.py`, because `entities.py` is in `sensor.py`'s six-script closure.

**What survives, and it is the finding's headline example.** `M12`
(`sensor.py:1002`, `UpperFloorTempSensor.native_value` returns `None` for
every state the integration can be in) and `M16` (`sensor.py:885`,
`HeatPumpActionSensor.extra_state_attributes` returns `None` where Home
Assistant is owed a mapping) leave `entities.py` at `ALL 1294 … PASSED`. I
also ran `edge.py` and `backtest.py` against M12 (green, and out of closure),
and `sensor.py`'s closure holds nothing else CI runs: `golden.py` is skipped
under `GOLDEN_MODE=drift`, which is the mode CI sets, leaving
`deployment_shape.py`, `structure.py`, `typing_ruler.py` and
`env_drift.py --all`, all of which the finder ran with a detector that works
for them. **So "a sensor that returns `None` for every state merges green" is
true — for that sensor.** The quantified claim around it is not.

## 3. D3-03 — one of the two guards is pinned, by the script the pre-screen
## could not read

```
RESULT BASELINE.tests/features.py.rc=0  'ALL 2136 FEATURE CHECKS PASSED'
RESULT M14.tests/features.py.rc=0       'ALL 2136 FEATURE CHECKS PASSED'
RESULT M19.tests/features.py.rc=1       '1 of 2136 FEATURE CHECKS FAILED'
RESULT isfinite_guards_unpinned=1 of 2 guards
```

* **`accuracy.py:378`** — `if not np.isfinite(parsed): continue` in
  `AccuracyTracker.from_dict`, the guard whose own comment says *"a poisoned
  sigma would reach the comfort bounds as a NaN margin"* — **is pinned**.
  `tests/features.py` is in `accuracy.py`'s 13-script closure, runs on every
  pull request that touches it, and goes `rc 0 -> 1`. The finder's screen ran
  that script and scored it a survivor because `features.py` was already red
  on the slot and its check count was never read.
* **`price_model.py:137`** — `if not np.all(np.isfinite(values)): return False`
  in `PriceShapeModel.observe_day` — **survives** `entities.py` and
  `features.py` both, and `edge.py`/`backtest.py` besides (out of closure,
  green). That half of the finding stands, and it is the half that decides
  the relative cost of each hour.

So "both … deletable with all 10 selected scripts green" is false as a
conjunction, and the `accuracy.py` half — the one the report argues hardest,
quoting the guard author's own comment — is the half that is caught.

## 4. D3-04 — executed end to end, and it reproduces exactly

I ran the whole sequence the brief asks for: mutate, commit, run the ratchet,
run the documented remedy, commit it, run every script CI would run for a
`coordinator.py` change.

```
  baseline: tests/structure.py rc=0            (STRUCTURE RATCHET PASSED)
  before:   tests/structure.py rc=1 (1.5s)
            RESULT cut_fetch=131 count
              gain cut_fetch 131 (budget 132, -1; not yet recorded -- see below)
              cut_fetch      132   131   -1  BETTER (lower is better)
            1 STRUCTURE BUDGET(S) IMPROVED AND NOT YET RECORDED
            Nothing here is a violation. Run the command above, commit the
            table with this change, and say in the commit which rows moved.
  remedy:   python3 tests/structure.py --record  rc=0
            tests/structure_budgets.json | 4 ++--   (2 insertions, 2 deletions)
  after:    tests/structure.py        rc=0   STRUCTURE RATCHET PASSED
            tests/entities.py         rc=0 (26.0s)
            tests/config_flow_steps.py rc=0 (1.0s)
            tests/deployment_shape.py rc=0 (2.0s)
            tests/typing_ruler.py     rc=0 (0.1s)
            tests/solar_alignment.py  rc=0 (0.8s)
            tests/plan_view.py        rc=0 (1.1s)
            tests/manual_plan.py      rc=0 (6.7s)
            tests/features.py         rc=0 (112.8s)
            tests/card.mjs            rc=0 (10.1s)
            tests/card_drift.mjs      rc=0 (3.8s)
RESULT structure_rc_before_record=1 code
RESULT structure_rc_after_record=0 code
RESULT green_after_record=11 of 12 scripts
```

Three things this adds to the finder's version, all of them in the finding's
favour:

1. **`features.py` does not rescue it.** `features.py` is in
   `coordinator.py`'s closure and was one of the two scripts the pre-screen
   could not score; run properly, on a checkout where it is green, it passes
   with the Open-Meteo fallback dead.
2. **The Node lane does not rescue it either.** `card.mjs` and
   `card_drift.mjs` were never driven by the finder and are in that closure;
   both pass.
3. **The remedy is two lines.** `structure.py --record` rewrites
   `cut_fetch` 132 -> 131 and the `recorded_at` stamp, and the ratchet then
   says `STRUCTURE RATCHET PASSED` with the fallback still disabled.

The twelfth script is `env_drift.py --all`, which I did not re-run (it does a
`git worktree add` in a repository shared with live sessions, and the disk had
4 GB free). The finder measured it byte-identical for this mutant with
`env_drift.py`'s own `_diff_leaves`, and `env_drift --all` is one of only two
scripts whose detector demonstrably worked in that screen, so I take it and
say so rather than claiming a run I did not make.

## 5. The `#525` flake — reproduced as a mechanism, with the number

The finder saw `tests/features.py` go red once in seven runs of the
**unmutated** tree on `null control: reaping inline DOES stall it, so the
heartbeat can see a stall  [blocking 0 ticks in 0.00s]`, and could not
reproduce it. The assertion is `_g525_block_ticks <= 5 and _g525_block_s >= 1.5`
(`tests/features.py:24114`): a **wall-clock lower bound**.

It is not a slow-box flake, it is a race, and `0.00s` is its signature.
`_g525_measure` spawns a child that ignores `SIGTERM`
(`signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(30)`), plants it
as `coordinator._PROCESS_WORKER`, and reaps it after a single
`await asyncio.sleep(0.05)`. `_shutdown_process_pool` stalls for the full
`worker.wait(timeout=2)` **only if the child is still alive after
`terminate()`** — which requires the child's interpreter to have reached
`signal.signal` inside that 50 ms. If `SIGTERM` lands first, the child dies on
the default action, `wait` returns at once, and `_g525_block_s` is 0.00.

Measured against the production symbol, with the child spawned exactly as
`features.py` spawns it:

| head start | trials | `race_rate` (elapsed < 1.5 s) | handler delay p50 / p90 / max | `elapsed_min` | `load1` |
|---|---|---|---|---|---|
| **0.05 s** (what `features.py` uses) | 25 | **0.00** | 37.6 / 43.7 / **47.6 ms** | 2.0006 s | 7.9 |
| 1.00 s (null control) | 10 | 0.00 | 33.0 / 35.4 / 42.7 ms | 2.0009 s | 7.7 |
| 0.02 s (perturbation) | 12 | **0.50** | 33.0 / 42.1 / 45.2 ms | **0.0017 s** | 7.1 |

The check's whole margin is **50 ms minus the time a fresh CPython
interpreter needs to install a signal handler**, and on this box at `load1`
7.9 that time was 37.6 ms median and **47.6 ms at its worst in 40 spawns** —
**2.4 ms of margin**. The perturbation moves the metric in the stated
direction and the null control pins it at zero, so the mechanism is
established rather than argued; the finder's 1-in-7 at `load1` 15–17 is what
this distribution does when the box is three times busier than it was for me.
`elapsed_min=0.0017 s` under the perturbation is the finder's `0.00s`,
reproduced.

**And it fired live, in this session, on the other arm.** The M32 re-run
above printed a third failure that has nothing to do with `dhw_schedule.py`:

```
FAIL the reap Home Assistant's stop fires keeps the loop running (#525)
     [fixed 1 ticks in 0.00s vs blocking 0 ticks in 2.01s]
```

That is the *sibling* assertion, `_g525_free_ticks >= 50 and _g525_free_s >=
1.5`, on a run where the blocking arm behaved perfectly (2.01 s) and the
stop-listener arm's child lost the race instead (`0.00s`). Both arms spawn a
fresh interpreter and reap it after the same 50 ms, so both carry the same
2–16 ms of margin. The same mutant's first run reported `2 of 2136`; the
second reported `3 of 2136`, and the extra one was this. One run in seven is
the finder's rate; I saw it once in 24 `features.py` runs on this box at
`load1` 7–31, which is the same order.

This is a defect in `tests/features.py`, not in production: the null control
should assert on the *child's state* (that it outlived the `terminate`), or
wait for a readiness byte before reaping, rather than on a wall-clock floor.
It is outside D3-01..D3-05 and I am not filing it; it belongs in whatever
stage owns `features.py`'s blocking lane, by `finding-propagation.md`.

## 6. D3-05 — the never-killed set, with two more scripts in it

My own number, from my own runs rather than from the pre-screen's record:
`tests/edge.py` ran 12 times and `tests/backtest.py` 12 times against mutants
of modules in their own closures (8 of the 12 in closure, 4 out of it), and
**neither changed a verdict once**: 0 kills in 24 runs, 1,055 s of executed
script time. Adding them to the finder's twelve:

```
RESULT scripts_that_ran_and_never_killed=8 of 14 scripts
  tests/deployment_shape.py  34 runs  0 kills   2.3 s recorded
  tests/typing_ruler.py      34 runs  0 kills   0.1 s
  tests/plan_view.py         28 runs  0 kills   1.2 s
  tests/manual_plan.py       28 runs  0 kills   6.6 s
  tests/validate.py           8 runs  0 kills  36.7 s
  tests/optimality.py         8 runs  0 kills  82.4 s
  tests/edge.py              12 runs  0 kills  38.2 s   (mine)
  tests/backtest.py          12 runs  0 kills  35.5 s   (mine)
```

The finder's "6 of 12 including both end-to-end solver scripts" survives my
re-scoring intact, and my correction to the kill rule cannot touch it:
`validate.py`, `optimality.py`, `deployment_shape.py`, `typing_ruler.py`,
`plan_view.py` and `manual_plan.py` were all **green on the unmutated slot**
(`baseline_rc 0`), so for those six the exit code was a working detector and
their zero is real. The two scripts my re-run changed — `entities.py` and
`features.py` — were already in the *killer* set, so the never-killed list
only grows.

**What I did not re-execute:** `solve_budget.py`'s 22.8-vs-2.8
assertions-per-solve. Its recorded run took 852.8 s for `optimality.py`
alone under instrumentation, and on a box at `load1` 7–80 that is not a number
I can retake honestly in this window. The finder states its own detector gap
for it (`plan_view.py`'s lower-case `issues` list), which is the right shape
for that kind of claim. I neither confirm nor dispute the ratio; the half of
D3-05 I measured is the kill half.

## 7. The attacks that failed, said out loud

* **"The aggregate is a grid artefact."** Not for the finder's number:
  `analyse.py` re-runs deterministically on the committed rows and reproduces
  `22/34 = 0.647`, and its leave-one-out over all 17 modules stays in
  **0.600–0.710**. It is *more* of a concern for **my** number, and I say so:
  under my verdicts the per-module rate is `optimizer.py 4/4`,
  `price_model.py 2/2`, `coordinator.py 2/4`, `sensor.py 2/4`,
  `thermal_model.py 2/3`, and **0/n in eight of the seventeen modules**; the
  leave-one-out range widens to **0.367–0.484**, and dropping `optimizer.py`
  alone takes 0.441 to **0.367**. So the corrected rate is carried further by
  `optimizer.py` than the finder's was — which is the module the weighting
  calls most consequential, and the one whose four survivors include the DHW
  division guard and the pinned-bound clamp. It makes the finding narrower
  and sharper, not weaker.
* **"The sample is not reproducible."**
  `mutant_pool.py --seed 20260910 --n 34` re-derives
  **34 of 34 mutants identically** (same file, line and replacement, in the
  same order) on my checkout. The seed, the pool and both weight tables
  reproduce.
* **"The wrong gate mode was used."** No. The pre-screen ran the differential
  comparison with `env_drift.py`'s own `_diff_leaves`, `SENSITIVE` and
  `may_drift_judged_diffs` over `--all` captures, which is what CI runs;
  `golden.py` is correctly skipped, exactly as `tests/run.sh` skips it when
  `GOLDEN_MODE=drift`.
* **"The numbers were taken under contention."** They are counts and exit
  codes, not times. The only wall-clock numbers in this report are §5's, and
  contention is that section's subject.
* **"`edge.py` will kill the survivors."** 0 of 24 runs.
* **"The path is only reachable through the stub."** Not attempted as a
  refutation: `entities.py` drives the real `async_setup_entry`, and the two
  mutants it kills are killed through published entity state, which is the
  same surface Home Assistant reads.

## 8. D3-01 — the headline number, re-measured

Re-running the two blind scripts against the finder's 22 survivors, in a
checkout where both are green on the baseline, kills **seven** of them:

| mutant | file:line | killed by | evidence |
|---|---|---|---|
| M07 | `sensor.py:1283` | `entities.py` | `1 of 1294 ENTITY CHECKS FAILED` — `FAIL the state summarises the same signals, and says so when there are none (#246)` |
| M27 | `sensor.py:2115` | `entities.py` | `1 of 1294` — `FAIL the learned comfort weight is visible` |
| M19 | `accuracy.py:378` | `features.py` | `1 of 2136` — `FAIL a corrupt store loads what survives and never bricks the score loop` |
| M24 | `external_heat.py:457` | `features.py` | **crash**: `TypeError: unsupported operand type(s) for -: 'datetime.datetime' and 'NoneType'` at `external_heat.py:461`, 1.0 s in |
| M30 | `inputs.py:390` | `features.py` | `3 of 2136` — `FAIL a missing entity is reported as such`, `FAIL a configured entity that does not exist is missing_entity`, `FAIL and the freeze reason names both the condition and the key (missing_entity)  [got 'unavailable:indoor_temp_entity']` |
| M32 | `dhw_schedule.py:118` | `features.py` | `2 of 2136` — `FAIL and renders back to the string the user typed`, `FAIL and in the weekly grammar when the configuration names days` |
| M33 | `sysid.py:234` | `features.py` | `1 of 2136` — `FAIL a recent run blocks another` |

**Every one of these was re-run a second time and the failing check named**,
because a count that moved could in principle be `features.py`'s own #525
flake (§5) rather than the mutant. All seven reproduce, and every named check
is on the mutated behaviour: the corrupt-store load for the `isfinite` guard,
the missing-entity freeze reason for `inputs.py`'s `if state is None:`, the
weekday grammar for `dhw_schedule.py`'s `if ordered == [5, 6]:`, the
run-interval lockout for `sysid.py`'s `if self.last_run is not None:`.

```
RESULT survivors_verifier1=15 of 34 mutants
RESULT survival_rate_verifier1=0.441 fraction
RESULT killed_that_were_scored_survivors=7 mutants (M07,M19,M24,M27,M30,M32,M33)
```

**M24 is the instrument defect in one line.** It crashes `features.py` in
1.6 s with a production `TypeError`, and the finder's rule has an arm for
exactly that — "a traceback appears". The recorded tail for that run *starts*
`t recent call last):` — the 1200-character window sliced the string
`Traceback (most recen` off the front, the substring test missed by a few
characters, and a crash was filed as a survivor.

Every survivor of mine has been through, at minimum: `entities.py`,
`structure.py`, `typing_ruler.py`, `deployment_shape.py` and
`env_drift.py --all`; every one whose closure names them has also been through
`config_flow_steps.py`, `solar_alignment.py`, `plan_view.py`,
`manual_plan.py`, `features.py`, `validate.py`, `optimality.py`, and — new
here — `edge.py`, `backtest.py`, `card.mjs` and `card_drift.mjs`. The only
script in any of their closures that nothing has run is `tests/stress.py`,
which the box rules forbid; it is a solve-time guard and no mutant here
changes a solve's cost class, but I did not run it and do not claim it.

### The Node lane, which nobody had driven

The finder says so itself: "the Node lane was not driven … a card-side kill is
unmeasured here." `card.mjs` and `card_drift.mjs` are in the 13- and
18-script closures, so I drove them for all 13 non-`sensor.py` survivors,
each preceded by `plan_view.py` in the same mutant window so the card reads a
payload produced by the *mutated* tree:

```
RESULT node_lane_runs=39 runs (13 mutants x plan_view.py, card.mjs, card_drift.mjs)
RESULT node_lane_kills=0 mutants
```

One honest note on that baseline: `card_drift.mjs` exits 1 on the *unmutated*
tree because `GOLDEN_REF` then resolves to `HEAD` and it is asked to compare a
card against itself; with a mutant committed it exits 0 every time. The
direction is `1 -> 0`, which is not a kill under any rule, and `card.mjs`
(rc 0 on both sides) carries the lane's verdict.

## 9. Residual — what is still unmeasured about my own 15

`tests/stress.py` is in the closure of seven of them (`optimizer.py`,
`thermal_model.py`, `wood_fuel.py` mutants) and was not run: the box rules
forbid it and it needs the gate lock. It is a solve-time ratio guard against a
calibrated reference; none of these mutants changes a solve's cost class, so I
expect nothing there, but I did not measure it and the finding stays
`provisional` in exactly that respect. `env_drift.py --all` I did not re-run
either (see §4); the finder's run of it is the one part of that screen whose
detector provably worked.

## 10. Votes

| finding | vote | severity I would give | my executed number |
|---|---|---|---|
| D3-01 | **weaken** | medium (finder: high) | **15 of 34 survive (0.441)**, not 22 of 34 (0.647); 7 of the 22 are killed by scripts already in their own closure |
| D3-02 | **weaken** | medium (finder: high) | **2 of 4** `sensor.py` mutants survive, not 4 of 4; `entities.py` has **63** value-pinning check sites and two of them kill M07 and M27 |
| D3-03 | **weaken** | low (finder: medium) | **1 of 2** guards unpinned: `accuracy.py:378` is killed by `features.py` (`1 of 2136 FEATURE CHECKS FAILED`); `price_model.py:137` survives |
| D3-04 | **verify** | medium (finder: medium) | `structure.py` rc `0 -> 1 -> 0` across `--record`; **11 of 12** closure scripts green after it, `features.py` and the Node lane included |
| D3-05 | **verify** | low (finder: low) | **8 of 14** scripts ran and never changed a verdict; my own contribution is `edge.py` 12 runs / 0 kills and `backtest.py` 12 runs / 0 kills |

**D3-01 — why weaken and not refute.** The claim's direction is right and its
consequence is real: 15 of 34 consequence-weighted single-line mutations still
leave every script CI runs green, including `optimizer.py:4771`'s division
guard, `optimizer.py:3234`'s pinned-bound clamp and `price_model.py:137`. But
"22 of 34 … 64.7%" is not a number the tree supports, and the reason it is
wrong is not sampling noise — it is that the screen could not read a check
failure in the two scripts that hold 3430 of the suite's assertions. Any
judge re-running `verdicts.py` on the same rows will get 22 again; the rows
are what is wrong.

**D3-02 — why weaken and not refute.** "4 of 4" is 2 of 4 and "nothing
asserts what number a sensor publishes" is 63 sites that do. But the
finding's own headline instance survives every script CI runs for a
`sensor.py` change: `UpperFloorTempSensor.native_value` can be made to return
`None` for every state the integration can be in, and the gate stays green.
The gap is real and narrower than claimed: it is the *unpinned subset* of the
published surface, not the surface.

**D3-03 — why weaken.** The conjunction is false, and the half that fails is
the half the report argues from (the guard whose author wrote the consequence
into a comment). The surviving half is on the money path and worth keeping as
a finding; it is one guard, and D3-01 already covers "guards survive".

**D3-04 — why verify at full strength.** I executed the whole sequence and it
reproduces exactly, including the two things the finder had not ruled out:
`features.py` (in that closure, and blind in the pre-screen) passes with the
fallback dead, and the Node lane passes. The remedy really is a two-line
`--record` after which the ratchet prints `STRUCTURE RATCHET PASSED`.

**D3-05 — why verify.** Its six never-killed scripts were all green on the
unmutated slot, so the exit code was a working detector for every one of them
and my correction cannot reach it; my own 24 runs add two more scripts to the
list. I did not re-execute the assertions-per-solve ratio and say so rather
than borrowing it.

## 11. Exposure

Read: `tools/audit/briefs/verifier.md`, `tools/audit/README.md`,
`tests/README.md`, `CLAUDE.md`, the D3 finder's `FINDINGS.md`, `REPORT.md`,
`PRESCREENED.md` and harnesses, and production and test sources as the method
required. **Not** read: the other verifier's output, `docs/audit-*.md`,
`docs/backlog.md`, `RELEASE_NOTES.md`, the audit register, `gh`, GitHub.
No branch was created or moved, nothing was pushed, `tests/stress.py` was
never run and the gate lock was never taken. The worktree is at
`ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1` with a clean tracked tree.
