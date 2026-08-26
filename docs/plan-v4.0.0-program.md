# v4.0.0 — the 36-feature program

## Context

Main is past v3.12.0: the storage feature works, backlog items 1–33 are shipped,
PR #37's improvements are merged, and #38 shipped `smart_write` — cited line
numbers below are from the v3.12.0 survey and may have drifted slightly; treat
them as anchors, not gospel. A feature-ideation pass (10
lens-specialised agents → 100 proposals → 84 unique → 3-judge adversarial
ranking, weighted 45 % money / 30 % buildability / 25 % adoption) produced a
ranked list. The user selected **36 proposals** to implement.

The goal is to capture the money the optimizer still cannot see. The judges'
consistent finding was that spot-price shifting is largely already captured —
what remains is in the parts of a Swedish bill the integration does not model
(grid time-of-use fees, seasonal capacity tariffs, fuse sizing), in the hot-water
subsystem, and in a set of learners and guardrails that make the existing model
honest about its own uncertainty.

**Decisions, fixed by the user:**
- One PR per theme tranche (10 PRs since T0b was added), config-flow
  restructure first.
- *Added 2026-08-25:* the user's eight feedback items on the v3.16.0 layout
  editor are part of this program. Items 4 and 6–8 (config-flow grouping and
  the wrong valve-outlet description) were folded into T0; items 1–3 and 5
  (card mobile access, the missing heat-pump→DHW pipe, the unremovable
  "wood mixing valve" box, the "needs: Undefined" save bug) are tranche T0b.
- Build from fresh `origin/main`.
- Single **v4.0.0** release at the end; version strings move only in the last PR.
- **Every new configuration option is optional and default inert** — an
  untouched install must behave byte-for-byte identically.
- The options flow is regrouped, with less-used options under "advanced".

**This document is the program's source of truth.** It lives at
`docs/plan-v4.0.0-program.md` and is written to be executed tranche by tranche
by a session with only this repository in front of it. Each tranche is one PR;
follow the repo's existing conventions for branches, commit prose and golden
re-record discipline. Appendix A carries the full text of all 36 selected
proposals.

## Execution model guidance

Each tranche names the model tier it should be executed at. Ultracode
(multi-agent orchestration) is a session mode, not a model — keep it on for
every tranche's verification sweep regardless of tier. In a workflow, spawned
agents carry their own `model`/`effort`, and subagent tokens bill at the
subagent's rate, so a Fable orchestrator with Opus implementation lanes is
genuinely cheaper than an all-Fable run.

| Role | Tier |
|---|---|
| Implementation lanes | Opus, xhigh |
| Adversarial verification panel | mixed; **at least one Fable** on objective-touching tranches |
| Mechanical sweeps (golden review, translation triples, README counts) | Sonnet/Opus, low |
| Orchestration + final diff review | Fable on T1/T2/T4/T5/T7; Opus elsewhere |

Rationale: five plausible claims in the preceding session died only under
adversarial measurement. That instinct is where the stronger tier pays; routine
additive work does not need it.

---

## Program-wide ground rules

**G1 — Inert by default, proven.** Each tranche ends with: feature-off equality
assertions in `tests/features.py`; `tests/golden.py` green with only
deliberately re-recorded diffs; full `./tests/run.sh`. The 41 fixtures in
`tests/golden/` (37 plan scenarios + 4 `coord_*` + `config_flow.json`) are what
prove fresh-install identity.

**G2 — New config keys.** `CONF_*`/`DEFAULT_*` in `const.py`; read sites use
`config.get(CONF_X, DEFAULT_X)` only, **never presence checks**. Presence
inference exists today only for the two-zone/DHW trios
(`thermal_model.py:581-597`) and must not gain members. Entity selectors use the
bare-`vol.Optional` `_entity()` helper (`config_flow.py:853`), plus None
writeback in the page's save handler and membership in `_OPTIONAL_ENTITY_KEYS`.

**G3 — Translation triples.** Every new page/menu entry/field needs identical key
trees in `strings.json`, `translations/en.json`, `translations/sv.json`
(`entities.py:635-661` enforces key identity; Swedish must genuinely differ).

**G4 — Golden discipline.** Options-field add/move re-records
`config_flow.json`; a new coordinator data key re-records the four `coord_*`.
Review rule: feature work may add leaves only — a *changed* existing leaf is a
regression unless the tranche explicitly claims it.

**G4b — The five container-sensitive fixtures need an explicit drift gate.**
`valve_storage_smart_write`, `wood_two_tank`, `wood_two_tank_smart_write`,
`wood_coil` and `valve_upper_direct_slab` do not reproduce in this container
— and NOT at the last decimal: scipy lands these non-convex valve/wood
solves in a different local optimum (plan-shape flips, compressor-start
counts, leaf deltas up to ~2e1), identically on a clean checkout of main.
"Fails, as expected" is therefore not evidence — a real regression in
exactly these scenarios would hide behind the label. The gate, run before
each tranche merges: `PYTHONPATH=tests/hastub python3 tests/env_drift.py`
captures all five from the branch AND from an `origin/main` worktree in
the same environment and requires the two computed payload sets to be
**byte-identical**; a tranche that deliberately moves them must claim the
delta instead. Never re-record these five here. (T2 status: verified —
zero differing leaves across all five after T0+T0b+T1+T2 stacked.)

**G5 — README counts.** `entities.py:169-180` pins `### Sensors (N total)` /
Binary Sensors / Buttons against instantiated entities. Currently **47/3/3**.

**G6 — Savings claims need a null control.** Any SEK claim must show the effect
vanishes on `flat_prices`; guards get mutation tests (an input that must trip
it, one that must not).

**G7 — Objective-touching changes** (prices, bounds, `power_caps`, comfort
floors, COP, peak term) additionally run `SLOW=1 tests/rolling.py` and get a
golden scenario with the feature ON.

**G8 — Learner pattern.** Copy the canonical skeleton: snapshot →
`_learning_frozen(keys)` → rejection guards → **symmetric** trust-region clamp
about the current estimate (`_LEARNER_TRUST_REGION`, `coordinator.py:363`;
derivation at 1711-1727) → EWMA + max-step → apply-clamp → samples++ → store
save. One-sided contamination uses the asymmetric-alpha pattern; event detectors
copy `external_heat.py` (rate window guard, evidence strings, 2/2 hysteresis,
decay tail, user-entity override, `suppressing` property). New plan-affecting
learners ship behind a flag defaulting False.

**G9 — Stores.** Learned scalars ride `_thermal_learning_store`; bucketed
estimators ride the accuracy store; profiles/ledgers get their own `Store`.
Extend **additively** — the silent-fallback loaders discard reshaped payloads.

---

## Tranche order and dependencies

```
T0 config-flow restructure
T0b #40 follow-ups   card + topology fixes from the user's v3.16.0 feedback
T1 bill model        #1 #13 #19 #34 #23   builds: grid_fee.py, ledger.py, price σ
T2 peak & power      #7 #5 #3 #22         builds: state-change listener, time-weighted
                                          PeakTracker, fuse config, power_caps extra,
                                          simulate cap-override
T3 hot water         #32 #18 #20 #24 #47 #9 #28 #6   builds: draw-event library, inlet model
T4 model & learning  #42 #26 #11 #12 #21 #30 #17 #36 #53 #2   builds: snapshots.py, COP residual
T5 comfort floors    #16 #54              builds: lead-time error quantiles
T6 insight           #29 #52 #55 #65 #39 #40
T7 hardware          #61 (go/no-go)
T8 v4.0.0 release
```

Dependencies honoured: #40 ← T1 ledger + #55 wear; #28 ← #20 + #32; #12 ← COP
residual; #16 ← lead-time bands; #3/#5 ← fuse config; #7 ← listener infra; #39 ←
T2's simulate override; #47 ← T1's price-expectation helper.

Two changes from the draft grouping: **#16 moved to T5** (it is a comfort-floor
mechanism like #54, and T4 was 11 features to T5's one); **#32 runs first in T3**
because every downstream ready-target computation depends on draw energy.

---

## T0 — Config-flow restructure (PR 1) · Opus

**`section()` is rejected.** `hacs.json` pins HA ≥ 2024.1.0, the test stub has no
section support, and `golden.py:capture_config_flow` walks schemas one level deep
— sections would silently stop covering their contents. **"Advanced" is a
second-level menu**, which works on every supported version.

**Top menu:** `setup_overview`, `comfort`, `hot_water`, `tuning`, `grid`, `away`,
`advanced →`.
**Advanced submenu:** `entities`, `building`, `building_preset`, `thermal_model`
(new), `solar_pv`, `learning`, `heat_curve`.

*(Amended during execution, per the user's #40 feedback items 6–8.)* The
`mixing_valve` page is **merged into `building`**, which becomes "Heating
system and heat storage": one page for everything between the heat sources
and the emitters — valve mode/target/entities, `buffer_max_temp`, buffer
volume, radiator share, and the wood-tank block
(`valve_outlet_temp_entity`, wood tank probes, `wood_tank_volume`,
`dhw_wood_coil_enabled`) which moves off `learning`. The purely structural
four (`window_area`, `solar_heat_gain_coefficient`, `wind_sensitivity_factor`,
`rain_heat_loss_multiplier`) move `building`→`building_preset`. The
external-heat *detector* settings stay on `learning`; only the plumbing it
observes moves. `presets.derive()` outputs none of the moved keys, so
enabling the preset cannot overwrite them.

*(Second amendment, user decision 2026-08-25: two-zone must be switchable
both ways.)* Presence of a zone key can only ever turn the model on — setup
writes the keys into `entry.data`, where options cannot erase them — so the
`thermal_model` page carries an explicit `two_zone_mode` select
(`auto`/`on`/`off`, `CONF_TWO_ZONE_MODE`). `auto` — the default, and what
every entry without the key has — is the presence rule byte-for-byte; an
unknown stored value falls back to `auto` rather than disabling a running
model. G2's "presence inference must not gain members" stands: the mode is
an override above the inference, not a new member of it.

Surviving page **keys never change** (`entities.py:508` hard-codes five;
translations key on them); the one removed page's translations move under
`building` in the same commit. The user's #40 item 4 (the valve-outlet
description claimed the sensor "measures what the house actually receives";
in every modelled layout it measures the blend the wood valve sends onward)
is fixed here as part of moving those strings.

Mechanics: keep `_MENU_LABELS` as the flat dict of all leaf pages (now 13) so
its two load-bearing consumers (`golden.py:575`, `entities.py:463`) are
unchanged in shape; add `_TOP_MENU`/`_ADVANCED_MENU` partitioning it plus the
synthetic `advanced` entry; refactor `_menu_options()` into
`_translated_menu(step_id, labels)`; add `async_step_advanced`.

**Field moves:** `CONF_CYCLING_COST` grid→tuning (an objective knob in SEK);
`CONF_PRICE_PRIOR_ENABLED` grid→learning (a learned model toggle). This leaves
`grid` purely "what the DSO charges" — the clean append target for T1/T2.

**New `thermal_model` page** surfaces the 15 initial-flow-only keys
(`house_thermal_mass`, `heat_pump_max_power`, zone masses/losses, …). Needed now:
T2's fuse advisor and T4's capacity learner are only correct if a wrong
`heat_pump_max_power` can be fixed without deleting the integration.

