# Review packet #3596
head: 9bdd6af9bde7489cd2b0f05751b7f664ecd6a5a2
base: d7004eaa775dd7b42aa392df0eb53aeec198b2b0

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arch-score / arch-score id=132596559289 queued
arm id=132593299175 skipped
budget-raise-gate / budget-raise-gate id=132596559541 queued
cancel-superseded id=132593266470 success
codeql id=132594993670 skipped
codeql / Analyze (actions) id=132596559124 queued
codeql / Analyze (javascript-typescript) id=132596559186 queued
codeql / Analyze (python) id=132596559147 queued
governance id=132594993943 skipped
governance / delivery-status id=132596559213 queued
governance / delivery-status-publish id=132596560896 skipped
governance / env-matrix id=132596559196 queued
governance / instrument-self-tests id=132596559210 queued
governance / policy-docs id=132596559187 queued
governance / record id=132596560963 skipped
governance / wave-script id=132596559228 queued
hassfest id=132594993979 skipped
hassfest / hassfest id=132596559351 queued
kernel-points id=132596559957 skipped
prelude id=132593266474 success
refresh id=132593266278 success
tests id=132594994358 skipped
tests / briefs id=132596559171 queued
tests / closure-scope id=132596559195 queued
tests / mutation id=132596559089 in_progress
tests / nightly-status id=132596559177 queued
validate id=132594994253 skipped
validate / validate-hacs id=132596559303 queued

