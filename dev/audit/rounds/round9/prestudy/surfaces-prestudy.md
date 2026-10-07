# Pre-study: logic consolidation of the HA surfaces — scoping report

tvofi, 2026-09-28. Read-only pre-study. All measurements at `origin/main` = `31394964` (`Merge pull request #1734`), taken in a detached worktree (`/Users/timmalmstrom/r9scratch/wt-main`, removed after this report). Every count below comes from a command run at that tree; file:line cites are at that baseline. NOT merging platform files (already ruled unsound) — this scopes merging the duplicated **decisions** the thin platform layers carry.

---

## 1. The surface modules

`PLATFORM_LIST` (`__init__.py:126-133`): sensor, binary_sensor, button, climate, switch, datetime — six platforms. `const.py:10` mirrors it (`PLATFORMS`). Diagnostics deliberately excluded (`__init__.py:134-140`).

| file | lines | entity classes (count) | notes |
|---|---|---|---|
| `config_flow.py` | 3940 | ConfigFlow 810 LOC, OptionsFlow 880 LOC (`structure.py`) | **out of scope** — see §5 |
| `sensor.py` | 2834 | 1 base + 3 mixins + **55 sensor classes** (`grep '^class'`) | the fat one |
| `services.py` | 1058 | 13 service handlers | **out of scope** — see §5 |
| `climate.py` | 372 | 1 class (`:74`) | |
| `binary_sensor.py` | 350 | 1 base (`:65`) + 6 classes | |
| `entity.py` | 257 | `HeatPumpOptimizerEntity` (`:91`), `ConfiguredInputMixin` (`:200`), `DHWEntityMixin` (`:222`) + 4 helpers | **the seed** |
| `switch.py` | 198 | 4 classes | no base class — each hand-rolls |
| `button.py` | 196 | 1 base (`:60`) + 4 classes | |
| `datetime.py` | 49 | 1 class | |

Import graph note: `entity.py` imports **nothing from the package** (only stdlib + `homeassistant.helpers`), and takes the coordinator as `Any` (`entity.py:91-141`). It is already in 10+ measured closures (`tests/closures.json`: entities.py, finite_boundary.py, env_drift.py, features.py, golden.py, doc_claims.py, structure.py, deployment_shape.py, typing_ruler.py, config_flow_steps.py, plus card.mjs/card_drift.mjs).

## 2. Duplication, decision-class by decision-class

### (a) Availability gating — 18 implementations of one shape

18 `available` overrides: `entity.py:218,252`; `sensor.py:182,332,365,1632,1936,1998,2260,2312,2369,2414,2518,2574` (13); `binary_sensor.py:334`; `button.py:89,146`; `climate.py:127`. Every one is the same rule — `super().available and <one payload fact>` — differing only in the fact. Two real structural facts sit above them and are already shared: `CoordinatorEntity.available` (freshness) and the two mixins (`entity.py:200-257`).

The **divergence** inside this class is the round-9 substance, not the boilerplate: the P2 S1 sweep names `D8-s3-61` (`sensor.py`, Valve Target Recommendation: "disabled where a mixing valve is set, and **available-but-unknown** where none is") — i.e. the 18 sites disagree on *unavailable vs unknown* as the gated state. `climate.py:127-139` carries the A3(e) gate (unavailable until the indoor thermometer has read), with its rationale in a 6-line docstring — a decision no sibling shares.

