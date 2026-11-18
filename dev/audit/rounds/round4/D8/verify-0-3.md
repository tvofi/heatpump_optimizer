# D8 verify-0-3 (round 4, seat 3 re-run)

Verifier 3 of 3 on panel D8-0. Tree: `claude/13-dimension-audit-920935` at
`3e91f85` (detached worktree `../audit-r4-verify-D8-3`). Baseline the finder
measured: `7dd68dd`. `git diff 7dd68dd..HEAD` over every file these findings
touch (`strings.json`, `icons.json`, `translations/`, `sensor.py`,
`binary_sensor.py`, `tests/hastub`, `tests/golden.py`, `tests/harness.py`,
card js) is **one line**: a `CARD_VERSION` bump 6.4.2→6.4.3. The numbers
below therefore measure the same code the finder measured.

Interpreter `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`,
always `PYTHONPATH=tests/hastub` (+`/tmp/d8pkgs` for the matrix, orjson
3.12.0, still present), always from the worktree root. **Every number here is
a count**; `load1` ran 3.2–11.6 (other agents on the box) and nothing here is
load-sensitive. Did not read verify-0-1.md, verify-0-2.md, `d8_own_*`,
`d8v1_*`, or `verify2_own*` — this seat's harness and report are written from
the finder's report and the tree alone. Own harness:
`tools/audit/round4/D8/verify3_own.py` (+ `verify3_own_detail.json`).

## D8-01 — alphabetical order splits five of seven families — **verify** (low, hygiene)

**Finder's harness re-run, as its header says** (`naming_order.py`, default
arm): `entities=74 families=7 id_order_intruders=178
name_order_intruders=159 sensor_id_order_intruders=92`. Per-family table
byte-identical to the finder's (dhw 7/1, tariff 60/4, learning 45/3,
accuracy 29/2, ecl110 0/0, pv 0/0, card_headline 18/4). Perturbation arm
`--perturb tariff-prefix`: `name_order_intruders 159 → 101`, tariff
`60→0` intruders `4→0` breaks — the metric moves under exactly the change
the finding prescribes. `load1=3.21`, counts only.

**My own harness, my own metric.** I rebuilt every entity through the real
`async_setup_entry` under **my own** all-features overlay and price/weather
series, wrote **my own** family regexes from the brief's words (the seven
families are the brief's — `briefs/D8.md` §3 names "DHW, tariff, learning,
accuracy, ECL110, PV, card headline", so the family set is not
finder-invented), and derived the card-headline family from the card's own
`HEADLINE_SUFFIXES` array (card js :1251) plus the `statEntity("_monthly_savings")`
join (:10075), not from the finder's regex. Metric: *non-member entities
strictly inside each family's span in the globally sorted English display-name
list, summed over the seven families*.

- `v3_name_intruders_codepoint_all = 159` — **exact match** under my own
  membership rules and my own construction. Per family: 7/60/45/29/0/0/18.
