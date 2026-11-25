# D3-s1, box D3-m5: D3.M5 resource use (round 11, resume slice)

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`. box D3-m5: Linux 6.18 x86_64, nproc 4, Intel(R) Xeon(R) Processor @ 2.10GHz, 16 GB, venv-ci CPython 3.14.7 (numpy 2.5.4, scipy 1.18.1), node v22.23.5, alone on the box. Every wall/CPU/RSS figure is
**provisional** (the judge re-takes it); counts are final. D3-s1-01 (env_drift's capture
child drops the reach hook) is already judged and is cited here, not re-reported.

## Method

R0 restored the carried evidence from `c0adbc19` (no box checkpoint existed). R1 re-took
every driver's traced baseline on this box (21/21 green), re-traced env_drift's capture
child, and re-ran both controls: null LIVES over 16 drivers, positive 2/2 KILLED by
`tests/manual_plan.py`. Then D3.M5 (a) to (e), with nothing else running during (a).

Universe: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/enumerate.py --scripts`, 27 closure scripts reaching the cells; all 27 examined.
Redispatched C1, C4, C7, C9: examined.

## Rows carried for D3.M1 to D3.M4

M1 1260/1260 and M4 35/35 as carried. M2 34/1260 as carried; the remainder is assigned to boxes D3-u1a, D3-u1b, D3-u1c, D3-u1d. M3: this box's matrix is the full net on all 35 survivors (19 killed, 16 survive); C3, the top-six full gate, is assigned to box D3-top6.

Full net, no early stop, every closure script of the file (27 incl. stress alone, golden strict, card scripts behind plan_view), on all 35 survivors: it is box D3-m5's M5(b) kill matrix, whose mutant set contains every SURVIVED verdict under results/{pre,c2,c3c6} (PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/m5_matrix.py table -v; drives under state/results/matrix and matrix-stress, D3S1_RELAX=0). 19 of 35 killed (features.py 18 of them; harness_headers.py alone kills thermal_model.py:270, by SIGXCPU in an audit harness, features.py timing out on it), 16 survive every script: coordinator.py:8806 M04, dhw_planner.py:1559 M19, flow_lift.py:47 CONST, :183 GUARD_OFF, :188 M35, grid_fee.py:173 GUARD_OFF, :355 M36, :383 M21, optimizer.py:773 GUARD_OFF, price_model.py:252 M34, :337 M25, sysid.py:610 GUARD_OFF, tariff.py:744 M31, thermal_model.py:169 GUARD_OFF, :835 M03, :2593 M07. Of the carried top six, tariff.py:64, price_model.py:201, coordinator.py:539, sysid.py:2246 M27 and sysid.py:1549 M26 are KILLED by tests/features.py; tariff.py:744 M31 survives. C3, the GATE_SCOPE=full GOLDEN_MODE=drift gate for the top six, is not driven here (assigned to box D3-top6). C5 answered by the carried run's REPORT.md. Counts exact; seconds provisional. 

## (a) Quiet-box gate table

`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/m5_gate_table.py` (one script at a time, GATE_JOBS=1 shape, fresh worktree of HEAD,
GOLDEN_REF=HEAD^1; .mjs rows after their producer plan_view.py, timed separately).

