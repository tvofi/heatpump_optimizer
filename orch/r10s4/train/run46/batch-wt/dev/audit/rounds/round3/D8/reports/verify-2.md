# D8 — verifier 2 of 2, stance refute-first, line of attack CONSEQUENCE

Baseline `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1`, in the verifier tree at
`.../audit-r3/verify/D8-2` (a `git archive` export: no `.git`, so every
comparison here is against the tree as given, never against a ref).
Box: 8-core Apple M1, 8 GB, python 3.11.5, numpy 2.4.6, scipy 1.17.1.
Five BLAS thread variables pinned before numpy on every run; `thread_factor`
was `1.000` on every run without exception.

**`load1` moved between 5.68 and 101.8 while these ran, and it does not
matter: every number in this report is a count, a set comparison or a ratio of
counts.** No `tests/stress.py`, no `./tests/run.sh`, no gate lock, no `gh`,
no other verifier's output, no register.

My own instruments, both under `tools/audit/round3/D8/verify-2/`:
`v2_consequence.py` (what a user loses, all three findings) and
`v2_horizon_spy.py` (what `night_advice` is actually handed in production).
Raw output: `v2_run.txt`, `v2_detail.txt`, `v2_shuffle.txt`,
`v2_horizon_spy_out.txt`; the finder's re-runs are `rerun_*.txt` and
`limit2_deadlist.txt`.

## 1. The finder's harnesses, re-run exactly as their headers say

Every number reproduced **exactly**. Nothing is outside tolerance because
nothing here has a tolerance.

| harness | expected in the header | I got | `load1` |
|---|---|---|---|
| `d8_wood_advisor.py` | `gate_combinations=6 gate_none_at_default_soc=4 gate_productive_at_0_5=0 arms=6 writers_of_wood_tank_soc=0 wood_fuel_ready=6 advice_available=6 advice_value_as_shipped=0` | identical, plus `advice_value_soc_low=3 advice_value_soc_high=0 cheap_wood_arms_value_soc_low=3` | 5.68 |
| `d8_ordering.py` | `entities=74 family_splits=36 family_splits_entity_id=36 family_splits_sv=36 rank_moves_ge_5=33 key_not_slug_of_name=15 case_style_minority=6 strings_vs_en=0 strings_vs_sv=0` | identical; per-family FAMILY lines identical, `temperature` at 7 | 5.75 |
| `d8_ordering.py --perturb split-ecl110` | 36 → 37, others unmoved | `family_splits_entity_id=37`, `family_splits=36`, `family_splits_sv=36`, `case_style_minority=6` | 24.17 |
| `d8_matrix.py` (23 cells, 46 solves) | all 18 RESULTs | all identical, including `dead_where_data_exists=1 unavailable_everywhere=8 available_but_unknown_everywhere=2 enabled_default_dead_first_hour=10 frozen_while_input_moved=9` and the six zeroes | 24.24, 147 s |
| `d8_matrix.py --limit 2 --perturb wood-gate` | `available_unknown_default_install` 2→1, `available_but_unknown_everywhere` 2→1 | exactly that (unperturbed `--limit 2` baseline re-taken in the same session: 2 and 2) | 23.84 |

`d8_timestamps.py` was not re-run: it carries no finding.

So the panel is not arguing about whether the numbers are real. It is arguing
about what they are worth. That is what I measured.

## 2. D8-01 — the wood night advisor

### 2.1 The finder's null control is genuine, and it is the interesting half

