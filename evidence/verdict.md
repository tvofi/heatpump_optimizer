Fix review: blocked e0128bda6ce664cac2d1130e6e2cae45858eb21d other: R9-RCA-1985.md's body-only count is inconsistent, so the cost figure and the revisit trigger do not re-derive under the doc's own rule

bus-nonce: a84d4cecd3149faeb3969d41b681f304

Round 1. Measured head e0128bda (origin/main be0cb821 at review; the doc measured 3910026e).

RESULT count: 12 PRs / 17 entries re-derived: entries.txt has 12 distinct PRs and 17 lines; stats_v6.7.16.txt prints 12 / 17. CONFIRMED.
RESULT timeline: re-derived from timeline_all.txt with my own parse (cancelled runs excluded): first pr-contract green 12/17; pr-contract failed before the verdict 11/17; the other 6 are the 6 with zero prior failures. CONFIRMED. The "6 before Tests completed" times come from the Actions API, not committed; not re-taken.
RESULT d-test: re-took 27 of 97 with gh (97 verdict-carrying PRs merged since 2026-10-02, 0 API failures, rcu verdict regex): 27. CONFIRMED. 11/370 NOT re-derived: verdicts_since_0916.txt keeps no verdict class and no merge date, so the earlier bucket cannot be rebuilt from the committed evidence (state (d) is declared not established, so this does not move the verdict).
RESULT process-state: (c) is argued from evidence (step 11 obeyed, pr-contract present and fired, intended key not delivered); not (b), not (d). ACCEPTED.
RESULT gates: fold_ledger.py check: 0 violation(s), 97 rca entries. merge-tree --write-tree origin/main HEAD exit 0. Claim files: no diff vs origin/main. VERSION, manifest, RELEASE_NOTES untouched. Body Red checks names delivery-status and nightly-status with an owner (#2011). OK.

BLOCKING: the cost test's rework figure and the revisit trigger rest on a count the doc states two ways.
1. Section 2's table: "next verdict is merge at the same head: 4 entries, 3 PRs (#1942, #1975, #1979)". seq.txt shows #1942 has NO second verdict (one line, the block). By that shape the figure is 3 entries / 2 PRs (#1975 x2, #1979).
2. Section 5's cost test: "about 22 min per window" = 5.7 + 4.3 + 12, and the 12 is #1942's time-to-merge at the blocked head, which the doc's own definition ("next verdict was merge at the same head") excludes. Under the stated rule it is 5.7 + 4.3 = 10.0 min. The 22 does not re-derive under the doc's rule (step 8).
3. The revisit trigger is "body-only repairs reach 3 PRs in one window". Section 5 item 2 calls the window's body-only set "the 3 body-only PRs" and the table says 3 PRs, so by the doc's own count the trigger is already met at the window it was measured in and the split is declined anyway. By the strict seq shape the count is 2 and the trigger is unmet, but then the table and the "3 body-only" sentence are wrong. Also "body-only" is used for two sets: section 2's "procedural-only" (#1942, #1948, #1975) and the same-head-merge set (#1942, #1975, #1979).

Repair (doc only, no policy): pick one definition of the trigger shape, fix the table row and the 22 min to match it (or state both figures), say plainly what the count is at the measured window against the trigger of 3, and carry that into the bugclasses countermeasure string and the PR body ("The other 4 are body-only debt" vs "procedural"). The decline itself may stand; the numbers under it must be one set. The PR body's head is e0128bda and matches.
