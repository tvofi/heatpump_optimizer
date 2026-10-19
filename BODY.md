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
    both green). Carry: R10-ADVISOR

The card is unchanged.

## Head

`68a94415f0db23c72199b20ef71b1d5f63742c77`. Its merge base with origin/main is
`05c39d3a6597e02c81f07e771a058da90f8ebb46`. The full mutant sweep ran at
`8ad272ef656adbc828bb5521b327266893f7b09e`, in three sweep worktrees. That
commit differs from this head by the merge of origin/main's #2435 only (the
learner, its tests and ledger files; no file this diff touches).

This is a re-carry of the handoff onto current main: the old tip conflicted in
the roster. `dev/programme/rosters/wave-r10-groups.json` was re-applied by JSON
load and dump on main's briefs (R10-ADVISOR, R10-SCORES, R10-UX-HEALTH); the
`tests/card.mjs` merge was automatic.

## Mutation proof

The driver is unchanged by this re-carry. The full 137-plant sweep ran at
`8ad272ef656adbc828bb5521b327266893f7b09e` (three worktrees, 46, 46 and 45
plants), each plant applied, `node tests/card.mjs` run, the file restored byte
for byte. Result: 137 `RESULT` lines.

- 107 plants are `rc=1` with at least one FAIL line, none a crash (no `tail:`
  line, no `rc=ERR`). That is every plant that must be refused, including the
  controls the driver documents as red (K3c, K5r, RV1c, RV5c, RD6c).
- 7 are the documented GREEN verdicts: F1, F2, F3 and F4 (the controls), V9,
  and the residual's witnesses RD8 and Y1.
- 23 are the X plants that mutate a census line. Alone, X3, X4, X6, X9, X14,
  X15, X19, X20, X21, X24 and X25 are green: dropping the line breaks nothing
  the census itself checks. Paired with the plant the line closes, X4K3t,
  X14RD9, X19V12, X20AL1, X21KD1, X24ON1 and X25UL1 are green: that plant's
  catch depends on the line. The rest of the X plants are `rc=1` (X17 returns
  28 undriven sites and X18 returns 6, the figures in `## Figures`).

The drift from the sweep's tree to this head is the #2435 merge only, which
touches no file the driver mutates.

## Null control

`python3 tools/audit/seat/r10_deeplink_mutants.py --null` at this head prints
`RESULT mutant=NULL_no_plant rc=0 fails=0`.

