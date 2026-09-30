# Silent windows: design and placement in round 9

Requested by tvofi on 2026-09-30 (thread "Silent windows", root message 14:08Z).
Written against origin/main 3dfebc16 and roster rev 3.1 (handoff/audit-r9-fixplan @1f02e063).
Status: proposal. The four roster entries are on `handoff/silent-windows-plan`
(one commit on top of handoff/audit-r9-fixplan); the Mac merge seat applies them.

## 1. What exists today

**Hot-water windows.** One config key, `dhw_windows`, holds a spec string in the
grammar of `dhw_schedule.py`: `HH:MM-HH:MM` ranges with an optional day selector
(`daily`, `weekdays`, `weekend`, or day tokens `Mo`..`Su`, lists and ranges).
`parse_windows` gives the every-day view, `parse_weekly_windows` the per-day
view, and `windows_for_day` resolves one date (per-day override keys
`dhw_windows_mon..sun`, then the holiday overlay, then the spec). The card's
what-if panel edits the list row by row (day selector, start, end, remove), prices
it through `simulate_plan` and saves it through `apply_schedule`. "Specific days"
in this grammar means single weekdays; there is no calendar-date support for hot
water windows either, so silent windows get exactly the same choices.

**A passive silent mode already exists (#1067, `silent_mode.py`).** On the Power
limits options page the user types the pump's *own* night-mode schedule
(`silent_mode_windows`, same grammar) and the fraction of nameplate it keeps
(`silent_mode_power_fraction`, slider 0.6 to 1.0, default 1.0 = inert).
`silent_mode.compose` turns that into a per-step electrical ceiling and folds it
into `power_caps_extra`, floored at `CAPACITY_FLOOR_FRACTION` (0.6). It never
writes anything: it only stops the plan from buying night hours the pump will
throttle on its own.

**Reading silent mode.** `heat_pump_capacity_limited_entity` is read as a
"capacity limited now" flag that keeps the learners off throttled intervals. The
device prefill maps it to the Tuya fork's `switch.<pump>_night_mode` (model
000004k4z6, the Rotenso) and to the GCHV Modbus package's
`binary_sensor.<p>_night_mode_frequency_reduction_active`.

**Writable silent controls.**
- Tuya fork: a switch on several models (`night_mode` on 000004k4z6, `mute` on
  default/000004wtcv, `SilentMdoe` on 000000324z; 0000000tqc has it inverted,
  "off = Silent"). Some models fold silent into the operating-mode select
  (e1kd83ng "Heating_Silent", 000004jrci "silence").
- GCHV Modbus package (`tools/gen_gchv_package.py` in tuya_heat_pump): no on/off
  register. Night mode is a daily schedule in holding registers 518/519 (start,
  end, hour*256+minute), exposed as writable time entities; register 68 reads
  whether it is active. One window per day, same every day.

**Writes and the two rulings.** `pump_arbiter.py` is the one writer of mode and
set-points while Optimizer active is on, and holds what it wrote (rewrite after
the echo grace, `pump_write_ignored` repair, retry every 5 minutes); while the
configured power switch reads off it compares and writes nothing, because the
pump resets its set-points to 25 degC when switched off. With Optimizer active off
nothing is written (#1708) except releasing its own disinfection switch and the
DHW repair confirm.

## 2. Design

### 2.1 What the user sets

A "Silent windows" list in the card, directly under the hot-water windows in the
what-if "usual schedule" section. Each row is the hot-water row plus one field:
day selector (same options), start, end, **action: Silent / Off**, remove. Below
the list, when any row is Silent, the silent power fraction slider (the existing
`silent_mode_power_fraction`, pre-filled from config), with a one-line note when
the setup has no silent control (see 2.3). Priced by "Apply" like the hot-water
windows and saved by "Save as my schedule".

Storage: two new option keys, one spec per action, both in the unchanged
`dhw_schedule` grammar (working names: quiet silent windows and quiet off windows).
The card splits its rows by action on save and merges them on load. Reusing the
grammar keeps its 127-day-set round-trip invariant and every existing loader; a
per-segment action tag would have meant a second grammar. The passive
`silent_mode_windows` key stays what it is, the pump's own schedule, relabelled on
the options page as "Pump's own night-mode schedule" so the two are not confused.

Validation on save (card and `apply_schedule` alike):
- an Off row that overlaps a hot-water window on the same day is refused, with the
  overlap named; a Silent row may overlap (the tank just charges slower);
- the existing too-short-window rule applies;
- Silent and Off rows may not overlap each other on the same day.

### 2.2 What the plan assumes

A new HA-free module beside `silent_mode.py` turns the two specs into a per-step
action array (none / silent / off) on the solver's own clock (`_utc_step_starts`,
after F1.10 unifies it), and composes:

