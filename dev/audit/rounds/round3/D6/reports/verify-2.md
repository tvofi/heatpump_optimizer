# D6 — verifier 2 of 3, refute-first

Baseline `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1`. Box: 8-core Apple M1, 8 GB,
python 3.11.5 (numpy 2.4.6 / scipy 1.17.1). `thread_factor=1.0` on every run;
`load1` ranged **5.16–9.46** across my runs against the finder's **70.05**.

**No number in this report is a timing number.** Every figure is a count of
exact comparisons — menu entries, schema keys, entity objects, store keys,
verdict-set diffs. The 14x load difference is the control for that claim and it
is reported below, not asserted.

My instruments are under `tools/audit/round3/D6/verify-2/`: `pages_census.py`,
`pages_perturb.py`, `census.py`, `services_runtime.py`,
`services_nullcontrol.py`, `storage_writes.py`, with their `.log` files. Each
resolves the repository as `Path(".")`. Every file I mutated was restored from
a byte copy and verified with `cmp` before the next arm; the production tree
outside `verify-2/` is byte-identical to the export (`claims.csv`/`claims.md`
were rewritten by the finder's own harness, byte-identically — md5 compared).

**Because counts are where this project's agents have most often disagreed,
every number below carries the counting rule that produces it, and the two
findings where a rule could plausibly differ (D6-01 pages, D6-02 entities) are
each counted by two independent rules that are required to agree.**

---

## 0. Reproduction of the finder's harnesses

Run exactly as their headers state, from the repository root.

| harness | finder | mine | load1 (finder → mine) |
|---|---|---|---|
| `store_probe.py` | 12 / 10 / 2 | **12 / 10 / 2** | 70.29 → 5.26 |
| `claims.py` | all 12 RESULT counts | **all 12 identical** | 70.05 → 6.81 |

`claims.py` wall time 16.9 s against the finder's 112.9 s, and the regenerated
`claims.csv` is **byte-identical** to the committed one; the 24 `FALSE` and 6
`UNVERIFIABLE` verdict lines diff clean. A 14x load difference moving no digit
is the evidence that these counts are contention-immune, which is what the
headers claim.

---

## D6-01 — options-page inventory (13 documented, 21 rendered) — **verify**, **medium**

### My metric definition, which is not the finder's

> An **options page** is a distinct step id that the options flow *offers the
> user* as a `menu_options` entry of `async_step_init` or `async_step_advanced`
> — the two menus a user actually sees — excluding the synthetic `advanced`
> entry, which opens a menu and not a form; **and** whose handler, driven with
> `user_input=None`, returns `type == "form"`. Editable = the form presents at
> least one field other than `after_save`.

The finder's `options_pages_rendered` is `len(config_flow._OPTION_PAGES)` — a
static table read (`claims.py:1033`). Its prose says "21 pages that render a
form", which is stronger than what that RESULT measures. Mine walks the two
rendered menus and follows each entry to its handler, so a table row wired into
neither menu, or one that answered with anything but a form, would make my
number *smaller* than the finder's. It does not.

```
RESULT menu_pages_total=21 count      RESULT menu_pages_top=6 count
RESULT menu_pages_advanced=15 count   RESULT menu_pages_editable=20 count
RESULT menu_pages_readonly=1 count    RESULT unreachable=0 count []
RESULT readme_undocumented_advanced=8 count
RESULT conf_undocumented_advanced=8 count
```

21 / 6 / 15, 20 editable + 1 read-only, and **every** declared row reachable.
The documented side is parsed out of the live markdown tables (first column of
the table under `Page` / `Advanced page` / `First menu` / `Advanced settings`),
not transcribed: 6 + 7 = 13 rows in each document. The 8 advanced pages with no
row in either: *Advanced learning features, Circulation pumps, Fuse and peak
guards, Heat pump telemetry, Hot water tank and inlet, Power and solar sensors,
Transfer fees and contract, Two-zone model*. Exactly the eight named.

### Attack — "what counts as a page?"

**(a) Does a conditionally-rendered page count when its condition is false?**
There is no such page. The two menus are an unfiltered query over
`_OPTION_PAGES`'s `menu` column (`config_flow.py:2273-2277`), with no
predicate anywhere. `config_flow.py` contains 14 `when=` occurrences and all 13
field rows are on the **`building`** page's `wood` group. Executed:

```
A0 default entry:   total=21 top=6 advanced=15
A1 wood furnace on: total=21 top=6 advanced=15
A1 per-page field counts that moved: {'building': (9, 22)}
RESULT page_count_condition_sensitive=0 count
```

Condition state moves exactly one *field* count and no *page* count — and
`building` is not one of the pages whose field count the finding cites, so no
cited number is a fixture artefact.

**(b) Does a page count if it is reachable only from the options flow?** All 21
are options-flow pages, and both documents place the claim under "Changing
settings later" / "Changing settings after setup" → **Configure**. The
population is the right one by the documents' own framing.

**(c) Is there any counting rule that yields 13?** I enumerated them:

| rule | value |
|---|---|
| pages offered by both menus | 21 |
| ... editable only | 20 |
| ... read-only only | 1 |
| clickable rows on the first menu (incl. *Advanced settings*) | 7 |
| pages + the submenu opener | 22 |
| first menu only / advanced only | 6 / 15 |
| **documented** | **13 (6 + 7)** |

`RESULT rules_yielding_13=0 count`. 13 is the row count of the documents' own
two tables, not a different rule applied to the same tree.

**(d) Null control.** Dropping one `_P(...)` row and re-walking:
`RESULT null_control_delta=-1 count`. The metric moves under its own
perturbation.

### Is anything in the gate watching?

`_OPTION_PAGES` is read by `tests/entities.py:10044` and `tests/nightly_ha.py`
— and both **derive** their expectation from `_OPTION_PAGES` itself (step ids
vs `strings.json`, menus vs the flat roster). Nothing anywhere compares it to
`README.md` or `docs/configuration.md`. The one-line production mutation the
suite would not notice as a *documentation* defect: add an `_P(...)` row to
`custom_components/heatpump_optimizer/config_flow.py` — the page count claim in
both documents is unchecked in either direction.

### Severity — earned by consequence

Not "a wrong expectation". `docs/configuration.md` is the document README sends
a user to for "every field, default and range", and measured against it:

```
RESULT option_fields_total=167 count
RESULT option_fields_on_undocumented_pages=64 count   (38.3%)
```

64 of 167 option fields sit on the 9 pages with no row in either document (56
fields on the 8 pages absent outright; 8 more on *Grid peak tariff*, whose
content is documented under the wrong name *Grid costs*). And the misdirection
is positive, not merely absent — independently confirmed from my rendered field
lists:

- `space_circulation_pump_entity` is on **building** (*Heating system and heat
  storage*); both documents put "Heating circulation pump switch" on *Hot water*.
- the away page's four fields are `away_presence_entity`,
  `holiday_calendar_entity`, `away_temperature`, `away_dhw_min_temperature` —
  neither "Enable away mode" nor "Expected return time" is among them.
- *Comfort and temperatures* renders **18** (documented 7 + 3 = 10);
  *Hot water* renders **10** (documented 11 + 12 = 23); *Sensors and entities*
  renders **15** (documented 22).

A user who cannot find a setting where the reference says it is costs more than
a wrong number. **Medium is earned.**

---

## D6-02 — census claims outside README are unpinned and stale — **verify**, **low**, restated

### My metric definition, counted twice by unrelated rules

> **Rule A (by platform module):** for each `Platform` in
> `heatpump_optimizer.PLATFORM_LIST`, import `heatpump_optimizer.<platform>`,
> run its real `async_setup_entry` with my own collector, count what it hands
> `async_add_entities`.
> **Rule B (by HA entity class):** classify every object rule A collected by
> which Home Assistant base class it inherits (`SensorEntity`,
> `BinarySensorEntity`, `ButtonEntity`, `SwitchEntity`, `ClimateEntity`,
> `DateTimeEntity`), ignoring which module produced it.

Rule A is "what the platform files register"; rule B is "what kind of thing the
user ends up with". Three agents have produced three numbers for this census
before, so both rules are printed and their agreement is a RESULT. **I did not
call `tests/entities.py:collect`** — the collector is mine, so a defect in
`collect` cannot enter both sides of the comparison.

```
RESULT entities_total=74 count   RESULT rules_A_B_agree=1 count
RESULT sensor=59  binary_sensor=5  button=4  switch=4  climate=1  datetime=1
```

74 = 59 + 5 + 4 + 4 + 1 + 1, both rules, zero disagreement. The census is also
payload-invariant: my coordinator published an **empty** data dict where the
finder used a full one, and the number is the same.

Documented: README 74 / 59 / 5 / 4 — **all four right**. `docs/configuration.md`
"All **65** entities" — wrong. `docs/architecture.md` 65 / 55 / 4 binary / 4
buttons / 1 switch / 1 climate — wrong on **four of six** (65, 55, 4 binary,
1 switch); 4 buttons and 1 climate are right, and the `datetime` platform is
absent from the diagram entirely. `RESULT census_sentences_wrong=5 count` across
the two files (1 + 4). The dispatch's summary of this finding as "65/55/4/1 vs
74/59/5/4" names exactly the four wrong ones.

### "Unpinned" is the load-bearing word — executed, and it holds

Four measurements, in increasing strength.

1. **No gate script opens either file.** `RESULT readme_read_by_gate=1`,
   `configuration_md_read_by_gate=0`, `architecture_md_read_by_gate=0`. Across
   `tests/*.py` and `.github/workflows/*.yml` the only `docs/` file read is
   `docs/HANDOVER.md`.
2. **`docs/` is blanket-`INERT`** in `tests/closure.py:170`, so a docs-only
   diff selects *zero* gate scripts under `GATE_SCOPE=auto`. The same list's
   comment records that `README.md` was **taken off** it because
   "tests/entities.py reads both … They are dependencies." The asymmetry is
   deliberate and written down.
3. **Doc-side mutation, two arms** (restored, `cmp`-verified):
   - README `All 74 entities` → `All 73`: **FAIL** *"README says 73, the
     platforms construct 74"*.
   - `architecture.md` `65 entities` → `999` **and** `configuration.md`
     `All 65` → `All 999`: **4 × ok**. Zero gate scripts even open the files.
4. **Production-side mutation** — the one the contract asks for. Deleting the
   single line `WoodCheaperBinarySensor(coordinator, entry),` from
   `custom_components/heatpump_optimizer/binary_sensor.py`:
   - README pins: **3 FAIL** (binary count, binary table rows, total).
   - `architecture.md`'s "4 binary sensors" **becomes correct**.

   That fourth arm is the sharpest statement available about the finding: an
   unpinned number is not merely stale, it is *uninformative* — architecture.md
   agreed with a deliberately broken tree, and its two currently-correct numbers
   (4 buttons, 1 climate) are right by coincidence, held by no mechanism.

### Restatement

The dispatch asked whether this should be restated as the absence of a pin
rather than as numbers. Both halves executed true, so I would state it as
**cause and symptom, not one or the other**: the numbers are stale
(5 sentences), and they are stale *because* README's census is derived and
pinned at `tests/entities.py:456-527` while the identical sentence in
`docs/configuration.md:191` — matching the pin's own `All (\d+) entities` regex
verbatim, differing only in filename — is read by nothing and lives under a
prefix the scoped gate declares inert. Fixing only the numbers leaves the
mechanism that produced them untouched.

### Severity

**Low.** The consequence is a wrong expectation in a prose aside and a mermaid
node: a user expects 65 entities and gets 74. Nothing reads either number at
runtime.

---

## D6-03 — configuration.md under-declares three services — **weaken to low**

### My metric definition — the schema registered at runtime, not `services.yaml`

> For each service, the top-level keys of the voluptuous schema that
> `hass.services.async_register` **actually received** during the integration's
> own `async_setup_entry` — captured by spying on the registration — with
> `vol.All` wrappers unwrapped. Required and optional keys count alike;
> `entry_id` counts, being a field a caller may pass.

The dispatch asked me to confirm against the runtime schema because it *can*
differ from `services.yaml`, and which one the user meets changes severity.
Executed through `harness.ha_setup_entry`, the full entry setup:

```
RESULT services_registered=12 count
RESULT simulate_plan_runtime_fields=16 count
RESULT assign_entity_runtime_fields=4 count
RESULT apply_topology_runtime_fields=5 count
RESULT set_thermal_parameters_runtime_fields=28 count
RESULT apply_schedule_runtime_fields=6 count
RESULT runtime_vs_yaml_services_differing=0 count
RESULT doc_field_counts_wrong=3 count
RESULT undocumented_fields_total=8 count
```

**They do not differ.** For all twelve services the symmetric difference between
the runtime schema's keys and `services.yaml`'s `fields:` keys is empty, so the
finder's YAML-derived count was safe. 16 / 4 / 5 against the documented
11 / 3 / 3, and the eight fields `docs/configuration.md` omits are
`wood_slots`, `wood_type`, `wood_packing`, `wood_price_sek_m3`,
`wood_furnace_efficiency` (`simulate_plan`), `manual_setpoint`
(`assign_entity`), `dhw` and `wood` (`apply_topology`). All confirmed present
in `services.py`'s schema constants by reading them.

**Null control:** removing `wood_type` from `SERVICE_SCHEMA_SIMULATE_PLAN`
before registration drops the runtime count 16 → 15
(`RESULT null_control_delta=-1 count`), so the harness reads what it claims to.

### Why I weaken it

The finding's severity rests on REPORT.md's sentence that the wood what-if is
"a documented-nowhere capability of a documented service". That is false, and
one executed number refutes it:

```
RESULT service_fields_without_ui_label=0 count
```

Every field in `services.yaml` — all eight of these included — has a `name` and
a prose `description` in `strings.json`, which is what Home Assistant renders in
**Developer Tools → Actions**, the surface where a user actually meets a service
field. e.g. `simulate_plan.wood_type` → *"Wood type / What-if wood type override
(birch, pine, mixed)."*; `assign_entity.manual_setpoint` and
`apply_topology.dhw`/`.wood` likewise.

So no capability is concealed. What survives is real and worth fixing:
`docs/configuration.md`'s service reference states three counts wrong and its
enumerated field lists read as exhaustive while omitting eight fields. That is
**the same class of consequence as D6-02** — a doc reader forms a wrong
expectation, while the product itself is self-describing and correct.
**Low, not medium.**

---

## D6-04 — README's removal list omits two `.storage` files — **verify**, **low**, and the repair is gate-blocked

### My metric definition — stricter than the finder's

> A `.storage` file a user must delete is one whose `Store` both **(a)** is
> constructed by production code for one config entry **and (b)** has
> `async_save` called on it with a payload — because `Store.async_save` is what
> creates the file. A `Store` only constructed and loaded leaves no residue and
> would be a smaller finding.

This is precisely the dispatch's attack, so I measured (b) rather than assuming
it. `Store.__init__`, `async_save` and `async_load` instrumented; two arms,
production paths only.

```
arm A — install (coordinator __init__ + boost.restore_session, the coroutine
        async_setup spawns at coordinator.py:1357). No user action.
arm B — arm A, then boost.set_channel per channel and away.persist_override.

RESULT stores_constructed=12 count
RESULT stores_written_on_install=1 count          ['away']
RESULT stores_written_after_user_action=2 count   ['away', 'boost']
RESULT readme_listed=10 count
RESULT undocumented_constructed=2 count  ['away', 'boost']
RESULT undocumented_written=2 count      ['away', 'boost']
RESULT has_async_remove_entry=0 count
```

Payloads, real user state, not empty markers:

- install-only `away`: `{'active': False, 'return_time': None, 'migrated_helpers': True}`
- after action `away`: `{'active': True, 'return_time': None, 'migrated_helpers': True}`
- after action `boost`: `{'dhw': {'until': '…'}, 'space': {'until': '…'}}`

**The away store is written on first startup of every install, with no user
action at all**: `restore_override` finds no stored payload →
`migrated_helpers` False → `_migrate_helpers` → `persist_override`
(`away.py:371-374`). So of the twelve, the file most certain to exist on every
install is one of the two the README omits. `_migrate_helpers` reads
`coord._entity_state(...)` and `coord.entry.options` only — plain reads, no
stub-specific behaviour — so the path is reachable in real Home Assistant, not
only through `FakeHass`.

The integration defines **no `async_remove_entry`**, so Home Assistant deletes
none of these with the entry — which is what the README itself says, and it is
true. The manual list is the only cleanup path there is.

### The part the finding does not state, and it is the expensive half

`tests/entities.py:763-817` exists to pin exactly this list —
*"the store files it says are left under .storage are exactly the ones the
coordinator keeps"* — and it is **green on a wrong README**. Its population is

```python
_store_holders = (_removal_coord, _removal_coord._dhw_learner)
_store_suffixes = {... for holder in _store_holders
                   for value in vars(holder).values() if isinstance(value, _Store) ...}
```

`vars()` over two objects. `away._away_store(coord)` and `boost._store(coord)`
build their `Store` inside a function and never bind it to an attribute, so
they are **structurally invisible** to that population:

```
the check's population: 10 ['accuracy','dhw_draws','dhw_legionella','dhw_profile',
 'energy','ledger','manual_plan','price_model','snapshots','thermal_learning']
away/boost visible to vars()?  False False
```

Executed consequence — I applied the **fix** (added the two names to the README
and changed "ten" to "twelve") and ran the gate:

```
FAIL the store files it says are left under .storage are exactly the ones the
     coordinator keeps  [documented [... 12 names ...], code keeps [... 10 ...]]
```

**Correcting the README turns the check red.** The check does not merely miss
the omission; it enforces it. This is the shape `CLAUDE.md` names — a check that
supplies the value it asserts and converts an open defect into a closed one —
and it means any fix for D6-04 must land with a change to
`tests/entities.py`'s census population (walk `Store` constructions, as
`store_probe.py` does, rather than `vars()`), or it cannot merge.

