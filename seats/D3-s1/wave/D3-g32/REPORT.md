# D3-s1 wave box D3-g32 — full gate for 16 D3.M3 full-net survivors (round 11)

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`. Seat D3-s1, dimension D3, step D3.M3/M4. Findings are returned as `gate_survivors` (ids are assigned at consolidation).

## Machine and controls

```
nproc: 4
cpu:  Intel(R) Xeon(R) Processor @ 2.10GHz
               total        used        free      shared  buff/cache   available
Mem:           16087        1114       13468          12        1802       14972
Swap:              0           0           0
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  18% /
load1: 0.95
python3: /opt/hpo/python/cpython-3.14.7-linux-x86_64-gnu/bin/python3.14
2026-11-22T21:43:37Z
```

Null control (`dev/audit/rounds/round11/D3/s1/fullgate.py null`): gate_rc=1, failed scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'], summary ['3 TEST SCRIPT(S) FAILED'], wall 3337.9 s (provisional), load1 0.74..0.92.

Procedure: gate_wave.sh (dispatch ref tool, out of tree): null control once (`fullgate.py null`, comment-only marker on tariff.py), then per key of keys.tsv in order `fullgate.py run --src complete --key <key>` under a 4 h cap, one gate at a time, tree reset to the baseline between gates; the verdict is fullgate.py's (KILLED = red and a failing script beyond the null).

## Tally

- gated: 16 of 16
- KILLED: 0
- SURVIVED: 0
- RED-AS-NULL: 16
- TIMEOUT: 0
- candidates (probe moves): 6
- equivalent-candidates: 10

| key | site | patch | verdict | killed_by | wall s | class |
|---|---|---|---|---|---|---|
| 0d159d7ddd1702d9 | custom_components/heatpump_optimizer/price_model.py:544 CMP_BOUND | `if model is None or model.confidence(when) <= 0.0: -> if model is None or model.confidence(when) < 0.0:` | RED-AS-NULL | - | 3196.4 | candidate |
| 80fd46122d85566c | custom_components/heatpump_optimizer/price_model.py:820 GUARD_OFF | `if state is None: -> if False:` | RED-AS-NULL | - | 3174.3 | equivalent-candidate |
| b539d4504385a139 | custom_components/heatpump_optimizer/price_model.py:825 BOOLOP | `isinstance(attrs, dict) and attrs -> isinstance(attrs, dict) or attrs` | RED-AS-NULL | - | 3315.1 | candidate |
| 55f9ec66dc8bfd54 | custom_components/heatpump_optimizer/price_model.py:855 GUARD_OFF | `if not config.get(CONF_PRICE_ENTITY): -> if False:` | RED-AS-NULL | - | 3289.3 | equivalent-candidate |
| 88732fcb7c604858 | custom_components/heatpump_optimizer/sysid.py:549 CONST | `FAST_MODE_SETTLE_TAUS = 3.0 -> FAST_MODE_SETTLE_TAUS = 6.0` | RED-AS-NULL | - | 3212.7 | candidate |
| 176d8ddb23988b95 | custom_components/heatpump_optimizer/sysid.py:1853 GUARD_OFF | `if self.result.completed: -> if False:` | RED-AS-NULL | - | 3178.6 | equivalent-candidate |
| de399cdbe79053ea | custom_components/heatpump_optimizer/sysid.py:1640 CMP_BOUND | `and abs(room_temp - base) > self.config.max_excursion_c -> and abs(room_temp - base) >= self.config.max_excursion_c` | RED-AS-NULL | - | 3269.8 | equivalent-candidate |
| c5ddabc7d9641cba | custom_components/heatpump_optimizer/sysid.py:1573 CLAMP_DROP | `cop = max(cop, 0.1) -> cop = (cop)` | RED-AS-NULL | - | 3263.4 | equivalent-candidate |
| 75d5865af3eceda7 | custom_components/heatpump_optimizer/sysid.py:1604 CMP_BOUND | `while hi - lo > 0.01: -> while hi - lo >= 0.01:` | RED-AS-NULL | - | 3258.6 | equivalent-candidate |
| 0d5a6ef5041b90f9 | custom_components/heatpump_optimizer/sysid.py:1606 GUARD_OFF | `if fits(q, bound): -> if False:` | RED-AS-NULL | - | 3253.3 | candidate |
| 4f2d93e67ccda975 | custom_components/heatpump_optimizer/sysid.py:1626 GUARD_OFF | `if best is not None: -> if False:` | RED-AS-NULL | - | 3223.4 | equivalent-candidate |
| afbdfa240c441812 | custom_components/heatpump_optimizer/sysid.py:1593 CMP_BOUND | `return peak <= bound and final <= bound -> return peak < bound and final <= bound` | RED-AS-NULL | - | 3189.2 | equivalent-candidate |
| ebd8c531fddf0a24 | custom_components/heatpump_optimizer/sysid.py:1593 CMP_BOUND | `return peak <= bound and final <= bound -> return peak <= bound and final < bound` | RED-AS-NULL | - | 3180.3 | equivalent-candidate |
| 4a189db92053760e | custom_components/heatpump_optimizer/sysid.py:2409 GUARD_OFF | `if refusal is not None: -> if False:` | RED-AS-NULL | - | 3311.0 | candidate |
| 80cb9a8152f72e57 | custom_components/heatpump_optimizer/sysid.py:2411 CLAMP_DROP | `gains_kw = float(np.clip(gains_kw, 0.0, 2.0)) -> gains_kw = float((gains_kw))` | RED-AS-NULL | - | 3382.4 | candidate |
| 1f4a10ae90bbf2d9 | custom_components/heatpump_optimizer/sysid.py:1705 CMP_BOUND | `dt = utc_elapsed_seconds(rows[-1].when, rows[-2].when) / 3600.0 if len(rows) > 1 else 0.25 -> dt = utc_elapsed_seconds(rows[-1].when, rows[-2].when) / 3600.0 if len(rows) >= 1 else 0.25` | RED-AS-NULL | - | 3601.2 | equivalent-candidate |

## Survivors: the step-4 answers

### 0d159d7ddd1702d9 — custom_components/heatpump_optimizer/price_model.py:544 CMP_BOUND (candidate)

Patch `if model is None or model.confidence(when) <= 0.0: -> if model is None or model.confidence(when) < 0.0:` in `extend_price_series`. Full gate: RED-AS-NULL (gate_rc 1). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_0d159d7ddd1702d9.py`: baseline [3.0, 3.0, 3.0]; mutant [2.0, 2.0, 2.0]. Inputs tried: known [1,2,3] on a fresh PriceShapeModel (confidence 0); null: model None; null: constant known window [2,2,2].

