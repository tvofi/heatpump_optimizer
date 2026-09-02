# D5 round 2 — verifier seat 1 of 3

Baseline `c398fc84eec25fc44b60d74aae05b9a2da205884`, read-only export
`audit-r2-baseline`. Apple M1, Python 3.13.1 (`tvofi-claude/.venv`),
`PYTHONPATH=tests/hastub` from the export root. Text/AST checks only; no
solver, no test suite. Every number is a count and contention-immune
(`thread_factor` 1.000 on every run, `load1` 1.69–2.11).

My harnesses live under `/tmp/verify-D5-1/` (`v1_tests_readme.py`,
`v1_ecl110.py`, `v1_links.py`, `v1_content.py`, `v1_comments.py`,
`v1_common.py`; logs beside them). Perturbations were run on a full copy of the
export at `/tmp/verify-D5-1/tree` with six edits applied at once (one per
predicted move); the export itself was not modified. This file is my one write
in the export.

## Re-run of the finder's harnesses (once each, as their headers say)

| harness | RESULT | finder | mine | load1 / thread_factor |
|---|---|---|---|---|
| reader_paths.py | tests_readme_drift | 7 | 7 | 1.91 / 1.000 |
| reader_paths.py | ecl110_guidance_contradiction | 1 | 1 | |
| reader_paths.py | unreachable_docs_from_readme | 3 | 3 | |
| reader_paths.py | content_defects_user_docs | 5 | 5 | |
| reader_paths.py | doc_fact_checks_failed (of 36) | 15 | 15 | |
| comment_numbers.py | constant_comment_mismatches_raw / vetted | 17 / 1 | 17 / 1 | 1.91 / 1.000 |
| comment_symbols.py | loose_missing_raw / vetted | 7 / 1 | 7 / 1 | 1.91 / 1.000 |
| comment_symbols.py | strict_missing_raw / vetted | 3 / 0 | 3 / 0 | |
| comment_symbols.py | redundant_single_line_comments | 11 | 11 | |

All exact. Perturbed copy (six edits, see per finding): reader_paths
`tests_readme_drift=6 ecl110_guidance_contradiction=0
unreachable_docs_from_readme=2 content_defects_user_docs=4
doc_fact_checks_failed=11`; comment_numbers `constant_comment_mismatches_vetted=0`;
comment_symbols `loose_missing_vetted=0`. Every predicted direction held.

---

## D5-01 · tests/README.md drift (7 statements)

**My metric.** Number of factual statements in `tests/README.md` (a path, a
count or a roster) whose value, extracted by my own regexes, differs from the
fact my script computes from the tree by its own method (ast over
`closure.py`/`golden.py`/`validate.py`, json over `closures.json`, regex over
`run.sh`/`tests.yml`/`plan_view.py`). The finder's seven are S1–S7; I added
six further factual statements from the same document (E1–E6) to test whether
7 is the right size.

```
RESULT v1_tests_readme_false_statements=7 count          (S1..S7: all seven false)
RESULT v1_S1_listed_items_not_inert_or_read=5 count       (of 7 concrete paths behind the l.129 list)
RESULT v1_ci_scripts_unnamed_in_tests_readme=1 count      (card_browser.mjs)
RESULT v1_extra_statements_checked=6 count
RESULT v1_extra_statements_false=2 count                  (E2, E3)
RESULT v1_tests_readme_false_statements_all=9 count
RESULT thread_factor=1.000  load1=2.05
perturbed copy (l.285 "53 fixtures (47" -> "55 fixtures (49"): v1_tests_readme_false_statements=6, _all=8
```

**Attacks and outcomes.**

