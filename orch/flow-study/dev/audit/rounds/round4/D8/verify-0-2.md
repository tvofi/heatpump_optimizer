# D8 round-4 verification — verifier 2 of 3 (panel D8-0)

- Worktree: `../audit-r4-verify-D8-2`, detached at branch head `0855277`
  ("Merge remote-tracking branch 'origin/main' into claude/13-dimension-audit-920935").
  Findings were measured at baseline `7dd68dd`;
  `git diff --stat 7dd68dd..0855277 -- custom_components/heatpump_optimizer/sensor.py
  custom_components/heatpump_optimizer/icons.json .../strings.json .../translations/
  tests/hastub/` is empty — none of the files these findings measure moved, which
  is why every number reproduces exactly.
- Stance: refute-first, per `tools/audit/briefs/verifier.md`. Other verifiers'
  output and the register were not read.
- Every number below is a count. `load1` ran 4.0–4.9 across my runs (other agents
  on the box); nothing here is a timing, wall, CPU or RSS number, so nothing is
  contention-sensitive. All harnesses were run from THIS worktree's root (they
  resolve `custom_components/...` relative to the cwd, so they measure my tree,
  not an evidence tag).

## Re-runs of the finder's harnesses (exact)

| harness | key RESULTs | load1 |
|---|---|---|
| `naming_order.py` | `entities=74`, `name_order_intruders=159`, `sensor_id_order_intruders=92`, `entity_without_icon_entry=4`, `orphan_icon_keys=0` — every header value exact | 4.86 |
| `naming_order.py --perturb tariff-prefix` | `name_order_intruders=101`; tariff family `60→0` intruders, `4→0` breaks | — |
| `naming_order.py --perturb drop-icon` | `entity_without_icon_entry=5` | — |
| `entity_matrix.py` (full 75 cells, `orjson_mode=real` from the pre-existing `/tmp/d8pkgs`) | `cells=75`, `entity_cells=5550`, `entity_category_declared=1500`, `timestamp_naive=75`, every other class 0 except `stale_dict_source_undecided=542`, `never_alive_enabled_default=12`, `never_available_enabled_default=6` — identical to the recorded `matrix_run.txt` on every count line | 4.45 |

## My own harness

`tools/audit/round4/D8/verify2_own.py` (this worktree, uncommitted): own span
code (position arithmetic), own family table (explicit translation-key sets I
wrote by hand from the entity dump against the seven families `briefs/D8.md`
itself names — no regex), own null control (closed form `(n-k)(k-1)/(k+1)`
checked against 2000-draw simulation per family), own perturbations
(`--perturb cost-prefix` renames only the six PRIMARY tariff members, excluding
the diagnostic-and-disabled `contract_comparison`; `--perturb drop-icon2`
removes `sensor.dhw_temperature`'s icons entry). D8-INST arm reduction stated
in its header: 1 cell of the finder's 75, 1 cycle of its 2, same real solve.

Numbers (default arm): `own_entities=74`, `own_name_intruders_total=159` with
per-family `dhw=7 tariff=60 learning=45 accuracy=29 ecl110=0 pv=0
card_headline=18` — byte-identical to the finder's table from independent code.

## D8-01 — alphabetical order splits five of seven families

**My number: 159 (incidences), 66 distinct foreign entities. Verify.**

Attacks, in the contract's order:

1. *Wrong gate mode / contention* — not applicable and not arguable: no
   `env_drift`/gate in these harnesses, counts only, both perturbation arms and
   the full matrix reproduce the recorded runs exactly at `load1` 4.0–4.9.
2. *Aggregate artefact* — two real finds, neither fatal.
   - The total 159 sums (family, intruder) **incidences**: an entity that
     intrudes into two families' spans counts twice. My distinct count is **66**
     of the 67 possible foreign entities (families overlap:
     `optimization_score` sits in both `accuracy` and `card_headline`). The
     claim's wording "159 foreign entities inside the seven families' spans"
     reads like a head-count; the true head-count is 66. The per-family table —
     the substance — is unaffected and exact.
   - Null control (mine): the expected intruder count for a uniformly random
     family of the same size among 74 entities totals **289.6** (simulated
     289.9) across the seven sizes, against the observed 159. So the families
     cluster better than chance in aggregate, but not uniformly: `tariff`
     (60 vs null 50.2) is **worse than a random family of 7**, and `learning`
     (45 vs 46.0) sits exactly at chance; `dhw` (7 vs 52.4) and `card_headline`
     (18 vs 46.0) beat chance substantially. The brief's bar is that related
     entities cluster, not that they beat chance, so this contextualises rather
     than refutes; it does confirm the finder's own emphasis on `tariff` as the
     worst case.
   - Leave-one-out was already the finder's (drop `tariff` → 99; dropping
     `ecl110` or `pv` changes nothing). My prefix test: only `ecl110`
     (`'ECL110 '`) and `pv` (`'Solar '`) share a literal common name prefix —
     exactly the two zero families, independently confirmed with
     `os.path.commonprefix`.
