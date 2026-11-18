I found 11 findings in my cells. All prototypes together read **delta_S = +7.0226** with every counter on, which is 114 % of the cells' 30 % target (6.138). Every move is admissible, `duplication_copies` falls 68 → 39, and no gate-only tripwire rises. Reverting the combined patch gives back the baseline vector exactly (perturbed delta_S +0.0000).

Baseline: `554e2ecfa7ad5b1660a1256ebf6cf6ac3810d9ef`. I pushed only `handoff/audit-r10-arch-s2` (`01d9d0be22d53b90f746a63079a34fa383bd8514`), with no PR and no GitHub API writes.

**REPORT.md is not committed.** The harness refused the file with "Subagents should return findings as text, not write report files". The report content is in this reply; the handoff holds the harnesses and patches only.

**Target.** The weights are 8.928 for duplication and 1.0 for each of the other three cells, so Σw = 11.928 and 0.5146 · Σw = 6.138. All of it comes from `duplication_copies`:
- **`dead_members` (1) and `public_unused` (1)** are the same symbol, `const.ENTITY_FAMILY_OVERRIDES`. Production never reads it, but ARCH-s3's `family_splits` metric and the C6 counter read it from the tree. Deleting it would be dishonest, so it is non-finding N1 and lead L1.
- **`import_cycle_modules`** is already 0, and no prototype adds a cycle.

The tree-wide ratchet census (`tests/structure.py`) also falls, from 37 to 19.

**Gate.** The last scoped run on the combined prototype printed `MODE: SCOPED -- 27 script(s) run, 6 scoped out`, `NO UNCLAIMED DRIFT: 56 scenario(s)` (all byte-identical) and `NO STALE FIXTURE`. features (4107), finite_boundary (84), config_flow_steps (499), the structure ratchet, arch_score_head and every other script that ran passed. That run still ended rc=1 with four scripts red:
- **typing_ruler:** one mypy error in `_PayloadPathMixin`. I fixed it (`tuple[type[int | float], ...]`), and mypy `--strict` on the package is now clean. That fix has not been through a full gate.
- **harness_headers:** my harnesses located the repo root with a parent-depth walk. They now use the canonical `repo_root`, and `harness_headers.py` passes 109/109.
- **entities "--anchor":** the mutation ledger's pins name the old `_as_float(` text. They need the usual ledger re-key, which I did not do for prototypes.
- **stress:** one CPU-budget check, 359x the reference against a 268x budget, on a heavily loaded box (load1 above 100). This is provisional and needs a quiet-window re-take.

**The first gate run caught a real bug.** Before patch 00 (D7-arch2-01), the 24 sensors moved onto the two new mixins escaped the NaN/numpy scrub. Patch 00 fixes it, and the gate suite now catches that escape.

| id | change | sev / class | Δcopies | delta_S | size |
|---|---|---|---|---|---|
| 01 | finite scrub resolves through the MRO (prerequisite of 02/03) | low / bug | 0 | 0 | small: `entity.py` |
| 02 | 00+01: 17 "rounded payload key" `native_value`s become `_PayloadValueMixin` | low / hygiene | 13 | +2.6888 | medium: `sensor.py` + `entity.py` |
| 03 | 00+02: 7 payload-section walks become `_PayloadPathMixin` | low / hygiene | 5 | +0.9689 | small: `sensor.py` |
| 04 | zone-setpoint renaming, 3 copies, becomes `entity.zone_setpoint_attributes` | low / hygiene | 2 | +0.3789 | small: `entity.py`, `sensor.py`, `climate.py` |
| 05 | two identical config-flow helpers become `_suggested_optional` | low / hygiene | 1 | +0.1880 | small: `config_flow.py` |
| 06 | 9 validating options pages use the `_page` template (`check`/`finish`/`placeholders`) | low / hygiene | 6 | +1.1717 | large: `config_flow.py` + 1 registry row in `tests/entities.py` |
| 07 | hour-of-day clock: 5 implementations, 2 meanings, become `format_clock` and `wall_clock` | low / hygiene | 1 | +0.1880 | small: `dhw_schedule.py`, `dhw_draws.py`, `quiet_windows.py`, `pump_arbiter.py` |
| 08 | finite-float coercion: 9 implementations, 10/17 probes disagree; 6 become `inputs.finite_float` | low / hygiene | 0 | +0 (the score cannot see it) | medium: 7 modules + 2 tests |
| 09 | wrapping named-range parser written twice in `grid_fee` | low / hygiene | 1 | +0.1880 | small: `grid_fee.py` |
| 10 | sensor payload guard spelled 4 ways (bool and text answers differ) | low / hygiene | (semantic view of 02/03) | — | — |
| 11 | power state → kW parsed 4 ways; `quiet_windows._power_entity_kw` returns `inf` on "1e400" | low / hygiene | not prototyped | — | small |

