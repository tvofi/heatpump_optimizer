# D10 — verifier seat 3 of 3 (angle: perturbation and fix scope)

Baseline `c398fc84eec25fc44b60d74aae05b9a2da205884`, export `audit-r2-baseline` (read-only;
untouched except this file — `diff -rq` against the working copy shows no source difference
after every revert). Apple M1, Python 3.13.1 from
`/Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/tvofi-claude/.venv`.
Perturbations were applied to a copy of the export at `/tmp/verify-D10-3/export`, one at a
time, each reverted before the next.

**Box constraint honoured:** AST/grep and stub-driven flows only. No coverage suite, no
`tests/run.sh`, no solver. mypy ran exactly once, inside the mandated `check_rules.py`
re-run; consequences for D10-13 and D10-14 are recorded under those findings.

## The mandated re-run

```
cd <export root>
PYTHONPATH=tests/hastub .venv/bin/python tools/audit/round2/D10/check_rules.py
```

Every count RESULT reproduces the committed `check_rules.out` **exactly** — all 54 rows,
`done=27 todo=21 exempt=6`, and `mypy_strict_errors=722`. The only diffs are the three
load-dependent lines: `mypy_wall_s` 8.5 → 5.1 s, `load1` 6.92 → **1.43**, `swapins_delta`
143 → 36. `thread_factor=1.00` both times. So the finder's headline counts were taken under
load1 6.9 but are load-invariant, as claimed; my re-take is inside the judge's `load1 ≤ 1.5`
gate and agrees to the digit.

## My own harness

`/tmp/verify-D10-3/mine.py` — a source-only AST/regex harness with **different metric
definitions** from `check_rules.py`: no stub, no roster, no entity instantiation. It walks
the class bodies and module ASTs directly. Its numbers appear per finding below as *mine*.
Independent confirmations of note:

| my metric (source-only) | mine | finder (stub/roster) |
|---|---|---|
| `available` property defs in the 5 platform files whose body never names `super().available` | **2** (`button.py:ForceOptimizationButton`, `button.py:SystemIdentificationButton`) | 2 of 65 entities available after a failed refresh |
| sensor **classes** whose `_attr_native_unit_of_measurement` maps to a device class and whose `_attr_device_class` is unset | **5** — the same five, by class name | 5 entities |
| defs mypy `--strict` would flag `no-untyped-def` (AST: any unannotated non-self param, or no return annotation) | **104** of 1062 defs | mypy: `no-untyped-def=106` |
| statements/misses recomputed from `coverage/coverage.json` | **12877 / 1491 → 88.42 %**, 20 modules ≥ 95 %, config_flow 86.4 % | 88.4 %, 20/45, 86.4 % |

---

## Per finding

### D10-01 — no unique-id / entries-match guard in the config flow — **verify** (medium)

**My number.** `unique_entry_guards=0`, `flow_aborts_with_existing_entry=0`.
*Mine:* `dup_entry_guard_tokens=0`, `manifest.single_config_entry=None`,
`config_flow_first_steps=1` (only `async_step_user`; no `async_step_import`, `_reauth` or
`_reconfigure` exists).

**Metric.** Count of duplicate-entry guard idioms in `config_flow.py` plus
`manifest.single_config_entry`; and whether `async_step_user` aborts with one entry already
in `hass.config_entries` (0/1).

**Perturbation — moves as stated.** Inserted at the top of `async_step_user`:
`if self.hass.config_entries.async_entries(DOMAIN): return self.async_abort(reason="already_configured")`.
**0 → 1** on both RESULTs; the `unique-config-entry` row flips `todo → done` and the totals
go `done 27 → 28`, `todo 21 → 20`. `test-before-configure` stays `done`, so the null path
(no existing entry) is unchanged — the guard's absence is the only difference.

**Fix scope.** Complete. `async_step_user` is the *only* entry-creating step in the file
(21 config-flow steps, one entry point; the 15 options steps cannot create an entry), so a
two-line guard there covers every path. Two caveats for the fixer:
1. the production idiom `self._async_abort_entries_match()` is **not implemented in
   `tests/hastub`** (`ConfigFlow` there has only `async_show_form/_menu/_create_entry/
   _abort`), so a fix written idiomatically will match the finder's grep but cannot be
   driven by this harness; either use the explicit `hass.config_entries.async_entries(DOMAIN)`
   form or extend the stub;
