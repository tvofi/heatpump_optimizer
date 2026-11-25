# D3-s1 round 11, box D3-g29: full gate of 16 u1 full-net survivors (D3.M3) and their D3.M4 answers

Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. box D3-g29: Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython 3.14, alone on its machine. Every wall and load1 is provisional; counts and probe values are exact.

## Machine and controls

```
nproc: 4
               total        used        free      shared  buff/cache   available
Mem:           16087        1103       13481          12        1801       14984
Swap:              0           0           0
model name	: Intel(R) Xeon(R) Processor @ 2.10GHz
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  18% /
load1: 0.90
Sun Nov 22 21:43:58 UTC 2026
--- re-fire 2026-11-25T00:52:32Z (resumed seat)
nproc 4
               total        used        free      shared  buff/cache   available
Mem:           16087         773       14039          12        1546       15313
Swap:              0           0           0
model name	: Intel(R) Xeon(R) Processor @ 2.10GHz
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  17% /
load1 0.45
```

Null control (`python3 dev/audit/rounds/round11/D3/s1/fullgate.py null`, a comment-only marker): gate_rc=1, red scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'], FAIL counts {'python3 tests/closure.py selftest': 2, 'python3 tests/entities.py': 1, 'python3 tests/harness_headers.py': 4}, wall 3893.3 s, load1 0.94..0.92. A mutant is KILLED only by a script red beyond the null or failing more checks than in it; red on the null's scripts alone reads RED-AS-NULL (survived).

Procedure: gate_wave.sh's null then run (one gate at a time, GATE_JOBS=1, 4 h cap, a checkpoint after each). Probes were executed in a separate baseline worktree so none imported a gate-mutated file; each applies its mutant in memory. The reach sweep (`probes/reach_sweep.py`, output `probes/reach_sweep.out`) solves the 50 tests/golden.py scenarios with recording spies on the five mutated symbols.

Re-fire. Re-fire: the first seat stalled after gating 6 of 16 keys (wip ref 49b66a44); a successor seat restored that checkpoint, re-executed all 16 probes in a fresh baseline worktree (every RESULT line identical except load1), and resumed gate_wave.sh run at 2d4e3ff8e818b777, whose interrupted gate left no record and was run in full. Gates 7..16 ran 2026-11-25 00:52-10:15Z on the same machine class.

## Tally

Gated 16 of 16: KILLED 1, RED-AS-NULL 15.
Killed by script: e196155b7525014c by python3 tests/stress.py.
Classes: candidate 5, equivalent-candidate 10, killed 1.

