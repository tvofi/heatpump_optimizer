# Round 9 — D3 (test-suite gaps), seat D3-s2

Baseline `1936d5ca72a06556eeed4e8e5bf3dea520e517e1`; box B2 (4-CPU Linux container, 15 GB,
shared with two other compute seats). Cells: D3.M1–M5 over
`custom_components/heatpump_optimizer/{optimizer,thermal_model,sysid,defrost,flow_lift,price_model,tariff,grid_fee}.py`.
Interpreter `/home/claude/venv314/bin/python`, `PYTHONPATH=tests/hastub`, BLAS pinned to 1 thread.

**Exposure:** none. No `docs/`, GitHub or earlier-round evidence was read. The host deleted
`tools/audit/round3..round8` from this export while the run was going, and none of it had been opened. The
worker worktrees (`git worktree add HEAD`) do contain those files, because the gate scripts need them. They
were run, never read. The mutation ledger (`tests/mutation_budgets.json`, `tests/mutation_ledger/`) was not
used for selection.

## Method

1. **M1 pool** (`pool.py`). The candidate inventory for the eight modules is the gate's own six operators
   (`tests/mutation_table.py:candidates`) plus two operators added here: `NP_CLIP`, which turns
   `np.clip(x,a,b)` into `x`, and `EXCEPT_RAISE`, which turns a one-line except-handler body into `raise`.
   GUARD_OFF sites whose body only logs, and TYPE_CHECKING guards, are dropped. The inventory holds 1283 sites.
   Weights are module times kind:
   - module: optimizer/thermal_model/tariff 3, grid_fee/price_model 2.5, the rest 2
   - kind: clamp/clip 3, guard/boolop/const/except/raise 2, return-delete 1.5

   The draw is 4 per module with seed 90302, giving 32 mutants (`pool.json`, byte-identical on re-run).
   Tranche 2 is 1 per module with seed 90303, giving 8 more (`pool2.json`, T01–T08).
2. **M2 pre-screen** (`prescreen.py`). Each mutant runs against the measured closure of its file from
   `tests/closures.json`, with these drivers left out:
   - `stress.py`, `edge.py` and `backtest.py`, as the brief says;
   - `golden.py`, whose default mode *is* the env_drift step;
   - `card_drift.mjs`, which takes no production input.

   `card.mjs` runs after `plan_view.py` with a private `HPO_PLANDATA`. `tests/env_drift.py --all <ref>` also
   runs. A kill is `tests/mutation_table.py:killed`: the driver is red *and* names more failing checks than its
   unmutated baseline did. Every mutant runs in its own `git worktree` under a mkdtemp root.
   - **Ref:** the baseline SHA is this worktree's HEAD, and env_drift refuses a self-comparison. The ref is
     therefore `HEAD^1` (8cca77bc). It differs only by the release stamp: VERSION, the manifest and card
     version strings, the claim headers and the D6 claims. The unmutated env_drift run against it was green.
   - **Baseline:** all 17 drivers were green (`baseline.json`).
   - **Null control:** a comment-only edit of `optimizer.py` LIVES under all 17 drivers, in each of the three
     runs.
   - **Early stop:** after a kill, only drivers recorded under 20 s keep running, and env_drift is skipped.
     Survivors run every driver.
3. **Store-guard census** (`storeguards.py`, which is also the seam rule). The rule enumerates every
   guard, return, except, clip or clamp site inside a persisted-state parser (`from_dict`, `_grid_of`,
   `_stored_peaks`, `restore*`, `load*`) in the eight modules. It finds 38 sites. The census pre-screened the 7
   finiteness and range sites with the same harness (`D3S2_ORDER=measured`, `results_store.jsonl`). It
   included S01–S04, which ran before the census was narrowed.
4. **M4** (`witness.py`, `mutload.py`). For each survivor, the witness loads the production module twice: as
   it is, and with the mutant line exec'd into a fresh module object. It then counts the probe inputs on which
   the production symbol's output diverges. There are two domains:
   - (a) the domain the integration can reach, such as config-flow ranges or a store payload's own shape;
   - (b) an out-of-domain positive control.

   If (a) shows no divergence, the survivor is an equivalent mutant (a non-finding). If (a) diverges and the
   suite stays green, it is a gap.
