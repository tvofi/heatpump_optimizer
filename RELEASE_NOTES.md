## v7.1.14

**Patch stamp: duty-switch restart learning part B, mode before supply on, ECL110 MQTT off-neutral, and user-docs corrections; the rest is tooling.**

### #3530 The pump arbiter writes the step's mode ahead of a supply switch-on (R10-MODE-BEFORE-SUPPLY-ON)

The arbiter now writes the step's mode before it switches the supply on (#3420 part E).

### #3534 The ECL110 MQTT off state is neutral (R10-ECL110-MQTT-OFF-NEUTRAL)

The ECL110 topic publish drops its dead early return; the off arm needs no topic guard of its own.

### #3524 The duty-switch learner publishes p and whole-episode n (R10-DUTY-SWITCH-RESTART-LEARNING, part B)

The learner publishes the restart probability and the whole-episode count, with N_ON pinned as a decayed weight.

### #3513 User docs verified (R10-USER-DOCS-VERIFY)

Docs now state the mold-safe range as uncapped with the floor held at the target, and a two-probe average for a stratified combi store as an estimate of its mean.

### Developer tooling, CI and audit machinery only

#3515, #3535, #3492, #3377, #3510, #3533, #3498, #3522, #3503, #3523.

### Record only

#3537, #3527 (delivery rows, autofix).


## v7.1.13

**Patch stamp: 24 merges since v7.1.12, stamped on the owner's order.** The user-visible changes are a duty-switch learner that records how the pump behaves after a hot-water-to-space mode write, and a hot-water write that now respects the entity's range and the user's own charge limit.

### #3461 The duty-switch learner observes mode switches and restarts (R10-DUTY-SWITCH-RESTART-LEARNING, part A)

Built from a finding by Bankaifan on an alpha innotec LWDV 91-1/3: after a mode write from hot water to space heating the compressor can stop within seconds and stay off for about eight minutes. A new learner, beside the start counter, observes when the compressor runs, records each mode write with its context, estimates per direction how often the compressor stops and for how long, keeps the estimate in its own per-pump store and publishes the counts and durations as sensor attributes. Nothing reads the estimate yet: plans and writes are unchanged until the later parts land.

### #3497 The hot-water write respects the entity's range and the charge limit (R10-OUTSIDE-DISINFECTION-SETPOINT, follow-up to #3452)

The entity's own minimum now outranks a caller's ceiling, so a write below the minimum on the step is no longer refused. With no cycle running, the everyday set-point is written on the step at or below the charge limit instead of rounded up past it. The disinfection-floor notice rounds its floor on the step and never above the tank's hard maximum, so its Fix cannot be written back below the floor.

### #3509 Card Health text test (R10-HOTFIX-CARD-HEALTH-TEXT, follow-up to #3485)

Browser test coverage for the Health and Advisor labels; no change to the card itself.

### Developer tooling, CI and audit machinery only

#3507 (closeout prep), #3518 (mutant run on Darwin hotfix), #3493 (carry audit, part 5), #3502 (Mach scorecard), #3484 (opener unblock hotfix), #3506 (main prepr read-set hotfix, part 2), #3448 (review dispatch residue, part 1), #3428 (plan page residue), #3500 (gate push ratchet), #3430 (architecture docs), #3501 (open-PR figure refresh hotfix), #3479 (prepr residue).

### Triage and delivery rows (record only)

#3382, #3386, #3387, #3388, #3390, #3391, #3381 (triage batches); #3504, #3517 (delivery rows, autofix).

## v7.1.12

**Patch stamp: 40 merges since v7.1.11, stamped on the owner's order.** The user-visible changes are a hot-water learner that no longer books the dip after a charge start as a draw, a price outage that no longer stops steering while the last prices still cover now, hot-water disinfection written at its own temperature, the optimizer's off switch restoring the pump's space set-point, a climate entity that works on both old and new Home Assistant cores, a dashboard card whose Health labels survive ad blockers, and a rebuilt product page.

### #3444 A hot-water charge start is not booked as a draw (R10-OUTSIDE-DHW-CHARGE-SETTLE)

Built from outside pull request #3434 by Bankaifan, with thanks. A hot-water charge start drops the tank reading by 3 to 5 K within minutes, and the draw statistics used to book that dip as a draw, which inflated the heavy-day figure the planner reads. The dip is now treated as part of the charge: it is bounded per charge, and a later rise once the charge stops takes back what was booked. Real draws are not taken back.

### #3454 A failed price fetch no longer stops steering while the last prices still cover now (R10-OUTSIDE-PRICE-OUTAGE-LAST-VALID)

