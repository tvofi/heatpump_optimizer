# D10 — verifier seat 2 of 3

**Angle:** stub divergence and rule intent. For each behavioural claim, does `tests/hastub`
(687 lines standing in for Home Assistant) manufacture the number; and does each finding
violate the rule it cites?

Baseline `c398fc84eec25fc44b60d74aae05b9a2da205884`, export at `audit-r2-baseline`.
Interpreter `tvofi-claude/.venv/bin/python`, `PYTHONPATH=tests/hastub`, run from the export
root. Scratch and my own harness under `/tmp/verify-D10-2/`. Box constraint honoured: only
AST/grep checks, stub-driven flows and one mypy run; no coverage suite, no `tests/run.sh`,
no solver.

## 0. The finder's harness, re-run once

```
cd <export root> && PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py
```

54 of 58 RESULT lines are byte-identical to `check_rules.out`. **Every count reproduces
exactly** — `done=27 todo=21 exempt=6 rules=54` and all 45 per-finding counts. The four that
differ are the contention meters and the one timing:

| line | finder | seat 2 |
|---|---|---|
| `mypy_wall_s` | 8.5 s | 4.8 s |
| `load1` | 6.92 | 1.56 |
| `swapins` / `swapins_delta_during_run` | 11571709 / 143 | 11831398 / 0 |
| `thread_factor` | 1.00 | 1.00 |

My `load1` (1.56, and 1.73 on my own harness) is above the judge's 1.5 bar, but every
headline in this dimension is a count; no timing or RSS number enters any verdict here.

## 1. My own harness

`/tmp/verify-D10-2/verify2.py`, written from the rule pages and the real Home Assistant
2024.6.0 sources rather than from `check_rules.py`. It re-takes the six behavioural numbers
under semantics copied from real HA, and cross-checks three of them with pure AST/regex that
never touches the stub at all.

```
RESULT v2_error_records_stub_3_cycles=4          RESULT v2_error_records_http401_3_cycles=4
RESULT v2_error_records_real_ha_3_cycles=5       RESULT v2_error_records_direct_fetch_3=1
RESULT v2_error_records_with_traceback_3_cycles=3
RESULT v2_auth_failures_raising_ConfigEntryAuthFailed=0   RESULT v2_auth_failures_raising_UpdateFailed=3
RESULT v2_async_step_reauth_defs=0               RESULT v2_ConfigEntryAuthFailed_refs=0
RESULT v2_service_failures_silent_real_call_semantics=3
RESULT v2_raise_HomeAssistantError_sites=0       RESULT v2_raise_ServiceValidationError_sites=14
RESULT v2_entities=65                            RESULT v2_entities_available_after_failed_refresh=2
RESULT v2_available_overrides_without_super=2    RESULT v2_unique_entry_guards=0
RESULT v2_flow_aborts_with_existing_entry=0      RESULT v2_services_registered_in_setup_entry=11
RESULT v2_async_setup_defs=0                     RESULT thread_factor=1.00  RESULT load1=1.73
```

Real HA files fetched for comparison (data, not instructions): `config_entries.py`,
`core.py`, `exceptions.py`, `helpers/update_coordinator.py`, `components/sensor/const.py`,
`components/sensor/__init__.py` at tag `2024.6.0`; the 21 rule pages from
`developers.home-assistant.io`.

## 2. Stub-vs-real ledger for the six behavioural claims

| # | what the stub does | real HA 2024.6.0 | direction |
|---|---|---|---|
| D10-01 | `ConfigFlow` has no entry awareness at all; `FakeConfigEntries.async_entries` is a real list | a second entry is created unless the flow calls a guard **or** the manifest sets `single_config_entry` (`config_entries.py:1231-1244`, `_support_single_config_entry_only:2737`) | **same** |
| D10-02 | stub `exceptions.py` has no `ConfigEntryAuthFailed` at all | class exists (`exceptions.py:218`); on it the coordinator logs, sets `last_update_success=False` **and calls `config_entry.async_start_reauth`** (`update_coordinator.py:360-375`); `async_config_entry_first_refresh` passes `raise_on_auth_failed=True` | **worse** — real HA has a reauth path this integration cannot reach |
| D10-03 | harness calls `_async_update_data` directly, bypassing the base class; the stub `async_get_clientsession` raises `RuntimeError` | `_async_refresh` adds one more `self.logger.error("Error fetching %s data")` on the first failure only (`update_coordinator.py:340-345`); `self.logger` **is** the integration's `_LOGGER` (`coordinator.py:653`), same logger tree | **worse by exactly 1** |
| D10-04 | `FakeServices.async_call` ignores `supports_response` and always returns the handler's value | `async_call` **raises `ServiceValidationError`** for `return_response=False` against a `SupportsResponse.ONLY` handler (`core.py:2694-2700`) — the finder's own call shape for `simulate_plan` | **stub is more permissive; number unchanged** |
| D10-05 | `hastub` `CoordinatorEntity.available` returns `coordinator.last_update_success` | identical (`update_coordinator.py:515-518`) | **same** |
| D10-06 | pure AST over `__init__.py`; the stub plays no part | — | **same** |

