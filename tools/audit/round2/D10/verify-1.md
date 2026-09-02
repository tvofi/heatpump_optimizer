# D10 verifier seat 1 — round 2

Baseline `c398fc84eec25fc44b60d74aae05b9a2da205884`, export root
`/Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/audit-r2-baseline`.
Interpreter `tvofi-claude/.venv/bin/python` (3.13.1), `PYTHONPATH=tests/hastub`,
run from the export root. Machine: Apple M1, 8 GB, macOS Darwin 25.6.0.

Two harnesses, both counts-only and therefore contention-immune:

1. **The finder's**, re-run once exactly as its header says:
   `PYTHONPATH=tests/hastub D10_COV_PREFIX=/tmp/d10-cov python tools/audit/round2/D10/check_rules.py`
   → `/tmp/verify-D10-1/check_rules.rerun.out`.
2. **Mine**, written for this panel with its own metric definitions:
   `/tmp/verify-D10-1/verify_d10.py`, output `/tmp/verify-D10-1/verify.out`,
   RESULT lines `/tmp/verify-D10-1/verify.results.txt`. It re-derives every
   finding from AST walks and stub-driven drives of the named production symbol;
   no number is copied from `check_rules.py`.

## Harness re-run: reproduced exactly

`diff check_rules.out /tmp/verify-D10-1/check_rules.rerun.out` differs in **three
places only**, none of them a count:

| line | recorded | my re-run |
|---|---|---|
| `mypy_wall_s` | 8.5 s | 4.9 s |
| `load1` | 6.92 | 1.56 |
| `swapins_delta_during_run` | 143 | 16 |

Plus six stray stdout lines the production loggers emit (the finder's capture
filtered them). **Every one of the 54 rule rows and all 43 headline counts
reproduce bit-for-bit**, including `mypy_strict_errors=722`, its by-code table
(`no-untyped-call=227, type-arg=111, no-untyped-def=106, attr-defined=90,
no-any-return=79, union-attr=25`) and its by-file table. `done=27 todo=21
exempt=6`. `thread_factor=1.00` on both runs.

The finder took its numbers at `load1=6.92`, above the judge's 1.5 bar. That bar
governs timing and memory RESULTs; every headline here is a count, and I re-took
all of them at `load1` 1.56–2.02 with identical values, so the contention
objection is closed rather than merely waved at.

## Box constraint

I ran no coverage suite, no `tests/run.sh`, no solver, and mypy exactly once —
inside the single `check_rules.py` re-run. D10-13 and D10-14 are judged from the
finder's recorded artefacts, as instructed; for D10-14 I re-derived the
percentage from `coverage/coverage.json` arithmetically rather than re-measuring.

---

## D10-01 — no duplicate-entry guard · **verify** (medium)

**My metric.** (a) AST count of calls to any member of HA's duplicate-entry API
(`async_set_unique_id`, `_abort_if_unique_id_configured`,
`_abort_if_unique_id_mismatch`, `_async_abort_entries_match`,
`_async_current_entries`, `_async_in_progress`, `async_abort`) anywhere in the
**package**, not just `config_flow.py`; (b) behavioural — with one entry already
in `hass.config_entries`, the number of `abort` results returned by
`async_step_user` across its two entry points (show-form and submit).

```
RESULT v01_guard_api_calls_in_config_flow=0
RESULT v01_guard_api_calls_in_package=0
RESULT v01_manifest_single_config_entry=0
RESULT v01_strings_abort_already_configured=1
RESULT v01_abort_results_with_one_existing_entry_of_2=0
NOTE  async_step_user(existing=1, submit=False) -> type=form id=user
NOTE  async_step_user(existing=1, submit=True)  -> type=form id=temperature
NOTE  null control: existing=0, submit=True     -> type=form id=temperature
```

**Attacks.**

- *Is the grep the whole story?* I widened it from `config_flow.py` to all 45
  modules and from a regex to an AST call-name match. Still 0. `strings.json`
  carries `config.abort.already_configured` (=1) with nothing that can reach it.
- *Is the path reachable outside the stub?* The guard would live at the top of
  `async_step_user`, which is HA's own entry point; nothing about `FakeHass`
  gates it. The null control (0 existing entries) returns the *identical*
  result, so the absent guard is the only variable.
- *Is medium earned by consequence?* Two independent levers, both measured:
  `v01_hardpinned_entity_ids_without_entry_id=5` — every platform hard-assigns
  `self.entity_id = "<domain>.heat_pump_optimizer_<key>"` with no entry
  discriminator (`sensor.py:216`, `binary_sensor.py:69`, `button.py:65`,
  `switch.py:53`, `climate.py:102`) while `_attr_unique_id` *does* carry
  `entry.entry_id`, so a second entry gets registry `_2` suffixes; and
  `v16_service_loops_over_every_coordinator=5` — five handlers iterate
  `hass.data[DOMAIN]` and apply to every coordinator, so `set_mode`,
  `apply_schedule` and friends silently hit both entries, and both solve every
  interval against the same heat pump switch.
