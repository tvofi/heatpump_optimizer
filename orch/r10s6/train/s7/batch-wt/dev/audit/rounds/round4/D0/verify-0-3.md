# D0 verification — seat 3 of 3 (re-run seat)

- **Worktree**: `.claude/../audit-r4-verify-D0-3`, detached at `3e91f85`
  (branch head). `git diff 7dd68dd..3e91f85 -- optimizer.py tests/profiles.py
  tests/optimality.py tests/stress.py` is empty, so the branch head *is* the
  baseline for every file the D0 harnesses hook; numbers measured here are
  numbers of the baseline code.
- **Interpreter**: `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`,
  `PYTHONPATH=tests/hastub`, always from the worktree root. The round-4
  harnesses live inside the tree under test (no evidence-tag copy needed);
  `d0lib.py` resolves imports from `os.getcwd()`, so they measured MY worktree.
- **Contention**: box shared with verifier 2 (its `ftol_gap.py` and
  `budget_knobs.py` were running in `audit-r4-verify-D0-2` for part of the
  window). `load1` at end of runs: 14.91 / 16.83 / 8.8 / 9.7 / 7.48 / 6.95;
  `thread_factor` 1.0000–1.0001 everywhere. No metric below is a wall, CPU or
  RSS number — all are objective values, ratios of objective values, iteration
  counts or gate pass/fail — so none is contention-provisional. No timing
  refute is claimed or needed.
- **Not done**: `tools/audit/round4/D0/verify-0-1.md`, `d0_own_*.py`,
  `outer_bound.verify-0-1.out` and the register's verdict columns were present
  in the tree and were NOT read.

## D0-01 — ftol=1e-6 halts the solve with descent remaining (`low`, bug)

### Re-run of the finder's harness

`tools/audit/round4/D0/ftol_gap.py` (80 cells) — **every RESULT identical to
the committed `ftol_gap.out`, and all 80 per-cell `CELL` lines byte-identical**
(diff empty):

```
mean_gap_priced_pct   0.117642 %   max 0.799815 %   loo 0.107755 %
mean_gap_flat_pct     0.104822 %   max 0.554255 %            (null control)
cells_gap_above_0p01pct        34  (of 70 priced)
cells_negative_gap             0
cells_challenger_worse_comfort 0  (of 80)
max_step0_delta_kW       4.05621   (9 priced cells differ > 0.01 kW)
lbfgsb_solves_observed       420   maxiter_binding_solves 0
```

`tools/audit/round4/D0/mpc_realised.py` (closed-loop day) — every RESULT
identical to the committed `mpc_realised.out`:

```
mean_realised_delta_priced_SEK_per_day   +0.320965   (0.563 % of a 57.02 bill)
cells_production_cheaper                 4 of 8 priced
mean_realised_delta_flat_SEK_per_day     -2.11318    (null control, wrong way)
cells_challenger_worse_comfort           1 of 10 (0.0016 degree-steps)
```

The finder's refusal of the money claim is reproduced to the last digit: the
priced mean saving (+0.32 SEK/day) is smaller than the flat-price null moving
the opposite way (−2.11 SEK/day), so no saving is claimed.

### My own harness (`own_v3_D0_01.py`)

