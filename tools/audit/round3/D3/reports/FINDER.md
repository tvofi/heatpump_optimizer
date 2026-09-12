# D3 — test-suite gaps, round 3

Baseline `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1`, in an isolated detached
worktree. Machine: 8-core Apple M1, 8 GB, macOS Darwin 25.6.0, python3 3.11.5,
numpy 2.4.6 / scipy 1.17.1 on OpenBLAS, BLAS threads pinned to 1 everywhere.
The box was shared with eleven other agent sessions throughout; `load1` moved
between 6.5 and 45.5 while these numbers were taken. **Every number in this
report is a count, not a time**, except where a wall-clock figure is explicitly
marked provisional.

Owner's brief: *"Test-suite gaps — what the suite cannot fail on. Unnecessary
test suite resource use."*

## Method

**Sampling.** `tools/audit/round3/D3/mutant_pool.py` parses all 55 production
modules under `custom_components/heatpump_optimizer/` into a pool of **3367**
single-line mutation candidates in six operator classes
(`GUARD_OFF` 1792, `RETURN_DEL` 776, `CLAMP_DROP` 400, `BOOLOP` 274,
`CONST` 121, `RAISE_DEL` 4), and draws **34** of them with
`random.Random(20260910).choices`, weighted by
`module_weight × kind_weight`, capped at **4 per module**. Seed **20260910**;
17 modules touched. Both weight tables are in the harness and are copied into
`mutants.json`, so the draw re-runs byte-identically. `module_weight` is 5 for
`optimizer.py`, `coordinator.py` and `thermal_model.py` (wrong money or wrong
comfort silently), 4 for the published-value and config surfaces, 3 for the
feature modules, 2 for plumbing, 1 for the rest; `kind_weight` is 3 for a
dropped clamp, a disabled guard or a deleted `raise`, 2 for the rest.