3. *Reachability in real Home Assistant* — the strongest attack I had, and it
   fails to dissolve the finding. On a real HA device page, DIAGNOSTIC-category
   entities render in a separate section and disabled entities are absent, so
   not all 74 names ever interleave. My UI-section variant (enabled entities
   only, per category section) still leaves `tariff=43`, `learning=20`,
   `accuracy=13`, `card_headline=11`, `dhw=3` — the money family remains split
   on the page the user actually sees. One rhetorical weaken: the showcase
   "good" family `ecl110` is entirely **disabled-by-default diagnostics** (both
   members), so it is not a user-visible exemplar; `pv` (3 primary, enabled)
   carries that side of the argument alone.
4. *Perturbation / mechanism* — my own `cost-prefix` arm (which renames only
   the six members that can ever sort together on a real page): total
   `159→101`, tariff `60→0` intruders `4→0` breaks, and my UI-section tariff
   count `43→0`. The stated cause (shared prefix clusters the family) is
   measured, twice, by two harnesses.
5. *Severity* — `low`/`hygiene` is right per COMMON.md ("`low` = hygiene"):
   nothing published is wrong; the fix is display names only. The finder's
   warning that `unique_id`/`entity_id` must not move is correct and material.

**Metric definition I measured under**: foreign-entity incidences strictly
inside each of the brief's seven families' span in the English-display-name
alphabetical order over the 74 entities built by the real `async_setup_entry`
on one all-features install — 159 incidences / 66 distinct entities.

**Vote: verify, severity low (hygiene).**

## D8-02 — four entities are the only ones without an icons.json entry

**My number: 4 (same four), control 31/4/38/0. Verify.**

1. *The finder's harness does not print the 31/0 control.* The report says the
   control was "folded into `naming_order.py`'s output"; the tree's
   `naming_order.py` has no device-class read and prints no such RESULT — the
   control arrived only as prose with a `/tmp/d8_icons.py` that is not in the
   tree. This is a harness-evidence gap, not a wrong number: my own harness
   reproduces the control exactly.
2. *My own 2x2 control* (device class read the corrected way, property-else-
   `_attr_`): **dc+icon = 31, dc+no-icon = 4, no-dc+icon = 38, no-dc+icon-missing
   = 0**. So the finder's "31 entities carry both a device class and an explicit
   icon; 0 entities without a device class lack one" is exact, and the
   convention ("every entity gets a chosen icon") holds in both directions:
   69 of 73 translation-keyed entities have an entry; the only four without are
   exactly `sensor.optimal_setpoint`, `sensor.outdoor_temperature_optimizer`,
   `sensor.measured_power`, `sensor.compressor_frequency_advisor` — and all
   four HAVE device classes (my `nodc_without_icon=0`), which is what makes
   them render with the stock device-class glyph rather than nothing.
3. *No alternate icon path*: `grep -rn "_attr_icon\|def icon"` over
   `custom_components/heatpump_optimizer/*.py` is empty — no entity sets an
   icon in Python, so `icons.json` (55 sensor keys) is the only icon mechanism
   and the gap is live on a real install, not stub-only.
