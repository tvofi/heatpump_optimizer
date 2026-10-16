`tests/card.mjs`'s link census (R10-DEEPLINK, #2283) is the guard that every
route out of the card goes through `haLink`. Its own round-4 review (#2317)
measured four routes that passed both of its arms, three of them with no string
trick at all: a bare `open(` on the feedback row the fixture never rendered, the
Navigation API, a `<form action>` on a rendered page, and an `Event`-built
`hass-more-info`. Both arms were spelling lists -- a token denylist over the
source, and four instruments whose reach depended on which rows the fixture
happened to render -- so each review round closed the last round's spellings and
found the next round's.

This closes the class on three seams instead, which is the shape the review
asked for (allow a known set; do not deny spellings):

- **Rows.** The census's fixture renders every row the card can put an `act`
  branch behind, and the reach check keys on the card's own `act === "..."` and
  literal `data-act` rows, compared with the census's declaration in *both*
  directions. A row that stops being rendered is a red reach check, not a token
  arm's private business. The slot menu's `add` and `remove` are reached through
  the chart's contextmenu gesture, the only route to them.
- **One surface, two arms.** `NAV_SURFACE` declares the navigation surface once
  and `navShapeInert` is that surface as an object graph: the static arm refuses
  a mention of any member in the card's code, the census wraps each member of the
  graph with a recorder, and every scenario before the census runs against the
  inert graph. An anchor's `href`, the location object, the history object, a
  qualified or bare `open(`, the Navigation API, `<form`, `action=`,
  `formaction` and both HA router events are the members.
- **An allow list.** The dynamic arm presses every element the shadow root wires
  to a click (the dialog's head, close button and tabs included, which the
  earlier form left out), records any event whose type the source does not write
  as a literal -- whatever class built it, the plain `Event` included -- reads
  `href`, `action` and `formaction` off the markup after every press, and
  refuses by name any global the card's code mentions that neither the global
  nor `window` binds. A spelling that *builds* a member's name reaches the same
  instrument, because every member is installed by name.

The inert graph and the token list are two readers of one declaration, which is
what keeps the surface self-maintaining: the scenario before the census must not
crash on a member (a plant killed only by an earlier scenario's crash is `rc=1`
with no FAIL line, so the census's arms never ran and nothing was measured), and
a member present on one side and absent on the other would hide a plant for the
opposite reason.

The residual neither arm reaches is written in the census's own header: a
surface name built at run time inside code no press reaches (a pointer, wheel or
keyboard handler). The static arm still refuses that surface's names wherever
they are written.

The census's global-name scan shares the identifier word grammar with
`tests/doc_claims.py`, which the agreement lane refuses as a grammar written
twice and unregistered; the copy is now registered in
`tools/policy/agreement.mjs` (class I4, the file the lane reads) and disclosed
where the scan lives.

Closes #2317.

## Head

`7ee88aa3b673e2b547b6549537413c9e01edfc10`, two commits on `92accb2cf` (the
merge base, `origin/main` at 2026-10-16T22:11Z). Everything below was measured
at that SHA.

## Mutation proof

Every plant is one mutation, applied by `tools/audit/seat/r10_deeplink_mutants.py`,
which restores the file byte for byte and refuses to start on a dirty tree.
`K*` are the round-4 review's plants (#2317) and this fix's isolating variants;
`W*` are two seams this fix found for itself; `X*` mutate this fix's own lines.

At the head, all 27 plants:

    python3 tools/audit/seat/r10_deeplink_mutants.py K5_bare_open_on_dismiss K5b_bracket_open_on_dismiss K5c_open_call_on_dismiss K5r_bare_open_rendered_control K1_navigation_api_in_try K1c_navigation_api_no_try K1b_navigation_name_built K2_form_action_rendered K2b_action_set_at_run_time K3t_event_runtime_more_info K3c_event_literal_more_info_control Z_open_in_undriven_keydown W1_guarded_frames W2_history_go_built X1_fixture_drops_feedback_row X1K5b_fixture_line_is_what_closes_K5b X2_card_gains_an_act_branch X3_anchors_drop_action X3K2b_anchors_line_is_what_closes_K2b X4_recordEvent_disabled X4K3t_recordEvent_line_is_what_closes_K3t X5_watch_swallows X5W1_watch_line_is_what_closes_W1 X6_surface_drops_bare_open X6Z_surface_member_is_what_closes_Z X7_sink_drops_navigation X7K1b_surface_member_names_the_primitive_K1b

Every one of the 22 plants and composites is rc=1 with a FAIL line, `fails=1`
or `fails=2`, and none is killed only by a crash tail; the five `X*` singles
with no plant under them are green (the composites' controls, below).

- **K5, K5b, K5c** (a bare, a bracketed and a `.call`-ed `open(` on the feedback
  row the old fixture never rendered): `every link the census records from a
  press is one haLink builds for this entry` -> `advisor:dismiss_feedback ->
  open /config/entities`. K5 is red on the static arm as well.
- **K1, K1c** (the Navigation API, with and without its `try`): the static arm
  and `advisor:settings -> navigation /config/entities`. The `try` no longer
  decides between a FAIL and a crash.
- **K1b** (the same navigation with the name *built*): one FAIL, `...
  -> navigation /config/entities`. At the merge base this plant is `rc=1
  fails=0` -- a crash with no FAIL line.
- **K2** (a `<form action>` on the health page): the static arm and `...
  -> action /config/entities`. **K2b** (the same action set at run time, so no
  token sees it): `advisor:settings -> action /config/integrations/...`.
- **K3t** (a plain `Event`, its type built at run time): `advisor:settings ->
  event hass-more-info:{}`.
- **K5r, K3c**: the review's own controls, red at *both* ends -- they name the
  spellings the old denylist already held, so they measure that this fix did not
  simply move the hole.
- **Z** (a bare `open(` inside the chart's keydown handler, which no press
  reaches): red on the static arm here, green at the merge base.
- **W1** (a feature-tested read of a global this census does not bind): `no
  primitive this census does not instrument is reached for on a page or a
  press` -> `frames`; green at the merge base.
- **W2** (the history object's back step, behind a built name): `...
  -> history go(-1)`; at the merge base `rc=1 fails=0`, a crash.

This fix's own lines, each mutated *under the plant it closes*, with the single
mutant as that composite's control:

- **X1** (the fixture's feedback row) -> the act-reach check red, naming
  `dismiss_feedback` unpressed and the other ten pressed. **X1K5b**: with the
  row gone, K5b's link is no longer recorded -- its only FAIL is that reach
  check -- so the fixture line is what feeds the sink.
- **X2** (the card gains an `act` branch the census does not declare) -> `the
  act set the census declares is the one the card's source dispatches`
  (`source-only navigate_home`).
- **X3** (drop `action`/`formaction` from the anchor read) + K2b -> green; X3
  alone is green. **X4** (disable the event-type recorder) + K3t -> green; X4
  alone green. **X5** (the unknown-global recorder swallows instead of
  refusing) + W1 -> green; X5 alone green. **X6** (drop the bare-open surface
  member) + Z -> green; X6 alone green.
- **X7** (drop the Navigation API's `navigate` recorder) + K1b -> red, but on
  `no press throws`: without the member the same plant is caught only as a
  `TypeError` inside a press, which is what a member installed by name
  replaces. X7 alone is green.

At the merge base, in a detached worktree with THIS BRANCH's driver copied in
(the driver is part of the fix):

    git worktree add --detach /tmp/r10-base 92accb2cf
    cd /tmp/r10-base && cp <head>/tools/audit/seat/r10_deeplink_mutants.py tools/audit/seat/
    PYTHONPATH=tests/hastub python3 tests/plan_view.py
    python3 tools/audit/seat/r10_deeplink_mutants.py K5_bare_open_on_dismiss K5b_bracket_open_on_dismiss K5c_open_call_on_dismiss K5r_bare_open_rendered_control K1_navigation_api_in_try K1c_navigation_api_no_try K1b_navigation_name_built K2_form_action_rendered K2b_action_set_at_run_time K3t_event_runtime_more_info K3c_event_literal_more_info_control Z_open_in_undriven_keydown W1_guarded_frames W2_history_go_built

prints: `K5` rc=0 fails=0, `K5b` rc=0 fails=0, `K5c` rc=0 fails=0, `K1` rc=0
fails=0, `K2` rc=0 fails=0, `K2b` rc=0 fails=0, `K3t` rc=0 fails=0, `Z` rc=0
fails=0, `W1` rc=0 fails=0 -- the nine routes that escaped both old arms;
`K1c` rc=1 fails=0, `K1b` rc=1 fails=0, `W2` rc=1 fails=0 -- killed only by a
crash tail; `K5r` rc=1 fails=1 and `K3c` rc=1 fails=1 -- the review's own
controls. The `X*` names do not exist at the merge base (`anchor not unique`),
which is the right refusal.

## Null control

`python3 tools/audit/seat/r10_deeplink_mutants.py --null` prints `RESULT
mutant=NULL_no_plant rc=0 fails=0`; `node tests/card.mjs` alone prints
`ALL CARD CHECKS PASSED`; the same null is green at the merge base, so every red
above is the plant's. The five `X*` singles with no plant under them (`X3`, `X4`,
`X5`, `X6`, `X7`) are green, which is what makes each composite a measurement of
its line rather than of the plant.

## Figures

All run from this branch's head, after `PYTHONPATH=tests/hastub python3
tests/plan_view.py`, except where the merge base is named.

- `1253` passing checks at the head, `1249` at the merge base --
  `node tests/card.mjs | grep -c "^  ok  "`.
- The card's own `act` set is the `ACTS` the census declares, both derived and
  both 11 names -- `grep -oE '\bact === "[a-z_]+"' custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js | sort -u`
  and `grep -oE 'data-act="[a-z_]+"' custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js | sort -u`.
- `42/25/10/32/24` pressables pressed on plan/setup/savings/advisor/health --
  the `X2_card_gains_an_act_branch` detail line.
- `MODE: SCOPED -- 4 script(s) run, 29 scoped out` over
  `dev/programme/rosters/wave-r10-groups.json`, `tests/card.mjs`,
  `tools/audit/seat/r10_deeplink_mutants.py` and `tools/policy/agreement.mjs` --
  `python3 tests/closure.py select --diff 92accb2cf --workdir <dir>`.
- `AGREEMENT ok` with the census's global-name scan registered --
  `python3 -I tools/policy/agreement_py.py --out /tmp/ag.json && node
  tools/policy/agreement.mjs --py-json /tmp/ag.json` (before the entry:
  `unregistered=1`, `"[A-Za-z_$][\w$]*" in tests/card.mjs, tests/doc_claims.py`).
- `8 TEST SCRIPT(S) PASSED; 27 SCOPED OUT AND NOT RUN`, the scoped gate (units
  lane included) --
  `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=92accb2cf ./tests/run.sh`.
- `STRUCTURE RATCHET PASSED` with every metric unmoved (`max_method_loc 373 <=
  373`, `seam_cut_total 752 <= 752`) -- `python3 tests/structure.py`; the diff
  adds no production line.
- `ALL 16 ARCHITECTURE SCORE HEAD CHECKS PASSED` -- `python3
  tests/arch_score_head.py`.

## Red checks

`none`.

## Forward-carry

`dev/programme/rosters/wave-r10-groups.json`: the `brief` of R10-UX-SETUP,
R10-ADVISOR, R10-UX-HEALTH and R10-SCORES now names the census's new refusals --
a new `data-act` row or `act` branch is red until the census renders and presses
a row that drives it, and a new mention of a `NAV_SURFACE` member outside
`navigateTo` is red at once -- and says to extend the census in the pull request
that adds the row, and to delete that stage's row from the census's `PENDING`
table as it converts the link. That file is in this diff. The orchestrator's
copy of the same roster on `handoff/audit-r10-roster` is the newer of the two and
is the orchestrator's to bring level from this one (finding-propagation.md: while
two copies disagree, the newer is right and the other is the bug).

## Friction

- `finding-propagation.md: stale: this group's brief carries R10-TICK (o) -- "`train.sh` line 182 sets the checkout with dirname of `$0` followed by `../..`" -- but at 92accb2cf `tools/audit/seat/train.sh:233` derives it with `git -C "$(dirname "$0")" rev-parse --show-toplevel`, and #2305 (R10-TICK-TRAIN) is merged; nothing on this branch reads train.sh, so the item is left alone.
- `finding-propagation.md: unclear: the same carry lands in this group's brief, whose `files` list is tests/card.mjs and tools/audit/seat/r10_deeplink_mutants.py, rather than in the group that owns train.sh.