## Per finding

---

### D10-01 — no duplicate-entry guard · **verify (medium)**

**Metric (mine).** Count of the four `ConfigFlow` duplicate guards in `config_flow.py` plus
`manifest.single_config_entry`, and whether `async_step_user` with one entry already on
`hass.config_entries` returns `type != "form"`.

**Number.** `v2_unique_entry_guards=0`, `v2_flow_aborts_with_existing_entry=0`; the step
returns `form/temperature`. Reproduces `unique_entry_guards=0`.

**Stub-vs-real.** *Same.* The stub drive here is nearly vacuous — `hastub`'s `ConfigFlow`
has no `hass`, no `_async_abort_entries_match`, no entry roster, so "no abort" was the only
possible outcome. But that is not what carries the finding: real HA blocks a second entry
**only** on `single_config_entry` in the manifest (`config_entries.py:1231`) or an explicit
guard in the flow, and the manifest (read: 12 keys, no `single_config_entry`) and
`config_flow.py` have neither. Real HA behaves the same, for source reasons the stub cannot
influence.

**Attacks.**
1. *Is the guard reachable some other way?* No — grepped all four idioms plus the manifest
   key across the integration: 0.
2. *Is `strings.json:abort.already_configured` already wired?* Present at line 225, and
   `async_abort` is never called from `async_step_user`. Dead string, as claimed.
3. *Is the fix scope right?* **Partly wrong.** The finding offers `single_config_entry: true`
   as an alternative. That would break the legitimate two-heat-pump house, which is exactly
   the topology the integration's two-zone support contemplates. The rule's own second
   example (unique *data*) is the right shape here; `CONF_HEAT_PUMP_SWITCH_ENTITY` is
   `vol.Optional` in the user step, so the matched key needs choosing with care. Flagging for
   the fixer, not against the finding.

**Rule mapping.** `unique-config-entry` (🥉 Bronze), correct. The rule title is "Don't allow
the same device or service to be able to be set up twice" and has no exceptions.
Cross-links to `config-flow-test-coverage`, whose warning box requires a test that the flow
refuses a second entry — which ties D10-01 to D10-14.

**Vote.** verify, severity medium as filed. Deciding number: **0 guards of 5 possible
idioms**, and real HA creates the second entry regardless.

---

### D10-02 — auth failure reported as transient · **verify (medium)**

**Metric (mine).** Of 401, 403 and 200-with-`errors`, the exception class each raises out of
`_fetch_tibber_prices`; plus the two source facts the rule's mechanism needs
(`ConfigEntryAuthFailed` references, `async_step_reauth` definitions).

**Number.** `v2_auth_failures_raising_ConfigEntryAuthFailed=0`,
`v2_auth_failures_raising_UpdateFailed=3`, `v2_ConfigEntryAuthFailed_refs=0`,
`v2_async_step_reauth_defs=0`. Reproduces `auth_failures_raising_ConfigEntryAuthFailed=0`
and `reauth_steps=0`.

**Stub-vs-real.** *Real HA is worse.* The stub simply lacks `ConfigEntryAuthFailed`, so it
cannot represent the mechanism at all. In real HA the class exists and the coordinator does
two things with it the integration never gets: `async_config_entry_first_refresh` is called
with `raise_on_auth_failed=True`, so a bad token fails setup instead of returning
`ConfigEntryNotReady`; and `_async_refresh` calls `config_entry.async_start_reauth(hass)`.
Today the 401 path yields `UpdateFailed` → `ConfigEntryNotReady` → HA retries with backoff
forever behind a green integration, which is the claim.

