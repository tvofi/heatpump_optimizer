# Round 10 judge

Judge seat, serial, under the gate_lock lease judge-r10. Input: JUDGE-INPUT.json (66 canonical after dedup; D11-s3-01 merged into D11-s1-01, D14-s2-01 into D14-s3-01). Scripted batch: judge-batch-1.md; every row flagged by-hand, void, re-take or rc!=0 was re-run by hand (load1 3.8-6.2 during the hand runs).

Tally: weakened 6, verified 51, unreproduced 9.

Batch void rows overturned: D1-s2-02, D12-s2-71, D2-s1-71, D2-s3-73, D14-s1-01, D7-s2-01, D7-s3-51, D13-s2-02 -- in each the batch keyed on a control or scenario count that cannot move by design, or ran a perturbation other than the stated one. Void upheld: D7-s2-61.

Unreproduced (not killed, not passed; the round is not dry until re-measured): D4-s1-01, D4-s3-01, D4-s3-02 (no browser on this box), D15-s1-01..05 (the owner bundle is not in the tree), D7-s2-61 (void harness).

New classes: N-registry-leak (nearest N-shared-config); N-future-clamp (nearest N-future-instant); N-no-expiry (nearest N-staleness); N-log-flood (nearest N-silent-zero); N-period-rollover (nearest P7); N-confounded-learner (nearest P5); N-move-stale-path (nearest I5); N-gate-yield (nearest I3). N-no-expiry and N-log-flood were placed against different nearest classes on purpose.

