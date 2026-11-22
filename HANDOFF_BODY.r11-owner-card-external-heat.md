R11-OWNER-CARD-EXTERNAL-HEAT (round 11, size S, owner item, seam `card`): the header's status pill now shows when external heat is detected, and its heating state names which plan is heating. Built to the approved design `design/R11-OWNER-CARD-EXTERNAL-HEAT` 6ed233f99c (`Design review: approve 6ed233f99c`, `design-verdict/R11-OWNER-CARD-EXTERNAL-HEAT`).

Closes #3861

What changed, by the design's sections:

- **`statusPill`** (`heatpump-optimizer-card.js`). The precedence is now manual > fallback > stale > **external_heat** > heating > idle. `external_heat` (tone `accent`, with a title) is on when the card's own External Heat Source binary sensor reads `on`. `off`, `unavailable`, `unknown` and a missing entity all read off. The heating state is built per kind (`{space, dhw}`), and its text is `status.heating_space`, `status.heating_dhw` or `status.heating_both`. The key stays `heating`, so the `data-status` selector contract and `statusSignature` (`key:text`) are unchanged. `status.heating` is removed from all three tables.
- **One twin derivation.** `planIdStems(plan)` gives each resolved plan id with its `PLAN_ID_DERIVE` suffix stripped. `planBinaryTwin(plan, suffix)` reads `binary_sensor.<prefix><suffix>` from those stems, so the read stays inside this card's config entry. `inputProblemState` and the external-heat read both call it, through the named constants `INPUT_PROBLEM_SUFFIX` and `EXTERNAL_HEAT_SUFFIX` (review carry `suffix-const`). The history source's `derive` had a byte-for-byte copy of the same loop, and it now reads `planIdStems` too (see `## Design deviations`).
- **Strings** en, sv and de, beside the `status.*` block in each table, per the design's table. The title is the exception, corrected under `title-truth` below.
- **`docs/dashboard-card.md`**: the pill table gains the external-heat row and the three heating rows. The sentence about hovering also covers the external-heat pill.

## Design deviations

- **Title text (design carry `title-truth`).** I checked it against `dhw_planner.py`'s external-heat block (`# --- External heat source (item 5)`). Only the DHW planner reads `external_heat_active` to hold back planned slots, and only while coasting meets the requirement. `grep -rn 'external_heat_active' custom_components/heatpump_optimizer/*.py` returns one other reader that changes behaviour, the coordinator's `_learning_frozen`, which freezes learning and holds back no heating. So "Planned heating is held back while they stay warm enough" overstated the hold for space heating. The title now reads "Something other than the heat pump is heating the tanks. Planned hot-water heating is held back while the tank stays warm enough." sv and de carry the same narrowing. The first sentence and the pill text are the owner's words, unchanged.
- **The history source's `derive` reads `planIdStems`.** The design named only `inputProblemState` for the fold. Without this second fold, `archscore --diff` read `card_clone_copies 101 -> 103` (inadmissible). The cause was the new twin's opening, which is the same 20-token window as `priceNow`'s. With `planIdStems` it reads `dS +0.0000 NULL`. `derive`'s loop was the same derivation as the stems: forms outer, then kinds space first, then the first matching suffix. It now reads the stems in the same order, so its behaviour is unchanged. Three `tests/card.mjs` history checks pin it (mutant M6 below). `statEntity` keeps its own loop on purpose, because it also requires `states[planId]` to be present. Folding it would change which stat entity a missing plan sensor resolves.

## Head

0b0d442c211095ce3e1eae93d17851feb9b315a6, on merge base 8ef450936a1786abf4bb9610dc3336da4e77e8de, which was origin/main at `date -u` 2026-11-22 16:24 UTC. `git merge-tree --write-tree origin/main HEAD` reports no conflict.

## Mutation proof