| key | site | patch | verdict | killed_by | wall s | load1 | class |
|---|---|---|---|---|---|---|---|
| e196155b7525014c | custom_components/heatpump_optimizer/optimizer.py:2844 GUARD_OFF | `if result.success: -> if False:` | KILLED | python3 tests/stress.py | 3491.6 | 0.86..0.92 | killed |
| 9d455ff4aaf3f3e0 | custom_components/heatpump_optimizer/optimizer.py:3328 CLAMP_DROP | `deficit / max(cop_end, 1e-6) -> deficit / (cop_end)` | RED-AS-NULL | - | 3467.1 | 0.53..1.02 | equivalent-candidate |
| 55022279c6d6bbda | custom_components/heatpump_optimizer/optimizer.py:3329 CLAMP_DROP | `+ buffer_deficit / max(cop_buffer, 1e-6) -> + buffer_deficit / (cop_buffer)` | RED-AS-NULL | - | 3443.8 | 0.86..0.95 | equivalent-candidate |
| 6a75a1ff72dc1df8 | custom_components/heatpump_optimizer/optimizer.py:3338 CLAMP_DROP | `return refill_price * deficit / max(cop_end, 1e-6) -> return refill_price * deficit / (cop_end)` | RED-AS-NULL | - | 3349.6 | 0.74..0.92 | equivalent-candidate |
| 133158399eac10ae | custom_components/heatpump_optimizer/optimizer.py:2357 CMP_BOUND | `if power[i] <= threshold: -> if power[i] < threshold:` | RED-AS-NULL | - | 3364.9 | 0.78..0.92 | equivalent-candidate |
| 4434c1fcedef6b6d | custom_components/heatpump_optimizer/optimizer.py:2286 GUARD_OFF | `if n_steps == 0: -> if False:` | RED-AS-NULL | - | 3221.2 | 0.78..0.92 | equivalent-candidate |
| 2d4e3ff8e818b777 | custom_components/heatpump_optimizer/optimizer.py:2294 CMP_BOUND | `if power[i] <= threshold: -> if power[i] < threshold:` | RED-AS-NULL | - | 3267.0 | 0.35..0.92 | equivalent-candidate |
| 69e4aa41f4562af9 | custom_components/heatpump_optimizer/optimizer.py:2299 CMP_BOUND | `room = room_temps[i + 1] if i + 1 < len(room_temps) else room_temps[-1] -> room = room_temps[i + 1] if i + 1 <= len(room_temps) else room_temps[-1]` | RED-AS-NULL | - | 3197.8 | 0.79..0.93 | equivalent-candidate |
| 8171db177f51df33 | custom_components/heatpump_optimizer/optimizer.py:2300 CMP_BOUND | `if room <= temp_min_bounds[i] + 0.15: -> if room < temp_min_bounds[i] + 0.15:` | RED-AS-NULL | - | 3167.7 | 0.86..0.99 | candidate |
| 2aff1f5c0b10dffa | custom_components/heatpump_optimizer/optimizer.py:2303 CMP_BOUND | `if surplus is not None and i < len(surplus) and surplus[i] > 1e-6: -> if surplus is not None and i < len(surplus) and surplus[i] >= 1e-6:` | RED-AS-NULL | - | 3233.5 | 0.85..0.92 | candidate |
| 000221f3921dd956 | custom_components/heatpump_optimizer/optimizer.py:2309 CMP_BOUND | `if i < len(heat_loss_factors) and heat_loss_factors[i] > 1.1: -> if i < len(heat_loss_factors) and heat_loss_factors[i] >= 1.1:` | RED-AS-NULL | - | 3199.5 | 0.94..0.92 | candidate |
| 8ef8417029ab8385 | custom_components/heatpump_optimizer/optimizer.py:3177 CMP_BOUND | `if span <= 0.0: -> if span < 0.0:` | RED-AS-NULL | - | 3276.2 | 0.93..1.01 | equivalent-candidate |
| b5d57e4a1fc22d96 | custom_components/heatpump_optimizer/optimizer.py:3177 GUARD_OFF | `if span <= 0.0: -> if False:` | RED-AS-NULL | - | 3388.5 | 1.01..0.92 | equivalent-candidate |
| f062e0cc415ee33e | custom_components/heatpump_optimizer/optimizer.py:3186 CLAMP_DROP | `return float(math.exp(-min(0.5 * ua * span / demand, 700.0))) -> return float(math.exp(-(0.5 * ua * span / demand)))` | RED-AS-NULL | - | 3501.2 | 0.78..0.92 | equivalent-candidate |
| 0ea7620ce058c489 | custom_components/heatpump_optimizer/price_model.py:66 CONST | `SHAPE_ALPHA = 0.12 -> SHAPE_ALPHA = 0.24` | RED-AS-NULL | - | 3984.5 | 0.72..1.01 | candidate |
| 213a122afd9ff3e1 | custom_components/heatpump_optimizer/price_model.py:69 CONST | `SHAPE_CONFIDENCE_DAYS = 5 -> SHAPE_CONFIDENCE_DAYS = 10` | RED-AS-NULL | - | 3436.8 | 0.93..0.92 | candidate |

## Gate survivors with a moving probe (finding candidates, ids left to consolidation)

### 8171db177f51df33 custom_components/heatpump_optimizer/optimizer.py:2300 CMP_BOUND: No check feeds classify_space_steps an active step at its next room temperature boundary

