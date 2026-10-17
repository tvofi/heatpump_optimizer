`tests/card.mjs`'s link census (R10-DEEPLINK, #2283) is the guard that every
route out of the card goes through `haLink`. Its own round-4 review (#2317)
measured four routes that passed both of its arms, three of them with no string
trick at all: a bare `open(` on the feedback row the fixture never rendered, the
Navigation API, a `<form action>` on a rendered page, and an `Event`-built
`hass-more-info`. Both arms were spelling lists -- a token denylist over the
source, and four instruments whose reach depended on which rows the fixture
happened to render -- so each review round closed the last round's spellings and
found the next round's.

The round-5 review (#2345, at `90407915e`) found two more *written* spellings in
the chart's keydown handler, which no press reaches:
`globalThis.open.call(globalThis, "/config/entities", "_self");` (the qualified
token wanted `open(` and the bare token refused a dot-prefixed `open`) and
`navigateTo ("/config/entities");` with one space before the paren (the reach
enumeration was `\b(navigateTo|openHaLink)\(`). Both passed both arms: `rc=0
fails=0`.

Both arms now deny the NAME rather than enumerate spellings:

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
  inert graph. An anchor's `href`, the location object, the history object, the
  Navigation API, `<form`, `action=`, `formaction` and both HA router events are
  the members; `open` is the single case-sensitive token `\bopen\b`, so a bare,
  qualified, indirect (`.call`/`.apply`/`.bind`), value-passed, computed-key or
  whitespace-separated invocation is refused wherever it is written. The card's
  own dialog uses -- its `open()` method definition and call, the `<dialog>`
  element's boolean `open` state, the `open` attribute its fallback sets, and
  the shadow root's `mode: "open"` -- are the only allowances, each removed
  because it cannot resolve the global. The local `open` accumulator in
  `SlotModel.runsFrom`, which shadowed the navigation primitive, is renamed
  `run`; that is an improvement the rule makes possible, not an exemption.
- **Reach by name.** The reach arm enumerates every mention of `navigateTo` and
  `openHaLink` in the card's code outside their definitions (and `openHaLink`'s
  own follow-through) and requires every one to be reached, so a call split from
  its `(` by whitespace or a comment, written `.call`/`.apply`, passed as a
  value, or read through a computed key cannot hide a call site.
- **An allow list.** The dynamic arm presses every element the shadow root wires
  to a click (the dialog's head, close button and tabs included), records any
  event whose type the source does not write as a literal -- whatever class
  built it, the plain `Event` included -- reads `href`, `action` and
  `formaction` off the markup after every press, and refuses by name any global
  the card's code mentions that neither the global nor `window` binds. A
  spelling that *builds* a member's name reaches the same instrument, because
  every member is installed by name.

The inert graph and the token list are two readers of one declaration, which is
what keeps the surface self-maintaining: the scenario before the census must not
crash on a member (a plant killed only by an earlier scenario's crash is `rc=1`
with no FAIL line, so the census's arms never ran and nothing was measured), and
a member present on one side and absent on the other would hide a plant for the
opposite reason.

The residual neither arm reaches is now only a surface name BUILT at run time
inside code no press reaches (a pointer, wheel or keyboard handler):
`globalThis["op" + "en"](...)` names nothing the static arm can read, and no
press drives the handler, so the dynamic arm never sees it. Every *written*
spelling is refused by name, which is what the round-5 plants measure at both
ends below.

Closes #2317.

## Head

`2393446eb30157a6b2096ce6c115eecd767e5c6b` carries the fix commit
`d3513acc8` and merge `6235b4e87`, which merges origin/main
`33e0ee4a2a7250f0bd08e1cf6de2c318e02dd9a1` (2026-10-17T15:48Z) into it with no
resolution. The merge base of this head and `origin/main` is `33e0ee4a2`.
Everything below was measured at `6235b4e87`, except the pre-fix end named
`90407915e` and the merge-base column at `33e0ee4a2`. The two commits after the
measured tree, `f2ae73d23` (the driver's class probes) and `2393446eb` (the
brief carry), leave `tests/card.mjs` and the card byte-identical --
`git diff --quiet 6235b4e87..HEAD -- tests/card.mjs
custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js` exits 0 --
and the null control was re-run at `2393446eb`.

## Mutation proof

Every plant is one mutation, applied by
`tools/audit/seat/r10_deeplink_mutants.py`, which restores the file byte for
byte and refuses to start on a dirty tree. `K*` are the round-4 review's plants
(#2317) and this fix's isolating variants; `W*` are the seams this fix found for
itself; `X*` mutate this fix's own lines; `Z2` and `Z3` are the round-5 review's
two written spellings; `Z3c` is their control.

The two new seams, at the pre-fix end `90407915e` (the review's head; this
branch's driver copied in, card and census byte-identical) and at this head:

    python3 tools/audit/seat/r10_deeplink_mutants.py Z2_open_call_in_undriven_keydown Z3_navigate_to_space_in_undriven_keydown Z3c_navigate_to_standard_in_undriven_keydown_control

- at `90407915e`: `Z2` rc=0 fails=0, `Z3` rc=0 fails=0 -- the two routes the
  review found; `Z3c` rc=1 fails=1, the control, with `sites 9294,10714;
  unreached 10714`.
- at this head: `Z2` rc=1 fails=1, `no navigation token in the card's code
  outside navigateTo` at `10714: globalThis.open.call(globalThis,
  "/config/entities", "_self"`; `Z3` rc=1 fails=1, `the census reached every
  navigateTo and openHaLink mention` with `sites 9294,10714; unreached 10714`;
  `Z3c` rc=1 fails=1, the same reach check. The space no longer decides red vs
  green.

The same handler with the other written forms of the same routes -- `.apply`, a
computed string key, a function value handed to `Reflect.apply`, `.call` on the
reach side, and a newline between the name and its `(` -- is red at this head by
the same two name rules, so the round closes the class rather than the two
strings:

    python3 tools/audit/seat/r10_deeplink_mutants.py Z2b_open_apply_in_undriven_keydown Z2c_open_bracket_in_undriven_keydown Z2d_open_reflect_in_undriven_keydown Z3b_navigate_to_call_in_undriven_keydown Z3d_navigate_to_newline_in_undriven_keydown

`Z2b` rc=1 fails=1, `Z2c` rc=1 fails=1 and `Z2d` rc=1 fails=1 (all on the
static arm at `10714`); `Z3b` rc=1 fails=1 and `Z3d` rc=1 fails=1 (both on the
reach check, `sites 9294,10714; unreached 10714`).

The two new lines, each mutated with the plant it closes as its control:

- **X6** drops the `open` member from `NAV_SURFACE`: `X6` alone rc=0, `X6+Z`
  rc=0 and `X6+Z2` rc=0 -- the named-open token is what closes both the direct
  and the indirect spelling.
- **X9** reverts `LINK_NAME` to the pre-fix `\b(navigateTo|openHaLink)\(`
  call-site form: `X9` alone rc=0, `X9+Z3` rc=0 -- the mention enumeration is
  what closes the whitespace spelling.

The full sweep at this head:

    python3 tools/audit/seat/r10_deeplink_mutants.py

    M1_options_drops_entry rc=1 fails=1; M2_entity_drops_settings_view rc=1 fails=2; M3_delete_advisor_pending_row rc=1 fails=1; M4_unreached_link_site rc=1 fails=1;
    M5_openPicker_no_focus rc=1 fails=1; M6_convert_advisor_settings rc=1 fails=1; R4_entry_ignored rc=1 fails=1; R5_anchor_href rc=1 fails=2;
    R6_more_info_instead_of_nav rc=1 fails=4; R6b_pending_nav_plus_event rc=1 fails=1; R6c_assign_fires_event rc=1 fails=3; R7b_setAttribute_unresolved rc=1 fails=1;
    R7c_setAttribute_runtime_name rc=1 fails=1; R7d_setAttribute_at_click rc=1 fails=1; N1_replaceState_after_pending_push rc=1 fails=2; N2_replaceState_on_dismiss rc=1 fails=3;
    N3_globalThis_open rc=1 fails=2; N4_location_assign_bare rc=1 fails=2; N5_open_on_dismiss rc=1 fails=3; N1t_replaceState_in_try rc=1 fails=2;
    N3t_globalThis_open_in_try rc=1 fails=2; H9t_innerHTML_template_in_try rc=1 fails=1; H1_setAttribute_backtick_rendered rc=1 fails=2; H2_setAttribute_backtick_unrendered rc=1 fails=1;
    H3_Reflect_set_rendered rc=1 fails=2; H4_Reflect_set_unrendered rc=1 fails=1; H5_Object_assign_unrendered rc=1 fails=1; H6_bracket_unrendered rc=1 fails=1;
    H7_attributes_setNamedItem rc=1 fails=1; H8_innerHTML_anchor_single_quote rc=1 fails=1; H9_innerHTML_template rc=1 fails=1; H10_setAttribute_literal_rendered rc=1 fails=2;
    K5_bare_open_on_dismiss rc=1 fails=2; K5b_bracket_open_on_dismiss rc=1 fails=2; K5c_open_call_on_dismiss rc=1 fails=2; K5r_bare_open_rendered_control rc=1 fails=2;
    K1_navigation_api_in_try rc=1 fails=2; K1c_navigation_api_no_try rc=1 fails=2; K1b_navigation_name_built rc=1 fails=1; K2_form_action_rendered rc=1 fails=2;
    K2b_action_set_at_run_time rc=1 fails=1; K3t_event_runtime_more_info rc=1 fails=1; K3c_event_literal_more_info_control rc=1 fails=1; Z_open_in_undriven_keydown rc=1 fails=1;
    Z2_open_call_in_undriven_keydown rc=1 fails=1; Z3_navigate_to_space_in_undriven_keydown rc=1 fails=1; Z3c_navigate_to_standard_in_undriven_keydown_control rc=1 fails=1; W1_guarded_frames rc=1 fails=1;
    W2_history_go_built rc=1 fails=1; W3_unicode_global rc=1 fails=1; X1_fixture_drops_feedback_row rc=1 fails=1; X1K5b_fixture_line_is_what_closes_K5b rc=1 fails=2;
    X2_card_gains_an_act_branch rc=1 fails=2; X3_anchors_drop_action rc=0 fails=0; X3K2b_anchors_line_is_what_closes_K2b rc=0 fails=0; X4_recordEvent_disabled rc=0 fails=0;
    X4K3t_recordEvent_line_is_what_closes_K3t rc=0 fails=0; X5_watch_swallows rc=0 fails=0; X5W1_watch_line_is_what_closes_W1 rc=0 fails=0; X6_surface_drops_bare_open rc=0 fails=0;
    X6Z_surface_member_is_what_closes_Z rc=0 fails=0; X6Z2_surface_member_is_what_closes_Z2 rc=0 fails=0; X9_reach_enumerates_call_sites_not_names rc=0 fails=0; X9Z3_reach_line_is_what_closes_Z3 rc=0 fails=0;
    X7_sink_drops_navigation rc=0 fails=0; X7K1b_surface_member_names_the_primitive_K1b rc=1 fails=1; X8_ascii_grammar rc=0 fails=0; X8W3_grammar_line_is_what_closes_W3 rc=0 fails=0;

Every plant outside the `X*` isolation family is red; the `X*` singles are
green by design, and each composite that pairs one with a plant is the
measurement of its line. The sweep ran before this round's rename of
`X6_surface_drops_bare_open` to `X6_surface_drops_the_open_name`; the renamed
trio in the class-probe run above reads `X6` rc=0, `X6+Z` rc=0, `X6+Z2` rc=0.

The merge-base column, this branch's driver copied into a detached worktree at
`33e0ee4a2` (`tests/card.mjs`, the card and the driver's anchors are unchanged
from the round-5 base `b254b5b06`):

    git worktree add --detach /tmp/r2345-base 33e0ee4a2
    cd /tmp/r2345-base && cp <head>/tools/audit/seat/r10_deeplink_mutants.py tools/audit/seat/
    PYTHONPATH=tests/hastub python3 tests/plan_view.py
    python3 tools/audit/seat/r10_deeplink_mutants.py K5_bare_open_on_dismiss K5b_bracket_open_on_dismiss K5c_open_call_on_dismiss K5r_bare_open_rendered_control K1_navigation_api_in_try K1c_navigation_api_no_try K1b_navigation_name_built K2_form_action_rendered K2b_action_set_at_run_time K3t_event_runtime_more_info K3c_event_literal_more_info_control Z_open_in_undriven_keydown Z2_open_call_in_undriven_keydown Z3_navigate_to_space_in_undriven_keydown Z3c_navigate_to_standard_in_undriven_keydown_control W1_guarded_frames W2_history_go_built W3_unicode_global

prints `K5` rc=0 fails=0, `K5b` rc=0 fails=0, `K5c` rc=0 fails=0, `K1` rc=0,
`K2` rc=0, `K2b` rc=0, `K3t` rc=0, `Z` rc=0, `Z2` rc=0, `Z3` rc=0, `W1` rc=0,
`W3` rc=0 -- every route that escaped the old arms, the two round-5 spellings
included; `K1c` rc=1 fails=0, `K1b` rc=1 fails=0, `W2` rc=1 fails=0 -- killed
only by a crash tail; `K5r` rc=1 fails=1, `K3c` rc=1 fails=1, `Z3c` rc=1
fails=1 -- the controls, red at both ends (`Z3c` on `unreached 10714`, the
round-5 review's own control). The base census prints its own check name, `the
census reached every navigateTo and openHaLink call site`, because this PR's
census is what supplies the mention form; the base is the pre-fix end.

## Null control

`python3 tools/audit/seat/r10_deeplink_mutants.py --null` prints `RESULT
mutant=NULL_no_plant rc=0 fails=0` at this head and at `90407915e`; `node
tests/card.mjs` alone prints `ALL CARD CHECKS PASSED` at both ends. The `X*`
singles with no plant under them (`X3`, `X4`, `X5`, `X6`, `X7`, `X8`, `X9`) are
green, which is what makes each composite a measurement of its line rather than
of the plant.

## Figures

All run from this branch's head, after `PYTHONPATH=tests/hastub python3
tests/plan_view.py`, except where the merge base is named.

- `1253` passing checks at the head, `1249` at the merge base `33e0ee4a2` --
  `node tests/card.mjs | grep -c "^  ok  "`.
- The card's own `act` set is the `ACTS` the census declares, and the source's
  dispatch set is the union the census's own extraction takes: `act === "..."`
  yields 11 names and `data-act="..."` yields 5 literal names (plus two
  `${...}` templates the `[a-z_]+` extraction skips), the union 11 -- the
  declared `ACTS`.
  `grep -oE '\bact === "[a-z_]+"' custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js | sort -u`
  and `grep -oE 'data-act="[a-z_]+"' custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js | sort -u`.
- `42/25/10/32/24` pressables pressed on plan/setup/savings/advisor/health --
  the `Z3` detail line.
- `MODE: SCOPED -- 9 script(s) run, 24 scoped out` over 5 files --
  `dev/programme/delivery/2345.md`, `dev/programme/rosters/wave-r10-groups.json`,
  `tests/card.mjs`, `tools/audit/seat/r10_deeplink_mutants.py` and the card --
  `python3 tests/closure.py select --diff 33e0ee4a2 --workdir <dir>`. The
  round-5 body printed the same `9/24`; at that head it re-derived only with the
  card counted as changed (a planted or dirty tree), and a clean tree gave
  `3/30` over 4 files. This head changes the card, so the clean 5-file, 9/24
  scope is the measured one.
- `AGREEMENT ok` with the census's global-name scan no longer a grammar written
  twice -- `python3 -I tools/policy/agreement_py.py --out /tmp/ag.json && node
  tools/policy/agreement.mjs --py-json /tmp/ag.json` prints
  `divergent=0 unregistered=0 dead=0 refused=0`.
- `STRUCTURE RATCHET PASSED` with every metric unmoved (`max_method_loc 373 <=
  373`, `seam_cut_total 752 <= 752`) -- `python3 tests/structure.py`; the diff
  adds no production line (the card change is a local-variable rename).
- `ALL 16 ARCHITECTURE SCORE HEAD CHECKS PASSED` -- `PYTHONPATH=tests/hastub
  python3 tests/arch_score_head.py`.
- `identical in all 40 states` -- `node tests/card_drift.mjs 33e0ee4a2`.
- `NO UNCLAIMED DRIFT` (56 scenarios) and `NO STALE FIXTURE` (56) --
  `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all 33e0ee4a2`.

## Red checks

- **`coverage-ratchet`** -- red on `early_cutoff.py` at `485d0aa81`, a
  `custom_components/` module this diff does not touch: the known base-reuse
  artifact, where the `coverage` job reuses `tests/features.py`'s base data when
  the diff changes no file in its measured closure. #2349, which lands the floor
  re-validation backstop, is in this head's merge base (`33e0ee4a2`). Cheaper
  detector: `python3 tests/coverage_ratchet.py` on the reused coverage JSON
  (sub-second grade).
- **`wave-script`** -- red on the earlier handoff head `1d45350ba` because
  `tests/card.mjs`'s global-name scan copied `tests/doc_claims.py`'s ASCII word
  grammar `[A-Za-z_$][\w$]*` -- one grammar written twice -- and the base's
  `agreement.mjs` (the copy the lane grades, restored from the base commit) does
  not register it. This head makes the two readers different grammars (the scan
  uses ECMAScript's IdentifierName production), so nothing is left to register.
  Cheaper detector, and it exists: `node tools/policy/agreement.mjs --only
  discovery` runs in under a second and prints the UNREGISTERED line before the
  fix and `AGREEMENT ok` after.
- **`pr-contract`** -- red on the earlier handoff head only as the cascade of the
  unnamed `wave-script` red: the body's `## Red checks` said `none` while the
  head carried a foreign red. This body names it, and `wave-script` is green at
  this head. Cheaper detector, and it exists: the same `policy_lint.mjs
  --pr-body <body> --head <sha> --red wave-script` run CI makes, driven locally
  by `tools/pr/prepr.sh <body> 2345`.

## Forward-carry

`dev/programme/rosters/wave-r10-groups.json`: the `brief` of R10-UX-SETUP,
R10-ADVISOR, R10-UX-HEALTH and R10-SCORES names the census's new refusals -- a
new `data-act` row or `act` branch is red until the census renders and presses a
row that drives it, a new mention of a `NAV_SURFACE` member outside `navigateTo`
is red at once, and a new `navigateTo`/`openHaLink` mention must be a press the
census reaches -- and says to extend the census in the pull request that adds
the row. That file is in this diff. The orchestrator's copy of the same roster
on `handoff/audit-r10-roster` is the newer of the two and is the orchestrator's
to bring level from this one (finding-propagation.md: while two copies disagree,
the newer is right and the other is the bug).

## Friction

- `finding-propagation.md: stale: this group's brief carries R10-TICK (o) -- "`train.sh` line 182 sets the checkout with dirname of `$0` followed by `../..`" -- but at 92accb2cf `tools/audit/seat/train.sh:233` derives it with `git -C "$(dirname "$0")" rev-parse --show-toplevel`, and #2305 (R10-TICK-TRAIN) is merged; nothing on this branch reads train.sh, so the item is left alone.
- `finding-propagation.md: unclear: the same carry lands in this group's brief, whose `files` list is tests/card.mjs and tools/audit/seat/r10_deeplink_mutants.py, rather than in the group that owns train.sh.