5. **M5** (`resources.py`). This is one unmutated pass per driver with a sitecustomize hook that counts
   `HeatPumpOptimizer.optimize` calls. It records checks, solves, child CPU (`os.wait4` rusage), and kills per
   driver across every results file.

## Pre-screen results (40 drawn mutants; 11 census sites)

| id | kind | site | verdict | killer |
|---|---|---|---|---|
| M01 | GUARD_OFF | optimizer.py:877 `if n_steps == 0:` | SURVIVED | – (equivalent) |
| M02 | GUARD_OFF | optimizer.py:6410 `if hi <= lo:` | SURVIVED | – (equivalent in domain) |
| M03 | BOOLOP | optimizer.py:3739 `two_zone and result.upper_temp_trajectory` | SURVIVED | – (equivalent) |
| M04 | GUARD_OFF | optimizer.py:816 `cost_per_cycle <= 0 or p_max <= 0 …` | SURVIVED | – (equivalent in domain) |
| M05 | CLAMP_DROP | thermal_model.py:2132 | KILLED | features |
| M06 | RETURN_DEL | thermal_model.py:1737 | KILLED | features |
| M07 | NP_CLIP | thermal_model.py:1360 | KILLED | features |
| M08 | CLAMP_DROP | thermal_model.py:1904 `max(dt_hours, 1e-6)` | SURVIVED | – (equivalent in domain) |
| M09 | GUARD_OFF | tariff.py:246 | KILLED | finite_boundary |
| M10 | RETURN_DEL | tariff.py:125 | KILLED | features |
| M11 | CLAMP_DROP | tariff.py:313 | KILLED | features |
| M12 | BOOLOP | tariff.py:136 | KILLED | env_drift |
| M13 | RETURN_DEL | grid_fee.py:202 | KILLED | config_flow_steps |
| M14 | GUARD_OFF | grid_fee.py:324 | KILLED | features |
| M15 | RETURN_DEL | grid_fee.py:356 | KILLED | env_drift |
| M16 | GUARD_OFF | grid_fee.py:157 | KILLED | env_drift |
| M17 | BOOLOP | price_model.py:355 | KILLED | features |
| M18 | GUARD_OFF | price_model.py:622 | KILLED | features |
| M19 | GUARD_OFF | price_model.py:415 `if known_count >= n_steps:` | SURVIVED | – (equivalent) |
| M20 | EXCEPT_RAISE | price_model.py:371 | KILLED | finite_boundary |
| M21 | GUARD_OFF | sysid.py:1175 | KILLED | features |
| M22 | GUARD_OFF | sysid.py:1657 | KILLED | features |
| M23 | GUARD_OFF | sysid.py:1302 | KILLED | features |
| M24 | CLAMP_DROP | sysid.py:1563 `max(thermal_mass_prior, 0.1)` | SURVIVED | – (equivalent in domain) |
| M25 | BOOLOP | defrost.py:722 | KILLED | features |
| M26 | BOOLOP | defrost.py:660 | KILLED | features |
| M27 | BOOLOP | defrost.py:480 | KILLED | finite_boundary |
| M28 | EXCEPT_RAISE | defrost.py:475 | KILLED | finite_boundary |
| M29 | RETURN_DEL | flow_lift.py:110 | KILLED | env_drift |
| M30 | GUARD_OFF | flow_lift.py:107 | KILLED | features |
| M31 | GUARD_OFF | flow_lift.py:210 `if not np.isfinite(bias) or samples < 0:` | **SURVIVED** | – (**gap**, D3-s2-01) |
| M32 | NP_CLIP | flow_lift.py:179 | KILLED | features |
| T01 | NP_CLIP | optimizer.py:6899 | KILLED | env_drift |
| T02 | GUARD_OFF | thermal_model.py:2555 | KILLED | features |
| T03 | GUARD_OFF | tariff.py:321 | KILLED | manual_plan, config_flow_steps |
| T04 | RETURN_DEL | grid_fee.py:121 | KILLED | features |
| T05 | GUARD_OFF | price_model.py:329 | KILLED | features |
| T06 | CONST | sysid.py:476 `_PROFILE_CHI2_95` | KILLED | entities |
| T07 | CLAMP_DROP | defrost.py:384 | KILLED | features |
| T08 | EXCEPT_RAISE | flow_lift.py:209 | KILLED | finite_boundary |
| S01–S04, S08, S31, S38 | store parsers | tariff/_stored_peaks, tariff.py:393/458, defrost.py:506, flow_lift.py:221 | KILLED | features / finite_boundary |
| S05 | GUARD_OFF | tariff.py:402 `if not math.isfinite(tracker._window_factor):` | **SURVIVED** | – (gap, D3-s2-01) |
| S17 | GUARD_OFF | price_model.py:324 shapes `if not np.all(np.isfinite(parsed)):` | **SURVIVED** | – (gap, D3-s2-01) |
| S18 | GUARD_OFF | price_model.py:349 quarter factors, same | **SURVIVED** | – (gap, D3-s2-01) |
| S19 | CLAMP_DROP | price_model.py:368 `max(0.0, float(v))` → `(0.0)` | **SURVIVED** | – (gap, D3-s2-02) |

