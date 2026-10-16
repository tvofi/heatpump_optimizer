R10-DEEPLINK: one card helper builds Home Assistant deep links, with direct checks on it.

Part of #2253.

Part of #2238.

#2253 asks for three things: a shared builder, the three call sites converted to it, and one test that enumerates every link-emitting button. This PR delivers only the builder.
- The three call sites go to R10-ADVISOR, R10-UX-SETUP and R10-UX-HEALTH.
- The complete enumeration went to #2317 after the round-4 review.

So #2253 stays open here.

The changes:
- **`haLink(kind, entryId, entityId)`** (pure) builds the routes that home-assistant-frontend 20260826.7 reads. With no entry it falls back to `?domain=`.
  - `options`: `#config_entry=`.
  - `entities`: `?config_entry=`, with disabled entities listed.
  - `entity`: the same, plus `more-info-entity-id` and `more-info-view=settings`.
- **`openHaLink`** resolves the card's entry with `config/entity_registry/get` and navigates through `navigateTo`.
- **ARCH2-s5 C2 is folded in** (`openPicker`, `openSetupSlot`).
- **Direct checks** in `tests/card.mjs` cover the three routes and the fallback, the registry lookup and its refusal, and `openSetupSlot`'s keyboard focus.
- **The census** in `tests/card.mjs` is narrowed to what it observes:
  - pressed buttons on rendered pages;
  - the instrumented primitives;
  - a token check over the card source;
  - `PENDING` rows for the three unconverted links.

  The test lists its known gaps: K5 (a bare `open(` on an unrendered row), K1 (`navigation.navigate`), K2 (a form `action`), K3t (an `Event`-built `hass-more-info`), and the split-token residual (`"hr" + "ef"`). The dynamic arm sees that residual only on a rendered row, and for an event name only through `CustomEvent`.

## Head

411cbe61bac4404327edab085383ec5dae34b226 (merge base 25afc1c771f9f0a3e60115e3c59326e22461a723).

- The mutation proof and the null control were taken at 974af2ca3.
- Since then, 411cbe61b changes the wording only:
  - the check `no press throws` is renamed from a name that over-claimed;
  - the inert-surface comment now names the four primitives it adds and the Navigation API it omits;
  - the delivery row carries the PR's retitle.
- No check's logic changed. The scoped gate and the structure ratchet were re-taken at 411cbe61b.

## Mutation proof

`python3 tools/audit/seat/r10_deeplink_mutants.py M1_options_drops_entry M2_entity_drops_settings_view M3_delete_advisor_pending_row M4_unreached_link_site M5_openPicker_no_focus M6_convert_advisor_settings R4_entry_ignored`: each plant is rc=1 on a FAIL line.
- **M1 and M2** (a route drops `#config_entry=` / `more-info-view=settings`): `haLink builds the three deep links Home Assistant routes`. M2 is also red on the fallback check.
- **R4** (`entryId = null`): `openHaLink asks the registry for its own plan sensor and links this entry`.
- **M5** (`openPicker` hands no focus): `openSetupSlot opens the slot's picker, focused only from the keyboard`.
- **M3** (delete a PENDING row): `every link the census records from a press is one haLink builds for this entry`.
- **M4** (a link site no press reaches): `the census reached every navigateTo and openHaLink call site`.
- **M6** (convert a pending button): `every PENDING row still names a button that makes its unconverted navigation`.

## Null control

`python3 tools/audit/seat/r10_deeplink_mutants.py --null` (no plant): `RESULT mutant=NULL_no_plant rc=0 fails=0`.

## Figures

- **Scoped gate:** `GATE_SCOPE=auto bash tests/run.sh` at 411cbe61b gives MODE: SCOPED (`tests/closure.py select --diff 25afc1c77`). Result: `12 TEST SCRIPT(S) PASSED; 23 SCOPED OUT AND NOT RUN`, rc 0. card_drift.mjs ran in that set and printed `card_drift: identical in all 40 states`.
- **`python3 tests/structure.py`** at 411cbe61b: STRUCTURE RATCHET PASSED.
- **`python3 -I tools/audit/seat/tmp_paths.py --check`** at 974af2ca3: 0 refused.

## Red checks

none

## Forward-carry

- **#2317, roster group R10-DEEPLINK-CENSUS:** the complete navigation census. Its review plants (K1, K2, K3t, K5) are listed as known gaps in `tests/card.mjs` at the census.
- **R10-ADVISOR, R10-UX-SETUP and R10-UX-HEALTH:** their briefs in `dev/programme/rosters/wave-r10-groups.json` (#2287, on origin/main) carry the call-site conversion, the `PENDING` rows each group deletes, the absence of an options-flow-step URL, and the disabled-only filter.

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