Mutant 8171db177f51df33 (optimizer.py:2300, the `if room <= temp_min_bounds[i] + 0.15` comparison flipped) survives the full gate, yet the probe's reason moves at the next room temperature exactly temp_min_bound + 0.15: baseline 'comfort_floor', mutant 'cheap_price'. Full gate verdict RED-AS-NULL. Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_8171db177f51df33.py`: baseline 'comfort_floor', mutant 'cheap_price'; null_delta=0 count. Inputs tried: tie at floor 19.0, 0.0, -5.0, 21.85, 35.0 (all move); null: room 19.16, 19.14, 21.0. Reach: golden matrix: room_eq_floor_plus_015 0 of 1999 active steps; the room trajectory is a continuous solver output, so the tie is in-domain. Step 4: the production line is custom_components/heatpump_optimizer/optimizer.py:2300 CMP_BOUND (`if room <= temp_min_bounds[i] + 0.15: -> if room < temp_min_bounds[i] + 0.15:`); the check that should have failed is tests/features.py: a classify_space_steps check at the exact boundary `if room <= temp_min_bounds[i] + 0.15` asserting the baseline reason 'comfort_floor'. Severity claimed low, class_guess new.

### 2aff1f5c0b10dffa custom_components/heatpump_optimizer/optimizer.py:2303 CMP_BOUND: No check feeds classify_space_steps an active step at its PV surplus boundary

Mutant 2aff1f5c0b10dffa (optimizer.py:2303, the `surplus[i] > 1e-6` comparison flipped) survives the full gate, yet the probe's reason moves at the PV surplus exactly 1e-6 kW: baseline 'cheap_price', mutant 'solar_surplus'. Full gate verdict RED-AS-NULL. Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_2aff1f5c0b10dffa.py`: baseline 'cheap_price', mutant 'solar_surplus'; null_delta=0 count. Inputs tried: tie surplus 1e-6; null: surplus 0.0, 2e-6, 1.0; idle_codes at the same tie (reads no sun). Reach: golden matrix: surplus_eq_1e-6 0 of 1999 active steps; the surplus is a forecast kW series, so the tie is in-domain; idle_codes (optimizer.py:2237) keeps `> 1e-6`, so the mutant splits the two classifiers at the tie. Step 4: the production line is custom_components/heatpump_optimizer/optimizer.py:2303 CMP_BOUND (`if surplus is not None and i < len(surplus) and surplus[i] > 1e-6: -> if surplus is not None and i < len(surplus) and surplus[i] >= 1e-6:`); the check that should have failed is tests/features.py: a classify_space_steps check at the exact boundary `surplus[i] > 1e-6` asserting the baseline reason 'cheap_price'. Severity claimed low, class_guess new.

### 000221f3921dd956 custom_components/heatpump_optimizer/optimizer.py:2309 CMP_BOUND: No check feeds classify_space_steps an active step at its weather heat-loss factor boundary

Mutant 000221f3921dd956 (optimizer.py:2309, the `heat_loss_factors[i] > 1.1` comparison flipped) survives the full gate, yet the probe's reason moves at the weather heat-loss factor exactly 1.1: baseline 'cheap_price', mutant 'preheat_weather'. Full gate verdict RED-AS-NULL. Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_000221f3921dd956.py`: baseline 'cheap_price', mutant 'preheat_weather'; null_delta=0 count. Inputs tried: tie factor 1.1; null: factor 1.0, 1.2; reach scan: _weather_loss_factors over wind 0..40 m/s (0.01 step) x 8 precipitation levels: 0 of 32008 exactly 1.1. Reach: golden matrix: hlf_eq_1.1 0 of 1999 active steps; scan 0 of 32008; the factor is a ratio of continuous weather inputs, so the tie is in-domain but unfound. Step 4: the production line is custom_components/heatpump_optimizer/optimizer.py:2309 CMP_BOUND (`if i < len(heat_loss_factors) and heat_loss_factors[i] > 1.1: -> if i < len(heat_loss_factors) and heat_loss_factors[i] >= 1.1:`); the check that should have failed is tests/features.py: a classify_space_steps check at the exact boundary `heat_loss_factors[i] > 1.1` asserting the baseline reason 'cheap_price'. Severity claimed low, class_guess new.

### 0ea7620ce058c489 custom_components/heatpump_optimizer/price_model.py:66 CONST: No check pins SHAPE_ALPHA's value; doubling the price-shape EWMA weight is unseen