*The presence hazard and its mitigation.* A `vol.Optional(key, default=…)` writes
its default on any untouched save, which would flip a legacy entry to two-zone.
This page therefore uses: for keys **already present**, `vol.Optional(key,
description={"suggested_value": current[key]})` (writing the current value back
is a no-op); for keys **absent**, bare `vol.Optional(key)` — an empty box is
omitted from `user_input` and never saved. Dedicated test: render and submit
`schema({})` from an entry with no zone keys, assert `two_zone_enabled` stays
False.

**Artifacts:** `config_flow.py`; the translation triple (init menu 7 entries, new
`advanced` step, new `thermal_model` step, moved fields); `tests/entities.py`
(menu split, partition assertion, **new guard: every schema key must have an
`options.step.<page>.data.<key>` translation** — closes today's silent-
untranslated blind spot); `tests/golden.py` (`capture_config_flow` also records
`_menu` structure); re-record `config_flow.json`; README.

**Initial flow untouched** — it is pinned by no test, and changing which keys land
in `entry.data` would change presence-inferred `two_zone_enabled`/`dhw_enabled`
for fresh installs.

~6 files, +550/−200. Risk **medium-low** (zero runtime change; both fixture
families and every translation move — which is why it ships alone and first).

---

## T0b — #40 follow-ups (PR between T0 and T1) · Opus · **executed**

The user's remaining feedback on v3.16.0's layout editor (items 1–3 and 5 of
their list; 4 and 6–8 were folded into T0). All card/topology work, no
optimizer surface. *Outcomes:* item 5 fixed both sides (catalog ships
`requirement`, card degrades without it); item 2 fixed (`heat_pump →
dhw_tank` composed on every layout when hot water is modelled); item 3
resolved by **dropping** the wood-valve box (tank-to-tank wood chain, the
outlet slot re-homed onto the wood tank / 4-way valve, stale payloads
re-homed in the card); item 1 fixed as far as this environment can verify
(blanket `svg { touch-action: none }` was swallowing touch on the setup
diagram — scoped to the chart — plus a wrapping dialog header and a
sideways-scrolling canvas at phone width); confirming the feel on a real
phone remains with the user. No golden re-record was needed: the coord_*
fixtures carry no topology payload.

1. **"needs: Undefined" save bug (item 5).** Root cause found during T0:
   `describe_setup()`'s catalog entries never include the `Layout.requirement`
   field, but the card renders `needs ${sameButUnusable.requirement}`
   (`heatpump-optimizer-card.js:1470`) when a drawn edge set matches an
   unusable layout — which is exactly the two-tank-4-way-without-coil case
   the user hit. Fix: add `"requirement": layout.requirement` to the catalog
   dict in `topology.py`, a card-side fallback for descriptions that predate
   the field, and a `card.mjs` case rendering the rejection text. Verify the
   4-way + two tanks + no coil arrangement saves (it is `selectable` and
   `valid` with a wood probe — the message was the bug, but confirm
   end-to-end).
2. **The heat pump visibly feeds the DHW tank (item 2).** `layout_edges()`
   never emits a `heat_pump → dhw_tank` edge, so the DHW tank floats
   unconnected in every drawing, coil or no coil. Add the edge whenever DHW
   is enabled (all layouts), keep `wood_tank → dhw_tank` for the coil, and
   update `match_layout` fixtures, the card drawing, and the setup-overview
   text. Editor round-trips must keep matching.
3. **The "wood mixing valve" box (item 3).** The `wood_valve` place is an
   artifact of the single-tank abstraction (the two-tank layout already folds
   it into the 4-way valve). The user finds the box meaningless and cannot
   remove it. Decide: either drop the place entirely — single-tank wood draws
   `wood_tank → buffer_tank` and the valve-outlet sensor slot moves onto the
   wood tank — or make the box deletable with both edge sets matching the
   same layout. Prefer dropping it: fewer boxes nobody owns. Migrate stored
   `CONF_TOPOLOGY_POSITIONS` for the removed place.
4. **Mobile setup page (item 1).** The card's setup page cannot be seen or
   entered on mobile. Investigate the card's tab/page navigation and canvas
   sizing on narrow viewports; fix CSS/interaction; cover what `card.mjs`
   can (page reachable, no horizontal dependence), note what only a device
   can verify.

~4 files (topology.py, the card, card.mjs, goldens for the setup payload).
Risk **medium** — drawing and matcher must move together or the editor
rejects its own default drawing.

---

## T1 — Bill model (PR 2) · **Fable** · #1 #13 #19 #34 #23 · **executed**

*Outcome notes:* built as specified, with one honest deviation from G6's
null-control wording: "flat spot + flat fee ⇒ plan identical" does not hold
for this optimizer — a uniform price rise legitimately buys slightly less
energy against the comfort weight (measured ~3.5% on the flat-price day).
The recorded null control is therefore *timing invariance*: a structureless
fee moves no energy in time (06–22 share unchanged within 2%), while a
höglast fee measurably empties the hours it prices up. The masks (#13) are
implemented as billed-equivalent kW — the tracker records a window's average
scaled by its hour's factor, and a masked-out month's windows are not
recorded at all. #34's sigma tracks *shape* dispersion per (profile, hour);
level risk is the level calibration's problem and normalisation removes it.
New fixtures: `peak_masked`, `price_risk`, `coord_grid_fee`.

Order: #1 → #13 → #19 → #34 → #23.

**Infrastructure built once:**
1. **`grid_fee.py`** — `GridFeeSchedule.from_config()` parsing rules like
   `"Nov-Mar Mon-Fri 06:00-22:00 = 0.25"` (reuse `dhw_schedule` parsing
   conventions); `fee_vector(step_starts)`, `current_fee(when)`.
2. **The fee chokepoint** — one `_fee_series()`/`_current_fee()` used in exactly
   three places so fees can never diverge: `_price_series`
   (`coordinator.py:2926`) **after** `extend_price_series` returns;
   `_get_current_price` (:3206); the settlement `pending` dict feeding
   `_accumulate_energy` (:4298). Tibber's `total` includes tax/VAT but **not** the
   DSO transfer fee, so this is additive, not double-counted.
3. **`ledger.py`** — month-keyed `{"YYYY-MM": {line: {kwh, sek}}}` with its own
   Store, pruned to 24 months. Fills the "no monthly bucketing anywhere" gap once;
   T6 extends it.

**Keys** (all on `grid` unless noted): `grid_fee_mode` `"none"` (sentinel ⇒ zeros);
`grid_fee_rules` `""`; `grid_fee_entity` unset; `grid_fee_fixed` `0.0`;
`peak_tariff_months` `""` (empty = all months = today); `peak_tariff_hours` `""`;
`peak_tariff_weekdays_only` `False`; `peak_tariff_offpeak_factor` `1.0`;
`price_risk_lambda` `0.0` (tuning; λ=0 ⇒ prior steps priced at the mean as today);
`contract_fixed_price` `0.0`.

**#19 (96-bin prior)** keeps the 24-bin `shapes` untouched and **adds**
`quarter_factors[profile][96]` with its own confidence ramp — old stores load
unchanged, fresh behaviour identical until quarter evidence exists. *Bug found
while reading:* `hourly_from_entries` (`price_model.py:238`) assigns
`by_day[...][when.hour] = value`, so with Tibber 15-minute entries the hourly
learner trains on the **:45 quarter only**; derive the hourly observation as the
mean of the four quarters (affects days observed after upgrade only).

**#34** adds an EWMA of squared prior residuals per (profile, hour);
`extend_price_series` returns a third `sigma` array (zeros on known steps); the
objective prices unknown steps at `price + λ·sigma`.

**Must not:** add fees before `extend_price_series` (contaminates the learned
shape *and* mis-scales level calibration, `price_model.py:188-201`); let
`observe_day` see fee-inclusive prices; let masked-out months contribute to
`PeakTracker.peaks` (must contribute nothing, not a discount); bump the
price-model store version.

**Verification:** fee-off price-array identity; `tou_grid_fee` golden scenario;
null control (flat spot + flat fee ⇒ plan identical to flat spot); mask-off
bit-identity for #13 and a mask mutation test; #19 fresh-model identity; #34 λ=0
identity plus a directional assert; #23 accumulator arithmetic vs a hand-computed
month. G7 applies.

~9 files, +900/−60. Risk **high** — #1/#13/#34 all reach the objective.

---

## T2 — Peak & power (PR 3) · **Fable** · #7 #5 #3 #22 · **executed**

*Outcome notes:* built as specified, with three findings worth recording.
(1) The per-channel `power_caps` array alone could not hold the fuse line
through a DHW block — space headroom was `min(p_max − dhw, caps)`, so
space + DHW could exceed an external *total* cap while each channel obeyed
its own. The extra cap is therefore threaded into the horizon
(`_Horizon.power_caps_extra`), bounds the DHW block's run power, and is
subtracted per-step in `solve_space` — deliberately without touching the
existing valve-install composition, which stays byte-identical. (2) The
test battery caught the meter listener dead on arrival: `_on_power_event`
passed the raw state string and the whole attributes dict to
`normalize_power_kw(value, unit)`, so every live event was dropped; and
`GuardState.update` discarded the sample that announces a new window,
making engagement need three events instead of two. Both fixed. (3) The
adversarial review round caught four more, all fixed with regression
tests: the advisor called a simulate method that did not exist (dead
feature, swallowed by the cycle's blanket except — the advisor now runs
end-to-end in tests, stubbed at the real method name); `_on_power_event`
lacked `@callback`, which in real HA dispatches it to an executor thread
where `async_create_task` raises; the guard compared a raw-kW projection
against a billed-equivalent threshold, so it would defend half-rate and
free hours (`window_snapshot` now returns the window's #13 factor and
both sides compare billed-equivalent, with the fuse compared raw);
and `power_cap_breach_c` judged the *initial* temperature against the
floor and dropped the last step (trajectories are n+1 long) — fixed, and
the advisor additionally attributes to the fuse only the shortfall the
capped plan adds over the uncapped baseline, so a cold snap is not
blamed on the candidate fuse. Weighted window accumulators now persist
across restarts; a rate-limited or echo-mismatched what-if is discarded
and retried tomorrow without displacing last month's verdict, and the
advisor restores the card's simulate cache. New fixture: `fuse_guard`
(60%-of-nameplate cap on the DHW winter day; `power_cap_breach_c` 0.0).
The suppression flag is deliberately byte-equivalent to
`external_heat_active` at the solver — the tests pin that equivalence.

Order: infra → fuse config → #5 → #3 → #7 → #22.

**Infrastructure:**
1. **`power_guard.py`** — the program's first `async_track_state_change_event`
   listener, registered only when the guard flag is on. Decision logic is a **pure
   function** `project_window_mean(window_sum, elapsed, current_kw, remaining)` so
   tests never touch the event system. `tests/hastub/.../event.py` gains the
   tracker (recording callbacks so tests fire synthetic states).
2. **Time-weighted `PeakTracker`** — `observe()` gains an optional `dt_hours`
   weight; without it, the existing unweighted path is bit-identical, so the
   30-min tick path and all goldens are unchanged while the listener supplies real
   dt.
3. **`power_caps` extra** — `optimize(..., power_caps_extra=None)`, elementwise
   min'ed into the existing array. Allocation stays conditional (valve **or**
   extra caps), so the no-valve byte-identity checks stay green.
