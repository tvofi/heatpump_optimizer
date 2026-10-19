Fix review: blocked b69ac5c1657df26fa3a9d973fbd851beca93a144 harness: class-open nav-surface-captured-at-card-load (REV_CAP4 history captured at load, back() in the driven keydown, green at head; control red)

Round: this is the **round-2** review of R10-DEEPLINK-HANDLERS (#2452, closes #2317). Round 1 blocked on census gaps; a third block would make a fourth round a re-cut (fix-review.md).
Measured head: b69ac5c1657df26fa3a9d973fbd851beca93a144 (still refs/pull/2452/head at posting). Merge base 4a3cbcf62e6f5e7b6594d376d714388caf2915cf = origin/main tip. Role files: `git diff $(merge-base)...origin/main -- dev/governance/roles/` empty, so current.

## Blocking

1. **class-open: a reference to the navigation surface captured at card evaluation escapes both arms.** tests/card.mjs runs the card source at line 53, before the inert navigation shape (line ~295) and long before the census installs its sink (~11750). So a value the card takes at load (`const H = window.history;`, `const L = location;`, `const o = open;`) is `undefined` in the rig, while a browser hands the live object; a later write through it in a *driven* handler throws inside its own try in the rig and navigates in a browser. The static arm no longer refuses `history` (the spelling rows went; `back` is no bare name), so the literal spelling passes too.
   - `RESULT mutant=REV_CAP4_history_captured_at_load_literal rc=0 fails=0` — top-level `const __revH = window.history;`, keydown `try { __revH.back(); } catch (_e) {}`, no built name at all.
   - `RESULT mutant=REV_CAP4c_window_captured_at_load_control rc=1 fails=1` — same shape capturing `window` and reading `.history` at drive time: red, so the drive reaches the line and the gap is the capture.
   - Same seam, built names: REV_CAP1 (location.pathname) rc=0, REV_CAP2 (history.back) rc=0, REV_CAP3 (open) rc=0, REV_CAP1d (lazily captured) rc=0. REV_CAP1c, my resolve control, is rc=0: it shows the captured location is not an object in the rig, i.e. the cause above.
   - The body's class rule ("every member, alias, interface or element through which a browser leaves the page, each reached under a name built at run time, in the chart keydown") enumerates *where* the surface is reached, not *when* it was taken; this seam is neither in the diff nor dispositioned. A fix in kind: bind the inert navigation surface before `vm.runInContext(cardSrc)` and have the census sink be the *same objects* (mutate recorders onto them rather than replacing `ctx.history` etc.), or refuse load-time captures of the surface.

2. **class-open (deferred work, bounded): `settle` runs at most 4 rounds.** `RESULT mutant=REV_TM5_history_back_five_timeouts_deep rc=0 fails=0` against `REV_TM4c_history_back_four_timeouts_deep_control rc=1 fails=1`. The body says deferred work is closed; a fifth nested timer is cleared unread. Either loop to a fixpoint (with a cap that FAILs when hit, not clears) or state the bound as residual.

3. **class-open (markup): an SVG anchor's `xlink:href`.** `RESULT mutant=REV_XL1_svg_xlink_href_markup rc=0 fails=0` (`document.body.innerHTML += \`<svg><a xlink:${built href}="/config/integrations">…\``); `REV_XL1c_svg_plain_href_markup_control rc=1 fails=1`. `MARKUP_WAY_OUT` requires `\s` before `href` and the node read asks `getAttribute("href")`; the HTML parser places `xlink:href` in the XLink namespace and the anchor navigates. The census shims `setAttributeNS` for exactly this attribute but not its markup form.

4. **pr-contract is red on this head and the body says `## Red checks: none`.** Both pr-contract runs (jobs 118349772063, 118349952504, started 22:46:32Z and 22:47:01Z, after the body's 22:46:25Z edit) fail on `carry_audit.py check`: `UNROUTED body item 18cf0de3` (Round 2, "Deferred work" bullet) and `UNROUTED body item e5c04ce8` (Forward-carry, "Round 2 changes none of those terms…"); `CARRY-AUDIT: 10 finding item(s): 8 routed, 2 unrouted`. The body owes `Carry:` markers (or a non-finding rewording). `closures` and `Analyze (python)` were still in progress when read, so this is not posted as root-cause-unanswered; the carry refusal stands on its own.

## Verified (finder's driver, tools/audit/seat/r10_deeplink_mutants.py, my own RESULT lines)

Head b69ac5c1657df26fa3a9d973fbd851beca93a144:
- `RESULT mutant=NULL_no_plant rc=0 fails=0`
- `RESULT mutant=F1_action_as_a_setattribute_value_control rc=0 fails=0`
- `RESULT mutant=RD8_insert_adjacent_html_built_href_driven_residual rc=0 fails=0` (residual witness, green as stated)
- `RESULT mutant=Y1_runtime_name_on_unresolved_selector_residual rc=0 fails=0` (residual witness, green as stated)
- `RESULT mutant=OWN1_meta_refresh_in_keydown rc=1 fails=1`; `OWN2_location_pathname_built_in_keydown rc=1 fails=1`; `LT2_parent_location_pathname_built rc=1 fails=1`; `TM1_history_back_in_timeout rc=1 fails=1`
- X pairs: `X31LT2_aliases_are_what_close_LT2 rc=0 fails=0`, `X30TM1_settle_is_what_closes_TM1 rc=0 fails=0` — the alias line and settle are what close LT2 and TM1.

Base = merge base 4a3cbcf62 (main's census) with the head's driver:
- `NULL_no_plant rc=0 fails=0`; `OWN1 rc=0 fails=0`; `OWN2 rc=0 fails=0`; `LT2 rc=0 fails=0` — reproduce at base, closed at head.
- `TM1_history_back_in_timeout rc=1 fails=1` at 4a3cbcf62 (`no navigation token in the card's code outside navigateTo` — main's `history.<member>` spelling row). The body's base for its table is round-1 head 68a94415f, where it reads rc=0; so "29 green at base" is against 68a94415f, not against main. Not re-derived for all 29 (I re-ran 4 of 39 table rows at each end).

My own adversarial plants (reviewer-built, `ev/rev_plants.py`, run through the finder's `run()`), red at head as they should be: REV_RF1 `Reflect.set(location,"hash")` rc=1; REV_RF2 `Reflect.defineProperty(location,"search")` rc=1; REV_WO1 `document.defaultView[built open]` rc=1; REV_PX1 Proxy-wrapped anchor, built href, click() rc=1; REV_FM1 a form from markup, no action rc=1; REV_PR1 history.back three `.then`s deep, unawaited rc=1. Not planted, dispositioned: iframe `src`/`srcdoc` navigate the frame, not the page (a `target=_top` link inside needs a user click inside the frame); `window.open` is covered via all aliases tried.

Figures re-taken at head: `node tests/card_drift.mjs 4a3cbcf62…` → `card_drift: identical in all 40 states`; `tests/structure.py` → `STRUCTURE RATCHET PASSED`; `PYTHONPATH=tests/hastub tests/entities.py` → `ALL 2351 ENTITY CHECKS PASSED`; `closure.py select --diff 4a3cbcf62` → `MODE: SCOPED -- 3 script(s) run, 30 scoped out.`; `env_drift.py --claims-only` rc=0; claim files, VERSION, manifest, RELEASE_NOTES heading, dom_stub.mjs and the card untouched (wc -l 0). `git merge-tree --write-tree origin/main b69ac5c1657df26fa3a9d973fbd851beca93a144` rc=0 (tree a5a7927cb), no conflict. Three-dot diff at this head is 4 files / 728+ 237- (the body's 3 files / 727+ is 8b3ea42cb; the 4th is the orchestrator's delivery row). 1259 ok / 2m42s and the full 191-plant sweep counts not re-derived (cite only).

bus-nonce: 4a722016d2bcc2faa75204235021970d