Mutant 0ea7620ce058c489 (price_model.py:66 SHAPE_ALPHA 0.12 -> 0.24) survives the full gate, yet the probe's learned 08:00 shape moves: baseline 1.478675497, mutant 1.36794702 after two observed weekdays. Full gate verdict RED-AS-NULL. Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_0ea7620ce058c489.py`: baseline shape_h8 1.478675497 after 2 days (predict 1.191470199), mutant shape_h8 1.36794702 (predict 1.147178808); null_delta=0 count. Inputs tried: 2, 3 and 6 alternating weekday observations (all move); null: 0 and 1 observations (first day copied, no EWMA). Reach: production: every observed day after the first per profile (PriceShapeModel.observe_day, price_model.py:229). Step 4: the production line is custom_components/heatpump_optimizer/price_model.py:66 CONST (`SHAPE_ALPHA = 0.12 -> SHAPE_ALPHA = 0.24`); the check that should have failed is tests/features.py: a PriceShapeModel check that folds a second day and asserts shape = (1 - 0.12) * old + 0.12 * new (renormalised). Severity claimed low, class_guess new.

### 213a122afd9ff3e1 custom_components/heatpump_optimizer/price_model.py:69 CONST: No check pins SHAPE_CONFIDENCE_DAYS; trusting the price shape half as fast is unseen

Mutant 213a122afd9ff3e1 (price_model.py:69 SHAPE_CONFIDENCE_DAYS 5 -> 10) survives the full gate, yet the probe's confidence after 5 observed weekdays moves: baseline 1.0, mutant 0.5, and expected_daily_min goes 0.4478 -> None. Full gate verdict RED-AS-NULL. Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_213a122afd9ff3e1.py`: baseline confidence 1.0, expected_daily_min 0.4478 after 5 days, mutant confidence 0.5, expected_daily_min None after 5 days (None until day 10); null_delta=0 count. Inputs tried: 1, 5 and 7 observed weekdays (all move); null: 0, 10 and 12 observed days. Reach: production: PriceShapeModel.confidence (shape_for, predict, sigma) and expected_daily_min (the elastic legionella gate) on every install with fewer than 10 observed days per profile. Step 4: the production line is custom_components/heatpump_optimizer/price_model.py:69 CONST (`SHAPE_CONFIDENCE_DAYS = 5 -> SHAPE_CONFIDENCE_DAYS = 10`); the check that should have failed is tests/features.py: a PriceShapeModel check asserting confidence == 1.0 and a non-None expected_daily_min after exactly 5 observed days (0.8 after 4). Severity claimed low, class_guess new.

## Equivalent-candidates (non-findings unless a later seat finds the input)

