# REPORT — D7-s1, audit round 11 (D7.M1 and D7.M7), updated after the ordered re-run

The re-run is done and `REPORT.json` is updated in place: 12 of the 18 ratchet rows are now recounted and the other six driven, ten prototypes are built and scored, and `golden.py`, `optimality.py` and `backtest.py` were run on the six-prototype tree. Coverage is M1 95 of 95 and M7 78 of 95, with 17 named `not_reached`. No `REPORT.md` was written; this message is that text.

- Tree: `/Users/timmalmstrom/hpo-orch/r10s6/r11/plant-export/audit-r11-baseline`, baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`
- Report directory: `/Users/timmalmstrom/hpo-orch/r10s6/r11/plant-export/audit-r11-baseline/dev/audit/rounds/round11/D7/s1/`
- `REPORT.json` (hand-validated against `finding.schema.json`; the venv has no `jsonschema`) and `findings/D7-s1-01.json` to `D7-s1-06.json` are in that directory.
- Box load1 ranged 16 to 350. Every number below is a static count or a deterministic score; suite wall figures are provisional.

## What the re-run changed

**1. The seven M1 rows read from `measure()` only.**
- Two are now recounted and agree at the baseline and under all 14 perturbation runs: `dead_top_level_symbols` (an independent resolver) and `coordinator_private_reach` (by receiver spelling, a weaker census than the ratchet's role engine).
- Five have no second census and were driven instead; each moved as its definition says:

| row | perturbation | reading |
|---|---|---|
| `coordinator_attrs` | a new attribute stored from two outside functions | 136 → 137 |
| `coordinator_multiassigned_attrs` | same | 104 → 105 |
| `name_kept_members` | two classes sharing a member name, one untyped load | 38 → 40 |
| `dead_methods` | ten dead probe methods | 0 → 10 |
| `seam_cut_total` | all 17 `dhw` units read as `views` | 415 → 393 |

- A true recount of those five needs a second role, receiver-type and seam-flow engine, which I did not build.
- One reading is left open: relabelling the single unit `_dhw_confidence_band` leaves `seam_cut_total` at 415. Whether one unit should move the row was not established.

**2. Prototypes for the remaining clone copies and layer violations.** Four more were built where a one-owner form exists:

| prototype | what | alone |
|---|---|---|
| `fdjac` | `sysid.py`: one `_fd_jacobian` for the two forward-difference Jacobians | +0.6964 |
| `entry` | `ledger.py`: one `_entry` lookup (the honest form on the class the `fold` game uses) | +0.6964 |
| `notice` | `legionella.py`: one `_interval_notice` for the two day-count notices | +0.6964 |
| `curr` | `currency.py`: its only Home Assistant import is one annotation; under `if TYPE_CHECKING:` `grid_fee` stops reaching the glue | +0.1069 |

- All ten prototypes combined: **dS +9.2671 IMPROVES, admissible** (`duplication_copies` 18 → 9, `layer_violations` 13 → 6), and +0.0000 when reverted.
- Against the guideline bar, which I read as +34.05 for a seat holding all 95 files (my interpretation), that is about a quarter. It is a review trigger and a list, not a target met.
- Named as needing a design, not built — six clone classes (9 copies):
  - `inputs.read` / `read_state`: one owner means inverting control around `_begin`.
  - `optimizer._optimize_space_only` / `_optimize_with_dhw` / `_solve_space`.
  - `optimizer` `objective` / `objective_batch`.
  - `tariff._smooth_topk_sum` / `_smooth_topk_sum_batch` / `peak_cost_batch`.
  - `thermal_model` step twins (`_simulate_step_single` / `_simulate_step_two_zone` / `simulate_trajectory_batch`).
  - `thermal_model` trajectory twins (`simulate_trajectory` / `simulate_trajectory_with_dhw`).
  - The last five are solver paths and scalar/batch twins; merging them changes float order and so the fixtures.
- Named as needing a design, not built — six layer violations:
  - `disinfection`, `price_model`, `quiet_windows` and `sysid` ride on `inputs.py`, which is glue by one function-scope clock import at line 984 that the suite freezes.
  - `setpoint_check` rides on `inputs` and on `issues.py`, which is real glue.
  - `snapshots` rides on `store.admitted`, whose domain table lives in the storage module.

**3. `golden.py`, `optimality.py`, `backtest.py` on the six-prototype tree.**
- `optimality.py`: 79 ok / 5 FAIL on both trees, identical lines, same exit code.
- `backtest.py`: 25 ok / 0 FAIL on both trees, identical.
- `golden.py`: its default drift mode needs a git ref and the export has none, so I ran it with `GOLDEN_MODE=strict`. It exits 1 on both trees and the two 430-line outputs are byte-identical. On the tree itself 56 of 56 scenarios read CHANGED against the committed fixtures (this machine's BLAS, the tree's own state, or both; not separated).

## Method

**M1.** `m1_ratchet_census.py` drives `tests/structure.py:measure`, prints one reading line per file (95), recounts 12 rows, adds the censuses the ratchet lacks, and runs 13 in-memory perturbation arms.

**M7.** Four harnesses:
- `m7_sites.py` lists every site behind every score metric by file: 56 files at their floor, 39 open.
- `m7_floor_plants.py` plants six defects in each of the 95 files and reads them back through the score's own censuses.
- `m7_layer_edges.py` names the import edge that carries each layer violation.
- `m7_prototypes.py` applies exact-text prototypes to a temp copy, scores them with every counter on, restores them, and compares the behaviour suite line by line against the tree's own output.

## Findings (all `low`)

| id | step | what | executed number | perturbation |
|---|---|---|---|---|
| D7-s1-01 | M1 | `const_modules_over_50` counts names on from-import statements, not names read. `entry_config.py` reads 118 const names and counts 3. | row reads 3; 4 modules are over the limit by distinct names read | re-spelling `thermal_model.py`'s from-import moves the row 3 → 2 with fan-out unchanged; the repair arm reads 4 |
| D7-s1-02 | M7 | Both clone censuses key a window by owning function, so a rule written twice in one function is not a copy. Stop class `bug`. | planted in-function copy unseen in 95 of 95 files; two-function control seen in 95 of 95. Folding two clone bodies verbatim under one `def` reads dS +0.6964 IMPROVES | keying the owner by place: holes 95 → 0, the fold's dS → +0.0000 |
| D7-s1-03 | M1 | No row counts a package import nothing uses. | 14 bound names in 6 modules are never loaded | a 15th moves 0 of 18 rows; the same import with one load stays at 14 |
| D7-s1-04 | M1 | No row holds `coordinator.py`'s size outside the class. | 11,414 lines; 7,877 class + 557 charged helpers are priced, 2,980 are not | 1,423 more lines of module functions move 0 rows; the same lines in a class move `class_excess_loc` by exactly 1,400 |
| D7-s1-05 | M7 | Eight of the 14 clone classes have a one-owner prototype the score admits. | `duplication_copies` 18 → 9, term +8.2671; leave-one-out (without `avail`) +5.9188 | every arm restored reads +0.0000 |
| D7-s1-06 | M7 | Seven pure modules reach Home Assistant through an import they do not need: `accuracy.py`'s re-exported helper and constant, and `currency.py`'s annotation. | `layer_violations` 13 → 6, term +1.0000; 11 of 13 violations ride on a single edge | `--cut accuracy` 13 → 7, `--cut currency` 12; null `--cut issues` stays 13 |

- **D7-s1-02 detail.** Today's tree already holds 6 in-function copies under the ratchet's window and 15 under the score's; none is priced.
- **D7-s1-03 detail.** No test reads 13 of the 14 through the importer; `tests/guard_pins.py:765` reads the fourteenth.

## Suite: unchanged, not passing

The tree's own suite is red, so "green" here means line for line unchanged.

- **Six-prototype tree.**
  - 16 scripts ran to the end on both trees with identical check lines (2,336 ok and 76 FAIL each side) and the same exit codes.
  - `features.py` was cut at 3,000 s; the 2,423 check lines each side had printed match position by position.
  - `golden.py`: as above, byte-identical.
- **Ten-prototype tree.**
  - 13 scripts identical (2,191 ok / 66 FAIL each side).
  - `boost_drift_replay.py` identical (41 / 5).
  - `features.py` ran to its end on both trees (2,945 ok / 131 FAIL each, same exit code). 3,075 of its 3,076 check lines are identical. The one other is the same FAIL check on both sides, whose message prints an elapsed-hours float: 216.00000012 against 216.00000020, 0.3 ms apart. I take that for a clock read; I did not confirm it with a second run of the same tree.

## Non-findings

- **Ratchet at budget.** `tests/structure.py` passes on the tree: 18 keys measured, 0 off budget.
- **Recount.** 12 rows agree in every arm.
- **Counters hold.** Dead-member, unused-public, C7, C17/C18 and C19 each see a plant in every one of the 95 files (0 holes; `reach` over 94).
- **Helper form refused.** The `note` dedupe spelled as a module function that mutates the list it is handed reads dS −6.4988 WORSENS (`shared_inplace_writes` 3 → 9).
- **`const.ENTITY_FAMILY_OVERRIDES` is not an opportunity.** Deleting it reads −6.6634 WORSENS (`family_splits` 0 → 2).
- **The one hub write is pinned.** `_apply_comfort_weight` at `coordinator.py:10941` is read 12 times in `tests/features.py` and once in `tests/entities.py`.
- **Module-level logic is small.** 81 decision points outside any function, at most 33 in one file (`store.py`).

## Not finished

- **M1.** The five driven rows have no independent recount (above).
- **M7, not prototyped and not in the re-run.** `hub_solve_writes` (1), `shared_inplace_writes` (3), `private_cross_module` (10; a rename is that metric's cheapest move and I did not count it), `params_over_10` (6), `literal_clone_copies` (118 in 43 classes).
- **M7, `not_reached` (17 files).** Fifteen hold only literal-clone, private-crossing or parameter-count sites; `inputs.py` and `thermal_model.py` hold clone classes that need a design.
- **M7, suite not run on a prototype tree.** `stress.py`, `validate.py`, `rolling.py`, `env_drift.py`, `typing_ruler.py`, the card scripts and the full `tests/run.sh`.
- **M7, not carried by the prototypes.** The `tests/seam_map.json` and budget re-records a real pull request would owe.

## Leads

All 14 are in `REPORT.json`; none was measured.

- **D7-s3 (M8), three clone classes that look like live disagreements:**
  - `pump_arbiter._planned_room` has no end-of-plan rule where `_step_index` has one; `early_cutoff._planned_room` is a third lookup.
  - The simulation twins in `thermal_model.py`: `tests/features.py` on the tree fails "batched simulation is bitwise-identical".
  - The top-k twins in `tariff.py`: `tests/features.py` on the tree fails "the peak charge equals the bill it models" (charged 0.00 against 114.00).
- **D7-s2:** `_apply_comfort_weight` edits `_opt_config` in place although `CoordinatorContext` documents publish-whole.
- **Unknown owner:**
  - `power_guard.project_window_mean` weights `current_kw` by `elapsed`; `remaining` is computed on the line above and never read.
  - `coordinator.py:9175` reads humidity through `InputReader(self.hass, {})`, without the entry's staleness settings.
  - The other eight are red lines the suite prints on the tree itself. `tests/features.py` run to its end prints 131 FAIL lines; `tests/entities.py` aborts at line 9634 with `KeyError 'house_heat_loss_coefficient'` after 32 FAIL lines.

## Exposure

`tools/audit/archscore/ABOUT.md` and the docstring of `tests/structure.py` cite earlier finding ids as context. I read no register, earlier round directory, `docs/` page or GitHub record. I opened the peer seat's `dev/audit/rounds/round11/D10/s1/REPORT.json` once for its JSON shape.

## One incident, already reported

At 20:11:12Z I overwrote the shared scratchpad's root `env.sh`, which D7-s3's scripts source. D7-s3 moved to its own copy two minutes later. I kept everything under `scratchpad/d7s1/` from then on, and the re-run wrote scratch only there.

## Harnesses

All in the report directory, each runnable by the command in its header:
- `m1_ratchet_census.py`
- `m7_sites.py`
- `m7_floor_plants.py`
- `m7_prototypes.py`
- `m7_layer_edges.py`