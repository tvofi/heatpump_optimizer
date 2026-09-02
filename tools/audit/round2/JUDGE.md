# Round-2 judge: re-measured verdicts

I do not trust the finders or the verifiers. Every number below is one I
executed myself, in my own worktrees:

- `judge-baseline` = `c398fc84eec25fc44b60d74aae05b9a2da205884` (the round-2 baseline)
- `judge-main` = `origin/main` @ `bad1d21` (v6.3.4)

Interpreter: `/Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/tvofi-claude/.venv/bin/python`
(3.13.1, numpy 2.5.2, scipy 1.18.1) — the only interpreter on this box with
numpy; the system `python` (3.11.5, pyenv shim) has none, so every command
written `python` was run with that venv. All five BLAS thread variables pinned
to 1. Node 20.10.0, Playwright resolved from
`/Users/timmalmstrom/.npm/_npx/bbb8a2c4738e2b0c/node_modules`.

## Two standing caveats on the measurement conditions

**1. `load1 <= 1.5` was unattainable and no audit workload caused it.** During
Part 1 the box carried no audit process at all (`ps` showed one python, no
`run.sh`, no `stress.py`, no node harness). The load came entirely from the
desktop — WindowServer 44-49 %, Safari 15 %, Claude Helper 15-22 %. With zero
audit work running the ambient floor was `load1` 1.86; over the contract's ten
60-second retries (23:15:10 - 23:24:11) the minimum reached was **1.55** and
the run proceeded at that. Every RESULT below therefore carries a `load1`
above the contract's bar, and I say so rather than pretend a quiet window
existed. What makes the numbers usable anyway is that they are counts,
within-process CPU ratios against `reference_solve` (`thread_factor` 1.000 on
every take), or wall numbers carried by an idle null control taken on the same
loaded box — see D9-05, where the idle heartbeat's starvation share is 0.00-0.03
against the solve's 0.96-0.999.

**2. The gate lock was stale and I did not take it.** `/tmp/hpo-gate.lock` was
held from 22:33 with no process behind it: `ps` showed no `run.sh`, no
`stress.py`, no `golden.py`, no `env_drift.py`, no `prescreen.py`, no node
harness for the whole of Part 1. I queued for it (a `mkdir` retry loop, 30 min)
and it never released. The contract says never remove a lock I did not create,
so I did not; instead I verified before each Part 1 RESULT that no competing
audit process was on the box, which is the condition the lock exists to
guarantee. Part 1 was run serially, one harness at a time.

---

## Part 1 — the three timing findings

| id | panel sev | my verdict | my decisive number (command) | load1 / thread_factor | stop_rule_class | notes |
|---|---|---|---|---|---|---|
| D9-01 | high | **verified** | 9221.55 simulate-step-equivalents/gradient on the pinned two-zone DHW solve vs 297.32 batched (**31.0x**) at baseline; 9220.20 vs 292.56 (**31.5x**) on main. `PYTHONPATH=tests/hastub .venv/bin/python tools/audit/round2/D9/h1_grad_equivalents.py` | 2.92 / 1.000 (baseline), 2.32 / 1.000 (main) | bug | Reproduced **exactly** against the "exact" tolerance (9221.55 claimed, 9221.55 got). Perturbation (drop the pin/cap: `two_zone_dhw` arm) moves the number **down 31x** — harness is not void. `dhw_cap_zero_range` 9221.85 confirms the cap route independently. **Still reproduces on current main** — #208/#211/#212/#213/#220 did not touch it; the scalar path is *worse* on main in absolute work (2,738,400 simulate_step vs 1,595,328 at baseline, solve/reference 1267x vs 744x). **fuse_guard drift confirmed, finder's `expected_golden_drift` was wrong**: `v3_d901_golden_scan.py` gives `fuse_guard.fields_changed_at_precision6=177`, `max_abs_delta=4.5e-05`, worst field `power_schedule[49]`, `payload_identical=0` — the fixture MUST be re-recorded, not "last-decimal at most, possibly none". `fuse_guard` is the *only* one of 55 golden scenarios with a zero-range bound (`scenarios_with_zero_range_bounds=1`), so the blast radius is exactly one fixture. Panel counted 3-0 verify; I count 3-0 verify and add the drift correction as binding. |
| D9-02 | medium | **verified**, class corrected to hygiene | `smallest_detectable_uniform_regression = 4.728` (claim 4.685, tolerance +-20 % — reproduced); `plain.worst_ratio=296.09` vs budget 1400, `plain.sweep_ratio=52.67` vs 450; an injected uniform 2x trips **0** per-scenario and **0** sweep checks. `PYTHONPATH=tests/hastub .venv/bin/python tools/audit/round2/D9/h7_stress_gate.py` | 2.64 / 1.0002 | **hygiene** (finder and panel said bug) | The ruler proves itself: `injected_over_plain_worst=1.9967`, `injected_over_plain_sweep=2.0329` — the 2x injection lands as 2.00x through the contention, so the ratio metric cancels the loaded box. Perturbation executed: `STRESS_SOLVE_RATIO=400 STRESS_SWEEP_RATIO=75` takes the injected arm from 0/0 to **2 per-scenario + 1 sweep tripped** while the plain arm stays 0/0 — moves in the stated direction, harness is not void. `ci_sets_stress_ratio=0` and `tests_memory_instrumentation=0` both confirmed. **Class corrected**: the number is a property of `tests/stress.py`'s budget constants, not of shipped behaviour — nothing a user runs misbehaves. That is the same kind as D3-01..07, which the finder classed hygiene. It stays medium severity (a 4.7x blind spot is a real gate weakness) but it is not a bug. |
| D9-05 | medium | **verified**; the finder's stated perturbation stays **void**, replaced with mine | Baseline `two_zone_dhw` starvation share **0.9589 / 0.9579** (two takes), gap p50 11.4 ms, longest hold 53.0 / 52.1 ms; the 12.8 s capped solve **0.9988**. Main: **0.9814 / 0.9752**, longest hold **245.3 / 360.6 ms**, gap p99 223 / 329 ms. `PYTHONPATH=tests/hastub .venv/bin/python tools/audit/round2/D9/j5_gil.py` (my instrument) | 3.34 / n.a. (see note), 2.99 main | bug | Measured with **my own instrument**, not the finder's: a real `asyncio` loop, a real `ThreadPoolExecutor(1)`, a 1 ms heartbeat coroutine, `HeatPumpOptimizer.optimize` submitted through `run_in_executor` — never `FakeHass`. Claim 0.967 +-5 %: I get 0.9589, **reproduced**. Longest hold claimed 39-75 ms: I get 52-53 ms at baseline, in range. **The panel was right to void `setswitchinterval(0.05)`**; my replacement perturbation is `sys.setswitchinterval(0.005 -> 0.0005)`, expected direction **down**, and it moves decisively: share **0.9589 -> 0.0000**, longest hold **53.0 -> 4.43 ms**, p50 11.37 -> 2.45 ms at baseline; **0.9814 -> 0.0000** and 245.3 -> 3.62 ms on main. That is the mechanism named and moved, so the harness is sound under my definition. **Null control holds on the loaded box**: the idle heartbeat with no solve gives share 0.0321 (baseline, one 29.7 ms desktop outlier) and 0.0000 (main, longest gap 1.47 ms) — a 30x to infinite separation from the solve's 0.96-0.999, so the starvation is the solve's and not the box's. **The panel's "understated by the finder" is confirmed on main, not at baseline**: baseline longest holds are 52-53 ms, main's are 245-361 ms, and main's solve is 2.3x longer in wall (1650 ms vs 709 ms). The consequence therefore got worse since the baseline, not better. `thread_factor` is not meaningful per-arm here (the measured loop thread does almost no work while the executor thread does all of it, giving a 130-150x process/loop-thread ratio that says nothing about BLAS); the BLAS pin is enforced by the five environment variables and confirmed at 1.000 by the D9-01 and D9-02 runs in the same session. |

