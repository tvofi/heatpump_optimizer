# D8 verification — seat 1 (verify-0-1)

Panel D8-0, audit round 4. Verifier stance: refute-first.

- Worktree: `../audit-r4-verify-D8-1`, detached at `0855277` (branch head of
  `claude/13-dimension-audit-920935`). Uncommitted; nothing outside
  `tools/audit/round4/D8/` was touched.
- Baseline relevance: `git diff --stat 7dd68dd..HEAD -- custom_components/`
  is two files, one line each — `manifest.json` and the card's
  `CARD_VERSION`, both `6.4.2 → 6.4.3`. No entity, name, icon or stub change.
  The findings' subject matter is identical to baseline.
- Interpreter: `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`,
  `PYTHONPATH=tests/hastub` (plus `:/tmp/d8pkgs` for `entity_matrix.py`, whose
  header names it; `/tmp/d8pkgs` still holds orjson 3.12.0).
- Every number below is a count; `load1` ran 2.7–6.6 and is quoted in the
  logs, ungated by contract (counts are contention-immune). No timing,
  wall, CPU or RSS number is relied on anywhere.

## Harnesses re-run (finder's, exactly per headers)

| run | result |
|---|---|
| `naming_order.py` (default) | all 20 RESULT lines identical to `naming_run.txt`: `name_order_intruders=159`, `entity_without_icon_entry=4`, `orphan_icon_keys=0`, `id_order_intruders=178`, `sensor_id_order_intruders=92`, families 7, entities 74; per-family name intruders 7/60/45/29/0/0/18, breaks 1/4/3/2/0/0/4 — byte-identical to the finder's recorded run |
| `naming_order.py --perturb tariff-prefix` | `name_order_intruders` **159 → 101**; tariff family 60 → 0 intruders, 4 → 0 breaks — exactly the finder's claim |
| `naming_order.py --perturb drop-icon` | `entity_without_icon_entry` **4 → 5** — exactly the finder's claim |
| `entity_matrix.py` (default arm, 75 cells × 74 entities × 2 cycles, real solve per cycle, real orjson) | all 20 RESULT lines identical to `matrix_run.txt`, including `entity_category_declared=1500`, `timestamp_naive=75`, `stale_dict_source_undecided=542`, `never_alive_enabled_default=12`, `never_available_enabled_default=6` |

Re-run logs archived as `d8v1_rerun_*.txt` beside this report. The re-runs
rewrote `naming_detail.json` / `matrix_detail_naive.json` (each harness writes
into its own directory; `naming_detail.json` was re-run last in the default
arm so it is again the default-arm detail).

## My own harnesses (one per finding, beside the finder's)

`d8_own_D8-01.py`, `d8_own_D8-02.py`, `d8_own_D8-INST.py`; logs
`d8v1_own_*.txt`; details `d8_own_D8-*_detail.json`. Each builds every
entity through the real `async_setup_entry` on the all-features topology
(my own seeding; `tests/entities.py:collect` is unimportable — that script
runs its whole check suite at import and exits, which the README's trap list
warns about). `tests/golden.py:coordinator_scenarios` is used as the README
directs.

---

## D8-01 — alphabetical order splits five of seven families — **vote: verify (low, hygiene)**

**Finder's number**: `name_order_intruders = 159`. Reproduced exactly.

**My own number**: `span_intruders_total = 159` (`d8_own_D8-01.py`), with
membership enumerated **by hand** as explicit translation-key sets — no
regex, nothing inherited from the finder's `FAMILIES` dict. Per family:
dhw 7 / tariff 60 / learning 45 / accuracy 29 / ecl110 0 / pv 0 /
card_headline 18; breaks 1/4/3/2/0/0/4 — identical to the finder's
per-family table.

**Metric definition (mine)**: over the 74 entities of an all-features
install, sorted by English display name, sum over the seven brief-named
families of the count of non-member entities sorting strictly between the
family's first and last member. (Note the sum counts (family, intruder)
*pairs* — there are only 67 non-family entities; the finder's report states
the per-family definition, so the number is honest, but a reader skimming
"159 foreign entities" should know it is a pair sum, not a head-count.)

**The prefix claim**: `zero_intruder_families = 2` (ecl110, pv) and
`shared_first_word_families = 2` — **the same two**, `zero_equals_shared_word
= True`. The two families that score zero are exactly the two whose display
names share a literal first word (`ECL110 …`, `Solar …`). Reproduced.

