Box G3-V3, lens V3 (reach and class), dimension D9 (leads unit)
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, evidence commit 96b8916318513c3617254c3ce43b10570eb16307
Worktree /home/claude/ev2, machine: 4-vCPU Linux container (shared with other sub-seats), CPython 3.14 at /home/claude/venv/bin/python, PYTHONPATH=tests/hastub
Date 2026-09-26
CPU numbers on this box are PROVISIONAL: another sub-seat runs concurrently. thread_factor and
load1 are quoted beside every timing number below, and ratio metrics with a same-session null
control are preferred over raw seconds throughout.

=====================================================================
D9-s1-71 -- Constant DHW parameter helpers recomputed 15-45k times per
solve; a per-solve cache saves 3-17% of CPU
=====================================================================

Method: re-ran tools/audit/round9/D9/leads/l3_dhw_helpers.py, memo and --null arms, across all 5
golden DHW cells; also wrote and ran an independent microbenchmark
(tools/audit/round9/D9/verify-v3-leads/v3_dhw_helpers_microbench.py) that times the three helpers
directly (200k calls each) on a real ThermalParameters instance and multiplies by the finder's own
recorded (contention-immune) calls-per-solve, to get a call-count-anchored estimate independent of
timing the full solve twice.

Numbers (mine, load1 0.44-0.55, thread_factor 1.000 throughout):
  memo arm:  saved_share per cell: winter_single_dhw 0.2071, winter_two_zone_dhw 0.0035,
             summer_dhw_only -0.0324, dhw_cold_tank 0.0289, dhw_learned_windows 0.0850
             mean 0.0584, min -0.0324, max 0.2071, plans_identical=5 of 5
  null arm:  saved_share per cell: 0.0170 to -0.0724, mean -0.0018, min -0.0724, max 0.0524
  microbench: per-call cost ua=3.17e-6s, inlet=1.48e-7s, pattern=1.80e-5s; on winter_single_dhw
              (11090/33205/98 calls/solve, as recorded) this gives an upper-bound share of 0.1597
              of that cell's own solve_cpu (0.262s) -- independent confirmation, same order of
              magnitude as my full-solve rerun's 0.2071 for that cell.
  call counts (contention-immune, exact): 11090/33205/98 (winter_single_dhw), 8809/26364/98
              (winter_two_zone_dhw), 3989/11930/97 (summer_dhw_only), 10316/30879/98
              (dhw_cold_tank), 10426/31213/100 (dhw_learned_windows) -- exact match to the
              finder's recorded ranges (4k-11k, 12k-33k, ~98).