Check that should have failed: tests/features.py, the extend_price_series block (~3697-3717): 'without a model the old flat repeat is used' checks model=None only and the other arms use a constant known window ([1.0]*40), where mean == last price; it lacks a check that a zero-confidence (fresh) model also repeats the last known price on a non-constant window.

Candidate: **No check pins the flat repeat for a zero-confidence price model; extend_price_series' <= 0.0 guard can loosen unseen** — severity claimed medium. Mutant 0d159d7ddd1702d9 at price_model.py:544 (`confidence(when) <= 0.0` -> `< 0.0`) survives the full gate, yet the probe's guessed tail moves from the last known price to the known window's mean: known [1,2,3] on a fresh model gives [3,3,3] at baseline and [2,2,2] under the mutant (delta 1.0 SEK/kWh per guessed step).

### 80fd46122d85566c — custom_components/heatpump_optimizer/price_model.py:820 GUARD_OFF (equivalent-candidate)

Patch `if state is None: -> if False:` in `prices_from_entity_state`. Full gate: RED-AS-NULL (gate_rc 1). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_80fd46122d85566c.py`: baseline 'Price entity is empty'; mutant 'Price entity is empty'. Inputs tried: state None at vat/surcharge (1.0,0.0) (1.25,0.3) (0.0,-1.0); non-None states unknown/{} , ''/None, numeric, unavailable+raw_today.

Check that should have failed: none: with the guard off, getattr(None, 'state', '') == '' and attrs None reach the next guard, which returns the same string; entities.py:8138's check prices_from_entity_state(None) == 'Price entity is empty' holds under both arms.

### b539d4504385a139 — custom_components/heatpump_optimizer/price_model.py:825 BOOLOP (candidate)

Patch `isinstance(attrs, dict) and attrs -> isinstance(attrs, dict) or attrs` in `prices_from_entity_state`. Full gate: RED-AS-NULL (gate_rc 1). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_b539d4504385a139.py`: baseline 'Price entity is empty'; mutant 'Price entity published no today/tomorrow series'. Inputs tried: state unknown/unavailable/'' with attributes {}, None, a non-dict tuple; null: numeric state with a 24-value series.

