## D3 sanity checks (judge, by hand, at 79aa98e tree; tvofi 13:41Z rule)
Light check only: mutant applied in memory / in a temp package copy, production symbol called directly.
Kill-count (survival) half rests on recorded evidence + votes; quiet window not run (tvofi rule).

| finding | sev in | check run | result | null |
|---|---|---|---|---|
| D3-s1-01 | low | behaviour.py C0043 | behaviour_delta=1 | --null 0 |
| D3-s1-91 | medium | lc_tz_probe_coordinator.py | 8384 differs: HASTUB_TZ unset 0, Stockholm 1 | unset arm is the null |
| D3-s2-01 | medium(split) | witness.py S05 S17 S18 M31 | S05 1/3 corrupt diverge; S17 12/288, S18 3/288 zero-priced; M31 6/6 non-inert restores, 1/6 fold raises | orig arms 0/288; in-domain 0 |
| D3-s2-02 | low | witness.py S19 | sigma nonzero 96/96 orig, 0/96 mutant; in-domain 10/10 | orig arm |
| D3-s3-01 | medium | distinguish.py M02 (TZ=Europe/Stockholm) | differs=1 (00:00 -> 23:00 prev day) | --tz=UTC 0; --identity 0 |
| D3-s3-02 | medium | distinguish.py M19 | 1.5 -> 0.0 kWh, differs=1 | --identity 0 |
| D3-s3-03 | medium | distinguish.py M21 | months kept 1 -> 0, kwh nan, differs=1 | --identity 0 |
| D3-s3-04 | medium | distinguish.py M24 | 0.0 -> 0.4396 kWh folded, differs=1 | --identity 0 |
| D3-s3-05 | low | distinguish.py M20 | 0 -> 5 deletes, differs=1 | --identity 0 |
All ran under 2 s each; tree clean after.

## Quiet re-takes by the judge (batch B rows J.md step 4 names provisional)
| finding | command | result |
|---|---|---|
| D9-s2-71 | l3_valve_solve.py / --perturb novalve (load1 0.48 / 0.66) | stress_sweep_valve_cases 0 of 51 both arms; valve step-equivalents max 9,426,048 -> 5,439,456; controls 3,507,029..4,219,488 unchanged exactly |
| D9-s2-01 | loop_work.py / --options all-candidates null (load1 0.31 / 0.47) | 384 simulate steps per read, advisor_share_of_loop 0.3306; null 0 and 0.0011 |
