Fix review: blocked ee409c81d7861741f2288491c69cb805c218e24c harness: class-open written history member and programmatic form spellings in the undriven keydown handler pass both arms rc=0 fails=0 (history["back"](), history?.back(), destructured back, createElementNS form, .action = <variable>, Object.assign quoted "action" key, a createElementNS form submitted by button.click()); each sits beside a red control, and the census comment's "The static arm still refuses that surface's names wherever they are written" is false for them

bus-nonce: a660646dc796957c80c5d0685831fbe4

Round: the body numbers the previous review round 7 (verdict on e59b1fb54), so this is round 8 on that count, and the third bus verdict on #2345 (after 90407915e and e59b1fb54). Past round 3, fixer.md owes a re-cut, not another repair (see Direction).

Measured head: ee409c81d7861741f2288491c69cb805c218e24c (refs/pull/2345/head re-read before posting). Contract current: git diff $(merge-base)...origin/main -- dev/governance/roles/ is empty. Merge base 0b1ddb7fd36d995b845374d2aa8b8aeea4545571.

## Resolution delta (orchestrator.md 11)
- ee409c81d and 6e8617475 are pure merges: git merge-tree --write-tree of each one's parents gives exactly its tree (ef8d141e5, c27db9021). git diff c6ef1959a ee409c81d touches only main's files plus the roster. Card, tests/card.mjs and the driver are byte-identical to the code head.
- 176db5f00 (the roster conflict): field by field against base, ours (f1542b17d) and main (6e5753a4a), only R10-SCORES.brief changed on both sides. The merged text is base plus main's item (4) from R10-RATIO-SITES at offset 1415 plus this group's carry appended at offset 3871. Every other changed field takes the side that changed it. The resolution is correct.
- git merge-tree --write-tree origin/main (e5f7e169d) ee409c81d7861741f2288491c69cb805c218e24c exits 0.