2. `strings.json` already carries `abort.already_configured` unused — no strings work needed.

**Vote: verify, medium.** Deciding number: `unique_entry_guards 0 → 1` under the stated
perturbation, from a metric that is 0 in three independent formulations.

---

### D10-02 — rejected Tibber token reported as transient `UpdateFailed` — **verify** (medium)

**My number.** `auth_failures_raising_ConfigEntryAuthFailed=0` of 3.
*Mine:* `ConfigEntryAuthFailed` appears **0** times anywhere in the package;
`coordinator.py` has no `status in (401, 403)` branch while `config_flow.py` has one
(`validate_tibber_token`, line 344 — the helper a reauth step would reuse already exists).

**Metric.** Of three auth-failure responses (401, 403, 200 + `errors` payload) driven
through `_fetch_tibber_prices` under a fake session, how many raise `ConfigEntryAuthFailed`
rather than `UpdateFailed`.

**Perturbation — re-checked carefully; both halves reproduce.** With
`class ConfigEntryAuthFailed(HomeAssistantError)` added to `tests/hastub/homeassistant/exceptions.py`:

| edit | RESULT |
|---|---|
| (a) alone — `if resp.status in (401, 403): raise ConfigEntryAuthFailed(...)` before the generic status check | **0** — swallowed |
| (a) + (b) — plus `except ConfigEntryAuthFailed: raise` ahead of `except aiohttp.ClientError` | **2** |

The finder's reported failed first attempt reproduces exactly. The mechanism is confirmed by
reading: `_tibber_fetch_failed` raises `UpdateFailed` **inside** the `try`, and the trailing
`except Exception as err` (coordinator.py, end of `_fetch_tibber_prices`) converts anything
raised in the request block; `ConfigEntryAuthFailed` is not an `aiohttp.ClientError`, so it
lands in the generic handler without (b). Under (a)+(b) the `test-before-setup` row reads
`401->ConfigEntryAuthFailed, 403->ConfigEntryAuthFailed, 200+errors->UpdateFailed`, and
`reauthentication-flow` correctly stays `todo` (`async_step_reauth=0`).

**Fix scope.** Complete for the auth class, and the files listed are the right three.
Checked the whole package for other unhandled credential paths: three HTTP call sites exist
(`config_flow.py:336`, `coordinator.py:5394`, `open_meteo.py:325`). `config_flow.py`
already classifies 401/403 as `invalid_auth`; Open-Meteo is keyless, so it has no auth class
to raise. The Tibber fetch is the only site. Two notes: the third case (200 + `errors`
payload) needs the same `except ConfigEntryAuthFailed: raise` to escape, since it also goes
through `_tibber_fetch_failed`; and the stub needs the exception class added for any
regression test to be written.

**Vote: verify, medium.** Deciding number: `auth_failures_raising_ConfigEntryAuthFailed
0 → 2` only with (b) present, `0 → 0` without it.

---

### D10-03 — every failed refresh logs ERROR with a traceback — **verify** (low)

**My number.** `error_records_over_3_failed_refreshes=4`; null control
`error_records_over_3_failed_fetches_direct=1`.
*Mine:* 9 `_LOGGER.error(` sites in `coordinator.py`, **3** of them with `exc_info=True`.

**Metric.** Records at level ≥ ERROR on logger `heatpump_optimizer` over three consecutive
`_async_update_data` calls whose Tibber fetch fails.

**Perturbation — moves as stated.** Demoting the `_LOGGER.error(` in the `except Exception`
at the end of `_async_update_data` (the **first** of the two identical blocks; the second is
in `_async_first_refresh_light`) to `_LOGGER.debug(` gives **4 → 1**; the null control stays
at 1; the `log-when-unavailable` row flips `todo → done`. So the surplus 3 is exactly the
outer handler, one per cycle. The stated arithmetic checks out: 24 h at the 30-minute
interval is 48 cycles → 48 outer + 1 latched = 49 records.