- *One stated consequence does not survive.* The finder writes that the second
  entry breaks "the card's id-suffix discovery". It does not: the card resolves
  by `id.endsWith(suffix)` (`www/heatpump-optimizer-card.js:3679`) and its
  defaults are the un-suffixed ids (`:835-837`), so it keeps resolving entry #1
  and simply orphans the `_2` set. The finding does not rest on this; the other
  two levers carry it.

**Deciding number: `v01_abort_results_with_one_existing_entry_of_2=0`** against a
Bronze rule (`unique-config-entry`). Vote **verify**, severity **medium**.

---

## D10-02 — rejected token reported as transient · **verify** (medium)

**My metric.** Of **five** Tibber failure shapes driven through
`_fetch_tibber_prices` behind my own fake session (401, 403, `200 + {"errors":
[{"message": "invalid token"}]}`, 500, `200` with no homes), the exception class
actually raised for each. The finder used three; I added 500 and empty-homes so
the *contrast* an operator needs — "your token is dead" vs "Tibber is down" — is
in the same table.

```
RESULT v02_ConfigEntryAuthFailed_names_in_package=0
RESULT v02_async_step_reauth_defs=0
RESULT v02_auth_cases_raising_ConfigEntryAuthFailed_of_3=0
RESULT v02_all_5_cases_raising_UpdateFailed=5
NOTE http_401 -> UpdateFailed      NOTE http_500        -> UpdateFailed
NOTE http_403 -> UpdateFailed      NOTE http_200_no_homes -> UpdateFailed
NOTE errors_invalid_token -> UpdateFailed
```

All five collapse to one class. There is no signal to distinguish them.

**Attacks.**

- *Is the stub hiding a positive?* `tests/hastub/homeassistant/exceptions.py`
  has no `ConfigEntryAuthFailed` (`v02_stub_has_ConfigEntryAuthFailed=0`), so I
  cannot demonstrate the fixed behaviour here — but the negative does not depend
  on the stub: the package contains **zero** textual references to the symbol
  (`v02_ConfigEntryAuthFailed_names_in_package=0`), so no import path could
  raise it however `hass` is built.
- *Is the outer handler really in the way?* Yes, and worse than reported.
  `_tibber_fetch_failed` raises `UpdateFailed` from *inside* the `try:` block, so
  the trailing `except Exception` at `coordinator.py:5438` catches the
  integration's own signal and re-wraps it. Measured:
  **`v02_outage_cycles_after_one_failed_fetch=2`** — one failed fetch burns two
  outage cycles, and the message that reaches the log is
  `"Unexpected error fetching prices: Tibber API error: 401"`. The finder's
  perturbation note ("the fix must re-raise ahead of it") shows it saw this; the
  double-count is an extra fact for the fixer.
- *Severity.* A revoked token produces "retrying setup" and unavailable entities
  forever, with no reauth repair (`v02_async_step_reauth_defs=0`) and no
  reconfigure path except the options flow. `ConfigEntryAuthFailed` and
  `async_step_reauth` both predate the 2024.1.0 floor. Medium is earned.

**Deciding number: `v02_all_5_cases_raising_UpdateFailed=5`.** Vote **verify**,
severity **medium**.

---

## D10-03 — four ERRORs over three failed refreshes · **verify** (low)

**My metric.** Records at `levelno >= ERROR` captured by my own handler attached
to the `heatpump_optimizer` logger (the package is imported as
`heatpump_optimizer.*` here, so that is where the production `_LOGGER` hangs),
over *n* consecutive `_async_update_data` calls whose Tibber fetch fails — plus,
which I added, the **distinct call sites** and how many carry a traceback, and
the same number at n = 1, 3 and 10 so the *shape* is visible rather than one
point.

```
RESULT v03_error_records_3_failed_refreshes=4       <- matches the finder
RESULT v03_error_records_1_failed_refresh=2
RESULT v03_error_records_10_failed_refreshes=11
RESULT v03_error_records_with_traceback=3
RESULT v03_distinct_error_call_sites=2
RESULT v03_null_control_error_records_3_direct_fetches=1   <- null control holds
NOTE ERROR coordinator.py:5451 exc_info=False  (the latch, once)
NOTE ERROR coordinator.py:4445 exc_info=True   (x3, once per cycle)
```

The law is **n + 1**: the latch fires once, the outer handler fires every cycle.
That is exactly the finder's mechanism, measured across three points rather than
asserted from one.

**Attacks.**

- *Null control.* Driving `_fetch_tibber_prices` alone three times gives 1 ERROR.
  The latch works; the surplus is entirely the outer handler.
- *Stub artefact?* No. `coordinator.py:4445` is an unconditional
  `_LOGGER.error(..., exc_info=True)` in production code on the path every
  refresh takes. Real HA adds `DataUpdateCoordinator`'s own record on top, so the
  real-world number is 4 or more, never fewer.
