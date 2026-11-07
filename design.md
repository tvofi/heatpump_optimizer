# R10-MIN-POWER-FLOOR design note (designer seat, note 2)

Base: origin/main 53273de4d449a990bc29734565f63babada9ff7f (no predecessor handoff head: the group has no `after` edge).
Finder: the fixer's STOP at d58242d8c54eec8ae822f1242bdacc513b7218e3 (`dev/audit/rca/r10-min-power-floor-STOP.md`,
harness `dev/audit/harnesses/r10_min_power_floor.py`, sha1 e21d29905d30), re-run at 53273de4d: all 16 lines byte-identical.
Revises note 1 (0391c607c) against verdict 00e526af: points 1 (shape) and 2 (evidence plan) and carry a1c0f3d2 answered below.
Issue 3289 is an outside report; the reporter's write surface is unknown, so nothing below assumes switch plus setpoint.

## Choice: (a), an explicit declaration, plus space projected against the planned DHW

1. **Declaration** (unchanged from note 1, confirmed). A select `compressor_modulation` on the options page `thermal_model`,
   next to `CONF_HEAT_PUMP_MIN_POWER` (`custom_components/heatpump_optimizer/config_flow.py:1721`), values `auto` (default,
   stored absent-equivalent) / `on_off` / `modulating`, house style of `CONF_TWO_ZONE_MODE`
   (`custom_components/heatpump_optimizer/const.py:749`). `on_off` forces the existing projection and with it
   `optimizer._relaxed_starts` and `_scores_rounded`, which already key on `clamp_planned_levels`: no solver change.
2. **Space against DHW.** At base the clamp=True arm with DHW on ships space+DHW totals of **5.30, 5.00, 5.00 kW** against
   p_max 3.5 (3 of 4 DHW cells), because `optimizer._realize_draw` (`optimizer.py:149`) and the publish at
   `optimizer.py:5103-5108` project space and DHW **separately** while one compressor serves both (`headroom = p_max - dhw`,
   `optimizer.py:4193`). DHW stays as the DHW planner booked it and as base projects it today; only space moves.

## Owning seam

`custom_components/heatpump_optimizer/thermal_model.py` owns both decisions: whether levels clamp
(`probe_install` -> `InstallCapability.can_duty_cycle` -> `duty_cycle_realizable` -> `levels_clamped`) and the projection
(`project_planned_levels`, new `project_space_against`). Callers only: `optimizer.py` (`OptimizationConfig.from_mapping`,
`_published_levels`, `_realize_draw`), `draw_range.py:584`, `config_flow.py` (writes the key). `tests/seam_map.json` covers
coordinator units only; none moves. One owner.

## Shape

- `const.py`: `CONF_COMPRESSOR_MODULATION`, `COMPRESSOR_MODULATION_{AUTO,ON_OFF,MODULATING}`, the tuple, default AUTO.
- `thermal_model.py`, unchanged from note 1: `declared_modulation(cfg) -> bool | None` is the **only** reader of the select and
  of the legacy raw `clamp_planned_levels` (true -> on/off, false -> modulating, read when the select is `auto`/absent).
  `InstallCapability.on_off: bool = False`, set by `probe_install` when `declared_modulation is False`; `can_duty_cycle`
  returns False first when `on_off`. `duty_cycle_realizable` and `learner_unmetered` replace their raw
  `cfg.get(CONF_CLAMP_PLANNED_LEVELS) is False` with `declared_modulation(cfg) is True`. Consequences of `on_off`, each
  tested: `fully_metered()` False -> clamped with a frequency sensor; `learner_unmetered` freezes when unmetered;
  `draw_range.planned_range` lets a metered floor raise the min end.