| script | rc | wall s | CPU s | recorded s | wall/recorded | load1 |
|---|---|---|---|---|---|---|
| tests/arch_score_head.py | 0 | 43.4 | 42.8 | 31.8 | 1.36 | 0.73 |
| tests/backtest.py | 0 | 56.7 | 55.6 | 61.6 | 0.92 | 0.87 |
| tests/block_duty.py | 0 | 7.3 | 7.0 | 8.3 | 0.88 | 0.95 |
| tests/boost_drift_replay.py | 0 | 178.7 | 153.7 | 341.1 | 0.52 | 0.96 |
| producer:tests/plan_view.py | 0 | 0.7 | 0.7 | 1.8 | 0.39 | 0.81 |
| tests/card.mjs | 0 | 87.0 | 93.5 | 82.3 | 1.06 | 0.81 |
| producer:tests/plan_view.py | 0 | 0.8 | 0.8 | 1.8 | 0.44 | 1.04 |
| tests/card_drift.mjs | 0 | 4.0 | 5.1 | 6.0 | 0.67 | 1.04 |
| tests/config_flow_steps.py | 0 | 17.5 | 17.1 | 32.5 | 0.54 | 1.04 |
| tests/debug_collect.py | 0 | 1.1 | 0.9 | 1.5 | 0.73 | 1.1 |
| tests/deployment_shape.py | 0 | 2.2 | 2.1 | 3.3 | 0.67 | 1.1 |
| tests/doc_claims.py | 0 | 9.6 | 9.6 | 11.4 | 0.84 | 1.1 |
| tests/edge.py | 0 | 21.6 | 20.7 | 21.5 | 1.0 | 1.08 |
| tests/entities.py | 0 | 507.7 | 512.3 | 867.9 | 0.58 | 1.06 |
| tests/env_drift.py | 0 | 96.4 | 92.8 | 1.0 | 96.4 | 1.04 |
| tests/features.py | 0 | 790.6 | 732.5 | 473.9 | 1.67 | 0.93 |
| tests/finite_boundary.py | 0 | 90.6 | 89.8 | 90.4 | 1.0 | 0.92 |
| tests/golden.py | 1 | 96.9 | 94.3 | 1.2 | 80.75 | 0.98 |
| tests/guard_pins.py | 0 | 4.5 | 4.4 | 8.2 | 0.55 | 0.91 |
| tests/harness_headers.py | 0 | 144.0 | 138.5 | 327.6 | 0.44 | 0.91 |
| tests/manual_plan.py | 0 | 5.8 | 4.9 | 6.5 | 0.89 | 0.94 |
| tests/optimality.py | 0 | 101.1 | 95.9 | 142.5 | 0.71 | 0.94 |
| tests/plan_view.py | 0 | 0.8 | 0.7 | 1.8 | 0.44 | 0.99 |
| tests/solar_alignment.py | 0 | 0.6 | 0.6 | 1.2 | 0.5 | 0.99 |
| tests/stress.py | 0 | 285.6 | 296.5 | 463.0 | 0.62 | 0.99 |
| tests/structure.py | 0 | 18.7 | 18.5 | 21.1 | 0.89 | 1.04 |
| tests/typing_ruler.py | 0 | 18.5 | 18.7 | 20.8 | 0.89 | 1.03 |
| tests/validate.py | 0 | 21.0 | 20.0 | 21.5 | 0.98 | 1.02 |
| tests/wood_advisor.py | 0 | 0.6 | 0.6 | 1.4 | 0.43 | 1.01 |
| tests/env_drift.py[strict] | 0 | 61.9 | 59.8 | 1.0 | 61.9 | 1.01 |
| tests/env_drift.py[nocache] | 0 | 197.2 | 191.4 | 1.0 | 197.2 | 0.92 |

(a) PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/m5_gate_table.py --out dev/audit/rounds/round11/D3/s1/state/gate_table.jsonl (GATE_JOBS=1 shape, one script at a time, fresh worktree of HEAD, GOLDEN_REF=HEAD^1): all 27 closure scripts timed; sum wall 2612.5 s, CPU 2529.1 s vs closures.json recorded 3051.3 s; load1 0.73-1.10 per row; thread_factor 1.00; nproc 4, Intel Xeon @ 2.10GHz. Outside closure.py's SECONDS_BAND (0.5x-2x): env_drift.py 1.0 s recorded vs 96.4 s measured warm --all (61.9 s strict form, 197.2 s cold DRIFT_NO_CACHE), golden.py 1.2 s vs 96.9 s strict (both record the documented stub, #934), harness_headers.py 0.44x, plan_view.py 0.44x, wood_advisor.py 0.43x; every other row 0.52x-1.67x. Top costs: features 790.6 s wall / 732.5 s CPU, entities 507.7/512.3, stress 285.6/296.5, boost_drift_replay 178.7/153.7, harness_headers 144.0/138.5. golden.py strict is red at baseline here (55 of 56 GOLDEN SCENARIOS CHANGED: fixtures from another machine); all other 26 rc=0. All seconds provisional. 