Reachability: the stub's failure trigger ("no HTTP session available") is stub-specific, but
the *path* is not — in real Home Assistant any `aiohttp.ClientError` reaches
`_tibber_fetch_failed` → `UpdateFailed` → the same outer `except Exception`. Real HA adds
its own coordinator ERROR on top, so the real count is ≥ the measured one.

**Fix scope — incomplete for the class, sufficient for the rule.** The two files/lines named
clear `log-when-unavailable`. But the same defect class appears at four more unlatched
per-cycle sites the finder does not list:
- `coordinator.py` `async_run_optimization`'s `except Exception`:
  `_LOGGER.error("Optimization failed: %s", err, exc_info=True)` — this is called **from
  `_async_update_data`**, so a persistent solve failure prints one ERROR *with traceback*
  per cycle, latched only for the repair issue (`_solve_failures`), not for the log;
- five unlatched actuation ERRORs that fire once per attempt: the two ECL110 MQTT publishes,
  `Error commanding valve target`, `Error toggling heat pump switch`,
  `Error commanding compressor frequency`.

None of these is `log-when-unavailable`, so the rule row is unaffected — but a fixer told
"demote two calls" will leave the same log-flood behaviour for a stuck MQTT bridge or a
persistently failing solve.

**Vote: verify, low.** Deciding number: `error_records_over_3_failed_refreshes 4 → 1`
against a null control fixed at 1.

---

### D10-04 — service actions swallow operational failures — **verify** (low)

**My number.** `service_failure_paths_returning_silently=3` of 3.
*Mine:* 11 `handle_*` service handlers; **14** `raise ServiceValidationError(`; **0**
`raise HomeAssistantError(` anywhere in the package.

**Metric.** Of `run_optimization`, `simulate_plan` and `restore_learned_snapshot` called
through the registered handlers on a coordinator with no prices/plan/snapshot, how many
return instead of raising.

**Perturbation — re-checked carefully; both halves reproduce.**

| edit | RESULT | `run_optimization` outcome |
|---|---|---|
| raise inside `async_run_optimization` (replacing the `len(prices) < 4` early return) | **3** — unchanged | `returned None` |
| raise in the handler, `__init__.py handle_run_optimization`, before `await coord.async_run_optimization()` | **2** | `raised HomeAssistantError` |

The finder's "3 → 3 if placed inside" reproduces exactly. **Correction to the report:** the
mechanism paragraph cites `coordinator.py:5536` as `async_run_optimization`'s
`except Exception`; line 5536 is inside `_fetch_weather_forecast`. The actual swallow is the
`except Exception as err: _LOGGER.error("Optimization failed: ...")` at coordinator.py:4825.
The mechanism is right, the line reference is not.

**Fix scope — files right, enumeration understated.** The two files named are the right
ones, but the class is wider than the three paths measured: `_manual_targets(target_entry)`
yields nothing for an unknown or unloaded `entry_id`, so `apply_manual_plan`,
`clear_manual_plan`, `restore_snapshot` and `diagnose_interval` all answer
`{"cleared": []}` / `{"restored": []}` / `{"diagnosis": {}}` on a target that does not exist
— indistinguishable from success. `handle_set_mode` and `handle_set_thermal_params` return
`None` after touching nothing when `hass.data[DOMAIN]` holds no coordinator. The harness
drives 3 of the 11 handlers, so the metric is a floor, not the class size.

**Vote: verify, low.** Deciding number: `service_failure_paths_returning_silently 3 → 2`
with the raise in the handler, `3 → 3` with it inside `async_run_optimization`.

---

### D10-05 — two buttons stay available after a failed refresh — **verify** (low)

**My number.** `entities_available_after_failed_refresh=2` of 65.
*Mine* (independent definition, no roster): **2** `available` property defs across the five
platform files whose body never names `super().available` —
`button.py:ForceOptimizationButton` and `button.py:SystemIdentificationButton`.

