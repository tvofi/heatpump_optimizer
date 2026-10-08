Fix review: blocked e6e5aea73809387f3b75f09cebcd04e74e6e2701 root-cause-unanswered: fast (3.14) went red at this head (tests/layout.py GUARD new-reference: the new prepr.sh self-test fixture cites retired path docs/delivery/), unanswered
bus-nonce: 932156bcb954d611a3d6bd75c4e15faa

PR #2062, delta round (round 2). Measured at e6e5aea73809387f3b75f09cebcd04e74e6e2701; the live head re-read at posting was unchanged. The delta from 539d300b is af5560f8 (test), a6984468 (fix), 23e200ad (RCA note) and a703959f (row), joined by e6e5aea = merge(539d300b, a703959f). This is not a main merge: origin/main has moved on to b296779f and merge-tree against it gives rc 0.

## The blocker: a red this diff caused
- CI `fast (3.14)` job 113385312852 is completed/failure. The scoped gate passed entities.py and harness_headers.py; the always-run tests/layout.py FAILED:
    new-reference: tools/pr/prepr.sh cites retired path docs/delivery/: (cd "$CLM/r" && $G checkout -q -b rowedit rec && echo edited > docs/delivery/9999.md \
    layout: GUARD: 1 refusal(s) against b296779f0e96
  The cited line is af5560f8's new fixture line. At 539d300b `fast (3.14)` was green.
- I reproduced it locally: `python3 tests/layout.py` in the CI venv gives rc=1 with the same single refusal (against merge base 0b89f781). This is the cheap local detector, about 4 s; the fixer's push gate did not run it.
- The body's `## Red checks` names only delivery-status and nightly-status at 539d300b, so this red is unanswered (fix-review.md step 11, defect-root-cause.md second trigger). It is the PR's own red, so naming it is not enough: the fixture line has to change. Moving the 9999 fixture row to dev/programme/delivery/ (DELIVERY_ROW accepts both homes) or using a form layout.py exempts would clear it. Either way the body owes the cheaper-detector answer.

## What passed (these numbers survive into the next round if the fix touches only the fixture path)
- Failing test first and mutation, `bash tools/pr/prepr.sh --self-test` in the CI venv:
  RESULT head: 212 passed, 0 failed
  RESULT at af5560f8 (test without fix): 211/1, the failure being `pr-body exempts a main-graded red when the diff only ADDS its own delivery row (got 1, wanted 0)`
  RESULT M_fix_removed (the `args+=(--existing-file "$ex")` line deleted at head): 211/1, the same failure
- Null control is real, not vacuous: RESULT M_null_no_red (drop `delivery-status` from both row_red calls): the null case flips to rc 0 (`got 0, wanted 1`). So the null control's rc 1 comes from the delivery-status refusal, not from some unrelated error swallowed by >/dev/null.
- Can --existing-file in prepr exempt a red the PR causes? Not beyond what CI already exempts:
  * prepr derives existing with the same rule pr-contract uses (`git diff --no-renames --name-only --diff-filter=a $BASE...HEAD`). It feeds the same base-copy function `reporterInputsTouched`, over the same range as PATHS (`diff_paths "$BASE"`, the live caller at line 2080).
  * --diff-filter=a keeps edited and deleted base rows. A moved row is a delete plus an add under --no-renames, so its old path still counts. Edits to REPORTER_INPUTS are matched over `paths`, not `existing`.
  * Only rows the PR adds become exempt. delivery-status grades main's first-parent rowless merges and nightly-status grades main's scheduled run, so an added row cannot cause either red.
  * If BASE is unset or the diff fails, no --existing-file is passed and the stricter reading stands. The self-test runs before BASE is assigned (line 974 vs 1824), so the other self-test callers are unchanged.
  * I found no widening. One residual: `$BASE...HEAD` reads the cwd's HEAD while `$2` is the head argument. In every live caller those are the same commit.
- RCA note (23e200ad) matches the code. The delivery row is at the new path dev/programme/delivery/2062.md. VERSION, the manifest version, the notes heading, both claim files and the budgets are untouched.
- Round-1 findings at 539d300b (the token fix, the entities pin and its mutants, the replays, the cost test) concern files the delta did not touch, so they carry.

## Other CI at e6e5aea (one poll, 37 runs)
- nightly-status failed: main's reporter, exempt as in round 1.
- delivery-status was not red at this poll.
- closures, coverage and Analyze (python) were still in progress. coverage is not required. closures may still turn red; read it before the next round.

Evidence: /Users/timmalmstrom/hpo-seats/review-2062/evidence2
