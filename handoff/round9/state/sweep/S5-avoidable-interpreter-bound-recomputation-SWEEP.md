# S5 class sweep: avoidable interpreter-bound recomputation in the solve

New class (round 9), `rca: true`, `n: 4` in the judge's table: D9-s1-01, D9-s1-02, D9-s1-04,
D9-s1-71.

## Enumerator

New harness, `enumerate.py` beside this file (no prior D14 detector existed for this class). Three
parts, all executed this session:

1. **Static call-graph reachability**: an AST walk of `optimizer.py`, rooted at
   `HeatPumpOptimizer.optimize`, `_scoped_minimize`, `_multi_start_minimize`,
   `_comfort_terms_batch`, `_batch_fd_gradient`, `_apply_dhw_min_run` (the objective/gradient/
   repair entry points scipy or the repair loop re-enters many times per solve), following
   `self.<name>(...)` and bare-name call edges.
2. **Static loop scan**: every `for ... in range(...)` inside a function reachable from those
   roots.
3. **Dynamic call-count profiling**: one production solve (`stress.build_case(season="winter",
   two_zone=True, dhw=True, tariff=True, hours=24)`, 96 steps) run under `sys.setprofile`,
   counting calls per (module, qualname) -- this both confirms which statically-reachable loops
   are actually hot, and widens the class to `ThermalParameters` properties/methods recomputed
   with no per-instance cache (the D9-s1-71 shape), not only the three named there.

Command: `PYTHONPATH=tests/hastub python3 tools/audit/round9/D14/sweep/avoidable-interpreter-bound-recomputation/enumerate.py [--json] [--fixture] [--reintroduce]`

## Controls (this session)

- **Baseline**: `recompute_seams=49`, `recompute_instances=15`, `recompute_guarded=0`,
  `recompute_not_applicable=34`. Full listing in `seams.json` beside this file.
- **Null control** (`--fixture`, a stub with no package to walk): `recompute_seams=0`.
- **Perturbation** (`--reintroduce`, a synthetic marker seam appended after the real enumeration
  to prove the counter moves): `recompute_seams` 49 -> 50, `recompute_instances` 15 -> 16. This is
  a weak perturbation (see Unfinished) -- it proves the counting and disposition logic reacts, not
  that a genuine one-line change in production code would be caught; a stronger perturbation would
  literally undo one of the confirmed caches/vectorisations and show the count fall, which needs a
  cache to exist first (this class's whole finding is that none does yet).

## Disposition

15 seams disposed `instance` (full data in `seams.json`); grouped by mechanism:

- **Per-row Python loops in the objective's hot path** (3, the D9-s1-01/02/04 shape):
  `HeatPumpOptimizer._comfort_terms_batch` (two loop bodies, lines 1889 and 1915, 453 calls in
  this one profiled solve), `cycling_penalty_batch` (453 calls), `HeatPumpOptimizer._clamp_dhw_to_capacity`
  (5 calls, the DHW min-run repair's shape). All four are called far more than once per solve
  (once per L-BFGS-B iterate or per repair round), confirming the "not once-per-solve" boundary
  that separates this class from ordinary setup/teardown loops.
- **Uncached `ThermalParameters` recomputation** (11, widening D9-s1-71's three named helpers to
  every property/method on the class that this profiled solve actually calls more than once per
  simulated step): `lower_floor_heat_loss_learned` (176354 calls -- an order of magnitude above
  D9-s1-71's own "15-45k" estimate, because this profiled scenario is two-zone+DHW rather than
  the finder's cell mix), `buffer_tank_heat_loss_coefficient` (88224), `buffer_tank_thermal_mass`
  (45096), `dhw_inlet_reference` (16747), `dhw_tank_thermal_mass` (11185), `dhw_hard_max_temp`
  (5594 -- new, not named by D9-s1-71), `dhw_tank_heat_loss_coefficient` (5594),
  `dhw_windows_active` (98, new), `effective_dhw_draw_pattern` (97), `topology_layout` (100, new)
  and `two_tank_modelled` (100, new). The last two are cheap boolean derivations (an `is not None`
  / equality check against already-loaded fields), so their CPU share is negligible even at 100
  calls -- disposed `instance` on the class's literal shape (recomputed, no cache) but flagged
  **low severity within this class**, distinct from the mass/heat-loss/draw-pattern properties
  which do real arithmetic (volume x density x specific heat, a table lookup, or a schedule scan)
  on every call.
- **34 not applicable**: every other statically-reachable loop is called O(1) times per solve in
  the profiled scenario (setup, one-shot repair passes bounded by `_SAFETY_REPAIR_ROUNDS`, or
  post-solve narrative/reporting code that runs once after the schedule is fixed) -- listed with
  their profiled call count in `seams.json`.
- **0 guarded**: no seam in this class currently has a cache or a vectorised twin already in
  place; that absence is the finding.

## Count and RCA

N = 4 verified findings (D9-s1-01, -02, -04, -71) + 8 additional sweep-confirmed instances beyond
those four (`cycling_penalty_batch`, `dhw_hard_max_temp`, `dhw_windows_active`, `topology_layout`,
`two_tank_modelled`, plus the 3 extra hot ThermalParameters properties not individually named by
D9-s1-71: `buffer_tank_thermal_mass`, `buffer_tank_heat_loss_coefficient`, `lower_floor_heat_loss_learned`,
`dhw_inlet_reference`, `dhw_tank_thermal_mass`, `dhw_tank_heat_loss_coefficient` are the same
mechanism D9-s1-71 already generalised over "the three ThermalParameters helpers", so are folded
into that one finding rather than counted as separate instances) = conservatively **5 confirmed
class members** (D9-s1-01, -02, -04, -71-as-one, plus `cycling_penalty_batch` as a second
independent per-row-loop instance in the objective). **rca: true** (N >= 3, matches the brief's
table).

## Barrier proposal

A nightly (not gate) ratchet: `enumerate.py`'s dynamic call-count profiling asserting
`recompute_instances` may only fall, run once per release against the same profiled scenario.
Cost: ~18s wall this session (dominated by the one profiled solve under `sys.setprofile`, which
itself roughly doubles solve wall time) -- too slow for the per-PR gate, matches the class's own
mechanism (CPU cost) with the CPU-gate-blind class below.

## Unfinished / exposure

- The reachability BFS and loop scan cover `optimizer.py` only; `thermal_model.py`'s own internal
  loops (inside `simulate_trajectory_batch`, `simulate_dhw_step`) were not statically scanned for
  new per-row Python loops, only profiled by call count through the `ThermalParameters` properties
  they read. A wider static pass over `thermal_model.py` is unfinished.
- The reintroduce perturbation is synthetic (an appended marker), not a genuine one-line
  production edit, because a real regression-inducing edit here would require un-vectorising
  `_comfort_terms_batch`'s numpy twin, which does not exist yet in production (that is the fix
  this class is waiting on). Once a fixer lands a cache or a vectorised twin for any of the 15
  instances, `--reintroduce` should be replaced with reverting that specific fix and showing the
  count return to its pre-fix value.
- Profiled against one scenario (winter, two-zone, DHW, tariff, 24h). Call counts for
  single-zone or no-DHW scenarios were not profiled and may disposition some seams differently
  (e.g. DHW-only properties would show 0 calls, correctly `not applicable`, in a no-DHW cell).
