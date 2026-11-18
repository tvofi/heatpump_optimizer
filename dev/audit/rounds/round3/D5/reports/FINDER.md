# D5 — docs structure, flow and content; comments in code

Round 3. Baseline `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1`.
Tree: `git archive` export, no `.git`, with `docs/audit-*.md`, `docs/backlog.md`
and `RELEASE_NOTES.md` removed.
Box: 8-core Apple M1, 8 GB, python3 3.11.5, node v20.10.0. Shared and very
busy: `load1` ran between 4.0 and 201.9 across the session. **Every number in
this report is a count over static text or over a driven code path.** No wall,
CPU or RSS number is claimed, so contention cannot move anything here; each
harness still prints `load1` and `thread_factor` beside its RESULT lines.

## Method

Six harnesses under `tools/audit/round3/D5/`, each runnable by the single
command in its own header, each accepting `D5_ROOT=<dir>` so a perturbation can
be run against a copy without touching the tree under review. Two of them drive
production code rather than reading it:

- `entity_doc_coverage.py` runs the real `async_setup_entry` of all six
  platforms and gets 74 entities.
- `option_doc_coverage.py` runs `config_flow._page_schema` over all 21 option
  pages with every boolean feature flag on, and gets 213 schema keys, 180 of
  them labelled user fields.

Three reader walks were done against those instruments rather than by
impression: a new user installing via HACS (README → Installation → Quick
start), a user configuring a specific feature (two-tank storage, ECL110,
capacity tariff, wood furnace), and a developer (README → docs/architecture.md
→ tests/README.md). The wood-furnace walk is where the reader path breaks.

All perturbations below were executed on a full copy of the tree under
`$TMPDIR/d5_pert` with `D5_ROOT` pointed at it. The tree under review was
never modified.

## Findings

### D5-01 — 10 rendered option fields, including the whole wood-fuel economics group, are named by no user-facing document (medium)

`config_flow._page_schema` renders 180 labelled fields across the 21 option
pages. Ten of them appear in none of README.md, docs/how-it-works.md,
configuration.md, dashboard-card.md, architecture.md, automations.md or
ecl110.md — not by config key, not by their `strings.json` label, not by that
label with a trailing parenthetical removed, and not as a single document line
carrying every content word of that label (the last rule is what lets a merged
row such as *"Weekend daytime / night comfort"* count as documenting two
fields, so it is deliberately generous).

Four of the ten are one coherent feature: **wood-fuel economics** —
`wood_type`, `wood_packing`, `wood_price_sek_m3`, `wood_furnace_efficiency`,
all on the `building` page's `wood` section. `wood_fuel.py` turns exactly those
four into a SEK/kWh figure (`WOOD_KWH_M3` × packing, ÷ efficiency, against
`wood_price_sek_m3`) and that figure is the "cheaper-than-pump rule" — the
module's own first line is *"Firewood price and the cheaper-than-pump rule."*
`wood_economics_doc_lines` over those seven documents, counting mentions by
key, by label, or by enumerated value (`birch`, `pine`, `packed`, `loose`,
"cubic metre", "furnace efficiency"), is **0**.

The other six: `space_setpoint_entity`, `dhw_setpoint_entity` (both carry real
behaviour in their `data_description` — the DHW one changes disinfection when
it sits below the disinfection temperature), `day_start_hour_weekend`,
`holiday_day_start_hour`, `holiday_day_end_hour` (docs document the weekday
"Day starts at"/"Day ends at" pair at `docs/configuration.md:87-88` and the
weekend/holiday *comfort temperatures* at `:89-90`, but never the weekend or
holiday *hours*), and `price_surcharge`, which is the one soft entry —
`docs/configuration.md:339` carries it inside a merged "VAT multiplier /
surcharge" row whose wording the rule cannot reach.

Severity `medium`, not higher: each field carries in-flow help text, so the
user is not left with nothing — but a user who wants to check what "Packing"
means, or what price basis the wood-versus-pump decision uses, has no reference
to consult, and the decision is about money.

Not a D6 item: this is not a claim in the docs being false, it is a reader path
that ends nowhere.

### D5-02 — 27 comment sites in production name identifiers that exist nowhere in the repository; 18 of them are the card's own private methods (low)

`comment_symbols.py` builds the repository's code vocabulary from every
`.py/.mjs/.js/.json/.yaml/.sh` file under `custom_components`, `tests`, `tools`,
`.claude` and `.github` with `#`, `//` and `/* */` comments and Python
docstrings stripped first — so a name kept alive only by another comment does
not count as existing. It then takes every backtick span in a production comment
or docstring that is exactly one identifier (formulas, pseudo-code, globs and
dotted external paths are excluded, so `full_price / k`, `factors[a][b]`,
`_init_*` and `homeassistant.util.loop.protect_loop` are not counted) and
checks membership.