**Perturbations, both directions, both executed**:
- finder's (re-run): give the seven tariff entities a shared `"Cost "` prefix
  → 159 → **101**, tariff 60 → 0 intruders, 4 → 0 breaks;
- mine (`--perturb scatter`, opposite direction): strip the literal prefix
  from the two zero families → 159 → **198**; `pv` (prefix removed) goes
  0 → **35** intruders. My ecl110 rename accidentally kept a shared
  ("Flow Displacement") prefix — and ecl110 stayed at 0, an unplanned
  within-run control: share a prefix → cluster; lose it → split.

**Attacks run**:
1. *Membership sensitivity*: a narrower "money-only" tariff family (the five
   cost/price/contract entities, without `monthly_peak_power` and
   `power_headroom`) scores **62** intruders, not fewer — including the two
   power-flavoured members does not inflate the finding. The seven families
   themselves are the brief's own list (`tools/audit/briefs/D8.md` step 3
   names DHW, tariff, learning, accuracy, ECL110, PV, card headline), so
   family selection is not the finder's invention.
2. *Leave-one-out*: min 99 (drop tariff), max 159 (drop a zero family) —
   matches the finder's stated range; no single family carries the number.
3. *Card claim*: `HEADLINE_SUFFIXES` (`www/heatpump-optimizer-card.js:1251`)
   resolves the four plan-narrative sensors together and
   `statEntity("_monthly_savings")` (`:10075`) joins them — the five really
   are one card row that alphabetical order scatters over 18 names and 4
   runs.
4. *Prose-table discrepancy (noted, does not reach the verdict)*: FINDER.md's
   per-family table's last column ("sensor-id intruders") says dhw 10,
   accuracy 44, learning 28 — the finder's own committed
   `naming_detail.json` (and my re-run) say **dhw 0, accuracy 6, learning
   24**. Three of seven rows of that one column disagree with the recorded
   JSON; the total 92 and the other four rows agree. The headline metric
   (display-name order) is untouched; if anything the true sensor-id column
   (dhw clustering perfectly under id order) supports the finding's
   prefix→cluster reading. A report-hygiene error, worth the judge's eye.
5. *Is the ordering real?* The criterion is the owner's brief verbatim
   ("grouping and naming such that alphabetical sort clusters related
   entities"), so the metric measures the dimension's own question. Nothing
   wrong with any published value — `low`/`hygiene` is the earned severity.

## D8-02 — four entities have no icons.json entry — **vote: verify (low, hygiene)**

**Finder's numbers**: `entity_without_icon_entry = 4` (`sensor.optimal_setpoint`,
`sensor.outdoor_temperature_optimizer`, `sensor.measured_power`,
`sensor.compressor_frequency_advisor`), `orphan_icon_keys = 0`. Both
reproduced exactly.

**My own numbers** (`d8_own_D8-02.py`, device class read from
`_attr_device_class` — see D8-INST for why that is the only live read):
`no_icon_entities = 4` (the same four), `dc_and_icon = 31`,
`dc_no_icon = 4`, `no_dc_no_icon = 0`, `no_dc_icon = 38`. And a **build-free
path** — `strings.json` keys minus `icons.json` keys per platform, no
entities constructed at all — also gives **4**.

**The 31/0 control**: 31 entities carry both a device class and a chosen
icon; 0 entities without a device class lack one. The device-class defence
("HA's default glyph makes an icon unnecessary") predicts the opposite of
31. All four exceptions **have** device classes (my harness prints them:
temperature, temperature, power, frequency), so they render stock
device-class glyphs beside siblings that chose theirs (`Indoor Temperature
(Optimizer)` → `mdi:home-thermometer` etc., verified in `icons.json`). The
integration's own convention is "every entity gets a chosen icon"; these
four are the exceptions. The finder's framing survives refutation-first.

**Perturbations, mine, both directions**: remove a *different* icon entry
(`sensor.recommended_power`) → **5**; add the four missing in memory →
**0**. The finder's own `drop-icon` (removing
`indoor_temperature_optimizer`) → **5**, re-run and reproduced. The count is
a measurement over the constructed set, not a constant.

**Attacks run**:
1. *Reachability*: `icons.json` is HA's real per-entity icon mechanism for
   custom integrations and all four entities exist on a real install (three
   enabled by default; `compressor_frequency_advisor` disabled but still
   iconless when enabled). Consequence is cosmetic — generic glyph beside
   chosen ones — so `low`/`hygiene` is earned, no more.
