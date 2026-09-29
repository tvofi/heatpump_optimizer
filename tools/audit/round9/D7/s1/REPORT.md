# D7-s1 — round 9, dimension D7 (architecture and maintainability), steps M1 and M5

Baseline `1936d5ca72a06556eeed4e8e5bf3dea520e517e1`, export `/home/claude/audit-r9-baseline`,
cloud container (linux x86_64, box B6, shared with other finders; load1 1.9–6.2 during the fan-out).
Every number here is a count; nothing is a timing.

## Method

**M1 (metrics).** Ran `tests/structure.py` (all 25 budget rows `ok`, `STRUCTURE RATCHET PASSED`,
values identical to `tests/structure_budgets.json`). Did not re-derive the metrics. Read how the seam
metrics find coordinator state (`state_root_bindings`, `is_state_root`: `self`, `self._ctx`,
`getattr(self, "_ctx", self)` and locals bound to them), then measured what they cannot see: coordinator
state reached through a module-level helper the class calls as `f(self, ...)`. Harness
`helper_escape.py` copies the package + `tests/seam_map.json` to a temp root, moves one such helper
byte-for-byte into the class (param renamed to `self`, calls rewritten to `self.f(...)`), and calls the
production `structure.measure()` on both copies.

**M5 (this year's train).** `train_mutations.py` makes one deletion-shaped spot mutant per train item in a
temp copy of the tree, and drives the runnable recorded drivers whose closure reaches the file (instruments:
the scripts that import them), cheapest first, scoring with the project's own
`tests/mutation_table.py:killed` (plus, for a driver already red in this git-less export, a failing check
name the baseline did not print). Production survivors are then put through an `env_drift.py --capture
... --all` comparison of baseline vs mutant (the CI drift gate's behavioural comparison, emulated because
the export has no `.git`). Null control: a comment-only edit to `optimizer.py` survives all 15 drivers.
`train_docs.py` counts user-facing doc files with a paragraph on each item and the modules that define it.

## Findings

### D7-s1-01 — the structural ratchet does not price coordinator state reached through `_helper(self, ...)`, so it rewards that move and refuses its reversal (M1)

`docs/HANDOVER.md` records `_helper(self, ...)` as refused ("it erases moved references at zero cost, a
measurement artefact, not a decomposition"), and `structure.py:state_root_bindings`'s docstring says the
same. The ratchet itself does not enforce it: `seam_metrics` only counts attribute references rooted at
`self`/`_ctx`, so a module-level function taking the coordinator as a parameter is invisible to every cut
and edge metric.

- `RESULT helpers=11` module-level functions are called by `HeatPumpOptimizerCoordinator` with `self` as an
  argument (10 in `coordinator.py`, plus `wood_fuel.wood_fuel_from_coordinator`); their bodies make
  `helper_state_refs=30` coordinator-state references and `helper_coord_method_calls=8` coordinator-method
  calls that no structure.py metric counts.
- Inlining `_fold_flow_lift` back into the class (identical behaviour) moves `cross_seam_edges` 136→138,
  `cut_learning` 285→290, `cut_grid` 197→198, `internal_call_edges` 317→321:
  `inline__fold_flow_lift_rows_up=4`, `cut_delta=8`. Each of those rows is at zero headroom, so
  `structure.py` exits 1 on the move that undoes the refused shape.
- Leave-one-out over the 10 coordinator.py helpers: `cut_delta` sum 36, min 0, max 12
  (`_republish_handover_ages`), 24 with the most favourable cell dropped, 8 of 10 cells non-zero.
- `_fold_flow_lift`'s own docstring gives the reason it is module-level: "a method here would cost
  `coordinator_methods` and a seam edge".
- Perturbation: `--helper _warm_seeded` (a helper whose one state reference stays inside its seam):
  `cut_delta` 8 → 0.

Fix scope: `structure.py:seam_metrics`/`state_root_bindings` treat a parameter that the coordinator
passes `self` into as a state root (and charge the call as an edge), with a `self_check` pin.

### D7-s1-02 — the drift gate's comparison and the stress gate's per-scenario budget verdict are deletable with every runnable check green (M5)

Two train items are verdict branches written inline in a script's `main` rather than in a function a check
drives:

| mutant | site | verdict |
|---|---|---|
| `drift` | `tests/env_drift.py` main loop: `_diff_leaves(baseline[name], branch[name], name, diffs)` → `pass` | **survived** entities.py, features.py |
| `stress` | `tests/stress.py` per-scenario budget: `if ratio > allowed:` → `if False:` | **survived** entities.py, features.py |
| `drift_leaf` (control) | the same comparison one frame down, in `_diff_leaves` (`elif a != b:` → `elif False:`) | killed by entities.py ("and every one of those moves is still counted for the nightly") |
| `drift_ctl` (control) | `env_drift._looks_like_version` → `return False` | killed by entities.py |

`RESULT survivors=2` (`--only drift_leaf,drift,stress`). With the `drift` mutant every CI run of
`env_drift.py --all <ref>` prints `ok` for every scenario whatever the branch did to the plan, and the
drift gate is the only behavioural comparison a scoped pull request always runs; with the `stress` mutant
no scenario can go over its recorded budget. Neither `env_drift.py` nor `stress.py` could be driven here
(both need a git ref; the export has none) — but a mutant *in the gate* makes the gate's own run on an
unchanged production tree green by construction, so its self-run cannot kill it either. Perturbation:
move the same deletion into the helper (`drift_leaf`) → killed; survivors 2 → 1 for the pair
drift/drift_leaf.

Fix scope: lift the per-scenario comparison loop of `env_drift.main` and the budget verdict of
`stress.py` into functions and pin each with a check in entities.py (the pattern `_diff_leaves` and
`scenario_budget` already follow).

## Non-findings (M5 table)

| item | mutant | verdict (killer) | user-facing docs | owner modules |
|---|---|---|---|---|
| null control | comment line in optimizer.py | survived all 15 drivers | — | — |
| batched gradient | `can_batch = False` | see unfinished (survived guard_pins, doc_claims, finite_boundary, config_flow_steps, entities) | 0 | optimizer.py, thermal_model.py |
| bounds gate | `if lo > hi` → `if False` | killed, features.py ("degenerate classes are still refused") | 0 | optimizer.py |
| drift gate | see D7-s1-02 | survived | — | tests/env_drift.py |
| scoped gate | `closure.select` hits → `[]` | killed, entities.py | — | tests/closure.py |
| card collaborators | `HistorySource.leftBound` → `null` | killed, card.mjs | 0 outside the plan doc | the card .js |
| stress budgets | see D7-s1-02 | survived | — | tests/stress.py |
| weekly windows | `dhw_weekly_windows = None` | killed, features.py | 4 | dhw_schedule.py |
| topology catalogue | drop `selectable=False` on slab_shunt | survived 11 drivers; killed by the env_drift capture (5 coord scenarios moved) | 3 | topology.py |
| wood variant | `usable = 0.0` in the valve law | killed, features.py | 5 | wood_fuel.py (+ law in thermal_model.py) |
| coil variant | `dhw_coil_active` → False | killed, guard_pins.py | 4 | thermal_model.py |
| DHW confidence | band always None | killed, doc_claims.py | 1 | coordinator.py |
| Tuya | drop the tuya_heat_pump source | killed, config_flow_steps.py | 1 | device_prefill.py |
| re-anchor law | `phi = 1.0` | killed, features.py | 0 | coordinator.py |

The zero-doc items (batched gradient, bounds gate, re-anchor law, card collaborators) are internal
mechanisms documented in code comments/plan docs; not a finding (no user-visible behaviour to describe).

## Harnesses

- `tools/audit/round9/D7/s1/helper_escape.py` — root rule: `Path.cwd()` (run from the export root).
- `tools/audit/round9/D7/s1/train_mutations.py` — root rule: `Path.cwd()`; copies the tree (skipping this
  round's `round9/D*` seat directories, keeping the earlier-round fixtures `entities.py` opens).
- `tools/audit/round9/D7/s1/train_docs.py` — root rule: `Path.cwd()`.

## Could not finish

- M5 `batch`: its features.py run on the scalar-FD path was still running at report time; verdict open.
- `stress.py`, `env_drift.py`, `golden.py`, `deployment_shape.py` could not be driven as mutation drivers
  (need `.git`).

## Exposure / notes

- An early M5 run copied the tree without `tools/audit/round3..7-fix`; `entities.py` then crashed at
  `:16606` opening `tools/audit/round4/D6/claims.json`. Those verdicts were discarded and re-run with the
  fixtures present. I did not read any earlier-round evidence file; the copy only carried them as inputs
  `entities.py` opens.
- `entities.py` is red in the export (13 failing checks, git/HANDOVER-dependent); kills through it are
  counted only on a failing check name its baseline did not print.
