# D0 round 4 — verifier report, seat 0-1 (own-harness seat)

- **Worktree**: `../audit-r4-verify-D0-1`, branch head `0855277` (detached).
- **Baseline parity**: `git diff --stat 7dd68dd..HEAD -- custom_components/`
  touches only `manifest.json` (version) and `www/heatpump-optimizer-card.js`
  (version banner). `optimizer.py` and `thermal_model.py` are **byte-identical**
  to baseline (`git diff` empty), so every number below measures the same
  production solver the finder measured at `7dd68dd`.
- **Interpreter**: `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`,
  always `PYTHONPATH=tests/hastub`, from the worktree root.
- **Contention**: load1 ranged 4.8–10.4 across the runs, `thread_factor`
  1.0000–1.0003. **No timing, wall, CPU or RSS claim is made or judged
  anywhere in this report** — every number is an objective value, a ratio of
  two objective values, an iteration count, or a solve count. Concurrent
  python-process counts beside the solve-heavy runs: 3–5 (the other two
  verifiers plus mine; the finder re-runs themselves showed 4–5).
- **Gate lock**: not taken — `tests/stress.py` was not run, no full gate run.
- **Production edits**: the two perturbation arms below edit
  `optimizer.py` in this worktree and are reverted with
  `git checkout --`; final `git status --porcelain custom_components/` is
  empty. Nothing else outside `tools/audit/round4/D0/` was touched.

## 1. Re-runs of the finder's harnesses (contract step 1)

| harness | result vs finder's `.out` |
|---|---|
| `ftol_gap.py` (80 cells) | **byte-identical** modulo `load1`/`swapins` lines (`diff` empty after filtering them). mean_gap_priced 0.117642 %, max 0.799815 %, flat null 0.104822 %, 34/70 cells > 0.01 %, 18/70 > 0.1 %, comfort-worse cells 0/80, 420 solves, 0 maxiter-binding. load1 10.35, tf 1.0001. |
| `mpc_realised.py` (10 cells) | **byte-identical** (same filter). priced +0.320965 SEK/day, flat null **−2.11318** SEK/day, production cheaper in 4/8 priced cells, mean bill 57.02 SEK/day, comfort-worse 1/10 (0.0016 degree-steps). load1 6.91, tf 1.0. |
| `budget_knobs.py` (12 cells) | **byte-identical** (same filter). maxiter×15 = 0.0000 % in every cell, gtol 1e-12 = 0.0000 % in every cell, ftol 1e-14 mean 0.164503 % / max 0.795787 %; 68 solves, 0 on cap, max nit 52, median 8. load1 4.84, tf 1.0002, concurrent 4. |
| `nonfindings.py` (12 cells) | **byte-identical** (same filter). restart-to-convergence mean 0.014006 % / max 0.134817 %; co-opt iterated 0.0000 % everywhere. load1 4.90, tf 1.0003, concurrent 5. |

Deterministic reproduction at the stated tolerance (±0.02 pp) — indeed to the
last printed digit — on the same box class. Nothing differed.

## 2. `outer_bound.py` executed (the harness the finder committed but never ran)

Its header is sound (metric, command, expected signs, baseline SHA,
perturbation, null control), so per the resume note I executed it.

```
mean_gap_A_to_B_priced_pct  0.119549   (stopping rule; agrees with ftol_gap's 0.1176 on a different weather mix)
max_gap_A_to_B_priced_pct   0.795787
mean_gap_B_to_C_priced_pct  0.0636779  (seeding beyond the tightened solve)
max_gap_B_to_C_priced_pct   0.443725
mean_gap_A_to_C_priced_pct  0.183097   (total gap to the 16-start tight-tolerance bound)
max_gap_A_to_C_priced_pct   0.807287
mean_gap_A_to_B_flat_pct    0.284989   (null control again does not vanish)
cells_wider_search_worse_than_B 0
```

What it shows: the finder's non-finding 5 ("wider seeding ≈ the same points
the tolerance arm reaches, never materially past them") is **approximately
right but not exactly zero** — a 16-start tight-tolerance outer bound buys a
further 0.064 % mean / 0.444 % max beyond ftol alone (A→C is ~1.5× A→B).
This does not touch D0-01 as filed (D0-01 claims only what the single ftol
change buys, and that is exactly A→B), but the register should record that
seeding has a small second component. The B→C flat control is 0.075 %. The
wider search is never worse than B in any cell (0/16).

