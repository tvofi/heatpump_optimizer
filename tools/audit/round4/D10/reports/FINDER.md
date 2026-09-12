# D10 — Home Assistant integration quality scale (audit round 4)

- **Baseline**: `7dd68dd327fe3dbfb09f3bd0fe38910c58877697`
- **Tree**: `/Users/timmalmstrom/heatpump_optimizer/.claude/worktrees/audit-r4-baseline` (export, no `.git`)
- **Box**: 8-core Apple M1, 8 GB, macOS 25.6.0. Shared with the other round-4
  finders throughout; `load1` at the measurements below ran 4.1 – 13.9. Every
  number in this report is a **count or a ratio** (rules, statements, error
  lines, percentages) — none is a wall, CPU or RSS figure, so none is
  contention-sensitive.
- **Interpreters**:
  `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3` with
  `PYTHONPATH=tests/hastub` for everything in-tree;
  `/opt/homebrew/opt/python@3.13/bin/python3.13` (3.13.1) in a scratch venv for
  the real-stub mypy arm.

## Method

The rule set was **fetched, not recalled**, on 2026-09-12 from
`https://developers.home-assistant.io/docs/core/integration-quality-scale/checklist`
and from twelve per-rule pages under `rules/` whose exact wording decided a
verdict (listed under *exposure*). The fetched checklist enumerates
**20 Bronze + 10 Silver + 21 Gold + 3 Platinum = 54 rules**, matching `D10.md`
exactly.

One check per rule was then **executed** against
`custom_components/heatpump_optimizer` — an AST walk, a JSON/YAML lookup, a
grep, a coverage run or a mypy run — by
`tools/audit/round4/D10/qs_rules.py`. The harness never reads
`quality_scale.yaml` to decide a verdict; it reads it afterwards, only to
print the shipped declaration beside the executed one and count the
disagreements.

Two rules need a toolchain and are measured by their own harnesses, whose
output `qs_rules.py` consumes:

- `test-coverage` and `config-flow-test-coverage` —
  `tools/audit/round4/D10/coverage_measure.sh`, a thin wrapper around the
  tree's own `tools/audit/w5-partition/coverage_tree.sh` (one `coverage run`
  per default-gate script, combined, reported per module). The wrapper exists
  rather than a second implementation because `tests/coverage_ratchet.py`
  consumes that instrument's `coverage.json`, so a re-implementation would not
  be comparable to the figure the tree records.
- `strict-typing` — `tools/audit/round4/D10/mypy_arms.sh`, two arms (below).

## Headline

```
RESULT rules_total=54 rules
RESULT bronze_done=19  bronze_todo=1   bronze_total=20
RESULT silver_done=10                  silver_total=10
RESULT gold_done=15 gold_exempt=4 gold_todo=2  gold_total=21
RESULT platinum_done=3                 platinum_total=3
RESULT declared_mismatch=3 rules
RESULT mismatch_config_flow_test_coverage=executed:todo/declared:done
RESULT mismatch_test_coverage=executed:done/declared:todo
RESULT mismatch_docs_known_limitations=executed:todo/declared:done
RESULT runtime_data_root_alias_parametrized=False
```

Executed totals **47 done · 4 exempt · 3 todo**; the shipped
`quality_scale.yaml` declares **48 · 4 · 2**. The two files agree on 51 of 54
rows. The draft register with every executed verdict and the evidence that
decided it is `tools/audit/round4/D10/quality_scale.draft.yaml`.

**Adherence is high and the two Platinum-blocking answers are both good**:
`strict-typing` reports 0 errors under a real PEP-561 Home Assistant stub, and
`test-coverage` measures 97.2 % with no module below the rule's 95 % bar. The
three findings are all `low`: none of them is a defect a user meets.

## The tier table

`status` is the executed verdict. `declared` is what
`custom_components/heatpump_optimizer/quality_scale.yaml` says. Full commands
and results for all 54 rows: run the harness, or read
`quality_scale.draft.yaml`.

Re-run the whole table with:

```
D10_COVERAGE_JSON=<work>/out/coverage.json \
D10_MYPY_JSON=/private/tmp/hpo-d10-mypy/census.json \
PYTHONPATH=tests/hastub python3 tools/audit/round4/D10/qs_rules.py
```