Check that should have failed: tests/features.py ~58585-58600 ('an unavailable price sensor still counts if it carries the series anyway'): it feeds _G8SpState('unknown', {}) but asserts only isinstance(..., str), never the reason; the assertion lacking is _g8_state_unknown == 'Price entity is empty'.

Candidate: **No check reads the reason for an unknown price entity with empty attributes; the and/or swap at prices_from_entity_state is unseen** — severity claimed low. Mutant b539d4504385a139 at price_model.py:825 (`isinstance(attrs, dict) and attrs` -> `or attrs`) survives the full gate, yet the probe's failed-fetch reason moves on 4 of 5 empty-entity inputs: 'Price entity is empty' at baseline, 'Price entity published no today/tomorrow series' under the mutant (both still a failed fetch).

### 55f9ec66dc8bfd54 — custom_components/heatpump_optimizer/price_model.py:855 GUARD_OFF (equivalent-candidate)

Patch `if not config.get(CONF_PRICE_ENTITY): -> if False:` in `pull_prices`. Full gate: RED-AS-NULL (gate_rc 1). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_55f9ec66dc8bfd54.py`: baseline ('fail', 'Price entity is empty'); mutant ('fail', 'Price entity is empty'). Inputs tried: through the coordinator's composition _price_entity_state + pull_prices: entity absent / '' / None with a hass whose every lookup finds a valid sensor (moved 0/3); direct pull_prices with a valid state and no entity configured (moved 1: reason only), an input the one call site (coordinator._fetch_tibber_prices) cannot produce because _price_entity_state returns None when no entity is configured.

Check that should have failed: none reachable: the only production caller hands None whenever the entity is unset, and prices_from_entity_state(None) returns the same ('fail', 'Price entity is empty'); features.py:58756's _g8_pull_noent check holds under both arms.

### 88732fcb7c604858 — custom_components/heatpump_optimizer/sysid.py:549 CONST (candidate)

Patch `FAST_MODE_SETTLE_TAUS = 3.0 -> FAST_MODE_SETTLE_TAUS = 6.0` in `<module>`. Full gate: RED-AS-NULL (gate_rc 1). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_88732fcb7c604858.py`: baseline (True, 'ok') at tau_fast 0.25 h; mutant (False, 'slab mode too slow ... needs 1.5 h ...') at tau_fast 0.25 h. Inputs tried: c_r=c_s=1, k_s in 0.4..6.0 (tau_fast 0.083-1.25 h) on the default 1 h shortest phase: 4 verdicts moved (tau_fast 0.200-0.333 h); null: c_s=0.

Check that should have failed: tests/features.py ~53978-53986 (#1401) calls slab_mode_one_state_identifiability only with unset slab constants (refused before the constant is read) and #1329 (~54066-54090) prices the shipped presets (tau_fast 0.94-3.72 h, refused under both 3 and 6); the assertion lacking is an admitted plant at tau_fast in (1/6, 1/3] h (e.g. c_r=c_s=1, k_s=2: tau 0.25 h) returning (True, 'ok').

Candidate: **No check admits a fast slab mode through the one-state predicate; FAST_MODE_SETTLE_TAUS can double unseen** — severity claimed low. Mutant 88732fcb7c604858 at sysid.py:549 (`FAST_MODE_SETTLE_TAUS = 3.0` -> `6.0`) survives the full gate, yet slab_mode_one_state_identifiability's verdict moves from admitted to refused for 4 of 10 plants (tau_fast 0.200-0.333 h on the default 1 h shortest phase). Its one consumer (identify_slab's cadence-gap fallback) returns completed=False either way, so what moves downstream is the refusal reason.

### 176d8ddb23988b95 — custom_components/heatpump_optimizer/sysid.py:1853 GUARD_OFF (equivalent-candidate)