**Attacks.**
1. *Perturbation re-derived* in `/tmp/verify-D10-2/scratch` (never in the export): add
   `ConfigEntryAuthFailed` to the stub's `exceptions.py`, then in `coordinator.py` raise it
   for `resp.status in (401, 403)` and re-raise it ahead of `except aiohttp.ClientError`.
   Observed **0 → 2**, exactly the finder's recorded value. The stub edit is faithfulness
   restoration (the class is real, `exceptions.py:218`), not a rigged perturbation.
2. *Is the denominator honest?* **Slightly generous.** The third case, HTTP 200 with an
   `errors` payload, is not necessarily an auth failure — Tibber's GraphQL returns 200 with
   `errors` for rate limits and malformed queries too. Even with the fix it stays
   `UpdateFailed` (observed). The honest headline is "0 of 2 unambiguous auth statuses". The
   count of 0 is unaffected either way.
3. *Would `ConfigEntryAuthFailed` alone fix it?* No — `async_start_reauth` needs an
   `async_step_reauth` on the flow, and there are 0. The finding's proposed fix scope names
   both, correctly.

**Rule mapping.** `reauthentication-flow` (🥈 Silver), correct — the rule applies because
token authentication exists. The finder additionally leaves `test-before-setup` as *done*
with a pointer here; that is the right split: temporary failures do surface through the first
refresh, only auth is misclassified.

**Vote.** verify, severity medium as filed. Deciding number: **0 of 3 (0 of 2 unambiguous)
auth responses raise `ConfigEntryAuthFailed`; 0 `async_step_reauth`.**

---

### D10-03 — ERROR-with-traceback on every failed refresh · **verify (low, understated)**

**Metric (mine).** Records at level ≥ ERROR on logger `heatpump_optimizer` over three
consecutive `_async_update_data` calls whose Tibber fetch fails — taken three ways: the
finder's path, the production HTTP-401 path, and the production path plus real HA's own
`_async_refresh` UpdateFailed branch.

**Number.** stub path **4**; HTTP-401 path **4**; with real HA's base branch **5**. Null
control (`_fetch_tibber_prices` alone, three times) **1**. Reproduces
`error_records_over_3_failed_refreshes=4` and `..._direct=1`.

**Stub-vs-real.** *Real HA is worse by one.* Two separate divergences, both checked:
- The stub's `async_get_clientsession` raises `RuntimeError`, so the finder's number was
  taken on the "no HTTP session" path rather than a real Tibber failure. **Re-taken on the
  production 401 branch with a mocked session it is the same 4** — funcName sequence
  `_tibber_fetch_failed, _async_update_data, _async_update_data, _async_update_data` in both
  cases. Path-independent; not an artefact.
- The harness calls `_async_update_data` directly, so it omits real HA's base-class ERROR.
  Adding that branch verbatim gives **5**, not 4 — and the extra record fires once only,
  because real HA guards it on `last_update_success`. The finder's REPORT already says this.

**Attacks.**
1. *Perturbation re-derived* in scratch: `_LOGGER.error(` → `_LOGGER.debug(` in
   `_async_update_data`'s trailing `except Exception`. Observed **4 → 1** (and 5 → 2 with the
   real-HA branch), matching the finder's recorded 1.
2. *Claim wording.* "four ERROR records with tracebacks" — only **3 of the 4** carry
   `exc_info` (`v2_error_records_with_traceback_3_cycles=3`); the first is the latch's own
   ERROR. Cosmetic, does not move the number.
3. *Is the aggregate real?* A 24 h outage at the default 1800 s interval is 48 cycles →
   49 ERROR records, 48 of them with a traceback. The finder's "49 tracebacks" is off by one
   in its own favour; immaterial.

**Rule mapping.** `log-when-unavailable` (🥈 Silver), correct — and the finding is
**understated against the rule**, which says two things this integration breaks. The rule's
coordinator example is *"the only thing you need to do is raise `UpdateFailed`"* and it
carries an explicit `:::info Logging should happen at info level`. The home-grown
`_tibber_fetch_failed` latch is therefore off-rule twice over (wrong level, and duplicating
machinery the base class already has) even before the outer handler re-logs. That argues the
severity is at the top of "low" rather than the bottom; I do not push it to medium because
the consequence is log noise, not behaviour.

