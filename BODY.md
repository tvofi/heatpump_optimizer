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
- **Deferred work.** A timer a drive starts (`setTimeout`, `setInterval`) is
  queued and run before that drive's read, so a navigation in its callback is
  recorded against the drive that scheduled it (TM1, TM2). Before this, the
  callback ran after the census had restored the surface.
- **`base` and `area`** were already read by `href` (B1, B2, red at the base
  too); planted so the enumeration states it.

Three controls stay green: a location read (LRc), a `meta` that is no pragma
(MRc), and a timer that does nothing (TMc). W1 read `frames` behind a feature
test, which is now bound to the window. W1 now reads `visualViewport`, a global
the rig still leaves unbound, and stays red.

The residual is unchanged: still the two kinds above. RD8 and Y1 are still
green, so the in-diff briefs' carries stay true as written.

## Head

`8b3ea42cbd45fcb30fefe03d2e74a79876f5c1c0`. Its merge base with origin/main is
`4a3cbcf62e6f5e7b6594d376d714388caf2915cf`, which was origin/main's tip at
2026-10-19T21:20:52Z.

It builds on the authored code head `68a94415f0db23c72199b20ef71b1d5f63742c77`,
not on the PR head `a01006c1b46bc5acd3f2c7d8ebe1232c5f4ee2a3`.
`a01006c1b` adds the orchestrator's merge `af74be911` and the delivery row
`dev/programme/delivery/2452.md` on top of `68a94415f`. Neither is in this
head's ancestry.

The commits after `68a94415f`:

- `8630c81aa`: the census change;
- `a7d2a19c1`: merges origin/main `64b0ae690`;
- `8b0726e21`: the markup read, tag by tag;
- `b3a97d1e1`: merges origin/main `4a3cbcf62` (the card's `CARD_VERSION`
  7.0.1 stamp is the only change to a file the census reads);
- `8b3ea42cb`: the X31LT2 plant.

Both merges were automatic.

The full sweep ran at `8b0726e21d83738c8a76e968698e322362387f05`, in four lane
copies taken with `git archive`. The base runs used `68a94415f`'s tree with
this head's driver. From the sweep's tree to this head, the files the census
reads changed in one line only. `git diff 8b0726e21 HEAD -- tests/card.mjs
tests/card_rig.mjs tests/dom_stub.mjs tests/plan_view.py
custom_components/heatpump_optimizer/www` shows the `CARD_VERSION` line alone.
The driver gained one plant.

## Mutation proof

`python3 tools/audit/seat/r10_deeplink_mutants.py <plant>`, one plant per run,
over all 191 plants of `PLANTS` plus `--null`, at `8b0726e21`. Each run
applies the plant, runs `node tests/card.mjs`, and restores the file byte for
byte. Result: 192 `RESULT` lines, 191 `restored` lines, and no `rc=ERR` or
`tail:` line (so no crash and no anchor miss).

The count rule is the `RESULT` line's `rc` and `fails`.

- 124 of the 134 non-X plants are `rc=1` with at least one FAIL line. That is
  every plant that must be refused, including the controls documented red
  (K3c, K5r, RV1c, RV5c, RD6c, OWN2c).
- 10 are the documented GREEN verdicts:
  - the controls F1, F2, F3, F4, LRc, MRc and TMc;
  - V9;
  - the residual's witnesses RD8 and Y1.
- The 57 X plants each mutate one census line.
  - Alone, 22 are green: X3-X9, X14, X15, X19-X21, X24-X33. Each drops a line
    the clean card does not exercise.
  - Paired with the plant its line closes, these 16 are green, so that
    plant's catch depends on the line: X4K3t, X5W1, X8W3, X14RD9, X19V12,
    X20AL1, X21KD1, X24ON1, X25UL1, X26OWN2, X27OWN1, X28UQ1, X29LD1, X30TM1,
    X32IH1, X33DW1.
  - The other 19 are `rc=1`. X31LT1 is one of them: with the aliases off, the
    census's watch still refuses `top` by name, because the card's code
    mentions `top` 64 times.
- So `X31LT2_aliases_are_what_close_LT2` was added and run at this head. It
  reads `rc=0 fails=0`, while LT2 alone reads `rc=1 fails=1`: the alias line
  is what closes `parent`, which the card never mentions.

Before and after, each round-2 plant (base `68a94415f` with this head's
driver, then head `8b0726e21`):