4. **Simulate cap override** — `async_simulate_plan(..., power_cap_kw=…)` threaded
   through `power_caps_extra`, used by #3 and later #39.

**Keys** (grid): `main_fuse_a` `0` (0 = unconfigured ⇒ advisor/guard/headroom all
dormant); `main_fuse_phases` `3`; `fuse_guard_enabled` `False`;
`peak_guard_enabled` `False` (listener not even registered when off);
`peak_guard_margin_kw` `0.5`; `outage_recovery_enabled` `False` (learning).
`fuse_kw = A × phases × 230 / 1000`.

**#5** ships as a **sensor, not a number entity** — the value is read-only
telemetry; a `number` implies writability and a new platform. Value
`min(fuse_kw?, threshold_kw) − current_house_kw`, clamped ≥0; per-step horizon
headroom in attributes, with `baseline_source` documented (`_baseline_house_load`
is flat and zero without a house meter).

**#3** runs `async_simulate_plan` at the next-smaller fuse on month rollover
(≤ weekly), publishing feasibility/margin/comfort-delta/SEK as Monthly Peak
attributes. The guard sets `power_caps_extra = fuse_kw − baseline` — a hard
per-step bound, not a new objective term.

**#7** folds each meter event into the tracker (time-weighted), projects the
window mean, and on `projection > threshold − margin` sets a `suppressing` flag
consumed where `external_heat.suppressing` already gates electric DHW, nudging
displace. Release at window close or with 2/2 hysteresis. **Never suppress** while
the DHW tank is below minimum or a comfort floor is breached. **No solve on the
event path**, ever; ≥10 s throttle.

**#22** persists `last_tick`; a gap > 90 min with the flag on opens a 2 h recovery
window that forces the peak term active (overriding the fresh-month infinite
threshold, `tariff.py:150`) and delays DHW behind space for 45 min unless the tank
is low.

**Must not:** actuate on anything but suppression *transitions*; make
`power_caps` allocation unconditional; change `billed_peak_kw` for existing
installs via the weighting; give `main_fuse_a` a plausible default (a wrong 16 A
would cap a 20 A house).

**Verification:** pure-function guard tests (crossing ⇒ suppress; sub-threshold ⇒
not; floor override wins); weighted≡unweighted on uniform samples; cap respected
every step with a mutation showing an infeasible cap surfaces as a reported
violation, not silence; synthetic 3 h gap ⇒ recovery, 20 min ⇒ nothing; new
`fuse_guard` golden. G7 applies.

~8 files (+1 hastub), +850/−40. Risk **high** — new event infra + live actuation.

---

## T3 — Hot water (PR 4) · Opus · #32 #18 #20 #24 #47 #9 #28 #6 · **executed**

*Outcome notes:* built as specified, with these decisions and findings.
(1) #20's blend lives in the optimizer, next to the mean it blends
against (`dhw_window_ready_energy` carries `(p90, count)` pairs, the ramp
is applied at the ready loop) — computing the blend in the coordinator
would have duplicated the mean's definition. (2) The draw statistic
records whole *occurrences* (one number per window per day, zeros
included) rather than tick samples, keyed by the window's spec string so
redrawn windows honestly forget. Heated intervals fold as lower bounds;
external-heat intervals are skipped outright. (3) #47 grew a
reachability guard during testing: the elastic placement had picked the
cheapest step even when the tank physically could not heat to the
disinfection temperature by then — a constraint the solver silently
relaxes — so candidates now start at the earliest step the pump can
reach the target. The honest inert control is elastic-ON with a young
prior (ceiling None ⇒ byte-identical to off); a flat-price day with a
trained prior legitimately runs the cycle early at zero marginal cost.
(4) #24's hold accumulates only hot-to-hot observation gaps — crediting
a gap that STARTED cold let a blip-cold-blip sequence pass the hold.
(5) The dhw None-presence quirk is fixed in the presence trio itself
(`config.get(key) is not None`); empty-string windows still count, and
none of the twelve new hot_water keys joins the trio. (6) The directional
tests run on flat prices with a 1500 L tank: on the winter day the
planner charges the tank for arbitrage anyway, and on 300 L one DHW
block moves it 3.4 °C — both swamp exactly the target changes under
test. Sensors 49 → 52 (Setpoint Advisor, Mixed Hot Water, Heavy Day
Demand); the G4b drift gate verified all five container-sensitive
fixtures byte-identical to origin/main after the tranche.

*Review round (1 major, 7 minor, all fixed with regression tests):*
the young-prior #47 control did not exist — a damped fresh shape put the
"expected daily minimum" at the daily MEAN, so an opted-in fresh install
would have run cycles at the minimum interval every time;
`expected_daily_min` now answers None until every requested day type is
fully trained, and a coordinator-path test pins it. The VVC lead probed
the single instant now+lead, going dark in the final approach to any
window shorter than the lead — now "does any window open within the
lead". The setpoint advisor gained its documented profile-mean fallback
(it recommended 48 °C for everyone) and, on tanks too small to hold
their heaviest window at any setpoint, recommends the top candidate
flagged `covers_heaviest_window: false` instead of answering nothing.
#20 is explicitly scoped to configured time frames (learned-window
labels can never match; option text updated). The open draw occurrence
persists on every energy-bearing fold, not only at close. A failed pump
command is retried (state recorded only after success), and a
configured VVC pump with hot water disabled is left ON, never abandoned
in its last commanded state. #18's blend trust counts distinct days,
not sensor ticks. The empty-table byte-identity test compared a solve
to itself; it now actually passes `{}`.

Infrastructure: **`dhw_draws.py`** (draw-event detection reusing the existing
standby-subtraction attribution; per-window reservoirs of event energies;
quantiles; own Store) and the **inlet model** on `ThermalParameters`.

**Keys** (hot_water): `dhw_inlet_temp` `10.0` (replaces the two hard-coded 10.0s
at `thermal_model.py:368,942` with the same value);
`dhw_inlet_seasonal_amplitude` `0.0`; `dhw_inlet_entity` unset;
`greywater_recovery_effectiveness` `0.0`; `dhw_quantile_targets_enabled` `False`;
`dhw_free_disinfection_enabled` `False`; `dhw_elastic_legionella_enabled`
`False`; `dhw_legionella_min_interval_days` `5`; `shower_flow_lpm` `8.0`
(display-only); `vvc_pump_entity` unset; `vvc_lead_minutes` `20`;
`space_circulation_pump_entity` unset.

**#18** adds `weekday`/`weekend` arrays beside the pooled profile (old stores load
pooled-only ⇒ identical), blended `w = n/(n+K)` toward pooled; the volume-
preservation invariant of `effective_dhw_draw_pattern` must hold **per day-type**.

**#20** replaces the mean draw energy feeding `ready_temps` with cold-start + p90
per window, falling back to the mean below 8 events (ramp, not gate).

**#24** integrates minutes above `dhw_legionella_temp` and writes the completion
timestamp exactly as a planned cycle does. **#47** schedules now iff
`min(known dhw_prices) ≤ E[min over remaining days]` from a new
`price_model.expected_daily_min()`; the hard deadline still forces placement.

**#9** is a read-only sweep sensor (48–60 °C candidates replayed against learned
profiles/quantiles/cooling/inlet). **#28** is greenfield display math:
`mixed_litres = V·(T_tank − T_inlet)/(40 − T_inlet)`.

**#6** (`pump_schedule.py`) actuates on transitions each tick. **Space-pump safety
rails** (the risky half): forced ON when the plan commands heat this or next step,
when displace is being driven, when any zone is within 0.3 °C of its floor, and
when outdoor < 0 °C. Off only in provably idle, warm slots.

*Noted during T0's review, for this tranche:* the entities page writes
`dhw_temp_entity: None` back when the sensor is cleared, and the
`dhw_enabled` presence rule counts a None-valued key as present — so
clearing a DHW sensor can phantom-enable hot water on an entry that never
had it. Pre-existing; fix here (where DHW semantics are already in scope),
either by ignoring None in the presence trio or with a `dhw_mode` override
mirroring T0's `two_zone_mode`.

**Must not:** change the `10.0` inlet default (every ready target sits on it — assert
bit-identity); let new hot_water keys join the `dhw_enabled` presence trio; let
contaminated events (external heat, frozen learners) reach the reservoirs; treat
the space pump as a cost actuator the optimizer reasons about (it is a
loss-trimming follower — no solver coupling in this program).

**Verification:** inlet default identity; off-equality per flag; #18 blend-at-zero
identity; #20 directional + volume preservation; #47 flat-price null; #24
mutation (58 °C for an hour must not credit; 61 °C for the hold must); #6 rail
mutations (cold snap ⇒ pump on regardless). README 49→52.

~10 files, +1100/−60. Risk **medium**.

---

## T3b — Shared-step honesty (small PR between T3 and T4) · user-reported · **executed**

*Outcome notes:* built as scoped. The chart marks shared spans with a
hatched band (drawn under the bars, only while both power series are
visible — a hidden channel takes its half of the story with it) whose
native tooltip and the hover tooltip both say "the pump alternates
circuits, hot water first"; `_plan_slots` gained the additive
`shared_kwh` (the other channel's energy inside a slot's shared steps,
absent when zero, and callers that pass no other channel produce the
pre-T3b slot byte for byte); the README explains the time-share at the
capacity diagram. The solar fallback reads the solar plan sensor's own
state + source tag ("120 W/m² · Open-Meteo" / "weather forecast"), so
"not configured" now only ever describes a value the plan truly lacks.
Slot rows prefer `hass.formatEntityState` — the user's unit system and
display overrides apply exactly as everywhere else in the frontend —
with the raw concatenation kept for older frontends. One test-harness
lesson recorded: the chart's default view window clips the horizon's
first hours, so fixtures that doctor overlap steps must place them deep
enough to be visible.

*Review round (no blockers, five polish items, all fixed):* the band
rect spans the full plot and paints after the what-if lanes, so it
needed `pointer-events: none` or a low-power shared span would have
swallowed the slot editor's drags; the tooltip's shared line now
requires both rows to come from the SAME timestamp (each series snaps
to its own nearest point, and mismatched grids could pair points hours
apart); the shared line moved into `_sharedTooltipHtml` and gained
direct tests; the pattern id is unique per chart (inline + dialog
render into one shadow root); and a comment that documented a defense
that did not exist was rewritten to say what the code actually does.

*Reported on v3.16.0:* the card shows hot water and space heating planned
in the same period even at maximum zoom, and the user could not tell
whether the display or the planner was wrong. Investigated: neither is
broken, but the story is untold. The optimizer's per-step contract is
``space + dhw ≤ p_max`` — a deliberate time-share relaxation. A step with
4.8 kW DHW + 1.2 kW space on a 6 kW pump means "this quarter-hour is
~80 % tank, ~20 % heating circuit"; the diverter valve serves one circuit
at an instant and alternates with DHW priority, so within-step sharing is
physically realizable, and hard per-step exclusivity would make the solve
combinatorial for no gain. Verified across all 31 DHW golden fixtures:
every overlap step respects the capacity sum exactly.

