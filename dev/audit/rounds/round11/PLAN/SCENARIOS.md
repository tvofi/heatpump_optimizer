# Round 11 plan: quality scenarios

Step 2 of `dev/governance/roles/architect-planner.md`. Two or three scenarios per quality
the owner's dimension briefs name, each with the sensitivity point (S) it turns on and the
tradeoff point (T) a fix touches. Seams and groups are those of `COMPONENTS.md`.

## Price optimality (D0)

- **Scenario.** A two-tank wood house on a mild day, or a storage plant at negative prices, is solved; the shipped plan costs no more than the one-run or all-off challenger at equal feasibility.
  - Sensitivity S1: the multi-start seed set in optimizer.py; one all-zero or all-energy set loses a basin.
  - Tradeoff T1: each added start costs solve time on a Raspberry-Pi-class host (D9).

- **Scenario.** price_risk_lambda is above zero; predicted cost, baseline, savings and the price tiles equal the feed's prices times energy, and the premium moves only the objective.
  - Sensitivity S2: the single prices array the solver hands both the objective and the result.
  - Tradeoff T2: carrying two price series widens the result payload the card and the ledger read.

## Robustness (D1)

- **Scenario.** A weather forecast stops advancing, a PV meter goes silent, or a push-mode flag is quiet for an hour; within one cycle the input is treated as stale, Input Problem tells the truth, and the plan falls back to the documented default.
  - Sensitivity S3: the age rule per input kind (polled, on-change, forecast row).
  - Tradeoff T3: a shorter age limit raises false Input Problem on healthy report-on-change devices (D14-s2-01).

- **Scenario.** A stored document, an option or a live state carries NaN, a boolean, an absurd hour count or a year-1 timestamp; setup and every later cycle complete, the value is quarantined once and one record says so.
  - Sensitivity S4: the finiteness and domain test at inputs.py and store.py.
  - Tradeoff T4: a strict boundary rejects values an earlier release stored, which then needs a migration rather than a refusal.

- **Scenario.** The solve worker's pipe breaks or Home Assistant stops mid-solve; the lock is released in bounded time and no repair issue outlives the next good solve.
  - Sensitivity S5: _PROCESS_LOCK held across worker.wait().
  - Tradeoff T5: a bounded wait can abandon a worker that is still alive and using memory (D9).

## Physical sanity (D2)

- **Scenario.** Flow temperature rises by 10 K at fixed source temperature; scalar and batch COP both fall, by the same factor.
  - Sensitivity S6: the Carnot factor exists twice in thermal_model.py.
  - Tradeoff T6: correcting the scalar twin shifts every learned COP correction and golden fixture that absorbed the inverted law (claimed drift, learner re-convergence).

- **Scenario.** A price sensor reports in a minor unit, or a tariff has weekday rules and a capacity charge; the plan's price vector, the fee vector and the billed peak equal a hand calculation for a known week.
  - Sensitivity S7: the unit scale at inputs.py and the day index in grid_fee.py.
  - Tradeoff T7: the fix changes published money for existing installs at upgrade; the release notes owe the step first (release extra steps rule).

- **Scenario.** An unplanned hot-water charge, an away week or a load-limited ceiling probe occurs; no house or capacity learner ingests the interval, and a genuine internal gain is recovered within its stated band.
  - Sensitivity S8: the freeze predicate, today split between the coordinator and each learner.
  - Tradeoff T8: a wider freeze slows learning on installs with few clean intervals.

## Actuator safety (D16)

- **Scenario.** The user selects Off, the plan goes stale on an idle step, or the entry is unloaded or removed; every entity the optimizer wrote reads its pre-optimizer value within one cycle, and a failed restore is retried.
  - Sensitivity S9: restore ownership; four writers have no owner at the fork.
  - Tradeoff T9: restoring on a stale plan hands the pump back sooner, giving up the hold a short forecast outage would have kept.

- **Scenario.** A step boundary passes between two solves; frequency, displace, curve offset and the disinfection switch follow the step covering now, not the step the last solve cut.
  - Sensitivity S10: the one rule for the step covering now, written four times.
  - Tradeoff T10: re-cutting the action between solves adds writes against the daily write budget and compressor wear.

- **Scenario.** A target is off the entity's step, above its max, or the entity is unavailable; the write is quantised to the entity's grid and range or not made, and never recorded as made.
  - Sensitivity S11: the arbiter's held record, which both suppresses repeat writes and decides release.
  - Tradeoff T11: reading the entity before each write costs a state read per actuator per cycle and can chase a pump's own echo (the 20 s echo grace).

## Maintainability (D7)