Patch `if self.result.completed: -> if False:` in `SystemIdentification._finish`. Full gate: RED-AS-NULL (gate_rc 1). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_176d8ddb23988b95.py`: baseline state (phase, last_run, result, routing flag) after _finish; 1 INFO record; mutant the same state; 0 INFO records. Inputs tried: identify_slab stubbed to a completed result and to a refusal ('fit failed'); state moved 0 in both; only the INFO 'System identification complete' record differs.

Check that should have failed: none behavioural: the branch only logs at INFO; a log-content check would be the only detector, and no seat has named that log line as behaviour.

### de399cdbe79053ea — custom_components/heatpump_optimizer/sysid.py:1640 CMP_BOUND (equivalent-candidate)

Patch `and abs(room_temp - base) > self.config.max_excursion_c -> and abs(room_temp - base) >= self.config.max_excursion_c` in `SystemIdentification._over_excursion`. Full gate: RED-AS-NULL (gate_rc 1). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_de399cdbe79053ea.py`: baseline False at an exact float tie; mutant True at an exact float tie. Inputs tried: 202 readings at 0.1 C resolution (15-25 C, room = base +- 0.8) moved 0 and had 0 exact ties; 2002 at 0.01 C, 402 at 0.05 C and 42 at 0.5 C had 0 exact ties (scratch scan); 600000 random indoor readings (base U[5,30] C, room base+-0.8 and both float neighbours) moved 0; the only tie found is base 0.2 C, room 1.0 C (moved), outside any indoor reading; max_excursion_c is fixed at 0.8 (SysIdConfig default, the coordinator never sets it), and 0.8 is not a multiple of ulp(x) for |x| >= 1, so no tie exists for room temperatures at or above 1 C.

Check that should have failed: none reachable: a check at |room - base| == 0.8 exactly cannot be built from indoor readings at or above 1 C.

### c5ddabc7d9641cba — custom_components/heatpump_optimizer/sysid.py:1573 CLAMP_DROP (equivalent-candidate)

Patch `cop = max(cop, 0.1) -> cop = (cop)` in `SystemIdentification._size_step_power`. Full gate: RED-AS-NULL (gate_rc 1). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_c5ddabc7d9641cba.py`: baseline 130.546875 kW at max_power 160, cop 0.05/0.0; mutant 160.0 kW. Inputs tried: 384 inputs at cop in {0, 0.05, 0.09, -1} x max_power {3,6,12,40,80,160} x outdoor {2,12,16,18} x 4 houses: 68 moved, all at max_power 160 kW; 24 inputs at cop >= 0.1 moved 0; production's cop is ThermalModel.compute_cop, floored at 1.0 by the COP law (min 1.050 over outdoor -40..40 C), so the dropped 0.1 floor never acts.

Check that should have failed: none reachable: the floor binds only below cop 0.1, which compute_cop never returns.

### 75d5865af3eceda7 — custom_components/heatpump_optimizer/sysid.py:1604 CMP_BOUND (equivalent-candidate)

Patch `while hi - lo > 0.01: -> while hi - lo >= 0.01:` in `SystemIdentification._size_step_power`. Full gate: RED-AS-NULL (gate_rc 1). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_75d5865af3eceda7.py`: baseline step power; mutant identical step power. Inputs tried: 216 tie inputs (q_max = 0.01*2^k, k 6..11, cop 1/2/4, outdoor 2/-5/8, 4 houses; 45 of them bisect) moved 0; 360 generic inputs moved 0: the extra halving at hi - lo == 0.01 only narrows the bracket and never changes best's value at the returned precision.

Check that should have failed: none found: the tie input bisects and returns the same power.

### 0d5a6ef5041b90f9 — custom_components/heatpump_optimizer/sysid.py:1606 GUARD_OFF (candidate)