- *Severity.* At the default 1800 s interval (`update_interval_default_s=1800`,
  confirmed in the re-run) a day-long Tibber outage writes 49 tracebacks. Noise,
  not damage. Low is right — and it is a hole in a *previous* round's fix: the
  latch's own docstring credits "D10-09" from an earlier round.

**Deciding number: `v03_error_records_10_failed_refreshes=11` vs a null control
of 1.** Vote **verify**, severity **low**.

---

## D10-04 — service failures returned, not raised · **weaken** (low; claim scope)

**My metric.** All 11 services registered by the real `async_setup_entry`, then
the three degraded ones called *through the registry* (`hass.services.async_call`,
schema and all) on a coordinator with no prices, no plan and no snapshot,
recording raise-vs-return **and** whether a returned value names the failure —
the axis the finder's binary count drops.

```
RESULT v04_services_registered=11
RESULT v04_raise_ServiceValidationError_sites=14
RESULT v04_raise_HomeAssistantError_sites=0
RESULT v04_degraded_services_returning_instead_of_raising_of_3=3   <- matches
RESULT v04_degraded_services_whose_return_names_the_failure_of_3=2 <- my addition
NOTE run_optimization          -> returned null
NOTE simulate_plan             -> returned {"results": {"test_entry": {"error": "no_plan", ...}}}
NOTE restore_learned_snapshot  -> returned {"restored": []}
```

**Attacks.**

- *Is the count right?* Yes — 3 of 3 return. The rule (`action-exceptions`) is
  unmet 3/3, because a response dict is not an exception.
- *Is the severity earned by consequence?* Only for one of the three, and the
  registration table decides it. `simulate_plan` is registered
  `supports_response=SupportsResponse.ONLY` and `restore_learned_snapshot`
  `SupportsResponse.OPTIONAL` (`__init__.py:864-869`, `:906-911`): both have a
  response channel and both use it to name the failure, so an automation with
  `response_variable` can branch on `error == "no_plan"` or `restored == []`.
  `run_optimization` is registered with **no** `supports_response`
  (`__init__.py:846-851`) — it has no channel but an exception, and returns
  `None` after a WARNING. It is the only one where a user genuinely cannot tell.
- *Is the fix where the finder says?* Yes — `async_run_optimization` wraps its
  own body in `except Exception` (`coordinator.py:5536`), so the raise has to go
  in the handler, as the finder's perturbation notes.

The finding is true but its headline over-counts the harm three-fold.

**Deciding number:
`v04_degraded_services_whose_return_names_the_failure_of_3=2`.** Vote
**weaken(low)** — severity stays at the floor; the *claim* should read "one
service (`run_optimization`) fails silently with no response channel; two report
failure inside a documented response contract but still do not raise".

---

## D10-05 — two buttons available after a failed refresh · **verify** (low)

**My metric.** Two independent measurements that must agree: (a) behavioural —
all 65 entities built by the five real platform `async_setup_entry`s, with
`coordinator.last_update_success = False`, counting `.available is True`; (b)
static — AST count of `available` property definitions in the platform files
whose source never mentions `super().available`.

```
RESULT v05_entities_collected=65
RESULT v05_entities_available_while_last_update_success_false=2   <- matches
NOTE  available: ForceOptimizationButton, SystemIdentificationButton
RESULT v05_available_properties_without_super_available=2         <- independent, agrees
NOTE  no-super sites: button.py:82:ForceOptimizationButton, button.py:110:SystemIdentificationButton
RESULT v05_entities_available_when_refresh_succeeds=42
```

Both routes name the same two entities and the same two source lines. Every
`available` override in `sensor.py` (11 of them, including the three mixins at
`:249`, `:270`, `:303`) does `bool(super().available and …)`; only `button.py`
does not.

**Attacks.**

- *Grid artefact?* No grid — 65 entities, exhaustive, one cell each.
- *Consequence.* `ForceOptimizationButton.async_press` calls
  `coordinator.async_force_optimization()`, which during an outage fails the
  same way the refresh did and (per D10-03) adds another traceback. So the
  button looks live, does nothing useful, and pollutes the log. Real but minor.
- *Is the rule's intent met another way?* No. `entity-unavailable` (Silver) wants
  the entity to go unavailable when the coordinator's data is stale; overriding
  `available` without `super()` is precisely how that is lost, and the codebase's
  own 11 other overrides show the house idiom.

**Deciding number: `v05_entities_available_while_last_update_success_false=2`,
corroborated by a static `2`.** Vote **verify**, severity **low**.

---

## D10-06 — services registered in `async_setup_entry` · **verify** (low)

**My metric.** AST: for every `hass.services.async_register` Call in
`__init__.py`, the *nearest enclosing function* via a parent map (not a regex
window); plus module-level `async_setup` defs; plus a behavioural check the
finder did not run — how many services survive the last entry's unload.

