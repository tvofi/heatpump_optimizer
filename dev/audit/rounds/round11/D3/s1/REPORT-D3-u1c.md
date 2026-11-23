# D3-s1 round 11, box D3-u1c slice (baseline 92d38ecb)

Seat D3-s1, resume box D3-u1c: the D3.M2 slice `state/keys-D3-u1c.txt` (309 keys, `8206a42b98c8dd86` <= key < `c0ecc8e0b6b66ded` of `state/u1_keys.txt` less carried results; sha256 5f427b5e35ba1659...) and D3.M3's full net for its survivors. D3-s1-01 (box D3R) is not re-reported. The full GATE_SCOPE=full GOLDEN_MODE=drift gate is box D3-top6's.

## Method

R0 restored c0adbc19's s1/ directory. R1: state/baselines.json was box D3R's, so all 21 drivers' traced baselines were re-taken here (`prescreen.py baseline --workers 4`, all rc=0 failed=0; D3R's kept as state/superseded/baselines-D3R.json) and the env_drift capture child re-traced (`prescreen.py trace-capture`, procs 2/2). Null control LIVES (16 fast drivers); positive control 2/2 KILLED by tests/manual_plan.py. K1: `prescreen.py run --anchors state/keys-D3-u1c.txt --sub pre --workers 4` (fresh tree per mutant). K2: `prescreen.py complete --src pre --keys state/keys-D3-u1c-surv.txt --workers 4`. Driven by u1c_chain.sh, checkpointed by u1c_ckloop.sh (every 25 pre-screened keys, every full-net result).

Machine: box D3-u1c: Linux x86_64, nproc 4, Intel(R) Xeon(R) Processor @ 2.10GHz (re-fire host; 2.30GHz before the restart), 16 GB, venv-ci CPython 3.14.7 (numpy 2.5.4, scipy 1.18.1), alone on the box. Every wall figure is provisional: true; counts and verdicts are final.

## Tally

- D3-u1c slice: 309 keys, 0 unparseable, 309 driven by the fast net (fast closure scripts + env_drift --all HEAD^1): 64 killed, 245 survived, 0 timeout, 0 with every driver skipped by reach; first kills typing_ruler.py 26, env_drift.py 11, plan_view.py 7, solar_alignment.py 6, manual_plan.py 6, structure.py 4, finite_boundary.py 2, doc_claims.py 1, block_duty.py 1; driver skips by the gate's reach rule 1600, by the relaxed rule 152.
- D3-u1c full net (prescreen.py complete, every deferred/relaxed-skipped closure driver, no relaxation, no early stop) on 245 of 245 slice survivors: 54 killed, 190 survived, 1 timeout; kills per driver (every kill) features.py 49, entities.py 6, harness_headers.py 3; sole killer features.py 46, entities.py 5.
- Provisional (judge re-takes): fast-net wall per mutant median 201 s, full-net wall per survivor median 1525 s, 4 workers, box D3-u1c: Linux x86_64, nproc 4, Intel(R) Xeon(R) Processor @ 2.10GHz (re-fire host; 2.30GHz before the restart), 16 GB, venv-ci CPython 3.14.7 (numpy 2.5.4, scipy 1.18.1), alone on the box, load1 1-5.

## Coverage

