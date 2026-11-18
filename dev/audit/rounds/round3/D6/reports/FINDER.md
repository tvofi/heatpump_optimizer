# D6 — README and documentation claim verification (round 3)

Baseline `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1`. Tree: a `git archive`
export with no `.git`, and with `docs/audit-*.md`, `docs/backlog.md` and
`RELEASE_NOTES.md` removed by the round-3 dispatch.

Box: 8-core Apple M1, 8 GB, python 3.11.5 (numpy 2.4.6 / scipy 1.17.1),
node v20.10.0. `load1` at the measuring run was **70.05** — irrelevant here,
because **every number in this report is a count of exact comparisons**
(entity counts, page counts, field counts, store-key counts, string equality
against `const.py`). No wall, CPU or RSS number carries any claim in this
dimension, so nothing here is provisional.

## Numbers

| | |
|---|---|
| claims extracted and numbered | **150** |
| claims checked (executed) | **144** |
| claims `true` | **120** |
| claims `false` | **24** |
| claims `stale` | **0** |
| claims `unverifiable` (in this export) | **6** |

The claims table is the harness output: `tools/audit/round3/D6/claims.csv`
(and the same rendered as `claims.md`) — id, source, claim, check command,
result, verdict, and the true statement for every false claim. The run log is
`claims-run.log`.

## Method

Sources read and mined for claims: `README.md` (868 lines), `docs/configuration.md`,
`docs/how-it-works.md`, `docs/architecture.md`, `docs/dashboard-card.md`,
`docs/ecl110.md`, `docs/automations.md`, `DISCLAIMER.md`,
`custom_components/heatpump_optimizer/services.yaml`, `strings.json`,
`translations/en.json`, `translations/sv.json`, `manifest.json`, `hacs.json`,
`VERSION`. The `docs/plan-*.md` programme records and `docs/HANDOVER.md` were
not mined — they are development records, not published claims.

Every claim carries **one executed check**, by family:

* **Entity names and counts** — `tests/entities.py:collect` over
  `heatpump_optimizer.PLATFORM_LIST`, driving the real `async_setup_entry`.
  `tests/entities.py` runs its checks at import and then terminates, so the
  harness `exec`s it into a namespace and catches the termination; `collect`
  and `display_name` are the suite's own, not re-implementations.
* **Defaults** — attribute reads on `heatpump_optimizer.const` and on
  `snapshots`, `curve_learning`, `freq_control`, `boost`, `dhw_draws`,
  `grid_fee`, compared value-for-value against the documented default.
* **Options pages and fields** — every `config_flow._OPTION_PAGES` row driven
  through its real `async_step_<step>` handler, and the presented schema's
  fields counted (`after_save`, the navigation control, excluded).
* **Service fields** — `services.yaml` parsed, and every `example:` payload in
  it fed through the service's own registered voluptuous schema
  (`services.SERVICE_SCHEMA_*`); documented field lists and physics ranges
  compared against those schemas' keys and `vol.Range` bounds.
* **Storage files** — `homeassistant.helpers.storage.Store.__init__`
  instrumented, driven through `HeatPumpOptimizerCoordinator.__init__` and
  `boost.restore_session` (the coroutine the coordinator spawns from
  `async_setup`, coordinator.py:1357).
* **Links** — every relative markdown target resolved on disk. External links
  were *not* HEAD-requested: this seat has no outbound network and the dispatch
  forbids reaching GitHub, so external-link liveness is out of scope here and
  is recorded as such rather than guessed.
* **Versions** — `VERSION` against `manifest.json`, and the README badge
  against `hacs.json`. Claims of the form "since vX.Y.Z…" cannot be settled
  against this export and are recorded `unverifiable`, not guessed.

**Root rule of both harnesses: `ROOT = Path(".")` — the current working
directory, never `__file__`.** Run them from the tree you want measured. This
is stated in each header, because `tools/audit/README.md` records that harnesses
resolving from `__file__` have silently measured the wrong checkout three times.

## Findings

### D6-01 — the options-page inventory in README.md and docs/configuration.md describes a superseded flow (13 pages claimed, 21 rendered)