- *Is each statement really false against the tree?*
  - S1 (l.129): the parenthetical names README.md, docs/, RELEASE_NOTES.md, the
    licence files, the brand images as "files no test can read".
    `closure.py:INERT` = LICENSE, NOTICE, icon.png, docs/, tests/README.md,
    .gitignore, tools/ — README.md, RELEASE_NOTES.md and the three images
    (`brand/icon.png`, `brand/logo.png`, `custom_components/.../icon.png`) are
    not on it, and `closures.json` records README.md and RELEASE_NOTES.md read
    by `entities.py`, the three images by `golden.py` and `env_drift.py`.
    5 of the 7 concrete paths are wrong. The document contradicts itself:
    l.102 says a RELEASE_NOTES.md change runs `entities.py`. False.
  - S2/S3: 55 files in `tests/golden/` all parse as JSON; `SCENARIOS` has 49
    keys (ast); 5 `coord_*`; 1 `config_flow`. `env_drift.py --all` captures
    SCENARIOS + coordinator scenarios + config_flow (env_drift.py:145–146,
    540–545) = 55, so "all 53 scenarios" is false too. False, false.
  - S4: `plan_view.py:130` defaults to `/tmp/plandata-<sha256[:12]>.json`;
    the document names `/tmp/plandata.json` twice and `HPO_PLANDATA` never.
    False.
  - S5: the sentence is scoped to the run.sh wiring accounting, so I compared
    to `run.sh:390`'s allow-list, not to NOT_A_TEST: 7 entries (harness.py,
    profiles.py, dst_checks.py, closure.py, dom_stub.mjs, card_rig.mjs,
    card_browser.mjs). The document's four include `derive_closures.sh`, which
    the `tests/*.py tests/*.mjs` glob never sees, and omit four that are
    excluded. False under the document's own scope (and under NOT_A_TEST=7).
  - S6: `tests.yml` has a `browser` job that runs `node tests/card_browser.mjs`;
    tests/README.md never names it (0 mentions); "verify in a real browser as
    well" is the only guidance. False.
  - S7: 22 module-level `run(...)` calls in validate.py (22 anywhere, ast);
    the document says 18. False.
- *Is the count inflated by non-defects?* No: every one of the seven is a
  path, count or roster a developer would act on. If anything it is deflated:
  the closure table at l.103–104 says a `tests/card.mjs` change runs "2 —
  plan_view.py, card.mjs" and a card-JS change "6 — …"; with closure.py's
  `PRODUCERS` rule applied (card.mjs and card_drift.mjs pull in plan_view.py)
  the closures give 3 and 7 — `card_drift.mjs` is missing from both rows
  (E2, E3). E1, E4, E5 (the other table rows) and E6 (the five sensitive
  fixtures vs `env_drift.py:SENSITIVE`) hold.
- *Consequence.* Developer path only; nothing published changes. Low is right.

**Vote: verify (low).** Deciding number: 7 of 7 false under my own extraction
(`v1_tests_readme_false_statements=7`); 9 under the wider sweep. The fix scope
should add the two closure-table rows (l.103–104).

---

## D5-02 · configuration.md's ECL110 guidance vs the shipped defaults and the per-cycle publish

**My metric.** `v1_ecl110_contradiction` = 1 iff (a) both
`DEFAULT_ECL110_*_TOPIC` constants are non-empty string literals and
coordinator.py reads them as `config.get(CONF, DEFAULT)`; (b) the per-cycle
chain `_async_update_data → _apply_action → async_publish_current_action →
async_publish_ecl110_command → hass.services.async_call("mqtt","publish")`
carries no If-guard mentioning ecl110/mqtt other than the both-topics-empty
early return and the per-topic non-empty checks (ast parent walk over every
If/Try ancestor on the path); (c) a user-facing page other than ecl110.md
addresses installs without an ECL110 in its ECL110 text and does not tell them
to clear the topics, while ecl110.md does. Sentences are split at table cells
so a table cannot glue words together.

```
RESULT v1_publish_path_ecl110_or_mqtt_guards_outside_early_return=0 count
RESULT v1_pages_addressing_non_owners_without_clear_instruction=1 count   (docs/configuration.md: 2 sentences, l.68-70 and l.457)
RESULT v1_pages_with_clear_instruction=1 count                            (docs/ecl110.md l.79-82)
RESULT v1_ecl110_contradiction=1 count
RESULT thread_factor=1.000  load1=1.69
perturbed copy (both defaults -> ""): v1_ecl110_contradiction=0
```