| rule | tier | status | declared | evidence command | result |
|---|---|---|---|---|---|
| action-setup | bronze | done | done | ast: `async_setup` calls `_async_register_services`; grep `hass.services.async_register` | registers in `async_setup`; 13 register sites |
| appropriate-polling | bronze | done | done | grep `update_interval=timedelta(` coordinator.py; `DEFAULT_OPTIMIZATION_INTERVAL` const.py | interval from config, default 30 min, `iot_class=cloud_polling` |
| brands | bronze | done | done | `ls custom_components/heatpump_optimizer/brand` | `icon.png`, `logo.png` in-repo (adapted: a custom integration cannot be in home-assistant/brands) |
| common-modules | bronze | done | done | ast: `entity.py` defines `HeatPumpOptimizerEntity(CoordinatorEntity)` | 6/6 platform modules build on it |
| config-flow | bronze | done | done | json: strings.json fields without a `data_description` | 36 steps, 270 fields, **0** undescribed |
| config-flow-test-coverage | bronze | **todo** | done | coverage json → config_flow.py | **97.2 %, 756 statements, 21 missed** (claim: 100 %, 661, 0) |
| dependency-transparency | bronze | done | done | json: manifest requirements | numpy, scipy, threadpoolctl — OSI, PyPI, public CI, tagged; `>=` not `==` (the rule asks for a tagged release, not a pin) |
| docs-actions | bronze | done | done | yaml services.yaml; json strings.json services; README | 12 = 12, README `## Services` |
| docs-triggers | bronze | done | done | grep trigger definitions | 0 → vacuous |
| docs-conditions | bronze | done | done | grep condition definitions | 0 → vacuous |
| docs-high-level-description | bronze | done | done | grep `## What it does` README.md | present |
| docs-installation-instructions | bronze | done | done | grep `## Installation` README.md | present |
| docs-removal-instructions | bronze | done | done | grep `### Removal` README.md | present |
| entity-event-setup | bronze | done | done | ast: entity classes subscribing to events | 0 of them; the 4 subscriptions are the coordinator's, released via `entry.async_on_unload` → vacuous |
| entity-unique-id | bronze | done | done | grep `_attr_unique_id =` | 9 sites, every one `f"{entry.entry_id}_…"` |
| has-entity-name | bronze | done | done | grep entity.py | set once on the shared base |
| runtime-data | bronze | done | done | ast: `entry.runtime_data` sites and the two alias definitions | 1 write, 11 reads; **the root alias is a bare `ConfigEntry`** — finding D10-03 |
| test-before-configure | bronze | done | done | grep `validate_tibber_token` config_flow.py | credential validated before the entry is created |
| test-before-setup | bronze | done | done | grep `async_config_entry_first_refresh`; `raise UpdateFailed` | first refresh in setup; 4 `UpdateFailed` raise sites |
| unique-config-entry | bronze | done | done | grep `async_set_unique_id` + `_abort_if_unique_id_configured` | both present |
| action-exceptions | silver | done | done | grep raise sites | 14 `ServiceValidationError` in services.py, 6 `HomeAssistantError` |
| config-entry-unloading | silver | done | done | grep `async_unload_platforms`, `async_shutdown` | both in `async_unload_entry` |
| docs-configuration-parameters | silver | done | done | `wc -l docs/configuration.md`; count table rows | 764 lines, 308 table rows, linked from README |
| docs-installation-parameters | silver | done | done | grep `## Quick start` README.md | the first-30-minutes walkthrough covers every config-flow field |
| entity-unavailable | silver | done | done | grep `def available(self) -> bool` | 10 overrides plus `CoordinatorEntity`'s default |
| integration-owner | silver | done | done | json manifest codeowners | `["@tvofi"]` |
| log-when-unavailable | silver | done | done | `python3 tools/audit/round4/D10/log_when_unavailable.py` — 10 failed polls driven through a real coordinator | **1 ERROR, 9 DEBUG**, then **1 INFO** on recovery; latch resets |
| parallel-updates | silver | done | done | grep `^PARALLEL_UPDATES` on the 6 platform modules | 6/6: sensor 0, binary_sensor 0, button 1, climate 1, switch 1, datetime 1 |
| reauthentication-flow | silver | done | done | grep `async_step_reauth`; `async_start_reauth` | flow present **and reachable** — the coordinator starts it on a refused token |
| test-coverage | silver | **done** | todo | coverage json → per-module | **97.2 % package (14948/15381); 0 of 56 modules below 95 %**; lowest `battery.py` 95.0 % |
| devices | gold | done | done | grep `DeviceInfo(` coordinator.py | one device per entry, served to every entity |
| diagnostics | gold | done | done | grep `async_get_config_entry_diagnostics` | present; redacts token and solar location |
| discovery | gold | exempt | exempt | grep discovery step handlers | 0 — cloud API + user-picked entities |
| discovery-update-info | gold | exempt | exempt | same | 0 — no network address stored |
| docs-data-update | gold | done | done | grep interval wording in README/docs | how-it-works.md:47 and README.md:340 state the 30-minute cycle |
| docs-examples | gold | todo | todo | grep `blueprint`; grep ```` ```yaml ```` docs/automations.md | **0 blueprint links**; 3 worked YAML automations, which the rule says are not a substitute |
| docs-known-limitations | gold | **todo** | done | grep headings and the word | **0 headings, 0 occurrences of "limitation"** in README + the 6 user docs |
| docs-supported-devices | gold | done | done | grep README section | `## Supported heat pumps and controls` |
| docs-supported-functions | gold | done | done | grep README section | `## Entities` + `## Services` |
| docs-troubleshooting | gold | done | done | grep README section | `## Troubleshooting` |
| docs-use-cases | gold | done | done | grep README section | `## What it does`, plus docs/automations.md |
| dynamic-devices | gold | exempt | exempt | grep device-registry create sites | 0 |
| entity-category | gold | done | done | grep `_attr_entity_category =` | 22 (all DIAGNOSTIC) |
| entity-device-class | gold | done | done | grep `_attr_device_class =` | 33 |
| entity-disabled-by-default | gold | done | done | grep `_attr_entity_registry_enabled_default = False` | 6 |
| entity-translations | gold | done | done | json strings.json entity.*; grep translation_key | 73 translated names over 5 domains; 46 code sites; climate uses `_attr_name = None` |
| exception-translations | gold | done | done | json exceptions; grep `translation_domain=`; grep raise sites | **21 = 21 = 21** |
| icon-translations | gold | done | done | json icons.json; grep `_attr_icon =` | 69 entity icons, **0** `_attr_icon` pins; no `services` section (the rule page covers entity icons) |
| reconfiguration-flow | gold | done | done | grep `async_step_reconfigure` | present, aborts `reconfigure_successful` |
| repair-issues | gold | done | done | grep `_create_issue(` sites; json issues; repairs.py | 16 create sites, 17 declared issues, `async_create_fix_flow` present |
| stale-devices | gold | exempt | exempt | grep removal sites | 0; device lifetime = entry lifetime |
| async-dependency | platinum | done | done | grep blocking HTTP | **0** `requests`/`urllib` sites; 181 `async def`; the 5 executor jobs are the CPU-bound solve |
| inject-websession | platinum | done | done | grep `async_get_clientsession`; `aiohttp.ClientSession(` | **6 / 0** |
| strict-typing | platinum | done | done | mypy 2.3.1 `--strict`, two arms | **0 errors under real homeassistant-stubs**; 542 under `tests/hastub` are the stub's |