- **Sort-key attack (died):** recomputed under casefold collation (closer to
  the HA frontend's locale compare) — also 159, identical per family. Every
  display name is Title Case, so codepoint and casefold agree; the finder's
  plain `sorted()` is not distorting the number.
- **Grid/re-aggregation attack (died):** recomputed on a `coord_minimal`
  install — also 159, identical. Entity construction is unconditional (74
  entities in every config; the 75-cell matrix prints
  `entities_per_cell=[74]` for all topologies and overlays), so the number is
  config-invariant, not an all-features artefact. Leave-one-family-out
  (casefold): dhw 152, tariff 99, learning 114, accuracy 130, ecl110 159,
  pv 159, card_headline 141 — matches the finder's stated range 99–159.
- **Prefix claim (verified my own way):** longest-common-prefix test over each
  family's display names: exactly `ecl110` ("ECL110 ") and `pv` ("Solar ")
  share a literal prefix, and they are exactly the two zero-intruder
  families. No other family shares one.
- **Aggregate-phrasing attack (lands as a note, not a weaken):** 159 is a sum
  of per-family *slots*, not distinct entities. My own recount:
  `v3_distinct_intruding_entities = 65`, and 68 of the 159 slots are held by
  entities that are themselves members of another audited family (e.g.
  tariff members sitting inside learning's span); `optimization_score` is the
  one entity claimed by two families (accuracy + card_headline). The
  finding's sentence "159 foreign entities inside the seven families' spans"
  reads as 159 distinct entities if you don't consult the table beside it.
  The finder's metric definition is per-family-and-summed and the table is
  per-family, so the number is honest under its own definition; the
  substance (five families split, worst is tariff at 60/4) is unaffected.
- **Reachability:** the surface is real — HA's device page and entity pickers
  sort by friendly name, and the English names come from `translations/en.json`
  via `translation_key`. The card's one-row treatment of the five headline
  entities is real (`HEADLINE_SUFFIXES`, `statEntity`, `statNumber` all
  present in the card at :1251/:4225/:10075). Nothing published is wrong;
  the brief's owner quote explicitly asks for "grouping and naming such that
  alphabetical sort clusters related entities", so this is that goal
  measured and missed.

**Vote: verify.** Severity `low`, stop-rule `hygiene` — earned: no wrong
value, cosmetic ordering; fix is display names only.

## D8-02 — four entities with no icons.json entry — **verify** (low, hygiene)

**Finder's harness re-run:** `entity_without_icon_entry=4`,
`orphan_icon_keys=0` (default arm); `--perturb drop-icon` → `5`. Exact.

**My own harness, my own metric.** Metric: *2×2 cross-tab over the 73
translation-keyed entities — (declares `_attr_device_class`) × (key present
in `icons.json`'s `entity` table)*, plus a structure check that every icon
entry carries a `"default": "mdi:…"` value, plus the reverse perturbation
(give the four missing keys an icon in memory; the count must fall to 0).

- `v3_entity_without_icon_entry = 4`; the four are exactly
  `sensor.optimal_setpoint`, `sensor.outdoor_temperature_optimizer`,
  `sensor.measured_power`, `sensor.compressor_frequency_advisor`.
- Cross-tab: **dc+icon 31, dc+noicon 4, nodc+icon 38, nodc+noicon 0** — the
  finder's 31/0 control reproduces under my own read. The device-class
  defence ("HA supplies the default icon, so they don't need one") is
  refuted as the integration's convention: all 38 entities *without* a
  device class nevertheless carry a chosen icon, so the convention here is
  "every entity gets a chosen icon"; these four are the exceptions.
- Consequence check in source: all four *do* declare device classes
  (`CurrentSetpointSensor`/`OutdoorTempSensor` TEMPERATURE,
  `MeasuredPowerSensor` POWER, `CompressorFrequencyAdvisorSensor` FREQUENCY,
  `sensor.py` :617/:716/:1595/:2526), so on a real install they render HA's
  generic device-class glyph beside siblings with chosen icons — precisely
  the finder's stated consequence, and bounded there. Nothing breaks.
- Reverse perturbation: adding the four icons in memory → count 0; finder's
  forward perturbation (drop one) → 5. The number is a measurement over the
  constructed entity set, not a constant. Malformed icon entries: 0.
- One trap I hit myself, recorded: my first cross-tab claimed all 73
  entities had a device class — my own bug (`str()` wrapped around a
  ternary, turning `None` into the truthy string `"None"`), caught because
  my inst-probe disagreed; fixed before any conclusion was drawn.

**Vote: verify.** Severity `low`, `hygiene` — cosmetic icon inconsistency,
no functional effect.

## D8-INST — stub SensorEntity has no device_class/state_class/entity_category property — **verify** (low, instrument defect)

**Finder's harness re-run** (`entity_matrix.py`, 75 cells, 75×74=5550
entity-cells, orjson real, two cycles, real solves): every EXPECTED line in
its header reproduced exactly — `state_write_raises=0`,
`entity_category_declared=1500`, `timestamp_naive=75` (naive arm),
`stale_dict_source_undecided=542`, `never_alive_enabled_default=12`,
`never_available_enabled_default=6`, all other classes 0. `load1=11.63`,
counts only.

**My own probes** (in `verify3_own.py`, §d8inst):

- `tests/hastub/homeassistant/components/sensor.py:57` — `class SensorEntity`
  declares exactly three properties (`options`, `state`, and
  `native_unit_of_measurement`). Executed check:
  `v3_stub_sensor_has_property = {device_class: False, state_class: False,
  entity_category: False}`. `helpers/entity.py` has the `EntityCategory`
  enum but no `entity_category` property either, so the gap is not patched
  from below.
- Over 74 built entities: `_attr_device_class` set on 35, `_attr_state_class`
  on 45, `_attr_entity_category` on 20 — while the public-property read
  (`getattr(ent, prop, None)`) returns **None for all 74 on all three
  properties** (`public_read_none=74` each). Any check keyed on the public
  property — the matrix's `enum_state_not_in_options`,
  `measurement_non_numeric`, `timestamp_naive`,
  `unit_device_class_mismatch`, `device_state_class_impossible` — is
  therefore structurally zero for a reason that has nothing to do with the
  code under test. That is the finder's "vacuous" claim, executed.
- The tell reproduces twice: my own per-build count
  `v3_entity_category_declared = 20`, and the finder's full matrix
  `entity_category_declared = 1500` (= 20 × 75) in my re-run. The corrected
  `_attr_*` read is live, not assumed.
- Reachability of the defect: real Home Assistant declares `device_class`
  and `state_class` on `SensorEntity` and `entity_category` on `Entity`
  (helpers), so on a real install the public reads return real values and
  those checks mean something. The stub's own docstrings say it mirrors
  upstream 2025.2.0 — it mirrors the `state` refusals faithfully but omits
  these three trivial pass-throughs. I could not import real HA (install
  nothing), so the upstream half rests on the stub's own mirroring claim
  plus common knowledge; the *stub* half, which is what the finding accuses,
  is executed fact.

Per `tools/audit/README.md` ("A defect in an instrument is a finding"), this
is a legitimate instrument finding; the finder repaired their own harness
read in place (allowed) but the stub gap remains for the next auditor, which
is exactly what the finding records.

**Vote: verify.** Severity `low` (instrument hygiene — a one-line stub
repair: three pass-through properties); no product consequence, but it
silently voids five of the matrix's checks for anyone who reads the public
API the way HA documents it.

## Conditions

All runs: counts only, `thread_factor=1.00`, `timing_results_reported=0`,
`swapins=0`. `load1` 3.21 (naming default), 11.63 (matrix) — quoted, not
gated; no number here is timing-derived, so contention proves nothing about
them.
