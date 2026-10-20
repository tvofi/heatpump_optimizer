`tests/card.mjs`'s link census (R10-DEEPLINK) now drives every handler the card
registers and reads the whole document after each drive. This closes the class
#2317 has left open: navigation written in a card handler the dynamic arm did
not drive. Closes #2317. Part of #201.

At #2345's head the dynamic arm pressed clicks only. It read markup in the
card's shadow root only. So two things rested on a spelling list:

- navigation in a keydown, pointer, wheel or other handler (RV1-RV7);
- markup appended outside the shadow root, even in a press the census drove
  (RD4, RD6).

What lands, all in `tests/card.mjs` and the driver:

- **Every listener is recorded and driven.** Each `addEventListener` call on
  any element, the window or the document is recorded with its source line.
  Each listener is driven from a fresh card:
  - on its element, and on one descendant per distinct `data-*` key set;
  - once per key literal the card compares a key with;
  - at both ends of the event fields it reads (modifiers, button, wheel
    direction, pointer type, detail).

  A listener the drive registers on the window, the document or a made
  element is then driven too: a gesture's move and up, and the slot menu's
  Escape. Fixture variants render what the five pages do not: the what-if
  panel, the advisor rows, the picker, the layout editor and the config
  editor. Each registration site is driven on the first fixture that renders
  it.
- **The read covers the whole document.** It reads the head, the body, the
  card host, every shadow root, and every element the document's factories
  made, attached or not. It reads `href`, `action` and `formaction`. A `form`
  element now counts as a way out on its own: submitted, a form with no action
  navigates to the page's own URL.
- **Reach checks.** Every `addEventListener` call site must have registered a
  listener a drive reached. A handler wired as an `on<event>` property or
  attribute is refused.