## 3. Own harness for D0-01 — `d0_own_D0-01.py`

**Method (deliberately different from the finder's).** The finder re-runs the
whole multi-start pipeline under a patched option. I patch nothing in the
production solve: I capture the `(objective, args, bounds, batch_objective,
fd_eps, maxiter)` that `_multi_start_minimize` receives during a real
`HeatPumpOptimizer.optimize` call, take the point it returned, and run
L-BFGS-B **myself** from that exact point with options identical to
production's dict except `ftol` 1e-14. A positive drop proves the shipped
point itself is not converged under the tighter rule — no seeding or basin
question can explain it. My census also hooks one level **below** the
finder's (`optimizer.minimize`, the module-level scipy symbol) so any
L-BFGS-B call outside their `_scoped_minimize` funnel would surface.

**Grid (different from the finder's)**: 8 price × 2 weather
(winter_cold, summer_warm) × tz ∈ {0,1} × dhw ∈ {True,False} = 64 cells —
covering **both** `_multi_start_minimize` call sites (the finder's 80 cells
were all dhw=True, i.e. only the maxiter=300 path).

```
RESULT own_cells_priced=56                       RESULT own_cells_flat_null_control=8
RESULT own_mean_descent_gap_priced_pct=0.0829919 %
RESULT own_max_descent_gap_priced_pct=1.1703 %        (finder max: 0.7998)
RESULT own_loo_mean_descent_gap_priced_pct=0.0632226 %
RESULT own_mean_descent_gap_flat_pct=0.143336 %       (null control: LARGER than priced)
RESULT own_max_descent_gap_flat_pct=1.12326 %
RESULT own_cells_gap_above_0p01pct=10  (of 56)   own_cells_negative_gap=0
RESULT own_mean_gap_dhw_path_priced_pct=0.0650978 %        (maxiter=300 site)
RESULT own_mean_gap_spaceonly_path_priced_pct=0.100886 %  (maxiter=200 site — NOT in the finder's grid)
RESULT own_scipy_minimize_calls=334   RESULT own_unexpected_scipy_paths=0
CENSUS status=0 n=204 'CONVERGENCE: NORM OF PROJECTED GRADIENT <= PGTOL'
CENSUS status=0 n=125 'CONVERGENCE: RELATIVE REDUCTION OF F <= FACTR*EPSMCH'   <- the ftol test, live in 125/334 solves
CENSUS status=2 n=5   'ABNORMAL: '
RESULT own_census_status1_maxiter=0
```

load1 7.97, tf 1.0002, concurrent_python_procs 5.

Restricting to winter_cold cells only (my weather mix's heating-relevant
half, comparable to the finder's mix): priced mean **0.165979 %**, max
1.1703 %, flat mean **0.286675 %** — bracketing the finder's 0.117642 % from
a different method, a different grid, and a different hook. The single
largest cell is `summer_negative / winter_cold / tz=0 / dhw=0` at **+1.1703 %**
on the space-only call site the finder never covered.

**Perturbations (real one-line production edits, reverted after each arm;
probe `d0_own_perturb.py`, constant challenger across arms):**

| arm | source edit | mean gap over 5 probe cells | max gap | ftol observed passed |
|---|---|---|---|---|
| shipped | — | 0.714864 % | 1.170304 % | 1e-06 |
| tight | `"ftol": 1e-6` → `1e-14` (both dicts) | **0.007808 %** (91× drop) | 0.038512 % | 1e-14 |
| loose | `"ftol": 1e-6` → `1e-4` | 0.641606 % | **1.376059 %** (grows) | 1e-4 |

The constant is causal and the metric moves in the stated directions. One
honest deviation from the finder's header: under the tight edit the gap falls
to ~0.008 %, **not exactly 0** — an ftol of 1e-14 still stops on
floating-point noise; "must fall to 0" is very nearly but not literally true.

## 4. Own harness for D0-02 — `d0_own_D0-02.py`

**Method (different from the finder's).** Census at the scipy boundary over
20 cells covering **both** call sites (dhw on and off), then two arms: (a)
maxiter pinned to the **tightest cap the census says is safe** (the observed
grid max nit, 47 — a sharper probe than the finder's ×15), and (b) the
`maxiter=3` starvation that `tests/optimality.py` challenger 3 uses,
replicated to confirm the existing gate fires on starvation while the
shipped budget never binds.

```
RESULT own_solves_observed_scipy_boundary=108   (both maxiter=200 and maxiter=300 seen)
RESULT own_solves_on_cap_shipped=0
RESULT own_max_nit_shipped=47     (46 on the 300 path, 47 on the 200 path)   median 8
RESULT own_tight_cap_used=47
RESULT own_solves_on_cap_tight=1  (a solve ending exactly at nit==cap; plan unchanged)
RESULT own_cells_plan_changed_tightcap=0        max abs objective gap 0.0000 % priced AND flat
RESULT own_solves_on_cap_starved3=99  of 106
RESULT own_mean_gap_starved3_priced_pct=-3.1176 %   min -11.8578 %   flat -1.5336 %
```

load1 5.25, tf 1.0003, concurrent_python_procs 3.

**Perturbation (production edit, reverted)**: `maxiter=300,` → `maxiter=3,`
at `optimizer.py:3004` and `maxiter=200,` → `maxiter=3,` at `:3530`; census
probe: `perturb_solves=17`, `perturb_solves_on_cap=14`, maxiter values seen
`[3]`. The census flips from 0/N to all-but-trivially-converged, and the
objective worsens by 3.1 % mean / 11.9 % worst — the knob the gate polices is
real; it simply never binds at the shipped budget. Headroom is exact:
200/47 ≈ 4.3× (space) and 300/46 ≈ 6.5× (DHW), and even the tightest
census-safe cap (47) changes **zero** of 20 plans.

Supporting source checks: `_MULTI_START_SOLVES = 4` (`optimizer.py:202`),
`maxiter=300` at `:3004`, `maxiter=200` at `:3530`, both option dicts
`{"maxiter": …, "ftol": 1e-6, "eps": 1e-4}` at `:407` and `:529`;
`tests/optimality.py:90-115` is challenger 3 ("the production iteration
budget buys a materially better plan", starving `maxiter` to 3). No test
gates `ftol`: the only `ftol` references in `tests/` are
`features.py:2676` (the restart keep-bar semantics of #826),
`stress.py:567` (the reference solve's own options) and `env_drift.py:328`
(a probe context) — none races a tighter tolerance against production. The
golden drift gate would detect that ftol moves plans, but as undirected
change, not as a quality gate.

## 5. Attacks run and outcomes

**D0-01**

1. *Contention* — no timing number exists to attack; all figures are
   objectives, ratios, counts. tf ≤ 1.0003 throughout.
2. *Hook completeness* — census at the scipy boundary (below the finder's
   hook): `own_unexpected_scipy_paths=0` of 334 calls; every call carried
   production's exact options. The finder's funnel is the funnel.
3. *Grid artefact* — dropping any single price profile from the finder's own
   cell data keeps the priced mean at 0.0976–0.1122 %; per-weather means
   0.119–0.183 % for four of five weathers (summer_warm is exactly 0 in both
   grids — trivial no-heat solves); both topologies affected (tz=0 0.105 %,
   tz=1 0.130 %). LOO drops the finder's mean only to 0.108 %. My own grid
   (different weather mix, plus the second call site) reproduces the effect.
   Not an artefact.
4. *Null control* — present, run, and it fails the money claim exactly as
   the finder says: flat objective gap does not vanish (finder 0.1048 %, mine
   0.143 % overall / 0.287 % winter-only — *larger* than priced), and
   closed-loop flat SEK moves the wrong way (−2.113 SEK/day) against the
   priced +0.321 SEK/day. The finder draws no money conclusion; the honest
   half is indeed the null control.
5. *User consequence / severity* — the finder's own re-run shows the priced
   **energy-cost** delta is −0.0397 SEK/day (production marginally cheaper on
   the bill): the objective gap is comfort-term dominated, not bill savings.
   Comfort is never worse in 80/80 cells (largest violation 0.147
   degree-steps on either arm); step-0 command differs > 0.01 kW in 9/70
   cells (max 4.06 kW), so the gap can reach the actuator within a cycle,
   but closed-loop SEK is noise-dominated. `low` is earned.
6. *Stop-rule attribution* — my termination-reason census: 125 of 334
   production solves stop on `RELATIVE REDUCTION OF F <= FACTR*EPSMCH`
   (L-BFGS-B's ftol test) directly; 0 on the iteration cap. The stop rule
   the finding names is measurably live.
7. *"Not a minimum of its own objective"* — my method descends from the
   shipped point itself; 10 of 56 priced cells still drop (> 0.01 %), up to
   1.17 %. The claim is proven from production's own output, independent of
   seeds.

**D0-02**

1. *Contention* — counts only.
2. *Census depth and coverage* — deeper hook (scipy boundary), both call
   sites: 0 of 108 (own-02) and 0 of 334 (own-01) on cap; finder's 0 of 488
   confirmed on a strictly wider surface. max nit 47–52 against caps 200/300.
3. *"changes no plan"* — verified sharper than filed: maxiter pinned at the
   observed max nit (47), not ×15, still changes 0 of 20 plans; ×15 is
   0.0000 % in the finder's 12 cells (byte-identical re-run).
4. *Is the gate simply wrong?* — no: the starvation arm (maxiter=3) puts
   99/106 solves on the cap and worsens the objective 3.1 % mean / 11.9 %
   worst, so the existing gate fires on real starvation; it is aimed at a
   knob with 4.3–6.5× slack while ftol — the stop rule 125/334 solves
   actually end on — has no quality gate.
5. *Wording* — "ftol … changes every plan" overstates: it changes the
   objective in 47 of 80 cells at print precision (34 of 70 priced > 0.01 %;
   9 of 12 budget_knobs cells). The defensible statement is "the only knob
   of the three that moves any plan, and it moves most". Measurement and
   census unaffected.

## 6. Votes

### D0-01 — verify (severity `low`, as filed)

- Finder's number re-executed byte-identically: mean 0.117642 %, max
  0.799815 % priced; flat null 0.104822 %; comfort-worse 0/80; MPC flat null
  −2.113 SEK/day against priced +0.321.
- My own number, own metric, own grid, own hook: descent-from-shipped-point
  mean 0.0829919 % (winter-only 0.165979 %), max 1.1703 %, flat null 0.143336 %
  (winter-only 0.286675 %), present at both call sites.
- Metric definition (mine): relative drop of the production objective from
  running L-BFGS-B myself, started at the exact point `_multi_start_minimize`
  returned in an unmodified production solve, options identical but
  `ftol` 1e-6 → 1e-14.
- Perturbation by source edit: tight → 91× smaller gap; loose → max grows to
  1.376 %. Causal.

### D0-02 — verify (severity `low`, as filed)

- Finder's census re-executed byte-identically: 68 solves, 0 on cap, max nit
  52, median 8; maxiter×15 and gtol arms exactly 0.0000 %.
- My own number, own census at the scipy boundary over both call sites:
  0 of 442 solves on cap; max nit 47 (space path) / 46 (DHW path); tightest
  census-safe cap (47) changes 0 of 20 plans; starvation (maxiter=3) flips
  the census to 99/106 on cap and worsens the objective 3.1 % mean /
  11.9 % worst.
- Metric definition (mine): L-BFGS-B calls terminating on the iteration cap
  (status 1, or nit ≥ the maxiter production passed) observed at
  `optimizer.minimize`, over dhw-on and dhw-off cells; plus the objective
  change from capping maxiter at the observed max nit and at 3.
- One wording correction for the register: "ftol changes every plan" →
  "ftol is the only one of the three knobs that moves any plan (34 of 70
  priced cells > 0.01 %)". Not severity-relevant.

## 7. Register notes beyond the findings

- `outer_bound.py` (never executed by the finder) now has executed numbers
  (§2): the seeding component beyond ftol is small but nonzero (mean
  0.0637 %, max 0.4437 % over 14 priced cells). The finder's non-finding 5
  stands as approximately true; "seeding buys nothing once the stop rule is
  fixed" should read "buys about a third as much again as the stop rule
  leaves, at 16 starts".
- My census saw 5 of 334 solves end `ABNORMAL` (line-search failure,
  status 2) — handled by production's restart machinery, out of scope for
  both findings, recorded for the next round.
- Harnesses added by this seat: `d0_own_D0-01.py`, `d0_own_D0-02.py`,
  `d0_own_perturb.py` (+ `.verify-0-1.out` transcripts), all under
  `tools/audit/round4/D0/`, runnable by the command in their headers.