**Vote.** verify, severity low. Deciding number: **4 ERROR records over 3 failed cycles on
the production 401 path (5 in real HA), against 1 from the fetch alone.**

---

### D10-04 — service actions swallow operational failures · **verify (low), scope narrowed**

**Metric (mine).** Of `run_optimization`, `simulate_plan` and `restore_learned_snapshot`
called through the registered handlers **under real HA's `async_call` gate** — `blocking=True`
throughout, `return_response=True` for the two response handlers — how many return instead of
raising. Plus a source-level count of `raise HomeAssistantError` sites.

**Number.** `v2_service_failures_silent_real_call_semantics=3`;
`v2_raise_HomeAssistantError_sites=0` against `v2_raise_ServiceValidationError_sites=14`.
Reproduces `service_failure_paths_returning_silently=3`.

Outcomes on a coordinator with no prices/plan/snapshot:
```
run_optimization          -> returned None
simulate_plan             -> returned {'results': {'test_entry': {'error': 'no_plan', ...}}}
restore_learned_snapshot  -> returned {'restored': []}
```

**Stub-vs-real.** *Stub more permissive; the number survives anyway.* This is the one place
the stub genuinely hid something: `tests/harness.py:FakeServices.async_call` ignores
`supports_response` entirely, so the finder's call — `async_call(DOMAIN, "simulate_plan", …)`
with the default `return_response=False` — returned a dict. Under real HA's gate
(`core.py:2694`) that same call **raises `ServiceValidationError`**, because the handler is
registered `SupportsResponse.ONLY`. I re-implemented the gate and re-drove all three with the
call shape a UI or automation caller actually uses; the count is still **3**.

**Attacks.**
1. *Does the rule cover all three?* **Only cleanly for one.** `action-exceptions` (🥈 Silver)
   says to raise `HomeAssistantError` "when the problem is caused by an error in the service
   action itself". `run_optimization` returns `None` after a WARNING — unambiguous. The other
   two return a documented response dict that names the failure (`{'error': 'no_plan'}`,
   `{'restored': []}`); the rule does not say a `ServiceResponse` action must raise rather
   than report in its response, and the finder itself concedes "arguably a response
   contract". So the headline **3 is 1 unambiguous + 2 arguable**.
2. *Is the raise reachable where the finding says?* Yes. `async_run_optimization` wraps its
   body in `except Exception` (coordinator.py), so a raise inside it never reaches the
   caller — the raise has to be in the handler. The finder states this and its perturbation
   (3 → 2 for a handler raise; 3 → 3 for a coordinator raise) encodes it.
3. *Is "no HomeAssistantError anywhere" true?* Independently: **0** `raise
   HomeAssistantError` sites across all 45 modules, 14 `raise ServiceValidationError`.

**Rule mapping.** `action-exceptions`, correct rule, partial coverage of the count.

**Vote.** verify, severity low as filed, with the scope note that the defensible core is
`run_optimization` (1 of 3) plus the 0 `HomeAssistantError` sites. Deciding number:
**3 silent returns under real-HA call semantics; 0 `raise HomeAssistantError` sites.**

---

### D10-05 — two buttons stay available after a failed refresh · **verify (low)**

**Metric (mine).** Two independent definitions. (a) Entities from the five real platform
`async_setup_entry`s whose `.available` is True while `coordinator.last_update_success` is
False. (b) *Stub-free:* `available()` overrides in the five platform files whose source never
mentions `super()`.

**Number.** (a) **2** of 65 — `button.ForceOptimizationButton`
(`test_entry_force_optimization`) and `button.SystemIdentificationButton`
(`test_entry_system_identification`). (b) **2** — the same two classes. Reproduces
`entities_available_after_failed_refresh=2` and `entities=65`.

**Stub-vs-real.** *Same.* `hastub`'s `CoordinatorEntity.available` returns
`bool(coordinator.last_update_success)`; real HA's returns `self.coordinator.last_update_success`
(`update_coordinator.py:515-518`). Semantically identical, and the stub file's own docstring
says it was written to make exactly this conjunction testable. The AST cross-check (b) removes
the stub from the loop entirely and lands on the same two classes.

**Attacks.**
1. *Perturbation re-derived* in scratch: `return super().available and not …` on both
   buttons. Observed **2 → 0** on both metrics, matching the finder.
