# Pre-study: the core modules behind the HA surfaces — scoping report

tvofi, 2026-09-28. Read-only pre-study. Companion to the surfaces study
(`r9scratch/surfaces-prestudy.md`); this covers the **core** modules the
surfaces sit on, plus four scope extensions folded in at tvofi's request
(test-corpus split §5.5, symbol-anchored pins §5.6, roster resume sidecar
§5.7, closures.json split §5.8) and one sequenced endgame plan (§6). All measurements taken in a detached worktree at
**`origin/main` = `31394964`** (Merge PR #1734, F2.5). Note: this seat's
branch ref initially sat at `cdbc2584` (60+ commits stale, missing F2.5's
`batchmath.py`); it was detached onto `31394964` before any count below was
taken. Every count comes from a command run at that tree; file:line cites are
at that baseline. Line counts for the study set, measured (`wc -l`):

| file | lines | god class (loc, methods, attrs) |
|---|---|---|
| `coordinator.py` | 10,947 | `HeatPumpOptimizerCoordinator` 9,026 / 224 / 153 |
| `optimizer.py` | 7,274 | `HeatPumpOptimizer` 5,453 / 70 / 8 |
| `config_flow.py` | 3,847 | OptionsFlow 880 / 32; ConfigFlow 810 / 24 |
| `thermal_model.py` | 3,379 | `ThermalModel` 1,933 / 31; `ThermalParameters` 910 / 25 |
| `tariff.py` | ~1,007 | — |
| `topology.py` | ~986 | — |
| `services.py` | 1,058 | — |
| `store.py` | ~— | — |
| `batchmath.py` | 64 | (new in #1734 — the F2.5 split precedent) |

`tests/structure_budgets.json` at this head: `coordinator_loc` 9,026,
`coordinator_methods` 224, `coordinator_attrs` 153, `cross_seam_edges` 134,
`cut_learning` 284 (the densest seam), `classes_over_300` 11,
`max_class_loc` 9,026, `max_method_loc` 386, `methods_over_150` 18.

---

## 1. Decision classes OUTSIDE the surfaces (question 1)

### (a) Merged-config read `{**entry.data, **entry.options}` — 6 sites, one helper

`coordinator.py:1821`, `__init__.py:370`, `services.py:657`, `services.py:784`,
`climate.py:101`, `binary_sensor.py:179` (grep, exact idiom). Four are
core-reachable. A `merged_config(entry)` helper is ~8 lines and
behavior-identical. This is the same class the surfaces study scoped (its 6
sites are the same 6); the core-resident half rides the same PR.

### (b) Time/clock handling — raw sites and the F1.1 helpers

Raw `dt_util.now()/utcnow()/datetime.now()/as_utc/start_of_local_day/
parse_datetime` call sites, per file (grep count): **coordinator.py 70**,
legionella 5, boost 4, binary_sensor 4, inputs 3, dhw_learning 3, switch 2,
services 2, pump_arbiter 2, open_meteo 2, `__init__.py` 2, store 1,
optimizer 1, defrost 1 — **102 sites across 14 files**. The class P7 (#1665)
and I1 (#1646) instances live here; F1.1's finder measured 8 production seams
still doing wall-clock arithmetic across DST, with `p7_static_sites.py` listing
**74 static candidates** (F1 brief, D14-s4-01).

The F1.1-era canonical helpers, and the one real duplication found:

- `_utc_age_seconds` — `coordinator.py:719`, 8 call sites, all in coordinator.
  Good.
- **`_utc_step_starts` is defined twice**: `coordinator.py:553` (midnight,
  n_steps, step_offset, step_minutes) and `optimizer.py:198` (start, n,
  dt_hours) — same name, same UTC-walking rule, different signatures;
  `silent_mode.py:58` imports the optimizer one, `tests/dst_checks.py` imports
  both (aliased). Name-level twins, not byte twins — dedup is a small
  signature-unifying refactor, not a move. This is the clock class's one
  cross-module consolidation left.
- `_solve_anchor` `coordinator.py:1451`; handover trio `__init__.py:154-173`.
- Barrier: `tests/dst_checks.py` + `tests/features.py` (`HASTUB_TZ`), the seam
  F10.1's aware-default stub clock feeds.

### (c) Error-path / repair-issue reporting — already consolidated

One canonical wrapper exists: `setpoint_check.create_issue`
(`setpoint_check.py:40`, defaults the documentation link, #558 F2). The
coordinator aliases it (`coordinator.py:445 _create_issue = …`) and calls it at
**11 sites**; `legionella.py` 6; `pump_arbiter` 1. F1.3's
`_note_solve_failure` is the coordinator's own `_solve_failures` state machine
(`coordinator.py:2000`, issue raised/cleared at `:5064-5131`) plus
`_note_worker_fallback` (`:1129`) — single-owner, no sibling. `services.py`
uses translated `HomeAssistantError` raises (a different mechanism). **Nothing
to merge.**

### (d) Price/tariff reads — already consolidated, one intra-file twin

All entity-price reads route through coordinator module-level helpers
(`_entity_price` `:1323`, `_unit_scale_of` `:1374`,
`_grid_fee_entity_value` `:1318`, `_entity_price_source` `:1733`); `_entity_price`
has 6 uses, all inside coordinator. `tariff.py` is imported by coordinator,
optimizer, topology. The residue the structure detector sees is **inside**
tariff: `peak_cost` (`:808`) vs `peak_cost_smooth` (`:876`), 12 normalized
lines — one of the 7 detected duplication pairs. F2.5 already began the
extraction (`batchmath.py`, 64 lines, `row_sums`). Route the pair to the F2
lane's brief, not a standalone PR.

### (e) `coordinator.data or {}` state reads — none in core

72 sites, all surfaces (`sensor.py` 67, `climate.py` 3, `repairs.py` 1,
`binary_sensor.py` 1). The core publishes; it never reads its own payload this
way. **Out of scope here** — the surfaces study owns it.

### (f) The structure duplication detector's 14 blocks — 7 pairs, 6 in these files

`tests/structure.py` tables, at this head (file, function, line, norm lines):

| pair | site A | site B | norm |
|---|---|---|---|
| config_flow `async_step_building_extras` / `async_step_thermal` | :2640 | :2676 | 10 |
| coordinator `_async_learn_house_heat_loss` / `_async_learn_lower_floor_loss` | :4186 | :4385 | 15 |
| optimizer `_space_traj` ×2 | :3934 | :6161 | 14 |
| optimizer `objective_batch` ×2 | :3996 | :6225 | 10 |
| tariff `peak_cost` / `peak_cost_smooth` | :808 | :876 | 12 |
| thermal_model `_simulate_step_two_zone` / `simulate_step` | :2080 | :2391 | 13 |
| thermal_model `simulate_trajectory` / `simulate_trajectory_with_dhw` | :2539 | :3082 | 19 |

`duplication_blocks` sits at 14 = budget, zero headroom: **refactoring any
pair frees budget headroom; copying anything new refuses.** These pairs are
each an F-lane file's business (coordinator→F1, optimizer/tariff/thermal_model→F2,
config_flow→F5); per `finding-propagation.md` they belong in those lanes'
briefs, not in a consolidation PR that would collide with them.

### (g) Config-key reads bypassing canonical predicates (P2 residuals)

The core-side canonical read is `effective_config` (`coordinator.py:2483`);
raw `entry.options.get`/`entry.data.get` in core survive only in
`services.py` (3 sites). The live P2 residue is the **proxy-key** class:
D14-s2-01 (F1.2) — the two-zone and wood-furnace facts re-derived from proxy
keys at three seams beside their canonical predicates — and D12-s3-01, where
the config-flow wizard invents presence from untouched defaults. The class
sweep (S1, `tools/audit/round9/D14/sweep/P2/SWEEP.md`, commit `c44e7bcd`)
dispositioned **N=27, rca: true** — the round's largest class — and its
enumerator (`sweep/P2/enumerator.py`, D14-s2-01's `p2_facts.py`) is the only
package-wide mechanical detector in the class. The canonical DHW predicate
chain is intact: `_dhw_enabled_from_config` (`thermal_model.py:1096`) →
`has_hot_water` (`entity.py:179`) → boost/entity readers. **The barrier is
F1.11's owners-registry** (P2 + P6 in `tests/entities.py`, `Fixes #1644`,
`Fixes #1651`) — anything in this study that touches a predicate seam must
land after it or re-key its registry entries.

### (h) Class-issue cross-references (from the fixplan briefs, F1–F5)

`#1644` P2 (12× Part-of), `#1647` P1 (5×), `#1645` I5 (4×), `#1651` P6 (3×),
`#1649` P11 (2×), `#1646` I1, `#1654` P3, `#1655` P5, `#1657` P8, `#1664` P4,
`#1665` P7, `#1683` N-shared-config, `#1686` N-structure-blind, `#1661`
N-dead-member, `#1650` I4. Of these, the ones that live **on the core
decision-classes above**: P7/P11/I1 (clock, b), P2 (config predicates, g),
P6 (state/payload keys, e), P1 (store boundaries — store.py already fully
pinned, see §2b), I5 (doc-claims reads of these files), N-structure-blind
(F10.4's `D7-s1-01`: coordinator state reached through module-level
`_helper(self, …)` escapes the ratchet — relevant to any split, which would
convert counted `self.` refs into uncounted module-level calls and move
several `coordinator_*` metrics in a direction the honest re-record may
raise).

---

## 2. Coordinator decomposition (question 2)

### (a) Seams, measured — and what the seam map says about a split

Existing seam map (`tests/seam_map.json`, 224 methods; `structure.py`
counting rules). Per-seam rows (methods / owned attrs / cross-attr refs /
cross-call edges / **cut cost**) and method-line share (computed from AST
spans):

| seam | methods | lines | share | attrs | cut |
|---|---|---|---|---|---|
| core (unassigned) | 118 | 4,480 | 51% | — | — |
| learning | 26 | 1,703 | 20% | 40 | **284** |
| grid | 22 | 812 | 9% | 33 | 195 |
| fetch | 28 | 673 | 8% | 15 | 129 |
| views | 15 | 567 | 6% | 3 | 109 |
| dhw | 16 | 480 | 6% | 3 | **73** |

`internal_call_edges` 312, `cross_seam_edges` 134, **cross-seam fraction
0.43**. The "core" bucket is the grab-bag: I re-partitioned it by name
(store = `_async_load_*/_async_save_*`, 9 methods/158 lines; glue =
setup/watch/subscription, 2/43; service entry points, 8/171; state accounting,
8/808; model-init, 10/361; the rest "cycle" **107 methods / 2,987 lines**) and
recomputed cut costs with structure.py's own rules: the cycle cluster alone
cuts at **836** and calls every other cluster (out-edges: fetch 15, grid 14,
learning 12, model 10, dhw 4, views 4, store 3, acct 5). Name-based
subdivision of the coordinator does **not** find a cheap cut; the existing
five named seams are the only ones with cut < 300, and only dhw (73) and views
(109) are under 150.

This reproduces the recorded round-2 verdict: D7-05 (`docs/audit-2026-09.md:613`)
— no clustering at k = 6..16 gets cross-cluster attribute references under
0.33; six hub attributes bind the class (`_config` read by 77 methods,
`_thermal_params` 63, `hass` 42, `_current_state` 36, `_opt_config` 32,
`_current_action` 23). And it reproduces the #193 programme's outcome:
**S0–S13 ran this experiment and closed 2026-09-10** with two recorded halts —
S4/fetch (`#508`, no component of size > 1 detaches at any k; 92 of cut_fetch
was *other* seams reading fetch's 15 attrs) and S12 (`#637`, no subsystem API
to migrate tests to) — plus S5/dhw merged (`#529`, cut_dhw 194→103 by
re-homing twelve misfiled attributes). Seam moves are "sequenced to S12, not
banned" — but S12 is itself a recorded halt.

**Named seam candidates, with the evidence**: if a split ever happens, the
only evidence-backed units are (1) **dhw** (16 methods, 480 lines, cut 73 —
the S5-proven seam), (2) **views** (15/567, cut 109), (3) **fetch** (28/673,
cut 129 — but S4's halt explains why: its attrs are read everywhere),
(4) **learning** (26/1,703, cut 284), (5) grid (22/812, cut 195). Cycle
orchestration, store management, press/service handling and HA glue do not
detach: they are the hub the other four call into. A 3–7-module split at
today's numbers would put 4,500–6,500 lines in one module and one-liners in
the rest.

### (b) Costs, measured

- **Mutation ledger** (`tests/mutation_ledger/`): coordinator.py carries
  **47 `killed_by` pins** (of 415 repo-wide, `find … -name '*.json' | wc -l`;
  second only to pump_arbiter's 104). The deterministic inventory
  (`mutation_table.py` counting rules, run at this head): coordinator.py
  **809 candidate sites, 759 unpinned** (of 4,057/3,592 repo-wide). A split
  re-keys the 47 pins
  (the key's FILE component changes; the `old`-text digest survives a pure
  move — the documented `--normalize` path, one command) and
  `mutation_budgets.json`'s single coordinator line-pin
  (`coordinator.py:10330 GUARD_OFF`) re-keys to the moved line. The 759
  unpinned sites are derived, not stored — they re-key for free.
- **Closures**: coordinator.py is in **16 of 27** recorded closures
  (`tests/closures.json`; the entities.py closure alone is 190 files, golden's
  169). Every new module joins all 16. Re-derivation is the CI
  closures-autofix path (never a Darwin full `derive_closures.sh` — gate-scoping.md;
  F10.4's brief confirms the autofix records new closures).
- **Structure budgets**: 13 coordinator-keyed metrics move **down** on a split
  (`coordinator_loc` 9,026, `max_class_loc`, `coordinator_methods` 224,
  `coordinator_attrs` 153, `coordinator_multiassigned_attrs` 116,
  `cross_seam_edges` 134, `internal_call_edges` 312, `cut_*` ×5) — allowed
  without a raise. **`classes_over_300` = 11 is the binding one**: it is at
  budget, and no measured cluster is under 300 lines (smallest detachable is
  dhw at 480), so every module added raises it — an owner-approved raise at
  head (0013). Precedent: W5-G9/G10 (`#750`, `#771`) raised
  `classes_over_300` once **per seam move**, on tvofi's word.
- **`seam_map.json`**: all 224 entries re-key to per-module maps; the
  `#1539` refusal ("a method the map does not name is refused") means the
  split PR rewrites the map in the same commit.
- **`local_imports`** (budget 7) grows by the split's cross-module imports —
  re-record direction up → possible raise.
- **D7-s1-01 (F10.4, N-structure-blind #1686)**: the ratchet does not price
  coordinator state reached via module-level `_helper(self, …)`. A split
  converts counted `self._x` reads into uncounted cross-module reads —
  several `coordinator_*` metrics move down *for the wrong reason*, and
  F10.4's honest-re-record rule (tvofi's card B5) is the instrument that
  would catch it. A split PR should land **after** F10.4, and say which of
  its metric drops are real.
- **Lane serialization**: the F1 lane owns `coordinator.py` outright and is
  11 PRs deep; at this writing **F1.1–F1.3 are merged, F1.4 is in flight**
  (active worktree `/Users/timmalmstrom/fix-r9-f1-coordinator-4`, PR dirs in
  `r9scratch/f1-4*`), and **F1.5–F1.11 (7 PRs) are not started**, each
  `After:`-chained on the previous because each edits coordinator.py.
  F10.4 borrows coordinator.py from F1; F3.1 borrows it for two store
  constructions; F1.7 is "cross-lane coordinator readers". A decomposition PR
  queues behind all of them, or forces a rebase of each.
- **What a split would buy, honestly**: `coordinator_loc`/`max_class_loc`
  relief — but the cap's job is refusing growth, and nothing in the round-9
  backlog needs to grow coordinator.py (the F1 fixes are behavior, mostly
  inside existing bodies). Review-round length does not improve: the scoped
  gate already runs the same 16-closure set for any coordinator touch, and
  new modules join it. F1 serialization relief is near zero: F1.5–F1.11's
  fixes live in the cycle cluster (error paths, cycle fencing, the P2/P6
  barriers' subject matter), which is the part that cannot detach.

### (c) The move-PR hazard — recorded in this repo's own history

`docs/plan-2026-09-open-issues.md:35`, plan principle 3: *"A behaviour fix in
a region lands before that region's move PR. A fix inside relocated lines is
reverted silently by the move's rebase, with no conflict and no failing test —
#324 nearly lost that way inside #340."* The hazard is not hypothetical and
not historical: with F1.4 in flight and F1.5–F1.11 pending, a coordinator move
PR cut today would rebase over up to seven behavior PRs landing inside the
moved block, each revert silent. Any decomposition must be sequenced strictly
after the lane drains, and its diff verified by the
`git diff $(git merge-base origin/main HEAD)...HEAD` three-dot discipline plus
a whole-file comparison at the resolution (the #719 protocol), because the
revert mechanism fires at rebase/merge time, not at diff time.

### (d) Verdict on 3–7 modules: **NOT WORTH IT — now, and the evidence says the honest endgame is smaller than 3**

Improves: the god-class number and nothing measured else (§2b). Costs: 37
ledger pins + 1 line-pin + 224-entry seam map re-key, 16 closures, 13 budget
re-records plus at least one structural raise (`classes_over_300`), collision
with the entire remaining F1 lane, and the plan-principle-3 revert hazard
amplified by seven pending in-block PRs. Against that: the repo's own
decomposition programme (#193 S0–S13) already established the ceiling —
hub attributes bind the class, no k-detachment exists, two of its stages
halted on exactly the evidence this study re-measured (cut costs 0.43
cross-seam fraction, cycle cluster cut 836).

**Recommendation**: no coordinator split in round 9 or the endgame wave. If
tvofi still wants the god-class number down after the lanes drain, the only
evidence-backed moves are the S5-proven kind: one attribute-ownership seam
move per PR, starting with **dhw** (cut 73, 480 lines) and **views** (cut
109, 567 lines) — two PRs, each with a `classes_over_300` raise on tvofi's
review. That is 2 modules, not 3–7, and it is the ceiling the measurements
support. The seam map itself (`tests/seam_map.json` + the `cut_*` metrics) is
already the standing instrument for any future attempt; nothing needs
building to keep the option alive.

---

## 3. optimizer.py — the same treatment (scope extension)

Clustered by name over `HeatPumpOptimizer`'s 70 methods (class loc 5,453;
plus 39 module-level functions, 971 lines — the solver mechanics:
`_multi_start_minimize` 147, `_batch_fd_gradient`, `_lbfgsb_restart`,
`_fused_value_and_gradient` — and the dataclasses `OptimizationResult` 113,
`OptimizationConfig` 198, `_Horizon` 96). Cut/edge matrix with structure.py's
self-call rule:

| cluster | methods | lines | in | out |
|---|---|---|---|---|
| **dhw_plan** (`_optimize_with_dhw` 386, `_build_dhw_requirements` 352, `_plan_dhw_min_cost` 211, `_repair_dhw_floor` 198, `_plan_dhw_cheapest_first` 171, legionella 300 across 4, …) | 20 | **2,237** | **4** | 12 |
| solve (optimize 376, `_optimize_space_only` 297, `_solve_space`, caps/holds/pins) | 20 | 1,341 | 11 | 14 |
| cost (`_terminal_cost[_batch]`, `_comfort_terms[_batch]`, `_energy_cost_fn`, `_grid_terms`, settlement/deferred/buffer) | 13 | 816 | 17 | 9 |
| baseline_view (`_compute_baseline_power` 133, `get_current_action` 139, `_build_result` 123, `_analyze_forecast_trajectory`, `power_to_*`) | 16 | 937 | 10 | 7 |

The priors verified and corrected: **dhw planning is the one genuinely
detachable cluster** (2237 lines, only 4 inbound edges; `optimize` calls into
it once). **Batch math is NOT already split** — F2.5's `batchmath.py` is 64
lines (`row_sums`); the `_*_batch` objective functions (816-line cluster) are
still inside the class and are **mutually coupled with the solve loop**
(solve→cost 8, cost→solve 7), so cost is not a seam, it is the solve's
co-routine. Storage-basin/two-zone handling are not clusters — two-zone lives
in `thermal_model` and the `_baseline_thermal_demand_*` pair (74/35 lines) in
baseline_view.

Costs, measured: optimizer.py carries **498 candidate sites / 465 unpinned /
30 `killed_by` pins** (inventory run at this head); it is in **22 of 27**
closures (worse than coordinator); **no `optimizer_*` budget exists** — the
only metrics a split touches are `classes_over_300` (raise, as above),
`max_class_loc` (stays 9,026 = coordinator, so no relief registers),
`duplication_blocks` (the two `_space_traj`/`objective_batch` pairs move but
stay detected), and `local_imports`. Test fan-in is heavy: `tests/features.py`
imports optimizer 38× (grep), so the golden/stress lane reads it regardless.

F2-lane collision: F2.1, F2.2, F2.4 not started (F2.3, F2.5 merged); the
roster's F2.3→F2.5→F2.4 resequencing was forced by optimizer.py's single-file
ownership — a split would have avoided that one serialization, but it comes
too late to help the remaining three PRs.

**Verdict: FEASIBLE WITH CAVEATS, after F2 drains, as 2 modules** —
`optimizer_dhw.py` (the 2,237-line cluster + its two module-level helpers) and
optimizer proper — not 3–7; the cost cluster's mutual coupling with solve is
the measured blocker. Pay: 29 ledger pins re-keyed, `classes_over_300` +1,
22 closures, seam-free (no seam map for optimizer — none needed at 2 modules).
Smallest honest version: extract only `_build_dhw_requirements` +
`_plan_dhw_*` + repair/clamp (≈1,600 lines) if tvofi wants less surface.

**Short paragraphs, as asked:**

- **thermal_model.py (3,379)** — cohesive physics with measured twin pairs,
  not clusters: the duplication detector flags `_simulate_step` vs
  `_simulate_step_two_zone` (13 norm lines) and `simulate_trajectory` vs
  `simulate_trajectory_with_dhw` (19) — those are in-file refactors for the
  F2 lane, not module seams. `ThermalParameters` (910-loc dataclass, 25
  methods) could lift out cheaply (10 importers) but buys no budget relief
  (`classes_over_300` +1, nothing else moves). **Not worth a split; worth the
  two twin refactors inside F2.**
- **config_flow.py (3,847)** — framework-constrained (HA ConfigFlow/OptionsFlow
  API shapes the two 800-line classes); the F5 lane owns it and F8.1/F8.3 +
  F10.4's I5 doc-claims arms read facts straight out of it. Its one detected
  dup pair (`async_step_building_extras`/`async_step_thermal`) routes to F5.
  **Excluded, same reasoning as the surfaces study.**
- **sensor.py (2,834) family file-split** — 55 flat one-per-entity classes;
  `entities.py`'s `collect()` does not care how they are filed; no
  `sensor_loc` budget exists, so a split buys no metric relief while adding
  ~5 classified files and closure entries. The surfaces PRs already take
  ~60 lines off. **Not worth it after the surfaces PRs either.**
- **`classes_over_300` = 11** — the god-CLASS layer is the binding constraint
  for every split in this report: module splits do **not** absorb it unless
  each new class lands under 300 lines, which no measured cluster does
  (smallest detachable: coordinator dhw at 480). Every decomposition PR in
  this report raises it, per move, on tvofi's approving review (0013;
  W5-G9/G10 precedent). If the owner wants architecture the budget currently
  prices at zero, this is the one raise that buys it — and the honest form is
  "raise per seam move", already precedented, not a blanket loosening.

---

## 5. Scope extensions 5–8 (tvofi, second extension)

### 5. Test-corpus split: `tests/features.py` and `tests/entities.py`

**The serialization point, measured.** Every one of the last 8 round-9 merges
touched `tests/features.py` — #1722 +78, #1724 +557, #1717 +265, #1718 +316,
#1723 +383, #1731 +388, #1734 +278 (`git show --stat` per merge) — and 4 of 8
also touched `tests/entities.py`. The file is 52,769 lines with **112
classes** (`grep -c '^class'`); `entities.py` is 26,860 lines (4 top-level
classes; the ~2k checks live in class-named blocks). Each lane appends its
block at its sorted position (`features.py:432`, `:1634`: "class-named
blocks, sorted by class"), so every in-flight lane branch collides at the
same tail of one file on every update-branch, and each merge re-shifts the
lines later branches cite.

**The runner contract.** `tests/run.sh:408` `lane_units()` runs
`python tests/features.py` and `python tests/entities.py` **wholesale** —
`GATE_SCOPE` selects *scripts*, never blocks (closure.py's measured unit is
the script). A one-block lane fix runs all 112 blocks in every scoped gate;
the scoped-gate granularity and the merge granularity are both the file.
Line-pinned artifacts anchored on features.py: **zero formal pins**
(`mutation_budgets.json`'s 14 line pins name no test file; the carry files'
only tests anchors are 5× `tests/doc_claims.py:NNN` in carry-1645 and one
prose reference in carry-1653) — the real fragility here is merge conflicts
and context shift, not pin breakage; `entities.py`'s own string-mark
self-checks (#1217 mark-staleness) are content-anchored and survive shifts.

**Scope of a per-class package split** (`tests/features/<class>.py` + runner):
`run.sh` gains block discovery (112 files for features, ~8 block families for
entities); `GATE_SCOPE=auto` then needs a closure **per block-file** — 27
recorded closures become ~120-150, all re-derived at the split commit (CI
closures-autofix, per F10.4's precedent). Shared fixtures stay in
`tests/harness.py` (F10-owned) plus a new `tests/features/_shared.py` for the
module-level helpers the 112 classes share today — a new tracked file,
classified into the measured closures. Move-PR hazard: features.py is the one
file **every** lane writes, so this is the highest-collision move in the repo
— it lands only in an inter-wave window with no lane branch open, single
writer, everyone rebases after (plan principle 2).

**Verdict: feasible with caveats — high value (kills the 8-of-8 merge
collision and cuts lane-fix gate time from 112 blocks to 1), highest move-PR
risk of any item here; features first, entities second if at all (its
internal self-checks make it a follow-on, not the same PR).**

### 6. Symbol-anchored pins

**Line-anchored today, measured**: the mutation ledger is **already
content-anchored** — all **415 `killed_by` pins** (`find
tests/mutation_ledger/killed_by -name '*.json' | wc -l`) plus **42
`survivor_triage` pins** are keyed `FILE:SCOPE KIND DIGEST[#N]`, "sha1 of its
`old` text, never its line number" (`tests/mutation_budgets.json` `_comment`;
the migration ran in `fix/rca-ledger-anchors`, 2026-09-24, 103 dispositions,
zero unmapped). What remains line-keyed: `mutation_budgets.json`'s **14
`FILE:LINE KIND` pins** and the carry files' **5 `tests/doc_claims.py:NNN`
anchors** (carry-1645). **19 line-anchored pins repo-wide.**

**Re-key events this session**: #1734 alone re-parented one ledger pin
(batchmath `row_sums` out of optimizer — visible in its merge stat);
F8.3's absorb re-anchored carry-1645's arms (`e9b85744`). 5 of the 14 budget
line pins sit in files the F1/F2 lanes are actively editing — the treadmill
is one re-pin per touching merge.

**Migration scope**: extend the proven content-anchor form to the 19 —
`mutation_table.py --normalize` already computes the digest; F10.5's nightly
ledger writer owns the budget file and gains the anchor key; carry-1645's
doc_claims anchors become I5 barrier arm-name anchors (F10.4's absorb already
half-did this). **~30 lines across `mutation_table.py`,
`mutation_budgets.json`, `carry-1645.json` + the F10.5 writer.**

**Verdict: feasible, cheap, sequenced BEFORE any split** — a content anchor
survives a move; a line anchor does not. Post-migration, a split's ledger
cost drops from "re-key N pins + re-pin FILE:LINE" to "FILE component
re-keys, digests survive" (the #1412 normalize run proved the property
tree-wide).

### 7. Roster generator resume preservation

**Verified regen path**: `handoff/round9/fix/src/gen.py:457`
`g["resume"] = resume_of(pid)`; `resume_of` (`gen.py:415-428`) builds a fresh
template every run — `stage: "not-started"`, `commit: None`,
`last_step: None`, boilerplate `next_step` — overwriting exactly the four
fields the entry's own note says the record seat updates at each hand-off
(`gen.py:427`). Seven hand-restores this session.

**Proposed shape (sidecar)**: gen.py stops emitting the four mutable fields;
they live in `.claude/workflows/wave-r9-resume.json` (keyed `R9-<pid>` →
`{stage, commit, last_step, next_step}`), written only by record seats, never
regenerated. gen.py's `resume` keeps the static half (branch, note_file,
pickup commands — all derived, never mutated) and names the sidecar. The
sidecar beats an in-place overlay because gen.py's regen stays stateless (its
asserts assume a clean generate) and the sidecar is single-writer by
construction. **Cost: ~35 lines in gen.py + one seed commit. The cheapest
item in the plan.** No lane dependency — but land it before F1.5 starts so
the remaining eight PRs' resume fields stop being wiped.

### 8. `closures.json` per-script split

**Consumers, measured** (grep `closures.json`): `tests/closure.py` (the
scoping engine: select/merge/selftest), `tests/run.sh`, 
`tests/derive_closures.sh`, `tests/mutation_table.py`,
`tests/deployment_shape.py`, `tests/entities.py`,
`.github/workflows/tests.yml` (closures-autofix),
`.claude/workflows/counts.mjs`, `.claude/workflows/policy_lint.mjs` — **nine
consumers**. The file: 2,283 lines, 27 scripts, 2,110 file entries.

**The treadmill, measured**: closure re-records are a standing commit class
(`cf6d4eff` re-recorded doc_claims after six new arms, this week), and
`tests/closures.json` carried a 78-line diff through #1734 alone. Every
lane's shared-ledger list names it ("re-record once at the hand-off"): two
lanes re-recording *different* scripts produce a same-file conflict with no
textual overlap — the classic no-overlap conflict.

**Scope of `tests/closures/<script>.json`** (27 files): `closure.py` is the
real work (its aggregate `merge`/`partial` union logic and the `--single`
recording path — ~100-150 lines), plus one read-path line each in the other
eight consumers and the autofix job's write path. The one-time split is
mechanical but single-writer (principle 2), proven by `closure.py selftest`
plus one `--single` round-trip. **Verdict: feasible; real conflict win
(same-file conflicts survive only when two lanes re-record the *same*
script, which the lane discipline already prevents). Sequence with item 5
and BEFORE it — item 5's ~120 new closure files make the directory shape
the natural home, and splitting the consumers once beats rewriting them
twice.**

---

## 6. The sequenced endgame plan

Stage gates: **F1.11** (P2/P6 owners-registry) and **F10.4** (I5 barrier +
structure truth, tvofi-gated, the round's last production-side PR by its own
brief) land before anything below that touches coordinator/optimizer
structure or a predicate seam. The **register PR** and **branch prune** close
the round; the **inter-wave gap** (no lane branch open) is the window for
every move-type item.

| # | item | PRs | cost (measured) | risk | after |
|---|---|---|---|---|---|
| 0a | Roster resume sidecar (§7) | 1 | ~35 lines, gen.py + seed | near zero | any time; before F1.5 starts |
| 0b | Symbol-anchored pins (§6) | 1 | ~30 lines; kills the 19-pin line treadmill | low; rides F10.5's writer | after F10.4 (owns mutation_table), with/after F10.5 |
| EG-S1 | Surfaces PR 1: identity core + `merged_config` + `_data()` | 1 | ~net −60 lines; `climate.py:144` re-pin | registry-compat (naming pin) | lanes drained; #1668 fix already merged |
| EG-S2 | Surfaces PR 2: availability gate + unknown-vs-unavailable | 1 | ~net −27; keyed into F1.11's registry | canonical-rule design | after F1.11 |
| EG-3 | `_utc_step_starts` dedup (coordinator:553 / optimizer:198); fold lane-owned dup pairs into F1/F2/F5 instead | 1 (or 0, folded) | 2 defs + callers; golden-drift care | low | after F1.1 + F2.1 |
| EG-4 | Closures directory split (§8) | 1 | 9 consumers, ~150 lines + mechanical split; selftest + `--single` proof | medium (scoping engine) | inter-wave gap; before EG-5 |
| EG-5 | features.py package split (§5) | 1–2 | 112 files + runner; ~120-150 closures (CI autofix) | **highest move-PR risk** (8-of-8 file) | inter-wave gap, after EG-4; entities follow-on optional |
| EG-6 | optimizer split: `optimizer_dhw.py` (§3) | 1 | 30 pins re-key (cheap post-0b); `classes_over_300` +1 | medium; golden drift | after F2 drains + F10.4 |
| EG-7 | Coordinator seam moves: dhw then views (§2d) — **tvofi opt-in only** | 2 | 47 pins re-key (cheap post-0b); `classes_over_300` +1 per move; 16 closures | high (hub attributes, measured) | last: after F1 drains, F10.4, register, prune |

**Dependency spine**: 0a independent; 0b before EG-6/EG-7 (anchors survive
moves); F1.11 before EG-S2; F10.4 before EG-6/EG-7 (honest re-record rule);
EG-4 before EG-5 (consumers rewritten once); register PR + branch prune
before EG-5/EG-7 (moves want drained lanes and a landed register so evidence
citations don't shift under them).

**Total endgame size: 9–11 PRs** — 2 infra (0a, 0b), 2 surfaces (EG-S1/S2),
1 clock dedup (or folded), 2 corpus/closures moves (EG-4, EG-5), 1 optimizer
split, 0–2 coordinator seam moves on opt-in. Recorded declines by
measurement: coordinator 3–7-module split (§2), thermal_model /
config_flow / sensor splits (§3), error-path and price-read consolidation
(already canonical, §1c/§1d), state-read helper in core (no core sites,
§1e).
