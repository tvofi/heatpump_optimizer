# Design: R11-OWNER-CARD-EXTERNAL-HEAT (round 11, size S, owner item)

Architect note, extended (`dev/governance/roles/designer.md`), light by the
roster brief (decision 0014). Closes #3861. Predecessor `R11-SEAM-card` merged
as #3821 (`608c95decc`); its handoff head 068fd74a333cf135ca516e11a50d57443e3e0b46
is an ancestor of `origin/main` 8ef450936a1786abf4bb9610dc3336da4e77e8de, where
the code was read, and the card file is byte-identical at both. `$F` is
`custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`; `:n` is
its line at that SHA. No production code on this ref.

**Evidence: no finder harness: owner report.** Issue #3861 (tvofi,
2026-11-22): the pill "reads only manual, fallback, stale, heating or idle. It
does not reflect that external heat is detected, and the heating state does
not say whether space heating, DHW or both are heating." Re-read here:
`statusPill` (`$F:9758`) returns those five keys and reads no external-heat
entity; its heating branch (`:9779`) folds both plans into one `some()`.

## 1. Owning seam

`card`: `$F` alone owns the pill. The backend already publishes everything the
card needs, so the change has one owner. `binary_sensor.py` is read, never
changed: `ExternalHeatBinarySensor` (`custom_components/heatpump_optimizer/binary_sensor.py:244`)
pins its object id to `heat_pump_optimizer_external_heat_source` through
`_pin_identity` (`custom_components/heatpump_optimizer/entity.py:293`), and its
`is_on` is the payload's `external_heat_active` (`custom_components/heatpump_optimizer/coordinator.py:8088`),
which is the detector's `state.active`.

## 2. Shape

**What the card reads.** The binary sensor's state, found as the binary twin of
the resolved plan id, the way `inputProblemState` (`$F:10479`) finds
`_input_problem`: for each plan kind, strip the `PLAN_ID_DERIVE` suffix from
`plan.resolveEntity(kind)`, read `binary_sensor.<prefix>_external_heat_source`.
That scopes the read to this card's config entry; a global scan could bind to
another entry's sensor. The fixer generalises `inputProblemState` into one
`planBinaryTwin(plan, suffix)` and calls it for both suffixes, so there is one
derivation, not two. On is `state === "on"`; `off`, `unavailable`, `unknown`
and a missing entity all read off.

**Not read:** `suppressing_electric_dhw` (`binary_sensor.py:273`), which is the
detector's `suppressing` (`custom_components/heatpump_optimizer/external_heat.py:489`),
true while active **or fading**. The owner asked for "detected", which is
`is_on`. See §3 B.

**`statusPill(plan, now)`**, signature unchanged, precedence:
manual > fallback > stale > **external_heat** > heating > idle.

| key | tone | text key | title key | when |
|---|---|---|---|---|
| `external_heat` | `accent` | `status.external_heat` | `status.external_heat_title` | twin sensor `on` |
| `heating` | `ok` | `status.heating_space` | none | only space `active_now` |
| `heating` | `ok` | `status.heating_dhw` | none | only DHW `active_now` |
| `heating` | `ok` | `status.heating_both` | none | both `active_now` |
| `idle` | `idle` | `status.idle` | none | neither |

The heating split reads the same filtered `plans` array, but keyed by kind:
build `{space, dhw}` states first, then `active_now` on each. A kind whose
sensor is `unavailable`/`unknown` counts inactive, as today. The key stays
`heating` for all three: `data-status` is a selector contract
(`tests/card_browser.mjs:508`, `tests/card.mjs:12256`), and
`statusSignature` (`$F:9794`) already keys on `key:text`, so a change of
variant redraws. External heat redraws the same way, because
`statusSignature` calls `statusPill`; no new signature term.

`status.heating` is removed from all three tables; no other caller reads it
(`grep -n 'status\.heating"' $F`).

**Strings** (en / sv / de), beside the current `status.*` block in each table:

| key | en | sv | de |
|---|---|---|---|
| `status.external_heat` | External heat detected | Extern värme upptäckt | Fremdwärme erkannt |
| `status.external_heat_title` | Something other than the heat pump is heating the tanks. Planned heating is held back while they stay warm enough. | Något annat än värmepumpen värmer tankarna. Planerad uppvärmning hålls tillbaka så länge de håller tillräcklig temperatur. | Etwas anderes als die Wärmepumpe heizt die Speicher. Geplantes Heizen wird zurückgehalten, solange sie warm genug bleiben. |
| `status.heating_space` | Heating space | Värmer huset | Heizt Räume |
| `status.heating_dhw` | Heating DHW | Värmer varmvatten | Heizt Warmwasser |
| `status.heating_both` | Heating space+DHW | Värmer huset+varmvatten | Heizt Räume+Warmwasser |

