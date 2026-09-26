# Round 9 leads, seat L4 (batch 1)

Baseline `1936d5ca72a06556eeed4e8e5bf3dea520e517e1`, export prepared as a finder's (git archive,
`docs/audit-*.md` and `docs/backlog.md` removed, `tools/audit/` from the baseline,
`handoff/round9/r9-strip-rounds.sh` applied: 498 files removed, 235 kept). Every harness runs from the
export root with `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python`. Owners were assigned with
`tools/audit/check_scopes.py --seat` at the baseline. No D3 mutation script was run.

18 leads: 5 converted, 13 closed. The machine-readable record is `leads-L4.json` beside this file.

## Findings

| id | severity | class | metric (perturbed) | harness |
|---|---|---|---|---|
| D2-s2-81 | medium | P3 | two-zone floor breach 2.4672 degree-steps over 12 cells (L1 x2: 0.8574); single-zone 0.1471, flat 0 | `tools/audit/round9/D2/leads/l4_zone_floor.py` |
| D4-s2-81 | medium | new | 41 setup strings identical en/sv (Swedish table: 0); narrative null 0 | `tools/audit/round9/D4/leads/l4_setup_labels.py` |
| D2-s4-81 | medium | P5 | 19 of 80 exact noise-free preset fits refused, 24 aborted, 37 admitted (bar ln 1.20: 2 refused) | `tools/audit/round9/D2/leads/l4_sysid_null_refusal.py` |
| D12-s3-81 | medium | P8 | 8 blocking verdicts, 4 of 12 currencies (bound 1e6: 4); SEK/EUR/NOK/DKK 0 | `tools/audit/round9/D12/leads/l4_fee_bound.py` |
| D6-s1-81 | low | P11 | SEK fallback reached on 0 of 2 HA core versions (unconditional fallback: 2); stub SEK | `tools/audit/round9/D6/leads/l4_currency_fallback.py` |

- **D2-s2-81.** `_comfort_terms` averages two zones with `0.5 x (...)`, which halves each zone's
  quadratic floor term and its `_COMFORT_FLOOR_L1` term; that constant's comment says 2.0 is the
  smallest value that removes residual floor violations. The breach sits in `winter_typical` (1.314
  with DHW, 1.139 without; coldest 16.54 C against min 17.0), so leave-one-out leaves 0.105 mean
  with the worst cell dropped. Holding the floor costs 70.52 against 67.50 SEK in
  `two|dhw|winter_typical`. The residual 0.856 under the perturbation is the still-halved quadratic.
- **D4-s2-81.** `topology._SLOTS` and `render_text_summary` are English literals with no language
  input. The Swedish `setup_overview` page renders 22 of its 23 text lines in English; the plan
  sensors' `setup_topology` and `sensor_advisor` labels, which the card prints verbatim, too.
  `narrative.render` on the same sensors follows `hass.config.language`. Owner D4-s2 because the
  flow seam (`config_flow._setup_overview_form`) is in its cells; the card seam is D4-s1's surface.
- **D2-s4-81.** Zero bias, zero noise, plant equal to the declaration. Refusals carry half-widths
  0.096 to 0.234 against the 0.0953 bar with fit error 0.0000, concentrated in radiator,
  post-2005 and low-energy houses (8 of 19 timber crawlspace; 11 with the worst structure
  dropped). The 24 plausibility aborts are not separated into "true tau/UA outside the box" and "fit
  misses it". sysid is off by default (`DEFAULT_SYSID_ENABLED = False`), which is why this is medium.
  D2-s4's own grid covered only `typical_slab` and `heavy_old`.
- **D12-s3-81.** The exchange-rate table and the 0.05 EUR/kWh fee are stated assumptions in the
  header; `--fee` moves the fee. Three seams: `grid_fee.spec_problem` (bound 10), the
  `grid_fee_fixed` selector (max 5, labelled in the instance currency), `_audit_grid_fee` (repair).