- `thermal_model.py`, **new**: `project_space_against(space, dhw, p_min, p_max) -> np.ndarray`, where `dhw` is the already
  projected DHW vector d (length N) and `space` is a vector or a B x N matrix. Per step: hi = max(0, p_max - d),
  lo = max(0, p_min - d); space -> clip(space, 0, hi), then a value in (0, lo) -> min(lo, hi). So space lies in
  {0} ∪ [max(0, p_min - d), p_max - d], the total in {0} ∪ [p_min, p_max] (d is in {0} ∪ [p_min, p_max] already, so lo is
  p_min where d = 0 and 0 elsewhere), and the map is the identity wherever space+d is already in [p_min, p_max]. With
  d = 0 it reduces exactly to `project_planned_levels`.
- `optimizer._realize_draw`: when `clamp` and `dhw is not None`, `d = _published_levels(clamp, dhw, ...)` (today's DHW
  projection, a vector) and space `= project_space_against(space, d, ...)`; otherwise today's code. DHW's output stays the
  same N-vector in `objective` (4617) and `objective_batch` (4679), broadcast against the batch rows: the twin's row-for-row
  identity holds. The publish at 5103-5108 becomes one `_realize_draw(self.config.clamp_planned_levels, optimal_space,
  optimal_dhw, p_min, p_max)` call. The space-only path (4838, DHW absent) is unchanged.
- Entity attributes, `plan_slots.py`: unchanged (STOP refuted the reporting hypothesis). No per-step sensor attribute.

```
entry.options -> declared_modulation -> probe_install.on_off -> can_duty_cycle -> duty_cycle_realizable -> levels_clamped
   (config_flow select)          -> OptimizationConfig.clamp_planned_levels -> _relaxed_starts, _scores_rounded,
                                    _realize_draw: d = project_planned_levels(dhw); space = project_space_against(space, d)
```

