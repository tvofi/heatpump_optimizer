# Round 10 form normalisation

Written by `dev/audit/rounds/round10/intake/normalise.py` (its docstring states rules R1-R9). Form only: no claim, number or command is changed; every changed field keeps its original in `<field>_original`. A row whose `after` is `(unchanged)` names why no rule applied; intake still rejects that finding.

| id | field | before | after | rule |
|---|---|---|---|---|
| D3-s1-01 | perturbation.expected_direction | prior_kept 1 -> 0 (fabricated 0 -> 1, rows 24 -> 48) | to_zero | R2 |
| D3-s1-01 | title | (122 chars) | (114 chars) No check pins that a raising weather fetch keeps the previous forecast; the and->or mutant at coordinator.py:6522… | R9 |
| D3-s1-02 | perturbation.expected_direction | live_guards 12 -> 0 | to_zero | R2 |
| D9-s1-01 | perturbation.expected_direction | cont sse_per_grad 288 -> 97; cont_fun SSE -> 0; total SSE falls 13.5-31%; main grads unchanged | down | R2 |
| D9-s1-01 | evidence.load1 | 19.98-25.98 | (unchanged) | unresolved: not a single number (a range) |
| D9-s1-01 | evidence.thread_factor | 1.000 | 1.0 | R4 |
| D9-s1-02 | perturbation.expected_direction | max heartbeat gap falls (measured 124->29 ms, 87->32 ms) | down | R2 |
| D9-s1-02 | evidence.load1 | 26.16-27.58 | (unchanged) | unresolved: not a single number (a range) |
| D9-s1-02 | evidence.thread_factor | 1.002 (residual after subtracting the deliberate executor thread CPU) | 1.002 | R5 |
| D5-s1-01 | perturbation.expected_direction | down: 5 -> 1 | down | R1 |
| D5-s1-01 | evidence.cpu_or_wall | n/a (count) | count | R6 |
| D5-s1-01 | metric_definition | (241 chars) | (198 chars) Count of (doc, line, label) in README.md and docs/*.md where an 'Add integration → X' target differs from manifest.json name, or a bold or quoted label equals a strings.json menu_options value plus… | R9 |
| D0-s2-01 | perturbation.expected_direction | down: winter mean polish gap 0.20 % -> 0.009 % measured; shipped objective lower in 7/8 winter cells (mean -0.40 %) | down | R1 |
| D5-s2-01 | perturbation.expected_direction | banner_mismatch 1 -> 0 | to_zero | R2 |
| D5-s2-01 | evidence.cpu_or_wall | n/a (count) | count | R6 |
| D9-s3-01 | perturbation.expected_direction | flagged_solve_arm 0 -> 5 (measured 5/5); null --factor 1.0 stays 0/5; positive control --arm kernel gives 5/5 | up | R2 |
| D9-s3-01 | evidence.load1 | 40.56 | 40.56 | R4 |
| D9-s3-01 | evidence.thread_factor | 1.000 | 1.0 | R4 |
| D9-s3-01 | evidence.cpu_or_wall | cpu (process_time) | cpu | R6 |
| D9-s3-01 | metric_definition | (208 chars) | (195 chars) Number of 5 sweep scenarios where any stress.py verdict fires on a solve injected with exactly 2x CPU via cpu_scaler around HeatPumpOptimizer.optimize, baseline = clean solve of same scenario in… | R9 |
| D5-s3-01 | perturbation.expected_direction | --perturb raises comment_symbols_untriaged_missing from 1 to 10 (executed); fixing the comment lowers it to 0 | up | R2 |
| D5-s3-01 | metric_definition | (225 chars) | (198 chars) Count of backticked identifiers in production .py comments/docstrings that match no identifier token in non-comment code of custom_components/, tests/, tools/ or the package json/yaml/js, excluding… | R9 |
| D1-s2-01 | perturbation.expected_direction | down to 0 (measured 5 -> 0) | to_zero | R1 |
| D1-s2-02 | perturbation.expected_direction | down to 0 (measured 4 -> 0); covered-cycle control stays 2 | to_zero | R1 |
| D1-s2-03 | perturbation.expected_direction | down (measured 4 -> 1 per arm) | down | R1 |
| D7-s2-01 | perturbation.expected_direction | freq_map_defrost_folds 8 -> 0; clean arm stays 8 | to_zero | R2 |
| D7-s1-01 | perturbation.expected_direction | keys_moved_second_class goes from 0 to 1 (executed: 1) | up | R2 |
| D7-s3-01 | perturbation.expected_direction | Cusum.reset_typed_hits 0 -> 1 (executed); namekept_no_production_call drops by 1 | up | R2 |
| D7-s3-01 | metric_definition | (201 chars) | (196 chars) Count of name-kept members with zero production-frame calls under features.py and the golden captures, and zero production attribute or getattr loads whose receiver is an instance of the member's… | R9 |
| D7-s3-02 | perturbation.expected_direction | dead_static 1 -> 0 (executed) | to_zero | R2 |
| D7-s3-02 | metric_definition | (224 chars) | (196 chars) Top-level card function declarations whose identifier occurs only at its declaration once comments are stripped (member access excluded, spread included), confirmed by 0 calls through a vm-global… | R9 |
| D12-s3-01 | perturbation.expected_direction | misdelivered_cells 2 -> 0 (measured) | to_zero | R2 |
| D12-s3-01 | evidence.cpu_or_wall | n/a (count) | count | R6 |
| D11-s1-01 | perturbation.expected_direction | escaped_heading_writes 1 -> 0 (measured) | to_zero | R2 |
| D11-s1-01 | evidence.cpu_or_wall | n/a (count) | count | R6 |
| D11-s1-01 | evidence.tolerance | 0 | 0 | R7 |
| D14-s1-01 | perturbation.expected_direction | down to 0 | to_zero | R1 |
| D14-s1-01 | evidence.tolerance | 0 | 0 | R7 |
| D14-s1-01 | step | M4 | D14.M4 | R8 |
| D14-s1-01 | metric_definition | (244 chars) | (196 chars) Calls to ThermalModel.simulate_* made outside process_worker.run_worker and off any executor thread, at the outermost kernel call, attributed to away.py, over 3 h of the synthetic-dhw-only replay… | R9 |
| D14-s2-01 | perturbation.expected_direction | mismatch 3 -> 0 | to_zero | R2 |
| D14-s2-01 | evidence.cpu_or_wall | n/a (count) | count | R6 |
| D14-s3-01 | perturbation.expected_direction | down to 0 under the fix; up to 14 under reintroduction | to_zero | R1 |
| D14-s3-01 | evidence.load1 | 16.95 | 16.95 | R4 |
| D14-s3-01 | evidence.thread_factor | 0.109 (parent only; work runs in child interpreters; no timing claim) | 0.109 | R5 |
| D14-s3-01 | evidence.cpu_or_wall | n/a (count) | count | R6 |
| D14-s3-01 | step | M4 | D14.M4 | R8 |
| D14-s3-02 | perturbation.expected_direction | down to 0 stale cycles | to_zero | R1 |
| D14-s3-02 | evidence.load1 | 58.80 | 58.8 | R4 |
| D14-s3-02 | evidence.thread_factor | 1.000 | 1.0 | R4 |
| D14-s3-02 | evidence.cpu_or_wall | n/a (count) | count | R6 |
| D14-s3-02 | step | M4 | D14.M4 | R8 |
| D11-s3-01 | perturbation.expected_direction | refused_heading_payloads rises from 2 to 3 and multiedit_refused from 0 to 1; null_refused stays 0 (observed) | up | R2 |
| D11-s3-01 | evidence.cpu_or_wall | n/a (count) | count | R6 |
| D13-s1-01 | perturbation.expected_direction | no_verdict 22 -> 23, coverage 163 -> 162 (executed) | up | R2 |
| D13-s2-01 | perturbation.expected_direction | root-cause-unanswered 37->36, blocked 124->123, outside_grammar 0->1 (observed) | down | R2 |
| D13-s2-01 | metric_definition | (205 chars) | (198 chars) Count of first-line 'Fix review: blocked <40hex> root-cause-unanswered:' verdicts across issue comments and reviews of the window's merged PRs, compared with the per-class counts of the engineering… | R9 |
| D13-s2-02 | perturbation.expected_direction | PROD head-moved row drops from 133 to 4 entries | down | R2 |
| D13-s3-01 | perturbation.expected_direction | dora_keys_loads 0 -> 1 (observed: 1, loads ['record']); FIX_IMPORT alone stays 0 with FileNotFoundError | up | R2 |
| D13-s3-01 | evidence.cpu_or_wall | n/a (count) | count | R6 |
| D13-s3-01 | title | (122 chars) | (118 chars) DORA base instrument dora_keys.py cannot run at baseline: d11lib import and exclusion-list path left behind by the R9… | R9 |
| D4-s1-01 | perturbation.expected_direction | band_max rises (5.75 -> 52.75 px); under-24 falls 30 -> 14; under-44 falls 30 -> 23 | up | R2 |
| D4-s1-01 | metric_definition | (225 chars) | (197 chars) Per pipe, the width in CSS px of the band along the pipe's normal at its midpoint over which shadowRoot.elementFromPoint returns an element whose closest [data-edge] is that pipe; counted below 24… | R9 |
| D4-s3-01 | perturbation.expected_direction | empty_state_chips 8 -> 0 (measured 0) | to_zero | R2 |
| D4-s3-02 | perturbation.expected_direction | plan ratio down below 1 (measured 0.884 at 1280, 0.889 at 1920/2560); setup seam unchanged at 1.19 | down | R3 |
| D15-s1-01 | perturbation.expected_direction | ingest_fails_unwrapped 1 -> 0, accuracy_bias_delta 0.115 -> 0.0 | to_zero | R2 |
| D15-s1-01 | evidence.load1 | 5.51 | 5.51 | R4 |
| D15-s1-01 | evidence.thread_factor | 1.000 | 1.0 | R4 |
| D15-s1-01 | evidence.cpu_or_wall | n/a (count) | count | R6 |
| D15-s1-02 | perturbation.expected_direction | replay_clean_passed_on_absent_replay 1 -> 0 | to_zero | R2 |
| D15-s1-02 | evidence.load1 | 5.51 | 5.51 | R4 |
| D15-s1-02 | evidence.thread_factor | 1.000 | 1.0 | R4 |
| D15-s1-03 | perturbation.expected_direction | ingest_fails_wrapped 6 -> 1 | down | R2 |
| D15-s1-03 | evidence.load1 | 5.51 | 5.51 | R4 |
| D15-s1-03 | evidence.thread_factor | 1.000 | 1.0 | R4 |
| D15-s1-04 | perturbation.expected_direction | bundle_credential_key_violations 1 -> 0 | to_zero | R2 |
| D15-s1-04 | evidence.load1 | 5.51 | 5.51 | R4 |
| D15-s1-04 | evidence.thread_factor | 1.000 | 1.0 | R4 |
| D15-s1-05 | perturbation.expected_direction | store_off_domain_fields 25 -> 0 | to_zero | R2 |
| D15-s1-05 | evidence.load1 | 5.51 | 5.51 | R4 |
| D15-s1-05 | evidence.thread_factor | 1.000 | 1.0 | R4 |
| ARCH-s2:D7-arch2-01 | perturbation.expected_direction | escapes 0 -> 17, mismatches 0 -> 44 | up | R2 |
| ARCH-s2:D7-arch2-02 | perturbation.expected_direction | delta_S -> 0 | to_zero | R2b |
| ARCH-s2:D7-arch2-03 | perturbation.expected_direction | delta_S -> 0 | to_zero | R2b |
| ARCH-s2:D7-arch2-04 | perturbation.expected_direction | delta_S -> 0 | to_zero | R2b |
| ARCH-s2:D7-arch2-05 | perturbation.expected_direction | delta_S -> 0 | to_zero | R2b |
| ARCH-s2:D7-arch2-06 | perturbation.expected_direction | delta_S -> 0 | to_zero | R2b |
| ARCH-s2:D7-arch2-07 | perturbation.expected_direction | implementations 5 -> 2 | down | R2 |
| ARCH-s2:D7-arch2-08 | perturbation.expected_direction | implementations 9 -> 4 | down | R2 |
| ARCH-s2:D7-arch2-09 | perturbation.expected_direction | delta_S -> 0 | to_zero | R2b |
| ARCH-s2:D7-arch2-10 | perturbation.expected_direction | implementations 35 -> 13 | down | R2 |
| ARCH-s2:D7-arch2-11 | perturbation.expected_direction | the negative-reading disagreement vanishes; 1e400 remains | (unchanged) | unresolved: no leading enum word, no numeric transition, and not exactly one direction verb |
| STUDY-reseed:D-1 | title | (124 chars) | (116 chars) _space_demand_kw uses lower_floor_heat_loss without the learned ratio: 43.7 % low on the test house; feeds the wood… | R9 |
| STUDY-reseed:D-2 | title | (124 chars) | (118 chars) sysid _zone_heat_loss and adoption_decision omit the lower-floor ratio: a perfect experiment adopts 43.7 % high (test… | R9 |
| STUDY-reseed:D-3 | title | (125 chars) | (114 chars) Lower-floor ratio has no anchor: an options edit of the lower-floor nameplate double-applies it, total kept, zone… | R9 |

92 field(s) changed, 3 left unresolved.