Patch `if fits(q, bound): -> if False:` in `SystemIdentification._size_step_power`. Full gate: RED-AS-NULL (gate_rc 1). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_0d5a6ef5041b90f9.py`: baseline 4.353515625 kW (peak 0.6499 C under bound 0.65); mutant 4.3125 kW (peak 0.6402 C). Inputs tried: 6 argument sets x 4 houses: 7 of 24 moved (every one where fits(q_max) fails and a grid point fits); the D2-s4-02 cell (6 kW, COP 3, 21 C, 2 C, ua 0.20, C 8.0, gains 0.3) is one of them.

Check that should have failed: tests/features.py ~2582-2600 (D2-s4-02) sizes exactly this cell but accepts bound - 0.05 <= peak <= bound: the mutant's peak 0.6402 C lies inside [0.60, 0.65]; the assertion lacking is a tolerance at the sizer's own 0.01 kW resolution (peak within ~0.005 C of the bound), or the sized step against an independent bisection.

Candidate: **The sizer's bisection branch can be disabled unseen: the D2-s4-02 check accepts a step 0.04 kW short** — severity claimed low. Mutant 0d5a6ef5041b90f9 at sysid.py:1606 (`if fits(q, bound):` -> `if False:`) survives the full gate, yet the probe's sized step moves on 7 of 24 inputs; on tests/features.py's own D2-s4-02 cell the step falls from 4.3535 to 4.3125 kW and its peak from 0.6499 to 0.6402 C, inside that check's 0.05 C tolerance.

### 4f2d93e67ccda975 — custom_components/heatpump_optimizer/sysid.py:1626 GUARD_OFF (equivalent-candidate)

Patch `if best is not None: -> if False:` in `SystemIdentification._size_step_power`. Full gate: RED-AS-NULL (gate_rc 1). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_4f2d93e67ccda975.py`: baseline step power; 1 DEBUG record; mutant identical step power; 0 DEBUG records. Inputs tried: 6 argument sets x 4 houses: returned value moved 0 of 24; the block's only effect is the 'System identification sizer' DEBUG line.

Check that should have failed: none behavioural: the guarded block only computes a one-state peak for a DEBUG log.

### afbdfa240c441812 — custom_components/heatpump_optimizer/sysid.py:1593 CMP_BOUND (equivalent-candidate)

Patch `return peak <= bound and final <= bound -> return peak < bound and final <= bound` in `SystemIdentification._size_step_power.fits`. Full gate: RED-AS-NULL (gate_rc 1). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_afbdfa240c441812.py`: baseline 6.0 kW with the predictor stubbed to (0.8, 0.7); mutant None. Inputs tried: 360 real rollouts (5 powers x 3 COPs x 2 baselines x 3 outdoors x 4 houses) moved 0; a peak exactly equal to the bound occurred only with the two-state predictor stubbed to return it (moved: 6.0 -> None); null stub 0.01 C under: 6.0 both.

Check that should have failed: none reachable: an exact float tie of a rollout's peak with 0.65/0.8 C was not produced by any real input; the stubbed tie is a collaborator substitution, not an input.

### ebd8c531fddf0a24 — custom_components/heatpump_optimizer/sysid.py:1593 CMP_BOUND (equivalent-candidate)

Patch `return peak <= bound and final <= bound -> return peak <= bound and final < bound` in `SystemIdentification._size_step_power.fits`. Full gate: RED-AS-NULL (gate_rc 1). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_ebd8c531fddf0a24.py`: baseline 6.0 kW with the predictor stubbed to (0.7, 0.8); mutant None. Inputs tried: 360 real rollouts moved 0; the final == bound tie occurred only with the predictor stubbed (moved: 6.0 -> None); null stub 0.01 C under: 6.0 both.

Check that should have failed: none reachable: as afbdfa240c441812, for the final-temperature half of the same comparison.

### 4a189db92053760e — custom_components/heatpump_optimizer/sysid.py:2409 GUARD_OFF (candidate)

