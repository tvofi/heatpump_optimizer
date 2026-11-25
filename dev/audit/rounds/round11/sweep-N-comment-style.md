# Class sweep: N-comment-style (round 11, D14 steps 3-4)

**Class status.** `N-comment-style` has no entry in `dev/audit/config/bugclasses.json`
at `handoff/audit-r11-register` (28b864af6d). It is a new class from this
round's judge, so its status is `open` by default. The ledger entry is owed
by the class-ledger step, not by this sweep.

**Property.** A comment, docstring or Markdown sentence runs over 40 words
(D5 criterion C5). The text is not false, only over-long.

## Detector

`python3 dev/audit/rounds/round11/D14/N-comment-style/enumerate.py ROOT [paths]`
reads every tracked `.py` (comments and triple-quoted strings), `.js/.mjs/.ts`
(comments) and `.md` (paragraphs, tables and fences skipped). It splits
sentences at `.!?` before a capital letter and counts those over 40 words.

- **Universe at 28b864af6d:** 17214 long sentences in 2683 files.
  By tree: `custom_components/` 90 files (1288 sentences), `tests/` 67,
  `tools/` 302, `docs/` 20, `dev/` 2176.
- **Positive control:** it re-finds every file-level finding site.
  `tests/features.py` 560 (D5-s7-01: 450), `tests/finite_boundary.py` 23
  (D5-s7-02: 14), `tests/frontend.py` 3 (D5-s7-03: 3),
  `docs/img/model/make_card_weekly_figure.mjs` 2 (D5-s2-06: 2). The splitter
  is coarser than the finders' own, so per-file counts sit above theirs.
  D5-s10-07, s3-03, s4-01, s5-07, s6-08, s8-06 and s9-04 count planted
  seat-cell copies with no file named. The tree-wide total covers them.
- **Null control:** a fixture with short comments in `.py` and `.mjs` gives `TOTAL 0`.
- **Perturbation:** appending one 45-word `#` comment to that fixture gives
  `clean.py 1`, `TOTAL 1`.

## Disposition

- **Instance** (probe: the enumerator on the file; a nonzero count fails it).
  All 90 `custom_components/` files with a count, `beyond_finding: true`, plus
  the 4 judged sites above, `beyond_finding: false`. Listed in
  `sweep-N-comment-style.json`.
- **Instance, not itemised.** Each `tests/`, `tools/`, `docs/` and `dev/` file
  the enumerator returns is an instance too. That makes 2589 files, too many
  for the fold ledger. Rerun the enumerator to list them. The JSON counts only
  the shipped package.
- **Guarded.** No file. No CI check enforces C5. `tests/features.py` measures
  but does not gate.
- **Not applicable.** Generated `.cursor/rules/*.mdc` and binary files have no
  matching suffix and are not read.

**Barrier proposal.** Add a ratchet metric `long_comment_sentences` to
`tests/structure_budgets.json`, recorded at today's count and allowed only to fall.
A hard zero would force rewriting 17k sentences of style-only text.

