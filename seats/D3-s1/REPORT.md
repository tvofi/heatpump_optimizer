# D3-s1 round 11, box D3-u1c slice (baseline 92d38ecb)

Seat D3-s1, resume box D3-u1c: the D3.M2 slice `state/keys-D3-u1c.txt` (309 keys, `8206a42b98c8dd86` <= key < `c0ecc8e0b6b66ded` of `state/u1_keys.txt` less carried results; sha256 5f427b5e35ba1659...) and D3.M3's full net for its survivors. D3-s1-01 (box D3R) is not re-reported. The full GATE_SCOPE=full GOLDEN_MODE=drift gate is box D3-top6's.

## Method

R0 restored c0adbc19's s1/ directory. R1: state/baselines.json was box D3R's, so all 21 drivers' traced baselines were re-taken here (`prescreen.py baseline --workers 4`, all rc=0 failed=0; D3R's kept as state/superseded/baselines-D3R.json) and the env_drift capture child re-traced (`prescreen.py trace-capture`, procs 2/2). Null control LIVES (16 fast drivers); positive control 2/2 KILLED by tests/manual_plan.py. K1: `prescreen.py run --anchors state/keys-D3-u1c.txt --sub pre --workers 4` (fresh tree per mutant). K2: `prescreen.py complete --src pre --keys state/keys-D3-u1c-surv.txt --workers 4`. Driven by u1c_chain.sh, checkpointed by u1c_ckloop.sh (every 25 pre-screened keys, every full-net result).

Machine: box D3-u1c: Linux x86_64, nproc 4, Intel(R) Xeon(R) Processor @ 2.30GHz, 16 GB, venv-ci CPython 3.14.7 (numpy 2.5.4, scipy 1.18.1), alone on the box. Every wall figure is provisional: true; counts and verdicts are final.

## Tally

- D3-u1c slice: 309 keys, 0 unparseable, 309 driven by the fast net (fast closure scripts + env_drift --all HEAD^1): 64 killed, 245 survived, 0 timeout, 0 with every driver skipped by reach; first kills typing_ruler.py 26, env_drift.py 11, plan_view.py 7, solar_alignment.py 6, manual_plan.py 6, structure.py 4, finite_boundary.py 2, doc_claims.py 1, block_duty.py 1; driver skips by the gate's reach rule 1600, by the relaxed rule 152.
- D3-u1c full net (prescreen.py complete, every deferred/relaxed-skipped closure driver, no relaxation, no early stop) on 72 of 245 slice survivors: 14 killed, 58 survived, 0 timeout; kills per driver (every kill) features.py 12, entities.py 3, harness_headers.py 1; sole killer features.py 11, entities.py 2.
- Provisional (judge re-takes): fast-net wall per mutant median 201 s, full-net wall per survivor median 1354 s, 4 workers, box D3-u1c: Linux x86_64, nproc 4, Intel(R) Xeon(R) Processor @ 2.30GHz, 16 GB, venv-ci CPython 3.14.7 (numpy 2.5.4, scipy 1.18.1), alone on the box, load1 1-5.

## Coverage