`docs/configuration.md:196` states "There are **13 pages**: six on the first
menu, and seven more behind **Advanced settings**", and `README.md` states "a
menu of 13 pages — 12 you can edit plus a read-only overview". Driving every
`config_flow._OPTION_PAGES` row through its own `async_step_*` handler returns
**21 pages that render a form**: 6 on the top menu and **15** behind Advanced
settings, 20 of them with editable fields. Eight advanced pages have no row in
either document's table: *Power and solar sensors*, *Heat pump telemetry*,
*Two-zone model*, *Hot water tank and inlet*, *Circulation pumps*, *Advanced
learning features*, *Fuse and peak guards*, *Transfer fees and contract*.

The same drift shows in the per-page prose, which still describes the merged
pages that were split: the *Sensors and entities* page is documented as "22
fields in all" and carries **15**; *Comfort and temperatures* is documented as
7 + 3 = 10 and carries **18**; the *Hot water* page is documented as 11 + 12 = 23
and carries **10**; *Grid costs* is the page's documented name and its real
label is **Grid peak tariff**; the "Heating circulation pump switch" documented
under *Hot water* is on **Heating system and heat storage**; and four of the
learners documented on *Self-learning and diagnostics* are on *Advanced learning
features* or *Heating system and heat storage*. Two settings documented on
*Away and holiday mode* — "Enable away mode" and "Expected return time" — are
not fields on that page at all (it has four: `away_presence_entity`,
`holiday_calendar_entity`, `away_temperature`, `away_dhw_min_temperature`);
that state lives on the Away switch and the Away Return datetime entity.

13 of the 24 false claims belong to this one mechanism. Nothing in the gate
compares `_OPTION_PAGES` with either document.

### D6-02 — entity-count claims outside README.md are pinned by nothing and are stale

`tests/entities.py` derives the README's entity census from `collect()` and
pins it (`the README's sensors count is right`, `…total entity count covers
every registered platform`), and those README numbers are **correct**: 74 total,
59 sensors, 5 binary sensors, 4 buttons. The identical claims elsewhere are
checked by nothing and are stale:
`docs/configuration.md:191` "All **65** entities appear at once", and
`docs/architecture.md:35` "**65** entities / **55** sensors / **4** binary
sensors / 4 buttons / **1** switch / 1 climate". Measured: 74 / 59 / 5 / 4 /
**4** switches / 1 climate (+ 1 datetime, which the architecture diagram omits
entirely).

### D6-03 — docs/configuration.md's service-field inventory under-declares three services

The gate derives the README's *services table* from `services.yaml`'s keys, but
nothing checks the per-service **field** lists in the configuration reference.
Measured against `services.yaml` and the registered voluptuous schemas:

| service | documented | declared | undocumented fields |
|---|---|---|---|
| `simulate_plan` | "11 optional comfort fields", listed | **16** | `wood_slots`, `wood_type`, `wood_packing`, `wood_price_sek_m3`, `wood_furnace_efficiency` |
| `assign_entity` | `key`, `entity_id`, `entry_id` | **4** | `manual_setpoint` |
| `apply_topology` | `layout`, `positions`, `entry_id` | **5** | `dhw`, `wood` |

`SERVICE_SCHEMA_SIMULATE_PLAN` accepts all five wood fields, so the card's
wood-burn what-if is a documented-nowhere capability of a documented service.
The other nine services' field counts are correct, and all 28
`set_thermal_parameters` fields and 25 of its documented physics ranges match
the schema exactly.

### D6-04 — README's removal instructions list ten `.storage` files; the integration creates twelve

README's Removal section says "Every entry keeps its learners and ledgers in
**ten** files under `.storage/`" and names ten. Instrumenting
`homeassistant.helpers.storage.Store.__init__` and driving the real coordinator
constructor plus `boost.restore_session` records **12** distinct store keys.
The two the list omits are `heatpump_optimizer_<entry id>_away` (the away
override) and `heatpump_optimizer_<entry id>_boost` (the boost session). A user
following the "clean slate" instruction leaves both behind.

