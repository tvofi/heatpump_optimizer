# D10-B round-2 report — 8 stub-run behavioral rules + CI/brands evidence

Baseline: `b39fc6f01f4caee9d3ef17bce5f0b4561392fdb9` (pinned export, no `.git`).
Auditor D10-B, fresh eyes. Harness: `tools/audit/round2/D10/B/harness.py`
(single command in its header). All numbers are counts (contention-immune);
`load1` was 2.5–4.9 during the fan-out and the numbers were identical across
four runs; `thread_factor=1.000`, `swapins=0`.

## Method

Every rule was driven through production symbols with the committed HA stub
(`PYTHONPATH=tests/hastub`) and the `tests/harness.py` fixtures (`FakeHass`,
`FakeEntry`, `ha_setup_entry`/`ha_unload_entry`), extending the round-1 B5
idiom. The one seam the stub does not provide is HTTP: the stub's
`async_get_clientsession` raises, so the harness replaces it *in the
`config_flow` and `coordinator` module namespaces* with a scriptable fake
session (200/401/500/exception). The real `validate_tibber_token`, the real
`_fetch_tibber_prices` and the real `_async_update_data` then run to their
verdicts; no production function is stubbed for the flow and log sections.
Heavy siblings of one update cycle (`_update_current_state`,
`_apply_action`, the solvers' savers) are patched to no-ops on the
coordinator *instance* so a poll is exactly "Tibber fetch + branch + log".
`DataUpdateCoordinator.__init__` is spied (not replaced) to capture the
`update_interval` kwarg the production constructor passes.

Two framework facts pinned by lookup of home-assistant/core `2024.6.0` (the
`hacs.json` floor), raw source, not this repo's history:

- `DataUpdateCoordinator.__init__` in 2024.6 has no `config_entry` parameter
  and sets `self.config_entry = config_entries.current_entry.get()` by
  contextvar inference. The coordinator never passes `config_entry`
  explicitly, so its `getattr(self, "config_entry", None)` in
  `_tibber_start_reauth` resolves only through that inference; the harness
  sets the attribute explicitly to mirror it (and measures the contrast with
  the attribute absent: 0 reauth starts).
- The stub's `CoordinatorEntity.available` mirrors the real base
  (`last_update_success`), so availability measurements are meaningful.

## Tier-table rows

| rule | tier | status | command (from export root) | number |
|---|---|---|---|---|
| unique-config-entry | bronze | done | `PYTHONPATH=tests/hastub .venv/bin/python tools/audit/round2/D10/B/harness.py` | `duplicate_flow_aborted=1` (abort reason `already_configured`), null control `distinct_flow_proceeds=1` |
| config-entry-unloading | silver | done | same | `unload_leak=0`; `unload_super_shutdown=1`; `unload_platforms_forwarded=5` |
| entity-unavailable | silver | done | same | `sensors_unavailable_after_failure=55` of `sensors_total=55`; `stale_publishers_after_key_removal=0` |
| log-when-unavailable | silver | done | same | `error_logs_during_5_failed_polls=6` (expected 1) — **finding**; `info_logs_at_recovery=1`; `outage_cycles_after_5_polls=10` (expected 5) |
| reauthentication-flow | silver | done | same | `reauth_flow_started_after_two_401s=1`; `reauth_confirm_fixes_entry=1`; `reauth_steps_present=2` |
| diagnostics | gold | done | same | `diagnostics_in_platform_list=0`; `token_leak_occurrences=0`; `redacted_field_count=1/1` |
| test-before-configure | bronze | done | same | `user_step_error_on_invalid_auth=1`, `user_step_error_on_cannot_connect=1` |
| appropriate-polling | bronze | done | same | `update_interval_default_seconds=1800` (30 min), `900` with `optimization_interval=15` |
| brands (adapted) | bronze | done | `ls -l ...brand/ icon.png` + `gh run list` | assets 3/3 non-zero PNG; Validate green on pinned SHA |
| CI gate (non-rule evidence) | — | done | `gh run list -R tvofi/heatpump_optimizer ...` | Hassfest success, Validate success, CodeQL success, Tests in_progress (parent `e729182`: Tests success) |

## Findings

### D10-21 (log-when-unavailable): every failed Tibber poll logs an ERROR (with traceback), and the outage latch counts two cycles per poll

Claim: during a Tibber outage the integration emits one ERROR log record per
failed poll (6 over 5 polls + transition, expected 1) because
`_tibber_fetch_failed`'s `raise UpdateFailed` is re-caught by
`_fetch_tibber_prices`'s own `except Exception` (re-entering the latch, so
`_tibber_outage_cycles` counts 2 per poll — 10 after 5 polls) and then
re-logged by `_async_update_data`'s blanket `except` at coordinator.py:4460;
the recovery line consequently reports "recovered after 10 failed cycle(s)"
for 5 failed polls.

