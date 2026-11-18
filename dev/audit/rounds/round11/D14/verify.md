# D14 verify, round 11

Verifier for D14. Tree: worktree audit-r11-verify-D14 at handoff/audit-r11-register (28b864af6d). No D14 scope is planted, so every number below comes from that git tree. load1 was 143-158 the whole time, and thread_factor was 1.000-1.065. No vote rests on a timing number.

| id | V1 (finder harness) | perturb / null | V2 (own) | vote |
|---|---|---|---|---|
| D14-s1-01 | seams_services=12 (both bounds of 6 fields), service_number_fields=47 | --perturb-svc -> 0 | own yaml walk: 6 of 47 number selectors have min not a multiple of step (slab/upper/lower thermal mass, slab/inter-zone transfer, window_area) | verify, low |
| D14-s1-02 | seams_baseline=1, reintroduced runtime_swallowed=1 vs control 0 | moves | own AST walk: return in finally at dev/archive/handoff/r9-f2-solver-*/mutation_proof.py:224. The gate_lock.py:970/972 break/continue sit in an inner loop and do not escape the finally. files_scanned is 2038 now, the claim says 1069 | weaken, info: the live seam is in archived tooling, not production |
| D14-s1-03 | money_seams=5 of 20 | null 0, perturb 0 | coordinator.py:2880 raises a price_currency repair that admits the label mismatch (#1657). The options bounds still use resolve_currency (config_flow 619/2106/3973) | verify, medium |
| D14-s2-01 | quiet_stale_flags=6, input_problem_on=1 | perturb inf -> 0. null 0, polled 0 | const.py:1855: INPUT_ON_CHANGE_MAX_AGE_MINUTES does not override the defrost/booster flags (30 min, 1810/1826) | verify, medium |
| D14-s2-02 | wind_mismatch_hours=72/72 | covering -> 0. outdoor sibling 0 | coordinator.py:5452 reads `_weather_forecast[0]` with no time check | verify, low-medium |
| D14-s2-03 | baseline counted_exception=0, critical=0 | --widen -> 1/1 | entities.py _r10_unlatched_logs tests `attr in ("warning","error")` | verify, low (barrier gap) |
| D14-s3-01 | divergent=3 | null 0, perturb 0 | the grid-fee bound refuses a plausible HUF rule (error grid_fee_rules_implausible at bound 10 SEK) | verify, medium; duplicate of D14-s1-03 |
