_Requested by **tvofi**_

Bug 7, the dashboard card's history view. Closes nothing: no issue exists.

The owner's report: "Card history has never worked as intended. Date is
clearly not correct historical data and especially temperature trends swings
eratically with no correlation with reality. Heating slots still not shown,
still only irrelevant power slots".

**Before.** Panning the plan chart into the past could draw one sensor's
history under another sensor's name: whenever any of the four numeric
sensors had recorded nothing in a 12 h window, Home Assistant left it out
of the answer and the card, reading the answer by position, shifted every
later series one place (the house temperature drew the outdoor temperature,
the outdoor line drew the price). The pump's recorded power was frozen at
whatever it was at the last mode change, because Home Assistant by default
only returns the rows where the mode itself changed. The past showed no
space-heating or hot-water slots at all, only one teal "actioned power"
series of total commanded power. The measured temperatures were drawn as a
smooth curve through the recorder's 0.1 K steps, on an axis fitted to the
data alone, so a 0.1 K flicker filled the plot height.

**After.** Each history list is matched to its sensor by the entity id Home
Assistant puts on its first row, so a missing sensor draws nothing instead
of shifting the others. The action query asks for every row
(`significant_changes_only=0`), so every recorded power update draws. The
past draws the same space and hot-water slot bars as the plan: a
`hot_water` run on the hot-water series, every other heating mode on the
space series, at the recorded power; the mode band along the plot base
stays, and an install that records no power draws no bars (the band still
shows when the pump ran). Measured temperatures are drawn as held steps up
to "now" (the forecast after it keeps its curve), and the temperature axis
never spans less than 2 K. The future (the plan) is untouched.

Root causes, each verified against the code at the merge base before it was
changed:

- **RC1 (verified).** `HistorySource.fetchChunk` assigned the numeric
  answer by index; HA's `/api/history/period` filters out entities with
  zero rows ("Filter out the empty lists if some states had 0 results").
  Now keyed by `rows[0].entity_id`.
- **RC2 (verified).** The heat_pump_action query omitted
  `significant_changes_only`, whose HA default "1" drops a sensor row
  whose state did not change. `historyPath` now adds
  `significant_changes_only=0` to the attribute-carrying (non-lean) query.
- **RC3 (verified).** No past slot series existed; `absorb` emitted only
  `action_power` points on the `actioned` series. It now emits
  `space_power` / `dhw_power` partial points from the action rows that
  carry `power_kw` (or are unavailable, which stays a hole), merged into the
  space and DHW overlays. The `actioned` series keeps its chip, band and
  tooltip row and carries no points. Known limit, not closed here:
  `power_kw` is the whole commanded draw (`commanded_power_kw`), so a step
  that ran both circuits under a space mode lands on the space series
  entire; heat_pump_action publishes no per-circuit split.
- **RC4b (verified).** `seriesPath` drew every `smooth` series through
  `smoothLine`, recorded points included, and `axisRange` had no minimum
  span. `buildSeries` now marks recorded points `measured`, `seriesPath`
  draws the leading measured run with `steppedLine`, and the temperature
  axis gets `TEMP_AXIS_MIN_SPAN` (2 K) centred on the data.

