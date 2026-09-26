# Round 9, D3: verifier V2 (independent), unit D3

Baseline `1936d5ca72a06556eeed4e8e5bf3dea520e517e1`. Machine: cloud box G1-V2, 4 vCPU Linux, CPython 3.14.0rc2. Standing rule (tvofi, 2026-09-26T11:37Z): no prescreen re-run, no mutant pool, no full gate; the vote rests on the seat's recorded evidence plus one fast in-memory harness of my own.

## D3-s1-01: _dhw_inlet_c lower bound (coordinator.py:1371) pinned by no check

**Vote: verify. Severity: low.**

**Finder's metric.** killed_by = scripts of coordinator.py's measured closure (minus stress/edge/backtest; env_drift --all for golden) exiting non-zero under the mutant. Recorded: 0 of 15 (`tools/audit/round9/D3/s1/logs/prescreen_C0043.log`, load1 4.16, thread_factor 1.000); null 0 (`prescreen_null.log`); counter control C0023 1 (`prescreen_C0023.log`, features.py, 6 of 3369 checks).

**My metric.** differential_inputs = number of distinct inlet readings (value, unit) that the tree's tests feed to `_dhw_inlet_c` on which C0043 returns a different value from the baseline. At 0, no assertion over those inputs can kill C0043. This bounds the finder's killed_by from the input side, and it covers the three scripts the prescreen skipped. It does not count assertions.

**Step 1 (re-run, the fast half).** `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D3/s1/behaviour.py C0043` gave behaviour_delta=1 (-5.0 -> None; DIFF_AT [1]). The same run with `--null` gave 0. load1 2.20 / 2.32, thread_factor 1.000. Both match the finder. I did not re-run `prescreen.py C0043` (about 11 min, the full closure) because the standing rule forbids it; the killed_by=0 is the seat's recorded log.

**Step 2 (own harness).** `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D3/verify-v2/inlet_census.py`:
- Static census of tests/features.py (every FakeState or `_p8_inlet_at` literal in statements that build `sensor.inlet`): ('10',°C) stale, ('12.0',None), ('unknown',°C), (10.0,°C), (10.0,None), (40.0,°C), (50.0,°F). census_size=7. This matches the finder's mechanism text.
- tests/config_flow_steps.py, the only other test script that names `CONF_DHW_INLET_ENTITY`: 0 dicts keyed `sensor.dhw_inlet` carry a state, and 0 FakeState lines name the inlet. It configures the slot but never feeds a reading.
- **differential_inputs=0**; positive control, with (-5.0,°C) and (23.0,°F) added: 2; null control (baseline vs baseline recompiled): 0.
- flip_points_on_0.01C_grid=1 over -10..40 °C: the mutant differs only at exactly -5.0.
- load1 4.08, thread_factor 1.000. Counts are contention-immune.
- An in-process `--dynamic` run of config_flow_steps.py under a recorder hit the 170 s timeout, over the 2-minute cap. It is off by default and no number from it is used.

**Step 3 attacks, in order.**
1. Contention: both metrics are counts, and the finder's run is at load1 4.16. No effect.
2. Gate mode: the finder ran `env_drift.py --all` (in the prescreen log's CLOSURE). A grep of `tests/golden/coord_*.json` shows each of the 5 coordinator goldens carries `dhw_inlet_temperature: 10.0` (the seasonal default) and no live inlet entity. `config_flow.json` exercises the flow only. So --all cannot observe the bound.
   - The quiet-window `GATE_SCOPE=full` run (D3.md step 3) was not run by the seat (its Unfinished list says so), and not by me (the standing rule).
   - Statically, stress.py, edge.py and backtest.py contain no `inlet`/`dhw_inlet` token (grep). Only features.py and config_flow_steps.py name the inlet entity key, and only features.py references `_dhw_inlet_c`. The full gate therefore has no additional input that can reach the bound. This outcome is inferred from grep; no full gate was executed.
3. Grid artefact: not applicable, since the finding is one mutant.
4. Null control: present, and re-run at 0 (behaviour.py --null; my null_control=0).
5. Reachability in real HA: the single call site is coordinator.py:2571 (`_prepare_dhw_inputs`, from `CONF_DHW_INLET_ENTITY`), reached with a real sensor state. A reading of exactly -5.0 °C (or 23 °F) is reachable but physically implausible for liquid inlet water. Under the mutant, that reading degrades to the seasonal model instead of being used.
6. Severity: the behaviour change is one point, and it gives the configured no-sensor fallback. `low` (hygiene) is the floor and is earned. No weaken.

Context, not a refute: `tests/mutation_ledger/killed_by/coordinator.py/` records BOOLOP, GUARD_OFF and RETURN_DEL on `_dhw_inlet_c` as killed by features.py. The ledger's operator set on this module (BOOLOP 6, GUARD_OFF 15, RETURN_DEL 12, CLAMP_DROP 1) has no comparison-bound operator, and `survivor_triage/` has no entry for this function. The census also has no reading at 35.0, so the symmetric upper-bound mutant (`value <= 35.0` -> `value < 35.0`) is equally undistinguished by any test input. That is deduced from the census and was not run.

**Step 4 (single-line production mutation).** `custom_components/heatpump_optimizer/coordinator.py:1371`, `-5.0 <= value` -> `-5.0 < value`: the seat's recorded mutant C0043, killed_by=0 of 15 in `prescreen_C0043.log`. No test file edit is involved.

**Metric line.** differential_inputs = distinct test-supplied inlet readings on which C0043 changes `_dhw_inlet_c`'s return value; measured 0 (positive control 2, null 0).

## Harnesses
- `tools/audit/round9/D3/verify-v2/inlet_census.py`