2. *Aggregate artefact*: the number does not depend on the install topology
   — the build-free file diff gives the same 4 without any coordinator at
   all.
3. *Orphans*: `orphan_icon_keys = 0` re-verified — no icon points at a
   nonexistent entity, so the finding is exactly "four entities lack
   entries", not "the file drifted".

## D8-INST — hastub SensorEntity's missing properties make checks vacuous — **vote: verify (low, instrument hygiene; filed unclassified)**

**Claim**: `tests/hastub`'s `SensorEntity` declares no `device_class` /
`state_class` / `entity_category` property, so four of the finder's checks
read 0 vacuously through the property path; the corrected `_attr_*` read is
live, told by `entity_category_declared = 1500`.

**My own numbers** (`d8_own_D8-INST.py`):
- `stub_property_declarations = 0` — none of the three names is defined as
  a property in the stub's sensor module; **0 anywhere in `tests/hastub`**
  (`rg 'def device_class|def state_class|def entity_category'` over the
  whole stub returns nothing), and 0 property declarations of those names
  in a built entity's entire MRO. Also verified absent from
  `custom_components/heatpump_optimizer/**` — no property exists to rescue
  the read.
- The vacuity, executed: over the built sensor entities, the public-property
  path reads non-None for **0** (device_class) / **0** (state_class) /
  **0** (entity_category) entities; the `_attr_*` path reads **32 / 45 /
  18** (sensor platform; 59 entities). `getattr(ent, "device_class", None)`
  is `None` for *every* entity in the tree.
- Injected violations (class-attribute swap with try/finally — the repo's
  own idiom — into real production classes `PlanNarrativeSensor`,
  `IndoorTempSensor`, `LastOptimizationSensor`): the finder's four check
  predicates fire **4 of 4** through the `_attr_*` path and **0 of 4**
  through the property path. That is the executed proof that "reads zero
  vacuously" is exactly what the property path does: four live violations
  sit in production classes and the property path counts none of them.
- The tell: the finder's full-matrix `entity_category_declared = 1500`
  reproduced in my re-run; my reduced matrix (**reduction stated**: 5 cells
  — 5 topologies × the merged-all overlay — sensor platform only, no solve;
  category is a class attribute, not payload-derived) gives 18/cell →
  18 × 75 = 1350 sensor-only, plus the 2 per-cell DIAGNOSTIC binary sensors
  (`input_problem`, `open_window_detected`, confirmed by grep and by
  building the other five platforms) = **1500** all-platform. The property
  path would print **0** at every cell count.

**Attacks run / notes**:
1. *"Four checks" is an undercount*: through the property path,
   `enum_missing_options_attr`, `unit_without_device_class_unlisted` and
   `device_state_class_impossible` also gate on the dead reads and would
   read 0 vacuously — seven check classes, not four. The finding's claim is
   true as stated and strictly stronger in scope; I could not attack it in
   the weakening direction.
2. *"Three runs"* (default / `--tz` / `--no-solve` arms) is not directly
   re-runnable — the finder corrected the harness before committing it —
   but my property-path simulation over the same construction is the
   equivalent evidence: every dc/sc-gated predicate is structurally dead
   through that path.
3. *Is it a finding at all?* Yes under `tools/audit/README.md`'s
   "a defect in an instrument is a finding" rule: `tests/hastub` is a named
   instrument, upstream HA's `SensorEntity`/`Entity` do define these three
   properties, and the stub's omission is silent (no error, plausible zero)
   — it already bit this dimension's own harness once, exactly the
   stub-pins-the-test failure the stub's own `state` docstring (#536/#543)
   warns about. Severity `low`: no product value is wrong; the cost is that
   any future harness reading the public property inherits a vacuous zero.
4. *Could the finder have staged the trap?* No: the properties are absent
   in the committed stub at both baseline and head (`git diff 7dd68dd..HEAD`
   touches no stub file), and the vacuity is structural, reproduced by my
   own read path independent of the finder's code.

## Votes

| id | vote | severity | value |
|---|---|---|---|
| D8-01 | verify | low (hygiene) | 159 (reproduced exactly; own harness 159; perturbations move both directions) |
| D8-02 | verify | low (hygiene) | 4 without icons, orphan 0; control 31/0 (all reproduced; own harness incl. build-free path) |
| D8-INST | verify | low (instrument hygiene; filed unclassified) | 0 properties; 0/4 vs 4/4 injected; tell 1500 reproduced and reconciled |

No timing-based evidence is relied on; nothing is left unresolved.
