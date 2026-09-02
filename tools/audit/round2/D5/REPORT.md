# D5 — Docs structure, flow and content; comments in code — round 2

Baseline `c398fc84eec25fc44b60d74aae05b9a2da205884`, read-only export
`audit-r2-baseline`. Machine: Apple M1 (8 cores, 8 GB), macOS 26.6,
Python 3.13.1 (`tvofi-claude/.venv`), run from the export root with
`PYTHONPATH=tests/hastub`. Every number below is a count, ratio or byte
figure — contention-immune — taken during the fan-out (load1 2.1–3.7,
`thread_factor` 1.000–1.006). Nothing in production, tests or docs was
modified; the five harnesses under `tools/audit/round2/D5/` are the only
writes.

## Method

1. **Reader paths.** Three readers were walked through the documents by
   reading every user-facing page in full (README.md, DISCLAIMER.md,
   docs/how-it-works.md, docs/configuration.md, docs/dashboard-card.md,
   docs/ecl110.md, docs/architecture.md, tests/README.md) and noting each
   place where the reader needs a fact that is elsewhere, nowhere, or
   contradicted. Every such note was then turned into an executable check in
   `reader_paths.py` (36 checks: a claim, the fact computed from the tree,
   pass/fail, the path(s) it sits on). "Dead end" = a failed check on that
   path.
2. **Structure.** `links.py` checks every internal path, every anchor (GitHub
   slug rules) and every external URL (HEAD only). `duplication.py` hashes
   normalised paragraphs, tables and code blocks and measures exact and
   near (5-shingle Jaccard ≥ 0.5) duplication across the eight user-facing
   documents. `reader_paths.py` also computes link-graph reachability from
   README.md, heading-level skips, and version strings against `VERSION`.
3. **Content.** Mechanism paragraphs were spot-checked against the code path
   they describe (ECL110 publish path, capacity-tariff window, activation
   threshold, module boundary counts, service and key counts, card
   constants); each spot-check is one of the 36 checks so the judge re-runs
   the same thing.
4. **Comments.** `comment_symbols.py` extracts every backtick/RST-role
   reference (strict tier, 1,120 references) and every bare snake_case /
   CamelCase / `name()` token (loose tier, 251) from all 45 production
   modules' comments and docstrings and from the card's comments, and checks
   each against the identifier universe of the tree (18,789 names: tokens,
   whole-string config keys, JSON/YAML keys, file names). `comment_numbers.py`
   compares the numbers cited in the comment attached to each of the 432
   module/class-level numeric constants with the constant's value under the
   conversions a comment legitimately uses, and checks every docstring
   "default N" claim against the signature. Both scripts print the raw count
   and a vetted count; every vetted-out entry carries the reason in an
   `ALLOW` dict in the script, so the judge can delete the dict and see the
   raw list. Redundant single-line comments ("what the next line does") are
   found by a content-word containment heuristic and then judged by reading.
   Comment blocks longer than three lines (515 in production, 242 in the
   card) were sampled with a fixed seed (24 of 515, `random.seed(5)`) and
   judged for concision and precision by reading.

## Findings

All five are hygiene, severity low: nothing here changes a plan, a published
value or the host's health. They are reported because each is a place where
a reader is told something the tree contradicts, and each count moves under
a stated one-line edit.

### D5-01 · tests/README.md has drifted from the gate it documents (7 statements)

**Claim.** Seven statements in `tests/README.md` state a fact — a path, a
count, a roster — that the tree contradicts.

**Evidence.** `reader_paths.py` → `RESULT tests_readme_drift=7`
(= `failed_in[tests/README.md]=7`), checks T1–T7:

| id | tests/README.md says | the tree says |
|---|---|---|
| T1 (l.129) | `README.md`, `RELEASE_NOTES.md` and "the brand images" are on "the short, checked list of files no test can read" | `tests/closure.py:INERT` deliberately excludes all three (its own comment says why: `entities.py` reads README.md and RELEASE_NOTES.md; the images are inside `env_drift.py`'s closure); `closures.json` records all five files as read |
| T2 (l.285) | "53 fixtures (47 plan scenarios, 5 coordinator captures and the config-flow schema)" | 55 fixture files, `golden.py:SCENARIOS` has 49 keys, 5 coordinator captures, 1 schema |
| T3 (l.355) | "all 53 scenarios" | 55 |
| T4 (l.228, l.457) | `plan_view.py` "writes /tmp/plandata.json" | it writes `/tmp/plandata-<sha256(tests dir)[:12]>.json`; `card.mjs` accepts the legacy path only "as a last resort, loudly" |
| T5 (l.487) | "Four files in tests/ are not tests at all" (dom_stub, card_rig, closure.py, derive_closures.sh) | `closure.py:NOT_A_TEST` has 7 (adds harness.py, profiles.py, setup_qa_render.mjs, card_browser.mjs); `run.sh` allow-lists 7 (adds dst_checks.py) |
| T6 (l.505) | "card.mjs does not lay anything out … verify in a real browser as well" — the only guidance | `tests/card_browser.mjs` is a Playwright lane with its own CI job (`tests.yml: browser`); tests/README.md never mentions it |
| T7 (l.221) | `validate.py # 18 seasonal scenarios` | 22 `run(...)` scenarios |

**Instrumented symbols.** `tests/closure.py:INERT`, `tests/closure.py:NOT_A_TEST`,
`tests/golden.py:SCENARIOS`, `tests/plan_view.py:plandata_path`,
`tests/validate.py` (`run(` call sites), `.github/workflows/tests.yml:browser`,
`tests/closures.json` — all read through ast/json/regex.

**Perturbation.** In `tests/README.md:285` change "53 fixtures (47 plan
scenarios" to "55 fixtures (49 plan scenarios" → `tests_readme_drift` 7 → 6
(down). Conversely, adding `"README.md"` to `closure.py:INERT` does not
repair T1 (RELEASE_NOTES.md and the images remain), which is the point: the
document, not the gate, is what drifted.

**Metric.** Number of checks T1–T7 (one per statement) whose fact computed
from the tree differs from the document's.

**Consequence.** Developer path (P3) only. The reader who follows the
document looks for a file that is never written, counts fixtures that do not
match, and does not learn that a real-browser lane exists.

**Fix scope.** Docs only: rewrite the seven statements; replace "Note on
browser checks" with a paragraph on `card_browser.mjs` (how to run it, that
it is its own CI job, why it is outside the closures roster — the
information is already in that file's header).

### D5-02 · ECL110 topic guidance: configuration.md tells non-owners to "leave blank" what ships non-empty and publishes every cycle

**Claim.** `docs/configuration.md` says of the ECL110 page "Leave blank if
you do not have one" (l.457) and that the eight settings "default sensibly
when absent" (l.70); the shipped defaults are the non-empty topics
`ecl110/flow_temp_control/displace/set` and `ecl110/command`, and the
coordinator publishes to MQTT on every cycle unless *both* are empty. Only
`docs/ecl110.md` (l.79–82) says so — "clear the set topic and the legacy
command topic … otherwise every cycle attempts a publish and logs the
failure" — and that page opens by telling everyone without an ECL110 that
it is not for them.

**Evidence.** `reader_paths.py` → `RESULT ecl110_guidance_contradiction=1`
(check E1): `const.py:DEFAULT_ECL110_DISPLACE_SET_TOPIC` and
`DEFAULT_ECL110_COMMAND_TOPIC` are non-empty; `coordinator.py` calls
`await self.async_publish_current_action(reason="scheduled_update")` in the
actuation step of every cycle; `async_publish_ecl110_command` returns early
only `if not self._ecl110_displace_set_topic and not self._ecl110_command_topic`,
otherwise it calls `hass.services.async_call("mqtt", "publish", …)` for each
configured topic and logs `_LOGGER.error` on any exception.

**Instrumented symbol.**
`custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.async_publish_ecl110_command`
(with `const.py:DEFAULT_ECL110_DISPLACE_SET_TOPIC`,
`DEFAULT_ECL110_COMMAND_TOPIC`).

**Perturbation.** Set both `DEFAULT_ECL110_*_TOPIC` constants to `""` in
`const.py` → E1 passes, `ecl110_guidance_contradiction` 1 → 0 (to_zero).
That edit would then make `ecl110.md` the wrong page; the documentation fix
is the other direction — make `configuration.md` say what `ecl110.md` says.

**Metric.** 1 if a user-facing page tells a non-ECL110 install it can leave
the topics at their defaults while the defaults are non-empty and the
publish path runs each cycle; else 0.

**Consequence.** New-user (P1) and feature (P2) paths. **For D6/D10, not
claimed here:** with the defaults and no MQTT integration loaded,
`hass.services.async_call("mqtt", "publish")` raises `ServiceNotFound` in
Home Assistant, so every non-ECL110 install without MQTT logs an ERROR every
optimization interval. `tests/harness.py:FakeServices.async_call` returns
`None` for an unregistered service, so no test can see it; no test names the
default topic or the error string (`grep` over tests/: 0 hits).

**Fix scope.** Docs: `configuration.md` l.457 and l.70, and one sentence in
README's ECL110 section. (Whether the code should instead default to empty
topics or gate the publish on the MQTT integration being loaded is D10's
call.)

### D5-03 · The link graph strands the developer: tests/README.md and two plan documents are unreachable from README.md

**Claim.** Following links from README.md never reaches `tests/README.md`,
`docs/plan-card-decomposition.md` or `docs/plan-open-issues.md`.

**Evidence.** `reader_paths.py` → `RESULT unreachable_docs_from_readme=3`
(checks R1, R2). README's "Documentation" table lists six documents plus
DISCLAIMER; `docs/architecture.md` — "for anyone reading or changing the
code" — names `tests/features.py` and `tests/entities.py` but never links
`tests/README.md`. The only inbound links to `tests/README.md` are from the
two plan documents, themselves orphaned.

**Instrumented symbol.** The markdown link graph over README.md,
DISCLAIMER.md, docs/*.md, tests/README.md (`reader_paths.py`, regex over
`[text](target)`), rooted at README.md.

**Perturbation.** Add a row `[tests/README.md](tests/README.md)` to README's
Documentation table → `unreachable_docs_from_readme` 3 → 2 (down); linking
`docs/plan-card-decomposition.md` from README's "Project status" (where
`docs/plan-v4.0.0-program.md` already is) → 0.

**Metric.** Number of documents in the set not reachable from README.md by
following relative markdown links.

**Fix scope.** README.md Documentation table (one row), docs/architecture.md
"Where to start reading" (one bullet); decide whether the two plan documents
belong in the table or in a "program plans" line under Project status.

### D5-04 · Five content defects in the user-facing documents

**Claim.** The user-facing pages carry five defects a reader meets on the
new-user or feature path: two editing artefacts, a stale status section,
an undefined term, and a heading-level skip.

**Evidence.** `reader_paths.py` → `RESULT content_defects_user_docs=5`
(checks H1, H2, S1, C6, ST1):

- **H2** `docs/how-it-works.md:562–565` does not parse: "both that prior
  and the range learning may move within follow the tank's **surface
  area**" — two drafts merged ("the range learning may move within" /
  "follow the tank's surface area").
- **H1** `docs/how-it-works.md:1189` is a 134-character line in a document
  wrapped at 80: a sentence ("until v5.1.7 the fall-through was
  `preheat_weather` …") was inserted without re-wrapping, and the sentence
  after it ("Without it, an unexpected slot is indistinguishable from a
  bug") now has "it" pointing at the wrong noun.
- **S1** README "Project status" (l.608–617): the newest release it names
  is v5.0.0 ("the v4.0.x–v5.0.0 releases have been an audit train") while
  `VERSION` is 6.2.14; it also rests on `docs/backlog.md` for "what remains
  open". (The release-history claim itself cannot be checked here:
  `RELEASE_NOTES.md` and `docs/backlog.md` are removed from the export.)
- **C6** "throttling valve" / "throttling mixing valve" is used 8 times in
  `docs/configuration.md` (the buffer-tank row and the whole layout catalog)
  and defined on no page. The code defines it (`mixing_valve.py:THROTTLING_MODES`
  = every mode except *No mixing valve*); `how-it-works.md:386–392` lists
  the four modes without using the word. A reader can infer it; the catalog
  is the one place the inference is load-bearing (two-tank layout requires
  "a throttling valve").
- **ST1** `docs/dashboard-card.md:31–133` are `###` sections directly under
  the `#` title; the first `##` is at l.134. On GitHub's outline the six
  sections about the chart appear as children of nothing.

**Instrumented symbol.** The document texts (`reader_paths.py` regexes:
line length, the sentence fragment, version strings under "## Project
status" against `VERSION`, `throttling` uses vs a defining sentence,
heading depth sequence).

**Perturbation.** Repair the sentence at `how-it-works.md:564` →
`content_defects_user_docs` 5 → 4 (down); each of the other four moves the
count by one when fixed.

**Metric.** Number of checks {H1, H2, S1, C6, ST1} failing.

**Fix scope.** Docs only: two sentences in how-it-works.md, one paragraph in
README, one defining clause in configuration.md (e.g. "a throttling valve —
any mixing-valve mode other than *No mixing valve*"), and a `## The chart`
heading in dashboard-card.md.

### D5-05 · Comment precision: one misnamed service, one bound the constant does not enforce, three restating comments

**Claim.** Of 1,120 strict and 251 loose symbol references and 65
number-citing constant comments in production, one comment names a service
that does not exist, one comment states a physical bound its constant does
not enforce, and three single-line comments say only what the next line
says.

**Evidence.**
- `comment_numbers.py` → `RESULT constant_comment_mismatches_vetted=1`:
  `open_meteo.py:66–69` — "The solar constant is ~1361 W/m²; surface GHI
  cannot exceed it, and values above ~1200 only occur with cloud-edge
  focusing." beside `_MAX_PLAUSIBLE_GHI = 1400.0`. The comment's own bound
  is 1361; the constant admits 1362–1400 without saying why (sensor slack,
  presumably). Raw count 17; the 16 vetted-out entries and their reasons are
  in the script's `ALLOW` dict (backlog item numbers, example quantities,
  narrative measurements, and two prose roundings noted below).
- `comment_symbols.py` → `RESULT loose_missing_vetted=1`:
  `thermal_model.py:189–192` — "Attribute writes after construction (the
  set_thermal_params service) call ``clamp`` again" — the service is
  `set_thermal_parameters` (services.yaml, README, configuration.md).
  Strict tier: 0 of 1,120 missing after vetting (raw 3: an elided prefix
  ``MIN_POWER``, the external integration name `tuya_heat_pump`, and
  `MixedHotWater` for `MixedHotWaterSensor`).
- `comment_symbols.py` → `RESULT redundant_single_line_comments=11` raw; by
  reading, three restate the next line and eight are section labels or
  attribute docs (`#:`) that are fine:
  `coordinator.py:4353` `# Fetch prices from Tibber` → `await self._fetch_tibber_prices()`;
  `optimizer.py:671` `# savings as percentage` → `savings_percentage: float`;
  `thermal_model.py:1830` `# Solar gains per zone` → `q_solar_upper, q_solar_lower = self.solar_gain_per_zone(...)`.
- Two prose roundings, noted and not counted: `defrost.py:93` "less than
  half its rated output" beside `DERATE_MIN = 0.55`; `defrost.py:120` "a
  third of its life defrosting" beside `DEFROST_DUTY_MAX = 0.3`.

**Instrumented symbol.** `custom_components/heatpump_optimizer/open_meteo.py:_MAX_PLAUSIBLE_GHI`
(comment_numbers.py); `thermal_model.py:ThermalParameters.__post_init__`'s
comment (comment_symbols.py).

**Perturbation.** Set `_MAX_PLAUSIBLE_GHI = 1361.0` (or reword the comment to
state the slack) → `constant_comment_mismatches_vetted` 1 → 0 (to_zero).
Renaming `set_thermal_params` to `set_thermal_parameters` in the comment →
`loose_missing_vetted` 1 → 0.

**Metric.** Constants whose attached comment cites at least one number and
none equals the value under the listed conversions, after vetting; comment
references to identifiers that nothing in the tree defines, after vetting.

**Fix scope.** Five comment edits; no behaviour.

**Judgement on the long comments (qualitative, seed 5, 24 of 515 blocks).**
Every sampled block explains *why* — a rejected alternative, a measured
number, a failure the design prevents — and none was wrong against the code
beside it. They are precise and often long: `const.py:389` spends 19 lines
on the history of the cycling-cost default, `const.py:1078–1090` on the
economy-mode measurement. That is a house style, not a defect; nothing in
the sample "explains what the next line obviously does". The redundancy list
above is the whole of what the heuristic found across 5,825 comments.

## Non-findings (checked and held)

| Claim | Command | Value |
|---|---|---|
| No broken internal link outside the export-removed `docs/backlog.md` | `links.py` | `broken_internal_paths_excluding_export_removed=0` of 46 (3 broken all point at docs/backlog.md, removed by the export) |
| No broken anchor | `links.py` | `broken_anchors=0` |
| Every external link answers 200 to HEAD | `links.py` | `external_links_total=6`, `external_broken=0`, inconclusive 0, unreachable 0 |
| README and docs do not duplicate each other | `duplication.py` | `exact_duplicate_units_cross_file=0` of 538 units; `near_duplicate_pairs=1` (README:420 sequence diagram ↔ how-it-works.md:54, J=0.57); `readme_twin_share=0.043` |
| Backticked symbols in production comments/docstrings exist | `comment_symbols.py` | `refs_production_strict=872`, `strict_missing_vetted=0` (raw 3, all vetted with reasons) |
| Backticked and bare symbols in the card's comments exist | `comment_symbols.py` | `refs_card_strict=248`, `refs_card_loose=42`, 0 missing |
| Symbols in tests' comments exist | `comment_symbols.py --tests` | `refs_tests_strict=357` raw missing 2 (`sensor.zz_probe_*` glob, `HASTUB_TZ=Europe/Stockholm`), `refs_tests_loose=206` raw missing 3 (`marginal_price` formula, `SelectEntity` ×2, an HA class) — all false positives on reading |
| Docstring "default N" claims match | `comment_numbers.py` | `docstring_default_claims=2`, `docstring_default_mismatches_vetted=0` |
| architecture.md: 45 modules, exactly ten import `homeassistant` at module level, only `inputs.py` touches it elsewhere (inside a function) | `reader_paths.py` A1, A2 | pass (45; 10; inputs.py function-level import, no other) |
| Eleven services, in README, architecture and configuration | `reader_paths.py` A3 | pass (services.yaml: 11) |
| `set_thermal_parameters` 28 fields, `simulate_plan` 11 fields, `assign_entity` 21 keys all listed | `reader_paths.py` C1–C3 | pass (28; 11; 21 = `topology.ASSIGNABLE_KEYS`) |
| README sensor table has 55 rows; six sensors disabled by default; README and architecture agree on 65/55 | `reader_paths.py` M2–M4 | pass (55 rows; 6 `entity_registry_enabled_default = False`; test-pinned by `tests/entities.py`, for D6) |
| Manual plan pins for up to 20 hours | `reader_paths.py` M1 | pass (`MANUAL_PLAN_WINDOW_HOURS=20`) |
| Card: 900×380 view box, hours 1..168, "about 200 keys, no Swedish entry missing" | `reader_paths.py` D1–D3 | pass (900×380; `hours > 168` guard; 232 en / 232 sv keys, 0 missing) |
| Capacity-tariff window offers 15 min / 1 h | `reader_paths.py` C4 | pass (`_select(["15", "60"])`) |
| how-it-works' "90- and 120-minute tariffs meter correctly" is reachable | `reader_paths.py` C5 | held as written: the code steps windows by length; the UI offers 15/60 and `set_thermal_parameters` has no window field — noted for D6 as a capability the reader cannot select |
| ECL110: ON when a circuit clears max(0.1 kW, half the modulation floor); eight settings on both pages | `reader_paths.py` E2, E3 | pass (`on_threshold = max(0.1, p.min_electrical_power * 0.5)`; 8 = 8) |
| tests/README: 48 combinations / 17 edge cases; "1 of 16" scripts | `reader_paths.py` T8, T9 | pass (7·2·2 + 2·7 + 3·2 = 48; `edges` dict 17; 16 closures) |
| Version strings in docs are historical ("since v5.0.0") and ≤ VERSION | `grep -o 'v[0-9]+\.[0-9]+\.[0-9]+'` over docs | 25 citations, max v6.2.5 ≤ 6.2.14; only README "Project status" reads as current (D5-04/S1) |
| The card's console example "v4.3.0" is framed as an example | `reader_paths.py` D4 (info) | `CARD_VERSION=5.4.17`; the paragraph says the card version is often lower and to compare with the release notes |
| README vs DISCLAIMER baseline wording | `reader_paths.py` W1 (info) | README: "conventional thermostat following the same comfort schedule, only the hot-water half always-on"; DISCLAIMER: "simulated always-on thermostat" — wording, for D6 |

Run logs with every RESULT line are reproduced at the end of this file.

## Reader-path notes (the dead ends, by path)

- **P1 — new user, HACS to first plan** (`dead_ends_new_user=4`): R2 (two
  orphaned program plans under docs/ that the Documentation table does not
  mention), E1 (ECL110 topics: told to leave blank, ships non-empty,
  publishes each cycle), C6 (throttling valve undefined — inferable), S1
  (Project status a major version behind). Held: the quick start is
  complete and self-contained; every option it names exists on the page it
  says; all 46 internal links resolve; the README's "Your first week"
  matches `Run System Identification`'s gating in configuration.md and
  how-it-works.md. Unverified here: HACS renders README.md in-app
  (`hacs.json: render_readme`); whether its renderer draws the three mermaid
  blocks or shows them as code could not be checked without HACS.
- **P2 — configuring a feature** (`dead_ends_feature=4`): E1 (ECL110), C6
  (two-tank layout "requires a throttling valve"), H1 and H2 (editing
  artefacts in the buffer-tank and reason-code sections of how-it-works.md,
  which is the page the feature reader is sent to). Held: two-tank storage
  is described consistently across configuration.md:358 ("the switch for the
  two-tank model"), the layout catalog and how-it-works.md:839–857; ECL110
  options, sensors and the lag model agree between ecl110.md,
  configuration.md and the code; the capacity tariff's Grid-costs table
  agrees with the selector, and the 90/120-minute remark is a code
  capability the UI does not expose (for D6).
- **P3 — developer running the tests** (`dead_ends_developer=8`): R1
  (tests/README.md unreachable from README), T1–T7 (D5-01). Held: the
  run.sh invocations in tests/README.md match run.sh; the closures
  description matches `closure.py` (INERT excepted); `GOLDEN_REF` guidance
  matches `env_drift.py`'s refusal of HEAD (tools/audit/README.md says the
  same).

## Harnesses

- `tools/audit/round2/D5/links.py` — link check (internal, anchors, external HEAD)
- `tools/audit/round2/D5/duplication.py` — paragraph hashing and near-duplicate measure
- `tools/audit/round2/D5/comment_symbols.py` — comment-named symbols, redundancy heuristic, long-block counts (`--tests` includes tests/)
- `tools/audit/round2/D5/comment_numbers.py` — numbers in comments vs the constant beside them; docstring defaults
- `tools/audit/round2/D5/reader_paths.py` — 36 doc-vs-tree checks, link-graph reachability, heading skips, per-path dead ends

Each runs from the export root with
`PYTHONPATH=tests/hastub .venv/bin/python <path>`; the expected values are in
each header.

## What was not finished

- Long comment blocks were judged by a fixed-seed sample of 24 of 515 (plus
  reading every block the two executable checks flagged), not all 515; the
  862 docstrings were checked executably (symbols, defaults) but not each
  read for concision.
- Release-history claims — README "Project status", dashboard-card.md
  "v5.0.0 ships card 4.3.0 unchanged", every "since v4.1.0 / v5.0.0 / v5.1.6
  / v5.1.7 / v5.3.0 / v6.2.5" — cannot be checked in this export
  (`RELEASE_NOTES.md` removed); they are listed for D6 with that caveat.
- Whether HACS's in-app README view renders mermaid was not checked.
- The `--tests` pass of the symbol checker over tests/ comments was run for
  the record; its five raw misses were read and are all false positives, but
  no `ALLOW` entries were added for them (the headline counts exclude tests).

## For D6 (claims met on the way, tagged, not audited here)

README 65 entities / 55 sensors / 4 binary / 4 buttons (test-pinned);
"Six sensors are disabled by default" and the six names; "up to 20 hours";
"Since v5.0.0 entity names are translated"; ecl110.md "at most 0.5 K per
week", "first eight hours", "displace minus 2 °C" (`PEAK_GUARD_DISPLACE_NUDGE_C`),
"rounds to a whole number"; how-it-works "6-hour window" congestion premium,
"2.6–4.7 kWh", "2.2 % / 0.2 %" multi-start, "25th-percentile price",
"100 litres" store threshold, "0.05–3.0 °C/h", "[0.5, 1.6]" cop_scale, "30 %"
tracking gate, "five consecutive days" drift alarm, "8 snapshots", "1.5×"
CUSUM cap, "60/180/30 minutes" staleness limits, "90 minutes" outage gap,
"two hours"/"45 minutes" recovery, "10 SEK/kWh" fee bound; dashboard-card
"about 200 keys" (232), "1 to 168", "20 hours read from
`manual_plan_window_hours`"; configuration.md every default and range in
its tables; the ECL110 default-topic publish consequence (D5-02, for D10);
the 90/120-minute window remark (C5); README vs DISCLAIMER baseline wording
(W1).

## Exposure

The export removed `docs/audit-*.md`, `docs/backlog.md` and
`RELEASE_NOTES.md`; none was read. What I was exposed to:

- Earlier finding ids cited in code and tests (context, not used as a
  to-do list): `coordinator.py` (D1-01, D1-02, D10-06, D10-07, D10-09,
  D8-02), `optimizer.py` (D9-01), `snapshots.py` (D1-05), the card
  (D4-01, D4-02, D4-03, D4-06), `tests/features.py` (D1-01, D1-02, D1-05,
  D3-02, D3-03, D3-04, D3-05, D3-07, D7-03, D8-02, D9-01, D10-06/07/09),
  `tests/entities.py` (D3-06, D3-08), `tests/optimality.py` (D9-01),
  `tests/card.mjs` and `tests/card_browser.mjs` (D4-01).
- `tools/audit/README.md` (required reading): its "traps" list names
  `tests/closure.py:96`'s `SLOW_GATED` assertion, the `FakeHass` executor
  trap, the `plan_view.py` path scheme and the `__main__`-guard roster; the
  path scheme and NOT_A_TEST roster overlap with D5-01 (T4, T5) and were
  re-derived from the tree, not taken from that file.
- `docs/plan-open-issues.md` (first 40 lines and headings): the delivery
  status of #86–#101 and the CodeQL alerts, v5.6.2–v6.0.0.
  `docs/plan-card-decomposition.md` and `docs/plan-v4.0.0-program.md`
  (first 40 lines and headings). Read only to classify them for the link
  graph and orphan check.
- README "Project status" names the backlog, the v4.0.0 program and "an
  audit train" (v4.0.x–v5.0.0) without detail.
- `tests/README.md:170` mentions "six known instances of a test that looked
  like it ran and asserted nothing" (no ids).

## Run logs (final)

```
links.py
RESULT internal_links_total=46 count
RESULT broken_internal_paths=3 count
RESULT broken_internal_paths_excluding_export_removed=0 count
RESULT broken_anchors=0 count
RESULT external_links_total=6 count
RESULT external_broken=0 count
RESULT external_inconclusive=0 count
RESULT external_unreachable=0 count
RESULT thread_factor=1.006  load1=2.73  swapins=11460048

duplication.py
RESULT units_total=538 count
RESULT words_total=37454 count
RESULT exact_duplicate_units_cross_file=0 count
RESULT near_duplicate_pairs=1 count
RESULT duplicated_words=237 count
RESULT readme_words_with_a_twin=237 count
RESULT readme_twin_share=0.043 ratio
RESULT thread_factor=1.000  load1=2.73  swapins=11460048

comment_symbols.py
RESULT refs_production_strict=872 count
RESULT missing_production_strict_raw=3 count
RESULT refs_production_loose=209 count
RESULT missing_production_loose_raw=7 count
RESULT refs_card_strict=248 count
RESULT missing_card_strict_raw=0 count
RESULT refs_card_loose=42 count
RESULT missing_card_loose_raw=0 count
RESULT strict_missing_raw=3 count
RESULT strict_missing_vetted=0 count
RESULT loose_missing_raw=7 count
RESULT loose_missing_vetted=1 count
RESULT redundant_single_line_comments=11 count
RESULT long_comment_blocks_production=515 count
RESULT long_comment_blocks_card=242 count
RESULT thread_factor=1.000  load1=2.75  swapins=11460056
(--tests adds: refs_tests_strict=357 missing_tests_strict_raw=2
               refs_tests_loose=206 missing_tests_loose_raw=3)

comment_numbers.py
RESULT numeric_constants_scanned=432 count
RESULT constants_with_numbers_in_comment=65 count
RESULT constant_comment_mismatches_raw=17 count
RESULT constant_comment_mismatches_vetted=1 count
RESULT docstring_default_claims=2 count
RESULT docstring_default_mismatches_raw=2 count
RESULT docstring_default_mismatches_vetted=0 count
RESULT thread_factor=1.000  load1=2.77  swapins=11460056

reader_paths.py
RESULT doc_fact_checks_total=36 count
RESULT doc_fact_checks_failed=15 count
RESULT failed_in[README.md]=2 count
RESULT failed_in[docs/]=1 count
RESULT failed_in[docs/configuration.md]=2 count
RESULT failed_in[docs/dashboard-card.md]=1 count
RESULT failed_in[docs/how-it-works.md]=2 count
RESULT failed_in[tests/README.md]=7 count
RESULT unreachable_docs_from_readme=3 count
RESULT tests_readme_drift=7 count
RESULT ecl110_guidance_contradiction=1 count
RESULT content_defects_user_docs=5 count
RESULT dead_ends_new_user=4 count
RESULT dead_ends_feature=4 count
RESULT dead_ends_developer=8 count
RESULT thread_factor=1.000  load1=3.24  swapins=11460064
```