- D3.M1: universe 1260, examined 1260, not reached 0 line(s). Enumerator: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/enumerate.py --unpinned`
- D3.M2: universe 1260, examined 340, not reached 10 line(s). Enumerator: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/enumerate.py --unpinned`
- D3.M3: universe 280, examined 247, not reached 33 line(s). Enumerator: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/tabulate.py --tsv | grep -P '\tSURVIVED\t'`
- D3.M4: universe 280, examined 280, not reached 0 line(s). Enumerator: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/tabulate.py --tsv | grep -P '\tSURVIVED\t'`
- D3.M5: universe 27, examined 23, not reached 4 line(s). Enumerator: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/enumerate.py --scripts`

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
| custom_components/heatpump_optimizer/optimizer.py:4272 CLAMP_DROP 86078a63 | `rain_intensity = min(avg_future_precip / 2.0, 1.0)  ->  rain_intensity = (avg_future_preci` | block_duty.py, env_drift.py, features.py, validate.py |
| custom_components/heatpump_optimizer/thermal_model.py:4751 CLAMP_DROP 5f84740b#2 | `) / max(dt, 1e-6)  ->  ) / (dt)` | env_drift.py, features.py, validate.py |
| custom_components/heatpump_optimizer/thermal_model.py:2946 CLAMP_DROP 351c0e21 | `span = np.maximum(flow_set - floor_temp, 1e-6)  ->  span = (flow_set - floor_temp)` | env_drift.py, features.py |
| custom_components/heatpump_optimizer/tariff.py:801 CMP_BOUND ba43bf7e | `positive = np.flatnonzero(np.any(values > 0, axis=1))  ->  positive = np.flatnonzero(np.an` | env_drift.py, features.py |
| custom_components/heatpump_optimizer/coordinator.py:9390 GUARD_OFF 97281aaf | `if x <= 1e-6 or not np.isfinite(y):  ->  if False:` | features.py |
| custom_components/heatpump_optimizer/optimizer.py:6648 CMP_BOUND 83c9652a | `if result.dhw_power_schedule and i < len(result.dhw_power_schedule):  ->  if result.dhw_po` | config_flow_steps.py, entities.py, features.py |
| custom_components/heatpump_optimizer/coordinator.py:4497 GUARD_OFF ee9a2c4c | `if not vvc_entity and not space_entity:  ->  if False:` | config_flow_steps.py, entities.py, features.py |
| custom_components/heatpump_optimizer/optimizer.py:2782 GUARD_OFF 68bf32a9 | `if self.holiday_comfort_night is not None:  ->  if False:` | entities.py, features.py |
| custom_components/heatpump_optimizer/coordinator.py:10445 CMP_BOUND 8635e542 | `if kwh > 0 and len(costs) > 1:  ->  if kwh >= 0 and len(costs) > 1:` | config_flow_steps.py, entities.py, env_drift.py, features.py, finite_boundary.py, manual_plan.py |
| custom_components/heatpump_optimizer/thermal_model.py:4140 GUARD_OFF bf9c0638 | `if n_sub == 1:  ->  if False:` | block_duty.py, boost_drift_replay.py, config_flow_steps.py, doc_claims.py, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py,  |
| custom_components/heatpump_optimizer/optimizer.py:5222 CMP_BOUND 1a159a14 | `temp = room[i + 1] if i + 1 < len(room) else room[-1]  ->  temp = room[i + 1] if i + 1 <= ` | features.py, manual_plan.py, optimality.py |
| custom_components/heatpump_optimizer/thermal_model.py:2581 CLAMP_DROP 4cc7cd0a | `hp_draw = min(drawn - wood_draw, max(avail_hp, 0.0))  ->  hp_draw = min(drawn - wood_draw,` | env_drift.py, features.py |
| custom_components/heatpump_optimizer/sysid.py:677 CMP_BOUND f4619cef | `if not (c_r > 1e-9 and c_s > 1e-9 and k_s > 1e-9) or not settle_band > 1e-9:  ->  if not (` | features.py |
| custom_components/heatpump_optimizer/tariff.py:806 CLAMP_DROP e202a9d1 | `scale = np.maximum(tau * peak, 1e-9)  ->  scale = (tau * peak)` | env_drift.py, features.py |
| custom_components/heatpump_optimizer/sysid.py:852 CMP_BOUND 5bc864cc | `if not accepted or float(np.max(np.abs(delta))) < 1e-10:  ->  if not accepted or float(np.` | entities.py, features.py |
| custom_components/heatpump_optimizer/optimizer.py:4610 CMP_BOUND d9b2b8a5 | `and candidate.objective_value < fixed_objective - 1e-9  ->  and candidate.objective_value ` | env_drift.py, features.py |
| custom_components/heatpump_optimizer/optimizer.py:1948 GUARD_OFF 510621f6 | `if not scored:  ->  if False:` | block_duty.py, boost_drift_replay.py, config_flow_steps.py, doc_claims.py, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py,  |
| custom_components/heatpump_optimizer/coordinator.py:8842 GUARD_OFF 688eecbd | `if params.two_zone_enabled:  ->  if False:` | features.py |
| custom_components/heatpump_optimizer/dhw_planner.py:556 GUARD_OFF d2584b72 | `if hour == prev + 1:  ->  if False:` | env_drift.py, features.py |
| custom_components/heatpump_optimizer/optimizer.py:5120 GUARD_OFF b467baf0 | `if refused is None:  ->  if False:` | env_drift.py, features.py, validate.py |
| custom_components/heatpump_optimizer/coordinator.py:9365 CMP_BOUND a84c93c2 | `if cap_i < p_max - 1e-9:  ->  if cap_i <= p_max - 1e-9:` | entities.py, features.py |
| custom_components/heatpump_optimizer/coordinator.py:9038 CMP_BOUND 8274eedf | `and utc_elapsed_seconds(self._outage_recovery_until, now) > 0  ->  and utc_elapsed_seconds` | features.py |
| custom_components/heatpump_optimizer/tariff.py:904 GUARD_OFF eb0a46c5 | `if house.size == 0:  ->  if False:` | env_drift.py, features.py |
| custom_components/heatpump_optimizer/coordinator.py:5674 CMP_BOUND 8256b8db | `if observed < low or observed > high:  ->  if observed < low or observed >= high:` | features.py |
| custom_components/heatpump_optimizer/optimizer.py:3328 CLAMP_DROP 1a5e5be6 | `deficit / max(cop_end, 1e-6)  ->  deficit / (cop_end)` | features.py |
| custom_components/heatpump_optimizer/coordinator.py:11271 BOOLOP 67eac7b8 | `if "power_cap_kw" in overrides and simulated.predictive_info  ->  if "power_cap_kw" in ove` | config_flow_steps.py, features.py |
| custom_components/heatpump_optimizer/sysid.py:1782 CLAMP_DROP 81525776 | `self.samples[-1].power_kw = max(plan_power_kw, 0.0) * thermal_cop  ->  self.samples[-1].po` | entities.py, features.py |
| custom_components/heatpump_optimizer/thermal_model.py:3479 CMP_BOUND 5eed5b5e | `if precipitation > 0.1:  # threshold for "raining"  ->  if precipitation >= 0.1:  # thresh` | block_duty.py, boost_drift_replay.py, config_flow_steps.py, doc_claims.py, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py,  |
| custom_components/heatpump_optimizer/optimizer.py:4828 CMP_BOUND 934404a3 | `if extra.size < n_steps:  ->  if extra.size <= n_steps:` | env_drift.py, features.py |
| custom_components/heatpump_optimizer/optimizer.py:2086 CLAMP_DROP f3416292 | `return 1.0 - 0.8 * ranks / float(max(len(prices) - 1, 1))  ->  return 1.0 - 0.8 * ranks / ` | features.py |
| custom_components/heatpump_optimizer/optimizer.py:5701 CLAMP_DROP cb686f74 | `n = min(len(power), len(self._pv_surplus))  ->  n = (len(power))` | env_drift.py, features.py |
| custom_components/heatpump_optimizer/optimizer.py:3402 CMP_BOUND 055feb1c | `if end <= i:  ->  if end < i:` | block_duty.py, boost_drift_replay.py, config_flow_steps.py, doc_claims.py, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py,  |
| custom_components/heatpump_optimizer/tariff.py:824 CMP_BOUND b17b660c | `close = np.abs(count - k) < 1e-6  ->  close = np.abs(count - k) <= 1e-6` | env_drift.py, features.py |
| custom_components/heatpump_optimizer/thermal_model.py:2598 CMP_BOUND 549bb130 | `elif available <= 0.0:  ->  elif available < 0.0:` | entities.py, env_drift.py, features.py, validate.py |
| custom_components/heatpump_optimizer/dhw_planner.py:1342 CMP_BOUND d209e002 | `covered = free_temps[1:] >= requirement - 0.5  ->  covered = free_temps[1:] > requirement ` | env_drift.py, features.py |
| custom_components/heatpump_optimizer/sysid.py:875 CMP_BOUND 9cd2a896 | `if len(dts) < 5:  ->  if len(dts) <= 5:` | entities.py, features.py |
| custom_components/heatpump_optimizer/dhw_planner.py:784 CMP_BOUND fe16bdce | `if need > boost_top:  ->  if need >= boost_top:` | env_drift.py, features.py, guard_pins.py, manual_plan.py |
| custom_components/heatpump_optimizer/dhw_planner.py:2140 CMP_BOUND 655157d4 | `if not bool(np.all(candidate[pos + 1: end + 1] <= limit + 1e-9)):  ->  if not bool(np.all(` | block_duty.py, doc_claims.py, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py, validate.py |
| custom_components/heatpump_optimizer/sysid.py:1715 CMP_BOUND 628390f0 | `if hw <= UA_ADOPTION_HALFWIDTH_BAR:  ->  if hw < UA_ADOPTION_HALFWIDTH_BAR:` | entities.py, features.py |
| custom_components/heatpump_optimizer/coordinator.py:4851 BOOLOP 4d085ae8 | `result.upper_temp_trajectory and result.lower_temp_trajectory  ->  result.upper_temp_traje` | config_flow_steps.py, doc_claims.py, entities.py, features.py, plan_view.py |
| custom_components/heatpump_optimizer/thermal_model.py:404 GUARD_OFF 0486e863 | `if cached is not None and cached[0] == key:  ->  if False:` | block_duty.py, boost_drift_replay.py, config_flow_steps.py, doc_claims.py, entities.py, env_drift.py, features.py, finite_boundary.py, guard_pins.py, manual_pla |
| custom_components/heatpump_optimizer/coordinator.py:6454 GUARD_OFF e2921a12 | `if self._solve_failures >= SOLVE_FAILURE_ISSUE_COUNT:  ->  if False:` | config_flow_steps.py, entities.py, features.py |
| custom_components/heatpump_optimizer/price_model.py:141 CMP_BOUND de1a0615 | `if low > 0.0 and high <= low * (hi / lo) * (1.0 + 1e-9):  ->  if low >= 0.0 and high <= lo` | boost_drift_replay.py, features.py, finite_boundary.py |
| custom_components/heatpump_optimizer/thermal_model.py:4668 CLAMP_DROP b186b210 | `np.maximum(T_wood, T_buf)  ->  (T_wood)` | env_drift.py, features.py |
| custom_components/heatpump_optimizer/grid_fee.py:355 CMP_BOUND 4a974762 | `if abs(rule.rate) > worst:  ->  if abs(rule.rate) >= worst:` | env_drift.py, features.py |
| custom_components/heatpump_optimizer/thermal_model.py:4679 CLAMP_DROP 2d9d455e | `floor_temp = np.minimum(T_upper, T_slab)  ->  floor_temp = (T_upper)` | env_drift.py, features.py, validate.py |
| custom_components/heatpump_optimizer/optimizer.py:4033 CMP_BOUND 6e5e1a9f | `if surplus is None or not np.any(surplus[: len(prices)] > 1e-6):  ->  if surplus is None o` | block_duty.py, boost_drift_replay.py, config_flow_steps.py, doc_claims.py, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py,  |
| custom_components/heatpump_optimizer/optimizer.py:6606 GUARD_OFF c9af7d41 | `elif p_norm < 0.9:  ->  elif False:` | config_flow_steps.py, entities.py, features.py |
| custom_components/heatpump_optimizer/sysid.py:2237 CMP_BOUND 9b28838f | `and abs(drift_c_per_h) < self.config.sensor_drift_prior_c_per_h  ->  and abs(drift_c_per_h` | features.py |
| custom_components/heatpump_optimizer/price_model.py:342 CMP_BOUND cb6981eb | `if self.days[idx] < SHAPE_CONFIDENCE_DAYS:  ->  if self.days[idx] <= SHAPE_CONFIDENCE_DAYS` | features.py |
| custom_components/heatpump_optimizer/optimizer.py:5945 CLAMP_DROP 8d062eb9 | `float(max(dhw_floor_temps[0], dhw_ready_temps[0]))  ->  float((dhw_floor_temps[0]))` | block_duty.py, doc_claims.py, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py, validate.py |
| custom_components/heatpump_optimizer/sysid.py:643 CMP_BOUND 72abb7dd | `if not (c_r > 1e-9 and c_s > 1e-9 and k_s > 1e-9):  ->  if not (c_r > 1e-9 and c_s > 1e-9 ` | entities.py, features.py |
| custom_components/heatpump_optimizer/thermal_model.py:3328 CLAMP_DROP 2723239c | `cop = self.params.cop_nominal * min(factor, 1.5) * self.params.cop_scale  ->  cop = self.p` | block_duty.py, boost_drift_replay.py, config_flow_steps.py, doc_claims.py, entities.py, env_drift.py, features.py, finite_boundary.py, guard_pins.py, manual_pla |
| custom_components/heatpump_optimizer/coordinator.py:6379 CMP_BOUND a306f8ef | `if len(prices) < 4:  ->  if len(prices) <= 4:` | config_flow_steps.py, entities.py, features.py |
| custom_components/heatpump_optimizer/coordinator.py:9153 GUARD_OFF 789d92ca | `if damp <= 1e-9:  ->  if False:` | config_flow_steps.py, features.py |
| custom_components/heatpump_optimizer/optimizer.py:2126 CMP_BOUND fc7a9935 | `if energy_kwh <= 0 or p_max <= 0 or dt <= 0:  ->  if energy_kwh <= 0 or p_max < 0 or dt <=` | block_duty.py, boost_drift_replay.py, config_flow_steps.py, doc_claims.py, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py,  |
| custom_components/heatpump_optimizer/sysid.py:2037 CLAMP_DROP 79ab3a2f | `x1_spread2 = float(np.var(a[:, 0])) * n_rows / max(n_rows - 1.0, 1.0)  ->  x1_spread2 = fl` | features.py |
| custom_components/heatpump_optimizer/optimizer.py:6070 GUARD_OFF 384d6fb8 | `if hi <= lo:  ->  if False:` | env_drift.py, features.py, validate.py |
| custom_components/heatpump_optimizer/coordinator.py:7118 GUARD_OFF 643e387c | `if not self._weather_outage_cycles:  ->  if False:` | config_flow_steps.py, entities.py, features.py, manual_plan.py |
| custom_components/heatpump_optimizer/sysid.py:1942 CMP_BOUND 3e0642e4 | `if len(rows) < 5:  ->  if len(rows) <= 5:` | features.py |
| custom_components/heatpump_optimizer/coordinator.py:9051 CMP_BOUND 936e7a6e | `if self._outage_dhw_until is None or utc_elapsed_seconds(self._outage_dhw_until, now) <= 0` | config_flow_steps.py, entities.py, features.py |
| custom_components/heatpump_optimizer/optimizer.py:4720 CMP_BOUND 164830ff | `if np.any(risk > 0.0):  ->  if np.any(risk >= 0.0):` | env_drift.py, features.py |
| custom_components/heatpump_optimizer/sysid.py:892 GUARD_OFF ebe7af8b | `if not (-0.5 <= gains_kw <= 2.0):  ->  if False:` | entities.py, features.py |
| custom_components/heatpump_optimizer/coordinator.py:10331 GUARD_OFF 8a2d264d | `if energy <= 0:  ->  if False:` | boost_drift_replay.py, entities.py, features.py |
| custom_components/heatpump_optimizer/coordinator.py:8265 GUARD_OFF 9e714704 | `if manual_state is not None:  ->  if False:` | config_flow_steps.py, entities.py, env_drift.py, features.py, finite_boundary.py, manual_plan.py |
| custom_components/heatpump_optimizer/optimizer.py:5054 GUARD_OFF d4fe0ab5 | `if p85 <= p25 * 1.05:  ->  if False:` | env_drift.py, features.py |
| custom_components/heatpump_optimizer/sysid.py:1545 CMP_BOUND 442ad6d1 | `if cfg.start_hour <= cfg.end_hour:  ->  if cfg.start_hour < cfg.end_hour:` | features.py |
| custom_components/heatpump_optimizer/coordinator.py:4538 GUARD_OFF 8817ad76 | `if params.two_zone_enabled:  ->  if False:` | config_flow_steps.py, features.py |
| custom_components/heatpump_optimizer/sysid.py:1708 CMP_BOUND 9330e956 | `or self._baseline_temp is None or not 1e-3 < dt <= 2.0  ->  or self._baseline_temp is None` | entities.py, features.py |
| custom_components/heatpump_optimizer/sysid.py:2375 CLAMP_DROP 6ca2df8a | `np.log(max(ua0, 1e-3)),  ->  np.log((ua0)),` | entities.py, features.py |
| custom_components/heatpump_optimizer/optimizer.py:4234 CLAMP_DROP 85664bbe | `n_6h = min(int(6 / dt_hours), n)  ->  n_6h = (int(6 / dt_hours))` | block_duty.py, boost_drift_replay.py, config_flow_steps.py, doc_claims.py, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py,  |
| custom_components/heatpump_optimizer/dhw_planner.py:2075 CMP_BOUND 0d9190a8 | `if bool(np.all(joint_temps <= joint_limit + 1e-9)):  ->  if bool(np.all(joint_temps < join` | block_duty.py, doc_claims.py, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py, validate.py |
| custom_components/heatpump_optimizer/optimizer.py:5225 CMP_BOUND 60d71c27 | `if i < len(temp_min_bounds)  ->  if i <= len(temp_min_bounds)` | features.py, manual_plan.py, optimality.py |
| custom_components/heatpump_optimizer/sysid.py:1593 CMP_BOUND 3896349a | `return peak <= bound and final <= bound  ->  return peak < bound and final <= bound` | entities.py, features.py |
| custom_components/heatpump_optimizer/defrost.py:795 GUARD_OFF 2e316dc7 | `if self._opened is None:  ->  if False:` | boost_drift_replay.py, config_flow_steps.py, entities.py, features.py |
| custom_components/heatpump_optimizer/coordinator.py:2360 GUARD_OFF 6fee1acd | `if result is not None:  ->  if False:` | config_flow_steps.py, entities.py, features.py |
| custom_components/heatpump_optimizer/thermal_model.py:835 GUARD_OFF 855229b8 | `if swing <= 0.0:  ->  if False:` | block_duty.py, boost_drift_replay.py, config_flow_steps.py, entities.py, features.py, finite_boundary.py, manual_plan.py, solar_alignment.py |
| custom_components/heatpump_optimizer/sysid.py:643 CMP_BOUND 72abb7dd | `if not (c_r > 1e-9 and c_s > 1e-9 and k_s > 1e-9):  ->  if not (c_r > 1e-9 and c_s >= 1e-9` | entities.py, features.py |
| custom_components/heatpump_optimizer/dhw_planner.py:1538 CLAMP_DROP f0477740 | `lo = max(0, j - window)  ->  lo = (0)` | block_duty.py, doc_claims.py, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py, validate.py |
| custom_components/heatpump_optimizer/price_model.py:72 CONST 90ecade5 | `SHAPE_MIN = 0.2  ->  SHAPE_MIN = 0.4` | block_duty.py, boost_drift_replay.py, config_flow_steps.py, debug_collect.py, doc_claims.py, entities.py, env_drift.py, features.py, finite_boundary.py, guard_p |
| custom_components/heatpump_optimizer/optimizer.py:6604 GUARD_OFF f6fcebcb | `elif p_norm < 0.7:  ->  elif False:` | config_flow_steps.py, entities.py, features.py |
| custom_components/heatpump_optimizer/dhw_planner.py:1018 CLAMP_DROP 152250ba | `window_hours = max((end_idx - start_idx) * dt, dt)  ->  window_hours = ((end_idx - start_i` | block_duty.py, doc_claims.py, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py, validate.py |
| custom_components/heatpump_optimizer/optimizer.py:3969 CMP_BOUND 674746fd | `pinned = (dhw_power > 1e-6) & (space_power >= headroom - 1e-3)  ->  pinned = (dhw_power >=` | block_duty.py, doc_claims.py, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py, validate.py |
| custom_components/heatpump_optimizer/dhw_planner.py:1527 CLAMP_DROP 0a81eaf0 | `demand = np.clip(np.asarray(space_demand, dtype=float), 0.0, None)  ->  demand = (np.asarr` | block_duty.py, doc_claims.py, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py, validate.py |
| custom_components/heatpump_optimizer/coordinator.py:2539 CMP_BOUND 78b040fc | `if now_s < starts[0]:  ->  if now_s <= starts[0]:` | entities.py, features.py |
| custom_components/heatpump_optimizer/dhw_planner.py:1184 GUARD_OFF f02474b2 | `if dhw_pins is not None:  ->  if False:` | block_duty.py, doc_claims.py, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py, validate.py |
| custom_components/heatpump_optimizer/thermal_model.py:3073 CMP_BOUND e46c5e3e | `if base_u <= 1e-6 or capacity <= 1e-6:  ->  if base_u <= 1e-6 or capacity < 1e-6:` | boost_drift_replay.py, entities.py, features.py |
| custom_components/heatpump_optimizer/coordinator.py:8785 CMP_BOUND ff55e496 | `if 0.0 < spacing <= 0.25:  ->  if 0.0 < spacing < 0.25:` | features.py |
| custom_components/heatpump_optimizer/optimizer.py:6602 CMP_BOUND b8bcfb6f | `elif p_norm < 0.4:  ->  elif p_norm <= 0.4:` | config_flow_steps.py, entities.py, features.py |
| custom_components/heatpump_optimizer/thermal_model.py:677 CLAMP_DROP 581f45bc | `rate = min(max(float(rate), low), high)  ->  rate = min((float(rate)), high)` | config_flow_steps.py, entities.py, env_drift.py, features.py, optimality.py, validate.py |
| custom_components/heatpump_optimizer/thermal_model.py:2587 GUARD_OFF 4f3bbbac | `elif delivered <= 0.0:  ->  elif False:` | env_drift.py, features.py |
| custom_components/heatpump_optimizer/coordinator.py:5654 CMP_BOUND dcf818be | `if dt_h < BUFFER_COOLING_MIN_SAMPLE_HOURS:  ->  if dt_h <= BUFFER_COOLING_MIN_SAMPLE_HOURS` | features.py |
| custom_components/heatpump_optimizer/sysid.py:1778 CLAMP_DROP 07b8a4e6 | `thermal_cop = max(cop, 0.1)  ->  thermal_cop = (cop)` | entities.py, features.py |
| custom_components/heatpump_optimizer/sysid.py:1922 GUARD_OFF d2773033 | `if dt_h <= 1e-3 or dt_h > 2.0:  ->  if False:` | features.py |
| custom_components/heatpump_optimizer/price_model.py:510 CMP_BOUND b4032e2b | `if known_count >= n_steps:  ->  if known_count > n_steps:` | config_flow_steps.py, entities.py, env_drift.py, features.py, solar_alignment.py |
| custom_components/heatpump_optimizer/sysid.py:1073 CMP_BOUND 501fd0e7 | `if solution.shape[0] >= 4:  ->  if solution.shape[0] > 4:` | features.py |
| custom_components/heatpump_optimizer/price_model.py:825 BOOLOP 44f0178f | `isinstance(attrs, dict) and attrs  ->  isinstance(attrs, dict) or attrs` | features.py |
| custom_components/heatpump_optimizer/optimizer.py:1994 CMP_BOUND f33dcd5d | `if np.isfinite(score) and score < best_score:  ->  if np.isfinite(score) and score <= best` | block_duty.py, boost_drift_replay.py, config_flow_steps.py, doc_claims.py, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py,  |
| custom_components/heatpump_optimizer/coordinator.py:5382 GUARD_OFF 6deb0603 | `if modelled_cop <= 0.1:  ->  if False:` | boost_drift_replay.py, features.py |
| custom_components/heatpump_optimizer/price_model.py:207 CMP_BOUND c00e502c | `if mean <= 1e-6:  ->  if mean < 1e-6:` | config_flow_steps.py, entities.py, features.py, finite_boundary.py, guard_pins.py, manual_plan.py |
| custom_components/heatpump_optimizer/price_model.py:90 CONST f47f8e99 | `VAR_ALPHA = 0.15  ->  VAR_ALPHA = 0.3` | block_duty.py, boost_drift_replay.py, config_flow_steps.py, debug_collect.py, doc_claims.py, entities.py, env_drift.py, features.py, finite_boundary.py, guard_p |
| custom_components/heatpump_optimizer/optimizer.py:3177 GUARD_OFF ddd90b1f | `if span <= 0.0:  ->  if False:` | env_drift.py, features.py, validate.py |
| custom_components/heatpump_optimizer/grid_fee.py:360 CMP_BOUND 23a3a01d | `and abs(float(entity_value)) > worst  ->  and abs(float(entity_value)) >= worst` | features.py |
| custom_components/heatpump_optimizer/sysid.py:1545 GUARD_OFF 442ad6d1 | `if cfg.start_hour <= cfg.end_hour:  ->  if False:` | features.py |
| custom_components/heatpump_optimizer/coordinator.py:5049 GUARD_OFF 1dc80a7a | `if self._pump_signals.mode_observed and not self._pump_signals.space_heat:  ->  if False:` | boost_drift_replay.py, entities.py, features.py |
| custom_components/heatpump_optimizer/coordinator.py:9153 CMP_BOUND 789d92ca | `if damp <= 1e-9:  ->  if damp < 1e-9:` | config_flow_steps.py, features.py |
| custom_components/heatpump_optimizer/coordinator.py:10564 CMP_BOUND 842b328c | `if mean_spot <= 0.01:  ->  if mean_spot < 0.01:` | features.py |
| custom_components/heatpump_optimizer/dhw_planner.py:1606 RETURN_DEL 90660fdb | `return best  ->  pass` | none of the closure executes the line: a direct check on DhwPlanner._plan_dhw_min_cost |
| custom_components/heatpump_optimizer/coordinator.py:7549 CLAMP_DROP 7b17a55a | `self._snow_accum_cm += rate_now * min(dt_true, 6.0)  ->  self._snow_accum_cm += rate_now *` | features.py |
| custom_components/heatpump_optimizer/sysid.py:1942 GUARD_OFF 3e0642e4 | `if len(rows) < 5:  ->  if False:` | features.py |
| custom_components/heatpump_optimizer/optimizer.py:2494 GUARD_OFF 69bbbda7 | `if _pin_is_free(pin) or pin < 0.5:  ->  if False:` | block_duty.py, features.py, manual_plan.py, optimality.py |
| custom_components/heatpump_optimizer/sysid.py:2038 CMP_BOUND f030484a | `if sigma2 > 0.0 and sigma2 > x1_spread2 / 9.0:  ->  if sigma2 >= 0.0 and sigma2 > x1_sprea` | features.py |
| custom_components/heatpump_optimizer/price_model.py:337 GUARD_OFF 4711f894 | `if not day_types or not np.isfinite(level) or level <= 0.0:  ->  if False:` | features.py |
| custom_components/heatpump_optimizer/thermal_model.py:698 GUARD_OFF 0486e863 | `if cached is not None and cached[0] == key:  ->  if False:` | env_drift.py, features.py |
| custom_components/heatpump_optimizer/coordinator.py:10231 CMP_BOUND 8a040c32 | `if 0 < idx < len(trajectory):  ->  if 0 <= idx < len(trajectory):` | config_flow_steps.py, entities.py, features.py |
| custom_components/heatpump_optimizer/sysid.py:846 CMP_BOUND 32465940 | `if np.isfinite(next_cost) and next_cost < cost:  ->  if np.isfinite(next_cost) and next_co` | entities.py, features.py |
| custom_components/heatpump_optimizer/price_model.py:303 GUARD_OFF 2c4b19d6 | `if trust <= 0.0:  ->  if False:` | entities.py, features.py |
| custom_components/heatpump_optimizer/thermal_model.py:3387 CLAMP_DROP 9e45afd9 | `carnot_flow = (flow_temp + 273.15) / max(flow_temp + 273.15 - t_out, 1.0)  ->  carnot_flow` | block_duty.py, config_flow_steps.py, doc_claims.py, entities.py, env_drift.py, features.py, finite_boundary.py, guard_pins.py, manual_plan.py, optimality.py, pl |
| custom_components/heatpump_optimizer/coordinator.py:5674 CMP_BOUND 8256b8db | `if observed < low or observed > high:  ->  if observed <= low or observed > high:` | features.py |
| custom_components/heatpump_optimizer/optimizer.py:5145 CMP_BOUND d629fd84 | `int(np.count_nonzero(refused > 1e-9)),  ->  int(np.count_nonzero(refused >= 1e-9)),` | features.py |
| custom_components/heatpump_optimizer/optimizer.py:5250 CMP_BOUND 2f71906b | `if temp >= float(req[i]) - 0.5:  ->  if temp > float(req[i]) - 0.5:` | block_duty.py, features.py, manual_plan.py |
| custom_components/heatpump_optimizer/coordinator.py:5157 GUARD_OFF d011a381 | `if probe.stale:  ->  if False:` | block_duty.py, boost_drift_replay.py, config_flow_steps.py, entities.py, features.py, finite_boundary.py, manual_plan.py, solar_alignment.py |
| custom_components/heatpump_optimizer/optimizer.py:6093 CMP_BOUND cf0ef9fc | `if net(lo) <= 0.0:  ->  if net(lo) < 0.0:` | features.py |
| custom_components/heatpump_optimizer/optimizer.py:5016 CLAMP_DROP c634563f | `take = min(n_steps, src.size)  ->  take = (n_steps)` | block_duty.py, features.py, manual_plan.py, optimality.py |
| custom_components/heatpump_optimizer/optimizer.py:4211 GUARD_OFF 2641a2a6 | `if n == 0:  ->  if False:` | block_duty.py, boost_drift_replay.py, config_flow_steps.py, doc_claims.py, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py,  |
| custom_components/heatpump_optimizer/thermal_model.py:3073 CMP_BOUND e46c5e3e | `if base_u <= 1e-6 or capacity <= 1e-6:  ->  if base_u < 1e-6 or capacity <= 1e-6:` | boost_drift_replay.py, entities.py, features.py |
| custom_components/heatpump_optimizer/thermal_model.py:2573 CLAMP_DROP 11808d14 | `) / max(dt_hours, 1e-6)  ->  ) / (dt_hours)` | env_drift.py, features.py |
| custom_components/heatpump_optimizer/optimizer.py:6097 CMP_BOUND c05d6fd2 | `if net(mid) > 0.0:  ->  if net(mid) >= 0.0:` | features.py |
| custom_components/heatpump_optimizer/sysid.py:643 CMP_BOUND 72abb7dd | `if not (c_r > 1e-9 and c_s > 1e-9 and k_s > 1e-9):  ->  if not (c_r >= 1e-9 and c_s > 1e-9` | entities.py, features.py |
| custom_components/heatpump_optimizer/thermal_model.py:2583 CMP_BOUND 01f70545 | `if drawn > delivered > 0.0:  ->  if drawn >= delivered > 0.0:` | env_drift.py, features.py |
| custom_components/heatpump_optimizer/coordinator.py:5083 CLAMP_DROP 61545c3f | `max_sample_hours=max(1.0, 1.5 * interval_hours),  ->  max_sample_hours=(1.0),` | block_duty.py, boost_drift_replay.py, config_flow_steps.py, doc_claims.py, entities.py, env_drift.py, features.py, finite_boundary.py, manual_plan.py, solar_ali |
| custom_components/heatpump_optimizer/defrost.py:181 CMP_BOUND 7b9d8278 | `if value <= centers[0]:  ->  if value < centers[0]:` | block_duty.py, boost_drift_replay.py, config_flow_steps.py, entities.py, env_drift.py, features.py, finite_boundary.py, manual_plan.py, solar_alignment.py |
| custom_components/heatpump_optimizer/coordinator.py:6360 RETURN_DEL 440ee7e3 | `return None  ->  pass` | features.py |

## Findings

None from this box: per D3.md step 3 the slice's survivors are candidates; only the quiet-window full gate (box D3-top6) makes findings.

## Non-findings

- Null control: the fast net LIVES on the unmutated tree (re-taken on box D3-u1c after re-taking all 21 traced baselines, all rc=0 failed=0): `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/prescreen.py null` -> null_verdict=LIVES over 16 fast drivers (state/null-D3-u1c.json, state/u1c-null.out)
- Positive control: the pre-screen kills ledger-pinned sites on this box: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/prescreen.py run --anchors dev/audit/rounds/round11/D3/s1/posctl_anchors.txt --sub posctl-D3-u1c` -> 2/2 KILLED by tests/manual_plan.py (state/u1c-posctl.out)
- 64 of 309 D3-u1c slice mutants are pinned by the fast net: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/u1c_slice.py` -> D3-u1c slice: 309 keys, 0 unparseable, 309 driven by the fast net (fast closure scripts + env_drift --all HEAD^1): 64 killed, 245 survived, 0 timeout, 0 with every driver skipped by reach; first kills typing_ruler.py 26, env_drift.py 11, plan_view.py 7, solar_alignment.py 6, manual_plan.py 6, structure.py 4, finite_boundary.py 2, doc_claims.py 1, block_duty.py 1; driver skips by the gate's reach rule 1600, by the relaxed rule 152.
- 54 of 245 fast-net survivors of the slice are pinned by the full closure net: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/u1c_slice.py` -> D3-u1c full net (prescreen.py complete, every deferred/relaxed-skipped closure driver, no relaxation, no early stop) on 245 of 245 slice survivors: 54 killed, 190 survived, 1 timeout; kills per driver (every kill) features.py 49, entities.py 6, harness_headers.py 3; sole killer features.py 46, entities.py 5. Killed sites: defrost.py:106 by features.py; coordinator.py:4893 by features.py; coordinator.py:3168 by features.py; coordinator.py:3102 by features.py; defrost.py:729 by features.py; coordinator.py:539 by features.py; coordinator.py:6537 by features.py; grid_fee.py:355 by features.py; sysid.py:1779 by harness_headers.py,entities.py,features.py; coordinator.py:7494 by entities.py; grid_fee.py:331 by features.py; coordinator.py:9360 by entities.py; grid_fee.py:383 by features.py; optimizer.py:5271 by features.py; defrost.py:540 by features.py; sysid.py:2038 by features.py; coordinator.py:9022 by features.py; coordinator.py:8978 by features.py; sysid.py:1759 by features.py; sysid.py:2208 by features.py; defrost.py:744 by features.py; coordinator.py:9023 by features.py; grid_fee.py:306 by features.py; optimizer.py:4604 by features.py; coordinator.py:10561 by features.py; coordinator.py:9107 by features.py; sysid.py:2038 by features.py; coordinator.py:6790 by features.py; defrost.py:808 by features.py; thermal_model.py:3651 by features.py; defrost.py:802 by features.py; coordinator.py:1643 by features.py; sysid.py:1083 by entities.py; grid_fee.py:310 by features.py; coordinator.py:2962 by features.py; coordinator.py:4168 by features.py; coordinator.py:3560 by features.py; coordinator.py:10445 by features.py; optimizer.py:6648 by features.py; coordinator.py:1915 by features.py; optimizer.py:6573 by features.py; optimizer.py:2780 by entities.py; coordinator.py:5969 by features.py; tariff.py:768 by features.py; coordinator.py:6892 by features.py; coordinator.py:6091 by features.py; optimizer.py:6602 by features.py; dhw_planner.py:882 by features.py; defrost.py:683 by features.py; optimizer.py:4828 by features.py; sysid.py:1798 by harness_headers.py,features.py; coordinator.py:10984 by features.py; tariff.py:1109 by entities.py; sysid.py:1549 by harness_headers.py,features.py
- custom_components/heatpump_optimizer/coordinator.py:6360 RETURN_DEL 440ee7e3 (return None -> pass) is not a survivor: the full net hangs on it: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/prescreen.py complete --src pre --keys <key 9efe002b48e1827d>` -> TIMEOUT: tests/features.py rc=124 after 2030 s (provisional wall); a CI job timeout fails the gate, so the site is detected, not pinned by an assertion

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