**Metric.** Entities from the real platform setups whose `.available` is True while
`coordinator.last_update_success` is False.

**Perturbation — moves as stated.** `return super().available and not self.coordinator.
optimization_running` (and the same for `system_identification_active`): **2 → 0**, and the
`entity-unavailable` row flips `todo → done` (`0/65 []`).

Reachability: `tests/hastub`'s `CoordinatorEntity.available` mirrors the real base class
(its docstring says so explicitly, and the 63 other entities go unavailable in the same
drive), so the conjunction is honestly tested and behaves the same in real Home Assistant.

**Fix scope — complete and exact.** I enumerated every `available` override in the package:
12 in `sensor.py` (all AND `super().available`), 2 in `button.py` (both drop it),
1 in `open_meteo.py` (an internal forecast-source class, not an entity — irrelevant), and
**none** in `binary_sensor.py`, `switch.py` or `climate.py`, which inherit the base
unchanged. The other two buttons have no override. "two one-line changes in `button.py`" is
the whole fix, with nothing of this class left elsewhere.

**Vote: verify, low.** Deciding number: `entities_available_after_failed_refresh 2 → 0`.

---

### D10-06 — 11 services registered in `async_setup_entry`, not `async_setup` — **verify** (low)

**My number.** `services_registered_in_setup_entry=11`, `async_setup_defs=0`.
*Mine:* 11 `hass.services.async_register(` in `__init__.py`, 0 module-level
`async def async_setup(`.

**Metric.** AST count of `hass.services.async_register` calls whose enclosing
`async_setup_entry` `ast.walk` reaches, in `__init__.py`; plus `async_setup` defs.

**Perturbation — executed (the finder left this one stated only); moves as stated.** I moved
all eleven registrations into a module-level `_register_services(hass, <11 handlers>)` called
from `async_setup_entry`, and added a module-level `async def async_setup(hass, config)`:
`services_registered_in_setup_entry` **11 → 0**, `async_setup_defs` **0 → 1**, row flips
`todo → done`. The lifecycle drive still reports 11 services after setup and 0 after unload,
so the integration keeps working.

**Fix-scope / metric weakness (for the judge).** That perturbation flips the row while the
services are still, at runtime, registered from the entry — the metric is a lexical AST
proxy for the rule, not a behavioural test of it, and a cosmetic extraction clears it. The
claim itself is independently true and its consequence is measured elsewhere in the same
run: `config-entry-unloading` reports `services after unload=0`, i.e. the services really do
vanish with the entry. A fixer must be told the rule wants registration in `async_setup`
*with a loaded-entry check in each handler* (the finder's prose says this; the metric does
not enforce it).

**Vote: verify, low.** Deciding number: `services_registered_in_setup_entry 11 → 0` with
`async_setup_defs 0 → 1`.

---

### D10-07 — no platform declares `PARALLEL_UPDATES` — **verify** (low)

**My number.** `platforms_declaring_parallel_updates=0` of 5. *Mine:* 0.

**Metric.** Platform files with a module-level `PARALLEL_UPDATES` assignment.

**Perturbation — executed; moves as stated.** `PARALLEL_UPDATES = 0` at module level in
`sensor.py`: **0 → 1** (`declared in 1/5 platforms`; the row needs 5/5 so it correctly stays
`todo`).

**Fix scope.** Complete — five one-line additions in exactly the five files listed; the
package has no sixth entity platform (`PLATFORM_LIST` and the roster both cover
sensor / binary_sensor / button / switch / climate).

**Vote: verify, low** (hygiene; one coordinator, no outbound device protocol, so no
consequence beyond the rule).

---

### D10-08 — runtime state in `hass.data[DOMAIN]`; base classes outside `entity.py` — **verify** (low)

**My number.** `runtime_data_refs=0`, `hass_data_domain_refs=24`,
`entity_base_classes_outside_entity_py=5`. *Mine:* `runtime_data` 0, `entity.py` absent.

**Metric.** Regex counts of `runtime_data` and of `hass.data[DOMAIN]` / `.get(DOMAIN` /
`.setdefault(DOMAIN` across the package; `CoordinatorEntity` base classes outside `entity.py`.