Asked of me directly, so measured directly, against the production symbol
`wood_fuel:night_advice` with the arms' own price series
(`v2_horizon_spy.py`, output in `v2_horizon_spy_out.txt`; steps are the
optimizer's 15-minute grid, so 48 of the 96 fall in the night window):

| wood price | SEK/kWh | night hours (18:00–06:00) in the horizon | of those, hours where wood beats pump heat | soc 0.2 | soc 0.5 | soc 0.9 |
|---|---|---|---|---|---|---|
| 900 SEK/m³ | 0.677 | 48 | **0** | none | none | skip¹ |
| 300 SEK/m³ | 0.226 | 48 | **48** | light | none | none |

¹ at a 14:00 cycle start; see §2.4.

The dear-wood arm is silent at `soc=0.2` because **zero** of its 48 night
steps have wood cheaper than pump heat — there is nothing to advise and
silence is the right answer. The cheap-wood arm has 48 of 48. So the 0 → 3
move under `wood_tank_soc=0.2` is the SOC gate opening on arms where a cheap
night genuinely exists, **not** "any injected value turns the sensor on". The
control holds. Confirmed.

### 2.2 The gate, measured exhaustively rather than at six points

The finder sampled 6 (price, soc) combinations. I swept all of them that
matter: 201 soc values across `[0, 1]` at 0.005, under both price regimes,
counting a value productive if **either** regime reaches `light` or `skip` —
the most generous possible reading.

```
RESULT advice_soc_window_pct=59.7      productive intervals [0.000,0.395] u [0.805,1.000]
RESULT advice_productive_at_0_5=0
```

59.7 % of the tank state-of-charge range produces advice. The one value the
tree can supply — the hard-coded `or 0.5` — sits in the 40.3 % dead band
between the two productive intervals. This is not an unlucky sample; it is the
whole gate, and the default is inside the only sub-interval that cannot speak.

### 2.3 Nothing can write the key — checked more widely than the finder did

The finder's census scans `custom_components/` and `tests/` only. Mine scans
the **whole tree** (README, docs, `.claude`, `.github`, `www`, everything but
the round-3 D8 directory), and separately enumerates the writable key set off
`config_flow:_OPTION_FIELDS` rather than by grepping:

```
RESULT soc_key_tree_mentions=1          (custom_components/heatpump_optimizer/wood_fuel.py:463, the read)
RESULT ui_writable_config_keys=175
RESULT soc_key_ui_writable=0
```

I also read the three `async_update_entry` call sites in `services.py`
(:629, :692, :840): each writes keys from a fixed whitelist
(`topology.ASSIGNABLE_KEYS`, a computed `updates` dict), none accepts a
caller-supplied key name. There is no back door. 175 keys the UI can write,
and `wood_tank_soc` is not one of them.

### 2.4 A correction to the finder, found by hooking the symbol

`v2_horizon_spy.py` wraps `night_advice` and records what a real coordinator
cycle hands it:

```
n_ts=96   first=2026-01-15 00:00   last=2026-01-15 23:45   days=1
```

Two things follow.

* **`advice_value_soc_high=0` is a clock artefact, not a product property.**
  The optimizer's horizon is 24 h (`optimizer.py:966`, `horizon_hours: float =
  24.0`), and `golden.START` is midnight, so all 96 steps fall on one calendar
  date and `expensive_next` — which needs `when.date() > now.date()` — can
  never be true. Re-freeze the same arm at 14:00 and `days=2`,
  `nextday_hours_pump_wins=56`, and the 900/`soc=0.9` arm returns **`skip`**.
  The finder reported that zero without noticing it belongs to the harness.
  It does not damage the claim (which rests on `soc=0.5` and on the 0 → 3
  move), but the judge should not read it as evidence the skip branch is dead.
* **The advertised horizon is wrong in both the code and the README.** The
  sensor docstring says "48 h light/skip advice" and `README.md:469` repeats
  it; the advisor sees 24 h. That belongs to D5/D6, not to me, and I am not
  filing it — recorded here so it propagates.

### 2.5 Consequence: what is actually lost

This was my assignment, so these are the numbers that decide my vote.

**Is the feature reachable at all?** Yes, and through ordinary UI. The wood
block is 13 fields in the options flow's `building` step
(`config_flow.py:1390-1403`), each carrying `when=wood_furnace_on`, and
`wood_furnace_on` is itself inferred from a wired tank probe, a DHW wood coil
or external heat (`wood_fuel.py:66-83`). A user with a wood furnace enables
it the way they enable anything else. So this is **not** a dead feature nobody
can reach; it is a feature that silently fails for **everyone** who reaches
it — which is the more serious of the two framings the panel was asked to
distinguish.

**Does its absence degrade anything else?** No. Building the same cheap-wood
arm twice, once as shipped and once with `wood_tank_soc=0.2` as the only
difference, and diffing all of `_build_data_dict()`:

```
RESULT payload_keys_moved_by_soc=1      (wood_fuel; solve_time_ms excluded as a wall-clock reading)
RESULT wood_night_advice_present_with_soc=1
RESULT night_advice_consumers=1
RESULT wood_view_live_keys=10
```

Exactly one published key moves. No plan, no cost, no setpoint, no control,
no statistic. `night_advice` has exactly one consumer in the whole package —
`WoodBurnAdvisorSensor` — so nothing else is silently degraded by its absence,
and the other 10 live keys of the `wood_fuel` view (ready, cheaper,
`cheaper_hour_count`, slots, …) work as shipped. The loss is exactly one
advisory string.

**But it is a documented loss, and the suite is complicit.** `README.md:469`
ships the row "Wood-burn night advisor | — | 48 h light/skip advice when the
wood furnace is on". And `tests/features.py:24835-24868` exercises
`night_advice` directly at `tank_soc=0.2` and `tank_soc=0.9` — the two values
production can never supply — and passes. The unit is green while the product
is dead: this is the "a test that re-implements a production formula pins
nothing" shape, one level up.

**Vote: `verify`, severity `medium` (unchanged).** A documented feature that
has never run on any install that ever existed, for every user who wired the
hardware, is medium. It is not high: nothing publishes a wrong number, no
money moves, no control acts.

## 3. D8-02 — Unknown where the sibling says Unavailable

### 3.1 What Home Assistant renders — the honest limit of what I can execute

I cannot run Home Assistant here, and I will not claim I did. Two in-tree
sources bear on it, one of them not the integration's own opinion:

* `tests/hastub/homeassistant/components/sensor.py:65-115` is a transcription
  of HA 2025.2.0's `SensorEntity.state`, and its docstring states that a
  `None` native value short-circuits to `STATE_UNKNOWN`. The stub itself
  returns bare `None`, so the string is not executable here — the transcription
  is the evidence, not a run.
* `sensor.py:388-407`, `_WaitsForEvidenceMixin`'s own docstring, says it in the
  maintainers' words: Home Assistant renders `None` as "Unknown", "which is the
  same thing it renders for a sensor whose integration has thrown", and
  "Unavailable is the state that means 'nothing to report'".

So the rendering claim is corroborated, not executed. Recorded as such.

### 3.2 The sibling comparison, and whether the omission is systematic

On the same cell, same payload, the two entities of the same feature
(`limit2_deadlist.txt`):

```
FIRSTHOUR_DEAD wood_cheaper       (WoodCheaperBinarySensor) available=False
FIRSTHOUR_DEAD wood_burn_advisor  (WoodBurnAdvisorSensor)   available=True
```

`WoodCheaperBinarySensor` gates on `fuel.get("ready")` in four lines
(`binary_sensor.py:202-205`). `WoodBurnAdvisorSensor` (`sensor.py:2604-2634`)
declares only `_attr_entity_category` and is added unconditionally at
`sensor.py:271`, on every install, wood furnace or not.

Is the omission systematic? I walked the MRO of all 74 entities and asked
which class defines `available`:

```
RESULT entities_total=74
RESULT entities_with_own_available=32      (19 via a mixin, 13 hand-rolled)
RESULT entities_ungated=42
```

Owners, from `v2_detail.txt`: `_MeasuredTemperatureMixin` 6, `_DHWEntityMixin`
6, `_WaitsForEvidenceMixin` 5, `_MeasuredStoreMixin` 2, and 13 one-off
properties. **`_WaitsForEvidenceMixin` is not the common mechanism** — it
covers 5 of 32 — and of the 8 correctly-unavailable siblings the finder counts,
3 come from it and 5 are hand-rolled. There is no base-class default:
`available` falls through to `CoordinatorEntity`, so **42 of 74 entities are
ungated and a new sensor joins that 42 unless its author remembers**. The
answer to "would a new sensor be added the same way" is yes, and there is a
precedent: `tests/entities.py:1863-2219` records a **round-2** audit finding,
also numbered D8-01, on exactly this principle ("Availability is the mechanism"),
whose countermeasure was a hard-coded roster of 13 named entities
(`_D801_IN_SCOPE`) rather than a rule. `WoodBurnAdvisorSensor` (#702) was added
after, is not on that list, and nothing noticed. The suite's 51 `.available`
mentions in `entities.py` are all per-entity assertions by name; none is a rule
of the form "an enabled-by-default entity that can publish `None` must gate".

### 3.3 Consequence, and why I weaken it

The round-2 precedent is also what bounds this one. There, an ungated entity
published **270 litres of shower water** derived from a thermometer nobody was
reading — a plausible wrong number, carrying a `state_class`, so Home Assistant
wrote it into long-term statistics. Here the entity publishes `None`. It
carries no `state_class` and no `device_class` (the class body sets only
`_attr_entity_category = DIAGNOSTIC`), so nothing enters statistics, nothing is
recorded, no reading is wrong. The user's loss is one permanently-Unknown row
in the collapsed Diagnostic section of the device page — about hardware most
installs do not own.

It is also half-downstream of D8-01: fix the SOC writer and the advisor speaks
on every install that has the furnace, leaving Unknown only where the feature
is off, which is precisely where the gate belongs. And the finder's own second
member, `AwayReturnDateTime`, is named in its report as arguably legitimate —
so the metric's population is 1 real case, not 2.

**Vote: `weaken` to `low`.** The defect is real and reproduced (2 → 1 under
`--perturb wood-gate`, both metrics, at `--limit 2` with the unperturbed
baseline re-taken in the same session), the omission is systematic, and the fix
is four lines the sibling already has. But a cosmetic Unknown on a diagnostic
row, with no wrong value and no statistics written, does not carry the same
weight as the round-2 case that established the principle. `low`, with the
systematic half worth more than the instance: the countermeasure that would
actually pay is the rule the round-2 fix chose not to build.

## 4. D8-03 — the alphabetical scatter

### 4.1 Are the three 36s the same 36? No — and the metric is not insensitive

Position indices are not comparable across three different orders, so I
identified a split by the **partition it induces on the family** — which
members share a run — which is order-independent:

```
RESULT families_measured=16
RESULT families_partitioned_alike_en_id=12
RESULT families_partitioned_alike_en_sv=7
RESULT runs_en=52   runs_shared_en_id=44   runs_shared_en_sv=33   runs_shared_by_all_sorts=28
```

The English and entity-id sorts agree on 12 of 16 families (expected: an
`entity_id` is usually the slug of the name) and differ on 4 — `optimization`
5/4, `away` 1/2, `wood` 0/1, `advisor` 5/4, which happen to cancel. The Swedish
sort agrees on only 7 of 16 and differs on 9; 33 of 52 runs survive into it.
**Three different distributions that coincidentally sum to the same total.**
The suspicion is answered and the finding survives it: the metric does respond
to which sort it is applied to; only the aggregate hides that. The aggregate is
the number the report leads with, which is worth saying out loud.

A note on method the judge should have: family membership is matched on the
**English** display name for all three sorts, so `family_splits_sv` is "how the
English-defined family scatters under Swedish names", not "the Swedish
family". Defensible — a family is semantic, not lexical — but it is not what
the metric name suggests.

### 4.2 The null control the finder did not run

5000 uniform random permutations of the same 74 entities, same family sets:

```
RESULT splits_random_mean=58.59   splits_random_sd=2.29   splits_random_min=50
RESULT splits_fraction_of_random=0.614
```

36 is **9.9 standard deviations below** what a list with no naming convention
at all would score, and 61 % of it. The floor is 0. So the honest reading of
"36 splits" is not "the entity list is chaos" — it is "the convention that
exists buys about 39 % of the available grouping and stops". That reframes the
rhetoric without touching the observation.

The control that the metric reads the order and not the word lists:
`--perturb shuffle-order` replaces the English alphabetical order with a
seeded permutation of the same roster, leaving membership untouched —
`family_splits_en` 36 → **55** (inside 1.6 sd of 58.59) while
`family_splits_id` stays at 36 and `interlopers_total` goes 413 → 734.

### 4.3 Consequence: measured under the order a user actually sees

A flat sort of all 74 entities is not what Home Assistant renders. A device
page renders four sections — Controls, Sensors, Configuration, Diagnostic —
each name-sorted. I modelled that (stated as a model, not executed HA:
`entity_category` decides Configuration/Diagnostic, otherwise
sensor/binary\_sensor go to Sensors and the rest to Controls):

```
RESULT family_splits_device_page=38
```

It goes **up** by 2: five families gain a split at a section boundary (`dhw`,
`away`, `wood`, `learning_accuracy`, `tariff_peak`, +1 each) and two lose
(`temperature` −1, `advisor` −2), netting +2. So
the finding is not an artefact of measuring a flat list; the user's real view
is marginally worse than the finder's number.

And the cost a split count does not carry — the unrelated rows you scroll past
to see a whole family, `(last − first + 1) − members`:

```
RESULT interlopers_total=413
RESULT interlopers_worst=cost=61
```

Worst families: `cost` 61 (6 entities spanning 67 of 74 rows), `advisor` 60,
`temperature` 57, `energy` 52, `plan` 45. To see all six cost entities you
scroll past 61 rows that are not cost entities. That is the consequence, and
it is real — though it is also the consequence a search box removes, and every
surface that lists these entities has one.

### 4.4 Is renaming a `translation_key` free? No — verified

The constraint the panel asked about, confirmed from source:

* `sensor.py:323,333` — `unique_id` is built from `key`, `entity_id` from
  `translation_key`, and the comment says the assignment "is used verbatim at
  first registration and ignored for entities that already exist". So a rename
  keeps history (good) and gives **new installs a different `entity_id` from
  existing ones** (bad): the installed base splits into two id conventions.
* The card resolves the plan and solar sensors by a `plan_kind` attribute
  marker first (`heatpump-optimizer-card.js:3950`), so those survive a rename.
  The headline stat sensors do not: `statEntity(suffix)` scans by
  `id.endsWith(suffix)` and the card's own comment calls the suffix
  "the discovery contract".

```
RESULT card_stat_suffixes_no_marker=4    (_monthly_savings, _optimization_score, _plan_narrative, _predicted_savings)
RESULT card_plan_marker_fallbacks=1
RESULT rename_pins_outside_package=27
RESULT readme_entity_ids=0
```

27 distinct entity ids are pinned outside the package, in `docs/` and
`tests/`. So the cheap fix — rename keys so the ids group — is blocked for at
least those four sensors and costs a split installed base for the rest. The
fix that *is* available is renaming **display names only** (the translations
are already per-language files, and `strings_vs_en`/`strings_vs_sv` are both
0), which moves `family_splits` and leaves `family_splits_entity_id`,
`unique_id`, the card and the 27 pins untouched.

### 4.5 One factual error in the finder's surrounding table

Not part of D8-03's number, but it sits in the same report and a judge should
know. The non-findings table claims "6 card suffixes + 6 README ids, all
present, none in the disabled roster". `README.md` contains **zero** entity
ids: `readme_entity_ids=0`, and the strings that look like them
(`README.md:238-247`) are `.storage` keys, `heatpump_optimizer_<entry id>_…`,
not entity ids. The README documents entities by display name. The card half
of that row is right (4 stat suffixes + the plan/solar trio). It does not
touch the three findings; it is one unexecuted side-claim in a report whose
executed numbers all reproduced.

**Vote: `verify`, severity `low` (unchanged).** Every number reproduced, the
perturbation reproduced exactly, my three attacks (same-36, flat-sort artefact,
fixability) all failed to break it, and my own metric — 413 interlopers, worst
family spanning 67 of 74 rows — corroborates a real cost. Recorded against it:
36 is 9.9 sd better than random, so the finding is "a convention applied to
half the families", exactly as its title says, and not a claim of chaos.

## 5. Attacks run, and what each returned

| attack (verifier contract §3) | outcome |
|---|---|
| taken under contention? | Irrelevant by construction: every number is a count or a set comparison. `thread_factor=1.000` on every run; `load1` 5.68 → 101.8 across the session and no number moved. The only wall figures (147 s, 11.8 s) are labelled provisional and are not metrics. |
| wrong gate mode? | No gate mode involved; no finding here is a suite-gap claim, so the `env_drift.py --all` trap does not apply. |
| aggregate a grid artefact? | D8-02: re-took the `--limit 2` unperturbed baseline in my own session before comparing, so the 2 → 1 is not against a 23-cell number. D8-03: dropped the flat sort entirely and re-aggregated under the device-page order (38) and under 5000 random orders (58.59 ± 2.29). D8-01: replaced 6 sampled cells with a 201-point exhaustive sweep. |
| null control missing or failing? | D8-01's control is genuine and I re-measured its mechanism (0 of 48 night steps favour wood at 900 SEK/m³ against 48 of 48 at 300). D8-03 had **no** null control; I supplied one (random order) and one perturbation control (`--perturb shuffle-order`, 36 → 55). |
| reachable in real HA or only through the stub? | D8-01: the config path is the real options flow, and the perturbation is a config change, not a tree edit — reachable. D8-02: the *rendering* half is **not** executable here; corroborated from hastub's transcription of HA 2025.2.0 and the integration's own mixin docstring, and reported as corroboration rather than measurement. D8-03: `entity_id` is pinned by production code (`sensor.py:333`), not by the stub. One stub artefact found and reported: the finder's `advice_value_soc_high=0` is an artefact of `golden.START` being midnight (§2.4). |
| severity earned by consequence? | D8-01 yes (documented feature, dead for every user who has the hardware; loss bounded at one payload key). D8-02 **no** at medium (a `None` on a diagnostic row with no `state_class`, nothing recorded, half-downstream of D8-01) → `low`. D8-03 yes at low. |
| test-gap claim (contract §4)? | None of the three is one, so no killing mutation is owed. Recorded anyway, because it bears on D8-01's consequence: `tests/features.py:24835-24868` pins `night_advice` at `tank_soc` 0.2 and 0.9, values production cannot supply, so the unit is green while the wired path is dead. |

## 6. Propagated, not filed

Per `finding-propagation.md`, these belong to other stages and are recorded
here rather than turned into issues:

* **D5/D6** — the sensor docstring (`sensor.py:2605`) and `README.md:469` both
  promise "48 h" advice; the advisor is handed the optimizer's 24 h horizon
  (`optimizer.py:966`), measured at `n_ts=96`.
* **D3** — `tests/entities.py` has 51 per-entity `.available` assertions and no
  rule; the round-2 D8-01 countermeasure is an enumerated roster
  (`_D801_IN_SCOPE`, 13 names) that a sensor added later joined without
  noticing. That is the shape `defect-root-cause.md` calls a check written from
  one failure.
* **D6** — the finder's non-findings row "6 README ids" has no referent
  (§4.5).