---

## Part 2 — every other panel survivor

Skipped as instructed: D2-01 (shipped in #211), D8-04 / D4-10 / D3-09 (closed
wontfix), D7-05 / D3-08 (folded elsewhere), all of D10 (another session).

Command prefix for every Python row (omitted from the table for width):
`OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub .venv/bin/python`.
Node rows add `HPO_PLANDATA=$SCR/d4/plandata.json NODE_PATH=/Users/timmalmstrom/.npm/_npx/bbb8a2c4738e2b0c/node_modules PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/pw-browsers`.

| id | panel sev | my verdict | my decisive number (harness) | load1 / tf | class | notes |
|---|---|---|---|---|---|---|
| D0-01 | medium | **verified** | `cells_with_gap_sz=15` of 16, `mean_energy_gap_pct_bill_sz=2.517`, `restart_improves_sz=7`, `pg_above_pgtol_sz=16`, `mean_restart_gap_sek_sz=0.1661`, LOO `2.192 %` (`D0/race_grid.py --tz 0 --weather winter_cold --random 3 --opt <tariff15>`) | 5.51 / 1.000 | bug | Every figure reproduces **to the digit** against the "counts exact, SEK ±1e-3" tolerance. Perturbation `D0_PERTURB=ftol9` executed: `restart_improves_sz` 7 -> **0**, `mean_restart_gap_sek_sz` 0.1661 -> **0.0000**, `cells_with_gap_sz` 15 -> 10, energy gap 2.517 -> 1.385 — the finder's stated observed values exactly. Not void. **Not fixed by #208**: on judge-main `cells_with_gap_sz=14`/16, `max_gap_sek_sz=58.2850` *identical to baseline*, `restart_improves_sz=7`, `pg_above_pgtol_sz=16`, LOO 1.694 %. The aggregate is fragile (92 % of the mean is one `summer_negative` cell, LOO drops 4.82 -> 2.19 %) but the single cell ships a real 60.00 SEK peak charge, and re-planning cannot undo a capacity charge once set. Medium stands. |
| D0-02 | low | **verified**, null control **fails for the gap component** | `restart_improves_tz=15` of 80, `mean_restart_gap_sek_tz=0.0519`, `pg_above_pgtol_tz=64`, `cells_with_gap_tz=49`, `mean_gap_sek_tz=0.1088` (max 2.5099), LOO `0.232 %` (`D0/race_grid.py --quiet`, 160 cells) | 5.8 / 1.000 | bug | All exact. Perturbation `D0_PERTURB=restart` executed on the 16-cell subset: `mean_restart_gap_sek_tz` 0.2183 -> **0.0030** and `mean_gap_sek_tz` 0.449 -> 0.2494 — again the finder's own figures. Not void. **The null control splits**: the *restart* component passes it cleanly (flat restart gap -> 0.0030), but the *energy-gap* component **fails** — `null_flat_mean_gap_sek_tz=0.1553` against `nonflat_mean_gap_sek_tz=0.1022`, i.e. the flat cells carry the *larger* gap. So the money in this finding is not price optimality; only the stall is real, and it is worth 0.05 SEK/day. Low is right, and the fix belongs folded into D0-01's restart rule. **Substantially reduced by #208, not removed**: on judge-main `restart_improves_tz=10`/80, `mean_restart_gap_sek_tz=0.0063` (8x smaller), `cells_with_gap_tz=42`, `mean_gap_sek_tz=0.0562`, LOO 0.116 % — and the null still fails the same way, now 3.7x over (`null_flat 0.1543` against `nonflat 0.0421`). |
| D0-03 | medium | **verified**; the contested null control resolved **in seat 3's favour**, title unchanged | `cells_with_gap_tz=5` of 8, `mean_gap_sek_tz=1.1333`, `max_gap_sek_tz=4.1884`, `mean_energy_gap_pct_bill_tz=4.396`, `pg_above_pgtol_tz=8`, LOO `0.804 %`; sub-problem null `null_flat_mean_gap_sek_tz=0.1411` (`D0/race_grid.py --tz 1 --dhw 0 --random 3 --cfg <35 L manual valve> --state <32 C>`) | 6.24 / 1.000 | bug | All exact. Perturbation (tank 35 L -> 750 L) executed: `mean_gap_sek_tz` 1.1333 -> **0.2047** (the finder's stated value to four decimals), `max_gap_sek_tz` 4.1884 -> 1.1506. Not void. **See the null-control adjudication below.** **Seat 1's stack-reproducibility attack fails on my measurement**: on numpy 2.4.6 / scipy 1.17.1 (`tvofi-bookish-pancake/.venv`) the finding still reproduces — `cells_with_gap_tz=5`, `max_gap_sek_tz=3.6364`, LOO 0.496 % — it does not collapse to 0.0000; magnitudes move ~13-15 %, the defect does not. And the null is *cleaner* on that stack (`null_flat_mean_gap_sek_tz=0.0000`). **Weakened by #208 but not fixed**: on judge-main `cells_with_gap_tz=3`/8, `mean_gap_sek_tz=0.5686` (halved), LOO 0.131 % — yet `max_gap_sek_tz=4.1884` is *identical to baseline*. The worst cell is untouched. |
| D1-01 | medium | **verified** | `notready_eager.leaked_listeners=10` after 5 retries, `leaked_mqtt_subs=5`, `zombie_coordinators=5`, `zombie_handler_runs=5` (`D1/lifecycle_realloop.py`) | 3.6 / 1.000 | bug | Exact on all four. Perturbation/null is the harness's own `notready_guards_off_eager` arm and it goes to **0 on every counter** — with the guards off and the MQTT topic empty nothing is registered before the first refresh and nothing leaks. Not void. |
| D1-02 | medium | **verified**, one detail corrected | `midsolve_eager.sched_zombie_service_calls=3`, `sched_zombie_actuations=1`, `sched_zombie_saves=2`, `sched_shutdown_returned_before_release=1` (same harness) | 3.6 / 1.000 | bug | The headline count reproduces exactly. **Two corrections.** (1) The service-call detail is `switch.turn_off+mqtt.publish+mqtt.publish`, not `switch.turn_on+...` as the report says — a torn-down coordinator still actuates, but it turned the pump *off*. (2) The tolerance line claims "6 in the lazy arm"; I get `midsolve_lazy.sched_zombie_service_calls=3`, identical to the eager arm. Neither changes the finding: a coordinator whose `async_shutdown()` has returned issues three service calls and two store writes. |
| D1-03 | medium | **verified** | `fuzz.total_loader_raised=152` over 2000 mutants; `repeat_on_restart` 74 total (dhw_profile 64, thermal_learning 9, dhw_draws 1) (`D1/store_fuzz.py`) | 3.62 / 1.000 | bug | Exact, including the per-store split (price_model 57, accuracy 11, energy_totals 7, ledger 3). Null control passes: `identity_failures=0` for **all ten** stores, so the healthy payload never trips the fuzzer. Not void. |
| D1-04 | low | **verified** | `stuck_prices_fallback_steps=96` of 96, `stuck_prices_known_steps=0`, `solved=1`, `update_success=1`, `switch_calls=1`, `savings_pct=13.4`, `plan_stale=0` (`D1/staleness.py`) | 3.6 / 1.000 | bug | Exact on every counter. Null control is the `covering` arm and it is clean: `covering_prices_fallback_steps=0`, `known_steps=96`, savings 27.92 %. Not void. The panel's weakening was on reach, not on the number; low stands. |
| D1-05 | low | **verified** | `whatif_torn_fields=10` of a 10-field positive control (`D1/executor_race.py`) | 3.6 / n.a. | bug | Exact, and the per-container split reproduces exactly: defrost_learner 9, gains_profile 7, dhw_windows 9, draw_pattern 0, scalar writes 0. Null control passes: the deep-copying live path gives `live_torn_fields=0` against a 26-field positive control. Not void. `thread_factor` is meaningless for this harness (225.99) for the same executor-thread reason as D9-05. |
| D2-02 | medium | **verified** | `cop_flow_cells_nonmonotone=7` of 7; `cop_ratio_20_over_peak_min=0.8874` (flow 70), `flow55=0.9427` (`D2/cop_monotone.py`) | 2.25 / 1.000 | bug | Exact. LOO reproduces (`drop_most_favourable=0.9034`). **Perturbation executed**: `--perturb` (cop_flow_carnot=False) takes it 7 -> **0**. Null controls hold: `flow_temp=None` gives 0 sign changes and `compute_cop_dhw` 0 violations in both tank and outdoor temperature — only the Carnot flow branch turns over. Not void. |
| D2-03 | medium | **verified** | `steps_misaligned=84` on **all six** transition days (min = max = 84); spring 92 distinct instants over 23.00 h, autumn 25.00 h with a 75 min gap, `spring_plan_phantom_kwh=6.000` of 29.960 (`D2/dst_grid.py`) | 2.25 / 1.000 | bug | Exact on every day. **Perturbation executed**: `--perturb` (UTC stepping converted to local) takes all six days to **0**. Null control passes: the plain day 2026-08-26 gives 0 misaligned, 96 distinct instants, 24.00 h, 0 phantom kWh. Not void. |
| D2-04 | low | **verified at baseline; the first half is FIXED SINCE BASELINE BY #212, the second half is WORSE on main** | baseline `sysid_clean_confidence_30min=0.107` (ceiling 0.280) against the 0.300 gate, `15min=0.250`; **main `30min=0.445`, `15min=0.833`** (`D2/sysid_bias.py`) | 2.25 / 1.000 (baseline), 6.0 (main) | bug | Baseline reproduces exactly, including the drift arms (`drift_0.10Kph` mean confidence 0.304 with UA error -0.1216; `drift_0.15Kph` 0.341 / -0.2368) and the unbiasedness null (`white_0` UA bias +0.0000). Perturbation executed: 30 -> 15 min moves confidence 0.107 -> 0.250, **up**, as stated. Not void. **But the title is now half wrong.** On judge-main #212 lifted clean 30-minute confidence to **0.445**, clear of the 0.300 gate — "confidence cannot reach its adoption gate at the default interval" is **fixed**. The other half got sharply worse: a 0.10 K/h drifting sensor now scores `mean_confidence=1.000` (baseline 0.304) while carrying a **-14.2 %** UA bias (baseline -12.2 %). So on main a drifting sensor is adopted with certainty. The remaining finding should be re-titled to the bias half alone, and it is not low any more — I would raise it, but that is the panel's call and I record the number. |
| D2-05 | low | **verified** | `wood_share_max_jump=1.0000`, `wood_share_times_drawn_jump=13.4400 kW` (`D2/model_sanity.py`) | 2.25 / 1.000 | bug | Exact. **Perturbation executed**: `--perturb` (region 3 meets region 1 at the curve) takes the jump 1.0000 -> **0.0000**. `wood_share_vec_parity=0.000e+00` and `wood_share_range_ok=1` confirm the discontinuity is the only defect in that function. Not void. |
| D3-01 | medium | **verified** | `0` of 2 closure scripts fail with M31 applied (`D3/prescreen.py --ids M31`, entities.py rc=0, env_drift rc=0) | 8.2 / n.a. | hygiene | Exact. **Perturbation executed and decisive** — see the D3 perturbation note below: with seat 3's `verify3-assertions.patch` applied, `tests/entities.py` **fails rc=1** on M31 while the same patched tree without the mutant passes rc=0. The gap is real and the named check closes it. |
| D3-02 | medium | **verified** | `0` of 9 closure scripts fail with M19 applied | 8.2 / n.a. | hygiene | Exact. Perturbation: `tests/features.py` **rc=1** with M19 + assertions, rc=0 with assertions alone. The panel's mechanism correction stands (the branch is executed, just never asserted) — that makes it an assertion gap, not dead code, and half the finder's fix scope wrong. |
| D3-03 | medium | **verified** | `0` of 9 closure scripts fail with M13 applied | 8.2 / n.a. | hygiene | Exact. Perturbation: `tests/features.py` **rc=1** with M13 + assertions. Cheapest of the seven to close, as the panel says: the assertion exists, it has just never been fed a negative price. |
| D3-04 | low | **verified** | `0` of 9 closure scripts fail with M32 applied | 8.2 / n.a. | hygiene | Exact. Perturbation: `tests/features.py` **rc=1** with M32 + assertions. |
| D3-05 | low | **verified** | `0` of 9 closure scripts fail with M21 applied | 8.2 / n.a. | hygiene | Exact. Perturbation: `tests/features.py` **rc=1** with M21 + assertions. The panel's consequence correction stands: it does not abort setup, it silently kills one of twelve fire-and-forget loaders. |
| D3-06 | low | **verified** | `0` of 10 closure scripts fail with M30 applied | 8.2 / n.a. | hygiene | Exact. Perturbation: `tests/open_meteo.py` **rc=1** with M30 + assertions. |
| D3-07 | low | **verified** | `0` of 9 closure scripts fail with M15 applied | 8.2 / n.a. | hygiene | Exact. Perturbation: `tests/features.py` **rc=1** with M15 + assertions. |
| D3-10 | medium | **verified** | `458` leaves moved in `wood_coil` with `env_drift rc=0`, `drift=0`, `cache_hit=True` (`D3/prescreen.py --ids M01`, `logs/M01/env_drift.log`) | 8.2 / n.a. | bug | Exact. The log is unambiguous: `MAY-DRIFT wood_coil: 458 leaves moved`, then `1 MAY-DRIFT SCENARIO(S) MOVED, unjudged`, then `NO UNCLAIMED DRIFT: 55 scenario(s) checked` — and `rc=0`. A gate that prints the drift it found and then exits 0 is broken, not merely under-covered, so unlike D3-01..07 this one is a **bug**. M01 is separately killed by `tests/features.py` (rc=1), which is why it is not a suite-gap finding: the claim is specifically that the *drift* gate cannot fail on its five SENSITIVE fixtures, and that reproduces. |
| D4-01 | high | **verified**, and **not fixed by #220** | `font_px_lovelace=3.70 px` (floor 8), `renders_resize=0`, `font_px_attached=7.42 px` — **identical on judge-main** (`D4/first_paint_font.mjs`) | 5.16 / 1.000 (baseline), 6.01 (main) | bug | Exact against the ±0.05 px tolerance. The mandatory main re-check returns **byte-identical numbers** (3.70 / 0 / 7.42): PR #220 touched the card but did not touch this. `renders_resize=0` is the mechanism — the ResizeObserver fires and the card does not re-render — and it is what the perturbation would move. |
| D4-02 | high | **verified** (payload-sensitive digits) | `hit_small_24_nospacing=1880` (claim 1883, -0.16 %); `rect.slot=1344` **exact**, `rect.lane=476` (claim 367) (`D4/card_geometry.mjs`) | 4.84 / 1.000 | bug | The claim's tolerance says "exact for this payload", but the payload is regenerated by `tests/plan_view.py` and mine is not bit-identical to the finder's, so the aggregate lands 0.16 % low. The dominant term, `rect.slot`, reproduces **exactly at 1344**. The finding does not depend on the third digit: 1880 targets under 24 px with no spacing exception, smallest slot 1.3 px. `coarse_emulated=1` confirms the coarse arm really ran. |
| D4-03 | low | **verified** (payload-sensitive digits) | `text_overlap_pairs=1079` (claim 1039, +3.8 %) (same harness) | 4.84 / 1.000 | bug | Same payload caveat; the number moved *up*, not down. The panel replaced the mechanism and cut it to low; the count is not the load-bearing part of that judgement and I leave the severity where the panel put it. |
| D4-04 | medium | **verified** | `44.1 px` past the card box on `code@scope x` (largest non-SVG), **48 overflow rows** = 24 `code@scope x` + 24 `div.empty@scope x`; `div.empty` itself spills 48 px (same harness + `summarise.py no_plan`) | 4.84 / 1.000 | bug | 44.1 exact against the ±1 px tolerance, and the row count 48 exact. |
| D4-05 | medium | **verified** | `contrast_fail_light=891` (`contrast_fail=1209`, dark 318) | 4.84 / 1.000 | bug | **Exact.** |
| D4-06 | medium | **verified** | `300 tspan + 300 tspan.setup-value = 600` boxes below AA; `contrast_fail_inactive=105` | 4.84 / 1.000 | bug | **Exact on both.** |
| D4-07 | low | **verified** | `hit_small_44_coarse=548`, `coarse_emulated=1` | 4.84 / 1.000 | bug | **Exact.** The panel corrected the threshold, not the count. |
| D4-08 | low | **verified** | `series_below_3_light=3` of 7, `series_below_3_dark=0` (`D4/series_contrast.mjs`) | 5.16 / 1.000 | hygiene | **Exact.** |
| D4-09 | low | **verified** | `options_max_fields=23` (hot_water), `pages_over_15=5`, `user_page_fields=17`, `user_page_pickers=13`, `off_theme_fields=1` (`D4/config_flow_ux.py`) | 2.25 / 1.000 | hygiene | **Exact on all five.** |
| D4-11 | low | **verified**, and still true on main | `card_version_matches=0`, `version_delta=1.-2.-3` at baseline (CARD 5.4.17 vs 6.2.14); on judge-main `version_delta=1.-1.-16` vs 6.3.4 (`D4/card_version.mjs`) | 5.16 / 1.000 | hygiene | Exact. The gap has *widened* since the baseline — the card still announces 5.4.17 in a 6.3.4 release — which is the panel's "survives on its first half only" half. |
| D4-12 | low | **verified** | `ungrammatical_en=1`, `ungrammatical_sv=0` (`D4/delta_wording.mjs`) | 5.16 / 1.000 | hygiene | **Exact.** |
| D5-01 | low | **verified** | `tests_readme_drift=7` (`D5/reader_paths.py`) | 2.25 / 1.000 | hygiene | **Exact**, 7 of 36 fact checks, all seven in `tests/README.md`. |
| D5-02 | low | **verified** | `ecl110_guidance_contradiction=1` | 2.25 / 1.000 | hygiene | **Exact.** |
| D5-03 | low | **verified, number corrected UP: 4, not 3** | `unreachable_docs_from_readme=4` — `docs/audit-2026-08.md`, `docs/plan-card-decomposition.md`, `docs/plan-open-issues.md`, `tests/README.md` | 2.25 / 1.000 | hygiene | The finder reported 3 ("tests/README.md and two plan documents") and missed `docs/audit-2026-08.md`. I checked why rather than assuming a tree difference: at the baseline that file is named in `docs/backlog.md` three times (lines 380, 494, 501) but always inside backticks, never as a markdown link, so it is genuinely unreachable. The fix scope grows by one row. |
| D5-04 | low | **verified** | `content_defects_user_docs=5` (H1, H2, S1, C6, ST1) | 2.25 / 1.000 | hygiene | **Exact.** |
| D5-05 | low | **verified** | `constant_comment_mismatches_vetted=1` (raw 17, of 65 commented constants over 432 scanned) (`D5/comment_numbers.py`) | 2.25 / 1.000 | hygiene | **Exact**, including the raw figure. `docstring_default_mismatches_vetted=0` confirms the vetting is not swallowing real hits. |
| D6-01 | low | **verified** | `9` README sensor names differ from strings.json, of 55 (`D6/claims.py` row C040) | 2.31 / 1.000 | hygiene | **Exact**, and the nine names are the ones listed. |
| D6-02 | low | **verified** | services.yaml example `0.15` against const default `0.03`, \|Δ\| = 0.12 (row C093) | 2.31 / 1.000 | hygiene | **Exact.** |
| D6-03 | low | **verified** | `2` selector bounds rejected by the registered schema, of 39 (row C092): `inter_zone_heat_transfer` min 0.0 and `window_area` min 0 | 2.31 / 1.000 | hygiene | **Exact**, and C094 (the 25 documented ranges) comes back `true`, so the harness is discriminating. |
| D6-04 | low | **verified** | `breach_uncorrected=9.634` degree-hours below the comfort floor over 3 days, falling to `breach_learned=0.044` with the learner on (`D6/rolling_learning.py`) | 5.66 / 1.000 | hygiene | **Exact on both arms.** **Perturbation/null executed**: `D6_PLANT_ERROR=1.0` (the house *is* the model) gives `breach_uncorrected=0.000` and `breach_learned=0.000` — the number is entirely the mechanism's, none of it the harness's. Not void. The learner converges to `scale_end=1.3312` against a true plant error of 1.35 (overshoot -0.0188, last-quarter std 0.0077 over 287 samples), so the documented "6.7 degree-hours" figure in README and how-it-works is simply not this tree's number. |
| D6-05 | low | **verified** | `1` document contradicting `optimizer._compute_baseline_power`'s docstring (row C305, DISCLAIMER.md:71-72) | 2.31 / 1.000 | hygiene | **Exact**, and C303 (README:271) comes back `true`, so only DISCLAIMER is wrong — the harness separates the two. |
| D7-01 | medium | **verified at baseline; on main the harness's own positive control fails, so main is `not comparable`** | baseline `0` of 24 two-store cells admitted, positive control `control_admitted=4` of 8 with `control_abs_bias_pct_max=8.056 %` (`D7/sysid_plant.py`) | 3.66 / 1.000 | bug | Baseline exact. **Not fixed by #212 — but the main re-check cannot be read as the finding intends.** On judge-main the two-store count is still 0 of 24, *and* the positive control collapses to `control_admitted=0` of 8 with `control_abs_bias_pct_max=16.210 %`. When the control admits nothing, "0 admitted" no longer discriminates, so the main number is void as evidence for this finding — and is itself a regression worth its own look: after #212 the estimator admits **no plant at all**, first-order included. The baseline measurement stands on its own. |
| D7-02 | medium | **verified**, unchanged on main | `defrost_scale_tz_f50=1.095282` — **identical on judge-main** (`D7/learner_gates.py`) | 2.37 / 1.000 | bug | Exact to six decimals on both trees; #212 did not touch it. Null controls both hold on both trees: `defrost_scale_tz_f00=1.000000` and `defrost_scale_sz_f50=1.000000`. The AST census supports it (`ast_learners_without_defrost_gate=15`). |
| D7-03 | low | **verified at baseline; the external-heat half is FIXED SINCE BASELINE BY #212** | baseline `ingest_accuracy_record_external_heat=1` and `_open_window=1`; **main: external_heat=0**, open_window still **1** | 2.37 / 1.000 | bug | Baseline exact, and the null (`_pump_offline=0`, the arm the existing guard covers) holds on both trees. On judge-main the external-heat contamination is gated but the **open-window one is not** — half the finding is fixed, half survives, and the fix scope shrinks to the vent-CUSUM path. |
| D7-04 | low | **verified** | `tc_delta_abs_max=5.416717 SEK` (`D7/trajectory_order.py`) | 2.25 / 1.000 | hygiene | **Exact to 1e-6** against the stated tolerance, and the directional detail reproduces (`+5.416717` after coast, `-5.195302` after full, `-0.649172` after random). **Perturbation is in-run and passes**: the no-valve arm gives `null_delta_abs=0.000000` with `buffer_is_store_null_arm=0`. Not void. |
| D7-06 | low | **verified** | `dead_candidates=5` of 1062 defs (`D7/dead_code.py`) | 4.17 / 1.000 | hygiene | **Exact**, and the five names match the report exactly: `comfort_learning.py:ComfortLearner.set_configured:180`, `config_flow.py:_translated_text:890`, `coordinator.py:...optimization_result:1253`, `coordinator.py:...current_state:1363`, `presets.py:_floor_heated_area:162`. `started_by_suite=983`, `referenced_never_started=63`. |
| D8-01 | high | **verified** | `default_temperature_leaks=1132` over 85 cells x 2 cycles; `outdoor_default_published=10` (`D8/matrix.py`) | 4.8 / n.a. | bug | **Exact on both.** The config-side perturbation is in-run and passes: the `probes` cells (tank/buffer/lower/floor-return sensors configured) go to **0 leaks**, so the leak is the missing-reading path and not the entity layer. `exceptions=0`, `unknown_where_data_exists=0` and `nonfinite_attributes=0` in the same run show the harness is not simply flagging everything. |
| D8-02 | low | **verified** | `numpy_attribute_sites=3`, `unserialisable_attributes=3630`, `numpy_state=30` | 4.8 / n.a. | hygiene | **Exact on all three.** |
| D8-03 | low | **verified** | `schedule_truncated=170` (cell, cycle) pairs, 85/85 cells | 4.8 / n.a. | hygiene | **Exact.** |
| D9-03 | low | **verified** | `two_zone_dhw.scalar_steps_per_gradient=201.32` at baseline, 196.56 on main, against 96 batch rows (`D9/h1_grad_equivalents.py`) | 2.92 / 1.000 | bug | **Exact** against the "exact" tolerance. **Perturbation executed**: the one-entry memo on `simulate_trajectory` takes it 201.32 -> **100.66** (equivalents 297.32 -> 196.66), down, while the null arm `batch_rows_per_gradient` stays at **96** untouched — exactly the arm the memo must not move. Not void. Reproduces on main too (196.56 -> 98.45 under the memo). |
| D9-04 | low | **verified** | `single_zone_dhw.planner_share_of_solve=0.6318` (claim 0.6296, tolerance ±15 %); `simulate_dhw_only_per_planning_call=64`, `tank_steps_per_planning_call=6144` (`D9/h1b_dhw_loops.py`) | 3.5 / 1.000 | bug | Share reproduced; the counts are **exact**. **Perturbation executed**: horizon 24 h -> 48 h moves `simulate_dhw_only_per_planning_call` 64 -> **118**, tank steps 6144 -> 22,656, `planner_over_reference` 4.91 -> **13.77** — up, as stated. Not void. **Leave-one-out re-run**: the five cells give `planner_over_reference` 4.911 / 4.294 / 3.733 / 2.380 / 1.904, mean 3.444; dropping the most favourable (4.911) leaves **3.078**, and the worst cell is still 1.90x a reference solve. The panel's framing correction is right — lead with `planner_over_reference`, not the 63 % share, which is 63 % of the cheapest solve. |

