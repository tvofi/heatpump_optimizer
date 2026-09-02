# D10 round 2, seat C — documentation, dependency transparency, integration owner

Auditor D10-C, fresh eyes, pinned export of `b39fc6f01f4caee9d3ef17bce5f0b4561392fdb9`
(no `.git`, `docs/audit-*.md`, `docs/backlog.md`, `RELEASE_NOTES.md` stripped by design).
17 assigned rules: the 14 `docs-*` instruments plus `dependency-transparency`
(bronze, web-lookup) and `integration-owner` (silver). All checks are counts
(contention-immune), re-emitted by two harnesses under this directory.

## Method

1. **Doc surface inventory.** The export's doc corpus is `README.md` plus the
   8 surviving `docs/*.md` files (architecture, configuration, dashboard-card,
   ecl110, how-it-works, plan-card-decomposition, plan-open-issues,
   plan-v4.0.0-program). The task brief's "11 docs/*.md" counts the three
   files stripped from the export (audit register, backlog, release notes);
   the audit runs on what is shipped to a user plus README, which is the right
   corpus for a documentation rule.
2. **doc_coverage.py** (single command `python3 tools/audit/round2/D10/C/doc_coverage.py`)
   derives every doc number from the tree:
   - actions parsed from `services.yaml` top-level keys, matched as
     word-boundary strings across the corpus;
   - triggers/conditions counted from platform exports in the integration
     code (`async_get_triggers`, `device_automation`, ...): zero of either;
   - presence rules located by heading regex with (file, line) DETAIL lines;
   - entity inventory: sensor instantiations inside `sensor.py`'s
     `async_setup_entry` list plus concrete classes in binary_sensor/button/
     climate/switch, vs the counts the README claims; `PLATFORMS` from
     `const.py` vs README platform mentions;
   - config/options parameters: every `vol.Required|Optional|Default(CONF_*)`
     key in `config_flow.py` (140 distinct), resolved to its string value via
     `const.py` (`CONF_NAME` resolved from `homeassistant.const`), then
     matched two ways — literal key string, or the human-readable setting
     label in `docs/configuration.md`'s field tables (labels wrap across
     lines, so the corpus is whitespace-normalised). `after_save` is excluded
     as a non-persisted dialog-navigation field (`config_flow.py:1616` pops
     it in `_save_or_menu` before anything persists — verified by regex in
     the harness).
   - automation examples: regex `service:\s*heatpump_optimizer\.|action:\s*-\s*service`
     (case-insensitive) across the corpus.
3. **dep_transparency.sh** (single command `bash tools/audit/round2/D10/C/dep_transparency.sh`)
   — for each manifest requirement (numpy>=1.24.0, scipy>=1.10.0,
   threadpoolctl>=3.5.0): PyPI metadata JSON (presence, license string /
   OSI classifier, project_urls.source), public CI as the file count of the
   source repo's `.github/workflows` via the GitHub contents API
   (unauthenticated; third-party repos only — the export's own repo was not
   touched), and version-to-tag correspondence via `git ls-remote --tags`
   for both the current PyPI version and the manifest floor. Also parses
   `manifest.json` codeowners and checks the account endpoint.
4. HTTP from the harnesses goes through `curl` (the audit box's framework
   Python has no CA bundle; urllib fails TLS verification).

## Tier table

| rule | tier | status | command | number |
|---|---|---|---|---|
| docs-actions | bronze | done | `python3 tools/audit/round2/D10/C/doc_coverage.py` | 11/11 actions covered, 0 uncovered |
| docs-triggers | bronze | done (vacuous) | same | 0 triggers provided |
| docs-conditions | bronze | done (vacuous) | same | 0 conditions provided |
| docs-high-level-description | bronze | done | same | 1 section (README.md:28 "What it does") |
| docs-installation-instructions | bronze | done | same | 5 sections (README:150/152/160; dashboard-card.md:378/398) |
| docs-removal-instructions | bronze | done | same | 1 section (README.md:167 "Removal") |
| docs-configuration-parameters | silver | done | same | 139/139 persisted fields documented (95 by key + 44 by label), 0 undocumented |
| docs-installation-parameters | silver | done | same | 64/64 persisted setup-flow fields documented |
| docs-data-update | gold | done | same | 3 sections (README:459; how-it-works.md:45,47 "every optimization interval (30 minutes by default)") |
| docs-examples | gold | done — **finding D10-01** | same | 0 automation examples |
| docs-known-limitations | gold | done | same | 2 limitation sections + 6 caveat statements |
| docs-supported-devices | gold | done | same | interfaces documented in 6 files |
| docs-supported-functions | gold | done | same | entity delta 0 (65 actual = 65 documented; platforms 5/5) |
| docs-troubleshooting | gold | done | same | 1 section, 6 problem entries (README.md:601) |
| docs-use-cases | gold | done | same | 9 use-case narratives (README.md:76–134) + Quick start |
| dependency-transparency | bronze | done | `bash tools/audit/round2/D10/C/dep_transparency.sh` | 12/12 sub-checks pass (3 deps × 4) |
| integration-owner | silver | done | same | 1 codeowner, account HTTP 200 |