Built from outside pull request #3437 by Bankaifan, with thanks. A failed price fetch used to make every entity unavailable and stop steering, even though the last fetched prices still covered the current step. Now, as long as a price is known for the current step, the failure is logged as a warning, the `price_feed_stale` repair is raised and the update carries on. Once no published price covers now, the update fails as before, and the repair stays until a fetch succeeds. A refused token always fails and raises no repair.

### #3460 The climate entity works on Home Assistant 2026.11 and on older cores (R10-OUTSIDE-CLIMATE-NATIVE-TEMP)

Built from outside pull request #3443 by Bankaifan, with thanks. Home Assistant 2026.11 serves the climate temperatures under new native names and logs every class that still defines the old ones. The climate entity now holds its logic under the native names and adds the old names only on a core whose base class lacks the native ones, so it works from the supported floor 2025.2.0 upward and logs nothing on 2026.11.

### #3452 Disinfection cycles are written at the disinfection temperature (R10-OUTSIDE-DISINFECTION-SETPOINT)

Built from outside pull request #3439 by Bankaifan, with thanks. With Pump duty control writing the hot-water set-point, a disinfection cycle used to write the everyday set-point (55 with the stock 55/60 pair), so the pump's own thermostat ended the cycle below its target. The cycle now writes its own temperature, capped at the tank's hard maximum of 70 C and bounded by the entity's range. The set-point repair no longer stands permanently against the optimizer's own write during a cycle.

### #3404 Turning the optimizer off restores the pump's space set-point (R10-ARBITER-OFF-RESTORE)

Turning the optimizer off, and every unload, now writes the space set-point that Pump duty control had changed back to the person's own baseline. The baseline is saved before the first write, a value the person sets between writes becomes the new baseline, and the restored value is kept within the entity's range and step. This replaces the earlier behaviour where off wrote nothing for that set-point. `docs/configuration.md` describes it under Pump duty control.

### #3469 Optional controller limits bound the water set-point (R10-WATER-SETPOINT-FEEDBACK, part 3)

Two new optional entity options on the options page that carries the space set-point unit, shown for a water unit, name the controller's own lower and upper limit sensors for the written set-point. An upper limit that leaves no room above the off value for a heating write is ignored, so a placeholder or misplaced sensor can no longer make the loop write the off value or lower. The options have labels in every translation and in the card.

### #3468 A heat-counter span survives a hot-water cycle (R10-OUTSIDE-LEARNER-ROBUSTNESS)

Part 1 of outside pull request #3435 by Bankaifan, with thanks. A heat-counter span used to be thrown away when a cycle inside it ran hot water. Where the counter is declared to see hot water, the mode dwell observed the charge, and no immersion element or pump backup heater is on, the charge is now removed from the span by its own counter steps and the rest is used for learning. A span with an unaccounted step still reads no space-heat figure.

### #3478 The heat pump switch follows the step it lands in (R10-OUTSIDE-SUPPLY-STALE-STEP)

Thank you to Bankaifan for pull request #3457. The cycle cuts its action at the solve, then waits on system identification, the fuse advisor and the price tile before writing the heat pump switch, so a write could land in the next step and stand against the plan for up to one plan step. The switch is now written for the step it lands in, falling back to the solved action where there is no plan for that step. The displace value and set-point are not changed by this.

### #3442 Stored heat is valued at the part-load rate (R10-SAV-VALUATION-RESIDUE)

Under a part-load derate, the end-of-horizon value of stored heat and the cost of deferred energy bought it back at a COP with no draw. Both now use one refill law, which spreads the heat evenly over the cheapest quarter of the horizon. With no derate the figures are unchanged, bit for bit.

### #3485 Health and Advisor labels survive ad blockers (R10-HOTFIX-CARD-HEALTH-TEXT)

The dashboard card's Health and Advisor labels lost their layout box when a content blocker's generic hide rules for `adv-text` and `adv-label` applied inside the card. Every `adv-*` class in the card is renamed to `fact-*`, which no tested filter list names. The change also carries the earlier fix for Health and Advisor text ink in a card whose dark mode is off.

### #3458 Product page redesign (R10-PRODUCT-PAGE-REDESIGN)

The product page is rebuilt around one illustrative day drawn by a generator, a scroll story over it, a first-week timeline and a control-path chooser in place of the table. Touch targets are at least 40 px, the page reads in order with styles off, and it can be operated by keyboard.

### Developer tooling, CI and audit machinery only

