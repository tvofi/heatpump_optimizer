Fix review: blocked a01006c1b46bc5acd3f2c7d8ebe1232c5f4ee2a3 harness: class-open location.pathname/search setters and a head meta refresh pass the census inside a driven handler, outside the stated residual and its carries

bus-nonce: 79d8ef828f8b4d8fa5dde25cf3da5733

Round: 1 (no earlier `Fix review:` comment on #2452). Measured head: a01006c1b46bc5acd3f2c7d8ebe1232c5f4ee2a3 (ev/HEAD), still the PR head at write time. Merge base 4e1b36070. Contract current: `git diff` of dev/governance/roles/ between merge base and origin/main is empty.

## RESULT lines

Finder's plants (RV1-RV7 from the round-8 review, RD4/RD6 from rounds 9-10; #2317's class), driven with the PR's driver at both ends:

| plant | merge base 4e1b36070 | head a01006c1b |
|---|---|---|
| RV1-RV7 (history/form spellings in the chart keydown) | rc=0 fails=0, all seven (finding reproduces) | rc=1 fails=1, all seven |
| RD4, RD6 (markup outside the shadow root, driven press) | rc=0 fails=0 | rc=1 fails=1 |
| RD7 (detached anchor) | rc=0 | rc=1 |
| ON1 (on<event> property) | rc=0 | rc=1 |
| AL1 | rc=1 | rc=1 |
| RD9, KD1, FT1, UL1 | -- | rc=1 fails=1 each |
| RD8 (stated residual witness) | -- | rc=0 (green, as stated) |
| F1 (control) | -- | rc=0 (green, as stated) |
| NULL_no_plant | -- | rc=0 fails=0 |

Mutation proof (the PR's own X pairs, at head): X24ON1 rc=0 (the inline check is what closes ON1 -- load-bearing, as the body says); X22RV1 rc=1 (body does not list it green; consistent). My X17 run aborted on a mistyped plant name (reviewer error, KeyError; tree restored). Full: ev/base_finder_plants.txt, ev/head_finder_plants.txt, ev/head_x_plants.txt.

## The blocking finding: the class is open beyond the stated residual

Reviewer-built plants (my instrument, disclosed: ev/own_plants.py, using the PR driver's run()/kd(); output ev/own_plants.txt), each one statement at the head of the chart keydown handler that this PR now drives:

- `RESULT mutant=OWN1_meta_refresh_in_keydown rc=0 fails=0` -- `<meta http-equiv="refresh" content="0;url=/config/integrations">` appended to document.head. A browser navigates on insertion. No listed name appears (static arm silent); the read enumerates only href/action/formaction and FORM, so the dynamic arm is silent too.
- `RESULT mutant=OWN2_location_pathname_built_in_keydown rc=0 fails=0` -- `globalThis[["loc","ation"].join("")].pathname = "/config/integrations"`. Navigates in a browser. sink.location records only the href setter, assign and replace; any other member write lands silently on a plain object.
- `RESULT mutant=OWN3_location_search_built_in_keydown rc=0 fails=0` -- same with `.search`.
- Control `OWN2c_location_href_built_in_keydown_control`: rc=1 fails=2 (static `href` token and the dynamic recorder both fire), so the position is driven and the recorder works for href. The gap is the member, not reach.

Why it blocks this PR rather than being an older gap: the location sink and the read's attribute list predate this diff, but this PR states the census's coverage. The census comment says "a name BUILT at run time ... is the dynamic arm's on every drive", and the body's Residual says "Two kinds of code still pass": undriven code, and markup through DOM members the stub lacks. OWN1-OWN3 are a third kind, in a driven handler, and are neither in the diff nor dispositioned in the body's "Seams outside that enumeration". The forward-carry exports that two-item residual to R10-ADVISOR, R10-SCORES and R10-UX-HEALTH ("write no navigation there"), so a later card stage would trust a census that passes these (fix-review.md step 6; finding-propagation.md).

The fix is small, either way: make sink.location record every member write (a Proxy set trap, or setters for pathname/search/hash/host/hostname/port/protocol), and add `meta[http-equiv=refresh]` to the read's ways out. Or state both in the census's Residual paragraph, the body and the three briefs' carries, each with a witness plant.

## Other checks (all pass unless noted)

- Merges cleanly: `git merge-tree --write-tree` rc=0 against origin/main 4e1b36070, and again against 64b0ae690 (main moved during the review). ev/merge_tree.txt.
- VERSION, manifest, RELEASE_NOTES.md, claim files, goldens, tests/dom_stub.mjs, closures.json and every *_budgets.json are untouched (three-dot diff empty). The card is unchanged. No fixture moved, so there is nothing to claim.
- `structure.py`: STRUCTURE RATCHET PASSED. `closure.py select`: `MODE: SCOPED -- 3 script(s) run, 30 scoped out`, matching the body. `entities.py` (env -u BASH_ENV): ALL 2350 ENTITY CHECKS PASSED. The body says 2346, which was at its older base; main has since added checks.
- `brief_lint` on the roster: **TOTAL: 1 error**, not the body's 0. The error is `[R10-SCORES] coordinator.py:10281 'heat_loss_coefficient' ... found at line 1075`, and it is identical at the merge base. It is inherited from main's coordinator drift and is not this diff's, but the body's figure does not reproduce at this head. CI `briefs` is green.
- The body's figure of 87 addEventListener sites in the card reproduces (grep count 87). The eleven static names reproduce (NAV_SURFACE has 11 rows).
- Body figures not re-derived: the 137-plant sweep tallies (107/7/23), and the 54.6 s to 3 min 11 s timing (this box ran about 3 min per census under parallel load). Not verified.
- Forward-carry: the in-diff briefs of R10-ADVISOR, R10-SCORES and R10-UX-HEALTH carry the new terms, with the control as a precondition (RV1 red, RD8 green, at the stage's merge base). Roster handoff/audit-r10-roster 04a641598 holds 7 `Source: #2452` entries: 5 in R10-ADVISOR, 1 in R10-RCA-FRICTION and 1 in R10-POLICY-FIXER-MD, matching the body. These carries are what export the incomplete residual above.
- CI on this head (ev/ci_checkruns.txt): the only red is `nightly-status`, which is not this PR's (its diff reaches nothing that check reads), so `## Red checks: none` stands. `coverage` and `Analyze (python)` were still in progress when read. The mutation lane drew no mutant, because the diff writes no production line.
- Architecture (step 15): test and driver code only; no breach seen.
