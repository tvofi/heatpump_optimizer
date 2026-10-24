# D10 finder seat s1 — report (round 8)

Baseline SHA `cdf82daabcfe3777d98b31489f36df5555ec9d82`. Tree:
`/home/claude/audit-r8/seats/D10-s1` (copy tree, `.git`-free export).
Focus: every rule of the HA integration quality-scale checklist, one
executed check per rule, tier table, draft `quality_scale.yaml`, compared
against the integration's own.

## Method

Fetched the live checklist and the `strict-typing` / `exception-translations`
rule pages (WebFetch) to get exact rule text rather than relying on memory or
the in-repo register's paraphrase. For every rule, ran a grep or AST
presence/absence check against `custom_components/heatpump_optimizer/`;
cross-referenced against the register's own claimed evidence where it cited
one. Two rules got a full re-derivation with a committed, perturbation-tested
harness because the register's own governance comment makes a literal,
checkable completeness claim ("every entry parameter... none bare", "every
raise site carries translation_domain + translation_key") and a spot check
suggested each was false. Every other rule got a single grep/AST presence
check (commands in Non-findings below). `config-flow-test-coverage`,
`test-coverage` and the mypy half of `strict-typing` are s2's measured rules.

## Findings

### D10-s1-01 — qs_entry_param_bare is 3, not the claimed 0
`quality_scale.yaml`'s strict-typing comment states "every entry parameter is
typed with HeatPumpOptimizerConfigEntry, none bare (qs_entry_param_bare=0)".
`diagnostics.py:119`'s `async_get_config_entry_diagnostics(hass, entry:
ConfigEntry[HeatPumpOptimizerCoordinator])` uses the bare HA-core
`ConfigEntry` generic instead of the alias; two more bare uses sit in
`config_flow.py`'s OptionsFlow dispatch (possibly a legitimate HA-forced
signature, not re-derived here). Severity low, stop-rule hygiene.

### D10-s1-02 — 4 of 25 exception raise sites lack translation kwargs
The register's exception-translations comment states "every raise site
carries translation_domain + translation_key". Four `raise UpdateFailed(...)`
sites in coordinator.py (the Tibber outage latch and two generic wrappers)
carry neither, even though UpdateFailed's text is the user-visible
"why unavailable" string. Severity low, stop-rule hygiene.

Both findings are grouped by phenomenon (the register's completeness claims
outrunning the code) rather than filed as four line items.

## Non-findings
- parallel-updates: all 6 platform modules declare it (1 for writers, 0 for
  the 2 read-only sensor platforms). `grep -n PARALLEL_UPDATES custom_components/heatpump_optimizer/*.py`
- inject-websession: all 3 network callers use `async_get_clientsession(hass)`,
  zero bare `ClientSession()` construction.
- async-dependency: zero `requests`/`urllib.request`/`http.client` imports.
- docs-examples: fetched the cited Discourse URL live; 3 blueprint links match
  `blueprints/automation/*.yaml` filenames exactly.
- reconfiguration-flow: `async_step_reconfigure` present in config_flow.py.
- repair-issues: repairs.py calls issue_registry.
- entity-category/entity-device-class/entity-disabled-by-default: attributes
  present via grep.
- translations/icons files present and non-empty (en.json, sv.json,
  icons.json, strings.json).
- discovery/discovery-update-info/dynamic-devices/stale-devices exemption
  bases hold: zero zeroconf/dhcp/ssdp imports, zero device-removal sites
  beyond the single static registration in entity.py.

## Harnesses
- `tools/audit/round8/D10/s1_entry_param_bare.py` — D10-s1-01, RESULT
  qs_entry_param_bare=3, perturbed to 2 (fix) and 4 (regress).
- `tools/audit/round8/D10/s1_exception_translations.py` — D10-s1-02, RESULT
  qs_exception_raise_missing_translation=4, perturbed to 3 (fix) and 5
  (regress).
- `tools/audit/round8/D10/quality_scale_draft.yaml` — draft register vs the
  integration's own.

Both harnesses restore patched files in a `finally` block; verified with
`diff -rq custom_components/heatpump_optimizer /home/claude/audit-r8/export/custom_components/heatpump_optimizer`
(no output) after both ran.

## What I could not finish
Did not re-derive config-flow-test-coverage, test-coverage, or the mypy
--strict half of strict-typing (s2's rules). Zero `todo` rows this round, so
the "minimum HA release" column is empty by construction. Did not deep-audit
docs-known-limitations/troubleshooting/use-cases prose content beyond
presence — that is a D6 question, out of D10 scope.

## Exposure
Fetched two external URLs (HA developer docs rule pages, the Discourse
blueprint topic) via WebFetch.