739 such mentions; **27 miss**. 18 of the 27 are in
`custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`, and all
18 are `_camelCase` private-method references — 13 distinct names. The card was
refactored from methods to module-level functions and the comments were not
carried across:

| named in a comment | what exists |
|---|---|
| `_lineLabel` (3 sites) | `lineLabel(def, line, isLowerModelled)` at `:3776` |
| `_fieldPoints` | `fieldPoints(s, field)` at `:3692` |
| `_extraFields` (2) | `extraFields(s)` at `:3712` |
| `_seriesUnit` | `seriesUnit(def)` at `:4074` |
| `_resolveEntity` (2) | `resolveEntity(kind)` at `:3923` |
| `_laneGroupInner` | `laneGroupInner(geom)` at `:6540` |
| `_onSlotEdit` | `onSlotEdit(ev)` at `:7676` |
| `_currency()` | `currency` appears only as a translation key |
| `_refreshLayout` (2), `_restoreSlotFocus`, `_chartWidthDrifted`, `_applyView`, `_runWhatIf` | **nothing under any name** — case-insensitive search over the whole 10k-line card returns only the comment itself |

The last five are the sharp end: those comments explain a mechanism by pointing
at a function the reader cannot find at all, which is the opposite of what a
comment is for.

On the Python side the one confirmed instance is
`optimizer.py:6457`, whose docstring says *"``ProcessPoolExecutor`` has to
pickle the callable"*. `ProcessPoolExecutor` occurs exactly once in the whole
repository — in that sentence. The route is a long-lived `subprocess.Popen` on
`process_worker.py` (`coordinator.py:714`, `:752-762`) with explicit pickling,
reached through `_run_in_process` / `_await_process`. The remaining eight
Python misses are shorthand or deliberate negatives and are listed as
non-findings below rather than claimed.

Severity `low`: nothing a user can see. It is squarely the brief's *"comments
that are wrong"*.

### D5-03 — one of the three links in README's control-path navigation block is a dead anchor (low)

`README.md:194` — *"Each path in full: `[Switch and climate entity](#switch-and-climate-entity)`,
`[Inverter frequency…]`, `[ECL110…]`"* (backticked here so this report is not
itself counted by `linkcheck.py`). The
first anchor matches no heading: the section is `### Switches, climate and
datetime entities` at `:494`, slug
`switches-climate-and-datetime-entities`. The other two resolve. On GitHub the
link silently does nothing.

This is the only broken link of 338 scanned in 98 markdown files, so it is
hygiene rather than a pattern — but it sits in the one paragraph whose whole
job is to route the reader to the control path they have hardware for, which is
the first decision the "Supported heat pumps and controls" section asks them to
make.

### D5-04 — README's Project status sends the reader to the superseded open-issues plan, and that plan has no forward pointer (low)

`docs/plan-2026-09-open-issues.md:10` states in its own words: *"It supersedes
`docs/plan-open-issues.md`, which covered #86–#101 and is complete."*
README's Project status paragraph links `docs/plan-open-issues.md` as "the
open-issues program" and never links the superseding document, which is
unreachable from README by any path. `docs/plan-open-issues.md` itself never
names its successor — grep for `plan-2026`, `2026-09` and `supersed` in it
returns nothing — so a reader who arrives there has no way to learn they are
reading a finished plan from `83b7ea0` (v5.5.0) rather than the live one.

`readme_index_omissions=4` is the same paragraph's other half: the README's
`## Documentation` table has 7 entries, while the README links 4 further
documents under `docs/` that the table omits — `docs/automations.md` (a
user-facing document, cited from the Services section and from
`docs/configuration.md:55`) plus the three plan documents. So the index does
not index, and the one plan document that is current is in neither place.

## Non-findings — what was checked and held