```
RESULT v06_async_register_calls_total=11
RESULT v06_async_register_calls_in_async_setup_entry=11   <- matches
RESULT v06_module_level_async_setup_defs=0
RESULT v06_async_remove_call_sites=1
RESULT v06_services_left_after_last_unload=0              <- my addition
```

**Attacks.**

- *Is the enclosing-function attribution right?* All 11 resolve to
  `async_setup_entry` by parent walk, none to a nested helper.
- *Does the consequence actually occur?* Yes, and I measured it rather than
  inferring it: after `async_unload_entry` on the only entry, the domain's
  service registry is empty. An automation naming `heatpump_optimizer.set_mode`
  then fails validation with "service not found" instead of the rule's intended
  `ServiceValidationError` saying the entry is not loaded.
- *Severity.* Confined to the unloaded / failed-setup window. Hygiene, low.

**Deciding number: `v06_services_left_after_last_unload=0` with
`v06_module_level_async_setup_defs=0`.** Vote **verify**, severity **low**.

---

## D10-07 — no `PARALLEL_UPDATES` · **verify** (low)

**My metric.** Module-level `PARALLEL_UPDATES` assignment, checked against the
platform set the integration **actually forwards to** (`PLATFORM_LIST` in
`__init__.py:82-86`: SENSOR, BINARY_SENSOR, BUTTON, CLIMATE, SWITCH), rather
than against a hand-listed set of files.

```
RESULT v07_platform_files_declaring_PARALLEL_UPDATES=0     <- matches
RESULT v07_platform_files_forwarded_by_PLATFORM_LIST=5
RESULT v07_platforms_with_outbound_writes=3
```

**Attacks.**

- *Is the rule really unmet, or exempt?* `parallel-updates` (Silver) asks for an
  explicit declaration; it is not satisfied by "the default happens to be fine".
  Unmet.
- *Is the severity earned?* No functional harm: one coordinator, no per-entity
  polling, no outbound device protocol that could be flooded. Three of the five
  do write outbound (button, switch, climate) and would take `1`; the two
  read-only ones take `0`. Correctly classed hygiene at low.

**Deciding number: `v07_platform_files_declaring_PARALLEL_UPDATES=0` of 5
forwarded.** Vote **verify**, severity **low**.

---

## D10-08 — `hass.data[DOMAIN]`, base classes outside `entity.py` · **verify** (low)

**My metric.** AST rather than regex: `hass.data[…]` Subscript nodes plus
`hass.data.get(…)` / `hass.data.setdefault(…)` Calls, counted with their key;
and ClassDefs anywhere in the package with `CoordinatorEntity` among their bases.

```
RESULT v08_runtime_data_refs=0                     <- matches
RESULT v08_hass_data_ast_nodes=27                  <- my definition
RESULT v08_files_touching_hass_data=7              <- matches the finder's 7 files
RESULT v08_entity_py_exists=0
RESULT v08_direct_CoordinatorEntity_subclasses=5   <- matches
```

**The two definitions reconcile exactly.** My 27 counts every `hass.data` touch;
24 of them are keyed on `DOMAIN`, which is the finder's regex. The three extras
are all in `frontend.py`: `hass.data.get("lovelace")` and two touches of a
private `_FLAG` key. So the finder's **24** is my 27 minus three non-DOMAIN
touches — same fact, narrower scope, no discrepancy.

**Attacks.**

- *Is `runtime_data` actually available?* No — it needs HA ≥ 2024.4 and
  `hacs.json` floors at 2024.1.0. The finder says so and does not pretend the
  fix is free. The `entity.py` half *is* floor-neutral and unmet: no `entity.py`
  exists and all five bases live in their platform files.
- *Consequence.* None user-visible. Layout convention only.

**Deciding number: `v08_runtime_data_refs=0` against 24 DOMAIN-keyed touches in
7 files.** Vote **verify**, severity **low**.

---

## D10-09 — no exception translations · **verify** (low)

**My metric.** AST: every `Raise` whose exception is a Call to
`HomeAssistantError`, `ServiceValidationError`, `ConfigEntryAuthFailed` or
`ConfigEntryNotReady` **across the whole package**, and how many carry a
`translation_key` keyword; plus the top-level keys of `strings.json` and of every
shipped translation file.

```
RESULT v09_raise_sites_total=14                     <- matches
RESULT v09_raise_sites_with_translation_key=0       <- matches
RESULT v09_strings_json_has_exceptions_block=0
RESULT v09_translation_files=2
NOTE en.json top keys: ['config', 'entity', 'issues', 'options', 'selector']
NOTE sv.json top keys: ['config', 'entity', 'issues', 'options', 'selector']
```

**Attacks.**

- *Is the API within the floor?* Yes — `translation_key` on `HomeAssistantError`
  landed in 2023.11, below the 2024.1.0 floor. No excuse from the floor here,
  unlike D10-08 and D10-10.