## RESULT lines (mine, at ee409c81d7861741f2288491c69cb805c218e24c, driver applied through its own run())
Sample of the 109-plant sweep, 25 plants, four detached worktrees (evidence/sweep1-4.log):
RESULT mutant=NULL_no_plant rc=0 fails=0
RESULT mutant=V3 rc=1 fails=1 | V8 rc=1 fails=1 | V13 rc=1 fails=1
RESULT mutant=F1 rc=0 fails=0 | F2 rc=0 fails=0 (the re-fixed one) | F3 rc=0 fails=0 | F4 rc=0 fails=0
RESULT mutant=X12V8 rc=0 fails=0 | X10V2 rc=0 fails=0
RESULT mutant=T1c rc=1 fails=2 | T2c rc=1 fails=2 | R7c rc=1 fails=1 | Y1 rc=0 fails=0
RESULT mutant=K1 rc=1 fails=2 | K2 rc=1 fails=2 | K3t rc=1 fails=1 | K5 rc=1 fails=2 | Z2 rc=1 fails=1 | Z3 rc=1 fails=1
RESULT mutant=X3 rc=0 fails=0 | X7 rc=0 fails=0 | X8 rc=0 fails=0 | X7K1b rc=1 fails=1 | X1K5b rc=1 fails=2 | X2 rc=1 fails=2
Every sampled plant reads as the body classifies it. node tests/card.mjs: ALL CARD CHECKS PASSED, 1257 ok, 0 FAIL. node tests/card_drift.mjs 0b1ddb7fd: identical in all 40 states (so the b.open to b.foldOpen rename, and runsFrom's open to run, change no rendered state).

Reviewer's own plants. evidence/review_plants.py is my own instrument: it reuses the PR driver's run(), KEYDOWN anchor and P. The plants sit in the same undriven chart keydown handler the round-5 and round-7 blocks used (evidence/rv1-4.log):
RESULT mutant=RV1_history_bracket_back rc=0 fails=0        globalThis.history["back"]()
RESULT mutant=RV2_history_optional_back rc=0 fails=0       globalThis.history?.back()
RESULT mutant=RV3_history_destructure rc=0 fails=0         const { back } = globalThis.history; back.call(...)
RESULT mutant=RV1c_history_dot_back_control rc=1 fails=1   globalThis.history.back(): red on "no navigation token"
RESULT mutant=RV7_create_element_ns_form rc=0 fails=0      document.createElementNS(xhtml, "form")
RESULT mutant=RV5_action_member_to_variable rc=0 fails=0   f.action = u
RESULT mutant=RV5c_action_member_to_literal_control rc=1 fails=1   f.action = "<path>": red
RESULT mutant=RV6_object_assign_quoted_action_key rc=0 fails=0     Object.assign(f, { "action": P })
RESULT mutant=RV4_form_ns_action_member_button_click rc=0 fails=0  a whole written form navigation: createElementNS form, .action = u, a button appended and .click()ed. It is #2345's round-7 class (a written programmatic form) with no refused row

## Why this blocks (fix-review 6)
These names are all written, not built at run time. The census comment's Residual paragraph says "The static arm still refuses that surface's names wherever they are written, the written form spellings included", and the body says a form "built or submitted by name is red wherever it is written". Both claims are false for RV1-RV7. The history row (/history\s*\.[A-Za-z_$]/) is this PR's own; at the merge base there is no NAV_SURFACE. It misses the computed key and the optional chain, which is the same shape the open row was blocked for in round 5 (Z2c). The form rows key on createElement( and on a literal after action =, so createElementNS, a member assignment to a variable, a quoted object key and a submit by button click are each outside every row. Each sits one spelling away from a red control.

## Direction (round 8: a re-cut, not a repair)
This is the third round in which the static arm misses a written spelling (open.call in round 5, the programmatic form in round 7, now these). Adding rows patches spellings, which is the denylist #2317 asked the census to stop being. A re-cut that closes the class removes the reason the static arm carries it: the dynamic arm drives the handlers no click reaches (keydown, pointer, wheel, focus) the way it already drives clicks, through the instrumented surface. A written or built name in those handlers is then the dynamic arm's, and the static arm keeps only the bare-name rows that need no spelling list. If the fixer keeps the static design, the history and form rows must at least be name-based (history as an identifier in any member or destructuring position; action as a member or key name in any write position; createElementNS; a submit through a button's click), with RV1-RV7 added to the driver as plants. The orchestrator may prefer to split the remaining written-spelling class into its own group.

## Other checks
- Stub-selector residual: honestly stated. The Residual paragraph names tests/dom_stub.mjs, a.zz, Y1 green and R7c red, and I reproduced both. Its follow-on sentence about the static arm is the false part (above).
- Card rename: b.open to b.foldOpen is behaviour-neutral. card_drift is identical in all 40 states and card.mjs is green. The body says "the rename is the only card change", but the branch also renames runsFrom's local open to run (d3513acc8, an earlier round). That rename is also neutral and is undisclosed in this body.
- Driver docstring inaccuracy: it says "X1, X2, X3, ... X12 and X13 alone are the detector demonstrations -- the check each line carries is red without it". The body and my runs show X3, X7 and X8 alone read rc=0 fails=0, as the body's "33 green" accounting requires. The docstring contradicts the measurement and should be corrected in the re-cut.
- Forward-carry (step 10): the carry text is present at ee409c81d7861741f2288491c69cb805c218e24c in R10-UX-SETUP, R10-ADVISOR, R10-SCORES and R10-UX-HEALTH, naming NAV_SURFACE, foldOpen and createElement. Its control is the census going red, and it is stated as a precondition. R10-UX-SETUP's resume.stage is already done, so its carry binds no future seat. The carry repeats the "red wherever it is written" claim RV4-RV7 refute, so the re-cut must amend all four.
- Red checks (step 11): the check-runs API over every branch commit (evidence/red_history.tsv) shows failure runs only for pr-contract, fast (3.14) and delivery-status at e59b1fb54, pr-contract and coverage-ratchet at 485d0aa81, and pr-contract and wave-script at 1d45350ba. ## Red checks names and answers each one. At ee409c81d7861741f2288491c69cb805c218e24c every latest run per name is success or skipped (evidence/checkruns_head.tsv), and pr-contract is success.
- VERSION, manifest, RELEASE_NOTES heading, both claim files, tests/closures.json and structure_budgets.json are untouched (three-dot diff is empty).
- Not re-run: full gate, mutation table, structure.py, archscore. I cite CI instead: arch-score, closures, mutation and fast (3.14) are success at ee409c81d7861741f2288491c69cb805c218e24c.
