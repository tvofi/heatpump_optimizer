import json, sys
W = "/root/audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes"
REL = "dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes"
H = {
"0d159d7ddd1702d9": ("guessed price tail extend_price_series returns for known [1,2,3] SEK/kWh on a fresh (zero-confidence) PriceShapeModel",
  "guessed_tail_baseline=[3.0, 3.0, 3.0] (flat repeat of the last price); guessed_tail_mutant=[2.0, 2.0, 2.0] (known-window mean); guessed_tail_delta=1.0000; null_delta=0; flat_known_delta=0",
  "custom_components.heatpump_optimizer.price_model:extend_price_series, line 544",
  "key 0d159d7ddd1702d9 (CMP_BOUND) `model.confidence(when) <= 0.0` -> `< 0.0`. Direction: the tail moves from last_known to mean(known)/shape_mean",
  "model=None (both arms flat-repeat) and a constant known window (mean == last)", []),
"80fd46122d85566c": ("reason string prices_from_entity_state returns for a None state",
  "none_state_inputs_moved=0 (both 'Price entity is empty'); other_states_moved=0",
  "custom_components.heatpump_optimizer.price_model:prices_from_entity_state, line 820",
  "key 80fd46122d85566c (GUARD_OFF) `if state is None:` -> `if False:`. Direction: none found; the fall-through reads getattr(None,'state','') == '' and returns the same string",
  "non-None states, where the guard is false either way", []),
"b539d4504385a139": ("reason string prices_from_entity_state returns for an unknown/unavailable/blank state with empty-dict or non-dict attributes",
  "inputs_moved=4 of 5 ('Price entity is empty' -> 'Price entity published no today/tomorrow series'); null_delta=0",
  "custom_components.heatpump_optimizer.price_model:prices_from_entity_state, line 825",
  "key b539d4504385a139 (BOOLOP) `isinstance(attrs, dict) and attrs` -> `or attrs`. Direction: empty-entity reason -> no-series reason",
  "a numeric state with a populated series, where the guard is not consulted", []),
"55f9ec66dc8bfd54": ("pull_prices verdict for an entity price source with no entity configured, through the coordinator's composition _price_entity_state + pull_prices",
  "caller_inputs_moved=0 (absent/''/None all ('fail','Price entity is empty')); direct_moved=1 (a state handed in with no entity configured: reason changes)",
  "custom_components.heatpump_optimizer.price_model:pull_prices, line 855; caller coordinator:_fetch_tibber_prices via _price_entity_state",
  "key 55f9ec66dc8bfd54 (GUARD_OFF) `if not config.get(CONF_PRICE_ENTITY):` -> `if False:`",
  "the caller arm is its own control: _price_entity_state returns None whenever the entity is unset", []),
"88732fcb7c604858": ("slab_mode_one_state_identifiability verdict (one-state fit allowed) across tau_fast on the default 1 h shortest phase",
  "verdicts_moved=4 (tau_fast 0.200-0.333 h: True -> False); null_delta=0",
  "custom_components.heatpump_optimizer.sysid:slab_mode_one_state_identifiability (reads FAST_MODE_SETTLE_TAUS, line 549, at line 683)",
  "key 88732fcb7c604858 (CONST) `FAST_MODE_SETTLE_TAUS = 3.0` -> `6.0`, in memory by mock.patch.object. Direction: admitted -> refused for tau_fast in (1/6, 1/3] h",
  "an unconfigured slab (c_s = 0), refused before the constant is read", []),
"176d8ddb23988b95": ("SystemIdentification state after _finish on a completed slab fit (phase, last_run, result, routing flag), plus INFO log records",
  "completed_state_moved=0; completed_info_logs_baseline=1 mutant=0; null_refused_state_moved=0",
  "custom_components.heatpump_optimizer.sysid:SystemIdentification._finish, line 1853 (identify_slab stubbed to a fixed result in both arms)",
  "key 176d8ddb23988b95 (GUARD_OFF) `if self.result.completed:` -> `if False:`. Direction: only the INFO 'System identification complete' record disappears",
  "a refused fit, where the branch is not taken either way", []),
"de399cdbe79053ea": ("_over_excursion verdict at |room - baseline| == max_excursion_c (0.8 C, not configurable)",
  "readings_moved=0 of 202 (0.1 C readings 15-25 C); random_indoor_moved=0 of 600000; tie_base0.2_room1.0 baseline=False mutant=True; null_delta=0",
  "custom_components.heatpump_optimizer.sysid:SystemIdentification._over_excursion, line 1640",
  "key de399cdbe79053ea (CMP_BOUND) `> self.config.max_excursion_c` -> `>=`. Direction: False -> True at an exact float tie only",
  "excursions clearly inside/outside the bound", []),
"c5ddabc7d9641cba": ("step power _size_step_power returns for cop below 0.1",
  "low_cop_inputs_moved=68/384 (only at max_power 160 kW); null_cop_ge_0.1_moved=0/24; production_cop_min=1.050",
  "custom_components.heatpump_optimizer.sysid:SystemIdentification._size_step_power, line 1573",
  "key c5ddabc7d9641cba (CLAMP_DROP) `cop = max(cop, 0.1)` -> `cop = (cop)`",
  "cop >= 0.1, where the floor is inert", []),
"75d5865af3eceda7": ("step power _size_step_power returns, at inputs where the bisection's hi - lo reaches exactly 0.01 and at generic inputs",
  "tie_inputs_that_bisect=45/216; tie_inputs_moved=0/216; generic_inputs_moved=0/360",
  "custom_components.heatpump_optimizer.sysid:SystemIdentification._size_step_power, line 1604",
  "key 75d5865af3eceda7 (CMP_BOUND) `while hi - lo > 0.01:` -> `>= 0.01:` (one more halving at the exact tie)",
  "the generic inputs, where the tie never occurs", []),
"0d5a6ef5041b90f9": ("step power (kW electrical) _size_step_power returns, and its noiseless peak excursion",
  "inputs_moved=7/24; features cell (6 kW, COP 3, 21 C, 2 C, ua 0.20 C 8.0 gains 0.3): baseline=4.353515625 mutant=4.3125; peak 0.6499 -> 0.6402 C under bound 0.65",
  "custom_components.heatpump_optimizer.sysid:SystemIdentification._size_step_power, line 1606",
  "key 0d5a6ef5041b90f9 (GUARD_OFF) `if fits(q, bound):` -> `if False:`. Direction: the bisection never raises lo; the step is the coarse grid point, smaller",
  "inputs where fits(q_max) already holds (both return max_power_kw)", []),
"4f2d93e67ccda975": ("step power _size_step_power returns, plus DEBUG records",
  "inputs_moved=0/24; debug_records_baseline=1 mutant=0",
  "custom_components.heatpump_optimizer.sysid:SystemIdentification._size_step_power, line 1626",
  "key 4f2d93e67ccda975 (GUARD_OFF) `if best is not None:` (the debug-log block) -> `if False:`",
  "the returned value is the control: the block only logs", []),
"afbdfa240c441812": ("step power _size_step_power returns at the fits() peak tie",
  "real_inputs_moved=0/360; stub_peak_tie (predictor stubbed to (0.8, 0.7)) baseline=6.0 mutant=None; stub_null_below baseline=6.0 mutant=6.0",
  "custom_components.heatpump_optimizer.sysid:SystemIdentification._size_step_power.fits, line 1593",
  "key afbdfa240c441812 (CMP_BOUND) `peak <= bound` -> `peak < bound`",
  "the predictor stubbed 0.01 C under the bound", []),
"ebd8c531fddf0a24": ("step power _size_step_power returns at the fits() final tie",
  "real_inputs_moved=0/360; stub_final_tie (predictor stubbed to (0.7, 0.8)) baseline=6.0 mutant=None; stub_null_below baseline=6.0 mutant=6.0",
  "custom_components.heatpump_optimizer.sysid:SystemIdentification._size_step_power.fits, line 1593",
  "key ebd8c531fddf0a24 (CMP_BOUND) `final <= bound` -> `final < bound`",
  "the predictor stubbed 0.01 C under the bound", []),
"4a189db92053760e": ("SysIdResult (completed, reason, internal_gains_kw) _slab_outcome returns for a converged fit outside the plausibility bands",
  "inputs_moved=16/21 (refused -> completed=True, reason 'ok'); null_in_band_delta=0",
  "custom_components.heatpump_optimizer.sysid:SystemIdentification._slab_outcome, line 2409 (interval/confidence helpers stubbed to constants in both arms)",
  "key 4a189db92053760e (GUARD_OFF) `if refusal is not None:` -> `if False:`. Direction: completed False -> True",
  "an in-band fit (ua 0.2, C 4, gains 0.4)", []),
"80cb9a8152f72e57": ("internal_gains_kw _slab_outcome publishes for a fitted gains value in [-0.5, 2.0]",
  "inputs_moved=4/8 (fitted gains in [-0.5, 0): baseline 0.0, mutant the negative value)",
  "custom_components.heatpump_optimizer.sysid:SystemIdentification._slab_outcome, line 2411 (helpers stubbed as for 4a189db92053760e)",
  "key 80cb9a8152f72e57 (CLAMP_DROP) `np.clip(gains_kw, 0.0, 2.0)` dropped. Direction: 0.0 -> negative gains",
  "fitted gains in [0, 2]", []),
"1f4a10ae90bbf2d9": ("_unadoptable outcome for 0/1/2/4 settling rows, and the settling-row count step() hands it",
  "rows1 baseline=refusal string, mutant=raised IndexError; rows0/2/4 moved=0; step_driven min_settling_rows=2 (15/30/60/90-min cadence)",
  "custom_components.heatpump_optimizer.sysid:SystemIdentification._unadoptable, line 1705",
  "key 1f4a10ae90bbf2d9 (CMP_BOUND) `len(rows) > 1` -> `>= 1`. Direction: one settling row raises IndexError (rows[-2])",
  "0, 2 and 4 rows, where both arms agree", []),
}
COMMON_BODY = {"c5ddabc7d9641cba": "sizer", "75d5865af3eceda7": "sizer", "0d5a6ef5041b90f9": "sizer", "4f2d93e67ccda975": "sizer",
               "afbdfa240c441812": "sizer", "ebd8c531fddf0a24": "sizer", "4a189db92053760e": "slab", "80cb9a8152f72e57": "slab"}
pro = open("prologue.py").read()
for k, (metric, exp, sym, pert, null, _) in H.items():
    hdr = f"""#!/usr/bin/env python3
# Box D3-g32 (round 11, seat D3-s1), D3 step 4 probe for full-gate survivor {k}.
# Metric: {metric}.
# Command: PYTHONPATH=tests/hastub python3 {REL}/probe_{k}.py   (from the repository root)
# EXPECTED: {exp}.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g32, 4 vCPU Intel Xeon @ 2.10GHz, venv-ci CPython 3.14.
# Instrumented symbol: {sym}.
# Perturbation: {pert}; applied in memory (the function re-compiled from its own source with the one line swapped), never on disk.
# Null control: {null}.
# Counts are exact (no timing); thread_factor/load1/swapins are printed per the harness contract.
"""
    body = open(f"b_{k}.py").read()
    common = {"sizer": open("sizer_common.py").read(), "slab": open("slab_common.py").read()}.get(COMMON_BODY.get(k), "")
    open(f"{W}/probe_{k}.py", "w").write(hdr + pro + "\n" + common + "\n" + body)
print(len(H))