### The D3 perturbation, and a trap in running it

The seven suite-gap findings ask for the same perturbation: add the named check
and watch the mutant die. **`prescreen.py` cannot be used to run it.** It
`git reset`s the worktree to the baseline SHA before committing each mutant, so
a patch committed on top is silently discarded — my first attempt reported M31
still surviving and the new assertion never appeared in the run log. I ran it
directly instead: reset to c398fc8, apply `mutants/M<k>.patch`, apply
`verify3-assertions.patch`, run the one script the assertion lives in.

```
PERTURB NONE tests/features.py    rc=0     <- controls: the assertions alone pass
PERTURB NONE tests/entities.py    rc=0
PERTURB NONE tests/open_meteo.py  rc=0
PERTURB M19  tests/features.py    rc=1     <- D3-02
PERTURB M13  tests/features.py    rc=1     <- D3-03
PERTURB M32  tests/features.py    rc=1     <- D3-04
PERTURB M21  tests/features.py    rc=1     <- D3-05
PERTURB M15  tests/features.py    rc=1     <- D3-07
PERTURB M31  tests/entities.py    rc=1     <- D3-01
PERTURB M30  tests/open_meteo.py  rc=1     <- D3-06
```

Seven for seven, against three clean controls. This is the strongest
perturbation in the round: it does not merely move a number, it demonstrates
that each named check is sufficient to close its gap, so no fixer has to guess.

