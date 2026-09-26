# Round 9, D14 seat s2: classes P2, P8, I4

Baseline `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1), worktree `/home/claude/audit-r9-D14-s2`,
box B8 (4 cores, 15 GB), CPython 3.14.0rc2 (`/home/claude/venv314`), node v22.22.2. Scope `D14-s2`:
every file, steps M1-M5, axis P2, P8, I4. All numbers are counts (contention-immune; seats s1 and s3
were running); the M5 barrier costs are wall timings, provisional. The machine-readable report is
`report.json` beside this file.

## Method

- M1: read `tools/audit/bugclasses.json`; P2, P8, I4 are `open`, detector null.
- M2: the seat's axis fixes the classes.
- M3: per class, a static seam rule (`--seams`) listing every seam in the package, plus a dynamic
  probe driving the named production symbols over a generated boundary grid. Each re-finds one
  listed instance at its pre-fix commit and moves under an in-memory one-line fix or
  re-introduction; the P2 rule also has a clean-fixture / re-introduction self-test.
- M4: one finding per class, below. M5: barrier proposals, costed by detector wall time.
- No production file was edited on disk: every perturbation recompiles a function, patches an
  attribute, or rewrites the card source string in memory.

## D14-s2-01 (P2, medium, bug): one configuration fact, three seams that re-derive it

Property: every decision about a presence-inferred configuration fact is made by its canonical
predicate (`two_zone_enabled` by `ThermalParameters.from_config`, `dhw_enabled` by
`_dhw_enabled_from_config`, `wood_furnace_on` by `wood_fuel.wood_furnace_on`).

Seam rule: `p2_facts.py --seams`. It extracts the proxy keys from the predicate bodies by AST and
lists every test-context read of them outside the predicate.

Command: `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D14/s2/p2_facts.py`

| seam | disagreeing cells | after perturbation |
|---|---|---|
| `config_flow._derive_preset` (config_flow.py:1125, `bool(current.get(CONF_UPPER_FLOOR_THERMAL_MASS))`) | 20 of 40 | 0 |
| `modbus_prefill._plant` via `infer` (modbus_prefill.py:212): offers a flow target `_prefill_errors` refuses, or misses one it would accept | 20 of 40 | 0 |
| `topology.describe_setup`: `wood.present` from `_wood_tank_shown` (topology.py:376) against `wood_furnace_on` | 2 of 21 | 0 |

- Grid: five `two_zone_mode` values (absent, auto, on, off, bogus) times eight zone-key presence
  patterns, one of them an upper mass of 0.0 (falsy but present).
- Null control: 0 on the 20 cells where upper-key presence and the canonical verdict coincide.
- Leave-one-out over the five modes: range 3 to 5; 15 with the most favourable mode dropped.
- Consequence: a `two_zone_mode=off` house whose zone keys survive in `entry.data` gets two-zone
  questionnaire physics written into a single-zone model (`house_thermal_mass` 0.267x the canonical
  preset's on the probe house; 3.75x under `two_zone_mode=on` with no upper-mass key). The GCHV
  pre-fill offers a flow write target its own save then refuses. The setup diagram draws a wood tank
  for a lone `valve_outlet_temp_entity` that the model does not run, and hides the one
  `dhw_wood_coil_enabled` turns on in the model.
- Positive control: `--seams --ref 3602b6ca^` lists 3 two-zone seams: the R7-D12-01 flow-target
  guard at config_flow.py:3400 plus the two above. At baseline there are 2.
- Self-test: clean fixture 0; one-line re-introduction 1.

Rule output at baseline, all 29 reads dispositioned:

| fact | reads | disposition |
|---|---|---|
| `two_zone_enabled` | 2 | both instances (above) |
| `wood_furnace_on` | 16 | `_wood_tank_shown` (topology.py:378-385, 6 reads) is one instance. Guarded: `coordinator._external_heat_config:3526` (ANDed with `wood_furnace_on`); `config_flow.async_step_building:3451/3453` (normalises the flag after `wood_furnace_on(merged)`); `ThermalParameters.from_config:968-976` (under `_on = wood_furnace_on(config)`). Not applicable: `quick_setup.stored_answers:144-148` (answer read-back) |
| `dhw_enabled` | 11 | all not applicable: probe presence (`legionella:351`, `coordinator._dhw_probe_temperature:9370`, `topology.rank_sensor_gaps:714`), a volume default (`sensor._gap_probe_terms:2726`), service data writes (`services:450/686/688/730`), the windows update (`coordinator:5245`), answer read-backs (`quick_setup:142-143`) |

Barrier: the seam rule as a `tests/entities.py` check with a disposition table for the guarded and
not-applicable reads, refusing any new decision-context proxy read. It shares entities.py's AST
parse; run alone it costs 1.30 s (provisional). A `two_zone_enabled(config)` helper beside
`_dhw_enabled_from_config` would give the seams a cheap call.

## D14-s2-02 (P8, medium, bug): a money figure's currency comes from the label source, never from the feed that denominates it

Property: every money label resolves through one function whose inputs include the currency the
number arrives in. A feed/instance mismatch is adopted or raised as a repair issue. No money unit is
a literal.

Seam rule: `p8_currency.py --seams` (42 sites): every `resolve_currency` call and `.currency` read,
every price-unit parse that drops the money code, every literal currency unit and untemplated
currency word in strings or translations, and every card resolver.

Command: `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D14/s2/p8_currency.py`

**A. Price feed to published unit.**
- Mechanism: `inputs.normalize_price_per_kwh` keeps `EUR/kWh`'s scale and drops `EUR`;
  `coordinator.currency` is `hass.config.currency`; `_audit_price_units` flags only an unparseable
  unit. So `CurrentPriceSensor` publishes `0.10` as `SEK/kWh` on an SEK instance.
- Measured: 12 cells (6 feed units x SEK/EUR instance), 8 mismatches, 0 flagged:
  `A_unflagged_mismatch=8`.
- Perturbation: `coordinator.resolve_currency` patched to return the feed's code gives 0.
- Null control: 0 on the 4 matching cells.
- Leave-one-out over the 6 feed units: range 1 to 2; 6 with the most favourable dropped.

**B. Config-flow money widgets.**
- `CONF_WOOD_PRICE_SEK_M3` hard-codes `'SEK/m³'` (config_flow.py:1645), as does the `simulate_plan`
  service description (strings.json, en, sv). `wood_fuel` compares that price directly with the
  plan's electricity prices.
- Measured: 1 of the 4 currency-labelled widgets ignores the instance currency (`[EUR]=1`,
  `[NOK]=1`); `[SEK]=0` is the null control.

**C. Card** (`p8_card.mjs`). The install is SEK everywhere, with card-config `currency: EUR`.
- The headline savings and savings table say SEK, because `savingsUnit()` lets the sensor's unit
  lead. The price axis and what-if delta say EUR, because `PlanSource.currency()` lets the card
  config lead.
- Measured: 2 distinct tokens; 3 counted surfaces off the install's currency (the price axis counted twice, as computed and as drawn, plus the what-if delta).
- Null control (no card currency): 1 token. Perturbation (drop `this.config.currency ||`): 1 token.
- Positive control: the R7-D4-03 pre-fix card (`57a6e19f^`) has 4 off-install surfaces, savings
  table included. That fix moved one seam of four.
- `tests/card.mjs:1336` pins "an explicit card setting still wins" for the delta; `:8071` pins the
  opposite rule for the savings table.
- In the use case the card documents for `currency:` (docs/dashboard-card.md:653, a price feed that
  disagrees with the published currency), the savings figures are in the feed's currency under the
  sensor's label. So the card override and seam A are one phenomenon.

Barrier:
- Keep the feed's declared money code (the price entity's unit, or Tibber's `priceInfo.currency`)
  and raise a repair issue when it differs from `coordinator.currency`.
- A `tests/entities.py` check: no literal currency unit in a selector or translation string, and
  every money surface through one resolver.
- A one-currency-per-screen assertion over all four card surfaces in `tests/card.mjs`, replacing the
  delta-only pin.
- Cost (provisional): 1.30 s static rule; 2.74 s full probe including `plan_view.py` and node.

## D14-s2-03 (I4, low, bug): the class roster and finding grammar have disagreeing readers

Property: each audit identifier has one definition. Every reader either loads it from there or is
held equal to it by a check that exercises the cases where they could differ.

Seam rule: `i4_roster.py --seams` (31 reader sites); `i4_roster.py --dims <ref>` for the dimension
roster.

Command: `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D14/s2/i4_roster.py`

**P11 is held by no D14 seat.**
- `bugclasses.json` has 16 ids; scopes.json's D14 axis has 15. So P11 (10 instances, open) is
  measured by no D14 seat this round.
- `check_scopes.check()` reports D14 `ok`, because it proves completeness against the dimension's
  own (stale) axis.
- Perturbation: with the axis set to the ledger ids in memory, `check()` fails with 5
  unowned-P11 lines.
- The schema enum equals the ledger: `check-wave-script.mjs` holds those two together, and nothing
  holds the axis.

**The intake admits what the schema refuses.**
- The `audit-find.js` intake, executed in a node vm on 22 boundary findings, admits 11 that
  `finding.schema.json` refuses.
- Class ids P0, P12, P99, I0, I6 and P011 pass because `CLASS_GUESS` is `/^([PI][0-9]+|new)$/` and
  `reportSchema.class_guess` is a bare string.
- Ids `D14-s2-1`, `-001`, `-xx`, `-` and `-01a` pass because the intake uses
  `startsWith(seat + '-')`, not the schema pattern.
- Perturbation: rebuilt from the ledger and schema, the count is 0.
- Null control: 0 of 17 admissible cases refused.
- `check-wave-script.mjs`'s intake test uses `X9` as its unknown class, a case both readers already
  agree on.

**Positive control.** `--dims 8d731d77^` finds `audit-find.js` DIMS missing D13 (R7-INSTR-01); 0 of
4 readers disagree at HEAD.

Barrier: assert in `check-wave-script.mjs` that the D14 axis equals the ledger ids, build the
intake's checks from `finding.schema.json`, and add P99 and `D1-s2-1` to the intake test. Cost:
0.24 s (provisional).

## Non-findings

- Dimension roster at HEAD: 0 of 4 readers disagree (`i4_roster.py --dims HEAD`).
- The schema `class_guess` enum equals the ledger ids plus `new`.
- Every Python money sensor reads `coordinator.currency` (12 sites). The narrative's live
  `resolve_currency` is the documented exception (`narrative.render` docstring).
- The R7-D12-01 guards (config_flow.py:2039, :3425) stay on the canonical predicate.
- 21 of the 29 P2 rule reads are guarded or not applicable; the other 8 are the 3 instance seams (table above).

## Unfinished

- M3: one ledger instance is replayed per class, not all. P2's rule covers config-key proxies only;
  R6-D12-01's proxy was a `ThermalState` field. P8's rule does not replay the unit instances, which
  #1513's `tests/entities.py` float barrier guards. I4 does not cover the verdict-grammar readers
  (R5/R6 D13).
- M5: barriers are proposed, not built or demonstrated as checks. Their gate-seconds inside
  `tests/entities.py` are unmeasured.

## Leads

- `grid_fee.IMPLAUSIBLE_FEE_SEK_PER_KWH`: one 10-per-kWh bound for every currency.
- `currency.FALLBACK_CURRENCY`: real HA always sets `config.currency` (default EUR), so the SEK
  fallback fires only under stubs.
- `quick_setup.stored_answers`: the buffer answer is volume-only, while `buffer_is_store` also
  requires a valve.

## Exposure

- Read under the D14 exception: `tools/audit/bugclasses.json`.
- Commit messages and diffs:

  | commits | what they fixed |
  |---|---|
  | 56cb0027, 4a19c425 | R8 P8, #1513 |
  | 57a6e19f | R7-D4-03 |
  | 7df2ce55, a97681b5, c6a19759, 2c135037 | earlier currency fixes |
  | f0e38526, 3602b6ca, 0f8d9a4f | R7-D12-01 |
  | 06ec54b5 | merge of `fix/r6-d8-01` (hot-water entities disabled by default) |
  | 5b83e369, d62195ad | R6-D12-01 |
  | 99212150 | R5-D7-03/04 |
  | 9eaa284c, d571cb79, 8d731d77, 5b367a63 | D11/D13 instrument fixes |

- Pre-fix trees via `git show`: 3602b6ca^, 57a6e19f^ and 8d731d77^.
- The currency lines of docs/dashboard-card.md.
- No file under `tools/audit/round3`..`round8` was read; the host removed them mid-run, none opened.
- No `gh`, no GitHub.

## Harnesses

`p2_facts.py`, `p8_currency.py`, `p8_card.mjs` and `i4_roster.py` under
`tools/audit/round9/D14/s2/`. Each header carries its command, expected values, baseline and machine.
Each prints `RESULT` lines plus `thread_factor`, `load1` and `swapins`.
