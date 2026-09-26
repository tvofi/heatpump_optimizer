# D10, verifier V3 (reach and class), round 9, box G2-V3

Baseline `1936d5ca` plus round-9 evidence (6f51db2c). 4-vCPU shared container, CPython 3.14.0rc2. Real HA: homeassistant 2026.2.3 in its own venv.

| finding | vote | severity |
|---|---|---|
| D10-s1-01 | verify | medium |
| D10-s1-02 | weaken | low (was medium) |
| D10-s1-03 | verify | low |
| D10-s2-01 | weaken | low (was medium) |

**Harnesses** (`tools/audit/round9/D10/verify-v3/`): `_realha.py` (shared bootstrap, not a harness), `realha_uid.py`, `realha_uid_service.py`, `realha_press.py`, `realha_auth.py`, `realha_presets.py`, `results_auth.txt` (recorded auth runs; that harness takes about 3 minutes).

**Environment shims in `_realha.py`** (none changes production code):
- A stand-in ABC for `typing.ByteString`, needed by mashumaro on 3.14.
- numpy, scipy, threadpoolctl symlinked from the CI venv into a temp dir exported on `PYTHONPATH`, so the integration's spawned solve worker imports numpy. (The first attempt without it failed with "No module named numpy"; fixed before counting anything.)
- `http` marked loaded; `hass.http` gets a no-op `async_register_static_paths`.

Everything else is real HA: FlowManager, OptionsFlowManager, ConfigEntries setup and retry, DataUpdateCoordinator, Debouncer, the service registry, ButtonEntity, entity platforms, translation and icon loading.

**Run command.** `env -u PYTHONPATH <ha-venv>/bin/python tools/audit/round9/D10/verify-v3/<h>.py`, from the repository root.

**Load and threads.** All metrics are counts. Finder re-runs: thread_factor 1.000. Real-HA runs: thread_factor 1.04–1.55 from HA's own executor threads (storage, loader, process-worker bridge); none of those numbers is a timing.

## D10-s1-01: unique id not re-derived after reauth or an options edit

**Step 1.** `unique_id_drift.py`: `dup_accepted=3`, `stale_refused=3` (load1 1.17, tf 1.000); `--fix` 0 and 0 (load1 1.23). Exact.

**Step 2 (`realha_uid.py`).**
- **Metric:** of 5 arms, how many let a fresh user flow through the real FlowManager (user → sectioned user_sensors → finish_now → setup_overview) be accepted when it submits the entry's current effective identity answers.
- **Arms:** control; reconfigure (real SOURCE_RECONFIGURE); reauth (real `ConfigEntry.async_start_reauth`, driven through the FlowManager); options token and options indoor sensor (real OptionsFlowManager, init → advanced → entities).
- **Baseline:** `dup_accepted=3` (reauth, options_token, options_indoor), `stale_refused=3`, `entries_after_dup_max=2` — real HA ends with two config entries for one plant. load1 1.46.
- **`--fix`** (real `async_update_entry` wrapped to re-stamp unique_id via its own `unique_id=` argument): 0, 0, 1 entry (load1 1.32). Control and reconfigure 0 in both runs.

**Attacks.** Contention: count. Gate mode: n/a. Grid: each arm a distinct write seam. Null control: control and reconfigure 0 in both modes. Reachability: real — a user changes the token or a sensor, then adds the same plant again. Severity: two optimizers actuating one heat-pump switch, exactly what the Bronze unique-config-entry guard exists to prevent — **medium earned**.

