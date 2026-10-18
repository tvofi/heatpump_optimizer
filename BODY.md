README gains a `## Minimal working setup` section, placed right after
`## Requirements` (owner request, tvofi 2026-10-18). It names the two smallest
setups that work — plan only (a price source plus a weather entity with hourly
forecasts) and the smallest setup that controls the pump (plus a heat-pump
on/off `switch`) — and, for each item, why it is needed and what happens
without it; then the indoor temperature sensor as the next addition, with what
it adds and what is missing without it. Every claim is traced to the code
below, under `## Figures`. Part of #201.

The section links rather than restates: the setup flow is
[Quick start](#quick-start--the-first-30-minutes), the other two control paths
are [Supported heat pumps and controls](#supported-heat-pumps-and-controls).
It overlaps `## Requirements` on the two required items by design — the brief
asks for a plain, complete recipe for a user, and README is outside the
development record's uniqueness rule.

**A README claim corrected before it shipped.** The first draft named the
switch field *Heat pump switch*; `tests/doc_claims.py`'s I5 arm ("every
options field the docs name is a label the forms render") refused it, and the
section now uses the label the form renders, *Heat pump on/off switch*
(`strings.json` `config.step.user_sensors.data.heat_pump_switch_entity`).

**Existing README claims checked while doing this, none false.** `## Requirements`'
two required items match `_user_credentials_fields`; `## Known limitations`'
"it may turn the pump off during expensive hours" is incomplete (the switch is
also turned on) but not false, and the new section states both directions.

**A code finding, traced, not fixed here (out of scope for a README change).**
With no indoor entity configured, `ThermalState.room_temperature` keeps its
21.0 °C constructor default (`coordinator.py` `_update_current_state` writes it
only under `if indoor.ok`), and `_learning_frozen` deliberately does not freeze
on an unconfigured slot. `_async_learn_house_heat_loss` has no other gate on
the indoor entity, so it appears to replay each interval against that constant
21.0 °C as the "observed" room; the lead-prediction scoring in the same file
(`score_lead_predictions`, gated on `actual_now is not None`) reads the same
constant. `topology.py`'s `rank_sensor_advisor` comment says the opposite ("the
scale sits at its prior"). Traced by reading only, not executed; the README
section therefore claims heat-loss correction only *with* an indoor sensor and
makes no claim about what the learner does without one. This belongs to the D1
(robustness) / D2 (physical sanity) brief, not to an issue, per
`finding-propagation.md`; it is named here for the orchestrator to route.

## Head

`9ef452f5d8def3b7e4de3fc692d5b5a33b0a7994` merges origin/main `55dc8d9c2` (66 commits ahead of the previous merge point) into `cb4e0195ba1db57f12fb345f5fe14f82bc175a7c`, which adds this PR's own row `dev/programme/delivery/2393.md` over the earlier orchestrator merge `b021a4c7e56151e06725e8d0a890a658af05d3e4`. The merge was clean (no conflicts); `git diff --name-only origin/main HEAD` lists `README.md` and `dev/programme/delivery/2393.md` only. The authored code head is `38743da446494ffebbf96974bcaeecbe88de4854`.

`38743da446494ffebbf96974bcaeecbe88de4854`, one commit on merge base
`64b1f82a3958a1701755bf60973c592078cd0a12` (= origin/main at measurement,
2026-10-18T09:36Z). The diff is `README.md` alone.

## Mutation proof

The section's sentences are prose; two of its mechanical properties are pinned
by `tests/doc_claims.py`, and each goes red when broken:

- Field label: `sed -i 's/\*Heat pump on\/off switch\* field/*Heat pump switch* field/' README.md`
  -> `FAIL every options field the docs name is a label the forms render  [['README.md: *Heat pump switch*']]`, `1 of 169 checks FAILED`.
- Anchor: `sed -i 's/(#quick-start--the-first-30-minutes)/(#quick-start-the-first-30-minutes)/' README.md`
  -> `FAIL the build exits 0 with no FAIL line  [README.md: anchor #quick-start-the-first-30-minutes is not a heading of readme.html]`, `1 of 169 checks FAILED`.

Both restored with `git checkout README.md`; the restored tree prints
`ALL 169 checks PASSED`. The behavioural claims (what happens without an
entity) are pinned by no check; each is cited to its code under `## Figures`.

## Null control

At the merge base `64b1f82a`, README has no `## Minimal working setup` heading
(`grep -c '^## Minimal working setup' README.md` -> `0`), and
`tests/doc_claims.py` passes there and here, so the arms above judge the new
text rather than a pre-existing red.

## Figures

Gate, at the head:

- `python3 tests/closure.py select --diff origin/main` -> `MODE: SCOPED -- 4 script(s) run, 29 scoped out.` (doc_claims, entities, harness_headers, md_tables).
- `python3 tests/doc_claims.py` -> `ALL 169 checks PASSED`.
- `python3 tests/harness_headers.py` -> `ALL 109 HARNESS HEADER CHECKS PASSED`.
- `node tests/md_tables.mjs` -> `doc_orphaned_table_rows=0`, `doc_misrendered_lines=0`, exit 0.
- `python3 tests/structure.py` -> `STRUCTURE RATCHET PASSED`.
- `python3 tests/entities.py` -> `ALL 2346 ENTITY CHECKS PASSED`, run with `BASH_ENV` and `ENV` unset (see `## Friction`); with them set, as this container exports them, it prints `1 of 2346 ENTITY CHECKS FAILED` identically at origin/main `64b1f82a`.

Each claim in the new section, and where it is true:

- Price source and weather entity are the only required inputs: `config_flow.py` `_user_credentials_fields` (`vol.Required(CONF_WEATHER_ENTITY)`; the price source is enforced in `async_step_user`, which returns `price_entity_required` / `tibber_token_required`); every picker in `_user_sensors_fields` is `vol.Optional`.
- A Tibber token is checked with Tibber before setup continues: `config_flow.py` `async_step_user` -> `validate_tibber_token`, errors `invalid_tibber_token` / `cannot_connect`.
- A price entity is read from `raw_today` / `raw_tomorrow`: `price_model.py` `prices_from_entity_attributes`.
- No prices -> no planning, no invented curve: `coordinator.py` `_price_series` ("No electricity price data available; skipping optimization until prices can be fetched").
- Hourly forecasts, with temperature, wind and rain: `coordinator.py` `_fetch_weather_forecast` calls `weather.get_forecasts` with `"type": "hourly"` and logs "full 24h+ trajectory: temp, wind, rain, solar".
- A failed fetch keeps the last forecast, marked stale: `coordinator.py` `_weather_fetch_failed` ("Plans continue on the last forecast, marked stale.").
- Without a control path the plan is published for your own automations: README `## Supported heat pumps and controls` (linked, not restated); `thermal_model.py` `probe_install` writes nothing without a switch, set-point or frequency entity.
- The switch turns the pump on and off to follow the plan: `coordinator.py` `_apply_action` calls `pump_arbiter.switch_supply(self.hass, switch_entity, heat_pump_on)`, gated on `switch_entity`; `pump_arbiter.py` `switch_supply` -> `on_off_service`.
- Field label *Heat pump on/off switch* on the *Optional sensors* screen: `strings.json` `config.step.user_sensors` (`title`, `data.heat_pump_switch_entity`).
- Without an indoor sensor every plan starts from an assumed 21 °C: `thermal_model.py` `ThermalState.room_temperature: float = 21.0`; `coordinator.py` `_update_current_state` assigns it only under `if indoor.ok`.
- Indoor Temperature sensor and the thermostat's current temperature are unavailable without one: `sensor.py` `IndoorTempSensor.available`; `climate.py` `available` / `current_temperature` (A3(e)).
- With one, the heat-loss estimate is corrected against the measured room: `coordinator.py` `_async_learn_house_heat_loss` (residual = observed − predicted room).
- With the switch too, a heating run is cut short on overshoot within an interval: `early_cutoff.py` (module docstring; releases unless both `indoor_temp_entity` and `heat_pump_switch_entity` are set).
- Without an outdoor sensor the forecast supplies the outdoor temperature: `coordinator.py` `_update_current_state` `forecast_outdoor_now` fallback; `topology.py` `_ADVISOR_UNPRICED` (`"weather_backed"`).

## Red checks

All four reds below sit on earlier heads of this branch (`b021a4c7e` and `cb4e0195b`), none on a code cause; this PR's diff is `README.md` plus its delivery row.

- `arch-score` (run 39120936105 and 39120938712, job 117656226223 / 117656233404, head `b021a4c7e`): the step "pull request 2393, body ... bytes" failed with `gh: API rate limit exceeded for installation ... (HTTP 403)` at 2026-10-18T10:52Z, before any scoring ran. Cause is outside this repository (the shared 5,000/hr GitHub installation quota, which the seats exhausted); owner is the orchestrator's poll cadence. There is no cheaper detector to name: the check did not execute. Re-runs on `9ef452f5d8def3b7e4de3fc692d5b5a33b0a7994`.
- `validate-hacs` (job 117656226469, head `b021a4c7e`): `aiogithubapi.exceptions.GitHubRatelimitException: API rate limit exceeded for installation` at 10:52:58Z, the same quota. Green at origin/main `55dc8d9c2`'s own run (`validate-hacs` -> success), so not a property of main or this diff.
- `nightly-status` (job 117656658301, head `cb4e0195b`): `NIGHTLY UNREADABLE ... HTTP 403 ... (rate limit exhausted)` at 10:54:27Z reading run 39106988523's jobs; the check fails closed by design. It reports main's nightly, is not a required context, and is not caused by this PR (a README-only diff cannot reach any nightly lane). Cause is the same quota exhaustion, outside this repository. It reports `skipped` at origin/main `55dc8d9c2` and is re-evaluated on the new head; I did not dispatch `tests.yml` on main (a seat does not start main runs).
- `pr-contract` (jobs 117671022850, 117671105728, head `cb4e0195b`): `[pr-body] check `arch-score` is red and `## Red checks` does not name it` and the same for `validate-hacs`, because `## Red checks` said "none". Fixed by this section; the `nightly-status` red is named here too.

## Forward-carry

`dev/governance/dimensions/D1.md` — the no-indoor-sensor learner finding above
is for the orchestrator to route to that brief; this seat does not edit policy.

## Friction

- `container-toolchain: cost: /etc/profile.d/hpo-toolchain.sh is exported as BASH_ENV and ENV, so every non-interactive bash re-prepends /opt/hpo/venv-ci/bin to PATH; tests/entities.py's graders-head-copy delivery_status arm puts a stub python first on PATH and runs bash -e -c, the venv python shadows the stub, every case returns 0, and prepr.sh's closures step then refuses (entities.py exit 1). Same red at origin/main 64b1f82a; with BASH_ENV and ENV unset: ALL 2346 ENTITY CHECKS PASSED`
- `r10-brief: stale: the brief names "tools/audit/round4/D6 claim checks"; tools/audit/round4/ holds only D11/, and the README claim checks are tests/doc_claims.py`

