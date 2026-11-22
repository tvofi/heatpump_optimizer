Owner item R11-OWNER-CARD-EXTERNAL-HEAT, with its carry from R11-OWNER-EXTHEAT-OVERRIDE built in. The card's header status pill reads `External heat detected` while the plan device's External Heat Source binary sensor is `on`, and its title says planned heating is held back. The heating state now says what is heating: `Heating space`, `Heating DHW` or `Heating space+DHW`. Strings are in en, sv and de.

Design (a light note: the group is size S, so decision 0014 owes no design seat; this section is the note the brief asks for):
- `statusPill` precedence is manual, fallback, stale, external heat, then heating or idle. External heat goes after stale because a stale plan already means the integration actuates nothing, so "held back" would not be true. The pill uses tone `accent`, because it is not a fault.
- The sensor is read by `planBinaryTwin(plan, suffix)`. It takes the resolved plan sensor's id and swaps the plan suffix for the binary sensor's suffix, so the read stays on this card's config entry. This is the derivation the health page's input-problem read already made: `inputProblemState` is folded into it, so there is one derivation and no second one. A global suffix scan lost because it can read another entry's sensor (mutant M5).
- Carry 0 (block_ignored): the pill takes `external_heat` only when `attributes.block_ignored !== true`. Otherwise it falls through to the heating or idle state the plan earns. Main publishes no `block_ignored` yet (#3862 has not merged), and an absent attribute reads as not ignored, so main's behaviour is the sensor alone. No new string for the fall-through.
- The key stays `heating` for all three variants. `statusSignature` keys on `key:text`, so a change of variant redraws, and `data-status="heating"` readers (card_browser) stay valid.
- `status.heating` ("Heating now") is removed: after the split nothing reads it. `docs/dashboard-card.md`'s pill table follows.
- The behavioural checks are in `tests/card.mjs`, the suite that renders the card's production code. `tests/features.py` runs no JS. Its check pins the contract the card cannot see: each binary-sensor suffix constant the card derives an id from equals the slug of its sensor class's en.json name.

## Head

f7202d2bf2893bef0c505f3bd1b8f52ef24c4faa, measured on origin/main e3cb5c019b464a770cc7c6fe2fbc858ed29debf7 (merge base).

## Mutation proof

The driver is `$HOME/mut/run.sh` (scratch). Each mutant is one exact replacement in the card, then `node tests/card.mjs`, then a restore. The tree was `git diff --quiet` after the run.
- M1, `&& !(ext.attributes && ext.attributes.block_ignored === true)` deleted: FAIL `OWNER-EXTHEAT pill: the sensor on with block_ignored true falls through to the heating the plan earns`.
- M2, external-heat branch disabled (`if (false && ext ...`): FAIL `... the external heat sensor on reads 'External heat detected', ahead of heating`, `... its title says planned heating is held back`, `... block_ignored false still reads external heat`, `... the sensor turning on redraws the pill with nothing else changing`.
- M3, both-active test forced false: FAIL `... space on, DHW on reads 'Heating space+DHW'`.
- M4, DHW variant collapsed to space: FAIL `... space off, DHW on reads 'Heating DHW'`, `... the sensor off leaves the pill on heating`.
- M5, the twin read as any `binary_sensor.*<suffix>`: FAIL `... an external heat sensor of another device prefix is not read`. Re-run on the final `find` form of `planBinaryTwin`: same single FAIL.
- M6, external heat moved ahead of stale: FAIL `... its title says planned heating is held back`, `... the sensor on with block_ignored true falls through ...`, `... a stale plan outranks external heat`.
- F1, `EXTERNAL_HEAT_SUFFIX` changed to `"_external_heat"`: `features_block.py 'R.section("R11-OWNER-CARD-EXTERNAL-HEAT'` FAILs `each binary sensor suffix the card derives an id from is the slug of its sensor class's en.json name ...`.

No added `.py` lines outside `tests/` or `dev/`, so prepr's Python mutant draw has nothing to sample.

## Null control

At the merge base, `node tests/card.mjs` with the new checks fails 12 of them, all `OWNER-EXTHEAT pill:`. The 3 that pass are the controls that hold on either tree: neither active reads `Idle`, the sensor off reads idle, and a foreign-prefix sensor is not read. Every other card check passed at the merge base. Each behavioural check has its neighbour as its null: the other kind inactive (space only / DHW only), neither active (idle), the sensor `off` (heating or idle stays), `block_ignored: false` (external heat stays), a stale plan (stale wins).

## Figures

- `node tests/card.mjs` at af28b105 (the code head; f7202d2b adds only the claim lines): `ALL CARD CHECKS PASSED`. At the merge base with these tests: `12 CARD CHECK(S) FAILED`.
- `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py 'R.section("R11-OWNER-CARD-EXTERNAL-HEAT'`: `ALL 1 FEATURES BLOCK PASSED`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: SCOPED`. Every script `scope.run` names was run, with the `run_always` scripts, and all exited 0 (list below).
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0000 NULL`. The first cut read `card_clone_copies` +2, because `planBinaryTwin`'s nested loop matched `priceNow`'s window. The single `find` over `PLAN_ID_DERIVE`'s suffixes is shorter, and it brought the score back to NULL.
- `python3 tests/structure.py`: exit 0.
- Scripts run with `PYTHONPATH=tests/hastub`, each exit 0: `tests/structure.py`, `tests/env_drift.py --claims-only <merge base>`, `tests/closure.py selftest`, `tests/layout.py`, `tests/harness_headers.py`, `tests/arch_score_head.py`, `tests/deployment_shape.py`, `tests/md_tables.mjs`, `tests/plan_view.py`, `tests/card.mjs`, `tests/doc_claims.py`, `tests/entities.py`, `tests/features.py`, and `tests/card_drift.mjs` at f7202d2b.
- `node tests/card_drift.mjs` against origin/main: `41 state(s) moved and claimed, 4 identical`. Before the claims it read 41 unclaimed. A script compared each moved state's `-`/`+` line pair after mapping `Heating space+DHW` back to `Heating now` (and `Värmer hus+varmvatten` back to `Värmer nu`): `pairs differing beyond the pill text: 0` of 82 lines. Null control: an unmapped pair would print `OTHER:`. The moved states read space+DHW because the drift fixture has both plans active at its frozen time. The four identical states render no pill.

## Red checks

none

## Forward-carry

none

## Friction

- brief: contradiction: the brief places the pill checks in `tests/features.py`, which runs no JS, while its carry names `tests/card.mjs`. The behaviour is pinned in card.mjs and features.py holds the id-suffix contract. Carry: dismissed: resolved in this PR as stated in the design note.