#3475 (mutant run fork cap), #3431 (suite environment residue), #3494 and #3464 (standing contracts, part 2), #3462 (GitHub read residue, part 2), #3488 (prepr word-count padding hotfix), #3471 (tick residue, part 2), #3476 (introduced-reds barrier), #3487 (main prepr scope hotfix), #3470 (train residue, part 2), #3473 (gate redispatch loop hotfix), #3465 (relay arm order), #3477 (replay class cut hotfix), #3355 (pull request body contract, part 3), #3482 (self-test scope union hotfix), #3455 (fixer spelling corpus, part 2), #3449 (Dependabot #3414 compatibility, part 2), #3467 (CodeQL pull request paths), #3463 and #3438 (restore base skew hotfix and its root cause), #3474 (pusher census hotfix), #3445 and #3450 (review dispatch residue, parts 4 and 3), #3472 (roster carry exact match), #3466 (vendor-name census fix, comments only).

### Triage and delivery rows (record only)

#3496, #3489, #3486, #3480 (delivery rows, autofix).

## v7.1.11

**Patch stamp: 25 merges since v7.1.10, stamped on the owner's order.** The user-visible changes are the water set-point that follows measured feedback, the configuration of a combi store, and a diagnostics download that no longer carries the home's location.

### #3405 and #3433 The water set-point follows measured feedback (R10-WATER-SETPOINT-FEEDBACK)