Things you should know about these changes:
- **06 is a behaviour change, on rejected forms only.** Eight of the nine pages re-rendered a rejected form with the stored entity the user had just cleared; one page did not. The template makes the cleared form the rule for all nine.
- **06 changes one registry row** in `tests/entities.py`: the `wood_furnace_on` disposition moves from `async_step_building` to `_building_wood_flag`.
- **08 leaves three helpers** (`away`, `wood_fuel`, `sensor`) because they need one decision from you: is `True` a number? `tests/features.py` pins `away._as_num(True, 7.0) == 7.0`.
- **11 inf leak:** its effect is bounded by the clip in `silent_cap_kw`. The proposed owner is `inputs.state_power_kw(state)`.

```json
{
 "dimension": "D7",
 "baseline_sha": "554e2ecfa7ad5b1660a1256ebf6cf6ac3810d9ef",
 "exposure": [],
 "coverage": [
  {"step": "duplication_copies", "depth": "deep", "evidence": "all 43 gapped clone classes read (census.py); 29 copies prototyped, the rest rejected as non-identical meaning (N3)"},
  {"step": "dead_members", "depth": "deep", "evidence": "structure.py dead_symbols table; git grep under custom_components; computed getattr(const, ...) census"},
  {"step": "public_unused", "depth": "deep", "evidence": "public_surface unused_names == ['const.ENTITY_FAMILY_OVERRIDES']"},
  {"step": "import_cycle_modules", "depth": "spot", "evidence": "baseline 0; harness shows no rise for any patch"},
  {"step": "semantic shapes (owner scope addition)", "depth": "spot", "evidence": "4 shapes driven (finite float, hour clock, payload guard, power kW); 5 more enumerated by grep only"}
 ],
 "unfinished": [
  {"step": "D7-arch2-11", "what": "no prototype patch for the power-kW owner"},
  {"step": "semantic shapes", "what": "slot flooring/DST, store-load defaults, inline unit conversions, price-parse entry points enumerated by grep, not driven"},
  {"step": "gate", "what": "the last scoped gate ended rc=1 with 4 scripts red (typing_ruler, harness_headers, entities '--anchor', stress); typing_ruler and harness_headers are fixed after it but not re-gated; the mutation-ledger re-key is not done; stress CPU budget is provisional (load1>100)"},
  {"step": "report", "what": "REPORT.md was refused by the seat harness (subagents return text); its content is in this reply"}
 ],
 "findings": [
  {"id": "D7-arch2-01", "scope": "custom_components/heatpump_optimizer/entity.py", "step": "duplication (blocks 02/03)", "title": "finite scrub keys on the class __dict__, so a mixin-supplied published property escapes it", "severity": "low",
   "claim": "HeatPumpOptimizerEntity.__init_subclass__ wraps native_value/extra_state_attributes/... only when the subclass's own __dict__ holds them; a mixin whose runtime base is object supplies one unscrubbed",
   "evidence": {"command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch-s2/scrub_escapes.py [--patch ...]", "result": "escapes=0 at baseline; 17 with patch 01; 7 with 02; 0 with 00+01 or 00+02. equiv_sensor_values.py: 00+01+02 -> 0/468 mismatches; 01+02 without 00 -> 44"},
   "instrumented_symbol": "entity:HeatPumpOptimizerEntity.__init_subclass__",
   "perturbation": {"change": "apply 01 without 00", "expect": "escapes 0 -> 17, mismatches 0 -> 44"},
   "metric_definition": "(entity class, published name) pairs whose MRO-resolved property fget lacks _finite_scrubbed and is defined in this package",
   "phenomenon_property": "every published property HA resolves on an entity class is scrubbed", "seam_rule": "scrub_escapes.py over every HeatPumpOptimizerEntity subclass in the six platforms",
   "stop_rule_class": "bug", "class_guess": "new", "files": ["custom_components/heatpump_optimizer/entity.py"], "proposed_fix_scope": "patches/00_scrub_resolves_mro.patch (14 lines)"},
  {"id": "D7-arch2-02", "scope": "sensor.py", "step": "duplication_copies", "title": "17 sensors spell the same rounded-payload-key read", "severity": "low",
   "claim": "17 native_value properties are the same 4-statement read; one _PayloadValueMixin owns it", "evidence": {"command": "bash dev/audit/rounds/round10/D7/arch-s2/run_findings.sh 01_value", "result": "delta_S=+2.6888, duplication_copies 68->55, admissible=1, perturbed_delta_S=+0.0000"},
   "instrumented_symbol": "sensor:_PayloadValueMixin.native_value", "perturbation": {"change": "reverse patches 00+01", "expect": "delta_S -> 0"},
   "metric_definition": "archscore duplication_copies (C3 gapped clone census), weight 8.928", "phenomenon_property": "one payload-to-state rule per meaning", "seam_rule": "census.py clone class [11]+[4] sensor.py native_value",
   "stop_rule_class": "hygiene", "class_guess": "P2", "files": ["custom_components/heatpump_optimizer/sensor.py", "custom_components/heatpump_optimizer/entity.py"], "proposed_fix_scope": "medium; requires D7-arch2-01"},
  {"id": "D7-arch2-03", "scope": "sensor.py", "step": "duplication_copies", "title": "7 advisor sensors walk their own payload section", "severity": "low",
   "claim": "one _PayloadPathMixin owns the section walk and number guard", "evidence": {"command": "run_findings.sh 02_path", "result": "delta_S=+0.9689, 68->63, perturbed 0"},
   "instrumented_symbol": "sensor:_PayloadPathMixin.native_value", "perturbation": {"change": "reverse 00+02", "expect": "delta_S -> 0"},
   "metric_definition": "duplication_copies", "phenomenon_property": "one section-walk rule", "seam_rule": "census.py clone classes [5]+[2] sensor.py native_value",
   "stop_rule_class": "hygiene", "class_guess": "P2", "files": ["custom_components/heatpump_optimizer/sensor.py"], "proposed_fix_scope": "small; requires 01"},
  {"id": "D7-arch2-04", "scope": "entity.py/sensor.py/climate.py", "step": "duplication_copies", "title": "zone-setpoint renaming written three times", "severity": "low",
   "claim": "entity.zone_setpoint_attributes owns the planned->published names", "evidence": {"command": "run_findings.sh 03_zone", "result": "delta_S=+0.3789, 68->66, perturbed 0"},
   "instrumented_symbol": "entity:zone_setpoint_attributes", "perturbation": {"change": "reverse patch 03", "expect": "delta_S -> 0"},
   "metric_definition": "duplication_copies", "phenomenon_property": "one renaming owner", "seam_rule": "census.py class [3] extra_state_attributes",
   "stop_rule_class": "hygiene", "class_guess": "P2", "files": ["custom_components/heatpump_optimizer/entity.py", "custom_components/heatpump_optimizer/sensor.py", "custom_components/heatpump_optimizer/climate.py"], "proposed_fix_scope": "small"},
  {"id": "D7-arch2-05", "scope": "config_flow.py", "step": "duplication_copies", "title": "two identical suggested-not-defaulted helpers", "severity": "low",
   "claim": "_options_suggested_numeric and _suggested_entity have identical bodies", "evidence": {"command": "run_all.sh 04_suggested_optional", "result": "delta_S=+0.1880, 68->67, perturbed 0"},
   "instrumented_symbol": "config_flow:_suggested_optional", "perturbation": {"change": "reverse patch 04", "expect": "delta_S -> 0"},
   "metric_definition": "duplication_copies", "phenomenon_property": "one rule", "seam_rule": "census.py pair config_flow.py:891/898",
   "stop_rule_class": "hygiene", "class_guess": "P2", "files": ["custom_components/heatpump_optimizer/config_flow.py"], "proposed_fix_scope": "small"},
  {"id": "D7-arch2-06", "scope": "config_flow.py", "step": "duplication_copies", "title": "validating options pages re-implement the page template", "severity": "low",
   "claim": "9 steps hand-write _page's sequence and had drifted (re-render over cleared vs stored; clear over merged vs current)", "evidence": {"command": "run_findings.sh 08_page", "result": "delta_S=+1.1717, 68->62, perturbed 0; config_flow_steps 499 ok, features 4107 ok"},
   "instrumented_symbol": "config_flow:HeatPumpOptimizerOptionsFlow._page", "perturbation": {"change": "reverse patch 08", "expect": "delta_S -> 0"},
   "metric_definition": "duplication_copies", "phenomenon_property": "one options-page skeleton", "seam_rule": "census.py classes [5],[2],[2] config_flow async_step_*",
   "stop_rule_class": "hygiene", "class_guess": "P2", "files": ["custom_components/heatpump_optimizer/config_flow.py", "tests/entities.py"], "proposed_fix_scope": "large; behaviour change on rejected-form re-render only"},
  {"id": "D7-arch2-07", "scope": "dhw_schedule/dhw_draws/quiet_windows/pump_arbiter", "step": "semantic shape", "title": "hour-of-day clock: 5 implementations, 2 meanings", "severity": "low",
   "claim": "label keeps 24:00, wall clock folds; 5 copies become 2 named owners", "evidence": {"command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch-s2/shape_hour_clock.py [--patch patches/05_hour_clock.patch]", "result": "implementations=5, disagreeing_hours=2 (23.999, 24.0); with 05: implementations=2; delta_S=+0.1880 (68->67)"},
   "instrumented_symbol": "dhw_schedule:format_clock; quiet_windows:wall_clock", "perturbation": {"change": "--patch 05", "expect": "implementations 5 -> 2"},
   "metric_definition": "functions rounding hour*60 and reducing by 24*60; probe hours whose HH:MM differ", "phenomenon_property": "one owner per clock meaning", "seam_rule": "shape_hour_clock.py is_seam AST rule",
   "stop_rule_class": "hygiene", "class_guess": "P2", "files": ["custom_components/heatpump_optimizer/dhw_schedule.py", "custom_components/heatpump_optimizer/dhw_draws.py", "custom_components/heatpump_optimizer/quiet_windows.py", "custom_components/heatpump_optimizer/pump_arbiter.py"], "proposed_fix_scope": "small"},
  {"id": "D7-arch2-08", "scope": "inputs/coordinator/entry_config/thermal_model/freq_control/binary_sensor/pump_arbiter", "step": "semantic shape", "title": "finite-float coercion: 9 implementations, 3 policies", "severity": "low",
   "claim": "thermal_model._optional_float raises OverflowError; pump_arbiter._finite_or_none passes NaN/inf; away/wood_fuel refuse bools and pass NaN; 6 consolidate to inputs.finite_float", "evidence": {"command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch-s2/shape_finite_float.py [--patch patches/06_finite_float_owner.patch]", "result": "implementations=9, disagreeing_inputs=10/17; with 06: 4 (residue away, wood_fuel, sensor); delta_S=+0.0000"},
   "instrumented_symbol": "inputs:finite_float", "perturbation": {"change": "--patch 06", "expect": "implementations 9 -> 4"},
   "metric_definition": "module-level coercion-named functions annotated -> float that call float(); probes on which answers differ", "phenomenon_property": "one coercion owner", "seam_rule": "shape_finite_float.py SEAM_RE + AST",
   "stop_rule_class": "hygiene", "class_guess": "P3", "files": ["custom_components/heatpump_optimizer/inputs.py", "custom_components/heatpump_optimizer/coordinator.py", "custom_components/heatpump_optimizer/entry_config.py", "custom_components/heatpump_optimizer/thermal_model.py", "custom_components/heatpump_optimizer/freq_control.py", "custom_components/heatpump_optimizer/binary_sensor.py", "custom_components/heatpump_optimizer/pump_arbiter.py", "tests/features.py", "tests/finite_boundary.py"], "proposed_fix_scope": "medium; owner decides bool policy for the residue"},
  {"id": "D7-arch2-09", "scope": "grid_fee.py", "step": "duplication_copies", "title": "wrapping named-range parser written twice", "severity": "low",
   "claim": "parse_month_range/parse_day_range are one parser over two cycles", "evidence": {"command": "equiv_cyclic_range.py [--break]; run_findings.sh 07_cyclic", "result": "522 tokens, 0 mismatches (--break: 487); delta_S=+0.1880, 68->67"},
   "instrumented_symbol": "grid_fee:_parse_cyclic_range", "perturbation": {"change": "reverse patch 07", "expect": "delta_S -> 0"},
   "metric_definition": "duplication_copies", "phenomenon_property": "one wrap rule", "seam_rule": "census.py pair grid_fee.py:114/133",
   "stop_rule_class": "hygiene", "class_guess": "P2", "files": ["custom_components/heatpump_optimizer/grid_fee.py"], "proposed_fix_scope": "small"},
  {"id": "D7-arch2-10", "scope": "sensor.py", "step": "semantic shape", "title": "a sensor's payload number is guarded four ways", "severity": "low",
   "claim": "26 driven sites, 5 distinct answer vectors; True published as 1/True/None; '21.5' raises TypeError at 18 sites", "evidence": {"command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch-s2/shape_payload_guard.py [--patch 00 --patch 01 --patch 02]", "result": "baseline implementations=35, driven=26, distinct=5, disagreeing_probes=3; with 00-02 implementations=13"},
   "instrumented_symbol": "sensor:*.native_value", "perturbation": {"change": "--patch 00/01/02", "expect": "implementations 35 -> 13"},
   "metric_definition": "native_value properties that read the payload through a guard; distinct answer vectors over probes", "phenomenon_property": "one payload-number guard", "seam_rule": "shape_payload_guard.py family()",
   "stop_rule_class": "hygiene", "class_guess": "P6", "files": ["custom_components/heatpump_optimizer/sensor.py"], "proposed_fix_scope": "follow-on to 02/03; bool policy decision"},
  {"id": "D7-arch2-11", "scope": "inputs/coordinator/quiet_windows", "step": "semantic shape", "title": "four power-state-to-kW parsers; one passes inf", "severity": "low",
   "claim": "quiet_windows._power_entity_kw returns inf for '1e400' kW; others refuse; sign policies differ by use", "evidence": {"command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch-s2/shape_power_kw.py [--sign-blind]", "result": "implementations=4, driven=3, disagreeing_states=3/10 (-0.4kW, 0kW, 1e400kW)"},
   "instrumented_symbol": "quiet_windows:_power_entity_kw", "perturbation": {"change": "--sign-blind", "expect": "the negative-reading disagreement vanishes; 1e400 remains"},
   "metric_definition": "functions calling normalize_power_kw on a value they parsed from a state; probes where driven answers differ", "phenomenon_property": "one parse+unit+finite owner, per-caller sign policy", "seam_rule": "shape_power_kw.py seams()",
   "stop_rule_class": "hygiene", "class_guess": "P3", "files": ["custom_components/heatpump_optimizer/quiet_windows.py", "custom_components/heatpump_optimizer/coordinator.py", "custom_components/heatpump_optimizer/inputs.py"], "proposed_fix_scope": "small; not prototyped"}
 ],
 "non_findings": [
  {"claim": "dead_members=1 and public_unused=1 are const.ENTITY_FAMILY_OVERRIDES, production-unreachable but the family_splits/C6 input; not removable in these cells", "command": "git grep ENTITY_FAMILY_OVERRIDES 554e2ecfa -- custom_components | wc -l; git grep 'getattr(const' 554e2ecfa -- custom_components", "value": "1 (definition only); 3 computed getattr, all CONF_/DEFAULT_ names"},
  {"claim": "import_cycle_modules is 0 and no prototype adds a cycle", "command": "run_findings.sh 99_all", "value": "no import_cycle_modules line moved"},
  {"claim": "available x3, _waiting_for x3, ledger.add/observe_meta_mean, legionella check_*, inputs.value/text, drift/power_guard _note are not one operation (merging would game)", "command": "census.py", "value": "rejected"},
  {"claim": "17 inline EMA updates are a formula, not a policy owner", "command": "grep (scout)", "value": "not proposed"}
 ],
 "harnesses": ["harness.py", "run_findings.sh", "run_all.sh", "census.py", "scrub_escapes.py", "equiv_sensor_values.py", "equiv_cyclic_range.py", "shape_finite_float.py", "shape_hour_clock.py", "shape_payload_guard.py", "shape_power_kw.py"],
 "leads": [
  {"owner_seat": "ARCH-s3", "file": "tools/audit/archscore/metrics/family_splits.py", "symbol": "const.ENTITY_FAMILY_OVERRIDES", "what": "the instrument's only production input pins dead_members and public_unused at 1"},
  {"owner_seat": "D9", "file": "tariff.py/optimizer.py/thermal_model.py", "symbol": "_smooth_topk_sum(_batch), objective(_batch), _simulate_step_*", "what": "scalar/batch twins, about 7 census copies; a merge needs a Pi-cost measurement"},
  {"owner_seat": "D3/D11", "file": "tests/entities.py", "symbol": "_p6_arm_e", "what": "error codes returned as {key: 'code'} literals are invisible to the P6 E census"},
  {"owner_seat": "D3", "file": "tests/", "symbol": "dhw_schedule.format_windows / quiet_windows._power_entity_kw", "what": "no test drives the 24:00 label disagreement or the inf kW"}
 ]
}
```