**Totals.** The drawn pool had 8 survivors out of 40. Seven are equivalent over the reachable domain, and one
(M31) is a gap. The store census had 4 survivors out of 11, and all four are gaps.

## Findings

### D3-s2-01: store-parser non-finite guards in flow_lift, tariff and price_model are pinned by no check (I1)

**Property.** Every finiteness guard in a persisted-state parser of the eight modules should turn a gate driver
red when it is deleted. `storeguards.py` enumerates six such `isfinite` guards, and deleting four of them
leaves every closure driver green:
- flow_lift.py:210 (M31, the same mutant as S34);
- tariff.py:402 (S05);
- price_model.py:324 (S17);
- price_model.py:349 (S18).

The other two, tariff.py:393 (S04) and :458 (S08), are killed by features.

**Witness.** The in-domain probes diverge 0 times: 60, 4, 10 and 10 well-formed payloads. The corrupt payloads a
Store can return diverge as follows. A string such as `"nan"` or `"inf"` parses through `float()`.
- **flow_lift.py:210:** 6 of 6 corrupt payloads restore a non-inert learner, where the original restores all
  six to inert. `"inf"` restores a 15 K bias, and the COP the plan prices at −10 °C moves from 2.0125 to
  1.8619. `"nan"` persists as a NaN bias through the next fold (2 of 6). `samples: -1` makes
  `FlowCurveBias.observe` raise `ZeroDivisionError` on the next fold (1 of 6).
- **price_model.py:324 and :349:** one `"nan"` bin prices the guessed steps at 0.0. The shapes guard gives
  0 of 288 steps originally against 12 of 288 under the mutant; the quarter-factor guard gives 0 against 3.
  This is exactly the #922 failure the code comment names.
- **tariff.py:402:** a stored `window_factor: "inf"` closes into `billed_peak_kw = inf`, and `threshold_kw`
  moves from 3.0 to 3.5.

**The check that should fail (M4).** `tests/features.py`, the check *"corrupt stored state restores to inert
too"*. It exercises `{"bias_k": "nonsense"}`, `None` and `900.0`, but no non-finite or negative-count payload.
The PriceShapeModel and PeakTracker corrupt-payload checks likewise feed no `"nan"` or `"inf"` in these
fields.

**Severity: medium.** The mutant is a regression the gate would ship green. Its consequence needs a corrupt
store, but then it is a crash on every fold, or a guessed hour priced free.

### D3-s2-02: the persisted `residual_var` round trip is pinned by no check (I1)

`price_model.py:368` survives with `[max(0.0, float(v)) …]` replaced by `[(0.0) …]`. That mutant throws away
every stored variance on load, and all 15 closure drivers stay green.

**Witness.** A learned model makes the restart round trip as_dict → from_dict → `extend_price_series`. The
original gives a non-zero sigma on 96 of 96 guessed steps; the mutant gives 0 of 96. Random stored variances
diverge on 10 of 10 probes. `tests/features.py:41446` loads only a corrupt `"x"` payload and compares the result
to a fresh model. The mutant satisfies that comparison, so no positive-control round trip exists.

**Severity: low.** The learned σ feeds the opt-in `price_risk_lambda` term, which defaults to 0.0, and the
`summary()` sigma diagnostics. Both would silently reset on every restart.

## Non-findings (M4, survivors that are equivalent)

Each line gives the reason and the witness result from `witness.py <ID>`.

- **M01:** `classify_space_steps` loops `range(n_steps)`, and the percentile is guarded. Divergence was 0 of 50.
- **M02:** the config flow bounds `buffer_max_temperature` to 40–90, and the flow reference is a fixed 35 °C,
  so `hi <= lo` is unreachable. Divergence was 0 of 44 in domain and 2 of 8 out of domain, at 25–30 °C.