2. *Is the rest of the codebase clean?* Yes — every `available` override in `sensor.py`
   (7 of them) ANDs `super().available`. The two buttons are the only outliers.
3. *Is the severity earned?* Low is right. Pressing Optimize now during an outage runs the
   solver on stale prices; it misleads, it does not damage.

**Rule mapping.** `entity-unavailable` (🥈 Silver), exactly on point: *"If there is any extra
availability logic needed, be sure to incorporate the `super().available` value."* No
exceptions clause applies (the media-player standby exception is unrelated).

**Vote.** verify, severity low. Deciding number: **2, from a metric that never touches the
stub.**

---

### D10-06 — services registered in `async_setup_entry` · **verify (low)**

**Metric (mine).** AST count of `*.async_register` calls whose enclosing function is
`async_setup_entry` in `__init__.py`, and count of `async_setup` definitions.

**Number.** `v2_services_registered_in_setup_entry=11`, `v2_async_setup_defs=0`. Reproduces
both.

**Stub-vs-real.** *Not applicable — no stub in the measurement.* The number is pure AST over
production source. The only stub-dependent part of the surrounding story is the lifecycle
drive (`11 → 0` services after unload), which `FakeServices` implements as a real registry
with real removal; I re-read it and it is honest. The rule's consequence also holds in real
HA: an unloaded entry means the services are absent, so `core.py:2674` raises
`ServiceNotFound` rather than the rule's preferred `ServiceValidationError("Entry not
loaded")`.

**Attacks.**
1. *Is the removal loop actually correct?* Yes, and better than most — it asks the registry
   rather than keeping a hand-written tuple, with a comment recording two past drifts. That
   makes the finding purely about *where* registration happens, not a leak.
2. *Severity.* Hygiene/low is earned: the visible cost is automation validation against an
   unloaded entry, not a runtime fault.

**Rule mapping.** `action-setup` (🥉 Bronze), correct, and the rule has no exceptions. Note
the fix interacts with D10-08: the rule's example resolves the entry via
`entry.runtime_data`, so `action-setup` and `runtime-data` are cheapest fixed together.

**Vote.** verify, severity low. Deciding number: **11 registrations inside
`async_setup_entry`, 0 `async_setup`.**

---

### D10-07 — no `PARALLEL_UPDATES` · **verify (low)**

**Metric.** Module-level `PARALLEL_UPDATES` assignments per platform file.
**Number (mine).** 0 in each of `sensor.py`, `binary_sensor.py`, `button.py`, `switch.py`,
`climate.py`. Reproduces `platforms_declaring_parallel_updates=0`.
**Attacks.** The rule (🥈 `parallel-updates`) has no exceptions and explicitly covers the
coordinator case: `0` for the read-only platforms, a considered number for the platforms with
actions. The finder's `quality_scale.yaml` comment prescribes exactly that split. Nothing here
depends on the stub.
**Vote.** verify, low.

---

### D10-08 — `hass.data[DOMAIN]`, no `entity.py` · **verify (low)**

**Metric.** Regex counts of `runtime_data` and the `hass.data[DOMAIN]` family; count of
`CoordinatorEntity` base classes outside `entity.py`.
**Number (mine).** `runtime_data` **0**; `entity.py` absent; `CoordinatorEntity` referenced in
all five platform files (2 each: import + base class). My looser `hass.data` regex gives 25
where the finder's tighter `hass\.data\[DOMAIN\]|hass\.data\.get\(DOMAIN|hass\.data\.setdefault\(DOMAIN`
gives 24 — the finder's pattern is the correct one; not a discrepancy.
**Attacks.** `runtime-data` (🥉) needs HA ≥ 2024.4 and the `hacs.json` floor is 2024.1.0, which
the finder records honestly in the yaml comment — the rule is unmet but the fix carries a
floor bump. `common-modules` (🥉) is met for `coordinator.py` and unmet for `entity.py`;
correct rules, correctly split.
**Vote.** verify, low.

---

### D10-09 — untranslated service exceptions · **verify (low)**

