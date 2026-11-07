# R10-MIN-POWER-FLOOR design note (designer seat, note 1)

Base: origin/main 53273de4d449a990bc29734565f63babada9ff7f (no predecessor handoff head: the group has no `after` edge).
Finder: the fixer's STOP at d58242d8c54eec8ae822f1242bdacc513b7218e3 (`dev/audit/rca/r10-min-power-floor-STOP.md`,
harness `dev/audit/harnesses/r10_min_power_floor.py`), re-run at 53273de4d: all 16 lines byte-identical to the STOP table.
Issue 3289 is an outside report; the reporter's write surface is unknown, so nothing below assumes switch plus setpoint.

## Choice: (a), an explicit declaration, plus a joint projection

1. **Declaration.** A select `compressor_modulation` on the options page `thermal_model`, next to
   `CONF_HEAT_PUMP_MIN_POWER` (`custom_components/heatpump_optimizer/config_flow.py:1721`), values
   `auto` (default, stored absent-equivalent) / `on_off` / `modulating`, house style of `CONF_TWO_ZONE_MODE`
   (`custom_components/heatpump_optimizer/const.py:749`). `on_off` forces the existing projection and with it
   `optimizer._relaxed_starts` and `_scores_rounded`, which already key on `clamp_planned_levels`: no solver change.
2. **Joint projection.** Measured at base with the harness extended by `max(space+dhw)`: the clamp=True arm
   with DHW on ships totals of **5.3, 5.0, 5.0 kW** against p_max 3.5 (3 of 4 DHW cells; clamp=False never
   exceeds 3.5). `optimizer._realize_draw` and the publish at
   `custom_components/heatpump_optimizer/optimizer.py:5103` project space and DHW **separately**, while the
   solve shares one compressor (`headroom = p_max - dhw`, optimizer.py:4193). The issue's invariant ("every step
   is 0 or between min and max") is per step and per compressor, so it binds the total; on today's probed
   switch-plus-setpoint installs this is a live defect, and the declaration would extend it to every `on_off` install.

## Owning seam

`custom_components/heatpump_optimizer/thermal_model.py` owns both decisions: whether levels clamp
(`probe_install` -> `InstallCapability.can_duty_cycle` -> `duty_cycle_realizable` -> `levels_clamped`) and the
projection (`project_planned_levels`). Callers only: `optimizer.py` (`OptimizationConfig.from_mapping`,
`_published_levels`, `_realize_draw`), `draw_range.py:584`, `config_flow.py` (writes the key). `tests/seam_map.json`
covers coordinator units only; none moves (`_init_model` core, `_learning_view` learning stay callers). One owner.

## Shape