Each mutant is one edit to the card file at the head. `node tests/card.mjs` ran with `PYTHONPATH=tests/hastub`, and the file was restored afterwards (`cmp` against the saved copy). The drivers are scratch (`mut.py`), and each edit is stated in full below.

| mutant | edit | `tests/card.mjs` checks that go red |
|---|---|---|
| M1 external branch deleted | `if (ext && ext.state === "on") {` to `if (false) {` | "external heat: the sensor on over a heating plan reads external_heat, tone accent, with its title"; "... over an idle plan reads external_heat"; "external heat: sv and de render every new pill text and title from their own table" |
| M2 on-test widened | `ext.state === "on"` to `ext.state !== "off"` | "external heat (null): the sensor off, unavailable or unknown leaves the heating pill" |
| M3 space read forced false | `const space = activeNow(byKind.space)` to `const space = false` | "only the space plan active now reads 'Heating space'"; "both plans active now read 'Heating space+DHW'"; the off/unavailable/unknown null; "another config entry's external-heat sensor does not light this card's pill"; the sv/de check |
| M4 DHW read forced false | `dhw = activeNow(byKind.dhw)` to `dhw = false` | "UI-3 pill: a plan step active now reads heating"; "only the DHW plan ... 'Heating DHW'"; "both plans ... 'Heating space+DHW'"; "an unavailable space plan counts inactive ..."; the sv/de check |
| M5 external branch moved below the heating return | the `external_heat` block placed after the idle return, just before the heating return | "the sensor on over an idle plan reads external_heat"; the sv/de check |
| M6 no stems | `if (sfx) stems.push(...)` to `if (false) stems.push(...)` | the external-heat checks, every Input Problem / Health check ("the header pill reads 1 input problem (warn)", "the render signature follows the Input Problem sensor", ...), and the history checks "the tank and lower-floor probes are asked for when the install has them" and "each past point is the value its own sensor held at that step" |

The unmutated head reads rc 0, with no `FAIL` line.

Failing test first: with the new checks added and the card at the merge base, `node tests/card.mjs` reads `8 CARD CHECK(S) FAILED`. They are the three heating variants, the unavailable-kind check, both external_heat checks, the off/unavailable/unknown null (it reads `Heating now`, not `Heating space`) and the sv/de check.

## Null control

- External heat: with the sensor `off`, `unavailable` or `unknown`, the pill is the heating pill. With it `off` over an idle plan, the pill markup is byte-identical to the markup with no sensor (`extPillHtml(withExt(idle(), "off")) === extPillHtml(idle())`). Another entry's `binary_sensor.other_house_external_heat_source` `on` leaves this card's pill at heating. Every pre-existing pill check is the "sensor absent" arm, because `mkStates` publishes no external-heat sensor (design carry `rig-absent`).
- Precedence: external heat on plus stale reads stale, and plus manual reads manual. Both pass at base and at head, as a control should, and M5 shows the position is pinned from below.
- Variants: neither plan active reads `idle` (the existing check). An unavailable space plan with both `active_now` reads `Heating DHW`.
- `tests/features.py`: with the payload's `external_heat_active` false, `ExternalHeatBinarySensor` reads `is_on` false under the same entity id. The check also refuses if the card's `EXTERNAL_HEAT_SUFFIX` const is not found (`_eh_card_suffix is not None`).
- Card drift is pill text only. A scratch script compared each of the 41 drifted states' `-`/`+` lines after replacing the old pill text with the new: `states 41 non-pill 0`. Without that replacement, every one of the 41 states compares unequal.

## Figures