Executed numbers (harness, RESULT lines `error_logs_during_5_failed_polls`,
`outage_cycles_after_5_polls`, `info_logs_at_recovery`):

- ERROR records during 5 failed polls: **6** (1 `Tibber API error: 500` on
  the first poll + 5 × wrapper `Error updating Heat Pump Optimizer: …`,
  each with `exc_info=True`). Expected by the rule: 1.
- Records at recovery: 1 INFO ("recovered after 10 failed cycle(s)") — the
  once-at-recovery half holds; the count is doubled.
- `_tibber_outage_cycles` after 5 failed polls: **10** (expected 5).

Instrumented symbol: `heatpump_optimizer.coordinator:_async_update_data`
(driven whole, with `_fetch_tibber_prices` reaching the real HTTP seam) and
`heatpump_optimizer.coordinator:_tibber_fetch_failed`.

Perturbations (both dry-run on /tmp copies, both moved the number):

1. coordinator.py:4460 `_LOGGER.error(` → `_LOGGER.debug(` →
   `error_logs_during_5_failed_polls` 6 → **1** (down).
2. coordinator.py:5465 `except Exception` in `_fetch_tibber_prices`: re-raise
   `UpdateFailed` instead of re-calling `_tibber_fetch_failed` →
   `outage_cycles_after_5_polls` 10 → **5** (down).

Metric definition: count of log records at level ≥ ERROR from loggers named
`heatpump_optimizer.*` while `_async_update_data` runs 5 polls whose Tibber
POST returns HTTP 500, minus nothing — compared against the rule's expected 1
per transition; plus the value of `_tibber_outage_cycles` after those 5
polls.

Severity: medium (log flooding with tracebacks once per poll during any
outage — every 30 min at defaults — plus a wrong outage length in the
recovery line; bounded, no data or money impact). Stop-rule class: bug.

Files: `custom_components/heatpump_optimizer/coordinator.py`
(`_fetch_tibber_prices` ~5463–5482, `_tibber_fetch_failed` 5470–5482,
`_async_update_data` wrapper 4459–4463).

Proposed fix scope: re-raise `UpdateFailed` untouched from
`_fetch_tibber_prices`'s handlers (`if isinstance(err, UpdateFailed): raise`)
so the latch counts one cycle per poll, and let the outage latch own the
per-transition ERROR (the wrapper should log DEBUG, or skip UpdateFailed
entirely). The v-comment at 5379–5385 documents exactly the intended
behavior; the wrapper predates/breaks it.

Note: HA core's own coordinator also logs once per failed refresh via
`self.logger`; that record is out of the integration's control and is not
counted here (the stub base does not log), so production will show one more
record per poll than this harness counts — the integration's own excess
stands either way.

## Non-findings (checked and held)

- unique-config-entry holds: the first-screen duplicate aborts
  `already_configured` (`duplicate_flow_aborted=1`) while a second heat pump
  (different switch) proceeds to the temperature step
  (`distinct_flow_proceeds=1`). Command: harness; symbols
  `config_flow:HeatPumpOptimizerConfigFlow.async_step_user` →
  `async_set_unique_id`/`_abort_if_unique_id_configured`
  (config_flow.py:1001–1002, identity = sha256 of token + entity slots,
  `entry_identity` config_flow.py:386).
- test-before-configure holds: the real `config_flow:validate_tibber_token`
  runs inside `async_step_user` (call at config_flow.py:988) before any
  entry is created; HTTP 401 → form error `invalid_tibber_token`
  (`user_step_error_on_invalid_auth=1`), transport failure →
  `cannot_connect` (`user_step_error_on_cannot_connect=1`).