**Metric.** Regex count of `raise (ServiceValidationError|HomeAssistantError)(` sites carrying
`translation_key`, over all such raises.
**Number (mine).** raises **14** (13 in `__init__.py`, 1 in `coordinator.py`), with
`translation_key` **0**; no `exceptions` block in `strings.json`. Reproduces
`exception_raises_with_translation_key=0`.
**Attacks.** One internal inconsistency to flag to the judge: `quality_scale.yaml` says *"All
15 service exceptions"*; the harness table, `check_rules.out` line 51 and the finding all say
14. My count is **14**. The yaml comment is the outlier.
**Rule mapping.** `exception-translations` (🥇 Gold), correct; the API predates the floor, as
the finder says.
**Vote.** verify, low.

---

### D10-10 — icons in code, no `icons.json` · **verify (low)**

**Metric.** `_attr_icon =` assignments across the five platform files; existence of `icons.json`.
**Number (mine).** 55 + 4 + 4 + 1 + 0 = **64**; `icons.json` absent. Reproduces `icons_in_code=64`.
**Attacks.** The rule (🥇 `icon-translations`) carries an `:::info` that entities whose context
matches their device class should *not* get a custom icon at all — which means part of the 64
should disappear rather than move to `icons.json`, and that overlaps D10-15. The finding is
correct as filed; the fixer should read the two together.
**Vote.** verify, low.

---

### D10-11 — no diagnostics platform · **verify (low)**

**Metric.** Existence of `diagnostics.py`; count of `async_get_config_entry_diagnostics` defs.
**Number (mine).** file absent, **0** defs. Reproduces `diagnostics_defs=0`.
**Rule mapping.** `diagnostics` (🥇 Gold), correct. Pure existence check, no stub involvement.
**Vote.** verify, low.

---

### D10-12 — documentation gaps · **verify (low)**

**Metric.** Case-insensitive matches over `README.md`, `docs/*.md`, `DISCLAIMER.md`.
**Number (mine).** removal/uninstall **0**, "known limitations" **0**, "blueprint" **0**,
"supported devices" **0**. Reproduces `docs_removal_instructions=0`,
`docs_known_limitations_sections=0`, `docs_blueprints=0`.
**Attacks.** `docs-examples` (🥇) is specifically about *blueprints* uploaded to the blueprint
folder or exchange, and explicitly says documentation pages must not substitute for them — so
the finding's "0 automation examples" is broader than the rule, though the blueprint count of
0 carries it on its own. `docs-supported-devices` (🥇) is a judgement call for an integration
that drives the user's own HA entities plus one MQTT bridge; the finder marks it `todo` rather
than `exempt`, which I read as defensible given the ECL110 hardware surface.
`docs-removal-instructions` (🥉 Bronze) is unambiguous.
**Vote.** verify, low.

---

### D10-13 — `mypy --strict` errors · **weaken (low; number inflated ~31 % by the stub)**

**Metric (finder).** Count of `error:` lines under `custom_components/`, python-version 3.13,
`MYPYPATH=tests/hastub`.
**Metric (mine).** The same count, **split by whether the error can exist against real Home
Assistant**: an error is stub-attributable when it is `attr-defined` on a class the stub
truncates (`HomeAssistant`, `ServiceCall`, `ConfigEntry`, the flow classes) or
`no-untyped-call` naming a symbol that only `tests/hastub` defines untyped
(`dt_util.now`/`utcnow`/`parse_datetime`, the coordinator's `async_request_refresh` /
`async_update_listeners`, the selectors, `async_get_clientsession`, `Store`, …).

**Number.** Re-ran mypy independently (`MYPYPATH=tests/hastub PYTHONPATH=/tmp/d10-cov`,
`--strict --python-version 3.13 --no-incremental`): **722 errors**, exactly reproducing the
finder, with the same code histogram (`no-untyped-call` 227, `type-arg` 111, `no-untyped-def`
106, `attr-defined` 90, `no-any-return` 79, `union-attr` 25).

**The split:** `attr-defined` attributable to the stub **87**, `no-untyped-call` attributable
to the stub **138**, union **225 of 722 = 31.2 %**. Integration-internal floor: **497**.

The unambiguous cases are stark — 27 × `"HomeAssistant" has no attribute "data"`, 14 ×
`"ServiceCall" has no attribute "data"`, 13 × `"HomeAssistant" has no attribute "services"`,
11 × `… "config_entries"`, 9 × the flow classes have no `hass`, 67 × `Call to untyped
function "now"`. Real HA ships `py.typed` and every one of those attributes and signatures;
none of these 225 errors can occur against the real package.