## Finding

### D10-01 — No automation example anywhere in the shipped documentation (docs-examples, gold)

**Claim.** Zero automation examples exist across README.md and all 8
`docs/*.md` files (regex `service:\s*heatpump_optimizer\.|action:\s*-\s*service`,
case-insensitive), even though the documentation twice directs users to build
automations — `docs/configuration.md:55` "the plan is published on sensors for
your own automations to act on" and `docs/plan-v4.0.0-program.md:1241` "a
two-line automation feeds it straight to the charger" (Power Headroom → EV
charger) — without ever showing one.

**Evidence.** `RESULT docs_automation_examples=0 examples`,
`RESULT docs_automation_sections=0 sections` from
`python3 tools/audit/round2/D10/C/doc_coverage.py` (count metric; exact; load1
2.56, thread_factor 1.0 at capture; fan-out box, counts are
contention-immune). The Services sections themselves are otherwise complete:
11/11 actions with full field tables (README:428–457, configuration.md:533–641)
— what is missing is any worked `automation:` YAML exercising a service or an
entity. `docs/dashboard-card.md`'s "Example configs" are Lovelace card
configs, not automations.

**Instrumented symbol.** `services.yaml:actions` (the 11 registered actions)
vs the `README.md` + `docs/*.md` corpus — the artifact the rule couples.

**Perturbation.** `HPO_DOC_PERTURB_FILE=tools/audit/round2/D10/C/perturb_automation_example.md
python3 tools/audit/round2/D10/C/doc_coverage.py` → `RESULT
docs_automation_examples=1 examples` (executed; the committed file adds one
worked `heatpump_optimizer.set_mode` automation). Direction: **up**. The same
edit made in README.md's Services section moves the baseline number.