- 9d455ff4aaf3f3e0 custom_components/heatpump_optimizer/optimizer.py:3328 CLAMP_DROP (`deficit / max(cop_end, 1e-6) -> deficit / (cop_end)`), gate RED-AS-NULL: unreachable through production. Baseline row_cost finite, floored at COP 1e-6 (e.g. 2000001.0 at COP 0); mutant ZeroDivisionError at COP 0, sign flip at COP -1, x1000 at COP 1e-9; identical at and above 1e-6; null_delta=0 count (COP 1.0, 1.05, 2.5, 4.0, nan). Inputs tried: cop_end (split branch, refill law set) = 0.0, -1.0, 1e-9, 1e-6; null: COP 1.0, 1.05, 2.5, 4.0, nan; reach: ThermalModel.compute_cop / marginal_cop('buffer') over outdoor -60..45 C x humidity x store 20..90 C x 3 parameter sets. Reach: every COP _terminal_row_cost receives comes from ThermalModel._cop_law, floored by `return max(cop, 1.0)`: scan minimum 1.0000; golden matrix minimum cop_end 1.5675, cop_buffer 1.1728 (reach_sweep.out). Step 4: tests/features.py: none through production: the 1e-6 floor sits under _cop_law's 1.0 floor; only a direct _terminal_row_cost call with COP < 1e-6 separates the arms. Command `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_9d455ff4aaf3f3e0.py --reach`.
- 55022279c6d6bbda custom_components/heatpump_optimizer/optimizer.py:3329 CLAMP_DROP (`+ buffer_deficit / max(cop_buffer, 1e-6) -> + buffer_deficit / (cop_buffer)`), gate RED-AS-NULL: unreachable through production. Baseline row_cost finite, floored at COP 1e-6 (e.g. 2000001.0 at COP 0); mutant ZeroDivisionError at COP 0, sign flip at COP -1, x1000 at COP 1e-9; identical at and above 1e-6; null_delta=0 count (COP 1.0, 1.05, 2.5, 4.0, nan). Inputs tried: cop_buffer (split branch, refill law set) = 0.0, -1.0, 1e-9, 1e-6; null: COP 1.0, 1.05, 2.5, 4.0, nan; reach: ThermalModel.compute_cop / marginal_cop('buffer') over outdoor -60..45 C x humidity x store 20..90 C x 3 parameter sets. Reach: every COP _terminal_row_cost receives comes from ThermalModel._cop_law, floored by `return max(cop, 1.0)`: scan minimum 1.0000; golden matrix minimum cop_end 1.5675, cop_buffer 1.1728 (reach_sweep.out). Step 4: tests/features.py: none through production: the 1e-6 floor sits under _cop_law's 1.0 floor; only a direct _terminal_row_cost call with COP < 1e-6 separates the arms. Command `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_55022279c6d6bbda.py --reach`.
- 6a75a1ff72dc1df8 custom_components/heatpump_optimizer/optimizer.py:3338 CLAMP_DROP (`return refill_price * deficit / max(cop_end, 1e-6) -> return refill_price * deficit / (cop_end)`), gate RED-AS-NULL: unreachable through production. Baseline row_cost finite, floored at COP 1e-6 (e.g. 2000001.0 at COP 0); mutant ZeroDivisionError at COP 0, sign flip at COP -1, x1000 at COP 1e-9; identical at and above 1e-6; null_delta=0 count (COP 1.0, 1.05, 2.5, 4.0, nan). Inputs tried: cop_end == cop_buffer (single-sum branch, no refill law) = 0.0, -1.0, 1e-9, 1e-6; null: COP 1.0, 1.05, 2.5, 4.0, nan; reach: ThermalModel.compute_cop / marginal_cop('buffer') over outdoor -60..45 C x humidity x store 20..90 C x 3 parameter sets. Reach: every COP _terminal_row_cost receives comes from ThermalModel._cop_law, floored by `return max(cop, 1.0)`: scan minimum 1.0000; golden matrix minimum cop_end 1.5675, cop_buffer 1.1728 (reach_sweep.out). Step 4: tests/features.py: none through production: the 1e-6 floor sits under _cop_law's 1.0 floor; only a direct _terminal_row_cost call with COP < 1e-6 separates the arms. Command `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_6a75a1ff72dc1df8.py --reach`.
- 133158399eac10ae custom_components/heatpump_optimizer/optimizer.py:2357 CMP_BOUND (`if power[i] <= threshold: -> if power[i] < threshold:`), gate RED-AS-NULL: unreachable through production. Baseline reasons identical to the mutant on all 7 default-threshold inputs; at threshold 0 with zero draw: all 'idle'/'idle_coasting'; mutant identical at the default threshold; at a non-default threshold (0.0, 0.5) every idle step at draw == threshold becomes active; null_delta=0 count (the default-threshold arm above is the null: no production caller passes threshold). Inputs tried: default threshold: zeros, exactly CHANNEL_ACTIVE_KW, one ulp above/below, mixed, nan, negative; threshold 0.0 with zero draws; threshold 0.5 with 0.5 kW draws. Reach: no production caller passes `threshold` (optimizer.py:2467, 3905), and channel_heating_draw returns 0.0 or a draw strictly above CHANNEL_ACTIVE_KW, so no step equals the default threshold: draws_equal_threshold=0 of 56; golden matrix nondefault_threshold 0, power_eq_threshold 0. Step 4: tests/features.py: none through production; only a direct classify_dhw_steps call with a non-default threshold separates the arms. Command `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_133158399eac10ae.py --reach`.
- 4434c1fcedef6b6d custom_components/heatpump_optimizer/optimizer.py:2286 GUARD_OFF (`if n_steps == 0: -> if False:`), gate RED-AS-NULL: equivalent for every in-contract input. Baseline [] for n_steps == 0; mutant [] for all 6 in-contract inputs; TypeError only for power=None (out of the np.ndarray contract); null_delta=0 count. Inputs tried: all-empty arrays; length-4 arrays; empty prices; nan prices; surplus given; empty room_temps; out of contract: power=None; null: n_steps=4. Reach: golden matrix: n_steps_zero 0 of 52 classify_space_steps calls. Step 4: tests/features.py: none: with n_steps == 0 the loop and idle_codes both return [] without the guard. Command `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_4434c1fcedef6b6d.py --reach`.
- 2d4e3ff8e818b777 custom_components/heatpump_optimizer/optimizer.py:2294 CMP_BOUND (`if power[i] <= threshold: -> if power[i] < threshold:`), gate RED-AS-NULL: unreachable through production. Baseline reasons identical to the mutant on all 7 default-threshold inputs; at threshold 0 with zero draw: all 'idle'/'idle_coasting'; mutant identical at the default threshold; at a non-default threshold (0.0, 0.5) every idle step at draw == threshold becomes active; null_delta=0 count (the default-threshold arm above is the null: no production caller passes threshold). Inputs tried: default threshold: zeros, exactly CHANNEL_ACTIVE_KW, one ulp above/below, mixed, nan, negative; threshold 0.0 with zero draws; threshold 0.5 with 0.5 kW draws. Reach: no production caller passes `threshold` (optimizer.py:2467, 3905), and channel_heating_draw returns 0.0 or a draw strictly above CHANNEL_ACTIVE_KW, so no step equals the default threshold: draws_equal_threshold=0 of 56; golden matrix nondefault_threshold 0, power_eq_threshold 0. Step 4: tests/features.py: none through production; only a direct classify_space_steps call with a non-default threshold separates the arms. Command `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_2d4e3ff8e818b777.py --reach`.
- 69e4aa41f4562af9 custom_components/heatpump_optimizer/optimizer.py:2299 CMP_BOUND (`room = room_temps[i + 1] if i + 1 < len(room_temps) else room_temps[-1] -> room = room_temps[i + 1] if i + 1 <= len(room_temps) else room_temps[-1]`), gate RED-AS-NULL: unreachable through production. Baseline last active step's reason 'terminal_value' when room_temps has n_steps samples; mutant IndexError on that call; null_delta=0 count. Inputs tried: room_temps of n_steps samples, active step 0, 5, n-2, n-1; null: n_steps + 1 samples at steps 0, 5, n-1. Reach: production passes the simulated trajectory, n_steps + 1 states (optimizer.py:3844): golden matrix room_index_at_len 0 of 1999 active steps. Step 4: tests/features.py: none through production; a direct classify_space_steps call with a short room_temps separates the arms. Command `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_69e4aa41f4562af9.py --reach`.
- 8ef8417029ab8385 custom_components/heatpump_optimizer/optimizer.py:3177 CMP_BOUND (`if span <= 0.0: -> if span < 0.0:`), gate RED-AS-NULL: unreachable through production. Baseline 1.0 at span 0 with demand 0 or -1; mutant 0.0 there; identical at span 0 with demand > 0 and at span > 0; null_delta=0 count. Inputs tried: span 0, demand 0.0 and -1.0; null: span 0 demand 2; span 30 demand 2 and 0. Reach: the only caller (optimizer.py:3593) passes caps['buffer'] = min(buffer_max_temp, max(ceiling, initial)), the ceiling bisected in [max(20, cop_flow_reference_temp=35), buffer_max_temp] and the config flow bounds buffer_max_temperature to 40..90 C, so span = cap - 20 >= 15 K; golden matrix span_zero 0 of 10 calls. Step 4: tests/features.py: none through production; a direct stored_heat_survival call with cap == ambient and demand <= 0 separates the arms. Command `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_8ef8417029ab8385.py --reach`.
- b5d57e4a1fc22d96 custom_components/heatpump_optimizer/optimizer.py:3177 GUARD_OFF (`if span <= 0.0: -> if False:`), gate RED-AS-NULL: unreachable through production. Baseline 1.0 for span < 0; mutant exp(+...) above 1 (3.4903 at span -10 K, demand 2 kW), 0.0 with no demand; null_delta=0 count. Inputs tried: span -10 demand 2 and 0; span 0 demand 0; span -0.5 demand 50; null: span 30 demand 2 and 0. Reach: the only caller (optimizer.py:3593) passes caps['buffer'] = min(buffer_max_temp, max(ceiling, initial)), the ceiling bisected in [max(20, cop_flow_reference_temp=35), buffer_max_temp] and the config flow bounds buffer_max_temperature to 40..90 C, so span = cap - 20 >= 15 K; golden matrix span_negative 0 of 10 calls. Step 4: tests/features.py: none through production; a direct stored_heat_survival call with cap below ambient separates the arms. Command `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_b5d57e4a1fc22d96.py --reach`.
- f062e0cc415ee33e custom_components/heatpump_optimizer/optimizer.py:3186 CLAMP_DROP (`return float(math.exp(-min(0.5 * ua * span / demand, 700.0))) -> return float(math.exp(-(0.5 * ua * span / demand)))`), gate RED-AS-NULL: equivalent at every observable output. Baseline 9.86e-305 for every exponent above 700; mutant 2.0e-313 at 720, 5e-324 at 745, 0.0 beyond; neither arm raises; null_delta=0 count. Inputs tried: exponent 720, 745, 800, 1e6, 1e301, overflow (demand 5e-324); consumer: 30 kWh/K x survival x 40 K added to a 0.01 SEK plan cost: identical floats; null: exponent 1, 100, 700. Reach: golden matrix: exponent_over_700 0 of 10 calls; the arms differ by at most 9.86e-305, below the ulp of any cost it is summed into. Step 4: tests/features.py: none: math.exp underflows to 0.0 without raising, so the cap changes no observable value. Command `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_f062e0cc415ee33e.py --reach`.

