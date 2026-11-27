Tests-only pins for the money seam's surviving mutants (#3755, class I1), judged at a826f55f8c (`dev/audit/rounds/round11/D3/wave-judge/JUDGE.json`), in the shape `dev/audit/rounds/round11/PLAN/ADR-011-survivor-pins.md` (at e8aefbb452) fixes. Of the 40 findings in `R11-D3-PINS-money`, 39 get one check each in `tests/guard_pins.py` (the `_money_pins()` group, reported as `R11-D3-PINS-money <key8> ...`) and one `tests/mutation_ledger/killed_by/` row each. One is a non-finding at this base (below). No file under `custom_components/` is edited.

Each pin drives the production entry point the judge's probe drives (`grid_fee.apply_catalog`, `max_abs_component`, `min_component`, `parse_rules`; `PriceShapeModel.observe_day`, `observe_day_quarters`, `shape_for`, `expected_daily_min`, `from_dict`, `summary`; `extend_price_series`, `prices_from_entity_state`, `pull_prices` over a stub session; `tariff.PeakTracker.from_dict`/`observe`/`as_dict`, `CapacityTariff.marginal_price_per_kw`, `_one_per_day`, `_smooth_topk_sum`, `_smooth_topk_sum_batch`, `realised_peak`, `metering_windows`) with the probe's moving input. It asserts the outcome the probe measured on the unpatched tree: a returned value, `None`, a label, a reason string, a WARNING count, or a value recorded from the unpatched run with a tolerance below the mutant's move. A module-constant mutant is asserted through the learned or predicted value, never the constant. No pin patches production in memory or re-states a production expression.

