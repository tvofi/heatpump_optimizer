# D5 — docs structure, flow and content; comments in code

- **baseline**: `7dd68dd327fe3dbfb09f3bd0fe38910c58877697`
- **tree**: `/Users/timmalmstrom/heatpump_optimizer/.claude/worktrees/audit-r4-baseline` (export, no `.git`)
- **machine**: Apple M1, 8 core, 8 GB, macOS 25.6. Shared with the other round-4
  finders throughout; `load1` ran 2.4–12.6. Every number below is a **count over
  file bytes or over one builder call** — contention-immune by construction. No
  wall, CPU or RSS number is reported, so nothing here needs a quiet window.
- **interpreter**: `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`,
  always `PYTHONPATH=tests/hastub`, always from the export root.
- **harness directory**: `tools/audit/round4/D5/`. Consolidated RESULT lines in
  `tools/audit/round4/D5/RESULTS.txt`.

**On the brief's statement that `RELEASE_NOTES.md` is gone:** it is **present**
in this export (the preparation defect that deleted it was repaired before
dispatch). Release-history claims therefore *can* be checked here, and
`versions.py` checks them. `docs/audit-*.md` and `docs/backlog.md` are genuinely
absent, as the brief says; `docs/plan-*.md` is present.

---

## Method

Nine harnesses, each standalone, each with a positive control that must move the
number it reports. The controls matter more than usual here, because seven of
the nine metrics came back at or near zero: without a control, "0 broken links"
and "a broken link checker" print the same thing.

| harness | what it measures | control |
|---|---|---|
| `links.py` | internal + anchor + external link resolution | — (a deliberate mis-target is one edit) |
| `dup.py` | paragraph/sentence duplication by hashing, plus 5-gram near-duplicates | `--selftest` re-reads README as an 8th document: 0 -> 87 paragraph, 197 sentence dupes |
| `comment_symbols.py` | identifiers a comment names that exist nowhere in the tree | `--selftest` injects 3 fabricated names: 20 -> 23 |
| `comment_numbers.py` | numbers a comment cites vs the constant on the next line | `--selftest` multiplies every value by 7: 25 -> 37 |
| `comment_restates.py` | comments whose words are a subset of the line below | `--selftest` injects one restating pair: 20 -> 21 |
| `reader_paths.py` | dead ends on the three reader paths | `--selftest` injects 3 tokens per path: 0 -> 9 |
| `options_placement.py` | `docs/configuration.md` vs the shipped options UI | `--selftest` rotates the section->page map: 4 -> 139 misplaced, 63 -> 200 undocumented |
| `structure.py` | orphan documents, heading-level skips, h1 count | `--selftest` blinds README's outbound links: 2 -> 14 orphans |
| `versions.py` | version strings cited by docs vs `RELEASE_NOTES.md` | `--selftest` injects `v99.9.9`: 0 -> 1 unreleased, 0 -> 1 future |
| `test_doc_counts.py` | counts `tests/README.md` states vs the code's own | two of the three counts agree — that is the control |

Two traps this dimension walked into and out of, recorded so the judge does not
repeat them:

1. **`urllib` reports every https URL broken on this box.** The framework Python
   has no CA bundle wired up, so the first external run printed a uniform, false
   `external_broken_reader=6`. `links.py` shells out to `curl` instead; all six
   URLs return 200. A "100 % of links broken" number is a harness fault, never a
   finding.
2. **A whole-tree token index is not stable during a fan-out.** `comment_symbols.py`
   scanned `tools/audit/round4/`, where the other finders were writing while it
   ran, and the dangling count moved 20 -> 19 between two runs of the same
   command. The index now excludes that prefix and the number is stable across
   repeats.

---

## Findings

### D5-01 — the configuration reference names 15 of the 200 shipped options fields nowhere at all

**Severity: medium.** **Stop-rule class: hygiene.**

