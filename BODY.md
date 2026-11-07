R10-HOTFIX-COP-UNMEASURED (hotfix, owner-reported, user-visible). The Health tab graded the heat pump from "measured COP" samples on installs that cannot measure COP. With no heat input, `flow_meter.cop_evidence` infers COP = model COP x (plan's ask / power reading), and the coordinator recorded that as the measured COP and fed it to the COP health watch, so a hot-water interval drawing exactly its ask stored `compute_cop_dhw(outdoor, tank)` itself. On the owner's install both inputs are now Tuya vendor models ("Estimated Heating Output", "Estimated Power Draw"), so heat over power is the vendor's own fitted COP on every interval: the same self-comparison through the other door.

What changes (owning seam: the COP observation path):

1. **A COP sample is measured only from metered heat over metered power.** `thermal_model.InstallCapability.cop_measured(dhw)`: a heat reading (heat counter, or thermal power entity) over an electrical one (the electric counter for a counter's span, else the power entity), neither a vendor estimate, and for a hot-water interval a heat reading declared to see that circuit. `InstallCapability.cop_sample(heat_kw, dhw)` turns it into the fold's answer per interval: `True` (record and grade), `False` (scale only), `None` (refuse). `coordinator._fold_cop_evidence` gates `MeasuredCop.record` and `_observe_cop_health` on it, together, in one `if measured:`.
2. **The card and the diagnostics say it cannot be measured, and name what would.** `accuracy.cop_observability` publishes `not_measurable` with no heat reading (whatever the draw does) and the new `estimated_inputs` for an estimate on either side; `draw_follows_plan` is retired. `machine_score` returns the new reason `cop_unmeasurable` instead of `cop_watch_learning` ("not enough data yet"). Card: `health.cop_reason_not_measurable` / `estimated_inputs` and `score.reason_cop_unmeasurable` (en, sv) say "COP cannot be measured on this install" and name a heat energy meter or thermal power meter covering the heating circuit, hot water included (and a power meter, neither an estimate); `score.part_machine` says a measured COP is metered heat over a power meter. The observed-COP sensor waits for `metered_inputs` on an estimate.
3. **Estimate versus meter, on both sides.** New options on the metering page: `heat_pump_power_source` and `heat_pump_thermal_power_source` (auto / meter / estimate, default auto) and `heat_meter_sees_dhw` (default off). No Home Assistant signal distinguishes a vendor estimate from a meter (both are `power` sensors), so the marker is config-level. `auto` reads an entity whose id contains `estimat` as an estimate (`const.ESTIMATE_ID_MARK`). Why name detection is sound here, and only here: it is a default the user can override either way, and its only effect is on the COP observation path. A false positive only withholds a COP grade. It never changes a plan or a learner. A false negative is today's behaviour. It catches the Tuya integration's "Estimated Power Draw" / "Estimated Heating Output" entity ids on the owner's install with no action from them. A heat counter outranks the thermal power entity and is read as metered.
4. **A negative or missing heat reading stops the fold.** A configured thermal power that reads no heat this interval (`read_heat_output_kw` turns a negative into `None`, as it does an unavailable one) now refuses with `no_heat_reading` instead of falling into the commanded inference.
5. **Migration: the stale bands are not read.** The watch's memory moves to `cop_baseline_measured` / `cop_health_cusum_measured` (`coordinator._COP_BASELINE_KEY`). The pre-fix `cop_baseline` bands carry no provenance, so no per-sample split is possible, and they are never loaded: every band restarts from measured samples alone, and real samples are never averaged with model ones. A pre-fix store's last COP is not shown as measured either. Why a key rename and not a store version bump: a major bump of the thermal-learning store would reset every learner on a downgrade (`QuarantiningStore` surfaces a newer version and starts afresh). The rename resets only the contaminated field, in both directions: an older release reads no `cop_baseline` and starts that watch empty. The cost is that a genuinely metered install re-learns its bands (20 samples each, `COP_BASELINE_MIN_SAMPLES`).

**Owner ruling, retained.** tvofi, 2026-11-07: "Training on estimated power should be good enough and better than nothing though so retain that". No learner is gated on the estimate marker. The COP scale (`_apply_cop_scale`) and the capacity envelope (`_fold_capacity_envelope`) still fold every interval they folded before, inference and estimates included (pinned: the null-control check asserts `_cop_samples == 1` on the no-heat interval; the Tuya check asserts 3 scale samples over 3 estimated intervals). The new `no_heat_reading` refusal (item 4) is the one change to what reaches them, and it fires only on a configured thermal power that read nothing.

**Learners consuming estimated inputs (information only, unchanged by this PR).** Heat reading: the house heat-loss learner (`_async_learn_house_heat_loss`, via `heat_energy.space_heat_kw` / `close_span`), the lower-floor loss learner (`_async_learn_lower_floor_loss`), the capacity envelope (`_fold_capacity_envelope`, thermal kW), the COP scale (`cop_evidence`), and the COP reference curve's supply-lift judgement (`_cop_reference_curve`). Power reading: the COP scale (`_fold_measured_cop`), the draw-range window (`draw_range.fold` in `_record_accuracy`), the slab propagation (`draw_range.space_draw_kw`), immersion detection (`_detect_immersion`), the capacity envelope, the accuracy tracker's actual cost, the compressor start counter and the frequency map (`_freq_map.observe`). Found by reading every reader of `_flow_bias.heat_output_kw`, `close_span` and `_measured_power` in `custom_components/heatpump_optimizer/`.

Alternatives considered: (a) a store major-version bump. It lost on the downgrade reset described above. (b) Per-sample provenance inside the existing bands. It lost because the old samples have none, so they would still need dropping, and it adds a field per band for no reader. (c) Gating the COP scale on a heat reading too. The owner ruled that out. (d) Name detection alone, without the option. It lost because nothing could override a misread id. (e) Leaving the coordinator helper as a module function. It lost because the decision is install capability, so it lives on `InstallCapability`, pure and testable without the coordinator.

## Head

4ed3f5445: 385264cac (the merge of origin/main 4b5d771bd, 2026-11-07T15:59:52Z, into 41d6984eb) plus the ledger commit, which only deletes three stale pins.

The scoped gate, the mutants and `python3 tests/env_drift.py --all origin/main` ran at 41d6984eb, fork a37c58e5f. Main's delta to 4b5d771bd touches only `dev/`, `.claude/workflows/audit-find.js` and one `tests/closures.json` row for a new harness, none of them in this diff. At 385264cac, `python3 tests/closure.py select` still prints `MODE: SCOPED -- 30 script(s) run, 3 scoped out.` and `python3 tests/structure.py` passes.

## Mutation proof

Each mutant was applied to a detached copy of 41d6984eb (production code identical to the head) and `PYTHONPATH=tests/hastub python3 tests/features.py` was run whole. The rows below are the checks that went red, then the line was restored:

- M1 `if measured:` -> `if True:` (coordinator `_fold_cop_evidence`, record and grade): "no heat input: a hot-water interval whose draw equals its ask records no measured COP ...", "estimated heat over estimated power observes the fitted COP on every interval ...", "metered heat over metered power records a space sample; a hot-water sample only where ...".
- M3 `return None if self.measured_heat and not self.heat_counter else False` -> `return False` (`InstallCapability.cop_sample`): "a thermal-power install with no heat reading refuses the COP fold; with no heat slot the same interval still trains the scale (null)".
- M4 `_estimated`'s id rule -> `return False`: "estimated heat over estimated power ...", "probe_install: an estimate on either side is not a measured COP ...", "cop_observability: no heat input is not measurable, an estimated input is an estimate ...".
- M5 the loader also reads the pre-fix key (`stored.get(_COP_BASELINE_KEY, stored.get("cop_baseline"))`): "a COP baseline stored before measured provenance loads empty with its CUSUM reset; one stored since round-trips".
- M6 `machine_score`'s `if not measurable: return None, "cop_unmeasurable", []` deleted: "a fresh install grades nothing, and says why for each part (#2258): with no heat reading the heat pump is never graded ...".
- M7 `and (self.heat_sees_dhw or not dhw)` deleted (`cop_measured`): "metered heat over metered power records a space sample; a hot-water sample only where the heat meter is declared to see the hot-water circuit".

Every mutant's run exited 1, and the head's run exits 0.

## Null control

The brief's null control, run at the base. The new section was transplanted alone into `tests/features.py` at origin/main a37c58e5f, with no production change, and the whole script was run. Base results:
- No heat slot, a DHW interval with ask == reading (2.0 kW): the base records `cop_baseline {(2, True): [2.5533587538536424, 1]}` and measured COP 2.55, where `compute_cop_dhw(8.0, 48.0)` = 2.5533587538536424. That is the model exactly, from zero heat information. The head records nothing (`{}`, `None`), and the scale still takes the sample (`_cop_samples == 1`).
- Tuya fixture (both entity ids `..._estimated_...`): heat / power observes [3.1, 2.4, 4.05], equal to the fitted COP fed in on every interval. The base recorded the band `{(2, False): [3.18..., 3]}`. The head records nothing, and the same config with both sources set to `meter` records `{(2, False): [3.1, 1]}`, the positive control.
- The base then stopped on the first symbol the fix adds (`InstallCapability.cop_measured`), so the later new checks have no base reading.

## Figures

- Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub ./tests/run.sh` prints `MODE: SCOPED -- 30 script(s) run, 3 scoped out.` and exits 0 at the head (the run's result line is the instrument; `tests/closure.py select` gives the same mode line).
- `python3 tests/env_drift.py --all origin/main`: NO UNCLAIMED DRIFT and NO STALE FIXTURE over the scenarios it lists, with six claims in `tests/golden/claimed_drift.txt`. config_flow was re-recorded: it is float-free and its leaves were only added. The five coord captures each move two string leaves (`reasons.machine`, cop_watch_learning -> cop_unmeasurable), edited by hand and never recorded.
- `node tests/card_drift.mjs origin/main`: only score_open moves (the part_machine text), claimed in `tests/golden/card_claimed_drift.txt`.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED, no budget re-recorded. The coordinator class is paid inside itself (see below).
- `python3 dev/audit/rounds/round3/D5/option_doc_coverage.py`: `option_fields_rendered` 204 -> 207 and `option_schema_keys_rendered` 237 -> 240, one per new option, header updated. `dev/audit/rounds/round4/D6/claims.md` was regenerated by the same gate (45 -> 47 selects).
- Class seams. Rule: every writer of a measured COP sample or health-watch input, `git grep -n -e "_measured_cop.record(" -e "_observe_cop_health(" -- custom_components`. It returns exactly the two calls inside `_fold_cop_evidence`'s `if measured:`, both closed in this diff. `_fold_cop_evidence` is the tail of both the per-cycle fold and the heat counter's span close (`heat_energy.close_span`'s COP arm), so both routes are covered. The rule's own null control: at the base the same command returns the same two calls, ungated.

Structure payment: the coordinator class gained the gate (the refusal, one `if measured:`, the score's `measurable` argument). It was paid by correcting two now-false texts in the class, never by a budget raise: the v4.0.5 ratio comment, since the ratio trains the scale and no longer "reads as efficiency", and `_fold_measured_cop`'s docstring, since "with either [a power entity or a heat counter], COP becomes an observable" is no longer true. Archscore: `tools/audit/archscore/` was not run separately. `tests/arch_score_head.py` ran green in the scoped gate, and `tests/arch_score.py` was scoped out.

## Unpinned sites

Each site is in `custom_components/`, so `mutation-autofix` pins it at the pull request head (`ci-autofix.md`). Each is killed by the check named, in the tests/features.py R10-HOTFIX-COP-UNMEASURED section unless another script is named:

- `custom_components/heatpump_optimizer/accuracy.py:843 GUARD_OFF`: pinned by mutation-autofix; killed by the cop_observability check (`no heat input` must read not_measurable).
- `custom_components/heatpump_optimizer/accuracy.py:845 RETURN_DEL`: pinned by mutation-autofix; killed by the cop_observability check (heat_metered / estimated_inputs).
- `custom_components/heatpump_optimizer/coordinator.py:3311 GUARD_OFF`: pinned by mutation-autofix; killed by the fresh-install grade check (`cop_unmeasurable`), as M6 measured.
- `custom_components/heatpump_optimizer/coordinator.py:5367 GUARD_OFF`: pinned by mutation-autofix; killed by the thermal-power-with-no-heat-reading refusal check, as M3 measured.
- `custom_components/heatpump_optimizer/coordinator.py:5399 GUARD_OFF`: pinned by mutation-autofix; killed by the metered-heat-records check (no sample would be recorded).
- `custom_components/heatpump_optimizer/sensor.py:1693 GUARD_OFF`: pinned by mutation-autofix; killed by tests/entities.py's observed-COP waiting_for check (`metered_inputs`).
- `custom_components/heatpump_optimizer/thermal_model.py:1319 GUARD_OFF`: pinned by mutation-autofix; killed by the no-heat-reading refusal check (a configured thermal power with no reading would record).
- `custom_components/heatpump_optimizer/thermal_model.py:1320 BOOLOP`: pinned by mutation-autofix; killed by the null-control check (a no-heat install would refuse and train no scale).
- `custom_components/heatpump_optimizer/thermal_model.py:1321 RETURN_DEL`: pinned by mutation-autofix; killed by the metered-heat-records check (every metered interval would refuse).
- `custom_components/heatpump_optimizer/thermal_model.py:1414 GUARD_OFF`: pinned by mutation-autofix; killed by the estimate-by-source check (`heat_pump_thermal_power_source: estimate` on a neutral id).
- `custom_components/heatpump_optimizer/thermal_model.py:1416 GUARD_OFF`: pinned by mutation-autofix; killed by the meter-by-source check (Tuya ids marked `meter` record).
- `custom_components/heatpump_optimizer/thermal_model.py:1418 RETURN_DEL`: pinned by mutation-autofix; killed by the Tuya-estimate checks, as M4 measured.

## Red checks

- `mutation` (predicted, `tests / mutation`): the twelve ADDED UNPINNED sites above. `ci-autofix.md`'s `mutation-autofix` answers them by pinning the killed mutants, and `prepr.sh` step 6d is the cheaper detector. It already ran here, before the handoff, at no standing cost beyond the prepr run. The ledger arm's three STALE PINs, `killed_by` entries for the `cop_observability` lines this diff removes, were deleted in 4ed3f5445.

Before the handoff, `tests/env_drift.py` (unclaimed drift and stale fixtures), `tests/structure.py` (the seam map, then class LOC) and `tests/harness_headers.py` (option_doc_coverage counts, D6 claims output) went red locally and were repaired on the branch. Each is the cheaper detector and fired before review. No other detector applies.

## Forward-carry

none

## Friction

none
