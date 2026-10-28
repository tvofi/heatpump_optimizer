Design review: revise 3f6990ecb0121e0cca9dcb69c6159d33459b6838 architecture-unsound

Reviewed: `dev/programme/designs/R10-UX-HEALTH.md` at `design/R10-UX-HEALTH` 3f6990ecb, round 1 of 3. I read it from a detached worktree at that SHA, and the ref has not moved. Code was read at the note's base `6d86acc90`. `git diff 6d86acc90 origin/main` (f844df1fe) is empty for the card, sensor.py, services.py, strings.json, inputs.py and tests/card.mjs. Code was also read at R10-COP-GATE part 1's handoff `d3ce1d33f` (merge base edd7e0e14, body `handoff-body/r10-cop-gate` 4f7479168). There is no earlier design-verdict for this group. Token count: not reported by this harness.

## What I measured and found as the note states

The note's figures hold. I re-derived them with my own scripts (`h/labels.py` in the seat directory) and by grep at 6d86acc90:
- **Labels.** The options flow has 44 `*_entity` fields. The card labels 11 of them, so 33 have no label, and no card key lies outside the set.
- **Read keys.** The `InputReader.read*` keys come to 29, counting `FLOW_INLET_KEYS`. Every one is an options field, so arm A's backend subset arm is sound.
- **Greps.** The raw-key `replace` gives 1 hit and `Number(attrs.` gives 4. `sticky` and `scroll-margin` give 0.
- **Health COP row.** `healthModelHtml` (card ~9405-9411) shows `model_cop_normal` whenever `cop.scale` is finite.
- **Debug collection.** `debug_collect` has `status` and `start` actions, and `start` on a final collection restarts it (debugger.py:696-718).
- **Finalize button.** `DebugFinalizeButton` publishes `waiting_for` only while unavailable.
- **ObservedCOPSensor.** It is unavailable whenever `_waiting_for` is set (`_WaitsForEvidenceMixin.available`, sensor.py:403), and HA then drops its attributes. So the note rightly rejects reading the COP row from it.
- **Sibling designs.** Among the open `design/*` refs, CONFIGFLOW-PAGES, LIVESTATE and ORCH-MACHINERY touch neither the card nor strings.json.

## Revise points