`docs/configuration.md` is titled *Configuration reference* and README sends the
reader to it with "Every field and its range is documented in
docs/configuration.md". Its "Changing settings later" chapter has one `###`
section per options page, and the mapping is perfect at the page level — 21
sections, 21 shipped steps, 0 orphan sections, 0 undocumented steps. At the
*field* level it is not.

Executed (`options_placement.py`):

```
RESULT fields_total=200 count            # data fields across the 21 options steps
RESULT rows_total=139 count              # setting-table rows in the matched sections
RESULT fields_undocumented=63 count      # a field with no row in its own page's section
RESULT fields_elsewhere=35 count         #   ... but described somewhere else in the doc
RESULT fields_nowhere=28 count           #   ... described nowhere in the doc
RESULT labels_absent_distinct=15 count   # EXACT arm: the label's text occurs in NO reader doc
RESULT labels_absent_occurrences=34 count
RESULT labels_checked=200 count
```

The 15-label arm is the one to key on: no fuzzy matching at all, just "does this
label's text occur, case-folded, in README.md or any `docs/*.md`", after
stripping one trailing parenthetical (`(optional)`, `(kW/degC)`) which is a UI
convention rather than part of the name.

The 15, by consequence:

| label | pages | why it matters |
|---|---|---|
| `After saving` | **20** | the navigation control on every options page; `docs/ecl110.md` even says "All **eight** settings live on the options page", and the page ships nine |
| `Detect a wood furnace or other heat source` | 1 | the switch the two-tank / wood reader path turns on |
| `Stove or flue sensor` | 1 | its evidence input |
| `Temperature rise that counts as evidence` | 1 | a threshold with no stated unit or range anywhere |
| `How long to keep assuming it after it stops` | 1 | a decay time with no stated unit or range anywhere |
| `What the control entity expects` | 1 | on the *building* page; the doc documents the similarly named `What that set-point entity expects`, which is a **different field on a different page** |
| `Weekend day starts at` / `Weekend day ends at` | 2 | the weekend schedule hours |
| `Holiday day starts at` / `Holiday day ends at` | 2 | the holiday schedule hours |
| `Weekend daytime comfort` / `Weekend night-time comfort` / `Holiday daytime comfort` / `Holiday night-time comfort` | 4 | covered by a *combined* row ("Weekend daytime / night comfort") in the setup walkthrough, so these four are findable in substance though not by name |
| `Surcharge per kWh` | 1 | covered by the combined row "VAT multiplier / surcharge", whose Default/Range cells (`1.0 / 0`, `0-2`) state VAT's range, not the surcharge's |

So of the 15: four are genuinely findable under a combined heading, one
(`Surcharge per kWh`) is findable but with the wrong range beside it, and **ten
are absent in substance** — including all four weekend/holiday hour fields and
the three external-heat detection fields that the "configuring two-tank storage"
reader path is entirely about.

**Mitigation, stated so the severity is not read as higher than it is:** every
one of these fields carries a `data_description` in `strings.json`, so the user
standing in front of the form is not stranded; and a `NumberSelector`'s bounds
render as the slider's own limits. What the reference is missing is the *lookup*
— a user who reaches for the document the README points at does not find the
field. That is a bounded cost with a workaround, hence `medium`, not `high`.

- **evidence command**: `PYTHONPATH=tests/hastub python3 tools/audit/round4/D5/options_placement.py --list`
- **harness**: `tools/audit/round4/D5/options_placement.py`
- **instrumented symbol**: `custom_components/heatpump_optimizer/strings.json:options.step.*.data`
  (the shipped field set) against `docs/configuration.md`
- **metric**: number of distinct options-field labels whose text occurs in no
  reader-facing document, after stripping one trailing parenthetical
- **perturbation**: add a row `| After saving | Return to the section menu |
  menu / close | Where the dialog goes after a save. |` to
  `docs/configuration.md`'s "Comfort and temperatures" table. `labels_absent_distinct`
  must fall 15 -> 14 and `labels_absent_occurrences` 34 -> 14. The reverse
  perturbation — delete the `Buffer tank size` row — must raise both.