**Attacks.**
1. The finder's REPORT says `no-untyped-call` is "partly the untyped stub, so the true count
   against real Home Assistant is lower but not near zero" — directionally right, but the
   headline that entered the finding, the yaml and the tier table is **722**, unqualified. My
   number puts the honest figure at **497**, with 225 measured as measurement artefact.
2. The verdict is unaffected: `strict-typing` (🥇 Platinum) is `todo` at 497 as surely as at
   722, and `no-untyped-def` (106) and `type-arg` (111) are wholly integration-internal.
3. This is a stub-driven measurement in a second sense: the stub *cannot* be fixed to remove
   these without annotating `tests/hastub`, so any re-take under a different stub will move
   the number. Tolerance "exact" is only meaningful against this stub.

**Vote.** **weaken** — severity stays low, but the number should be recorded as
**497 integration-internal errors (722 measured against `tests/hastub`, 225 of them stub
artefacts, 31.2 %)**. Deciding number: **225 of 722**.

---

### D10-14 — test coverage · **verify on the config-flow half; unresolved on the percentages**

**Metric (config-flow half, mine).** Count of suite call sites that drive
`HeatPumpOptimizerConfigFlow.async_step_user` with a non-`None` `user_input`.
**Number.** **0.** The suite's only call is `tests/entities.py:3470`,
`asyncio.run(_fresh_flow().async_step_user(None))` — it renders the form and never submits it.
Reproduces `tests_driving_async_step_user_with_input=0`. (The suite drives the *options* flow
heavily — `async_step_entities`, `async_step_thermal_model`, `async_step_building` — which is
why `config_flow.py` still reaches 86.4 %.)

**Test-gap mutation, as the brief requires.** In the production file
`custom_components/heatpump_optimizer/config_flow.py`, `async_step_user` (line ~960):
change `if verdict == "invalid_auth":` to `if verdict == "cannot_connect":`. The whole
`user_input is not None` branch is unreached by the suite, so no gate notices; the user
submitting a bad Tibber token would be told "cannot connect". The mutation lives in a
production file, not a test file — the gap stands.

**Attacks / limits.** The three percentages (88.4 % overall, 20 of 45 modules ≥ 95 %,
`config_flow.py` 86.4 %) come from `coverage_suite.sh`, which the box constraint forbids me
from re-running; I read them from the finder's `coverage/coverage.json` via the checker and
they reproduce as *stored values*, not as *re-measurements*. I therefore record the
percentages as **not independently re-taken by this seat**. Two notes for the judge: (a) the
rule `test-coverage` (🥈) assumes an HA-style pytest suite, and this integration's "tests" are
end-to-end scripts, so counting their coverage is a generous proxy that favours the
integration; (b) `config-flow-test-coverage` (🥉 Bronze) demands **100 %** and its warning box
demands specifically a test that the flow refuses a second entry — which does not exist, tying
back to D10-01.

**Vote.** **verify** the config-flow half (deciding number: **0 suite submissions of
`async_step_user`**, plus the named production mutation); **unresolved** on the three
coverage percentages, which need a quiet-box re-run of `coverage_suite.sh`.

---

### D10-15 — declarative metadata gaps · **weaken (low → the fix is wrong and half maps to no rule)**

**Metric (finder).** Count of sensors whose native unit maps to a `SensorDeviceClass` but
whose `_attr_device_class` is None; count of `DeviceInfo` with `entry_type`.
**Number.** `sensors_with_unit_but_no_device_class=5` reproduces; `device_entry_type_service=0`
reproduces.

**Attacks — three, two of which bite.**
1. *Headline ≠ claim.* The RESULT is **5**; the claim is **2**. The finder itself exempts the
   three °C sensors (`ecl110_displace`, `ecl110_effective_displace`, `prediction_accuracy`) as
   deltas where TEMPERATURE would convert wrongly. So the evidence number the register would
   carry overstates the claim by 2.5×. The metric definition and the claim are not the same
   quantity.