## (b) Kill-overlap matrix

(b) PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/m5_matrix.py table -v (drives: D3S1_RELAX=0 prescreen.py run --full --mutants dev/audit/rounds/round11/D3/s1/matrix_mutants.json --sub matrix, 4 workers, then --sub matrix-stress, stress.py alone): 38 mutants (C2 12, C3/C6 8, every SURVIVED under results/{pre,c2,c3c6}, de-duplicated) x every closure script of each mutant's file, 27 script columns incl. golden.py strict, card.mjs/card_drift.mjs behind plan_view.py, edge, backtest, stress: 921 pairs = 33 killed, 587 ran-and-survived, 300 reach-skipped (gate's own reach_skip), 1 timeout (features.py on thermal_model.py:270), 0 relaxed skips. 22 mutants killed, 16 survive every closure script; duplicate kills 11 (mutants with 1/2/3/6 killers: 16/4/1/1). Kills: features 21 (15 unique), harness_headers 4 (1 unique: thermal_model.py:270, SIGXCPU in an audit harness), entities 3, env_drift 2, finite_boundary 1, optimality 1, stress 1 (0 unique each). 25 of 27 scripts kill no mutant another script misses on this sample (incl. entities.py 20550 s summed over 38 runs, env_drift.py 3952 s, golden.py 3838 s, stress.py 4692 s over 17). Perturbation: --drop tests/features.py raises survivors 16 -> 31 (its 15 unique kills); --drop tests/entities.py leaves 16 (null). env_drift ran on 21 mutants whose line its --capture --all child never executes and killed 0 of them (D3-s1-01, cited, not re-reported). Survivors of the full no-early-stop net (data for the boxes owning M3): coordinator.py:8806 M04, dhw_planner.py:1559 M19, flow_lift.py:47 CONST, :183 GUARD_OFF, :188 M35, grid_fee.py:173, :355 M36, :383 M21, optimizer.py:773, price_model.py:252 M34, :337 M25, sysid.py:610, tariff.py:744 M31, thermal_model.py:169, :835 M03, :2593 M07. Counts exact; seconds provisional. 

Per-script columns: `state/m5box-matrix-table.out`.

## (c) Checks per solve

(c) PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/m5_solves.py --hastub-hook --scripts tests/stress.py,tests/env_drift.py (+ plain arm, + --double-solve arm): stress.py 116 checks / 240 HeatPumpOptimizer.optimize solves = 0.48 checks per solve (21 processes; the gate's PYTHONPATH-prepended hook sees 140, the parent's own: 100 solves run in children that rebuild PYTHONPATH); env_drift.py --all 112 checks (56 scenarios + 56 committed fixtures) / 100 solves cold (50 per side) = 1.12, warm cache (tree side only) 112/50 = 2.24; plain hook sees 0 solves. Perturbation --double-solve: env_drift 100 -> 200 solves, checks flat. Carried (state/solves.jsonl): boost_drift_replay 46/789 = 0.058, edge 0.95, backtest 2.27, optimality 3.65, manual_plan 4.26, features 12.0, block_duty 25.5, entities 82.5. 

## (d) Closure over-approximation, boost_drift_replay and stress