- `const.py`: `CONF_COMPRESSOR_MODULATION`, `COMPRESSOR_MODULATION_{AUTO,ON_OFF,MODULATING}`, the tuple, default AUTO.
- `thermal_model.py`: one helper `declared_modulation(cfg) -> bool | None` (True modulating, False on/off, None
  probe). It reads the select, and the legacy raw `clamp_planned_levels` (true -> on/off, false -> modulating)
  when the select is `auto`/absent; it is the **only** reader of either key. `InstallCapability` gains
  `on_off: bool = False` (set by `probe_install` when `declared_modulation is False`); `can_duty_cycle` returns
  False first when `on_off`. `duty_cycle_realizable` and `learner_unmetered` replace their raw
  `cfg.get(CONF_CLAMP_PLANNED_LEVELS) is False` with `declared_modulation(cfg) is True` (today's opt-out, unchanged).
  Consequences of `on_off`, all intended and each tested: `fully_metered()` False -> clamped even with a frequency
  sensor; `learner_unmetered` freezes when unmetered (same as a probed switch+setpoint); `draw_range.planned_range`
  lets a metered floor raise the min end.
- `thermal_model.py`: `project_planned_draw(space, dhw, p_min, p_max) -> (space, dhw)` on the **total** t:
  t <= 0 -> (0, 0); 0 < t < p_min -> both scaled by p_min/t; t > p_max -> both by p_max/t; DHW `None` reduces to
  `project_planned_levels`. `_realize_draw` calls it; optimizer.py:5103-5107 becomes one `_realize_draw` call.
- Entity attributes, `plan_slots.py`: unchanged (the slot average is correct once the steps are; STOP refuted the
  reporting hypothesis). The per-step sensor attribute is not needed.

```
entry.options --> declared_modulation --> probe_install.on_off --> can_duty_cycle --> duty_cycle_realizable
      |                                                                                      |
  config_flow select                                    levels_clamped --> OptimizationConfig.clamp_planned_levels
                                                       --> _relaxed_starts, _scores_rounded, _realize_draw -> project_planned_draw
```

Invariants kept: absent key and `auto` are byte-identical to base on every install; legacy `false` keeps
today's reading at every read site; `_relaxed_starts` and the multi-start count are untouched.

## Alternatives, and why each lost

- **(b) integer on/off in the solve.** The solver is continuous L-BFGS-B (`from scipy.optimize import minimize`,
  optimizer.py:54; `_lbfgsb_run`), no MILP path exists. A binary per step x channel is a second solver backend
  on a Pi-class target (D9), and still needs the same "which installs" decision (a) makes; the projection
  scored inside the objective (`_scores_rounded`) already reads 0 sub-minimum steps in 8 of 8 cells.
- **(c) flip the probe's default** (clamp unless frequency is seen). Entity mapping cannot observe
  modulation; the flip clamps every modulating install on a setpoint-only or no-write surface. The five
  `coord_*` goldens (`tests/golden.py:880-927`) map no write entity and would all move, value-bearing,
  needing canonical-environment claims, for installs no finding names.
- **(a') reuse the raw `clamp_planned_levels` as the UI key.** A boolean selector cannot store "absent", so
  the UI would erase the probe; a mapping layer in the flow has no precedent. Kept as the legacy input of the one helper instead.
- **Per-channel projection kept.** Ships 5.3 kW on a 3.5 kW pump (above); lost on the measured defect.

## Sibling sites (step 5)

`grep -rn "can_duty_cycle()\|fully_metered()\|CONF_CLAMP_PLANNED_LEVELS\|levels_clamped(\|_published_levels(\|project_planned_levels(\|_realize_draw(" custom_components tests/*.py`
at base lists 18 sites: thermal_model.py:1318, :1446-1447, :1509-1511 (covered: helper); optimizer.py:145, 158, 161,
4617, 4679, 4838, 5103, 5106 (covered: joint projection; 4838 is the space-only path, DHW absent, unchanged
behaviour); draw_range.py:584 (covered, consequence above); optimizer.py:2112 (unchanged caller); tests/features.py
68460-68507, 74529 (extended, below). `diagnostics.py:404` (draw-range view) reads the probe and follows it.

## Evidence plan (by file)

- **Failing tests first**, `tests/features.py` beside the #1955 block (68460-68520):
  1. `OptimizationConfig.from_mapping({**_PP_METERED, compressor_modulation: on_off}).clamp_planned_levels is True`
     (fails at base: fully metered -> realizable), and the same on a setpoint-only and a frequency-sensor-only map.
  2. **Per-step**, not slot-average: the harness's spread/DHW/-4 C cell, declared `on_off`, asserts every step's
     space+DHW total is 0 or in [2.5, 3.5]. Fails at base twice: unclamped, 7 steps below 2.5 while slot averages
     stay >= 3.2; clamped, totals up to 5.3. A slot-average assertion passes at base and is not acceptable.
  3. `auto`, absent and legacy `false` give base's `clamp_planned_levels` on `_PP_UNMETERED`, `_PP_METERED`, `{}`.
- **Finder's harness at both ends**, unchanged, plus a declared-`on_off` arm: the fix head must read
  `total_below_min=0` in all 8 `on_off` cells and max total <= 3.5 in every clamp=True cell.
- **Null control**: the harness's clamp=False arm and the absent key stay byte-identical at both ends; every cost
  figure quoted is beside its flat-price cell (objective values, never a savings claim).
- **Moving goldens**: solver goldens none (no golden sets the key or maps a switch plus setpoint);
  `config_flow` moves ADD-ONLY (one new leaf per appearance of the options page) and is claimed in
  `tests/golden/claimed_drift.txt` with that direction. `tests/golden/card_claimed_drift.txt` byte-identical.
- **Mutation targets**: the `on_off` early return in `can_duty_cycle`; `is True` in the replaced opt-out reads;
  the `t < p_min` and `t > p_max` branches and the shared scale in `project_planned_draw` (per-channel revert must
  fail test 2); the `auto` fallthrough in `declared_modulation`.

## Docs and strings

`docs/configuration.md`: a row after "Heat pump min power" in "### Thermal model (expert)" (line 855) and one
sentence at line 211 naming the option for a pump that cannot modulate. Labels in
`custom_components/heatpump_optimizer/strings.json`, `translations/en.json`, `translations/sv.json` (selector
`compressor_modulation` like `two_zone_mode`). There is no German file at base: the label goes to R10-I18N-DE.

## Hot files and serial position

Roster edit owed (orchestrator): size L; files add `config_flow.py`, `const.py`, `strings.json`, `en.json`,
`sv.json`, `draw_range.py`, `tests/features.py`, `tests/config_flow_steps.py`, `tests/golden/claimed_drift.txt`;
`plan_slots.py` stays listed but untouched. `after`: **R10-HOTFIX-COP-UNMEASURED** (#3297 adds fields to
`InstallCapability` and `probe_install`, and fields to `_OPTION_FIELDS`, `const.py`, the three string files, the
same docs table) and **R10-GENERIC-HEAT-CURVE** (#3284: `_OPTION_FIELDS`/`_OPTION_PAGES`, strings, docs). Both
are textual, no semantic dependence. R10-PARTLOAD-RESIDUE (optimizer.py; diff is harness-only so far),
R10-GENERIC-HEAT-CURVE-PERSISTENT and R10-ARBITER-OFF-RESTORE (docs/configuration.md only): no edge, rebase at
merge. R10-USER-DOCS-VERIFY already orders after this group.

## Notes for the fixer

- Joint scaling can leave a channel's own share below p_min in a mixed step; that is a diverter time-share of a
  compressor running at >= p_min. Count the harness's `space_steps_below_min` only on space-only steps, and say
  so in the body. Carry: R10-MIN-POWER-FLOOR (item f7b24e7a)
- Re-read #3297's `probe_install` at its merge: if it changes `can_duty_cycle` or `fully_metered`, revalidate
  here first. Carry: R10-MIN-POWER-FLOOR (item df5196cc)
- The new option's German label. Carry: R10-I18N-DE (item 9980b124)
- The docs row is a claim `tests/doc_claims.py` may pin. Carry: R10-USER-DOCS-VERIFY (item df23e57c)
- Per-step power beside `avg_power_kw` on the plan sensor. Carry: dismissed: steps correct once projected, slot average then honest (item f3c0e349)
- The issue reporter must pick `on_off` unless their surface is switch plus setpoint; the reply on 3289 names the
  option. Carry: R10-MIN-POWER-FLOOR (item 052fa8fb)