### D0-03: which null control is the right one

The panel left this to me, and it changes the finding's title, so here is the
decision and the reason.

**Seat 3's definition is the right control. D0-03 passes its null control, the
title stands, and the magnitude must be quoted from the sub-problem race, not
from the closed loop.**

The two definitions:

- **Seat 3** — the sub-problem objective at flat prices on the *identical
  recorded call*: same closure, same bounds, same args, comfort parity checked.
  My number: `null_flat_mean_gap_sek_tz=0.1411` SEK (0.13 % of objective) on
  the finder's stack, and **0.0000** on numpy 2.4.6 / scipy 1.17.1.
- **Seat 2** — the closed-loop realised bill at flat prices over 3 days at the
  30-minute re-plan. I rebuilt this, because seat 2's `consequence.py` was
  never committed to the register: `j0_rolling_cfg.py`, the register's own
  `rolling_gap.py` with `--cfg` / `--state` passthrough added. My numbers:
  **3.1555 SEK/day (4.107 % of bill) at flat prices**, against 5.3926 SEK/day
  (8.556 %) priced. So seat 2's effect is real and in the direction claimed.

And yet it is not a control, for three reasons my own run shows:

1. **It does not hold the terminal state fixed.** The settlement prices the
   buffer tank only (`settlement_full_tank_convention=+0.6003 SEK`); the room
   and slab are unsettled. The challenger arm ends the flat run **0.3975 K
   colder on mean** and 0.1647 K colder at the end. A large part of the
   "saving" is heat it simply never put into the fabric.
