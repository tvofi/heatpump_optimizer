Fix review: blocked 1826c67c37a1332a36fb284eecfad248e07a1ee3 harness: class-open bare open() on an unrendered row, navigation.navigate, form action and an Event-built hass-more-info pass the census

bus-nonce: 0065e4a25f536290e796c54ddc54e1bc

This is round 4, the re-cut round. I reviewed from a detached worktree at 1826c67c37a1332a36fb284eecfad248e07a1ee3 and re-read that head before posting. The roles diff against origin/main is empty, so this contract is current.

The card blob is cb4035b6. It is byte-identical to 0b4d46abd and to the round-3 head. `tests/card.mjs` is b9f842a5. The new driver is `tools/audit/seat/r10_deeplink_mutants.py`.

## Is the defect in the fix itself?

**No.** The card change is sound at this head:
- `haLink`, `openHaLink` and the C2 fold (`openSetupSlot`, `openPicker`) are pinned by their direct checks. M1, M2, R4 and M5 are red on those checks.
- The finder's harnesses agree at both ends.

**The defect is in the census's completeness claim.** The title says "one census holds every link the card emits". The body says "Every navigation primitive is instrumented", and it names a single residual, a name split across a string concatenation, that "the census's dynamic arm sees on a rendered row". At this head, four spellings with **no string concatenation** pass every check. A fifth falsifies the residual as stated.

A split is possible: land the builder, its direct checks and the census under a narrowed claim that lists these as residuals, or close the census class in its own PR.

## Blocking: class-open

Each of the following was planted by my own driver, `mut4.py`, which reuses the fixer's `run()`. Each passes with `rc=0 fails=0`.

- **`K5_bare_open_on_dismiss`**: `open("/config/entities", "_self");`, placed before `dismissFeedback();`.
  - The token arm matches `\.open\s*\(`, which needs a dot, and a bare global `open(` is the commonest spelling.
  - The census fixture does not render the feedback row, so the dynamic arm never presses the button. This is N5's row, one spelling over.
  - `K5b globalThis["open"](...)` and `K5c globalThis.open.call(globalThis, ...)` pass the same way.
  - The control `K5r` puts a bare `open(` on a rendered row, and it is red on `every link a button emits ...`. So the hole is the token arm, which is the only guard on unrendered rows.
- **`K1_navigation_api_in_try`**: `try { globalThis.navigation.navigate("/config/entities"); } catch (_e) {}` after the pending settings push, on a rendered and pressed row.
  - The Navigation API is not instrumented, and `navigation` is not a token.
  - This is round 3's N1t shape with another primitive.
  - Without the `try` (`K1c`), it is "killed" only by crashing an earlier scenario (rc=1 with no FAIL line), which is the accident the inert surface was added to remove for the listed primitives.
- **`K2_form_action_rendered`**: `<form action="/config/entities"><button type="submit">go</button></form>` on the rendered health page.
  - This navigates with no script at all.
  - `anchors()` reads only `href`, a submit button has no own listener, and `action`/`formaction` are not tokens.
- **`K3t_Event_runtime_more_info_rendered_in_try`**: Home Assistant's own `fireEvent` shape, `new Event(name)` plus `detail`, with the name built as `["hass","more","info"].join("-")`, on a rendered pressed row.
  - The dynamic arm hooks only `CustomEvent` construction, and the rig has no `Event`.
  - So the stated residual ("the dynamic arm sees it on a rendered row") is false for events.
  - The literal spelling (`K3c`) is red on the token arm.

**A sound re-cut would allow, not deny.** Every round has closed the spellings the last reviewer planted, and a denylist of names cannot be complete. Three changes would make it allow-based:
- Make the dynamic arm cover every row by rendering a fixture that includes the feedback row. Extend the reach check from the `navigateTo`/`openHaLink` lines to every `data-act` handler, so an unrendered row is a red reach check, not a token-arm job.
- Run each press with a global that records any read of a name outside a known set (`navigation`, `open`, `location` and so on), so an uninstrumented primitive is refused rather than swallowed.
- Have `anchors()` also read `action` and `formaction`.

## The four questions in the brief

- **The fixer's driver**: `--null` gives `RESULT mutant=NULL_no_plant rc=0 fails=0`. All 32 plants give rc=1 with at least one FAIL line (18 with fails=1, 12 with fails=2, one with 3, one with 5). None of them shows only a crash tail, and the tree was restored.
- **The split-string residual**: on rendered rows the dynamic arm does catch `setAttribute(["hr","ef"].join(""))` (R7c, R7d) and a `CustomEvent` with a runtime name (R6b, R6c). It does not catch an `Event`-built one (K3t). The residual is acceptable only once stated with that exception, and with K5, K1 and K2 alongside it.
- **The `this.dialog.open()` exemption hides nothing**: it strips that exact no-argument call on `ExpandedDialog`, and the rest of the line is still scanned. `K6` puts `this.dialog.open(); globalThis.open("/config/entities");` on one line, and it is red on both arms. A no-argument `open()` names no link.
- **The inert surface does not mask a census-reached row**: the census replaces `history`, `open` and `location` on both `ctx` and `ctx.window` for its own run (`K5r` is red). On rows the census does not render, though, it removes the crash that used to flag N2 and N5. Those rows now rest on the token arm alone, and that arm misses K5.
- **A press that throws is refused**: `T1b` (a synchronous throw only inside the census) and `T2b` (an async rejection) are each red on `no press throws, so no navigation primitive is swallowed`, with fails=1. My first marker, `CustomEvent.name` (T1 and T2), was wrong: the rig's class is anonymous, so those two crashed scenario 1. They are recorded, not counted.

## Verified

- **The finder's harnesses** (my own run): `card_shapes.mjs` (sha1 677b7542, from 3930b421a) and `v2_card_lines.mjs` (sha1 b3a1890e, at the head), run on the 5603ee319 card and the head card:
  - RESULT `picker_open` 3 -> 1
  - RESULT `picker_lines` 5 -> 3, `total` 36 -> 34
- **The card test**: `node tests/card.mjs` prints ALL CARD CHECKS PASSED at the head, after `plan_view.py`.
- **The release files are untouched**: `VERSION`, `manifest.json`, `RELEASE_NOTES.md`, `tests/golden`, the structure budgets and `closures.json`, checked three-dot against merge base 8087e8576.
- **The head merges cleanly**: `git merge-tree --write-tree origin/main` exits 0.
- **CI**: all 45 check-runs at the head have concluded, 30 success and 15 skipped. The range's intermediate commits carry no runs. The body's `Red checks: none` holds.
- **The forward-carry** is 9b1320d37 on origin/main, as round 3 confirmed. It is unchanged.
- **The body's head** names 1826c67c3 as a merge of the code head 56789d0ab and origin/main 8087e8576, which matches `git log`.

My instrument is my own, `mut4.py`, not the finder's. It is disclosed here.

Evidence (relative to the scratchpad, under `rev-2283-r4/evidence`): `mut4.py`, `mut4_out.txt`, `fixer_driver_out.txt`, `finder_harness.txt`, `card_head.txt`, `check_runs.txt`, `HEAD_MEASURED`.