## Killed (non-findings)

- e196155b7525014c custom_components/heatpump_optimizer/optimizer.py:2844 GUARD_OFF: KILLED by python3 tests/stress.py (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key e196155b7525014c`); failing lines in dev/audit/rounds/round11/D3/s1/wave/D3-g29/results/e196155b7525014c.json

## Unfinished

- none

## Coverage

- D3.M1: universe 1260, examined 1260, not reached 0 line(s). Enumerator `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/enumerate.py --unpinned`.
- D3.M2: universe 1260, examined 343, not reached 29 line(s). Enumerator `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/enumerate.py --unpinned`.
- D3.M3: universe 742, examined 16, not reached 46 line(s). Enumerator `awk -F'\t' '$6=="gate"' SURVIVORS.tsv`.
- D3.M4: universe 268, examined 225, not reached 43 line(s). Enumerator `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/tabulate.py --tsv | grep -P '\tSURVIVED\t'`.
- D3.M5: universe 27, examined 23, not reached 4 line(s). Enumerator `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/enumerate.py --scripts`.

Redispatched C-items under D3.M3, carried verbatim from REPORT-D3-u1b.json: C3 not_reached, C5 examined.

## Leads

- unknown custom_components/heatpump_optimizer/optimizer.py stored_heat_survival (line 3184-3186): The comment 'Capped before exp() so a near-zero demand underflows to 0.0 cleanly rather than raising' describes no reachable behaviour: math.exp of any negative argument underflows to 0.0 without raising (probe_f062e0cc415ee33e: raises 0 in both arms over exponents 720..1e301 and an overflowed one). A docs/comments seat (D5) owns the wording.

## Harnesses

- dev/audit/rounds/round11/D3/s1/fullgate.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_000221f3921dd956.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_0ea7620ce058c489.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_133158399eac10ae.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_213a122afd9ff3e1.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_2aff1f5c0b10dffa.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_2d4e3ff8e818b777.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_4434c1fcedef6b6d.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_55022279c6d6bbda.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_69e4aa41f4562af9.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_6a75a1ff72dc1df8.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_8171db177f51df33.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_8ef8417029ab8385.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_9d455ff4aaf3f3e0.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_b5d57e4a1fc22d96.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_e196155b7525014c.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_f062e0cc415ee33e.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/reach_sweep.py

## Exposure

none: no docs/ or GitHub records read; the other 46 boxes' keys.tsv on their dispatch refs were read only to name not_reached by box
