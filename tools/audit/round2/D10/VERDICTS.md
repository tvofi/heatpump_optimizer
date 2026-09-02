# D10 round-2 judge verdicts (register lines)

Judge re-measurement of the 3 survivors and the 1 number-based kill.
Baseline b39fc6f; export
`/Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/audit-r2-D10-export`
(read-only; every perturbation run on copies under `/tmp/hpo-d10-judge/`).
Artifacts: `judge_B_baseline.txt`, `judge_B_perturb1.txt`, `judge_B_perturb2.txt`,
`judge_A_baseline.txt`, `judge_A_perturb17.txt`, `judge_A_perturb19.txt`,
`judge_C_baseline.txt`, `judge_C_perturb18.txt`, `judge_d10_16_modes.py/.out`.

Load discipline: the box was busy throughout (load1 2.0–2.7, 8 cores) — above
the 1.5 gate — but every metric in this dimension is an exact count
(contention-immune per this audit's stated discipline) and every harness
self-reported `thread_factor` 1.000–1.001 (< 1.05). All numbers reproduced the
finder/panel values exactly, so no re-take is warranted; load1 is recorded per
run below. No aggregates (no leave-one-out applicable); D10-16's null control
(recovery half) re-run and holds (1 INFO / 0 ERROR at recovery in every run).

---

## D10-16 — log-when-unavailable (silver)

VERDICT: `verified` — votes 3×verify at medium; final severity **medium**;
final stop_rule_class **bug** (judge-assigned; agrees with finder).

- Judge re-run of B/harness.py (load1=2.19, tf=1.001):
  `error_logs_during_5_failed_polls=6` (rule expects 1 per transition),
  `outage_cycles_after_5_polls=10` (truth 5), `info_logs_at_recovery=1`,
  `error_logs_at_recovery=0` (null control holds), recovered message
  "Tibber prices recovered after 10 failed cycle(s)". Reproduced.
- Perturbation 1 on /tmp copy (coordinator.py:4460 `_LOGGER.error`→`_LOGGER.debug`
  in `_async_update_data`'s wrapper): 6→1 (load1=2.28, tf=1.000). Moves.
- Perturbation 2 on /tmp copy (except-Exception at 5465 re-raises UpdateFailed
  instead of re-calling `_tibber_fetch_failed`): 10→5 and the recovery message
  becomes "after 5 failed cycle(s)" (load1=2.21, tf=1.000). Moves. Harness live.
- Judge's own independent driver (fresh seam, not the committed harness; 5
  failed polls + 1 recovery per mode; load1=2.46): all five failure modes give
  6 ERROR records; latch = 10 for the four in-try modes (HTTP-500, 401,
  GraphQL errors, no-homes) but 5 for connect-failure (aiohttp ClientError →
  except-ClientError path, single latch entry). Mode-specificity confirmed.
- Metric comparability: finder and all three verifiers counted the same
  construct (ERROR records + latch increments over 5 failed polls + recovery
  through the real update path); my driver agrees. Comparable; no tie-break needed.
- stop_rule_class: the number shows a latch that double-counts events (wrong
  bookkeeping that leaks into user-visible log text) plus a wrapper that
  defeats the code's own documented log-once latch (docstring at
  coordinator.py:5384: "logged once (D10-09), not on every cycle") — misbehavior,
  not style → bug.

Recommended claim wording:

**Title:** "Every failed Tibber poll logs an ERROR with traceback, and the outage latch double-counts in the in-try failure modes"

**Body:** During a Tibber outage the `_async_update_data` wrapper
(coordinator.py:4459–4462) logs an ERROR with full traceback on every failed
poll — 6 ERRORs over 5 polls, one per poll cycle during an outage — defeating
the integration's own log-once latch (docstring at 5384: "logged once
(D10-09), not on every cycle"); this half is universal to all failure modes
including connect failures. Additionally, in the four in-try failure modes
(HTTP non-200, 401/403, GraphQL errors payload, empty homes) the
`UpdateFailed` raised by `_tibber_fetch_failed` (~5482) is re-caught by
`_fetch_tibber_prices`'s own `except Exception` (5465–5468) and the latch is
re-entered, so the outage counter advances 2 per poll and recovery after 5
failed polls logs "Tibber prices recovered after 10 failed cycle(s)"; the
connect-failure (aiohttp ClientError) mode counts correctly at 5, so only the
ERROR-per-poll half is mode-independent.

## D10-17 — exception-translations (gold)

VERDICT: `verified` — votes 3×verify at low; final severity **low**; final
stop_rule_class **hygiene** (judge-assigned; agrees with finder).

- Judge re-run of A/ast_checks.py (load1=2.44, tf=1.0):
  `raise_sites_total=13`, `raises_with_translation_kwargs=0`,
  `exceptions_section_strings.json=0`, `exceptions_section_en.json=0`; my own
  JSON check adds `sv.json` exceptions = 0. Site list matches the candidate
  exactly: `__init__.py:413,417,427,558,605,611,656,722,765,788,832,846;
  coordinator.py:1370`. Reproduced.
- User-reachability spot-check: climate.py:281 awaits
  `coordinator.async_set_target_temperature(...)`, which raises
  ServiceValidationError at coordinator.py:1370 — reachable from the climate
  entity's set_temperature. Consistent with the panel's enumeration.
