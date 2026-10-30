The owner asked for a blueprint that sends an app notification when the Wood Cheaper Than Heat Pump sensor is expected to turn on during the day, with a recommended time window to light the furnace (tvofi, 2026-10-30). The sensor said only whether wood is cheaper now (`sek_per_kwh`, `cheaper_hour_count`) and nothing about when. This change gives the existing sensor today's cheaper windows and a lighting window as attributes, adds one option for the lighting lead time, and ships the blueprint.

- `wood_fuel.py`: `cheaper_steps` is the per-step rule (the plan runs the pump, the COP is usable, and wood's SEK/kWh is below price / COP). `cheaper_hour_count` is now its sum, so the count and the windows cannot disagree. `cheaper_windows` merges contiguous cheaper steps of the local calendar day of the plan's first step into (start, end), and a run that crosses midnight ends there. `lighting_window` opens `wood_lighting_lead_minutes` before the first window and closes at its start, never before the plan's first step. `build_wood_fuel_view` attaches `cheaper_windows`, `lighting_start` and `lighting_end` only while today has a window, so a view without one is byte-unchanged (the coordinator goldens do not move).
- `binary_sensor.py`: `WoodCheaperBinarySensor` publishes `cheaper_windows` (an empty list when there are none), `lighting_start` and `lighting_end` (None when there are none). No new entity: the attributes carry it.
- Option `wood_lighting_lead_minutes` (wood group, shown only while the wood furnace is on, 0–240 min in 15-min steps, **default 60**). Why 60: a batch wood boiler takes roughly half an hour to an hour to get from kindling to a full burn with its water hot enough for the load valve (Laddomat-type valves open in the low 60s °C) to start charging the tank. 60 is the upper end of that range, so the fire is charging as the cheaper window opens, and lighting a little early costs little because the heat goes to the store. 0 means "light at the window start" for an install whose boiler comes up fast.
- `local_tz`: the plan's timestamps are UTC. The coordinator, which is the HA glue, passes `dt_util.DEFAULT_TIME_ZONE` through `wood_fuel_from_parts`, so `wood_fuel.py` gains no `homeassistant` import. Windows and the lighting window are published in local time.
- Blueprint `blueprints/automation/notify_wood_cheaper_window.yaml`, in the style of `notify_on_manual_plan.yaml` (`source_url`, `author: tvofi`, documented inputs). Inputs: the wood sensor; a companion-app device (`notify.mobile_app_<device>`); a send time (default 06:00); a follow-up toggle; title and message templates. At the send time it sends one notification if today has a window, naming the windows and the lighting window as HH:MM local time, and stays silent otherwise. If enabled, it sends a follow-up later the same day only when a replan brings a window that is not yet open and was not in the previous state.
- Classified like its siblings: on `tests/closure.py`'s `INERT_EXCEPT` beside the other four blueprints, and in the measured closures of `doc_claims.py` (which globs every blueprint) and `wood_advisor.py`. It is listed in `docs/automations.md` and `README.md` (`entities.py` requires the two lists to be set-equal), and the option and attributes are documented in `docs/configuration.md`.

Alternatives considered:
- A new entity (sensor) for the next window. Lost: the brief asks for attributes unless an attribute cannot carry it, and both fit.
- Computing "today" in UTC. Lost: in Sweden the UTC day ends at 01:00 or 02:00 local, so an evening window would land on the wrong day. A check pins this (UTC+1: the 23:00 UTC step is tomorrow).
- Converting the timestamps to local time before the view. Lost: `night_advice` reads `when.hour` from the same timestamps, so its 18–06 night band would shift, a behaviour change out of scope.

## Head

Head `6d434319629e`, merge base `c098261d4f44`. The figures were measured at `95eebb247775`. The last three commits only delete seven stale ledger pins, re-run the D6 claims register and rename four test helpers; `tests/wood_advisor.py` was re-run at the head (`ALL 24 … PASSED`), and so was `ci_predict.py` (no closures, fast, governance or instrument red). `origin/main` was at `a9ba3022e321` at 2026-10-30T20:31:29Z, and `git merge-tree --write-tree origin/main HEAD` reports no conflict, so main is not merged in.

## Mutation proof

The failing test came first: commit `0546b7208` adds the checks before any production change. Each mutant below was applied to `wood_fuel.py` (or the blueprint) in a detached worktree of the head and run with `PYTHONPATH=tests/hastub:<jinja2> python3 tests/wood_advisor.py`. All were killed (rc 1); the failing check names are listed under each. The rule they mutate is in the first column.

| rule | mutant | killed by |
|---|---|---|
| pump-off step is never a window | `cheaper_steps` drops `bool(on) and` | "a cheaper step while the pump is planned off is not a window"; "a day with two cheaper runs gives two windows…" |
| contiguous steps merge into one window | `if out and out[-1][1] == ts:` → `if False:` | "a day with two cheaper runs gives two windows, each contiguous run once" |
| today only | the `if day(ts) != today: break` lines deleted | "a cheaper step tomorrow is counted but is not one of today's windows"; "today is the local day…" |
| today is the LOCAL day | `day()` returns `ts.date()` | "today is the local day: at UTC+1 the 23:00 UTC step is tomorrow…" |
| lighting opens lead-time before | `first_start - timedelta(minutes=lead_minutes)` → `first_start` | "the lighting window opens the default 60 min before…"; "the lead time is the configured option" |
| lead is the option | `config.get(CONF_WOOD_LIGHTING_LEAD_MINUTES)` → `None` | "the lead time is the configured option" |
| never opens before now | the `max(..., now)` clip removed | "a window open at the plan's first step lights now, never in the past" |
| closes no later than the window's start | lighting end = the window's end | "the lighting window opens … and closes at its start"; "a window open at the plan's first step lights now…" |
| blueprint: silent without a window | the two window conditions deleted | "null control: on a day with no cheaper window it stays silent" |
| blueprint: follow-up only after the send time | `now() >= today_at(send_time)` deleted | "and one whose windows did not change, or that lands before the send time, does not" |
| blueprint: follow-up only for a new window | `w not in old and` deleted | the same check |

The production base fails the new checks. At the merge base, with the head's `tests/wood_advisor.py`, the run stops at `TypeError: build_wood_fuel_view() got an unexpected keyword argument 'local_tz'`. With that keyword stripped for the base run, these fail: "a day with two cheaper runs…", "the lighting window opens the default 60 min…", "the lead time is the configured option", "a window open at the plan's first step…", "today is the local day…", and then `KeyError: 'cheaper_windows'`.

## Null control

- View: a day on which wood never beats the pump (every price 1.0 against wood's 1.0 SEK/kWh at COP 3) gives no `cheaper_windows` and no lighting window, with `cheaper_hour_count` 0, through the production `build_wood_fuel_view`.
- A cheaper step while the pump is planned off is not a window.
- A cheaper step tomorrow is counted (`cheaper_hour_count` 1) but is not one of today's windows.
- Sensor: with no window it publishes `cheaper_windows: []` and `lighting_start`/`lighting_end` None.
- Blueprint: rendered against the null sensor state, the conditions evaluate False (silent). A replan whose windows did not change, or one before the send time, does not follow up.
- The positive arms (two windows, the lighting window, a new window after a replan) pass on the same fixture, so these are not vacuous.

## Figures

- `PYTHONPATH=tests/hastub:<scratch jinja2 3.1.6> python3 tests/wood_advisor.py` at the head: `ALL 24 wood-advisor checks PASSED`. Without jinja2 (CI's fast lane, `tests/requirements-ci.txt`): `ALL 20 wood-advisor checks PASSED`, and the section heading prints `NOT RENDERED: jinja2 is not installed`. The four template-render checks therefore run only where jinja2 is installed. The structural blueprint checks (inputs declared ⇔ referenced, `source_url`/author, triggers) run everywhere.
- Template rendering uses jinja2's `NativeEnvironment`, with the six HA helpers the blueprint calls (`state_attr`, `as_timestamp`, `timestamp_custom`, `now`, `today_at`, `device_attr`, `slugify`) shaped as Home Assistant's are and local time fixed at UTC. It is not Home Assistant's template engine. A run under real HA (the nightly-ha environment) is not done here.
- Mutants: 11 applied, 11 killed (table above). The rule is one mutant per window rule and per blueprint condition. Runner: a scratch script that copies the head into a detached worktree per mutant.
- `python3 tests/structure.py`: no `FAIL` row at the head. What moved and how it was paid:
  - `max_class_loc` and `class_excess_loc` (+1, the coordinator's `local_tz=` argument line): paid by `configured_quiet_windows` returning `quiet_windows.configured_specs(...)` directly instead of through a one-use local.
  - `dead_top_level_symbols` (+1 at the first implementation commit, `cheaper_hour_count` left without a production caller): paid by the view counting with `cheaper_hour_count` again. `cheaper_steps` runs only on a day with a cheaper step.
- `python3 -I tools/audit/archscore/gate.py --base c098261d4f44 --head 95eebb247775`: `PASS: dS +0.0006 IMPROVES, no gate metric rose` (`coord_footprint 2381 -> 2380`). At the commit before the last, `params_over_10 6 -> 7` (`build_wood_fuel_view` at 11 parameters). Paid by removing `suppressing`, which `forecast_kw` already carries: production forecasts only while suppressing and passes `[]` otherwise, and every other caller passed `suppressing=False, forecast_kw=[]` (`tests/features.py` ×3, `dev/audit/rounds/round9/D12/leads/l2_wood_currency.py`, both ported).
- `GOLDEN_MODE=drift python3 tests/golden.py` against the merge base: `CLAIMED config_flow: 1 leaves moved`, `NO UNCLAIMED DRIFT: 56 scenario(s)`, `NO STALE FIXTURE: 56`. `tests/golden/config_flow.json` was re-recorded alone (`golden.py --record --only config_flow`); its diff is the one added `wood_lighting_lead_minutes` field. It is claimed in `claimed_drift.txt` under `claims-for: 7.1.0`.
- `python3 tests/env_drift.py --claims-only c098261d4f44`: `claims hygiene: … ok`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` at the head (run under `derive_closures.sh --single tests/entities.py --record-only`): `ALL 2488 ENTITY CHECKS PASSED`. The merged record leaves the entities closure unchanged, because it does not open the new blueprint.
- `tests/features.py` at the head: `ALL 4605 FEATURE CHECKS PASSED`.
- `tests/closure.py selftest`: exit 0. `derive_closures.sh --single` was run for `wood_advisor.py` and `doc_claims.py`: both closures now hold the blueprint (`tests/closures.json`, +4 lines).
- Scope: `python3 tests/closure.py select --diff c098261d4f44` prints `MODE: FULL -- … tests/closure.py changes the gate itself`, a diff the gate cannot scope. The scripts the diff reaches were run as above, and the rest is CI's.
- Seams of the rule "a cheaper hour is a planned-pump hour with wood below price/COP", enumerated by `grep -n "finite_float(price, 0.0) / cop_f\|/ cop\b" custom_components/heatpump_optimizer/wood_fuel.py`:
  - `cheaper_steps`: closed in this diff. It is now the one owner, and both the count and the windows read it.
  - `_scan_wood_night`: it computes the pump's price/COP margin for the night advice, an independent advisory with its own 18–06 band, and does not consult the plan's on schedule. That is distinct behaviour, untouched here. Its band reads `when.hour` of the UTC plan timestamps, so in Sweden it is local 19–07 or 20–08. That was not measured against an owner intent and is not changed here.

## Red checks

- `mutation` (predicted by `tools/pr/ci_predict.py`): the diff adds 18 sites with no ledger pin, listed under Unpinned sites. The cheaper detector is that predictor, which `prepr.sh` step 6d already runs before any push. It costs nothing more. The repair is `mutation-autofix`'s pin after the push (`ci-autofix.md`). The window rules behind these sites are killed by the hand mutants above.
- `ledger` (predicted, repaired before the handoff): seven `killed_by` pins named sites this branch rewrote: `cheaper_hour_count`'s body ×5, `wood_cheaper` ×1 and `configured_quiet_windows` ×1. They were deleted by hand, which is the route `ci_predict.py` names. The same predictor is the cheaper detector.
- Locally, before any push, `entities.py` went red twice at the first implementation commit:
  - "every tracked file is either measured or deliberately classified": the new blueprint was not yet in a measured closure. Repaired with `derive_closures.sh --single` for `wood_advisor.py` and `doc_claims.py`. The cheaper detector is `prepr.sh` step 6b / `ci_predict.py`.
  - "the CI ratchet … passes the committed table at its own recorded count": `archscore.public_unused` went 2 > 1 because `cheaper_hour_count` had become dead. Repaired by the structure payment. The cheaper detector is `tests/structure.py`, which reports the same symbol as `dead_top_level_symbols`.

## Unpinned sites

- `custom_components/heatpump_optimizer/wood_fuel.py:137 CMP_BOUND`: value check: the zero-COP and pump-on checks in `tests/wood_advisor.py`; pin by `mutation-autofix`
- `custom_components/heatpump_optimizer/wood_fuel.py:138 CMP_BOUND`: value check: "a day with two cheaper runs gives two windows…" (prices on both sides of wood's 1.0 SEK/kWh); pin by `mutation-autofix`
- `custom_components/heatpump_optimizer/wood_fuel.py:140 RETURN_DEL`: value check: every window check reads `cheaper_steps`' list; pin by `mutation-autofix`
- `custom_components/heatpump_optimizer/wood_fuel.py:150 RETURN_DEL`: value check: "that hour counts" (`tests/features.py`) and `cheaper_hour_count` 1/0 in `tests/wood_advisor.py`; pin by `mutation-autofix`
- `custom_components/heatpump_optimizer/wood_fuel.py:164 CMP_BOUND`: pin by `mutation-autofix`; a one-step plan is not driven (the guard refuses a step it cannot measure)
- `custom_components/heatpump_optimizer/wood_fuel.py:164 GUARD_OFF`: pin by `mutation-autofix`; as above
- `custom_components/heatpump_optimizer/wood_fuel.py:174 GUARD_OFF`: value check: "a cheaper step tomorrow is … not one of today's windows" (hand mutant "today only" killed); pin by `mutation-autofix`
- `custom_components/heatpump_optimizer/wood_fuel.py:176 GUARD_OFF`: value check: "a day with two cheaper runs gives two windows…"; pin by `mutation-autofix`
- `custom_components/heatpump_optimizer/wood_fuel.py:178 BOOLOP`: value check: "a day with two cheaper runs gives two windows, each contiguous run once" (hand mutant "contiguous steps merge" killed); pin by `mutation-autofix`
- `custom_components/heatpump_optimizer/wood_fuel.py:178 GUARD_OFF`: value check: as above; pin by `mutation-autofix`
- `custom_components/heatpump_optimizer/wood_fuel.py:182 RETURN_DEL`: value check: every window check; pin by `mutation-autofix`
- `custom_components/heatpump_optimizer/wood_fuel.py:193 CLAMP_DROP`: value check: "a window open at the plan's first step lights now, never in the past" (hand mutant "never before now" killed); pin by `mutation-autofix`
- `custom_components/heatpump_optimizer/wood_fuel.py:193 RETURN_DEL`: value check: the lighting-window checks; pin by `mutation-autofix`
- `custom_components/heatpump_optimizer/wood_fuel.py:492 GUARD_OFF`: pin by `mutation-autofix`; an equivalent-output guard (it skips the step scan on a day with no cheaper step)
- `custom_components/heatpump_optimizer/wood_fuel.py:494 CMP_BOUND`: value check: "ready with an idle plan is off" (`tests/entities.py`) and the `cheaper` flag in `tests/features.py`; pin by `mutation-autofix`
- `custom_components/heatpump_optimizer/wood_fuel.py:531 GUARD_OFF`: value check: null control "a day wood never beats the pump gives no windows and no lighting window"; pin by `mutation-autofix`
- `custom_components/heatpump_optimizer/wood_fuel.py:602 BOOLOP`: pin by `mutation-autofix`; the suppressing-forecast arm of `wood_fuel_from_parts` (a moved line: the old `suppressing` local folded in)
- `custom_components/heatpump_optimizer/wood_fuel.py:602 GUARD_OFF`: pin by `mutation-autofix`; as above

## Forward-carry

`none`

## Friction

- fixer.md: cost: CI's fast lane installs no jinja2 (`tests/requirements-ci.txt`), so a blueprint's templates can be rendered only where it is installed; adding it changes the canonical environment. Carry: dismissed: environment change belongs to the orchestrator, not this fix
