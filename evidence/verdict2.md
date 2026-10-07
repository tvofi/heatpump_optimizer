Fix review: merge 4544077b94b6f9d934c54712c6928f087f2a611e

bus-nonce: 33a1ff3eb2de4f6508e6fb4d77d13b6b

Round 2. Measured head 4544077b (live head at posting, unchanged); origin/main at review 59b5ac6e.

RESULT body-only: one definition, section 2 table row "next verdict in seq.txt is merge at the same head" = 3 entries / 2 PRs (#1975 x2, #1979), matching seq.txt; #1942 has its own row (no later verdict). Procedural-only set (#1942, #1948, #1975) = 4 entries / 3 PRs, a separate named row. 13+3+... partition: 13 moved-head, 3 same-head, 1 no verdict = 17. CONFIRMED.
RESULT minutes: #1975 21:26:03 -> 21:31:45 = 5.7; #1979 23:09:52 -> 23:14:09 = 4.3; sum 10.0, with 22 disclosed only as the with-#1942 figure. CONFIRMED.
RESULT trigger: measured 2 < 3, not met, so the decline stands; the same figure is in section 5 (both items), the Disposition, section 6, the bugclasses.json countermeasure string and the PR body. No remaining "3 body-only" or "22 min" claim stated as the measure. CONFIRMED.
RESULT d-test: re-took from the committed verdicts_since_0916.txt with my own script (467 PRs, per-PR date and class): before 2026-10-02 11 of 370 carry root-cause-unanswered; from 2026-10-02 27 of 97 (the 27/97 also matched my gh re-take in round 1). CONFIRMED.
RESULT gates: fold_ledger.py check 0 violation(s); merge-tree --write-tree origin/main HEAD exit 0 (no conflict); three-dot diff against origin/main touches no claim file, VERSION or RELEASE_NOTES; the delta e0128bda..4544077b is the doc, the evidence file and one bugclasses string only.
Note (not blocking): the doc's body still says "the other 4 are..."-style wording only as "procedural-only"; line 161 "genuine body debt" for the earlier-window pr-contract-only PRs is a different, unquantified sense and does not feed a number.