| plant | base | head |
|---|---|---|
| OWN1 meta refresh, head | rc=0 fails=0 | rc=1 fails=1 |
| OWN2 `location.pathname`, built | rc=0 fails=0 | rc=1 fails=1 |
| OWN2c `location.href`, built (control) | rc=1 fails=2 | rc=1 fails=2 |
| OWN3 `location.search`, built | rc=0 fails=0 | rc=1 fails=1 |
| L1 hash | rc=0 fails=0 | rc=1 fails=1 |
| L2 host | rc=0 fails=0 | rc=1 fails=1 |
| L3 hostname | rc=0 fails=0 | rc=1 fails=1 |
| L4 port | rc=0 fails=0 | rc=1 fails=1 |
| L5 protocol | rc=0 fails=0 | rc=1 fails=1 |
| L6 reload | rc=0 fails=0 | rc=1 fails=1 |
| L7 `Object.assign(location, ...)` | rc=0 fails=0 | rc=1 fails=1 |
| L8 global location assigned | rc=1 fails=1 | rc=1 fails=1 |
| L9 `window.location` assigned | rc=1 fails=1 | rc=1 fails=1 |
| LD1 `document.location` assigned | rc=0 fails=0 | rc=1 fails=1 |
| LD2 `document.location.pathname` | rc=0 fails=0 | rc=1 fails=1 |
| LT1 `top` | rc=1 fails=1 | rc=1 fails=1 |
| LT2 `parent` | rc=0 fails=0 | rc=1 fails=1 |
| LT3 `frames` | rc=0 fails=0 | rc=1 fails=1 |
| LT4 `window.self` | rc=0 fails=0 | rc=1 fails=1 |
| LT5 `document.defaultView` | rc=0 fails=0 | rc=1 fails=1 |
| IH1 `History.prototype.pushState` | rc=0 fails=0 | rc=1 fails=1 |
| IH2 `getPrototypeOf(history).back` | rc=0 fails=0 | rc=1 fails=1 |
| IN1 `Navigation.prototype.navigate` | rc=0 fails=0 | rc=1 fails=1 |
| DO1 `document.open(url, ...)` | rc=0 fails=0 | rc=1 fails=1 |
| DW1 `document.write` | rc=0 fails=0 | rc=1 fails=1 |
| DW2 `document.writeln` | rc=0 fails=0 | rc=1 fails=1 |
| MR1 pragma as the `httpEquiv` member | rc=0 fails=0 | rc=1 fails=1 |
| MR2 pragma, quoted markup | rc=0 fails=0 | rc=1 fails=1 |
| MR3 pragma, unquoted markup | rc=0 fails=0 | rc=1 fails=1 |
| B1 `base`, built href | rc=1 fails=1 | rc=1 fails=1 |
| B2 `area`, built href, detached | rc=1 fails=1 | rc=1 fails=1 |
| UQ1 unquoted built href, markup | rc=0 fails=0 | rc=1 fails=1 |
| UQ2 single-quoted built href, markup | rc=0 fails=0 | rc=1 fails=1 |
| TM1 `history.back` in a timeout | rc=0 fails=0 | rc=1 fails=1 |
| TM2 `history.back` in an interval | rc=0 fails=0 | rc=1 fails=1 |
| LRc location read (control) | rc=0 fails=0 | rc=0 fails=0 |
| MRc meta, no pragma (control) | rc=0 fails=0 | rc=0 fails=0 |
| TMc timer, no work (control) | rc=0 fails=0 | rc=0 fails=0 |
| W1 unbound global, feature test | rc=1 fails=1 | rc=1 fails=1 |

So 29 plants are green at the base and red at the head (the finding and its
class reproduce, then close). Seven are red at both ends: L8, L9, LT1, B1 and
B2 were already guarded, OWN2c is the review's red control, and W1 is the
retargeted watch plant. The three controls are green at both ends. The table is the
base lane's 39 `RESULT` lines against the head sweep's, by name.

## Null control

`python3 tools/audit/seat/r10_deeplink_mutants.py --null` prints
`RESULT mutant=NULL_no_plant rc=0 fails=0`, at this head and at the sweep's
tree `8b0726e21`.

At this head, `node tests/card.mjs` prints `ALL CARD CHECKS PASSED`, with 1259
`  ok` lines and 0 `  FAIL` lines. The count rule is `grep -c` of each line
prefix in its output. The plan payload came from `tests/plan_view.py`, which
ran here (rc=0).

## Figures

Each command ran at this head, with the seat's venv first on `PATH` and under
`env -u BASH_ENV`. Each `PYTHONPATH=tests/hastub` command used it.

- `node tests/card.mjs`: `ALL CARD CHECKS PASSED`, 1259 `ok`, 0 FAIL, in 163 s.
  That run had `NODE_OPTIONS=--max-old-space-size=12288` on this loaded 8-core
  box.
  - The first round-2 form scanned markup with a lookbehind over each
    element's whole markup string. It cost 9 min a run under a five-lane
    load, against about 3 min a run on the base lane in the same load.
  - Read tag by tag (`8b0726e21`), the census ran in 2 min 42 s alone.