| what | command | number |
|---|---|---|
| Internal markdown links resolve | `python3 tools/audit/round3/D5/linkcheck.py` | `broken_file_links=0` of `links_scanned=338` across `markdown_files=98` (this round's own output directory excluded); the only miss is D5-03's anchor. 6 further links point at `RELEASE_NOTES.md`, `docs/backlog.md` and `docs/audit-*.md`, which this export deletes — excluded, they resolve on `main` |
| No prose duplicated between README and docs | `python3 tools/audit/round3/D5/doc_duplication.py` | `duplicated_sentences=0`, `near_duplicate_sentence_pairs=0` over `sentences_scanned=1160` (≥12-word sentences, 8 user-facing documents). The 5-gram Jaccard arm at 0.6 finds nothing either. Perturbation confirms the instrument is live: pasting one README sentence into `docs/configuration.md` gives `duplicated_sentences=1`, `duplicated_words=26`, `near_duplicate_sentence_pairs=3` |
| Every entity the integration creates is documented | `python3 tools/audit/round3/D5/entity_doc_coverage.py` | `entities_created=74` (driven through the real `async_setup_entry` of sensor, binary_sensor, button, climate, switch, datetime), `undocumented_entities=0`. README alone names 73 of 74. Instrument proved live: deleting README's `## Entities` section takes it to `undocumented_entities=39` |
| Heading structure | `python3 tools/audit/round3/D5/doc_structure.py` | `heading_level_jumps=0`, `docs_without_single_h1=0` over the 12 documents reachable from README |
| No document cites a version that does not exist yet | inline scan, `VERSION`=6.3.20 | 102 `vX.Y.Z` citations in `README.md`/`DISCLAIMER.md`/`docs/*.md` and 198 in production comments; **0** newer than `VERSION` |
| Numbers a comment cites match the constant beside it | inline AST scan over every module-level numeric constant in `custom_components/heatpump_optimizer/` | 1 candidate — `const.py:1109 DEFAULT_WIND_SENSITIVITY=0.03` against *"The previous default of 0.15"* — read and confirmed a correct historical statement, not a mismatch. Of the 7 constants carrying an inline numeric comment, 3 flagged and all 3 are the "2" in the unit `W/m2K`. **0 real mismatches** |
| `docs/configuration.md:243` "The eleven fields from setup step 4 reappear here unchanged" | `_page_schema("hot_water", …)` | 11 labelled fields rendered. Holds exactly |
| Orphaned documents are development records, not user documents | `doc_structure.py` | `unreachable_docs=15` of `docs_md_total=24`; 14 of the 15 are ADRs, superpowers plans/specs and `HANDOVER.md`, which are deliberately out of the reader path (`writing-for-agents.md` governs them). The 15th is D5-04 |

## What I could not finish

- **External link liveness.** 211 distinct external URLs. `linkcheck.py
  --external` returns **211/211 `URLError`**, including `https://www.python.org`
  — this box has no outbound network, so this is a measurement of the sandbox,
  not of the links. Nothing about external links is claimed. The command is
  committed and needs one networked re-run.
- **Release-history and backlog claims.** README's Project status and its
  Documentation table reference `RELEASE_NOTES.md`, `docs/audit-2026-08.md`,
  `docs/audit-2026-09.md` and `docs/backlog.md`, all excised from this export by
  the audit harness. Their claims — *"Backlog items 1–33 are all delivered"*,
  *"Every v6.0.0 or later release has its detail in RELEASE_NOTES.md"* — cannot
  be checked here. **for D6.**
- **"Comments that explain what the next line obviously does."** Sampled by
  hand across `optimizer.py`, `coordinator.py`, `thermal_model.py`,
  `const.py` and the card; the comment style in this repository is
  overwhelmingly *why*, not *what*, and the long blocks earn their length. I
  built no executable metric that separates the two honestly, so nothing is
  claimed either way.

## for D6

- `docs/configuration.md:232` — *"The seven temperature fields are exactly those
  from setup step 2, with the same defaults, ranges and cross-checks. Three more
  live here"* implies 10 for the Comfort page. `_page_schema("comfort", …)`
  renders **19** labelled fields. The excess includes the weekend and holiday
  comfort pair and the weekend/holiday day-start and day-end hours — the same
  fields D5-01 reports as undocumented. (The neighbouring hot-water claim,
  "eleven fields", is exact.)
- README's Documentation table lists `docs/backlog.md`; README's Project status
  cites `docs/audit-2026-08.md`, `docs/audit-2026-09.md` and `RELEASE_NOTES.md`.
  All four are absent from this export; none of their claims were checked.
- `README.md:838-846` — the Documentation table's one-line description of each
  document ("The full theory: …", "Every setup field and options page, …") is a
  claim about coverage; D5-01 shows the second one is not true of the wood-fuel
  economics group.
- `optimizer.py:6457`'s `ProcessPoolExecutor` sentence (D5-02) is a factual
  statement about the runtime, not only a stale name.

## Harnesses

| file | metric | baseline |
|---|---|---|
| `tools/audit/round3/D5/linkcheck.py` | unresolvable markdown links (file targets + heading anchors), and `--external` HEAD per distinct URL | `broken_links_total=1`, `broken_file_links=0`, `links_scanned=338`, `markdown_files=98`, `external_links_distinct=211` |
| `tools/audit/round3/D5/comment_symbols.py` | bare backticked identifiers in production comments/docstrings absent from the repository's non-prose code text | `dangling_comment_symbols=27`, `dangling_card=18`, `dangling_card_private_distinct=13`, `dangling_py=9`, `backticked_identifier_mentions=739` |
| `tools/audit/round3/D5/doc_duplication.py` | sentences (≥12 words) repeated across user-facing documents, exact and 5-gram-Jaccard≥0.6 | `duplicated_sentences=0`, `near_duplicate_sentence_pairs=0`, `sentences_scanned=1160` |
| `tools/audit/round3/D5/doc_structure.py` | BFS reachability from README, heading structure, index completeness, supersession pointers | `unreachable_docs=15`, `readme_index_omissions=4`, `superseded_docs_without_forward_pointer=1`, `readme_links_to_superseded_doc=1`, `heading_level_jumps=0` |
| `tools/audit/round3/D5/entity_doc_coverage.py` | entities produced by the real `async_setup_entry` that no user-facing document names | `entities_created=74`, `undocumented_entities=0` |
| `tools/audit/round3/D5/option_doc_coverage.py` | fields rendered by the real `_page_schema` that no user-facing document names | `option_fields_rendered=180`, `option_fields_undocumented=10`, `wood_economics_fields_rendered=4`, `wood_economics_doc_lines=0` |

### Perturbations executed (all on a copy, `D5_ROOT`)

| harness | change | expected | observed |
|---|---|---|---|
| `linkcheck` | append `[x](docs/definitely-not-here.md)` to README | up 1 | `broken_file_links` 0 → 1 |
| `linkcheck` | rewrite the anchor to `#switches-climate-and-datetime-entities` | to zero | `broken_links_total` 1 → 0 |
| `comment_symbols` | `` `_lineLabel` `` → `` `lineLabel` `` (3 sites) | down 3 | `dangling_card` 18 → 15, distinct 13 → 12 |
| `comment_symbols` | append `` # see `_no_such_helper_xyz` `` to optimizer.py | up 1 | `dangling_py` 9 → 10, total 27 → 28 |
| `doc_duplication` | paste one README sentence into configuration.md | up 1 | `duplicated_sentences` 0 → 1, `duplicated_words` 0 → 26 |
| `doc_structure` | add a successor pointer to `docs/plan-open-issues.md` | to zero | `superseded_docs_without_forward_pointer` 1 → 0 |
| `doc_structure` | point README at `docs/plan-2026-09-open-issues.md` | to zero | `readme_links_to_superseded_doc` 1 → 0 |
| `option_doc_coverage` | add a "Wood type" row to configuration.md | down 1 / up 1 | `option_fields_undocumented` 10 → 9, `wood_economics_doc_lines` 0 → 1 |
| `option_doc_coverage` | delete configuration.md's "Wood tank volume" row | up 1 | `option_fields_undocumented` 10 → 11 |
| `entity_doc_coverage` | delete README's `## Entities` section | up | `undocumented_entities` 0 → 39 |

## exposure

The brief sends D5 into `docs/` and into every production comment, so exposure
to earlier-round finding ids was unavoidable. Recorded, and not used as a
worklist — no `D<k>-nn` id in this report came from any of these:

- **Auto-loaded before I could decline it:** `CLAUDE.md` (project instructions,
  loaded at session start), which names the audit programme, tracking issue
  #201, the round briefs D0–D11 and the plan of record.
- **In-tree documents opened, that carry earlier finding ids or PR/issue
  numbers:** `docs/plan-2026-09-open-issues.md` (opened head + grepped;
  3 `D<k>-nn` ids, ~200 PR references), `docs/plan-open-issues.md` (head),
  `docs/HANDOVER.md` (listed only, never opened),
  `docs/plan-card-decomposition.md` (one grep line, `:115` and `:171`),
  `tools/audit/README.md`, `tools/audit/briefs/COMMON.md`,
  `tools/audit/briefs/D5.md`, `tools/audit/round3/BASELINE.md`.
- **Production and test files whose comments cite `D<k>-nn` ids** and which my
  harnesses read in bulk: `coordinator.py` (17), `sysid.py` (11),
  `optimizer.py` (9), `www/heatpump-optimizer-card.js` (33),
  `config_flow.py` (5), `quality_scale.yaml` (7), `sensor.py` (2),
  `grid_fee.py` (2), `thermal_model.py` (1), `snapshots.py` (1); in tests,
  `features.py` (52), `entities.py` (32), `card_browser.mjs` (13),
  `stress.py` (11), `card.mjs` (8), `optimality.py` (3), `rolling.py` (1),
  `nightly_ha.py` (1), `closure.py` (1). Only two were read as prose:
  `optimizer.py:6448-6460` and the card comment sites listed in D5-02.
- **Absent by design, and it cost coverage:** `RELEASE_NOTES.md`,
  `docs/backlog.md`, `docs/audit-2026-08.md`, `docs/audit-2026-09.md`. README
  links all four; their claims are unverifiable in this export and are handed
  to D6.
- No `gh`, no GitHub, no network reached anything (211/211 URLError).