The water set-point now follows the measured feedback, as an advanced-settings option that defaults on for qualifying installs (#3405). #3433 carries the contributor's answers on registers, watchdog and hysteresis into that work.

### #3398 Combi tank store, part B (R10-COMBI-TANK)

For outside request #3225 by Bankaifan, with thanks. A combi store, where one body of heating water serves both the space circuit and hot water, can now be configured; part A (#3358, v7.1.10) landed its physics in the thermal model.

### #3447 Download diagnostics redacts the location (R10-OUTSIDE-DIAG-REDACT-LOCATION)

Built from outside pull request #3436 by Bankaifan, with thanks. Download diagnostics used to round latitude and longitude to one decimal and publish the solar location option's coordinate as that rounded cell. Both are now redacted outright, so a replay taken from a download carries no solar location. The on-instance replay export is unchanged.

### Developer tooling, CI and audit machinery only

#3423 (worktree collection keeps live worktrees), #3453 (gh shim escapes hotfix), #3425 (tick residue), #3427 (GitHub read residue), #3424 (train residue), #3419 (prepr read-set hotfix), #3379 (later review rounds review only the delta), #3429 (root cause: Dependabot stale hash), #3426 (Dependabot #3414 compatibility), #3384 (no merge blocked on a non-required red, part 2), #3417 (carry sink barrier), #3366 (dispatch at handoff, part 2), #3322 (GitHub Actions group bump), #3321 (mermaid 12.2.0 to 12.3.0 for the site).

### Triage and delivery rows (record only)

#3389, #3392, #3383, #3374 (triage batches); #3459, #3432, #3422 (delivery rows).

## v7.1.10

**Patch stamp: 36 merges since v7.1.9 and one direct commit, stamped on the owner's order after the combi tank store landed.** The user-visible changes are the heat curve control through a Home Assistant number entity, the COP that is no longer graded from a self-comparison, and a German translation. The combi tank store lands as engine physics that no option reaches yet. The rest of the window is round-10 tooling, audit machinery and delivery records.

### #3299 and #3402 Heat curve control through a number entity (R10-GENERIC-HEAT-CURVE, R10-GENERIC-HEAT-CURVE-PERSISTENT)

Adopts the design of outside pull request #3284 by Bankaifan, with thanks. The "Heat curve control" options page can now name a Home Assistant `number` or `input_number` entity as the target of the heat curve displace, for a controller without MQTT. Two kinds, chosen under "What the entity is":

- **Offset** (#3299): the displace is written as a temperature difference, 0 being neutral, to a volatile entity. It is bounded to a configurable band (default 3 K) and to the entity's own range, written only on change, and an entity whose range excludes 0 is refused. Turning the optimizer off, or unloading it, writes 0 back to an entity the optimizer wrote.
- **Persistent** (#3402): for a controller that has only a stored curve parameter. The optimizer displaces that parameter from the value it held, within a band, with a daily write budget and a minimum time between writes because every write wears the controller's memory, and writes the original value back when the optimizer is turned off.

`docs/ecl110.md` gains "Without MQTT: a number entity" and "Kind persistent: a stored curve parameter", with a Luxtronik example and a warning that a stored curve parameter is rarely a true parallel shift. The MQTT arms are unchanged.

### #3297 COP is graded only from a metered heat-over-power sample (R10-HOTFIX-COP-UNMEASURED)

The Health tab no longer grades the heat pump from a "measured COP" that was the model's own COP in disguise on installs that cannot measure it, including installs whose heat and power inputs are the vendor's own estimates. A COP sample is now recorded only from a heat reading over an electrical reading, neither an estimate. Where it cannot be measured, the card and diagnostics say "COP cannot be measured on this install" and name the meter that would fix it. The metering page gains `heat_pump_power_source` and `heat_pump_thermal_power_source` (auto, meter, estimate) and `heat_meter_sees_dhw`. The COP health watch restarts from measured samples only, so its baseline is relearned after the upgrade.

### #3331 and #3378 German translation (R10-I18N-DE)

German is now a third interface language beside English and Swedish, in the integration's translations and in the dashboard card. #3378 adds the German text for the keys that #3372 and #3360 added while #3331 was in review.

### #3358 Combi tank store, part A (R10-COMBI-TANK-STORE)

For outside request #3225 by Bankaifan, with thanks. A combi store, where one body of heating water serves both the space circuit and hot water, was counted twice when entered as both tanks. This change lands the store's physics in the thermal model: one hot-water step shared by the separate tank and the combi store, and the exchange of heat between the space side and the hot-water side. **No option or loader switches it on yet**, so nothing changes for an existing install; the setup an install can reach is part B.

### Developer tooling, CI and audit machinery only

#3304 (outside requests first), #3399 (outside requests share replan's top tier), #3350 (R10-OUTSIDE-INTAKE part 2: plan-page closure rule, flow metrics and bottleneck alert), #3364 (train stale-verdict guard), #3359 (train rejoin without re-carry), #3345 (tick levels part 2), #3341 (review enumerate), #3361 (gh read retry part 3), #3375 (bound the instrument-self-tests read-set measurement), #3395 (state docs push race), #3396 (opener reads the tick board's flagged lines), #3400 (review packet: required-red asks classify's whole verdict), #3401 (the train's pre-flight judges a policy head with the mandate's due approval), #3403 (sweep token actor), #3406 (stress memory pass), #3408 (the pip group's dependency bumps re-applied with hashes), #3409 (repair main's instrument-self-tests red), #3412 (post #201 records to a continuation issue), #3416 (roster drain replay hotfix), #3397 (spelling-corpus sentence in the fixer contract; policy). Dependabot: #3413 (playwright 1.64.1 to 1.65.0 in the pwlane group). Root-cause records: #3329 (sweep settle loop), #3351 (stamp claim conflict), #3410 (main's instrument-self-tests red), #3411 (slow open prepr), #3415 (roster drain replay).

Direct commit 57091a694e, "ci: record nightly kills" (no pull request): the nightly ledger.

### Delivery rows (record only)

#3393, #3407, #3418, #3332.

## v7.1.9

**Patch stamp: 38 merges since v7.1.8, stamped early so outside users can try the water set-point fix.** The user-visible changes are the water set-point lift and ceiling options, the part-load and savings-meter fixes, and the COP gate. The rest of the window is round-10 tooling and audit machinery.

### #3372 Water set-point lift and ceiling (R10-WATER-SETPOINT-LIFT)

Adopts outside pull request #3356 by Bankaifan, with thanks. When Pump duty control is set to Control and the space set-point is a water temperature, the Sensors and entities page now offers two options: the modulation floor's lift over the measured inlet, and the full-power flow ceiling. The space set-point unit can now also be `return`, for a controller that takes the number as its return-water target. A stored ceiling at or below 25 °C, which only a hand-edited entry can produce, now reads as 55 °C instead of switching heating off.

### Product fixes

- #3291 Part-load residue (R10-PARTLOAD-RESIDUE).
- #3360 Savings-meter floor (R10-SAV-METER-FLOOR).
- #3347 Savings comfort, part 4 (R10-SAV-COMFORT).
- #3371 COP gate, part E (R10-COP-GATE-E).
- #3346 "Why now" widget, part 2 (R10-WHY-NOW-WIDGET).

### Developer tooling, CI and audit machinery only

#3349, #3348, #3367, #3337, #3339, #3315, #3305, #3343, #3327, #3326, #3330, #3310, #3338, #3363 (closes #3283), #3325, #3342, #3344, #3336, #3317, #3340, #3333, #3318: round-10 hotfixes and tooling, which include one BLAS controller per process, the gate-busy deferral, per-leg CodeQL timeouts, roster read and write sweeps, the relay sweep and the body contract. #3353, #3354, #3352, #3334, #3362, #3316: root-cause records. #3319: the round playbook (R10-ROUND-PLAYBOOK). #3373, #3370, #3357: delivery-status rows (record only).

## v7.1.8

**Patch stamp: 6 merges since v7.1.7.** The user-visible change is that the heat-pump plan now respects the "Heat pump min power" setting. The rest of the window is round-10 tooling and audit machinery.

### #3308 The plan respects "Heat pump min power" (R10-MIN-POWER-FLOOR)

The heat-pump plan now respects the "Heat pump min power" setting. A pump that cannot modulate is no longer planned at steps below its minimum, and a pump that also heats hot water no longer has space heating and hot water planned together above its maximum power. A new "compressor modulation" option (auto, on/off, modulating) on the thermal model page lets you declare how your pump behaves. Closes #3289.

### #3294 Standing contracts for the orchestrator's sessions, part 2 (R10-FLY-STANDING-CONTRACTS)

The hooks that the orchestrator's sessions depend on are now tracked, described and installable, including a guard on the orchestrator's shell commands. Developer tooling only.

### #3320 Suite host determinism, part 2 (R10-SUITE-HOST-DETERMINISM)

The entity test script gives the same answer on any host. Test tooling only.

### #3335 Root-cause record for the stamp flush cost (R10-RCA-STAMP-FLUSH-COST)

Records that the existing root-cause note on stamps dispatching a whole Nightly run already covers the owner's ruling. No code changed.

### #3324 Closeout instruments (R10-CLOSEOUT-INSTRUMENTS)

The instruments for closing out an audit round: worktree collection, closeout exemptions and tag pruning. Developer tooling only.

### #3328 Delivery rows recorded (autofix)

Delivery-status rows for #3262, #3288, #3301, #3311 and #3312. Record only.

## v7.1.7

**Patch stamp: 5 merges since v7.1.6.** The user-visible change is that the round's plan page is now public: the developer documentation links it, and outside contributors have a stated intake route. The rest of the window is round-10 engineering and audit machinery.

### #3262 The round's plan page is public (R10-OUTSIDE-INTAKE)

The plan page for an ongoing audit round is now published from the developer documentation (owner ruling, 2026-11-06). The same change states how issues, pull requests and posts from outside users are taken in and answered during a round.

### #3301 CI's prediction covers every restoring job (R10-FLY-CIPREDICT-RESTORING)

`tools/pr/ci_predict.py` now predicts every CI job that restores a grader from the base, not only governance's three. A prediction no longer misses a red those jobs would raise. Closes #2952.

### #3288 The merge train retries its carry-path fetch (R10-TRAIN-MERGE-LOOP part 2)

The merge loop's second part: the approval carry path retries a failed `git fetch` instead of refusing on the first transient error.

### #3312 The figure block is registered with the field-coverage grader (R10-BODY-CONTRACT part 3 bootstrap)

`tools/pr/figure_block.py` is registered as pending in main's field-coverage registry, so the body-contract work that builds on it can pass the grader CI restores from the base.

### #3311 The "other" friction family is disposed (R10-FRICTION-OTHER-FAMILY)

The record of the friction family that matched no class: mostly spelling dispersion, and one taught obligation that three pull requests had missed. It lands as `dev/audit/rca/R10-RCA-OTHER-UNTAUGHT.md`.

## v7.1.6

**Patch stamp: 27 merges since v7.1.5.** The user-visible changes are a live "Why now" explanation on the card, a saving that says when it includes wood heat, a buffer tank that no longer starts every solve from a fixed 40 °C, and inputs that come back as soon as their entity reports again. The rest of the window is round-10 engineering and audit machinery.

### #3274 Why now widget (R10-WHY-NOW-WIDGET)

The solver now publishes five signed drivers for each step: price rank, comfort floor, mold guard, away and forecast. Each is a percent of that step's push. The space-plan sensor publishes the current step's drivers as `why_now`, and the card shows them after the headline, in English and Swedish. They are computed in a new pure module, `slot_drivers.py`.

### #3244 The monthly saving says it includes wood heat (R10-HOTFIX-SAV-ESTIMATE part 2)

Wherever wood is configured, the saving now states that it includes wood's heat and excludes the cost of firewood (owner ruling, 2026-11-04). The receipt event, the `MonthlySavingsSensor` attribute `saving_includes_wood`, the card's receipt and savings table, and the notification blueprint all read one definition. The CodeQL autoescape alert on its render harness is fixed at the root.

### #3268 Buffer tank seeded without a probe (R10-COMBI-TANK PR 0)

Without a buffer probe, the buffer temperature never advanced. Every solve started from the 40 °C default or a stale value. It is now seeded from the previous plan's trajectory, the way the DHW tank already was. The rise inputs used for external-heat detection read only measured values, so a planned rise is no longer counted as evidence of external heat.

### #3300 A missing input is re-read when its entity returns (R10-INPUT-REAPPEAR)

This adopts the outside pull request #3292 from @Bankaifan. When the cycle finds a configured input missing or unavailable, it is now re-read as soon as its entity reports a value, instead of one optimisation interval later.

### #3273 One owner for each clone-class fact (R10-CLONE-2238)

The remaining #2238 clone-class instances (one fact decided twice) now each have a single owner in the module that held both copies, and every other copy calls it. Examples are the planned space/DHW split, the fabric-loss residual refusal and the indoor-sensor trajectory.

### #3307 Session-start hook self-test pins its clock (R10-HOTFIX-MAIN-IST-RED)

Main's `instrument-self-tests` job went red when git's relative clock ticked between two reports that the self-test compares byte for byte. The self-test now pins `GIT_TEST_DATE_NOW`. The hook's normal output is unchanged.

### #3295 Root-cause record for the ci-red friction key (R10-FRICTION-CI-RED)

The record behind the recurring-friction key `ci-red` (#3156). It names each of the 18 entries' PR and red check, and finds that one verdict word covers four mechanisms. It also re-files #3219 from group A to group D.

### #3264 Plan-model correctness and the Gantt-drift instrument (R10-FLOW-TOOLKIT-MODEL)

`tools/plan/replan.py` now prices only pending carries as open work. The Gantt-drift instrument is now tracked in the tree.

### #3296 The stamp's record flush dispatches only the beat (R10-FLY-STAMP-FLUSH-COST)

`nightly.yml` gains a `lanes` input (all or beat), and the stamp's record flush posts `lanes=beat`, so it no longer runs every nightly lane. Rules 4 and 5 now read one window.

### #3302 Each PR's own delivery row no longer counts as non-product (R10-CI-OWN-DELIVERY-ROW)

CI-throughput lever 2. A pull request's own delivery row no longer stops the machinery lanes from standing down on an all-product change. A strace recording measures which lanes actually read a row.

### #3290 The merge train waits for a deferring gate (R10-HOTFIX-TRAIN-DEFER-WAIT)

CI-throughput lever 1. The train no longer treats an edit run's deferring red gate as final while the head's code run is still running.

### #3287 A deferring gate publishes at once and the sweep settles it (R10-HOTFIX-GATE-BUSY-DEFER, part 3)

A deferring gate no longer holds a runner. `gate-sweep.yml` re-runs it once the deciding run completes. A new `settle` branch covers gates that deferred to each other and deciders that ended red or cancelled.

### #3278 Root cause of the busy gate deferral (R10-RCA-GATE-BUSY-DEFER-2)

The root-cause record beside the gate-deferral fix. Re-runs replayed a pre-fix `gate.py` restored from the payload's base SHA. The record also reclassifies #3263's edit/code-run red as a defect, the one #3276 fixed.

### #3277 Whole-run cancels at live heads (R10-RCA-LIVEHEAD-CANCEL)

The root-cause record, detector and bug class for whole-run cancels at live heads. They were operator cancels under the owner credential, not CI machinery.

### #3285 Root cause of the record flush dispatching all of Nightly (R10-RCA-FLUSH-DISPATCH)

The record, harness and class `N-dispatch-overreach`. The flush treated a job as the unit of dispatch, but the API dispatches a whole workflow.

### #3280 The record flush honours a train hold (R10-FLY-STAMP-FLUSH-HOLD)

`stamp.py` no longer spends its flush dispatches under a live `train-hold`. `merge_train.py` keeps the hold DELETE from being skipped by a second signal during the unwind.

### #3275 Instrument self-tests run detached (R10-HOTFIX-SELFTEST-TIMEOUT)

The five slow self-tests in `instrument-self-tests` now start detached at the beginning of the job, so the job takes as long as the longer of the two parts instead of their sum. The 30-minute timeout is not raised.

### #3269 Nightly pins per night (R10-HOTFIX-NIGHTLY-PIN-THROUGHPUT)

Mutation-ledger runs are now seeded by run id, so two runs on one date no longer draw the same slice. Two more changes, each tied to a measured line of the 06 Nov breakdown, raise the number of pins per night.

### #3265 Plan page lanes (R10-HOTFIX-PLAN-LANES)

`roster_lane` now places a group by the files it owns, so instrument, CI and record groups are no longer drawn in the core-model lane.

### #3267 Sweep template sync (R10-SWEEP-TEMPLATE-SYNC)

The 11-06 sweep changes made outside the tree are folded into the tracked sweep instruments, and the template declares the overlay keys its rows read.

### #3252 Relay residue (R10-RELAY-SWEEP)

The residue in `cloud_relay.sh` is fixed on one owning seam (carries 0-9).

### #3293 Handoff path, part 2 (R10-HANDOFF-PATH)

`pr_args.sh` resolves its own directory once, when it is sourced. `open_driver.py` gains a stem escape, a guarded log read and a STUCK line after three tries.

### #3272 Triage batch 128

P399, cloud fires without sources, is accepted, narrowed to R10-POLICY-ROLE-PACK.

### #3286, #3298, #3306, #3309 Delivery rows (autofix)

Record-class merges that write the delivery rows: #3286 for #3244 and #3277; #3298 for #3252, #3265, #3272, #3273, #3278, #3280, #3285 and #3287; #3306 for #3267, #3268, #3269, #3275 and #3293; #3309 for #3264, #3274, #3290, #3295, #3296, #3300, #3302 and #3307.


## v7.1.5

**Patch stamp: 23 merges since v7.1.4.** One user-visible fix: the optimiser no longer hangs when its worker process goes silent.

Stamped with --allow-red before main's gate completed, on the owner's standing order to stamp without waiting for main CI.

User-visible:

- #3232 (outside contribution from @Bankaifan, adopted from #3226): the coordinator's process worker reply wait is now bounded, and the stop path no longer holds the worker lock indefinitely, so a silent worker cannot hang optimisation or Home Assistant shutdown.

Engineering and audit programme (round 10):

- Audited fix groups and instruments (15): #3250 (roster-reader predicates, carries 1-4), #3251 (ref privacy for cloud seats), #3259 (gate stale-jobs carries, part 2), #3260 (body-contract carries, part 2), #3249 (dispatch at handoff), #3241 (carry residue), #3276 (an edit gate no longer defers to a code run it cannot see conclude), #3263 (nightly-status hotfix), #3234 (replay cost budget, round 2), #3242 (train merge loop), #3246 (one concurrent gate run decides at a head), #3248 (obligations ledger residue), #3253 (roster write path residue), #3255 (friction records), #3256 (policy role pack).
- Brief carries (2): #3247 (D0 brief: stop-tolerance refusal and DHW cert-cell gap), #3261 (D1 brief: the process-worker hang root cause).
- Roster and record merges (5): #3258 (round-10 roster and triage rulings), #3270 (delivery rows, autofix), #3271 (triage batch 127, P393 to P398), #3279 (delivery rows for #3232, #3246, #3255, #3263, autofix), #3281 (delivery rows for #3241, #3249, #3250, #3251, #3259, #3261, #3271, #3276, autofix).

- Delivery record: the rows the stamp flushed before tagging (#3282).

## v7.1.4

**Patch stamp: 10 merges since v7.1.3.** No user-visible change. The window is release and audit machinery.

Stamped with --allow-red before main's gate completed, on the owner's standing order to stamp without waiting for main CI.

Engineering and audit programme (round 10):

- Audited fix groups and instruments (3): #3236 (the stamp bumps from the highest release tag), #3243 (gate lease TOCTOU), #3240 (planted-defect audit).
- Triage rulings (3): #3212, #3237, #3238.
- Roster and record merges (4): #3239 (round-10 roster and triage rulings), #3235, #3254 and #3257 (delivery rows, autofix).

- Delivery record: the rows the stamp flushed before tagging (#3254).

- Delivery record: the rows the stamp flushed before tagging (#3257).

## v7.1.3

**Patch stamp: 84 merges since v7.1.1.** v7.1.2 was never stamped, so this window opens at v7.1.1 and carries v7.1.2's contents. The user-visible part is the savings estimate and a handful of pricing and learner fixes, plus a contributed DHW set-point input. The rest of the window is the round-10 engineering and audit machinery.

User-visible changes:

- Savings: the month row settles stored heat (#3195), and settles against the meter (#3220).
- DHW set-point: a water_heater entity is accepted as the set-point input (#3231, outside contribution).
- Compressor part-load pricing (#3182), COP gate part D (#3193).
- Overbook residual (#3183), two-zone heat-loss (#3196), learned-store load (#3185).

Engineering and audit programme (round 10):

- Audited fix groups and instruments (52): #3054, #3055, #3065, #3077, #3078, #3085, #3089, #3090, #3147, #3149, #3150, #3151, #3153, #3160, #3163, #3164, #3165, #3167, #3168, #3169, #3170, #3173, #3174, #3175, #3179, #3180, #3181, #3184, #3186, #3189, #3191, #3192, #3194, #3197, #3198, #3199, #3200, #3201, #3205, #3206, #3208, #3216, #3217, #3218, #3219, #3221, #3222, #3223, #3227, #3228, #3229, #3230.
- Triage rulings (16): #3154, #3157, #3158, #3159, #3161, #3171, #3172, #3177, #3202, #3203, #3204, #3209, #3210, #3211, #3213, #3214.
- Record and bot merges (8): #3091, #3155, #3162, #3176, #3178, #3207, #3215, #3233.

## v7.1.2

**Unstamped release.** v7.1.2 was a hand tag of b8e82369, published 2026-11-02, never stamped: its manifest and VERSION read 7.1.1. Its contents are included in v7.1.3.

## v7.1.1

**Patch stamp: 107 merges since v7.1.0.** Users were waiting on a set of fixes: a factory reset, the ceiling probe, and a run of away-mode and learner corrections. The rest of the window is the round-10 engineering and audit machinery.

User-visible changes:

- SAV comfort: the duty ledger's run fold settles one tick into each step (#3145).
- Factory reset: the integration can be reset to a clean state (#3047).
- Ceiling probe: the heat-pump ceiling is probed instead of assumed (#3050).
- Away presence: the plan is recomputed when presence or the holiday calendar changes (#3052).
- Away setback: weekend and holiday comfort no longer override the away setback (#3013), and the away override survives an entry reload and the restore (#3015).
- Learner inputs: a sensor swap voids the heat-loss learners, and a reset action is added (#3022).
- Vent freeze skips only the learners room air cannot reach (#3009).
- Step-boundary actuation: the pump switch is written at the step boundary (#2968).
- COP: compressor part-load inverse conversions and residual carries (#3006, #3005), COP gate part 6 (#3038).
- Wood: the blueprint notifies when wood beats the heat pump, with a recommended lighting window (#3016).
- Health tab: no-meter heat-loss bar and history-free strings (#3062), residual carries (#2997).
- README figures render on the Marketplace page, light and dark (#3014); final user docs (#3048).

Engineering and audit programme (round 10):

- Audited fix groups and instruments (40): #2925, #2962, #2989, #2992, #2994, #2995, #3000, #3001, #3002, #3004, #3010, #3011, #3012, #3024, #3037, #3041, #3042, #3045, #3049, #3051, #3056, #3058, #3059, #3060, #3061, #3063, #3064, #3066, #3070, #3072, #3073, #3075, #3076, #3086, #3092, #3097, #3118, #3143.
- Triage rulings (36): #2987, #3003, #3007, #3017, #3018, #3019, #3020, #3023, #3025, #3026, #3027, #3029, #3030, #3031, #3033, #3034, #3035, #3036, #3039, #3043, #3046, #3053, #3067, #3068, #3069, #3079, #3080, #3082, #3084, #3095, #3096, #3141, #3142, #3144, #3146, #3152.
- Record and bot merges (14): #3008, #3021, #3028, #3032, #3040, #3044, #3057, #3071, #3074, #3081, #3093, #3094, #3098, #3148.

## v7.1.0

**Round-10 merge-train stamp: 98 merges since v7.0.5.** The window is the merge seat's train clearing the programme's remaining audited fix groups: the claim-carry barrier, the train's single admission rule, the COP gate and compressor part-load pricing, the Health tab and the Home Assistant Marketplace integration.

User-visible changes:

- Marketplace: the integration ships through the Home Assistant Marketplace (#2973, #2967).
- Health tab: reworked from the owner's report of 2026-10-14 (#2976).
- COP: the compressor's power is priced in COP, off by default (#2872); the COP gate's pending-prediction readers (#2917, #2975).
- Advisor what-if and the config flow pages (#2963, #2946, #2915).

Engineering and audit programme (round 10):

- Audited fix groups (50): #2973, #2975, #2978, #2872, #2976, #2977, #2955, #2917, #2969, #2961, #2964, #2971, #2967, #2954, #2959, #2953, #2963, #2960, #2956, #2957, #2939, #2949, #2948, #2946, #2933, #2947, #2896, #2935, #2936, #2915, #2887, #2919, #2916, #2937, #2913, #2938, #2912, #2930, #2920, #2923, #2918, #2910, #2873, #2909, #2905, #2883, #2894, #2876, #2853, #2897.
- Roster batches (4): #2988, #2914, #2903, #2899.
- Triage rulings (31): #2993, #2991, #2986, #2985, #2980, #2983, #2981, #2982, #2970, #2974, #2972, #2958, #2945, #2906, #2934, #2932, #2931, #2922, #2929, #2927, #2928, #2926, #2924, #2921, #2908, #2902, #2900, #2891, #2892, #2890, #2898.
- Record and bot merges (13): #2996, #2990, #2984, #2979, #2966, #2951, #2944, #2943, #2941, #2940, #2911, #2904, #2901.

- Delivery record: the rows the stamp flushed before tagging (#2996).