**Seam rule.** 12 grep lines in config_flow.py; four identity writes: :2464 reconfigure (re-stamps correctly), :2950 reauth, :3021 `_save`, :3055 `_save_or_menu`. Scoped to config_flow.py, it misses **services.py:629 `handle_assign_entity`** (the card's click-to-assign), which writes 12 of the 13 `_IDENTITY_ENTITY_KEYS` (the overlap of `topology.ASSIGNABLE_KEYS` and `_IDENTITY_ENTITY_KEYS`). Measured in real HA with `realha_uid_service.py` on a LOADED entry (`hass.services.async_call(DOMAIN, "assign_entity", {indoor_temp_entity → sensor.indoor_new})`): baseline `dup_accepted=1`, 2 entries; `--fix` 0; control 0. The other `async_update_entry` sites write no identity key (services :692, :840; coordinator :2529; away :432). **Partial.**

**Class:** P2 confirmed (re-stamp guard at the reconfigure seam, missing at its siblings).

**Vote: verify, medium.**

## D10-s1-02: Optimize-now press returns normally when the solve did not run

**Step 1.** `press_vs_service.py`: `silent_presses=2` (load1 1.23, tf 1.000); `--fix` 0 (load1 1.99). Matches.

**Step 2 (`realha_press.py`).** Entry created by the real flow with a price-entity source and set up by real ConfigEntries (platforms, first refresh, background first solve). Press via `hass.services.async_call("button", "press", blocking=True)` on the real ButtonEntity; action via `hass.services.async_call(DOMAIN, "run_optimization", blocking=True)`. Arm state applied after a healthy setup; the real Debouncer's cooldown waited out before the press. Metric `silent_presses`: arms where the press returned with no exception and no solve completed with reason None.

| run | silent_presses | finder_metric | debounced_presses | load1 |
|---|---|---|---|---|
| baseline | 2 (stale_prices, feed_down); prices_ok 0 | 1 | 3 | 1.20 |
| `--fix` (finder's) | 0 | – | – | 0.63 |
| `--fix-fetch` | 0 | – | – | 0.67 |

- **finder_metric = 1, not 2.** A loaded coordinator in real HA has cached prices from setup; in feed_down the service solves on them and succeeds, while the press's refresh fails its fetch and never solves. The finder's feed_down arm had no cached prices, so its "service raises" pairing there is a harness-state artefact. The phenomenon (press returns silently with no solve) holds in 2 of 3 arms.
- **debounced_presses = 3.** A press within the 10 s cooldown of a previous refresh request returns before any solve starts; the refresh runs later. The stub's modelled Debouncer has this path too.
- **The finder's `--fix` reaches 0 in real HA by solving on cached prices, not by raising**: stale_prices shows `press_solve=[None]`.
- **`--fix-fetch`** (press fetches first, UpdateFailed → HomeAssistantError, then solves, raises on a reason code): stale_prices and feed_down raise, prices_ok stays ok. A real fix has to fetch and bypass the debouncer, because `async_request_refresh` cannot return a reason.

**Attacks.** Contention: counts. Gate mode: n/a. Grid: the feed_down correction above. Null control: prices_ok 0 in all modes. Reachability: real. Severity: feedback only — no wrong actuation, the last plan keeps running, and in feed_down the coordinator entities go unavailable (visible). Only stale_prices is fully silent. A Silver action-exceptions gap: **low**.

**Seam rule.** 27 lines across button, switch, climate, datetime. Every switch, climate and datetime action uses `refresh=False` and requests no solve; the only kept hit is ForceOptimizationButton. The named candidate DiagnoseIntervalButton matches its service (`handle_diagnose_interval` also returns a None report without raising): no asymmetry. No select or number platforms. **All.**

**Class:** P2 confirmed.

**Vote: weaken, low.**

## D10-s1-03: Tibber auth refusal reaches HA as ConfigEntryNotReady/UpdateFailed

**Step 1.** `auth_failed.py`: `auth_as_transient=3`, `transient_ok=2` (load1 1.23, tf 1.000); `--fix` 0 and 2 (load1 1.99). Matches.

**Step 2 (`realha_auth.py`).** Entry created by the real flow with a Tibber token that validates 200 and set up by real ConfigEntries; the coordinator session is a counting stand-in; the end state read is real HA's own.
- **Metric:** auth arms where the entry ends SETUP_RETRY with a retry timer armed, or (steady) the coordinator has its next poll scheduled.
- **Baseline:** `auth_as_transient=3`, `transient_ok=2`.
  - setup_401 and setup_403 end SETUP_RETRY with retry armed and stay there after 40 s.
  - The integration's own reauth flow is present (1 per arm), so the user is still prompted.
  - Tibber is POSTed 4 times in 40 s per arm with the revoked token (retries at 5, 10, 20 s; backoff caps at 80 s, about 45 per hour indefinitely). `revoked_posts=8` over 2 arms.
  - steady_401: `last_exception=UpdateFailed`, next poll scheduled.
  - load1 1.19, tf 1.069.
- **`--fix`** (`_async_update_data` wrapped in memory to re-raise the real `homeassistant.exceptions.ConfigEntryAuthFailed` once reauth has started): `auth_as_transient=0`; both setup arms SETUP_ERROR, no retry, `revoked_posts=2` (first attempt only); steady polling stops. 500 and connection-error controls stay SETUP_RETRY (2/2). load1 0.84.
- One wrapper suffices in real HA because the first refresh runs `_async_first_refresh_light` inside `_async_update_data`.

**Attacks.** Contention: counts (post counts from a wall-clock window, ±1). Gate mode: n/a. Grid: setup and steady separate seams. Null control: passes. Reachability: real. Severity: the reauth prompt already appears; the cost is the wrong entry state ("retrying" not an auth error) plus indefinite polling of Tibber with a known-revoked token. **Low** earned.

**Seam rule.** 52 coordinator lines, mostly `except Exception` noise, 0 stub hits; `tests/ha_contract.py` has no entry for ConfigEntryAuthFailed or reauth. The relevant seams — the fetch (:5687, the only `pull_prices` caller and only credentialed fetch) and the two update wrappers (:4599, :4733 callers) — are all covered. **All** (noisy).

**Class:** P11 confirmed (the stub lacks the exception class and upstream's auth arm, so no test could express the correct behaviour; real HA shows the wrong one).

**Vote: verify, low.**

## D10-s2-01: climate presets auto/economy untranslated and without an icon

**Step 1.** `climate_presets.py`: 2/2/2/2 (load1 1.23, tf 1.000); `--perturb translate` 0; `--perturb eco` 1 (load1 1.99). Matches.

**Step 2 (`realha_presets.py`).** Entry set up in real HA. `preset_modes` read from the real state machine: `['auto', 'comfort', 'economy', 'boost']`; registry `translation_key` None. Each preset resolved as the frontend does, against real `async_get_translations` (entity for this integration, then entity_component for climate) and `async_get_icons`.
- **Baseline:** `untranslated_en=2`, `untranslated_sv=2` (auto and economy shown as raw tokens; comfort → "Komfort", boost → "Boost"); `no_specific_icon=2`; `hvac_untranslated=0`. load1 0.85, tf 1.042.
- **`--perturb`** (economy → eco): 1/1/1/0 (load1 1.27).
- **Correction to the claim:** the two presets are not icon-less. Real HA's climate icons.json gives them the component default `mdi:circle-medium`; they lack a specific state icon.

**Attacks.** Contention none; gate mode n/a; grid none; null control passes (translate 0). Reachability: real (frontend display path). Severity: cosmetic — two labels shown as lowercase English tokens in both languages with a generic dot icon, nothing functional. The quality_scale.yaml rows `entity-translations: done` and `icon-translations: done` overclaim. **Low**, not medium.

**Seam rule.** The finder's harness covers preset_mode; my harness checked hvac_modes (all 3 HA-standard and translated); no fan or swing modes. **All.**

**Class:** correct I5 → **P6** (the frontend reads `...preset_mode.state.<p>`, which no strings file writes, and falls back silently to the raw token and default icon). I5 applies only to the secondary symptom, the quality_scale.yaml rows marked done.

**Vote: weaken, low.**

---

Counts: verify 2, weaken 2, refute 0, unresolved 0.
