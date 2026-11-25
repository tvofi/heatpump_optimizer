# D3-s1 wave box D3-g15: full gate for 16 D3.M3 full-net survivors (round 11)

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`. Seat D3-s1, box D3-g15. Keys: `dev/audit/rounds/round11/D3/s1/wave/D3-g15/keys.tsv` (all 16 in `dhw_planner.py`, `DhwPlanner._dhw_legionella_ceilings` lines 740-807 and `DhwPlanner._dhw_legionella_due` lines 596-659).

## Machine and controls

```
date_utc: 2026-11-22T21:39:41Z
nproc: 4
cpu_model: Intel(R) Xeon(R) Processor @ 2.10GHz
load1: 0.68
free -m:
               total        used        free      shared  buff/cache   available
Mem:           16087        1067       13517          12        1801       15020
Swap:              0           0           0
df -h $HOME:
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  18% /
python3: /opt/hpo/venv-ci/bin/python3 Python 3.14.7
node: v22.23.5

## resumed fire (new container), 2026-11-25T00:48:32Z
nproc: 4
cpu_model:  Intel(R) Xeon(R) Processor @ 2.10GHz
load1: 0.67
               total        used        free      shared  buff/cache   available
Mem:           16087         745       14071          12        1541       15341
Swap:              0           0           0
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  17% /
python3: /opt/hpo/venv-ci/bin/python3 Python 3.14.7
null control: restored from the predecessor's checkpoint (same machine class, 4 cores, Xeon 2.10GHz); gate_wave.sh null keeps it.
```

Null control (`fullgate.py null`, comment-only marker on tariff.py): gate_rc=1, failed scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'], fail lines {'python3 tests/closure.py selftest': 2, 'python3 tests/entities.py': 1, 'python3 tests/harness_headers.py': 3}, summary ['3 TEST SCRIPT(S) FAILED'], wall 3642.7 s, load1 0.74..0.92 (provisional). A mutant is KILLED only by a script red beyond the null, or failing more checks than in the null. Every red check of the null is an environment artefact, no production file involved (`dev/audit/rounds/round11/D3/s1/wave/D3-g15/gates/null-note.txt`): closure.py selftest's two merge-tool pins, entities.py's scoped-gate pin, harness_headers.py's round-4 D6/claims.py re-run on the finder-wall-stripped tree; the same three scripts box D3-rem's null recorded red.

Procedure: `gate_wave.sh run` drove `fullgate.py run --src complete --key <key>` (GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF=<baseline> GATE_JOBS=1 ./tests/run.sh) one key at a time, alone on the box, 4 h cap. Every wall, CPU and load number is provisional (nproc 4, Intel Xeon @ 2.10GHz; the judge re-takes it); counts are final.

Probes ran from a separate baseline worktree (never the gate's tree), with the mutant applied in memory (the method recompiled from its own source with the one line replaced, attached with mock.patch.object). tests/harness_headers.py rglobs every script under dev/audit/rounds (tracked or not) and requires each inlined repo_root to equal tools/audit/repo_root.py's; _lg_common.py carries the canonical copy, and inline_scan with the probes present returns 0 with no depth seams. The probes entered the gate's tree during the null control (orchestrator NOTE 2, save every probe in the wave dir); every key gate ran with them present.

## Tally

- gated: 16 of 16; RED-AS-NULL 16
- KILLED by script: none
- candidates (full-gate survivors whose probe moves on an in-range input): 5
- equivalent-candidates: 11
- TIMEOUT: 0 

| key | site | patch | verdict | killed_by | wall s (prov.) | class |
|---|---|---|---|---|---|---|
| 0e752f692873e876 | dhw_planner.py:740 CLAMP_DROP | `runup_temps = np.zeros(max(n_steps, 0)) -> runup_temps = np.zeros((n_steps))` | RED-AS-NULL | - | 3440.6 | equivalent-candidate |
| 3e26ea9048504c31 | dhw_planner.py:743 CMP_BOUND | `if c_dhw > 0.0 and legionella_step is not None and n_steps > 0 and ( -> if c_dhw > 0.0 and legionella_step is not None and n_steps >= 0 and (` | RED-AS-NULL | - | 3486.1 | equivalent-candidate |
| 77d5e6c8ea98273a | dhw_planner.py:783 CLAMP_DROP | `need = (need + drawn - gain - rise) / max(decay, 1e-6) -> need = (need + drawn - gain - rise) / (decay)` | RED-AS-NULL | - | 3423.4 | equivalent-candidate |
| a1ebeff0870dfa76 | dhw_planner.py:784 CMP_BOUND | `if need > boost_top: -> if need >= boost_top:` | RED-AS-NULL | - | 3381.9 | candidate |
| f1549576a94b99be | dhw_planner.py:784 GUARD_OFF | `if need > boost_top: -> if False:` | RED-AS-NULL | - | 3418.6 | candidate |
| 1d455987c970dfde | dhw_planner.py:790 CMP_BOUND | `if need > everyday: -> if need >= everyday:` | RED-AS-NULL | - | 3496.5 | equivalent-candidate |
| 7cd9b966a3bd0008 | dhw_planner.py:793 CMP_BOUND | `if need <= floor_temps[m]: -> if need < floor_temps[m]:` | RED-AS-NULL | - | 3248.9 | candidate |
| 8e9a502f439ceeeb | dhw_planner.py:807 CMP_BOUND | `if temp <= everyday: -> if temp < everyday:` | RED-AS-NULL | - | 3251.5 | equivalent-candidate |
| f9c1b49fde6e1d52 | dhw_planner.py:807 GUARD_OFF | `if temp <= everyday: -> if False:` | RED-AS-NULL | - | 3250.0 | equivalent-candidate |
| 79ba0b9f6b3cf22d | dhw_planner.py:596 CMP_BOUND | `and interval_hours > 0 -> and interval_hours >= 0` | RED-AS-NULL | - | 4046.2 | equivalent-candidate |
| 56d2279a568e8891 | dhw_planner.py:598 CMP_BOUND | `and n_steps > 0 -> and n_steps >= 0` | RED-AS-NULL | - | 3794.8 | equivalent-candidate |
| 31c1881164f2dcdf | dhw_planner.py:626 CMP_BOUND | `hot = np.where(ramp[1:] >= params.dhw_legionella_temp - 1e-6)[0] -> hot = np.where(ramp[1:] > params.dhw_legionella_temp - 1e-6)[0]` | RED-AS-NULL | - | 3833.5 | candidate |
| 7640e80a994db479 | dhw_planner.py:628 CMP_BOUND | `if deadline_step < n_steps: -> if deadline_step <= n_steps:` | RED-AS-NULL | - | 3854.8 | candidate |
| 5224cce5f7a150cb | dhw_planner.py:658 CLAMP_DROP | `first = min(max(reach_step, 0), n_steps - 1) -> first = (max(reach_step, 0))` | RED-AS-NULL | - | 3692.5 | equivalent-candidate |
| c124ea447555a04a | dhw_planner.py:658 CLAMP_DROP | `first = min(max(reach_step, 0), n_steps - 1) -> first = min((reach_step), n_steps - 1)` | RED-AS-NULL | - | 3807.0 | equivalent-candidate |
| 8fb9093f7470e6aa | dhw_planner.py:659 CLAMP_DROP | `limit = max(first + 1, min(deadline_step + 1, n_steps)) -> limit = max(first + 1, (deadline_step + 1))` | RED-AS-NULL | - | 4057.5 | equivalent-candidate |

## Survivors: the step-4 answer per key

### 0e752f692873e876 — dhw_planner.py:740 CLAMP_DROP, `runup_temps = np.zeros(max(n_steps, 0)) -> runup_temps = np.zeros((n_steps))` (equivalent-candidate)

Gate: RED-AS-NULL (gate_rc 1, `dev/audit/rounds/round11/D3/s1/wave/D3-g15/gates/0e752f692873e876.json`). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_0e752f692873e876.py`: moved_in_range=0 count | neg_n_mutant=raises ValueError. identical on every n_steps >= 0 (14 inputs); separates only at n_steps=-1 (baseline empty arrays, mutant ValueError), and optimize() hands the planner min(len(prices), len(outdoor), config.n_steps) >= 0 (reach_min_n_steps=96): unreachable through production. Inputs tried: n_steps -1/0/1/2/96/192 x cycle step None/0/middle/last; a production optimize() spy. Should have failed: none through production; only a direct call with a negative n_steps separates (tests/features.py drives _dhw_legionella_ceilings directly at line 12099 but never with n_steps < 0).

### 3e26ea9048504c31 — dhw_planner.py:743 CMP_BOUND, `if c_dhw > 0.0 and legionella_step is not None and n_steps > 0 and ( -> if c_dhw > 0.0 and legionella_step is not None and n_steps >= 0 and (` (equivalent-candidate)

Gate: RED-AS-NULL (gate_rc 1, `dev/audit/rounds/round11/D3/s1/wave/D3-g15/gates/3e26ea9048504c31.json`). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_3e26ea9048504c31.py`: direct_n0_step0_baseline=unchanged | direct_n0_step0_mutant=raises IndexError. identical on n_steps >= 1 (12 inputs); separates only for a direct call at n_steps=0 WITH a cycle step (no-op -> IndexError); through the caller the due stage's own `n_steps > 0` guard returns step None at n_steps 0 (reach_n0_plan_moved=0), optimize() raises IndexError at n_steps 0 in both arms, and coordinator.py:6379 refuses a solve with fewer than 4 price steps: unreachable through production. Inputs tried: n_steps 0/1/2/96 x cycle step None/0/middle/last; _dhw_legionella_plan at n_steps 0 for hours_since 20/150/400; optimize() on a 0-step horizon, both arms. Should have failed: none through production; only a direct call with n_steps 0 and a cycle step separates.

### 77d5e6c8ea98273a — dhw_planner.py:783 CLAMP_DROP, `need = (need + drawn - gain - rise) / max(decay, 1e-6) -> need = (need + drawn - gain - rise) / (decay)` (equivalent-candidate)

Gate: RED-AS-NULL (gate_rc 1, `dev/audit/rounds/round11/D3/s1/wave/D3-g15/gates/77d5e6c8ea98273a.json`). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_77d5e6c8ea98273a.py`: decay0_baseline=returned, run-up min -2.44e+08 | decay0_mutant=raises ZeroDivisionError. identical for every in-range decay (24 inputs: cooling 0.05/0.3/3.0 C/h, dt 0.25/1 h, draws 0 and 3 kW); separates only at decay 0 (UA*dt/C >= 1: dt 9 h at the 3 C/h cap; baseline returns, mutant ZeroDivisionError), while production's smallest decay at a 1 h step is 0.88 (separate tank) and 0.81 (combi store) and the step is 15 min: unreachable through production. Inputs tried: cooling rate 0.05/0.3/3.0 C/h x dt 0.25/1.0 h x draws 0/3 kW x cycle step middle/last; dt 9 h at 3 C/h. Should have failed: none through production; only a direct call at a step of >= 8.3 h separates.

### a1ebeff0870dfa76 — dhw_planner.py:784 CMP_BOUND, `if need > boost_top: -> if need >= boost_top:` (candidate)

Gate: RED-AS-NULL (gate_rc 1, `dev/audit/rounds/round11/D3/s1/wave/D3-g15/gates/a1ebeff0870dfa76.json`). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_a1ebeff0870dfa76.py`: tie_runup_steps_baseline=6 count | tie_runup_steps_mutant=0 count. at an exact tie need == boost_top (16 of 601 draws scanned at the crossing, in-range parameters) the baseline keeps the run-up (6 steps; ceiling at step 39 60 C, requirement 60 C), the mutant cuts it (0 steps; 55 C, 20 C); off the tie no draw separates (moved_near_tie=16 = the ties; moved_random=0). Inputs tried: draw at the cycle step bisected to the need == 60 C crossing and +-300 floats (601 inputs), 200 L tank 55/60 C, cooling 0.1 C/h, 4 kW run, 0 C outdoor; a 30-configuration sweep (sweep_configs_with_ties) found ties in 16 of them; 60 seeded random draws. Should have failed: tests/features.py (executes line 784 on its traced baseline; its check 'legionella ceilings: with the rating at the charge limit no step's ceiling moves ...' at line 12109 drives _dhw_legionella_ceilings directly) lacks an assertion at the need == boost_top boundary that the run-up is kept.

Candidate finding (id assigned at consolidation): **No check pins the legionella run-up walk at need == boost top (`>` vs `>=`)**, severity low (claimed), class_guess new. Metric: count of run-up floor steps _dhw_legionella_ceilings writes when the walk's first need equals the boost top exactly. Null: off-tie draws (scanned floats that are not exact ties, and 60 seeded random draws): 0 inputs differ. Fix scope: tests only: a features.py check at an exact need == boost_top draw (the probe's tie_draw_kw) pinning the run-up the baseline writes.

### f1549576a94b99be — dhw_planner.py:784 GUARD_OFF, `if need > boost_top: -> if False:` (candidate)

Gate: RED-AS-NULL (gate_rc 1, `dev/audit/rounds/round11/D3/s1/wave/D3-g15/gates/f1549576a94b99be.json`). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_f1549576a94b99be.py`: req_at_boost_steps_baseline=0 count | req_at_boost_steps_mutant=20 count. with a draw the pump cannot carry (20 kW-equivalent for the hour before the cycle on a 4 kW pump) the baseline cuts the walk at once (run-up max 0 C, 0 steps required at the 60 C boost top), the mutant walks on: run-up floors up to 139.13 C (20 above the boost top), 20 steps whose folded requirement is the 60 C boost top, 21 boost-top ceilings instead of 1; no draw: identical. Inputs tried: 200 L tank 55/60 C, 4 kW run, cycle at step 40 of 96, draws 0 (null) and 20 kW on steps 36-40. Should have failed: tests/features.py (executes line 784; the legionella-ceilings check at line 12109) lacks a case where the pump cannot carry the ramp asserting no run-up floor exceeds the boost top and the walk stops.

Candidate finding (id assigned at consolidation): **No check pins the legionella run-up cut when the pump cannot carry the ramp**, severity medium (claimed), class_guess new. Metric: count of steps before the cycle whose min(max(floor, run-up), ceiling) reaches the boost top, under a draw the pump cannot carry. Null: zero draws (the guard never fires): null_moved=0. Fix scope: tests only: a features.py check with a heavy pre-cycle draw asserting max(runup_temps) <= boost top and no boost-top ceiling before the walk's cut.

### 1d455987c970dfde — dhw_planner.py:790 CMP_BOUND, `if need > everyday: -> if need >= everyday:` (equivalent-candidate)

Gate: RED-AS-NULL (gate_rc 1, `dev/audit/rounds/round11/D3/s1/wave/D3-g15/gates/1d455987c970dfde.json`). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_1d455987c970dfde.py`: moved_under_tie=0 count | moved_near_tie=0 count. 374 exact ties need == everyday found over 30 in-range configurations; at every one both arms agree (min(boost_top, everyday) is the value the ceiling already holds; each m is visited once); 60 random inputs agree: equivalent. Inputs tried: cooling 0.05/0.1/0.3/1/3 C/h x outdoor -10/0/7 C x run 2/4 kW, draw bisected to the need == 55 C crossing +-50 floats (1414 inputs, 374 ties); 60 seeded random draws and steps. Should have failed: none: equivalent at the tie by construction.

### 7cd9b966a3bd0008 — dhw_planner.py:793 CMP_BOUND, `if need <= floor_temps[m]: -> if need < floor_temps[m]:` (candidate)

Gate: RED-AS-NULL (gate_rc 1, `dev/audit/rounds/round11/D3/s1/wave/D3-g15/gates/7cd9b966a3bd0008.json`). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_7cd9b966a3bd0008.py`: tie_runup_steps_baseline=2 count | tie_runup_steps_mutant=5 count. when the availability floor at a walk step equals that step's need exactly the baseline stops the walk (2 run-up steps at a tie on step 38), the mutant walks on (5 steps), raising the folded requirement before the cycle by 14.0886 C summed; every one of the 5 walk steps separates at its tie; a floor 1e-9 C higher: identical. Inputs tried: 200 L tank 55/60 C, 4 kW run, cycle at step 40 of 96, floor 20 C with the tie placed on each walk step 39..35; null +1e-9 C. Should have failed: tests/features.py (executes line 793 on its traced baseline) lacks an assertion at need == floor that the walk stops there.

Candidate finding (id assigned at consolidation): **No check pins the legionella run-up stop at need == availability floor (`<=` vs `<`)**, severity low (claimed), class_guess new. Metric: count of run-up floor steps _dhw_legionella_ceilings writes when one step's availability floor equals the walk's need there. Null: the same floor raised 1e-9 C: null_moved=0. Fix scope: tests only: a features.py check with floor_temps[m] equal to the baseline run-up at m pinning the run-up steps.

### 8e9a502f439ceeeb — dhw_planner.py:807 CMP_BOUND, `if temp <= everyday: -> if temp < everyday:` (equivalent-candidate)

Gate: RED-AS-NULL (gate_rc 1, `dev/audit/rounds/round11/D3/s1/wave/D3-g15/gates/8e9a502f439ceeeb.json`). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_8e9a502f439ceeeb.py`: ties_exact=8 count | ties_moved=0 count. 8 exact ties temp == everyday (everyday set to the coast-down value 1..8 steps after the cycle); at every one both arms agree (max(everyday, everyday) into a ceiling already at everyday, and the next decay falls below it); 40 random inputs agree: equivalent. Inputs tried: cycle at step 40 of 96, everyday limit set to the exact coast-down value k = 1..8 steps after it; 40 seeded random cooling rates, limits and steps. Should have failed: none: equivalent at the tie by construction.

### f9c1b49fde6e1d52 — dhw_planner.py:807 GUARD_OFF, `if temp <= everyday: -> if False:` (equivalent-candidate)

Gate: RED-AS-NULL (gate_rc 1, `dev/audit/rounds/round11/D3/s1/wave/D3-g15/gates/f9c1b49fde6e1d52.json`). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_f9c1b49fde6e1d52.py`: moved=0 count | coast_steps_written_baseline=3375 count  mutant=3375 count. 147 inputs (everyday limit 15/40/55/59 C, cooling 0.05/0.3/3 C/h, horizons 96x15 min, 192x15 min, 24x1 h, cycle step first/middle/last two, and a combi store) give identical outputs; the coast-down past the limit writes max(everyday, temp<everyday) = everyday, so the break only saves iterations: equivalent. Inputs tried: everyday 15/40/55/59 C x cooling 0.05/0.3/3.0 C/h x (n, dt) (96, 0.25)/(192, 0.25)/(24, 1.0) x cycle step 0/mid/n-2/n-1; combi store 330 L at steps 10/48/90. Should have failed: none: equivalent (the break is an early exit).

### 79ba0b9f6b3cf22d — dhw_planner.py:596 CMP_BOUND, `and interval_hours > 0 -> and interval_hours >= 0` (equivalent-candidate)

Gate: RED-AS-NULL (gate_rc 1, `dev/audit/rounds/round11/D3/s1/wave/D3-g15/gates/79ba0b9f6b3cf22d.json`). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_79ba0b9f6b3cf22d.py`: interval0_baseline=(False, None) | interval0_mutant=(True, 1). separates only at an interval of exactly 0 days (baseline no cycle, mutant overdue cycle at step 1); every positive interval (16 inputs incl. 0.01 d) agrees; the options flow's selector floor is 1 day and the set_parameters service refuses 0 (accepts from 0.01): unreachable through production. Inputs tried: interval 0, 0.01, 1, 7, 30 d x hours_since 0/20/150/1000 h; the flow selector and service schema bounds. Should have failed: none through production; only a direct ThermalParameters(dhw_legionella_interval_days=0) separates.

### 56d2279a568e8891 — dhw_planner.py:598 CMP_BOUND, `and n_steps > 0 -> and n_steps >= 0` (equivalent-candidate)

Gate: RED-AS-NULL (gate_rc 1, `dev/audit/rounds/round11/D3/s1/wave/D3-g15/gates/56d2279a568e8891.json`). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_56d2279a568e8891.py`: n0_hours_since_400_baseline=(False, None, None) | n0_hours_since_400_mutant=raises ValueError. identical on n_steps >= 1 (15 inputs); at n_steps 0 an overdue clock separates (baseline no cycle, mutant ValueError from an empty argmin), but optimize() at n_steps 0 already fails in the baseline (IndexError; mutant ValueError) and coordinator.py:6379 refuses any solve with fewer than 4 price steps: unreachable through production. Inputs tried: n_steps 0/1/2/96 x hours_since 0/20/150/167.9/168/400 h; optimize() on a 0-step horizon, both arms. Should have failed: none through production; only a direct call at n_steps 0 separates.

### 31c1881164f2dcdf — dhw_planner.py:626 CMP_BOUND, `hot = np.where(ramp[1:] >= params.dhw_legionella_temp - 1e-6)[0] -> hot = np.where(ramp[1:] > params.dhw_legionella_temp - 1e-6)[0]` (candidate)

Gate: RED-AS-NULL (gate_rc 1, `dev/audit/rounds/round11/D3/s1/wave/D3-g15/gates/31c1881164f2dcdf.json`). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_31c1881164f2dcdf.py`: tie_step_baseline=0  tie_step_mutant=1 | tie_step_mutant=None. when the flat-out ramp ends step 0 exactly on the reach threshold 59.999999 C (6 exact ties in 3606 scanned initial temperatures over 6 in-range configurations) the baseline calls step 0 reachable and places the cycle on the cheap step 0, the mutant calls it unreachable and places it on step 1; off the tie no input separates. Inputs tried: initial tank temperature bisected to the ramp[1] == 59.999999 C crossing, +-300 floats, outdoor -10/0/7 C x run 2/4 kW, hours_since 150 h, price 0.1 at step 0. Should have failed: tests/features.py (executes line 626 on its traced baseline) lacks an assertion at ramp == legionella_temp - 1e-6 that the step counts as reachable.

Candidate finding (id assigned at consolidation): **No check pins the legionella reach threshold as inclusive (`>=` vs `>`)**, severity low (claimed), class_guess new. Metric: the step _dhw_legionella_due places the cycle on when the simulated ramp hits legionella_temp - 1e-6 exactly at step 0's end. Null: scanned initial temperatures that are not exact ties: moved_off_tie=0. Fix scope: tests only: a features.py check at the probe's tie input pinning the placed step.

### 7640e80a994db479 — dhw_planner.py:628 CMP_BOUND, `if deadline_step < n_steps: -> if deadline_step <= n_steps:` (candidate)

Gate: RED-AS-NULL (gate_rc 1, `dev/audit/rounds/round11/D3/s1/wave/D3-g15/gates/7640e80a994db479.json`). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_7640e80a994db479.py`: edge_solve_due_baseline=False dhw_kwh=4.6915 | edge_solve_due_mutant=True dhw_kwh=4.8211. with the hard deadline exactly at the horizon's end (hours_since 144 h of a 168 h interval: deadline_step 96 == n_steps, a 15-minute window the clock crosses once per interval) the baseline plans no cycle in this solve, the mutant buys it now: _dhw_legionella_due False -> True (step 1), the production optimize()'s published predictive_info dhw_legionella_due False -> True, planned hot water 4.6915 -> 4.8211 kWh (+0.1295 kWh); deadline n+1 and n-1: identical. Inputs tried: hours_since 143.75 / 144 / 144.25 h on 96 x 15 min (deadline n+1, n, n-1), direct and through optimize(). Should have failed: tests/features.py (executes line 628 on its traced baseline) lacks a check at deadline_step == n_steps that the cycle is left to the elastic branch.

Candidate finding (id assigned at consolidation): **No check pins the legionella hard-deadline branch at deadline == horizon end (`<` vs `<=`)**, severity low (claimed), class_guess new. Metric: predictive_info['dhw_legionella_due'] of one optimize() whose legionella deadline step equals n_steps. Null: hours_since 143.75 h and 144.25 h (deadline n+1, n-1): null_moved=0, null_solve_moved=0. Fix scope: tests only: a features.py check at hours_since = interval - horizon pinning due False with elastic off.

### 5224cce5f7a150cb — dhw_planner.py:658 CLAMP_DROP, `first = min(max(reach_step, 0), n_steps - 1) -> first = (max(reach_step, 0))` (equivalent-candidate)

Gate: RED-AS-NULL (gate_rc 1, `dev/audit/rounds/round11/D3/s1/wave/D3-g15/gates/5224cce5f7a150cb.json`). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_5224cce5f7a150cb.py`: moved=0 count | inputs_tried=432 count. 432 inputs over every hard-deadline branch (124 reachable, 156 overdue reachable, 8 unreachable) agree: in this branch reach_step < n_steps, so min(..., n_steps - 1) never binds: equivalent. Inputs tried: n_steps 4/96/192 x hours_since 0/100/150/167/168/170/400/2000 h x initial tank 20/45/55/59.5/60/65 C x Off window none/step 0/band, seeded random prices. Should have failed: none: equivalent by the branch invariant.

### c124ea447555a04a — dhw_planner.py:658 CLAMP_DROP, `first = min(max(reach_step, 0), n_steps - 1) -> first = min((reach_step), n_steps - 1)` (equivalent-candidate)

Gate: RED-AS-NULL (gate_rc 1, `dev/audit/rounds/round11/D3/s1/wave/D3-g15/gates/c124ea447555a04a.json`). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_c124ea447555a04a.py`: moved=0 count | inputs_tried=432 count. 432 inputs over every hard-deadline branch agree: reach_step is an np.where index or n_steps, never negative, so max(reach_step, 0) never binds (the carried u1d answer's negative reach_step does not occur): equivalent. Inputs tried: n_steps 4/96/192 x hours_since 0/100/150/167/168/170/400/2000 h x initial tank 20/45/55/59.5/60/65 C x Off window none/step 0/band, seeded random prices. Should have failed: none: equivalent by the branch invariant.

### 8fb9093f7470e6aa — dhw_planner.py:659 CLAMP_DROP, `limit = max(first + 1, min(deadline_step + 1, n_steps)) -> limit = max(first + 1, (deadline_step + 1))` (equivalent-candidate)

Gate: RED-AS-NULL (gate_rc 1, `dev/audit/rounds/round11/D3/s1/wave/D3-g15/gates/8fb9093f7470e6aa.json`). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_8fb9093f7470e6aa.py`: moved=0 count | inputs_tried=432 count. 432 inputs over every hard-deadline branch agree: the branch runs only when deadline_step < n_steps, so min(deadline_step + 1, n_steps) never binds: equivalent. Inputs tried: n_steps 4/96/192 x hours_since 0/100/150/167/168/170/400/2000 h x initial tank 20/45/55/59.5/60/65 C x Off window none/step 0/band, seeded random prices. Should have failed: none: equivalent by the branch invariant.

## Harnesses

- `dev/audit/rounds/round11/D3/s1/fullgate.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/_lg_common.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_0e752f692873e876.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_3e26ea9048504c31.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_77d5e6c8ea98273a.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_a1ebeff0870dfa76.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_f1549576a94b99be.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_1d455987c970dfde.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_7cd9b966a3bd0008.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_8e9a502f439ceeeb.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_f9c1b49fde6e1d52.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_79ba0b9f6b3cf22d.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_56d2279a568e8891.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_31c1881164f2dcdf.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_7640e80a994db479.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_5224cce5f7a150cb.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_c124ea447555a04a.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_8fb9093f7470e6aa.py`
- the box's gate_wave.sh procedure (out of tree, on the dispatch ref), named above

## Unfinished

- none

## Coverage

D3.M1, D3.M2, D3.M4 and D3.M5 and their redispatched C-items are carried verbatim from REPORT-D3-u1b.json. D3.M3 here: universe 742 (the wave list), examined 16 (this box's gated keys), not_reached by box: 46 rows. Findings: [] — candidates are under gate_survivors for the orchestrator's consolidation, which assigns ids.

