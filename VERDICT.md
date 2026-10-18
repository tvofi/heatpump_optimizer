Fix review: blocked 2fe8d1ec16f3476473baa82b5dea8927435eff67 harness: class-open residual part 2 names only a form, but its own cause (the dynamic arm reads the shadow root only) also passes an anchor outside the shadow root: RD6, an <a> whose href is set by a run-time-built name, appended to document.body and click()ed inside the driven advisor:settings press, reads rc=0 fails=0 beside RD6c (the same anchor in the shadow root) rc=1 fails=1; the body, the census paragraph and the four carries ("append no form outside the shadow root") and R10-DEEPLINK-HANDLERS' "document-level read OR form-submit instrument" all stop at forms, and a form-submit instrument would not close RD6

bus-nonce: d387478d09fef81fb707cf57aa75d008

Round: 10, a delta review of b7e2ee654 plus main merges since e9e6b99b3. Measured head: 2fe8d1ec16f3476473baa82b5dea8927435eff67; refs/pull/2345/head was re-read just before posting.

## RESULT lines (mine, at 2fe8d1ec16f3476473baa82b5dea8927435eff67, PR driver: evidence10/a-e.log)
RESULT mutant=NULL_no_plant rc=0 fails=0
node tests/card.mjs: ALL CARD CHECKS PASSED, 1257 ok, 0 FAIL
RESULT mutant=RD4_form_ns_action_member_button_click_driven rc=0 fails=0
RESULT mutant=RD5_action_member_to_variable_on_rendered_form_driven rc=1 fails=1
RESULT mutant=RV1_history_bracket_back_in_undriven_keydown rc=0 fails=0
RESULT mutant=RV2_history_optional_back_in_undriven_keydown rc=0 fails=0
RESULT mutant=RV3_history_destructure_in_undriven_keydown rc=0 fails=0
RESULT mutant=RV4_form_ns_action_member_button_click_in_undriven_keydown rc=0 fails=0
RESULT mutant=RV5_action_member_to_variable_in_undriven_keydown rc=0 fails=0
RESULT mutant=RV6_object_assign_quoted_action_key_in_undriven_keydown rc=0 fails=0
RESULT mutant=RV7_create_element_ns_form_in_undriven_keydown rc=0 fails=0
RESULT mutant=RV1c_history_dot_back_control rc=1 fails=1
RESULT mutant=RV5c_action_member_to_literal_control rc=1 fails=1
My round-10 plants (evidence10/review_plants10.py, my own instrument, using the PR driver's after_nav and run(); evidence10/rd6*.log):
RESULT mutant=RD6_anchor_built_href_outside_root_click_driven rc=0 fails=0
RESULT mutant=RD6c_anchor_built_href_in_root_driven_control rc=1 fails=1   (FAIL every link the census records from a press is one haLink builds for this entry: advisor:settings -> href <bare path>)

## (a) Residual statement: not yet exact
- The fixer's text is correct about the cause: "the dynamic arm reads markup in the card's shadow root only". It draws only the form consequence from it, though. Any element appended outside the shadow root whose navigation name no static row refuses passes both arms in a driven press. RD4 is that case for a form submitted by click(), and RD6 is the same case for an anchor whose href name is built at run time and which is click()ed.
- The carries' instruction "so append no form outside the shadow root" leaves a later stage free to append an anchor there.
- R10-DEEPLINK-HANDLERS's brief (f51fe8a30, unchanged at handoff/audit-r10-roster 563d721fa) offers "a document-level read, or instrument a click that submits a form". The second alternative cannot close RD6.
Fix (text and driver only):
1. State part 2 as "any element appended outside the shadow root" (a form submitted by click(), an anchor with a run-time-built href, ...) in the census paragraph, the body and the four carries, and make the instruction "append no markup outside the shadow root".
2. Add RD6 (green) and RD6c (red) to the driver beside RD4 and RD5.
3. The orchestrator amends HANDLERS: the document-level read is required, RD4 and RD6 must go red, and RD5 and RD6c must stay red.
Everything else in (a) holds. Part 1, the Z comment and "Part of #2317" are accurate, and the carries in R10-UX-SETUP, R10-ADVISOR, R10-SCORES and R10-UX-HEALTH are byte-identical to one another in the new clause.

## (b) Plants: verbatim and re-run
RD4, RD5 and RV1-RV7, RV1c and RV5c in the driver are byte-identical to my review_plants.py and review_plants9.py; I compared each plant's edit list programmatically and all 11 read VERBATIM. The results are above, green and red as claimed. A minor point that does not block: the driver and body call RD5 "the same form appended in the shadow root", but RD5 has no button and no click(). It is the same form element and action, placed and not submitted.

## (c) Merges: pure
git merge-tree --write-tree of each merge's parents equals its tree for 2fe8d1ec1, 8e58991d9 and 52f698905. git merge-tree --write-tree origin/main 2fe8d1ec16f3476473baa82b5dea8927435eff67 exits 0. The b7e2ee654 diff to tests/card.mjs changes comment lines only, so no census check changed.

## Checks
At 2fe8d1ec16f3476473baa82b5dea8927435eff67 all 42 check names' latest runs are success or skipped (evidence10/checkruns_head.tsv). There is no closing keyword and closingIssuesReferences is []. Not re-run: gate, mutation table, structure, archscore (CI's, green).
