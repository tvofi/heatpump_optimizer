# D2 verify-2 -- round 11, box V5 (seat D2-v2)

Every finding of this unit carries the planted-export scope D2-s3: every number was taken in a private copy of the planted export (`../audit-r11-px-D2-2`, PYTHONPATH=tests/hastub). load1 0.6-2.4 on 4 cpu, thread_factor 1.000; all metrics are counts or seeded values, load-immune. Finder re-runs `$HOME/vout/D2-v2/v1/`, verifier harness `$HOME/vout/D2-v2/harness/v2_d2b.py` (it reuses the D17-v1 rig `$HOME/vout/D17-v1/harness/myrig.py`).

## D2-s3-01 -- weaken (medium)

- metric: published savings inflation (currency) from the risk premium booked into predicted/baseline cost on the price_risk golden
- method: V1 m3_risk.py base/--perturb-raw; V2 v2_d2b.py: own coordinator, a 10-hour raw feed (tail guessed), lambda 0 vs 1, published step prices and predicted/baseline cost compared; tree: planted export copy ../audit-r11-px-D2-2 (PYTHONPATH=tests/hastub; m4_tariff with HASTUB_TZ=Europe/Stockholm)
- V1 reproduced: savings inflation 12.4574 at lambda 1, 25.0586 at 2.0; perturb 0
- V2 independent: 0.0000 on a fresh install with lambda 1 (no learned sigma): the premium and the booking error need a learned prior
- attacks: perturb 12.4574 -> 0.0 (max 25.0586 -> 0), reproduced exactly; null lambda 0: 0. My fresh-install arm: lambda 1 vs 0 move nothing (published prices max diff 0.0000, predicted_cost 40.5564 both) -- the premium needs a learned price sigma (optimizer.py:4717 `price_sigma is not None`), and lambda defaults to 0.0 (opt-in, config max 2.0). The defect is real where both hold; severity weakened for that reach
- V3 reach: yes, only with price_risk_lambda > 0 (opt-in) and a learned price sigma; class: new (confirmed; the risk-adjusted series feeds both the objective and the booked figures); seam_rule enumerates: partial: optimizer.py stash only; the published per-step prices leave through the coordinator payload

## D2-s3-02 -- verify (critical)

- metric: price units whose normalize_price_per_kwh result differs from the documented minor = 1/100 major
- method: V1 m4_tariff.py base/--perturb minor; V2 v2_d2b.py: normalize_price_per_kwh on 5 minor + 3 major units, and an own coordinator fed an entity in öre/kWh vs SEK/kWh; tree: planted export copy ../audit-r11-px-D2-2 (PYTHONPATH=tests/hastub; m4_tariff with HASTUB_TZ=Europe/Stockholm)
- V1 reproduced: unit_mismatches 8; perturb 0
- V2 independent: 5 of 5 minor units 100x; end to end published price 100.0 vs 1.0
- attacks: perturb 8 -> 0; null major units exact; mine 5 of 5 minor wrong (150 öre/kWh -> 150.0, 150000 öre/MWh -> 150.0), 0 of 3 major; reach: an öre/kWh entity at 100 publishes current_price 100.0 and first-step price 100.0 where SEK/kWh 1.0 publishes 1.0
- V3 reach: yes: any price entity in öre/c/p (Nord Pool price_in_cents) in real HA; class: new (corrected from P8: one surface, a missing /100); seam_rule enumerates: yes: PRICE_MINOR_UNITS has the one reader

## D2-s3-03 -- verify (high)

- metric: Tibber rows dropped from a today+tomorrow payload; known steps at 14:00
- method: V1 m4_tariff.py base/--perturb tomorrow; V2 v2_d2b.py: prices_from_tibber_payload on my own 96+96 payload; tree: planted export copy ../audit-r11-px-D2-2 (PYTHONPATH=tests/hastub; m4_tariff with HASTUB_TZ=Europe/Stockholm)
- V1 reproduced: rows dropped 96; known_steps_at_14h 40
- V2 independent: 192 in -> 96 out, 0 of 96 tomorrow rows
- attacks: perturb 96 -> 0, known steps 40 -> 96; null at 00:07 today covers the horizon; mine: 192 rows in, 96 out, 0 tomorrow rows
- V3 reach: yes: Tibber price source in real HA (afternoon solves); class: new (confirmed); seam_rule enumerates: yes: tibber loop and the entity path's raw_tomorrow

## D2-s3-04 -- verify (high)