- **The static arm is bare names only.** The names are `href`, `location`,
  `pushState`, `replaceState`, `open`, `navigation`, `formaction`, `submit`,
  `requestSubmit`, `hass-more-info` and `hass-action`. The spelling rows are
  gone (fixer.md step 17; #1874 refused that shape): `history.<member>`,
  `createElement("form")`, `action` through `setAttribute`, `Reflect.set` or
  `Object.assign`, and `.submit(`.
- **Two stub gaps are closed for the census only.** The stub's selector engine
  could not answer a selector list or an unquoted attribute value. It also had
  no `setAttributeNS`. So the handlers wired through those selectors were wired
  to nothing, and no drive could reach them. `tests/dom_stub.mjs` itself is
  unchanged.
- **Residual, stated in the census.** Two kinds of code still pass:
  - code no fixture or drive executes, where only the bare names are refused;
  - markup written through a DOM member the stub does not implement (RD8, Y1;
    both green). Carry: R10-ADVISOR (roster 04a641598)

The card is unchanged.

### Round 2: every way out the dynamic arm can be handed, not only `href`

The round-1 review (comment 6270204863) found three ways out that passed the
census inside a driven handler: a head `<meta http-equiv="refresh">` (OWN1),
and the location object's `pathname` and `search` setters under a built name
(OWN2, OWN3). The location sink recorded `href`, `assign` and `replace` only,
and the read named only `href`, `action` and `formaction`.

The class rule this round enumerates: every member, alias, interface or
element through which a browser leaves the page, each reached under a name
built at run time, in the chart keydown the census drives. Each seam it returns
is closed in this diff and planted:

- **The location object records a write to any member.** It is a `Proxy` whose
  `set` and `defineProperty` traps record every member, so `href` and every URL
  part (`pathname`, `search`, `hash`, `host`, `hostname`, `port`, `protocol`)
  are recorded, through a plain write or `Object.assign`. `reload` is
  recorded beside `assign` and `replace`. Plants OWN2, OWN3, L1-L7.
- **Every road to that object.** The global and `window` already carried it
  (L8, L9, red at the base too). The document now does: `document.location`,
  assigned whole or by member (LD1, LD2). So do the window's aliases `top`,
  `parent`, `frames`, `window.window`, `window.self` and `document.defaultView`
  (LT1-LT5).
- **The interface prototypes.** `History` and `Navigation` are bound, with
  prototypes holding the same recorders, so
  `History.prototype.pushState.call(history, ...)` and
  `Object.getPrototypeOf(history).back` are recorded (IH1, IH2, IN1).
- **The document's page-replacing members.** `document.open` with a URL is
  recorded as an `open`; without one, and `write` / `writeln`, are recorded as
  `document` (DO1, DW1, DW2).
- **The refresh pragma.** The read takes any element whose `http-equiv`
  attribute or `httpEquiv` member is `refresh`, with or without a URL (OWN1,
  MR1). Its markup form is read too (MR2, MR3).
- **Markup the stub's parser drops.** The stub keeps double-quoted attributes
  only. The read now also scans the markup string each element was given, tag
  by tag, under all three quotings HTML admits (UQ1 unquoted, UQ2
  single-quoted, MR3 an unquoted pragma).
- **Timers.** A timer a drive starts (`setTimeout`, `setInterval`) is queued
  and run before that drive's read, so a navigation in its callback is recorded
  against the drive that scheduled it (TM1, TM2). Before this, the callback ran
  after the census had restored the surface.
- **`base` and `area`** were already read by `href` (B1, B2, red at the base
  too); planted so the enumeration states it.

Three controls stay green: a location read (LRc), a `meta` that is no pragma
(MRc), and a timer that does nothing (TMc). W1 read `frames` behind a feature
test, which is now bound to the window. W1 now reads `visualViewport`, a global
the rig still leaves unbound, and stays red.

The residual is unchanged: still the two kinds above. RD8 and Y1 are still
green, so the in-diff briefs' carries stay true as written.

### Round 3: one navigation surface, live before the card loads

The round-2 review found the harness class behind its three blocks (its
`rev_plants.py`, verbatim in the driver as REV_CAP1-4): the census installed
its recorders long after the card's source ran, so a reference the card took when it loaded -- `const H =
window.history`, a bound element factory, the `CustomEvent` class, a timer,
the registration method -- held the rig's `undefined` or its original, and a
use through that reference was invisible. Two more blocks landed with it: a
fixed four-round timer settle dropped a fifth nested timer unread (REV_TM5),
and the read missed an svg anchor's `xlink:href` (REV_XL1).

What changes:

- **One graph, installed before the card's source runs.** The file builds the
  whole navigation surface -- history, `open`, `location` (a Proxy over every
  URL part), the Navigation API, the `History` / `Navigation` / `Document`
  interfaces, the document's `open` / `write` / `writeln`, the two event
  classes, the four timer members, the element factories and the registration
  method -- at the top of `tests/card.mjs`, before `vm.runInContext(cardSrc,
  ctx)`. Every member reports through `navHook`, empty outside the census and
  filled inside it. The census no longer REPLACES a member -- a reference the
  card took at load would still hold the old one -- it switches the live graph
  on. CAP5-CAP13 are the class beyond the review's four: `document.write`, the
  element factory, `CustomEvent`, `setTimeout`, the registration method, the
  Navigation API, the History prototype, the location's own descriptor and a
  window alias, each taken when the card loads, each red.
- **The surface asserts its own precondition.** Before recording, the census
  checks that every global and the document still hold the graph the card
  loaded against, so a scenario that swapped one and did not put it back is a
  FAIL rather than a silent misread. Plant X34 loads the card before the
  surface; alone it is green, and paired with REV_CAP4 it leaves the capture
  green too -- the ordering line is what closes the class.
- **Timers settle to a fixpoint, and refuse.** A timer a drive starts runs
  before that drive's read until none is left, to a cap of 64 rounds; a chain
  still pending is a throw, never a silent drop. REV_TM5, five deep, is red;
  TMX, 80 deep, is red as unsettled; X35 removes the refusal and leaves TMX
  green, so the refusal is the line that closes it.
- **`xlink:href` is read.** Both the markup read and the attribute read take
  an optional `xlink:` prefix, and the stub gains `setAttributeNS` outside the
  census, so an attribute written through it sets a real attribute instead of
  a TypeError the card's own `try` swallowed. REV_XL1 is red; REV_XL1c, a plain
  href, stays red; X36 drops the `xlink` arm and leaves XL1 green.
- **The census tells itself apart by its shim.** The navigation surface is the
  same object inside and outside the census since this round, so T1c / T2c --
  a press that throws or rejects only when the census is watching -- key on
  the selector-list shim the census alone installs. Both stay red.

RD4 and RV4, a `createElementNS("form")` with `.action` set, appended to
`document.body` and submitted by a button's `click()`, are red at this head by
the document-level read (RD4 was green at #2345's head). They are not red by
the handler drive: RD4 sits in a driven click, RV4 in the chart's keydown, and
each is caught by the read that walks the body and every element the document
made, not by the drive. RD5 and RD6c, the same elements placed in the shadow
root and never submitted or clicked, stay red.

## Head

`dd74b93f458763e3ac22e9e478215f998f9e762e`. Its merge base with origin/main
is `a25de7a686767cedd5071ba7ccf3f323c3050804`, origin/main's tip at
2026-10-20T08:12:12Z, which the head merges.

It builds on the authored code head `68a94415f0db23c72199b20ef71b1d5f63742c77`,
not on the PR head `a01006c1b46bc5acd3f2c7d8ebe1232c5f4ee2a3`.
`a01006c1b` adds the orchestrator's merge `af74be911` and the delivery row
`dev/programme/delivery/2452.md` on top of `68a94415f`. Neither is in this
head's ancestry.

The commits after `68a94415f`:

- `8630c81aa`: the census change (round 1);
- `a7d2a19c1`: merges origin/main `64b0ae690`;
- `8b0726e21`: the markup read, tag by tag;
- `b3a97d1e1`: merges origin/main `4a3cbcf62` (the card's `CARD_VERSION`
  7.0.1 stamp is the only change to a file the census reads);
- `8b3ea42cb`: the X31LT2 plant (round 2);
- `e600218d3`: round 3 -- one navigation surface live before the card loads,
  the settle fixpoint and its cap, the `xlink:href` read;
- `6962b99fb`: the wip-sync transport commit, tree-identical to `e600218d3`
  (`git diff --stat e600218d3 6962b99fb` prints nothing);
- `6e710b948`: merges origin/main `0c298f6b5`. The roster conflict was
  resolved as a union: main's newer `coordinator.py:10283` reference and its
  added groups, with this branch's three carried census briefs (R10-ADVISOR,
  R10-SCORES, R10-UX-HEALTH), which supersede main's pre-fix "write no
  navigation in such a handler until R10-DEEPLINK-HANDLERS drives them" text;
- `aa5b81e58`: the driver runs node with a 4096 MB heap budget.
- `dc3c5e070`: the driver's docstring states RV4's disposition (the
  document-level read, not the drive) and T1c/T2c's shim, both as measured.
- `dd74b93f4`: merges origin/main `a25de7a68` (automatic; main's delta since
  `0c298f6b5` touches no file the census reads).

The full sweep ran in two generations across a seat crash and the two main
merges: the first 46 plants at `6e710b948` under
`NODE_OPTIONS=--max-old-space-size=4096`, the remaining 182 at `dd74b93f4`,
whose driver passes the same flag (`aa5b81e58`). The census's inputs are the
same file set at both heads: this branch's `tests/card.mjs` is identical, and
`git diff 0c298f6b5 a25de7a68 -- tests/card.mjs tests/card_rig.mjs
tests/dom_stub.mjs tests/plan_view.py custom_components/heatpump_optimizer/www`
prints nothing. The base runs used `8b3ea42c`'s tree with this head's driver.
The decisive set ran its first 15 plants at `aa5b81e58` and its last 3 at
`dd74b93f4`; `git diff aa5b81e58 dc3c5e070` is docstring text only. The null
control was re-run at `dd74b93f4`.

## Mutation proof

`python3 tools/audit/seat/r10_deeplink_mutants.py <plant>`, one plant per run,
over all 228 plants of `PLANTS` plus `--null`. Each run applies the plant, runs
`node tests/card.mjs`, and restores the file byte for byte; each driver process
ends with `restored` (8 processes: the six lanes and the two post-crash
base and decisive runs; the pre-crash generations restored after every plant in
`run()`'s `finally`, and their worktrees were clean on `git status --short`
after the crash). No process printed `NOT RESTORED`. Result: 228
`RESULT` lines, no `rc=ERR` anchor miss, and one run that exits on a crash with
no FAIL line, X7K1b, dispositioned below.

The count rule is the `RESULT` line's `rc` and `fails`.

- 151 of the 161 non-X plants are
  `rc=1 fails>=1`: every plant that must be refused, the controls documented
  red included (K3c, K5r, RV1c, RV5c, RD5, RD6c, OWN2c, REV_CAP1c, REV_CAP4c,
  REV_TM4c, REV_XL1c).
- 10 are the documented GREEN verdicts: the controls
  F1-F4, LRc, MRc and TMc; V9; the residual's witnesses RD8 and Y1.
- The 67 X plants each mutate one census line.
  - Alone, 24 are green, the line dropping something the clean card does not
    exercise through the census: X14, X15, X19, X20, X21, X24, X25, X26, X27, X28, X30, X31, X32, X33, X34, X35, X36, X3, X4, X5, X6, X7, X8, X9.
  - Paired with the plant its line closes, 21 are green, so that plant's catch
    depends on the line: X14RD9, X19V12, X20AL1, X21KD1, X24ON1, X25UL1, X26OWN2, X27OWN1, X28UQ1, X30CAP8, X30TM1, X31LT2, X32IH1, X33CAP5, X33DW1, X34CAP4, X35TMX, X36XL1, X4K3t, X5W1, X8W3.
  - 8 alone and 13 paired are `rc=1`:
    X16, X17, X18, X1, X22, X23, X29, X2, X15RV1, X16CAP6, X16RD4, X16RD7, X1K5b, X22RV1, X23FT1, X29LD1, X31LT1, X3K2b, X6Z2, X6Z, X9Z3.
- X7K1b is `rc=1 fails=0`: with the surface's `navigate` member removed, the
  card's own call throws during the diagnostics press at `tests/card.mjs`'s
  `Promise.all(...)`, so the run aborts before the census's `no press throws`
  check prints a FAIL. It is red, but it does not prove X7's necessity --
  X7 alone is green, and K1b is refused by the throw, not by a recorded
  navigation. The round-2 sweep read the same pair red.

Before and after, each round-3 plant run at both ends (base `8b3ea42c`, this
head `dd74b93f4`); `-` is not measured at the base:

| plant | base | head |
|---|---|---|
| CAP10_navigation_captured_at_load | `rc=0 fails=0` | `rc=1 fails=1` |
| CAP11_history_interface_captured_at_load | `rc=1 fails=0` (the run aborts at load) | `rc=1 fails=1` |
| CAP12_location_descriptor_captured_at_load | `rc=0 fails=0` | `rc=1 fails=1` |
| CAP13_window_alias_captured_at_load | `rc=0 fails=0` | `rc=1 fails=1` |
| CAP5_document_write_captured_at_load | `rc=1 fails=0` (the run aborts at load) | `rc=1 fails=1` |
| CAP6_create_element_captured_at_load | `rc=0 fails=0` | `rc=1 fails=1` |
| CAP7_custom_event_captured_at_load | `rc=0 fails=0` | `rc=1 fails=1` |
| CAP8_set_timeout_captured_at_load | `rc=0 fails=0` | `rc=1 fails=1` |
| CAP9_add_event_listener_captured_at_load | `rc=0 fails=0` | `rc=1 fails=1` |
| RD5_action_member_to_variable_on_rendered_form_driven | - | `rc=1 fails=1` |
| RD6_anchor_built_href_outside_root_click_driven | - | `rc=1 fails=1` |
| RD6c_anchor_built_href_in_root_driven_control | - | `rc=1 fails=1` |
| RD7_detached_anchor_built_href_click_driven | - | `rc=1 fails=1` |
| REV_CAP1_location_captured_at_load | `rc=0 fails=0` | `rc=1 fails=1` |
| REV_CAP1c_captured_location_resolves | `rc=0 fails=0` | `rc=1 fails=1` |
| REV_CAP1d_location_captured_lazily | `rc=0 fails=0` | `rc=1 fails=1` |
| REV_CAP2_history_captured_at_load | `rc=0 fails=0` | `rc=1 fails=1` |
| REV_CAP3_open_captured_at_load | `rc=0 fails=0` | `rc=1 fails=1` |
| REV_CAP4_history_captured_at_load_literal | `rc=0 fails=0` | `rc=1 fails=1` |
| REV_CAP4c_window_captured_at_load_control | `rc=1 fails=1` | `rc=1 fails=1` |
| REV_FM1_form_from_markup_no_action | `rc=1 fails=1` | `rc=1 fails=1` |
| REV_PR1_history_back_in_unawaited_promise_chain | `rc=1 fails=1` | `rc=1 fails=1` |
| REV_PX1_proxy_wrapped_anchor_href | `rc=1 fails=1` | `rc=1 fails=1` |
| REV_RF1_reflect_set_location_hash | `rc=1 fails=1` | `rc=1 fails=1` |
| REV_RF2_reflect_define_location_search | `rc=1 fails=1` | `rc=1 fails=1` |
| REV_TM4c_history_back_four_timeouts_deep_control | `rc=1 fails=1` | `rc=1 fails=1` |
| REV_TM5_history_back_five_timeouts_deep | `rc=0 fails=0` | `rc=1 fails=1` |
| REV_WO1_defaultview_open_built | `rc=1 fails=1` | `rc=1 fails=1` |
| REV_XL1_svg_xlink_href_markup | `rc=0 fails=0` | `rc=1 fails=1` |
| REV_XL1c_svg_plain_href_markup_control | `rc=1 fails=1` | `rc=1 fails=1` |
| RV1c_history_dot_back_control | - | `rc=1 fails=1` |
| RV2_history_optional_back_in_undriven_keydown | - | `rc=1 fails=1` |
| RV3_history_destructure_in_undriven_keydown | - | `rc=1 fails=1` |
| RV4_form_ns_action_member_button_click_in_undriven_keydown | - | `rc=1 fails=1` |
| RV5_action_member_to_variable_in_undriven_keydown | - | `rc=1 fails=1` |
| RV5c_action_member_to_literal_control | - | `rc=1 fails=1` |
| RV6_object_assign_quoted_action_key_in_undriven_keydown | - | `rc=1 fails=1` |
| RV7_create_element_ns_form_in_undriven_keydown | - | `rc=1 fails=1` |
| TMX_history_back_eighty_timeouts_deep | `rc=0 fails=0` | `rc=1 fails=1` |
| X34CAP4_load_order_is_what_closes_REV_CAP4 | - | `rc=0 fails=0` |
| X34_card_loads_before_the_surface | - | `rc=0 fails=0` |
| X35TMX_cap_refusal_is_what_closes_TMX | - | `rc=0 fails=0` |
| X35_settle_cap_drops_silently | - | `rc=0 fails=0` |
| X36XL1_xlink_read_is_what_closes_REV_XL1 | - | `rc=0 fails=0` |
| X36_no_xlink_read | - | `rc=0 fails=0` |

16 plants are green at the base and red at the head: the
captured-at-load class (REV_CAP1, CAP1c, CAP1d, CAP2, CAP3, CAP4, CAP6-CAP10,
CAP12, CAP13), the settle fixpoint (REV_TM5, five timers deep) and the cap
(TMX, 80 deep, green at the base because the fixed four rounds dropped it
silently), and the read (REV_XL1). 9 are red at both ends, already
guarded at the base: REV_CAP4c, REV_FM1, REV_PR1, REV_RF1, REV_RF2, REV_PX1,
REV_TM4c, REV_WO1, REV_XL1c. CAP5 and CAP11 do not run at the base at all:
there the card loads before the surface, so at load `document.write.bind` and
`History.prototype` are undefined and the run aborts -- the defect, measured.

## Null control

`python3 tools/audit/seat/r10_deeplink_mutants.py --null` prints
`RESULT mutant=NULL_no_plant rc=0 fails=0` at `dd74b93f4`: the control that a
green plant's `rc=0 fails=0` is the census passing, not the runner's own
crash. The driver runs node with `--max-old-space-size=4096`; at the default
the same command dies rc=134 (the measurement is in `run()`).

`node --max-old-space-size=4096 tests/card.mjs` at this head prints `ALL CARD
CHECKS PASSED`, with 1260 `  ok` lines and 0 `  FAIL`. The count rule is
`grep -c` of each line prefix in its output. The plan payload came from
`tests/plan_view.py`, which ran here (rc=0).

## Figures

Each command ran at this head, with the seat's `venv-ci` and
`tests/hastub` first on `PYTHONPATH`. The census runs used
`--max-old-space-size=4096`: the 46 plants before the crash under node 20.10.0
with `NODE_OPTIONS`, the 182 after it under node 23.6.0 with the driver's own
flag (`aa5b81e58`).

- `node --max-old-space-size=4096 tests/card.mjs`: `ALL CARD CHECKS PASSED`,
  1260 `  ok` lines, 0 `  FAIL`, 159.43 s user and 322.45 s real on a loaded
  8-core box. The count rule is `grep -c '  ok '` and `grep -c '  FAIL'` of
  its output. The same command without the flag dies rc=134 (SIGABRT,
  "Ineffective mark-compacts near heap limit").
- `python3 tools/audit/seat/r10_deeplink_mutants.py --null`: `RESULT
  mutant=NULL_no_plant rc=0 fails=0`.
- `python3 tests/closure.py select --diff a25de7a686767cedd5071ba7ccf3f323c3050804 --workdir <dir>`:
  `MODE: SCOPED -- 3 script(s) run, 30 scoped out`. `scope.run` names
  `tests/plan_view.py`, `tests/card.mjs` and `tests/card_drift.mjs`; all three
  ran here.
- `node tests/card_drift.mjs a25de7a686767cedd5071ba7ccf3f323c3050804`:
  `card_drift: identical in all 40 states`.
- The `run_always` lines, each rc=0: `python3 tests/env_drift.py --claims-only
  a25de7a686767cedd5071ba7ccf3f323c3050804` (`claims hygiene: ... ok`),
  `python3 tests/closure.py selftest` (`ALL 124 closure shrink pins PASSED`),
  `python3 tests/harness_headers.py` (`ALL 109 HARNESS HEADER CHECKS PASSED`),
  `python3 tests/layout.py` (`layout self-test: ok`).
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- The rest of the gate: `python3 tests/entities.py` `ALL 2358 ENTITY CHECKS
  PASSED`; `python3 tests/features.py` `ALL 4232 FEATURE CHECKS PASSED`;
  `python3 tests/arch_score_head.py` `ALL 18 ARCHITECTURE SCORE HEAD CHECKS
  PASSED`; `python3 tests/deployment_shape.py` `ALL DEPLOYMENT SHAPE CHECKS
  PASSED`; `python3 tests/doc_claims.py` `ALL 169 checks PASSED`;
  `python3 tests/plan_view.py` rc=0.
- `node tools/policy/brief_lint.mjs dev/programme/rosters/wave-r10-groups.json`:
  `TOTAL: 0 error(s) across 1 file(s)` (3 warnings).
- `python3 -I tools/audit/carry_audit.py check --body BODY.md`: 9 finding
  item(s), 9 routed, 0 unrouted, 0 bad destination(s).
- Claim files, `VERSION`, the manifest version, the `RELEASE_NOTES.md`
  heading, `tests/dom_stub.mjs` and the card are untouched:
  `git diff --stat origin/main HEAD -- tests/golden/claimed_drift.txt
  tests/golden/card_claimed_drift.txt VERSION
  custom_components/heatpump_optimizer/manifest.json RELEASE_NOTES.md
  tests/dom_stub.mjs custom_components/heatpump_optimizer/www | wc -l` prints
  `0`.
- The three-dot diff is 3 files, 928 insertions and 335 deletions:
  `dev/programme/rosters/wave-r10-groups.json`, `tests/card.mjs` and
  `tools/audit/seat/r10_deeplink_mutants.py`. `git diff --name-only
  origin/main HEAD` names the same three, so the merges reverted no file main
  had written.
- The class rule (fixer.md step 8), round 3: every global the census records
  through is one graph installed before the card loads, and each is planted --
  REV_CAP1-4 (the review's four), CAP5-CAP13 (the rest of the graph), TMX (the
  settle cap) and REV_XL1 (the read). The table below gives each base and head
  verdict; the seams the enumeration returns are all red at the head, and the
  ones green at the base are the finding.
- The census's own reach check `the census drove a listener from every
  addEventListener site in the card` is one of the 1260 `ok` lines above.

## Red checks

- `pr-contract` at the PR head `b69ac5c165` (job 118349952504):
  `carry_audit.py check` refused two UNROUTED body items -- `18cf0de3`, the
  Round 2 bullet "Deferred work.", and `e5c04ce8`, the Forward-carry paragraph
  "Round 2 changes none of those terms". Both were body phrasing that read as
  a finding lead, not a defect in this diff: the bullet is retitled "Timers.",
  and the paragraph opens `n/a:`. `python3 -I tools/audit/carry_audit.py check
  --body BODY.md` on this body reads `CARRY-AUDIT: ... 0 unrouted, 0 bad
  destination(s)`; the figure is re-taken in ## Figures.

## Forward-carry

`dev/programme/rosters/wave-r10-groups.json`, in this diff. The briefs of the
three live card groups (R10-ADVISOR, R10-SCORES and R10-UX-HEALTH) carried
#2345's census refusals. Those were the spelling rows, "write no navigation in
an undriven handler" and "append no markup outside the shadow root". Each brief
now carries this census's terms instead:

- every `addEventListener` site must be driven on a census fixture, or the
  same PR adds one; Carry: R10-ADVISOR (roster 04a641598)
- `on<event>` wiring is refused; Carry: R10-ADVISOR (roster 04a641598)
- the static arm's eleven bare names; Carry: R10-ADVISOR (roster 04a641598)
- the residual, with its control (RV1 red, RD8 green), re-measured at the
  stage's own merge base. Carry: R10-ADVISOR (roster 04a641598)

n/a: rounds 2 and 3 change none of those terms. The briefs list the ways out the dynamic
arm records as examples ("a history member, a form or its action, an anchor
anywhere in the document"). The residual they export is still the census's two
kinds, with the same witnesses: RV1 red and RD8 green at `dd74b93f4`.

R10-UX-SETUP is `done` and is not a destination. Carry: dismissed: a done group, nothing to route

## Friction

- `fixer.md: contradiction: the seat's setup line sources /etc/profile.d/hpo-toolchain.sh, which exports BASH_ENV pointing at itself, so every bash -c re-puts the venv's python ahead of a test's stub PATH; tests/entities.py's graders-head-copy delivery_status case then reads 1 of 2346 checks failed, at the merge base c09d61dc9 as at this head, and prepr.sh's closures step refused on it; under env -u BASH_ENV it prints ALL 2346 ENTITY CHECKS PASSED.` Carry: R10-POLICY-FIXER-MD (roster 04a641598)
- `fixer.md: cost: tests/card.mjs takes 159.43 s of CPU (322.45 s real on this shared box), and the 182 plants of the round-3 sweep left after the crash took 3 h 18 m across six lanes; the rule each drive needs a fresh render is what makes the census honest and also what prices it.` Carry: R10-RCA-FRICTION (roster 04a641598)
- `tools/audit/seat/r10_deeplink_mutants.py: cost: the census's live set -- every element the document's factories made, held for the whole run -- passes node's default old space: `node tests/card.mjs` alone dies rc=134 (SIGABRT, "Ineffective mark-compacts near heap limit") at the 2096 MB default, where 2560 MB completes rc=0 at 1 233 567 744 B peak RSS and 4096 MB at 841 007 104 B. The driver now passes `--max-old-space-size=4096`, so its documented null-control command runs as documented.` Carry: R10-RCA-FRICTION (roster 04a641598)
