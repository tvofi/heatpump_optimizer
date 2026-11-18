# D8 panel — verifier 1 of 2, refute-first

Baseline `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1`. Tree: a `git archive` export
with no `.git`, so no branch-vs-main diff was available or attempted. Box:
8-core Apple M1, 8 GB, python 3.11.5, numpy 2.4.6, scipy 1.17.1 — the same
environment the finder reports.

**The box was heavily shared throughout.** `load1` ran between 4.8 and 74.2 while
these harnesses executed. Every number in this report is a **count**, and
`thread_factor` was 1.000 on every run (single-threaded, five BLAS variables
pinned before the numpy import), so no number here can move with load. No
timing, wall or RSS number is claimed. No `tests/stress.py`, no `./tests/run.sh`,
no gate lock, no artefact larger than a few kB.

My own instruments are under `tools/audit/round3/D8/verify-1/`:
`v1_wood_reach.py` (D8-01), `v1_mute.py` (D8-02), `v1_families.py` (D8-03), each
with its own header, metric definitions, command, expected values and
perturbation, each runnable from the repository root with
`PYTHONPATH=tests/hastub`. Their raw output and the finder's re-run output are
beside them.

---

## 1. Reproduction of the finder's harnesses

Run exactly as each header says. **Every number reproduced exactly.**

| harness | numbers | verdict | `load1` | `thread_factor` |
|---|---|---|---|---|
| `d8_wood_advisor.py` | 12 of 12 | exact | 6.85 | 1.000 |
| `d8_ordering.py` | 9 of 9 | exact | 6.46 | 1.000 |
| `d8_matrix.py` (23 cells) | 19 of 19 | exact | 73.91 | 1.000 |

Perturbations, also exact:

- `d8_ordering.py --perturb split-ecl110`: `family_splits_entity_id` 36 → **37**;
  `family_splits`, `family_splits_sv`, `case_style_minority` unmoved.
- `d8_matrix.py --limit 2` baseline `available_unknown_default_install=2`,
  `available_but_unknown_everywhere=2`, `frozen_while_input_moved=9`;
  `--perturb wood-gate` → **1** and **1**; `--perturb same-inputs` → **0**.
- `d8_wood_advisor.py`: the `soc=0.2` column publishes `'light Thu 23:00'` in
  the three cheap-wood arms and nothing in the three dear-wood arms, as reported.

`d8_timestamps.py` was not re-run: it backs a non-finding, not any of the three
findings under vote.

The finder's harnesses read `_attr_`-prefixed class attributes rather than
`ent.<property>` wherever the trapped four are involved, so none of the three
findings rests on a vacuous zero. I confirmed the trap is real and applies to my
own work: `tests/hastub`'s entity stubs declare no `device_class`,
`state_class`, `entity_category` or `icon` property. Both of my instruments that
touch those attributes (`v1_mute.py` for enabled-by-default,
`v1_families.py` for the device-page bucket) read the class attribute, and each
says so in its own header.

---

## 2. D8-01 — the Wood-burn night advisor can never advise

**Vote: `verify`, severity `medium`.**

### My number and my metric definition

**`advice_attached_shipped = 0` of 4000.** Metric: the number of
randomized-but-shipped wood-furnace scenarios — seeded, so exact — whose
**published** `wood_fuel` view carries a `night_advice` key, with the
configuration restricted to keys the tree can actually write. Measured by
calling the real publisher `wood_fuel.build_wood_fuel_view` and reading the dict
it returns, so "attached" is observed on the payload rather than inferred from a
branch. `furnace_on_draws = 4000` of 4000 confirms the advisor's own
precondition (`wood_furnace_on` true, wood price resolves) held in every draw,
so the zero is not "the feature was off".

This differs from the finder's `advice_value_as_shipped=0` deliberately: six
solved arms cannot show that *no other input* rescues the advisor. 4000 draws
sweep wood type and packing (all six), wood price 100–2500 SEK/m³, efficiency
45–92 %, horizon 24/36/48 h, start hour 0–23, outdoor −22 to +12 °C, COP
1.6–5.5, and price series with the night dip drawn **in both directions**, so
cheap nights and dear nights are both in the sample.

Controls, on the identical seeded draws:

| arm | count |
|---|---|
| as shipped | **0** |
| `wood_tank_soc=0.2` injected, nothing else changed | **1890** |
| `wood_tank_soc=0.9` injected | **3693** |
| `wood_tank_soc=0.5` injected **explicitly** (null control) | **0** |

The fourth row is the control the finder does not have. It injects the key with
the value the fallback already supplies, so the 0 → 1890 move is attributed to
the **value crossing a threshold** and not to the key merely being present.

### Attack 1 — "one writer refutes it". No writer exists, and here is the closure

I did not grep. `v1_wood_reach.py` builds a **write-set from the parse tree**,
resolving `CONF_*` constants to their string values and unwrapping voluptuous
markers, over every `.py` under `custom_components/`:

- `soc_write_sites = 0` — no dict-literal key, Store-context subscript,
  `dict()` keyword or `.setdefault()` first argument resolves to `wood_tank_soc`.
- `soc_read_sites = 1` — exactly one reader, `wood_fuel.py:463`.
- `unresolvable_write_keys = 175` — the scan's own blind spot, printed in full
  to `v1_wood_reach.sites.txt`.

175 unresolvable key expressions is too large a blind spot to close by
inspection, so I closed the question a second, narrower way. The mapping
`_attach_night_advice` reads is `coord._config`, built **once** as
`{**entry.data, **entry.options}` in `HeatPumpOptimizerCoordinator.__init__`
(`coordinator.py:1300`), so a key can only reach it by being written into the
config entry:

- `async_update_entry_sites = 8`, `async_create_entry_sites = 3`,
  `entry_write_expressions = 10` — every `data=`/`options=` expression in the
  package, each printed with the literal keys it introduces and the name of any
  mapping it splats. All ten carry only literal `CONF_*` keys plus a splat of an
  already-existing mapping (`entry.data`, `entry.options`) or of schema-validated
  `user_input`. `repairs.py:55` is a repair flow's `async_create_entry(data={})`,
  not a config entry.
- `config_mapping_mutations = 3` — and all three are
  `config['unit_of_measurement']`, `config['min']`, `config['max']` on a local
  dict inside `config_flow._number()`'s selector builder, not the entry mapping.
  Nothing adds to `coord._config` after construction.

The set is closed. **There is no writer.**

### Attack 2 — injection past the UI

- `option_pages_rejecting_soc = 21` of `option_pages = 21`. Every option page's
  **real** voluptuous schema, built through the production `_page_schema` on a
  config with every feature block open, raises on `{"wood_tank_soc": 0.2}`.
  Voluptuous defaults to `PREVENT_EXTRA` and there is no `extra=ALLOW_EXTRA`
  anywhere in the package. I checked voluptuous is the real library and not a
  stub (`/Library/.../site-packages/voluptuous/__init__.py`).
- `soc_in_key_universe = 0` of `entry_key_universe = 175` — the union of the
  options-flow field registry `_OPTION_FIELDS` and `topology.ASSIGNABLE_KEYS`,
  taken by executing them rather than reading them.

### Attack 3 — the converse: is it waiting on YAML or a service call?

**No.** `yaml_entry_only_marker = 1`, `async_step_import_defs = 0`: the
integration declares `CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)`
— Home Assistant's canonical "this domain has no YAML configuration" — and
defines no import step. There is no YAML surface for the key to arrive through.
No service writes it either: `assign_entity` validates its key against
`ASSIGNABLE_KEYS`, `apply_topology` and `apply_schedule` write bounded literal
key sets, and the string appears nowhere in `services.yaml`.

**A gap I named rather than measured.** I first wrote this metric as an executed
one — call `CONFIG_SCHEMA({DOMAIN: {"wood_tank_soc": 0.2}})` and see whether it
raises. It returned **`yaml_rejects_soc=0`**, which reads as "YAML accepts the
key". That number is a property of `tests/hastub`'s
`cv.config_entry_only_config_schema`, which is a documented pass-through that
returns the config unchanged and raises nothing. Exactly the class of gap that
made four `device_class` checks measure nothing. I removed the executed metric
and replaced it with the two parse-tree facts above, which the stub cannot
distort.

### Attack 4 — the converse that actually settles it: the value already exists

