# Class sweep — "structure metric blind to a code shape"

Not in `tools/audit/bugclasses.json` (new class this round).

Round-9 finding: **D7-s1-01** (verified, low — `tests/structure.py`'s structural ratchet cannot
see coordinator state reached through a module-level `_helper(self, ...)` call — the exact shape
`docs/HANDOVER.md` records as refused. Splitting a method out to a module-level helper that takes
`self` lowers `coordinator_loc`/`coordinator_methods` (rewarded) while raising
`cross_seam_edges`/`cut_grid`/`cut_learning`/`internal_call_edges` if it is ever inlined back
(refused), even though nothing about the code's behaviour changed either way).

## Enumerator

`tools/audit/round9/D14/sweep/structure-metric-blind-to-shape/enumerate.sh` reuses the finder's
own harness verbatim (`tools/audit/round9/D7/s1/helper_escape.py --all`), whose leave-one-out grid
already covers every one of the 11 module-level `f(self, ...)` helpers the coordinator calls —
it IS the class enumerator, not merely the finder's own positive control.

Positive control: re-running reproduces `helpers=11`, `helper_state_refs=30`,
`helper_coord_method_calls=8`, `grid_cells=10`, `grid_cut_delta_sum=36`, `grid_cut_delta_max=12`,
`grid_cells_nonzero=8`, and the headline `inline__fold_flow_lift_cut_delta=8` (`rows_up=4`) —
exact matches to the finding's own `Expected` line.
Null control: the transformed-vs-untransformed diff excludes `coordinator_loc`/
`coordinator_methods` by construction (an inlined method legitimately costs those, so the harness
does not count them as blind-spot evidence).
Perturbation: `--helper _warm_seeded` (a helper whose references cross no seam) gives
`cut_delta=0` — the harness's own built-in null arm, reproduced in the `--all` grid below as one
of the two zero cells.

## Disposition

| seam (module-level `f(self, ...)` helper) | `cut_delta` | disposition | note |
|---|---|---|---|
| `_republish_handover_ages` | 12 | **instance** | Nonzero — inlining raises a ratchet metric the class's own shape does not deserve. |
| `_fold_flow_lift` | 8 | **instance** | The finding's own headline cell (`rows_up=4`: `cross_seam_edges`, `cut_grid`, `cut_learning`, `internal_call_edges` all rise). |
| `_diagnose_payload` | 5 | **instance** | Nonzero. |
| `_power_windows` | 3 | **instance** | Nonzero. |
| `_watch_lift` | 3 | **instance** | Nonzero. |
| `_cop_fold_blocked` | 2 | **instance** | Nonzero. |
| `_freq_fold_blocked` | 2 | **instance** | Nonzero. |
| `_store_diagnosis` | 1 | **instance** | Nonzero. |
| `_space_pump_to_drive` | 0 | **guarded** | `cut_delta=0` — this helper's references cross no seam the ratchet misses; not blind here. |
| `_warm_seeded` | 0 | **guarded** | `cut_delta=0` — the harness's own documented null arm. |
| `wood_fuel.py:wood_fuel_from_coordinator` | (not in the 10-cell grid; listed among the 11 `helpers` but outside `coordinator.py`) | **not applicable** | Outside the coordinator-inlining transform the grid measures (a different module); the seam list shows it as a sibling `f(self, ...)` call for completeness, not a disposed grid cell. |

## Count

N = 1 verified finding (D7-s1-01, covering all 8 nonzero-`cut_delta` helpers as one mechanism —
the ratchet's blind spot, not 8 separate findings) + 0 additional sweep-confirmed instances
beyond the finder's own 10-cell grid. **rca = false** (N=1 < 3, not a ledger class, not
barriered) — matches the class table's precomputed N=1/rca=no.

## Barrier proposal

Extend `tests/structure.py`'s counting rule to resolve a module-level function's first `self`-like
parameter back to the class whose instance it binds, and count its body's state references and
internal calls against that class's own metrics — closing the exact blind spot this harness
demonstrates. Estimated gate cost: the existing `structure.py` run, plus one extra name-resolution
pass over module-level functions (no HA boot, pure AST).