### Severity

**Low, by consequence to the user**, and I would not raise it on that axis: two
stray files after a "clean slate", and the README correctly says a re-added
entry gets a new id and never reads them, so the residue is inert. But the
finding as filed under-states its *cost*: the obvious one-line doc fix is
blocked by a green gate check, so this is a two-file change with a test-side
defect attached, not a typo. The judge should know that before sizing it.

---

## Where my numbers came from, one line each

| finding | my number | rule |
|---|---|---|
| D6-01 | 21 / 6 / 15 / 20 editable | menu entries the flow renders, followed to a `type == "form"` handler |
| D6-02 | 74 = 59+5+4+4+1+1 | objects handed to `async_add_entities`, by platform module **and** by HA base class, required to agree |
| D6-03 | 16 / 4 / 5 | top-level keys of the schema `async_register` received at runtime |
| D6-04 | 12 constructed, 2 written, 10 listed | `Store` keys constructed *and* `async_save`-d for one entry |

## exposure

Audit-era documents opened: `tools/audit/round3/D6/{FINDINGS,REPORT}.md`,
`claims.py`, `store_probe.py` and their logs — the material under verification.
`tools/audit/briefs/{verifier,D6}.md`. Seat 1's report was read **only after**
every number above was recorded, per the contract. Not opened: `COMMON.md`,
the round-2 evidence, `docs/plan-*.md`, `docs/HANDOVER.md`, `docs/audit-*.md`.
Read for measurement: `README.md`, `docs/configuration.md`,
`docs/architecture.md`, `config_flow.py`, `services.py`, `services.yaml`,
`strings.json`, `away.py`, `boost.py`, `coordinator.py` (setup spawn only),
`binary_sensor.py`, `tests/entities.py`, `tests/closure.py`, `tests/harness.py`,
`tests/closures.json`. No `gh` was run and no GitHub page was read.

## Votes

| finding | vote | severity | my executed number |
|---|---|---|---|
| D6-01 | **verify** | medium (as filed) | 21 pages / 6 top / 15 advanced / 8 undocumented |
| D6-02 | **verify** | low (as filed) | 74 entities, both rules; 5 wrong sentences; 0 gate scripts read either file |
| D6-03 | **weaken** | **low** (from medium) | 16 / 4 / 5 runtime fields; 0 fields lacking a UI label |
| D6-04 | **verify** | low (as filed) | 12 constructed, 2 written and undocumented, 0 `async_remove_entry` |