**Perturbation — executed; moves as stated.** `entry.runtime_data = coordinator` in
`async_setup_entry`: `runtime_data_refs` **0 → 1**, `hass_data_domain_refs` unchanged at
**24**, row flips `todo → done`.

**Fix-scope / metric weakness.** As with D10-06, one cosmetic line flips the row while all
24 readers still go through `hass.data`. Credit where due: the finder's *proposed fix scope*
is not fooled by its own metric — it says "plus reader updates (24 sites) once the floor is
2024.4". The floor argument is correct and checkable: `ConfigEntry.runtime_data` is 2024.4
and `hacs.json` declares 2024.1.0, so this is a floor decision. The `entity.py` half is
floor-neutral and its file list (7 files) matches the 7 files my grep finds.

**Vote: verify, low.** Deciding number: `runtime_data_refs 0 → 1` with
`hass_data_domain_refs` pinned at 24.

---

### D10-09 — 14 service exceptions with literal English, no `exceptions` block — **verify** (low)

**My number.** `exception_raises_with_translation_key=0` of 14 raises; `strings.json`
`exceptions` block absent. *Mine:* same two numbers.

**Metric.** Regex count of `raise ServiceValidationError|HomeAssistantError` sites whose call
carries `translation_key`, over all such raises.

**Perturbation — executed; moves as stated.** Gave the `Entity {raw} does not exist` raise
`translation_domain=DOMAIN, translation_key="entity_missing"` and added an `exceptions`
block to `strings.json`: **0 → 1**, row detail becomes `raises=14; with translation_key=1;
strings.json exceptions block=True` and correctly stays `todo` (needs 14/14).

**Fix-scope note.** The `translated` regex is
`raise (…)\([^)]*translation_key` — `[^)]*` means it cannot see past a closing paren, so a
raise whose message argument contains a call (e.g. `f"...{float(minimum):g}..."`, several of
the 14) would **not** be counted as translated even after it is fixed, unless
`translation_key` is placed before the message. A fixer following the metric will hit a
false negative on those sites. The count of 14 total raises is right (my independent count
agrees: 13 in `__init__.py` + 1 in `coordinator.py`), and the API floor claim is right
(`translation_key` on `HomeAssistantError` is 2023.11, inside the 2024.1.0 floor).

**Vote: verify, low.** Deciding number: `exception_raises_with_translation_key 0 → 1`.

---

### D10-10 — icons are entity state; 64 `_attr_icon`, no `icons.json` — **verify** (low)

**My number.** `icons_in_code=64`, `icons.json` absent. *Mine:* 64, absent.

**Metric.** Regex count of `_attr_icon =` across the five platform files; existence of
`icons.json`.

