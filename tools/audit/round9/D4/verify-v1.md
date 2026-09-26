# Round 9 — D4 verify-v1 (lens V1, reproduce), box G2-V1

Tree: /home/claude/wt/D4, evidence commit 6f51db2c (baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 + round9 evidence). 4-core cloud container shared with up to two verifier seats; Python 3.14 venv, Node 22, Playwright 1.56.1, Chromium 141. Every number below is a count or pixel measure (contention-immune); load1 quoted, thread_factor 1.00 on every run, swapins 0. No production file was edited (all perturbations in memory); `git status` shows only `tools/audit/round9/D4/verify-v1/`.

Tally: verify 13, weaken 1 (D4-s1-05), refute 0, unresolved 0.

## s1 (card, Chromium): sweep.mjs canonical targeted run, 144 cells, load1 3.71–5.61

| perturbation | contrast_instances | popup_out_cells | option_indistinct_pairs | now_marker_collisions |
|---|---|---|---|---|
| none | 90 | 6 | 8 | 24 |
| status_text_token | **12** | 6 | 8 | 24 |
| menu_clamp | 90 | **0** | 8 | 24 |
| picker_wrap | 90 | 6 | **0** | 24 |
| now_temp_below | 90 | 6 | 8 | **0** |

Matches the finder's table exactly. The cross-arms are the specificity control: each perturbation moves only its own metric. Null arm (`--states expanded_plan,plan_inline`, 24 cells): contrast 0, popup 0, options 0, now 0.

**D4-s1-01** (verify, medium). contrast_instances=90 in 72 cells; 12 under status_text_token (the white-on-error confirm buttons). My own WCAG luminance ratios match the finder's: #ffa600/#fff 1.96, #43a047/#fff 3.30, #db4437/#fff 4.29, #fff on #db4437 4.29, #db4437/#1c1c1c 3.97. Success (5.16) and warning (8.69) on dark pass, as the finder states. Leave-one-out by site (13 distinct sites): the largest site is `.delta.dearer` with 36; dropping it leaves 54. Ratios range 1.96–4.29 across sites and every site is below 4.5. The failures are fixed by the tokens, so they are not a grid artefact. Metric: visible enabled text runs below 4.5:1 (3:1 large), summed over 144 cells.

**D4-s1-02** (verify, medium). popup_out_cells=6, max viewport spill 9.7 px; 0 and 0 under menu_clamp. All 6 cells are sv-SE:
- 375 px: chartOut 18.2 / 44.2 px; the DHW menu also spills 9.7 px past the viewport.
- 768 px: the DHW menu is 9.3 px past its chart.

The claim's English 64 px column is not counted by this metric. Null: mid-chart opening and every 1280-px cell give 0. The opening point is chosen by the harness, but a real tap near the right edge reaches the same unclamped `openMenu` line. Metric: cells with a .slot-menu/.tooltip more than 0.5 px outside the viewport or its .chartwrap.

**D4-s1-03** (verify, medium). option_indistinct_pairs=8 (375 px box 190 px, 768 px box 322 px, widest option 377 px); option_cut 16. Both are 0 under picker_wrap. Null: the four 1280-px cells give 0. Reaching it needs two entities that share a friendly name, which is plausible, so medium holds. Metric: pairs of differing option texts whose measureText-fitted visible prefix is identical.

**D4-s1-04** (verify, medium). `layout_kbd.mjs`: pipes=12, pipes_click=12, pipes_keyboard=0, boxes=18, boxes_keyboard=0. Under `--perturb kbd`, pipes_keyboard=12 (up, as stated); boxes stay 0 because the perturbation touches only pipes. The layout canvas has no keydown listener. There is a workaround outside the card: the `apply_topology` service, which the card calls, can be reached by keyboard from Developer tools. That supports medium, not higher. load1 2.59–3.20. Metric: pipes removed from `LayoutEditor.edit.edges` after Tab plus Enter/Delete/Space.