- reauthentication-flow holds: `async_step_reauth` (config_flow.py:1428) and
  `async_step_reauth_confirm` (1452) exist (`reauth_steps_present=2`); a 401
  during the update calls `entry.async_start_reauth(hass)` once per auth
  outage (`reauth_flow_started_after_two_401s=1`, idempotence guard at
  coordinator.py:5504); a good token in the confirm step updates the entry
  data, reloads it and aborts `reauth_successful`
  (`reauth_confirm_fixes_entry=1`). Contrast arm: with the `config_entry`
  link absent (bare stub), 0 starts — the link exists in production only via
  HA 2024.6's contextvar inference (verified against 2024.6.0 source).
  Deviation from the rule's letter, not its substance: the trigger is a
  direct `entry.async_start_reauth(hass)` call, not a raised
  `ConfigEntryAuthFailed` — the same UI result without failing the entry.
- config-entry-unloading holds: `async_unload_entry` forwards all 5 platforms
  (`unload_platforms_forwarded=5`), `async_shutdown` calls `super()` first
  (`unload_super_shutdown=1`, coordinator.py:5015), nothing survives unload
  (`unload_leak=0`: 0 pending background tasks, 0 unsub hooks left set, 0
  `async_on_unload` callbacks left), the reload handover is popped by the
  next setup (`unload_handover_after_reload=0`) and a reload builds a new
  coordinator (`unload_new_coordinator=1`). Known limit: the stub's
  `async_create_task` closes coroutines, so `_background_tasks` is empty by
  construction — the pending-task arm of the metric is vacuous under the
  stub.
- entity-unavailable holds: after a failed update
  (`last_update_success=False`, the stub base mirroring HA) all 55 sensor
  entities report `available=False` (`sensors_unavailable_after_failure=55`
  = `sensors_total=55`); removing any single published key never leaves the
  sensor named for it publishing the old value
  (`stale_publishers_after_key_removal=0`; the two first-pass candidates,
  `CurrentSetpointSensor`/`CurrentPowerSensor`, read the fresh
  `current_action` dict and return None once that is gone — metric mapping
  artefact, not a stale publish). With the payload entirely empty the only
  publishers are designed string sentinels (`'unknown'`, `'not_run'`,
  `'no schedule'`, `'no plan'`); no numeric sensor fabricates a value.
  Note: 24 of 55 are unavailable even on success — designed gates
  (`reading_ok` freshness, `dhw_enabled`, waits-for-evidence mixins).
- diagnostics holds: `diagnostics.py` is discovered as a diagnostics module,
  NOT listed in `PLATFORM_LIST` (`diagnostics_in_platform_list=0`, the
  v6.3.1 platform regression is not present); the payload executes under
  the stub with top-level keys `config, coordinator, domain, entry`
  (`diagnostics_top_level_key_count=4`); the Tibber token is redacted
  wholesale — 0 occurrences of the secret in the serialized payload
  (`token_leak_occurrences=0`), redaction coverage 1/1 sensitive candidates
  (`TO_REDACT={tibber_token}`; entity ids kept deliberately, documented in
  the module docstring).
- appropriate-polling holds: the coordinator is constructed with
  `update_interval=timedelta(minutes=30)` by default
  (`update_interval_default_seconds=1800`), and honors a configured
  `optimization_interval=15` (`900 s`) — a configurable cloud-polling
  interval with a sane default, per the rule.
- brands (adapted) holds: `custom_components/heatpump_optimizer/brand/icon.png`
  (98834 bytes, 256×256 PNG), `brand/logo.png` (98834 bytes, 256×256 PNG),
  repo-root `icon.png` (377596 bytes, 512×512 PNG) — all non-zero; Validate
  (HACS) workflow conclusion `success` on the pinned SHA.
- CI gate on the pinned SHA (the hassfest/validate execution record):
  Hassfest `success`, Validate `success`, CodeQL `success`; Tests
  `in_progress` at both checks (20:24 and 20:33 local); parent commit
  `e7291826…` Tests `success`.

## Unfinished / limits

- Tests on `b39fc6f` was still `in_progress` at the second re-check; parent
  `e729182` Tests success recorded as the proxy, per brief.
- The unload harness cannot see real pending background tasks (stub closes
  coroutines at creation); that leak vector is unmeasurable under the stub
  and was not claimed.
- Only the sensor platform was roster-measured for entity-unavailable (55
  entities); binary_sensor/button/climate/switch availability was not
  roster-run (their `available` overrides at button.py:86/114 etc. follow
  the same `super().available` conjunction pattern seen in sensor.py).

## Exposure

None: no `docs/audit-*`, no backlog, no GitHub issues/PRs read. The two
framework lookups were home-assistant/core `2024.6.0`
`update_coordinator.py` (raw source, pinned tag) to pin `config_entry`
inference semantics.