The defect is that nothing says this. Scope (display + docs only, plan
byte-identical by construction):

1. **Card:** where a space slot and a DHW slot overlap in time, mark the
   shared span visibly in both lanes (hatched overlay) and say it in the
   tooltip: "Shared quarter-hour: the pump alternates circuits — hot
   water first. X kWh hot water, Y kWh heating." No new entities.
2. **Plan sensors:** `_plan_slots` slots gain a `shared_kwh` field where
   the other channel is active in the same steps (additive attribute —
   coord goldens re-record as additive-only).
3. **README:** the DHW capacity diagram gains the time-share paragraph —
   "a step can carry both loads; that is the pump splitting the quarter
   hour, not both circuits running at once."

*Two more card defects reported on v3.16.0, same tranche:*

4. **The Outside box says "not configured" for solar radiation even when
   Open-Meteo supplies it.** `_slotLive` only reads the configured entity
   and `describe_setup` is config-pure, so the fetched irradiance never
   reaches the diagram. Fix in the card: when the solar slot has no
   entity, fall back to the published `solar_radiation`/`solar_source`
   ("210 W/m² · Open-Meteo"); if those keys are not reachable from an
   entity the card already reads, extend the plan sensor's attributes
   additively. Never show "not configured" for a value the plan is
   actually using.
5. **Slot values ignore the user's unit system** — the wood tank probes
   render as raw `state + unit_of_measurement`, so a natively-°F probe
   shows °F on a metric install while every other HA surface converts.
   Fix: format slot rows through `hass.formatEntityState` when the
   frontend provides it (raw concatenation as fallback) — fixes every
   slot, not just the wood tank.

**Must not:** change any schedule; add exclusivity constraints; touch the
objective. Verification: card test for the shared-span rendering + a
features check that `shared_kwh` sums match the overlap integral on a
fixture with known overlap steps; card tests for the solar fallback (no
entity + meteo data ⇒ value with source tag, no entity + no data ⇒
"not configured" stays) and for formatEntityState being preferred.

---

## T4 — Model & learning (PR 5) · **Fable** · #42 #26 #11 #12 #21 #30 #17 #36 #53 #2

**Split executed at the pre-agreed point:** T4a (#42 #26 #11 #12, insurance +
detectors) shipped as its own PR; T4b (#21 #30 #17 #36 #53 #2, weather inputs +
learners) follows as the next tranche.

*T4a outcome notes:* built as scoped, on two new modules. **`drift.py`** is the
one CUSUM primitive all three detectors share — one-sided, drift allowance,
hysteresis release at threshold/4, evidence trail capped at six, `as_dict`/`load`
with thresholds code-owned (never persisted). **`snapshots.py`** is the weekly
ring (8) plus the daily bias watch; the coordinator serialises snapshots
exclusively through `_learner_snapshot_payloads()`, which reuses every store's
own producer — the thermal-learning save path was refactored onto the same
`_thermal_learning_payload()` so there is exactly one serialiser (a features
check now pins that). Auto-rollback fires once per alarm, only when every
counted drift day had healthy inputs, and restores the newest snapshot that was
both healthy and in-band at capture; `restore_learned_snapshot` is the manual
override. **#26** feeds the residual `_async_learn_house_heat_loss` already
computes, clipped to `VENT_CUSUM_CLIP_C` = half the threshold — chosen during
testing after the draft's ±2 °C clip was caught letting a single glitched
reading trip a 1.2-threshold detector on its own, contradicting the design
comment; at half the threshold at least three consecutive abnormal samples
(~1.5 h) are needed. While tripped, `_learning_frozen()` says "ventilation" and
the heat-loss learner passes through detector-feed-only, which is what lets the
window's closing release the freeze. Binary sensors 3→4 ("Open Window
Detected", WINDOW class, evidence attributes). **#11** latches on 2/2 samples
over nameplate × 1.15 while commanded, skips COP folds while latched, books the
excess as its own "immersion" ledger line, and (gated) three rescues in 14 days
raise `params.dhw_ready_margin_c` to 2.0 — 0.0 is byte-inert in the solve by
construction and a mutation pair proves both directions. **#12** keeps the
per-3 °C-bucket COP baseline fed only through `_learn_measured_cop`'s already-
guarded path (frost band, immersion, freezes, low duty all inherited), judges
the shortfall before the observation joins the baseline, and raises/deletes the
`cop_degradation` repair issue with an SEK/month estimate. All detector memory
rides the thermal-learning store additively; a pre-T4 payload loads clean with
every detector quiet. Goldens: coord_* re-recorded additive-only
(ventilation/immersion/cop_health/snapshots keys), config_flow re-recorded for
the two new learning-page toggles, optimizer fixtures untouched.

*T4a review round (1 critical, 9 major, 7 minor, 1 nit — all fixed forward,
none deferred):* the critical was the rollback restoring the AccuracyTracker,
which erased the alarm's own evidence — the next counted day read in-band,
released the alarm, deleted the notice, and under genuine drift the cycle
repeated until a drifted snapshot laundered itself into the restore pool; the
tracker is now never restored (it is evidence, not a learner), snapshots taken
during an active alarm are excluded from the pool, and during an alarm only
snapshots older than the out-of-band streak qualify (slow drift keeps its
bias tag in band for days after the learners walked away). The majors: `take()`
now deep-copies via a JSON round trip (payloads aliased live learner state —
a week-old snapshot mutated in place, making defrost/price rollback a no-op);
the restored defrost derate is rebound onto `thermal_params` and the restored
comfort learner re-applies its weight (the model otherwise kept reading the
orphaned pre-restore objects); the CUSUM statistic is capped at 1.5× threshold
(release lag no longer grows with trip length) and a tripped vent latch that
nothing has fed for 6 h force-releases as stale (the feed dries up entirely in
mild weather, and a latch nothing can feed froze every learner indefinitely);
both repair issues are `is_persistent` (they survive the restart their alarm
state survives); the bias streak is persisted daily, not weekly (a restart on
drift day 3 rewound the count); the COP baseline stops absorbing samples while
tripped (the EWMA otherwise re-anchored to the fault and a permanent
degradation cleared its own issue); the DHW profile gained the shared
`_dhw_profile_payload()` producer and day-type profiles now restore with the
pool. Minors: staleness outranks ventilation in `_learning_frozen` so a dead
battery's flatline cannot drive the detector through the vent-only pass; the
immersion ledger line is carved OUT of the spot line (lines sum to metered
energy; the contract settlement folds it back in); SEK/month scales
month-to-date receipts to a full month; the young COP baseline uses a plain
mean until twenty samples so one outlier first interval cannot anchor it; the
heartbeat gates on the snapshot store having loaded (the first cycle could
snapshot half-loaded learners over the persisted ring); day health is
accumulated worst-of-day across heartbeats instead of sampled at one tick; the
relax gating and the rollback-alarm interplay got direct tests (the original
rollback-once check had passed for the wrong reason). Features suite grew to
662 checks in the round.

*T4b outcome notes:* built as scoped, on the T4a-verified hook sites. **#21**
ships ungated: `relative_humidity_2m` rides the existing Open-Meteo forecast
request (hourly), overlays the weather entity's per-entry humidity by
wall-clock time, and threads as an appended `ForecastArrays.humidity` (NaN =
unknown = the ambient fallback) through `optimize()` into every
`simulate_step` — the derate lookup now sees each step's own air. Inert by
construction with zero defrost evidence, and an all-NaN series is dropped
before the objective's inner loop so the no-data path costs nothing. **#30**
(two gates): the optimizer's precipitation array is pre-weighted by the
liquid fraction (snow does not wet the envelope) at the chokepoint where the
horizon is assembled, so with the flag off the array is byte-identical; the
roof-snow damping keeps a decaying snowfall accumulator (decay over the full
gap, credit over a bounded one — the first draft clamped both and kept
two-day-old snow fresh forever, caught by its own test) whose heavy-fall
trigger halves modelled solar for two days, persisted so a restart does not
brighten the roof. **#17** learns the per-3 °C upper envelope of delivered
thermal power in `_learn_measured_cop`'s vetted tail and composes its
electrical caps through T2's `caps_extra` via `np.minimum` — never a second
channel — floored at 0.6 × nameplate. **#36** regresses sunny-step residuals
(EWMA moments) against modelled Q_solar into `solar_aperture_scale`
[0.3, 2.0], applied per solve; the convergence test runs the honest closed
loop after an open-loop draft overshot. **#53** learns per-hour internal
gains from dark intervals only (sunny surplus belongs to #36 — a hard
attribution split), ridge-tethered to the configured constant, threaded as
`hour_of_day` through the step functions. **#2** (`curve_learning.py`) creeps
the ECL110 displace bias down ≤0.5 K/week on days that held comfort with
margin and resets to 0 instantly on any miss with the bias applied; it joins
the displace after every guard, before the configured clamp. All four
learners persist additively on the thermal store through one parser shared
with the snapshot restore, and every T4b flag gates learning AND application
together. New goldens: `capacity_curve` (a per-step VARYING cap through
caps_extra — the fuse fixture only ever exercised a constant) and
`precip_snow` (the liquid-fraction transform on a wet mild day); coord_* and
config_flow re-recorded additive-only. One harness lesson recorded: the
golden recorder's `--only` filter re-recorded all fixtures, and the five
machine-sensitive ones had to be restored from HEAD — the never-re-record
rule needs the recorder's cooperation, not just the operator's.

*T4b review round (1 critical, 3 major, 5 minor, 3 nits — all acted on):*
the critical was that first restore failing silently: the recorder job ran
two `--record` passes, and the second rewrote the five protected fixtures
AFTER the restore, so the container-local bytes were committed anyway (and
the "all 52 unchanged" run that looked like good news was comparing the
tree against its own fresh recordings). The review proved behaviour
byte-identical across the revisions at default flags, the fixtures are
restored from the T4a merge commit, and the `--only` fix makes the class of
accident unrepeatable. The majors: #53 was an open-loop integrator — the
learner replay predicted with the flat constant, so its residuals never
re-centred and the profile converged to α/ridge = 2.5× the true correction;
both learner replays now pass `hour_of_day`, closing the loop the way #36's
scale always was, with a source-pinned regression. #17's envelope was
self-censoring — the caps limit the plan, the plan limits the samples, and
every partial-load bucket would have ratcheted to the 0.6 floor within
weeks; only near-nameplate commands (≥95%) are envelope evidence now, since
partial load bounds nothing. #2's comfort tracker read the normal floor
while away mode enforced a lower one inside the solve envelope, so every
vacation read as a comfort miss and wiped the bias; the tracker stands down
during away/recovery and whenever the indoor sensor's learners are frozen.
Minors: the snow accumulator's clock persists (a restart after a multi-day
outage skipped the decay and could re-trip the roof damping on stale snow);
rollback resets the aperture moments and curve bias too, so a pre-T4b
snapshot restores to inert rather than merging; the buffer-refusal cap
shave simulates with the same per-hour gains as the objective; the
liquid-fraction arithmetic moved into a named helper with direct tests
(all-snow 0, half-snow ½, cross-source disagreement clips); Open-Meteo's
plausibility ceiling is per-variable now (the GHI limit meant nothing to a
humidity series). Features suite closed the round at 711 checks. The
timing gate also caught the per-step hour threading costing ~5% of solve
time on the default path (interleaved A/B against main); the hot loops now
compute the hour only when a learned gains profile exists, restoring
parity within noise with byte-identical outputs.