2. *The proposed fix is invalid in real Home Assistant.* Both flagged kWh sensors declare
   `_attr_state_class = SensorStateClass.MEASUREMENT` (`sensor.py`: `PVSurplusSensor`, and the
   DHW heavy-day class). Real HA's `DEVICE_CLASS_STATE_CLASSES`
   (`components/sensor/const.py:600-603`) permits `SensorDeviceClass.ENERGY` **only** with
   `TOTAL` or `TOTAL_INCREASING`, and `components/sensor/__init__.py:558-582` logs a
   per-entity WARNING — *"is using state class 'measurement' which is impossible considering
   device class ('energy')"* — for the combination. Applying the finding's fix scope verbatim
   ("`_attr_device_class = SensorDeviceClass.ENERGY` on DHWHeavyDayDemand", and its
   perturbation does exactly that to move 5 → 4) trades a missing device class for a warning
   in every user's log. And the semantics say the same thing: one sensor is a *forecast* of
   surplus kWh, the other a *p90 statistic* over learned draws — neither is a meter total, so
   neither belongs in the Energy dashboard. On the rule's own logic these two are closer to
   the three °C deltas the finder already exempted than to a genuine ENERGY entity.
3. *The `entry_type` half maps to no rule.* The rule it sits under is `devices` (🥇), which
   says only that device information "should be as complete as possible" and never mentions
   `entry_type`; the finder's own `quality_scale.yaml` scores `devices: done` and relegates
   the gap to a comment. So half of D10-15 is a best-practice nit with no checklist rule
   behind it. (`manufacturer='Custom'` likewise.)

**Rule mapping.** `entity-device-class` (🥇) for the first half — correct rule, but the two
instances are contestable for the reason in attack 2. `devices` for the second half — the rule
does not carry the requirement; **no rule violated**.

**Vote.** **weaken.** Severity low stands, but the finding should be recorded as: metric
number **5**, claim number **2**, of which **0 are safely fixable as proposed** without also
changing the state class, and the `entry_type`/`manufacturer` half attaches to **no
checklist rule**. Deciding number: **`SensorDeviceClass.ENERGY` admits exactly
{TOTAL, TOTAL_INCREASING}; both flagged sensors declare MEASUREMENT** (real HA 2024.6.0,
`components/sensor/const.py:600`).

---

## Summary

| finding | vote | deciding number |
|---|---|---|
| D10-01 | verify (medium) | 0 guards; real HA creates the second entry regardless |
| D10-02 | verify (medium) | 0 of 3 (0 of 2 unambiguous); 0 `async_step_reauth`; perturbation 0 → 2 |
| D10-03 | verify (low) | 4 on the production 401 path (5 in real HA) vs 1 from the fetch alone |
| D10-04 | verify (low), scope 1 of 3 clean | 3 under real-HA call semantics; 0 `raise HomeAssistantError` |
| D10-05 | verify (low) | 2, from a stub-free AST metric; perturbation 2 → 0 |
| D10-06 | verify (low) | 11 in `async_setup_entry`, 0 `async_setup` |
| D10-07 | verify (low) | 0 of 5 platforms |
| D10-08 | verify (low) | `runtime_data` 0; no `entity.py`; 5 base classes in platform files |
| D10-09 | verify (low) | 14 raises, 0 with `translation_key` (yaml's "15" is the outlier) |
| D10-10 | verify (low) | 64 `_attr_icon`, no `icons.json` |
| D10-11 | verify (low) | 0 diagnostics defs |
| D10-12 | verify (low) | 0/0/0/0 across README, docs/, DISCLAIMER |
| D10-13 | **weaken** | 225 of 722 (31.2 %) are `tests/hastub` artefacts; floor 497 |
| D10-14 | verify (config-flow half); **unresolved** (percentages) | 0 suite submissions of `async_step_user`; coverage not re-run under the box constraint |
| D10-15 | **weaken** | ENERGY admits only TOTAL/TOTAL_INCREASING; both sensors are MEASUREMENT; `entry_type` maps to no rule |

**Stub verdict overall.** `tests/hastub` did **not** manufacture any of the six behavioural
findings. Where it diverges from real Home Assistant it does so in the integration's favour
(D10-02 cannot represent `ConfigEntryAuthFailed` at all; D10-03 omits the base class's extra
ERROR) or neutrally (D10-01, D10-05, D10-06). The one place it was genuinely more permissive
than real HA — `FakeServices` ignoring `supports_response`, which let the finder's
`simulate_plan` call succeed where real HA raises — does not change D10-04's count when the
call is re-driven correctly. The stub's real distortion in this dimension is in **D10-13**,
where being untyped inflates the headline by 31 %.
