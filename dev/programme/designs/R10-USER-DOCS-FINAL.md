# R10-USER-DOCS-FINAL design note (designer seat, `dev/governance/roles/designer.md`)

Read at `origin/main` 14ed135512e3d7db899081f2c2639ce5674b8f2a. The roster was read at `handoff/audit-r10-roster`
5fdf8b4581ef865cdfb7f029205a7966a9f15597. This group has no predecessor, and the re-scope carry dropped every
after-edge, so there is no predecessor head. R10-USER-DOCS-VERIFY (M) reuses this note's sections 2, 3 and 4 and
has no design of its own.

## Owning seam

The check is owned by `tests/doc_claims.py`. It already holds three of the enumerators this design needs:
`entity_census`, `registered_service_fields` and `options_field_pages`. It also holds the marker resolver
(`_MARKER`, `marker_census`, `--markers`). The pages are content, and no code calls them. Production code is only
read: `custom_components/heatpump_optimizer/config_flow.py` (`_OPTION_PAGES`, `_OPTION_FIELDS`),
`custom_components/heatpump_optimizer/__init__.py` (`PLATFORM_LIST`), `custom_components/heatpump_optimizer/notifier.py`
(`EVENT_*`) and `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js` (`DEFAULTS`, the
`tab("<id>"` calls). `tests/seam_map.json` maps only coordinator methods, so it says nothing here. One owner, no
production change, no design finding.

## 1. Page map

Each surface class has exactly one **home**: a page, a section, and a shape the coverage arm can read. Other
pages may mention a surface, but the home is where its description and default live.

| class | source in the tree | home page, section | home shape |
|---|---|---|---|
| `entity` | `entity_census({CONF_DHW_TANK_VOLUME: 200.0})` over `PLATFORM_LIST` | `README.md` `## Entities` | a table row whose first cell is the translated name; default = enabled or disabled by default |
| `service` | top-level keys of `services.yaml`, anchored equal to `registered_service_fields()` | `docs/configuration.md` `## Services`, summary row in `README.md` `## Services` | a `**`name`**` paragraph, and a table row |
| `setup_step`, `setup_field` | `config.step` in `translations/en.json` | `docs/setup.md` (step), `docs/configuration.md` `## Initial setup` (field) | `## Screen`/`### n ·` heading; table row with a Default cell |
| `option_page` | `_OPTION_PAGES` | `docs/configuration.md` `## Changing settings later` | `### <title>` heading |
| `option` | `_OPTION_FIELDS` (key, step, default), label from `options.step` | under its page's `###` heading | table row, first cell `_label()`-equal to the label, with a Default cell |
| `blueprint` | every YAML file in `blueprints/automation/` | `docs/automations.md` `## Blueprints` | a bullet linking the file's raw URL |
| `event` | `notifier.py` `EVENT_* = f"{DOMAIN}_…"` | `docs/automations.md` `## Events` | a table row |
| `card_view` | the card's `tab("<id>"` calls, plus the compact card | `docs/dashboard-card.md` | `## Reading the chart` (plan) or `## The <id> page` |
| `card_option` | `DEFAULTS` keys ∪ `config.<key>` reads in the card | `docs/dashboard-card.md` `## Configuration options` | a `` | `key` | `` row with a Default cell |
| `repair` | `issues` in `strings.json` | `README.md` `## Troubleshooting` | a bold lead naming the issue's title |

What is measured at 14ed13551: there are 82 entities (62 sensor, 6 binary_sensor, 6 button, 6 switch, 1 climate,
1 datetime), 14 services, 15 setup steps, 23 option pages, 205 option fields, 4 blueprints, 5 events, 5 card tabs, 10 card
options and 26 repair issues. Every entity name, every service name and every normalised option label appears
somewhere in the corpus already. So bare mention is satisfied, and the coverage arm has to check the **home
shape** and the default. Some homes are not there: 8 of the 205 option labels are not the first cell of any
table (the seven `dhw_windows_*` weekdays and `debug_collect_enabled`), and none of the 26 repair issues is named
by title or key.

**Two readings the design review should confirm.** (a) The brief lists `number` and `select` platforms. The tree
has neither, and it has `datetime`, which the brief does not list. The enumeration follows `PLATFORM_LIST`, never
the brief's list. (b) `repair`, `event`, `setup_*` and `card_option` are wider than the brief's five classes. They
are in because the brief's test is "every user-facing feature". If the review strikes `repair`, the class moves to
the exemption list with that ruling as its reason. Entity attributes are not enumerated: no brief item names them, and no
registry lists them. Their exemption is class-level, and a group that adds an attribute documents it itself.

**Pages, and what each pass does.** All seven pages get the correctness pass (section 4) and the stateless pass.
The following get rewritten, because history is mixed into how they describe the integration:

- `README.md` `## Entities`: the intro (#1669, "Since v5.0.0", "Since #1335") and the "Renamed from … by #174" notes.
- `docs/setup.md`: v6.6.5 and #1258.
- `docs/how-it-works.md`: the v3.9.0, v5.1.7 and v5.3.0 paragraphs, rewritten to state what the integration does.
- `docs/dashboard-card.md`: #1227, v4.1.0+, v4.2.0 and v6.2.5.
- `docs/ecl110.md` and `docs/configuration.md`: v4.1.0.

Homes for the round-10 additions the brief names:

- Away mode and its recovery: `docs/configuration.md` `### Away and holiday mode`, `docs/how-it-works.md`
  `## Away and holiday mode`, and the `set_away` row.
- The learner reset: `reset_heat_loss_learners`, plus `### The house heat loss coefficient`.
- The heat-loss learner's inputs, and what an estimated power reading means: `## The learning loops`, from
  R10-HOTFIX-LEARNER-INPUTS' merged diff.
- The factory reset and the wood windows: still in flight (section 3).

`docs/index.html` and `docs/architecture.md` are out of scope. They are `check_product_page` and R10-ARCH-DOCS.

## 2. The enumeration rule

The fixer adds one command: `python3 tests/doc_claims.py --surfaces`. It is dispatched in `__main__` beside
`--markers`, and it prints one sorted tab-separated line per surface:
`class  id  label  home-page  home-found(0|1)  default`. Its sources are exactly the ones in the table above.
Nothing in it is a list kept by hand. `--surfaces` exits 1 while any non-exempt row has `home-found 0`.

The suite arm `check_surface_coverage` calls the same function (`surface_rows()`), so the CLI and the gate cannot
differ. There is no committed snapshot, because a carried count goes stale. VERIFY takes its delta by running the
command twice, at the draft's merge commit and at its own base, and diffing:

    diff <(cd "$DRAFT_WT" && python3 tests/doc_claims.py --surfaces) <(python3 tests/doc_claims.py --surfaces)

The diff's added lines are what landed after the draft. Its removed lines are features to delete from the pages.

## 3. Drafting while code groups land

Surfaces that are stable at main: everything `--surfaces` prints at the fork. The draft documents all of them.

Surfaces in flight, by group, at roster 5fdf8b458:

| group | stage, head | user surface it moves | how it is covered |
|---|---|---|---|
| R10-FACTORY-RESET | in-progress, no head | a new service (scope, `entry_id`), a new options menu step | new rows: the coverage arm turns its PR red until it writes the homes |
| R10-WOOD-NOTIFY | handoff `0d47d35cc` | a lead-time option, a new blueprint, window attributes on Wood Cheaper Than Heat Pump | option and blueprint: the coverage arm; attributes: a marker on the README row |
| R10-COP-GATE | carries-open, `d081ec7ad` | a "COP not measurable" reading | a marker in `### COP, and the tracking-error gate` |
| R10-UX-HEALTH | carries-open, design `e6797ca9d` | the card's Health page | a marker under `## The health page` |
| R10-CEILING-PROBE | design rev 3, `2212054e9` | a ceiling step in the experiment | a marker in `### Active system identification` |
| R10-COP-PARTLOAD | PR #2872 | a part-load COP term | a marker in `### COP, and the tracking-error gate` |
| R10-ARCH-SHAPES-CLASSIFIER | queued | sub-running steps read as idle | a marker under `### Why a step is idle` |

A new surface needs no marker, because the coverage arm reads it from the tree the moment it lands. A **changed**
surface does need one, because the arm cannot see that a description went stale. The marker is the existing
grammar, wrapped in an HTML comment so neither GitHub nor the Marketplace renders it:
`<!-- [target: R10-COP-GATE] -->`, on the line above the paragraph that changes. `check_marker_census` and
`--markers` grow a `USER_DOCS` tuple beside `WIRING_DOCS`. A due marker prints and does not fail, as now, so a
landing code group never turns main red. The stateless arm ignores comments. VERIFY ends with
`--markers` showing 0 user-doc markers.

Edits in flight on the same pages: R10-WOOD-NOTIFY touches `docs/configuration.md` and `docs/automations.md`, and
R10-ARCH-DOCS touches `README.md`. Each is a distinct section from the draft's, so they are hot-file overlap by seam.
Whichever merges second rebases. The draft does not pre-write another group's section.

## 4. The claim-check method VERIFY inherits

Every arm reads the tree, and every arm carries an anchor and a null control.

1. **Coverage** (`check_surface_coverage`). Every `surface_rows()` row has `home-found 1`, or appears in
   `SURFACE_EXEMPT: dict[tuple[class, id], reason]`. A reason must be two or more words. An exemption naming an id
   that is no longer enumerated is red, so the list cannot rot. For `option`, `setup_field` and `card_option`, a
   literal default must also equal the row's Default cell, after the unit and locale normalisation the
   `check_ecl110_defaults` arm uses. A computed default (`_STORED`, a callable, or a copy of a weekday value) needs a
   non-empty cell that does not name a number. Red fixture: a planted service in a probe `services.yaml` dict. Null
   control: the tree as it is.
2. **Stateless** (`check_stateless`). It scans the seven pages after stripping code spans, fences, HTML comments
   and link targets. The lexicon is `new in`, `since (v\d|version|#\d)`, `previously`, `no longer`, `used to`
   (the history sense), `until v\d`, `as before`, `renamed from`, `\bv\d+\.\d+`, `#\d{3,}`, `R\d+-`,
   `\bround \d`. A purpose-sense `used to` (sentence start, or after `,`, `is`, `are`, `only` or `also`) passes.
   The bare word `now` is not in the lexicon: there are 69 hits, nearly all of them "right now" or a UI label.
   `STATELESS_EXEMPT` holds `(page, fragment, reason)` entries, each of which must match exactly once. Red fixtures:
   a planted "new in v9" and a planted "previously". Null control: "previous day". Baseline at 14ed13551 for the
   seven pages: `used to` 14, `no longer` 7, `since v/version` 5, `v\d.\d` 20, `#\d{3,4}` 10, `new in` 1,
   `previously` 1.
3. **Correctness.** The existing arms stay green: service fields, entity counts and enum states, option labels and
   page placement, UI labels, ECL110 defaults, figures and card figures. Re-take the card pictures with
   `tests/card_browser.mjs` when a view changes. A prose claim that no arm reads (a number, a unit or a behaviour)
   goes into the body's claim table: `page:line | claim | tree symbol | verdict`, each resolved to a `const.py`
   name or a function. VERIFY re-opens only the claims whose symbol appears in
   `git diff <draft-merge>...<base> -- custom_components blueprints`.
4. **Drift attribution.** For each line that differs, VERIFY names the group by
   `git log --format=%s <draft-merge>..<base> -- <the symbol's file>`.

## Alternatives rejected

- **A separate surfaces module under `tools/audit/`.** It would take the three enumerators out of `tests/doc_claims.py`,
  which keeps calling them for its counts. That makes two owners of one fact set, and a new file to classify.
- **A committed surface snapshot (JSON).** It is a carried count, it is wrong after the first code merge, and the
  live two-run diff in section 2 gives the delta without it.
- **A visible `[target: …]` in user pages, or an external in-flight ledger.** The visible marker breaks item (6)
  on the rendered page. A ledger cannot point at the sentence after edits move it. The comment-wrapped marker reuses
  `marker_census` and adds no mechanism.
- **Mention-level coverage.** It passes 100 % today, so it pins nothing.

## Sibling sites

`grep -rnE 'async_register|vol.Schema|_F\("|async_add_entities|async_fire|tab\("' custom_components/heatpump_optimizer`.
Every site belongs to one class above. The covers that are out of scope: `diagnostics.py` (downloaded, never
shown as a feature) and the `exceptions` text in `strings.json` (31 errors the UI shows inline, belonging to the
service they refuse).

## Evidence plan, by file

- `tests/doc_claims.py`: `surface_rows`, `check_surface_coverage`, `check_stateless`, `--surfaces`, `USER_DOCS` in
  the marker census. Each arm is failing first, on its fixture, and its null control is green on the tree.
- Mutation targets: the `home-found` predicate, the default comparison, the `used to` purpose guard, and the stale
  exemption check.
- No golden moves, so both claim files stay byte-identical.
- `tests/closure.py`: `doc_claims.py` now opens `services.yaml`, `config_flow.py`, `notifier.py` and the card. Move
  any of them that is INERT into its recorded closure, as the R10-README-GRAPHICS block did.

## Hot files and serial position

`README.md` and `tests/doc_claims.py`, the group's own `hot_files`. The draft starts now. Whichever merges second,
the draft or any of R10-WOOD-NOTIFY, R10-ARCH-DOCS or R10-FACTORY-RESET, rebases. R10-USER-DOCS-VERIFY comes after
all of them.

## Notes for the fixer

- Carry: R10-FACTORY-RESET (item udf-reset-homes). If the draft merges first, the new service needs a `**`name`**`
  paragraph under `docs/configuration.md` `## Services` and a row in `README.md` `## Services`, and the new options
  step needs a `### <title>` section, or `check_surface_coverage` is red on your PR.
- Carry: R10-WOOD-NOTIFY (item udf-wood-homes). The blueprint bullet goes in `docs/automations.md` `## Blueprints`
  (and the README list). The lead-time option is a row with a Default cell under its page's heading. Resolve the
  `<!-- [target: R10-WOOD-NOTIFY] -->` marker on the Wood Cheaper Than Heat Pump row once you document the window
  attributes.
- Carry: R10-USER-DOCS-VERIFY (item udf-method). Run sections 2–4 as written: the two-run `--surfaces` diff,
  `--markers` showing 0 user-doc markers, the claim table re-opened by symbol diff, and drift named by `git log`.
- Carry: dismissed: UI strings are outside the user docs (item udf-strings-history). `strings.json` carries history
  wording ("used to be a flat repeat", "as before" in `price_prior_enabled` and `price_risk_lambda`). The stateless
  item covers the docs only, so this group leaves it; the designer's report hands it to the orchestrator.