- **D6-s1-81.** HA core's `Config.__init__` sets `currency = "EUR"` in 2025.2.0 (hacs.json minimum)
  and 2026.2.3, read by AST from wheels fetched with `pip download --no-deps` into a mktemp root.
  The SEK label comes from `tests/harness.py`'s stub, which pins it.

## Closed

| raised by | symbol | why |
|---|---|---|
| D0-s2 | `_comfort_terms` (summer_warm constant) | owner D2-s2; measured non-finding: polish gap 0.0000 % in 12 summer_warm cells |
| D0-s3 | `_terminal_cost` | owner D2-s2 measured it: terminal/continuation ratio 0.997-1.123 over 6 cells incl. shoulder |
| D0-s3 | `_warm_start_starts` docstring | done by L1: D5-s2-51 |
| D0-s3 | `predicted_cost` | owner D2-s2 identity (cost_err 0 on 50 fixtures); README:488 claims only the plan's cost |
| D1-s2 | `_diagnose_payload` docstring | owner D5-s2; measured non-finding: leaked_writes 0 (in-thread perturbation 1) |
| D2-s1 | `forecast_free_heat` NaN | owner D1-s5; measured non-finding: 0 of 27 non-finite forecasts |
| D8-s2 | `_idle_action` (entity power) | covered by D8-s1-03's property and fix scope; the idle seam belongs in its enumeration |
| D9-s2 | `_finite` scrub | owner D9-s2's non-findings bound the whole entity read and the retained series it walks |
| D12-s2 | `get_current_action` power_normalized | covered by D12-s2-03 (property [0,1] on every compressor kind; null arm measured -0.2) |
| D12-s2 | `_idle_action` (coordinator consumers) | owner D1-s2; reachable only on a >1-step backward clock jump between `_solve_anchor` and the one caller at coordinator.py:5074; not measured |
| D12-s3 | `_build_data_dict` defaults | owner D1-s2; every surface gates on `reading_ok`, which rides in the same dict; not measured |
| D14-s2 | `stored_answers` | owner D4-s2; measured non-finding: round-trip mismatch 0 of 32 |
| D14-s3 | `_multi_start_minimize` ABNORMAL | owner D0-s1; a challenger's ftol 1e-12 termination, not production; residue is D0-s2-01 |

## Non-findings

- summer_warm constant: `tools/audit/round9/D0/s2/polish.py --horizon 24 --prices summer_typical,shoulder,flat --weather summer_warm --tz 0,1 --dhw 0,1`
  (D0-s2's harness from `origin/handoff/audit-r9-find-B2`; log `D2/leads/l4_summer_warm_polish.log`): gap 0.0000 % in 12 of 12.
- `tools/audit/round9/D5/leads/l4_diag_copy.py`: the payload is the live record (1), yet leaked_writes 0; `--perturb` 1.
- `tools/audit/round9/D1/leads/l4_free_heat_nan.py`: nonfinite_forecast_cells 0 of 27; `--perturb` 1;
  `_space_demand_kw` non-finite only on inf state (2 of 6), which InputReader never delivers.
- `tools/audit/round9/D4/leads/l4_quick_roundtrip.py`: 0 of 32; store-keyed read-back `--perturb` 16.

## Not finished

- D2-s4-81: the 24 plausibility aborts are not attributed (plant outside the box versus fit error).
- The two leads closed "not measured" (coordinator idle consumers, data-dict defaults) were closed on
  the code path, not on an executed number.

## Exposure

Read under the leads brief: owner and raiser reports in the intake `reports.json`, and D0-s2's
`polish.py`/`race.py`, D14-s3's `p5_gate.py`, D2-s2's `terminal_continuation.py` header, D2-s4's
`coverage.py` header and D9-s2's `loop_work.py` header from their handoff branches. No `docs/audit-*`,
no GitHub, no `gh`.