**Attacks and outcomes.**

- *Does the claim hold in the code?* Yes, by ast:
  `_async_update_data:4403 → _apply_action()` (guard: `try` only);
  `_apply_action:6584 → async_publish_current_action("scheduled_update")` (no
  guard); `:6419 → async_publish_ecl110_command` (only early return: `not
  self._current_action`, which is set from the first cycle on);
  `:6384/:6401 → hass.services.async_call("mqtt","publish")`, each guarded only
  by its own topic being non-empty, inside `try … except Exception:
  _LOGGER.error(...)`. Early return only when both topics are empty
  (`:6378`). Defaults `ecl110/flow_temp_control/displace/set` and
  `ecl110/command` (const.py:1045–1046), read at coordinator.py:1226–1231 with
  the non-empty default when the key is absent. The options form pre-fills
  both fields with the same defaults (`config_flow.py:2342–2352`,
  `vol.Optional(..., default=current.get(CONF, DEFAULT)): str`).
- *Is "Leave blank" (l.457) perhaps the right instruction read as "make
  blank"?* A reader who never opens the page keeps the non-empty defaults; a
  reader who opens it sees pre-filled fields and "leave" tells them to do
  nothing. And l.70 "default sensibly when absent" is unambiguous and, for a
  non-owner, false: the absent-key default is a live topic. The contradiction
  with ecl110.md:79–82 ("clear the set topic and the legacy command topic …
  otherwise every cycle attempts a publish and logs the failure") stands.
  README's ECL110 section (l.599–606) says nothing either way.
- *Reachable in real Home Assistant or only through the stub?* The path is the
  DataUpdateCoordinator's per-interval method with no feature gate; in real HA
  an unregistered `mqtt.publish` raises `ServiceNotFound`, which the `except
  Exception` turns into an ERROR log per interval. `tests/harness.py:144–148`
  (`FakeServices.async_call`) returns `None` for an unregistered service and
  `ServiceNotFound` appears nowhere in the hastub (grep: 0), so no test can
  see it — the finder tagged this for D6/D10 correctly; it is not part of the
  docs claim.
- *Severity.* Docs only; every non-ECL110 reader of configuration.md is
  misdirected. Low is right.

**Vote: verify (low).** Deciding number: `v1_ecl110_contradiction=1`, with 0
guards on the publish path outside the topic checks.

---

## D5-03 · tests/README.md and two plan documents unreachable from README.md

**My metric.** A: number of documents in {README.md, DISCLAIMER.md, docs/*.md,
tests/README.md} with no directed path from README.md where an edge is an
inline `[t](p)`, a reference definition `[t]: p`, an autolink `<p>` or an HTML
`href` to a relative `.md` in the set (code fences ignored, fragments
stripped). B: the same plus an edge for every backticked relative `.md` path
mention.

```
RESULT v1_unreachable_links=3 count                 (docs/plan-card-decomposition.md, docs/plan-open-issues.md, tests/README.md)
RESULT v1_unreachable_links_or_mentions=3 count     (the mention tier adds nothing reachable)
RESULT v1_unreachable_not_a_directory_readme=2 count
RESULT thread_factor=1.000  load1=1.81
perturbed copy (one README table row linking tests/README.md): v1_unreachable_links=2
```

**Attacks and outcomes.**

- *Reproducible under a different extractor?* Yes: in-degree under A is 0 for
  all three; `docs/architecture.md` ("for anyone reading or changing the
  code") carries exactly one link (to how-it-works.md) and names
  `tests/features.py`/`tests/entities.py` only in prose. The backtick mentions
  of `tests/README.md` come only from the two orphaned plan documents, and
  `plan-open-issues.md` is mentioned only by `plan-card-decomposition.md`, so
  tier B changes nothing.
- *Is the consequence overstated?* Partly: `tests/README.md` is a directory
  README, which GitHub renders when a developer browses `tests/`, a route that
  needs no link. The two plan documents have no such route. The claim as
  stated ("by links") is exact; the "stranded developer" wording is softer
  than it reads.
- *Are the plan documents deliberately unlisted?* Possibly (program plans);
  that is a fix-scope decision, not a refutation, and the finder already
  frames it so.

**Vote: verify (low).** Deciding number: `v1_unreachable_links=3`.

---

## D5-04 · Five content defects

**My metric.** Five checks under my own definitions: H2 the clause "may move
within follow" present in how-it-works.md; H1 prose lines longer than 1.5× the
document's 95th-percentile prose length (tables, code, lists, headings
excluded), per user-facing document; S1 the highest version cited under README
"## Project status" has a major below VERSION's; C6 sentences using
"throttling" across the eight user-facing documents that carry a definitional
cue (is a / means / i.e. / that is / any mode / other than / every mode / a
valve that / defined as); ST1 heading-level skips outside code fences in all
eleven documents. `v1_content_defects` = failing checks.

```
RESULT v1_H2_garbled_sentence=1 count
RESULT v1_H1_outlier_prose_lines_how_it_works=1 count     (l.1189, 134 chars; the document's p95 is 80, next-longest 85)
RESULT v1_S1_project_status_major_behind=1 count          (cites v4.0.0, v5.0.0; VERSION 6.2.14)
RESULT v1_C6_throttling_sentences=9 count
RESULT v1_C6_throttling_defining_sentences=0 count
RESULT v1_ST1_heading_skips=1 count                       (docs/dashboard-card.md:31 h1->h3; the only skip in 11 documents)
RESULT v1_content_defects=5 count
RESULT thread_factor=1.000  load1=1.81
perturbed copy (H2 sentence repaired): v1_content_defects=4
```

**Attacks and outcomes.**

- H2: read in full — "both that prior and the range learning may move within
  follow the tank's surface area rather than its volume" — two drafts merged.
  Real.
- H1: across the other seven user documents the outlier count is 0 (README's
  l.10 at 131 chars is a badge line my filter let through; not prose). One
  134-char line in a document of 847 prose lines with p95 = 80 is an unwrapped
  insertion, not a house style. The finder's second remark (that "Without it"
  now refers to the wrong noun) is a reading judgement I share but did not
  measure; the count does not rest on it.
- S1: the section describes "the v4.0.x–v5.0.0 releases" as the current phase
  at VERSION 6.2.14. Every other version string in README is a historical
  "since vX" (max v5.0.0), so this is the one section that reads as present
  tense and is stale. The `docs/backlog.md` link it carries is broken only in
  the export (removed), not a defect.
- C6: the nine uses are in configuration.md (buffer-tank row, the layout rule
  at l.482–484, four catalog rows) and how-it-works.md:200; none defines the
  term. The substance of the definition exists at how-it-works.md:386–392
  ("a mixing valve … limits how much heat reaches the house") and in code
  (`mixing_valve.py:57–63`, `is_throttling` = any mode but none), and the UI
  strings never use the word (grep over translations/strings: 0). Inferable,
  hence low; still undefined on every page.
- ST1: lines 31–133 of dashboard-card.md are `###` directly under the `#`
  title; first `##` at l.134. Real.
- *Inflated?* No: each of the five is an executable, reader-facing defect;
  none is a matter of taste except the degree of H1's consequence.

**Vote: verify (low).** Deciding number: `v1_content_defects=5`.

---

## D5-05 · Comment precision: GHI bound, misnamed service, three restating comments

**My metrics.** (a) `v1_bound_comment_mismatches`: module/class-level numeric
constants whose attached comment states a bound (cannot exceed / ceiling /
upper bound / at most / no more than / never above / physical limit / hard
cap) with a number, and no cited number equals the constant under ×/÷ 10,
100, 1000, 60, 3600. (b) `v1_service_name_misses`: every "<snake_case>
service" / "service <snake_case>" phrase in a production comment or docstring
whose name is not a key of `services.yaml`. (c) `v1_restating_*`: single-line
standalone comments (neighbours not comments; not `#:`; not a dashed banner)
and inline comments whose content words (≥3 letters, non-stop, ≥2 of them)
all occur among the next/same code line's identifier fragments; each hit read.

```
RESULT v1_bound_comment_mismatches=1 count      (open_meteo.py:69 _MAX_PLAUSIBLE_GHI=1400 vs "cannot exceed" 1361)
RESULT v1_service_name_phrases=10 count
RESULT v1_service_name_misses=2 count           (thermal_model.py:191 set_thermal_params; snapshots.py:170 restore_snapshot)
RESULT v1_restating_standalone=8 count
RESULT v1_restating_inline=1 count
RESULT thread_factor=1.000  load1=2.09
perturbed copy (GHI -> 1361.0; comment -> set_thermal_parameters): v1_bound_comment_mismatches=0, v1_service_name_misses=1
```

**Attacks and outcomes.**

- *GHI: is the comment or the constant wrong?* The comment states a hard
  physical bound ("surface GHI cannot exceed" 1361) and the constant admits
  1362–1400 without a word about slack; `_parse_block`'s docstring calls it
  "the variable's own plausibility ceiling". Cloud-edge enhancement above the
  solar constant is real, so the defensible fix is the comment, not the
  constant. My bound metric over all 432 constants finds exactly this one
  (an earlier draft also flagged `freq_control.py:46` "1 per 5 minutes" beside
  300 s — my missing ×60 conversion, fixed). Real, no behaviour consequence.
- *Misnamed service: is it really missing?* `services.yaml` has
  `set_thermal_parameters`; README and configuration.md use that name; the
  handler is `handle_set_thermal_params`, so a grep for the comment's name
  lands on the handler — a small imprecision, but the sentence says "the
  set_thermal_params service" and no such service exists. Under my metric
  there is a second one the finder's loose tier did not surface:
  `snapshots.py:170` "the manual restore_snapshot service" — the service is
  `restore_learned_snapshot` (services.yaml:679, README:402,
  configuration.md:554/636); handler `handle_restore_snapshot`. Count 2, not 1.
- *Are the "restating" comments really redundant?* My 9 candidates (the
  finder's 11 minus the `#:` attribute doc and the dashed banner my rules
  drop) read as: six group labels above a run of fields, dict entries or
  constructor calls (`const.py:871`, `sensor.py:115`,
  `thermal_model.py:343/738/802`) or a formula with units (`const.py:966`) —
  not defects; and three that say only what the next line's name says:
  `coordinator.py:4353` "Fetch prices from Tibber" → `_fetch_tibber_prices()`
  (its neighbouring step labels add something; this one does not),
  `optimizer.py:671` "savings as percentage" → `savings_percentage: float`
  (its neighbours add content, e.g. "cost with constant-temp strategy"),
  `thermal_model.py:1830` "Solar gains per zone" → `solar_gain_per_zone(...)`.
  Same three as the finder. All three restate; none is wrong; consequence nil.
  They are style, not error, and the finder already grades them so.
- *Severity.* Two precision defects (GHI, service name ×2) and three style
  items; nothing behavioural. Low is the floor and is right.

**Vote: verify (low).** Deciding numbers: `v1_bound_comment_mismatches=1`,
`v1_service_name_misses=2` (one more than the finder: add `snapshots.py:170`
to the fix scope, six edits rather than five), three restating comments by
reading.

---

## Summary

| finding | finder | seat 1 (own metric) | vote |
|---|---|---|---|
| D5-01 | tests_readme_drift=7 | v1_tests_readme_false_statements=7 (9 with the two closure-table rows) | verify (low) |
| D5-02 | ecl110_guidance_contradiction=1 | v1_ecl110_contradiction=1; 0 guards on the publish path | verify (low) |
| D5-03 | unreachable_docs_from_readme=3 | v1_unreachable_links=3 (=3 with mentions; 2 excluding the directory README) | verify (low) |
| D5-04 | content_defects_user_docs=5 | v1_content_defects=5 | verify (low) |
| D5-05 | 1 bound + 1 service + 3 restating | 1 bound + 2 services + 3 restating | verify (low) |

Nothing refuted; no timing numbers involved, so nothing is provisional.