The rig's `historyApi` stub (tests/card_rig.mjs) now serves HA's semantics,
which is what lets the new checks fail at the merge base: empty lists are
dropped, the first row of every list (every row of a non-lean query) carries
`entity_id`, and under significant-changes-only a row repeating its
predecessor's state is dropped **when it carries attributes**. That last
clause is a design choice of the stub: a bare repeat (the grid
`historyFixture`'s own sample) is served as written, since the recorder
would not have written it at all, and treating it as an attribute update
made "the measured irradiance renders left of now" depend on the host's time
of day. `realisticHistory`'s action rows now walk the optimizer's own mode
ladder (off, eco, hot_water, pre_heat, normal) with a `power_kw` that moves
under an unchanged mode.

Three existing checks pinned the replaced behaviour and were restated:
"the pump's own action record renders as a power series" became "... as past
slot bars"; "power_kw, where the attribute exists, still draws the overlay"
became "... draws the past slot bars"; "the realistic fixture produces a path
worth asking about" now accepts an `L`-only path, since the measured stretch
is stepped and cannot run backward (the backward-in-time check it guards
still runs on every path).

## Head

6caefba8449f77524f2e49a002d10ba66eec1761. Merge base
67a0cb9816565113447bb54415989090706435b4 (origin/main at the branch cut).
The commit on top of it adds only this file, under `tools/audit/`, which
`tests/closure.py`'s INERT list covers.

## Mutation proof

Each fix's production line(s) replaced in the working tree, `node
tests/card.mjs` run, file restored (byte-identity asserted after the loop):

- RC1 positional mapping restored → FAIL "an indoor sensor with no recorded
  rows draws no measured indoor trace", "the outdoor trace carries its own
  sensor's rows when another entity is dropped", "the price trace carries
  its own sensor's rows when another entity is dropped".
- RC2 `significant_changes_only=0` deleted → FAIL "every recorded power_kw
  update draws its own past slot step".
- RC3 the two slot `emit` calls deleted → FAIL "the pump's own action record
  renders as past slot bars", "power_kw, where the attribute exists, draws
  the past slot bars", "the recorded past draws its space and DHW slots from
  the action record", "every recorded power_kw update draws its own past
  slot step".
- RC3 power-attribute filter made `true` → FAIL "without a power attribute
  no past slot bar is drawn".
- RC4b `held` forced to 0 → FAIL "the measured temperatures are drawn as
  held steps, not a fitted curve".
- RC4b minimum-span pad forced to 0 → FAIL "a flat measured temperature
  keeps a temperature axis of at least 2 K".

## Null control

At the merge base's card with this branch's tests and rig, `node
tests/card.mjs` fails nine checks and nothing else: the seven new ones (the
three RC1 checks, the RC3 and RC2 slot checks, the two RC4b checks) and the
two restated slot-bar checks ("the pump's own action record renders as past
slot bars", "power_kw, where the attribute exists, draws the past slot
bars"); at the head it passes all. The added null control "without a power
attribute no past slot bar is drawn" passes at both ends and fails under the
RC3 filter mutation above; before that filter existed, card_drift showed
the no-power state drawing zero-height DHW bars mid-plot, which is why the
control asks for no point at all rather than no positive one. The investigation's harness (repro.mjs, sha1
aba70837839eee647ac34a25c6d76d0a2b3d8978, run with the card path swapped
between the base export and the head) reads the RC1 shift at the base
(`'room'` plots the outdoor rows) and none at the head (`'room'` n=0,
`'outdoor'` equals the outdoor rows). Its CAUSE2 stub ignores the query, so
a companion (repro_c2.mjs, sha1 9654f98e28b093991f3ef2f832798cddb0d87bfd,
the same stub honouring `significant_changes_only`) reads 7 of 96 action
rows absorbed at the base and 96 of 96 at the head.

Seams of the class (the card reading a history/period answer): `grep -n
"callApi(" custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`
returns two call sites, both in `fetchChunk`. The numeric call is closed in
this diff. The action call asks for one entity id, so its `res[0]` is that
entity or absent (absent reads as `[]`); it stays as written. Seams of the
drawing class: `grep -n '"smooth"'` returns three series (outdoor,
dhw_temp, house_temp); the stepped branch is in `seriesPath`, which all
three share, and only outdoor and house_temp receive recorded points.

## Figures

- 9 checks fail at the merge base, 0 at the head: `PYTHONPATH=tests/hastub
  node tests/card.mjs` with the card at 67a0cb9 and at 6caefba, tests and
  rig at 6caefba.
- 3 card_drift states moved and claimed, 37 identical: `PYTHONPATH=tests/hastub
  node tests/card_drift.mjs 67a0cb9816565113447bb54415989090706435b4`.
- repro 7/96 → 96/96 absorbed action rows: `node repro_c2.mjs` with `CARD`
  set to the base export and to the head card.
- scoped gate: `python3 tests/closure.py select --diff
  67a0cb9816565113447bb54415989090706435b4 --workdir "$D"` prints `MODE:
  SCOPED -- 8 script(s) run, 18 scoped out`; `GATE_SCOPE=auto
  GOLDEN_MODE=drift GOLDEN_REF=67a0cb9816565113447bb54415989090706435b4
  ./tests/run.sh` ran them: ok for env_drift.py (--claims-only and
  --all), closure.py selftest, plan_view.py, card.mjs, card_drift.mjs,
  features.py, harness_headers.py and deployment_shape.py; golden.py
  printed its drift-mode SKIP (fixtures go through env_drift.py
  --all); entities.py FAILED on two
  HANDOVER `updated-for` ancestry checks only, because the local clone was
  shallow (the check's own message says a shallow clone cannot answer it;
  this diff does not touch `docs/HANDOVER.md`). After `git fetch
  --unshallow origin`, with origin/main unchanged at 67a0cb9,
  `python3 tests/entities.py` prints `ALL 1924 ENTITY CHECKS PASSED`.
  stress.py was not selected, so no gate lease was taken.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.

## Red checks

none

## Forward-carry

none

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code) https://claude.ai/code/session_01GkTHXz5AEFdwvcCLvpJSrY