| id | verdict | sev | class | value | note |
|---|---|---|---|---|---|
| D0-s1-01 | weakened | low | P4 | 26 of 80 cells gap_rel>1e-3, max 5.06e-2; drop-most-favourable 1.39e-3; flat null 4.98e-3 | Reproduced 26/80 (load1 6.18, tf 1.000). Perturbation on tz1 winter_typical/winter_cold maxiter 20 gives 5.80e-3 vs 3.99e-3 claimed baseline: moved up. Batch void row ran the perturbation over the whole grid with a different metric; not comparable. Null control: gap survives flat prices, so it is a solver basin gap, not money; LOO drops it to 1.4e-3. Panel contested; weakened to low on LOO. |
| D0-s2-01 | verified | low | P4 | polish_gap_winter_mean 0.2025 % (max 1.2344, drop-max 0.0551) | Reproduced exactly (load1 4.76, tf 1.000); --ftol 1e-10 drops it to 0.0088 %: moved down. Flat-price cell carries 0.1573 %, so gap is objective, not price. |
| D1-s1-01 | verified | medium | N-registry-leak | 5 torn coordinators alive of 5 | Reproduced 5/5 (load1 4.37, tf 1.053 retaken 1.056; counts contention-immune). --perturb pops _STATES: 5 -> 0. |
| D1-s1-02 | weakened | medium | N-shared-config | torn_midsolve_total 1 of 2 cells (claimed 2 of 2) | Re-run gives torn_midsolve_total=1, cells=2, null 0 (load1 4.61, tf 1.070; retaken 1.075, same count). --perturb: 1 -> 0. Mechanism holds; number is half the claim. |
| D1-s2-01 | verified | low | N-future-clamp | 5 instants rewritten, 5 WARNINGs | Reproduced 5 (tf 1.223, retaken 1.247 - deterministic count). --perturb: 5 -> 0; control accuracy store 0. |
| D1-s2-02 | verified | high | N-no-expiry | 4 of 4 uncovered cycles publish and book a finite stale price | Reproduced (tf 1.154/1.160, deterministic). --perturb: published 4 -> 0, booked 4 -> 0, covered control stays 2. Batch void row keyed on uncovered_cycles, the scenario count, which is not the finding metric. |
| D1-s2-03 | verified | low | N-log-flood | 4 WARNING records over 4 cycles per arm | Reproduced 4 (tf 1.156); --perturb latch: 4 -> 1 per arm; control 0. Panel contested on severity only; hygiene. |
| D1-s3-01 | verified | medium | N-silent-zero | empty_ok_wipes=1 | Reproduced (load1 4.51, tf 1.000); --perturb 1 -> 0. |
| D1-s3-02 | weakened | low | P1 | 95 of 96 startless rows misplaced | Reproduced 95/96; --perturb 95 -> 0. Requires a malformed Tibber response no observed feed sends; weakened to low. |
| D10-s1-51 | verified | low | P2 | actions_silent_on_bogus_entry=1 | Scripted batch reproduced 1 (expected 1), perturbation 1 -> 0, tf 1.000. |
| D11-s1-01 | verified | low | I3 | escaped_heading_writes=1 (with D11-s3-01 merged) | Batch: 1 -> 0 under --perturb, tf 1.000. D11-s3-01 merged in at dedup. |
| D11-s1-51 | verified | low | I5 | lint_missed_stale_counts=1, retired_key_claims=3 | Re-run by hand (batch rc=2 was cwd): 1 and 3; --perturb 1 -> 0. |
| D12-s3-01 | verified | high | P8 | 2 of 6 cells misdelivered on degF; degC null 0 of 6 | Batch reproduced 2 (expected 2), --perturb 2 -> 0, tf 1.000. |
| D12-s2-71 | verified | medium | P3 | upper -36.8 %, lower +21.5 % after options reseed; house within 0.11 % | Re-run: upper_rel_err 0.3681, lower 0.2145, house 0.0011 (load1 4.47, tf 1.000); --ratio 1.0 drives all to 0. Batch void row read model_rollout diff, which is 0 by design in both arms. |
| D13-s1-01 | weakened | low | I3 | 23 of 197 merges with no parsable verdict (window grew from 185) | Re-run with token: verdict_prs 174 of 197; --reshape-one 174 -> 173, outside_grammar 0 -> 1. The 17-of-22 unexempted split was not re-derived. Process-yield observation; hygiene. |
| D13-s2-01 | weakened | medium | N-gate-yield | root-cause-unanswered 37 of 124 blocked verdicts (29.8 %) | Reproduced 37/124; --perturb=verdict 124 -> 123, 37 -> 36. A share of blocks is a cost observation, not a defect: weakened from high, hygiene. |
| D13-s2-02 | verified | medium | I4 | PROD head-moved row 133 entries vs 4 blocked head-moved verdicts | Reproduced 133 vs 4. Stated perturbation (comment out policy_lint.mjs:2850 reverify bump, restored after) drops the row to 4. Batch void row ran a different --perturb. |
| D13-s3-01 | verified | medium | N-move-stale-path | dora_keys_loads=0 (ModuleNotFoundError d11lib) | Reproduced 0; with D13S3_FIX_IMPORT and the registered exclusions path, 0 -> 1. Run created an untracked cache dir, removed. |
| D13-s2-51 | verified | low | I4 | 34 of 34 moved corpus files split | Re-run by hand from repo root: 34; --perturb split_keys_perturbed 0, plumbing-only 34. |
| D14-s1-01 | verified | low | P10 | 183 loop kernel calls over 6 cycles (30.5/cycle) | Re-run: loop_kernels_away_seam 183 (tf 1.016); --deficit 0: 0. Batch void row read static_seams, a site count that cannot move. |
| D14-s3-01 | verified | medium | P8 | 1 of 14 money seams mismatched; narrative_fixed 0; reintroduce 14 | Re-run: base 1, clean 0, narrative_fixed 0, reintroduce 14 (D14-s2-01 merged). tf printed 0.074 (idle harness thread), counts deterministic. |
| D14-s3-02 | verified | medium | N-staleness | power 39 stale of 48 cycles, 78 newly-unavailable entity-cycles; mode 47; polling 0 | Reproduced exactly; unbounded max-age arm 0 and 0. |
| D15-s1-01 | unreproduced | medium | I4 | not measured | Needs the owner diagnostics download the finder read in place; not in the tree, and the synthetic generator output failed to load. Not killed, not passed. |
| D15-s1-02 | unreproduced | low | N-silent-zero | not measured | As D15-s1-01: bundle unavailable. |
| D15-s1-03 | unreproduced | low | I4 | not measured | As D15-s1-01: bundle unavailable. |
| D15-s1-04 | unreproduced | low | I4 | not measured | As D15-s1-01: synthetic bundle arm did not load. |
| D15-s1-05 | unreproduced | medium | P6 | not measured | As D15-s1-01: bundle unavailable. |
| D2-s2-01 | verified | low | P2 | dhw_mode_ratio_max 1.4346 at (7 C, 65 C) | Reproduced; --perturb single law: 1.0000. Panel contested on physics; the ratio is the same tank lift priced by two laws. |
| D2-s3-01 | verified | medium | N-period-rollover | last_window_reached 0 of 24 | Reproduced 0/24; --perturb close before reset: 24/24, billed spike 1 -> 5 kW. |
| D2-s3-71 | verified | medium | N-confounded-learner | UA bias slope +0.094..+0.254 per unit aperture error, n=6; LOO +0.161..+0.254 | Re-run run_q1 + collect: slopes P0 .180 P1 .254 P2 .094 P3 .221 P4 .161 P5 .191; night-only spread <=0.0001 (perturbation moved); flat-irradiance arm spread 0. |
| D2-s3-72 | verified | high | P5 | vent trips 17.2-18.7 % of intervals at delivery 0.4, 0 at 1.0 | Re-run: vent(fix1) 0.187 (P0) and 0.172 (P1) at g0.40, 0.000 at g1.00 on all plants. |
| D2-s1-71 | verified | medium | P3 | space demand 43.7 % low (7.741 vs 11.122 kW) | Same harness as D12-s2-71: space_demand_rel_diff 0.4367; --ratio 1.0: 0. |
| D2-s3-73 | verified | medium | P3 | sysid adopts 614.6 W/K for a 427.8 fit (43.7 % high) | Same harness: sysid_adopt_effective_rel_err_A 0.4367, B 0; --ratio 1.0: 0. |
| D3-s1-01 | verified | medium | I1 | prior_kept 1 baseline, 0 under the and->or mutant | Re-run: 1 -> 0 (fabricated 0 -> 1). Suite-arm M08 survival taken from the finder; not re-run. |
| D3-s1-02 | verified | low | I1 | live_guards 12 of 12 | Re-run: 12; --equal: 0. |
| D3-s2-01 | verified | low | I1 | loaders_correct 2 of 2, 0 under negation; tests naming the WARNING 0 | Re-run: 2 -> 0 under --mutate. |
| D4-s1-01 | unreproduced | medium | P9 | not measured | No Playwright/Chromium on this box (batch rc=1, pinned cache path absent). Not killed, not passed. |
| D4-s3-01 | unreproduced | low | P9 | not measured | As D4-s1-01. |
| D4-s3-02 | unreproduced | low | P9 | not measured | As D4-s1-01; panel contested. |
| D5-s1-01 | verified | low | I5 | 5 mismatched UI labels | Batch: 5 -> 1 under --perturb, tf 1.000. |
| D5-s2-01 | verified | low | I5 | banner_mismatch 1 | Batch: 1 -> 0, tf 1.000. |
| D5-s3-01 | verified | low | I5 | 1 untriaged missing comment symbol | Batch: 1 -> 10 up under --perturb, tf 1.000. |
| D5-s3-51 | verified | low | I5 | 4 stale count statements; 13 registered | Batch: registered 13 -> 14 under --perturb, tf 1.000. |
| D7-s1-01 | verified | low | N-structure-blind | 1201 lines added move 0 of 16 budget keys (second-class arm) | Re-run 1201/0; with max_class_loc summed in an edited copy of structure.py: 0 -> 1. |
| D7-s1-51 | verified | medium | N-shared-config | delta_S +6.5186 | Batch: +6.5186 -> 0 under --revert, tf 1.000. |
| D7-s1-52 | verified | low | N-shared-config | delta_S +2.3771 | Batch: +2.3771 -> 0, tf 1.000. Panel contested; number holds. |
| D7-s1-53 | verified | low | N-shared-config | delta_S +1.5020 | Batch: +1.5020 -> 0, tf 1.000. Panel contested; number holds. |
| D7-s2-01 | verified | low | P2 | 8 FrequencyMap folds over 8 defrost intervals | Re-run: freq_map_defrost_folds 8 -> 0 under --perturb; clean arm stays 8. Batch void row read the clean arm. |
| D7-s2-51 | weakened | low | P2 | escapes 0 at baseline; 17 only under patch 01 without 00 | Re-run: 0 at baseline, 17 with 01. No published property escapes today; latent hazard for a mixin refactor, weakened to hygiene. |
| D7-s2-52 | verified | low | P2 | delta_S +2.6888, copies 68 -> 55 | run_findings 01_value: +2.6888; perturbed 0. |
| D7-s2-53 | verified | low | P2 | delta_S +0.9689, 68 -> 63 | run_findings 02_path: 68 -> 63; perturbed 0. |
| D7-s2-54 | verified | low | P2 | delta_S +0.3789, 68 -> 66 | run_findings 03_zone reproduced; perturbed 0. |
| D7-s2-55 | verified | low | P2 | delta_S +0.1880, 68 -> 67 | run_findings 04_suggested reproduced; perturbed 0. |
| D7-s2-56 | verified | low | P2 | delta_S +1.1717, 68 -> 62 | run_findings 08_page reproduced; perturbed 0. |
| D7-s2-57 | verified | low | P2 | 5 implementations, 2 disagreeing hours | Re-run 5; --patch 05: 2. |
| D7-s2-58 | verified | low | P3 | 9 implementations, 10 of 17 inputs disagree | Re-run 9; --patch 06: 4. |
| D7-s2-59 | verified | low | P2 | 522 tokens, 0 mismatches; --break 487 | Re-run exact; equivalence harness moves under --break. |
| D7-s2-60 | verified | low | P6 | 35 implementations, 5 distinct answer vectors, 3 disagreeing probes | Re-run 35; patches 00+01+02: 13. |
| D7-s2-61 | unreproduced | low | P3 | 4 implementations, 3 disagreeing states; --sign-blind leaves 3 | Perturbation does not move: disagreeing states stay -0.4kW, 0kW, 1e400kW under --sign-blind. Harness void. |
| D7-s3-01 | verified | low | N-structure-blind | 6 dead members with 0 typed hits | Re-run 6/0; injected production call: typed hits 0 -> 1. Panel contested; number holds. |
| D7-s3-02 | verified | low | N-structure-blind | 1 dead card function (textWidth, 0 calls) | Re-run; HPO_SENT_INJECT=1: 1 -> 0. |
| D7-s3-51 | verified | low | N-structure-blind | 10 AwayView keys blind to the census (166 of 169) | Re-run blind_keys 10; patch arch3-01 applied and reverted: 10 -> 0. Batch void row read census_keys. |
| D7-s3-52 | verified | low | N-structure-blind | 4 Any spellings read 0 of 6 keys untyped | Re-run 0 for the 4 spellings; patch arch3-02: 6 for all four. |
| D7-s3-53 | verified | low | N-name-sort | invented family: 0 orphans at baseline | Re-run 0; patch arch3-03: game orphan overrides 0 -> 2. |
| D7-s3-54 | verified | low | N-shared-config | 578917 wrong reads of 1808075 (32 %; finder 437525/1419348, 31 %) | Absolute counts scale with workload; share reproduces. Null idle-writer arm 0; patch arch3-04: 0. |
| D8-s1-01 | verified | low | P2 | 1 of 36 snapshots publishes heating now on an off step | Re-run 1; --perturb 1 -> 0. |
