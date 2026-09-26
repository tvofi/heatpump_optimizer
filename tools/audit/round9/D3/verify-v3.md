# Round 9 verify, D3, lens V3 (reach and class), box G1-V3

Baseline 1936d5ca. No heavy D3 re-run under tvofi's rule: no mutation pre-screen, no pool, no full-gate confirmation. Quiet window not run (tvofi rule).

## D3-s1-01: No closure script fails when _dhw_inlet_c's lower plausibility bound moves

**Harness re-run (step 1).** `prescreen.py C0043` was not re-run: about 11 min, a heavy D3 mutation run. The seat's recorded mutant and log are cited instead. C0043 changes coordinator.py:1371 from `-5.0 <= value` to `-5.0 < value`. `logs/prescreen_C0043.log` reads scripts_run=15, killed_by=0, KILLERS -, load1=4.16, thread_factor=1.000. The cheap behaviour harness was re-run: `behaviour.py C0043` gives behaviour_delta=1 (BASE -5.0, MUT None at index 1), and `--null` gives 0 (load1 2.08/2.15, thread_factor 1.000). Matches the finder exactly.

**Own measurement (step 2).** Harness: `tools/audit/round9/D3/verify-v3/D3-s1-01_reach.py`, on real HA 2026.2.3 (/root/venvha, no hastub) with genuine `homeassistant.core.State` readings; C0043 applied in memory through mock.patch.object.
- Metric: reach_delta = number of 7 readings (-5.1, -5.0, -4.9, 12.0, 35.0, 35.1 degC; 23 degF) on which the return repr differs between the mutant and the baseline.
- Result: reach_delta=2. Both -5.0 degC and 23 degF (exactly -5.0 degC) move from -5.0 to None. `--null` gives 0. load1 2.59/3.02, thread_factor 0.994/0.983.
- The finder's metric counts killing scripts; this one counts output deltas on real HA. Complementary, not the same quantity.
- Environment shim, not production: HA's mashumaro imports `typing.ByteString`, which CPython 3.14.0rc2 removed; the harness shims it before import.

**Attacks (step 3).**
- **Contention.** The kill count is not a timing number.
- **Gate mode.** The prescreen ran env_drift.py --all, and the mutant stayed green. Holds.
- **Closure.** tests/closures.json has 16 scripts whose closure includes coordinator.py. Swapping golden.py for env_drift --all gives the finder's 15. stress/edge/backtest are outside that closure and contain 0 references to `inlet`.
- **Test text.** The features.py inlet checks (`_p8_inlet_at`) probe 50 degF, 10 degC, 40.0 degC, a stale reading and 'unknown'. None probes at -5.0, below it, or at 35.0.
- **Null control.** Present in both harnesses; 0 in both.

**Reach in real HA.** Reachable. coordinator.py:2571 calls `_dhw_inlet_c` whenever CONF_DHW_INLET_ENTITY is configured. The real-HA State path reproduces the mutant's behaviour change on HA 2026.2.3; the production target may be newer.

**Severity.** low (hygiene). The mutant changes one exact reading, -5.0 degC, physically implausible for liquid mains water. The consequence is a fallback to `seasonal_inlet_temp` (coordinator.py:2572-2573), not a wrong published value.

**Test-gap line (step 4).** The single production line coordinator.py:1371, `-5.0 <= value` -> `-5.0 < value`, in custom_components/heatpump_optimizer/coordinator.py. No test-file mutation is involved.

**Seam rule.** `mutants.py --list | grep '"func": "_dhw_inlet_c"'` returns C0041-C0045. Partial: a listing, not a kill check, with no constant shift on -5.0 and no drop of the lower conjunct alone. Pushing each seam through prescreen.py is the forbidden heavy run, so it was not executed.

**Class.** I1 (a guard whose deletion leaves the gate green), confirmed.

**Vote.** verify, low.