- **Silent step:** electrical ceiling `max(fraction, CAPACITY_FLOOR_FRACTION) *
  p_max`, through the existing `power_caps_extra` channel by elementwise minimum,
  exactly as `silent_mode.compose` does. The DHW plan must respect it too: today
  the DHW block is subtracted from the space headroom under `power_caps_extra`
  (optimizer.py, the fuse-guard comment in the space warm start) but the DHW charge
  power itself is not visibly capped per step. SW-1 checks this and caps it.
- **Off step:** no space heat and no DHW charge in that step. `space_blocked` and
  `dhw_blocked` are horizon-wide booleans today, so this needs a per-step mask in
  the solver (space via a zero entry in the caps array, which is not floored; DHW
  via a new per-step DHW ceiling). Comfort and tank floors are soft penalties
  (optimizer.py module docstring), so a long Off window in cold weather stays
  feasible: the plan pre-heats before it, and prices any shortfall.
- **Where the capacity figure comes from:** the configured
  `silent_mode_power_fraction`. No integration exposes the silent capacity
  (GCHV's `unit_capacity` is nameplate). A learned figure (measured draw during
  capacity-limited intervals, which the flag slot already marks) is a sensible
  follow-up, not part of this feature. If the fraction is still 1.0 when a Silent
  row exists, the plan uses 1.0 (nothing capped) and the card says the fraction
  is unset.
- **Inert when unset:** no rows means the module returns None, and every golden
  stays byte-identical. That is the null control for SW-1.
- **When the window cannot be enforced, the plan does not assume it.** Silent
  rows without a usable silent control, and all rows while Optimizer active is
  off, give no silent cap and no off mask (the passive pump schedule still caps
  as today). Planning for silence the pump will not deliver would buy the wrong
  hours; see 2.4.

### 2.3 What gets written (actuation)

**Silent control.** The capacity-limited slot doubles as the control when its
domain is `switch` (the Tuya night_mode/mute/SilentMdoe switches). No new slot,
and the flag stays truthful: when the optimizer turns silent on, the pump really
is capped, and the learners skip those intervals as they should. A
`binary_sensor` there (GCHV) is read-only, so GCHV goes through SW-4. Inverted
switches (0000000tqc) and silent-as-mode-option selects are out of v1: the
select is the arbiter's mode slot, and writing silent through it would fight the
duty table.

**Hold rule.** The silent switch becomes a fourth held slot in the arbiter, on
the same machinery: record what was written, rewrite a differing reading after
`ECHO_GRACE_S`, raise `pump_write_ignored` and retry every `RETRY_MINUTES` if the
pump will not hold it. Inside a Silent window it holds on; outside, it holds off,
but only while at least one silent row exists (an install that sets no rows never
has the switch written). Nothing is compared or written while the power switch
reads off, as today.

**Off.** Recommended: an Off step is the arbiter's idle row with both gates: hot
water set-point to `DHW_GATE_C` (or the entity minimum), space or flow set-point
to `FLOW_GATE_C` / the room gate, mode unchanged. The pump stays powered, keeps
its own frost and pump-protection logic, and nothing depends on the power switch.
Turning the power switch off instead would meet the pump's reset to 25 degC and
the arbiter's rule to stop comparing while it reads off, so the optimizer could
not tell its own off from a person's (decision D1).

**Precedence.** Explicit user actions win for their duration: a boost button
overrides a Silent or Off window (boost duty as today, silent released for the
boost). The anti-legionella hard deadline wins over an Off window (the planner
schedules around Off windows until the deadline). The comfort rail: if the room
falls below the configured minimum comfort by more than the existing rail margin,
the Off window yields to the baseline row and a warning repair says why.

### 2.4 Optimizer off, and silent unavailable