**Commands, with their rc** (all from the worktree root):
- **Setup:** `git fetch origin && git checkout -b audit/r10-arch-s2 origin/main` rc 0.
- **Baseline:** `vector.py .` rc 0; `census.py` rc 0.
- **Per-patch harness:** `harness.py` for 02 rc 0. `run_all.sh` for 01/03/04/05 rc 0. `run_findings.sh` for 00/02/06/07/08 rc 0, for 01/03/08/99_all rc 0, and for 02/99_all rc 0.
- **Shape harnesses, baseline and patched, all rc 0:** `shape_finite_float.py`, `shape_hour_clock.py`, `shape_payload_guard.py`, `shape_power_kw.py`.
- **Equivalence and escapes, all rc 0:** `scrub_escapes.py` (4 arms), `equiv_sensor_values.py` (both arms), `equiv_cyclic_range.py` (both arms).
- **Single scripts on the combined prototype:** `tests/finite_boundary.py` rc 0 (84/84). `tests/structure.py --record` rc 0. mypy `--strict` on the package: no errors.
- **Scoped gate** (`GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=554e2ec... ./tests/run.sh`), three runs: the first was killed (exit 144); the second I stopped after its findings; the third ended rc=1 with the four reds above.
- **After the fixes:** `tests/harness_headers.py` rc 0 (109/109).
- **Push:** `git push origin HEAD:refs/heads/handoff/audit-r10-arch-s2` rc 0, confirmed with `git ls-remote`.

The local prototype branches (`proto/s2-*`) are not pushed. The worktree is left on `audit/r10-arch-s2`.

Files are in `~/heatpump_optimizer/.claude/worktrees/agent-a09c8f8f34cdd82d0/dev/audit/rounds/round10/D7/arch-s2/`:
- `harness.py`
- `run_findings.sh`
- `census.py`
- `scrub_escapes.py`
- `equiv_sensor_values.py`
- `shape_finite_float.py`
- `shape_power_kw.py`
- `patches/00_scrub_resolves_mro.patch` through `patches/08_options_page_template.patch`
- `patches/99_combined.patch` and `patches/99t_combined_tests.patch`