## Non-findings — what was checked and held

Each with the executed number. Full detail per claim in `claims.csv`.

* **README entity census** — 74 total / 59 sensors / 5 binary sensors /
  4 buttons, and the six disabled-by-default sensors are exactly the six named
  (`collect()` + `_attr_entity_registry_enabled_default`).
* **12 services registered**, matching `services.yaml`'s 12 keys; the seven
  services accepting `entry_id` are exactly seven.
* **Every `example:` in `services.yaml` validates against its own registered
  schema** — 9 example payloads fed through `SERVICE_SCHEMA_*`, 0 rejected.
* **`set_thermal_parameters`: 28 fields**, and all 25 documented physics ranges
  equal the schema's `vol.Range` bounds (`0.01–200`, `1.0–8.0`, `30–75`,
  `55–75`, `−30–0`, `0–30`, …).
* **`assign_entity`: 21 assignable keys**, and the documented list is exactly
  `topology.ASSIGNABLE_KEYS`.
* **Hydronic catalog**: 5 layouts, 4 selectable, matching the catalog table.
* **~60 documented defaults equal `const.py`** — target 21.0, min 19.0,
  max 23.0, day 21.0 / night 19.5, day 07–22, DHW windows
  `06:00-08:30, 17:00-22:00`, DHW 200 L / 55 °C / 45 °C / 150 L/day / 0.3 °C/h /
  idle 20 °C, legionella on / 60 °C / 7 d / floor 5 d, wind 0.03, rain 1.15,
  interval 30 min, comfort weight 5.0, area 140 m², COP 3.5, 5.0/1.0 kW,
  masses 10/5/3/8, losses 0.15/0.08/0.07, inter-zone 0.5, radiator share 0.4,
  buffer 35 L / 70 °C, window 10 m², orientation 0.7, SHGC 0.7, fRsi 0.75,
  inlet 10 °C, shower 8 L/min, VVC lead 20 min, capacity 45/kW & 3 peaks,
  fuse 0 A / 3 phases, peak-guard margin 0.5 kW, away 16 °C / 20 °C, valve 0 °C,
  wood tank 500 L, PV efficiency 0.80, staleness scale 1.0, external heat
  1.5 °C/h / 90 min, rated starts 100 000, and all seven ECL110 defaults.
* **Learner bounds** — curve learning at most 0.5 K/week and cool-only
  (`BIAS_MAX = 0.0`); snapshots weekly with a ring of 8; COP scale bounded
  `[0.5, 1.6]`; DHW cooling rate clamped `0.05–3.0 °C/h`; solar aperture
  `0.3×–2×`; capacity floor 60 % of nameplate; confidence margin capped 0.8 °C;
  outage recovery 2 h with DHW 45 min behind; snow damping 0.5 for 2 days;
  window relax 1 °C; mould RH limit 0.8; grid-fee plausibility bound 10/kWh;
  buffer planned as a store only at ≥ 100 L; DHW min at least 5 °C below the
  charge limit.
* **Actuation limits** — one `number.set_value` per 300 s, 3 divergence ticks
  to stand down, boost 2 h, manual-plan window 20 h, peak-guard hysteresis
  2 samples, mixed water at 40 °C, heavy-day quantile 0.9.
* **Modes** — `set_mode` accepts exactly auto/comfort/economy/boost/off;
  economy widens 1.5 °C and floors at 15 °C.
* **Version and platform** — `manifest.json` version `6.3.20` equals `VERSION`;
  `hacs.json` declares `2025.2.0` and the README badge and requirement line
  agree; manifest requirements are exactly
  `numpy>=1.24.0`, `scipy>=1.10.0`, `threadpoolctl>=3.5.0`; the documentation
  URL is the repository.
* **Translations** — every `strings.json` entity leaf exists in both
  `translations/en.json` and `translations/sv.json` (0 missing either way), so
  "translated (English and Swedish)" holds for every entity name.
