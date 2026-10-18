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
    both green).

The card is unchanged.

## Head

`04c7314202e357bfdd1d4816be16d4adf34772d3`. Its merge base with origin/main is
`c09d61dc9c9779e721eb73b1ea402913a52242fb`. The full mutant sweep ran at
`8018f67e1876640d059ec6a45480f88f4cc50aac`. That commit's tree differs from
this head in two places only:

- the roster's three brief carries;
- the driver's `F1` plant, re-measured at this head, below.

`git diff 8018f67e1876640d059ec6a45480f88f4cc50aac 04c7314202e357bfdd1d4816be16d4adf34772d3 --stat`
names only `dev/programme/rosters/wave-r10-groups.json` and
`tools/audit/seat/r10_deeplink_mutants.py`.

## Mutation proof

Each plant is one mutation applied by
`tools/audit/seat/r10_deeplink_mutants.py`, which restores the file byte for
byte. The sweep ran in four detached worktrees at `8018f67e1`:

    python3 tools/audit/seat/r10_deeplink_mutants.py <every plant in PLANTS>

**Count rule:** a `RESULT` line per plant, with red meaning `rc=1` and at least
one FAIL line. Result: 137 plants, 108 red, 29 green, 0 crashes. A crash is
`rc=1 fails=0`; the count of `rc=1 fails=0` and `rc=ERR` lines is 0. All four
worktrees printed `restored`.

**The brief's controls**, at the merge base (`c09d61dc9`, this head's driver
copied outside the tree) and then at the head:

| plant | merge base | head | check at head |
|---|---|---|---|
| RV1-RV7 | each `rc=0 fails=0` | each `rc=1 fails=1` | `every link the census records from a press is one haLink builds for this entry` |
| RV1c, RV5c | each `rc=1 fails=1` | each `rc=1 fails=1` | same |
| RD4, RD6 | each `rc=0 fails=0` | each `rc=1 fails=1` | same |
| RD5, RD6c | each `rc=1 fails=1` | each `rc=1 fails=1` | same |
| Y1 | `rc=0 fails=0` | `rc=0 fails=0` | residual witness, by design |

RV4 and RD4 are a form appended to `document.body`. RV7 is a form with no
action; the form row is what reds it. At the merge base, RV1c, RV5c, RD5 and
RD6c were red on `no navigation token in the card's code outside navigateTo`.

**New plants**, green at the merge base and red at the head:

- RD7, a detached anchor;
- RD9, `document.body.innerHTML` with a built href;
- ON1, an `onkeydown` property, red on `the card wires no handler outside addEventListener`;
- UL1, a listener site no fixture renders, red on `the census drove a listener from every addEventListener site in the card`.

AL1, KD1 and FT1 are red at both ends. At the merge base their
`globalThis.history.back()` matched the retired `history.<member>` row. Their
X pairs below show the drive is what closes them now.

RD8 stays green at both ends: `insertAdjacentHTML`, which the stub does not
implement, is the residual witness.

**This fix's lines**, each alone and paired with the plant it closes. Read by
FAIL line:

- **X14** (read the host and made elements, not the head or body). Alone it is
  green. With RD9 it is green: the body read alone closes RD9. With RD4 the
  link FAIL stays, because the form is a made element.
- **X16** (made elements untracked). Alone it is red on reach. With RD7 only
  the reach FAIL remains and RD7's link FAIL is gone: tracking is what closes
  RD7.
- **X17** (no variants) and **X18** (selector shim off). Each alone is red on
  reach.
- **X19** (no `setAttributeNS`). Alone it is green. With V12 it is green.
- **X20** (no alt drive). Alone it is green. With AL1 it is green.
- **X21** (no key drive). Alone it is green. With KD1 it is green.
- **X22** (own target only). Alone it is red on reach. With RV1 the link FAIL
  is gone.
- **X23** (no follow-through). Alone it is red on reach. With FT1 the link FAIL
  is gone.
- **X24** (inline check off). Alone it is green. With ON1 it is green.
- **X25** (reach counts only driven sites). Alone it is green. With UL1 it is
  green.
- **X15** (drop the five plain pages from `FIXTURES`). Alone it is green, and
  with RV1 it is red: the variants render every site the pages do. The pages
  stay because they are the cheaper render. Without them, `node tests/card.mjs`
  took 3 min 49 s against 3 min 11 s on this box. No verdict needs them, and
  the census comment says so.

**Verdicts the retired spelling rows change** (plants of #2345):

- **V9** goes red to green. It is an attribute node built and attached to
  nothing, so it names no way out.
- **X6Z, X6Z2, X9Z3 and X3K2b** go green to red. Each of their plants sits in
  a handler the census now drives, or is a form, so a second line closes it.

These carry over from #2345 unchanged:

- F2-F4 green;
- X3-X9 alone green;
- X4K3t, X5W1 and X8W3 green;
- X7K1b red on `no press throws`.

**F1** read `sensor`, a name not bound in the keydown handler. Once that
handler was driven, the census refused it on `no primitive this census does not
instrument is reached for on a page or a press`: `rc=1 fails=1` at `8018f67e1`.
The control is repaired to compare the handler's own `key`. At this head:
`python3 tools/audit/seat/r10_deeplink_mutants.py F1_action_as_a_setattribute_value_control`
prints `rc=0 fails=0`.

## Null control

`python3 tools/audit/seat/r10_deeplink_mutants.py --null` prints `RESULT
mutant=NULL_no_plant rc=0 fails=0`:

- in each of the four sweep worktrees at `8018f67e1`;
- at this head;
- at the merge base, with this head's driver.

`node tests/card.mjs` prints `ALL CARD CHECKS PASSED` with 1259 `ok` lines and
0 FAIL lines. The merge base has 1257 `ok` lines. The two added checks are the
site-reach check and the inline-handler check.

## Figures

- `PYTHONPATH=tests/hastub python3 tests/plan_view.py` then `node tests/card.mjs`:
  `ALL CARD CHECKS PASSED`, 1259 `ok`, 0 FAIL.
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
  same PR adds one;
- `on<event>` wiring is refused;
- the static arm's eleven bare names;
- the residual, with its control (RV1 red, RD8 green), re-measured at the
  stage's own merge base.

R10-UX-SETUP is `done` and is not a destination.

## Friction

- `fixer.md: contradiction: the seat's setup line sources /etc/profile.d/hpo-toolchain.sh, which exports BASH_ENV pointing at itself, so every bash -c re-puts the venv's python ahead of a test's stub PATH; tests/entities.py's graders-head-copy delivery_status case then reads 1 of 2346 checks failed, at the merge base c09d61dc9 as at this head, and prepr.sh's closures step refused on it; under env -u BASH_ENV it prints ALL 2346 ENTITY CHECKS PASSED.`
- `fixer.md: cost: tests/card.mjs goes from 54.6 s to 3 min 11 s on this box, and a full 137-plant sweep took about 3 h on 4 cores; the rule each drive needs a fresh render is what makes the census honest and also what prices it.`