- D3.M2: universe 1260, examined 340, not reached 10 line(s). Enumerator: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/enumerate.py --unpinned`
- D3.M3: universe 280, examined 74, not reached 206 line(s). Enumerator: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/tabulate.py --tsv | grep -P '\tSURVIVED\t'`
- D3.M4: universe 280, examined 280, not reached 0 line(s). Enumerator: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/tabulate.py --tsv | grep -P '\tSURVIVED\t'`

## Prescreened survivors of the full net (for box D3-top6's full gate), with D3.M4's answer

| site | patch | should have failed |
|---|---|---|
| custom_components/heatpump_optimizer/optimizer.py:2144 CMP_BOUND 8d209fd1 | `if baseline_cost <= 0.01:  ->  if baseline_cost < 0.01:` | block_duty.py, boost_drift_replay.py, config_flow_steps.py, doc_claims.py, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py,  |
| custom_components/heatpump_optimizer/thermal_model.py:835 CMP_BOUND 855229b8 | `if swing <= 0.0:  ->  if swing < 0.0:` | block_duty.py, boost_drift_replay.py, config_flow_steps.py, entities.py, features.py, finite_boundary.py, manual_plan.py, solar_alignment.py |
| custom_components/heatpump_optimizer/sysid.py:1708 CMP_BOUND 9330e956 | `or self._baseline_temp is None or not 1e-3 < dt <= 2.0  ->  or self._baseline_temp is None` | entities.py, features.py |
| custom_components/heatpump_optimizer/defrost.py:802 GUARD_OFF ea64107d | `if self._state and self._since is not None:  ->  if False:` | boost_drift_replay.py, config_flow_steps.py, entities.py, features.py |
| custom_components/heatpump_optimizer/coordinator.py:5108 CMP_BOUND 9f0fd699 | `if capacity <= 1e-6:  ->  if capacity < 1e-6:` | block_duty.py, boost_drift_replay.py, config_flow_steps.py, entities.py, features.py, finite_boundary.py, manual_plan.py, solar_alignment.py |
| custom_components/heatpump_optimizer/optimizer.py:2796 GUARD_OFF 22a69ea5 | `if self.day_end_hour_weekend is not None:  ->  if False:` | boost_drift_replay.py, entities.py, features.py |
| custom_components/heatpump_optimizer/sysid.py:2010 CLAMP_DROP bea40588 | `k_hat = max(float(pass1[0]), 0.0)  ->  k_hat = (float(pass1[0]))` | features.py |
| custom_components/heatpump_optimizer/coordinator.py:900 CMP_BOUND ad0739c1 | `if gap_minutes <= OUTAGE_GAP_MINUTES:  ->  if gap_minutes < OUTAGE_GAP_MINUTES:` | features.py |
| custom_components/heatpump_optimizer/sysid.py:892 CMP_BOUND ebe7af8b | `if not (-0.5 <= gains_kw <= 2.0):  ->  if not (-0.5 <= gains_kw < 2.0):` | entities.py, features.py |
| custom_components/heatpump_optimizer/coordinator.py:11091 CLAMP_DROP b4fd5e0d | `override / max(ctx._thermal_params.max_electrical_power, 0.1)  ->  override / (ctx._therma` | entities.py, features.py |
| custom_components/heatpump_optimizer/dhw_planner.py:2232 CLAMP_DROP f29a02b3 | `j for j in range(max(0, k - max_lead_steps), k + 1) if usable(j)  ->  j for j in range((0)` | block_duty.py, doc_claims.py, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py, validate.py |
| custom_components/heatpump_optimizer/optimizer.py:5211 CMP_BOUND f6038118 | `while j >= 0:  ->  while j > 0:` | block_duty.py, features.py, manual_plan.py |
| custom_components/heatpump_optimizer/sysid.py:1212 CMP_BOUND 950dc213 | `hold = (baseline - r0) / (r1 - r0) if abs(r1 - r0) > 1e-12 else 0.0  ->  hold = (baseline ` | entities.py, features.py |
| custom_components/heatpump_optimizer/tariff.py:391 CMP_BOUND ea09d31b | `if len(self.peaks) < n:  ->  if len(self.peaks) <= n:` | entities.py, features.py, finite_boundary.py |
| custom_components/heatpump_optimizer/thermal_model.py:4578 BOOLOP afe9dcd9 | `if p.two_zone_enabled and throttled:  ->  if p.two_zone_enabled or throttled:` | block_duty.py, boost_drift_replay.py, config_flow_steps.py, doc_claims.py, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py,  |
| custom_components/heatpump_optimizer/sysid.py:2126 CMP_BOUND 036bc6d8 | `if one_over_c <= 1e-6 or ua_over_c <= 1e-6:  ->  if one_over_c <= 1e-6 or ua_over_c < 1e-6` | features.py |
| custom_components/heatpump_optimizer/sysid.py:1785 RETURN_DEL b2994929#2 | `return None  ->  pass` | features.py |
| custom_components/heatpump_optimizer/thermal_model.py:2598 GUARD_OFF 549bb130 | `elif available <= 0.0:  ->  elif False:` | entities.py, env_drift.py, features.py, validate.py |
| custom_components/heatpump_optimizer/price_model.py:535 CMP_BOUND 4b53a999 | `if shape_mean > 1e-6:  ->  if shape_mean >= 1e-6:` | entities.py, features.py |
| custom_components/heatpump_optimizer/sysid.py:549 CONST 745545cd | `FAST_MODE_SETTLE_TAUS = 3.0  ->  FAST_MODE_SETTLE_TAUS = 6.0` | block_duty.py, boost_drift_replay.py, config_flow_steps.py, debug_collect.py, doc_claims.py, entities.py, env_drift.py, features.py, finite_boundary.py, guard_p |
| custom_components/heatpump_optimizer/dhw_planner.py:2236 GUARD_OFF 4d962260#2 | `if not candidates:  ->  if False:` | block_duty.py, doc_claims.py, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py, validate.py |
| custom_components/heatpump_optimizer/dhw_planner.py:548 CMP_BOUND d8dd626d | `busy_hours = [h for h in range(24) if pattern[h] >= threshold]  ->  busy_hours = [h for h ` | env_drift.py, features.py |
| custom_components/heatpump_optimizer/coordinator.py:3013 CMP_BOUND 9a9af603 | `if not math.isfinite(value) or not lo <= value <= hi:  ->  if not math.isfinite(value) or ` | entities.py, features.py |
| custom_components/heatpump_optimizer/coordinator.py:10188 GUARD_OFF 43fd1c3a | `if not trajectory:  ->  if False:` | config_flow_steps.py, entities.py, features.py |
| custom_components/heatpump_optimizer/thermal_model.py:4463 BOOLOP 66b15be8 | `if flow_carnot_eligible and p.cop_flow_carnot:  ->  if flow_carnot_eligible or p.cop_flow_` | block_duty.py, boost_drift_replay.py, config_flow_steps.py, doc_claims.py, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py,  |
| custom_components/heatpump_optimizer/coordinator.py:9386 GUARD_OFF aba82b00 | `if capacity <= 1e-6 or dt_h <= 1e-6:  ->  if False:` | features.py |
| custom_components/heatpump_optimizer/coordinator.py:467 CMP_BOUND 713016cb | `if not np.isfinite(count) or not 0 <= count <= 2**31:  ->  if not np.isfinite(count) or no` | boost_drift_replay.py, features.py, finite_boundary.py |
| custom_components/heatpump_optimizer/coordinator.py:6752 BOOLOP 9f6c1950 | `elif wood_mean is not None and not had:  ->  elif wood_mean is not None or not had:` | features.py |
| custom_components/heatpump_optimizer/optimizer.py:5059 GUARD_OFF 720b1445 | `if not bool(expensive.any()) or not bool(charging.any()):  ->  if False:` | env_drift.py, features.py |
| custom_components/heatpump_optimizer/coordinator.py:9931 GUARD_OFF cdf855f8 | `if not self._weather_forecast:  ->  if False:` | block_duty.py, boost_drift_replay.py, config_flow_steps.py, entities.py, env_drift.py, features.py, finite_boundary.py, manual_plan.py, solar_alignment.py |
| custom_components/heatpump_optimizer/coordinator.py:10192 CMP_BOUND 8a040c32 | `if 0 < idx < len(trajectory):  ->  if 0 < idx <= len(trajectory):` | entities.py, features.py |
| custom_components/heatpump_optimizer/coordinator.py:11002 CMP_BOUND 3036d119 | `if float(np.max(prices) - np.min(prices)) / mean_price < 0.15:  ->  if float(np.max(prices` | config_flow_steps.py, features.py |
| custom_components/heatpump_optimizer/dhw_planner.py:1528 CLAMP_DROP 16576d0c | `headroom = np.clip(p_total_max - demand, 0.0, None)  ->  headroom = (p_total_max - demand)` | block_duty.py, doc_claims.py, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py, validate.py |
| custom_components/heatpump_optimizer/coordinator.py:9440 CMP_BOUND 9f0fd699 | `if capacity <= 1e-6:  ->  if capacity < 1e-6:` | features.py |
| custom_components/heatpump_optimizer/dhw_planner.py:807 CMP_BOUND b8ab8111 | `if temp <= everyday:  ->  if temp < everyday:` | env_drift.py, features.py, guard_pins.py, manual_plan.py |
| custom_components/heatpump_optimizer/optimizer.py:5229 CMP_BOUND 9384ba6e | `pinned_off = not _pin_is_free(pin) and pin < 0.5  ->  pinned_off = not _pin_is_free(pin) a` | features.py, manual_plan.py, optimality.py |
| custom_components/heatpump_optimizer/optimizer.py:3177 CMP_BOUND ddd90b1f | `if span <= 0.0:  ->  if span < 0.0:` | env_drift.py, features.py, validate.py |
| custom_components/heatpump_optimizer/dhw_planner.py:1343 CLAMP_DROP 051a1593 | `horizon = min(n_steps, max(1, int(round(2.0 / max(dt, 1e-6)))))  ->  horizon = min(n_steps` | env_drift.py, features.py |
| custom_components/heatpump_optimizer/dhw_planner.py:659 CLAMP_DROP 29c2028d | `limit = max(first + 1, min(deadline_step + 1, n_steps))  ->  limit = max(first + 1, (deadl` | env_drift.py, features.py, manual_plan.py |
| custom_components/heatpump_optimizer/dhw_planner.py:1343 CLAMP_DROP 051a1593 | `horizon = min(n_steps, max(1, int(round(2.0 / max(dt, 1e-6)))))  ->  horizon = min(n_steps` | env_drift.py, features.py |
| custom_components/heatpump_optimizer/dhw_planner.py:470 CMP_BOUND 6e5e1a9f | `if surplus is None or not np.any(surplus[: len(prices)] > 1e-6):  ->  if surplus is None o` | block_duty.py, doc_claims.py, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py, validate.py |
| custom_components/heatpump_optimizer/optimizer.py:5234 GUARD_OFF e1c03d20 | `if pinned_off:  ->  if False:` | features.py, manual_plan.py, optimality.py |
| custom_components/heatpump_optimizer/optimizer.py:5271 CMP_BOUND 32915bf0 | `while j >= 0 and not _pin_is_free(float(pins[j])) and float(pins[j]) < 0.5:  ->  while j >` | features.py, manual_plan.py |
| custom_components/heatpump_optimizer/optimizer.py:5044 GUARD_OFF cf033f9b | `if n == 0 or len(prices) != n:  ->  if False:` | env_drift.py, features.py |
| custom_components/heatpump_optimizer/sysid.py:677 CMP_BOUND f4619cef | `if not (c_r > 1e-9 and c_s > 1e-9 and k_s > 1e-9) or not settle_band > 1e-9:  ->  if not (` | features.py |
| custom_components/heatpump_optimizer/grid_fee.py:496 RETURN_DEL d7923b87#3 | `return None  ->  pass` | none of the closure executes the line: a direct check on apply_catalog |
| custom_components/heatpump_optimizer/dhw_planner.py:1800 CMP_BOUND c97627da | `pinned = np.where(temps[: b + 1] >= ceiling[: b + 1] - 0.1)[0]  ->  pinned = np.where(temp` | block_duty.py, doc_claims.py, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py, validate.py |
| custom_components/heatpump_optimizer/grid_fee.py:483 GUARD_OFF 481898b9 | `if not product_id or product_id == DSO_PRODUCT_NONE:  ->  if False:` | config_flow_steps.py, entities.py, features.py |
| custom_components/heatpump_optimizer/thermal_model.py:2903 CMP_BOUND 5dfd3ad3 | `if hp_temp > flow_set:  ->  if hp_temp >= flow_set:` | env_drift.py, features.py |
| custom_components/heatpump_optimizer/optimizer.py:1996 GUARD_OFF dd7f271c | `if best is None:  ->  if False:` | block_duty.py, boost_drift_replay.py, config_flow_steps.py, doc_claims.py, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py,  |
| custom_components/heatpump_optimizer/thermal_model.py:3569 CLAMP_DROP c141a98b | `alpha = float(np.clip(dt_hours / tau, 0.0, 1.0))  ->  alpha = float((dt_hours / tau))` | boost_drift_replay.py, entities.py, features.py |
| custom_components/heatpump_optimizer/dhw_planner.py:1893 GUARD_OFF 0cdf6545 | `if np.array_equal(plan, before):  ->  if False:` | block_duty.py, doc_claims.py, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py, validate.py |
| custom_components/heatpump_optimizer/coordinator.py:6615 GUARD_OFF 49b44a5c | `if pending:  ->  if False:` | config_flow_steps.py, entities.py, features.py |
| custom_components/heatpump_optimizer/sysid.py:2376 CLAMP_DROP 73b72613 | `np.log(max(cr0 * mult, 1e-2)),  ->  np.log((cr0 * mult)),` | entities.py, features.py |
| custom_components/heatpump_optimizer/dhw_planner.py:1346 GUARD_OFF 71cd0ad3 | `if legionella_step is not None:  ->  if False:` | env_drift.py, features.py |
| custom_components/heatpump_optimizer/thermal_model.py:4460 GUARD_OFF 4cb5c458 | `if hum_i is None:  ->  if False:` | boost_drift_replay.py, config_flow_steps.py, entities.py, features.py |
| custom_components/heatpump_optimizer/sysid.py:1913 CMP_BOUND 8acc76b0 | `if len(usable) < 6:  ->  if len(usable) <= 6:` | features.py |
| custom_components/heatpump_optimizer/coordinator.py:5658 GUARD_OFF 9be11266 | `if buffer_temp > previous_temp:  ->  if False:` | features.py |

## Findings

None from this box: per D3.md step 3 the slice's survivors are candidates; only the quiet-window full gate (box D3-top6) makes findings.

## Non-findings

- Null control: the fast net LIVES on the unmutated tree (re-taken on box D3-u1c after re-taking all 21 traced baselines, all rc=0 failed=0): `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/prescreen.py null` -> null_verdict=LIVES over 16 fast drivers (state/null-D3-u1c.json, state/u1c-null.out)
- Positive control: the pre-screen kills ledger-pinned sites on this box: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/prescreen.py run --anchors dev/audit/rounds/round11/D3/s1/posctl_anchors.txt --sub posctl-D3-u1c` -> 2/2 KILLED by tests/manual_plan.py (state/u1c-posctl.out)
- 64 of 309 D3-u1c slice mutants are pinned by the fast net: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/u1c_slice.py` -> D3-u1c slice: 309 keys, 0 unparseable, 309 driven by the fast net (fast closure scripts + env_drift --all HEAD^1): 64 killed, 245 survived, 0 timeout, 0 with every driver skipped by reach; first kills typing_ruler.py 26, env_drift.py 11, plan_view.py 7, solar_alignment.py 6, manual_plan.py 6, structure.py 4, finite_boundary.py 2, doc_claims.py 1, block_duty.py 1; driver skips by the gate's reach rule 1600, by the relaxed rule 152.
- 14 of 72 fast-net survivors of the slice are pinned by the full closure net: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/u1c_slice.py` -> D3-u1c full net (prescreen.py complete, every deferred/relaxed-skipped closure driver, no relaxation, no early stop) on 72 of 245 slice survivors: 14 killed, 58 survived, 0 timeout; kills per driver (every kill) features.py 12, entities.py 3, harness_headers.py 1; sole killer features.py 11, entities.py 2. Killed sites: defrost.py:106 by features.py; coordinator.py:4893 by features.py; coordinator.py:3168 by features.py; coordinator.py:3102 by features.py; defrost.py:729 by features.py; coordinator.py:539 by features.py; coordinator.py:6537 by features.py; grid_fee.py:355 by features.py; sysid.py:1779 by harness_headers.py,entities.py,features.py; coordinator.py:7494 by entities.py; grid_fee.py:331 by features.py; coordinator.py:9360 by entities.py; grid_fee.py:383 by features.py; optimizer.py:5271 by features.py

## Harnesses

- `dev/audit/rounds/round11/D3/s1/enumerate.py`
- `dev/audit/rounds/round11/D3/s1/prescreen.py`
- `dev/audit/rounds/round11/D3/s1/tabulate.py`
- `dev/audit/rounds/round11/D3/s1/m5_closure_reach.py`
- `dev/audit/rounds/round11/D3/s1/m5_solves.py`
- `dev/audit/rounds/round11/D3/s1/m5_envdrift_reach.py`
- `dev/audit/rounds/round11/D3/s1/build_report.py`
- `dev/audit/rounds/round11/D3/s1/finalize.py`
- `dev/audit/rounds/round11/D3/s1/u1c_slice.py`
- `dev/audit/rounds/round11/D3/s1/u1c_report.py`
- `dev/audit/rounds/round11/D3/s1/u1c_chain.sh`
- `dev/audit/rounds/round11/D3/s1/u1c_ckloop.sh`

## Unfinished

None for this box's slice.

## Exposure

No docs/ or GitHub read. Redispatch items C2/C3/C6 name round-10 mutant ids from dev/audit/rounds/round10/D3/s1/mutants.py, which the export strips: the seat read that one file from the worktree's object store (git show HEAD:...) only to re-draw its seed-10 sample at this baseline (c2_mutants.json, c3c6_mutants.json); no round-10 report, verdict or finding text was read. `git diff --stat HEAD^1 HEAD -- custom_components` was run once to confirm the env_drift comparison ref HEAD^1 (2c84a85c) carries production byte-identical to the baseline. Box D3R run (inline in the box session, the Agent spawn being refused by the frugal guard): read COMMON.md, D3.md, dev/audit/README.md, finding.schema.json (through a haiku extractor), the seat's own carried harnesses and state, and the three new survivor lines in custom_components; no docs/ or GitHub read beyond the box's own dispatch/inbox/wip refs. Box D3-u1c run: read the carried evidence directory (c0adbc19, box D3R's return), COMMON.md, D3.md, dev/audit/README.md, finding.schema.json; no docs/, no GitHub, no earlier-round findings.