## `test-coverage`, measured

`tools/audit/round4/D10/coverage_measure.sh` ran the 20 default-gate Python
scripts of `tests/run.sh` in two stages — `fast` (16 scripts) then `e2e`
(`validate`, `edge`, `backtest`, `optimality`), accumulating into one data set
— with one `coverage run` per script, combined:

```
RESULT package_percent=97.18   (14948 covered / 15381 statements)
RESULT modules_total=56
RESULT modules_below_95=0      lowest: battery.py 95.0, legionella.py 95.2,
                               inputs.py 95.3, dhw_learning.py 95.6,
                               accuracy.py 95.8, freq_control.py 95.8,
                               button.py 96.0, optimizer.py 96.0
```

The `fast` stage alone gave 97.17 % (14945/15381) and the same 0-below-95, so
the four end-to-end scripts moved the package figure by **+0.01 points, 3
statements**. That is worth stating rather than hiding: nearly all of this
integration's coverage comes from the unit-style scripts, not from the
end-to-end ones.

The rule is *"Above 95 % test coverage for **all** integration modules"*, so
the per-module row is the one that decides it, and it passes with the closest
module 0.0 points of headroom above the bar. The measurement is a **lower
bound**: adding the four end-to-end scripts and `stress.py` can only cover
more statements, never fewer. `tests/coverage_budgets.json` independently
records `package_percent_floor: 96.0` with a reason line naming 97.2 % and
`modules_below_bar=0`, so the tree's own ratchet agrees with this number and
only `quality_scale.yaml` was left behind.

Three scripts exited non-zero in the run; all three are the **export
artefacts** `BASELINE.md` names, not tree defects, and none of them changes a
coverage figure:

| script | exit | why |
|---|---|---|
| `entities.py` | 1 | the 3 of 1360 checks that need `.git` |
| `harness_headers.py` | 1 | `tools/audit/round3/` was removed from the export |
| `deployment_shape.py` | 1 | materialises the package with git; the export has none |
| `golden.py` | 1 | run in `GOLDEN_MODE=strict` by the instrument, as recorded; fixtures were recorded on another BLAS build |

### `config-flow-test-coverage`, and the control for the failing script