`wood_tank_soc_already_published = 1`. On a two-tank install with the tank
probes reading, the coordinator payload already carries
`battery.components[name="wood_tank"].soc_percent = 61.5`, derived by
`battery.py:354-371` from the **same** top/bottom probes that
`wood_fuel.wood_fuel_ready` already requires before the advisor may speak at all.

So `wood_tank_soc` is not an undocumented option and this is not a documentation
gap. It is a placeholder for a number the tree already computes and publishes,
and `_attach_night_advice` reads the wrong source for it. **The remedy is a
one-line re-point, not a new config field** — which is worth carrying to the
fixer, because "add a `wood_tank_soc` option to the config flow" would be the
obvious wrong fix and would cost a ratchet-relevant schema page.

Two traps inside this probe, recorded because both produced a confident zero
first:

1. The payload key is **`battery`**, not `thermal_battery`. My first probe read
   `data["thermal_battery"]`, got `components=[]`, and would have reported
   "the SoC is not published" — the opposite of the truth.
2. `two_tank_modelled` is not a flag. It resolves through
   `thermal_model.topology_layout`, which requires a **throttling** mixing-valve
   mode *and* two zones *and* a wood probe. Setting `topology_layout:
   two_tank_4way` alone silently resolves to `no_valve`, and the wood tank never
   becomes a component.

### Attack 5 — why it survived to a release (a test gap, named with its mutation)

The verifier contract asks, for any test-gap claim, for the single-line
**production** mutation the suite fails to notice and the file it lives in.

- `tests/features.py:24835` imports `night_advice` and exercises it **directly**
  at `tank_soc=0.2` and `tank_soc=0.9` — the two values the tree cannot produce
  — and never through `_attach_night_advice`. The function is proven to work
  with inputs the integration can never give it.
- `tests/entities.py:6450` pins only the advisor's attribute **key set**
  `{action, reason, when}`, which is present either way (the defaults are
  `"none"`, `None`, `""`).
- All five golden coordinator fixtures have `wood_fuel.sek_per_kwh = null`
  (executed check over `tests/golden/coord_*.json`), so `_attach_night_advice`
  returns at its `sek is None` guard before the fallback line is reached.
  `night_advice` appears in **zero** golden fixtures.

**The mutation:** `custom_components/heatpump_optimizer/wood_fuel.py:464`,
`soc = 0.5` → `soc = 0.2`. Nothing in the suite notices. It is in a production
file, so the gap is not a test measuring itself. Forward-carry to D3.

### Severity by consequence

`README.md:469` documents the feature — "Wood-burn night advice … 48 h
light/skip advice when the wood furnace is on" — and
`docs/plan-2026-09-open-issues.md:395` records #702 as "shipped … Issue CLOSED
completed". A documented, shipped, closed feature that has never produced output
on any install that has ever existed. Against that: it is advisory only, it
never lights a stove, it is `EntityCategory.DIAGNOSTIC`, and no money, comfort or
safety outcome depends on it. **`medium` is earned; `high` is not.** I agree with
the finder's severity.

---

## 3. D8-02 — one entity renders Unknown where every sibling renders Unavailable

**Vote: `weaken`, severity `low`, value `1` (not 2).**

### My number and my metric definition

**`mute_reporters = 1`** — `WoodBurnAdvisorSensor`. Metric: distinct entity
classes on the **read-only** platforms (`sensor`, `binary_sensor`) that are
enabled by default and, in **every** cell and **both** cycles, report
`available is True` while their published state (`native_value` for sensor,
`is_on` for binary_sensor) is `None`. Six cells — the five golden topologies plus
one where the wood furnace is genuinely configured and `wood_fuel.ready` is True
— each solved twice with the clock +3 h, prices +0.45 and weather −6 K.
`reporter_classes = 58`. Enabled-by-default is read from the
`_attr_entity_registry_enabled_default` **class attribute**.

`control_none_entities = 1` — `AwayReturnDateTime` — reported separately, so the
judge can see precisely which half of the finder's 2 this definition drops.

### The null control, decided

The finder reports 2 and names `AwayReturnDateTime` as "arguably legitimate".
I decided it, and it is **not** the same defect:

`datetime.py:27` — `AwayReturnDateTime(HeatPumpOptimizerEntity, DateTimeEntity)`
with `async_set_value`. It is a **control**, not a reporter. `None` is its correct
representation of "no away override set", and Home Assistant disables a control
whose entity is unavailable — so giving it an `available` gate on "has a value"
would make it impossible to set the very value whose absence triggered the gate.
Marking it unavailable would be a worse defect than the one being fixed.

My metric therefore excludes controls **by construction** rather than by
argument: the platform decides, so no judgement call sits inside the count.
**The count is 1.** The finder named this itself and did not claim it, so this
is a weaken on framing, not a refutation of the mechanism.

The perturbation the finding rests on then moves the metric by exactly 1, which
is the whole finding.

### Perturbation and my own null control

- `--perturb wood-gate` (the proposed one-line fix: give `WoodBurnAdvisorSensor`
  the `available` gate on `wood_fuel.ready` that `WoodCheaperBinarySensor`
  already has at `binary_sensor.py:203`): `mute_reporters` **1 → 0**.
- `--perturb inert-gate` (**my null control**, which the finder does not have):
  an `available` property on the same class returning `super().available`
  unchanged — the same shape of edit carrying no condition. `mute_reporters`
  **1 → 1**. So the drop is caused by the condition, not by the act of defining
  the property.

### The attack that moves my vote — the countermeasure is incomplete

**`mute_on_wood_ready_after_gate = 1`.** On the cell where the wood furnace *is*
configured and `wood_fuel.ready` is True, the **gated** sensor is still
`available=True` with a `None` value. The one-line fix removes the Unknown only
from installs that do not have the feature; installs that do have it keep it.

That is not an accident of my cell. After D8-01 is fixed, `action == "none"` is
the *normal* branch — advice fires only on a low tank with a cheap night, or a
full tank with an expensive next day. So a wood-ready install will publish `None`
most of the time no matter what, and the remaining question — should "nothing to
advise right now" render as Unavailable or as Unknown? — is a UX preference. The
sibling answers the analogous question with `False`, not with unavailable.

### Severity by consequence

- Both entities are added **unconditionally** (flat lists at `sensor.py:271` and
  `binary_sensor.py:50`), so the finder's "every install" is correct.
- The consequence is that one `EntityCategory.DIAGNOSTIC` row among 74 reads
  "Unknown" instead of "Unavailable". No cost, no control action, no safety
  impact, and it is weak evidence of breakage to a user troubleshooting — the
  integration already ships `InputHealthBinarySensor` for that job.
- The defect is **entirely downstream of D8-01**: fix D8-01 and the sensor speaks
  on the installs that have the feature.

A cosmetic diagnostic-category presentation issue, fully dependent on another
finding, whose named one-line countermeasure does not fully remove it. **`low`.**

---

## 4. D8-03 — family splits in the alphabetical sort

**Vote: `verify`, severity `low`.** The count is what it says. One supporting
sub-claim does not survive my definition, and the interpretation is a preference,
which the finder itself says.

### My number and my metric definition

**`trailing_noun_splits = 26`** over `trailing_noun_groups = 14`. Metric: a
family is the **last word** of an entity's English display name, lower-cased,
with any parenthesised qualifier and punctuation stripped; groups of two or more
count; the number is the sum over groups of (maximal contiguous runs in the
alphabetical display-name sort − 1). Nothing is hand-picked, so nothing can be
gerrymandered.

**Null control: `leading_word_splits = 0`** over 13 first-word groups — as an
alphabetical sort requires, and confirming the run-counter itself is sound.

Same worst offenders as the finder: `temperature` 8 entities in 8 runs, `cost`
6 in 6, `advisor` 4 in 4.

### Attack 1 — arithmetic

`finder_families_recomputed = 36`, in independent code, with every per-family
figure matching the finder's stderr exactly. The count reproduces.

### Attack 2 — is `FAMILIES` gerrymandered to produce 36?

Partly. `finder_single_keyword = 23`: cutting every multi-keyword bundle to its
first keyword drops the total 36 → 23, so **13 of the 36 (36 %) come from the
bundling choices**. The largest offender is `tariff_peak`, whose bundle is
`("peak", "headroom", "contract", "price", "savings")` — five different topics
in one "family" — contributing 4 → 0. `learning_accuracy` 2 → 0, `away` 1 → 0,
`dhw` 1 → 0, `optimization` 5 → 3, `advisor` 5 → 3, `plan` 3 → 2.
`finder_family_leave_one_out_max = 7` (`temperature`), 19 % of the total from one
family.