Consolidation is real but shallow: a declarative gate (`_gated_on` / a helper `available_and(fact)`) collapses 18 bodies to 18 one-liners. **~55 lines → ~25.** The unknown-vs-unavailable rule cannot ride this PR alone — it needs the canonical rule named first (ties to F1.11's predicate registry).

### (b) Naming / identity pinning — the fattest clean win (9 sites, 5 copied comments)

One decision — "`unique_id` = `entry_id_key`; `_attr_translation_key` = key; `entity_id` pinned to `<platform>.heat_pump_optimizer_<translation_key>`" — is hand-rolled at **9 constructor sites**:

- `sensor.py:287-309` (base, covers 55 classes), `binary_sensor.py:72-85` (base), `button.py:68-77` (base)
- `switch.py:63-70, 118-126, 155-158, 181-186` (4 explicit, no base)
- `datetime.py:33-39`, `climate.py:105-110`

The entity-id-pinning rationale comment ("integration suggested-object-id mechanism… Swedish native entity ids would derive *translated* object ids…", `sensor.py:296-304`) is **copied verbatim 5×** (`grep` count: sensor, binary_sensor, switch, button, climate — 1 each). #1668's class (entity-family-name-sort-split, CLOSED, fix staged in `carry-1668.json`) is exactly a naming-table decision: families lead-token rule lives in `strings.json` + `translations/{en,sv}.json` and is re-derived per family. A single identity core gives that rule one seam to land on and one place to lint.

Consolidation: `pin_identity(entry, key, translation_key=None)` (or base-`__init__` args) in `entity.py`. **~75 lines (incl. comments) → ~20.**

### (c) Translation-key / strings resolution — already consolidated

No per-platform string reads exist: every entity resolves its name through `_attr_translation_key` → `strings.json`/`translations/*.json` (`entity.py:91-99` documents the contract; `climate.py:82-86` documents the device-named-entity exception). **Nothing to merge.** The only finding here is that the resolution rule is documented in a docstring, not enforced anywhere — F10.4 (I5 barrier) territory, not this item.

### (d) Config reads of one fact — largely fixed already; one seam left

- The P2 config class is **already canonical on the entity side**: `_dhw_enabled_from_config` (`thermal_model.py:1096-1101`) → `has_hot_water` (`entity.py:179-191`, "the one answer every reader takes", incl. `boost.py:141`) → `DHWEntityMixin`/`ConfiguredInputMixin` (`entity.py:200-257`). The #1542/#1527/#1398 fixes landed the mixins; the S1 sweep's D14-s2-01 instance lives in `config_flow.py`, not the platforms.
- Residual seam: `config_flow.py:412` imports the **private** `_dhw_enabled_from_config` across modules — a naming smell, one-line fix (expose it), but it belongs to the config_flow file this study excludes.
- Merged-config read `{**entry.data, **entry.options}` at **6 sites**: `services.py:657,687,784`; `coordinator.py:1905`; `__init__.py:370`; `climate.py:106`; `binary_sensor.py:179`. Surface-reachable sites are 2; a `merged_config(entry)` helper is worth ~8 lines and is safe.

### (e) device_class / state_class / units — per-platform rendering, stays

4 `_attr_device_class` in `binary_sensor.py:99,137,172,265`; 153 `state_class`/unit/`suggested_` lines in `sensor.py`. These are per-entity facts, not shared decisions. **No merge.**

### (f) Registration (`async_setup_entry`) — boilerplate only

6 setup functions, ~10 lines each (`sensor.py:189-274` builds the 61-entity list; `datetime.py:17-22` is one line of content). The entity lists are content; the boilerplate is HA convention. **No merge** — a decorator would fight `tests/entities.py`'s `collect()` over `PLATFORM_LIST` (`entities.py:526-539, 3771-3796, 10343, 14074-14079`) for no line gain.

### (g) `_data()` access — mechanical consistency

`binary_sensor.py:84-85` defines `_data()`; `sensor.py` spells `self.coordinator.data or {}` **67×** (grep), `climate.py` 3×. Moving `_data()` onto `HeatPumpOptimizerEntity` is neutral-to-slightly-negative on lines but removes the last per-platform accessor divergence. Optional rider.

### Round-9 cross-reference (findings already touching these files)

P2 S1 instances (#1644, baseline `1936d5ca`) on surfaces: `sensor.py` D8-s1-02, D8-s3-61; `entity.py` D8-s1-03; `climate.py` D8-s2-02, D8-s2-03; `button.py` D10-s1-02; `config_flow.py` D10-s1-01, D12-s3-01, D14-s2-01. Plus #1668 (naming families, fix staged, `carry-1668.json`). The class with the most round-9 weight on the *shared* decisions is (b) naming (via #1668) with (a) availability second (via D8-s3-61).

## 3. Target shape

**Extend `entity.py`; do not create `surfaces_core.py`.** Reasons:

1. `entity.py` is already the shared base, package-import-free (no closure-cycle risk), and already in every surfaces closure — a new file buys a new tracked-file classification (`tests/entities.py` refuses unclassified files; CLAUDE.md rule 4-side condition) and re-derivation noise for zero architectural gain.
2. The ratchet has **no per-file LOC budget** for `entity.py` (all 25 metrics checked: none tracks it; only `coordinator_loc`, `const_modules_over_50` etc. are per-file). Its 257 lines can absorb ~45 moved lines without touching any budget.
3. The mega-module lesson applies to *growing* a module that accretes decisions, not to consolidating ~45 lines of shared identity code next to the two mixins that already live there.

What moves into `entity.py`: `pin_identity` (class b), a `merged_config` helper (class d), `_data()` (class g), and — optionally, second PR — the availability gate helper (class a). What stays per-platform: every `native_value`/`is_on`/`extra_state_attributes` body, device_class/state_class/units (e), registration lists (f), and all of `config_flow.py`/`services.py`.

**Migration order: (b) first** — most sites, zero behavior change, unblocks the #1668 family rule with one seam, and no round-9 finding resists it. (a) second, but only after F1.11's canonical-predicate registry lands, and carrying the unknown-vs-unavailable rule (D8-s3-61) with it — without that payload it is line-shuffling, and landing it before the barrier would move the AST seam the barrier lints.

## 4. Cost

**Production lines** (measured site counts × observed line spans, not estimates):

- (b): ~75 deleted (9 blocks of 5-15 lines incl. the 5×8-line comment), ~22 added → **net ≈ -53**
- (d) merged-config: 6 sites, ~8 lines → **net ≈ -5**
- (g) `_data()`: ~0
- (a) availability (deferred): 18 sites, ~55 → ~28 → **net ≈ -27**
- Total in-scope-for-endgame (b+d+g): **~net -60 production lines**; with (a): ~net -87.

**Test impact — the closures give no per-file relief.** Every surface file sits in the same `tests/entities.py` closure (`tests/closures.json`), so touching `entity.py` runs entities.py, finite_boundary, env_drift, features, golden, doc_claims, structure, deployment_shape, typing_ruler, config_flow_steps — the largest surfaces closure, regardless of how small the diff is. The **a3 roster's `collect()` over `PLATFORM_LIST` survives unchanged**: no platform is added, renamed or merged; identity pinning is internal to each entity's `__init__`, invisible to `collect()` (`entities.py:14074-14079`'s entity_id-unique rule still holds — the pin is the same rule, moved).

**Instruments needing work:**

- **Closures**: no re-derive — `entity.py` and all touched files are already in their closures; no new file, no new import edge that escapes a measured closure.
- **Structure budgets**: *no metric moves, and none needs to.* The duplication detector (`structure.py`, ≥10 normalized lines across functions) currently reports 14 blocks, all in config_flow/coordinator/optimizer/tariff/thermal_model — **none in the surfaces**; these dup blocks are each <10 normalized lines, so the detector never saw them and won't miss them. `duplication_blocks` stays 14 = budget (zero headroom, unchanged). No re-record, no budget raise, no owner approval needed.
- **Mutation ledger**: 21 `killed_by` pins on the touched files (`entity.py` 9, `binary_sensor.py` 9, `button.py` 3). The entity.py pins sit on exactly the symbols class (a) would touch (`has_hot_water`, `input_configured`, `ConfiguredInputMixin.available`, `DHWEntityMixin.entity_registry_enabled_default`) — class (b) leaves them alone. Re-keying is the documented `--normalize` path; run the ledger + `brief_lint` locally before push.
- **Line-shift pins**: `mutation_budgets.json` pins `climate.py:144 BOOLOP` — any climate.py edit above line 144 breaks it; the class (b)/(d) edits in `climate.py:105-110` sit above it. Re-pin in the same PR.

**Lane serialization — the real cost.** Round-9 F-lanes on or reading these files (from the carry files):

| lane | files | interaction |
|---|---|---|
| F8.1/F8.3 + F10.4 (`carry-1645.json`) | reads `config_flow.py` + `services.py` **directly** (doc_claims arms extract facts from the code) | any refactor of those files moves the doc-claims anchors. **Hard exclusion of config_flow/services from this item.** |
| #1668 fix (`carry-1668.json`) | `strings.json`, `translations/*`, `sensor.py`, `button.py` families | merge-order: land the identity core **after** or rebase onto it; both edit sensor/button |
| F1.11 P2 barrier (`carry-1644.json`) | new lint over canonical predicates; instances in `config_flow.py` | land class (a) after the barrier registry exists, keyed into it |
| F4.1 state-stamp (`carry-1651.json`) | coordinator/store | no surface overlap |
| F3.1-3.3 stores (`carry-1647.json`) | stores | no overlap |

**Timing: not round 9.** The F-lanes above are still draining; a surfaces PR now would collide with at least two of them at the merge gate and force a re-base of the #1668 fix or the doc-claims barrier.

## 5. Verdict: FEASIBLE AS ENDGAME ITEM — small, one PR, not round 9

**FEASIBLE WITH CAVEATS** if class (a) is pulled into scope; clean **FEASIBLE** for (b)+(d)+(g) alone.

Concrete win: one seam for the entity identity/naming decision (9 sites, 5 copied rationale comments → 1), which is the precondition for #1668's family-lead-token rule to be lintable rather than convention; ~60 net production lines off the platforms; the last per-platform accessor divergence (`_data()`) gone. Concrete risk on the same coin: entity_id pinning is a **registry-compat-sensitive** decision (the Swedish-native-entity-id trap the comment documents) — moving it touches every entity's constructor on every platform, and a mistake there is invisible until a fresh install in a translated HA renames the dashboard card's id-suffix contract.

Concretely NOT worth it: classes (c), (e), (f) — already consolidated, per-entity rendering, or HA-convention boilerplate. Concretely excluded: `config_flow.py` and `services.py` — the F8.x/F10.4 doc-claims arms read facts straight out of them, and their P2 instances (D10-s1-01, D12-s3-01, D14-s2-01) are behavior fixes already routed to F1.11/F5.1, not dedup.

**Recommended shape**: one PR at endgame (after the round-9 F-lanes drain), scope = class (b) identity core + `merged_config` + `_data()`; a second optional PR later for class (a) availability, gated on F1.11's registry landing and carrying the unknown-vs-unavailable canonical rule. No budget raise, no closure re-derive, no golden/claim touch; expect the full surfaces closure (~10 scripts) in the scoped gate and a `climate.py:144` mutation re-pin in the same PR.