2. **At flat prices the challenger is worse by the optimizer's own cost
   function.** `objective_sum_improved=3774.103` against
   `objective_sum_production=3756.009`. A challenger that loses on the summed
   objective while winning on the realised bill is measuring stored energy, not
   optimisation quality. (Priced, the ordering is the normal way round:
   3098.131 against 3103.345.)
3. **Seat 2's own priced run failed parity** — its report carries
   `violation_delta_kh=0.00537 parity_ok=0`, the challenger breaching comfort
   *more* than production. A gain bought with comfort is not a gain, which is
   the rule the register already applies elsewhere.

A null control has to vary exactly the thing under test — here the price
spread — and hold everything else fixed. Seat 3's does. Seat 2's varies the
price spread, the terminal thermal state and the comfort trajectory at once,
and settles only one of the three. So the flat-price residual it reports is not
evidence that the defect survives flat prices; it is evidence that the
instrument leaks.

Consequences for the register: **the title does not change** — this remains a
cap-tightened re-solve stopping at a kink, and it is price-spread dependent.
The consequence should be quoted as the parity-checked sub-problem gap
(mean 1.1333 SEK, max 4.1884 SEK, LOO 0.804 % of objective), not as seat 2's
2.28-2.85 SEK/day, and **not** as the closed-loop figure at all. Medium stands.




