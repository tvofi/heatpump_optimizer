Fix review: merge 9fc2f98be69b1949e86d60ec13d9b12a9005a81b

bus-nonce: 4ec22ff14912b2f7246e50d117bfa7e6

Round: 11, a delta review of 92e0513b1 plus the main merges since 2fe8d1ec1. Measured head: 9fc2f98be69b1949e86d60ec13d9b12a9005a81b; refs/pull/2345/head was re-read just before posting.

## RESULT lines (mine, at 9fc2f98be69b1949e86d60ec13d9b12a9005a81b, PR driver: evidence11/a-c.log)
RESULT mutant=NULL_no_plant rc=0 fails=0
node tests/card.mjs: ALL CARD CHECKS PASSED, 1257 ok, 0 FAIL
RESULT mutant=RD4_form_ns_action_member_button_click_driven rc=0 fails=0
RESULT mutant=RD5_action_member_to_variable_on_rendered_form_driven rc=1 fails=1
RESULT mutant=RD6_anchor_built_href_outside_root_click_driven rc=0 fails=0
RESULT mutant=RD6c_anchor_built_href_in_root_driven_control rc=1 fails=1
RD4-RD6c and RV1-RV7, RV1c and RV5c in the driver are byte-identical to my review_plants, review_plants9 and review_plants10 (13 plants, compared programmatically, all VERBATIM). The RV1-RV7 results stand from round 10 (evidence10). 92e0513b1 changes none of those plants and no census check line: its tests/card.mjs diff is comment lines only.

## Text consistency
- Census paragraph, body ("Residual, exactly", part 2) and all four carries (R10-UX-SETUP, R10-ADVISOR, R10-SCORES, R10-UX-HEALTH) now state part 2 as any markup appended outside the shadow root whose navigation name no static row refuses. Each names RD4 and RD6 as green witnesses, with RD5 and RD6c as red controls placed and not submitted or clicked, and gives the document-level read as the closer. The four carry clauses are byte-identical (one md5). Grepping the roster for "append no form" or "form-submit" finds nothing. The body's only "form-submit" sentence says such an instrument would NOT close RD6, which is correct.
- RD5 is now described as placed and not submitted, which matches its plant.
- R10-DEEPLINK-HANDLERS on origin/main requires the document-level read, with RD4 and RD6 to go red and RD5 and RD6c to stay red, so the split stage's controls now match what I measured.
- Closing keyword: none. The body says "Part of #2317" and closingIssuesReferences is [].

## Merges
Every merge in 2fe8d1ec1..9fc2f98be69b1949e86d60ec13d9b12a9005a81b is pure: the merge of its parents gives exactly its tree for 9fc2f98be, 6cb6e2b78, 9a1ce39c3, 52270b291, a7bb3ec34, fe81e7a5f, 826e4aeb3 and 799bf9c60. git merge-tree --write-tree origin/main 9fc2f98be69b1949e86d60ec13d9b12a9005a81b exits 0. The tests.yml and orchestrator_tick.py changes in the range are main's #2360, arriving through 6cb6e2b78. VERSION, the manifest, the RELEASE_NOTES heading and both claim files are untouched.

## Checks
At 9fc2f98be69b1949e86d60ec13d9b12a9005a81b all 42 check names' latest runs are success or skipped after every workflow concluded (evidence11/checkruns_head.tsv). Not re-run: gate, mutation table, structure, archscore (CI's, green).

## Earlier rounds that still hold
Round 8: the 25-plant sample matched the body, card_drift was identical in all 40 states, the roster conflict resolution was correct, and every red in the branch's history was answered. Round 9: RV1-RV7 verbatim, the runsFrom rename disclosed, the docstring corrected. Round 10: the RD4/RD5 pair. Nothing since changed a census check.