- *Is the consequence real?* Yes. `sv.json` is a genuinely shipped second
  language with `config`, `options`, `entity` and `issues` all translated — the
  integration clearly cares — yet all 14 service errors reach a Swedish user in
  English. The 13 repair issues *are* translated (`strings.json.issues` has 13
  keys, matching the 12 `ir.async_create_issue` sites plus one), which sharpens
  rather than softens the inconsistency.
- *Severity.* Cosmetic for one language. Low.

**Deciding number: `v09_raise_sites_with_translation_key=0` of 14.** Vote
**verify**, severity **low**.

---

## D10-10 — 64 `_attr_icon`, no `icons.json` · **verify** (low)

**My metric.** AST assignment-target count of `_attr_icon` (class-body `Assign`/
`AnnAssign` **and** `self._attr_icon = …`) across **all 45 modules**, not five
named files; plus dynamic `icon` property defs; plus whether the declared floor
permits the fix.

```
RESULT v10_attr_icon_assignments_ast_whole_package=64   <- matches, different definition
NOTE by file: sensor.py=55, binary_sensor.py=4, button.py=4, switch.py=1
RESULT v10_dynamic_icon_properties=0
RESULT v10_icons_json_exists=0
RESULT v10_hacs_min_ha_version_allows_icon_translations=0
```