- **files**: `docs/configuration.md`, `custom_components/heatpump_optimizer/strings.json`
- **proposed fix scope**: docs only. Add rows for the ten substantively absent
  fields (five of them on "Heating system and heat storage", four on "Comfort and
  temperatures"), give `After saving` one row in the "Changing settings later"
  preamble rather than 21 copies, and split the two combined rows whose Default
  and Range cells cannot be read for both fields at once.

### D5-02 — `tests/README.md` states a suite size the suite has not had for two pull requests

**Severity: low.** **Stop-rule class: hygiene.**

`tests/README.md:356` annotates the script list with

```
python tests/stress.py       # 48 combinations, 17 edge cases, economics
```

`tests/stress.py:sweep_combinations()` returns **51**. `tools/audit/README.md` in
the same tree already records the change ("was 48 before #286/#287's 3
zero-range-bounds scenarios"), so the tree knows; the developer-facing document
was not updated with it.

Executed (`test_doc_counts.py`):

```
RESULT doc_stress_sweep=48 count     RESULT code_stress_sweep=51 count   <- MISMATCH
RESULT doc_stress_edges=17 count     RESULT code_stress_edges=17 count
RESULT doc_validate_cases=22 count   RESULT code_validate_cases=22 count
RESULT counts_checked=3 count        RESULT mismatches=1 count
```

The other two counts are the null control, and they are strong ones: `17 edge
cases` is in **the same sentence** as the stale number, and `22 seasonal
scenarios` is in the same list. A harness that disagreed with documents in
general would have flagged those too.

- **evidence command**: `PYTHONPATH=tests/hastub python3 tools/audit/round4/D5/test_doc_counts.py`
- **harness**: `tools/audit/round4/D5/test_doc_counts.py`
- **instrumented symbol**: `tests/stress.py:sweep_combinations`
- **metric**: count stated in `tests/README.md`'s per-script annotation minus the
  count the named symbol produces, per annotation; mismatches is how many differ
- **perturbation**: add one entry to `tests/stress.py:SEASONS`. `code_stress_sweep`
  must rise by `len(BUILDINGS)` = 3, to 54, and `mismatches` must stay 1 with the
  gap widening. Conversely, editing the README to say 51 must drive `mismatches`
  to 0 and must not move `code_stress_sweep`.
- **files**: `tests/README.md`
- **proposed fix scope**: one word in `tests/README.md`. Worth pairing with a
  gate check, since this is the class of sentence that goes stale silently —
  `test_doc_counts.py` is already that check in miniature and is cheap enough to
  wire into `entities.py`'s documentation section.

---

## Non-findings

Everything checked that held. These are what let a later round call this
dimension dry.

| claim | command | value |
|---|---|---|
| No internal link in a reader document is broken | `links.py` | `internal_broken_reader=0` of `links_scanned_reader=85` |
| No `#anchor` in a reader document fails to resolve to a heading (GitHub slug rules) | `links.py` | `anchor_broken_reader=0`, `anchor_broken_all=0` |
| Every external URL a reader document links resolves | `links.py --external` | `external_broken_reader=0` of `external_urls_reader=6` (all 200 via curl; **urllib reports 6/6 broken on this box — a CA-bundle artefact, not a defect**) |
| The four unresolved reader links point at `docs/audit-2026-08.md`, `docs/audit-2026-09.md` and `docs/backlog.md`, which the export script removed | `links.py` | `absent_in_export_reader=4` — present on main, not defects |
| No paragraph is duplicated between README.md and any `docs/*.md` | `dup.py` | `dup_paragraph_pairs=0` over `paragraphs_ge20w=433` (control: 87 with README doubled) |
| No sentence of >=10 words appears in two reader documents | `dup.py` | `dup_sentence_pairs=0`, `dup_sentence_bytes=0` (control: 197) |
| No paragraph is repeated inside one document | `dup.py` | `intra_doc_repeated_paragraphs=0` |
| No cross-document paragraph pair even *resembles* another | `dup.py` | `near_dup_para_pairs=0` at 5-gram Jaccard >= 0.60; **1** pair at >= 0.30 |
| The three reader paths have no dead end: every entity id, service, UI label, settings-table row, storage-file name and test command they put in front of the reader resolves to a shipped artefact | `reader_paths.py` | `deadends_install=0` / `configure=0` / `develop=0` over `101 + 201 + 35 = 337` actionable tokens (control: 9 injected, 9 reported) |
| Every reader document is reachable by a link walk from README.md | `structure.py` | `unreachable_reader_docs=0` of `reader_docs=6`, `documents_walked=18` |
| No heading skips a level anywhere in README.md, the six reader docs or `tests/README.md` | `structure.py` | `level_skips=0`; `max_depth=h4` (README only; every `docs/*.md` stops at h3) |
| Every one of those documents has exactly one `h1` | `structure.py` | `docs_without_single_h1=0` |
| Only two documents are unlinked, both deliberately | `structure.py` | `orphans=2`: `SECURITY.md` (GitHub surfaces it natively) and `docs/HANDOVER.md` (internal by design; `CLAUDE.md` and `writing-for-agents.md` govern it) |
| No documentation cites a version that was never released, or one ahead of `VERSION` | `versions.py` | `refs_unreleased=0`, `refs_future=0` over `refs_total=9` distinct / `22` occurrences, against `released_total=122` |
| Comments and docstrings in the production package do not name symbols that have vanished | `comment_symbols.py --list` | `dangling_refs=20` of `refs_extracted=995` over `comments_scanned=7292` — **all 20 triaged as prose, none a stale symbol** (see below) |
| A number a comment cites agrees with the constant beside it | `comment_numbers.py --list` | `unit_matched_unreconciled=2` of `unit_matched_citations=4`; `loose_unreconciled=25` of `constants_with_commented_numbers=73` — **both unit-matched cases triaged as correct prose** (see below) |
| Comments do not restate the line below them | `comment_restates.py --list` | `restating_comments=20` of `blocks_checked=846` — all 20 are section-divider labels (`# Buffer tank` above `buffer_tank_volume: ...`), none a redundant explanation |
| The package is commented at a sane density and its long comments are not rare | `comment_restates.py` | `comment_lines=5991` over `code_lines=33419` = `0.179`; `comments_ge3_lines=890` across `files=56` |
| Every `###` section of the configuration reference corresponds to a shipped options page, and every shipped options page has one | `options_placement.py` | `sections_matched=21`, `sections_orphan=0`, `steps_undocumented=0` |
| `docs/configuration.md`: "There are **21 pages**: six on the first menu, and fifteen more behind Advanced settings" | `options_placement.py` + `strings.json` | init menu = 6 pages + "Advanced settings"; advanced menu = 15; 21 steps matched |
| `tests/README.md`: "17 edge cases" | `test_doc_counts.py` | `edges` dict in `tests/stress.py` has 17 entries |
| `tests/README.md`: "22 seasonal scenarios" | `test_doc_counts.py` | `tests/validate.py` makes 22 module-level `run(...)` calls |
| Every `tests/*` path named in `tests/README.md` exists | `reader_paths.py` | `deadends_develop=0` over 35 tokens, which are mostly those commands |

### The 20 `dangling_refs`, triaged

None is a stale symbol. Five classes, all prose:

- **Index placeholders**: `factors[temp_bucket][humidity_bucket]` (`defrost.py:169`),
  `t_i` (`open_meteo.py:92`), `buckets[decile] = [kw_per_hz_ewma, count]`
  (`freq_control.py:53`), `(cop, dhw_curve, dhw_tank_temp)` (`coordinator.py:3297`),
  `(reduced_draw_kw, coil_heat_kw)` (`thermal_model.py:1210`) — names for the
  slots of a returned tuple or a nested list, not symbols.
- **External vocabulary**: `is_state` / `has_value` (Jinja, `sensor.py:338,388`),
  `input_boolean.holiday_mode` (an example entity id, `away.py:150`),
  `tuya_heat_pump` (another integration's domain, `const.py:98`),
  `ABNORMAL_TERMINATION_IN_LNSRCH` (SciPy's own message, `optimizer.py:1200`),
  `fev_per_jev` (a scipy `approx_derivative` concept, `optimizer.py:322`),
  `MixedHotWater` (named as a *convention*, `thermal_model.py:1681`; the symbol
  beside it, `coordinator._dhw_mixed_water`, does exist).
- **Deliberate statements of absence**: `UPPER_FLOOR_TEMP` (`sensor.py:965` says
  in as many words that no such configuration key exists) and `MIN_POWER`
  (`const.py:80`, shorthand sharing the `CONF_HEAT_PUMP_...` prefix with the name
  before the slash).
- **Globs**: `_init_*`, `sensor....._hot_water_energy`.
- **Section names**: `_learned`.

### The 2 `unit_matched_unreconciled`, triaged

Both correct, and both say so themselves:

- `const.py:1137` `MANUAL_PLAN_WINDOW_HOURS = 20` beside a comment citing 24 h —
  the comment's entire subject is *"20 rather than 24 is load-bearing, so do not
  quietly round it up"*.
- `const.py:1267` `MODE_LAST_GOOD_MAX_AGE_MINUTES = 180.0` beside a comment
  citing 60 minutes — it reads *"Three hours: comfortably longer than the
  reading's own 60 minute horizon"*. The constant is written in minutes and the
  prose in hours; the harness's unit arm cannot bridge that and reported it.

---

## For D6 (claims I met on the way, not verified here)

D6 owns claim-by-claim truth. These are what I walked past; several are probably
fine, and none is a D5 finding.

1. **README badge "Python: 3.13+"** and the Installation callout *"Home Assistant
   2025.2.0 and Python 3.13 are the minimum, and that was a breaking change"*.
   `manifest.json` declares no Python floor and `hacs.json` declares only
   `"homeassistant": "2025.2.0"`. The round-4 audit box runs this tree's tests
   under **Python 3.11** without complaint, so whatever enforces 3.13 is not the
   test suite. Worth a claim check.
2. **README "All 74 entities appear"** and the per-domain headings *Sensors (59
   total)*, *Binary Sensors (5 total)*, *Buttons (4 total)*. `strings.json`
   carries 59 sensor, 5 binary_sensor, 4 button, 4 switch and 1 datetime
   translation key = 73, and the untranslated climate entity makes 74. That is
   arithmetic over `strings.json`, not a run of `tests/entities.py:collect`;
   D6 should close it through the real setup.
3. **README "Six sensors are disabled by default"** — `sensor.py` has exactly six
   `_attr_entity_registry_enabled_default = False`, which agrees, but only D6
   should call a claim verified.
4. **`docs/configuration.md` "The seven temperature fields are exactly those from
   setup step 2 ... Three more live here"** on the Comfort page. The shipped
   `comfort` step has **19** fields (18 settings + `After saving`), and setup step
   2's own table has **9** rows covering 11 fields. Both halves of that sentence
   look wrong; it is a stated count, so it is D6's.
5. **`docs/ecl110.md` "All eight settings live on the options page"** — the
   `heat_curve` step ships 9 fields. The ninth is `After saving`, which is
   D5-01's subject; whether "eight settings" is the right way to count a
   navigation control is a claim question.
6. **`docs/configuration.md` "VAT multiplier / surcharge | 1.0 / 0 | 0-2"** —
   one row, two fields, and the Range cell can only be true for one of them.
7. **`README.md` Acknowledgement** links `strutsfarm/heatpump_optimizer` and
   `strutsfarm/ecl110` while `manifest.json` names `tvofi`. Both URLs resolve
   200; whether the fork attribution is accurate is a claim, not a link.

---

## Exposure

Per `COMMON.md`, everything audit-era I opened, recorded rather than used as a
list of things to re-find:

- **`docs/plan-2026-09-open-issues.md`** — opened by the first `links.py` run,
  which scanned every `docs/*.md`. I read the six regions the link scanner
  flagged (lines 119-194 and 1067), which are a linter's worked examples of
  markdown link syntax. The document is now excluded from the harness corpus by
  name (`PLAN_DOCS`) because it quotes link syntax as data. I did not read its
  plan content, its Delivery-status table or any finding id in it.
- **`docs/plan-open-issues.md`** — one line (`:5`), a link to `audit-2026-09.md`.
- **`tools/audit/README.md`** — required reading per my task; it names round-2
  and round-3 harness paths and the `audit-round2-evidence` tag. I did not open
  any of them.
- **`tools/audit/w5-g5-195-coverage/`** — hit incidentally by one over-broad grep
  for `MixedHotWater`, which matched a coverage `.json` and an `entities.log`
  line naming `#373`. The log line is why `comment_symbols.py` now excludes
  `tools/audit/round4/` from its index; the coverage artefacts are still in the
  index, which is the conservative direction (it can only *reduce* the dangling
  count).
- **In-code finding ids**, which the brief says to treat as context: `D6-03`,
  `D4-05`, `R1-D0-02`, `D9-01`, `T4a`, and a large number of bare `#NNN` issue
  references in `const.py`, `optimizer.py`, `coordinator.py` and elsewhere.
  `comment_numbers.py` strips them as references rather than citations; that is
  the only use I made of them.
- **`RELEASE_NOTES.md`** — heading set only (122 version headings), read by
  `versions.py`. I did not read release bodies.
- **`docs/HANDOVER.md`** — heading/orphan status only, via `structure.py`'s link
  walk. Not read.
- **GitHub**: none. No `gh`, no API. `links.py --external` issues six `curl`
  HEAD/GET requests to `hacs.xyz`, `home-assistant.io`, `python.org`,
  `developer.tibber.com` and two `github.com/strutsfarm/...` pages, and reads
  only the HTTP status code.

---

## What I could not finish

- **`docs/dashboard-card.md` card options were only spot-checked.** Its
  "Configuration options" and "Entity discovery" tables are in the install
  path's token set (`reader_paths.py`, `cardopt` class) and all resolve, but the
  resolver accepts a match against `www/heatpump-optimizer-card.js` *or* against
  `strings.json`, which is generous. A sharper arm — parse the card's own option
  schema and diff it against the doc's tables the way `options_placement.py`
  does for the integration — would be the natural next instrument. I did not
  build it.
- **Prose truth against the code path.** The brief's step 3 asks whether every
  paragraph explaining a mechanism is *true* to the code. I checked structure,
  reachability, duplication, symbol currency and cited numbers; I read code paths
  only where a harness pointed at one (`_solver_status`, `dhw_coil_draw_reduction`,
  `interpret_presence`, `_cop_reference_curve`, `_dhw_mixed_water`,
  `MANUAL_PLAN_WINDOW_HOURS`, `MODE_LAST_GOOD_MAX_AGE_MINUTES`). The 1304 lines
  of `docs/how-it-works.md` and the 764 of `docs/configuration.md` were not read
  paragraph by paragraph against the optimizer. That is the largest uncovered
  area of this dimension and it is not automatable the way the rest was.
- **Docstring quality, as distinct from correctness.** `comments_ge3_lines=890`
  is a corpus, not a judgement. I read perhaps forty of them. Those I read are
  unusually good — they state why rather than what, they name the alternative
  that was rejected, and several carry the measurement that decided the constant.
  I have no executed metric for that impression and so it is not a finding in
  either direction.
- **`--selftest` on `links.py`** is the one harness without a built-in control;
  its perturbation is a one-line edit to a document rather than a flag.
