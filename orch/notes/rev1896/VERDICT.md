Fix review: merge b2c7121ae13e0d351e3a2751d1b7b212c60e1781

All measurements re-taken 2026-10-04 at head b2c7121ae / base b3372838b (= origin/main = merge-base; diff is one commit), finder's commands; evidence/ on this box carries outputs.

1. Row truth: each row's SHA and subject match `gh pr view --json title,mergeCommit` exactly — #1886 cc442e3e, #1891 283eb22f, #1892 b3372838; all MERGED. RESULT: rows true.
2. Base control: `tests/delivery_status.py --check` at b3372838b — `0 rowed, 3 pending, 0 overdue`, pending exactly #1892/#1891/#1886; no other rowless merge (#1893/#1894 open, not merged). RESULT: batch complete.
3. Head: same command — `3 rowed, 0 pending, 0 overdue`; #1896's own row is the documented Forward-carry deferral. RESULT: confirmed.
4. Mutation proof: removing each row flips that merge to `pending`; restored, OK. RESULT: rows load-bearing.
5. Figures re-derived: `policy_lint.mjs --record --since v6.7.16` = `TOTAL: 0 error(s) over 3 merged pull request(s)`. RESULT: confirmed.
6. Scope: exactly docs/delivery/{1886,1891,1892}.md; no VERSION/claims. RESULT: confirmed.
7. Body contract: requested-by first line, headings, Figures with commands, nightly-status answered with run ids, `Friction: none`, preflight rc 0, no armed closing keyword. RESULT: met.
8. CI at head (check-runs API): 0 failures, none in progress at posting. RESULT: red-check trigger answered.
9. Head re-read before posting: still b2c7121ae; nothing moved under the review.

Evidence: /Users/timmalmstrom/hpo-seats/review-1896/evidence/.
