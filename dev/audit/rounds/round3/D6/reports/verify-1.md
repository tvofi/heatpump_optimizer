# D6 — verifier 1 of 2, refute-first

Baseline `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1`. Box: 8-core Apple M1,
8 GB, python 3.11.5 (numpy 2.4.6 / scipy 1.17.1). `load1` ranged 5.1–13.9
across my runs against the finder's 70.05; `thread_factor=1.0` throughout.
**No number in this report is a timing number.** Every figure is a count of
exact comparisons — entity counts, page counts, schema-field counts, store
keys, verdict-set diffs — so none of it is provisional under contention, and
none of my numbers moved with load.

My harnesses are under `tools/audit/round3/D6/verify-1/`:
`v1_pages.py`, `v1_contents.py`, `v1_census.py`, `v1_services.py`,
`v1_store.py`, `v1_versions.py`, `v1_execution_audit.py`, and two mutation
scripts, `v1_asymmetry.sh` and `v1_docside_all.sh`. Each resolves the
repository as `Path(".")` and each restores every file it mutates from a byte
copy, verified by `cmp` before exit. All three mutated documents and
`claims.csv` are byte-identical to their pre-run state (md5 recorded in the
logs).

---

## 0. Reproduction, and the attack on the dimension's own premise

**Both finder harnesses reproduce exactly.** `store_probe.py` returns
12 / 10 / 2. `claims.py` returns all twelve RESULT counts at their stated
values, and the `claims.csv` it regenerates is **byte-identical** to the
committed one. Wall time 19.5 s against the finder's 112.9 s — a load
difference that carries nothing.

### Attack 1 — "one executed check per claim"

The dispatch asked me to confirm each verdict was *executed* rather than read.
I measured it two ways rather than reading the harness and forming an opinion.