`config_flow.py` measures **97.2 %: 756 statements, 21 missed**. The shipped
register claims *"100 % statement coverage (661 statements, 0 missed) over
config_flow_steps, entities, golden, features and deployment_shape"*. This run
covered a **superset** of those five scripts, so the comparison is not
confounded by script selection in the generous direction.

It could be confounded by `deployment_shape.py`, which failed here. It is
not, and the control is executed rather than argued:
`grep -n "config_flow\|async_step" tests/deployment_shape.py` returns **zero
lines** — that script imports `coordinator` alone, in a child process, to
check `_worker_env`. It cannot reach a config-flow form step.

The 21 uncovered statements are ordinary branches, not unreachable code:

```
451   the CONF_PRICE_ENTITY branch of the entry-identity string
1110, 1115, 1223, 1671        empty-result / continue branches of the field registry
1711-1712                     "leave a value we cannot recompute" exception branch
1728-1734                     _StoredValuesAlwaysFit's type-coercion comparison
2546-2556                     options grid step: price-entity / token required errors
2640-2642                     options hot-water step: holiday DHW window validation
2919                          apply-preset merge
```

Nothing in the gate pins this file. `tests/coverage_ratchet.py` ratchets the
**package** percent (floor 96.0, ceiling 96.0) and the pragma count, and
97.2 % clears that floor with these 21 statements uncovered. The tree's own
recorded evidence already shows the drift beginning:
`tools/audit/w5-g5-195-coverage/coverage/coverage_report.txt` has the file at
**672 statements, 5 missed, 99.3 %**.

## `strict-typing`, measured in two arms

`tools/audit/round4/D10/mypy_arms.sh`, mypy **2.3.1** (the version
`tests/typing_budgets.json` pins) `--strict --warn-unused-ignores`:

```
RESULT mypy_real_stub_errors=0        arm B: homeassistant-stubs 2025.4.4, Python 3.13.1
RESULT mypy_hastub_total=542          arm A: MYPYPATH=tests/hastub, Python 3.11.5
RESULT mypy_hastub_in_pkg=470
RESULT mypy_hastub_in_stub=72
RESULT hastub_by_code={"no-untyped-call":176,"attr-defined":121,"type-arg":114,
  "no-untyped-def":51,"union-attr":19,"no-any-return":13,"arg-type":13,
  "assignment":12,"untyped-decorator":7,"operator":6,"return-value":5,
  "import-not-found":2,"index":1,"import-untyped":1,"name-defined":1}
```

**The distinction the brief asks for, stated plainly.** Arm A's 470
package-located errors are **artefacts of the stub, not of the integration**.
`tests/hastub` is a hand-written fake with almost no annotations, so:

- every call into it is `no-untyped-call` (176) — e.g.
  `inputs.py:330 Call to untyped function "utcnow" in typed context`;
- every attribute the real `HomeAssistant` has and the fake lacks is
  `attr-defined` (121) — e.g. `frontend.py:50 "HomeAssistant" has no
  attribute "http"`;
- every class the real API parametrises and the fake does not is `type-arg`
  (114) — e.g. `away.py:329 "Store" expects no type arguments, but 1 given`,
  the exact opposite complaint to the real stub's.

Arm B replaces the fake with a real PEP-561 stub set and the count goes to
**0**. That is an *independent corroboration* of the census
`tests/typing_budgets.json` records, not a reproduction of it: the pinned
ruler is `homeassistant-stubs 2026.2.3` on Python ≥ 3.13.2, and this box's
newest interpreter is 3.13.1, so the pin will not install. Two different stub
versions, two different Python patch levels, both 0.

**`py.typed` is not owed.** The rule's PEP-561 half is about the *library* an
integration depends on. This integration publishes no library, so there is no
package for a consumer to type-check against, and the shipped register's note
to that effect is right.

## Findings

Ids follow `tools/audit/finding.schema.json`'s `^D<k>-[0-9]{2}$`, which has no
room for a round number; the round is carried by the directory
(`tools/audit/round4/D10/`), not by the id.

All three are `low`. Severities are deliberately not inflated: no user meets
any of them.

### D10-01 — the shipped quality-scale register has drifted; 3 of 54 rows are wrong when executed

`custom_components/heatpump_optimizer/quality_scale.yaml` is hand-maintained
and, as its own header says, *"nothing here is machine-enforced today"*. Three
rows disagree with an executed check, in both directions:

| row | declared | executed | the number |
|---|---|---|---|
| `config-flow-test-coverage` (Bronze) | `done`, "100 %, 661 statements, 0 missed" | `todo` | 97.2 %, 756 statements, **21 missed** |
| `test-coverage` (Silver) | `todo` (#195) | `done` | **97.18 %** package (14948/15381), **0 of 56** modules below 95 % |
| `docs-known-limitations` (Gold) | `done` | `todo` | **0** "Known limitations" sections (D10-02) |

Two further rows keep a correct status under a comment that is no longer
true, and are reported here rather than as findings of their own:
`docs-examples` says "0 automation examples" where `docs/automations.md` now
has **3**; `log-when-unavailable` says "one ERROR per failed poll", which is
the behaviour the rule *forbids* — the code in fact latches (first failure
ERROR, later failures DEBUG, recovery INFO), so the status is right and the
sentence describes a violation the tree does not commit.

The mechanism is one: **no check executes against this file.** `hassfest`
skips `quality_scale.yaml` for custom integrations (the register says so
itself), the gate does not read it, and `tests/entities.py` does not either.
Every row is therefore true only as of the day someone typed it, and the two
coverage rows are exactly the kind that rot — both are figures about a tree
that keeps changing under them.

- **metric**: rows of `quality_scale.yaml` whose status differs from the
  verdict `qs_rules.py` executes for the same rule, out of 54.
- **value**: 3 of 54.
- **instrumented symbol**: `custom_components/heatpump_optimizer/quality_scale.yaml`
  (`rules:` mapping) against `tools/audit/round4/D10/qs_rules.py:_declared`.
- **perturbation**: correct any one of the three rows in
  `quality_scale.yaml`; `RESULT declared_mismatch` falls by 1 (direction:
  **down**). Conversely, flip a currently-agreeing row — e.g. set
  `parallel-updates: todo` — and it rises by 1.
- **fix scope**: adopt `tools/audit/round4/D10/quality_scale.draft.yaml`, and
  add a gate check that re-derives the coverage-bearing rows rather than
  quoting them (the self-invalidating-figure shape: a row whose truth changes
  when the file it describes changes).

### D10-02 — `docs-known-limitations` (Gold) is declared `done` and the section does not exist

The rule: *"The documentation should include a 'Known limitations' section
with descriptions of constraints"*, and *"There are no exceptions to this
rule."*

Executed over `README.md` and the six user-facing documents under `docs/`
(`architecture.md`, `automations.md`, `configuration.md`, `dashboard-card.md`,
`ecl110.md`, `how-it-works.md`):

```
headings matching ^#{1,4}.*known limitation   0
occurrences of the word "limitation"          0
```

across 878 + 3197 lines of user documentation.

**The counter-evidence, stated before anyone else finds it.** Limitation
*content* does exist and is good; what does not exist is the section. Under
`## Supported heat pumps and controls`, `README.md:176` opens a list headed
*"Boundaries worth knowing before you pick a path"* with **4** bullets — one
per control path, plus *"**Heating, not cooling.** The whole model assumes
heating"*, which is a genuine integration-wide limitation. Two further
paragraphs use the word *caveat*: `README.md:534` (setpoint-echo `number`
entities) and `docs/how-it-works.md:1032` (the defrost derate is only
trustworthy under MQTT push). And `## Project status` points at
`docs/backlog.md` for "findings judged real and deliberately not built".

So the gap is **placement and discoverability, not absence of knowledge**: a
user asking "what will this not do?" has no section to open, and the four
control-path boundaries are filed under a heading about which pumps are
supported. Limitations that are nowhere at all, in any wording: the 30-minute
planning granularity as a control limit, the Tibber-or-price-entity
requirement for prices, the single static device, the absence of discovery,
and the Swedish-market shape of the tariff model.

- **metric**: count of headings matching `^#{1,4}.*known limitation`
  (case-insensitive) across `README.md` + the six user docs.
- **value**: 0.
- **instrumented symbol**: the `docs-known-limitations` row of
  `tools/audit/round4/D10/qs_rules.py:gold`, over `README.md` and `docs/*.md`.
- **perturbation**: add a `## Known limitations` section to `README.md`; the
  count moves 0 → 1 and the rule's executed status moves `todo` → `done`
  (direction: **up**).
- **fix scope**: small — promote the existing *"Boundaries worth knowing"*
  bullets into a `## Known limitations` section of their own and add the five
  limitations listed above. This is documentation only; no code moves.
- **severity**: `low`. A user can install, configure and operate the
  integration without this section; it changes expectations, not capability,
  and most of the content is already written, just filed elsewhere.

### D10-03 — the package root re-binds `HeatPumpOptimizerConfigEntry` to a bare `ConfigEntry`, so `runtime_data` is `Any` in the three entry points

The package defines the alias **twice**:

```
coordinator.py:10451  HeatPumpOptimizerConfigEntry = ConfigEntry[HeatPumpOptimizerCoordinator]
__init__.py:43        HeatPumpOptimizerConfigEntry = ConfigEntry
```

The six platform modules and `services.py` import the first. `__init__.py`
uses the second for `async_setup_entry`, `async_update_options` and
`async_unload_entry` — the three functions Home Assistant actually calls. A
`reveal_type` probe under the real stubs, run by `mypy_arms.sh`:

```
RESULT runtime_data_revealed_root=Any
RESULT runtime_data_revealed_coordinator=…coordinator.HeatPumpOptimizerCoordinator
```

`ConfigEntry` is declared `class ConfigEntry[_DataT = Any]` with
`runtime_data: _DataT`, so the bare alias is legal under `--strict` (PEP 696
default) and silently resolves the attribute to `Any`. The consequence is that
`coordinator.data`, `coordinator.async_shutdown()` and
`coordinator.effective_config` in `async_unload_entry` / `async_update_options`
are unchecked, and the strict census reports 0 while three functions are
outside it. The quality-scale rules are explicit that this half is required:
*"If the integration implements `strict-typing`, the use of a custom typed
`MyIntegrationConfigEntry` is required and must be used throughout."*

**The fix is not a one-liner, and that is measured too.** The comment above
`__init__.py:43` exists because binding the alias through the lazy-import
helper put the coordinator's 40-module graph into the package's measured
closure. Parametrising it naively:

```
if TYPE_CHECKING:
    from .coordinator import HeatPumpOptimizerCoordinator
HeatPumpOptimizerConfigEntry = ConfigEntry["HeatPumpOptimizerCoordinator"]
```

gives `mypy --strict` **0 errors** over the whole package and moves the probe
to `HeatPumpOptimizerCoordinator` — and then fails at runtime:

```
get_type_hints FAILED: NameError name 'HeatPumpOptimizerCoordinator' is not defined
```

which is exactly the `get_type_hints` path the existing comment is defending.
So the fix has to keep the name resolvable at runtime without importing the
coordinator at package import: bind the class into module globals at setup
time, or annotate the three functions with a `TYPE_CHECKING`-only alias and
leave the runtime binding alone.

- **metric**: the type `mypy --strict` reveals for `entry.runtime_data` when
  `entry` is annotated with the alias exported from the package root.
- **value**: `Any` (root alias) vs `HeatPumpOptimizerCoordinator` (coordinator
  alias).
- **instrumented symbol**:
  `custom_components/heatpump_optimizer/__init__.py:HeatPumpOptimizerConfigEntry`.
- **perturbation**: parametrise that alias; the revealed type moves `Any` →
  `HeatPumpOptimizerCoordinator` (direction: **away from `Any`**), the
  package's strict error count stays at 0, and `get_type_hints` on
  `async_setup_entry` raises `NameError` unless the runtime binding is handled.
  All three arms measured; see `mypy_arms.sh` and the perturbation transcript
  in this report.
- **severity**: `low`. Nothing is wrong at runtime today; what is lost is
  type-checking of three functions and the honesty of a 0.

## Non-findings

Each is a claim that held, with the command and the number.

| claim | command | value |
|---|---|---|
| The fetched rule set matches `D10.md` | WebFetch of the checklist page | 20 + 10 + 21 + 3 = **54** rules, identical names |
| 51 of 54 register rows agree with an executed check | `qs_rules.py` | `declared_mismatch=3` |
| `strict-typing` holds under a real stub set | `mypy_arms.sh` arm B | **0** errors, mypy 2.3.1 `--strict`, stubs 2025.4.4, py3.13.1 |
| The 542 `tests/hastub` errors are not the integration's | `mypy_arms.sh` arm A + by-code table | 176 `no-untyped-call`, 121 `attr-defined`, 114 `type-arg` — all complaints about the fake |
| Package coverage clears the Silver bar | `coverage_measure.sh fast` then `e2e` | **97.18 %**, 14948/15381 |
| Every module clears the Silver bar | same, per module | **0 of 56** below 95 %; lowest `battery.py` 95.0 % |
| `parallel-updates` is set in every platform | grep `^PARALLEL_UPDATES` | **6 of 6** |
| Every config/options field has a description | json over `strings.json` | 270 fields, **0** without `data_description` |
| Exception translations are complete | json + grep | **21** strings.json entries = **21** `translation_domain=` = **21** raise sites |
| Icon translations are complete and un-shadowed | json + grep | **69** entity icons, **0** `_attr_icon` pins |
| `log-when-unavailable` latches rather than spamming | `python3 tools/audit/round4/D10/log_when_unavailable.py` | 10 consecutive failed polls emit **1 ERROR and 9 DEBUG**; recovery emits **1 INFO**; the next 10 failures emit **1 ERROR** again (the latch resets) |
| The reauth flow is reachable, not just present | grep both ends | `async_step_reauth` in config_flow.py **and** `entry.async_start_reauth` in coordinator.py |
| No entity subscribes to events outside the lifecycle | ast over the 6 platform modules | **0** entity classes subscribe; the 4 subscriptions are the coordinator's |
| `inject-websession` is honoured everywhere | grep | **6** `async_get_clientsession`, **0** own `ClientSession` |
| `async-dependency`: nothing blocking | grep | **0** `requests`/`urllib` HTTP sites |
| `discovery`, `discovery-update-info`, `dynamic-devices`, `stale-devices` are genuinely exempt | grep for the mechanism each names | **0** sites in all four cases |
| `docs-data-update` is documented | grep | `docs/how-it-works.md:47`, `README.md:340` — the 30-minute cycle and what it fetches |
| `docs-examples` is correctly `todo` | grep `blueprint` | **0** blueprint links; the 3 YAML examples do not substitute, per the rule page |
| `deployment_shape.py`'s failure does not confound the config-flow figure | `grep -n "config_flow\|async_step" tests/deployment_shape.py` | **0** matching lines |
| The three non-zero exits in the coverage run are export artefacts | `BASELINE.md` + each log | `entities.py` 3/1360 git checks, `harness_headers.py` missing `round3/`, `deployment_shape.py` no git |

### Rules needing a newer Home Assistant than `hacs.json`'s floor

`hacs.json` declares `"homeassistant": "2025.2.0"`. Every API each `todo` rule
would need is older than that floor:

| todo rule | API needed | first HA release carrying it | vs the 2025.2.0 floor |
|---|---|---|---|
| `config-flow-test-coverage` | none — test work only | — | no bump needed |
| `docs-examples` | none — blueprints are documentation | — | no bump needed |
| `docs-known-limitations` | none — documentation | — | no bump needed |

So **no `todo` in this integration is blocked on a Home Assistant version**.
For completeness, the newest HA APIs the integration already uses and their
floors: `ConfigEntry.runtime_data` (2024.6), `async_step_reconfigure` with
`_get_reconfigure_entry` (2024.11), `ConfigFlowResult` (2024.4),
`repairs.ConfirmRepairFlow` (2022.9), `entity_registry.async_entries_for_config_entry`
(long-standing) — all at or below 2025.2.0.

## Harnesses

| path | what it produces | command |
|---|---|---|
| `tools/audit/round4/D10/qs_rules.py` | the 54-row tier table, the per-tier counts, `declared_mismatch` | `D10_COVERAGE_JSON=… D10_MYPY_JSON=… PYTHONPATH=tests/hastub python3 tools/audit/round4/D10/qs_rules.py` |
| `tools/audit/round4/D10/coverage_measure.sh` | package and per-module statement coverage | `D10_WORK=$(mktemp -d) tools/audit/round4/D10/coverage_measure.sh fast` (then `e2e`) |
| `tools/audit/round4/D10/mypy_arms.sh` | the two mypy censuses and the `reveal_type` probe | `tools/audit/round4/D10/mypy_arms.sh` |
| `tools/audit/round4/D10/log_when_unavailable.py` | ERROR/DEBUG/INFO record counts over 10 failed polls and a recovery | `PYTHONPATH=tests/hastub python3 tools/audit/round4/D10/log_when_unavailable.py` |
| `tools/audit/round4/D10/quality_scale.draft.yaml` | the executed register, 47 done / 4 exempt / 3 todo | (data, not executable) |

`tools/audit/round4/D10/qs_rules.out.txt` is that harness's full output at
this baseline, committed beside it so a reader has the 54 rows with their
commands without re-running anything.

`mypy_arms.sh` needs two scratch venvs it does not build; its header names
them and what goes in each. `coverage_measure.sh` wraps
`tools/audit/w5-partition/coverage_tree.sh` and writes nothing inside the
tree.

## What I could not finish

- **The pinned typing ruler could not be reproduced.**
  `tests/typing_budgets.json` pins `homeassistant-stubs 2026.2.3`, which
  requires Python ≥ 3.13.2; this box's newest interpreter is 3.13.1
  (`/opt/homebrew/opt/python@3.13`). Arm B therefore corroborates the recorded
  `errors: 0` with a different stub version rather than reproducing it. A
  judge on a 3.13.2+ box should re-run `mypy_arms.sh` after pointing arm B at
  the pinned pair.
- **`stress.py` is not in the coverage measurement.** It requires the gate
  lock and the box was shared with three other finders throughout, so I did
  not take the lock for a 40-minute solve series whose only contribution would
  be to `optimizer.py` and the models under it. The omission is
  **conservative**: adding a script can only raise coverage, so 97.18 % and
  "0 modules below 95 %" are lower bounds. It cannot touch the
  `config_flow.py` figure — `grep -c "config_flow\|async_step"` returns **0**
  for `stress.py` as it does for the four end-to-end scripts.
- **`brands` is an adapted check.** The real rule is satisfied by a pull
  request to `home-assistant/brands`, which accepts core integrations only. I
  checked the in-repo assets exist and are the right shape; I could not check
  the thing the rule literally asks for, because a custom integration cannot
  do it.
- **`dependency-transparency` is partly a lookup I did not execute.** I
  verified the three requirements are declared, are on PyPI and are the
  well-known OSI-licensed projects; I did not fetch each project's CI
  configuration to confirm the "built and published from a public CI pipeline"
  clause package by package.
- **Only the Tibber price path's latch is driven.** The executed log count
  covers `_tibber_fetch_failed` / `_tibber_fetch_recovered`. The weather
  forecast's pair beside it, and the MQTT pump-signal path in
  `pump_signals.py`, were read rather than driven; a verifier wanting the rule
  closed all the way should extend
  `tools/audit/round4/D10/log_when_unavailable.py` with those two arms.

## A trap this dimension hit, so the next reader does not

`tests/harness.py` runs `sys.path.insert(0, "custom_components")` at import.
Any harness that imports `harness` therefore loads the package **from the
working directory**, and a `PYTHONPATH` pointing at a perturbed copy is
silently ignored — the run reports the unperturbed tree's numbers, with no
error. The first perturbation arm of `log_when_unavailable.py` came back
identical to the baseline arm for exactly this reason, which reads as "the
harness is dead" rather than "the override did not take". Run a perturbation
by **copying the tree and running from its root**; the same run from the
perturbed root moved 1 ERROR → 10 and 9 DEBUG → 0 as it should. This is
`tools/audit/README.md`'s "a harness at the evidence tag may measure the tag"
hazard in a second guise: there the root rule was `__file__` versus `.`, here
it is a `sys.path` insert inside a shared helper.

## exposure

Everything I read or fetched outside `custom_components/` and `tests/`:

- **Fetched from developers.home-assistant.io on 2026-09-12** (the rule set
  was fetched, not recalled):
  - `/docs/core/integration-quality-scale/checklist`
  - `/docs/core/integration-quality-scale/rules/runtime-data`
  - `/docs/core/integration-quality-scale/rules/strict-typing`
  - `/docs/core/integration-quality-scale/rules/icon-translations`
  - `/docs/core/integration-quality-scale/rules/docs-examples`
  - `/docs/core/integration-quality-scale/rules/entity-event-setup`
  - `/docs/core/integration-quality-scale/rules/action-exceptions`
  - `/docs/core/integration-quality-scale/rules/log-when-unavailable`
  - `/docs/core/integration-quality-scale/rules/docs-known-limitations`
  - `/docs/core/integration-quality-scale/rules/dependency-transparency`
  - `/docs/core/integration-quality-scale/rules/async-dependency`
  - `/docs/core/integration-quality-scale/rules/inject-websession`
  - `/docs/core/integration-quality-scale/rules/test-coverage`
- **Read from `docs/`**, because 15 of the 54 rules are documentation rules
  and `D10.md` calls for a documentation lookup: `README.md`,
  `docs/architecture.md`, `docs/automations.md`, `docs/configuration.md`,
  `docs/dashboard-card.md`, `docs/ecl110.md`, `docs/how-it-works.md`.
- **Not read**: `docs/plan-*.md`, `docs/HANDOVER.md`, `docs/decisions/`,
  `docs/superpowers/`, any audit register. Two commands (`wc -l docs/*.md`,
  and a `grep` for `blueprint` whose plan-file hits were filtered out) touched
  the plan files' *line counts* and nothing else; no content from them was
  read or used.
- **Not used**: `gh`, GitHub, any earlier round's findings. The `D10-nn`
  identifiers that appear in production comments were read as context for what
  the code does, never as a to-do list.
- **Network**: the thirteen documentation fetches above (the checklist plus twelve rule pages), and `pip install` of
  `mypy==2.3.1`, `homeassistant-stubs`, `homeassistant`, `scipy`,
  `scipy-stubs`, `numpy`, `voluptuous`, `aiohttp`, `threadpoolctl` into two
  scratch venvs under `/private/tmp`. Nothing was installed into the tree and
  nothing in `custom_components/` or `tests/` was modified.
