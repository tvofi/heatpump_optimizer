# Round 9, D3: verifier V1 (reproduce), unit D3

Environment: CPython 3.14.0rc2, numpy 2.4.6, scipy 1.17.1. Evidence tree 6f51db2c (branch handoff/audit-r9-verify-g1-v1, baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1). Machine: 4 vCPU cloud container (box G1-V1), Linux 6.18, shared with two other sub-seats (load1 2.5 to 3.1, thread_factor 1.000). All numbers below are counts, so contention does not affect them.

tvofi's rule (2026-09-26T11:37Z) applies: I did not re-run the mutation pre-screen, any mutant pool, or any full-gate mutant confirmation. prescreen.py was not re-run, so the kill count comes from the D3-s1 seat's recorded logs. Quiet window not run (tvofi rule).

## D3-s1-01: no closure script kills C0043 (`_dhw_inlet_c`, coordinator.py:1371, `-5.0 <= value` -> `-5.0 < value`)

**Vote: verify. Severity: low (agreed).**

**Numbers**
- Recorded killed_by = 0 of 15. Read from tools/audit/round9/D3/s1/logs/prescreen_C0043.log: every script has rc=0, including env_drift.py (--all) and features.py; load1 4.16.
- Recorded null run: killed_by = 0 (prescreen_null.log).
- Recorded C0023 control: killed_by = 1, by features.py, with 6 checks failing (prescreen_C0023.log). This shows the counter moves.
- The applied diff in the C0043 log is exactly the one-line change the finding names.

**Executed (cheap, in memory)**
1. The production line exists as stated. coordinator.py:1371 reads `return value if value is not None and -5.0 <= value <= 35.0 else None`.
2. `behaviour.py C0043` re-run: behaviour_delta=1. The baseline returns -5.0 and the mutant returns None; the other six probes do not differ (load1 2.53). `behaviour.py C0043 --null`: behaviour_delta=0 (load1 2.65). The perturbation moves in the stated direction (up) and the null control holds.
3. My own harness, tools/audit/round9/D3/verify-v1/inlet_probe_domain.py. It builds the mutant in memory by an exact one-occurrence string replacement of the function source, then runs it on every inlet reading the suite feeds `_dhw_inlet_c`:
   - features.py ~18850: 12.0 fresh and 12.0 frozen for 48 h.
   - features.py ~45236-45305: 50 °F, 10 °C, 10 with no unit, a stale 10 °C, 40 °C and "unknown".

   Results: suite_inputs_differing = 0; suite_numeric_inputs_at_or_below_bound = 0; boundary_inputs_differing = 2 (-5.0 °C and 23 °F, which is exactly -5 °C, both become None). With --null, both counts are 0.

**Attacks run**
- **Contention:** the metric is a count, so contention does not apply. The recorded load1 is 4.16 and my load1 is about 3.
- **Wrong gate mode:** the recorded pre-screen replaced golden.py with `env_drift.py --all` against the baseline, and it stayed rc=0. So this is not a default-5-fixture artefact. It also cannot be one: all five coordinator goldens carry only a static `dhw_inlet_temperature: 10.0` and configure no live inlet entity.
- **Other reach:** entities.py has only a static 8.5; config_flow_steps.py names `sensor.dhw_inlet` in config data only and sets no state.
- **Equivalent mutant:** refuted. The behaviour delta is 1 in behaviour.py and 2 in my harness, so production output changes at the bound.
- **Existing coverage and triage:** tests/mutation_ledger/killed_by records BOOLOP, RETURN_DEL and GUARD_OFF on this function, all killed by features.py. No CMP_BOUND on line 1371 is recorded as killed. Nothing under survivor_triage/ names `_dhw_inlet_c`, so the gap is not already dispositioned.
- **Test-gap rule (verifier.md step 4):** the unnoticed single-line mutation is in the production file custom_components/heatpump_optimizer/coordinator.py, line 1371. The gap stands.
- **Leave-one-out:** not applicable, because there is no aggregate.
- **Severity:** a -5.0 °C reading exactly at the bound is an edge case. The mutant changes one boundary value, which then falls back to the seasonal model. Low is earned, and I would not go lower.

**Limit of the evidence:** the claim that the whole 15-script closure is green rests on the seat's recorded log, not on a re-run. That log is internally consistent: the correct diff is applied, all rc values are 0, and the null and control runs behave as expected. My executed number independently shows that no suite input reaches the bound.

**Metric:** suite_inputs_differing = the number of suite-fed inlet readings on which the mutant's return value differs from the baseline's (0 means no check can observe the mutant).