Attacks (verifier.md step 3):
- Contention: this box shows load1 0.44-0.88 across my runs (lighter than the finder's 1.79), so
  my CPU-share numbers are, if anything, LESS contended, not more -- the discrepancy from the
  finder's mean (0.0584 mine vs 0.094 theirs) is not explained by contention direction and should
  be read as genuine run-to-run variance in a fan-out CPU ratio metric on 0.4-8s solves.
  thread_factor=1.000 throughout both runs (single-threaded BLAS held), so it is not a multi-core
  fan-out artefact either.
- Null control: present and correctly designed (same wrapper layer, no cache). My null arm reads
  mean -0.0018, band -0.0724..+0.0524. Two of five memo-arm cells (winter_two_zone_dhw 0.0035,
  summer_dhw_only -0.0324) fall INSIDE this null band and are not distinguishable from noise on my
  run. The other three (winter_single_dhw 0.2071, dhw_cold_tank 0.0289, dhw_learned_windows 0.0850)
  sit outside it, and winter_single_dhw's effect is corroborated by the independent microbenchmark
  (0.1597 upper bound, same order of magnitude, computed a different way).
- Grid artefact: dropping the most favourable cell (winter_single_dhw) still leaves a mean of
  0.0212 (recomputed from my own numbers) -- small but not zero across the remaining four.
- Reachable in real Home Assistant: yes. `ThermalParameters.dhw_tank_heat_loss_coefficient`,
  `.dhw_inlet_reference` and `.effective_dhw_draw_pattern()` (thermal_model.py:632, 651, 748) are
  pure numeric properties/methods with no Home Assistant API surface at all, called from
  `HeatPumpOptimizer.optimize`'s DHW step simulation, which is the coordinator's real production
  solve path -- nothing here is reachable only through tests/hastub or FakeHass.
- Severity by consequence: the finder called this low, and I agree -- even the high end of my
  reproduction (0.21 on one cell) is a modest constant-factor CPU cost, not a correctness bug, and
  the mean effect across cells is weak-to-absent by my numbers.

Correction to the finder's seam_rule: it states "seams = ThermalParameters properties/methods
called from simulate_dhw_step and the DHW planners" and the harness counts calls only along that
one production solve path. I grepped all three symbol names across every module:
`dhw_tank_heat_loss_coefficient` also appears at battery.py:325 and coordinator.py:2718,2649
(inlet)/2691(pattern)/6833, and `optimizer.py` alone has eight further call sites
(3384, 3403, 4189, 4383, 4568, 4684, 5152, 5391, 5579-5580, 5813) outside the harness's own DHW
step path -- sizing helpers, disinfection/legionella cost estimates, and other planners each call
these same "constant within a solve" properties independently, and the harness's call counts do
not include any of them. The seam_rule as stated names its scope narrowly ("simulate_dhw_step and
the DHW planners") and the harness measures exactly that scope, so it is internally consistent,
but it does NOT enumerate the full set of consumers this class of constant-recomputation affects
in the module -- it demonstrates one production path among at least three others.
seam_rule_enumerates: false (it enumerates its own stated, narrower scope, not the phenomenon's
full seam set across the module).

Class: class_guess "new" -- I checked tools/audit/bugclasses.json (P1-P11, I1-I5) and none of the
17 classes covers "a value constant within one solve recomputed on every simulated step/call
instead of hoisted once" -- P3 (capacity floor/divisor inconsistency) and P10 (a solve on a
GIL-holding thread starves the event loop) are the closest by subject (D9/CPU) but neither
mechanism matches (no divisor inconsistency, no starvation claim here, purely wasted recomputation
of solve-invariant scalars/lists). Confirmed as new, no existing class fits.

Metric definition (mine, same as the finder's): 1 - (thread CPU of golden.capture with the three
helpers memoised per ThermalParameters instance / plain), interleaved, per DHW cell; independently
cross-checked via per-call microbenchmark cost x recorded calls-per-solve / solve_cpu.

Vote: weaken. Severity: low (unchanged from the finder's own call). Value: 0.058 (my mean saved
share across 5 cells, vs the finder's 0.094) -- the mechanism, call counts and null-control design
are all confirmed and real, but on this run the aggregate magnitude is smaller than claimed and
2 of 5 cells do not clear the null-noise band, so I record the smaller number rather than the
finder's.

=====================================================================
D9-s2-71 -- stress.py samples 0 of 51 throttling-valve plants; a valve
adds 1.3-2.7x solve CPU the gate never sees
=====================================================================

Method: re-ran tools/audit/round9/D9/leads/l3_valve_solve.py, baseline and --perturb novalve arms;
also wrote an independent axis-coverage check
(tools/audit/round9/D9/verify-v3-leads/v3_stress_axis_coverage.py) that walks
stress.sweep_combinations() itself (using the same sentinel-before-solve trick, so it costs
nothing to run) and records BOTH mixing_valve_mode and topology_layout per case, rather than only
mixing_valve_mode as the finder's harness does.

Numbers (mine):
  RESULT stress_sweep_valve_cases=0 of 51 -- exact match, reproduced identically on both runs
    (load1 0.68 and 0.72, but this is a contention-immune count, not a timing number).
  Per-cell CPU (baseline arm, load1=0.68): valve_storage 6.04s, valve_storage_smart_write 12.23s,
    valve_upper_direct_slab 5.48s, wood_two_tank 7.09s; controls winter_two_zone_no_dhw 3.69s,
    shoulder_two_zone 3.11s.
  Per-cell CPU (novalve arm, load1=0.72): valve_storage 4.26s, valve_storage_smart_write 4.18s,
    valve_upper_direct_slab 4.22s, wood_two_tank 4.67s; controls 3.64s, 3.06s (essentially
    unchanged, +/-1.5%).
  My own valve/no-valve ratio per cell (baseline/novalve, same cell): valve_storage 1.42x,
    valve_storage_smart_write 2.93x, valve_upper_direct_slab 1.30x, wood_two_tank 1.52x --
    controls 1.01x, 1.02x. step_equivalents for the controls are EXACT and unchanged across both
    runs (winter_two_zone_no_dhw 4219488, shoulder_two_zone 3507029 in both arms), confirming the
    perturbation touches only the valve cells.

Attacks (verifier.md step 3):
- Contention: the exact count (0 of 51) is unaffected by load; the CPU ratios are provisional --
  my range (1.30x-2.93x) brackets the finder's claimed 1.30x-2.70x closely, with one cell
  (smart_write) running slightly hotter on my box (2.93x vs their 2.70x), consistent with normal
  fan-out variance under a similar shared-box load (load1 0.68-0.72 mine vs the finder's 1.83).
- Null control: present and correct -- the two non-valve controls move by only ~1-2% under the
  same perturbation machinery, versus 30-193% on the valve cells; this is the discriminator the
  finding needs and it holds on my re-run.
- Grid artefact: this is a coverage count over the full 51-case sweep, not an aggregate that could
  hide behind a favourable cell; 0 of 51 is exact and I verified it iterates `sweep_combinations()`
  to completion (`assert seen == len(combos)` in the harness, which passed silently both times).
- Reachable in real Home Assistant: yes, and this is the crux of the finding. `mixing_valve_mode`
  is a real, user-facing config_flow field (config_flow.py:1625,
  `_F("building", CONF_MIXING_VALVE_MODE, mixing_valve.MODE_NONE,
  _select(list(mixing_valve.SELECTABLE_MODES), 'mixing_valve_mode'), group="valve")`), not a
  test-only construct, and `mixing_valve.is_throttling` is read directly off that same field by
  the production `ThermalParameters` the solve builds. So a real installation with a manual or
  smart-write valve runs the exact under-sampled kernel path in production every optimize() cycle.
  Nothing here touches Home Assistant's own API, so ha_contract.py's stub/real divergence table is
  not implicated -- the gap is a Home Assistant-independent, but production-code-real, coverage
  hole in the CI gate.
- Severity by consequence: I'd keep this at medium, as the finder gave. The consequence is not a
  live production bug today, it is that a future regression confined to the valve branches of
  `_simulate_step_two_zone`/`simulate_trajectory_batch` (a real, user-reachable, 1.3-2.9x-CPU code
  path on a Raspberry-Pi-class target, per D9's stated dimension) could ship and pass the only
  per-PR CPU gate undetected. That is a real but latent risk, appropriately medium rather than high
  until an actual regression is shown to have shipped through this hole.

seam_rule (mine, run against the finder's stated scope: "topology axes = const TOPOLOGY_* and
mixing_valve modes; count sweep cases per axis value"): I found this to be UNDER-INCLUSIVE of its
own stated scope. The harness (`l3_valve_solve.py`) counts only `mixing_valve_mode` via
`mixing_valve.is_throttling`; it never varies or counts `topology_layout`
(`CONF_TOPOLOGY_LAYOUT`/the five `TOPOLOGY_*` constants in const.py: `TOPOLOGY_NO_VALVE`,
`TOPOLOGY_SINGLE_TANK_VALVE`, `TOPOLOGY_TWO_TANK_4WAY`, `TOPOLOGY_VALVE_UPPER_DIRECT_SLAB`,
`TOPOLOGY_SLAB_SHUNT`), and I confirmed by grep that `tests/stress.py` never mentions
`topology_layout` or any `TOPOLOGY_*` constant at all -- every one of the 51 sweep cases runs on
whatever `build_case`'s default topology is, on top of also never throttling. My independent
`v3_stress_axis_coverage.py` confirms this directly (n_cases=51, seen=51):
`mixing_valve_mode values seen across the sweep = ['none']`,
`topology_layout values seen across the sweep = ['no_valve']` -- BOTH axes are pinned to a single
value across the entire 51-case sweep, not merely under-sampled. So the true gap the
finding's own seam_rule names is at least two axes wide (mixing-valve-mode AND topology-layout),
and the harness measures and reports only one of them. Separately, I confirmed `golden.py` (the
fixture set used for the CPU-ratio demonstration, not the coverage count) never exercises
`mixing_valve_mode="smart_read"` either -- only `manual` and `smart_write` appear -- so even the
demonstrated-cost side of the finding has an unexamined third throttling mode.
seam_rule_enumerates: false (the mixing-valve axis itself is fully and correctly enumerated across
all three throttling modes by `is_throttling`, but the rule names "topology axes" plural and the
harness only measures one of the (at least) two axes it names).

Class: class_guess "I1" (mutation kill miscounted, or a guard whose deletion leaves the gate
green) does NOT fit -- I1's mechanism is specifically about mutation testing and gate defeat via a
deletable guard; this finding has no mutation and no guard being deleted, it is a parameter-space
coverage hole in a hand-written combinatorial sweep (`sweep_combinations()`never crossing
mixing_valve_mode or topology_layout as an axis). I checked all 17 classes in bugclasses.json; none
covers "a CI budget/coverage sweep omits a real config axis that changes the kernel." I correct
class_guess to "new: sweep coverage gap (a config axis absent from a combinatorial CI sweep, not a
guard or a mutation)."

Metric definition (mine, same as the finder's): count of tests/stress.py sweep_combinations()
cases whose built ThermalParameters throttle (mixing_valve.is_throttling), of 51; plus per golden
valve-plant optimize() thread CPU with the valve vs the same plant with mixing_valve_mode="none".

Vote: verify. Severity: medium. Value: 0 of 51 (exact); CPU ratio 1.30x-2.93x on my re-run
(finder: 1.30x-2.70x, provisional on both sides).