**Static** (`v1_execution_audit.py`, which imports `claims.py` and walks each
row's check function through its code objects and closure cells):

| | |
|---|---|
| claim rows | **150** |
| rows that parse the document they quote | **6** |
| rows whose documented side is a literal in the harness | **138** |
| unverifiable rows | 6 |

The six that parse are `C-CONF-33`, `C-CONF-57`, `C-LINK-01`, `C-MAN-06`,
`C-RM-11`, `C-RM-34`.

**Behavioural** (`v1_docside_all.sh`): corrupt *every* standalone number in all
six mined documents — README, configuration, architecture, how-it-works,
ecl110, dashboard-card — and re-run the finder harness.

```
RESULT claims_compared=150 count
RESULT verdict_changed_when_docs_corrupted=0 count
RESULT result_text_changed_when_docs_corrupted=0 count
```

I verified the mutation actually applies before believing that zero
(`All 74 entities` → `All 747 entities` in the mutated README), because a
mutation that silently fails prints the same zero as a check that ignores the
file.

**What this does and does not mean.** The dominant helper is
`eq(cid, …, measured, expected)`: `measured` is executed against production —
a `getattr` on the real `const` module, a driven flow handler, a registered
voluptuous schema — while `expected` is the documented number typed into the
harness. So the production side of all 144 checked claims *is* executed, and
the specific failure the dispatch warned about — inferring a value from an
absence and never calling the thing that answers it — **is not present here**.
What is not executed is the documented side of 138 of them: the table is a
reliable statement about production joined to the finder's transcription of
the documents.

That matters for a table read as a standing record, less for these four
findings — because I re-parsed the documented side of **every** number the
four findings rest on (13 pages, 7 advanced rows, 6 first-menu rows, 65
entities, 65/55/4/4/1/1, 11/3/3 service fields, "ten" `.storage` files and the
ten names) directly out of the markdown, and every transcription is correct.
No finding turns on a mis-typed quotation.

---

## D6-01 — options-page inventory — **verify**, severity **medium**

### My number, my method

`v1_pages.py` does not iterate `_OPTION_PAGES`. It **walks the dialog**: calls
`async_step_init`, takes the entries the top menu actually offers, calls
`async_step_advanced`, takes that submenu's entries, and drives each to see
what answers `{"type": "form"}`. That counts what a user can reach rather than
rows in a table, so a row present in the table but wired into neither menu
would show up as a difference instead of silently agreeing.

```
RESULT reachable_pages=21 count
RESULT reachable_top=6 count
RESULT reachable_advanced=15 count
RESULT editable_pages=20 count
RESULT unreachable_table_rows=0 count []
RESULT menu_entries_not_in_table=0 count []
RESULT section_expansion_divergence=0 count {}
RESULT doc_pages_configuration_md=[13] parsed
RESULT doc_pages_readme=[13] parsed
```

21 / 6 / 15 / 20 — the finder's numbers, from a different traversal. The table
and the menus agree exactly in both directions, so there is no "counted a page
the user cannot reach" refutation available. I also expanded each page's
schema with my own section-unwrapper keyed on
`isinstance(value, data_entry_flow.section)`, against `golden.py`'s duck-typing
on `.schema`; the two disagree on **0** pages.

The documented side is parsed from the live markdown, not transcribed: both
documents yield 13.

### The contents claim — the finder *understated* it

The dispatch flagged "several documented page contents on the wrong page" as
the vaguer, easier-to-overstate half. It is the opposite.

`v1_contents.py` resolves every first-column table label under each `###` page
section of configuration.md through the **shipped English translations**
(`options.step.<step>.data`, sections included) to a real field, and compares
that field's `_OPTION_FIELDS.step` against the section documenting it. Both
sides parsed; nothing hardcoded.

```
RESULT doc_page_sections=12 count
RESULT doc_rows_resolved=87 count
RESULT misplaced_rows=31 count
RESULT not_a_field_rows=0 count
RESULT unmatched_rows=10 count
```

**31** documented settings are on a page other than the one documenting them —
12 under *Hot water* (nine now on *Hot water tank and inlet*, two on
*Circulation pumps*, and "Heating circulation pump switch" on *Heating system
and heat storage*), 5 under *Sensors and entities* (all on *Power and solar
sensors*), 13 under *Self-learning and diagnostics* (four on *Heating system
and heat storage*, nine on *Advanced learning features*), and one under
*Thermal model (expert)*. The finder's own check hardcodes five learner keys
and finds four; walking every row finds 31. Its "several" is conservative.

The finder's specific sub-claims all hold against the document text I read
directly:

- configuration.md:200 states "There are **13 pages**: six on the first menu,
  and seven more behind **Advanced settings**"; its two tables carry 6 and 7
  rows. Real: 6 and 15, so **8 advanced pages have no row** — exactly the eight
  named.
- The first-menu table says *Grid costs*; `_P("grid", …)`'s label is
  **Grid peak tariff**.
- *Sensors and entities* is documented "22 fields in all" and renders **15**;
  *Comfort and temperatures* documented 7 + 3 = 10 and renders **18**;
  *Hot water* documented 11 + 12 = 23 and renders **10**.
- The Away page's table documents *Enable away mode* and *Expected return
  time* as settings. Neither resolves to any option field — I confirmed there
  is no `away_enabled` key among the 175 `_OPTION_FIELDS` rows, and that state
  lives on `switch.heat_pump_optimizer_away` and
  `datetime.heat_pump_optimizer_away_return`. The page has the four fields the
  finder names.

### Severity

Documentation-only; no runtime consequence. But this is the documentation
dimension, and the document misdescribes the integration's primary
configuration surface: 8 of 21 pages absent, 31 settings filed under the wrong
page, three per-page field counts wrong by 7, 8 and 13. **Medium is earned.**

---

## D6-02 — census claims outside README are unpinned and stale — **verify**, severity **low**

### My number, my method

`v1_census.py` counts entities twice, by two unrelated routes:

- **A**: my own driver calling each platform's real `async_setup_entry` and
  counting what it hands `async_add_entities` (the finder reused
  `tests/entities.py:collect`; I did not, so a bug in `collect` cannot
  propagate into both sides).
- **B**: the shipped `strings.json` `entity` inventory — translation keys, a
  wholly different artefact from constructed objects.

```
RESULT entities_constructed=74 count {'sensor': 59, 'binary_sensor': 5, 'button': 4, 'climate': 1, 'switch': 4, 'datetime': 1}
RESULT entities_from_strings=74 count {'sensor': 59, 'binary_sensor': 5, 'button': 4, 'switch': 4, 'datetime': 1}
RESULT methods_agree=True
RESULT documented[README.md]={'total': 74, 'sensor': 59, 'binary_sensor': 5, 'button': 4}
RESULT documented[docs/configuration.md]={'total': 65}
RESULT documented[docs/architecture.md]={'total': 65, 'sensor': 55, 'binary_sensor': 4, 'button': 4, 'switch': 1, 'climate': 1}
```

74 both ways. README correct on all four numbers it states; configuration.md's
65 wrong; architecture.md's node wrong.

### The asymmetry, executed rather than argued

`v1_asymmetry.sh` corrupts each document in turn and reports what
`tests/entities.py`'s four census checks say:

| arm | mutation | census checks |
|---|---|---|
| 0 | none | 4 × `ok` |
| A | README `All 74` → `All 65` | **FAIL** — "README says 65, the platforms construct 74" |
| B | configuration.md `All 65` → `All 999` | 4 × `ok` |
| C | architecture.md `65/55` → `999/888` | 4 × `ok` |
| D | README `### Sensors (59 total)` → `(55 total)` | **FAIL** — "README says 55, there are 59" |

Only README is pinned. The check reads one file — `readme =
Path("README.md").read_text()` at `tests/entities.py:456` — and the census
block names no other `.md`. Note that `docs/configuration.md:191` says "All
**65** entities appear at once": the same sentence shape the check's own
`All (\d+) entities` regex already matches. The regex would work verbatim on
the other file; only the filename differs.

### What widening would cost — measured, not guessed

- `docs/` is a blanket entry on `tests/closure.py`'s `INERT` list
  ("nothing in the gate reads it"), and `closure.py` fails a run where an
  INERT file is actually read, and separately refuses a file that is both
  INERT and inside a recorded closure (#357). So the two docs cannot simply be
  opened.
- **The carve-out mechanism already exists and is precedented**: `is_handover()`
  exempts `docs/HANDOVER*` from the `docs/` prefix, and `docs/HANDOVER.md` is
  in `tests/entities.py`'s 118-file closure today — the only `docs/` file in
  any closure. So widening does not require a new mechanism.
- Concretely: two more `R.check` blocks reusing the existing regexes against
  the two paths; an `INERT` carve-out for those paths; and a closure
  re-derivation — which `gate-scoping.md` requires be done on Linux, never a
  full `derive_closures.sh` off this box.
- **The standing cost** is the real one: every edit to `docs/configuration.md`
  or `docs/architecture.md` would then select `tests/entities.py` in the scoped
  gate (~19 s here), where today such an edit selects nothing at all. That is
  the trade — docs edits stop being free — and it is a judgement for the owner,
  not a defect.

### One correction to the finding as stated to the panel

`FINDINGS.md` says architecture.md is "wrong on **five of six** numbers". It is
wrong on **four of six**: 65→74, 55→59, 4→5 binary, 1→4 switch are wrong;
**4 buttons and 1 climate are right**. The finder's own harness says so
(`C-ARCH-04` and `C-ARCH-06` both `true`) and `REPORT.md`'s body states the
measured tuple correctly. Five is the count of false census claims across
*both* documents (1 in configuration.md + 4 in architecture.md). The summary
line conflates the two. The finding's substance is unaffected.

### Severity

Low stands. The wrong numbers sit in a prose aside and a mermaid node; nothing
reads them at runtime.

---

## D6-03 — configuration.md under-declares three services — **weaken** to **low**

### The counts verify, from a different source

The finder counted `len(services.yaml[svc]["fields"])`. `v1_services.py` takes
the **registered voluptuous schemas** instead — the object `async_register` is
handed — and parses the documented side out of the services table and each
service's own prose paragraph.

```
RESULT services_in_yaml=12 count   RESULT services_with_schema=12 count
RESULT apply_topology:   schema=5  yaml=5  doc_says=3   <-- MISMATCH   undocumented: ['dhw', 'wood']
RESULT assign_entity:    schema=4  yaml=4  doc_says=3   <-- MISMATCH   undocumented: ['manual_setpoint']
RESULT simulate_plan:    schema=16 yaml=16 doc_says=11  <-- MISMATCH   undocumented: ['wood_furnace_efficiency', 'wood_packing', 'wood_price_sek_m3', 'wood_slots', 'wood_type']
```

16 / 4 / 5 against 11 / 3 / 3, the finder's numbers. The other nine services
match, and schema and YAML agree on all 69 fields — zero divergence, so the
finder's YAML-based count was not materially different here.

### But the claim that carries the severity is false

The finding says the eight fields are "documented nowhere", and REPORT.md calls
the wood what-if "a documented-nowhere capability of a documented service".
Home Assistant does not render `docs/configuration.md`; it renders the
`services` block of `strings.json` / `translations/*.json` in
**Developer Tools → Actions**, which is where a user meets a service field.

```
RESULT service_fields_total=69 count
RESULT undocumented_in_strings.json=0 count []
RESULT undocumented_in_en.json=0 count []
RESULT undocumented_in_sv.json=0 count []
```

**Every one of the 69 service fields — all eight included — carries a `name`
and a prose `description` in all three files, in English and Swedish.**
For example `simulate_plan.wood_slots`: *"What-if wood fires as a list of
objects each carrying a start, an end and a volume in liters. Injected only
into the shadow solve; never written to the config entry."* And
`assign_entity.manual_setpoint`, and `apply_topology.dhw` and `.wood`.

The finder had these files open — its non-findings check every `strings.json`
**entity** leaf against both translations — and did not check the **services**
block, which is the one that refutes its own strongest sentence.

### What survives

`docs/configuration.md`'s service reference is incomplete: three counts wrong,
and its enumerated field lists read as exhaustive while omitting eight fields.
Worth fixing. But no capability is hidden from users, and the eight fields are
documented in the surface HA actually shows, in both shipped languages. The
severity rested on concealment that does not exist.

**Weaken to `low`.**

---

## D6-04 — README's removal list omits two `.storage` files — **verify**, severity **low**

### Double-counting, conditionality, and a static bound

`v1_store.py` spies `Store.__init__` under two arms and reports raw
constructions beside distinct keys, because `away._away_store` and
`boost._store` build a fresh `Store` on every call:

```
RESULT [setup] raw_constructions=13   constructed=12
RESULT [used]  raw_constructions=15   constructed=12
```

No double-counting: 13 and 15 constructions collapse to the same 12 distinct
keys, and the finder's probe de-duplicates, so its 12 is right.

Not configuration-dependent either. All 12 appear in the **bare** arm — a
coordinator built on an empty entry — and a static sweep finds exactly **12
`Store(` construction sites in the entire integration**, in four files
(`coordinator.py` ×8, `dhw_learning.py` ×2, `away.py`, `boost.py`). There is
no thirteenth site any configuration could reach.

### Do the two extra ones actually persist anything?

This is the attack that mattered, and it needed executing: constructing a
`Store` creates no file, so a key that is only ever loaded from would not leave
anything behind to delete. Three independent counters agree — my
`async_save` spy, the stub's own `SAVE_COUNTS`, and its `_DISK`:

```
RESULT [setup] persisted=1 ['away']          persisted_by_stub_counter=1   on_disk=1
RESULT [used]  persisted=2 ['away','boost']  persisted_by_stub_counter=2   on_disk=2
    payload away:  {'active': True, 'return_time': '2026-09-20T18:00:00+02:00', 'migrated_helpers': True}
    payload boost: {'space': {'until': '2026-09-11T12:52:01.749816'}}
```

Both hold real user state. And the **setup** arm is the striking one: the away
store is written on first startup with no user action at all —
`restore_override` → `_migrate_helpers` → `persist_override`. So of the twelve,
the file most certain to exist for every single install is one of the two the
README omits.

> **A phantom zero I had to catch in my own harness.** My first spy read
> `self.key`; the stub names it `_key`, and both `away.persist_override` and
> `boost.persist` swallow every `Exception` at debug level. It printed
> `persisted=0` for both arms — the spy failing, reported as the code not
> saving. Fixed, cross-checked against two counters I did not write, and the
> spy-error count is now printed beside the number.

`listed_but_never_persisted=10` in my output is an artefact of my arms' scope,
not evidence about the ten documented stores: my arms drive setup plus the two
features, and the learners write later during real operation. It is not
evidence for or against the finding.

### Severity

Low stands, and low is right rather than generous-in-either-direction: the
README itself says "a re-added entry gets a new id and never reads them", so
the leftovers are inert. The consequence is two stray files after a clean
slate, not misbehaviour.

---

## Attack 5 — the `unverifiable` verdicts

`v1_versions.py`. Two questions, both answered by execution.

**Is any of the six settleable from `VERSION`, `manifest.json` and `hacs.json`
alone?** No — `0 of 6`. All six are historical ("since vX", "until vX",
"before vX", "by #174"), and `VERSION=6.3.20` fixes only the present.

**Does any carry a present-tense half this export can settle?** Three do, and
all three execute `true`:

| claim | present-tense half | executed |
|---|---|---|
| C-VER-01 | entity names are translated | 73/73 entity leaves present in both en and sv |
| C-VER-02 | ECL110 settings live only on Heat curve control | all 8 `ecl110_*` option fields on step `heat_curve` |
| C-VER-05 | ECL110 MQTT fields no longer asked in setup | 13 setup-flow steps driven; **0** present an `ecl110_*` field |

So the finder's verdicts are not wrong, but three are under-reported: it folded
each claim in whole rather than splitting the tense, and the present halves
were checkable here.

**A correction against my own first pass.** I initially scored C-VER-03
("existing installs keep their entity id") checkable and probed it by grepping
`sensor.py` for the old slug. That probe answers nothing. The claim is about
the registry of an install predating the rename; it holds if the unique id did
not move, and this export carries only the current suffix (`dhw_cost_total`)
with no way to execute what the pre-rename one was. The only evidence here is a
source comment asserting the unique id did not move — itself a documentation
claim, not a check. **The finder's `unverifiable` is right and my first attempt
was the over-reach.** C-VER-04 and C-VER-06 are likewise correctly unverifiable.

**Does any `true` verdict rest on a file the export lacks?** No. The four
absent files (`RELEASE_NOTES.md`, `docs/backlog.md`, `docs/audit-2026-08.md`,
`docs/audit-2026-09.md`) are referenced by exactly one claim, `C-VER-06`,
correctly marked `unverifiable`. The link check excludes those four from its
broken count and says so in its own result string, so its "0 broken" is
disclosed as conditional rather than quietly conditional.

---

## Votes

| finding | vote | severity |
|---|---|---|
| D6-01 | **verify** | medium (as filed) |
| D6-02 | **verify** | low (as filed); one stated count corrected 5→4 |
| D6-03 | **weaken** | **low** (from medium) — counts hold, "documented nowhere" is false |
| D6-04 | **verify** | low (as filed) |