(d) PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/m5_trace_hastub.py --scripts tests/stress.py,tests/env_drift.py,tests/golden.py,tests/boost_drift_replay.py (+ --plain arm) and PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/m5_closure_reach.py: boost_drift_replay's closure holds all 12 cell files and its traced run executes lines in all 12 (5849 lines; reach clean, 2 processes 2 recorded); stress.py's closure holds 6 cell files (optimizer, thermal_model, flow_lift, batchmath, tariff, dhw_planner) and its run executes all 6 (5189 lines; 21/21 processes recorded under the hastub hook, 24 started / 12 recorded under the gate's own hook). over_approx_pairs 0 for both; 0 of 245 closure pairs over the 22 traced drivers (m5_closure_reach.py, baselines re-taken on this box). File-level closures do not over-approximate for these two; the gate reach row of stress.py is refused (children uncounted), a further seam of D3-s1-01's property. 

## (e) card.mjs, card_drift.mjs, golden.py, stress.py

(e) card.mjs executes no Python (its cell reach is its producer plan_view.py's, 5144 cell lines), costs 87.0 s wall / 93.5 s CPU (+0.7 s producer), killed 0 of the 10 matrix mutants plan_view executes; card_drift.mjs: same producer reach, 4.0 s / 5.1 s, killed 0 of 10, and PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/m5_card_drift_payload.py shows it cannot move on a production edit (finding D3-s1-52); golden.py strict executes 7969 cell lines in all 12 files (same set as env_drift's capture), costs 96.9 s / 94.3 s, red at baseline here (55/56), killed 0 of 38 (CI runs drift mode: tests.yml:374, nightly.yml:496); stress.py executes 5189 lines in its 6 cell files, costs 285.6 s / 296.5 s, 0.48 checks per solve, killed 1 of 17 (thermal_model.py:730 M01, which 5 other scripts also kill).

## Findings

### D3-s1-52 (low, hygiene): card_drift.mjs inherits plan_view.py closure, yet compares two cards over one payload: no cell edit can move it

tests/closure.py's _widen unions tests/plan_view.py's closure into tests/card_drift.mjs's, so 11 of the 12 D3-s1 cell files schedule card_drift on every one-file diff (closure.select), yet card_drift renders the working tree's card and the ref's card against ONE shared plan payload, so a production edit that changes that payload (sha256 differs) leaves 0 of its 45 states moved, while a one-token card edit moves 44.

Mechanism: PRODUCERS = {'tests/card.mjs': [plan_view], 'tests/card_drift.mjs': [plan_view]} is used twice: as a selection-ordering edge (a selected card script needs its producer first: sound) and, in _widen, as a closure union ('anything that can change the payload can change what they test'). The union is sound for card.mjs, whose checks are absolute assertions over the payload, and unsound for card_drift.mjs, whose verdict is byte-equality of two card renders that both read the same payload in one process (tests/card_drift.mjs header, renderAll over makeSide(treeSrc) and makeSide(baseSrc)). A cell-file diff changes only the payload, which both sides share, and touches neither the card source nor a solver fixture (claimsAreThisBranchs), so the comparison is an identity.

Evidence: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/m5_card_drift_payload.py`: base moved 0/45; prod_small and prod_large
(payload sha256 changed) moved 0/45; card arm moved 44/45 (rc 0 -> 1).
`--select-only`: 11 of 12 single-cell-file diffs schedule card_drift.mjs. Matrix: card_drift
0 kills of 10 driven. Cost 4.0 s wall per cell diff (provisional). Fix scope:
tests/closure.py: keep card_drift.mjs's PRODUCERS entry for selection ORDER (a card diff still runs plan_view first) but stop _widen from unioning the producer's closure into card_drift.mjs's; re-derive its closures.json entry (its raw trace was 6 files, #527). Verify with this harness's --select-only (11 -> 0) and the card arm (still 44).

## Non-findings

- boost_drift_replay.py's and stress.py's measured closures do not over-approximate for the cell files: every cell file in each closure is executed by the traced run. `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/m5_trace_hastub.py --scripts tests/stress.py,tests/boost_drift_replay.py` -> boost_drift_replay 12/12 files executed (5849 lines), stress 6/6 (5189 lines); over_approx_pairs=0; m5_closure_reach.py: 0 of 245 pairs over 22 traced drivers
- closures.json recorded.seconds stays inside closure.py's 2x SECONDS_BAND for 22 of the 27 cell-closure scripts on a quiet box; the two differential guards record their documented stub (#934) and mutation_table keeps env_drift eager for that reason. `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/m5_gate_table.py` -> in band 22/27; out: env_drift 96.4x, golden 80.8x (stubs), harness_headers 0.44x, plan_view 0.44x, wood_advisor 0.43x (all provisional, load1 0.7-1.1)
- boost_drift_replay.py's low checks-per-solve (46/789) is not unasserted work: its solves drive the 9-day closed-loop replay whose learner trajectory the checks read. `cat dev/audit/rounds/round11/D3/s1/state/solves.jsonl; sed -n 1,40p tests/boost_drift_replay.py` -> 0.058 checks per solve; 3 arms x 9 days of 30-minute cycles, each cycle's solve adopted and actuated (header); no perturbation showing a check independent of the solves was found
- stress.py and env_drift.py assert at a density of the same order as the other solve-heavy scripts. `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/m5_solves.py --hastub-hook --scripts tests/stress.py,tests/env_drift.py` -> stress 0.48, env_drift 1.12 cold / 2.24 warm checks per solve, against edge 0.95, backtest 2.27, optimality 3.65
- harness_headers.py's matrix kills are behavioural, not contention artefacts of its CPU bounds. `python3 -c "import json,glob;[print(k,j['checks'][:2]) for f in glob.glob('dev/audit/rounds/round11/D3/s1/state/results/matrix/*.json') for k,j in json.load(open(f))['runs'].items() if k=='tests/harness_headers.py' and j['killed']]"` -> 4 kills: 3 are RESULT-header mismatches of audit harnesses driving production (sysid_estimator_frontier, dst_window_factors); 1 (thermal_model.py:270) a SIGXCPU at the 480 CPU-s bound that features.py also timed out on (2314 s)
- golden.py's closure edges cost the CI gate nothing: CI runs GOLDEN_MODE=drift, which skips golden.py; its strict mode (run.sh's local default) is red at baseline on a non-canonical machine and can kill no cell mutant here. `grep -rn GOLDEN_MODE .github/workflows/; PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/m5_matrix.py table | grep golden` -> tests.yml:374 and nightly.yml:496 set drift; strict baseline 55 of 56 changed; 0 of 38 mutants killed
- The mutation-lane cost D3-s1-01 names shows in the no-early-stop matrix: env_drift kills nothing on lines its capture never executes (cited, not re-reported). `matrix rows of dev/audit/rounds/round11/D3/s1/state/results/matrix/ against baselines.json capture_reach (see REPORT.md, (b))` -> 21 of 38 matrix mutants on lines the capture never executes; env_drift killed 0 of those 21 (2 of the other 17)
- Pre-screen instrument controls hold on this box. `cat dev/audit/rounds/round11/D3/s1/state/m5box-null.out dev/audit/rounds/round11/D3/s1/state/m5box-posctl.out` -> null LIVES over 16 drivers; positive 2/2 KILLED by tests/manual_plan.py

## Leads (outside the cells)

- D3-s3 `tests/gate_lock.py` `needs_lease / _recorded_seconds`: Classifies a SCOPE_RUN as light ('none', unleased) when every name's closures.json recorded.seconds is under SLOT_MIN_SECONDS=69, but tests/env_drift.py (1.0 s) and tests/golden.py (1.2 s) record a stub invocation (#934) while a real run measured 96-197 s and 97 s here (m5_gate_table.py); a scope that selects only those two plus light scripts would run unleased.
- D3-s3 `tests/card_drift.mjs` `the closing process.exit(1) after console.log`: Exiting with process.exit right after console.log truncates a PIPED stdout: captured through subprocess capture_output, a card edit's run showed 1 of 44 DRIFT lines and no summary, a file redirect all 44 (measured while building m5_card_drift_payload.py). Any instrument reading card_drift's (or card.mjs's) verdict through a pipe reads a truncated count.

## Harnesses (new on this box)

- `m5_gate_table.py` (a); `m5_matrix.py` (b, tabulation + drop-one perturbation);
  `m5_trace_hastub.py` (d/e, child-inclusive reach via a hastub sitecustomize and a
  synthetic HEAD^1+hook ref); `m5_card_drift_payload.py` (e, finding D3-s1-52).
- Extended: `prescreen.py` (D3S1_EXTRA_DRIVERS / D3S1_ONLY, golden strict spec, node
  drivers behind their producer), `m5_solves.py` (`--hastub-hook`, env_drift tally).

## Unfinished

None for this box's slice.