**D4-s1-05** (weaken high → medium). now_marker_collisions=24 in all 24 `x_live_default*` cells (13.8x8.6 px en, 7.8x8.6 px sv); 0 under now_temp_below (overlap_instances 160 → 136). Null: 0. Reach is real: `withActuals` publishes `sensor.*_indoor_temperature_optimizer`, which a live install publishes. On severity, the collision is the word "now" printed over "now". In the finder's own crop (`evidence_now_collision_375.png`) the reading "21.1 °C" stays legible and no value is wrong or hidden. That makes it a cosmetic collision, rated medium to match this unit's other visual defects (s1-02 and s1-03). Separately, the sweep also counts 160 axis tick/unit overlaps (e.g. "60" x "°C"). This finding does not claim them, and I cast no vote on them.

## s2 (config/options flows), load1 0.56–1.65

| id | harness | baseline (finder = mine) | --perturb | null control |
|---|---|---|---|---|
| s2-01 | prefill_config_strings.py | unlabelled 3/3, untranslated errors 1/1 (en/sv), preview_fields 5 | 0 all | options twin 0/0 |
| s2-01 | prefill_after_save.py | rendered 1, destinations 1, leaks 1 | 0/0/0 | options destinations 2 |
| s2-02 | currency_units.py | foreign 1 of 4; static texts 2 | 0 | `--currency SEK` 0 |
| s2-03 | escaped_text.py | reached 4, en 1, sv 9, all_files 6 | 0 | other error texts 0 |
| s2-04 | zones_default.py | expert 1 | 0 | describe 0 |
| s2-05 | step_grid.py (Chromium) | defaults 8, derived 4 (box 50, slider 42) | 0/0 | slider 0 |
| s2-06 | preset_warning.py | unwarned 6/6, warned 4/4 | unwarned 0 | `--disarmed` warned 0 |
| s2-07 | quick_menu.py | repeated 1, identical 1 | 0/0 | 0 |
| s2-08 | service_icons.py | 12 of 12 | 0 | entity keys 0 |
| s2-09 | unit_typography.py | 8/8 | 0 | selector bare C 0 |

Method attacks, beyond reproduction:
- **s2-01:** my whole-file enumeration (`static_xcheck.py`) finds 11 `options.step.modbus_prefill.data` keys absent from `config.step.device_prefill.data`, and `prefill_device_unreadable` absent from `config.error` in all 3 files. The finder's 3 is the subset rendered for one device, so the property is broader than the claim.
- **s2-02:** the only literal-currency `_number` is `config_flow.py:1645`; the other literal is `services.yaml:358`.
- **s2-03:** the 6 escaped leaves sit at strings.json:362/1457, en.json:362/1457 and sv.json:360/1455. The claim that ICU prints the escape verbatim remains the finder's stated inference.
- **s2-04:** `async_step_zones` (config_flow.py:2729) stores `user_input` wholesale over `vol.Optional(default=…)` fields. `from_config` in auto mode enables two-zone when any zone key is present (thermal_model.py:1010–1018). The page text (strings.json:116) promises the opposite. Real HA submits the defaults and voluptuous refills them, so this is not stub-only. High is earned: it silently builds the wrong thermal model.
- **s2-05:** the inference that HA forwards min/max/step to a native input is not measured; the low rating accounts for it.
- **s2-09:** my enumeration finds 9 leaves per language — the 8 rendered plus one on a page the finder's walk does not render.

Votes: all s2 findings verify, each at the finder's severity.

## Harnesses written (under tools/audit/round9/D4/verify-v1/)
- `static_xcheck.py`: a whole-file cross-check for s2-01/02/03/08/09 with `--perturb`. Baseline: escaped_leaves=6, prefill_keys_missing_cfg=11, prefill_err_missing_cfg=1, services_without_icon=12, bare_unit_leaves_en/sv=9, literal_currency_units=1. All are 0 under `--perturb`.
- `run_s1.sh <outdir>`: re-runs the s1 Chromium harnesses — baseline, the 4 perturbations, the kbd perturbation and the now-marker null arm.

## Not finished
Nothing. The finder's full 1626-cell grid (`sweep_full.log`) was not re-run: no finding rests on it.