* **Options-page titles** — all 21 pages have a `strings.json` step block.
* **Links** — every relative markdown target in README and the seven docs
  resolves on disk; the only misses are the four files this export deletes on
  purpose (`docs/backlog.md`, `docs/audit-2026-08.md`, `docs/audit-2026-09.md`,
  `RELEASE_NOTES.md`), which are reported separately and not counted as broken.
* **Card options** (`docs/dashboard-card.md`) — `hours` default 24 with the
  documented `>0 and <=168` guard, `what_if` default `true`, `show_stats`
  default `true`, the seven `series` keys, and the `SEK` currency fallback all
  match `parseConfig`/`DEFAULTS` in the shipped card.

Disproved leads, with the gap named:

* *"docs/configuration.md's `apply_schedule` field count is stale like the
  others"* — it is not: 5 schedule fields + `entry_id` = 6, exactly what
  `services.yaml` declares.
* *"the per-page field counts are wrong because the harness renders with an
  empty entry"* — real risk, and it is why the finding rests on
  `config_flow._OPTION_FIELDS` (the static page/field table) rather than only
  on a rendered schema: conditional fields (the wood-tank block on *Heating
  system and heat storage*) are present in `_OPTION_FIELDS` whether or not the
  entry enables them, so the counts cited are not an artefact of the fixture.

## What I could not finish

* **External links were not HEAD-requested.** This seat is walled off from
  GitHub and has no outbound network; `hacs.xyz`, `developer.tibber.com`,
  `img.shields.io`, `home-assistant.io`, `python.org` and the two
  `github.com/strutsfarm/*` URLs are therefore unchecked. They are not counted
  in the false or true totals.
* **Six version/history claims are `unverifiable` in this export** and are
  recorded as such, not guessed: "Since v5.0.0 entity names are translated";
  "Since v4.1.0 the ECL110 settings live only on the Heat curve control page";
  "The Danfoss ECL110 MQTT fields were asked here until v4.1.0"; "DHW Cost
  renamed from Hot Water Cost by #174, existing installs keep their entity id";
  "Before v5.1.6 the page simply refused to save"; "Backlog items 1–33 are all
  delivered". The first five need release history; the last needs
  `docs/backlog.md`, which the dispatch deletes.
* **`docs/how-it-works.md` is 1304 lines** and its prose carries more
  mechanism-level claims than the ~20 numeric bounds sampled here. The bounds
  checked all held; a full pass over its behavioural prose (each claim driven
  through a golden scenario) did not fit the budget.
* **`DISCLAIMER.md` and `docs/automations.md`** were read and their links
  resolved, but their claims are legal/illustrative rather than numeric; no
  check beyond link resolution was executed against them.

## Harnesses

* `tools/audit/round3/D6/claims.py` — the claims table. One command in its
  header; writes `claims.csv` and `claims.md`; prints one `RESULT` per number.
* `tools/audit/round3/D6/store_probe.py` — the `.storage` census by
  instrumenting `Store.__init__`. Imported by `claims.py` and runnable alone.

Both pin BLAS threads before any numpy import, write only under their own
directory, and resolve the repository as `Path(".")`.

## exposure

Documents opened that could carry earlier audit findings: **none of the audit
records** — `docs/audit-2026-08.md`, `docs/audit-2026-09.md`, `docs/backlog.md`
and `RELEASE_NOTES.md` are absent from this export and were not sought. No
`docs/plan-*.md` and not `docs/HANDOVER.md` were opened. Read in full or in
part for claim extraction: `README.md`, `DISCLAIMER.md`, `docs/configuration.md`,
`docs/how-it-works.md` (scanned for numeric claims), `docs/architecture.md`,
`docs/dashboard-card.md` (options table and card source), `docs/ecl110.md`,
`docs/automations.md` (link targets only), `CLAUDE.md`, `tools/audit/README.md`,
`tools/audit/briefs/COMMON.md`, `tools/audit/briefs/D6.md`, and the round-3
seat block. Code comments in `tests/entities.py` cite issue numbers (`#174`,
`#558`, `#546`, `#286/#287`, `#516`, `#294`) and a round-2 harness path; these
were treated as context, not as a to-do list, per the dispatch. No `gh` was run
and no GitHub page was read.