## Per-file counts, custom_components/
- custom_components/heatpump_optimizer/__init__.py: 6
- custom_components/heatpump_optimizer/accuracy.py: 12
- custom_components/heatpump_optimizer/away.py: 4
- custom_components/heatpump_optimizer/batchmath.py: 4
- custom_components/heatpump_optimizer/battery.py: 4
- custom_components/heatpump_optimizer/binary_sensor.py: 3
- custom_components/heatpump_optimizer/boost.py: 9
- custom_components/heatpump_optimizer/button.py: 2
- custom_components/heatpump_optimizer/climate.py: 3
- custom_components/heatpump_optimizer/comfort_band.py: 6
- custom_components/heatpump_optimizer/comfort_learning.py: 3
- custom_components/heatpump_optimizer/config_flow.py: 52
- custom_components/heatpump_optimizer/const.py: 60
- custom_components/heatpump_optimizer/coordinator.py: 114
- custom_components/heatpump_optimizer/currency.py: 1
- custom_components/heatpump_optimizer/curve_learning.py: 1
- custom_components/heatpump_optimizer/debugger.py: 2
- custom_components/heatpump_optimizer/defrost.py: 21
- custom_components/heatpump_optimizer/device_prefill.py: 11
- custom_components/heatpump_optimizer/dhw_draws.py: 3
- custom_components/heatpump_optimizer/dhw_learning.py: 7
- custom_components/heatpump_optimizer/dhw_planner.py: 39
- custom_components/heatpump_optimizer/dhw_schedule.py: 9
- custom_components/heatpump_optimizer/diagnosis.py: 2
- custom_components/heatpump_optimizer/diagnostics.py: 11
- custom_components/heatpump_optimizer/disinfection.py: 5
- custom_components/heatpump_optimizer/draw_range.py: 11
- custom_components/heatpump_optimizer/drift.py: 4
- custom_components/heatpump_optimizer/driving_grade.py: 2
- custom_components/heatpump_optimizer/duty_legs.py: 4
- custom_components/heatpump_optimizer/duty_switch.py: 6
- custom_components/heatpump_optimizer/early_cutoff.py: 5
- custom_components/heatpump_optimizer/entity.py: 12
- custom_components/heatpump_optimizer/external_heat.py: 6
- custom_components/heatpump_optimizer/flow_lift.py: 9
- custom_components/heatpump_optimizer/flow_meter.py: 1
- custom_components/heatpump_optimizer/freq_control.py: 9
- custom_components/heatpump_optimizer/frontend.py: 2
- custom_components/heatpump_optimizer/grid_fee.py: 9
- custom_components/heatpump_optimizer/heat_curve.py: 5
- custom_components/heatpump_optimizer/heat_energy.py: 5
- custom_components/heatpump_optimizer/inputs.py: 16
- custom_components/heatpump_optimizer/issues.py: 1
- custom_components/heatpump_optimizer/learner_progress.py: 3
- custom_components/heatpump_optimizer/ledger.py: 7
- custom_components/heatpump_optimizer/legionella.py: 10
- custom_components/heatpump_optimizer/manual_plan.py: 3
- custom_components/heatpump_optimizer/mixing_valve.py: 7
- custom_components/heatpump_optimizer/modbus_prefill.py: 1
- custom_components/heatpump_optimizer/name_match.py: 8
- custom_components/heatpump_optimizer/narrative.py: 5
- custom_components/heatpump_optimizer/notifier.py: 1
- custom_components/heatpump_optimizer/off_restore.py: 5
- custom_components/heatpump_optimizer/open_meteo.py: 5
- custom_components/heatpump_optimizer/optimizer.py: 109
- custom_components/heatpump_optimizer/payload.py: 8
- custom_components/heatpump_optimizer/plan_step.py: 1
- custom_components/heatpump_optimizer/power_guard.py: 1
- custom_components/heatpump_optimizer/prefill_offer.py: 4
- custom_components/heatpump_optimizer/presets.py: 5
- custom_components/heatpump_optimizer/price_model.py: 5
- custom_components/heatpump_optimizer/price_tiles.py: 10
- custom_components/heatpump_optimizer/pump_arbiter.py: 39
- custom_components/heatpump_optimizer/pump_mode.py: 9
- custom_components/heatpump_optimizer/pump_schedule.py: 2
- custom_components/heatpump_optimizer/pump_signals.py: 15
- custom_components/heatpump_optimizer/pv.py: 3
- custom_components/heatpump_optimizer/quick_setup.py: 7
- custom_components/heatpump_optimizer/quiet_windows.py: 12
- custom_components/heatpump_optimizer/replay_doc.py: 6
- custom_components/heatpump_optimizer/rooms.py: 3
- custom_components/heatpump_optimizer/running_signal.py: 2
- custom_components/heatpump_optimizer/runs.py: 2
- custom_components/heatpump_optimizer/sensor.py: 32
- custom_components/heatpump_optimizer/services.py: 10
- custom_components/heatpump_optimizer/setpoint_check.py: 2
- custom_components/heatpump_optimizer/silent_mode.py: 2
- custom_components/heatpump_optimizer/slab_seed.py: 2
- custom_components/heatpump_optimizer/snapshots.py: 3
- custom_components/heatpump_optimizer/store.py: 11
- custom_components/heatpump_optimizer/supply_hold.py: 5
- custom_components/heatpump_optimizer/switch.py: 3
- custom_components/heatpump_optimizer/sysid.py: 64
- custom_components/heatpump_optimizer/tariff.py: 33
- custom_components/heatpump_optimizer/thermal_model.py: 93
- custom_components/heatpump_optimizer/topology.py: 15
- custom_components/heatpump_optimizer/wear.py: 4
- custom_components/heatpump_optimizer/whatif.py: 4
- custom_components/heatpump_optimizer/wood_fuel.py: 1
- custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js: 205