- `node tests/card.mjs` at 0b0d442c21: rc 0, no `FAIL` line. At the merge base with the new checks: `8 CARD CHECK(S) FAILED`.
- `node tests/card_drift.mjs 8ef450936a1786abf4bb9610dc3336da4e77e8de` at 4fd5fbc1e1, before the `planIdStems` fold, and in the scoped gate at the head: `41 state(s) moved and claimed, 4 identical`. Every moved state has both plans active now, so "Heating now" becomes "Heating space+DHW" (sv "Värmer huset+varmvatten"). Each is claimed in `tests/golden/card_claimed_drift.txt` with this group's reason. `claims-for:` is unchanged and equals `VERSION`. `tests/golden/claimed_drift.txt` is byte-identical, because no solver golden moves.
- `python3 tools/audit/archscore/score.py --diff 8ef450936a1786abf4bb9610dc3336da4e77e8de`: `Architecture score: dS +0.0000 NULL`. Before the `planIdStems` fold it read `dS -0.0280 WORSENS (inadmissible: card_clone_copies 101->103)`.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- Class enumeration (fixer.md step 8), the design's section 4 commands re-run at the head (`$F` the card file):
  - `grep -n 'L("status\.' $F`: every hit is inside `statusPill`, and the variant text is `L(variant)` there too. Disposition: closed in this diff.
  - `grep -n '_input_problem\|PLAN_ID_DERIVE\[' $F`: three hits. `INPUT_PROBLEM_SUFFIX` is the const. `planIdStems` is the one derivation. `PlanSource.statEntity` keeps its loop because it also requires `states[planId]` (see `## Design deviations`). The history `derive` copy is folded.
  - `grep -rn 'Heating now\|Heizt gerade\|Värmer nu' docs tests custom_components`, excluding the claim file: 0.
  - `grep -rn 'status\.heating\b' tests custom_components docs`, excluding `heating_`: 0.
- Scoped gate at 0b0d442c21: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh`, under `HPO_GATE_LOCK_LABEL`. Mode line `MODE: SCOPED -- 12 script(s) run, 21 scoped out`. Every script it ran reads ok: env_drift (`--claims-only`, `--all`), plan_view, closure selftest, card.mjs, card_drift.mjs, arch_score_head, features, entities, doc_claims, md_tables, layout, deployment_shape and harness_headers. Summary line `14 TEST SCRIPT(S) PASSED; 20 SCOPED OUT AND NOT RUN`; the two summary counts include the `run_always` lines.
- `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node tests/card_browser.mjs` at 0b0d442c21 on Linux. No scope selects this script, and the diff is on `GRID_SURFACE`. Result: rc 0, `ALL BROWSER CHECKS PASSED`, `P9 grid: 396 cells, 23871 text runs, 1190 box-intersecting pairs inked, 112 colour rules`. The grid renders no external-heat state, so it measures the new heating texts only. The `accent` tone the external-heat pill uses is the same rule the manual pill already draws.
- prepr: `PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <body>` at 0b0d442c21 reads `PRE-PR: 0b0d442c211095ce3e1eae93d17851feb9b315a6 ... rc=0`. It ran scoped: no change outside the card, its doc and its tests reaches what only a full run measures. Its `ci predict` step reads no closures, fast, governance or instrument red predicted, and its `merged structure` step reads STRUCTURE RATCHET PASSED.

## Red checks

none

## Forward-carry

- **title-under-override** (design review carry). `R11-OWNER-EXTHEAT-OVERRIDE` is in design and not on main, so nothing here can condition on it. If it lands, the title's hold sentence should read the effective-block attribute or be dropped. Carry: R11-OWNER-CARD-EXTERNAL-HEAT (item title-under-override), pending the orchestrator's ordering decision between the two groups.
- **fading-window** (design carry). While the detector fades, the sensor is off, so the pill reads idle or heating even though the DHW hold may continue. The owner asked for "detected". Carry: R11-OWNER-CARD-EXTERNAL-HEAT (item fading-window), a new owner ask if wanted.
- **features.py versus card.mjs** (design review, routed to the owner). The three variant checks and their nulls are in `tests/card.mjs`, and `tests/features.py` carries the backend half. Carry: R11-OWNER-CARD-EXTERNAL-HEAT (item variant-checks-home), pending owner confirmation.

## Friction

none
