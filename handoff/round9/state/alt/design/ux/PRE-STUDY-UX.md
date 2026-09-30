# Pre-study: lane UX (explanations, advisor inbox, receipts and notifications, health)

Requested by tvofi on 2026-09-30: "Do a small pre-study for items 1-4 and find optimal places for them in the ongoing
plan. Defer 5 for later, add it as a feature request issue." Measured at origin/main `5dfa6684` (after #1788, F1.7)
against the live roster on `handoff/audit-r9-fixplan` at `1c3558f0` (rev 4 applied, lane UI with feature issue #1791).
`cc/` is `custom_components/heatpump_optimizer/`; `card` is `cc/www/heatpump-optimizer-card.js`. Line numbers are at
`5dfa6684`; re-derive them at your own merge base.

The ideation behind the four items is in this folder's `DESIGN-UX.md`. Its evidence came from three read-only surveys:
- what the integration offers and computes;
- comparable products, where most vendor pages were blocked by the network, so those findings rest on search snippets
  and GitHub READMEs;
- the request history.

## Decisions (tvofi, 2026-09-30)

| # | question | answer |
|---|---|---|
| U1 | how notifications reach the user | the integration fires documented events and ships a blueprint where the user picks the notify target and the events; no new option fields |
| U2 | how far the trust replay goes | the full day-ahead replay: a daily snapshot of the plan's promise, compared with what happened |
| U3 | item 5, the shared household power budget | deferred beyond round 9, filed as a feature request |
| U4 | budgets | "The budgets are in place to make sound architectural decisions, they can be raised as a last resort if payment does not yield better code, after codeowner approval." |
| U5 | documentation | "Make sure that the finished card pages gets described with screenshots in the documentation." |

## Item 1: why now, why not, and the trust replay

**What exists:**
- Every space step carries a reason. `classify_space_steps` (`cc/optimizer.py:943`) is a ranked reading of the solved
  plan. Its "cheap" test is the horizon's 35th price percentile, which is not published.
- The reason codes are `comfort_floor`, `cheap_price`, `preheat_weather`, `scheduled`, `terminal_value`,
  `solar_surplus`, `dhw_window`, `dhw_ready`, `dhw_preheat`, `legionella`, `idle`, `manual_plan` and `pump_mode`
  (`_mark_blocked_reasons`, `cc/optimizer.py:1107`).
- DHW steps are classified only on the DHW path. Elsewhere their reason is `None`.
- The plan sensors' `forecast` attribute carries per step:
  - space: `t`, `price`, `price_known`, `outdoor`, `space_power`, `room`, `upper`, `lower`, `reason`, `pv_surplus`;
  - DHW: `t`, `price`, `price_known`, `outdoor`, `dhw_power`, `dhw_temp`, `dhw_temp_lo`, `dhw_temp_hi`, `reason`;
  - built in `_build_plan_views` (`cc/coordinator.py:3641`).
- The card hides idle steps on purpose (`reasonHtml`, card :6675: an idle or empty reason is skipped unless the pump
  mode blocks the channel).
- The narrative sensor (`PlanNarrativeSensor`, `cc/sensor.py:2501`) publishes every line in English or Swedish from
  `_narrative_view` (`cc/coordinator.py:10381`). The card shows the first line only.

**What an idle explanation needs:**
- Available per step: price rank (the card can rank the horizon itself), the tank temperature against the published
  `dhw_min_temperature`, `pv_surplus`, the other channel's power, the previous and next heating runs.
- Not published: the per-step room floor (the card knows only the day/night comfort settings, which are wrong during
  away setback), the fuse cap, the heat-loss factor.
- So the card can say "likely because" from the first list, and exact sub-codes belong in the backend classifiers and
  `narrative.TEMPLATES`.

**Replay:**
- Measured indoor, outdoor, price and action history is on the recorder, and the card reads 48 h of it
  (`HISTORY_SPAN_MS`, card :1498).
- `cc/accuracy.py` keeps `HISTORY_LENGTH` 672 one-interval-ahead samples, persists the last 192, and publishes
  aggregates only.
- The plan forecasts are unrecorded.
- The day-ahead replay (U2) therefore needs a new daily snapshot of the plan's 24-hour room trajectory and cost, about
  2–3 KB a day. It is persisted beside the accuracy history and published unrecorded.
- The next-interval prediction becomes a recorded sensor, so the recorder builds that history for free.

## Item 2: advisor inbox

The card's Advisor tab (`advisorPageHtml`, card :7109) reads only the sensor ranking.

| advisor | class | default | what it says | apply path today |
|---|---|---|---|---|
| sensor gap | `SensorGapAdvisorSensor` (`cc/sensor.py:2794`) | on | money per month for the top unfilled sensor slot, with a list | `assign_entity` |
| valve target | `ValveTargetRecommendationSensor` (:2167) | dynamic | °C | `assign_entity` with a manual setpoint |
| hot-water setpoint | `DHWSetpointAdvisorSensor` (:2337) | on with DHW | cheapest setpoint that covers the heaviest window, with candidates | **none that persists**: `set_thermal_parameters` is lost on reload, and `apply_schedule` (`services.yaml:408`) has no setpoint field |
| wood burn | `WoodBurnAdvisorSensor` (:2849) | off | light or skip tonight; its text is English-only | advisory |
| frequency | `FrequencyAdvisorSensor` (:2656) | off | recommended Hz | advisory |
| fuse | attribute on the monthly-peak sensor | off | candidate fuse and its cost delta | advisory |
| price of a degree | attribute on the score sensor, opt-in | off | monthly cost of ±1 °C and of a 75 % power cap | no persistent target service |

**Card rules:**
- New reads of separate sensors join `_signature` (card :11297), not `HEADLINE_SUFFIXES` (card :1414).
- `tests/entities.py` refuses card reads of sensors that are disabled by default. So an opt-in advisor appears as an
  "enable to see" row, never as a read.

## Item 3: receipts and notifications

**Receipts:**
- They are frozen monthly by `_freeze_month_report` (`cc/coordinator.py:10187`, called from `_roll_month` :10148) and
  persisted for `KEEP_MONTHS` 24.
- Only the latest is published, as `monthly_report` on `ContractComparisonSensor` (:2232), which is **disabled by
  default**. The Savings tab reads `savings_months` from `MonthlySavingsSensor` (:450), which is enabled.
- 24 receipts come to about 30 KB, over Home Assistant's 16 KB attribute limit, so they must be published unrecorded or
  trimmed.

**Defect found (fixed by UX-6, failing test first):**
- The receipt's `total_sek` is the sum of every line's cost minus the reason lines. The lines include `spot` and also
  `space` and `dhw`, which split the same energy (`cc/coordinator.py:9965`), plus `savings_baseline` and
  `savings_actual` (`cc/ledger.py:171`, :175). So one month's cost is counted up to four times.
- `total_sek` was written before those lines existed (`2e0d3d96`, then `aa2677ba` and `bf08217d` added them), and no
  test covers it.
- It surfaces only in the disabled sensor's attribute today, and it would surface in the receipt view.

**Ledger coverage:**
- Booked: spot, the grid energy fee, immersion and wear.
- Not booked: the capacity charge, because the peak tracker wipes the month's peaks at month change. A report that
  names the capacity charge needs it booked first.

**Notifications:**
- There is no `async_fire`, `persistent_notification` or notify call anywhere in `cc/`.
- A notifier module can subscribe with `coordinator.async_add_listener` next to `entry.runtime_data = coordinator`
  (`cc/__init__.py:316`) and diff `coordinator.data`. That needs no coordinator lines.
- Every signal exists:
  - the receipt month in the insight view (`_insight_view`, :10533);
  - the released pins from `_record_manual_release` (:7861);
  - `stale_inputs` and `problem_messages`;
  - `plan_stale` and `plan_age_minutes`;
  - the plan's minimum room temperature against the configured minimum.
- Per U1, events plus a blueprint, so no option field and no options-flow change.

## Item 4: health and onboarding

**What exists:**
- Input Problem publishes `problems`, `problem_messages`, input ages and the learner freeze.
- Evidence-waiting sensors go unavailable, which hides their `waiting_for`.
- `_learning_view` (`cc/coordinator.py:7246`) holds about 12 learned-model keys that no entity or card reads: heat-loss
  scale and samples, lower-floor loss, solar aperture, internal gains, capacity envelope, COP health, heat curve,
  snapshots, system identification.
- The diagnostics download (`cc/diagnostics.py:123`) redacts `TO_REDACT` (the token and the name) and coarsens the
  location. A richer bundle must also redact the `person.*` and `calendar.*` ids held in the options.

**Already done, and the record is stale:**
- Options back navigation: #123, `4daf8c51`.
- The wizard's "no tank" answer: `3110b24d`, `ed2318e6`.
- The heat-loss re-anchor: #110, `cca2b115`.

`docs/backlog.md` still lists two of them as open, and a coordinator comment in `_learning_view` still describes the
fixed heat-loss defect.

## Budgets (U4)

- Every metric in `tests/structure_budgets.json` sits at zero headroom. `coordinator_loc`, `coordinator_methods` and
  `coordinator_attrs` bind the coordinator. `sensor.py`, `diagnostics.py`, `__init__.py` and new modules meet only the
  global shape metrics.
- No metric measures the card.
- The architecture score (EG-A4) reads Python and the translation JSONs, so new modules, entities and payload keys
  count.
- Design order:
  1. New logic goes where it belongs: a notifier module, pure functions in `ledger.py` and `accuracy.py`, sensors that
     read published data.
  2. Pay for lines only where the payment is itself the better design. For example, the receipt freeze moves out of
     the coordinator into `ledger.py` as a pure, tested function. That is its sound home, and it also pays for the new
     call sites.
  3. A raise is a last resort. The PR body shows why paying would not give better code, and tvofi confirms the raise
     as code owner before the push. It merges on tvofi's approving review. The programme mandate does not pre-confirm
     raises for this lane.

## Documentation with screenshots (U5)

- Every card page this programme finishes is described in `docs/dashboard-card.md` with screenshots: Plan, Setup,
  Savings, Advisor and Health.
- The screenshots are generated from the real card on the repository fixture, never hand-captured, so they stay true
  to the code (D6). Today's browser test already has a hero mode that renders the README image.
- R9-UI-3 generalises it into a page-screenshot mode that writes one image per page and theme into `docs/img/card/`.
  That is the reorganisation's final folder: `tests/layout.json` already admits it, and R9-RO-3 moves the older images
  there.
- Each later card group regenerates the images of the page it changes and updates that page's section in the same PR.
  The Health tab is new in UX-3 and gets its own section there.

## Placement

The depths count open groups only, at `1c3558f0` (47 open), and `alt/build_roster_rev41.py` asserts them.

| group | after | depth | gates | why here |
|---|---|---|---|---|
| UX-1 why now, why not (card) | UI-4 | UI-4 + 1 | RO-2 | the card is one file: after the lane-UI chart it explains |
| UX-2 advisor inbox (card) | UX-1 | + 2 | RO-2 | serial on the card |
| UX-3 health view (card) | UX-2 | + 3 | RO-2 | serial on the card |
| UX-4 events and blueprint (backend) | EG-B3 | EG-B3 + 1 | RO-2 | reads the typed payload contract EG-B3 lands, not bare keys |
| UX-5 advisor actions and idle sub-codes | EG-B6, SW-1, EG-B5, EG-B1, UX-3 | after the last owners of `services.py` and `optimizer.py` | RO-9 | `apply_schedule` and the classifiers |
| UX-6 money and memory | EG-B7, EG-B11, UX-5 | after the last owners of `coordinator.py` and `sensor.py` | RO-9 | receipts, capacity line, day-ahead snapshot |
| UX-7 model status and diagnostics | EG-B6, EG-B11, UX-5 | same depth as UX-6, no edge between them | RO-9 | the diagnostics bundle after EG-B6; new sensors after EG-B11 |

UX-6 and UX-7 both touch the card and `sensor.py`, in different functions, so whichever merges second merges main.
UX-1..3 and SW-3 follow the same rule on the card.

The build script refuses the result if the longest open chain or EG-A4's chain grows.

## Item 5 (deferred, U3)

Filed as a feature request: publish the heat pump's planned load and its up/down flexibility with duration; accept
other planned loads and "reduce now" signals as solver constraints so the household stays under its monthly peak;
optional SG-Ready. It would sit in the solve's input assembly after EG-B1 and EG-B6, like SW-1.