**Metric definition.** Count of YAML automation snippets invoking a
`heatpump_optimizer` service (case-insensitive `service:\s*heatpump_optimizer\.`
or `action:\s*-\s*service`) across README.md + docs/*.md.

**Severity.** low (docs gap; the service tables and field ranges are
complete, so no user-visible misuse — only friction for the automation-first
user the docs themselves address). **Stop-rule class.** hygiene.
**Files.** README.md, docs/configuration.md.
**Proposed fix scope.** One worked example under README "## Services" — the
Power Headroom → EV-charger feed the program doc already describes in prose
is the natural candidate — plus optionally one `set_mode` price-trigger
example in configuration.md's Services section.

## Non-findings (all held, with the executed number)

| # | claim | command | value |
|---|---|---|---|
| 1 | docs-actions: all 11 services.yaml actions (run_optimization, set_mode, set_thermal_parameters, simulate_plan, assign_entity, apply_topology, apply_schedule, apply_manual_plan, clear_manual_plan, restore_learned_snapshot, diagnose_interval) are named in README.md and docs/configuration.md | doc_coverage.py | 11/11 covered, 0 uncovered |
| 2 | docs-triggers: the integration provides no trigger platform, so the rule (document what is provided) is vacuously satisfied | doc_coverage.py | 0 provided triggers |
| 3 | docs-conditions: same basis | doc_coverage.py | 0 provided conditions |
| 4 | docs-high-level-description: README.md:1–7 plus "## What it does" (README.md:28) state the purpose in plain terms | doc_coverage.py | 1 section |
| 5 | docs-installation-instructions: HACS and manual install paths with prerequisites (README "Requirements":138) present | doc_coverage.py | 5 sections |
| 6 | docs-removal-instructions: README.md:167 "### Removal" covers entry deletion, the ten leftover `.storage` learner files, the leftover Lovelace resource, and HACS/manual code removal | doc_coverage.py | 1 section |
| 7 | docs-configuration-parameters: every persisted config/options-flow field is documented — 95 by literal key string and 44 by their setting-table label in docs/configuration.md (e.g. `tibber_token` → "Tibber API token", configuration.md:46); the single remaining schema key `after_save` is dialog plumbing popped before persisting (config_flow.py:1616) | doc_coverage.py | 139/139 documented, 0 undocumented |
| 8 | docs-installation-parameters: every persisted setup-flow field (token, weather entity, all entity selectors, temperatures, building questionnaire, DHW, weather sensitivity) is documented | doc_coverage.py | 64/64 documented |
| 9 | docs-data-update: polling cadence and sources stated — how-it-works.md:47 "Every optimization interval (30 minutes by default)" plus the Tibber/weather/sensor flow in README "How it works" | doc_coverage.py | 3 sections |
| 10 | docs-known-limitations: dedicated sections exist and are non-trivial — dashboard-card.md:586 "Behaviour when data is missing", how-it-works.md:895 "What freezes them" — plus 6 caveat statements (README:417 number-entity echo registers, how-it-works:1010 defrost-duty resolution bias, README:288 draw-quantiles "stay unavailable") | doc_coverage.py | 2 sections, 6 statements |
| 11 | docs-supported-devices: the supported control interfaces (any HA `switch` entity, ECL110 over MQTT, compressor-frequency `number` entity via Modbus/ESPHome) are documented across README.md, configuration.md, ecl110.md and 3 more files; no specific device models are claimed | doc_coverage.py | 6 files |
| 12 | docs-supported-functions: README's inventory is exact — 55 sensor instantiations in sensor.py `async_setup_entry`, 4 binary + 4 button + 1 climate + 1 switch classes = 65, equal to the README's claimed 65; PLATFORMS (sensor, binary_sensor, button, climate, switch) all documented | doc_coverage.py | delta 0 entities, 0 platforms |
| 13 | docs-troubleshooting: README.md:601 with 6 bold-lead problem entries (zone swings, solar over-heating, slow floor response, hot water cold/too-frequent, predictive optimization inert, wrong numbers) | doc_coverage.py | 1 section, 6 entries |
| 14 | docs-use-cases: 9 use-case narratives in README "What it does" (lines 76–134) plus the "Quick start — the first 30 minutes" walk-through | doc_coverage.py | 9 narratives |
| 15 | dependency-transparency: numpy (BSD-3-Clause, PyPI 2.5.2, 24 workflow files, tags v2.5.2 + v1.24.0), scipy (BSD OSI classifier, PyPI 1.18.1, 17 workflows, tags v1.18.1 + v1.10.0), threadpoolctl (BSD-3-Clause, PyPI 3.6.0, 2 workflows, tags 3.6.0 + 3.5.0) — all four sub-checks pass per dependency | dep_transparency.sh | 12/12 sub-checks |
| 16 | integration-owner: manifest codeowners `["@tvofi"]`, account exists (HTTP 200, type User, id 70032254) | dep_transparency.sh | 1 codeowner, HTTP 200 |

Note on #7: a literal-key-string-only metric would report 95/140 (45 keys
whose snake_case name never appears). All 44 persisted keys in that residue
were hand-mapped to their setting-table rows in docs/configuration.md and the
mapping is committed as `LABEL_ALIASES` in the harness, so the judge re-runs
the same two-layer count. This is a documentation-style choice (labels, not
key names), not a gap.

## Unfinished / why

- Nothing unfinished. Two provisional notes: (a) PyPI "latest version" and
  workflow counts can drift over time; the harness prints the captured values
  on DETAIL lines and re-derives them on every run (numpy/scipy/threadpoolctl
  release cadence makes 12/12 stable in practice). (b) GitHub API
  unauthenticated rate limit (60/h) could throttle a judge re-run that
  follows other GitHub traffic; every sub-check degrades to an explicit
  0-with-DETAIL rather than silently passing.

## Exposure

None beyond the audit's own subject matter: D10 reads `README.md` and
`docs/*.md` as the measured corpus, not as prior-audit carriers; the stripped
export contained no audit register, backlog or release notes anyway. The
integration's own GitHub issues/PRs were not read; GitHub was queried only
for the three third-party dependency repos and the codeowner account
existence endpoint.

## Harnesses

- `tools/audit/round2/D10/C/doc_coverage.py` — all doc-rule numbers (35 RESULT lines).
- `tools/audit/round2/D10/C/dep_transparency.sh` — dependency matrix + owner (22 RESULT lines).
- `tools/audit/round2/D10/C/perturb_automation_example.md` — committed
  perturbation input for D10-01 (not a harness; consumed via
  `HPO_DOC_PERTURB_FILE`).