Written from scratch: own cell builder (profiles **tiled** to the horizon,
which `d0lib.build_cell`'s truncation cannot do for 48 h), own grid on axes
the finder never ran — horizons 6 h and 48 h, DHW-off cells, single-zone 48 h,
warm-weather 48 h — and a second, independent metric: a **polish arm** that
replaces `_lbfgsb_restart` with a replica of itself at `ftol` 1e-14 adopting
any strict improvement, i.e. plain continued descent from production's own
stopping point (no new seed, no re-solve of the multi-start).

```
ftol arm, my grid (13 priced cells):  mean 0.076 %  max 0.451 %  LOO 0.047 %
                                     0 negative gaps, 0 worse-comfort cells
ftol arm, flat null (5 cells):       mean 0.217 %  max 0.531 %
polish arm, priced:                  mean 0.047 %  max 0.511 %
polish arm, flat:                    mean 0.165 %  max 0.603 %
wiring: both arms forced tight -> identical J (gap exactly 0), 1 of 1;
        challenger loosened to 1e-4 -> never better, 4 of 4 cells
```

The gap reproduces on horizons, topologies and DHW settings the finder did
not cover, at the same order of magnitude; and the polish arm confirms the
core claim by a different instrument — production's own returned point still
admits up to 0.51 % (priced) / 0.60 % (flat) of descent under the production
objective. The shipped plan is not a minimum of its own objective.

(Grid note, mine not the finder's: the two `summer_warm` 48 h cells are
degenerate — J≈63120, gap 0 — an artefact of tiling two warm days; they add
two zeros to the flat/priced means and nothing else.)

### Attacks, in the contract's order

1. **Contention** — nothing timed; see header. Not a refute path.
2. **Wrong gate mode** — n/a; D0-01 makes no suite-gap claim. (The gate-mode
   attack on the *perturbation* was run anyway as the wiring check: forcing
   ftol 1e-14 on both arms collapses the gap to exactly 0; 1e-4 never beats
   production — the metric moves in the stated direction.)
3. **Aggregate artefact** — the finder's LOO drops 0.118→0.108; six of eight
   price profiles sit above 0.045 % mean; my disjoint-axis grid lands at
   0.076 % mean / 0.451 % max. Not one cell's work.
4. **Null control** — present and honest. The flat gap does NOT vanish
   (finder 0.105 %, mine 0.217 %), and the finder draws exactly the
   conclusion the D0 brief demands: named as premature termination of the
   local solve, money claim withdrawn when the MPC flat null moved the wrong
   way. In-dimension: the brief's three homes of sub-optimality include
   "the budget (iterations, function evaluations, **tolerance**)".
5. **Reachability** — real-HA path confirmed:
   `coordinator.py:992–1003` → `optimize_in_process` (`optimizer.py:6572`)
   → `HeatPumpOptimizer.optimize` → `_multi_start_minimize` /
   `_lbfgsb_restart` → `_scoped_minimize`, with `ftol` hardcoded in the
   options dict (lines 407, 529) and not config-overridable. No `FakeHass` in
   the loop; the harnesses never instantiate hass.
6. **Severity** — low is earned: bounded (≤ 0.80 % one-shot objective),
   no demonstrated money (null control fails), no comfort harm (0 of 80
   worse; worst violation 0.147 degree-steps on either arm). The trade-off
   comment at `optimizer.py:372–378` documents the *restart threshold's*
   fixture-stability cost, not the stop tolerance's — no documented
   rationale exists for ftol=1e-6 itself, so "bug" at low stands.

**Vote: verify, severity low.** My number: mean priced gap 0.117642 %
(finder harness re-run, exact) / 0.076 % on my own 6–48 h grid; polish arm
max 0.511 %.

**Metric definition**: relative objective gap `(J_prod − J_tight)/|J_prod|`
between `HeatPumpOptimizer.optimize`'s plan and the same solve with only
L-BFGS-B's `ftol` changed 1e-6→1e-14 at `_scoped_minimize`, `J` being
`OptimizationResult.objective_value` (production's own re-evaluation of the
final schedule).

## D0-02 — the policed budget (maxiter) never binds; ftol has no gate (`low`, bug)

### Re-run of the finder's harness

`tools/audit/round4/D0/budget_knobs.py` — **every RESULT identical to the
committed `budget_knobs.out`**:

```
max_gain_maxiter_x15_priced_pct   0.0 (exactly, all cells)
max_gain_gtol_1e-12_priced_pct    0.0 (exactly)
max_gain_ftol_1e-14_priced_pct    0.795787 %
lbfgsb_solves_observed            68
solves_terminating_on_maxiter     0
max_nit_observed                  52     median 8   (caps 200/300)
```

Together with the `ftol_gap.py` re-run (420 solves, 0 on cap) that is the
finder's 488-solve census, reproduced exactly.

### My own harnesses

`own_v3_D0_02.py` — my own census wrapper over `_multi_start_minimize` /
`_scoped_minimize`, on a **wider** grid (horizons 6/24/48 h with tiled
profiles, DHW on AND off, single- and two-zone, flat null):

```
own_lbfgsb_solves_observed         85
own_solves_terminating_on_maxiter   0
own_max_nit_observed               62   (median 12, p95 37; caps 200/300)
own_max_gain_maxiter_x15_*          0 % in every cell, priced and flat,
                                     0 cells changed
own starved wiring: maxiter -> 3:  24 of 24 solves on the cap,
                                     objective worse in 4 of 4 cells
```

The largest solve reachable in this configuration family (192-variable,
48 h two-zone) peaks at nit 62 against a 300 cap: "never binding"
generalizes beyond the finder's grid, and the census metric demonstrably
moves when the budget is actually cut.

`own_v3_gate_probe.py` — the mutation probe for the "no gate" half. It runs
the repository's own quality gate `tests/optimality.py` (at import, catching
its `sys.exit`) with production's options forced at `_scoped_minimize`:

```
gate unmodified control                 exit 0, 0 failures
gate with ftol 1e-6 -> 1e-3 (1000x)     exit 0, 0 failures
gate with maxiter -> 3                  exit 1 — challenger 3 fires
                                        ("the production iteration budget buys
                                        a materially better plan": full-budget
                                        67.76 vs starved 67.76, failed by
                                        construction, as that check designed
                                        itself to do)
```

The single-line production mutation the suite fails to notice is
`custom_components/heatpump_optimizer/optimizer.py` lines 407/529,
`"ftol": 1e-6` → `1e-3`: the optimality gate passes it outright. The
premise facts were also checked in the tree: `_MULTI_START_SOLVES = 4`
(line 202), `maxiter=300` (line 3004) and `maxiter=200` (line 3530);
challenger 3 is at `tests/optimality.py:89–113` and starves `maxiter` to 3.

### Attacks, in the contract's order

1. **Contention** — iteration counts and pass/fail; immune.
2. **Wrong gate mode** — the probe runs the gate file itself; there is no
   5-fixture-vs-`--all` ambiguity in the direction claimed (the claim is the
   gate does NOT fire). One nuance recorded: the *golden* fixtures pin plan
   bytes, so an ftol change would trip the drift gate as a behaviour change —
   but that pins value, not quality; with fixtures regenerated nothing
   complains, which is precisely what challenger 3 exists to prevent for
   maxiter and what is missing for ftol. The finding's substance is the
   quality-race sense and it holds by execution.
3. **Aggregate artefact** — n/a (a census, and "exactly zero" in 488+85
   solves on two different grids).
4. **Null control** — flat cells included in both censuses; x15 moves nothing
   at flat prices either.
5. **Reachability** — same production funnel as D0-01; the census hooks the
   real `_multi_start_minimize` calls the coordinator's executor makes.
6. **Severity** — low is earned: nothing user-visible today; it is a control
   aimed at a knob with 4–6x slack while the knob that decides plans is
   ungated (demonstrated at 1000x).

One wording flaw, not verdict-changing: the claim says ftol "changes every
plan" — literally it changes 34 of 70 priced cells above 0.01 % (8 of 12 on
the budget_knobs grid); the finder's own table states this correctly.

**Vote: verify, severity low.** My number: 0 of 85 solves on the cap (max
nit 62, caps 200/300) on my wider grid, x15 gain exactly 0 %; gate probe
exit 0 under a 1000x ftol loosening, exit 1 under maxiter→3.

**Metric definition**: L-BFGS-B calls terminating on the iteration cap
(scipy `status==1` or `nit ≥ maxiter` passed) over a solve grid, plus the
relative objective change `(J_prod − J_x15)/|J_prod|` from multiplying
production's `maxiter` by 15.

## Files

- Finder harnesses re-run: `ftol_gap.py`, `mpc_realised.py`,
  `budget_knobs.py` (outputs `.verify-0-3.out` beside them).
- Mine: `own_v3_D0_01.py` (+ `.out`), `own_v3_D0_02.py` (+ `.out`),
  `own_v3_gate_probe.py`.