**Isolation.** Six worker slots, each a full copy of the checkout under
`$TMPDIR/d3audit/slot-N` with its own `git init` (so
`tests/deployment_shape.py`'s `git ls-files` works). The checkout itself was
never mutated, no branch was created, no commit was made, and no git worktree
was added — `git worktree list` at the end shows exactly the two audit
worktrees that were there at dispatch.

**The differential gate.** `tests/env_drift.py --all <ref>` is two `--all`
captures compared byte-for-byte with `_diff_leaves`, with the five `may-drift`
fixtures judged only on `MAY_DRIFT_JUDGED_KEYS`. The pre-screen runs exactly
that comparison, but supplies the baseline half from a capture of the
unmutated tree taken once: `env_drift.py --capture <root> <out> --all`, then
**env_drift's own `_diff_leaves`, `SENSITIVE` and `may_drift_judged_diffs`**
(imported, never re-implemented) over the two payload sets. That is
`--all`'s comparison with the baseline capture hoisted out of the loop; it
also sidesteps the refusal of a ref that resolves to `HEAD`, which is what a
worktree sitting *on* the baseline would otherwise hit. All 55 fixtures were
captured for every mutant that reached this stage. **A verifier who wants the
gate itself rather than its comparison runs the command in "What the quiet
window must run" below.**

**The verdict rule, and why the obvious one is wrong.** A script kills a
mutant when *its own verdict* moves: the exit code differs from the same
slot's unmutated run, a traceback appears where the baseline had none, or its
reporter's `N of M ... CHECKS FAILED` count changes. A changed `FAIL <name>
[detail]` **line** is not a kill. `tests/harness.py:Results.check` and
`tests/nightly_ha.py:Checks` print the same `  FAIL name  [detail]` shape, and
`entities.py` and `features.py` drive deliberate *negative arms* through the
second — so a mutant that moves a value quoted inside a negative arm's detail
string prints new `FAIL` lines while the script still passes.

That distinction is not academic: under the naive rule 33 of 34 mutants
"died", under the correct one 7 did. It was checked directly rather than
argued — `tests/entities.py` run against M01 (`tariff.py:429`) prints
`1 of 1294 ENTITY CHECKS FAILED`, exactly what it prints on the unmutated
slot, with an identical set of FAIL *names*.

**Two tiers.** Tier 1 ran every fast script of the mutant's measured closure
that finishes inside about a minute (`entities.py`, `config_flow_steps.py`,
`structure.py`, `typing_ruler.py`, `deployment_shape.py`, `solar_alignment.py`,
`plan_view.py`, `manual_plan.py`), then the differential gate. Tier 2 ran
`features.py`, `validate.py` and `optimality.py` for everything tier 1 left
alive. `stress.py`, `edge.py` and `backtest.py` were never run (D3 brief);
`golden.py` was never run because `tests/run.sh` skips it whenever
`GOLDEN_MODE=drift`, which is the mode CI sets. The gate lock was never taken
and `tests/run.sh` was never invoked.

**The closure of each mutated file** came from `tests/closure.py select
--files <path>` — the gate's own selector — recorded in
`closures_by_module.json`. Every selection reported `MODE: SCOPED`.

## The prescreened table

`tools/audit/round3/D3/PRESCREENED.md` — one row per mutant: the patch as
`old -> new` at a named file and line, the size of its measured closure, every
script that ran, and what killed it or that nothing did. The machine-readable
form with every script's exit code, seconds and failure lines is
`prescreened_verdicts.json`.

## The headline number

```
RESULT mutants=34 mutants
RESULT survivors=22 mutants (M03,M04,M05,M06,M07,M10,M11,M12,M14,M15,M16,
                             M17,M18,M19,M20,M24,M27,M29,M30,M31,M32,M33)
RESULT survival_rate=0.647 fraction
RESULT killed=12 mutants (M01,M02,M08,M09,M13,M21,M22,M23,M25,M26,M28,M34)
RESULT killed_only_by_differential_gate=5 mutants (M01,M23,M25,M26,M28)
RESULT kills_by_script={"tests/env_drift.py --all": 5,
                        "tests/config_flow_steps.py": 3,
                        "tests/entities.py": 2, "tests/features.py": 1,
                        "tests/solar_alignment.py": 1, "tests/structure.py": 1}
RESULT runs_by_script={"tests/deployment_shape.py": 34, "tests/entities.py": 34,
                        "tests/structure.py": 34, "tests/typing_ruler.py": 34,
                        "tests/env_drift.py --all": 32,
                        "tests/config_flow_steps.py": 30,
                        "tests/manual_plan.py": 28, "tests/plan_view.py": 28,
                        "tests/solar_alignment.py": 28,
                        "tests/features.py": 19, "tests/optimality.py": 8,
                        "tests/validate.py": 8}
RESULT survivors_by_module={"optimizer.py": "4/4", "sensor.py": "4/4",
   "price_model.py": "2/2", "coordinator.py": "2/4", "thermal_model.py": "2/3",
   "tariff.py": "0/3", "config_flow.py": "0/2", "dhw_schedule.py": "1/2",
   "topology.py": "1/2", "accuracy.py": "1/1", "dhw_learning.py": "1/1",
   "external_heat.py": "1/1", "inputs.py": "1/1", "sysid.py": "1/1",
   "wood_fuel.py": "1/1", "battery.py": "0/1", "grid_fee.py": "0/1"}
RESULT survivors_by_kind={"GUARD_OFF": "17/23", "CLAMP_DROP": "2/5",
                          "RETURN_DEL": "2/5", "CONST": "1/1"}
```

```
RESULT leave_one_out_cells=17 modules
RESULT per_module_survival_min=0.0 fraction   (tariff.py, config_flow.py,
                                               battery.py, grid_fee.py)
RESULT per_module_survival_max=1.0 fraction   (optimizer.py, sensor.py,
                                               price_model.py, and six
                                               single-mutant modules)
RESULT survival_rate_drop_most_favourable=0.600 fraction (dropping optimizer.py)
```

Leave-one-out over the 17 modules: the rate stays between **0.600** and
**0.710** whichever single module is dropped, so 22/34 is not one module's
doing.

Command: `python3 tools/audit/round3/D3/analyse.py`.

## Findings

All five are marked `provisional`: `stress.py`, `edge.py` and `backtest.py`
were not run, and no survivor has been through a real `GATE_SCOPE=full` run.
See "What the quiet window must run".

### D3-01 — two thirds of a consequence-weighted mutation sample survives the whole fast gate, including the differential golden gate

**22 of 34** single-line mutations of production guards, clamps and returns
leave every fast script of their own measured closure green *and* leave all
55 golden fixtures byte-identical. The survival rate is not uniform: it is
**4/4 in `optimizer.py`**, **4/4 in `sensor.py`** and **2/2 in
`price_model.py`** — the three most consequential module classes in the
weighting — against **0/3 in `tariff.py`** and **0/2 in `config_flow.py`**.
Twelve of the survivors are `GUARD_OFF` on a guard whose body simply never
runs; five are dropped clamps or deleted returns.

The concrete shape, one line each, all `SURVIVOR`:

* `optimizer.py:4771` (`HeatPumpOptimizer._repair_dhw_floor`) —
  `max(c_dhw, 0.05)` becomes `c_dhw`, removing the division guard on the DHW
  tank's decay factor. Twelve scripts ran,
  `validate.py` and `optimality.py` among them.
* `optimizer.py:3234` (`HeatPumpOptimizer._seed_pinned_guess`) — the lower clamp
  `min(max(out[i], low), high)` becomes `min(out[i], high)`, so a starting
  guess may sit below a pinned bound. `optimality.py`, whose whole subject is
  a plan built with a fixed variable in it, ran and passed.
* `optimizer.py:3838` (`HeatPumpOptimizer._dhw_legionella_ceilings`) — the run-up loop's `if need <= floor_temps[m]: break`
  never fires.
* `thermal_model.py:2435` (`ThermalModel.simulate_trajectory_batch`) —
  `if solar_radiation is None: solar_radiation =
  np.zeros(n_steps)` never fires.
* `coordinator.py:2293` (`HeatPumpOptimizerCoordinator._async_drive_pumps`)
  — the pump-command early return
  `if not vvc_entity and not space_entity: return` never fires, so the
  "only entities the user explicitly configured are ever touched" contract
  is unpinned in that direction.

### D3-02 — a published entity value is pinned by shape, never by value

All four `sensor.py` mutants survive, and `sensor.py` selects the smallest
closure of any module sampled: **6 scripts, 37.3 s of recorded time**, with
`features.py`, `plan_view.py`, `validate.py` and `optimality.py` all
correctly scoped out because none of them opens `sensor.py`. The five that do
run cannot see a wrong value:

* `sensor.py:1002` — `if self.coordinator.data:` becomes `if False:`, so
  `sensor.py:UpperFloorTempSensor.native_value` returns `None`
  for **every** state the integration can be in. The sensor goes permanently
  blank in Home Assistant. `entities.py` runs (34/34 mutants), constructs the
  entity through the real `async_setup_entry`, and passes.
* `sensor.py:885` — a `return {}` becomes `return None`, so
  `HeatPumpActionSensor.extra_state_attributes` returns `None` where Home
  Assistant is owed a mapping.
* `sensor.py:2115` — a rounding return is deleted, so
  `ComfortWeightSensor.native_value` returns `None` instead of the number.

The mechanism, and why this is one finding rather than four: the golden
fixtures record `coordinator.data`
(`tests/golden.py:_capture_coordinator`), not entity attributes — the claim
file says so in as many words — and `entities.py`'s checks are structural
(the roster, `json_bytes` acceptance, finiteness, device-class/state-class
pairs, constructor defaults). Between them nothing asserts *what number a
sensor publishes*. Every published value in the integration is in this gap.

### D3-03 — the non-finite guards on the money and comfort paths are unpinned

Two `if not …isfinite(…)` guards can be deleted with no script failing, over
a 10-script closure each:

* `price_model.py:137` (`PriceShapeModel.observe_day`) — `if not np.all(np.isfinite(values)): return False`
  in the daily-shape admission check. With it gone a day carrying `nan` or
  `inf` spot prices is admitted into the learned price shape, which is the
  relative cost of each hour and therefore the thing the plan is bought
  against.
* `accuracy.py:378` (`AccuracyTracker.from_dict`) — `if not
  np.isfinite(parsed): continue`, immediately
  under the comment *"max(0, NaN) is NaN — a poisoned sigma would reach the
  comfort bounds as a NaN margin."* The guard's own author wrote down the
  consequence; nothing in the suite reproduces it.

`HeatPumpOptimizerSensorBase.__init_subclass__` scrubs non-finite values at
the *publish* boundary, which is why `entities.py`'s finiteness checks stay
green — the scrub is downstream of both of these.

### D3-04 — one mutant is caught only by the structural ratchet, reporting an improvement

`coordinator.py:5433` (`HeatPumpOptimizerCoordinator._update_current_state`)
— `if not solar_from_sensor and self._open_meteo is not
None:` becomes `if False:`, so Open-Meteo irradiance never fills in for a
house with no pyranometer. The whole solar-gain input silently becomes zero
for those installs.

Twelve scripts run. `tests/solar_alignment.py` — the script whose one job is
that irradiance lands on the right optimizer steps — runs and passes. The
differential gate captures all 55 fixtures and finds them byte-identical.
`tests/entities.py` passes. The **only** script that goes red is
`tests/structure.py`, and what it says is:

```
  cut_fetch    132   131   -1  BETTER (lower is better)
  ...
1 STRUCTURE BUDGET(S) IMPROVED AND NOT YET RECORDED
Nothing here is a violation.
```

Its documented remedy is `python3 tests/structure.py --record`, after which
the gate is green and the defect is unchanged. A ratchet counting one fewer
line is the entire distance between this change and a merge.

### D3-05 — the two end-to-end solver scripts killed nothing this sample could give them

`tests/validate.py` and `tests/optimality.py` each ran for 8 mutants (every
`optimizer.py`, `thermal_model.py`, `wood_fuel.py` and `dhw_schedule.py`
mutant whose closure names them) and killed **0**. `tests/deployment_shape.py`
(34 runs), `tests/typing_ruler.py` (34), `tests/plan_view.py` (28) and
`tests/manual_plan.py` (28) also killed 0 — but those are 0.1–6.6 s each,
where `validate.py` and `optimality.py` are 36.7 s and 82.4 s of recorded
closure time, and `optimality.py` is the script that buys only 2.8 assertions
per solve (item 5 below). Six of the twelve scripts that ran never moved.

This is reported at `low` because a script that kills nothing on 34 mutants is
not thereby useless — `validate.py` runs 501 assertions over 22 solves and
`optimality.py` is a quality floor, both of which guard classes of failure a
line deletion does not produce. It is the number that says where to point the
next, larger mutation sample.

## Item 5 — unnecessary suite resource use

All of these are counts or comparisons between recorded seconds already in the
tree; none is a new wall-clock measurement on this box.

### Assertions per solve

`tools/audit/round3/D3/solve_budget.py` wraps
`heatpump_optimizer.optimizer.HeatPumpOptimizer.optimize`,
`scipy.optimize.minimize` and `scipy.optimize.linprog`, and counts executions
of each script's own assertion lines (a `check(...)` call, or the `if` that
guards an `issue(...)` / `FAIL.append(...)`).

| script | `optimize` | `minimize` | `linprog` | assertions run | sites | assertions/solve |
|---|---|---|---|---|---|---|
| `tests/validate.py` | 22 | 88 | 58 | 501 | 44 | **22.8** |
| `tests/optimality.py` | 10 | 40 | 16 | 28 | 9 | **2.8** |
| `tests/plan_view.py` | 1 | 4 | 4 | 0 (detector gap, see below) | 0 | — |
| `tests/solar_alignment.py` | 0 | 0 | 0 | 22 | 12 | n/a (solves nothing) |

`optimality.py` buys 2.8 assertions per full optimizer solve where
`validate.py` buys 22.8 — an 8.1× difference in what a solve is asked to pin.
Its recorded closure time is 82.4 s against `validate.py`'s 36.7 s, so it is
the more expensive of the two *and* the less assertive. That is partly by
design (its nine checks are a solution-quality floor, and a challenger sweep
is inherently one number per sweep), and it is stated here as a shape rather
than as a defect: it is the script to look at first if the suite ever needs
seconds back. **Detector gap, said out loud:** `plan_view.py` accumulates into
a lower-case `issues` list, which `solve_budget.py`'s `REPORT_CALLS` name
filter does not recognise, so its `0` is my harness's blind spot and not a
claim about that script.

### What a change actually costs, per module

Summing `tests/closures.json`'s own recorded seconds over the scripts
`closure.py select` picks:

| changed module | scripts selected | recorded s | pulls `stress.py`? |
|---|---|---|---|
| `tariff.py`, `optimizer.py`, `thermal_model.py`, `wood_fuel.py`, `dhw_schedule.py` | 18 | 931.6 | yes |
| `coordinator.py`, `price_model.py`, `dhw_learning.py`, `topology.py`, `accuracy.py`, `grid_fee.py`, `external_heat.py`, `battery.py`, `inputs.py`, `sysid.py` | 13 | 152.2 | no |
| `config_flow.py` | 8 | 132.3 | no |
| `sensor.py` | 6 | 37.3 | no |

`stress.py` alone is 586.6 s of the 932.8 s recorded across all 22 recordings
— **63%** — and five of the seventeen modules sampled here pull it in. The
inversion worth naming: `coordinator.py` is the largest production module
(10 899 lines) and its change selects 152 s of gate, while `tariff.py`
(579 lines) selects 931 s. Nothing here says the closures are wrong — they are
measured — only that the cost of a change is decided by which scripts import
the solver, not by how much of the system the change can reach.

### Duplicated coverage

Across the 34 mutants, the scripts that killed anything and the mutants each
killed overlap in exactly **one** pair: `config_flow_steps.py` and
`entities.py` both kill M08. Every other kill is a sole kill. On this sample
there is no redundant killer to remove.

### Closure over-approximation, measured by consequence

Rather than re-deriving closures (a full `derive_closures.sh` off Linux is
forbidden, and a Darwin recording is a subset of `strace`, so "Darwin did not
open it" proves nothing), over-approximation is measured by what a selected
script could actually do: **which scripts ran for a mutant of a module in
their closure and never once changed verdict.** See the numbers block for the
list; `typing_ruler.py`, `plan_view.py`, `manual_plan.py` and
`deployment_shape.py` are all in that class here. They are cheap (0.1–6.6 s
recorded between them), so this is a coverage observation, not a cost one:
they are in the closure because they read the file, and reading a file is not
the same as being able to fail on it.

## Non-findings — what held

* **No vacuous quantifier assertion.** `tools/audit/round3/D3/vacuous.py`
  wraps `builtins.all` / `builtins.any` and attributes every call to the
  `tests/` frame that made it. Over `entities.py`, `features.py`,
  `manual_plan.py`, `config_flow_steps.py`: **93 quantifier sites inside
  `features.py`'s checks, 5 of them over an empty container; 62 inside
  `entities.py`'s, 1 over an empty container; 4 in `manual_plan.py`, none.**
  Every one of the six was read: all are negative assertions ("no Repairs
  card was raised", "no may-drift name leaked into the claim list") whose
  container is empty *because production behaved*, each with a paired
  positive arm — `features.py:21926` even carries the comment "Mutation
  value: a pair the owner actually edited still gets the card, so the check
  above is not passing because the notice was simply deleted". A perturbation
  that raises the issue makes the container non-empty and the check fails.
  None is an assertion that cannot fail. This is the class of defect the
  project has been bitten by before, and on this sample it is dry.
* **The differential gate earns its place, and pre-screening without `--all`
  would have produced five false gaps.** Five mutants (M01 `tariff.py:429`,
  M23 `thermal_model.py:1388`, M25 `tariff.py:548`, M26 `tariff.py:304`,
  M28 `battery.py:61`) pass every assertion script in their closure and are
  killed **only** by the byte comparison of two `--all` captures. Four of
  them are not among the five `SENSITIVE` fixtures' business at all, so the
  default five-fixture mode would have missed them too.
* **Deleting a line that production genuinely depends on is caught fast.**
  `tests/config_flow_steps.py` (0.9 s recorded) kills three mutants on its
  own; `tests/solar_alignment.py` (1.2 s) kills one; `tests/entities.py`
  kills two by crashing. The cheap end of the suite is doing real work.
* **The pre-screen can distinguish a kill from a non-kill.** Seven mutants
  died and the rest did not, under a rule that was itself checked against a
  hand-run control (`entities.py` on M01 prints the baseline's own
  `1 of 1294 ENTITY CHECKS FAILED`). A screen that killed everything or
  nothing would be worthless; this one does neither.

## One observation I could not make reproducible

`tests/features.py` failed once on the **unmutated** checkout with
`1 of 2136 FEATURE CHECKS FAILED` and the failing check
`null control: reaping inline DOES stall it, so the heartbeat can see a
stall  [blocking 0 ticks in 0.00s]` (#525). That assertion is a wall-clock
lower bound — `_g525_block_s >= 1.5` — inside the blocking gate. It did not
reproduce: six independent unmutated slot runs of `features.py` at `load1`
15–17 all passed it, each failing instead on a git-only artefact of my copy
(`recorded_at = 'unknown'`, #363, because the slot has no commit). So: one
red in seven runs of the same tree on the same box, cause not established.
Recorded here rather than as a finding, with the raw log at
`$TMPDIR/d3audit/features.log`, because a wall-clock lower bound in a
blocking lane is the shape that produces exactly this and the next auditor
should not have to re-discover the instance.

## Disproved leads

* **`tests/entities.py` "fails" on a mutated tree far more often than it
  actually fails.** The first pass credited it with 20+ kills. Every one of
  those was a changed `FAIL <name> [detail]` string printed by a *deliberate
  negative arm* driven through `tests/nightly_ha.py:Checks`, which shares
  `harness.Results.check`'s output format. Named here because the next
  auditor will hit it within ten minutes of grepping for `FAIL`.
* **`entities.py:12323` `not any("may-drift" in name for name in _md_claims)`
  quantifies over an empty list on every clean tree** (the claim protocol
  keeps the list empty between claims). It is still not a cannot-fail
  assertion: making `_parse_claims` stop splitting on `#` — its one line,
  `body, _, comment = line.partition("#")` — puts the `# may-drift:` comment
  lines into `_md_claims` and the check goes red. Reported as a non-finding
  because the perturbation moves it.

## What the quiet window must run

Every survivor-based finding here is `provisional`. Three things this
pre-screen did **not** run, all of them by the D3 brief's own instruction or
by the shared-box rule: `tests/stress.py`, `tests/edge.py` and
`tests/backtest.py`. `edge.py` in particular ("degenerate inputs and boundary
conditions": flat/zero/negative prices, −25 °C, a collapsed comfort range) is
the script most likely to reach the guards these mutants disable, and it is
the single largest reason a survivor here may not survive there.

The confirmation, per survivor, from a detached worktree at the baseline with
the mutant applied and **committed** (`env_drift.py` refuses a comparison ref
that resolves to `HEAD`, which is why the mutant has to be a commit and the
baseline a distinct ref):

```bash
# in a detached worktree of ae36eff, with the one-line patch applied
git commit -aqm "D3 mutant <id>"
python3 tests/gate_lock.py take --label d3-confirm
HPO_GATE_LOCK_LABEL=d3-confirm GATE_SCOPE=full GOLDEN_MODE=drift \
  GOLDEN_REF=ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1 GATE_JOBS=1 \
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  ./tests/run.sh
python3 tests/gate_lock.py release --label d3-confirm
```

A survivor is confirmed when that run exits 0. Read the mode line, not the
count: `GATE_SCOPE=full` prints no `MODE:` line at all.

To re-run this pre-screen end to end instead:

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub \
python3 tools/audit/round3/D3/mutant_pool.py --seed 20260910 --n 34
python3 tools/audit/round3/D3/prescreen.py --tier 1 --workers 5
python3 tools/audit/round3/D3/prescreen.py --tier 2 --workers 6 \
    --slot-prefix t2 --prev tools/audit/round3/D3/prescreened.json
python3 tools/audit/round3/D3/merge_runs.py \
    tools/audit/round3/D3/prescreened.json \
    tools/audit/round3/D3/prescreened_tier2.json
python3 tools/audit/round3/D3/verdicts.py \
    tools/audit/round3/D3/prescreened_merged.json
python3 tools/audit/round3/D3/analyse.py
```

**Give concurrent `prescreen.py` runs different `--slot-prefix` values.** Two
runs sharing the default prefix cost me one 22-mutant tier-2 pass: the shorter
run's cleanup deleted the longer run's worker slots mid-flight and the longer
run died with `FileNotFoundError` before writing its JSON.

## Harnesses

All under `tools/audit/round3/D3/`, each runnable by the single command in its
own header, each printing `RESULT <name>=<value> <unit>` lines.

| harness | what it produces |
|---|---|
| `mutant_pool.py` | the seeded, weighted sample; writes `mutants.json` |
| `prescreen.py` | the two-tier screen; writes `prescreened*.json` |
| `merge_runs.py` | folds the passes into one record per mutant |
| `verdicts.py` | the strict kill rule; writes `PRESCREENED.md` |
| `analyse.py` | every count this report cites |
| `solve_budget.py` | assertions per solve, per script |
| `vacuous.py` | quantifier assertions that ran over an empty set |

Supporting data: `closures_by_module.json` (`closure.py select --files` for
each mutated module), `solve_budget.json`, `vacuous.json`,
`prescreened_verdicts.json`, `PRESCREENED.md`.

## What I could not finish

* `tests/stress.py`, `tests/edge.py` and `tests/backtest.py` were never run.
  Any survivor may die on `edge.py`.
* No survivor was confirmed by a real `GATE_SCOPE=full` run; the command is
  above.
* Wall-clock per-script figures were not re-taken; `closures.json`'s recorded
  seconds are used only against each other.
* The Node lane (`card.mjs`, `card_drift.mjs`, `setup_qa_render.mjs`) was not
  driven. None of the 34 mutants touches the card's JavaScript, but two of
  them (`sensor.py`, `coordinator.py`) sit in the card's closure through the
  payload, so a card-side kill is unmeasured here.

## Exposure

Read: `tools/audit/briefs/COMMON.md`, `D3.md`, `tools/audit/README.md`,
`tests/README.md`, `CLAUDE.md`, and production and test sources as the method
required. **Not** read: `docs/audit-*.md`, `docs/backlog.md`,
`RELEASE_NOTES.md` (present on disk in this worktree and deliberately left
closed), `git log`, `gh`, GitHub. Two `D<k>-nn`-shaped identifiers appear in
`tests/env_drift.py` comments (`M01`, `#254`) and were read as context only;
the `M01`…`M34` ids in this report are my own mutant numbering and have no
relation to them.