Patch `if refusal is not None: -> if False:` in `SystemIdentification._slab_outcome`. Full gate: RED-AS-NULL (gate_rc 1). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_4a189db92053760e.py`: baseline (False, 'fitted gains outside plausible bounds' | 'fitted parameters outside plausible bounds', None); mutant (True, 'ok', gains clipped). Inputs tried: 21 converged fits (ua 0.005/0.2/6.0 x C 4.0 x gains -0.8..2.5; negative capacities skipped, the solver works in log space): 16 moved from refused to completed; null in-band fit (0.2, 4.0, 0.4): 0.

Check that should have failed: tests/features.py ~53988 (#1401) calls _slab_refusal directly and never drives _slab_outcome with an out-of-band fit; the assertion lacking is _slab_outcome on a converged out-of-band best_x (e.g. ua 0.2, gains 2.5, which the solver's (-5, 10) gains clip admits) returning completed=False with the refusal reason.

Candidate: **No check drives _slab_outcome with an implausible fit; dropping its refusal return publishes the fit as completed** — severity claimed medium. Mutant 4a189db92053760e at sysid.py:2409 (`if refusal is not None:` -> `if False:`) survives the full gate, yet the probe's _slab_outcome result moves from refused (completed=False, 'fitted gains/parameters outside plausible bounds') to completed=True, reason 'ok' on 16 of 21 converged fits; the slab fit's solver clips gains only to (-5, 10) and leaves UA unbounded, so such fits reach this line.

### 80cb9a8152f72e57 — custom_components/heatpump_optimizer/sysid.py:2411 CLAMP_DROP (candidate)

Patch `gains_kw = float(np.clip(gains_kw, 0.0, 2.0)) -> gains_kw = float((gains_kw))` in `SystemIdentification._slab_outcome`. Full gate: RED-AS-NULL (gate_rc 1). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_80cb9a8152f72e57.py`: baseline internal_gains_kw 0.0 for fitted gains -0.5/-0.3/-0.1/-1e-6; mutant the negative value itself. Inputs tried: fitted gains -0.5, -0.3, -0.1, -1e-6, 0.0, 0.4, 1.99, 2.0 at ua 0.2, C 4.0: 4 of 8 moved (all in [-0.5, 0)).

Check that should have failed: no check in tests/features.py or tests/entities.py drives _slab_outcome with a fitted gains value in [-0.5, 0) (admitted by _slab_refusal's -0.5 lower band); the assertion lacking is internal_gains_kw == 0.0 for such a fit.

Candidate: **No check pins the slab fit's gains clip; negative internal gains can be published unseen** — severity claimed low. Mutant 80cb9a8152f72e57 at sysid.py:2411 (np.clip(gains_kw, 0.0, 2.0) dropped) survives the full gate, yet the probe's published internal_gains_kw moves on 4 of 8 fitted gains values: every fit in [-0.5, 0) publishes 0.0 at baseline and the negative value under the mutant (-0.5 kW at the band's edge).

### 1f4a10ae90bbf2d9 — custom_components/heatpump_optimizer/sysid.py:1705 CMP_BOUND (equivalent-candidate)

Patch `dt = utc_elapsed_seconds(rows[-1].when, rows[-2].when) / 3600.0 if len(rows) > 1 else 0.25 -> dt = utc_elapsed_seconds(rows[-1].when, rows[-2].when) / 3600.0 if len(rows) >= 1 else 0.25` in `SystemIdentification._unadoptable`. Full gate: RED-AS-NULL (gate_rc 1). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_1f4a10ae90bbf2d9.py`: baseline refusal string (dt 0.25 h default) at 1 settling row; mutant raised IndexError at 1 settling row. Inputs tried: 0/1/2/4 settling rows called directly: only 1 row moves (IndexError from rows[-2]); driving step() from SETTLING at 15/30/60/90-min cadence, _unadoptable is reached 4 times, always with >= 2 settling rows (the first settling call has elapsed 0 < settle_hours 1.0, a constant the coordinator never sets), so the one-row input is unreachable.

Check that should have failed: none reachable: production reaches _unadoptable only with >= 2 settling rows.

## Unfinished

- none

## Harnesses

- `dev/audit/rounds/round11/D3/s1/fullgate.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g32/build.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g32/report.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_0d159d7ddd1702d9.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_80fd46122d85566c.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_b539d4504385a139.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_55f9ec66dc8bfd54.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_88732fcb7c604858.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_176d8ddb23988b95.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_de399cdbe79053ea.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_c5ddabc7d9641cba.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_75d5865af3eceda7.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_0d5a6ef5041b90f9.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_4f2d93e67ccda975.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_afbdfa240c441812.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_ebd8c531fddf0a24.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_4a189db92053760e.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_80cb9a8152f72e57.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_1f4a10ae90bbf2d9.py`