**Perturbation — executed; moves as stated.** Deleting one `_attr_icon =` line
(`PVSurplusSensor`'s `mdi:solar-power-variant`): **64 → 63**.

**Fix scope.** Correct, including the `hacs.json` floor bump to 2024.2.0 — the file list
names the four platform files that carry icons plus `hacs.json`. `climate.py` is listed in
the *Files* line of D10-07 but not here, correctly: it assigns no `_attr_icon`.

**Vote: verify, low** (a floor decision, as the finder says, not an oversight).

---

### D10-11 — no diagnostics platform — **verify** (low)

**My number.** `diagnostics_defs=0`; `custom_components/heatpump_optimizer/diagnostics.py`
does not exist. *Mine:* same.

**Metric.** Existence of `diagnostics.py` and count of
`async_get_config_entry_diagnostics` definitions.

**Perturbation — executed; moves as stated.** Added a 7-line `diagnostics.py` with
`async_get_config_entry_diagnostics`: **0 → 1**, row flips `todo → done`.

**Fix scope.** One new file; nothing else in the package needs to change. The redaction
target is real — `CONF_TIBBER_TOKEN` is stored in `entry.data`.

**Vote: verify, low.**

---

### D10-12 — docs gaps: removal, known limitations, blueprints, supported devices — **verify** (low)

**My number.** `docs_removal_instructions=0`, `docs_known_limitations_sections=0`,
`docs_blueprints=0`, supported-devices sections 0.

**My method (broader than the finder's).** I re-grepped `README.md`, `docs/*.md` and
`DISCLAIMER.md` with wider patterns than `check_rules.py` uses — adding `\.storage`,
`delete the (integration|entry|config entry)`, `compatible`, and any heading containing
`limitation` — and still got **zero matches on all four**. A wider net finding nothing is
stronger evidence than the finder's narrower one.

**Perturbation — executed; moves as stated.** Appending a `## Removing the integration`
section to `README.md`: `docs_removal_instructions` **0 → 1**, the `docs-removal-instructions`
row (Bronze) flips `todo → done`, totals `done 27 → 28`.

**Fix scope.** Complete; `docs-removal-instructions` is the only Bronze rule of the four and
a `README.md` section clears it.

**Vote: verify, low.**

---

### D10-13 — `mypy --strict` reports 722 errors in 37 of 45 modules — **verify** (low), perturbation not executed

**My number.** `mypy_strict_errors=722`, `mypy_strict_files_with_errors=37` — **exact**
reproduction of the committed value, at load1 1.43 rather than 6.92, in 5.1 s rather than 8.5 s.

**Metric.** Count of `error:` lines from `mypy --strict --python-version 3.13
custom_components/heatpump_optimizer` with `tests/hastub` on `MYPYPATH`, whose path starts
with `custom_components/`.

**My independent measurement (no mypy).** AST over the package: **104** of 1062 defs have at
least one unannotated non-self parameter or no return annotation — i.e. 104 defs that
`no-untyped-def` must fire on, against the finder's `no-untyped-def=106`. Concentration
matches too: `sensor.py` 58 of my 104, and the finder's worst-file list is
`coordinator.py=172, sensor.py=144, config_flow.py=114, __init__.py=70`. I also confirmed
the perturbation target exists and is unannotated:
`OptimizationModeSensor.__init__(self, coordinator, entry)` in `sensor.py`, no return
annotation.

**Perturbation — NOT executed.** The stated perturbation needs a second mypy run and the box
constraint allows one, which the mandated `check_rules.py` re-run consumed. I record two
things for the judge rather than pretending:
1. the direction is **not obviously down**. `--strict` implies `--check-untyped-defs`, so
   the body of that `__init__` is already checked against implicit `Any`; annotating
   `coordinator: HeatPumpOptimizerCoordinator` replaces `Any` with a concrete type and can
   *add* `attr-defined` / `arg-type` errors at its use sites. "goes down by at least 1" is
   plausible but untested, and this is exactly the kind of perturbation that has already
   failed twice on this panel (D10-02, D10-04);
2. the perturbation matters less here than elsewhere. The metric is mypy's own output over
   the production package, not a number derived from constants, so the "is it hooked to
   production" question the perturbation exists to answer is settled by construction. The
   rule is binary (0 errors = done), so the claim does not hinge on the perturbation's
   direction.

**Fix scope.** The four files listed are the right starting points and the ordering advice
(mechanical `no-untyped-def` + `type-arg` first, then Optional narrowing) matches where the
errors are. The stated caveat is honest and load-bearing: `no-untyped-call=227` is partly
the untyped stub, so the count against real Home Assistant is lower — the finder says so.

**Vote: verify, low**, with the perturbation recorded as **unexecuted by box constraint**.
Deciding number: 722 reproduced exactly, corroborated by an independent AST count of 104 vs
mypy's 106 on the largest structural error class.

---

### D10-14 — statement coverage 88.4 %, 20 of 45 modules ≥ 95 %, config_flow 86.4 % — **verify** (low), with one prose correction

**My numbers, re-derived independently from `coverage/coverage.json`** (not from the
finder's tables): 45 modules, **12877** statements, **1491** missed → **88.42 %**;
modules ≥ 95 %: **20**; `config_flow.py` 86.4 % (67 of 493 missed).

**Correction.** REPORT.md's prose says "**1493** missed"; the harness's own
`coverage/RESULTS.txt` says `coverage_missing=1491`, and `per_module.tsv` sums to 1491. The
88.4 % headline is unaffected (1493 would give 88.41 %). Separately, the coverage section's
"wall 1818 s" is the sum of the per-script wall column, while `RESULTS.txt` records
`wall_s=982`; both are marked PROVISIONAL and neither is load-bearing.

**Perturbation — NOT executed** on the coverage half: the stated perturbation
(`SLOW=1 coverage_suite.sh`) is the coverage suite, which the box constraint bars outright.

**What I executed instead.** Two cheap checks that attack the *mechanism* rather than the
aggregate:
1. **the causal claim, confirmed exactly.** `config_flow.py`'s missing-line set from
   `coverage.json` contains lines 957, 960–966 — the entire `user_input is not None` branch
   of `async_step_user`, including both error assignments — and 337, 341–346, the whole
   response-handling body of `validate_tibber_token` (`status == 200`, `status in (401, 403)`,
   `return "cannot_connect"`). The suite renders the form and never submits it, precisely as
   claimed;
2. **the sub-claim, confirmed and perturbed.** `grep -rn async_step_user tests/*.py` returns
   exactly **one** call, `tests/entities.py:3470`,
   `asyncio.run(_fresh_flow().async_step_user(None))` — with `None`. Appending one call with
   a dict argument to `tests/entities.py` moves
   `tests_driving_async_step_user_with_input` **0 → 1**, so that half of the harness is live.

**Fix scope, and one caveat on magnitude.** `tests/entities.py` is the right file for the
config-flow half, and that half is solid: `tests/rolling.py`, the one gate script excluded
from the measured set, imports `HeatPumpOptimizerCoordinator` and never touches
`config_flow` (`grep -c config_flow tests/rolling.py` = 0), so the 86.4 % against a 100 %
rule cannot be an artefact of the exclusion.

The **overall 88.4 % is a lower bound**, and by more than the report's phrasing suggests:
`coordinator.py` alone accounts for **843 of the 1491 missed statements (56.5 %)**, and
`rolling.py` is the closed-loop driver of exactly that module. Its exclusion, plus
`entities.py` aborting at 4360/4587 on the export's absent `RELEASE_NOTES.md`, both push the
measured number down. The finder discloses both, but a judge should read 88.4 % as "≥ 88.4 %
on this measured set", not as the suite's coverage.

**Vote: verify, low**, with the coverage perturbation recorded as **unexecuted by box
constraint** and the prose figure corrected 1493 → 1491. Deciding number: 88.42 %
recomputed from the artifact, and `config_flow.py` missing lines 957/960–966 and 337/341–346.

---

### D10-15 — two kWh sensors without `ENERGY`; `DeviceInfo` without `entry_type` — **verify** (low)

**My number.** `sensors_with_unit_but_no_device_class=5`, `device_entry_type_service=0` of 65.
*Mine* (class-attribute AST scan, no roster): the same **5**, by class name —
`ECL110DisplaceSensor[°C]`, `ECL110EffectiveDisplaceSensor[°C]`,
`PredictionAccuracySensor[°C]`, `PVSurplusSensor[kWh]`, `DHWHeavyDaySensor[kWh]`;
`entry_type` appears 0 times in `coordinator.py`.

**Metric.** Sensor entities whose native unit maps to a `SensorDeviceClass` (°C, W, kW, kWh,
W/m², Hz, min, h, L) but whose `_attr_device_class` is None; and `DeviceInfo`s carrying
`entry_type`.

**Perturbations — both executed; both move as stated.**
- `_attr_device_class = SensorDeviceClass.ENERGY` on `DHWHeavyDaySensor`:
  **5 → 4** (`sensors with device_class=29 → 30`, and the remaining list is the three °C
  deltas plus `solar_surplus_forecast`);
- `entry_type="service"` in `coordinator.device_info`: `device_entry_type_service`
  **0 → 65**, direction up as stated.

**Fix scope — complete for what the metric measures; the metric is narrower than "all 55
sensors".** I enumerated every native unit in `sensor.py`: 14 °C, 6 kWh, 5 `coordinator.
currency`, 5 kW, 2 `<currency>/kWh`, 2 `PERCENTAGE`, 1 L, 1 W/m², 1 Hz. The checker's unit
map covers none of the currency or percentage units, so **9 sensors are outside the metric
entirely**. Checking them by hand: the currency ones are deliberate — `sensor.py` carries an
explicit comment that Home Assistant only accepts state class `TOTAL` for `MONETARY` while
these are `MEASUREMENT` forecasts, and the settled accumulators *do* carry `MONETARY` (1 use);
the two `PERCENTAGE` ones have no forced class (`BATTERY` is used once where it fits). So the
answer is "no further unmapped device classes across the 55", but the finder's mechanism
paragraph justifies only the three °C exclusions and is silent on the nine the map never
looked at. The three °C sensors are genuinely deltas (displacement, prediction error) where
`TEMPERATURE` would convert wrongly — I agree they are correctly classless.

**Vote: verify, low.** Deciding numbers: `sensors_with_unit_but_no_device_class 5 → 4` and
`device_entry_type_service 0 → 65`.

---

## Summary

| finding | perturbation | outcome | fix scope | vote |
|---|---|---|---|---|
| D10-01 | executed | 0 → 1 (both RESULTs), row flips | complete; stub lacks `_async_abort_entries_match` | **verify** medium |
| D10-02 | executed, both halves | (a) alone 0; (a)+(b) 0 → 2 | complete for the auth class | **verify** medium |
| D10-03 | executed | 4 → 1, null control fixed at 1 | **incomplete for the class**: 6 more unlatched ERROR sites | **verify** low |
| D10-04 | executed, both halves | handler 3 → 2; inside 3 → 3 | files right, enumeration understated (4 more silent paths); line cite 5536 → 4825 | **verify** low |
| D10-05 | executed | 2 → 0, row flips | **complete and exact** (all 15 `available` overrides audited) | **verify** low |
| D10-06 | executed (finder had not) | 11 → 0, `async_setup_defs` 0 → 1 | metric is a lexical proxy; a cosmetic move clears it | **verify** low |
| D10-07 | executed (finder had not) | 0 → 1 | complete | **verify** low |
| D10-08 | executed (finder had not) | 0 → 1, `hass_data` pinned at 24 | lexical proxy; finder's own scope is not fooled | **verify** low |
| D10-09 | executed (finder had not) | 0 → 1 | `[^)]*` regex will false-negative on parenthesised messages | **verify** low |
| D10-10 | executed (finder had not) | 64 → 63 | complete | **verify** low |
| D10-11 | executed (finder had not) | 0 → 1, row flips | complete | **verify** low |
| D10-12 | executed (finder had not) | 0 → 1, row flips; wider grep also 0 | complete | **verify** low |
| D10-13 | **not executed** (one-mypy budget) | — ; 722 reproduced exactly, my AST gives 104 vs 106 | direction not obviously down; see body | **verify** low |
| D10-14 | **not executed** (coverage suite barred) | — ; mechanism confirmed line-by-line; grep half perturbed 0 → 1 | prose 1493 → **1491**; 88.4 % is a lower bound (coordinator.py = 56.5 % of misses) | **verify** low |
| D10-15 | executed, both | 5 → 4; 0 → 65 | metric excludes 9 currency/percentage sensors (checked by hand: no further gaps) | **verify** low |

Fifteen findings, thirteen perturbations executed and every one moved in the stated
direction — including both of the two the finder flagged as having failed first time, which
reproduce their failure exactly under the wrong edit and their success under the right one.
Two perturbations (D10-13, D10-14) were barred by the box constraint and are recorded as
unexecuted rather than guessed; for both, the underlying number was re-derived independently
and agrees.

No refutations. Three corrections for the register: the D10-04 line citation
(coordinator.py:5536 → 4825), the D10-14 missed-statement figure (1493 → 1491), and the
D10-03 fix scope, which should name `async_run_optimization`'s per-cycle `_LOGGER.error(...,
exc_info=True)` alongside the two it lists.