**Infrastructure:** **`snapshots.py`** — weekly ring buffer (8) serialising every
learner's existing `as_dict()` tagged with `accuracy.summary()`; drift test on
`temperature_bias` out of band 5 consecutive days ⇒ repair issue + one-click
`restore_learned_snapshot` service; auto-rollback only when inputs were healthy
throughout. Add a no-op `issue_registry` stub to the hastub.
**`AccuracySample` gains `cop_residual`** (`from_dict` is already tolerant of
missing keys).

**Keys:** `open_window_relax_enabled` `False` (detection + learner-freeze ship
default-ON as guard extensions, plan-neutral; only the comfort relaxation is
gated); `immersion_feedback_enabled` `False` (detection + ledger line default-on;
the DHW margin nudge gated); `precip_type_enabled` `False`;
`snow_roof_factor_enabled` `False`; `capacity_curve_enabled` `False`;
`solar_aperture_learning_enabled` `False`; `internal_gains_learning_enabled`
`False`; `curve_learning_enabled` `False` (heat_curve).

**#26** runs CUSUM on the residual already computed in
`_async_learn_house_heat_loss` (`coordinator.py:1680`); trip ⇒ freeze reason
`"ventilation"` + a binary sensor (3→4). **#11** detects `measured_power >
hp_max × 1.15` while heating and books a COP-premium ledger line. **#12** keeps a
long-baseline COP per 3 °C bucket updated **only outside the frost band**
(disjoint attribution) with weeks-scale CUSUM ⇒ repair issue with SEK/month.

**#21** adds `relative_humidity_2m` to the Open-Meteo fetch and a `humidity` array
to `ForecastArrays` (**append** the NamedTuple field — never insert), so the
defrost derate evaluates per step in both solve paths. Inert by construction: with
zero defrost samples the derate is 1.0 everywhere. **#30** separates `snowfall`
from `precipitation` and weights the rain multiplier by liquid fraction.

**#17** learns an upper envelope of delivered thermal power per 3 °C bucket and,
when enabled, caps per-step electrical power at
`max(envelope, 0.6 × hp_max_power)` through T2's `power_caps_extra`, gated at ≥5
samples per bucket. **#36** regresses sunny-step residual against modelled
`Q_solar` into a scale clamped [0.3, 2.0]. **#53** fits a ridge-regularised
per-hour internal-gains vector toward the configured constant. **#2**
(`curve_learning.py`, shaped like `comfort_learning.py`) accumulates a displace
bias with asymmetric steps — down ≤0.5 K/week, **instant full reset up on any
comfort miss** — clamped [−4, 0] K.

**Must not:** bypass `_learning_frozen` or the trust region; disturb the
load-bearing learner ordering in `_update_current_state`; let #17's cap reach zero
or undercut comfort-feasible power (a starved house at −15 °C is the program's
worst failure mode); let #12's baseline include frost-band samples; serialise
snapshots by any path other than the learners' own `as_dict()`.

**Verification:** off-equality per flag; #26/#11/#12 mutation pairs; #21
zero-samples identity; #17 envelope never above nameplate and floor respected;
#42 snapshot→corrupt→rollback round-trip. New goldens `capacity_curve`,
`precip_snow`. G7 mandatory. **Pre-agreed split point after #12** (T4a detectors +
insurance / T4b learners) if review size demands it.

~12 files, +1400/−80 — the largest tranche. Risk **high**.

---

## T5 — Comfort floors (PR 6) · **Fable** · #16 #54

Isolated deliberately: both features move the comfort floor inside the objective.

*Outcome notes:* built as scoped, both floors through ONE new optimizer
channel — `optimize()` gained `min_temp_margins` (additive per step) and
`min_temp_floors` (absolute per step), applied at the single site where the
temperature bounds are built so every consumer (objectives, safety releases,
pin repair) sees the same effective floor, with a band-never-shut clamp at
`max − 0.5` that runs only when either argument is present. The lead-time
infrastructure lives on the AccuracyTracker: each solve files one promise per
bucket {1, 3, 6, 12, 24 h} ("at T+k the room will be X", the same trajectory
and mode gate the one-step sample uses), matured promises score into a
per-bucket EWMA of |error| within a ±30-minute matching window (a promise
that misses its window is discarded unscored — filing it under the wrong lead
would corrupt the very statistic), and `sigma(lead)` answers from the nearest
bucket with evidence, zero with none. All of it persists additively on the
accuracy store, pending promises included, so a restart does not starve the
long buckets. **#16** computes `min(sigma(lead_i) × (1 − trust), 0.8)` per
step — trust at 1 margins nothing however noisy the history, no history
means sigma 0 means byte-inert, and cap+damping is the anti-oscillation
argument: the margin can only shrink as accuracy improves, so the
margin→plan→errors loop has a contracting fixed point (asserted on replayed
history). **#54** got a closed form instead of the planned bisection: with
the measured vapour pressure held constant, surface RH < 80 % inverts to
`T_room ≥ T_out + (T_dew(e/0.8) − T_out)/fRsi` (Magnus both ways,
module-level functions in thermal_model with round-trip tests), evaluated
per forecast step so colder nights raise the floor. Double-gated on flag AND
a live humidity entity, and capped at the comfort target — at 60 % indoor RH
and −15 °C the honest physics wants 27 °C, and heating past target to fight
a ventilation problem is the runaway the cap forbids. Keys: tuning page got
the margins flag; the comfort page got the mold flag, the humidity entity
(device-class-filtered picker, clearable) and fRsi (default 0.75, the BBR
guidance value). New golden `confidence_margins` rides both channels in one
solve; coord_*/config_flow re-recorded additive-only. The recorder's fixed
`--only` recorded exactly one fixture this time.

*T5 review round (0 critical, 3 major, 6 minor, 4 nits — all acted on):*
the three majors were all "the promise machinery believes the plan more
than the plant". **Bucket starvation**: the scoring window was the fixed
±30-minute tolerance, so any install whose optimization interval is coarser
discards every promise maturing between ticks and the long buckets starve
forever — `score_lead_predictions` now takes the caller's cadence as
`window_hours` (floored at the tolerance) and the coordinator passes its
configured interval. **Void promises**: leaving auto/economy
(`async_set_mode`) now clears unmatured promises — in comfort/boost/off the
room is driven by fixed rules and scoring the dead plan's promises would
charge the model with errors it never made; an active sys-ID experiment
likewise files nothing and voids what the overridden plan had filed.
**Away-blind mold cap**: the floor was capped at the *live*
`_opt_config.target_temp`, which the away setback lowers — disarming the
guard exactly when mold risk peaks (a cold, damp, unheated house). The cap
is now the *configured* comfort target, with an explicit `target_cap`
parameter so what-if solves cap at their simulated target. Minors: the two
new optimizer arguments became keyword-only and the main solve moved to a
lambda executor call (both are per-step temperature series the same shape
as half the solver's inputs — a positional transposition would have been
silent); promises are anchored to the solve's own timestamp, not "after
the solve"; `from_dict` grew corruption barriers (a tz-naive pending
timestamp would raise on the first aware subtraction and brick every
subsequent score; a NaN sigma reaches the bounds as a NaN margin); exact
between-bucket ties resolve to the longer, more conservative bucket; the
vacuous fixed-point test became a real replay (identical errors → identical
margins, smaller errors → strictly smaller margins); and the curve-comfort
tracker documents that eating into #16's cushion is not a comfort miss.
One finding dispositioned as non-action: the commit-trailer attribution
line is mandated by the development harness and is not repository content,
so it stays. Checks 734 → 744.

**Infrastructure:** lead-time error quantiles. Score realised temperature against
the prediction made k steps ago for buckets {1, 3, 6, 12, 24 h}; per-bucket EWMA
persisted additively; exposed as `accuracy.sigma(lead_hours)`.

**Keys:** `confidence_margins_enabled` `False` (tuning); `mold_guard_enabled`
`False` (comfort); `indoor_humidity_entity` unset (double gate: flag AND entity);
`thermal_bridge_frsi` `0.75`.

**#16:** `T_min_eff[i] = T_min[i] + min(sigma(lead_i) × (1 − trust), 0.8)` —
capped at 0.8 K and trust-damped, applied to `temp_min_bounds` pre-solve.
**#54:** `T_surface = T_out + fRsi·(T_room − T_out)`; invert Magnus against
measured indoor humidity for the lowest room temperature keeping surface RH < 80 %.

**Must not:** leave the margin unbounded or undamped — the loop (bigger margin →
different plan → different errors) oscillates; `features.py` asserts a fixed point
on replayed history. Zero-history ⇒ sigma 0 ⇒ byte-identical plans.

**Verification:** zero-history identity; fixed-point test; mold mutation (20 % RH
must not raise the floor; 60 % at −15 °C must); `confidence_margins` golden; G7.

~5 files, +450/−20. Risk **high per line**, small and isolated.

---

## T6 — Insight (PR 7) · Opus · #29 #52 #55 #65 #39 #40

*Outcome notes:* built as scoped, with the settlement infrastructure exactly
as planned: `get_current_action` now carries the current step's
`space_reason`/`dhw_reason` (one index search owns "which step is running"),
the pending dict captures them at prediction time, and `_accumulate_energy`
books `reason:<code>` ledger lines that PARTITION the metered spot line —
the immersion carve-out comes out of the reason lines too, an untagged
interval (manual modes, restarts, sys-ID overrides) books as
`reason:untagged`, and the receipt publishes `reasons_reconcile` instead of
asserting it. **#40** freezes receipts at rollover, derived from the ledger
itself (any ledger month older than the current one without a receipt gets
one — self-healing across restarts spanning month ends) with the closed
month's contract comparison via a `month` parameter on the T1 settlement.
**#55**: `wear.py` StartCounter — two-sample hysteresis on measured power at
the optimizer's own on/off threshold (half `min_electrical_power`), the
immersion flag freezes the machine AND resets the streak so half-edges
cannot combine across an element event; each confirmed start books
`replacement_cost/rated_starts` on a kWh-0 `wear` line; the autotune
(`_effective_cycling_cost`, gated) floors the cycling penalty with max(),
never replace. **#65**: envelope = the house time constant (mass over
learned-scaled loss, 20 h→0, 100 h→100), machine = 1 − the COP watch's
Cusum fill, operation = a daily replay of settled kWh against the day's
time-mean spot (20 % under = 100), EWMA'd; None means no evidence, never
zero. **#29**: `narrative.py` groups both channels' steps by reason
(arithmetic over the published schedule, untagged included) and renders
`str.format` templates from language-keyed tables — as data in the module,
NOT in the translation triple, because hassfest's strings schema has no room
for free-form sections; the en/sv parity the triple would have given is
enforced by tests (same keys, same placeholders). **#52**: `diagnosis.py`
re-runs the settled interval swapping realised inputs one at a time
(planned set captured in the pending dict at prediction time, realised at
settle); `predicted + contributions + unexplained == actual` by
construction; service + fourth button, result on the Prediction Accuracy
sensor. **#39** (gated): ONE tile per scheduled solve, rotating through the
fixed set (target ±1 °C, 75 % power cap), through `async_simulate` itself —
a rate-limited answer skips the cycle so the card's budget always wins.
Publication: one additive `insight` block in the data dict; three new
sensors (Plan Narrative, Optimization Score, Compressor Starts — README
52→55), receipts on Contract Comparison, diagnosis on Prediction Accuracy,
buttons 3→4. Starts, receipts and the operation score persist as riders on
the ledger store. Goldens: coord_*×5 + config_flow re-recorded, additive
only (+139/−0); the five protected fixtures untouched.

**Infrastructure:** reason-tagged settlement — the `pending` dict carries the
interval's plan-slot reason codes so every settled SEK is attributable; the T1
ledger gains per-reason lines; a month-rollover hook fires #40.

**Keys:** `compressor_replacement_cost` `0.0` (⇒ wear SEK/start 0);
`compressor_rated_starts` `100000`; `wear_autotune_enabled` `False` (the only
plan-affecting piece); `price_tiles_enabled` `False` (three extra rate-limited
solves is real CPU).

**#29** `narrative.py` groups slots by reason and fills templates from the
translation triple. **#52** `diagnosis.py` re-runs the last interval swapping
realised inputs one at a time to attribute the residual (service + button, 3→4).
**#55** builds the **first realised start counter** (edge detection on measured
power with 2-sample hysteresis, ignoring immersion events classified by #11) and
books `starts × cost/rated`. **#65** scores envelope/machine/operation, the
operation term using a daily replay against realised prices. **#39** runs the
fixed perturbation set through `async_simulate_plan` after each scheduled solve,
via the existing rate limiter and executor. **#40** freezes the ledger month and
publishes itemised receipts.

**Must not:** run #39 on demand or outside the executor; count immersion events as
compressor starts; let receipts disagree with accounting — assert the per-reason
lines sum to the lifetime totals' month delta; put narrative text in f-strings
(sv parity).

~10 files, +1100/−30. README 53→56, buttons 3→4. Risk **medium-low** (mostly
read-only publication).

---

## T7 — Hardware (PR 8) · **Fable** · #61 · go/no-go

**Gate:** T2's guard and T4's capacity curve shipped clean, and a real
Modbus/ESPHome number entity validated by the user.

Two stages in one PR. **Observe** (default when the entity is set):
`compressor_freq_entity` unset, `freq_control_mode` `"observe"`; learn a
kW-per-Hz map (envelope pattern, per-decile buckets); publish a recommendation
sensor; **no actuation**. **Control**: write via `number.set_value`, rate-limited
1/5 min, clamped to the entity's min/max, with a watchdog — reported Hz diverging
from commanded for 3 ticks ⇒ fall back to observe + repair issue.

**Must not:** apply the part-load COP factor in observe mode — it would change
plans with no actuation to realise them.

~4 files, +500. Risk **high but fully isolated**; a no-go removes exactly one PR.

---

## T8 — v4.0.0 release (PR 9) · Opus

`VERSION` → 4.0.0, `manifest.json`, `CARD_VERSION`; `RELEASE_NOTES.md` in the
repo's prose style with a per-tranche summary and a **feature-flag table showing
every new key and its inert default**; upgrade note: no store migrations required.
No code. Full suite including `SLOW=1 tests/rolling.py` and `node tests/card.mjs`.

---

## The five most dangerous items

1. **#7 live peak guard** — the only event-driven actuation. De-risked by a pure
   decision function, opt-in flag (listener not registered when off),
   transition-only actuation, floor precedence, hysteresis copied from
   `external_heat.py`, and a hastub extension so the logic tests without HA.
2. **#17 capacity-curve cap** — a learner that can constrain heating exactly when
   it matters. De-risked by max-envelope semantics, a 0.6×nameplate hard floor, a
   ≥5-sample gate, flag-off default, delivery through the proven `power_caps`
   path, and #42 rollback shipping first.
3. **#16 confidence margins** — a feedback loop through the objective. De-risked
   by the 0.8 K cap, trust damping, zero-history byte-identity, an isolated
   tranche, and a fixed-point test.
4. **T1 fee chokepoint** — silent prior contamination or a settlement
   double-count would corrupt *every* SEK figure downstream (#23, #40, #65).
   De-risked by a single chokepoint strictly after `extend_price_series`, spot
   kept separate in accounting, mask-off bit-identity, and a provably fee-free
   `observe_day`.
5. **#61 frequency control** — direct hardware writes. Last, isolated,
   observe-first, watchdogged, explicit go/no-go.

Honourable mention: the 96-bin prior's store compatibility — solved by *additive*
quarter factors rather than reshaping `shapes`, so the silent-fallback loader can
never discard learned state.

---

## Verification contract (every tranche)

1. `./tests/run.sh` green; `SLOW=1 tests/rolling.py` additionally on G7 tranches.
2. Feature-off byte-identity asserted explicitly in `tests/features.py`, not
   merely implied by an empty golden diff (the backlog records that an empty diff
   alone is not evidence a new path is wired up).
3. Golden re-records reviewed leaf by leaf; additive-only unless the tranche
   claims a change.
4. Every guard mutation-tested: an input that must trip it, one that must not.
5. Every SEK claim measured with the `flat_prices` null control.
6. README entity counts, translation triples, and `config_flow.json` updated in
   the same commit as the code.

## Critical files

- `custom_components/heatpump_optimizer/config_flow.py` — `_MENU_LABELS` (:739),
  T0's whole surface, every tranche's field additions
- `.../coordinator.py` — fee chokepoint (`_price_series` :2926,
  `_get_current_price` :3206, `_accumulate_energy` :4298), learner ordering
  (`_update_current_state` :2475), simulate harness (:4550)
- `.../optimizer.py` — `power_caps` (:1418-1532, :1838, :2983), ready-temps and
  legionella (:2080-2135), reason codes
- `.../tariff.py` — masks/seasonality, time-weighted `PeakTracker`, `peak_cost`
- `tests/entities.py`, `tests/golden.py` — the enforcement layer every tranche
  moves in lockstep

---

## Appendix A — the 36 selected proposals, in full

Rank numbers refer to the ideation ranking; savings are the proposers' own
order-of-magnitude claims as judged. Effort: S < 1 week, M 1–3 weeks, L > 3 weeks.

### #1 — Time-of-use and dynamic grid-fee layer in the price vector  ·  300-800 SEK/yr  ·  effort S

Swedish DSOs increasingly price the grid by time, not only peak kW: höglast energy fees (roughly +25 öre/kWh weekday 06-22, Nov-Mar at several DSOs) and, soon, per-hour dynamic fees. A configurable grid-fee schedule — static ToU rules or a live HA entity — is summed into the hourly price vector and accounted separately, moving load to nights and weekends in winter even when spot alone would not.

*Mechanism:* A grid_fee module beside tariff.py yields an SEK/kWh vector across the horizon from ToU rules or an entity trajectory; inputs.py adds it to the effective price before the solve; savings accounting books the fee as its own line.

### #2 — Heat-curve auto-flattening from closed-loop comfort evidence  ·  600-1500 SEK/yr  ·  effort M

The supply temperature curve is almost always commissioned with safety margin, and every degree of excess flow temperature costs COP all winter. Learn the lowest curve that still meets the comfort band: if rooms consistently attain target with margin while return temp is high, bias the curve down a step; back off on any comfort miss. Applied automatically on the ECL110 path, published as a numbered recommendation for everyone else.

*Mechanism:* New curve_learning.py module following comfort_learning.py's pattern: consumes accuracy.py residuals plus comfort-band attainment, maintains a persistent displace bias with asymmetric steps (down slowly, up instantly on a miss), clamped and exposed as a sensor. The bias is added to the existing displace command; no new solve needed.

### #3 — Fuse-size right-sizing advisor with an opt-in fuse guard  ·  1500-3000 (0 if infeasible) SEK/yr  ·  effort M

The fixed grid fee steps with main fuse size; 20A to 16A is typically worth 1500-3000 SEK/yr. The integration already tracks the whole-house peak and can re-solve under a cap, so it can answer the question no one else can: would this house, with the optimizer actively flattening peaks, run a whole winter under 11 kW - and at what comfort and energy cost? If yes, an opt-in soft cap holds the line.

*Mechanism:* A monthly shadow solve with peak power hard-capped at the smaller fuse's kW, reusing the tighten-and-re-solve loop built for `buffer_max_temp`; publish feasibility, worst-case margin and the SEK delta as attributes on the Monthly Peak sensor. The opt-in guard adds the cap as a steep soft penalty in the live objective.

### #5 — Power headroom broadcast for dynamic charger limits  ·  500-1500 SEK/yr  ·  effort S

Publish a number entity stating how many kW the house can draw right now — and per step over the horizon, in attributes — without raising the capacity bill or approaching the main fuse. Easee, Zaptec and Wallbox integrations accept a dynamic circuit limit, so a two-line automation feeds it straight to the charger. The heat pump keeps its planned slots; everything else gets what is genuinely left over.

*Mechanism:* headroom[t] = min(fuse_kw, PeakTracker.threshold_kw) minus planned HP power minus forecast baseline load, recomputed each optimization from data already assembled in _grid_report, and clamped between runs on live house-meter readings. One sensor plus one number entity; no solver changes.

### #6 — VVC recirculation pump scheduling from the learned draw profile  ·  500-1500 SEK/yr  ·  effort S

Houses with a VVC loop run its pump around the clock, and the loop is often the tank's single biggest standby loss, 500-2000 kWh/year. The integration already learns exactly when hot water is drawn; feed that schedule to the VVC pump so the loop runs only around real demand windows plus a short lead time. The DHW planner then also stops paying to refill losses that no longer happen.

*Mechanism:* Optional VVC switch entity. The learned hourly draw profile and configured demand frames (both already in dhw_schedule.py) generate an on/off schedule with a configurable lead; coordinator publishes it. The tank cooling-rate learner will observe the improvement automatically, shrinking planned DHW energy.

### #7 — Real-time peak guard inside the live metering window  ·  300-800 SEK/yr  ·  effort M

Planning avoids forecast peaks, but an unforecast coincidence — oven, sauna, surprise EV plug-in — can set a new monthly peak in one hour the plan never saw. PeakTracker already accumulates the current metering window's running sum. When the window's projected mean crosses the billed threshold, defer DHW heating (the tank rides through for free) and nudge the ECL110 displace down for the remainder of the window, then release.

*Mechanism:* On each house-meter update, project window mean = accumulated sum plus current draw times remaining minutes. If projection exceeds threshold_kw minus a margin, suppress the DHW block through the existing external-heat suppression path and lower the displace command; release at window close. Comfort and tank floors still override, as with manual pins.

### #9 — Storage-temperature advisor: the scald margin priced  ·  200-600 SEK/yr  ·  effort M

Many tanks store at 60°C while the thermostatic mixing valve delivers 40°C — the scald margin is pure standby loss plus COP penalty. Compute, from the learned draw distribution, cooling rate and `dhw_hold_hours()`, the lowest storage setpoint that still covers p95 window demand between planned reheats (legionella cycles retained for hygiene), and publish it with the SEK/year the current gap costs — the Valve Target Recommendation pattern applied to DHW.

*Mechanism:* A diagnostic sweep: for candidate setpoints 48-60°C, replay the existing DHW energy balance over the learned week; report the lowest candidate that never misses a window, and annualize the delta via the COP model and standby-loss term. Read-only sensor first, like the buffer valve recommendation.

### #11 — Immersion-heater event detection charged back to the plan  ·  100-600 SEK/yr  ·  effort S

When the plan coasts too deep, the pump's backup resistance heater silently finishes the job at COP 1 — the most expensive kWh in the system, and today it just looks like consumption. Detect immersion events from measured power exceeding compressor max while heating, price the COP-1 premium, and feed events back as evidence that recovery margins are too thin, widening the DHW ready-margin or comfort recovery lead the way comfort_learning.py consumes overrides.

*Mechanism:* Threshold detector on the measured-power input (draw > configured hp_max_power + tolerance) in the coordinator's measurement pass; a ledger of events with the SEK premium vs. planned COP. A slow nudge on the DHW pre-heat margin per confirmed event, clamped and persisted like other learned parameters.

### #12 — COP drift alarm: refrigerant-leak and fouling detection  ·  0 most years; 1,000-3,000 when it fires SEK/yr  ·  effort S

Observed COP already exists but nobody watches its slow trend. Normalize each measured COP sample by outdoor-temperature bucket and the learned defrost derate, then run a weeks-scale CUSUM: a sustained drop not explained by weather flags degradation — refrigerant loss, fouled filter, failing fan. Raise an HA repair issue stating the drift, the estimated extra SEK/month it is costing, and that a service visit is likely cheaper than the drift.

*Mechanism:* _learn_measured_cop already produces per-bucket samples; add a per-bucket long baseline plus a CUSUM statistic persisted like other learning state. Alert via issue_registry with the cost delta computed from recent consumption times (baseline COP / current COP - 1).

### #13 — Windowed and seasonal effekttariff structures  ·  200-700 SEK/yr  ·  effort M

The capacity model bills every hour of the month equally, but most Swedish DSO effect tariffs do not: many count only weekday daytime peaks (e.g. 07-19), bill night peaks at half rate, or apply a higher November-March rate. Under the flat model the optimizer avoids night-time stacking that is actually free - surrendering exactly the cheap-hour concentration this integration exists to find.

*Mechanism:* Extend `CapacityTariff` with hour/weekday/month masks and an off-peak rate factor; `PeakState.add_sample` and the optimizer's `capacity()` cost term apply the mask per step so unmasked hours contribute nothing. Config page gains the fields plus presets for common DSO structures.

### #16 — Confidence-aware comfort margins  ·  200-700 SEK/yr  ·  effort M

The planner treats its predicted trajectory as exact, so users defend themselves with a high minimum temperature. Publish a per-step prediction band grown from realized error, and hold the comfort floor against the band's lower edge instead of the mean. A young or drifting model keeps margin automatically; a converged one coasts closer to the true limit — which is where the deep savings live. The card shades the band so the margin is visible.

*Mechanism:* Extend accuracy.py from horizon-wide MAE/bias to error quantiles per lead-time bucket. optimizer.py adds sigma(lead_k) to T_min per step, using the same tighten-and-re-solve pattern as buffer_max_temp and pin safety. Margin shrinks as the tracker's trust score rises.

### #17 — Cold-weather capacity curve learning  ·  100-400 SEK/yr  ·  effort M

hp_max_power is one configured constant, but an air-source unit's deliverable thermal output falls steeply below -5 C — exactly when the plan matters most. A plan built on phantom capacity fails, and the shortfall is bought back at peak prices or as a fresh capacity-tariff peak. Learn maximum delivered thermal power per outdoor-temperature bucket from intervals where the pump ran flat out, and cap the solver's per-step power with it.

*Mechanism:* With the power meter, delivered thermal = P_el x observed COP; keep the upper envelope per 3 C outdoor bucket — the mirror image of the tank learners' lower envelope, same clamp-and-persist pattern. optimizer.py's capacity bound becomes temperature-dependent through the horizon's outdoor trajectory; defrost derate already composes.

### #18 — Weekday/weekend draw profiles  ·  100-300 SEK/yr  ·  effort M

The learned draw pattern is a single 24-bucket profile, so weekday 06:30 showers and weekend 09:30 showers average into both: the tank is hot at 06:00 Saturday for nobody and lukewarm when the household actually wakes. Learn separate weekday and weekend profiles, shrunk toward the pooled profile while day-type samples are few, so preparation follows the household's real week.

*Mechanism:* Split the coordinator's `_dhw_hourly_profile` Store into two profiles keyed by `weekday() < 5`, blended with the pooled profile by sample count. `dhw_draw_rates()` currently indexes hour-of-day only; the optimizer already carries per-step timestamps, so pass day-type through and index the matching profile per step.

### #19 — Quarter-hour price prior (96 bins) for the 15-minute MTU  ·  100-300 SEK/yr  ·  effort S

Since October 2025 the day-ahead auction clears in 15-minute periods and Tibber delivers quarter prices; the coordinator aligns them correctly, but the learned prior is a 24-bin hourly shape. The unpublished tail therefore smears intra-hour ramp structure - the 06:00 and 06:45 quarters can differ 50-100 ore - exactly where pre-13:00 deferral decisions are made.

*Mechanism:* Extend `price_model.py` from 24 to 96 bins with shrinkage toward the hourly mean until quarter-level evidence accumulates, keeping the weekday/weekend split, damping and per-step confidence flags. `extend_price_series` and the card shading need no interface change; the step grid is already 15-minute.

### #20 — Draw-event library with quantile ready targets  ·  150-400 SEK/yr  ·  effort M

Draws are modelled as smeared average power, so every window's ready temperature covers a mean that no real morning resembles. Detect discrete draw events from tank-temperature drops, keep a per-window distribution of event energies, and set each window's ready temperature to cover the p90 draw — usually lower than today's setpoint hold, occasionally higher before the recurring Sunday triple-shower.

*Mechanism:* In the coordinator's existing DHW temperature sampler, flag dT/dt exceeding the learned cooling rate as a draw event and accumulate (window, energy) pairs into the profile Store. In the DHW planner, replace the mean `draw_energy` sum feeding `ready_temps` with cold-start plus p90 window energy over `c_dhw`.

### #21 — Defrost avoidance windows via forecast humidity  ·  100-350 SEK/yr  ·  effort S

The defrost derate is learned but applied at a single current humidity, so the plan cannot steer around tomorrow's frosting hours. Fetch the relative-humidity forecast, evaluate the learned derate per step along the horizon, and let per-step COP carry it: DHW charging and slab pre-heat then migrate on their own to hours outside the 0-5 °C humid band, where each purchased kWh delivers more heat. Moved slots carry a new frost-avoidance reason code.

*Mechanism:* relative_humidity_2m joins the Open-Meteo fetch; _forecast_arrays() adds a humidity trajectory; thermal_params takes that array instead of one scalar so DefrostDerate.factor() is evaluated per step in both optimizer paths, including the DHW LP's COP column; add REASON_FROST_AVOID.

### #22 — Post-outage staggered recovery that protects the monthly peak  ·  50-400 SEK/yr  ·  effort S

After a power cut everything restarts at once: cold house, cold tanks, compressor plus immersion — precisely the hour a new monthly capacity-tariff peak is set, alongside the whole neighbourhood. Detect the outage (coordinator update gap plus HA restart), enter a recovery mode that treats re-warming as a deadline problem with the capacity charge weighted at full price, and stagger DHW after space heating instead of stacking them.

*Mechanism:* Persist a last-update timestamp; a gap beyond threshold at startup triggers recovery. Reuse away.py's deadline recovery for the house and the DHW planning order, with tariff.py's peak term forced active (no free-headroom assumption post-outage). A recovery flag on the binary sensors.

### #23 — Contract-type shadow settlement (spot vs manadsspot vs fixed)  ·  0 insight; 500-2000 via a switch SEK/yr  ·  effort S

Each month, settle the actually-metered consumption against the contract types on the Swedish market: hourly spot (what Tibber bills), monthly-average spot, and a configured fixed price. Publishes the load-profile value - how many ore/kWh below the flat-consumer average the optimizer's shifting earns - and which contract would have been cheapest. A household on manadsspot gains nothing from hourly shifting; this sensor is the proof, either way.

*Mechanism:* The coordinator already samples hourly energy and price for the cost accumulators; add parallel accumulators per contract model plus a volume-weighted monthly average price, and one new sensor with per-month attributes. No solver changes.

### #24 — Free-heat disinfection credit  ·  100-300 SEK/yr  ·  effort S

The wood furnace — or a PV-rich afternoon — can push the DHW tank past 60°C on its own, yet the legionella clock ignores it and the optimizer later pays for a redundant electric cycle. Track time-above-temperature continuously and, once the tank has held disinfection temperature long enough by any means, reset the interval for free.

*Mechanism:* The coordinator already samples DHW temperature every cycle and external_heat.py already flags furnace charging. Integrate minutes above `dhw_legionella_temp`; on reaching the configured hold duration, write the timestamp to `_dhw_legionella_store` exactly as a completed planned cycle does, resetting `dhw_hours_since_legionella`.

### #26 — Open-window detection from thermal residuals  ·  100-400 SEK/yr  ·  effort S

An open window makes the room fall far faster than the model predicts. Detect it as a step change in the one-step prediction residual the heat-loss learner already computes: freeze learning (the costly victim), stop the plan chasing the loss in that zone, and raise a binary sensor. Clears when the residual returns to band. No contact sensors required; where they exist they confirm detections and calibrate the threshold.

*Mechanism:* A CUSUM change-point detector on the per-interval residual from the house heat-loss replay in coordinator.py. A trip sets a ventilation flag consumed by the existing watchdog freeze path and a temporary comfort-penalty relaxation for that zone in optimizer.py; surfaced via the Input Problem sensor pattern.

### #28 — Cold-shower risk and deliverable-liters sensor  ·  0 (insight only) SEK/yr  ·  effort S

Publish hot water in the unit households reason in: liters of 40°C mixed water and minutes of shower available right now, plus a run-out risk for the next demand window given the current plan. No direct savings — but it is the trust instrument that lets users accept the lower setpoints and tighter targets where the money in the quantile and advisor features actually comes from, and it flags a failing plan before the cold shower does.

*Mechanism:* Each coordinator cycle: mixed liters ≈ tank volume × (T_tank − T_inlet)/(40 − T_inlet); minutes at a configured shower flow. Risk compares the planned tank trajectory's margin against the p90 draw of the next window. Two sensors plus a card readout.

### #29 — Plain-language plan narrative  ·  0 (insight only) SEK/yr  ·  effort S

Three to five generated sentences above the card's chart describing today's plan as a story: 'Heating banks 6 kWh into the slab between 02:00 and 05:00 because 07:00-09:00 costs 3.10 kr/kWh; hot water waits for the 13:00 solar surplus; the tank gets its legionella cycle at 03:00 Sunday, the cheapest hour before the deadline.' Deterministic templating, translated via the existing en/sv files.

*Mechanism:* Reason codes plus slot energies and price deltas already exist on the plan sensors. A small narrative module groups consecutive slots by code, ranks the three most expensive-to-explain decisions, fills sentence templates from strings.json, and publishes the text as a plan-sensor attribute the card renders.

### #30 — Precipitation-type envelope loss  ·  50-200 SEK/yr  ·  effort S

The rain multiplier raises envelope loss 15% for any precipitation, but Swedish winter precipitation is mostly snow: dry snow at -10 °C does not wet a wall, so the plan pre-heats against a phantom loss all winter. Split forecast precipitation by type using Open-Meteo's snowfall variable: full multiplier for liquid, a temperature-blended fraction for wet snow near 0 °C, none for dry snow. An optional roof snow-depth insulation factor, off by default.

*Mechanism:* _forecast_arrays() carries rain and snowfall as separate arrays; thermal_model's U_effective applies the rain multiplier weighted by liquid fraction (blend over roughly -1 to +2 °C); an optional snow_depth-driven roof factor caps at a few percent. No new config required for the correction itself.

### #32 — Effective inlet temperature: seasonal mains and greywater recovery  ·  50-200 SEK/yr  ·  effort S

`dhw_draw_power` assumes a 10°C cold feed year-round, but Swedish mains swing roughly 4°C in February to 16°C in August, and a drain-water heat-recovery unit lifts the effective inlet another 10-15°C during showers. Model the inlet as a yearly sinusoid (optional sensor override) with a configured recovery effectiveness on high-flow draws, so draw energy — and every ready target built on it — tracks the season.

*Mechanism:* Replace the fixed `delta_t = setpoint - 10` in thermal_model.py with a day-of-year sinusoid (config amplitude/phase, or a real inlet sensor); an optional GHX effectiveness factor scales draw energy for shower-class events. Both feed `dhw_draw_power` and the window energy sums.

### #34 — Risk-adjusted pricing on the unpublished horizon  ·  100-300 SEK/yr  ·  effort M

The prior fills unknown steps with its mean, so the optimizer treats a guessed trough as bankable and defers real heating into it. The error is asymmetric: a trough that fails to appear forces buying at a peak, while charging slightly early costs only standby loss. Track the prior's dispersion and make deferral into guessed steps pay a risk premium; buying now against known prices stays at face value.

*Mechanism:* `price_model.py` already keeps an EWMA shape; add an EWMA of squared residuals per bin and return a sigma vector from `extend_price_series`. The optimizer prices energy in prior-only steps (the existing `price_known` mask) at mean plus lambda-sigma, with lambda a tuning constant defaulting small.

### #36 — Effective solar aperture learning  ·  200-600 SEK/yr  ·  effort M

Window area, orientation factor and SHGC are three guessed numbers that only ever act as one product. Learn that product — the effective solar aperture — by regressing sunny-step residual warming against measured irradiance, per zone, bucketed monthly so sun angle and seasonal shading fold in. A wrong aperture makes the optimizer skip preheating for sun that never reaches the rooms, or preheat before sun that would have done the job free.

*Mechanism:* On steps with irradiance above a floor and learners unfrozen, the residual left after the heat-loss replay is regressed against the model's Q_solar driver; a damped scale on the configured aperture per month bucket, clamped and persisted like house_heat_loss_scale. Identifiability guard: update only when within-day irradiance variance is high.

### #39 — Price-of-a-degree tiles: live marginal cost of every comfort knob  ·  300-1000 SEK/yr  ·  effort M

Small always-current tiles on the card: 'one degree warmer: 2.30 kr/day right now', 'evening hot water one hour earlier: 0.90 kr/day', 'dropping the night minimum 1 °C: -1.60 kr/day'. The what-if simulator exists but demands the user compose a scenario; these are pre-computed answers to the three questions everyone actually has, refreshed each solve.

*Mechanism:* After each scheduled solve, run the existing rate-limited simulate_plan path against a fixed set of unit perturbations (±1 °C target, ±1 h DHW window, -1 °C minimum), cache the cost deltas, and publish them as attributes on a new sensor the card renders as tiles.

### #40 — Monthly Optimizer Report: itemized SEK receipts per lever  ·  0 (insight only) SEK/yr  ·  effort M

A month-end report answering 'what did this thing actually do for me': total realized saving vs the thermostat baseline, decomposed into load shifting, DHW windowing, capacity-peak avoidance, PV self-use, external-heat displacement and away mode — each with its top three itemized 'receipts' ('pre-heating 02:00-05:00 on 12 Jan saved 6.40 SEK'). Published as a sensor, rendered as a report page in the card, delivered via persistent notification.

*Mechanism:* The settlement accounting already prices each interval against the baseline; tag every settled interval with its plan slot's reason code, accumulate per-code SEK in a monthly ledger persisted like the learners, and add a card page that renders the ledger. A coordinator month-rollover event fires the notification.

### #42 — Learned-parameter snapshots with drift rollback  ·  0-500 (insurance) SEK/yr  ·  effort M

Learned parameters persist but have no history: a corrupted estimate survives restarts and the only way back is manual reset. Keep weekly snapshots of every learned parameter tagged with the prediction accuracy achieved under them. When signed bias stays out of band for N days, raise an HA repair issue naming the drifted parameter and offer one-click rollback to the best-scoring snapshot; auto-rollback only when the watchdog confirms sensors were healthy throughout.

*Mechanism:* Serialize the learners' existing as_dict() payloads (tank rates, heat-loss scale, defrost, comfort weight) into a ring buffer in coordinator storage, keyed weekly and tagged with accuracy.summary(). Drift test: temperature_bias beyond threshold N consecutive days. Rollback: from_dict() restore plus forced re-solve.

### #47 — Elastic multi-day disinfection placement  ·  50-150 SEK/yr  ·  effort S

Today the cycle is placed at the cheapest step only once its deadline enters the 24-48h horizon, so it always lands in the interval's last two days regardless of prices. Treat the interval as elastic (e.g. 5-9 days) and, each run, compare today's known cheapest DHW-priced step against the learned price prior's expectation for the remaining days — firing early when a windy negative-price day beats the expected future.

*Mechanism:* An option-value test in the legionella block of optimizer.py: schedule when `min(dhw_prices)` now is at or below price_model.py's daily-shape expectation of the cheapest step in the days remaining to the hard deadline, which still forces placement as today.

### #52 — Why-is-it-cold button: instant deviation diagnosis  ·  0 (insight only) SEK/yr  ·  effort M

One button for the most common support moment. It compares the room against the plan's predicted trajectory and returns a ranked plain-language cause: 'The room is 0.9 °C under plan: wind is 6 m/s above forecast (0.6 °C) and the 13:00 slot was skipped by your manual pin (0.3 °C). Recovery is planned 14:00 at 0.31 kr/kWh.' Also answers 'why is it heating now when prices are high'.

*Mechanism:* accuracy.py holds predicted-vs-realized state; re-run the last interval through the thermal model swapping realized inputs one at a time (wind, sun, price, override, learner freeze) to attribute the residual. Expose as a service returning text, a card button, and a state attribute.

### #53 — Diurnal internal-gains profile learning  ·  150-400 SEK/yr  ·  effort M

Cooking, appliances and people inject a predictable few hundred watts on a daily rhythm; today internal gains are a flat configured term, so the heat-loss learner absorbs the rhythm as biased noise and the plan buys heat just before the evening's free gains arrive. Fit an hourly internal-gain vector, weekday/weekend split, from the time-of-day structure of prediction residuals, and feed it into the trajectory exactly like solar gain.

*Mechanism:* Gated on house_heat_loss_scale having converged (sample count), regress per-hour residual warming with ridge regularization toward the configured constant, damped like the price prior. 48 values persisted in coordinator storage; thermal_model.py adds them to each zone's gain term using the existing zone split.

### #54 — Dew-point mold guardrail for cold corners  ·  0-300 (mainly risk avoidance) SEK/yr  ·  effort M

How deep a setback is safe is a moisture question the optimizer cannot currently ask. With an indoor humidity sensor, compute the coldest interior surface temperature from a thermal-bridge factor (fRsi, preset-derived by building era) and raise the comfort floor whenever a planned setback would push corner surface RH past the ~80 % mold-growth criterion. On dry winter days the same arithmetic certifies deeper economy dips as safe rather than reckless.

*Mechanism:* Per step: T_surface = T_out,forecast + fRsi·(T_room − T_out,forecast); invert the Magnus formula with measured indoor absolute humidity for the lowest room temperature keeping surface RH under 80 %; apply it as a floor on comfort_band before the solve. fRsi defaults come from presets.py building eras; a reason code marks slots the guardrail held up.

### #55 — Compressor wear ledger settled into the savings accounting  ·  200-800 amortized SEK/yr  ·  effort M

The plan's start count is published, but nobody prices what actually happened. Detect real compressor starts from the measured power sensor (including thermostat-driven starts between plan updates), amortize each against a configured replacement cost and rated start lifetime, and settle the resulting SEK/day into the savings accounting next to energy. If measured wear cost exceeds what aggressive cycling saved, suggest (or opt-in auto-set) a non-zero cycling weight from evidence.

*Mechanism:* Edge-detect starts on the measured-power series in the coordinator (count_compressor_starts exists for planned power). A wear ledger module: SEK/start = replacement_cost / rated_starts. Feed the calibrated value into the existing cycling_penalty weight via the same options path set_thermal_parameters uses.

### #61 — Compressor frequency setpoint control with learned modulation map  ·  400-1000 SEK/yr  ·  effort L

Replace the implicit on/off-plus-curve actuation with direct compressor frequency commands for pumps that expose a Hz or capacity register (Nibe, Thermia, Panasonic via Modbus/ESPHome number entities). The MPC already plans continuous kW per 15-min step; today that resolution is thrown away at the actuator. Commanding frequency delivers the planned power exactly, exploits the part-load COP sweet spot, and cuts starts to near zero.

*Mechanism:* New optional number entity in config_flow. A learner in coordinator.py fits kW-per-Hz from the existing measured-power sensor (same envelope pattern as COP learning). thermal_model.py gains a part-load COP factor; coordinator inverts planned kW through the map and writes the frequency each step, alongside the ECL110 publish.

### #65 — Energy-label operation score (A-G) with sub-grades  ·  0-500 SEK/yr  ·  effort M

A monthly A-G grade in the energy-label visual style, split into three sub-scores: envelope (learned heat-loss per m² vs the building-preset archetypes), machine (observed COP vs nameplate), and operation (share of the available price spread the plan actually captured). Each sub-grade links to the one setting or action that would raise it.

*Mechanism:* presets.py provides archetype heat-loss baselines to normalize the learned coefficient; observed COP and nameplate exist; 'spread capture' = (baseline cost - settled cost) / (baseline cost - hindsight LP bound). One sensor with sub-scores as attributes, one card tile.


*User addition to #6: the same schedule-following control for a Home-Assistant-controlled space-heating circulation pump, with the safety rails specified in T3.*
