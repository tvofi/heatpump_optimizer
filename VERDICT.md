Fix review: blocked 0c78705926a8af8910996b876ca9ddbc922cbef7 harness: class-open replaceState, globalThis.open and location= navigations pass the census and the static guard

bus-nonce: eb728ebf950f1cab2e3ec31b3a4d9bf3

This is round 3. I reviewed from a detached worktree at 0c78705926a8af8910996b876ca9ddbc922cbef7, and that head was re-read before posting. The roles diff against origin/main is empty. The card blob is cb4035b6, byte-identical to 0b4d46abd. `tests/card.mjs` is b3db20da, the same at the code head 8960c7019. The delta from round 2 is `tests/card.mjs` only.

The next round is round 4. From there `fixer.md` owes a re-cut, not a repair (`fix-review.md`, last line).

## Blocking

**R7b is closed, but the census's own class is still open.** The body states that `pushState` is the card's only history write. The static check is named "navigateTo is the card's only way out: no other history write, navigation, ...". At this head, three ordinary navigation spellings pass every check, each planted right after the pending `settings`/`diagnostics` button's `navigateTo(SETTINGS_PATH);`:

- `N1t`: `try { globalThis.history.replaceState(null, "", "/config/entities"); globalThis.dispatchEvent(new CustomEvent("location-changed")); } catch (_e) {}`. This is Home Assistant's own `navigate(path, {replace: true})` shape, wrapped in a `try` exactly as `navigateTo` is. Result: `RESULT mutant=N1t_replaceState_in_try_after_pending_push rc=0 fails=0`.
- `N3t`: `try { globalThis.open("/config/entities", "_self"); } catch (_e) {}`. Result: `RESULT mutant=N3t_globalThis_open_in_try rc=0 fails=0`.
- `N4`: `globalThis.location = "/config/entities";`. Result: `RESULT mutant=N4_location_assign_bare rc=0 fails=0`.

These are not obfuscations. The card already spells its history access `globalThis.history`, and the guard misses them for two reasons:
- **The dynamic arm** replaces `ctx.history` with `{ pushState }` only. It does not instrument `open` or the `location` setter, so the first two throw inside the press and are swallowed, and the third assigns a vm global nobody reads.
- **The static arm** counts only `.pushState(` and names only `window.open(` and `location.(href|assign|replace)`.

Without the `try`, N1, N2 (replaceState on `dismiss_feedback`), N3 and N5 (`open` on `dismiss_feedback`) are "killed" only because an earlier, unrelated press test crashes on the stub's missing method (`rc=1`, no FAIL line). That is an accident of the stub, not a check.

**The href guard is a spelling list, and four more spellings of R7b's own shape pass.** Each was planted on an `<a class="zz">` set at attach through `"a.zz"`, which the stub cannot resolve, so only the static arm can see it:
- `` H2 setAttribute(`href`, ...) ``: `rc=0 fails=0`
- `H4 Reflect.set(a, "href", ...)`: `rc=0 fails=0`
- `H5 Object.assign(a, { href: ... })`: `rc=0 fails=0`
- `H6 a["href"] = ...`: `rc=0 fails=0`
- `H7 a.attributes.setNamedItem(<href attr>)`: `rc=0 fails=0`

The same spellings on a selector the stub resolves are red on the dynamic read (H1 and H3: `every link a button emits ...`).

**The fix is a re-cut, not a fifth regex.** Every round so far has added the spelling the last reviewer planted. One sound shape would be:
- **The static arm becomes token-based, not spelling-based.** Refuse any source line outside `haLink`/`navigateTo` that mentions the token `href` in any quoting, `location`, `replaceState`, `pushState` or `.open(`. Only the split-string residual below would survive that.
- **The dynamic arm instruments every primitive it claims to refuse.** That means `history.pushState`/`replaceState`, `open`, and a `location` setter, so a press that uses one is recorded, not thrown and swallowed.

Re-run N1t, N3t, N4 and H2 to H7 against it; my driver is in the evidence (`mut3.py`).

## Verified (the delta's claims)

- **All fourteen of the fixer's plants were re-run at this head** with a copy of the fixer's `round2_mutants.sh`, cd'd into my worktree. Each is red on the checks the body names: M1 to M6, R4, R5, R6, R6b, R6c, R7b (static guard), R7c and R7d (`every link a button emits ...`).
- **My R7b control, now planted through `.zz`, is red on both arms** (H10: the census reports `health:a -> href ...` and the static guard reports the `setAttribute` line).
- **Pending rows now excuse only their own push.** R7d's after-press walk, the `via` field and the stale check keyed on `push <path>` are as the body says.
- **H8 is red on the static guard.** It is an `innerHTML` anchor with single-quoted `href`, which the stub's parser does not read.
- **H9t is red on the static guard.** It is a template-literal `insertAdjacentHTML` anchor.
- **The finder's harnesses agree at both ends.** Sources: `card_shapes.mjs` sha1 677b7542 from 3930b421a, and `v2_card_lines.mjs` sha1 b3a1890e from handoff/audit-r10-catchup-verify, run on the 5603ee319 card and the head card:
  - RESULT `card_shapes`: total 33 -> 31, dead 1 -> 2 (`openHaLink`)
  - RESULT `v2_card_lines`: picker_lines 5 -> 3, total 36 -> 34
- **The card test passes at this head.** `node tests/card.mjs` prints ALL CARD CHECKS PASSED, after `tests/plan_view.py` with `PYTHONPATH=tests/hastub`.
- **The release files are untouched:** `VERSION`, `manifest.json`, `RELEASE_NOTES.md` and `tests/golden`, against merge base 613b10c51.
- **The head merges cleanly:** `git merge-tree --write-tree origin/main` exits 0.
- **CI is green:** all 45 check-runs at this head concluded 30 success and 15 skipped. The intermediate commits carried no runs.
- **The forward-carry is on main:** 9b1320d37 is an ancestor of origin/main, and the roster text names the PENDING rows for R10-ADVISOR and R10-UX-HEALTH.

## Residual, not blocking

Split-string attribute or event names (`"hr" + "ef"`, `"hass-" + "more-info"`) still survive a static check, as in round 2. The dynamic arm catches them only on rendered rows.

Evidence: the evidence directory published with this verdict (`mut3.py`, `mut3_out.txt`, `mut3_rerun.txt`, `mut3_try.txt`, `fixer_driver_out.txt`, `finder_harness.txt`, `check_runs.txt`, `card_head.txt`, `HEAD_MEASURED`).