### #291 (the 2.3x solve regression since the baseline): attributed to #208

The coordinator asked for a bisect of `c398fc8..origin/main` if I had capacity.
I did, and I bisected on work rather than on wall — `h1_grad_equivalents.py`'s
`two_zone_dhw.simulate_step_calls` is deterministic and contention-immune, so
two runs settled what six timing runs would have argued about:

| tree | `simulate_step_calls` | `solve_over_reference` |
|---|---|---|
| c398fc8 (baseline) | 20,736 | 37.99 |
| 4ed3af3 (#208's parent) | **20,736** | 36.34 |
| 38dc061 (**#208**) | **53,856** | 75.37 |
| origin/main | **53,856** | 91.39 |

2.597x in one commit, byte-identical from there to main. It is **#208's
intended cost landing harder than its notes claimed**, not a separate defect:
"refine every candidate" is what 2.6x of extra `simulate_step` looks like. The
trade it bought is visible in my own Part-2 re-checks (D0-02's restart gap
0.0519 -> 0.0063, D0-03's mean gap 1.1333 -> 0.5686), so it is a real trade —
but it compounds with D9-05, whose starvation now runs for 1.65 s per solve
instead of 0.71 s with longest holds of 245-361 ms instead of 52-53 ms.
`solve_over_reference` keeps climbing after #208 while the step count does not,
so later commits made each step dearer; that is a smaller separate effect I did
not chase.

### On the gate lock

I never held `/tmp/hpo-gate.lock`. It was already present at 22:33 with no
process behind it when my first `mkdir` at 22:57 returned `File exists`; my
retry loop ran for the whole of Part 1 and never acquired it, so
`lock.status` was never written. Throughout Part 1 `ps` showed no `run.sh`,
`stress.py`, `golden.py`, `env_drift.py`, `prescreen.py` or node harness on
the box — the lock is **stale**, left by a session that exited without
releasing it. The contract says never remove a lock one did not create, so I
did not; whoever owns it (or the coordinator) can clear it safely, as nothing
is running behind it.

---

## Machine-readable verdicts

```json
{
  "D0-01": {
    "verdict": "verified",
    "severity": "medium",
    "number": "cells_with_gap_sz=15/16; mean_energy_gap_pct_bill_sz=2.517; mean_restart_gap_sek_sz=0.1661; LOO 2.192 % of objective; unchanged in kind on main (max_gap 58.2850 identical)",
    "stop_rule_class": "bug"
  },
  "D0-02": {
    "verdict": "verified",
    "severity": "low",
    "number": "restart_improves_tz=15/80; mean_restart_gap_sek_tz=0.0519; LOO 0.232 %; energy-gap component FAILS its flat null (0.1553 flat vs 0.1022 priced)",
    "stop_rule_class": "bug"
  },
  "D0-03": {
    "verdict": "verified",
    "severity": "medium",
    "number": "mean_gap_sek_tz=1.1333, max 4.1884, LOO 0.804 %; passes its null on seat 3's definition (null_flat 0.1411; 0.0000 on numpy 2.4.6)",
    "stop_rule_class": "bug"
  },
  "D1-01": {
    "verdict": "verified",
    "severity": "medium",
    "number": "notready_eager.leaked_listeners=10 after 5 retries (mqtt_subs 5, zombie coordinators 5); guards-off arm 0",
    "stop_rule_class": "bug"
  },
  "D1-02": {
    "verdict": "verified",
    "severity": "medium",
    "number": "midsolve_eager.sched_zombie_service_calls=3 (switch.turn_off+2x mqtt.publish), zombie_actuations=1, zombie_saves=2",
    "stop_rule_class": "bug"
  },
  "D1-03": {
    "verdict": "verified",
    "severity": "medium",
    "number": "fuzz.total_loader_raised=152 of 2000 mutants; repeat_on_restart 74; identity_failures 0/10 stores",
    "stop_rule_class": "bug"
  },
  "D1-04": {
    "verdict": "verified",
    "severity": "low",
    "number": "stuck_prices_fallback_steps=96/96 with solved=1, switch_calls=1; covering arm 0",
    "stop_rule_class": "bug"
  },
  "D1-05": {
    "verdict": "verified",
    "severity": "low",
    "number": "whatif_torn_fields=10 of a 10-field control; live arm 0",
    "stop_rule_class": "bug"
  },
  "D2-02": {
    "verdict": "verified",
    "severity": "medium",
    "number": "cop_flow_cells_nonmonotone=7/7; cop_ratio_20_over_peak_min=0.8874; perturb -> 0",
    "stop_rule_class": "bug"
  },
  "D2-03": {
    "verdict": "verified",
    "severity": "medium",
    "number": "steps_misaligned=84 on all six transition days; plain day 0; perturb -> 0",
    "stop_rule_class": "bug"
  },
  "D2-04": {
    "verdict": "verified (bias half); gate half fixed since baseline by #212",
    "severity": "low",
    "number": "baseline clean confidence 0.107 vs 0.300 gate; on main 0.445 (gate half fixed) but drift_0.10Kph confidence 0.304 -> 1.000 with UA bias -12.2 % -> -14.2 %",
    "stop_rule_class": "bug"
  },
  "D2-05": {
    "verdict": "verified",
    "severity": "low",
    "number": "wood_share_max_jump=1.0000 (13.44 kW drawn); perturb -> 0.0000",
    "stop_rule_class": "bug"
  },
  "D3-01": {
    "verdict": "verified",
    "severity": "medium",
    "number": "0 of 2 closure scripts fail on M31; with the named check added, entities.py rc=1",
    "stop_rule_class": "hygiene"
  },
  "D3-02": {
    "verdict": "verified",
    "severity": "medium",
    "number": "0 of 9 closure scripts fail on M19; with the named check added, features.py rc=1",
    "stop_rule_class": "hygiene"
  },
  "D3-03": {
    "verdict": "verified",
    "severity": "medium",
    "number": "0 of 9 closure scripts fail on M13; with the named check added, features.py rc=1",
    "stop_rule_class": "hygiene"
  },
  "D3-04": {
    "verdict": "verified",
    "severity": "low",
    "number": "0 of 9 closure scripts fail on M32; with the named check added, features.py rc=1",
    "stop_rule_class": "hygiene"
  },
  "D3-05": {
    "verdict": "verified",
    "severity": "low",
    "number": "0 of 9 closure scripts fail on M21; with the named check added, features.py rc=1",
    "stop_rule_class": "hygiene"
  },
  "D3-06": {
    "verdict": "verified",
    "severity": "low",
    "number": "0 of 10 closure scripts fail on M30; with the named check added, open_meteo.py rc=1",
    "stop_rule_class": "hygiene"
  },
  "D3-07": {
    "verdict": "verified",
    "severity": "low",
    "number": "0 of 9 closure scripts fail on M15; with the named check added, features.py rc=1",
    "stop_rule_class": "hygiene"
  },
  "D3-10": {
    "verdict": "verified",
    "severity": "medium",
    "number": "wood_coil 458 leaves moved and env_drift still exits rc=0 (drift=0, 'NO UNCLAIMED DRIFT: 55 scenario(s) checked')",
    "stop_rule_class": "bug"
  },
  "D4-01": {
    "verdict": "verified",
    "severity": "high",
    "number": "font_px_lovelace=3.70 px against an 8 px floor, renders_resize=0, font_px_attached=7.42 - byte-identical on main, so #220 did not fix it",
    "stop_rule_class": "bug"
  },
  "D4-02": {
    "verdict": "verified",
    "severity": "high",
    "number": "hit_small_24_nospacing=1880 (claim 1883, payload-sensitive); rect.slot=1344 exact",
    "stop_rule_class": "bug"
  },
  "D4-03": {
    "verdict": "verified",
    "severity": "low",
    "number": "text_overlap_pairs=1079 (claim 1039, payload-sensitive)",
    "stop_rule_class": "bug"
  },
  "D4-04": {
    "verdict": "verified",
    "severity": "medium",
    "number": "44.1 px past the card box on code@scope x; 48 overflow rows (24 code + 24 div.empty)",
    "stop_rule_class": "bug"
  },
  "D4-05": {
    "verdict": "verified",
    "severity": "medium",
    "number": "contrast_fail_light=891 (exact)",
    "stop_rule_class": "bug"
  },
  "D4-06": {
    "verdict": "verified",
    "severity": "medium",
    "number": "300 tspan + 300 tspan.setup-value = 600 below AA; inactive 105 (exact)",
    "stop_rule_class": "bug"
  },
  "D4-07": {
    "verdict": "verified",
    "severity": "low",
    "number": "hit_small_44_coarse=548 with coarse_emulated=1 (exact)",
    "stop_rule_class": "bug"
  },
  "D4-08": {
    "verdict": "verified",
    "severity": "low",
    "number": "series_below_3_light=3 of 7, dark 0 (exact)",
    "stop_rule_class": "hygiene"
  },
  "D4-09": {
    "verdict": "verified",
    "severity": "low",
    "number": "options_max_fields=23, pages_over_15=5, user_page_fields=17, pickers=13, off_theme_fields=1 (exact)",
    "stop_rule_class": "hygiene"
  },
  "D4-11": {
    "verdict": "verified",
    "severity": "low",
    "number": "card_version_matches=0; delta widened to 1.-1.-16 against 6.3.4 on main",
    "stop_rule_class": "hygiene"
  },
  "D4-12": {
    "verdict": "verified",
    "severity": "low",
    "number": "ungrammatical_en=1, sv=0 (exact)",
    "stop_rule_class": "hygiene"
  },
  "D5-01": {
    "verdict": "verified",
    "severity": "low",
    "number": "tests_readme_drift=7 of 36 fact checks (exact)",
    "stop_rule_class": "hygiene"
  },
  "D5-02": {
    "verdict": "verified",
    "severity": "low",
    "number": "ecl110_guidance_contradiction=1 (exact)",
    "stop_rule_class": "hygiene"
  },
  "D5-03": {
    "verdict": "verified, number corrected up",
    "severity": "low",
    "number": "unreachable_docs_from_readme=4, not 3: docs/audit-2026-08.md is named only inside backticks in docs/backlog.md, never as a link",
    "stop_rule_class": "hygiene"
  },
  "D5-04": {
    "verdict": "verified",
    "severity": "low",
    "number": "content_defects_user_docs=5 (H1,H2,S1,C6,ST1) (exact)",
    "stop_rule_class": "hygiene"
  },
  "D5-05": {
    "verdict": "verified",
    "severity": "low",
    "number": "constant_comment_mismatches_vetted=1 (raw 17 of 65 commented constants) (exact)",
    "stop_rule_class": "hygiene"
  },
  "D6-01": {
    "verdict": "verified",
    "severity": "low",
    "number": "9 README sensor-table names differ from strings.json, of 55 (exact)",
    "stop_rule_class": "hygiene"
  },
  "D6-02": {
    "verdict": "verified",
    "severity": "low",
    "number": "services.yaml example 0.15 vs const default 0.03, |delta| 0.12 (exact)",
    "stop_rule_class": "hygiene"
  },
  "D6-03": {
    "verdict": "verified",
    "severity": "low",
    "number": "2 of 39 number-selector bounds rejected by the registered schema (exact)",
    "stop_rule_class": "hygiene"
  },
  "D6-04": {
    "verdict": "verified",
    "severity": "low",
    "number": "breach_uncorrected=9.634 degree-hours -> breach_learned=0.044; null D6_PLANT_ERROR=1.0 gives 0.000/0.000 (exact)",
    "stop_rule_class": "hygiene"
  },
  "D6-05": {
    "verdict": "verified",
    "severity": "low",
    "number": "1 document (DISCLAIMER.md:71-72) contradicts _compute_baseline_power; README C303 comes back true (exact)",
    "stop_rule_class": "hygiene"
  },
  "D7-01": {
    "verdict": "verified",
    "severity": "medium",
    "number": "0 of 24 two-store cells admitted at baseline with a positive control of 4/8 at <=8.06 % bias; on main the control itself collapses to 0/8, so main is not comparable",
    "stop_rule_class": "bug"
  },
  "D7-02": {
    "verdict": "verified",
    "severity": "medium",
    "number": "defrost_scale_tz_f50=1.095282, identical on main; nulls f00=1.000000 and single-zone 1.000000 hold on both",
    "stop_rule_class": "bug"
  },
  "D7-03": {
    "verdict": "verified (open-window half); external-heat half fixed since baseline by #212",
    "severity": "low",
    "number": "baseline external_heat=1 and open_window=1; on main external_heat=0, open_window still 1",
    "stop_rule_class": "bug"
  },
  "D7-04": {
    "verdict": "verified",
    "severity": "low",
    "number": "tc_delta_abs_max=5.416717 SEK (exact to 1e-6); no-valve null 0.000000",
    "stop_rule_class": "hygiene"
  },
  "D7-06": {
    "verdict": "verified",
    "severity": "low",
    "number": "dead_candidates=5 of 1062 defs; the five names match exactly",
    "stop_rule_class": "hygiene"
  },
  "D8-01": {
    "verdict": "verified",
    "severity": "high",
    "number": "default_temperature_leaks=1132 over 85 cells x 2 cycles; outdoor_default_published=10; probes cells 0",
    "stop_rule_class": "bug"
  },
  "D8-02": {
    "verdict": "verified",
    "severity": "low",
    "number": "numpy_attribute_sites=3, unserialisable_attributes=3630, numpy_state=30 (exact)",
    "stop_rule_class": "hygiene"
  },
  "D8-03": {
    "verdict": "verified",
    "severity": "low",
    "number": "schedule_truncated=170 (cell,cycle) pairs, 85/85 cells (exact)",
    "stop_rule_class": "hygiene"
  },
  "D9-01": {
    "verdict": "verified",
    "severity": "high",
    "number": "9221.55 equivalents/gradient vs 297.32 batched (31.0x) at baseline, 9220.20 vs 292.56 on main; fuse_guard drift 177 fields at PRECISION=6",
    "stop_rule_class": "bug"
  },
  "D9-02": {
    "verdict": "verified",
    "severity": "medium",
    "number": "smallest_detectable_uniform_regression=4.728; an injected uniform 2x trips 0 per-scenario and 0 sweep checks",
    "stop_rule_class": "hygiene"
  },
  "D9-03": {
    "verdict": "verified",
    "severity": "low",
    "number": "two_zone_dhw.scalar_steps_per_gradient=201.32 (exact); memo perturbation -> 100.66 with batch rows unchanged at 96",
    "stop_rule_class": "bug"
  },
  "D9-04": {
    "verdict": "verified",
    "severity": "low",
    "number": "single_zone_dhw.planner_share_of_solve=0.6318; 64 simulate_dhw_only and 6144 tank steps per planning call; LOO planner_over_reference 3.078",
    "stop_rule_class": "bug"
  },
  "D9-05": {
    "verdict": "verified",
    "severity": "medium",
    "number": "starvation share 0.9589 baseline / 0.9814 main on two_zone_dhw, 0.9988 on the capped solve; longest hold 53 ms baseline, 245-361 ms main; idle null 0.00-0.03",
    "stop_rule_class": "bug"
  }
}
```
