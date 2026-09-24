# D0 round 8: verifier v1 (the only verifier on the panel)

- Baseline: `cdf82daabcfe3777d98b31489f36df5555ec9d82`.
- Tree: `/home/claude/audit-r8/seats/D0-v1`, a git worktree.
- Machine: a shared 4-vCPU cloud container.
- `thread_factor` was 1.000 on every run. load1 ranged from 5.3 to 16.6 during the runs.
- No timing number is used. Every number below is a count, an objective ratio or a SEK figure. They are deterministic on this box.
- The finder evidence from D0-s1 and D0-s2 was copied in with `cp -rn`. No harness hard-codes a seat path, so none needed rewriting.
- Production is byte-identical to the export (`diff -rq -x __pycache__ custom_components`). `git status` shows only `tools/audit/round8/` as untracked.
- Logs are in `tools/audit/round8/D0/v1_logs/`.

This panel has one verifier. I therefore did both jobs: I re-ran the finder's harness, its perturbation and its null control, and I measured the finding with my own harnesses:

- `v1_descent.py`: plan-level local descent headroom, plus my own re-implementation of the ftol arms.
- `v1_mpc.py`: whether the gap is realised in closed loop.

## D0-s1-01: L-BFGS-B ftol=1e-6 stops refinements short

### 1. Finder's harness, re-run as its header says

`s1_budget.py --tz 1 --dhw 0 --arms prod,ftol` (log `v1_logs/s1_rerun_tz_d0.log`). Every RESULT matches the finding to the last printed digit:

- `runs_stopped_by_ftol=219/320`, pgtol 64, maxiter 0, other 37.
- `ftol_cells_gap_gt_1e-3=15/40`.
- Gap mean 1.1249e-3, max 1.1074e-2, min -2.6041e-4, mean with the best cell dropped 8.6984e-4.
- Flat mean 7.2917e-4, flat max 3.9062e-3, non-flat mean 1.1815e-3.
- Cost delta mean 0.0353 SEK/day, max 0.80 SEK/day.
- nfev ratio median 1.824, max 4.514.
- thread_factor 1.000, load1 12.66.

**Perturbation.** `s1_budget_perturb.sh` ran after all my other runs had finished, because it edits production (log `v1_logs/s1_perturb_rerun.log`). It reproduced exactly:

- 5 of 5 cells reach `ftol_gap=0`.
- The five cells show 1+1+1+4+4 = 11 ftol stops out of 40 runs.
- winter_typical|winter_cold goes to J = 77.699680.
- The file was restored, and the script printed `RESTORED`.

**Attack on this perturbation: it is tautological for the gap.** Editing production to ftol 1e-12 makes production *identical* to the arm, so gap → 0 by construction. The edit does prove that the seam patch and the literal edit are the same code path: production J equals the arm's J bit for bit. That shows the harness hooks the real symbol. It does not independently show that a gap exists. My own perturbation below does move non-tautologically.

### 2. My own measurement

**Metric (one line), `v1_descent.py` "cont" arm.** Per cell, headroom = (J_prod − J_cont)/|J_prod|, with J the shipped `optimize(...).objective_value`. The cont arm:

- lets every production `_multi_start_minimize` finish as shipped;
- then continues from the returned x with an independent descent: L-BFGS-B at ftol 1e-15, gtol 1e-9 and maxiter 3000, using my own central-difference gradient (h = 1e-5) through production's `batch_objective`;
- is counted only where the degree-steps below 17 °C of the room *and both zones* are no worse.

This measures what the stop left locally at the shipped point. The finder's arm re-runs the whole multi-start from the same seeds with a tighter ftol, so the two definitions differ. The judge decides whether they are comparable.

Two-zone grid, DHW off, 40 cells (log `v1_logs/descent_tz_d0.log`). The ftol9 and ftol12 arms are my own seam re-implementations:

| arm | cells > 1e-3 | mean | mean, best cell dropped | leave-one-out range | max | flat mean | comfort-worse cells | nfev, total ratio |
|---|---|---|---|---|---|---|---|---|
| cont (local headroom) | 7/40 | 6.06e-4 | 5.02e-4 | 5.02e-4 to 6.21e-4 | 4.66e-3 | 9.33e-4 | 2 | — |
| ftol12, raw (the finder's arm) | 15/40 | 1.1249e-3 | — | — | 1.1074e-2 | — | — | 2.313 |
| ftol12, zone-aware comfort | 13/40 | 9.97e-4 | 7.38e-4 | — | 1.11e-2 | −5.2e-5 | 3 | 2.313 |
| ftol9 (a practical fix size) | 12/40 (raw 15/40) | 8.78e-4 (raw 1.05e-3) | — | — | 1.11e-2 | — | 4 | 2.168 |

- **Independent reproduction.** My ftol12 raw numbers equal the finder's exactly: 15/40 cells, mean 1.1249e-3.
- **The effect is real.** The shipped point has measurable local descent left: mean 6.1e-4 of the objective, and 7/40 cells above 0.1 %.

**My perturbation, which is not a tautology** (`--prod-ftol 1e-12 --arms prod,cont`, log `v1_logs/descent_tz_d0_perturb.log`). Production itself was set to ftol 1e-12, and I then re-measured the local headroom in the 8 cells where cont exceeded about 7e-4. In 6 of the 8 the headroom collapsed by 10× or more (direction: to zero):

| cell | cont headroom before | after |
|---|---|---|
| winter_typical\|winter_mild | 2.40e-3 | 0 |
| shoulder\|winter_cold | 3.14e-3 | 1.3e-5 |
| winter_narrow\|winter_cold | 2.45e-3 | 5.7e-5 |
| winter_narrow\|winter_mild | 3.38e-3 | 1.2e-4 |
| winter_moderate\|winter_mild | 1.40e-3 | 8.7e-5 |
| flat\|winter_cold | 4.66e-3 | 5.1e-4 |

In the other two cells, winter_typical|winter_cold (2.4e-3) and winter_moderate|winter_cold (4.6e-3), headroom remains. In both, the continuation buys J by worsening zone comfort. That residual comes from the forward-difference eps = 1e-4 gradient and the line search, not from ftol. So in most cells ftol is the mechanism behind the local shortfall.

### 3. Attacks, in verifier.md order

1. **Contention.** Not applicable: no timing number is used. Counts and ratios came out bit-identical between the finder's box run (load1 18.8) and mine (load1 12.7).
2. **Gate mode.** Not applicable: this is not a test-gap claim.
3. **Grid artefact.** The finding partly survives this attack.
   - The 5 summer_warm cells are degenerate: J = 10597.97, nfev 12, and a gap of exactly 0. They dilute the mean. Without them the ftol12 mean is 1.29e-3.
   - Leave-one-out is stable: 7.4e-4 to 1.03e-3 under my zone-aware filter.
   - **The maximum cell is not what the title says.** The 1.11 % maximum is summer_negative|shoulder, a J = 0.22 day with cost −1.52 SEK, where the arm moves cost by 0.008 SEK. The local continuation from the shipped point finds only 2.3e-4 there.
   - **Mechanism split.** Of the finder's 15 cells above 1e-3:
     - 7 have local headroom ≥ 1e-3, so they genuinely stop short;
     - 3 have partial headroom;
     - 5 have *no* local headroom (< 1e-6): winter_extreme|shoulder, summer_negative|winter_mild (5.8e-3 → 2.8e-7), shoulder|summer_cool, shoulder|shoulder and winter_moderate|summer_cool.

     In those 5 the shipped point is a stationary point. A tighter ftol reaches a *different basin* along a longer path. That is basin selection, the finder's own non-finding "Extra seeds", and not the solver stopping short of a minimum. The title and claim ("stops short of the minimum the same solver reaches") hold on about half the cells, not all 15.
4. **Null control.** The gap is not a price effect.
   - The finder's gap survives flat prices, and the finder says so.
   - It is a convergence gap on the whole objective, not price optimality. Under the brief ("A gap that survives flat prices is not price optimality; name what it is") that makes it **out-of-dimension for D0**. It belongs to solver convergence.
   - The flat survival itself is fragile. Under my zone-aware comfort filter, the flat cell that carries the finder's null number (flat|winter_cold, 3.9e-3) is comfort-worse, so the flat mean falls to −5.2e-5. The zone shortfall differences are all below 0.002 degree-steps, however, so I treat the comfort filter as near-parity, not as a refutation.
   - The finder's filter checks `room_temp_trajectory` only. On a two-zone house it should check the zones. The count moves from 15 to 13.
5. **Reachable in real HA.** Yes. `optimize` → `_multi_start_minimize` / `_lbfgsb_restart` → `_scoped_minimize` is the shipped path, and no `FakeHass` is involved.
6. **Severity by consequence** (`v1_mpc.py`, log `v1_logs/mpc.log`).
   - **Setup.** Closed loop over 24 h with a re-plan every hour. The plant is the optimizer's own model, two-zone, DHW off. Cost is settled by stored-heat change (s2_rolling's rule). The arm is ftol 1e-12 against production.
   - **Settled cost.** The arm is cheaper in 3 of 5 cells and dearer in 2:
     - cheaper: winter_typical|winter_cold +1.06 SEK (1.5 %), winter_narrow|winter_cold +0.55, flat|winter_cold +0.43;
     - dearer: shoulder|shoulder −0.09, winter_extreme|winter_mild −0.0002.
   - **Comfort.** The arm is *worse* on realised comfort: +3.94 degree-hours below target in total and +0.42 degree-hours below 17 °C.
   - **Compute.** The arm pays 2.42× function evaluations in closed loop and 2.31× on the plan grid (nfev ratio, not timing). That compute is scarce on Pi-class hardware.
   - **Conclusion.** The realised effect is a mixed trade between cost and comfort, and the flat control realises as much as the price cells do. A 0.1 % objective gap does not justify more than low.

### Vote: verify, at low

- The finding's numbers reproduce exactly, both in the finder's harness and in my independent re-implementation.
- My own metric, local descent headroom at the shipped point, independently confirms the stop leaves descent: 7/40 cells above 0.1 %, mean 6.1e-4.
- That headroom moves to zero under the ftol perturbation in 6 of 8 cells.

Three qualifications go to the judge:

- About a third of the claimed cells (5/15) are basin changes, not local shortfall. That includes the headline maximum.
- The comfort filter should read the zones on two-zone.
- It is out-of-dimension for D0, as the flat control shows.

There is only one finding, so there is no mechanism pairing within this panel. The basin-change share overlaps D0-s1's own "Extra seeds" non-finding (basin selection on the comfort and cycling terms).