**Behaviour that changes, by install** (no "byte-identical everywhere" claim):
- *Probed switch-plus-setpoint, no frequency, DHW on* (today's clamped arm): **changes**, space capped at p_max - d. This is
  the measured over-p_max defect, fixed for installs that are clamped today.
- *Declared `on_off`* on any surface: newly clamped, with the joint projection.
- *Clamped, DHW off*, and every *unclamped* install (absent/`auto` on any other surface, legacy `false`, `modulating`):
  unchanged; the harness clamp=False arm is byte-identical base vs spike.

## Spike measurement (uncommitted, on 53273de4d; space-against-DHW in `_realize_draw` and the publish)

Finder's harness, clamp=True arm, extended by `max_total` and a space-only counter (DHW <= 0.1 kW):

| cell (clamp=True) | base max total | spike max total | spike total_below_min | space-only below min | objective base -> spike |
|---|---|---|---|---|---|
| spread, DHW, -4 C | 5.30 (3 over) | 3.50 | 0 | 0 | 38.844 -> 39.056 |
| spread, DHW, 5 C | 5.00 (1 over) | 3.50 | 0 | 0 | 20.652 -> 20.601 |
| flat, DHW, -4 C (null control) | 5.00 (3 over) | 3.50 | 0 | 0 | 67.571 -> 67.364 |
| flat, DHW, 5 C (null control) | 3.50 | 3.50 | 0 | 0 | 39.167 -> 39.167 |

The four DHW-off clamp=True lines and all eight clamp=False lines are byte-identical base vs spike. The harness's original
`space_steps_below_min` reads 3, 1, 3, 0 in the DHW cells at the spike: mixed steps, where space is a diverter share of a
compressor at >= p_min; the space-only counter reads 0 (carry a1c0f3d2). Objective deltas move both ways at spread and at
flat prices alike, so they are not a savings claim: base's objective scored draws the pump cannot deliver.
`GOLDEN_MODE=strict python3 tests/golden.py` at base and at the spike: reports byte-identical (both red with the same
environment drift on this non-canonical host), so no golden scenario, `coord_dhw` and `coord_all_features` included
(`tests/golden.py:893-917`), probes clamped.

## Alternatives, and why each lost

- **Shared scale on the total** (note 1): writes into the DHW schedule the space solve treats as fixed
  (`optimizer.py:4190`, `4690-4694`), so the tank can fall short of the DHW plan; and a per-row scale turns the shared DHW
  vector into a B x N matrix in `objective_batch`, breaking the twin's identity.
- **(b) integer on/off in the solve**: the solver is continuous L-BFGS-B (`optimizer.py:54`), no MILP path; a second backend
  on a Pi-class target (D9) that still needs (a)'s "which installs" decision.
- **(c) flip the probe's default**: entity mapping cannot observe modulation; clamps every modulating install on a
  setpoint-only or no-write surface, moving all five `coord_*` goldens (`tests/golden.py:880-927`) for installs no finding names.
- **(a') reuse raw `clamp_planned_levels` as the UI key**: a boolean selector cannot store "absent" and would erase the
  probe; kept as the legacy input of `declared_modulation`.
- **Per-channel projection kept**: ships 5.3 kW on a 3.5 kW pump (above).

## Sibling sites (step 5)

`grep -rn "can_duty_cycle()\|fully_metered()\|CONF_CLAMP_PLANNED_LEVELS\|levels_clamped(\|_published_levels(\|project_planned_levels(\|_realize_draw(\|clamp_planned_levels=True" custom_components tests/*.py`
at base: production sites thermal_model.py:1318, 1446-1447, 1509-1511 (helper); optimizer.py:145, 158, 161, 4617, 4679, 5103,
5106 (space against DHW); 4838 (space-only, unchanged); draw_range.py:584 (consequence above); optimizer.py:2112
(unchanged caller); diagnostics.py:404 follows the probe. Test sites: tests/features.py 68460-68520 and 74529 (extended);
**65608** (`_r10s_solve`, `dhw=False`: does not move); **68743** (`_sp_solve`, its DHW cells move, below); **68820**
(`_sp_clamped`/`_sp_free` with a quadratic objective, never reaches `_realize_draw`: does not move).

## Evidence plan (by file)

- **Failing tests first**, `tests/features.py` beside the #1955 block (68460-68520):
  1. `OptimizationConfig.from_mapping({**_PP_METERED, compressor_modulation: on_off}).clamp_planned_levels is True`
     (fails at base), and the same on a setpoint-only and a frequency-sensor-only map.
  2. **Per step, declared**: the harness's spread/DHW/-4 C cell, `on_off` on `_PP_METERED`, asserts every step's
     space+DHW total is 0 or in [2.5, 3.5]. Fails at base: unclamped, 7 steps below 2.5 while slot averages stay >= 3.2.
  3. **Per step, probed and undeclared**: the same cell through `OptimizationConfig.from_mapping(_PP_UNMETERED)` (switch
     plus setpoint, no key) asserts every total <= 3.5 and none in (0, 2.5). Fails at base: totals up to 5.30 kW.
  4. `project_space_against` unit rows: d = 0 equals `project_planned_levels`; d = p_min, space 2.8 -> p_max - p_min;
     d = p_max -> space 0; space 0.3 with d = 0 -> p_min; a 2 x N matrix row-equals the vector call.
  5. `auto`, absent and legacy `false` give base's `clamp_planned_levels` on `_PP_UNMETERED`, `_PP_METERED`, `{}`.
- **Pins that move** (value-bearing only in their margins, all `R.check` predicates): the four DHW cells and the flat DHW
  cell of `_sp_solve` at `tests/features.py:68737-68776`. Re-measured on the spike: relaxed-start deltas -0.325, -0.401,
  -1.092, -0.503 (base 0.000, 0.000, -0.991, -0.524) and flat-DHW fix <= control (30.308 vs 31.106): both checks still
  hold; base's cells shipped totals 5.63 and 5.90 over their 5.5 kW p_max, the spike none. The fixer updates any quoted
  margin and the comment block above the section. No golden fixture moves (spike measurement above), so
  `tests/golden/claimed_drift.txt` and `tests/golden/card_claimed_drift.txt` gain no solver claim.
- **Finder's harness at both ends**, unchanged, plus `max_total` and the space-only counter: the fix head must read
  `total_below_min=0` in all clamp=True cells and a declared-`on_off` arm, and `max_total <= 3.5` in each.
- **Null control**: the harness's clamp=False arm stays byte-identical at both ends; every cost figure sits beside its
  flat-price cell (the table above), as objective values, never a savings claim.
- **Moving goldens**: `config_flow` ADD-ONLY (one new leaf per appearance of the options page), claimed in
  `tests/golden/claimed_drift.txt` with that direction; card file byte-identical.
- **Mutation targets**: the `on_off` early return in `can_duty_cycle`; `is True` in the replaced opt-out reads; the `hi`
  cap and the `(0, lo)` raise in `project_space_against` (each must fail test 3 or 4); the `clamp and dhw is not None`
  branch in `_realize_draw` (reverting to per-channel must fail test 3); the publish's single `_realize_draw` call; the
  `auto` fallthrough in `declared_modulation`.

## Docs and strings

`docs/configuration.md`: a row after "Heat pump min power" in "### Thermal model (expert)" (line 855) and one sentence at
line 211 for a pump that cannot modulate. Labels in `custom_components/heatpump_optimizer/strings.json`,
`custom_components/heatpump_optimizer/translations/en.json`, `custom_components/heatpump_optimizer/translations/sv.json` (selector like `two_zone_mode`). No German file at base: label to R10-I18N-DE.

## Hot files and serial position

Roster edit owed (orchestrator): size L; files add `config_flow.py`, `const.py`, `custom_components/heatpump_optimizer/strings.json`, `custom_components/heatpump_optimizer/translations/en.json`, `custom_components/heatpump_optimizer/translations/sv.json`,
`draw_range.py`, `tests/features.py`, `tests/config_flow_steps.py`, `tests/golden/claimed_drift.txt`; `plan_slots.py`
stays listed but untouched. `after`: **R10-HOTFIX-COP-UNMEASURED** (#3297: `InstallCapability`, `probe_install`,
`_OPTION_FIELDS`, `const.py`, strings, the docs table) and **R10-GENERIC-HEAT-CURVE** (#3284: `_OPTION_FIELDS`/`_OPTION_PAGES`,
strings, docs); textual. R10-PARTLOAD-RESIDUE (optimizer.py, harness-only so far), R10-GENERIC-HEAT-CURVE-PERSISTENT and
R10-ARBITER-OFF-RESTORE (docs/configuration.md): no edge, rebase at merge. R10-USER-DOCS-VERIFY already orders after this group.

## Notes for the fixer

- Count `space_steps_below_min` only on space-only steps (DHW <= `MIN_RUNNING_DRAW_KW`); in a mixed step space is a
  diverter share of a compressor at >= p_min. Say so in the body. Carry: R10-MIN-POWER-FLOOR (item a1c0f3d2)
- Re-read #3297's `probe_install` at its merge: if it changes `can_duty_cycle` or `fully_metered`, revalidate here first.
  Carry: R10-MIN-POWER-FLOOR (item df5196cc)
- Re-check the golden claim in drift mode at the fix head (`GOLDEN_MODE=drift GOLDEN_REF=<merge base>`): the spike read no
  solver fixture moving on a non-canonical host. Carry: R10-MIN-POWER-FLOOR (item 6e2b19c4)
- The new option's German label. Carry: R10-I18N-DE (item 9980b124)
- The docs row is a claim `tests/doc_claims.py` may pin. Carry: R10-USER-DOCS-VERIFY (item df23e57c)
- Per-step power beside `avg_power_kw` on the plan sensor. Carry: dismissed: steps correct once projected, slot average then honest (item f3c0e349)
- The reply on 3289 names the option: the reporter picks `on_off` unless their surface is switch plus setpoint.
  Carry: R10-MIN-POWER-FLOOR (item 052fa8fb)