4. *Perturbation*: finder's `drop-icon` 4→5 reproduced; my `drop-icon2`
   (different entity, `dhw_temperature`) also 4→5 with `dc_with_icon`
   31→30. The number measures the constructed set, not a constant.
5. *Severity* — cosmetic rendering beside siblings; `low`/`hygiene` earned.

**Metric definition I measured under**: translation-keyed entities of the real
`async_setup_entry` build with no `icons.json["entity"][platform][key]` entry,
crossed with a corrected-read device_class declaration — 4 without an entry;
31 dc+icon / 4 dc-only / 38 icon-only / 0 neither-side violations.

**Vote: verify, severity low (hygiene).**

## D8-INST — hastub's SensorEntity declares no device_class/state_class/entity_category, so property reads are vacuously None

**My numbers: 35/45/20 vacuous reads; the four checks 0/0/0/0 under the property
read vs naive=1 under the corrected read on a solved cell; 20 declared
entity_categories per cell → 1500 over 75 cells. Verify.**

1. *Source confirmed by reading the stub*, not by running it:
   `tests/hastub/homeassistant/components/sensor.py`'s `SensorEntity` declares
   exactly three members — `options`, `state` (which itself reads
   `_attr_device_class` via getattr, consistently with the gap),
   `native_unit_of_measurement` — and `tests/hastub/homeassistant/helpers/
   entity.py` is 10 lines with no `Entity` base and no such properties.
   No production or test class overrides `device_class`/`state_class`/
   `entity_category` as a property (grep is empty), so `getattr(ent, "device_class")`
   is `None` for every entity under the stub regardless of what the tree
   declares.
2. *Vacuousness demonstrated, not asserted* (my reduced arm, stated: 1 cell of
   75, 1 cycle of 2, real solve): every entity that declares
   `_attr_device_class`/`_attr_state_class`/`_attr_entity_category` reads
   `None` through the property — **35 / 45 / 20 entities** — and the four
   checks the finder names all read **0** under the property read on a solved
   payload, while the corrected read turns `timestamp_naive` to **1** (75 over
   the finder's 75 cells) with the other three 0. The corrected read is live;
   the property read cannot ever fire.
3. *The 1500 tell*: my full-scale re-run of the finder's harness prints
   `entity_category_declared=1500` (= 20 × 75), and my own reduced run counts
   the same 20 declaring entities per cell. Two independent constructions
   agree.
4. *One understatement, in the finder's favour of accuracy*: the claim says
   "four of D8's checks read zero vacuously"; at least six were vacuous —
   `enum_missing_options_attr`, `device_state_class_impossible` and
   `unit_without_device_class_unlisted` key on the same dead reads. The gap is
   broader than claimed, which strengthens the instrument finding.
5. *Is the corrected read sound?* Property-first-then-`_attr_` is upstream's
   semantics (the property exists in real HA and reads `_attr_`); the harness
   would prefer a property if one existed. Sound. Per `tools/audit/README.md`'s
   "a defect in an instrument is a finding", this is a legitimate D8 instrument
   finding; the finder repaired it in-harness, and the stub gap remains for the
   next auditor (exactly the trap `verify2_own.py` documents in its header).

**Metric definition I measured under**: entities of the real
`async_setup_entry` build where `getattr(ent, P)` is None while
`getattr(ent, "_attr_"+P)` is declared (P in device_class, state_class,
entity_category) — 35/45/20; and entity-cells with a declared entity_category
under the corrected read over the 75-cell matrix — 1500.

**Vote: verify, severity low (instrument/hygiene; the finder left it
unclassified — the stub is a test double, the consequence is confined to
auditors, but it silently zeroed D8 checks and will do so again).**

## Conditions

`RESULT thread_factor=1.00` everywhere (counts only; the pin is applied before
the numpy import in both harnesses). `swapins=0`. `load1` 4.0–4.9 (shared box,
quoted not gated). Files written: `tools/audit/round4/D8/verify2_own.py`,
`verify2_own_detail.json`, this file, and the harnesses' own detail JSONs
(naming/matrix) refreshed by my runs — all inside the D8 directory of this
worktree, nothing committed, main checkout untouched.