## Refusals
introduced-red: unreadable: head governance / instrument-self-tests job 132596559210: queued has not concluded: an introduced red cannot be ruled out (fail closed)

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
FIGURES: 0 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/programme/delivery/3596.md b/dev/programme/delivery/3596.md
new file mode 100644
index 0000000000..f455be56bb
--- /dev/null
+++ b/dev/programme/delivery/3596.md
@@ -0,0 +1 @@
+- [#3596](https://github.com/tvofi/heatpump_optimizer/pull/3596) — **open**, R10-USER-DOCS-VERIFY (savings-valuation delta): re-read the user and architecture docs against #3587 and #3588 (R10-USER-DOCS-VERIFY)
diff --git a/docs/architecture.md b/docs/architecture.md
index 7647afc35c..b216b81be5 100644
--- a/docs/architecture.md
+++ b/docs/architecture.md
@@ -393,7 +393,7 @@ Each bullet names the module that owns one rule, and what the rule is.
 - **The thermal parameters have one writer.** `_publish_params` in `coordinator.py` builds a new parameter set, which re-runs the divisor floor, and rebinds the coordinator context and the live model to it. A solve or a learner in the middle of an await keeps the set it read. The coordinator context is a frozen dataclass, replaced whole.
 - **A long computation works on a snapshot of the live state.** In `coordinator.py` a solve takes its own deep copy of the configuration, the parameters and the thermal state, and the away recovery job and the diagnosis each take a copy of the thermal state.
 - **One owner per duplicated shape.** `inputs.py` owns the power conversion: `normalize_power_kw` converts by the entity's declared unit and refuses an unknown one, and `state_power_kw` refuses a reading that is not finite before or after conversion. `finite_float` in `const.py` gives a value as a finite float, or a default. Two functions own what the end of the day reads as: `quiet_windows.wall_clock` folds it to 00:00, and `dhw_schedule.format_clock` keeps a window label's 24:00.
-- **One payload read on the entity base.** `entity.py` owns the finite scrub, the payload-number rule and the zone set-point attributes. A mixin in `sensor.py` reads the number at one path of the payload.
+- **One payload read on the entity base.** `entity.py` owns the finite scrub, the payload-number rule, the zone set-point attributes and the combi store's `dhw_split` attribute, which the hot-water cost and energy sensors and the climate entity all publish from one function. A mixin in `sensor.py` reads the number at one path of the payload.
 - **A delivered-heat counter.** `heat_energy.py` owns the span a delivered-heat kWh counter measured, the time the pump spent in each duty, and the one rule that splits an interval between space heating and hot water: the observed shares, else the plan's split. It imports nothing from Home Assistant; the coordinator reads the entities and calls in.
 - **An honest COP state.** `accuracy.cop_observability` owns the state: no electric meter, then an electric meter with no measured heat, which reads "not measurable", then estimated inputs or a heat meter.
 - **One rule for scores.** `compose_scores` in `coordinator.py` puts the grades on one scale; no evidence is no grade with one reason code, never zero. The insight payload takes the restart advice once and hands the same advice to the scores, and `house_loss_converged` is the convergence rule that both the envelope grade and the learning view's "learned" flag read.
diff --git a/docs/configuration.md b/docs/configuration.md
index 74c3dc778e..ae9cef0a84 100644
--- a/docs/configuration.md
+++ b/docs/configuration.md
@@ -984,7 +984,7 @@ catalog below keys off.
 | Price the supply temperature lift (no mixing valve) | off | on/off | For a plant with **no** mixing valve, where the pump feeds the emitters directly. When on, every plan and cost accounts for the pump working harder to make hotter water: the supply temperature is the model's own weather curve plus the offset learned from the *Supply (flow) water temperature* sensor, if you set one. With that sensor the efficiency health watch also judges the pump at a common water temperature, so a hotter supply is not reported as a failing compressor, and it skips any interval where the sensor has no fresh reading — **so while that sensor is dead the watch does not judge space heating at all**. Readings judged this way keep their own baseline, so switching the option or the sensor on or off starts that baseline afresh rather than comparing unlike numbers. **The learned offset lowers the supply at most 15 K below the modelled curve and raises it at most to a 75 °C supply**; a reading above 75 °C is not learned from. The lift is only charged above a 35 °C supply. Refused together with a throttling valve, whose tank temperature already sets the price. |
 | Buffer tank size | 35 L | 10–1500, 5 steps | The tank between pump and circuits. It is only planned around as a store when a throttling valve exists and the volume is at least 100 L; below that it holds less than one optimizer step of heat. |
 | Maximum buffer tank temperature | 70 °C | 40–90 | A hard ceiling. The tank is never charged above this, however cheap electricity is. |
-| Hot water is made from the buffer tank (combi tank) | off | on/off | For one tank of heating water that serves both heating and hot water with no separate hot water tank: a multifunction or hygiene store with an internal coil, a tank-in-tank, or a fresh-water station on the buffer. The buffer and the hot water are then planned as **one** store, so its heat is counted once. Refused unless the buffer is a store (a throttling valve and at least 100 L), hot water is on and no wood coil heats the hot water. Enter the tank's heating-water volume as the buffer size. For the buffer cooling rate, prefer the datasheet's ErP standing loss S in watts at 65 °C: the loss per kelvin is S / 45 K, assuming a 20 °C room. Example: 111 W over 504 L is 2.47 W/K, about 0.106 °C/h at the 25 K reference. One probe is read as the whole tank's mean, so point the buffer sensor at the middle well (with a hot water sensor only, that one is used). A tall, stratified store without a middle well has no single probe that reads its mean, and a top probe alone reads high, so the plan believes the tank holds more heat than it does. Make the buffer temperature entity a template sensor averaging a top and a bottom probe instead. That average is an estimate of the mean, not the mean itself: the temperature between the two probes does not change in a straight line. As an example, not a guarantee: on one user's 600 L store the top and bottom probes differed by a median 24.8 K, and the top probe alone overstated the stored heat by about 9 kWh. Two tanks in one shell, a buffer section under a hot water section, are not a combi tank: set them up as two tanks. While it is on, DHW Heating Cost (next 24 h), DHW Energy (lifetime) and DHW Cost (lifetime) count what the heat pump spends in hot-water mode, which includes space heat drawn from the tank: it is one store, so no meter can split it by use. Each says so in its `dhw_split` attribute. |
+| Hot water is made from the buffer tank (combi tank) | off | on/off | For one tank of heating water that serves both heating and hot water with no separate hot water tank: a multifunction or hygiene store with an internal coil, a tank-in-tank, or a fresh-water station on the buffer. The buffer and the hot water are then planned as **one** store, so its heat is counted once. Refused unless the buffer is a store (a throttling valve and at least 100 L), hot water is on and no wood coil heats the hot water. Enter the tank's heating-water volume as the buffer size. For the buffer cooling rate, prefer the datasheet's ErP standing loss S in watts at 65 °C: the loss per kelvin is S / 45 K, assuming a 20 °C room. Example: 111 W over 504 L is 2.47 W/K, about 0.106 °C/h at the 25 K reference. One probe is read as the whole tank's mean, so point the buffer sensor at the middle well (with a hot water sensor only, that one is used). A tall, stratified store without a middle well has no single probe that reads its mean, and a top probe alone reads high, so the plan believes the tank holds more heat than it does. Make the buffer temperature entity a template sensor averaging a top and a bottom probe instead. That average is an estimate of the mean, not the mean itself: the temperature between the two probes does not change in a straight line. As an example, not a guarantee: on one user's 600 L store the top and bottom probes differed by a median 24.8 K, and the top probe alone overstated the stored heat by about 9 kWh. Two tanks in one shell, a buffer section under a hot water section, are not a combi tank: set them up as two tanks. While it is on, DHW Heating Cost (next 24 h), DHW Energy (lifetime) and DHW Cost (lifetime) count what the heat pump spends in hot-water mode, which includes space heat drawn from the tank: it is one store, so no meter can split it by use. Each says so in its `dhw_split` attribute, and so does the climate entity. |
 | How the tank makes hot water | Internal coil | Internal coil / Tank-in-tank / Fresh-water station / Custom | Changing it fills in the two numbers below (coil 0.85 and 30 L, tank-in-tank 0.95 and 150 L, station 0.75 and 0 L); edit them afterwards, or choose Custom. A multifunction store with a 40 L coil is Internal coil with 40 L. |
 | Exchanger effectiveness | 0.85 | 0.1–1 | (tap − cold inlet) / (tank − cold inlet) at your usual draw flow. It moves the tank temperature a tap minimum needs (45 °C at the tap from a 10 °C inlet needs 51.2 °C in the tank at 0.85); the legionella target stays a tank temperature. A station's effectiveness falls with flow (one table: 0.88 at 16 L/min, 0.58 at 38 L/min), so read it at your typical flow; manufacturers recommend at most 60 °C on the primary side. **To measure yours:** charge the tank, then let hot water run at full flow for a few minutes with a thermometer in the stream, until the tap temperature stops changing; read the tank sensor the optimizer uses at the same moment (the ratio belongs to that sensor, wherever it sits in the tank); then let the cold tap run until it settles and enter that reading as *Cold water inlet temperature* (Hot water tank and inlet), or fit a sensor on the cold pipe and set *Cold water inlet sensor*. Divide as above. Do this with a fully charged tank: when the tank is warmer at the top than at the sensor, as after a few showers, the same install read 1.10–1.15 against 0.96 when full. Read the tap value in the stream, not on the pipe, and a hot tank (50 °C and up) gives a larger difference to divide by and so a steadier result than a cool one. |
 | Drinking water held inside the tank | 30 L | 0–500 | The coil's content or the inner tank (about 100–250 L); 0 for a station. It adds to the store's heat capacity. |

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