`node tests/card.mjs` (at `8ad272ef6`, the sweep's tree) prints `ALL CARD
CHECKS PASSED` with 1259 `ok` lines and 0 FAIL lines. The two checks this
change adds are the site-reach check and the inline-handler check.

## Figures

- `node tests/card.mjs`: `ALL CARD CHECKS PASSED`, 1259 `ok`, 0 FAIL. This Mac
  has no Home Assistant stack for `tests/plan_view.py` (it stops at
  `ModuleNotFoundError: No module named 'paho'`), so the run read an existing
  plan payload from another checkout through `HPO_PLANDATA`, and it needed
  `NODE_OPTIONS=--max-old-space-size=12288` on this loaded box (the default heap
  aborts). CI regenerates the payload. The figures below that name `c09d61dc9`
  are the earlier head's and were not re-run here.
- `node tests/card_drift.mjs c09d61dc9c9779e721eb73b1ea402913a52242fb`:
  `card_drift: identical in all 40 states`.
- `python3 tests/closure.py select --diff c09d61dc9c9779e721eb73b1ea402913a52242fb --workdir <dir>`:
  `MODE: SCOPED -- 3 script(s) run, 30 scoped out`. `scope.run` names
  `tests/plan_view.py`, `tests/card.mjs` and `tests/card_drift.mjs`, and all
  three were run here.
- The `run_always` lines, with `PYTHONPATH=tests/hastub`, each `rc=0`:
  - `python3 tests/env_drift.py --claims-only c09d61dc9c9779e721eb73b1ea402913a52242fb`;
  - `python3 tests/closure.py selftest`;
  - `python3 tests/harness_headers.py`;
  - `python3 tests/layout.py`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py`:
  `ALL 2346 ENTITY CHECKS PASSED`. The roster file in this diff puts it in
  `prepr.sh`'s closure recording. With the seat's `BASH_ENV` set it reads
  `1 of 2346 ENTITY CHECKS FAILED`, the same at the merge base (see
  `## Friction`).
- `node tools/policy/brief_lint.mjs dev/programme/rosters/wave-r10-groups.json`:
  `TOTAL: 0 error(s) across 1 file(s)`.
- The census's own cost, `node tests/card.mjs`, measured on this 4-core box:
  54.6 s at the merge base (`time`), 3 min 11 s at this head (`date -u`
  around the run). That is about 3.5x. The added time is the handler drive,
  one fresh render per drive. CI recorded 18.7 s for this script in
  `tests/closures.json`.
- The class rule (fixer.md step 8). The seams are enumerated by the census's
  own check `the census drove a listener from every addEventListener site in
  the card`. It returns every `addEventListener` call site, out of the card's
  87, that no drive reached.
  - With the fixture variants removed (X17, at `8018f67e1`) it returned 28
    sites: the away strip, the advisor rows, the what-if panel's buttons and
    inputs, the picker, the layout editor and the config editor.
  - With the selector shim removed (X18) it returned 6 sites, in the what-if
    panel: `input[type=time]`, and the quiet and wood selector lists.

  Each of those sites is closed in this diff, by a fixture variant or by the
  shim. At this head the check returns none (`ok`).
- Seams outside that enumeration, each with its disposition:
  - an `on<event>` handler: closed, ON1;
  - markup outside the shadow root: closed for the body (RD9), for made
    elements (RD7) and for the host's light DOM;
  - DOM members the stub lacks: residual, RD8 and Y1, stated in the census;
  - event field values other than the two ends: residual, stated;
  - code no fixture reaches: residual, stated.
- Claim files, `VERSION`, the manifest version and the `RELEASE_NOTES.md`
  heading are untouched: `git diff --stat c09d61dc9c9779e721eb73b1ea402913a52242fb...HEAD --
  tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt VERSION
  custom_components/heatpump_optimizer/manifest.json RELEASE_NOTES.md` prints
  nothing.

## Red checks

none

## Forward-carry

`dev/programme/rosters/wave-r10-groups.json`, in this diff. The briefs of the
three live card groups (R10-ADVISOR, R10-SCORES and R10-UX-HEALTH) carried
#2345's census refusals. Those were the spelling rows, "write no navigation in
an undriven handler" and "append no markup outside the shadow root". Each brief
now carries this census's terms instead:

- every `addEventListener` site must be driven on a census fixture, or the
  same PR adds one; Carry: R10-ADVISOR
- `on<event>` wiring is refused; Carry: R10-ADVISOR
- the static arm's eleven bare names; Carry: R10-ADVISOR
- the residual, with its control (RV1 red, RD8 green), re-measured at the
  stage's own merge base. Carry: R10-ADVISOR

R10-UX-SETUP is `done` and is not a destination. Carry: dismissed: a done group, nothing to route

## Friction

- `fixer.md: contradiction: the seat's setup line sources /etc/profile.d/hpo-toolchain.sh, which exports BASH_ENV pointing at itself, so every bash -c re-puts the venv's python ahead of a test's stub PATH; tests/entities.py's graders-head-copy delivery_status case then reads 1 of 2346 checks failed, at the merge base c09d61dc9 as at this head, and prepr.sh's closures step refused on it; under env -u BASH_ENV it prints ALL 2346 ENTITY CHECKS PASSED.` Carry: R10-POLICY-FIXER-MD
- `fixer.md: cost: tests/card.mjs goes from 54.6 s to 3 min 11 s on this box, and a full 137-plant sweep took about 3 h on 4 cores; the rule each drive needs a fresh render is what makes the census honest and also what prices it.` Carry: R10-RCA-FRICTION