- **M03:** a single-zone step sets `upper_floor_temperature = new_room` (thermal_model.py:2025). The two
  trajectories differ only at index 0, which the loop never reads. Divergence was 0 of 60, and 26 of 60
  probes released steps.
- **M04:** the config flow bounds the cycling cost to 0–10 and the rating to 1–20 kW. Divergence was 0 of 45
  in domain and 3 of 3 out of domain.
- **M08:** the planner's steps are ≥5 minutes. Divergence was 0 of 40, with 20 floor hits among them, and 1 of
  1 at dt = 0.
- **M19:** when `known_count >= n_steps`, the fall-through loop is empty. Divergence was 0 of 80.
- **M24:** `RANGE_HOUSE_THERMAL_MASS` is (0.5, 80), which is ≥ 0.1. Divergence was 0 of 42, with 31 completed
  fits, and 2 of 2 for priors below 0.1.

M11 was killed, by features.py. Its witness shows why an equivalence argument would have been wrong. Billed and
threshold values diverge 0 times in 3360, but the persisted peaks diverge 1190 times in 3360, and a check reads
them.

## M5: resource use

Every wall and CPU number is **provisional**, taken with load1 between 2 and 5 on the shared box. In
`resources.py`, the harness's own `thread_factor` covers only its pipe-reader threads. The children are pinned
to one BLAS thread by the environment.

**Checks, solves, and CPU against recorded seconds:**

| driver | checks | solves | checks/solve | child CPU s | recorded s |
|---|---|---|---|---|---|
| features.py | 3420 | 126 | 27.1 | 237 | 140.7 |
| optimality.py | 84 | 23 | 3.65 | 141 | 198.4 |
| entities.py | 2025 | 0 | – | 64 | 106.8 |
| validate.py | ISSUES format | 22 | – | 35 | 56.5 |
| manual_plan.py | 85 | 21 | 4.0 | 6 | 6.4 |

The env_drift baseline is a real `--all` run and took 474 s wall. `closures.json` records the 0.3 s stub run, and
its comment says so (#934).

**Kills per driver over all 51 screened mutants** (drivers that ran / killed):
- features.py: 25/37
- finite_boundary.py: 6/44
- env_drift.py: 5/44
- config_flow_steps.py: 2/51
- entities.py: 1/38
- manual_plan.py: 1/51
- validate.py: 0/23
- optimality.py: 0/11
- 0/51 for each of card.mjs, plan_view, typing_ruler, solar_alignment, wood_advisor, guard_pins,
  deployment_shape, structure and doc_claims.

**Reading these numbers:**
- The early stop makes the "sole" counts an artefact of cost order, so they are not reported as duplication.
  Duplicated coverage was measured only among the cheap drivers. No two of them killed the same mutant, except
  on T03: manual_plan and config_flow_steps.
- The nine zero-kill cheap drivers together cost under 25 s per run. They are in the closure because they read
  the source text, which is a static-analysis dependency and not an over-approximation worth a finding.
- entities.py is in every one of the eight closures and costs about 64 s of CPU per run. It made 0 solves and
  killed 1 of 38 mutants.
- None of these is filed as a finding, because no bar is violated.

## Harnesses

- `tools/audit/round9/D3/s2/pool.py`
- `prescreen.py`
- `witness.py` and `mutload.py`
- `storeguards.py`
- `resources.py`

Data files:
- `pool.json`, `pool2.json`, `storeguards.json`
- `baseline.json`
- `results.jsonl`, `results2.jsonl`, `results_store.jsonl`
- `resources.json`

## Unfinished

- **D3.M3:** the quiet-window full `GATE_SCOPE=full GOLDEN_MODE=drift` gate for the top survivors still has to
  run: M31/S34, S17, S18, S05 and S19. It belongs to the judge's quiet window.
- **D3.M2:** the census drove only the 7 finiteness and range sites, plus the 4 that had already run. The other
  27 store-parser sites in `storeguards.json` (isinstance, return and except sites) are not pre-screened.
- **D3.M5:** the wall and CPU numbers need the quiet-window re-take. Duplicated coverage across the heavy
  drivers (features, entities, optimality, env_drift) needs an `--all-drivers` run.