A. **architecture-unsound: arm E designs against a contract that COP-GATE part 1 does not publish. Its names differ, and its boolean loses four of the five states** (note, arm E, line 41, and the "ux-cop-contract" carry, line 103). The note was written before part 1 existed, and it invents `cop.observable` (bool) and `cop.last_refusal` on `ModelStatusSensor`. At `d3ce1d33f`, part 1 publishes these:
   - In the learning view (payload.py `LearningView`): `cop_observability`, one of `heat_metered`, `draw_follows_plan`, `not_measurable`, `awaiting_draw_evidence` or `no_electric_meter` (`accuracy.cop_observability`). Beside it are `cop_refusal` (a `COP_REFUSED_*` or `SPAN_REFUSED_*` code, verbatim) and `measured_cop_at` (when the latch folded, the D15 seam-2 age).
   - On `ObservedCOPSensor` only: the attributes `observability`, `last_refusal` and `measured_at`. That sensor goes unavailable with `waiting_for: heat_meter` exactly when `not_measurable` holds, so the card cannot read any of the three in the state item 5 names.
   - `ModelStatusSensor.cop` is unchanged: `scale`, `samples`, `alarm`, `watched_buckets`.

   A boolean `observable` folds `no_electric_meter` (a counter install with no electric counter, part 1's answer to carry 8) and `awaiting_draw_evidence` into one of two buckets. The note also says nothing of `measured_at`, though the roster's D15 carry asks for the latch's time to be shown.

   **Fix wanted:**
   - Re-cut arm E to read `ModelStatusSensor`'s `cop` attribute with part 1's own names and enum: `observability`, `last_refusal` and `measured_at`.
   - Re-word the carry to R10-COP-GATE part 2 (`r10-cop-gate-p2`, in flight). Its job is to copy the three existing learning-view keys into that dict in `sensor.py`. It adds no new state and no boolean.
   - State the value precedence over the enum:
     - `alarm` first.
     - Then `not_measurable` or `no_electric_meter`, which render a dash and their words, **ahead of** "Normal" even when `watched_buckets > 0`. Folds made before the gate turned the ratio into no COP do not vouch for it now.
     - Then "Normal (scale)" only while `watched_buckets > 0`. On a counter install, `span_open` beside a measured COP stays "Normal" (carry 11's control).
     - Otherwise a dash plus `last_refusal`, `awaiting_draw_evidence` or `cop_watch_learning`.
   - Render `measured_at`'s age on the row while a latch exists.
   - Add a failing test with `observability: "not_measurable", watched_buckets: 3` that asserts no "Normal".
   - Add a null test with `observability: "heat_metered", last_refusal: "span_open", watched_buckets: 3` that asserts "Normal".

B. **class-open: a second Health site renders the COP state, and the note leaves it static** (card `HEALTH_WAITING` at ~9222, rendered by `healthLearningHtml` at ~9335-9338; string `health.learn_cop_why` at card:123 and 889). It reads "Needs a power meter on the heat pump, then some running time". After part 1, `ObservedCOPSensor` is unavailable for three reasons: `measured_power_entity`, `heat_meter` (`not_measurable`) and `first_cop_sample`. The learning block shows this one fixed sentence for all three. On a `not_measurable` install, which has a power meter, the sentence is false. The note's sibling enumeration (lines 62-66) has no COP-state class.
   **Fix wanted:**
   - The learning block's `cop` row takes its words from the same reason function as arm E's row. It reads `ModelStatusSensor.cop`, because the observed sensor's own attributes are dropped while it waits.
   - Add a sibling-site command for COP-state renderers: `grep -nE "learn_cop|model_cop|_learning_observed_cop" <card>`.
   - Add a failing test on a `not_measurable` fixture: no "Needs a power meter".

C. **architecture-unsound: arm A's one stated rule does not hold for sv, and the sv source is ambiguous for the note's own failing-test key** (note, arm A, line 20). Measured over `options` in `translations/sv.json`:
   - Optional fields are suffixed " (valfri)" (11) or " (valfritt)" (16), never " (optional)". Under "strip the trailing ' (optional)' and nothing else", the sv equality either fails or puts "(valfri)" into card labels.
   - `wood_tank_top_entity` and `wood_tank_bottom_entity` carry two different sv labels, and en carries one. In `step/building/sections/wood` they are "Vedtankens toppgivare" and "Vedtankens bottengivare". In `step/quick_setup` they are "Givare, toppen av vedtanken" and "Givare, botten av vedtanken". So "the sv.json label" is undefined for exactly the key arm A's failing test uses.
   - `translations/sv.json` is not in `files`, so the fixer cannot normalise it at the source.

   **Fix wanted:**
   - State the strip rule per language, including the sv suffixes.
   - Name which step is canonical when a field appears on more than one page, for example the field's own page over `quick_setup`, with the equality arm asserting that rule.
   - Or, as **decision: orchestrator**, add `translations/sv.json` to `files` so the two sv labels can be made one.

D. **harness: arm H's stub does not have the service's response shape** (note, evidence plan, line 75). `handle_debug_collect` (services.py:1217-1223) returns `{"debug": {<entry_id>: status}}`. With `returnResponse`, `hass.callService` resolves to `{context, response: {...}}`. A stub returning `{final: true, rows: 40}` passes a card that reads the wrong level, and fails a card that reads the right one.
   **Fix wanted:**
   - The stub returns `{response: {debug: {[entry_id]: {active, final, rows, bytes, started_at}}}}`, mirroring `debugger._IDLE` and `status()`.
   - Add one case where the response holds a different entry id only, which must render "off" and not "finished".

## Decisions routed (not revise points)

- **decision: orchestrator.** Point A's carry must reach R10-COP-GATE part 2's brief now, under finding-propagation.md. Part 2 is in progress (`r10-cop-gate-p2`, per part 1's RESUME), and the note's line-103 carry exists only on this unmerged design ref. The same applies to `machine_drivers` (arm F). That name has to be agreed with part 2, which owes carries 6, 7 and 14 (the `envelope_drivers` mirror).
- **decision: orchestrator.** Arm F's "driving scale". The note already routes it.
- **decision: orchestrator.** Arm H's `button.py` lines. The note already routes them, and I agree with leaving `button.py` untouched.

## Notes for the fixer

- Carry: R10-UX-HEALTH (item heat-loss-clause). Arm D widens the demand-overbook carry from "no power meter" to "no power meter and no heat meter". Before building, confirm with `dev/audit/harnesses/r10_demand_overbook.py` that a heat reading makes the scale observable. Otherwise keep the carry's own predicate.
- Carry: R10-UX-HEALTH (item enum-strings). Give each of the five `cop_observability` values its own `health.cop_reason_*` string, in en and sv. `awaiting_draw_evidence` is also a `COP_REFUSED_*` code (accuracy.py:798), so one string covers both readings.
- Carry: R10-UX-HEALTH (item archscore-base). The note's `card_clone_copies` 108 and `card_dead_definitions` 0 were not re-measured by this review, because `vector.py` had not returned on the loaded box. Re-take both at your merge base.
