Fix review: blocked 3ec83def2112ceb09416beab2de0efe314b0edab merge-resolution: tests/deployment_shape.py lost the "184 of the 561" marker, tests/entities.py #1218 check fails

bus-nonce: 268d1e252ae7a6048c0bc1a592367df2

## Review scope

delta: git diff e4a8523d 3ec83def2112ceb09416beab2de0efe314b0edab (main merge 3ee06864 / dbdc520e and its resolution). Previous verdict: merge at e4a8523d.

## Block

- The resolution of tests/deployment_shape.py's selection-cost note deleted the headline line ("recording finds N of the 561 script pairs (34 choose 2) sharing 0.80 or more") instead of re-deriving it. The paragraph now reads "the same / of their production-module closure (184 on the merge ...", which is broken prose, and the docstring no longer carries the string "184 of the 561".
- tests/entities.py (lines ~18176-18190) requires f"{len(_D308_PAIRS)} of the {_D308_TOTAL}" in the whitespace-normalised docstring. At this head the run gives: `FAIL and the lane's docstring records those measured numbers as the selection-cost note (#1218) [... 184 of 561 pairs at >= 0.80; 435 pairs comparable; ... missing markers -> ['184 of the 561']]` (ev/entities_1218.txt).
- The count itself is right: _d308_pairs over tests/closures.json at this head gives 184 of 561, and the trailing "all 184 among the 435 pairs" is correct. The union history (main's 184/180/182/167 and this branch's 184/182) is present.
- Fix: restore the line as "recording finds 184 of the 561 script pairs (34 choose 2) sharing 0.80 or more" ahead of "of their production-module closure (184 on the merge joining ...". The parenthetical's first figure probably wants another look too: it says "184 on the merge", which repeats the headline instead of naming a prior state.

## Evidence

- Production: the PR's own custom_components/ +/- lines, merge-base..head, are byte-identical at e4a8523d (base d9100de7) and 3ec83def2112ceb09416beab2de0efe314b0edab (base 3ee06864): 874 diff lines each. PROD_PM_IDENTICAL.
- In the PR's own diff only tests/deployment_shape.py and tests/structure_budgets.json differ between the two heads. The structure_budgets.json difference is main's merge and was not examined further, because this delta's scope is the resolution.
- git merge-tree --write-tree origin/main (76dd8811) 3ec83def2112ceb09416beab2de0efe314b0edab: clean.
- merge_train.py classify at 3ec83def2112ceb09416beab2de0efe314b0edab: `WAIT 3ec83def2112ceb09416beab2de0efe314b0edab pending: gate red: none` (twice). CI was not yet graded when this verdict was written, and the entities.py lane is expected to go red on the #1218 check above.
- The other FAIL lines in ev/entities.log (a3/a4/a5/a8/hb ...) are harness self-test arm output, not module checks.
- Local run: PYTHONPATH=tests/hastub python3 tests/entities.py with OPENBLAS_CORETYPE=Haswell (cloud-setup OK). The full log is ev/entities.log.
