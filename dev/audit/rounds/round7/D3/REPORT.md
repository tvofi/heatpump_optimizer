# D3 — test-suite gaps, round 7

Baseline: `f9d6f78243fa65f6fa128d2357752a2ae7f60648` (round-6 fix wave merged).
Tree: `~/audit-r7-D3`, an isolated git worktree of that SHA
with earlier audit rounds stripped from the working tree.

## Method

`D3.md`'s method, run against this baseline:

1. **Candidate list.** The six single-line operators of
   `tests/mutation_table.py:candidates` — `CLAMP_DROP`, `GUARD_OFF`,
   `RETURN_DEL`, `RAISE_DEL`, `BOOLOP`, `CONST` — over the production package,
   weighted by consequence (money/comfort/hardware module 5, user-facing
   payload/service module 3, hygiene 1) times the operator's own severity.
   `screen.py --sample --seed 20260923` draws a frozen sample of **40 mutants
   over 21 modules, at most 4 per module**; the sample is committed at
   `sample.json` with the operator, the old line and the new.
2. **Pre-screen** each mutant with its **measured closure** from
   `tests/closures.json` (`tests/closure.py`'s own selection), minus the three
   scripts `D3.md` says to skip (`tests/stress.py`, `tests/edge.py`,
   `tests/backtest.py`), plus `tests/env_drift.py --all <baseline>`.
   Tiers run under the fan-out, for the box's sake:
   * `t1` — the closure's scripts whose recorded seconds are <= 20 s; the whole
     sample, 22 of 40 sites covered before the run was stopped;
   * `confirm` — `t1` plus `tests/features.py` and
     `tests/env_drift.py --all f9d6f782`, taken for 7 sites: the 2 highest-
     consequence `t1` survivors and 5 more.
   `tests/golden.py` is not driven: its default mode *is* `env_drift.py --all`,
   so driving it would run the same 233 s capture twice (the exclusion
   `tests/mutation_table.py:DRIVER_EXCLUSIONS` states).
3. **Kill rule.** `tests/mutation_table.py`'s, read off the whole output: a
   mutant is killed when a driver's exit status changes, or when its
   `N of M ... FAILED` count rises above that same tree's baseline. Exit
   status alone is not enough (#805).
4. **Not-equivalent proof.** A `killed=0` is only a suite gap if the mutant is
   distinguish*able*. `probe.py` calls the production symbol on named inputs
   and prints the value it **delivers** — the returned value or the exception;
   the count is keyed on that, never on an input attribute, so a fix that
   re-labels inputs cannot move it.

Every returned number is a count, a boolean or an exit status, so **all are
contention-immune**. The box was shared (`load1` 2.3–8.8); no wall or CPU
number is claimed as final and none is used in a finding.

## Exposure

* The working tree has **571 files deleted** relative to the baseline — the
  export's deliberate stripping of earlier rounds (`COMMON.md`). Three are read
  by the suite: `tests/entities.py:14596` opens `docs/audit-2026-09.md`.
  Consequence, stated rather than worked around: **`tests/entities.py` is red at
  baseline in this export** (rc=1, 38 failing checks) and red in both arms
  alike, so kill detection for it is keyed on `fails > 38` and no false
  survivor can come from it.
* No `git log`, no `gh`, no GitHub, and `docs/` was not read.
* Every harness mutates production in place for one mutant and restores it in a
  `finally`; `git diff --stat -- custom_components tests` was verified empty
  after every run.

## Findings

### D3-01 — four production guards and clamps are deletable with no driver failing

The suite's whole measured closure for these files — including
`tests/features.py` and the differential `tests/env_drift.py --all f9d6f782` —
reports nothing when the line is removed. `screen.py --tier confirm`, 7 sites
evaluated, **4 survivors**:

```
RESULT mutant=custom_components/heatpump_optimizer/legionella.py:528:GUARD_OFF   drivers=13 killed=0
RESULT mutant=custom_components/heatpump_optimizer/optimizer.py:3131:GUARD_OFF   drivers=16 killed=0
RESULT mutant=custom_components/heatpump_optimizer/sensor.py:2547:GUARD_OFF      drivers=10 killed=0
RESULT mutant=custom_components/heatpump_optimizer/thermal_model.py:1309:CLAMP_DROP drivers=16 killed=0
```

Each is a real behaviour change, not an equivalent mutant:

* `legionella.py:528` `if signature == self.ceiling_notice:` in
  `LegionellaGuard.check_ceiling` — the de-duplication that stops the
  `dhw_legionella_above_setpoint` Repairs issue being re-created every cycle.
  Without it `create_issue(...)` runs on every coordinator tick, so a notice the
  user dismissed comes straight back.
* `optimizer.py:3131` `if m.size < n_steps:` in
  `HeatPumpOptimizer._build_comfort_bounds` — the pad that makes a short
  `min_temp_margins` array the length of the horizon. Without it
  `temp_min_bounds + m[:n_steps]` is a shape mismatch, so the comfort-bound
  construction raises instead of padding.
* `sensor.py:2547` `if not isinstance(items, list):` in
  `PlanNarrativeSensor.native_value` — the payload-type guard. Without it a
  truthy non-list `insight.narrative.items` is iterated directly, no element is
  a dict, and the entity publishes `"idle"` where the guarded tree publishes
  `None` (unknown) — a wrong published value on a malformed payload.
* `thermal_model.py:1309` `t_in = min(t_in, dhw_setpoint)` in
  `ThermalModel.dhw_coil_draw_reduction` — the clamp that limits the coil-side
  draw temperature to the tank's setpoint.

**Instrumented symbols**: `heatpump_optimizer.legionella:
LegionellaGuard.check_ceiling`, `heatpump_optimizer.optimizer:
HeatPumpOptimizer._build_comfort_bounds`, `heatpump_optimizer.sensor:
PlanNarrativeSensor.native_value`, `heatpump_optimizer.thermal_model:
ThermalModel.dhw_coil_draw_reduction`.

**Perturbation**: each site's single-line mutant (`GUARD_OFF` = the `if` test
replaced by `False`; `CLAMP_DROP` = the `min` removed). The number must move
*killed >= 1*; it does not, in either tier.

The five that did *not* survive the `confirm` tier, for the record:
`tariff.py:139` killed twice (`env_drift.py` rc=1 fails=0, `features.py` rc=1
fails=3); `coordinator.py:7743` killed by `features.py` (fails=5);
`optimizer.py:6377` killed by `env_drift.py` (rc=1, fails=0 — a golden fixture
moved with no assertion failing, which is exactly what that instrument is for);
`coordinator.py:8708` killed by `tests/structure.py` alone.

### D3-02 — a mutation-table "kill" can be a driver that reports no violation

`tests/mutation_table.py`'s kill rule is "a driver's exit status changed, or its
`N of M ... FAILED` count rose". `tests/structure.py` exits 2 for a metric that
IMPROVED, and its own text is:

```
1 STRUCTURE BUDGET(S) IMPROVED AND NOT YET RECORDED
  metric                                 budget     measured      delta
  cut_learning                              285          284         -1  BETTER (lower is better)
Nothing here is a violation.
```

A single-line mutant can lower a structure metric *because it made code
unreachable* — the call-edge screen stops counting the calls inside the disabled
block — so `tests/structure.py` exits 2 while reporting **zero** failing checks,
and the mutation engine reads that exit status as a kill. A site whose behaviour
no assertion covers is then recorded as killed by a message that says no rule
was broken, and the recorded `survivor_fraction` — the one-sided cap in
`tests/mutation_budgets.json`, whose `last_measured.full` is 0.30 against a 0.30
cap — is optimistic by however many sites that channel covers.

**Executed numbers** (`structure_kill.py --sites 40`, control arm first):

```
RESULT control_structure_rc=0
RESULT control_structure_failures=0 count
RESULT structure_fires=3 of 40 mutants
RESULT fired_with_zero_assertion_failures=1 count
```

`coordinator.py:8708:GUARD_OFF` is the zero-failure fire: rc=2, `cut_learning`
285 -> 284, no assertion anywhere failing. The other two fires are
`rc=1 BUDGET(S) BREACHED` with one failing check each
(`name_match.py:351:RETURN_DEL`, `dhw_learning.py:435:GUARD_OFF`). In the
22-mutant `t1` pre-screen this channel produced **2 of the 5 kills**.

## Non-findings

* **A `t1`-only pre-screen produces false survivors, and the brief's `+env_drift
  --all` step is load-bearing.** The two highest-consequence `t1` survivors —
  `coordinator.py:7743:BOOLOP` (`_guard_floor_hold`, 10 `t1` drivers, 0 kills) and
  `optimizer.py:6377:CLAMP_DROP` (`_deferred_energy_cost`'s `_capped`, 12 `t1`
  drivers, 0 kills) — are both killed once `tests/features.py` and
  `tests/env_drift.py --all f9d6f782` join: `features.py` for the first (rc=1,
  5 failing checks) and `env_drift.py` for the second (rc=1, 0 failing checks).
  `RESULT tier=confirm evaluated=2 survivors=0`.
* **`probe.py` is not a probe that fires on everything.** Control arm,
  `guard_floor_hold`: `0 / 1 / 0 / 1`. Mutant arm: `1 / 1 / raised:TypeError / 1`
  — 2 of 4 inputs differ, and the two that should not (a room 2 K below the
  floor; a DHW tank below its minimum) do not.
* **`tests/mutation_budgets.json`'s `unpinned_sites: 3781` is not stale.**
  `inventory()` generates 3816 sites; `unpinned_sites(budgets, sites)` is 3781;
  `ratchet_refusal` returns `None` (proceed); `completeness_problems` and
  `cap_problems` are both empty.
* **`tests/structure.py`'s ratchet passes on the unmutated tree**: 25 metric
  keys, `RESULT control_structure_rc=0`, 0 failing checks.
* **17 of the 22 `t1`-screened mutants were killed by no `t1` driver** — but the
  `t1` tier is not the verdict; 5 of 7 carried into `confirm` survived and 2 did
  not, so the tier's survivor count is an upper bound, never the finding.
  `results-t1.json` holds all 22 with site, operator and driver count.
* **`last_measured.full` sits exactly at its cap** (12 survivors of 40 = 0.30
  against `max_survivor_fraction.full = 0.30`). Not a violation — the rule is
  `rate > cap` — but there is zero headroom, so D3-02's channel is worth
  removing before the next survivor is recorded.

## What could not be finished

* The full `GATE_SCOPE=full GOLDEN_MODE=drift` gate for the four survivors — the
  quiet window's job, and not runnable in this worktree anyway
  (`tests/env_drift.py` refuses a `GOLDEN_REF` that resolves to `HEAD`; the
  baseline SHA was used instead, which is what the drift comparison wants).
* The `t1` pre-screen covered **22 of the 40** sampled mutants: at ~80 s wall
  each and a load1 of 6–9 for most of the round, the run was stopped at 22. The
  remaining 18 are in `sample.json`, untouched.
* No resource-use finding is returned. `D3.md` item 5 asks for one and its
  numbers are **wall** numbers, which this round cannot honestly take on a box
  carrying a load1 of 2.3–8.8. It is left for the quiet window, with
  `baseline-t1.json` and `baseline-confirm.json`, which hold the measured wall
  beside every driver, against `tests/closures.json`'s recorded `seconds`.

## Harnesses

All under `tools/audit/round7/D3/`, run from the export root with
`PYTHONPATH=tests/hastub` and
`/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`.

| file | what it does | command |
|---|---|---|
| `screen.py` | the seeded sample and the pre-screen; one RESULT block per mutant | `--sample --write --seed 20260923`, then `--tier t1` / `--tier confirm --only <keys>` |
| `structure_kill.py` | `tests/structure.py` alone over the sample, with the metric it moved | `--sites 40`, `--control` |
| `probe.py` | the delivered value of one production symbol, control vs mutant | `probe.py guard_floor_hold`, `probe.py guard_floor_hold --mutate` |
| `sample.json`, `results-t1.json`, `confirm.json`, `confirm2.json`, `structure_kill.json`, `baseline-*.json` | the frozen sample and every RESULT block | — |