- **Scenario.** A rule with several copies changes (water heat capacity, the covering step, the evidence cap); the change is one edit at one owner and an agreement test fails if a copy returns.
  - Sensitivity S12: duplication_copies 18, shape_copies 40 and layer_violations 13 at the fork.
  - Tradeoff T12: a shared helper adds an import edge; done carelessly it raises layer_violations or seam_cut_total while lowering the clone count.

- **Scenario.** A fixer adds a cycle step to coordinator.py; the structure ratchet prices the growth whether it lands inside the class or beside it.
  - Sensitivity S13: max_class_loc and class_excess_loc see class spans only; 2,980 lines sit outside.
  - Tradeoff T13: a new ratchet row at zero headroom blocks unrelated fixes on the hot file until someone pays.

## Efficiency (D9)

- **Scenario.** A user presses a what-if three times in a second while the fuse advisor is due; at most one extra solve is in flight, the main solve is not delayed past its interval, and nothing runs a thermostat simulation on the event loop.
  - Sensitivity S14: the solve budget and in-flight guard at the cycle seam.
  - Tradeoff T14: a strict budget delays or refuses a user's what-if answer (D4).

- **Scenario.** The card stays open for a week; retained history rows stay within the 48 h span.
  - Sensitivity S15: HistorySource.absorb has no trim.
  - Tradeoff T15: trimming forces a re-fetch when the user scrolls back past the span.

## Generalization (D12)

- **Scenario.** A one-zone house, an on/off compressor, a pump with no heating-only mode and an install with no hot water are set up with defaults; model, plan views, entities and advisor each describe that plant and no other.
  - Sensitivity S16: the plant-shape predicates (two-zone, modulating, has hot water) and their defaults.
  - Tradeoff T16: changing the default of two_zone_mode moves the plan of every install that never set it.

- **Scenario.** A Fahrenheit install writes a set-point; the written value converts back to the Celsius the plan chose.
  - Sensitivity S17: TEMPERATURE_UNIT_TO_C and its two readers in inputs.py.
  - Tradeoff T17: none found; the inverse is exact.

## Integration quality (D10)

- **Scenario.** A user reconfigures an entry after saving options, or changes the weekday comfort value while keeping the weekend one; the saved entry holds exactly what the form showed.
  - Sensitivity S18: settings stored in entry.data and entry.options, merged by every reader.
  - Tradeoff T18: moving 41 settings to options needs a config-entry migration that cannot be undone by a downgrade.

- **Scenario.** A press or an action is refused or given an unparseable argument; the caller gets a translated error, and energy meters carry the state class the statistics engine needs.
  - Sensitivity S19: off_the_action returns before the outcome exists.
  - Tradeoff T19: awaiting the outcome holds the service call open for the length of a solve.

## Usability and text truth (D4, D5, D6)

- **Scenario.** A German or Swedish user on a phone removes a pipe, reads a stale-plan tooltip and a failure line; the target is at least 24 px, every placeholder is filled and no English is spliced in.
  - Sensitivity S20: card rules written beside the token scales (card_rule_copies 70).
  - Tradeoff T20: larger hit bands overlap neighbouring pipes in dense layouts.

- **Scenario.** A reader compares a number in README.md, docs/ or strings.json with the constant that decides it (legionella interval, input age, echo grace, wood packing); they agree, and the fact has one home.
  - Sensitivity S21: prose numbers no check derives from code.
  - Tradeoff T21: generating or pinning text ties every default change to a text and translation change in the same pull request.

- **Scenario.** A reader follows a path or name cited in a comment or policy file; it resolves at the fork, and no sentence runs past 40 words.
  - Sensitivity S22: no detector for prose paths or sentence length.
  - Tradeoff T22: rewriting about 2,200 long sentences in production and tests touches every hot file and collides with each behaviour group, so it lands last.

## Governance and process (D11, D13)

- **Scenario.** A merge reaches main while a gate run at that head is red, or a live ruleset changes; a detector reports it within one sweep.
  - Sensitivity S23: counts.mjs reads one of three rulesets; `gate` is published by several runs.
  - Tradeoff T23: the fix is instrument work, frozen until round 12; the exposure stays open for the round.

- **Scenario.** A reviewer blocks a pull request or a fixer records friction; the class word resolves to one vocabulary and one policy file.
  - Sensitivity S24: two writers of the block vocabulary and a free-form friction id.
  - Tradeoff T24: a closed vocabulary refuses a genuinely new class until someone extends it.

## Test-suite reach (D3)

- **Scenario.** A fixer breaks the path from a rendered form error to the corrected submit, or doubles the solves in one coordinator cycle; a script of the gate fails.
  - Sensitivity S26: flow tests stop at the error (51 of 53 rendered errors) and the stress gate runs no coordinator cycle and probes 6 of 54 scenarios for memory.
  - Tradeoff T26: each added lane costs gate minutes on every scoped run that reaches it.