**Non-finding, returned to the judge:** `D3-wave-b5a482468c783209` (`observe_day`, `if mean <= 1e-6:` -> `<`). At this base the guard moved into `price_model._usable_day` as `float(np.mean(values)) <= 1e-6` (R11-SEAM-money, #3726). Its `CMP_BOUND` mutant there is already killed by `tests/features.py`'s check "R11-SEAM-money: a day of prices averaging exactly the 1e-6 floor is not learned; 2e-6 is". The ledger already holds that row at `tests/mutation_ledger/killed_by/price_model.py/_usable_day.CMP_BOUND.fc735ea9.json` (`killed_by: tests/features.py`). No pin was written.

Seven findings sit in functions that differ from the wave baseline 92d38ecb64 at the merge base (`d3_fnstate.py` at e8aefbb452: same 25, changed 7, gone 0, module 8). Each was re-located by its patch text, scoped to its enclosing function. Two pairs share one patch text: in `observe_day`, 0b10a7c7 is the first `if self.days[idx] == 0:` (residual-variance seed) and c4697335 the second (shape seed); in `summary`, 3a064c11 is the first sqrt clamp and efa02472 the second. 911f3cf5 is the third `return None` of `apply_catalog` (the stale-row branch, judge site `grid_fee.py:496`, unchanged).

## Head

bb13a40c24ce376eab6d56c55c2aadf6c78a078a, merge base and `origin/main` 7194ff84c09dd9d54a99f8208c906136981fd9dc, measured 2026-11-27T01:27Z.

## Mutation proof

Each row's own mutant, run through the ledger's own instrument against the pin script: `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --anchor '<anchor>' --scripts tests/guard_pins.py`. It printed `killed by tests/guard_pins.py: <file>:<line> <KIND>` for each of the 39 anchors below, with its `NULL_COMMENT` null control surviving. The checks named are the `FAIL` lines `tests/guard_pins.py` printed with that one patch applied to a copy of the tree. Every other check of the script passed (130 checks in all).

| key | sev | anchor | FAIL under the patch |
|---|---|---|---|
| b9b6cf1d15a84248 | medium | `custom_components/heatpump_optimizer/price_model.py:PriceShapeModel.expected_daily_min GUARD_OFF 4711f894` | `R11-D3-PINS-money b9b6cf1d expected_daily_min guard` |
| c4697335da324182 | medium | `custom_components/heatpump_optimizer/price_model.py:PriceShapeModel.observe_day GUARD_OFF 6ea17095#2` | `R11-D3-PINS-money c4697335 shape seed on first day`; `R11-D3-PINS-money 3a064c11 summary weekday sigma`; `R11-D3-PINS-money efa02472 summary weekend sigma`; `R11-D3-PINS-money 0ea7620c SHAPE_ALPHA`; `R11-D3-PINS-money 213a122a SHAPE_CONFIDENCE_DAYS`; `R11-D3-PINS-money b10967dd SHAPE_MIN`; `R11-D3-PINS-money b5aef007 VAR_ALPHA` |
| 3a064c11321daba7 | medium | `custom_components/heatpump_optimizer/price_model.py:PriceShapeModel.summary CLAMP_DROP 2db6a2f4` | `R11-D3-PINS-money 3a064c11 summary weekday sigma`; `R11-D3-PINS-money b5aef007 VAR_ALPHA`; `R11-D3-PINS-money 0b10a7c7 residual var seed` |
| efa02472a5a773bc | medium | `custom_components/heatpump_optimizer/price_model.py:PriceShapeModel.summary CLAMP_DROP 2db6a2f4#2` | `R11-D3-PINS-money efa02472 summary weekend sigma` |
| 28de20de50a9540b | medium | `custom_components/heatpump_optimizer/price_model.py:_profile_index CMP_BOUND 7c9e7277` | `R11-D3-PINS-money efa02472 summary weekend sigma`; `R11-D3-PINS-money 28de20de saturday is weekend` |
| e5eea05f4463602e | medium | `custom_components/heatpump_optimizer/price_model.py:_tibber_post GUARD_OFF 906a65ed` | `R11-D3-PINS-money e5eea05f tibber non-200 no json` |
| 0d159d7ddd1702d9 | medium | `custom_components/heatpump_optimizer/price_model.py:extend_price_series CMP_BOUND 4c916e3a` | `R11-D3-PINS-money 0d159d7d zero-confidence flat tail` |
| de935c38786265e7 | medium | `custom_components/heatpump_optimizer/tariff.py:PeakTracker.from_dict GUARD_OFF b770da79` | `R11-D3-PINS-money de935c38 non-finite window_factor keeps window` |
| 7fcaf91cced5ce41 | medium | `custom_components/heatpump_optimizer/tariff.py:PeakTracker.observe GUARD_OFF 84e98156` | `R11-D3-PINS-money 7fcaf91c non-finite/negative sample dropped` |
| 3e9a439baa86a074 | medium | `custom_components/heatpump_optimizer/tariff.py:_stored_peaks CMP_BOUND 6d475b09` | `R11-D3-PINS-money 3e9a439b zero stored peaks survive restart` |
| 9297f123a6265555 | low | `custom_components/heatpump_optimizer/grid_fee.py:apply_catalog GUARD_OFF 481898b9` | `R11-D3-PINS-money 9297f123 none/empty product no warning` |
| 911f3cf5172ffc44 | low | `custom_components/heatpump_optimizer/grid_fee.py:apply_catalog RETURN_DEL d7923b87#3` | `R11-D3-PINS-money 911f3cf5 stale catalog row returns None` |
| b5f0a73275608684 | low | `custom_components/heatpump_optimizer/grid_fee.py:max_abs_component CMP_BOUND 23a3a01d` | `R11-D3-PINS-money b5f0a732 max_abs tie labelled fixed` |
| 68cc141bf2c3493a | low | `custom_components/heatpump_optimizer/grid_fee.py:min_component CMP_BOUND ead59e4c` | `R11-D3-PINS-money 68cc141b min_component tie labelled fixed` |
| 2043855ef5cf151d | low | `custom_components/heatpump_optimizer/grid_fee.py:parse_rules GUARD_OFF 4893b0a8` | `R11-D3-PINS-money 2043855e parse_rules None is empty` |
| 0ea7620ce058c489 | low | `custom_components/heatpump_optimizer/price_model.py:<module> CONST 5633f4fc` | `R11-D3-PINS-money 3a064c11 summary weekday sigma`; `R11-D3-PINS-money efa02472 summary weekend sigma`; `R11-D3-PINS-money 0ea7620c SHAPE_ALPHA`; `R11-D3-PINS-money 213a122a SHAPE_CONFIDENCE_DAYS`; `R11-D3-PINS-money b5aef007 VAR_ALPHA` |
| 213a122afd9ff3e1 | low | `custom_components/heatpump_optimizer/price_model.py:<module> CONST a15838a8` | `R11-D3-PINS-money 3a064c11 summary weekday sigma`; `R11-D3-PINS-money efa02472 summary weekend sigma`; `R11-D3-PINS-money 213a122a SHAPE_CONFIDENCE_DAYS`; `R11-D3-PINS-money b5aef007 VAR_ALPHA`; `R11-D3-PINS-money a5c9796d five days trusted` |
| b10967dd4ea185fd | low | `custom_components/heatpump_optimizer/price_model.py:<module> CONST 90ecade5` | `R11-D3-PINS-money c4697335 shape seed on first day`; `R11-D3-PINS-money 0ea7620c SHAPE_ALPHA`; `R11-D3-PINS-money 213a122a SHAPE_CONFIDENCE_DAYS`; `R11-D3-PINS-money b10967dd SHAPE_MIN`; `R11-D3-PINS-money 0b10a7c7 residual var seed` |
| 7e5493bcbddd6c18 | low | `custom_components/heatpump_optimizer/price_model.py:<module> CONST df03c978` | `R11-D3-PINS-money 7e5493bc QUARTER_ALPHA` |
| 66686e3bc3bac9b9 | low | `custom_components/heatpump_optimizer/price_model.py:<module> CONST 74d4ee92` | `R11-D3-PINS-money 7e5493bc QUARTER_ALPHA`; `R11-D3-PINS-money 66686e3b QUARTER_CONFIDENCE_DAYS` |
| 5bf50f5d986f927d | low | `custom_components/heatpump_optimizer/price_model.py:<module> CONST 0f3977a9` | `R11-D3-PINS-money 5bf50f5d QUARTER_FACTOR_MIN`; `R11-D3-PINS-money cc96ce9e QUARTER_FACTOR_MAX` |
| cc96ce9e391ca6f2 | low | `custom_components/heatpump_optimizer/price_model.py:<module> CONST 8c1b36af` | `R11-D3-PINS-money cc96ce9e QUARTER_FACTOR_MAX` |
| b5aef00760fd5ea8 | low | `custom_components/heatpump_optimizer/price_model.py:<module> CONST f47f8e99` | `R11-D3-PINS-money 3a064c11 summary weekday sigma`; `R11-D3-PINS-money efa02472 summary weekend sigma`; `R11-D3-PINS-money b5aef007 VAR_ALPHA` |
| a5c9796d35117839 | low | `custom_components/heatpump_optimizer/price_model.py:PriceShapeModel.expected_daily_min CMP_BOUND cb6981eb` | `R11-D3-PINS-money a5c9796d five days trusted` |
| 13cadf1ab9a2de61 | low | `custom_components/heatpump_optimizer/price_model.py:PriceShapeModel.from_dict CMP_BOUND 73f28fdd` | `R11-D3-PINS-money 13cadf1a residual var max kept` |
| 0b10a7c76e2514d2 | low | `custom_components/heatpump_optimizer/price_model.py:PriceShapeModel.observe_day GUARD_OFF 6ea17095` | `R11-D3-PINS-money 3a064c11 summary weekday sigma`; `R11-D3-PINS-money efa02472 summary weekend sigma`; `R11-D3-PINS-money b5aef007 VAR_ALPHA`; `R11-D3-PINS-money 0b10a7c7 residual var seed` |
| 4e79ba6ea642d086 | low | `custom_components/heatpump_optimizer/price_model.py:PriceShapeModel.observe_day_quarters CMP_BOUND 6d5792ad` | `R11-D3-PINS-money 4e79ba6e hour mean 1e-6 unusable` |
| 12cd6ddd79fb36fc | low | `custom_components/heatpump_optimizer/price_model.py:PriceShapeModel.observe_day_quarters GUARD_OFF 6b2d03c8` | `R11-D3-PINS-money 7e5493bc QUARTER_ALPHA`; `R11-D3-PINS-money 66686e3b QUARTER_CONFIDENCE_DAYS`; `R11-D3-PINS-money 5bf50f5d QUARTER_FACTOR_MIN`; `R11-D3-PINS-money cc96ce9e QUARTER_FACTOR_MAX`; `R11-D3-PINS-money 12cd6ddd quarter seed` |
| a38612ad3ad9cd34 | low | `custom_components/heatpump_optimizer/price_model.py:_in_domain CMP_BOUND de1a0615` | `R11-D3-PINS-money a38612ad zero shape renormalised` |
| b539d4504385a139 | low | `custom_components/heatpump_optimizer/price_model.py:prices_from_entity_state BOOLOP 44f0178f` | `R11-D3-PINS-money b539d450 empty attrs reason` |
| 246043395831f540 | low | `custom_components/heatpump_optimizer/tariff.py:CapacityTariff.marginal_price_per_kw CMP_BOUND 9b86f195` | `R11-D3-PINS-money 24604339 zero peaks_averaged marginal 0` |
| 4ad3dc13bfdb70a8 | low | `custom_components/heatpump_optimizer/tariff.py:PeakTracker.from_dict CMP_BOUND 55d61241` | `R11-D3-PINS-money 4ad3dc13 window_factor 0.0 kept` |
| 37b3c9a03326d207 | low | `custom_components/heatpump_optimizer/tariff.py:_one_per_day GUARD_OFF b1117b0c` | `R11-D3-PINS-money 37b3c9a0 undated peaks all kept` |
| 6536ff6b094f971d | low | `custom_components/heatpump_optimizer/tariff.py:_smooth_topk_sum GUARD_OFF 65785e02` | `R11-D3-PINS-money 6536ff6b smooth topk k<=0 is 0` |
| 5371ee2b5e897750 | low | `custom_components/heatpump_optimizer/tariff.py:_smooth_topk_sum GUARD_OFF 6bee434a` | `R11-D3-PINS-money 5371ee2b smooth topk no positive is 0` |
| 2d037a10caa62e28 | low | `custom_components/heatpump_optimizer/tariff.py:realised_peak GUARD_OFF eb0a46c5` | `R11-D3-PINS-money 2d037a10 realised_peak empty is 0` |
| 5f094dbca9a593e9 | low | `custom_components/heatpump_optimizer/tariff.py:_smooth_topk_sum CLAMP_DROP 39986157` | `R11-D3-PINS-money 5f094dbc smooth topk tiny plateau value` |
| 996dce5148e02763 | low | `custom_components/heatpump_optimizer/tariff.py:_smooth_topk_sum_batch CLAMP_DROP e202a9d1` | `R11-D3-PINS-money 996dce51 smooth topk batch tiny plateau value` |
| 1894e6dcd2251a30 | low | `custom_components/heatpump_optimizer/tariff.py:metering_windows GUARD_OFF eb0a46c5` | `R11-D3-PINS-money 1894e6dc metering_windows empty stays empty` |

Several patches also fail sibling pins that share a learned model (e.g. the SHAPE_ALPHA, SHAPE_CONFIDENCE_DAYS and SHAPE_MIN patches each fail 5). The table lists every failing check, and each key's own pin is among them.

## Null control

- Unpatched tree: `PYTHONPATH=tests/hastub python3 tests/guard_pins.py` -> `ALL 130 GUARD PIN CHECKS PASSED`, 39 of them `R11-D3-PINS-money`.
- Each `--anchor` run applies its own comment-only `NULL_COMMENT` edit to the mutated file. Every one survived `tests/guard_pins.py`, so a pin goes red on the mutant, not on any edit.
- No production line changed: `git diff --stat $(git merge-base origin/main HEAD)...HEAD -- custom_components/` prints nothing.

## Figures

- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` -> `MODE: SCOPED -- 3 script(s) run, 31 scoped out` (doc_claims, entities, guard_pins).
- Scoped scripts, `PYTHONPATH=tests/hastub`: `python3 tests/doc_claims.py` -> ALL 445 checks PASSED; `python3 tests/entities.py` -> ALL 2787 ENTITY CHECKS PASSED; `python3 tests/guard_pins.py` -> ALL 130 GUARD PIN CHECKS PASSED.
- run_always: `python3 tests/env_drift.py --claims-only 7194ff84c09dd9d54a99f8208c906136981fd9dc` -> ok; `python3 tests/closure.py selftest` -> ALL 118 closure shrink pins PASSED; `python3 tests/layout.py` -> ok; `python3 tests/harness_headers.py` -> ALL 112 HARNESS HEADER CHECKS PASSED.
- Structure: `python3 tests/structure.py` -> STRUCTURE RATCHET PASSED. Architecture score: dS 0 (no file under `custom_components/` changed; ADR-011 Consequences).
- Ledger: `cd tests && python3 -c "import mutation_table as m; b=m.load_budgets(); s=m.inventory(); print(m.layout_problems(), m.completeness_problems(b, s))"` -> `[] []`.
- Re-location, from the export of e8aefbb452 (`$EXPORT/dev/audit/rounds/round11/PLAN/d3_fnstate.py` sha1 12167cf457102840685558bc28c9c6833e3aae11, `$EXPORT/dev/audit/rounds/round11/PLAN/D3-FOLD.json` sha1 25231ce450a8ddf169b7b56f7f6f3b05b6944900): `python3 -I $EXPORT/dev/audit/rounds/round11/PLAN/d3_fnstate.py $EXPORT/dev/audit/rounds/round11/PLAN/D3-FOLD.json 7194ff84c09dd9d54a99f8208c906136981fd9dc --group R11-D3-PINS-money --ids` -> same 25 changed 7 gone 0 module 8.
- Finder's harness, at the merge base, from the export of a826f55f8c. `$EXPORT/<path>` is run as its header's `Command:` line, with only its line-number anchor updated where the production line moved: 39 of 40 reproduce their `EXPECTED RESULT` lines (the moving arm moves, the null arm reads 0). b5a48246's anchor text is gone, as above. The probes mutate in memory, and this diff leaves every line they mutate alone, so they read the same at the head: flat at both ends by construction. The companion that reads the defect at the base and not at the head is each pin's FAIL under its patch, above. Paths and sha1s:

  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_9297f123a6265555.py` sha1 4d54ade884576853ace2cc60c9268f07eb9448cc
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_911f3cf5172ffc44.py` sha1 07e62983de2429c01de086f29f745ac1fc9e2164
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_b5f0a73275608684.py` sha1 7e95624a3bc764f1b04a06bca4e38f09eb5c2a4f
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_68cc141bf2c3493a.py` sha1 b71f0d6ae66838db6764825c8e520d198ce0abfc
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_2043855ef5cf151d.py` sha1 e7cbc392b9518a7eed6d51e067b8ccdb2d9ad987
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_0ea7620ce058c489.py` sha1 0667d58cff52d2c27c2601317cffda853c6abb90
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/probe_213a122afd9ff3e1.py` sha1 db31c073e102e688397749b37adab7ee4c75202e
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_b10967dd4ea185fd.py` sha1 9218e8f9cbbef724fb983d5c8754777379daf7ec
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_7e5493bcbddd6c18.py` sha1 27ac9bf51b72c652fc4797bf13e759b885d9f441
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_66686e3bc3bac9b9.py` sha1 a8bcc24dbfe27fab96b553cb0d2671269755b3ae
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_5bf50f5d986f927d.py` sha1 76ec33e25f7aa789838e175c4f135095482d43b6
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_cc96ce9e391ca6f2.py` sha1 0d5c2c5ca2b3a537b0a775e9c32761ddadfe22a8
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_b5aef00760fd5ea8.py` sha1 6956a79379c34a1a4c29511c6e4ace2add22f3ed
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_b9b6cf1d15a84248.py` sha1 04011657e9e91cbac31f2674a46799e435b78916
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_a5c9796d35117839.py` sha1 05bf5eac9ccd957fa3cec519fc80e6e81e85eb0d
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_13cadf1ab9a2de61.py` sha1 db6ebd2aadda76a39501cbabe9b1eb229ef6019e
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_b5a482468c783209.py` sha1 7e2cfb7d5b3efcdc67a1b55bcadcf521714a9217
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_0b10a7c76e2514d2.py` sha1 f5436f96e56088a8f019a02f5af72e89d37ffe23
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_c4697335da324182.py` sha1 2cbc633d50a88e4f1731779fd66cd6de46f0cbcb
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_4e79ba6ea642d086.py` sha1 84bc0b342dda70d04e7ed01af84dee75724207f6
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_12cd6ddd79fb36fc.py` sha1 1c2de48720fc7b2e15853a3c5fb14b7467b9f650
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_3a064c11321daba7.py` sha1 3bf2018d3afd9464c8d0a4d579d84ff267ddda53
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_efa02472a5a773bc.py` sha1 e5d90a20464ee7ed8e656c5bd6beb4f3e157cb15
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_a38612ad3ad9cd34.py` sha1 b3d0a4c444c764470f4d972470d62c096e9911fa
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_28de20de50a9540b.py` sha1 523cf9f0144e90e9e24b1326571aa3a4c74d28d9
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_e5eea05f4463602e.py` sha1 c01914757e2b35ab6709d355e9fa5b8d40a21883
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_0d159d7ddd1702d9.py` sha1 d980f6667898f3874eef385a2e5abbb5fff731a6
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_b539d4504385a139.py` sha1 bfc63bc1764d54027d83af6b38423d865fb9d5d5
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g39/probes/probe_246043395831f540.py` sha1 81ba6cea11c07c3e9cb54e3e6166888fd66fc6ca
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g39/probes/probe_de935c38786265e7.py` sha1 e3126c5d639ea050c5d1e0098f98846b1c802728
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g39/probes/probe_4ad3dc13bfdb70a8.py` sha1 37429b9fa33e470ad86d979efe6f0e3532defaf9
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g39/probes/probe_7fcaf91cced5ce41.py` sha1 3fe5400f133490ea47a02666a01bdf6723d548fe
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g39/probes/probe_37b3c9a03326d207.py` sha1 02bec96c1cafc294bf7464153d6ed5f328313400
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g39/probes/probe_6536ff6b094f971d.py` sha1 6cd7565978e8977177229a77fc1704c764289219
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g39/probes/probe_5371ee2b5e897750.py` sha1 b825d4f6e0e134255441e616bed68ee8051957a0
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g41/probes/probe_2d037a10caa62e28.py` sha1 54cc74d5c2576d0777dabfad9d680df02a7894ef
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_5f094dbca9a593e9.py` sha1 2a78e0bf3237f393bbfeba0e7dac5f282b2d5b10
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_996dce5148e02763.py` sha1 07f7a3df7fd71d6e0244f001eba62b37bc8c22e3
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_3e9a439baa86a074.py` sha1 8a2822e549a3e2b01069be05bc60bee81c97f6b2
  - `$EXPORT/dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_1894e6dcd2251a30.py` sha1 ad303bda27af21e8fc6663090a9b81288b3c5a15
- Existing checks under each patch: `python3 tools/audit/seat/features_block.py --prelude 'exec(open("OUT").read())' "# R11-SEAM-money (D8-s1-02, D2-s3-07)" "# R10-HOTFIX-SAV-ESTIMATE"`, with OUT from `--emit-prelude` on the same markers. These are the only `tests/*.py` lines added since 92d38ecb64 that name the seam's symbols, per `git diff 92d38ecb64 HEAD -- 'tests/*.py'` filtered for them. Under each of the 40 patches: `ALL 10 FEATURES BLOCK PASSED` for 39, and 1 FAILED for b5a48246 alone.

## Red checks

none

## Forward-carry

none

## Friction

none