**So the exact figure 36 is materially list-dependent and should not be quoted as
a property of the tree.** The *phenomenon* is not list-dependent: it reproduces
at 26 under a partition nobody chose, with the same shape and the same worst
offenders. The finding survives; the number needs its definition quoted with it,
which the harness header does.

### Attack 3 — is it even the sort Home Assistant uses? (the attack fails)

Home Assistant's device page does not render one alphabetical list: it buckets
entities into Controls / Sensors / Diagnostic / Configuration and sorts by name
**inside** each bucket, so a family straddling two sections cannot be contiguous
however it is named. Recomputed under that order — the bucket read from the
`_attr_entity_category` class attribute, because `ent.entity_category` would put
all 74 in one bucket and measure nothing:

| metric | one alphabetical list | device-page order |
|---|---|---|
| mine (`trailing_noun_splits`) | 26 | **24** |
| the finder's (`family_splits`) | 36 | **38** |

The claim is order-robust: ±2 either way. This attack fails.

### Attack 4 — the "not an artefact of English" sub-claim is refuted

The finder writes: "Swedish scatters the same total differently (DHW 1 → 3,
temperature 7 → 4), so this is not an artefact of English."

Under a mechanical trailing-noun partition, **Swedish is 8 against English's 26**
(`trailing_noun_splits_sv = 8`). Swedish compounds the noun into the word —
"Utomhustemperatur" — so there is no trailing-noun family to scatter in the first
place. The finder's Swedish 36 comes from its keyword list matching *substrings
inside compounds*, which measures a different phenomenon from a multi-word
trailing noun. **The English-artefact defence does not hold** under a definition
that does not use substring matching; the scattering is substantially a property
of English multi-word naming.

This does not change the headline number, the severity, or the fact that the
English list scatters. It removes one supporting argument.

### Attack 5 — perturbation

`--perturb prefix-one` prepends `"Zz "` to one member of the largest
currently-contiguous trailing-noun group (at baseline `sensor.ecl110_displace`,
"ECL110 Displace"), sending it to the end of the alphabet without changing its
last word, so its family membership is untouched and only its position moves.
`trailing_noun_splits` **26 → 27**, up by exactly 1; `leading_word_splits`
unmoved at 0.

### Defect or preference? Plainly

**Mostly a preference; a narrow slice is a defect.**

An alphabetical sort clustering by leading token is a property of alphabetical
sorting, not of this integration. Home Assistant's own naming guidance runs the
other way: an entity name is the *measurement*, with the device name prepended by
the frontend, which is exactly what a trailing noun produces. Renaming ~36
entities to lead with a family noun would fight that guidance and would break
every dashboard, automation and recorder history that names them — a large,
user-visible cost for a browsing convenience. I would not call that a defect.

The narrow slice I *would* call a defect, because it is internal inconsistency
with no migration cost to speak of:

- `case_style_minority = 6` (reproduced exactly) — six sentence-case display
  names against 68 in Title Case, in one file, with no rule distinguishing them.
- `key_not_slug_of_name = 15` (reproduced exactly) — the `translation_key` is not
  the slug of the display name, so the id order and the name order disagree about
  where an entity lives (`rank_moves_ge_5 = 33`). Changing a `translation_key`
  changes the `entity_id`, so this one is *not* free either, and is worth fixing
  only for entities added in the future.

As the finder says, this is an owner decision before it is a diff. `low`,
hygiene: agreed.

---

## 5. Exposure

Nothing beyond this tree. No `gh`, no GitHub, no other verifier's output, no
audit register (`docs/audit-*.md` is absent here), no round-1 or round-2
findings. `README.md` and `docs/plan-2026-09-open-issues.md` were read only to
establish whether the wood advisor is a documented, shipped feature, which bears
on D8-01's severity. `tests/features.py`, `tests/entities.py` and
`tests/golden/coord_*.json` were read to name the test gap and its mutation. No
file outside `tools/audit/round3/D8/verify-1/` was written.