- metric: quarter steps of one week whose applying grid-fee rules differ from the calendar weekday
- method: V1 m4_tariff.py base/--perturb weekday; V2 v2_d2b.py: FeeRule.applies vs my own weekday expectation on my own spec '= 0.05, Mon-Fri 07:00-21:00 = 0.30, Sat-Sun = 0.12'; tree: planted export copy ../audit-r11-px-D2-2 (PYTHONPATH=tests/hastub; m4_tariff with HASTUB_TZ=Europe/Stockholm)
- V1 reproduced: 192 of 672
- V2 independent: 192 of 672 on my spec (Fri 96, Sun 96)
- attacks: perturb 192 -> 0; null entity/none modes 0; mine 192 of 672 (Fri 96, Sun 96) with a different spec; parse_day_range('Mon-Fri') = {0..4} (weekday numbering) while applies tests isoweekday
- V3 reach: yes: grid_fee rules mode in real HA; class: I4 (corrected from new: two weekday numberings of one concept disagree); seam_rule enumerates: yes: isoweekday/weekday() sites in grid_fee, tariff and dhw_schedule

## D2-s3-05 -- verify (high)

- metric: billed_peak_kw understatement vs the per-day maximum on the capacity-tariff plan
- method: V1 m4_tariff.py base/--perturb oneperday; V2 v2_d2b.py: _one_per_day on a planted ranked list; tree: planted export copy ../audit-r11-px-D2-2 (PYTHONPATH=tests/hastub; m4_tariff with HASTUB_TZ=Europe/Stockholm)
- V1 reproduced: tracker_peak_err_max 2.1268 kW; perturb 0
- V2 independent: keeps per-day minima 1.0 and 0.5 where maxima are 4.0 and 3.0
- attacks: perturb 2.1268 -> 0.0000 kW; null capacity line 0 on 8 shapes; mine: _one_per_day([(4,d1),(1,d1),(3,d2),(0.5,d2),(2,'')]) keeps (1,d1),(0.5,d2),(2,'') -- each day's lowest; its docstring says highest
- V3 reach: yes: PeakTracker under distinct_days (default) in real HA, feeds billed_peak_kw and the peak guard threshold; class: new (confirmed); seam_rule enumerates: yes: _one_per_day and distinct_days sites

## D2-s3-06 -- verify (medium)

- metric: published peak_cost error vs the k largest window excesses on the capacity_tariff plan
- method: V1 m4_tariff.py base/--perturb topk; V2 v2_d2b.py: _exact_topk_sum on a planted excess vector; tree: planted export copy ../audit-r11-px-D2-2 (PYTHONPATH=tests/hastub; m4_tariff with HASTUB_TZ=Europe/Stockholm)
- V1 reproduced: peak_cost_err_max 41.4976; perturb 0.0004
- V2 independent: 0.30 vs 12.0 on a planted vector
- attacks: perturb 41.4976 -> 0.0004 (rounding); mine: excess [0.1,5,0.2,3,0,4], k 3 -> 0.30 (k smallest) vs 12.0 (k largest, its docstring)
- V3 reach: yes: OptimizationResult.peak_cost with peak_distinct_days off; class: P2 (corrected from new: scalar top-k sum and the batch twin take opposite arms); seam_rule enumerates: yes: np.sort sites in tariff.py

## D2-s3-07 -- verify (low)

- metric: coverage_factor for a month settled for every real hour
- method: V1 m4_tariff.py base/--perturb realhours; V2 v2_d2b.py: month_hours vs real elapsed hours in Europe/Stockholm, coverage_factor on a fully settled meta, Jan/Mar/Oct 2026; tree: planted export copy ../audit-r11-px-D2-2 (PYTHONPATH=tests/hastub; m4_tariff with HASTUB_TZ=Europe/Stockholm)
- V1 reproduced: coverage_full_23h 1.001346
- V2 independent: March 1.001346, October 1.000000 (floored), January 1.000000
- attacks: perturb 1.001346 -> 1.0; null January and 25-h 1.000000; mine: March 744 vs 743 real -> 1.001346; October 744 vs 745 real -> 1.000000 only because coverage_factor floors at max(1.0, ...): the 25-hour month is masked, not right
- V3 reach: yes: ledger estimates in real HA in DST months; class: P7 (confirmed); seam_rule enumerates: yes: month_hours/monthrange in ledger.py

## D2-s3-08 -- verify (medium)

- metric: kWh of hot-water draw booked from a charge-start dip with no draw, per combi construction
- method: V1 m5_tankfall.py base/--perturb-skip-heated; V2 v2_d2b.py: ChargeSettle.advance driven directly with a one-sample and a four-sample charge (4 K dip recovered while heated); tree: planted export copy ../audit-r11-px-D2-2 (PYTHONPATH=tests/hastub; m4_tariff with HASTUB_TZ=Europe/Stockholm)
- V1 reproduced: 3.0160 kWh (internal_coil 2.4592); short 0.0389
- V2 independent: take-back 0.00 K of a 4 K dip on a multi-sample charge vs 4.00 K on a one-sample charge
- attacks: perturb 3.016 -> 0 (note: also zeroes the short shape 0.0389 -> 0); null short shape 0.0389; mine: the dip taken back is 4.00 K of 4 for a one-sample charge and 0.00 K of 4 for a four-sample charge (rises on heated intervals return 0, ChargeSettle.advance `if not self.open or heated_interval: return 0.0`)
- V3 reach: yes: combi tanks' draw learner in real HA on every charge longer than one sample; class: new (confirmed); seam_rule enumerates: yes: ChargeSettle.advance and its fold call site