- Perturbation on /tmp copy via `HPO_D10A_INT` (translation_key= +
  translation_domain= added to the raise at `__init__.py:427`):
  `raises_translatable` 0→1 (load1=2.03, tf=1.0). Moves. Harness live.
- Metric comparability: finder counted kwargs-carrying raise sites vs total +
  exceptions-section keys; verifiers' independent AST enumerations got the
  same 13 sites; identical construct. Comparable.
- V2's wording quibble adopted: the sites are service handlers and
  config-entry resolution helpers; config-flow step errors correctly use the
  translated step-errors dict (0 raises in config_flow.py) — do not call this
  a "service/config" gap.

Recommended claim wording:

**Title:** "All 13 service/config-entry resolution exception raise sites are untranslated; strings.json/en.json/sv.json carry no exceptions section"

**Body:** All 13 ServiceValidationError/HomeAssistantError raise sites
(`__init__.py:413,417,427,558,605,611,656,722,765,788,832,846` and
`coordinator.py:1370`, the latter reached via climate set_temperature) raise
English f-strings with no translation_key/translation_domain, and
strings.json/en.json/sv.json contain 0 `exceptions` keys, so service and
config-entry resolution errors remain English-only even on a translated UI
(the integration ships sv.json for everything else). Config-flow step errors
are unaffected — they use the translated step-errors dict, which is correct.

## D10-18 — docs-examples (gold)

VERDICT: `verified` — votes 3×verify at low; final severity **low**; final
stop_rule_class **hygiene** (judge-assigned; agrees with finder).

- Judge re-run of C/doc_coverage.py (load1=2.62, tf=1.0):
  `docs_automation_examples=0`, `docs_automation_sections=0`, actions 11/11
  covered. Reproduced.
- Perturbation via `HPO_DOC_PERTURB_FILE` pointing at the committed
  `perturb_automation_example.md`: 0→1 (sections 0→1) (load1=2.50, tf=1.0).
  Moves. Harness live.
- Metric comparability: finder counted automation example blocks in the docs
  corpus; verifiers independently counted fenced YAML blocks (6, all Lovelace
  card configs), 0 `trigger:`/`alias:` lines and 0 blueprint mentions
  repo-wide — same construct, same result. Comparable.
- Rule-page note (verified live against the rule page): the docs-examples
  remedy is hosted blueprint(s) plus a link from the integration page, and
  docs must not be used as a blueprint replacement; the gap stands under both
  readings because the repo has 0 inline examples AND 0 blueprints/links.
  configuration.md:55 directs users to build their own automations on the
  published sensors; plan-v4.0.0-program.md:1241 is a future-feature roadmap
  entry and should not be leaned on. Record the remedy as
  blueprint-or-inline.

Recommended claim wording:

**Title:** "No automation example or blueprint link anywhere in the shipped documentation"

**Body:** README.md and docs/*.md contain 0 automation examples (0
`trigger:`/`alias:` lines; the 6 fenced YAML blocks are all Lovelace card
configs) and 0 blueprint mentions or hosted-blueprint links, even though
configuration.md:55 tells users the plan is "published on sensors for your own
automations to act on" and all 11 services are fully tabled. The rule's
preferred remedy is hosted blueprint(s) with a link from the docs (inline
worked examples acceptable; docs are not a blueprint substitute) — either
route closes the gap; today neither exists.

## D10-19 — config-flow data_description sub-check (KILL; panel 3×refute)

VERDICT: `refuted` — kill **CONFIRMED** by judge re-measurement (votes 3×refute).

Judge's own parser over strings.json, translations/en.json and
translations/sv.json (identical results in all three):

- flow steps total (config+options) = **25** (config 10, options 15);
- steps with a `data_description` section = **20**;
- schema fields total = **238**, fields with helper text = **237** (99.6%);
- **0** data_description keys without a matching data field (no mismatches);
- single gap: **tibber_token on config/reauth_confirm**; the other four
  no-section steps (config/building, options/init, options/advanced,
  options/setup_overview) have no data fields at all — nothing to describe.

This matches the verifiers' numbers (V1: 8/10 config + 12/15 options = 237
fields; V2/V3: 20/25 steps, 237/238, gap tibber_token/reauth_confirm).

Perturbation re-run on /tmp copy via `HPO_D10A_INT`
(`vol.Required(CONF_TIBBER_TOKEN, description="...")` in config_flow.py's
user step): `config-flow.data_description_kwargs` stays **0** (load1=2.68,
tf=1.0) — the candidate's own perturbation fails to move its own metric; the
harness is void.

Refutation text (for the register's refuted rows):

Judge re-measured the kill's numbers with an independent parser and confirms
them: 25 flow steps (10 config + 15 options), 20 with data_description
sections, and 237 of 238 schema fields (99.6%) carry field helper text in
strings.json, en.json and sv.json alike, with exactly one gap
(tibber_token on reauth_confirm) and zero key mismatches — so the claim's
conclusion "no field-level helper text is shown to users in the UI" is false;
the helper text ships via strings.json, which is the mechanism the rule page
itself names (data_description appears in the bronze rule's non-binding
Reasoning text, "use data_description in the strings.json"). The candidate's
harness counted `data_description=` kwargs in config_flow.py — a mechanism HA
config flows do not use — and its own perturbation (adding `description=` to
a voluptuous field) leaves its metric at 0, so the harness is void as well.
Residue, not register-worthy: the single missing helper text for
tibber_token/reauth_confirm (1/238) is a one-line nit.