- **Optimizer active off:** quiet windows write nothing, like everything else
  (#1708). Today turning the optimizer off leaves whatever the arbiter last wrote
  in place, gates included ("Off writes nothing, not even the baseline", tvofi
  2026-09-26, in `_arbitrate`). That is harmless for a 15-minute gate but not for
  a window: switched off inside a Silent window the pump stays silent, and inside
  an Off window both set-points stay at their gates, with no writer left to undo
  either. Recommended: on that transition only, restore what the window changed
  (silent switch off; the two gated set-points back to configured), once, as a
  third documented exception beside the disinfection switch and the DHW repair
  confirm (decision D2).
- **Silent unavailable** (no switch, or a read-only entity, and SW-4 not in
  place): normal operation with a warning, as you proposed. The plan is not
  capped, the card marks the rows "not enforced", and one repair issue names the
  missing control. I considered treating an unavailable Silent row as Off, and
  recommend against it: silence is a noise wish, and switching heating off in its
  place changes comfort without being asked.

## 3. PR split

Four groups in a new lane **SW**. None is policy or code-owned if tests stay in
`tests/features.py` and `tests/card.mjs` and no new test script is added
(`tests/run.sh`, `tests/derive_closures.sh`, `tests/card_browser.mjs` and
`tests/closure.py` are code-owned). The new production module goes into a
measured closure through CI's closures autofix, not onto the INERT list.

| group | what | fixer | after |
|---|---|---|---|
| R9-SW-1 | model and plan: specs, per-step actions, silent cap, per-step off mask and DHW ceiling in the solver, `apply_schedule` / `simulate_plan` / `set_thermal_params` fields, plan-sensor attributes, the not-enforced repair | opus (solver) | R9-EG-B1, R9-F1.10, R9-F10.1c |
| R9-SW-2 | actuation: silent switch as a held arbiter slot, Off as gated idle, precedence, optimizer-off restore (per D2), repairs | opus (write safety) | R9-SW-1, R9-EG-B6 |
| R9-SW-3 | card: silent rows beside hot-water rows, action select, fraction slider, chart band, en/sv strings, README/docs section | sonnet (mirrors the hot-water editor) | R9-SW-1, R9-F10.6, R9-F11.5, R9-F6.4 |
| R9-SW-4 | GCHV Modbus: silent through night-mode schedule registers 518/519 (per D4) | sonnet | R9-SW-2 |

Reviewers are opus for all four.

## 4. Placement, and why there

Critical path: F1.7, F1.8, F1.9, F1.10, F1.11, F10.4, F10.5, F10.6, EG-B1,
EG-B6, EG-B7, EG-A4. The feature touches the solve's input assembly, the arbiter,
the services and the card, and each of those is reshaped by a group on or near
that path:

- **EG-B1** rebuilds how a solve gets its inputs (a per-solve record replacing
  writes to the hub objects, including `async_simulate`) and makes
  `HeatPumpOptimizer.optimize` keyword-only. A per-step action array added before
  it would be one more input B1 must carry on the critical path. After it, SW-1
  adds one field to the record. **SW-1 goes after EG-B1** (which is itself after
  EG-B5's planner and F10.6).
- **F1.10** unifies the two step-start clocks that `silent_mode.py` imports.
- **F10.1c** is the last open group that edits `services.py` before EG-B6.
- **EG-B6** rewrites every arbiter reach into the coordinator into explicit
  inputs. Arbiter code written before it would be rewritten by it. **SW-2 goes
  after EG-B6**, and uses B6's interface.
- **The card** is edited by F10.x through F10.6, F11.4/F11.5 and F6.3/F6.4.
  **SW-3 goes after the last of them**, and after SW-1 so the service fields exist.

So SW-1 runs beside EG-B6, SW-2 and SW-3 beside EG-B7, and SW-4 beside EG-A2/A4.
None of the four is on the critical path and none of the critical groups gains
an edge on them. Two overlaps are left to merge order rather than an edge, because
an edge would put a feature on the critical path:
- SW-1 and EG-B6 both touch `services.py` (different functions); whichever
  merges second merges main.
- SW-2 and EG-A2 both touch `pump_arbiter.py` (A2 dedups the store-load prelude
  shared with `boost.restore`); if SW-2 lands first, A2 folds one more copy.

**Landing before EG-A4** matters: A4 makes "delta-S >= 0 with the counters" a
required check. SW-1..SW-3 fit inside the report-only window if they merge before
A4; SW-4 may land after it and then explains its score change in the body.

**Budgets.** SW-1 keeps `coordinator_loc` flat by composing in the new module
(the coordinator's only change is the call site, which after EG-B1 is the
record builder). SW-2 grows `pump_arbiter.py` and SW-3 the card; re-measure with
`tests/structure.py` at the merge base rather than trusting this estimate. If an honest re-record
still raises a structure budget, CLAUDE.md rule 2 treats this as a genuine new
feature: the raise needs your confirmation before the push and merges on your
approving review (decision D3). EG-B7 and the SW groups must not re-record
budgets at the same time (EG-B1/B5/B7 are the structure-budget writers).

**Issue.** Round-9 groups carry class issues; this is a feature with none. On
approval the orchestrator files one feature issue so the delivery rows have a
number; until then `issues` is empty.

## 5. Decisions for tvofi

- **D1. How does an Off window stop the pump?** Gates (recommended): set-points
  to their gates, power stays on, frost protection intact. Power: the power
  switch off, which meets the 25 degC reset and the arbiter's stop-while-off rule.
- **D2. Turning Optimizer active off inside a Silent or Off window: undo what the
  window changed, once?** Yes (recommended): silent switch off, gated set-points
  back to configured, a third exception to the no-writes rule. No: the pump stays
  as the window left it, as today's gates do.
- **D3. May SW-1..SW-4 raise a structure budget to the measured value if the
  honest re-record needs it?** Yes (recommended), still merged on your review.
  No: fixers must pay for every line.
- **D4. GCHV Modbus silent through the night-mode schedule registers?** Yes
  (recommended, SW-4): one window per day, written only when the next window
  changes, at most twice a day. Later: GCHV rows show "not enforced" for now.

Defaults taken without asking: the capacity figure is the configured fraction;
unavailable silent falls back to normal with a warning; an Off row may not overlap
a hot-water window; boost and the legionella deadline win over a window.