Two independent definitions (the finder's regex over five files, my AST over 45)
land on the same 64. `climate.py` contributes 0, so the finder's "five platform
files" is really four.

**Attacks.**

- *Is the rule reachable?* Not at the declared floor: icon translations need
  2024.2 and `hacs.json` says 2024.1.0, so the fix moves the floor. The finder
  states this and classes it hygiene rather than a bug — correct.
- *Any dynamic icons that would resist translation?* None (`0` `icon`
  properties), so the migration really is mechanical.

**Deciding number: `v10_attr_icon_assignments_ast_whole_package=64` with
`v10_icons_json_exists=0`.** Vote **verify**, severity **low**.

---

## D10-11 — no diagnostics platform · **verify** (low)

**My metric.** File existence plus an AST scan of all 45 modules for
`async_get_config_entry_diagnostics` **or** `async_get_device_diagnostics`
(the finder checked only the first), plus `async_redact_data` usage.

```
RESULT v11_diagnostics_py_exists=0
RESULT v11_diagnostics_entrypoint_defs=0            <- matches, wider scope
RESULT v11_async_redact_data_imports=0
RESULT v11_code_mentions_of_a_diagnostics_dump=1
```

**Attacks.**

- *Could the entry point live elsewhere?* HA looks only for
  `diagnostics.py`, but I scanned the package anyway. Zero either way.
- *One stated fact is thinner than written.* The finder says "the sensor
  docstrings mention 'the diagnostics dump'". There is exactly **one** such
  mention in the whole package (`sensor.py`, `_WaitsForEvidenceMixin`'s
  docstring), not "docstrings" plural. It is still a real dangling reference to
  a feature that does not exist, so the point stands; the plural does not.
- *Severity.* There is genuine material to dump (a ~149-key payload, thirteen
  learners) and a genuine secret to redact (the Tibber token, which
  `async_redact_data` would handle and which nothing currently touches). Gold
  rule, no user-facing breakage. Low.

**Deciding number: `v11_diagnostics_entrypoint_defs=0`.** Vote **verify**,
severity **low**.

---

## D10-12 — docs gaps · **weaken** (low; two of four sub-claims are heading-shaped)

**My metric.** My own regex family over README.md, DISCLAIMER.md and all 8
`docs/*.md` (10 files), deliberately *looser* than the finder's so a section
that exists under a different name is not scored as missing — a heading match
**and** a whole-document "any mention" match for removal, plus `.storage` and
automation-example probes the finder did not run.

```
RESULT v12_doc_files=10
RESULT v12_removal_instructions=0     RESULT v12_removal_any_mention=0
RESULT v12_known_limitations=0        RESULT v12_blueprint=0
RESULT v12_supported_devices=0        RESULT v12_automation_example=0
RESULT v12_storage_files=0
NOTE README h2: Acknowledgement | What it does | Requirements | Installation |
     Quick start | Entities | Services | How it works | Changing settings after
     setup | Dashboard card | Troubleshooting | ECL110 heat-curve control |
     Project status | Documentation | Disclaimer | License
```

**Attacks — and two of them land.**

- *`docs-removal-instructions` (Bronze): stands, and is worse than a missing
  heading.* Zero matches even on the loosest whole-word scan across all 10
  files. The nearest thing is `docs/dashboard-card.md:442`, which explains how to
  remove the **card resource**, not the integration. And there is real residue:
  `coordinator.py` constructs **10** `Store(...)` objects, so a user who deletes
  the entry leaves ten `.storage` files behind, and `v12_storage_files=0` says
  the docs never mention them. Verified.
- *`docs-examples` / blueprints: stands.* Zero blueprint mentions, zero
  automation YAML examples anywhere, for an integration that ships 11 services.
  Verified.
- *`docs-known-limitations`: weakened.* The **heading** is absent, but the
  information is not. `docs/how-it-works.md:1010` opens "Two caveats are worth
  stating plainly" and spends two bullets on exactly what the defrost derate
  cannot honestly claim at coarse polling resolution; `README.md:376` states a
  hardware caveat about `number` setpoint entities. The rule's intent — a user
  can find out what this cannot do — is partly met in prose. This is a
  discoverability gap, not an information gap.
- *`docs-supported-devices`: weakened.* No section, but the README documents all
  three control paths in prose and a diagram (heat pump switch / ECL110 displace
  / frequency advisor, `README.md:55`, `:123`, `:296-297`, `:358-362`) and marks
  which entities need which hardware. Again a heading, not the content.

**Deciding numbers: `v12_removal_any_mention=0` against 10 `Store(` sites
(verified, Bronze); `v12_known_limitations=0` against prose limitations at
`how-it-works.md:1010` and `README.md:376` (weakened).** Vote **weaken(low)** —
the Bronze removal-instructions gap and the blueprints gap verify; the
known-limitations and supported-devices halves should be recorded as "present in
prose, absent as a findable section".

---

## D10-13 — mypy `--strict` 722 errors · **verify the number, weaken the reading** (low)

Judged from the finder's recorded output, as instructed; my single re-run of
`check_rules.py` reproduced it exactly.

```
RESULT mypy_strict_errors=722          (recorded: 722)
RESULT mypy_strict_files_with_errors=37 of 45   (recorded: 37 of 45)
by code:  no-untyped-call=227, type-arg=111, no-untyped-def=106,
          attr-defined=90, no-any-return=79, union-attr=25   (identical)
worst:    coordinator.py=172, sensor.py=144, config_flow.py=114, __init__.py=70
```

Only `mypy_wall_s` moved (8.5 → 4.9 s), at load 6.92 → 1.56. The count is stable
across a 4× load swing, as a count should be.

**Attacks.**

- *How much of 722 is the integration's own debt, and how much is the stub?*
  Measured what I could without a second mypy run:
  `v13_hastub_function_defs=50`, `v13_hastub_fully_annotated_defs=13`,
  `v13_hastub_untyped_defs=37`, `v13_hastub_has_py_typed=0`. Three-quarters of
  the stub's surface is unannotated and it ships no `py.typed`, so a large share
  of `no-untyped-call=227` is calls into the stub, and much of
  `attr-defined=90` is attributes real HA carries and the stub does not.
  Against real Home Assistant those two codes (317 of 722, **44 %**) would fall
  substantially. What is **not** disputable is the integration-internal core:
  `no-untyped-def=106` + `type-arg=111` + `no-any-return=79` = **296** errors
  that are about this code's own annotations and cannot be blamed on any stub.
- *What would decide the split?* One `mypy --strict` run with `homeassistant`
  actually installed (or `--follow-imports=skip` on the stub path), diffing the
  by-code table against the recorded one. The box constraint forbids a second
  whole-package mypy run, so I did not take it; the judge should, on the quiet
  box, before the register records "722" as the integration's typing debt.
- *Is the finder overselling?* No — its own mechanism field says
  "no-untyped-call is partly the untyped stub, so the true count against real
  Home Assistant is lower but not near zero". That is the honest reading. My
  objection is only that the **title** carries the un-caveated 722.

**Deciding number: 296 integration-internal errors inside a headline of 722.**
Vote **verify** (the measurement is exact and reproducible), severity **low**,
with the register asked to carry "722 total / ~296 stub-independent" rather than
"722".

---

## D10-14 — coverage 88.4 %, config_flow 86.4 % · **verify** (low)

Judged from the finder's recorded `coverage/`, as instructed. I re-derived the
headline **arithmetically from its own `coverage.json`** rather than re-running
anything:

```
RESULT v14_modules_in_coverage_json=45
RESULT v14_statements=12877          RESULT v14_missing=1491
RESULT v14_recomputed_total_pct=88.4      <- matches RESULTS.txt exactly
RESULT v14_modules_ge95_recomputed=20 of 45   <- matches
config_flow.py: 493 statements, 67 missing -> 86.4 %   <- matches
```

**Attacks.**

- *Two scripts exited non-zero — does that void the number?* No, and I checked
  both logs rather than taking the caveat on trust. `entities.py` aborted at
  `tests/entities.py:4360` on a missing `RELEASE_NOTES.md`; the log shows the
  abort is inside the **final** "Release metadata" section, after every entity,
  binary-sensor and service check has already run and passed — so it costs
  essentially no integration-module coverage. `golden.py` exited 1 with "34 of 55
  GOLDEN SCENARIOS CHANGED", and the diffs are `…after_save: new`, i.e. fields
  the committed fixtures predate — fixture staleness, which changes what is
  *asserted*, not which lines *execute*.
- *Is the aggregate an artefact of the measured set?* The set omits
  `env_drift.py`, `closure.py`, `rolling.py` and every Node script, so 88.4 % is
  a **floor**. That cuts against the finding, not for it, and the finder says so.
- *Does the config-flow mechanism hold?* `tests_driving_async_step_user_with_input=0`
  in the re-run, and my own V01 corroborates it from the other side: to drive the
  submit branch at all I had to monkeypatch `validate_tibber_token` myself, which
  is precisely what no existing test does. So `invalid_tibber_token` /
  `cannot_connect` are unexecuted, against a rule
  (`config-flow-test-coverage`) that wants 100 %.
- *Timing.* `wall_s=982` in `RESULTS.txt` vs "1818 s" in the report's
  contention note — an inconsistency in the finder's prose, but both are
  PROVISIONAL wall numbers that no claim rests on. The percentage is a count
  ratio and load-independent.

**Deciding number: `v14_recomputed_total_pct=88.4` from 12877/1491, and 20 of 45
modules ≥ 95 %.** Vote **verify**, severity **low**.

---

## D10-15 — kWh sensors without ENERGY; DeviceInfo without `entry_type` · **weaken** (low)

Two claims bundled. They do not survive equally.

**My metric.** Read off the **live entity objects** built by the real platform
setups (the stub's `SensorEntity` has no `device_class` /
`native_unit_of_measurement` properties, so a property read returns nothing and a
source-text match misses `UnitOfEnergy.KILO_WATT_HOUR`; reading the `_attr_`
slots off the instances catches both class-level and `__init__`-set units such as
`coordinator.currency`). My unit→class map is deliberately **wider** than the
finder's, and I additionally record each candidate's `state_class`.

```
RESULT v15_sensor_entities_from_real_setup=55
RESULT v15_sensor_entities_with_a_unit=39
RESULT v15_sensor_entities_with_device_class=29        (finder: 29 — matches)
RESULT v15_sensor_entities_with_mappable_unit_and_no_device_class=12   (finder: 5)
RESULT v15_kWh_sensor_entities_without_ENERGY=2        (finder: 2 — same two)
RESULT v15_kWh_sensor_entities_without_ENERGY_but_with_a_state_class=2
RESULT v15_device_info_entry_type=0
RESULT v15_device_info_manufacturer_is_Custom=1
```

My 12 vs the finder's 5 is a definition difference, not a contradiction: I map
`SEK`→MONETARY and count `%` and `SEK/kWh` as candidates; the finder does not.
Both of us land on the **same two kWh sensors**: `PVSurplusSensor`
(`solar_surplus_forecast`) and `DHWHeavyDaySensor` (`dhw_heavy_day_demand`).

**The attack that lands.** Both carry `_attr_state_class =
SensorStateClass.MEASUREMENT`, and Home Assistant permits `ENERGY` only with
`TOTAL` or `TOTAL_INCREASING`:

```
NOTE HA allows ENERGY only with state classes: total, total_increasing
RESULT v16_kWh_gaps_whose_ENERGY_fix_HA_forbids=2
RESULT v16_suite_gates_device_class_state_class_pairs=1
```

So the finder's stated perturbation — "Set `_attr_device_class =
SensorDeviceClass.ENERGY` on DHWHeavyDayDemand's sensor class" — creates a pair
HA logs as *"state class … which is impossible considering device class"*, and
would **fail the repository's own existing gate** at `tests/entities.py:1225`
("no sensor pairs a device class with a state class HA forbids"). It is not a
one-line fix; it is a two-line change that also converts a forecast into a
long-term-statistics total, which is wrong on the merits: neither sensor is a
meter. `solar_surplus_forecast` is tomorrow's predicted surplus;
`dhw_heavy_day_demand` is a learned quantile of demand. Summing either as an
energy total would produce nonsense in the Energy dashboard.

That is *the same reasoning the finder itself accepted* for the three it
exempted, and the same reasoning the suite already pins for two of them
(`tests/entities.py:1236-1245`: "ECL110 Displace stays bare: it is a parallel
shift, not a temperature"; "Prediction Accuracy stays bare for the same reason").
Applied consistently, it exempts the two kWh sensors too.

**The other half stands.** `entry_type` is absent from `DeviceInfo`
(`coordinator.py:1323-1329`, 5 keys: identifiers, name, manufacturer "Custom",
model, sw_version). `DeviceEntryType.SERVICE` has existed since 2021.12, well
below the floor, and this integration *is* a service, not a device. Trivially
true, trivially fixable, and it changes only presentation.

**Deciding number: `v16_kWh_gaps_whose_ENERGY_fix_HA_forbids=2` of 2.** Vote
**weaken(low)** — the `entry_type`/`manufacturer` half verifies; the "two kWh
sensors without ENERGY" half should be **struck**, moved to the finder's own
correctly-classless list alongside `ecl110_displace`,
`ecl110_effective_displace` and `prediction_accuracy`, on the state-class
argument the finder already used for those three.

---

## Summary

| finding | finder | seat 1 | deciding number |
|---|---|---|---|
| D10-01 | medium | **verify** medium | `v01_abort_results_with_one_existing_entry_of_2=0` |
| D10-02 | medium | **verify** medium | `v02_all_5_cases_raising_UpdateFailed=5` |
| D10-03 | low | **verify** low | `v03_error_records_10_failed_refreshes=11` vs null 1 |
| D10-04 | low | **weaken** low (scope) | `v04_..._whose_return_names_the_failure_of_3=2` |
| D10-05 | low | **verify** low | `v05_entities_available_..._false=2` (static 2) |
| D10-06 | low | **verify** low | `v06_services_left_after_last_unload=0` |
| D10-07 | low | **verify** low | `v07_platform_files_declaring_PARALLEL_UPDATES=0` of 5 |
| D10-08 | low | **verify** low | `v08_runtime_data_refs=0`; 24 of my 27 are DOMAIN-keyed |
| D10-09 | low | **verify** low | `v09_raise_sites_with_translation_key=0` of 14 |
| D10-10 | low | **verify** low | `v10_attr_icon_assignments_ast_whole_package=64` |
| D10-11 | low | **verify** low | `v11_diagnostics_entrypoint_defs=0` |
| D10-12 | low | **weaken** low (scope) | `v12_removal_any_mention=0` vs 10 `Store(` sites |
| D10-13 | low | **verify** low (reading) | 296 stub-independent inside 722 |
| D10-14 | low | **verify** low | `v14_recomputed_total_pct=88.4` from 12877/1491 |
| D10-15 | low | **weaken** low | `v16_kWh_gaps_whose_ENERGY_fix_HA_forbids=2` of 2 |

Eleven verify, four weaken (three of them scope rather than severity), **no
refutes**. Every count in `check_rules.py` reproduced exactly; nothing here rests
on a timing mismatch, so nothing goes to the judge as `unresolved`.

## Note for the judge: what may already be fixed on `main`

I cannot read `main`. Two signals bear on it. `coordinator.py`'s
`_fetch_tibber_prices` and `_tibber_fetch_failed` docstrings cite **"D10-07"** and
**"D10-09"** ids from an *earlier* round, so a previous D10 pass already shipped
fixes into exactly this code; and the visible commit log at the head of this
worktree is entirely card-decomposition work (PR 5b–9 of #136), which touches no
integration module. My expectation is therefore that all fifteen mechanisms still
stand at `main`, with **D10-03 the one most likely to have moved** — it is a hole
in the round-1 log-once latch, and the kind of thing a follow-up round closes.

What would decide each, run in the live repository (not this export):

- **D10-03** — `git show main:custom_components/heatpump_optimizer/coordinator.py | grep -n -B2 -A2 'Error updating Heat Pump Optimizer'`; if both outer handlers now call `_LOGGER.debug`, or gate on `_tibber_outage_cycles`, the mechanism is fixed.
- **D10-01** — `git show main:custom_components/heatpump_optimizer/config_flow.py | grep -cE '_async_abort_entries_match|async_set_unique_id'` and `git show main:custom_components/heatpump_optimizer/manifest.json | grep single_config_entry`; any hit closes it.
- **D10-02** — `git show main:custom_components/heatpump_optimizer/coordinator.py | grep -c ConfigEntryAuthFailed` and `… config_flow.py | grep -c async_step_reauth`; both must be non-zero.
- **D10-05** — `git show main:custom_components/heatpump_optimizer/button.py | grep -c 'super().available'`; 2 closes it.
- **D10-11** — `git ls-tree main custom_components/heatpump_optimizer/diagnostics.py`.
- **D10-15** — `git show main:custom_components/heatpump_optimizer/sensor.py | grep -n -B4 "dhw_heavy_day\|pv_surplus"`; if `_attr_state_class` moved to `TOTAL` alongside a new `_attr_device_class`, the fix was taken properly and my weaken is moot; if only a device class was added, the suite gate at `tests/entities.py:1225` should now be failing.
- **D10-13 / D10-14** — both are whole-suite measurements; only a re-run on the quiet box settles them, and D10-13's stub/real split needs the `homeassistant`-installed mypy run described above.

## Artefacts

- `/tmp/verify-D10-1/verify_d10.py` — my harness (self-contained header: metric, command, expected values, baseline SHA, machine, instrumented symbols).
- `/tmp/verify-D10-1/verify.out`, `/tmp/verify-D10-1/verify.results.txt` — its output.
- `/tmp/verify-D10-1/check_rules.rerun.out` — the finder's harness, re-run once.

All measurements taken at `load1` 1.56–2.02, `thread_factor=1.00`. Every number
is a count or a count ratio.
