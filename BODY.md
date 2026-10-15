R10-DEEPLINK: one card helper builds every Home Assistant deep link, and one census holds every link the card emits to it.

Closes #2253.

Part of #2238.

Owner report (2026-10-14): Advisor "Open settings", Setup "Configure" and Health "Show" each built their own link, and each landed on the integration's front page. This adds the shared builder and the census only. Per the architect note, the three call sites stay for R10-ADVISOR, R10-UX-SETUP and R10-UX-HEALTH, which run `after` this group.

- **`haLink(kind, entryId, entityId)`** (pure) builds the routes that home-assistant-frontend 20260826.7 reads. With no entry it falls back to `?domain=`, never a guessed entry.
  - `options`: `#config_entry=` on the integration page. The frontend has no route into an options-flow step.
  - `entities`: `?config_entry=`. Disabled entities are listed, because a URL filter clears the state filter.
  - `entity`: the same, plus `more-info-entity-id`/`more-info-view=settings`.
- **`openHaLink`** resolves the card's own entry with `config/entity_registry/get` and navigates through the existing `navigateTo`.
- **ARCH2-s5 C2 is folded in:** `SetupPage.openPicker` and `openSetupSlot`.
- **The census** is in `tests/card.mjs` and has two arms:
  - **Dynamic:** every page is rendered, and every own-listener element is pressed on a fresh card. Every navigation primitive is instrumented, so using one is recorded rather than thrown: `history.pushState`/`replaceState`, `open`, the `location` setter and its `href`/`assign`/`replace`, `hass-more-info`/`hass-action` events, and anchor hrefs after the press. Each recorded link must be a path `haLink` builds. A press may not throw.
  - **Static:** the card's code, with comments stripped, may not contain `href` (in any quoting or key form), `location`, `pushState`, `replaceState`, `.open(` or the two event names outside `navigateTo`'s body. `this.dialog.open()` is the one exemption.
  - Unconverted links are `PENDING` rows, each excusing exactly its own `navigateTo` push. A stale row is refused. Every `navigateTo`/`openHaLink` source line must be reached by a press.

Re-cut at round 4 (three-round rule). Rounds 1 to 3 each closed the spelling the last review planted. This round instruments every primitive the static arm names, and the static arm matches by token.

## Head

56789d0ab683ff38b9b651cfd1b626288576e28d. Merge base: c42d7cea65ab81c5bb27e99071ef38719a6a8885.

- The plants and the census were measured at c0d580c4c.
- ce63ed9dd merges origin/main and changes none of the card, `tests/card.mjs`, the test rig or the driver.
- 56789d0ab moves the driver from `dev/audit/harnesses/` to `tools/audit/seat/`, because `tests/harness_headers.py` reads the former. The driver changes by its own usage line only.
- The scoped gate ran at ce63ed9dd. At 56789d0ab, `tests/closure.py select` names the same nine scripts.
- The card source is byte-identical to 0b4d46abd, the first reviewed head.

## Mutation proof

`python3 tools/audit/seat/r10_deeplink_mutants.py` (in this PR) applies 32 plants one at a time and restores the card after each: the fixer's M1 to M6, the reviews' R4 to R7d, and the round-3 review's `mut3.py` N1 to N5 and H1 to H10, verbatim. At the head:

- **All 32 plants are red on a FAIL line** (rc=1, fails 1 to 5). None is "killed" by crashing the run.
- **The token arm alone** catches the shapes the stub cannot render or resolve:
  - R7b, H2, H4, H5, H6, H7 (an href set on `"a.zz"`, which the stub never resolves);
  - H8 (`innerHTML`);
  - H9 and H9t (`insertAdjacentHTML`, which the stub lacks).
- **The dynamic arm alone** (`every link a button emits is one haLink builds for this entry`) catches the run-time-assembled names:
  - R6b and R7c;
  - R7d (the after-press walk);
  - R6c (plus the two older Assign checks).
- **Both arms** catch N1, N1t, N3, N3t, N4, R5, R6 (plus the reach and stale-row checks), H1, H3 and H10.
- **N2 and N5** are red on the token arm, plus an unrelated dismiss check.
- **Route, lookup and focus mutants** are red on their own direct checks:
  - M1 and M2: `haLink builds the three deep links ...` (M2 also on the fallback check);
  - R4: `openHaLink asks the registry for its own plan sensor and links this entry`;
  - M5: the `openSetupSlot` focus check;
  - M4: `the census reached every line that emits a Home Assistant link`.
- **M3 and M6** are refused by `every link a button emits ...` and by the stale-row check, respectively.

N1 to N5 and H9 used to be "killed" only by crashing an earlier scenario, before any check printed. Two test-context changes fix that:
- The test context now carries a complete, inert navigation surface from load, as a browser does: `replaceState`, `open`, `location` and window `dispatchEvent`. The census then sees N1, N3 and N4 on its own.
- The token arm runs at the top of `card.mjs`, before any card renders. Its FAIL line therefore prints even for H9, which still crashes later on the stub's missing `insertAdjacentHTML`.

N2 and N5 sit on the feedback row's dismiss button, which the census fixture does not render, so the token arm is the one that holds them.

## Null control

`r10_deeplink_mutants.py --null` (no plant) prints `RESULT mutant=NULL_no_plant rc=0 fails=0`. At the head, the census presses `plan=12 setup=0 savings=0 advisor=4 health=3` elements, with no press throwing, and it reaches both link-emitting source lines.

## Figures

- **Finder harnesses.** The card blob is unchanged since 79c5974e1, and the round-3 review re-ran these at 0c7870592.
  - `node $EXPORT/dev/audit/rounds/round10/D7/arch2-s5/card_shapes.mjs <card>` (sha1 677b75421ca84ac0f404dc90fa0b6a0b72edea0e), base 5603ee319 to head:
    - `picker_open` 3 -> 1
    - `total` 33 -> 31
    - `dead` 1 -> 2. The added symbol is `openHaLink`, which has no caller until the later groups convert their buttons.
  - `node $EXPORT/dev/audit/rounds/round10/catchup/arch-b/v2_card_lines.mjs <card>` (sha1 b3a1890e77115f9dbe0e2b64954bb21419890366): `picker_lines` 5 -> 3.
- **Scoped gate:** `GATE_SCOPE=auto bash tests/run.sh` at ce63ed9dd gives MODE: SCOPED, with the selection `tests/closure.py select --diff c42d7cea6`. It printed `12 TEST SCRIPT(S) PASSED; 23 SCOPED OUT AND NOT RUN`, rc 0. card_drift.mjs ran in that set against origin/main and printed `card_drift: identical in all 40 states`.
- **`python3 tests/structure.py`** at ce63ed9dd: STRUCTURE RATCHET PASSED. No budget moved.
- **`python3 -I tools/audit/seat/tmp_paths.py --check`**: 0 refused. The new driver names no temp or machine path.

## Red checks

none

## Forward-carry

Delivered by #2287 (9b1320d37, on origin/main) into the R10-ADVISOR, R10-UX-SETUP and R10-UX-HEALTH briefs in `dev/programme/rosters/wave-r10-groups.json`:
- there is no URL into an options-flow step;
- each group deletes its own `PENDING` rows;
- every new link button is built with `haLink`/`openHaLink` and is pressable in the census;
- for R10-UX-HEALTH, the disabled-only filter has no URL.

## Friction

- fixer-step-6: contradiction: the shared seat brief told the seat to open the PR with app_push.sh and post on #201, while fixer.md step 6 and the group brief say seats push refs only; the orchestrator corrected it mid-task and only refs were pushed.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