- **Scenario.** The quantity a ratchet row names grows through another spelling (const read through a module binding, a rule written twice in one function, an import nothing loads, lines beside the class); the row moves.
  - Sensitivity S27: rows keyed on one spelling of the thing they count.
  - Tradeoff T27: a repaired row that reads higher is a budget raise, which waits for the owner's confirmation.

## Sensor truth and ordering (D8)

- **Scenario.** A month has one settled interval, or the install has no hot water; a sensor that cannot yet know its value is unavailable or bounded, and its availability and its value come from one predicate.
  - Sensitivity S28: availability and value decided in two places (the open-month projection, the gap advisor's hot-water test).
  - Tradeoff T28: a minimum coverage holds back a figure the user expects on the first day of the month.

- **Scenario.** A sensor's state class, device class or name is corrected; statistics accept it, and no entity id changes without a registry migration.
  - Sensitivity S29: metadata written beside the value and never compared with it.
  - Tradeoff T29: a corrected class or name on a published entity can break the continuity of its long-term statistics.

## Recurring classes (D14)

- **Scenario.** A class with a barrier from an earlier round returns in another spelling (an unlatched .exception, forecast row 0 read as now, an off-grid selector in services.yaml); the barrier refuses it.
  - Sensitivity S30: barriers that match one syntactic shape of the class.
  - Tradeoff T30: a wider barrier refuses sound code until the site joins the reasoned list.

- **Scenario.** A fix for one instance of a class merges; the class's sweep over every seam reads no instance left at the stamp.
  - Sensitivity S31: a class spans seams, and each seam's group fixes only its own instances.
  - Tradeoff T31: sweeping every seam per class costs seat hours no single finding asked for.

## Diagnosis from a live bundle (D15)

- **Scenario.** A user's diagnostics bundle is loaded; every document a writer stored is admitted by its loader, and a debug row with an unpriced sample is kept.
  - Sensitivity S32: store.DOMAINS declares less than the writers write.
  - Tradeoff T32: a wider schema admits documents an earlier release wrote wrongly (T4).

- **Scenario.** An analyst reads the solver self-test and the learner state from the bundle; a restart that ran no solve is not counted as a solve, and a learner's stored evidence survives the restart that wrote it.
  - Sensitivity S33: values published before the cycle that produces them has run.
  - Tradeoff T33: withholding a not-yet-run value leaves the entity unknown for the first cycle after every restart.

## Feature effect as documented (D17)

- **Scenario.** A user calls set_thermal_parameters on a two-zone house, answers quick setup's wood questions, or calls run_optimization; the plan moves as the field's description says, or the call is refused with the reason.
  - Sensitivity S34: a feature whose effect depends on a plant condition its own surface does not state.
  - Tradeoff T34: refusing a call that was accepted and inert breaks automations that send it.

- **Scenario.** A user configures an outdoor temperature sensor or restores a learned snapshot; the reading reaches the plan, and the restore picks a snapshot that carried accuracy evidence.
  - Sensitivity S35: a configured input or a stored record that no later step reads.
  - Tradeoff T35: a measured outdoor value joined to the forecast moves the first plan step of every install that has the sensor.

## Tradeoff points that cross seams

- T6 and T8 meet at the learners: the plant-model fixes land first, then the freeze, so a learner is re-measured once.
- T9, T10 and T11 meet at `pump_arbiter.py`'s held record; `actuation-release` fixes its meaning before `actuation-writes` reads it.
- T1, T5 and T14 are all paid in solve time on the small host; `tests/stress.py` and the D9 harnesses are the check.
- T7, T16 and T18 change what an existing install does at upgrade; each owes its step in the release notes.
- T13 and T27 meet at `tests/structure_budgets.json`: a new row lands at zero headroom and a corrected one needs the owner, so the two are separate groups.
- T12 and T13 are where the score can read better than the code; the counters stay on and `seam_cut_total` is watched beside each move.

## Added at step 6 (the moves)

Two scenarios the refactor group `R11-ARCH-cycle-surface` serves, which the
briefs' qualities imply under D7 and D1 and step 2 did not write.

- **Scenario.** The coordinator changes how it stores its mode or another private value; no collaborator module is edited, because each received the value as an argument or read it from a published view.
  - Sensitivity S25: collaborators handed the coordinator itself (`boost.py`, `diagnostics.py`, `pump_arbiter.py`).
  - Tradeoff T25: handing values widens call signatures; past ten parameters it needs a value object.

- **Scenario.** Home Assistant stops or the entry unloads with background tasks pending; each task is cancelled once and the task set is empty, with one writer of the set.
  - Sensitivity S36: the task set written in place by the shutdown and by every task's done-callback.
  - Tradeoff T36: dropping the shutdown's clear relies on each done-callback firing on cancel.
