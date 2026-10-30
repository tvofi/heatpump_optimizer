CLOUD PROBE seat for tvofi/heatpump_optimizer, topic r10-live-plan-energy, at head cc930cdd1a3cfb005ba7ec557f4451ff5e53e364. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: a read-only probe. Measure what the brief below asks against the tree at cc930cdd1a3cfb005ba7ec557f4451ff5e53e364 (`git fetch origin cc930cdd1a3cfb005ba7ec557f4451ff5e53e364`); change no tracked file and send no code to any ref.
Output: write your result as a body file and run `bash tools/audit/seat/body_push.sh r10-live-plan-energy <result.md>`, which pushes refs/heads/handoff-body/r10-live-plan-energy; that push is the return signal. A return push carries only your own result tokens.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
INVESTIGATION PROBE seat (read-only for production code; harness only), topic r10-live-plan-energy. This is a second live user finding (tvofi, 2026-10-30), at expedite priority. It is separate from the away-override defect, which the hotfix group R10-HOTFIX-AWAY-LIVE is fixing; do not touch that seam.

The owner's words: "Even if away mode had not been on, having an almost day long heating slot using 67kW while the temperature already is 22 degrees with an 18,5 target and 17-21 comfort band seems way off."

Facts from the owner's live diagnostics, about 18:50 local on 2026-10-30. Only the needed fields are restated here; never ask for or commit the bundle.
- Plan: fresh and optimal. The space plan is 96 steps (24 h at 15 min) holding ONE contiguous slot, total_energy_kwh 66.71 and total_cost 152.84 SEK. space_reason is preheat_weather. The current step is off.
- Config now: target_temperature 18; comfort day 19.5, night 18.5; min_temperature 18; max_temperature 21; comfort_weight 2.0; mode auto; two_zone_mode on (upper floor radiators, lower floor underfloor heating, upper_floor_area_ratio 0.5, inter_zone_heat_transfer 0.5); confidence_margins_enabled and mold_guard_enabled true; optimization_interval 15.
- Model config now, with the setup values in brackets:
  - house_heat_loss_coefficient 0.4 [0.15]
  - lower_floor_heat_loss 0.2 [0.07]
  - upper_floor_heat_loss 0.13 [0.08]
  - lower_floor_thermal_mass 1.0 [5.0]
  - upper_floor_thermal_mass 1.26 [3.0]
  - slab_thermal_mass 1.0 [2.0]
  - slab_heat_transfer 1.5 [0.8]
- Learned: house_heat_loss_effective 0.6409 kW/K over 535 samples; house_heat_loss_scale 1.2356; lower_floor_loss_ratio 1.943 over 345 samples; measured COP 3.76 (cop_scale 0.999, 3 samples).
- Sensors over 645 samples: indoor min 18.0, median 19.7, max 21.1 (the owner reports 22); outdoor min -2, median 6, max 12. The indoor entity was switched from the heat pump's T6 sensor at setup to a room BTHome sensor; T6 is now the lower-floor entity.

Question: why does the solve plan about 67 kWh electrical over 24 h for a house at about 20-22 °C, with a comfort band of 18-21 and outdoor around 6 °C? Is that a defect?

Arithmetic to test first: 0.64 kW/K × about 14 K is about 9 kW of heat, which at COP 3.8 is about 2.4 kW electrical, or about 57 kWh per day. So the energy may follow from the learned heat loss. The real question is whether 0.64 kW/K is plausible for a house that holds 20-22 °C, and how the learner arrived at it. Also check the configured coefficient raised from 0.15 to 0.4 and the ×1.24 scale on top.

Work in a detached worktree at origin/main. Rebuild this house's solve through the production path, the way coordinator._solve_hubs does: OptimizationConfig.from_mapping, then the two-zone ThermalParameters from this config, then HeatPumpOptimizer.optimize. Use a 24 h late-October horizon with outdoor around 6 °C and a realistic SE3 price curve.

Arms, each reporting kWh, slot count and the room and floor trajectories:
(1) as configured, with indoor 22;
(2) indoor 20;
(3) the setup heat-loss values;
(4) the learned effective loss replaced by the configured 0.4 with no scale;
(5) single-zone, to isolate the lower floor;
(6) confidence margins and the mold guard off;
(7) null control: flat price, to separate price-driven preheat from comfort-driven heat.

Then read the heat-loss learner (house_heat_loss_effective, house_heat_loss_scale, lower_floor_loss_ratio). Check whether its samples could be biased upward: DHW or defrost energy counted as space heat, solar or internal gains ignored, sensor-switch history, or a lower-floor ratio applied on top of an already effective loss. Cite path:line for each.

Classify the cause as one of:
(a) the learned heat loss is inflated, naming how;
(b) the configured model parameters are implausible, so the plan is consistent with what the user set;
(c) two-zone lower-floor heat, from a cold floor sensor or slab, drives the energy;
(d) preheat_weather charges for a forecast cold spell, which is correct behaviour, with the weather measured;
(e) the comfort pull or margins hold the room above the band;
(f) other.
If it is a defect, give a minimal fix brief in prose and the owning roster group: search origin/handoff/audit-r10-roster for the learner's file. Name the diagnostics fields that would settle anything you cannot.

Commit nothing. Put the report, with its harness inline and its measured table, on handoff-body/r10-live-plan-energy via bash tools/audit/seat/body_push.sh r10-live-plan-energy <file>.
