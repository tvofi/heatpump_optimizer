## Summary

Round-9 fix-wave group F5.2 — the config flow's texts, menus and number-field
grids, and the climate entity's self-naming. Five findings, five fixes, one
line to a line.

- Fixes #1679 (N-step-grid) — box-mode number fields take step "any".
- Fixes #1685 (N-menu) — the finished quick-setup path leaves the finish_setup menu.
- Part of #1651 (P6) — arms F, E and P at zero.
- Part of #1644 (P2) — the two-zone page shows the derivation warning it computes.
- Part of #201.

## Changes

1. `_number` (#1679): box mode → `"step": "any"`; the increment is kept for
   sliders. Refused arm: min-snapping (measured residue off_grid_derived=2 —
   house_thermal_mass 2.8, house_heat_loss_coefficient 0.112 are arbitrary
   derived floats that cannot be grid-aligned; RANGE_SLAB_THERMAL_MASS's min
   0.1 is derive's documented floor). The S7 SWEEP.md names step="any" as the
   fix shape, choice left to the fixer.
2. finish_setup menu (#1685): `quick_setup` is offered only while
   `CONF_BUILDING_STRUCTURE` is not stored. The questionnaire path stores the
   same key, so its menu drops the re-offer as well — defensible, the user
   already answered the questionnaire. Every pre-existing
   `offers_finish_setup` pin sits on a flow that never stores the key and
   passes unchanged (the lane re-ran green).
3. D4-s2-01 (P6 arm F+E): the nine device_prefill field labels and
   descriptions copied verbatim from `options.step.modbus_prefill` into
   `config.step.device_prefill`, and the three error codes
   (`silent_mode_window_too_short`, `flow_target_needs_two_zone`,
   `prefill_device_unreadable`) into `config.error`, in all three catalogues
   (strings.json, translations/en.json, translations/sv.json). The one
   deliberate wording divergence between the twins (device-route "The heat
   pump's X sensor" vs options' package phrasing, #1262) is pinned by the
   labels-copy check (labels must match, descriptions only presence).
4. D4-s2-06 (P2): `{preset_warning}` appended to
   `options.step.thermal_model_zones.description` in all three catalogues.
   Disposition: config expert pages render `vol.Required(default=...)`
   defaults, never derived stored values, so no overwrite is possible there —
   out of scope by the instrument (options steps only); no code change.
5. D10-s2-01 (P6 arm P): the climate entity gains
   `_attr_translation_key = "heat_pump_optimizer"` (its pinned
   `entity_id = "climate.heat_pump_optimizer"` is unchanged);
   `entity.climate.heat_pump_optimizer` name + preset_mode states (auto,
   economy) in strings/en/sv; icons.json block (default mdi:thermometer,
   auto mdi:autorenew, economy mdi:leaf); quality_scale.yaml entity- and
   icon-translation rows/comments updated. comfort/boost are HA-standard
   (exempt). entities.py: climate joins the named-entities roster; its object
   id is exempt from the v5 scheme (legacy pinned id).

## Failing-test-first

61330e0b — 23 of 492 checks fail across the five findings, null controls
pass (run/failing-test-baseline2.txt). Fix commit 1938fc88 turns the lane
492/492.

## Mutation proofs

Driver: run/mutation-driver.log (one fix line reverted at a time; applied
assertion on every mutant; worktree verified clean after). First driver run
was VOID — its `docker exec` lacked `-i`, the mutation heredocs never reached
python3, and no mutant was applied (green-on-green); outputs deleted, script
fixed, re-run.

- M1 `_number` box step back to the increment → tests/config_flow_steps.py
  2 of 492 FAILED: "_number runtime passes min/max and explicit BOX mode
  with step \"any\" (#1679…)", "a box-mode field's step is \"any\": every
  real value renders selectable".
- M2 finish_setup menu offers quick_setup unconditionally → 1 of 492 FAILED:
  "walking the quick path to its end lands on a menu without it".
- M3 strings.json dhw_min_temperature label+description deleted → 3 of 492
  FAILED: labelled / description / label-copy (1 unlabelled:
  ['dhw_min_temperature']).
- M4 en.json zones description loses "{preset_warning}" → 1 of 492 FAILED:
  "the zones description carries the warning its step computes, in en.json".
- M5 climate.py `_attr_translation_key` deleted → tests/entities.py aborts
  ("AttributeError: 'HeatPumpOptimizerClimate' object has no attribute
  '_attr_translation_key'") and tests/config_flow_steps.py 5 of 492 FAILED
  (names-itself; preset names in strings/en/sv; preset icons).

## Figures

All measured at the merge base 12b0df68 and at this head, in the hpo-ci
container (step_grid on the host — pw-browsers are macOS binaries).
Artifacts under fix-r9-f5-exports/run/.

| instrument | base 12b0df68 | head |
|---|---|---|
| P6 arms (p6_arms_fep.py, arms verbatim from aa2026b7) | universe=15, F=54, E=9, P=8, offered=4 | universe=15, **F=0, E=0, P=0**, offered=4 |
| D4-s2-01 prefill_config_strings | 9 unlabelled + 9 no-help + 3 untranslated errors per catalogue | **0 / 0 / 0** (en and sv); options twin 0 |
| D4-s2-01b prefill_after_save (open seam, NOT fixed) | after_save_leaks=1, config_distinct=1, options_distinct=2 | unchanged 1 / 1 / 2 |
| D4-s2-05 step_grid (Chromium stepMismatch) | off_grid_defaults=8, off_grid_derived=4, sliders=0 | **0 / 0** / 0, out_of_range 0 |
| D4-s2-06 preset_warning | 6 unwarned per language | unwarned **0** (10 warned per language, en and sv) |
| D4-s2-07 quick_menu | repeated=1, identical=1, null=0 | **0 / 0**, null 0 |
| D10-s2-01 climate_presets | untranslated 2, uniconed 2 | **0 / 0** (strings, en, sv) |
| D2-s1-51 dhw_sweep_outdoor (other lane, open) | off_total_cold=14 of 14 | unchanged |
| D12-s1-01 state_seed (other lane, open) | A_omitted dhw_init_mismatch=23 | unchanged |
| D14-s1-02 p6_keys (other lane, open) | p6_unproduced_reads=2 | unchanged |
| P2 enumerator, dynamic | derive_preset_disagree=0, prefill_refused_or_missed=0, null 0/20 | identical 0 / 0, null 0/20 |
| P2 enumerator --seams | two_zone=0, dhw=13, wood=10 | identical seam list (only this diff's line shifts in config_flow.py; no new seams) |
| selector_min_off_step_grid/enumerate.py | 0 seams | 0 seams — dead instrument at both refs |

Instrument dispositions:

- P2 enumerator: the class's two_zone seam is already 0 at the merge base
  (fixed on main since the round-9 audit baseline 1936d5ca). Its perturbation
  arm cannot run at this ref — the anchor line
  (`two_zone=bool(current.get(CONF_UPPER_FLOOR_THERMAL_MASS))`) no longer
  exists, identically at base and head; disclosed as an instrument
  limitation. This diff's P2 deliverable is the zones-description warning,
  measured by preset_warning above.
- selector_min_off_step_grid/enumerate.py matches zero
  `NumberSelectorConfig(...)` sites at base and head — it keys on literal
  `min=`/`step=` constructor keywords, but the package builds selector dicts
  (`NumberSelectorConfig(**config)`). The executed enumeration of the class
  is the step_grid harness (row above).
- state_blind_menu_reoffer greps re-run at head: `async_step_finish_setup`'s
  menu is now the site conditioned on prior state; the options-flow "missed
  quick setup" menu remains the guarded counterpart. Disposition table
  unchanged, N=1 instance fixed.

Null controls: quick_menu null_repeated_options=0; P2 null_control_disagree=0
of 20; D2's F+5 arm 0 of 7 (the instrument's own).

## Golden drift

`config_flow` claimed in tests/golden/claimed_drift.txt: selector step "any"
and the post-quick-setup menu_options move — structure only, float-free, 120
leaves, every one `selector.config.step` → "'any'" plus the captured menu.
env_drift --all verdict CLAIMED, NO UNCLAIMED DRIFT, NO STALE FIXTURE at the
merged head (run/env-drift-final.txt); fixture re-recorded in strict mode
(run/golden-record2.txt). The roster's "Golden drift plausible: not
expected" is contradicted by the measurement; claimed with reason. The
branch carried the claim stamped 6.7.8 (its own tree's VERSION) until the
origin/main merge brought the v6.7.9 stamp it is now keyed to.

## Gates (final head 3dadb916 = 7b238090 + merged origin/main; VERSION 6.7.9)

- Scoped gate at the pre-merge head 7b238090 (run/gate-final.log):
  `MODE: SCOPED -- 10 script(s) run, 17 scoped out` — dropping the branch's
  resume note flipped it out of the forced FULL. One failure:
  - harness_headers: TimeoutExpired — round-4 D7
    sysid_estimator_frontier.py exceeded the 240s per-harness CI budget
    under the gate's parallel lanes on this Mac. Attributed, not this diff:
    the same harness PASSES quiet at the merge base (rc=0,
    run/base-harness_headers.txt) AND quiet at this head (rc=0, 15 RESULT
    lines, run/sysid-head-quiet.txt) — a gate-parallelism load artifact of
    this box, not a code difference. CI's hardware runs it inside the
    budget.
- The FULL-gate run (run/gate-head.log, forced by the then-tracked resume
  file) surfaced two solver-measurement failures, both attributed at the
  merge base:
  - optimality 1 of 84: "the production stop rule (ftol) buys a materially
    better plan [ftol 1e-6 61.28 vs loosened 1e-3 61.09 (-0.32% gap, bound
    0.1%)]" — reproduced IDENTICALLY (same figures) at the merge base
    (run/base-optimality.txt): pre-existing, not this diff; this diff moves
    no solver input.
  - stress 1 of 87: "no scenario got dramatically cheaper without a
    re-record [winter/pv at 28.6x vs recorded 109.5x]" — measured-vs-recorded
    cost ratios are machine-sensitive, and the SAME check fails at the merge
    base on this box with a different scenario (flat/1z/dhw 12.2x vs
    recorded 47.9x), alongside the kernel-CPU-per-call timing check
    (base-stress.txt, 2 of 87): environmental drift of solver-cost
    baselines on this Rosetta container, not this diff. Config-flow text
    cannot make PV 3.8x cheaper.
- On the merged head 3dadb916 (base = origin/main 5b903344):
  - tests/config_flow_steps.py: ALL 492 checks PASSED (run/lane-final.txt).
  - entities.py: ALL 1979 ENTITY CHECKS PASSED — no orphan; the branch's
    resume note is dropped at the freeze.
  - structure.py: STRUCTURE RATCHET PASSED (no budget moved).
  - env_drift.py --all against the new base: `CLAIMED config_flow` (120
    leaves), `NO UNCLAIMED DRIFT: 56 scenario(s)`, `NO STALE FIXTURE`, exit 0
    (run/env-drift-final.txt). The merge carried main's v6.7.9 stamp, so the
    claim's `claims-for: 6.7.9` matches the tree's VERSION (6.7.8 was the
    pre-merge tree's version — stamped for its own tree, per claim-files.md;
    the merge re-keyed it).
  - typing ruler --mypy (CI-pinned toolchain per tests.yml's
    --require-hashes --no-deps recipe, in a container venv): ALL 9 PASSED,
    errors did not grow, type_ignores did not grow. The step-"any" literal
    needed no new ignores.

## Open seam reported, not fixed

prefill_after_save (D4-s2-01b): after saving the device pre-fill, the
wizard's next page renders with the entry's data (after_save_leaks_into_entry=1,
config_distinct_destinations=1, options_distinct_destinations=2), unchanged
at head. Not in any sweep seam list. Probe:
`PYTHONPATH=tests/hastub python3 tools/audit/round9/D4/s2/prefill_after_save.py`.
Left for the orchestrator to disposition.

## Class issues

"Part of #1651 (P6); Fixes #1679 (N-step-grid); Part of #1644 (P2); Fixes
#1685 (N-menu)" + Part of #201.

## RCA carry-in (P6)

The universe is the nine pre-fill preview fields; the config error table owes
prefill_device_unreadable, flow_target_needs_two_zone and
silent_mode_window_too_short; the climate key needs auto/economy in all three
catalogues plus icons.json and the name block. Control: the P6 prototype arms
F, E and P at zero (aa2026b7) — delivered at head.

## Handoff notes

- The branch's handoff/round9/fix/resume/F5.2.md is dropped at the freeze
  commit: a tracked-but-unclassified handoff file is an entities orphan and
  forces MODE: FULL. F1.2's precedent verified — its PR-merge tip 96199690
  carries an empty handoff/ tree. This body therefore lives in the pull
  request itself and in the seat's scratch mirror, not in the tree.
- origin/main is merged into the hand-off head (3dadb916); the only
  conflict was tests/golden/claimed_drift.txt, resolved per the file's own
  merge instruction: keep the claims that describe THIS branch's diff.
- The gate regenerates tools/audit/round4/D6 artifacts; they were restored
  (`git checkout -- tools/audit/round4/D6`) after every gate run.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
🤖 Generated with [Claude Code](https://claude.com/claude-code)