- `python3 tests/closure.py select --diff 4a3cbcf62e6f5e7b6594d376d714388caf2915cf --workdir <dir>`:
  `MODE: SCOPED -- 3 script(s) run, 30 scoped out`. `scope.run` names
  `tests/plan_view.py`, `tests/card.mjs` and `tests/card_drift.mjs`. All three
  ran here.
- `node tests/card_drift.mjs 4a3cbcf62e6f5e7b6594d376d714388caf2915cf`:
  `card_drift: identical in all 40 states`.
- The `run_always` lines, each `rc=0`:
  - `python3 tests/env_drift.py --claims-only 4a3cbcf62e6f5e7b6594d376d714388caf2915cf`;
  - `python3 tests/closure.py selftest`;
  - `python3 tests/harness_headers.py`;
  - `python3 tests/layout.py`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/entities.py`: `ALL 2351 ENTITY CHECKS PASSED`.
- `node tools/policy/brief_lint.mjs dev/programme/rosters/wave-r10-groups.json`:
  `TOTAL: 1 error(s) across 1 file(s)`.
  - The error is `[R10-SCORES] coordinator.py:10281: 'heat_loss_coefficient'
    not found ... found at line 1075 instead`.
  - It is main's coordinator drift under R10-SCORES's brief, not this diff's.
    The round-1 review read it identically at merge base `4e1b36070`.
  - This diff's three-dot change to the roster is the three briefs' census
    paragraph, with no `path:line` reference.
- The class rule (fixer.md step 8), round 1. The census's own check `the
  census drove a listener from every addEventListener site in the card`
  returns each `addEventListener` call site no drive reached. The card has 87
  such sites.
  - With the fixture variants removed (X17) it returns 28 sites. With the
    selector shim removed (X18) it returns 6. Both are red at this head
    (X17 rc=1, X18 rc=1).
  - At this head it returns none (`ok`).
- The class rule, round 2: the enumeration in the Round 2 section above. Each
  seam it returns has a plant in the table above, with its disposition:
  - closed in this diff: 29;
  - already guarded and red at the base: L8, L9, LT1, B1, B2.
  - Each new recorder or read line has its X pair, green when paired, as
    listed in `## Mutation proof`.
  - The one alias pair that is red (X31LT1) is answered by X31LT2.
- Seams outside both enumerations, each with its disposition:
  - an `on<event>` handler: closed, ON1;
  - markup outside the shadow root: closed for the body (RD9), for made
    elements (RD7) and for the host's light DOM;
  - DOM members the stub lacks: residual, RD8 and Y1, stated in the census
    (both green at `8b0726e21`);
  - event field values other than the two ends: residual, stated;
  - code no fixture reaches: residual, stated.
- Claim files, `VERSION`, the manifest version, the `RELEASE_NOTES.md`
  heading, `tests/dom_stub.mjs` and the card are untouched. The check was
  `git diff --stat 4a3cbcf62e6f5e7b6594d376d714388caf2915cf...HEAD --
  tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt VERSION
  custom_components/heatpump_optimizer/manifest.json RELEASE_NOTES.md
  tests/dom_stub.mjs custom_components/heatpump_optimizer/www | wc -l`, which
  prints `0`.
- The three-dot diff is 3 files, 727 insertions and 237 deletions:
  `dev/programme/rosters/wave-r10-groups.json`, `tests/card.mjs` and
  `tools/audit/seat/r10_deeplink_mutants.py`.

## Red checks

none

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

Round 2 changes none of those terms. The briefs list the ways out the dynamic
arm records as examples ("a history member, a form or its action, an anchor
anywhere in the document"). The residual they export is still the census's two
kinds, with the same witnesses: RV1 red and RD8 green at `8b0726e21`.

R10-UX-SETUP is `done` and is not a destination. Carry: dismissed: a done group, nothing to route

## Friction

- `fixer.md: contradiction: the seat's setup line sources /etc/profile.d/hpo-toolchain.sh, which exports BASH_ENV pointing at itself, so every bash -c re-puts the venv's python ahead of a test's stub PATH; tests/entities.py's graders-head-copy delivery_status case then reads 1 of 2346 checks failed, at the merge base c09d61dc9 as at this head, and prepr.sh's closures step refused on it; under env -u BASH_ENV it prints ALL 2346 ENTITY CHECKS PASSED.` Carry: R10-POLICY-FIXER-MD (roster 04a641598)
- `fixer.md: cost: tests/card.mjs goes from 54.6 s to 3 min 11 s on this box, and a full 137-plant sweep took about 3 h on 4 cores; the rule each drive needs a fresh render is what makes the census honest and also what prices it.` Carry: R10-RCA-FRICTION (roster 04a641598)