## D2-s3-09 -- verify (medium)

- metric: solve max narrowing (kW) from ceiling-probe intervals metered at the pump's floor
- method: V1 m5_drawrange.py base/--perturb-floor; V2 v2_d2b.py: DrawRange.takes_ceiling on a floor draw at the ceiling command, then 14 observe_ceiling samples at 1.5 kW and learned_max_kw; tree: planted export copy ../audit-r11-px-D2-2 (PYTHONPATH=tests/hastub; m4_tariff with HASTUB_TZ=Europe/Stockholm)
- V1 reproduced: narrowing 4.100 kW
- V2 independent: learned top 1.5 kW from floor-censored samples (configured 6.0)
- attacks: perturb 4.1 -> 0.0 (awaiting_probe); null uncensored arm keeps 6.0 and learns a genuine 4.0; mine: takes_ceiling(1.5 kW)=True, learned_max_kw=1.5 after 14 floor samples
- V3 reach: yes: ceiling experiments on a pump whose load sits below its minimum (mild weather) in real HA; class: new (confirmed); seam_rule enumerates: yes: takes_ceiling, learned_max_kw, solve_band, observe_ceiling

## D2-s3-10 -- verify (medium)

- metric: admitted slab fits whose UA error exceeds the admitted half-width, per noise arm
- method: V1 m5_sysid.py base/--perturb-bar5; V2 my own coverage test on the executed arms: one-sided binomial tail of the miss count against the nominal 0.05, and leave-one-arm-out; tree: planted export copy ../audit-r11-px-D2-2 (PYTHONPATH=tests/hastub; m4_tariff with HASTUB_TZ=Europe/Stockholm)
- V1 reproduced: 19 of 43 admitted fits miss (quantised 9 of 11)
- V2 independent: binomial tail 4.8e-14 against nominal 0.05; 0.31 miss rate with the quantised arm left out
- attacks: reproduced exactly: quantised 9/11, white 0.05 4/4, white 0.02 6/28 (19 of 43), white 0.005 1/166 (0.006), noise-free bias 4.88e-14; perturb: 0 misses in every arm (the bar at log 1.05 admits fewer fits, so to_zero is met partly by admitting fewer); P(X>=19 | n 43, p 0.05) = 4.8e-14, quantised alone 9.8e-11, white 0.02 alone 0.0023; leave-quantised-out 10 of 32 (0.31); seeded, counts, load-immune
- V3 reach: yes: sysid experiments in real HA with 0.1 C room sensors; class: new (confirmed); seam_rule enumerates: yes: adoption_decision, the half-width functions and the bar

## D2-s3-11 -- weaken (low)

- metric: learned gain / genuine gain averaged over gain hours; end house_heat_loss_scale
- method: V1 m5_crosscov.py base/--perturb-ridge0; V2 my own decomposition: the ridge's designed fixed point alpha/(alpha+ridge) = 0.05/0.07 against the measured recovery; tree: planted export copy ../audit-r11-px-D2-2 (PYTHONPATH=tests/hastub; m4_tariff with HASTUB_TZ=Europe/Stockholm)
- V1 reproduced: 0.5573; scale 0.9725 on zero-mean arms
- V2 independent: 0.557 = 0.780 of the designed fixed point 0.714; confounded share ~22 % of the designed recovery
- attacks: reproduced: recovery 0.5573 (0.5401-0.5687), white/quantised scale bias -0.0275 (0.9725), no-gain white/quantised within 1e-4; the drifting arm (not zero-mean) moves the scale +0.03 and is outside the claim. Perturb ridge 0: recovery 0.5573 -> 0.7748 (up, as stated), still 0.23 short of 1 with no ridge at all: the confounded share stands. The ridge tethers the profile to 0.714 of the gain by design (documented 'a perturbation of the prior'), so of the 44 % shortfall about 16 points are the cross-covariate defect (0.557 / 0.714 = 0.78) and the rest is designed; severity weakened
- V3 reach: yes: both learners fold the same residual in real HA once the heat-loss level converges; class: N-confounded-learner (confirmed); seam_rule enumerates: yes: ridge, alpha, the fold and learner_newton_step sites
