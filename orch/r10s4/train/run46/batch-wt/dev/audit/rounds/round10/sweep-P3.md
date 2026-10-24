# Round 10 class sweep: P3

Class P3 in `dev/audit/config/bugclasses.json` is "a capacity floor or divisor
applied inconsistently across sibling formulas". Its status is `barriered`. The
barrier is R9-P3 arm (a) in `tests/features.py`, and it covers `max(E, c>0)`
floors only. That record says so itself: "a sibling disagreement that is not a
floor ... is pinned per pair, not class-wide".

All four round-10 survivors are outside that arm:

| finding | shape |
|---|---|
| D2-s1-71 | a learned multiplier (the lower-floor ratio) is applied by some readers of the nameplate and skipped by others |
| D2-s3-73 | the same shape, in sysid's prior and adoption base |
| D12-s2-71 | a learned multiplier has no anchor, so an options edit of its nameplate double-applies it |
| D7-s2-58 | one coercion rule is implemented nine times under three policies |

The sweep runs D14 method steps 3 and 4 for those shapes. `barriered` is
`false` in `sweep-P3.json` because no CI check covers these shapes. The R9
barrier passed every seam listed below.

Measured at `handoff/audit-r10-register` @ 9355f107d, detached worktree, venv-ci
Python 3.14.7, macOS arm64. All figures are counts or ratios, so timing does not
affect them.

## Enumerator

`dev/audit/rounds/round10/D14/sweep-P3/enumerate.py`. It walks the AST of the
whole package and nothing in it is listed by hand. It has four arms:

| arm | seam rule | listed | flagged |
|---|---|---|---|
| R | every Load of `.lower_floor_heat_loss`, flagged when its statement does not name `lower_floor_loss_ratio` | 6 | 4 |
| S | every function reading `.upper_floor_heat_loss`, flagged when its body applies no house scale (name, `effective_heat_loss_coefficient`, or a `scale` argument) | 14 | 4 |
| A | every learned multiplier key (`*scale`/`*ratio`) in `store.DOMAINS["thermal_learning"]`, flagged when no `*_anchor` key shares its stem | 4 | 3 |
| F | D7 ARCH-s2's coercion seam rule (`SEAM_RE` + AST), on this tree | 9 | 9 |

`RESULT tree R=4 S=4 A=3 F=9 seams_total=33`.

**Positive control.** The enumerator re-finds every finding:
- R flags `_space_demand_kw` (D2-s1-71), and `sysid._zone_heat_loss` and
  `sysid.adoption_decision` (D2-s3-73).
- A flags `lower_floor_loss_ratio` (D12-s2-71).
- F lists the nine implementations of D7-s2-58.

**Null control.** `--null` runs it over `D14/sweep-P3/fixture_clean/`, a fixture
in which the ratio and scale are applied, every multiplier is anchored and one
coercion owner exists. It prints `R=0 S=0 A=0 F=1`. A single implementation
cannot disagree with itself, so `F=1` is the clean value.

**Perturbation.** `--perturb` makes two one-line re-introductions on a temporary
copy of the package:
- drops `* self._lower_floor_loss_ratio` from
  `coordinator._house_heat_loss_anchor`;
- drops the `house_heat_loss_anchor` DOMAINS key.

It prints `perturb_delta R=1 A=1` (expected 1 and 1).

## Disposition of every seam

**Instances that are judged sites** (`beyond_finding: false`):

| seam | probe |
|---|---|
| coordinator `_space_demand_kw` | `reparam_sites.py`: `space_demand_rel_diff=0.4367` (D2-s1-71) |
| sysid `_zone_heat_loss` | `sysid_prior_ua_rel_diff=0.4367` (D2-s3-73) |
| sysid `adoption_decision` | `sysid_adopt_effective_rel_err_A=0.4367`, 614.6 W/K adopted for 427.8 (D2-s3-73) |
| store `lower_floor_loss_ratio` (no anchor) | `options_reseed_both_zones` upper 0.3681, lower 0.2145 (D12-s2-71) |
| F: away `_as_num`, coordinator `_as_float` and `_at_least`, entry_config `_number`, inputs `_finite`, pump_arbiter `_finite_or_none`, sensor `_as_float`, thermal_model `_optional_float`, wood_fuel `_optional_float` | `shape_finite_float.py`: implementations=9, disagreeing 10/17 (D7-s2-58) |

**Instances beyond the findings** (`beyond_finding: true`, 2). The probe is
`D14/sweep-P3/probe_anchor.py`. It exits 1 on these two seams; `--null` prints 0
for every arm and exits 0.

| seam | what happens on an options edit | probe |
|---|---|---|
| store `cop_scale` (no anchor) | Editing `heat_pump_cop_nominal` x1.2 under a stored `cop_scale` 0.8 reloads the scale verbatim. Effective COP becomes 3.36 against the learned 2.80. | `cop rel_err=0.2000` |
| store `solar_aperture/scale` (no anchor) | Editing `window_area` x1.5 under a stored scale 1.6 reloads the scale verbatim. The effective aperture becomes 43.2 against the learned 28.8. | `aperture rel_err=0.5000` |

These two seams have the same mechanism as D12-s2-71: the #86 re-anchor law was
built for the house scale only. The probe's control arm is the house scale
itself, and its `rel_err` stays at 0.0019 (the phi law), not 0.25.

**Guarded:**

| seam | guard |
|---|---|
| R `ThermalParameters.lower_floor_heat_loss_learned` | the owner of the product |
| R `_house_heat_loss_anchor` (coordinator 4775) | applies the ratio |
| A `house_heat_loss_scale` | `house_heat_loss_anchor` plus `_reanchor_house_heat_loss_scale`; probe control arm 0.0019 |
| S `battery.build`, `_space_demand_kw` (for the scale), `optimizer.hold_demand_kw`, `_buffer_charge_ceiling`, `_compute_baseline_power`, `_baseline_thermal_demand_two_zone`, `sysid._held_state`, `ThermalModel.flow_target_for_indoor`, `ThermalModel._zone_loss` | apply the scale directly or through `effective_heat_loss_coefficient`, which multiplies `house_heat_loss_scale` |
| S `_effective_house_heat_loss` | takes the scale as an argument |

**Not applicable:**

| seam | reason |
|---|---|
| R `_async_learn_lower_floor_loss` (coordinator 5205) | This is the ratio's own Newton base. The ratio is the unknown and is passed as the current value, so its base must exclude it. |
| S `_house_loss_terms` | This is the scale's own fit base, and it excludes the scale by design. |
| S `_house_heat_loss_anchor` | The anchor is the pre-scale UA by definition. |
| S `sysid._zone_heat_loss`, `adoption_decision` | These are the base the scale multiplies, which is right for the scale. Arm R lists them as instances because they omit the ratio. |

## Barrier proposal

Extend R9-P3 in `tests/features.py` with two arms:
- arm R as a zero-group check. The only raw read of `.lower_floor_heat_loss`
  allowed is the owner property, plus the named learner base.
- arm A as a check that every learned multiplier in `DOMAINS["thermal_learning"]`
  carries an anchor, or sits on a named exception list with its reason.

Both are AST-only and cost under 1 s of gate time. Arm F belongs to D7-s2-58's
one-owner fix (`inputs.finite_float`), not to a class check.

## Not done

- These files are untracked. A committer must classify the four new files under
  `D14/sweep-P3/`, or `tests/entities.py` fails.
- Arm S covers the house scale only. Other learned multipliers (`cop_scale`,
  `solar_aperture_scale`) were not swept for raw reads; arm A sweeps them for
  anchors only.