The en texts are the owner's words. "while they stay warm enough" is there
because the hold is conditional: `dhw_planner.py` suppresses only while
coasting meets the requirement (`custom_components/heatpump_optimizer/dhw_planner.py:1332`).

**Invariants kept:** no plan sensor is still no pill; manual, fallback and stale
still win over everything below them; sensor off gives byte-identical pill
markup to today's for idle; the pill stays one `<span>`.

## 3. Alternatives

- **A. A separate pill key per heating variant** (`heating_space` ...). Lost:
  three selectors where tests and the browser rig read one, and the text already
  carries the variant into the signature.
- **B. Show the pill while `suppressing_electric_dhw` is true (fading too).**
  Lost: the sensor reads off while fading, so the pill would contradict the
  entity it names; the owner asked for "detected". Carried as an observation.
- **C. Find the sensor by `_findPinnedEntity`** (`$F` away strip). Lost: its
  fallback matches `attributes.unique_id`, which Home Assistant does not put in
  state attributes, so a renamed id is never found; the plan-twin derivation is
  entry-scoped and already used.
- **D. Tone `warn`.** Lost: `warn` is the stale pill, a fault to act on;
  external heat is someone other than the plan in charge, as a manual plan is.

## 4. Sibling sites (by command)

- `grep -n 'L("status\.' $F`: every pill text; all in `statusPill`.
- `grep -n '_input_problem\|PLAN_ID_DERIVE\[' $F`: the twin derivations; the
  one in `inputProblemState` is folded into `planBinaryTwin`.
- `grep -rn 'Heating now\|Heizt gerade\|Värmer nu' docs tests`: the pill table in
  `docs/dashboard-card.md:75` gains the external-heat row and the three heating
  rows. In scope here: no other group's `files` names that doc, and leaving it
  says a pill the card no longer draws.
- `grep -rn 'status\.heating\b' tests`: none at the base.

## 5. Evidence plan, by file

- **`tests/card.mjs`, in the UI-3 pill block (`:12240`), failing first:**
  (1) `withPlan(idle(), "space", active_now)` reads `heating` / "Heating space";
  (2) DHW only reads "Heating DHW"; (3) both read "Heating space+DHW";
  null for each: the other kind inactive gives the single variant, neither
  gives `idle` (already pinned). (4) `binary_sensor.heat_pump_optimizer_external_heat_source`
  `on` over a heating plan reads `external_heat`, tone `accent`, with the title;
  null: the same states with it `off`, `unavailable`, or absent read heating.
  (5) precedence: external on plus stale reads stale; plus manual reads manual.
  (6) sv and de: one render each resolves every new key (no raw key text).
- **`tests/features.py`, as the owner asked:** the backend half of the contract,
  in the `R10-LEARNER-ETA` pattern (`tests/features.py:25822`): build
  `ExternalHeatBinarySensor` on a payload with `external_heat_active` true and
  check `entity_id` ends with the suffix the card's source names (read from
  `$F` by regex) and `is_on`; null arm: the payload false gives `is_on` false
  with the same id. The pill behaviour itself cannot be rendered from Python, so
  it lives in `tests/card.mjs`, where `tests/README.md` puts card behaviour.
- **Mutation proof targets:** the `external_heat` branch's condition and its
  position (swap it below the heating return); each `active_now` read in the
  split (force one to false); the `=== "on"` test (`!== "off"`, which would let
  `unavailable` through).
- **Card goldens:** run `node tests/card_drift.mjs`; every state whose plan has
  a step active now moves its pill text. Claim those states in
  `tests/golden/card_claimed_drift.txt` by `claim-files.md`, `claims-for:` equal
  to `VERSION` at the branch; no solver golden moves.

## 6. Order, hot files, carries

Serial position: after `R11-SEAM-card` (merged). Hot file `$F` is shared with
`R11-SEAM-product-text` and `R11-SEAM-comments-production` (card part), neither
`after` this group: the orchestrator orders them by PLAN.md's hot-file order.
`docs/dashboard-card.md` joins this group's files. Carries owed: none received.

## Notes for the fixer

- The fading window: the sensor goes off while the detector still suppresses
  (`external_heat.py:489`), so for that hour the pill reads idle while planned
  DHW heating is still held. The owner asked for "detected"; if a pill for the
  fading window is wanted it is a new owner ask, not this group.
  Carry: R11-OWNER-CARD-EXTERNAL-HEAT (item fading-window)
- Check the title sentence against `dhw_planner.py:1332` before merging: the
  hold is on DHW electric heating while coasting covers the requirement; if
  the space plan holds nothing, "planned heating" must not read as both.
  Carry: R11-OWNER-CARD-EXTERNAL-HEAT (item title-truth)
- `tests/card.mjs`'s `mkStates` publishes no external-heat sensor, so every
  existing pill check is already the "absent" null arm; add the entity only in
  the new checks.
  Carry: R11-OWNER-CARD-EXTERNAL-HEAT (item rig-absent)
