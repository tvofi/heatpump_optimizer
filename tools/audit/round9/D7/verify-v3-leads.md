# D7 — verify-v3-leads (V3: reach and class)

## D7-s3-51 — nightly_ha._async_check_a4 returns inside finally, swallowing an in-flight exception

**Executed numbers.** Re-ran `tools/audit/round9/D7/leads/nightly_finally_return.py`: baseline `swallowed=2 of_2`, `syntax_warnings=1`; `--fixed`: `0`/`0`. Exact match. load1 1.15, thread_factor 1.000.

**Independent measurement.** Wrote `tools/audit/round9/D7/verify-v3-leads/v3_finally_return_seam_sweep.py` to attack the finder's own seam_rule, which is a *non-recursive* `glob.glob('tests/*.py')` — a pattern `tools/audit/README.md` names as a known trap ("a script in a subdirectory is invisible"). A naive hand-rolled AST walk (checking for `Return`/`Break`/`Continue` anywhere inside a `Try` node's `finalbody`) over-counted, flagging `tests/gate_lock.py:433` and `:435` as extra sites. Cross-checked directly with `python3 -W error::SyntaxWarning -c "py_compile.compile('tests/gate_lock.py', doraise=True)"`, which returned `ok` — no warning. Reading the code: those are a `break`/`continue` scoped to their *own* nested `for` loop entirely inside the finally block, which does not escape the finally and so does not swallow anything; CPython's compiler (which understands loop scoping) correctly does not warn. Rewrote the harness to use CPython 3.14's own `compile()`-time `SyntaxWarning` (the actual PEP 765 check) recursively over `tests/`, `custom_components/`, and `tools/`: result is exactly one site tree-wide (`tests/nightly_ha.py: 'return' in a 'finally' block`), and it sits at `tests/` top level, so the finder's non-recursive command already covers it (`covered_by_top_level_glob=1`).

**Attacks.** Reachability: `tests/nightly_ha.py` is not `custom_components` production code, but `tests/ha_contract.py`'s own docstring states this exact file is run, unmodified, against real, container-installed Home Assistant in the nightly lane (`#521`) — so the swallow is reachable in real HA, in the audit's own instrument. Per `tools/audit/README.md`'s "a defect in an instrument is a finding" rule, this is a legitimate D7 finding, not void for being test tooling. No gate-mode, grid, or contention concerns apply to this count metric. Consequence: an interrupted nightly run (cancellation, timeout) is recorded as an ordinary A4 check failure instead of aborting, which can send a later seat chasing a phantom regression — bounded to the nightly informational lane (not a PR merge gate), so low stands.

**Class.** `new` confirmed — no existing `bugclasses.json` entry fits precisely (closest in spirit to `I1`'s "a guard whose deletion leaves the gate green," but this is a swallow inside the harness's own control flow, not a mutation-kill miscount).

**Metric definition.** Of 2 arms (`CancelledError`, `KeyboardInterrupt` from the first refresh, recovery refresh then raising), arms where `_async_check_a4` returns instead of propagating; plus `SyntaxWarnings` on compile.

**Vote: verify.** Severity low, class new, seam_rule_enumerates true (corrected assessment: the stated non-recursive command happens to already cover the sole tree-wide site).

## D7-s1-71 — cold-water inlet default held three ways

**Executed numbers.** Re-ran `tools/audit/round9/D7/leads/l3_cold_water_default.py`: baseline `sites_not_following=3 of 5`; `--perturb literal`: `1 of 5`; `--no-move`: `sites_disagreeing=0 of 5`. Exact match. load1 1.19-1.46, thread_factor 1.000.

**Independent measurement.** Wrote `tools/audit/round9/D7/verify-v3-leads/v3_cold_water_default_recheck.py`: confirmed the 3 spellings (`dhw_inlet_temp: float = 10.0` bare literal in `thermal_model.py`; `DEFAULT_DHW_INLET_TEMP` in `const.py`/`config_flow.py`; `DHW_COLD_WATER_TEMP` as `dhw_coil_draw_reduction`'s own default argument) by direct source read across the four relevant files, and independently enumerated every `dhw_coil_draw_reduction(...)` call site in `optimizer.py` and `thermal_model.py` (found by bracket-matching, skipping the `def`): `coil_callers=3`, `coil_callers_passing_inlet=3`, `coil_callers_omitting=0`.

**Attacks.** Reachability: bare `ThermalParameters()` is reached through `sysid.py:_sizing_model` (production call sites at `sysid.py:276` and `:1203`, part of the real plant-identification path) — not test-only. The third site, `dhw_coil_draw_reduction`'s own default argument, is confirmed never actually reached today: all 3 production call sites (`optimizer.py:3397`, `optimizer.py:4571`, `thermal_model.py:3155`) pass `inlet_temp` explicitly. This matches the finder's own null control ("no user-visible divergence today") exactly — an honestly scoped hygiene finding, not an inflated live-divergence claim.

**Class.** `new` confirmed — no exact `bugclasses.json` fit (nearest kin is `P8`'s "divergent precedence" pattern, but `P8` is scoped to currency/unit resolution specifically, not a temperature default).

**Metric definition.** Of 5 production sites resolving a cold-water inlet default, those whose delivered value does not move when `const.DEFAULT_DHW_INLET_TEMP` is moved 10.0 -> 12.5.

**Vote: verify.** Severity low, class new, seam_rule_enumerates true.

## D7-s3-72 — 4 of 5 ThermalModel per-step scratch members write-only

**Executed numbers.** Re-ran `tools/audit/round9/D7/leads/l3_write_only_scratch.py`: baseline `write_only_members=4 of 5`, `live_control_buffer_consumer_reads=97344`; `--perturb reader`: `3 of 5`. Exact match. load1 1.88-2.15, thread_factor 1.000.

**Independent measurement.** Wrote `tools/audit/round9/D7/verify-v3-leads/v3_write_only_scratch_static_recheck.py`: a *static*, tree-wide grep across all of `custom_components/` (not the finder's dynamic 4-golden-solve descriptor trace) for external references to each of the 4 named members. Result: `external_refs=0` for all 4, matching the dynamic trace. Also scanned `thermal_model.py` itself for any `self.<member>` appearance that is a read (not a plain assignment target): found one, `thermal_model.py:2399`, `wood_refused += self._step_wood_refused`, inside `simulate_step`'s multi-substep averaging.

**Attacks.** Reachability: all four members are written inside `simulate_dhw_step` / `_simulate_step_two_zone`, which run on every real solve — production, not test-only. The one self-read the static check found fires only when a stability substep split (`n_sub>1`) triggers, which none of the finder's 4 traced golden solves (`winter_single_dhw`, `dhw_cold_tank`, `wood_two_tank`, `wood_coil`) hit, so the finder's `self_reads=0` is an accurate count of the *traced* scenarios, not a static absence — and since `simulate_step` is already listed as a writer of `_step_wood_refused`, this read is a "self_read" under the finder's own taxonomy, never a "consumer_read," so it does not change the write-only-to-external-consumers verdict. Marking `seam_rule_enumerates` as `partial`: the finder's method (a dynamic trace over 4 named scenarios) does not statically enumerate every code path (e.g., the substep branch), even though the conclusion it reaches for those 4 scenarios is confirmed correct. Severity: dead bookkeeping with a bounded CPU cost, no wrong output — hygiene/low earned.

**Class.** `new` confirmed — no exact fit (closest conceptually to the *inverse* of `P6`, which is about a consumer reading a key no producer writes; here it's a producer writing a key no consumer reads).

**Metric definition.** ThermalModel `_step_*` members with >=1 production write and 0 reads from production functions that never write that member, over four golden solves.

**Vote: verify.** Severity low, class new, seam_rule_enumerates partial (see attack above).
